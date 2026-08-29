#!/usr/bin/env python3
"""Validate the proposed delivery-first lane status contract."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from typing import Any

SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")
GIT_OID = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
OWNER = re.compile(r"^(thread|owner):[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
MAX_DOCUMENT_BYTES = 16 * 1024 * 1024
ACTIONS = {"LAND_ACCEPTED", "CLOSE_GATE", "DELIVER_MILESTONE"}
LANE_ACTIONS = {
    "EXECUTE_DELIVERABLE", "ESCALATE_STALLED_QUEUE", "HOLD_NO_EXECUTABLE_DELIVERABLE",
    "EXPAND_LANE",
}
ROTATION_REASONS = {"NONE", "SAFETY_CONTINUITY_ONLY", "EXECUTABLE_HANDOFF"}


class DeliveryFirstError(ValueError):
    pass


def _pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    folded: set[str] = set()
    for key, value in items:
        if not isinstance(key, str) or key.casefold() in folded:
            raise DeliveryFirstError("DUPLICATE_OR_CASE_COLLIDING_KEY")
        folded.add(key.casefold())
        out[key] = value
    return out


def load_json(path: Path) -> dict[str, Any]:
    try:
        raw = path.read_bytes()
        if len(raw) > MAX_DOCUMENT_BYTES:
            raise DeliveryFirstError("JSON_DOCUMENT_TOO_LARGE")
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise DeliveryFirstError("JSON_INVALID") from exc
    if type(value) is not dict:
        raise DeliveryFirstError("JSON_ROOT_INVALID")
    return value


def _exact(value: Any, keys: set[str], code: str) -> dict[str, Any]:
    if type(value) is not dict or set(value) != keys:
        raise DeliveryFirstError(code)
    return value


def _utc(value: Any, code: str) -> datetime:
    if type(value) is not str or not value.endswith("Z"):
        raise DeliveryFirstError(code)
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise DeliveryFirstError(code) from exc
    if parsed.tzinfo != timezone.utc:
        raise DeliveryFirstError(code)
    return parsed


def _nonnegative_int(value: Any, code: str) -> int:
    if type(value) is not int or value < 0:
        raise DeliveryFirstError(code)
    return value


def _evidence_rows(value: Any, id_key: str, code: str) -> list[dict[str, Any]]:
    if type(value) is not list:
        raise DeliveryFirstError(code)
    rows: list[dict[str, Any]] = []
    identities: set[str] = set()
    keys = {id_key, "evidenceSha256"}
    if id_key == "commitSha":
        keys.add("targetRef")
    if id_key == "milestoneId":
        keys.add("declarationSha256")
    for raw in value:
        row = _exact(raw, keys, code)
        identity = row[id_key]
        if type(identity) is not str or not identity:
            raise DeliveryFirstError(code)
        if id_key == "commitSha" and not GIT_OID.fullmatch(identity):
            raise DeliveryFirstError(code)
        if id_key == "commitSha":
            target = row["targetRef"]
            if type(target) is not str or not re.fullmatch(r"refs/heads/[A-Za-z0-9._/-]+", target) or ".." in target:
                raise DeliveryFirstError(code)
            identity = f"{identity}\0{target}"
        if type(row["evidenceSha256"]) is not str or not SHA256.fullmatch(row["evidenceSha256"]):
            raise DeliveryFirstError(code)
        if id_key == "milestoneId" and (
            type(row["declarationSha256"]) is not str or not SHA256.fullmatch(row["declarationSha256"])
        ):
            raise DeliveryFirstError(code)
        if identity in identities:
            raise DeliveryFirstError(f"{code}_DUPLICATE")
        identities.add(identity)
        rows.append(row)
    return rows


def verify(
    doc: dict[str, Any],
    previous: dict[str, Any] | None = None,
    *,
    _history_shape_only: bool = False,
) -> None:
    _exact(doc, {
        "schema", "laneId", "observedAtUtc", "queue", "outcomes", "acceptedUnlanded",
        "nextExecutableDeliverable", "primaryBlocker", "laneAction", "rotation",
        "evidenceAuthoring", "stalledEscalation", "progressCredit",
    }, "ROOT_SHAPE_INVALID")
    if doc["schema"] != "fleet-delivery-first-lane-status/v1":
        raise DeliveryFirstError("SCHEMA_INVALID")
    if type(doc["laneId"]) is not str or not re.fullmatch(r"[a-z][a-z0-9-]{1,62}", doc["laneId"]):
        raise DeliveryFirstError("LANE_ID_INVALID")
    observed = _utc(doc["observedAtUtc"], "OBSERVED_AT_INVALID")
    if previous is not None:
        if type(previous) is not dict or previous.get("laneId") != doc["laneId"]:
            raise DeliveryFirstError("PREVIOUS_LANE_ID_MISMATCH")
        prior_observed = _utc(previous.get("observedAtUtc"), "PREVIOUS_OBSERVED_AT_INVALID")
        if prior_observed >= observed:
            raise DeliveryFirstError("PREVIOUS_NOT_STRICTLY_EARLIER")
        verify(previous, _history_shape_only=True)

    queue = _exact(doc["queue"], {"fingerprintSha256", "unchangedWakeCount", "unchangedMinutes", "actionable"}, "QUEUE_SHAPE_INVALID")
    if type(queue["fingerprintSha256"]) is not str or not SHA256.fullmatch(queue["fingerprintSha256"]):
        raise DeliveryFirstError("QUEUE_FINGERPRINT_INVALID")
    wakes = _nonnegative_int(queue["unchangedWakeCount"], "UNCHANGED_WAKE_COUNT_INVALID")
    minutes = _nonnegative_int(queue["unchangedMinutes"], "UNCHANGED_MINUTES_INVALID")
    if type(queue["actionable"]) is not bool:
        raise DeliveryFirstError("QUEUE_ACTIONABLE_INVALID")
    if previous is not None:
        prior_queue = previous["queue"]
        if prior_queue["fingerprintSha256"] == queue["fingerprintSha256"]:
            if wakes <= prior_queue["unchangedWakeCount"] or minutes < prior_queue["unchangedMinutes"]:
                raise DeliveryFirstError("UNCHANGED_QUEUE_COUNTER_REGRESSION")

    outcomes = _exact(doc["outcomes"], {"mergedCommits", "closedGates", "userVisibleMilestones", "receiptArtifacts"}, "OUTCOME_SHAPE_INVALID")
    merged = _evidence_rows(outcomes["mergedCommits"], "commitSha", "MERGED_COMMIT_INVALID")
    closed = _evidence_rows(outcomes["closedGates"], "gateId", "CLOSED_GATE_INVALID")
    milestones = _evidence_rows(outcomes["userVisibleMilestones"], "milestoneId", "MILESTONE_INVALID")
    evidence_hashes = [row["evidenceSha256"] for row in merged + closed + milestones]
    if len(evidence_hashes) != len(set(evidence_hashes)):
        raise DeliveryFirstError("OUTCOME_EVIDENCE_DUPLICATE")
    _nonnegative_int(outcomes["receiptArtifacts"], "RECEIPT_COUNT_INVALID")
    current_sets = [
        {(row["commitSha"], row["targetRef"], row["evidenceSha256"]) for row in merged},
        {(row["gateId"], row["evidenceSha256"]) for row in closed},
        {(row["milestoneId"], row["declarationSha256"], row["evidenceSha256"]) for row in milestones},
    ]
    prior_sets: list[set[tuple[str, ...]]] = [set(), set(), set()]
    if previous is not None:
        prior_outcomes = previous["outcomes"]
        prior_merged = _evidence_rows(prior_outcomes["mergedCommits"], "commitSha", "PREVIOUS_MERGED_COMMIT_INVALID")
        prior_closed = _evidence_rows(prior_outcomes["closedGates"], "gateId", "PREVIOUS_CLOSED_GATE_INVALID")
        prior_milestones = _evidence_rows(prior_outcomes["userVisibleMilestones"], "milestoneId", "PREVIOUS_MILESTONE_INVALID")
        prior_sets = [
            {(row["commitSha"], row["targetRef"], row["evidenceSha256"]) for row in prior_merged},
            {(row["gateId"], row["evidenceSha256"]) for row in prior_closed},
            {(row["milestoneId"], row["declarationSha256"], row["evidenceSha256"]) for row in prior_milestones},
        ]
        if any(not prior.issubset(current) for current, prior in zip(current_sets, prior_sets)):
            raise DeliveryFirstError("OUTCOME_HISTORY_NOT_APPEND_ONLY")
    credit = sum(len(current - prior) for current, prior in zip(current_sets, prior_sets))
    if _history_shape_only:
        _nonnegative_int(doc["progressCredit"], "PREVIOUS_PROGRESS_CREDIT_INVALID")
    elif type(doc["progressCredit"]) is not int or doc["progressCredit"] != credit:
        raise DeliveryFirstError("PROGRESS_CREDIT_INCLUDES_NON_OUTCOME")

    accepted = doc["acceptedUnlanded"]
    if type(accepted) is not list or len(accepted) > 256:
        raise DeliveryFirstError("ACCEPTED_UNLANDED_INVALID")
    accepted_ids: list[str] = []
    accepted_order: list[tuple[datetime, str]] = []
    for row in accepted:
        row = _exact(row, {"id", "acceptedAtUtc"}, "ACCEPTED_ROW_SHAPE_INVALID")
        if type(row["id"]) is not str or not row["id"]:
            raise DeliveryFirstError("ACCEPTED_ID_INVALID")
        accepted_at = _utc(row["acceptedAtUtc"], "ACCEPTED_AT_INVALID")
        if accepted_at > observed:
            raise DeliveryFirstError("ACCEPTED_AT_AFTER_OBSERVATION")
        accepted_ids.append(row["id"])
        accepted_order.append((accepted_at, row["id"]))
    if len(set(accepted_ids)) != len(accepted_ids):
        raise DeliveryFirstError("ACCEPTED_ID_DUPLICATE")
    if accepted_order != sorted(accepted_order):
        raise DeliveryFirstError("ACCEPTED_QUEUE_NOT_OLDEST_FIRST")

    deliverable = doc["nextExecutableDeliverable"]
    if deliverable is not None:
        deliverable = _exact(deliverable, {"id", "action", "owner", "deadlineUtc", "authority"}, "DELIVERABLE_SHAPE_INVALID")
        if type(deliverable["id"]) is not str or not deliverable["id"] or deliverable["action"] not in ACTIONS:
            raise DeliveryFirstError("DELIVERABLE_ID_OR_ACTION_INVALID")
        if type(deliverable["owner"]) is not str or not OWNER.fullmatch(deliverable["owner"]):
            raise DeliveryFirstError("DELIVERABLE_OWNER_INVALID")
        deadline = _utc(deliverable["deadlineUtc"], "DELIVERABLE_DEADLINE_INVALID")
        if deadline <= observed or (deadline - observed).total_seconds() > 3600:
            raise DeliveryFirstError("DELIVERABLE_DEADLINE_OUT_OF_BOUNDS")
        if deliverable["authority"] not in {"AUTHORIZED", "BLOCKER_CLOSURE_ONLY"}:
            raise DeliveryFirstError("DELIVERABLE_AUTHORITY_INVALID")
        if deliverable["action"] in {"LAND_ACCEPTED", "DELIVER_MILESTONE"} and deliverable["authority"] != "AUTHORIZED":
            raise DeliveryFirstError("DELIVERY_ACTION_NOT_AUTHORIZED")

    blocker = doc["primaryBlocker"]
    if blocker is not None:
        blocker = _exact(blocker, {"id", "owner", "deadlineUtc", "status"}, "BLOCKER_SHAPE_INVALID")
        if type(blocker["id"]) is not str or not blocker["id"]:
            raise DeliveryFirstError("BLOCKER_ID_INVALID")
        if type(blocker["owner"]) is not str or not OWNER.fullmatch(blocker["owner"]):
            raise DeliveryFirstError("BLOCKER_OWNER_INVALID")
        blocker_deadline = _utc(blocker["deadlineUtc"], "BLOCKER_DEADLINE_INVALID")
        if blocker_deadline <= observed or (blocker_deadline - observed).total_seconds() > 3600:
            raise DeliveryFirstError("BLOCKER_DEADLINE_OUT_OF_BOUNDS")
        if blocker["status"] != "OPEN":
            raise DeliveryFirstError("BLOCKER_STATUS_INVALID")

    fingerprint_payload = {
        "laneId": doc["laneId"],
        "actionable": queue["actionable"],
        "acceptedUnlanded": accepted,
        "nextExecutableDeliverable": None if deliverable is None else {
            key: deliverable[key] for key in ("id", "action", "owner", "authority")
        },
        "primaryBlocker": None if blocker is None else {
            key: blocker[key] for key in ("id", "owner", "status")
        },
    }
    expected_fingerprint = "sha256:" + hashlib.sha256(
        json.dumps(fingerprint_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    if queue["fingerprintSha256"] != expected_fingerprint:
        raise DeliveryFirstError("QUEUE_FINGERPRINT_CONTENT_MISMATCH")

    if doc["laneAction"] not in LANE_ACTIONS:
        raise DeliveryFirstError("LANE_ACTION_INVALID")
    stalled = queue["actionable"] and (wakes >= 2 or minutes >= 30)
    if stalled and (doc["laneAction"] != "ESCALATE_STALLED_QUEUE" or blocker is None):
        raise DeliveryFirstError("UNCHANGED_QUEUE_NOT_ESCALATED")
    if doc["laneAction"] == "ESCALATE_STALLED_QUEUE" and blocker is None:
        raise DeliveryFirstError("ESCALATION_WITHOUT_BLOCKER")
    if doc["laneAction"] == "EXECUTE_DELIVERABLE" and deliverable is None:
        raise DeliveryFirstError("EXECUTION_WITHOUT_DELIVERABLE")
    if doc["laneAction"] == "HOLD_NO_EXECUTABLE_DELIVERABLE" and deliverable is not None:
        raise DeliveryFirstError("HOLD_WITH_EXECUTABLE_DELIVERABLE")

    escalation = doc["stalledEscalation"]
    if doc["laneAction"] == "ESCALATE_STALLED_QUEUE":
        escalation = _exact(escalation, {"id", "queueFingerprintSha256", "settled"}, "ESCALATION_SHAPE_INVALID")
        expected = "sha256:" + hashlib.sha256(
            f"{doc['laneId']}\0{queue['fingerprintSha256']}\0{blocker['id']}".encode("utf-8")
        ).hexdigest()
        if escalation["id"] != expected or escalation["queueFingerprintSha256"] != queue["fingerprintSha256"]:
            raise DeliveryFirstError("ESCALATION_IDENTITY_INVALID")
        if type(escalation["settled"]) is not bool or escalation["settled"]:
            raise DeliveryFirstError("OPEN_ESCALATION_SETTLEMENT_INVALID")
        if previous is not None:
            prior = previous.get("stalledEscalation")
            if type(prior) is dict and prior.get("id") == escalation["id"] and prior.get("settled") is False:
                raise DeliveryFirstError("REPEATED_UNCHANGED_ESCALATION")
    elif escalation is not None:
        raise DeliveryFirstError("ESCALATION_WITHOUT_ACTION")

    if accepted:
        if deliverable is None or deliverable["action"] != "LAND_ACCEPTED" or deliverable["id"] != accepted_ids[0]:
            raise DeliveryFirstError("ACCEPTED_WORK_NOT_FIRST")
        expected_lane_action = "ESCALATE_STALLED_QUEUE" if stalled else "EXECUTE_DELIVERABLE"
        if doc["laneAction"] != expected_lane_action:
            raise DeliveryFirstError("ACCEPTED_WORK_LANE_ACTION_INVALID")

    if deliverable is not None and deliverable["action"] == "CLOSE_GATE":
        if blocker is None:
            raise DeliveryFirstError("GATE_CLOSURE_WITHOUT_BLOCKER")
        if deliverable["authority"] != "BLOCKER_CLOSURE_ONLY":
            raise DeliveryFirstError("GATE_CLOSURE_AUTHORITY_INVALID")
        if (deliverable["id"], deliverable["owner"], deliverable["deadlineUtc"]) != (
            blocker["id"], blocker["owner"], blocker["deadlineUtc"]
        ):
            raise DeliveryFirstError("GATE_CLOSURE_BLOCKER_BINDING_INVALID")

    rotation = _exact(doc["rotation"], {"requested", "reason"}, "ROTATION_SHAPE_INVALID")
    if type(rotation["requested"]) is not bool or rotation["reason"] not in ROTATION_REASONS:
        raise DeliveryFirstError("ROTATION_INVALID")
    if rotation["requested"] != (rotation["reason"] != "NONE"):
        raise DeliveryFirstError("ROTATION_REQUEST_REASON_MISMATCH")
    if rotation["requested"] and deliverable is None and rotation["reason"] != "SAFETY_CONTINUITY_ONLY":
        raise DeliveryFirstError("ROTATION_WITHOUT_DELIVERABLE")
    if rotation["requested"] and deliverable is None and doc["laneAction"] != "HOLD_NO_EXECUTABLE_DELIVERABLE":
        raise DeliveryFirstError("SAFETY_ROTATION_MUST_HOLD")
    if doc["laneAction"] == "EXPAND_LANE" and deliverable is None:
        raise DeliveryFirstError("EXPANSION_WITHOUT_DELIVERABLE")

    evidence = _exact(doc["evidenceAuthoring"], {"requested", "closesGateId"}, "EVIDENCE_SHAPE_INVALID")
    if type(evidence["requested"]) is not bool:
        raise DeliveryFirstError("EVIDENCE_REQUEST_INVALID")
    if evidence["requested"]:
        if accepted or deliverable is None or deliverable["action"] != "CLOSE_GATE":
            raise DeliveryFirstError("EVIDENCE_WHILE_LANDING_AVAILABLE")
        if type(evidence["closesGateId"]) is not str or not evidence["closesGateId"]:
            raise DeliveryFirstError("EVIDENCE_GATE_UNBOUND")
        if evidence["closesGateId"] != deliverable["id"]:
            raise DeliveryFirstError("EVIDENCE_GATE_DELIVERABLE_MISMATCH")
        if blocker is not None and evidence["closesGateId"] != blocker["id"]:
            raise DeliveryFirstError("EVIDENCE_GATE_BLOCKER_MISMATCH")
    elif evidence["closesGateId"] is not None:
        raise DeliveryFirstError("EVIDENCE_GATE_WITHOUT_REQUEST")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    history = parser.add_mutually_exclusive_group(required=True)
    history.add_argument("--previous", type=Path)
    history.add_argument("--bootstrap", action="store_true")
    args = parser.parse_args()
    try:
        verify(load_json(args.path), load_json(args.previous) if args.previous else None)
    except DeliveryFirstError as exc:
        print(f"DELIVERY_FIRST_INVALID:{exc}")
        return 1
    print("DELIVERY_FIRST_VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
