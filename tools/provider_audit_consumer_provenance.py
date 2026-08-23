"""Deployment-inert provider audit-consumer provenance contract.

This module validates evidence.  It never invokes a provider, shell, command, workload, or
substantive final opinion.  A positive decision is eligible only for a separate adjudication and
always carries ``execution_authorized=False``.
"""

from __future__ import annotations

import base64
import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping, Sequence


SHA256_PREFIX = "sha256:"
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


def _integer(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise EvidenceError("MALFORMED", f"{name} must be an integer")
    return value


def _exact_bytes(record: Mapping[str, Any], name: str) -> bytes:
    try:
        raw = base64.b64decode(_nonempty(record.get("contentBase64"), f"{name}.contentBase64"), validate=True)
    except (ValueError, base64.binascii.Error) as exc:
        raise EvidenceError("BYTE_CUSTODY", f"{name} is not canonical base64") from exc
    byte_count = _integer(record.get("bytes"), f"{name}.bytes")
    sha256 = _nonempty(record.get("sha256"), f"{name}.sha256")
    if byte_count != len(raw) or sha256 != SHA256_PREFIX + hashlib.sha256(raw).hexdigest():
        raise EvidenceError("BYTE_CUSTODY", f"{name} byte tuple does not authenticate its content")
    return raw


def _canonical_sha256(value: Mapping[str, Any]) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return SHA256_PREFIX + hashlib.sha256(encoded).hexdigest()


def _identity_tuple(value: Mapping[str, Any], name: str) -> tuple[str, str, str, str]:
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
    shell_tuple = (
        _nonempty(shell.get("path"), "claim.actualShell.path"),
        _nonempty(shell.get("version"), "claim.actualShell.version"),
        _nonempty(shell.get("sha256"), "claim.actualShell.sha256"),
    )
    if not shell_tuple[2].startswith(SHA256_PREFIX):
        raise EvidenceError("WRAPPER_SELF_TEST", "actual shell digest is not SHA-256")
    wrapper_tuple = (
        _nonempty(wrapper.get("path"), "claim.wrapper.path"),
        _integer(wrapper.get("bytes"), "claim.wrapper.bytes"),
        _nonempty(wrapper.get("sha256"), "claim.wrapper.sha256"),
    )
    if wrapper_tuple[1] <= 0 or not wrapper_tuple[2].startswith(SHA256_PREFIX):
        raise EvidenceError("WRAPPER_SELF_TEST", "wrapper tuple is not exact")
    if self_test.get("beforeClaim") is not True or self_test.get("outcome") != "PASS":
        raise EvidenceError("WRAPPER_SELF_TEST", "wrapper self-test was not a preclaim PASS")
    if (
        self_test.get("shellPath"),
        self_test.get("shellVersion"),
        self_test.get("shellSha256"),
    ) != shell_tuple:
        raise EvidenceError("WRAPPER_SELF_TEST", "self-test did not run under the claimed actual shell")
    if (
        self_test.get("wrapperPath"),
        self_test.get("wrapperBytes"),
        self_test.get("wrapperSha256"),
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
    for index, raw_command in enumerate(commands):
        command = _mapping(raw_command, f"postflight.commands[{index}]")
        command_id = _nonempty(command.get("commandId"), f"postflight.commands[{index}].commandId")
        if command_id not in allowed:
            raise EvidenceError("COMMAND_ALLOWLIST", f"command {command_id!r} is outside the read allowlist")
        if command.get("readOnly") is not True:
            raise EvidenceError("COMMAND_ALLOWLIST", f"command {command_id!r} is not classified read-only")
        if _integer(command.get("exitCode"), f"postflight.commands[{index}].exitCode") != 0 or command.get("status") != "completed":
            raise EvidenceError("FAILED_COMMAND", f"command {command_id!r} did not complete with exit 0")
    if _integer(postflight.get("failedCommandCount"), "postflight.failedCommandCount") != 0:
        raise EvidenceError("FAILED_COMMAND", "postflight reports a failed command")
    if _integer(postflight.get("deniedCommandCount"), "postflight.deniedCommandCount") != 0:
        raise EvidenceError("FAILED_COMMAND", "postflight reports a denied command")


def classify_provider_diagnostic(record: Mapping[str, Any]) -> str:
    """Authenticate and deterministically classify provider-only diagnostic bytes."""

    _exact_bytes(record, "providerDiagnostic")
    kind = _nonempty(record.get("kind"), "providerDiagnostic.kind")
    expected = PROVIDER_DIAGNOSTIC_CLASS.get(kind)
    if expected is None:
        raise EvidenceError("DIAGNOSTIC_CLASS", f"unsupported provider diagnostic kind {kind!r}")
    if record.get("immutable") is not True or record.get("classification") != expected:
        raise EvidenceError("DIAGNOSTIC_CLASS", "provider diagnostic classification is mutable or incorrect")
    return expected


def _validate_opinion_custody(claim: Mapping[str, Any], terminal: Mapping[str, Any]) -> None:
    custody = _mapping(claim.get("finalOpinionCustody"), "claim.finalOpinionCustody")
    opinion = _mapping(terminal.get("finalOpinion"), "terminal.finalOpinion")
    if (
        custody.get("path") != opinion.get("path")
        or custody.get("pathAbsentBeforeClaim") is not True
        or custody.get("createDisposition") != "CreateNew"
        or opinion.get("createDisposition") != "CreateNew"
        or opinion.get("createSucceeded") is not True
        or _integer(opinion.get("writeCount"), "terminal.finalOpinion.writeCount") != 1
    ):
        raise EvidenceError("OPINION_CUSTODY", "final opinion does not have exact CreateNew custody")
    raw = _exact_bytes(opinion, "terminal.finalOpinion")
    if (
        opinion.get("rejoinedBytes") != len(raw)
        or opinion.get("rejoinedSha256") != SHA256_PREFIX + hashlib.sha256(raw).hexdigest()
    ):
        raise EvidenceError("OPINION_CUSTODY", "final opinion did not physically rejoin exact bytes")


def _hold(code: str) -> AuditDecision:
    return AuditDecision(AuditDisposition.HOLD, code)


def evaluate_audit_evidence(contract_value: Mapping[str, Any], evidence_value: Mapping[str, Any]) -> AuditDecision:
    """Evaluate one audit evidence package without granting or performing execution."""

    try:
        contract = _mapping(contract_value, "contract")
        evidence = _mapping(evidence_value, "evidence")
        claim = _mapping(evidence.get("claim"), "evidence.claim")
        terminal = _mapping(evidence.get("terminal"), "evidence.terminal")
        postflight = _mapping(evidence.get("postflight"), "evidence.postflight")
        consumer_session = _nonempty(claim.get("consumerSession"), "claim.consumerSession")
        if terminal.get("consumerSession") != consumer_session:
            raise EvidenceError("SESSION_CUSTODY", "terminal does not bind the claimed consumer session")
        _validate_shell_and_wrapper(claim)
        _validate_command_accounting(contract, claim, postflight)

        diagnostics = tuple(
            classify_provider_diagnostic(_mapping(item, "providerDiagnostics[]"))
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

        outcome = _nonempty(terminal.get("outcome"), "terminal.outcome")
        if outcome == "NO_VERDICT":
            if (
                not diagnostics
                or any(item != "RESOURCE_LIMIT_NO_VERDICT" for item in diagnostics)
                or terminal.get("inferenceOccurred") is not False
                or terminal.get("opinionPresent") is not False
                or terminal.get("spent") is not True
                or terminal.get("retryAuthorized") is not False
            ):
                raise EvidenceError("NO_VERDICT_LINEAGE", "resource-limit no-verdict lineage is incomplete")
            return AuditDecision(
                AuditDisposition.NO_VERDICT_RESOURCE_LIMIT,
                "RESOURCE_LIMIT_NO_VERDICT",
                spent_session=consumer_session,
                lineage_sha256=_canonical_sha256(evidence),
            )

        if outcome not in ("EXECUTION_READY", "HOLD"):
            raise EvidenceError("TERMINAL_OUTCOME", "terminal outcome is unsupported")
        for field in (
            "terminalIdentityAuthenticated",
            "opinionCreateNewRejoined",
        ):
            if postflight.get(field) is not True:
                raise EvidenceError("POSTFLIGHT", f"postflight field {field} is not true")

        requested = _mapping(claim.get("requestedIdentity"), "claim.requestedIdentity")
        authenticated = _mapping(terminal.get("authenticatedIdentity"), "terminal.authenticatedIdentity")
        if authenticated.get("authenticated") is not True or authenticated.get("source") != "provider_terminal":
            raise EvidenceError("TERMINAL_IDENTITY", "provider identity is not terminal-authenticated")
        if _identity_tuple(requested, "claim.requestedIdentity") != _identity_tuple(authenticated, "terminal.authenticatedIdentity"):
            raise EvidenceError("TERMINAL_IDENTITY", "requested and authenticated provider identities differ")
        _nonempty(authenticated.get("providerSession"), "terminal.authenticatedIdentity.providerSession")

        _validate_opinion_custody(claim, terminal)
        if outcome == "HOLD":
            return _hold("PROVIDER_HOLD")
        if terminal.get("substantiveVerdict") != "EXECUTION_READY":
            raise EvidenceError("SUBSTANTIVE_TEXT", "exact final opinion lacks the required substantive verdict")
        return AuditDecision(
            AuditDisposition.ACCEPTED_NO_EXECUTION_AUTHORITY,
            "AUDIT_EVIDENCE_ACCEPTED",
            opinion_accepted=True,
            eligible_for_separate_execution_adjudication=True,
        )
    except EvidenceError as exc:
        return _hold(exc.code)


def evaluate_provider_substitution(
    prior_evidence: Mapping[str, Any],
    authority_value: Mapping[str, Any],
    next_claim_value: Mapping[str, Any],
) -> AuditDecision:
    """Verify explicit provider substitution after a spent resource-limit no-verdict."""

    try:
        prior_contract = _mapping(prior_evidence.get("contract"), "priorEvidence.contract")
        prior_package = _mapping(prior_evidence.get("evidence"), "priorEvidence.evidence")
        prior = evaluate_audit_evidence(prior_contract, prior_package)
        if prior.disposition is not AuditDisposition.NO_VERDICT_RESOURCE_LIMIT:
            return _hold("SUBSTITUTION_PRIOR_NOT_SPENT")
        authority = _mapping(authority_value, "authority")
        next_claim = _mapping(next_claim_value, "nextClaim")
        _exact_bytes(_mapping(authority.get("artifact"), "authority.artifact"), "authority.artifact")
        if (
            authority.get("decision") != "EXPLICIT_PROVIDER_SUBSTITUTION_ONLY"
            or authority.get("priorLineageSha256") != prior.lineage_sha256
            or authority.get("priorSession") != prior.spent_session
            or authority.get("authorized") is not True
        ):
            raise EvidenceError("SUBSTITUTION_AUTHORITY", "substitution authority does not bind spent lineage")
        new_session = _nonempty(next_claim.get("consumerSession"), "nextClaim.consumerSession")
        if new_session == prior.spent_session:
            raise EvidenceError("SUBSTITUTION_AUTHORITY", "spent session cannot be retried or resumed")
        selected = _mapping(authority.get("selectedIdentity"), "authority.selectedIdentity")
        requested = _mapping(next_claim.get("requestedIdentity"), "nextClaim.requestedIdentity")
        if _identity_tuple(selected, "authority.selectedIdentity") != _identity_tuple(requested, "nextClaim.requestedIdentity"):
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
