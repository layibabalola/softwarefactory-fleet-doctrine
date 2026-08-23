from __future__ import annotations

import base64
import hashlib
import json
import unittest
from pathlib import Path

import jsonschema

from tools.provider_audit_consumer_provenance import (
    AuditDecision,
    AuditDisposition,
    evaluate_audit_evidence,
    evaluate_provider_substitution,
)


def exact_bytes(content: bytes) -> dict[str, object]:
    return {
        "contentBase64": base64.b64encode(content).decode("ascii"),
        "bytes": len(content),
        "sha256": "sha256:" + hashlib.sha256(content).hexdigest(),
    }


def identity(provider: str = "openai", model: str = "gpt-sol") -> dict[str, object]:
    return {
        "provider": provider,
        "model": model,
        "transport": "firstParty",
        "accountScope": "fleet-review",
    }


def contract() -> dict[str, object]:
    return {
        "schema": "fleet-provider-audit-consumer-contract/v1",
        "readCommandAllowlist": ["read-file", "hash-file"],
    }


def evidence() -> dict[str, object]:
    opinion = exact_bytes(b"VERDICT=EXECUTION_READY\n")
    opinion.update(
        {
            "path": "review/final.md",
            "createDisposition": "CreateNew",
            "createSucceeded": True,
            "writeCount": 1,
            "rejoinedBytes": opinion["bytes"],
            "rejoinedSha256": opinion["sha256"],
        }
    )
    diagnostic = exact_bytes(b'{"status":"healthy"}\n')
    diagnostic.update(
        {
            "kind": "provider_status",
            "immutable": True,
            "classification": "PROVIDER_STATUS_NON_AUTHORITATIVE",
        }
    )
    requested = identity()
    authenticated = identity()
    authenticated.update(
        {
            "authenticated": True,
            "source": "provider_terminal",
            "providerSession": "provider-thread-1",
        }
    )
    return {
        "claim": {
            "consumerSession": "consumer-1",
            "requestedIdentity": requested,
            "actualShell": {
                "path": "C:/Program Files/PowerShell/7/pwsh.exe",
                "version": "7.5.2",
                "sha256": "sha256:" + "1" * 64,
            },
            "wrapper": {
                "path": "review/run-audit.ps1",
                "bytes": 1234,
                "sha256": "sha256:" + "2" * 64,
            },
            "preclaimSelfTest": {
                "beforeClaim": True,
                "outcome": "PASS",
                "shellPath": "C:/Program Files/PowerShell/7/pwsh.exe",
                "shellVersion": "7.5.2",
                "shellSha256": "sha256:" + "1" * 64,
                "wrapperPath": "review/run-audit.ps1",
                "wrapperBytes": 1234,
                "wrapperSha256": "sha256:" + "2" * 64,
                "checks": [
                    "wrapper-syntax",
                    "create-new-probe",
                    "jsonl-terminal-parse",
                    "postflight-fail-closed",
                ],
            },
            "readCommandAllowlist": ["read-file", "hash-file"],
            "finalOpinionCustody": {
                "path": "review/final.md",
                "pathAbsentBeforeClaim": True,
                "createDisposition": "CreateNew",
            },
        },
        "terminal": {
            "consumerSession": "consumer-1",
            "outcome": "EXECUTION_READY",
            "authenticatedIdentity": authenticated,
            "providerDiagnostics": [diagnostic],
            "substantiveVerdict": "EXECUTION_READY",
            "finalOpinion": opinion,
        },
        "postflight": {
            "passed": True,
            "commands": [
                {"commandId": "read-file", "readOnly": True, "exitCode": 0, "status": "completed"},
                {"commandId": "hash-file", "readOnly": True, "exitCode": 0, "status": "completed"},
            ],
            "failedCommandCount": 0,
            "deniedCommandCount": 0,
            "runtimeErrors": [],
            "toolErrors": [],
            "frozenInputsRejoined": True,
            "claimRejoined": True,
            "terminalIdentityAuthenticated": True,
            "opinionCreateNewRejoined": True,
            "zeroUnauthorizedWrites": True,
        },
    }


def no_verdict_evidence() -> dict[str, object]:
    value = evidence()
    diagnostic = exact_bytes(b'{"error":"rate_limit"}\n')
    diagnostic.update(
        {
            "kind": "rate_limit",
            "immutable": True,
            "classification": "RESOURCE_LIMIT_NO_VERDICT",
        }
    )
    value["terminal"] = {
        "consumerSession": "consumer-1",
        "outcome": "NO_VERDICT",
        "providerDiagnostics": [diagnostic],
        "inferenceOccurred": False,
        "opinionPresent": False,
        "spent": True,
        "retryAuthorized": False,
    }
    return value


