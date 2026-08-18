import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path
from unittest import mock


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

    def _lease(self, **overrides):
        lease = {
            "lease_id": "existing-lease-0001",
            "quota_domain_id": self.snapshot["request"]["quota_domain_id"],
            "state": "RUNNING",
            "expires_at": "2026-08-18T16:10:00Z",
            "process_id": 4242,
            "process_start_time": "2026-08-18T15:58:00Z",
            "process_status": "live",
            "provider_requested": "anthropic",
            "model_requested": "claude-opus-5",
            "provider_observed": "anthropic",
            "model_observed": "claude-opus-5",
            "seat_epoch": 7,
            "registered_session_id_hash": "sha256:" + "c" * 64,
            "observed_session_id_hash": "sha256:" + "c" * 64,
            "registry_status": "verified",
            "progress_status": "fresh",
        }
        lease.update(overrides)
        return lease

    def test_example_is_admitted(self):
        decision = MODULE.decide(self.snapshot)
        self.assertEqual("ADMIT", decision["decision"])
        self.assertEqual("2026-08-18T16:12:00Z", decision["lease_offer"]["expires_at"])

    def test_same_quota_domain_is_single_flight(self):
        self.snapshot["active_leases"].append(self._lease())
        decision = MODULE.decide(self.snapshot)
        self.assertEqual("DENY", decision["decision"])
        self.assertIn("CONCURRENCY_LIMIT", decision["reason_codes"])

    def test_different_account_fingerprint_does_not_collide(self):
        self.snapshot["active_leases"].append(
            self._lease(
                lease_id="other-account-0001",
                quota_domain_id="anthropic/hmac-sha256:ffffffffffffffffffffffffffffffff",
            )
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

    def test_r1_red_stale_or_future_capacity_is_r2_green_denied(self):
        stale = copy.deepcopy(self.snapshot)
        stale["capacity"]["observed_at"] = "2020-01-01T00:00:00Z"
        self.assertIn("CAPACITY_OBSERVATION_STALE", MODULE.decide(stale)["reason_codes"])
        future = copy.deepcopy(self.snapshot)
        future["capacity"]["observed_at"] = "2026-08-18T16:00:01Z"
        self.assertIn("CAPACITY_OBSERVATION_FROM_FUTURE", MODULE.decide(future)["reason_codes"])

    def test_schema_date_time_format_is_enforced(self):
        self.snapshot["capacity"]["observed_at"] = "not-a-date-time"
        with self.assertRaisesRegex(MODULE.ContractError, "schema violation|invalid RFC3339"):
            MODULE.decide(self.snapshot)

    def test_r1_red_unchanged_prior_idle_fingerprint_is_r2_green_denied(self):
        self.snapshot["request"]["prior_idle_input_fingerprint"] = self.snapshot["request"][
            "idle_input_fingerprint"
        ]
        decision = MODULE.decide(self.snapshot)
        self.assertEqual("DENY", decision["decision"])
        self.assertIn("UNCHANGED_IDLE_INPUT", decision["reason_codes"])

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
        blocked["active_leases"].append(self._lease(lease_id="existing-lease-0002"))
        self.assertIn("CONCURRENCY_LIMIT", MODULE.decide(blocked)["reason_codes"])

    def test_r1_red_malformed_lease_state_is_r2_green_schema_failure(self):
        self.snapshot["active_leases"].append(self._lease(state="RUNNING "))
        with self.assertRaisesRegex(MODULE.ContractError, "schema violation"):
            MODULE.decide(self.snapshot)

    def test_dead_process_with_fresh_lease_is_not_live(self):
        self.snapshot["active_leases"].append(self._lease(process_status="dead"))
        self.assertEqual("ADMIT", MODULE.decide(self.snapshot)["decision"])

    def test_live_process_with_stale_lease_degrades_without_takeover(self):
        self.snapshot["active_leases"].append(
            self._lease(expires_at="2026-08-18T15:59:59Z")
        )
        decision = MODULE.decide(self.snapshot)
        self.assertEqual("DENY", decision["decision"])
        self.assertIn("LIVE_PROCESS_STALE_LEASE", decision["reason_codes"])

    def test_registry_or_session_ambiguity_blocks_takeover(self):
        for changes in (
            {"registry_status": "mismatch"},
            {"observed_session_id_hash": "sha256:" + "d" * 64},
            {"model_observed": "claude-sonnet-5"},
            {"process_status": "ambiguous"},
            {"process_start_time": "2026-08-18T16:00:01Z"},
        ):
            with self.subTest(changes=changes):
                snapshot = copy.deepcopy(self.snapshot)
                snapshot["active_leases"].append(self._lease(**changes))
                decision = MODULE.decide(snapshot)
                self.assertEqual("DENY", decision["decision"])
                self.assertIn("IDENTITY_AMBIGUOUS", decision["reason_codes"])

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
        with self.assertRaisesRegex(MODULE.ContractError, "schema violation"):
            MODULE.validate_usage_event(event)

    def test_r1_red_idle_with_omitted_counter_or_tokens_is_r2_green_rejected(self):
        base = json.loads((ROOT / "examples" / "provider-usage-events-v1.jsonl").read_text().splitlines()[1])
        missing = copy.deepcopy(base)
        missing["measurement"].pop("request_count")
        with self.assertRaisesRegex(MODULE.ContractError, "schema violation"):
            MODULE.validate_usage_event(missing)
        inferred = copy.deepcopy(base)
        inferred["measurement"]["input_tokens"] = 999
        with self.assertRaisesRegex(MODULE.ContractError, "schema violation"):
            MODULE.validate_usage_event(inferred)

    def test_raw_identity_or_credentials_are_rejected(self):
        event = json.loads((ROOT / "examples" / "provider-usage-events-v1.jsonl").read_text().splitlines()[0])
        event["account_email"] = "forbidden@example.invalid"
        with self.assertRaisesRegex(MODULE.ContractError, "prohibited"):
            MODULE.validate_usage_event(event)

    def test_r1_red_extra_identity_field_is_r2_green_schema_failure(self):
        event = json.loads((ROOT / "examples" / "provider-usage-events-v1.jsonl").read_text().splitlines()[0])
        event["account_identifier"] = "real-account@example.invalid"
        with self.assertRaisesRegex(MODULE.ContractError, "schema violation"):
            MODULE.validate_usage_event(event)

    def test_schema_or_validator_absence_fails_closed(self):
        MODULE._schema_validator.cache_clear()
        with mock.patch.object(MODULE, "jsonschema", None):
            with self.assertRaisesRegex(MODULE.ContractError, "fails closed"):
                MODULE.decide(self.snapshot)
        MODULE._schema_validator.cache_clear()
        with mock.patch.object(MODULE, "SCHEMA_ROOT", ROOT / "schemas-does-not-exist"):
            with self.assertRaisesRegex(MODULE.ContractError, "schema unavailable"):
                MODULE.decide(self.snapshot)
        MODULE._schema_validator.cache_clear()


if __name__ == "__main__":
    unittest.main()
