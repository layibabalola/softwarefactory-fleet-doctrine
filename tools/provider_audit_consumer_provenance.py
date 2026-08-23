"""Deployment-inert provider audit-consumer provenance contract.

This module validates evidence.  It never invokes a provider, shell, command, workload, or
substantive final opinion.  A positive decision is eligible only for a separate adjudication and
always carries ``execution_authorized=False``.
"""

from __future__ import annotations

import base64
import hashlib
import json
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping, Sequence


SHA256_PREFIX = "sha256:"
SHA256_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")
EVIDENCE_SCHEMA = "fleet-provider-audit-consumer-provenance/v1"
CONTRACT_SCHEMA = "fleet-provider-audit-consumer-contract/v1"
DIAGNOSTIC_SCHEMA = "fleet-provider-terminal-diagnostic/v1"
FINAL_OPINION_SCHEMA = "fleet-provider-final-opinion/v1"
LINEAGE_SCHEMA = "fleet-provider-audit-consumer-lineage/v1"
SUBSTITUTION_SCHEMA = "fleet-provider-substitution-authority/v1"
REQUIRED_SELF_TEST_CHECKS = (
    "wrapper-syntax",
    "create-new-probe",
    "jsonl-terminal-parse",
    "postflight-fail-closed",
)
PROVIDER_DIAGNOSTIC_CLASS = {
    "rate_limit": "RESOURCE_LIMIT_NO_VERDICT",
    "quota": "RESOURCE_LIMIT_NO_VERDICT",
    "provider_status": "PROVIDER_STATUS_NON_AUTHORITATIVE",
}


class AuditDisposition(str, Enum):
    ACCEPTED_NO_EXECUTION_AUTHORITY = "ACCEPTED_NO_EXECUTION_AUTHORITY"
    HOLD = "HOLD"
    NO_VERDICT_RESOURCE_LIMIT = "NO_VERDICT_RESOURCE_LIMIT"
    SUBSTITUTION_AUDIT_ELIGIBLE = "SUBSTITUTION_AUDIT_ELIGIBLE"


@dataclass(frozen=True, slots=True)
class AuditDecision:
    disposition: AuditDisposition
    reason: str
    opinion_accepted: bool = False
    eligible_for_separate_execution_adjudication: bool = False
    provider_substitution_authorized: bool = False
    execution_authorized: bool = False
    spent_session: str | None = None
    lineage_sha256: str | None = None

    def __post_init__(self) -> None:
        if self.execution_authorized:
            raise ValueError("reference doctrine can never grant execution authority")


class EvidenceError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def _mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise EvidenceError("MALFORMED", f"{name} must be an object")
    return value


def _sequence(value: Any, name: str) -> Sequence[Any]:
    if isinstance(value, (str, bytes, bytearray)) or not isinstance(value, Sequence):
        raise EvidenceError("MALFORMED", f"{name} must be an array")
    return value


