from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "check_delivery_first_lane_status.py"
SPEC = importlib.util.spec_from_file_location("delivery_first", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class DeliveryFirstLaneStatusTests(unittest.TestCase):
    def setUp(self):
        self.doc = MODULE.load_json(ROOT / "examples" / "delivery-first-lane-status-v1.json")

    def _rebind_queue(self, doc):
        deliverable = doc["nextExecutableDeliverable"]
        blocker = doc["primaryBlocker"]
        payload = {
            "laneId": doc["laneId"],
            "actionable": doc["queue"]["actionable"],
            "acceptedUnlanded": doc["acceptedUnlanded"],
            "nextExecutableDeliverable": None if deliverable is None else {
                key: deliverable[key] for key in ("id", "action", "owner", "authority")
            },
            "primaryBlocker": None if blocker is None else {
                key: blocker[key] for key in ("id", "owner", "status")
            },
        }
        fingerprint = "sha256:" + hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        doc["queue"]["fingerprintSha256"] = fingerprint
        escalation = doc["stalledEscalation"]
        if escalation is not None:
            escalation["queueFingerprintSha256"] = fingerprint
            escalation["id"] = "sha256:" + hashlib.sha256(
                f"{doc['laneId']}\0{fingerprint}\0{blocker['id']}".encode("utf-8")
            ).hexdigest()

    def test_example_passes(self):
        MODULE.verify(self.doc)

    def test_receipts_never_earn_progress_credit(self):
        hostile = copy.deepcopy(self.doc)
        hostile["progressCredit"] = hostile["outcomes"]["receiptArtifacts"]
        with self.assertRaisesRegex(MODULE.DeliveryFirstError, "PROGRESS_CREDIT_INCLUDES_NON_OUTCOME"):
            MODULE.verify(hostile)

    def test_accepted_work_must_land_first(self):
        hostile = copy.deepcopy(self.doc)
        hostile["acceptedUnlanded"] = [{"id": "READY-1", "acceptedAtUtc": "2026-08-26T20:00:00Z"}]
        self._rebind_queue(hostile)
        with self.assertRaisesRegex(MODULE.DeliveryFirstError, "ACCEPTED_WORK_NOT_FIRST"):
            MODULE.verify(hostile)

    def test_accepted_work_cannot_expand_lane(self):
        hostile = copy.deepcopy(self.doc)
        hostile["queue"]["unchangedWakeCount"] = 0
        hostile["queue"]["unchangedMinutes"] = 0
        hostile["acceptedUnlanded"] = [{"id": "READY-1", "acceptedAtUtc": "2026-08-26T20:00:00Z"}]
        hostile["nextExecutableDeliverable"]["id"] = "READY-1"
        hostile["nextExecutableDeliverable"]["action"] = "LAND_ACCEPTED"
        hostile["nextExecutableDeliverable"]["authority"] = "AUTHORIZED"
        hostile["primaryBlocker"] = None
        hostile["evidenceAuthoring"] = {"requested": False, "closesGateId": None}
        hostile["stalledEscalation"] = None
        hostile["laneAction"] = "EXPAND_LANE"
        self._rebind_queue(hostile)
        with self.assertRaisesRegex(MODULE.DeliveryFirstError, "ACCEPTED_WORK_LANE_ACTION_INVALID"):
            MODULE.verify(hostile)

    def test_accepted_queue_must_be_oldest_first(self):
        hostile = copy.deepcopy(self.doc)
        hostile["acceptedUnlanded"] = [
            {"id": "READY-2", "acceptedAtUtc": "2026-08-26T20:30:00Z"},
            {"id": "READY-1", "acceptedAtUtc": "2026-08-26T20:00:00Z"},
        ]
        hostile["nextExecutableDeliverable"]["id"] = "READY-2"
        hostile["nextExecutableDeliverable"]["action"] = "LAND_ACCEPTED"
        hostile["evidenceAuthoring"] = {"requested": False, "closesGateId": None}
        with self.assertRaisesRegex(MODULE.DeliveryFirstError, "ACCEPTED_QUEUE_NOT_OLDEST_FIRST"):
            MODULE.verify(hostile)

    def test_stalled_actionable_queue_must_escalate(self):
        hostile = copy.deepcopy(self.doc)
        hostile["laneAction"] = "EXECUTE_DELIVERABLE"
        with self.assertRaisesRegex(MODULE.DeliveryFirstError, "UNCHANGED_QUEUE_NOT_ESCALATED"):
            MODULE.verify(hostile)

    def test_blocker_owner_and_deadline_are_bounded(self):
        for field, value, code in (
            ("owner", "committee", "BLOCKER_OWNER_INVALID"),
            ("deadlineUtc", "2026-08-27T21:00:00Z", "BLOCKER_DEADLINE_OUT_OF_BOUNDS"),
        ):
            hostile = copy.deepcopy(self.doc)
            hostile["primaryBlocker"][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(MODULE.DeliveryFirstError, code):
                MODULE.verify(hostile)

    def test_gate_deliverable_and_blocker_share_owner_and_deadline(self):
        hostile = copy.deepcopy(self.doc)
        hostile["nextExecutableDeliverable"]["owner"] = "thread:different-owner"
        self._rebind_queue(hostile)
        with self.assertRaisesRegex(MODULE.DeliveryFirstError, "GATE_CLOSURE_BLOCKER_BINDING_INVALID"):
            MODULE.verify(hostile)

    def test_gate_closure_requires_current_blocker(self):
        hostile = copy.deepcopy(self.doc)
        hostile["queue"]["unchangedWakeCount"] = 0
        hostile["queue"]["unchangedMinutes"] = 0
        hostile["primaryBlocker"] = None
        hostile["laneAction"] = "EXECUTE_DELIVERABLE"
        hostile["stalledEscalation"] = None
        self._rebind_queue(hostile)
        with self.assertRaisesRegex(MODULE.DeliveryFirstError, "GATE_CLOSURE_WITHOUT_BLOCKER"):
            MODULE.verify(hostile)

    def test_delivery_actions_require_full_authority(self):
        for action in ("LAND_ACCEPTED", "DELIVER_MILESTONE"):
            hostile = copy.deepcopy(self.doc)
            hostile["queue"]["actionable"] = False
            hostile["queue"]["unchangedWakeCount"] = 0
            hostile["queue"]["unchangedMinutes"] = 0
            hostile["nextExecutableDeliverable"]["action"] = action
            hostile["nextExecutableDeliverable"]["authority"] = "BLOCKER_CLOSURE_ONLY"
            hostile["primaryBlocker"] = None
            hostile["laneAction"] = "EXECUTE_DELIVERABLE"
            hostile["evidenceAuthoring"] = {"requested": False, "closesGateId": None}
            hostile["stalledEscalation"] = None
            if action == "LAND_ACCEPTED":
                hostile["acceptedUnlanded"] = [{
                    "id": hostile["nextExecutableDeliverable"]["id"],
                    "acceptedAtUtc": "2026-08-26T20:00:00Z",
                }]
            with self.subTest(action=action), self.assertRaisesRegex(
                MODULE.DeliveryFirstError, "DELIVERY_ACTION_NOT_AUTHORIZED"
            ):
                MODULE.verify(hostile)

    def test_non_safety_rotation_requires_deliverable(self):
        hostile = copy.deepcopy(self.doc)
        hostile["nextExecutableDeliverable"] = None
        hostile["rotation"] = {"requested": True, "reason": "EXECUTABLE_HANDOFF"}
        self._rebind_queue(hostile)
        with self.assertRaisesRegex(MODULE.DeliveryFirstError, "ROTATION_WITHOUT_DELIVERABLE"):
            MODULE.verify(hostile)

    def test_evidence_cannot_displace_accepted_landing(self):
        hostile = copy.deepcopy(self.doc)
        hostile["acceptedUnlanded"] = [{"id": "READY-1", "acceptedAtUtc": "2026-08-26T20:00:00Z"}]
        hostile["nextExecutableDeliverable"]["id"] = "READY-1"
        hostile["nextExecutableDeliverable"]["action"] = "LAND_ACCEPTED"
        hostile["nextExecutableDeliverable"]["authority"] = "AUTHORIZED"
        self._rebind_queue(hostile)
        with self.assertRaisesRegex(MODULE.DeliveryFirstError, "EVIDENCE_WHILE_LANDING_AVAILABLE"):
            MODULE.verify(hostile)

    def test_evidence_must_bind_the_current_gate(self):
        hostile = copy.deepcopy(self.doc)
        hostile["evidenceAuthoring"]["closesGateId"] = "UNRELATED-GATE"
        with self.assertRaisesRegex(MODULE.DeliveryFirstError, "EVIDENCE_GATE_DELIVERABLE_MISMATCH"):
            MODULE.verify(hostile)

    def test_future_accepted_item_is_rejected(self):
        hostile = copy.deepcopy(self.doc)
        hostile["acceptedUnlanded"] = [{"id": "READY-1", "acceptedAtUtc": "2026-08-26T22:00:00Z"}]
        with self.assertRaisesRegex(MODULE.DeliveryFirstError, "ACCEPTED_AT_AFTER_OBSERVATION"):
            MODULE.verify(hostile)

    def test_outcome_credit_requires_unique_evidence_bound_rows(self):
        hostile = copy.deepcopy(self.doc)
        row = {
            "gateId": "GATE-1",
            "evidenceSha256": "sha256:" + "b" * 64,
        }
        hostile["outcomes"]["closedGates"] = [row, copy.deepcopy(row)]
        hostile["progressCredit"] = 2
        with self.assertRaisesRegex(MODULE.DeliveryFirstError, "CLOSED_GATE_INVALID_DUPLICATE"):
            MODULE.verify(hostile)

    def test_milestone_credit_requires_predeclaration_binding(self):
        hostile = copy.deepcopy(self.doc)
        hostile["outcomes"]["userVisibleMilestones"] = [{
            "milestoneId": "MILESTONE-1",
            "evidenceSha256": "sha256:" + "b" * 64,
        }]
        hostile["progressCredit"] = 1
        with self.assertRaisesRegex(MODULE.DeliveryFirstError, "MILESTONE_INVALID"):
            MODULE.verify(hostile)

    def test_repeated_unchanged_escalation_is_rejected(self):
        previous = copy.deepcopy(self.doc)
        current = copy.deepcopy(self.doc)
        current["observedAtUtc"] = "2026-08-26T21:10:00Z"
        current["queue"]["unchangedWakeCount"] = 3
        current["queue"]["unchangedMinutes"] = 40
        current["nextExecutableDeliverable"]["deadlineUtc"] = "2026-08-26T21:55:00Z"
        current["primaryBlocker"]["deadlineUtc"] = "2026-08-26T21:55:00Z"
        with self.assertRaisesRegex(MODULE.DeliveryFirstError, "REPEATED_UNCHANGED_ESCALATION"):
            MODULE.verify(current, previous=previous)

    def test_previous_must_match_lane_and_precede_current(self):
        for mutation, code in (
            (lambda prior: prior.update(laneId="another-lane"), "PREVIOUS_LANE_ID_MISMATCH"),
            (lambda prior: prior.update(observedAtUtc="2026-08-26T22:00:00Z"), "PREVIOUS_NOT_STRICTLY_EARLIER"),
        ):
            previous = copy.deepcopy(self.doc)
            current = copy.deepcopy(self.doc)
            current["observedAtUtc"] = "2026-08-26T21:10:00Z"
            mutation(previous)
            with self.subTest(code=code), self.assertRaisesRegex(MODULE.DeliveryFirstError, code):
                MODULE.verify(current, previous=previous)

    def test_unchanged_queue_counters_cannot_reset(self):
        previous = copy.deepcopy(self.doc)
        current = copy.deepcopy(self.doc)
        current["observedAtUtc"] = "2026-08-26T21:10:00Z"
        current["queue"]["unchangedWakeCount"] = 0
        current["queue"]["unchangedMinutes"] = 0
        current["laneAction"] = "EXECUTE_DELIVERABLE"
        current["stalledEscalation"] = None
        with self.assertRaisesRegex(MODULE.DeliveryFirstError, "UNCHANGED_QUEUE_COUNTER_REGRESSION"):
            MODULE.verify(current, previous=previous)

    def test_queue_fingerprint_cannot_be_changed_to_reset_stall(self):
        hostile = copy.deepcopy(self.doc)
        hostile["queue"]["fingerprintSha256"] = "sha256:" + "d" * 64
        hostile["queue"]["unchangedWakeCount"] = 0
        hostile["queue"]["unchangedMinutes"] = 0
        hostile["laneAction"] = "EXECUTE_DELIVERABLE"
        hostile["stalledEscalation"] = None
        with self.assertRaisesRegex(MODULE.DeliveryFirstError, "QUEUE_FINGERPRINT_CONTENT_MISMATCH"):
            MODULE.verify(hostile)

    def test_outcome_rows_are_cumulative_but_credit_only_the_delta(self):
        gate = {"gateId": "GATE-1", "evidenceSha256": "sha256:" + "b" * 64}
        previous = copy.deepcopy(self.doc)
        previous["outcomes"]["closedGates"] = [copy.deepcopy(gate)]
        previous["progressCredit"] = 1
        current = copy.deepcopy(previous)
        current["observedAtUtc"] = "2026-08-26T21:10:00Z"
        current["queue"]["unchangedWakeCount"] = 0
        current["queue"]["unchangedMinutes"] = 0
        current["queue"]["actionable"] = False
        current["nextExecutableDeliverable"] = None
        current["primaryBlocker"] = None
        current["laneAction"] = "HOLD_NO_EXECUTABLE_DELIVERABLE"
        current["evidenceAuthoring"] = {"requested": False, "closesGateId": None}
        current["stalledEscalation"] = None
        current["progressCredit"] = 1
        self._rebind_queue(current)
        with self.assertRaisesRegex(MODULE.DeliveryFirstError, "PROGRESS_CREDIT_INCLUDES_NON_OUTCOME"):
            MODULE.verify(current, previous=previous)
        current["progressCredit"] = 0
        MODULE.verify(current, previous=previous)

    def test_rotation_reason_requires_a_rotation_request(self):
        hostile = copy.deepcopy(self.doc)
        hostile["rotation"] = {"requested": False, "reason": "EXECUTABLE_HANDOFF"}
        with self.assertRaisesRegex(MODULE.DeliveryFirstError, "ROTATION_REQUEST_REASON_MISMATCH"):
            MODULE.verify(hostile)

    def test_safety_continuity_rotation_holds_without_deliverable(self):
        valid = copy.deepcopy(self.doc)
        valid["queue"]["actionable"] = False
        valid["queue"]["unchangedWakeCount"] = 0
        valid["queue"]["unchangedMinutes"] = 0
        valid["nextExecutableDeliverable"] = None
        valid["primaryBlocker"] = None
        valid["laneAction"] = "HOLD_NO_EXECUTABLE_DELIVERABLE"
        valid["rotation"] = {"requested": True, "reason": "SAFETY_CONTINUITY_ONLY"}
        valid["evidenceAuthoring"] = {"requested": False, "closesGateId": None}
        valid["stalledEscalation"] = None
        self._rebind_queue(valid)
        MODULE.verify(valid)


if __name__ == "__main__":
    unittest.main()
