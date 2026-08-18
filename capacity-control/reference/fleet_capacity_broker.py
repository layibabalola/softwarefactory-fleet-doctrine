#!/usr/bin/env python3
"""Provider-free reference broker for fleet inference capacity admission.

The broker is deliberately not a launcher. It consumes normalized, credential-free
request and capacity JSON, commits one idempotent decision under a SQLite write
transaction, and issues an expiring quota-domain lease. Provider adapters and
project-owned launchers remain separate authority boundaries.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import os
import pathlib
import sqlite3
import sys
import time
import uuid
from dataclasses import dataclass
from typing import Any, Sequence


UTC = dt.timezone.utc
REQUEST_SCHEMA = "fleet-capacity-admission-request/v1"
SNAPSHOT_SCHEMA = "fleet-capacity-snapshot/v1"
DECISION_SCHEMA = "fleet-capacity-admission-decision/v1"
POLICY_SCHEMA = "fleet-capacity-policy/v1"
PRIORITIES = {"OWNER_FOREGROUND", "REQUIRED_REVIEW", "PRODUCT_WORK", "BACKGROUND"}
ROLES = {"IMPLEMENT", "REVIEW", "DESIGN", "NARRATE", "COORDINATE", "PROBE"}


class BrokerError(RuntimeError):
    pass


class ConflictingReplay(BrokerError):
    pass


def now_utc() -> dt.datetime:
    return dt.datetime.now(UTC)


def parse_time(value: Any, field: str) -> dt.datetime:
    if not isinstance(value, str):
        raise BrokerError(f"{field} must be an RFC3339 timestamp")
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise BrokerError(f"{field} is not an RFC3339 timestamp") from exc
    if parsed.tzinfo is None:
        raise BrokerError(f"{field} lacks a timezone")
    return parsed.astimezone(UTC)


def iso(value: dt.datetime) -> str:
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def read_json(path: pathlib.Path) -> dict[str, Any]:
    def strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, item in pairs:
            if key in value:
                raise ValueError("duplicate JSON object key")
            value[key] = item
        return value

    try:
        value = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=strict_object,
            parse_constant=lambda _value: (_ for _ in ()).throw(ValueError("non-finite JSON number")),
        )
    except (OSError, json.JSONDecodeError, UnicodeError, ValueError) as exc:
        raise BrokerError(f"cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise BrokerError(f"{path} must contain a JSON object")
    return value


def validate_digest(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.startswith("sha256:") or len(value) != 71:
        raise BrokerError(f"{field} must be sha256:<64 lowercase hex>")
    if any(c not in "0123456789abcdef" for c in value[7:]):
        raise BrokerError(f"{field} must be sha256:<64 lowercase hex>")
    return value


def validate_domain(value: Any, provider: str | None = None) -> str:
    if not isinstance(value, str) or ":sha256:" not in value:
        raise BrokerError("quota_domain must be provider:sha256:<64 lowercase hex>")
    prefix, suffix = value.rsplit(":sha256:", 1)
    if not prefix or len(suffix) != 64 or any(c not in "0123456789abcdef" for c in suffix):
        raise BrokerError("quota_domain must be provider:sha256:<64 lowercase hex>")
    if provider is not None and prefix != provider:
        raise BrokerError("quota_domain provider prefix does not match provider")
    return value


def require_exact_keys(value: dict[str, Any], expected: set[str], field: str) -> None:
    missing = sorted(expected - value.keys())
    extra = sorted(value.keys() - expected)
    if missing or extra:
        raise BrokerError(
            f"{field} key set mismatch"
            + (f"; missing={','.join(missing)}" if missing else "")
            + (f"; extra={','.join(extra)}" if extra else "")
        )


def validate_request(request: dict[str, Any]) -> None:
    if request.get("schema") != REQUEST_SCHEMA:
        raise BrokerError("unsupported request schema")
    required = {
        "request_id", "project", "lane", "subject_digest", "role", "priority", "profile",
        "issued_at", "expires_at", "budget", "quality_contract", "owner_override",
    }
    require_exact_keys(request, required | {"schema"}, "request")
    if request["role"] not in ROLES or request["priority"] not in PRIORITIES:
        raise BrokerError("request role or priority is invalid")
    issued = parse_time(request["issued_at"], "request.issued_at")
    expires = parse_time(request["expires_at"], "request.expires_at")
    if expires <= issued:
        raise BrokerError("request expires_at must follow issued_at")
    validate_digest(request["subject_digest"], "request.subject_digest")
    profile = request.get("profile")
    if not isinstance(profile, dict):
        raise BrokerError("request.profile must be an object")
    require_exact_keys(
        profile,
        {"provider", "quota_domain", "independence_class", "requested_model", "requested_effort", "transport"},
        "request.profile",
    )
    for field in ("provider", "quota_domain", "independence_class", "requested_model", "transport"):
        if not isinstance(profile.get(field), str) or not profile[field]:
            raise BrokerError(f"request.profile.{field} is required")
    validate_domain(profile["quota_domain"], profile["provider"])
    budget = request.get("budget")
    if not isinstance(budget, dict):
        raise BrokerError("request.budget must be an object")
    require_exact_keys(budget, {"max_wall_seconds", "max_turns", "max_context_tokens", "window_estimates"}, "request.budget")
    for field in ("max_wall_seconds", "max_turns", "max_context_tokens"):
        if not isinstance(budget.get(field), int) or budget[field] <= 0:
            raise BrokerError(f"request.budget.{field} must be a positive integer")
    estimates = budget.get("window_estimates")
    if not isinstance(estimates, dict) or not estimates:
        raise BrokerError("request.budget.window_estimates must be a non-empty object")
    for name, value in estimates.items():
        if not isinstance(name, str) or not isinstance(value, (int, float)) or not math.isfinite(float(value)) or not 0 <= float(value) <= 1:
            raise BrokerError("window estimates must be named fractions in [0,1]")
    quality = request.get("quality_contract")
    if not isinstance(quality, dict) or quality.get("requires_exact_profile") is not True:
        raise BrokerError("quality contract must require the exact profile")
    require_exact_keys(quality, {"requires_exact_profile", "role_cell_evidence"}, "request.quality_contract")
    if not isinstance(quality.get("role_cell_evidence"), str) or not quality["role_cell_evidence"]:
        raise BrokerError("quality contract requires role_cell_evidence")
    if not isinstance(request["owner_override"], bool):
        raise BrokerError("owner_override must be boolean")
    if request["owner_override"] and request["priority"] != "OWNER_FOREGROUND":
        raise BrokerError("owner_override is valid only for OWNER_FOREGROUND")


def validate_snapshot(snapshot: dict[str, Any], request: dict[str, Any]) -> None:
    require_exact_keys(snapshot, {"schema", "provider", "quota_domain", "observed_at", "windows", "source"}, "snapshot")
    if snapshot.get("schema") != SNAPSHOT_SCHEMA:
        raise BrokerError("unsupported snapshot schema")
    profile = request["profile"]
    if snapshot.get("provider") != profile["provider"]:
        raise BrokerError("snapshot provider does not match request")
    if snapshot.get("quota_domain") != profile["quota_domain"]:
        raise BrokerError("snapshot quota domain does not match request")
    parse_time(snapshot.get("observed_at"), "snapshot.observed_at")
    windows = snapshot.get("windows")
    if not isinstance(windows, list) or not windows:
        raise BrokerError("snapshot.windows must be a non-empty array")
    names: set[str] = set()
    for window in windows:
        if not isinstance(window, dict) or not isinstance(window.get("name"), str):
            raise BrokerError("snapshot window has invalid shape")
        require_exact_keys(window, {"name", "used_fraction", "resets_at", "window_started_at"}, "snapshot.window")
        if window["name"] in names:
            raise BrokerError("snapshot window names must be unique")
        names.add(window["name"])
        used = window.get("used_fraction")
        if used is not None and (not isinstance(used, (int, float)) or not math.isfinite(float(used)) or not 0 <= float(used) <= 1):
            raise BrokerError("snapshot used_fraction must be null or a fraction in [0,1]")
        if window.get("resets_at") is not None:
            parse_time(window["resets_at"], "snapshot.window.resets_at")
        if window.get("window_started_at") is not None:
            parse_time(window["window_started_at"], "snapshot.window.window_started_at")
    source = snapshot.get("source")
    if not isinstance(source, dict) or not isinstance(source.get("kind"), str):
        raise BrokerError("snapshot.source is invalid")
    require_exact_keys(source, {"kind", "artifact_sha256"}, "snapshot.source")
    artifact = source.get("artifact_sha256")
    if not isinstance(artifact, str) or len(artifact) != 64 or any(c not in "0123456789abcdef" for c in artifact):
        raise BrokerError("snapshot.source.artifact_sha256 is invalid")


def validate_policy(policy: dict[str, Any]) -> None:
    required = {
        "schema", "automatic_launch_gate", "max_concurrent_leases_per_domain",
        "snapshot_max_age_seconds", "lease_max_seconds", "post_reset_quiet_seconds",
        "reserve_fraction_by_priority", "required_windows_by_provider",
    }
    require_exact_keys(policy, required, "policy")
    if policy.get("schema") != POLICY_SCHEMA:
        raise BrokerError("unsupported policy schema")
    for field in (
        "max_concurrent_leases_per_domain", "snapshot_max_age_seconds", "lease_max_seconds",
        "post_reset_quiet_seconds", "reserve_fraction_by_priority", "automatic_launch_gate",
        "required_windows_by_provider",
    ):
        if field not in policy:
            raise BrokerError(f"policy missing {field}")
    if not isinstance(policy["max_concurrent_leases_per_domain"], int) or policy["max_concurrent_leases_per_domain"] < 1:
        raise BrokerError("max_concurrent_leases_per_domain must be positive")
    if policy["automatic_launch_gate"] not in {"closed", "open"}:
        raise BrokerError("automatic_launch_gate must be closed or open")
    for field in ("snapshot_max_age_seconds", "lease_max_seconds", "post_reset_quiet_seconds"):
        if not isinstance(policy[field], int) or policy[field] < 0:
            raise BrokerError(f"{field} must be a nonnegative integer")
    if policy["snapshot_max_age_seconds"] < 1 or policy["lease_max_seconds"] < 1:
        raise BrokerError("snapshot_max_age_seconds and lease_max_seconds must be positive")
    reserves = policy["reserve_fraction_by_priority"]
    if not isinstance(reserves, dict) or set(reserves) != PRIORITIES:
        raise BrokerError("policy must define every priority reserve")
    if any(not isinstance(v, (int, float)) or not 0 <= float(v) < 1 for v in reserves.values()):
        raise BrokerError("reserve fractions must be in [0,1)")
    required_windows = policy["required_windows_by_provider"]
    if not isinstance(required_windows, dict) or not required_windows:
        raise BrokerError("required_windows_by_provider must be a non-empty object")
    for provider, names in required_windows.items():
        if not isinstance(provider, str) or not provider or not isinstance(names, list) or not names:
            raise BrokerError("every provider must define required capacity windows")
        if any(not isinstance(name, str) or not name for name in names) or len(set(names)) != len(names):
            raise BrokerError("required provider windows must be unique non-empty strings")


@dataclass(frozen=True)
class Evaluation:
    status: str
    reasons: tuple[str, ...]


def evaluate(
    request: dict[str, Any],
    snapshot: dict[str, Any],
    policy: dict[str, Any],
    active_leases: Sequence[sqlite3.Row | dict[str, Any]],
    at: dt.datetime,
) -> Evaluation:
    validate_request(request)
    validate_snapshot(snapshot, request)
    validate_policy(policy)
    reasons: list[str] = []
    if policy["automatic_launch_gate"] != "open":
        reasons.append("AUTOMATIC_LAUNCH_GATE_CLOSED")
    issued = parse_time(request["issued_at"], "request.issued_at")
    expires = parse_time(request["expires_at"], "request.expires_at")
    observed = parse_time(snapshot["observed_at"], "snapshot.observed_at")
    if issued > at + dt.timedelta(seconds=5):
        reasons.append("REQUEST_FROM_FUTURE")
    if expires <= at:
        reasons.append("REQUEST_EXPIRED")
    age = (at - observed).total_seconds()
    if age < -5:
        reasons.append("SNAPSHOT_FROM_FUTURE")
    elif age > int(policy["snapshot_max_age_seconds"]):
        reasons.append("SNAPSHOT_STALE")
    if len(active_leases) >= int(policy["max_concurrent_leases_per_domain"]):
        reasons.append("DOMAIN_CONCURRENCY_HELD")
    if int(request["budget"]["max_wall_seconds"]) > int(policy["lease_max_seconds"]):
        reasons.append("BUDGET_EXCEEDS_LEASE_MAX")

    active_estimates: dict[str, float] = {}
    for lease in active_leases:
        raw = lease["window_estimates_json"]
        estimates = json.loads(raw) if isinstance(raw, str) else raw
        for name, value in estimates.items():
            active_estimates[name] = active_estimates.get(name, 0.0) + float(value)

    requested = request["budget"]["window_estimates"]
    reserve = float(policy["reserve_fraction_by_priority"][request["priority"]])
    owner_override = bool(request["owner_override"])
    if owner_override:
        reasons.append("OWNER_OVERRIDE_UNSUPPORTED")
    windows = {window["name"]: window for window in snapshot["windows"]}
    provider = request["profile"]["provider"]
    required_names = policy["required_windows_by_provider"].get(provider)
    if required_names is None:
        reasons.append("PROVIDER_CAPACITY_POLICY_MISSING")
        required_names = []
    for name in required_names:
        if name not in requested:
            reasons.append("WINDOW_ESTIMATE_MISSING")
            continue
        estimate = requested[name]
        window = windows.get(name)
        if window is None:
            reasons.append("WINDOW_MISSING")
            continue
        used = window.get("used_fraction")
        if used is None:
            reasons.append("WINDOW_USAGE_UNKNOWN")
            continue
        projected = float(used) + active_estimates.get(name, 0.0) + float(estimate)
        if projected > 1.0:
            reasons.append("HARD_CAP_FORECAST")
        elif projected > 1.0 - reserve and not owner_override:
            reasons.append("RESERVE_FORECAST")
        started = window.get("window_started_at")
        if (
            request["priority"] == "BACKGROUND"
            and started is not None
            and (at - parse_time(started, "snapshot.window.window_started_at")).total_seconds()
            < int(policy["post_reset_quiet_seconds"])
        ):
            reasons.append("POST_RESET_QUIET")
    unique = tuple(dict.fromkeys(reasons))
    if not unique:
        status = "ADMIT"
    elif any(reason in {"REQUEST_FROM_FUTURE", "REQUEST_EXPIRED", "BUDGET_EXCEEDS_LEASE_MAX", "OWNER_OVERRIDE_UNSUPPORTED"} for reason in unique):
        status = "REFUSE"
    else:
        status = "HOLD"
    return Evaluation(status, unique or ("ALL_GATES_GREEN",))


class Broker:
    def __init__(self, state_path: pathlib.Path):
        state_path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(state_path, timeout=30, isolation_level=None)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA busy_timeout=30000")
        for attempt in range(120):
            try:
                self.db.execute("PRAGMA journal_mode=WAL")
                break
            except sqlite3.OperationalError as exc:
                if "locked" not in str(exc).lower() or attempt == 119:
                    raise
                time.sleep(0.05)
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.executescript(
            """
            CREATE TABLE IF NOT EXISTS decisions (
                request_id TEXT PRIMARY KEY,
                request_digest TEXT NOT NULL,
                decision_json TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS leases (
                lease_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                quota_domain TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                window_estimates_json TEXT NOT NULL,
                state TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS leases_domain_state ON leases(quota_domain, state);
            CREATE TABLE IF NOT EXISTS events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                event_kind TEXT NOT NULL,
                request_id TEXT,
                payload_digest TEXT NOT NULL,
                payload_json TEXT NOT NULL
            );
            """
        )

    def close(self) -> None:
        self.db.close()

    def _begin(self) -> None:
        self.db.execute("BEGIN IMMEDIATE")

    def _commit(self) -> None:
        self.db.execute("COMMIT")

    def _rollback(self) -> None:
        self.db.execute("ROLLBACK")

    def decide(
        self,
        request: dict[str, Any],
        snapshot: dict[str, Any],
        policy: dict[str, Any],
        at: dt.datetime | None = None,
    ) -> dict[str, Any]:
        at = at or now_utc()
        validate_request(request)
        validate_snapshot(snapshot, request)
        validate_policy(policy)
        request_digest = digest(request)
        snapshot_digest = digest(snapshot)
        policy_digest = digest(policy)
        self._begin()
        try:
            prior = self.db.execute(
                "SELECT request_digest, decision_json FROM decisions WHERE request_id=?",
                (request["request_id"],),
            ).fetchone()
            self.db.execute(
                "UPDATE leases SET state='EXPIRED' WHERE state='ACTIVE' AND expires_at<=?",
                (iso(at),),
            )
            if prior is not None:
                if prior["request_digest"] != request_digest:
                    raise ConflictingReplay("request_id was reused with different bytes")
                decision = json.loads(prior["decision_json"])
                prior_lease = decision.get("lease")
                if prior_lease is not None:
                    state = self.db.execute(
                        "SELECT state FROM leases WHERE lease_id=? AND request_id=?",
                        (prior_lease["lease_id"], request["request_id"]),
                    ).fetchone()
                    if state is None or state["state"] != "ACTIVE":
                        decision = {
                            "schema": DECISION_SCHEMA,
                            "status": "REFUSE",
                            "reason_codes": ["TERMINAL_REQUEST_REPLAY"],
                            "request_id": request["request_id"],
                            "request_digest": request_digest,
                            "snapshot_digest": snapshot_digest,
                            "policy_digest": policy_digest,
                            "decided_at": iso(at),
                            "lease": None,
                        }
                self._commit()
                return decision
            domain = request["profile"]["quota_domain"]
            active = list(
                self.db.execute(
                    "SELECT * FROM leases WHERE quota_domain=? AND state='ACTIVE' ORDER BY expires_at",
                    (domain,),
                )
            )
            evaluation = evaluate(request, snapshot, policy, active, at)
            lease = None
            if evaluation.status == "ADMIT":
                requested_expiry = parse_time(request["expires_at"], "request.expires_at")
                lease_expiry = min(
                    at + dt.timedelta(seconds=int(request["budget"]["max_wall_seconds"])),
                    requested_expiry,
                )
                lease_id = str(uuid.uuid4())
                lease = {
                    "lease_id": lease_id,
                    "quota_domain": domain,
                    "issued_at": iso(at),
                    "expires_at": iso(lease_expiry),
                    "budget": request["budget"],
                }
                self.db.execute(
                    "INSERT INTO leases VALUES (?, ?, ?, ?, ?, 'ACTIVE')",
                    (
                        lease_id,
                        request["request_id"],
                        domain,
                        lease["expires_at"],
                        canonical_json(request["budget"]["window_estimates"]),
                    ),
                )
            decision = {
                "schema": DECISION_SCHEMA,
                "status": evaluation.status,
                "reason_codes": list(evaluation.reasons),
                "request_id": request["request_id"],
                "request_digest": request_digest,
                "snapshot_digest": snapshot_digest,
                "policy_digest": policy_digest,
                "decided_at": iso(at),
                "lease": lease,
            }
            encoded = canonical_json(decision)
            self.db.execute(
                "INSERT INTO decisions VALUES (?, ?, ?)",
                (request["request_id"], request_digest, encoded),
            )
            self.db.execute(
                "INSERT INTO events(ts,event_kind,request_id,payload_digest,payload_json) VALUES(?,?,?,?,?)",
                (iso(at), "ADMISSION_DECISION", request["request_id"], digest(decision), encoded),
            )
            self._commit()
            return decision
        except BaseException:
            self._rollback()
            raise

    def release(
        self,
        lease_id: str,
        request_id: str,
        terminal_class: str,
        evidence_digest: str | None = None,
        at: dt.datetime | None = None,
    ) -> bool:
        at = at or now_utc()
        if not isinstance(terminal_class, str) or not terminal_class or not terminal_class.replace("_", "").isalnum():
            raise BrokerError("terminal_class must be a non-empty identifier")
        if evidence_digest is not None:
            validate_digest(evidence_digest, "evidence_digest")
        self._begin()
        try:
            row = self.db.execute(
                "SELECT state FROM leases WHERE lease_id=? AND request_id=?",
                (lease_id, request_id),
            ).fetchone()
            changed = row is not None and row["state"] == "ACTIVE"
            if changed:
                self.db.execute("UPDATE leases SET state='RELEASED' WHERE lease_id=?", (lease_id,))
                payload = {
                    "lease_id": lease_id,
                    "request_id": request_id,
                    "released_at": iso(at),
                    "terminal_class": terminal_class,
                    "evidence_digest": evidence_digest,
                }
                self.db.execute(
                    "INSERT INTO events(ts,event_kind,request_id,payload_digest,payload_json) VALUES(?,?,?,?,?)",
                    (iso(at), "LEASE_RELEASED", request_id, digest(payload), canonical_json(payload)),
                )
            self._commit()
            return changed
        except BaseException:
            self._rollback()
            raise


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    decide_parser = sub.add_parser("decide")
    decide_parser.add_argument("--request", type=pathlib.Path, required=True)
    decide_parser.add_argument("--snapshot", type=pathlib.Path, required=True)
    decide_parser.add_argument("--policy", type=pathlib.Path, required=True)
    decide_parser.add_argument("--state", type=pathlib.Path, required=True)
    decide_parser.add_argument("--now")
    release_parser = sub.add_parser("release")
    release_parser.add_argument("--lease-id", required=True)
    release_parser.add_argument("--request-id", required=True)
    release_parser.add_argument("--terminal-class", required=True)
    release_parser.add_argument("--evidence-digest")
    release_parser.add_argument("--state", type=pathlib.Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    broker = Broker(args.state)
    try:
        if args.command == "decide":
            at = parse_time(args.now, "--now") if args.now else now_utc()
            decision = broker.decide(read_json(args.request), read_json(args.snapshot), read_json(args.policy), at)
            print(json.dumps(decision, indent=2, sort_keys=True))
            return 0 if decision["status"] == "ADMIT" else 23
        changed = broker.release(
            args.lease_id,
            args.request_id,
            args.terminal_class,
            args.evidence_digest,
        )
        print(canonical_json({"released": changed, "lease_id": args.lease_id}))
        return 0 if changed else 24
    except ConflictingReplay as exc:
        print(canonical_json({"error": "CONFLICTING_REPLAY", "detail": str(exc)}), file=sys.stderr)
        return 25
    except BrokerError as exc:
        print(canonical_json({"error": "UNEVALUABLE", "detail": str(exc)}), file=sys.stderr)
        return 22
    finally:
        broker.close()


if __name__ == "__main__":
    raise SystemExit(main())
