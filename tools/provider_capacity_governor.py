#!/usr/bin/env python3
"""Provider-neutral fleet capacity admission and telemetry conformance tool.

This reference implementation is deliberately read-only. It emits a decision from a frozen
snapshot and validates publishable usage events. It does not acquire leases, launch providers, or
mutate project state.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

try:
    import jsonschema
except ImportError:  # pragma: no cover - exercised by deployment environments, not this test env
    jsonschema = None


QUOTA_DOMAIN_RE = re.compile(
    r"^(?P<provider>[a-z0-9-]+)/(?:opaque:|hmac-sha256:)[a-f0-9]{16,64}$"
)
HASH_RE = re.compile(r"^[a-f0-9]{64}$")
RFC3339_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$")
EMAIL_RE = re.compile(r"(?i)(?<![A-Z0-9._%+-])[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}(?![A-Z0-9.-])")
SAFE_PATH_COMPONENT_RE = re.compile(r"^[A-Za-z0-9._-]+$")
EVENTS = {
    "ADMISSION_REQUESTED",
    "ADMISSION_ADMITTED",
    "ADMISSION_DENIED",
    "PROCESS_STARTED",
    "USAGE_OBSERVED",
    "CHECKPOINTED",
    "TERMINAL",
    "CAPACITY_BLOCKED",
    "RESET_OBSERVED",
    "IDLE_SKIPPED",
    "UNPARSEABLE",
}
PROHIBITED_KEYS = {
    "account_id",
    "account_email",
    "account_identifier",
    "account_alias",
    "organization_id",
    "org_id",
    "tenant_id",
    "subscription_id",
    "user_id",
    "username",
    "email",
    "api_key",
    "access_token",
    "refresh_token",
    "raw_prompt",
    "transcript",
    "command_line",
}
TOKEN_FIELDS = {
    "request_count",
    "input_tokens",
    "cached_input_tokens",
    "cache_write_tokens",
    "reasoning_tokens",
    "output_tokens",
    "tool_calls",
    "active_seconds",
    "context_tokens",
}
SCHEMA_ROOT = Path(__file__).resolve().parents[1] / "schemas"


class ContractError(ValueError):
    pass


def _parse_utc(value: Any, field: str) -> datetime:
    if not isinstance(value, str):
        raise ContractError(f"{field}: expected RFC3339 string")
    if not RFC3339_RE.fullmatch(value):
        raise ContractError(f"{field}: invalid RFC3339 timestamp")
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ContractError(f"{field}: invalid RFC3339 timestamp") from exc
    if parsed.tzinfo is None:
        raise ContractError(f"{field}: timezone is required")
    return parsed.astimezone(timezone.utc)


def _canonical_hash(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _canonical_session_id(value: Any) -> str | None:
    if value is None:
        return None
    return value.removeprefix("sha256:")


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, child in pairs:
        if key in value:
            raise ContractError(f"duplicate JSON key prohibited: {key!r}")
        value[key] = child
    return value


def _reject_nonfinite_json(value: str) -> None:
    raise ContractError(f"non-finite JSON number prohibited: {value}")


def _strict_json_loads(raw: str, source: str) -> Any:
    try:
        return json.loads(
            raw,
            object_pairs_hook=_strict_object,
            parse_constant=_reject_nonfinite_json,
        )
    except json.JSONDecodeError as exc:
        raise ContractError(f"{source}: invalid JSON: {exc.msg}") from exc


def _decode_utf8(raw: bytes, source: str) -> str:
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ContractError(f"{source}: invalid UTF-8") from exc


@lru_cache(maxsize=2)
def _schema_validator(schema_name: str) -> Any:
    if jsonschema is None:
        raise ContractError("jsonschema dependency unavailable; conformance fails closed")
    schema_path = SCHEMA_ROOT / schema_name
    try:
        raw = schema_path.read_bytes()
        schema = _strict_json_loads(_decode_utf8(raw, str(schema_path)), str(schema_path))
        jsonschema.Draft202012Validator.check_schema(schema)
    except (OSError, ContractError, jsonschema.SchemaError) as exc:
        raise ContractError(f"{schema_name}: schema unavailable or invalid: {exc}") from exc
    return jsonschema.Draft202012Validator(
        schema,
        format_checker=jsonschema.FormatChecker(),
    )


def _validate_schema(value: Any, schema_name: str) -> None:
    validator = _schema_validator(schema_name)
    errors = sorted(validator.iter_errors(value), key=lambda error: list(error.absolute_path))
    if not errors:
        return
    error = errors[0]
    location = "$"
    for component in error.absolute_path:
        location += f"[{component}]" if isinstance(component, int) else f".{component}"
    raise ContractError(f"{location}: schema violation: {error.message}")


def _walk_keys(value: Any, path: str = "$") -> Iterable[tuple[str, str]]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield path, key
            yield from _walk_keys(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk_keys(child, f"{path}[{index}]")


def _walk_strings(value: Any, path: str = "$") -> Iterable[tuple[str, str]]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield from _walk_strings(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk_strings(child, f"{path}[{index}]")
    elif isinstance(value, str):
        yield path, value


def _validate_opaque_event(event: dict[str, Any]) -> None:
    leaked = [(path, key) for path, key in _walk_keys(event) if key.lower() in PROHIBITED_KEYS]
    if leaked:
        path, key = leaked[0]
        raise ContractError(f"{path}.{key}: raw identity, credential, prompt, or transcript data prohibited")


def _validate_project_local_path(value: Any, field: str) -> None:
    if value is None:
        return
    if not isinstance(value, str) or not value:
        raise ContractError(f"{field}: non-empty project-relative path required")
    if value.startswith(("/", "\\", "~")) or "\\" in value or re.match(r"^[A-Za-z]:", value):
        raise ContractError(f"{field}: absolute, UNC, home, and Windows paths prohibited")
    components = value.split("/")
    if any(component in {"", ".", ".."} or not SAFE_PATH_COMPONENT_RE.fullmatch(component) for component in components):
        raise ContractError(f"{field}: normalized project-relative path required")
    lowered = [component.lower() for component in components]
    if lowered[0] in {"home", "root", "users"} or (
        len(lowered) >= 3 and lowered[0] == "mnt" and lowered[2] == "users"
    ):
        raise ContractError(f"{field}: user-profile paths prohibited")


def _validate_publishable_event_values(event: dict[str, Any]) -> None:
    for path, value in _walk_strings(event):
        if EMAIL_RE.search(value):
            raise ContractError(f"{path}: email-like publishable value prohibited")
        normalized = value.replace("\\", "/")
        lowered = normalized.lower().split("/")
        if (
            normalized.startswith(("/", "~"))
            or "//" in normalized
            or any(re.fullmatch(r"[a-z]:", component) for component in lowered)
            or any(
                re.fullmatch(r"[a-z]:(?:users|documents and settings)", component)
                for component in lowered
            )
            or any(
                lowered[index] in {"home", "users"} and index + 1 < len(lowered)
                for index in range(len(lowered))
            )
            or "root" in lowered
            or any(
                lowered[index] == "mnt"
                and index + 2 < len(lowered)
                and re.fullmatch(r"[a-z]", lowered[index + 1])
                and lowered[index + 2] == "users"
                for index in range(len(lowered))
            )
        ):
            raise ContractError(f"{path}: absolute or user-profile publishable value prohibited")
    for index, ref in enumerate(event.get("refs", [])):
        if isinstance(ref, dict):
            _validate_project_local_path(
                ref.get("project_local_path"),
                f"refs[{index}].project_local_path",
            )


def validate_usage_event(event: Any) -> None:
    if not isinstance(event, dict):
        raise ContractError("event: expected object")
    _validate_opaque_event(event)
    _validate_publishable_event_values(event)
    _validate_schema(event, "provider-usage-event-v1.schema.json")
    required = {
        "schema_version",
        "event_id",
        "ts",
        "project",
        "host_cell",
        "quota_domain_id",
        "provider",
        "transport",
        "actor",
        "event",
        "measurement",
    }
    missing = sorted(required - event.keys())
    if missing:
        raise ContractError(f"event: missing required fields: {', '.join(missing)}")
    if event["schema_version"] != 1:
        raise ContractError("schema_version: expected 1")
    _parse_utc(event["ts"], "ts")
    match = QUOTA_DOMAIN_RE.fullmatch(str(event["quota_domain_id"]))
    if not match:
        raise ContractError("quota_domain_id: expected provider/opaque-or-hmac identifier")
    if event["provider"] != match.group("provider"):
        raise ContractError("provider: must equal quota_domain_id provider prefix")
    if event["event"] not in EVENTS:
        raise ContractError(f"event: unsupported value {event['event']!r}")
    actor = event["actor"]
    if not isinstance(actor, dict) or not actor.get("lane") or not actor.get("role"):
        raise ContractError("actor: lane and role are required")
    measurement = event["measurement"]
    if not isinstance(measurement, dict):
        raise ContractError("measurement: expected object")
    if measurement.get("reset_at") not in (None, "unknown"):
        _parse_utc(measurement["reset_at"], "measurement.reset_at")
    if measurement.get("quality") not in {"exact", "estimated", "mixed", "unknown"}:
        raise ContractError("measurement.quality: unsupported value")
    if not isinstance(measurement.get("source"), str) or not measurement["source"]:
        raise ContractError("measurement.source: non-empty string required")
    for field in TOKEN_FIELDS:
        value = measurement.get(field)
        if value is None:
            continue
        if value != "unknown" and (not isinstance(value, int) or isinstance(value, bool) or value < 0):
            raise ContractError(f"measurement.{field}: expected non-negative integer or 'unknown'")
    input_tokens = measurement.get("input_tokens")
    cached_tokens = measurement.get("cached_input_tokens")
    if isinstance(input_tokens, int) and isinstance(cached_tokens, int) and cached_tokens > input_tokens:
        raise ContractError("measurement.cached_input_tokens: cannot exceed input_tokens")
    utilization = measurement.get("window_utilization_pct")
    if utilization != "unknown" and utilization is not None:
        if not isinstance(utilization, (int, float)) or isinstance(utilization, bool) or not 0 <= utilization <= 100:
            raise ContractError("measurement.window_utilization_pct: expected 0..100 or 'unknown'")
    if event["event"] == "TERMINAL" and not event.get("outcome"):
        raise ContractError("outcome: TERMINAL requires an explicit non-green-or-green outcome")
    if event["event"] == "USAGE_OBSERVED" and not any(field in measurement for field in TOKEN_FIELDS):
        raise ContractError("measurement: USAGE_OBSERVED requires at least one usage field")
    if event["event"] == "IDLE_SKIPPED":
        zero_fields = {
            "request_count",
            "input_tokens",
            "cached_input_tokens",
            "cache_write_tokens",
            "reasoning_tokens",
            "output_tokens",
            "tool_calls",
        }
        nonzero = sorted(field for field in zero_fields if measurement.get(field) != 0)
        if nonzero:
            raise ContractError(
                "measurement: IDLE_SKIPPED requires explicit zero counters: "
                + ", ".join(nonzero)
            )
    for field in ("task_id_hash", "session_id_hash"):
        value = event.get(field)
        if value is not None:
            raw = value.removeprefix("sha256:") if isinstance(value, str) else ""
            if not HASH_RE.fullmatch(raw):
                raise ContractError(f"{field}: expected SHA-256 digest")


def validate_usage_file(path: Path) -> dict[str, Any]:
    count = 0
    event_ids: set[str] = set()
    errors: list[str] = []
    with path.open("rb") as handle:
        for line_number, raw in enumerate(handle, 1):
            if not raw.strip():
                continue
            try:
                decoded = _decode_utf8(raw, f"line {line_number}")
                event = _strict_json_loads(decoded, f"line {line_number}")
                validate_usage_event(event)
                event_id = event["event_id"]
                if event_id in event_ids:
                    raise ContractError(f"event_id: duplicate {event_id!r}")
                event_ids.add(event_id)
                count += 1
            except ContractError as exc:
                errors.append(f"line {line_number}: {exc}")
    return {"valid": not errors, "event_count": count, "errors": errors}


def _validate_claimant_rows(active_leases: list[dict[str, Any]]) -> None:
    seen_lease_ids: dict[str, int] = {}
    seen_processes: dict[tuple[int, datetime], int] = {}
    seen_sessions: dict[str, int] = {}
    seen_seat_epochs: dict[tuple[str, int], int] = {}

    def claim(seen: dict[Any, int], identity: Any, index: int, field: str) -> None:
        previous = seen.get(identity)
        if previous is not None:
            raise ContractError(
                f"active_leases[{index}].{field}: claimant identity duplicates active_leases[{previous}]"
            )
        seen[identity] = index

    for index, lease in enumerate(active_leases):
        claim(seen_lease_ids, lease["lease_id"], index, "lease_id")
        claim(
            seen_processes,
            (
                lease["process_id"],
                _parse_utc(
                    lease["process_start_time"],
                    f"active_leases[{index}].process_start_time",
                ),
            ),
            index,
            "process_id/process_start_time",
        )
        claim(
            seen_seat_epochs,
            (lease["seat_id"].casefold(), lease["seat_epoch"]),
            index,
            "seat_id/seat_epoch",
        )
        row_sessions = {
            _canonical_session_id(session)
            for session in (
                lease.get("registered_session_id_hash"),
                lease.get("observed_session_id_hash"),
            )
            if session is not None
        }
        for session in row_sessions:
            claim(
                seen_sessions,
                session,
                index,
                "session_id_hash",
            )


def decide(snapshot: Any) -> dict[str, Any]:
    if not isinstance(snapshot, dict):
        raise ContractError("snapshot: expected object")
    _validate_schema(snapshot, "provider-admission-snapshot-v1.schema.json")
    for field in ("schema_version", "observed_at", "policy", "request", "capacity", "active_leases"):
        if field not in snapshot:
            raise ContractError(f"snapshot: missing {field}")
    if snapshot["schema_version"] != 1:
        raise ContractError("schema_version: expected 1")
    observed_at = _parse_utc(snapshot["observed_at"], "observed_at")
    policy = snapshot["policy"]
    request = snapshot["request"]
    capacity = snapshot["capacity"]
    active_leases = snapshot["active_leases"]
    if not all(isinstance(item, dict) for item in (policy, request, capacity)):
        raise ContractError("policy, request, and capacity must be objects")
    if not isinstance(active_leases, list):
        raise ContractError("active_leases: expected array")
    _validate_claimant_rows(active_leases)
    quota_domain_id = request.get("quota_domain_id")
    match = QUOTA_DOMAIN_RE.fullmatch(str(quota_domain_id))
    if not match:
        raise ContractError("request.quota_domain_id: invalid opaque quota domain")
    if request.get("provider") != match.group("provider"):
        raise ContractError("request.provider: must equal quota-domain provider prefix")
    if capacity.get("quota_domain_id") != quota_domain_id:
        raise ContractError("capacity.quota_domain_id: must equal request quota domain")
    capacity_observed_at = _parse_utc(capacity.get("observed_at"), "capacity.observed_at")
    if capacity.get("reset_at") != "unknown":
        _parse_utc(capacity.get("reset_at"), "capacity.reset_at")
    owner_override = request.get("owner_override") is True
    reasons: list[str] = []
    warnings: list[str] = []
    if request.get("actionable_work") is not True:
        reasons.append("NO_ACTIONABLE_WORK")
    if request.get("requires_exact_profile") is True and request.get("profile_available") is not True:
        reasons.append("EXACT_PROFILE_UNAVAILABLE")
    slice_minutes = request.get("slice_minutes")
    max_turns = request.get("max_agent_turns")
    if not isinstance(slice_minutes, int) or slice_minutes < 1:
        raise ContractError("request.slice_minutes: positive integer required")
    if not isinstance(max_turns, int) or max_turns < 1:
        raise ContractError("request.max_agent_turns: positive integer required")
    if slice_minutes > policy.get("max_slice_minutes", 0):
        reasons.append("SLICE_LIMIT_EXCEEDED")
    if max_turns > policy.get("max_agent_turns", 0):
        reasons.append("TURN_LIMIT_EXCEEDED")
    status = capacity.get("status")
    if status not in {"available", "exhausted", "unknown"}:
        raise ContractError("capacity.status: expected available, exhausted, or unknown")
    if status == "exhausted":
        reasons.append("CAPACITY_EXHAUSTED")
    is_background = request.get("foreground") is not True
    if (
        is_background
        and request.get("actionable_work") is True
        and request.get("prior_idle_input_fingerprint") == request.get("idle_input_fingerprint")
    ):
        reasons.append("UNCHANGED_IDLE_INPUT")
    automatic_gate = policy.get("automatic_launch_gate")
    if automatic_gate not in {"closed", "open"}:
        raise ContractError("policy.automatic_launch_gate: expected closed or open")
    if is_background and automatic_gate == "closed":
        reasons.append("AUTOMATIC_GATE_CLOSED")
    max_capacity_age = policy.get("capacity_observation_max_age_seconds")
    if capacity_observed_at > observed_at:
        reasons.append("CAPACITY_OBSERVATION_FROM_FUTURE")
    elif observed_at - capacity_observed_at > timedelta(seconds=max_capacity_age):
        reasons.append("CAPACITY_OBSERVATION_STALE")
    if (
        status == "unknown"
        and is_background
        and not owner_override
        and policy.get("deny_background_when_capacity_unknown")
    ):
        reasons.append("CAPACITY_UNKNOWN")
    elif status == "unknown" and owner_override:
        warnings.append("OWNER_OVERRIDE_CAPACITY_UNKNOWN")
    live_count = 0
    for index, lease in enumerate(active_leases):
        expires_at = _parse_utc(lease.get("expires_at"), f"active_leases[{index}].expires_at")
        process_start_time = _parse_utc(
            lease.get("process_start_time"),
            f"active_leases[{index}].process_start_time",
        )
        startup_fence_expires_at = _parse_utc(
            lease.get("startup_fence_expires_at"),
            f"active_leases[{index}].startup_fence_expires_at",
        )
        cooldown_expires_at = _parse_utc(
            lease.get("cooldown_expires_at"),
            f"active_leases[{index}].cooldown_expires_at",
        )
        if not (
            process_start_time < startup_fence_expires_at < expires_at
            and process_start_time < cooldown_expires_at < expires_at
        ):
            raise ContractError(
                f"active_leases[{index}]: claimant timeline must satisfy "
                "process_start_time < each fence expiry < expires_at"
            )
        if lease.get("quota_domain_id") != quota_domain_id:
            continue
        fence_active = False
        if cooldown_expires_at > observed_at:
            reasons.append("COOLDOWN_ACTIVE")
            fence_active = True
        if lease.get("state") == "STARTING" and startup_fence_expires_at > observed_at:
            reasons.append("STARTUP_FENCE_ACTIVE")
            fence_active = True
        if fence_active:
            continue
        process_status = lease.get("process_status")
        if process_status == "dead":
            continue
        if process_status == "ambiguous":
            reasons.append("IDENTITY_AMBIGUOUS")
            continue
        if process_start_time > observed_at or expires_at <= process_start_time:
            reasons.append("IDENTITY_AMBIGUOUS")
            continue
        if expires_at <= observed_at:
            reasons.append("LIVE_PROCESS_STALE_LEASE")
            continue
        if lease.get("state") == "STARTING":
            live_count += 1
            continue
        registered_session_id = _canonical_session_id(lease.get("registered_session_id_hash"))
        observed_session_id = _canonical_session_id(lease.get("observed_session_id_hash"))
        identity_agrees = (
            lease.get("provider_requested") == lease.get("provider_observed")
            and lease.get("model_requested") == lease.get("model_observed")
            and registered_session_id is not None
            and registered_session_id == observed_session_id
            and lease.get("registry_status") == "verified"
            and lease.get("progress_status") in {"fresh", "unavailable"}
        )
        if not identity_agrees:
            reasons.append("IDENTITY_AMBIGUOUS")
            continue
        live_count += 1
    max_concurrency = policy.get("max_automatic_concurrency")
    if not isinstance(max_concurrency, int) or max_concurrency < 1:
        raise ContractError("policy.max_automatic_concurrency: positive integer required")
    if live_count >= max_concurrency:
        reasons.append("CONCURRENCY_LIMIT")
    reserve = policy.get("interactive_reserve_pct")
    reserved = capacity.get("reserved_pct")
    estimate = request.get("estimated_window_pct")
    utilization = capacity.get("utilization_pct")
    for name, value in (("interactive_reserve_pct", reserve), ("reserved_pct", reserved)):
        if not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 <= value <= 100:
            raise ContractError(f"{name}: expected 0..100")
    if status == "available":
        if estimate == "unknown" or utilization == "unknown":
            if is_background and not owner_override:
                reasons.append("CAPACITY_ESTIMATE_UNKNOWN")
            elif owner_override:
                warnings.append("OWNER_OVERRIDE_ESTIMATE_UNKNOWN")
        else:
            if not all(isinstance(value, (int, float)) and not isinstance(value, bool) for value in (estimate, utilization)):
                raise ContractError("capacity utilization and request estimate must be numeric or 'unknown'")
            if utilization + reserved + estimate > 100 - reserve:
                if owner_override:
                    warnings.append("OWNER_OVERRIDE_RESERVE")
                else:
                    reasons.append("COMPLETION_RESERVE")
    decision = "DENY" if reasons else "ADMIT"
    decision_hash = _canonical_hash(snapshot)
    result: dict[str, Any] = {
        "schema_version": 1,
        "decision_id": f"sha256:{decision_hash}",
        "request_id": request.get("request_id"),
        "quota_domain_id": quota_domain_id,
        "decision": decision,
        "reason_codes": sorted(set(reasons)),
        "warnings": sorted(set(warnings)),
        "observed_at": observed_at.isoformat().replace("+00:00", "Z"),
        "snapshot_sha256": decision_hash,
    }
    if decision == "ADMIT":
        expires_at = observed_at + timedelta(minutes=slice_minutes)
        result["lease_offer"] = {
            "expires_at": expires_at.isoformat().replace("+00:00", "Z"),
            "max_slice_minutes": slice_minutes,
            "max_agent_turns": max_turns,
        }
    return result


def _load_json(path: Path) -> Any:
    raw = path.read_bytes()
    return _strict_json_loads(_decode_utf8(raw, str(path)), str(path))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate_parser = subparsers.add_parser("validate-events", help="validate a provider usage JSONL shard")
    validate_parser.add_argument("path", type=Path)
    decide_parser = subparsers.add_parser("decide", help="evaluate one frozen admission snapshot")
    decide_parser.add_argument("path", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "validate-events":
            result = validate_usage_file(args.path)
            print(json.dumps(result, indent=2, sort_keys=True))
            return 0 if result["valid"] else 2
        result = decide(_load_json(args.path))
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["decision"] == "ADMIT" else 3
    except (OSError, ContractError) as exc:
        print(json.dumps({"valid": False, "errors": [str(exc)]}, indent=2, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