class ProviderAuditConsumerProvenanceTests(unittest.TestCase):
    def assert_hold(self, value: dict[str, object], reason: str) -> None:
        result = evaluate_audit_evidence(contract(), value)
        self.assertEqual(AuditDisposition.HOLD, result.disposition)
        self.assertEqual(reason, result.reason)
        self.assertFalse(result.execution_authorized)
        self.assertFalse(result.eligible_for_separate_execution_adjudication)

    def test_ready_evidence_is_accepted_without_execution_authority(self) -> None:
        result = evaluate_audit_evidence(contract(), evidence())
        self.assertEqual(AuditDisposition.ACCEPTED_NO_EXECUTION_AUTHORITY, result.disposition)
        self.assertTrue(result.opinion_accepted)
        self.assertTrue(result.eligible_for_separate_execution_adjudication)
        self.assertFalse(result.execution_authorized)

    def test_requested_identity_without_authenticated_terminal_is_insufficient(self) -> None:
        value = evidence()
        del value["terminal"]["authenticatedIdentity"]
        self.assert_hold(value, "MALFORMED")

    def test_identity_must_be_provider_terminal_authenticated(self) -> None:
        value = evidence()
        value["terminal"]["authenticatedIdentity"]["source"] = "wrapper_request"
        self.assert_hold(value, "TERMINAL_IDENTITY")

    def test_authenticated_identity_must_match_requested_tuple(self) -> None:
        value = evidence()
        value["terminal"]["authenticatedIdentity"]["model"] = "different-model"
        self.assert_hold(value, "TERMINAL_IDENTITY")

    def test_final_opinion_requires_preclaim_absence_and_create_new(self) -> None:
        value = evidence()
        value["claim"]["finalOpinionCustody"]["pathAbsentBeforeClaim"] = False
        self.assert_hold(value, "OPINION_CUSTODY")

    def test_final_opinion_exact_bytes_are_recomputed(self) -> None:
        value = evidence()
        value["terminal"]["finalOpinion"]["rejoinedSha256"] = "sha256:" + "0" * 64
        self.assert_hold(value, "OPINION_CUSTODY")

    def test_wrapper_self_test_must_use_actual_shell_version(self) -> None:
        value = evidence()
        value["claim"]["preclaimSelfTest"]["shellVersion"] = "7.4.0"
        self.assert_hold(value, "WRAPPER_SELF_TEST")

    def test_wrapper_self_test_check_set_and_order_are_exact(self) -> None:
        value = evidence()
        value["claim"]["preclaimSelfTest"]["checks"].reverse()
        self.assert_hold(value, "WRAPPER_SELF_TEST")

    def test_unlisted_command_refuses(self) -> None:
        value = evidence()
        value["postflight"]["commands"][0]["commandId"] = "write-file"
        self.assert_hold(value, "COMMAND_ALLOWLIST")

    def test_nonzero_command_exit_refuses(self) -> None:
        value = evidence()
        value["postflight"]["commands"][0]["exitCode"] = 1
        value["postflight"]["commands"][0]["status"] = "failed"
        self.assert_hold(value, "FAILED_COMMAND")

    def test_denied_command_is_not_zero_failure_evidence(self) -> None:
        value = evidence()
        value["postflight"]["deniedCommandCount"] = 1
        self.assert_hold(value, "FAILED_COMMAND")

    def test_provider_diagnostic_bytes_are_immutable(self) -> None:
        value = evidence()
        value["terminal"]["providerDiagnostics"][0]["bytes"] += 1
        self.assert_hold(value, "BYTE_CUSTODY")

    def test_provider_diagnostic_classification_is_deterministic(self) -> None:
        value = evidence()
        value["terminal"]["providerDiagnostics"][0]["classification"] = "RESOURCE_LIMIT_NO_VERDICT"
        self.assert_hold(value, "DIAGNOSTIC_CLASS")

    def test_provider_diagnostic_cannot_suppress_runtime_error(self) -> None:
        value = evidence()
        value["postflight"]["runtimeErrors"] = ["wrapper parse failure"]
        self.assert_hold(value, "RUNTIME_OR_TOOL_ERROR")

    def test_provider_diagnostic_cannot_suppress_tool_error(self) -> None:
        value = evidence()
        value["postflight"]["toolErrors"] = ["read tool failed"]
        self.assert_hold(value, "RUNTIME_OR_TOOL_ERROR")

    def test_substantive_ready_text_cannot_override_failed_postflight(self) -> None:
        value = evidence()
        value["postflight"]["passed"] = False
        self.assert_hold(value, "POSTFLIGHT")

    def test_every_governed_postflight_field_is_required(self) -> None:
        value = evidence()
        value["postflight"]["opinionCreateNewRejoined"] = False
        self.assert_hold(value, "POSTFLIGHT")

    def test_rate_limit_is_spent_no_verdict_lineage(self) -> None:
        result = evaluate_audit_evidence(contract(), no_verdict_evidence())
        self.assertEqual(AuditDisposition.NO_VERDICT_RESOURCE_LIMIT, result.disposition)
        self.assertEqual("consumer-1", result.spent_session)
        self.assertTrue(result.lineage_sha256.startswith("sha256:"))
        self.assertFalse(result.execution_authorized)

    def test_no_verdict_cannot_hide_inference(self) -> None:
        value = no_verdict_evidence()
        value["terminal"]["inferenceOccurred"] = True
        self.assert_hold(value, "NO_VERDICT_LINEAGE")

    def test_no_verdict_cannot_publish_an_opinion(self) -> None:
        value = no_verdict_evidence()
        value["terminal"]["opinionPresent"] = True
        self.assert_hold(value, "NO_VERDICT_LINEAGE")

    def test_rate_limit_diagnostic_cannot_suppress_failed_postflight(self) -> None:
        value = no_verdict_evidence()
        value["postflight"]["passed"] = False
        self.assert_hold(value, "POSTFLIGHT")

    def test_hold_opinion_still_requires_exact_create_new_custody(self) -> None:
        value = evidence()
        value["terminal"]["outcome"] = "HOLD"
        value["terminal"]["substantiveVerdict"] = "HOLD"
        value["terminal"]["finalOpinion"]["writeCount"] = 2
        self.assert_hold(value, "OPINION_CUSTODY")

    def substitution_inputs(self) -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
        prior = {"contract": contract(), "evidence": no_verdict_evidence()}
        lineage = evaluate_audit_evidence(prior["contract"], prior["evidence"]).lineage_sha256
        authority = {
            "decision": "EXPLICIT_PROVIDER_SUBSTITUTION_ONLY",
            "priorLineageSha256": lineage,
            "priorSession": "consumer-1",
            "authorized": True,
            "selectedIdentity": identity("anthropic", "claude-opus"),
            "artifact": exact_bytes(b"explicit substitution\n"),
        }
        next_claim = {
            "consumerSession": "consumer-2",
            "requestedIdentity": identity("anthropic", "claude-opus"),
        }
        return prior, authority, next_claim

    def test_explicit_substitution_uses_fresh_session_and_selected_provider(self) -> None:
        prior, authority, next_claim = self.substitution_inputs()
        result = evaluate_provider_substitution(prior, authority, next_claim)
        self.assertEqual(AuditDisposition.SUBSTITUTION_AUDIT_ELIGIBLE, result.disposition)
        self.assertTrue(result.provider_substitution_authorized)
        self.assertFalse(result.execution_authorized)

    def test_spent_session_cannot_be_retried_as_substitution(self) -> None:
        prior, authority, next_claim = self.substitution_inputs()
        next_claim["consumerSession"] = "consumer-1"
        result = evaluate_provider_substitution(prior, authority, next_claim)
        self.assertEqual("SUBSTITUTION_AUTHORITY", result.reason)

    def test_substitution_requires_explicit_authority(self) -> None:
        prior, authority, next_claim = self.substitution_inputs()
        authority["authorized"] = False
        result = evaluate_provider_substitution(prior, authority, next_claim)
        self.assertEqual("SUBSTITUTION_AUTHORITY", result.reason)

    def test_substitution_cannot_change_selected_identity(self) -> None:
        prior, authority, next_claim = self.substitution_inputs()
        next_claim["requestedIdentity"]["model"] = "lower-model"
        result = evaluate_provider_substitution(prior, authority, next_claim)
        self.assertEqual("SUBSTITUTION_AUTHORITY", result.reason)

    def test_malformed_prior_substitution_lineage_fails_closed(self) -> None:
        result = evaluate_provider_substitution({}, {}, {})
        self.assertEqual(AuditDisposition.HOLD, result.disposition)
        self.assertEqual("MALFORMED", result.reason)

    def test_decision_object_rejects_execution_authority(self) -> None:
        with self.assertRaises(ValueError):
            AuditDecision(AuditDisposition.HOLD, "impossible", execution_authorized=True)

    def test_ready_fixture_conforms_to_portable_schema(self) -> None:
        schema = json.loads(
            (Path(__file__).parents[1] / "schemas/provider-audit-consumer-provenance-v1.schema.json").read_text(
                encoding="utf-8"
            )
        )
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.validate(
            {"schema": "fleet-provider-audit-consumer-provenance/v1", **evidence()},
            schema,
        )

    def test_no_verdict_fixture_conforms_to_portable_schema(self) -> None:
        schema = json.loads(
            (Path(__file__).parents[1] / "schemas/provider-audit-consumer-provenance-v1.schema.json").read_text(
                encoding="utf-8"
            )
        )
        jsonschema.validate(
            {"schema": "fleet-provider-audit-consumer-provenance/v1", **no_verdict_evidence()},
            schema,
        )


if __name__ == "__main__":
    unittest.main()