def _nonempty(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise EvidenceError("MALFORMED", f"{name} must be a nonempty string")
    return value


def _exact_keys(value: Mapping[str, Any], name: str, expected: set[str]) -> None:
    actual = set(value)
    if actual != expected:
        raise EvidenceError(
            "MALFORMED",
            f"{name} fields differ: missing={sorted(expected - actual)!r} extra={sorted(actual - expected)!r}",
        )


def _digest(value: Any, name: str) -> str:
    digest = _nonempty(value, name)
    if SHA256_PATTERN.fullmatch(digest) is None:
        raise EvidenceError("MALFORMED", f"{name} is not an exact lowercase SHA-256 digest")
    return digest


def _integer(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise EvidenceError("MALFORMED", f"{name} must be an integer")
    return value


def _exact_bytes(record: Mapping[str, Any], name: str) -> bytes:
    content_base64 = _nonempty(record.get("contentBase64"), f"{name}.contentBase64")
    try:
        raw = base64.b64decode(content_base64, validate=True)
    except (ValueError, base64.binascii.Error) as exc:
        raise EvidenceError("BYTE_CUSTODY", f"{name} is not canonical base64") from exc
    if base64.b64encode(raw).decode("ascii") != content_base64:
        raise EvidenceError("BYTE_CUSTODY", f"{name} is not canonical base64")
    byte_count = _integer(record.get("bytes"), f"{name}.bytes")
    sha256 = _digest(record.get("sha256"), f"{name}.sha256")
    if byte_count != len(raw) or sha256 != SHA256_PREFIX + hashlib.sha256(raw).hexdigest():
        raise EvidenceError("BYTE_CUSTODY", f"{name} byte tuple does not authenticate its content")
    return raw


def _canonical_sha256(value: Mapping[str, Any]) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return SHA256_PREFIX + hashlib.sha256(encoded).hexdigest()


def _canonical_descriptor_bytes(value: Mapping[str, Any]) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8") + b"\n"


def _identity_tuple(value: Mapping[str, Any], name: str) -> tuple[str, str, str, str]:
    _exact_keys(value, name, {"provider", "model", "transport", "accountScope"})
    return (
        _nonempty(value.get("provider"), f"{name}.provider"),
        _nonempty(value.get("model"), f"{name}.model"),
        _nonempty(value.get("transport"), f"{name}.transport"),
        _nonempty(value.get("accountScope"), f"{name}.accountScope"),
    )


def _authenticated_identity_tuple(value: Mapping[str, Any], name: str) -> tuple[str, str, str, str]:
    _exact_keys(
        value,
        name,
        {"provider", "model", "transport", "accountScope", "authenticated", "source", "providerSession"},
    )
    if value.get("authenticated") is not True or value.get("source") != "provider_terminal":
        raise EvidenceError("TERMINAL_IDENTITY", "provider identity is not terminal-authenticated")
    _nonempty(value.get("providerSession"), f"{name}.providerSession")
    return (
        _nonempty(value.get("provider"), f"{name}.provider"),
        _nonempty(value.get("model"), f"{name}.model"),
        _nonempty(value.get("transport"), f"{name}.transport"),
        _nonempty(value.get("accountScope"), f"{name}.accountScope"),
    )


def _validate_shell_and_wrapper(claim: Mapping[str, Any]) -> None:
    shell = _mapping(claim.get("actualShell"), "claim.actualShell")
    wrapper = _mapping(claim.get("wrapper"), "claim.wrapper")
    self_test = _mapping(claim.get("preclaimSelfTest"), "claim.preclaimSelfTest")
    _exact_keys(shell, "claim.actualShell", {"path", "version", "sha256"})
    _exact_keys(wrapper, "claim.wrapper", {"path", "bytes", "sha256"})
    _exact_keys(
        self_test,
        "claim.preclaimSelfTest",
        {
            "beforeClaim", "outcome", "shellPath", "shellVersion", "shellSha256",
            "wrapperPath", "wrapperBytes", "wrapperSha256", "checks",
        },
    )
    shell_tuple = (
        _nonempty(shell.get("path"), "claim.actualShell.path"),
        _nonempty(shell.get("version"), "claim.actualShell.version"),
        _digest(shell.get("sha256"), "claim.actualShell.sha256"),
    )
    wrapper_tuple = (
        _nonempty(wrapper.get("path"), "claim.wrapper.path"),
        _integer(wrapper.get("bytes"), "claim.wrapper.bytes"),
        _digest(wrapper.get("sha256"), "claim.wrapper.sha256"),
    )
    if wrapper_tuple[1] <= 0:
        raise EvidenceError("WRAPPER_SELF_TEST", "wrapper tuple is not exact")
    if self_test.get("beforeClaim") is not True or self_test.get("outcome") != "PASS":
        raise EvidenceError("WRAPPER_SELF_TEST", "wrapper self-test was not a preclaim PASS")
    if (
        _nonempty(self_test.get("shellPath"), "claim.preclaimSelfTest.shellPath"),
        _nonempty(self_test.get("shellVersion"), "claim.preclaimSelfTest.shellVersion"),
        _digest(self_test.get("shellSha256"), "claim.preclaimSelfTest.shellSha256"),
    ) != shell_tuple:
        raise EvidenceError("WRAPPER_SELF_TEST", "self-test did not run under the claimed actual shell")
    if (
        _nonempty(self_test.get("wrapperPath"), "claim.preclaimSelfTest.wrapperPath"),
        _integer(self_test.get("wrapperBytes"), "claim.preclaimSelfTest.wrapperBytes"),
        _digest(self_test.get("wrapperSha256"), "claim.preclaimSelfTest.wrapperSha256"),
    ) != wrapper_tuple:
        raise EvidenceError("WRAPPER_SELF_TEST", "self-test did not bind the claimed wrapper bytes")
    checks = tuple(_nonempty(item, "claim.preclaimSelfTest.checks[]") for item in _sequence(self_test.get("checks"), "claim.preclaimSelfTest.checks"))
    if checks != REQUIRED_SELF_TEST_CHECKS:
        raise EvidenceError("WRAPPER_SELF_TEST", "preclaim wrapper checks are incomplete or reordered")


def _validate_command_accounting(contract: Mapping[str, Any], claim: Mapping[str, Any], postflight: Mapping[str, Any]) -> None:
    allowed = tuple(
        _nonempty(value, "contract.readCommandAllowlist[]")
        for value in _sequence(contract.get("readCommandAllowlist"), "contract.readCommandAllowlist")
    )
    claimed = tuple(
        _nonempty(value, "claim.readCommandAllowlist[]")
        for value in _sequence(claim.get("readCommandAllowlist"), "claim.readCommandAllowlist")
    )
    if not allowed or len(set(allowed)) != len(allowed) or claimed != allowed:
        raise EvidenceError("COMMAND_ALLOWLIST", "read-command allowlist is empty, duplicate, or not exact")
    commands = _sequence(postflight.get("commands"), "postflight.commands")
    if not commands:
        raise EvidenceError("COMMAND_ALLOWLIST", "postflight contains no read-command evidence")
    observed: list[str] = []
    for index, raw_command in enumerate(commands):
        command = _mapping(raw_command, f"postflight.commands[{index}]")
        _exact_keys(command, f"postflight.commands[{index}]", {"commandId", "readOnly", "exitCode", "status"})
        command_id = _nonempty(command.get("commandId"), f"postflight.commands[{index}].commandId")
        observed.append(command_id)
        if command_id not in allowed:
            raise EvidenceError("COMMAND_ALLOWLIST", f"command {command_id!r} is outside the read allowlist")
        if command.get("readOnly") is not True:
            raise EvidenceError("COMMAND_ALLOWLIST", f"command {command_id!r} is not classified read-only")
        if _integer(command.get("exitCode"), f"postflight.commands[{index}].exitCode") != 0 or command.get("status") != "completed":
            raise EvidenceError("FAILED_COMMAND", f"command {command_id!r} did not complete with exit 0")
    if tuple(observed) != allowed:
        raise EvidenceError("COMMAND_ALLOWLIST", "postflight command accounting is not exact and ordered")
    if _integer(postflight.get("failedCommandCount"), "postflight.failedCommandCount") != 0:
        raise EvidenceError("FAILED_COMMAND", "postflight reports a failed command")
    if _integer(postflight.get("deniedCommandCount"), "postflight.deniedCommandCount") != 0:
        raise EvidenceError("FAILED_COMMAND", "postflight reports a denied command")


def classify_provider_diagnostic(record: Mapping[str, Any], expected_provider_session: str | None = None) -> str:
    """Authenticate and deterministically classify provider-only diagnostic bytes."""

    _exact_keys(
        record,
        "providerDiagnostic",
        {"contentBase64", "bytes", "sha256", "kind", "immutable", "classification"},
    )
    raw = _exact_bytes(record, "providerDiagnostic")
    try:
        descriptor = _mapping(json.loads(raw.decode("utf-8")), "providerDiagnostic.content")
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise EvidenceError("DIAGNOSTIC_CLASS", "provider diagnostic content is not canonical JSON") from exc
    _exact_keys(descriptor, "providerDiagnostic.content", {"schema", "kind", "code", "providerSession"})
    if raw != _canonical_descriptor_bytes(descriptor) or descriptor.get("schema") != DIAGNOSTIC_SCHEMA:
        raise EvidenceError("DIAGNOSTIC_CLASS", "provider diagnostic descriptor is not canonical or versioned")
    kind = _nonempty(descriptor.get("kind"), "providerDiagnostic.content.kind")
    if record.get("kind") != kind:
        raise EvidenceError("DIAGNOSTIC_CLASS", "provider diagnostic sibling kind was reclassified")
    _nonempty(descriptor.get("code"), "providerDiagnostic.content.code")
    provider_session = _nonempty(descriptor.get("providerSession"), "providerDiagnostic.content.providerSession")
    if expected_provider_session is not None and provider_session != expected_provider_session:
        raise EvidenceError("DIAGNOSTIC_CLASS", "provider diagnostic does not bind the authenticated provider session")
    expected = PROVIDER_DIAGNOSTIC_CLASS.get(kind)
    if expected is None:
        raise EvidenceError("DIAGNOSTIC_CLASS", f"unsupported provider diagnostic kind {kind!r}")
    if record.get("immutable") is not True or record.get("classification") != expected:
        raise EvidenceError("DIAGNOSTIC_CLASS", "provider diagnostic classification is mutable or incorrect")
    return expected


def _validate_opinion_claim(claim: Mapping[str, Any]) -> str:
    custody = _mapping(claim.get("finalOpinionCustody"), "claim.finalOpinionCustody")
    _exact_keys(custody, "claim.finalOpinionCustody", {"path", "pathAbsentBeforeClaim", "createDisposition"})
    custody_path = _nonempty(custody.get("path"), "claim.finalOpinionCustody.path")
    if custody.get("pathAbsentBeforeClaim") is not True or custody.get("createDisposition") != "CreateNew":
        raise EvidenceError("OPINION_CUSTODY", "final opinion claim lacks preclaim CreateNew custody")
    return custody_path


def _validate_opinion_custody(
    claim: Mapping[str, Any],
    terminal: Mapping[str, Any],
    consumer_session: str,
    provider_session: str,
) -> str:
    custody_path = _validate_opinion_claim(claim)
    opinion = _mapping(terminal.get("finalOpinion"), "terminal.finalOpinion")
    _exact_keys(
        opinion,
        "terminal.finalOpinion",
        {
            "contentBase64", "bytes", "sha256", "path", "createDisposition", "createSucceeded",
            "writeCount", "rejoinedBytes", "rejoinedSha256",
        },
    )
    opinion_path = _nonempty(opinion.get("path"), "terminal.finalOpinion.path")
    if (
        custody_path != opinion_path
        or opinion.get("createDisposition") != "CreateNew"
        or opinion.get("createSucceeded") is not True
        or _integer(opinion.get("writeCount"), "terminal.finalOpinion.writeCount") != 1
    ):
        raise EvidenceError("OPINION_CUSTODY", "final opinion does not have exact CreateNew custody")
    raw = _exact_bytes(opinion, "terminal.finalOpinion")
    if (
        opinion.get("rejoinedBytes") != len(raw)
        or _digest(opinion.get("rejoinedSha256"), "terminal.finalOpinion.rejoinedSha256")
        != SHA256_PREFIX + hashlib.sha256(raw).hexdigest()
    ):
        raise EvidenceError("OPINION_CUSTODY", "final opinion did not physically rejoin exact bytes")
    try:
        descriptor = _mapping(json.loads(raw.decode("utf-8")), "terminal.finalOpinion.content")
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise EvidenceError("SUBSTANTIVE_TEXT", "final opinion content is not canonical JSON") from exc
    _exact_keys(
        descriptor,
        "terminal.finalOpinion.content",
        {"schema", "verdict", "consumerSession", "providerSession"},
    )
    if raw != _canonical_descriptor_bytes(descriptor) or descriptor.get("schema") != FINAL_OPINION_SCHEMA:
        raise EvidenceError("SUBSTANTIVE_TEXT", "final opinion descriptor is not canonical or versioned")
    verdict = _nonempty(descriptor.get("verdict"), "terminal.finalOpinion.content.verdict")
    if verdict not in ("EXECUTION_READY", "HOLD"):
        raise EvidenceError("SUBSTANTIVE_TEXT", "final opinion descriptor verdict is unsupported")
    if (
        descriptor.get("consumerSession") != consumer_session
        or descriptor.get("providerSession") != provider_session
        or terminal.get("substantiveVerdict") != verdict
    ):
        raise EvidenceError("SUBSTANTIVE_TEXT", "mutable terminal metadata does not match exact final-opinion bytes")
    return verdict


def _hold(code: str) -> AuditDecision:
    return AuditDecision(AuditDisposition.HOLD, code)


def evaluate_audit_evidence(contract_value: Mapping[str, Any], evidence_value: Mapping[str, Any]) -> AuditDecision:
    """Evaluate one audit evidence package without granting or performing execution."""

    try:
        contract = _mapping(contract_value, "contract")
        evidence = _mapping(evidence_value, "evidence")
        _exact_keys(contract, "contract", {"schema", "readCommandAllowlist"})
        _exact_keys(evidence, "evidence", {"schema", "claim", "terminal", "postflight"})
        if contract.get("schema") != CONTRACT_SCHEMA or evidence.get("schema") != EVIDENCE_SCHEMA:
            raise EvidenceError("MALFORMED", "contract or evidence schema is unsupported")
        claim = _mapping(evidence.get("claim"), "evidence.claim")
        terminal = _mapping(evidence.get("terminal"), "evidence.terminal")
        postflight = _mapping(evidence.get("postflight"), "evidence.postflight")
        _exact_keys(
            claim,
            "evidence.claim",
            {
                "consumerSession", "requestedIdentity", "actualShell", "wrapper", "preclaimSelfTest",
                "readCommandAllowlist", "finalOpinionCustody",
            },
        )
        _exact_keys(
            postflight,
            "evidence.postflight",
            {
                "passed", "commands", "failedCommandCount", "deniedCommandCount", "runtimeErrors",
                "toolErrors", "frozenInputsRejoined", "claimRejoined", "terminalIdentityAuthenticated",
                "opinionCreateNewRejoined", "zeroUnauthorizedWrites",
            },
        )
        consumer_session = _nonempty(claim.get("consumerSession"), "claim.consumerSession")
        if terminal.get("consumerSession") != consumer_session:
            raise EvidenceError("SESSION_CUSTODY", "terminal does not bind the claimed consumer session")
        _validate_opinion_claim(claim)
        _validate_shell_and_wrapper(claim)
        _validate_command_accounting(contract, claim, postflight)

        outcome = _nonempty(terminal.get("outcome"), "terminal.outcome")
        if outcome == "NO_VERDICT":
            _exact_keys(
                terminal,
                "evidence.terminal",
                {
                    "consumerSession", "outcome", "authenticatedIdentity", "providerDiagnostics",
                    "inferenceOccurred", "opinionPresent", "spent", "retryAuthorized",
                },
            )
        elif outcome in ("EXECUTION_READY", "HOLD"):
            _exact_keys(
                terminal,
                "evidence.terminal",
                {
                    "consumerSession", "outcome", "authenticatedIdentity", "providerDiagnostics",
                    "substantiveVerdict", "finalOpinion",
                },
            )
        else:
            raise EvidenceError("TERMINAL_OUTCOME", "terminal outcome is unsupported")

        requested = _mapping(claim.get("requestedIdentity"), "claim.requestedIdentity")
        authenticated = _mapping(terminal.get("authenticatedIdentity"), "terminal.authenticatedIdentity")
        if _identity_tuple(requested, "claim.requestedIdentity") != _authenticated_identity_tuple(
            authenticated, "terminal.authenticatedIdentity"
        ):
            raise EvidenceError("TERMINAL_IDENTITY", "requested and authenticated provider identities differ")
        provider_session = _nonempty(authenticated.get("providerSession"), "terminal.authenticatedIdentity.providerSession")

        diagnostics = tuple(
            classify_provider_diagnostic(_mapping(item, "providerDiagnostics[]"), provider_session)
            for item in _sequence(terminal.get("providerDiagnostics"), "terminal.providerDiagnostics")
        )
        runtime_errors = _sequence(postflight.get("runtimeErrors"), "postflight.runtimeErrors")
        tool_errors = _sequence(postflight.get("toolErrors"), "postflight.toolErrors")
        if runtime_errors or tool_errors:
            raise EvidenceError("RUNTIME_OR_TOOL_ERROR", "provider diagnostics cannot suppress runtime or tool errors")
        if postflight.get("passed") is not True:
            raise EvidenceError("POSTFLIGHT", "governed postflight did not pass")
        for field in ("frozenInputsRejoined", "claimRejoined", "zeroUnauthorizedWrites"):
            if postflight.get(field) is not True:
                raise EvidenceError("POSTFLIGHT", f"postflight field {field} is not true")

        if postflight.get("terminalIdentityAuthenticated") is not True:
            raise EvidenceError("POSTFLIGHT", "postflight did not authenticate terminal provider identity")
        if outcome == "NO_VERDICT":
            if (
                not diagnostics
                or any(item != "RESOURCE_LIMIT_NO_VERDICT" for item in diagnostics)
                or terminal.get("inferenceOccurred") is not False
                or terminal.get("opinionPresent") is not False
                or terminal.get("spent") is not True
                or terminal.get("retryAuthorized") is not False
                or postflight.get("opinionCreateNewRejoined") is not False
            ):
                raise EvidenceError("NO_VERDICT_LINEAGE", "resource-limit no-verdict lineage is incomplete")
            return AuditDecision(
                AuditDisposition.NO_VERDICT_RESOURCE_LIMIT,
                "RESOURCE_LIMIT_NO_VERDICT",
                spent_session=consumer_session,
                lineage_sha256=_canonical_sha256(
                    {"schema": LINEAGE_SCHEMA, "contract": contract, "evidence": evidence}
                ),
            )

        if any(item == "RESOURCE_LIMIT_NO_VERDICT" for item in diagnostics):
            raise EvidenceError(
                "RESOURCE_LIMIT_TERMINAL_CONFLICT",
                "resource-limit diagnostics preclude a substantive terminal outcome",
            )
        if postflight.get("opinionCreateNewRejoined") is not True:
            raise EvidenceError("POSTFLIGHT", "postflight did not rejoin exact CreateNew opinion")

        opinion_verdict = _validate_opinion_custody(claim, terminal, consumer_session, provider_session)
        if opinion_verdict != outcome:
            raise EvidenceError("SUBSTANTIVE_TEXT", "exact final-opinion verdict does not match terminal outcome")
        if outcome == "HOLD":
            return _hold("PROVIDER_HOLD")
        return AuditDecision(
            AuditDisposition.ACCEPTED_NO_EXECUTION_AUTHORITY,
            "AUDIT_EVIDENCE_ACCEPTED",
            opinion_accepted=True,
            eligible_for_separate_execution_adjudication=True,
        )
    except EvidenceError as exc:
        return _hold(exc.code)


def evaluate_provider_substitution(
    prior_evidence: Any,
    authority_value: Mapping[str, Any],
    next_claim_value: Mapping[str, Any],
) -> AuditDecision:
    """Verify explicit provider substitution after a spent resource-limit no-verdict."""

    try:
        prior_root = _mapping(prior_evidence, "priorEvidence")
        _exact_keys(prior_root, "priorEvidence", {"contract", "evidence"})
        prior_contract = _mapping(prior_root.get("contract"), "priorEvidence.contract")
        prior_package = _mapping(prior_root.get("evidence"), "priorEvidence.evidence")
        prior = evaluate_audit_evidence(prior_contract, prior_package)
        if prior.disposition is not AuditDisposition.NO_VERDICT_RESOURCE_LIMIT:
            return _hold("SUBSTITUTION_PRIOR_NOT_SPENT")
        authority = _mapping(authority_value, "authority")
        next_claim = _mapping(next_claim_value, "nextClaim")
        _exact_keys(authority, "authority", {"artifact"})
        _exact_keys(next_claim, "nextClaim", {"consumerSession", "requestedIdentity"})
        artifact_record = _mapping(authority.get("artifact"), "authority.artifact")
        _exact_keys(artifact_record, "authority.artifact", {"contentBase64", "bytes", "sha256"})
        artifact_raw = _exact_bytes(artifact_record, "authority.artifact")
        try:
            artifact = _mapping(json.loads(artifact_raw.decode("utf-8")), "authority.artifact.content")
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise EvidenceError("SUBSTITUTION_AUTHORITY", "substitution authority is not canonical JSON") from exc
        _exact_keys(
            artifact,
            "authority.artifact.content",
            {
                "schema", "decision", "priorLineageSha256", "priorSession", "newConsumerSession",
                "authorized", "selectedIdentity",
            },
        )
        if artifact_raw != _canonical_descriptor_bytes(artifact) or artifact.get("schema") != SUBSTITUTION_SCHEMA:
            raise EvidenceError("SUBSTITUTION_AUTHORITY", "substitution authority is not canonical or versioned")
        if (
            artifact.get("decision") != "EXPLICIT_PROVIDER_SUBSTITUTION_ONLY"
            or artifact.get("priorLineageSha256") != prior.lineage_sha256
            or artifact.get("priorSession") != prior.spent_session
            or artifact.get("authorized") is not True
        ):
            raise EvidenceError("SUBSTITUTION_AUTHORITY", "substitution authority does not bind spent lineage")
        new_session = _nonempty(next_claim.get("consumerSession"), "nextClaim.consumerSession")
        if new_session == prior.spent_session or artifact.get("newConsumerSession") != new_session:
            raise EvidenceError("SUBSTITUTION_AUTHORITY", "spent session cannot be retried or resumed")
        selected = _mapping(artifact.get("selectedIdentity"), "authority.artifact.content.selectedIdentity")
        requested = _mapping(next_claim.get("requestedIdentity"), "nextClaim.requestedIdentity")
        if _identity_tuple(selected, "authority.artifact.content.selectedIdentity") != _identity_tuple(
            requested, "nextClaim.requestedIdentity"
        ):
            raise EvidenceError("SUBSTITUTION_AUTHORITY", "next claim does not use explicitly selected identity")
        return AuditDecision(
            AuditDisposition.SUBSTITUTION_AUDIT_ELIGIBLE,
            "EXPLICIT_SUBSTITUTION_ACCEPTED",
            provider_substitution_authorized=True,
        )
    except EvidenceError as exc:
        return _hold(exc.code)


__all__ = [
    "AuditDecision",
    "AuditDisposition",
    "EvidenceError",
    "classify_provider_diagnostic",
    "evaluate_audit_evidence",
    "evaluate_provider_substitution",
]
