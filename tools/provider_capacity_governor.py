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
from pathlib import Path
from typing import Any, Iterable


QUOTA_DOMAIN_RE = re.compile(
    r"^(?P<provider>[a-z0-9-]+)/(?:opaque:|hmac-sha256:)[a-f0-9]{16,64}$"
)
HASH_RE = re.compile(r"^[a-f0-9]{64}$")
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
    "active_seconds",
    "context_tokens",
}


class ContractError(ValueError):
    pass


def _parse_utc(value: Any, field: str) -> datetime:
    if not isinstance(value, str):
        raise ContractError(f"{field}: expected RFC3339 string")
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


def _walk_keys(value: Any, path: str = "$") -> Iterable[tuple[str, str]]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield path, key
            yield from _walk_keys(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk_keys(child, f"{path}[{index}]")


def _validate_opaque_event(event: dict[str, Any]) -> None:
    leaked = [(path, key) for path, key in _walk_keys(event) if key.lower() in PROHIBITED_KEYS]
    if leaked:
        path, key = leaked[0]
        raise ContractError(f"{path}.{key}: raw identity, credential, prompt, or transcript data prohibited")


def validate_usage_event(event: Any) -> None:
    if not isinstance(event, dict):
        raise ContractError("event: expected object")
    _validate_opaque_event(event)
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
    if event["event"] == "IDLE_SKIPPED" and measurement.get("request_count") not in (None, 0):
        raise ContractError("measurement.request_count: IDLE_SKIPPED must consume zero model requests")
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
    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw in enumerate(handle, 1):
            if not raw.strip():
                continue
            try:
                event = json.loads(raw)
                validate_usage_event(event)
                event_id = event["event_id"]
                if event_id in event_ids:
                    raise ContractError(f"event_id: duplicate {event_id!r}")
                event_ids.add(event_id)
                count += 1
            except (json.JSONDecodeError, ContractError) as exc:
                errors.append(f"line {line_number}: {exc}")
    return {"valid": not errors, "event_count": count, "errors": errors}


def decide(snapshot: Any) -> dict[str, Any]:
    if not isinstance(snapshot, dict):
        raise ContractError("snapshot: expected object")
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
    quota_domain_id = request.get("quota_domain_id")
    match = QUOTA_DOMAIN_RE.fullmatch(str(quota_domain_id))
    if not match:
        raise ContractError("request.quota_domain_id: invalid opaque quota domain")
    if request.get("provider") != match.group("provider"):
        raise ContractError("request.provider: must equal quota-domain provider prefix")
    if capacity.get("quota_domain_id") != quota_domain_id:
        raise ContractError("capacity.quota_domain_id: must equal request quota domain")
    _parse_utc(capacity.get("observed_at"), "capacity.observed_at")
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
        if lease.get("quota_domain_id") != quota_domain_id:
            continue
        expires_at = _parse_utc(lease.get("expires_at"), f"active_leases[{index}].expires_at")
        if expires_at > observed_at and lease.get("state") in {"STARTING", "CLAIMED", "RUNNING", "CHECKPOINTED"}:
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
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


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
    except (OSError, json.JSONDecodeError, ContractError) as exc:
        print(json.dumps({"valid": False, "errors": [str(exc)]}, indent=2, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
