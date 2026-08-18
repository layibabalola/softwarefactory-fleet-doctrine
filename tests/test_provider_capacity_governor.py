import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
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
            "startup_fence_expires_at": "2026-08-18T15:59:00Z",
            "cooldown_expires_at": "2026-08-18T15:59:30Z",
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

    def _run_cli(self, *args):
        return subprocess.run(
            [sys.executable, str(MODULE_PATH), *map(str, args)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

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
        for invalid in ("not-a-date-time", "2026-08-18 16:00:00Z"):
            with self.subTest(value=invalid):
                snapshot = copy.deepcopy(self.snapshot)
                snapshot["capacity"]["observed_at"] = invalid
                with self.assertRaisesRegex(MODULE.ContractError, "schema violation|invalid RFC3339"):
                    MODULE.decide(snapshot)

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

    def test_r2_red_dead_starting_claimant_is_r3_green_fenced_independently(self):
        cases = (
            {
                "startup_fence_expires_at": "2026-08-18T16:01:00Z",
                "cooldown_expires_at": "2026-08-18T15:59:30Z",
                "reason": "STARTUP_FENCE_ACTIVE",
            },
            {
                "startup_fence_expires_at": "2026-08-18T15:59:00Z",
                "cooldown_expires_at": "2026-08-18T16:01:00Z",
                "reason": "COOLDOWN_ACTIVE",
            },
        )
        for case in cases:
            with self.subTest(reason=case["reason"]):
                snapshot = copy.deepcopy(self.snapshot)
                snapshot["active_leases"].append(
                    self._lease(
                        state="STARTING",
                        process_status="dead",
                        startup_fence_expires_at=case["startup_fence_expires_at"],
                        cooldown_expires_at=case["cooldown_expires_at"],
                    )
                )
                decision = MODULE.decide(snapshot)
                self.assertEqual("DENY", decision["decision"])
                self.assertIn(case["reason"], decision["reason_codes"])

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
        with self.assertRaisesRegex(MODULE.ContractError, "schema violation|prohibited"):
            MODULE.validate_usage_event(event)

    def test_r2_red_email_and_unsafe_paths_are_r3_green_rejected(self):
        base = json.loads((ROOT / "examples" / "provider-usage-events-v1.jsonl").read_text().splitlines()[0])
        email = copy.deepcopy(base)
        email["actor"]["role"] = "real-account@example.invalid"
        with self.assertRaisesRegex(MODULE.ContractError, "email-like"):
            MODULE.validate_usage_event(email)
        disguised_path = copy.deepcopy(base)
        disguised_path["model_requested"] = "C:/Users/alice/raw-account.json"
        with self.assertRaisesRegex(MODULE.ContractError, "publishable value prohibited"):
            MODULE.validate_usage_event(disguised_path)
        for unsafe_path in (
            "C:/Users/alice/usage.json",
            "/home/alice/usage.json",
            "\\\\server\\share\\usage.json",
            "Users/alice/usage.json",
            "../private/usage.json",
        ):
            with self.subTest(path=unsafe_path):
                event = copy.deepcopy(base)
                event["refs"][0]["project_local_path"] = unsafe_path
                with self.assertRaisesRegex(
                    MODULE.ContractError,
                    "paths? prohibited|path required|publishable value prohibited",
                ):
                    MODULE.validate_usage_event(event)

    def test_r2_red_duplicate_and_nonfinite_snapshot_cli_is_r3_green_rejected(self):
        raw = (ROOT / "examples" / "provider-admission-snapshot-v1.json").read_text()
        cases = {
            "duplicate.json": raw.replace(
                '"schema_version": 1,',
                '"schema_version": 1, "schema_version": 1,',
                1,
            ),
            "nan.json": raw.replace('"estimated_window_pct": 8', '"estimated_window_pct": NaN', 1),
            "negative-infinity.json": raw.replace(
                '"estimated_window_pct": 8',
                '"estimated_window_pct": -Infinity',
                1,
            ),
        }
        with tempfile.TemporaryDirectory() as directory:
            for name, payload in cases.items():
                with self.subTest(name=name):
                    path = Path(directory) / name
                    path.write_text(payload, encoding="utf-8")
                    result = self._run_cli("decide", path)
                    self.assertEqual(2, result.returncode, result.stdout)
                    self.assertRegex(result.stdout, "duplicate JSON key|non-finite JSON number")

    def test_r2_red_duplicate_nonfinite_and_invalid_utf8_jsonl_cli_is_r3_green_rejected(self):
        raw = (ROOT / "examples" / "provider-usage-events-v1.jsonl").read_text().splitlines()[0]
        cases = {
            "duplicate.jsonl": raw.replace('"schema_version":1,', '"schema_version":1,"schema_version":1,', 1).encode(),
            "infinity.jsonl": raw.replace('"request_count":73', '"request_count":Infinity', 1).encode(),
            "invalid-utf8.jsonl": b"\xff\n",
        }
        with tempfile.TemporaryDirectory() as directory:
            for name, payload in cases.items():
                with self.subTest(name=name):
                    path = Path(directory) / name
                    path.write_bytes(payload + (b"\n" if not payload.endswith(b"\n") else b""))
                    result = self._run_cli("validate-events", path)
                    self.assertEqual(2, result.returncode, result.stdout)
                    self.assertRegex(result.stdout, "duplicate JSON key|non-finite JSON number|invalid UTF-8")

    def test_every_snapshot_date_time_is_explicitly_parsed(self):
        self.snapshot["active_leases"].append(
            self._lease(
                quota_domain_id="anthropic/hmac-sha256:ffffffffffffffffffffffffffffffff",
                process_status="dead",
                startup_fence_expires_at="not-a-date-time",
            )
        )
        with self.assertRaisesRegex(MODULE.ContractError, "schema violation|invalid RFC3339"):
            MODULE.decide(self.snapshot)

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

    def test_r2_red_unlocked_dependency_is_r3_green_hash_locked_in_ci(self):
        lock_path = ROOT / "requirements-provider-capacity-governor.lock.txt"
        lock = lock_path.read_text(encoding="utf-8")
        self.assertNotIn("--index-url", lock)
        for package in (
            "jsonschema==4.25.1",
            "rfc3339-validator==",
            "jsonschema-specifications==",
            "referencing==",
            "rpds-py==",
        ):
            self.assertIn(package, lock)
        lines = lock.splitlines()
        package_indexes = [
            index
            for index, line in enumerate(lines)
            if line and not line.startswith(("#", " ")) and "==" in line
        ]
        self.assertGreater(len(package_indexes), 5)
        for index in package_indexes:
            self.assertIn("--hash=sha256:", lines[index + 1], lines[index])
        workflow = (ROOT / ".github" / "workflows" / "provider-capacity-governor.yml").read_text()
        self.assertIn("--require-hashes", workflow)
        self.assertIn(lock_path.name, workflow)


if __name__ == "__main__":
    unittest.main()
