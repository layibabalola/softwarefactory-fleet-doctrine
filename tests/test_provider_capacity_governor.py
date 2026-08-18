import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "provider_capacity_governor.py"
SPEC = importlib.util.spec_from_file_location("provider_capacity_governor", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class ProviderCapacityGovernorTests(unittest.TestCase):
    def setUp(self):
        self.snapshot = json.loads((ROOT / "examples" / "provider-admission-snapshot-v1.json").read_text())

    def test_example_is_admitted(self):
        decision = MODULE.decide(self.snapshot)
        self.assertEqual("ADMIT", decision["decision"])
        self.assertEqual("2026-08-18T16:12:00Z", decision["lease_offer"]["expires_at"])

    def test_same_quota_domain_is_single_flight(self):
        self.snapshot["active_leases"].append(
            {
                "lease_id": "existing-lease-0001",
                "quota_domain_id": self.snapshot["request"]["quota_domain_id"],
                "state": "RUNNING",
                "expires_at": "2026-08-18T16:10:00Z",
            }
        )
        decision = MODULE.decide(self.snapshot)
        self.assertEqual("DENY", decision["decision"])
        self.assertIn("CONCURRENCY_LIMIT", decision["reason_codes"])

    def test_different_account_fingerprint_does_not_collide(self):
        self.snapshot["active_leases"].append(
            {
                "lease_id": "other-account-0001",
                "quota_domain_id": "anthropic/hmac-sha256:ffffffffffffffffffffffffffffffff",
                "state": "RUNNING",
                "expires_at": "2026-08-18T16:10:00Z",
            }
        )
        self.assertEqual("ADMIT", MODULE.decide(self.snapshot)["decision"])

    def test_no_actionable_work_consumes_no_inference(self):
        self.snapshot["request"]["actionable_work"] = False
        decision = MODULE.decide(self.snapshot)
        self.assertEqual("DENY", decision["decision"])
        self.assertIn("NO_ACTIONABLE_WORK", decision["reason_codes"])

    def test_unknown_capacity_blocks_unattended_work(self):
        self.snapshot["capacity"]["status"] = "unknown"
        self.snapshot["capacity"]["utilization_pct"] = "unknown"
        decision = MODULE.decide(self.snapshot)
        self.assertEqual("DENY", decision["decision"])
        self.assertIn("CAPACITY_UNKNOWN", decision["reason_codes"])

    def test_reset_does_not_open_automatic_launch_gate(self):
        self.snapshot["policy"]["automatic_launch_gate"] = "closed"
        self.snapshot["capacity"]["status"] = "available"
        self.snapshot["capacity"]["utilization_pct"] = 0
        decision = MODULE.decide(self.snapshot)
        self.assertEqual("DENY", decision["decision"])
        self.assertIn("AUTOMATIC_GATE_CLOSED", decision["reason_codes"])

    def test_owner_override_is_explicit_but_does_not_steal_live_claim(self):
        self.snapshot["request"]["owner_override"] = True
        self.snapshot["capacity"]["status"] = "unknown"
        self.snapshot["capacity"]["utilization_pct"] = "unknown"
        decision = MODULE.decide(self.snapshot)
        self.assertEqual("ADMIT", decision["decision"])
        self.assertIn("OWNER_OVERRIDE_CAPACITY_UNKNOWN", decision["warnings"])
        blocked = copy.deepcopy(self.snapshot)
        blocked["active_leases"].append(
            {
                "lease_id": "existing-lease-0002",
                "quota_domain_id": blocked["request"]["quota_domain_id"],
                "state": "RUNNING",
                "expires_at": "2026-08-18T16:10:00Z",
            }
        )
        self.assertIn("CONCURRENCY_LIMIT", MODULE.decide(blocked)["reason_codes"])

    def test_completion_reserve_blocks_background_slice(self):
        self.snapshot["capacity"]["utilization_pct"] = 55
        self.snapshot["capacity"]["reserved_pct"] = 10
        self.snapshot["request"]["estimated_window_pct"] = 10
        decision = MODULE.decide(self.snapshot)
        self.assertIn("COMPLETION_RESERVE", decision["reason_codes"])

    def test_required_exact_profile_never_silently_downgrades(self):
        self.snapshot["request"]["profile_available"] = False
        decision = MODULE.decide(self.snapshot)
        self.assertIn("EXACT_PROFILE_UNAVAILABLE", decision["reason_codes"])

    def test_usage_examples_validate(self):
        report = MODULE.validate_usage_file(ROOT / "examples" / "provider-usage-events-v1.jsonl")
        self.assertTrue(report["valid"], report["errors"])
        self.assertEqual(2, report["event_count"])

    def test_idle_event_with_model_request_is_rejected(self):
        event = json.loads((ROOT / "examples" / "provider-usage-events-v1.jsonl").read_text().splitlines()[1])
        event["measurement"]["request_count"] = 1
        with self.assertRaisesRegex(MODULE.ContractError, "zero model requests"):
            MODULE.validate_usage_event(event)

    def test_raw_identity_or_credentials_are_rejected(self):
        event = json.loads((ROOT / "examples" / "provider-usage-events-v1.jsonl").read_text().splitlines()[0])
        event["account_email"] = "forbidden@example.invalid"
        with self.assertRaisesRegex(MODULE.ContractError, "prohibited"):
            MODULE.validate_usage_event(event)


if __name__ == "__main__":
    unittest.main()
