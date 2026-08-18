import copy
import importlib.util
import json
import shutil
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
            "seat_id": "review-seat",
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
                with self.assertRaisesRegex(MODULE.ContractError, "SCHEMA_VALIDATION_FAILED|RFC3339_INVALID"):
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
        with self.assertRaisesRegex(MODULE.ContractError, "SCHEMA_VALIDATION_FAILED"):
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

    def test_r3_red_impossible_claimant_timelines_are_r4_green_rejected(self):
        cases = (
            {"startup_fence_expires_at": "2026-08-18T15:58:00Z"},
            {"startup_fence_expires_at": "2026-08-18T15:57:59Z"},
            {"cooldown_expires_at": "2026-08-18T15:58:00Z"},
            {"cooldown_expires_at": "2026-08-18T15:57:59Z"},
            {"startup_fence_expires_at": "2026-08-18T16:10:00Z"},
            {"startup_fence_expires_at": "2026-08-18T16:10:01Z"},
            {"cooldown_expires_at": "2026-08-18T16:10:00Z"},
            {"cooldown_expires_at": "2026-08-18T16:10:01Z"},
        )
        for changes in cases:
            with self.subTest(changes=changes):
                snapshot = copy.deepcopy(self.snapshot)
                snapshot["active_leases"].append(self._lease(**changes))
                with self.assertRaisesRegex(MODULE.ContractError, "CLAIMANT_TIMELINE_INVALID"):
                    MODULE.decide(snapshot)

    def test_r3_red_duplicate_claimant_identities_are_r4_green_rejected(self):
        unique_second = {
            "lease_id": "existing-lease-0002",
            "process_id": 4343,
            "process_start_time": "2026-08-18T15:58:30Z",
            "seat_id": "implementation-seat",
            "seat_epoch": 8,
            "registered_session_id_hash": "sha256:" + "d" * 64,
            "observed_session_id_hash": "sha256:" + "d" * 64,
        }
        collisions = (
            {"lease_id": "existing-lease-0001"},
            {"process_id": 4242, "process_start_time": "2026-08-18T15:58:00Z"},
            {"process_id": 4242, "process_start_time": "2026-08-18T10:58:00-05:00"},
            {
                "registered_session_id_hash": "sha256:" + "c" * 64,
                "observed_session_id_hash": "sha256:" + "c" * 64,
            },
            {
                "registered_session_id_hash": "c" * 64,
                "observed_session_id_hash": "c" * 64,
            },
            {"seat_id": "review-seat", "seat_epoch": 7},
            {"seat_id": "REVIEW-SEAT", "seat_epoch": 7},
        )
        for collision in collisions:
            with self.subTest(collision=collision):
                snapshot = copy.deepcopy(self.snapshot)
                snapshot["active_leases"].append(self._lease())
                second = dict(unique_second)
                second.update(collision)
                snapshot["active_leases"].append(self._lease(**second))
                with self.assertRaisesRegex(MODULE.ContractError, "CLAIMANT_IDENTITY_COLLISION"):
                    MODULE.decide(snapshot)

    def test_r4_red_row_local_session_prefix_variants_are_r5_green_equivalent(self):
        digest = "c" * 64
        for registered, observed in (
            ("sha256:" + digest, digest),
            (digest, "sha256:" + digest),
        ):
            with self.subTest(registered_prefixed=registered.startswith("sha256:")):
                snapshot = copy.deepcopy(self.snapshot)
                snapshot["active_leases"].append(
                    self._lease(
                        registered_session_id_hash=registered,
                        observed_session_id_hash=observed,
                    )
                )
                decision = MODULE.decide(snapshot)
                self.assertEqual("DENY", decision["decision"])
                self.assertIn("CONCURRENCY_LIMIT", decision["reason_codes"])
                self.assertNotIn("IDENTITY_AMBIGUOUS", decision["reason_codes"])

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
        with self.assertRaisesRegex(MODULE.ContractError, "SCHEMA_VALIDATION_FAILED"):
            MODULE.validate_usage_event(event)

    def test_r1_red_idle_with_omitted_counter_or_tokens_is_r2_green_rejected(self):
        base = json.loads((ROOT / "examples" / "provider-usage-events-v1.jsonl").read_text().splitlines()[1])
        missing = copy.deepcopy(base)
        missing["measurement"].pop("request_count")
        with self.assertRaisesRegex(MODULE.ContractError, "SCHEMA_VALIDATION_FAILED"):
            MODULE.validate_usage_event(missing)
        inferred = copy.deepcopy(base)
        inferred["measurement"]["input_tokens"] = 999
        with self.assertRaisesRegex(MODULE.ContractError, "SCHEMA_VALIDATION_FAILED"):
            MODULE.validate_usage_event(inferred)

    def test_raw_identity_or_credentials_are_rejected(self):
        event = json.loads((ROOT / "examples" / "provider-usage-events-v1.jsonl").read_text().splitlines()[0])
        event["account_email"] = "forbidden@example.invalid"
        with self.assertRaisesRegex(MODULE.ContractError, "PRIVACY_VALUE_PROHIBITED"):
            MODULE.validate_usage_event(event)

    def test_r1_red_extra_identity_field_is_r2_green_schema_failure(self):
        event = json.loads((ROOT / "examples" / "provider-usage-events-v1.jsonl").read_text().splitlines()[0])
        event["account_identifier"] = "real-account@example.invalid"
        with self.assertRaisesRegex(MODULE.ContractError, "SCHEMA_VALIDATION_FAILED|PRIVACY_VALUE_PROHIBITED"):
            MODULE.validate_usage_event(event)

    def test_r2_red_email_and_unsafe_paths_are_r3_green_rejected(self):
        base = json.loads((ROOT / "examples" / "provider-usage-events-v1.jsonl").read_text().splitlines()[0])
        email = copy.deepcopy(base)
        email["actor"]["role"] = "real-account@example.invalid"
        with self.assertRaisesRegex(MODULE.ContractError, "PRIVACY_VALUE_PROHIBITED"):
            MODULE.validate_usage_event(email)
        for embedded_path in (
            "x/C:/Users/Alice/secret",
            "safe//home/alice/secret",
            "prefix/Users/Alice/secret",
        ):
            with self.subTest(embedded_path=embedded_path):
                disguised_path = copy.deepcopy(base)
                disguised_path["model_requested"] = embedded_path
                with self.assertRaisesRegex(MODULE.ContractError, "PRIVACY_VALUE_PROHIBITED"):
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
                    "PRIVACY_VALUE_PROHIBITED",
                ):
                    MODULE.validate_usage_event(event)

    def test_r4_red_embedded_drive_relative_user_paths_are_r5_green_rejected(self):
        base = json.loads((ROOT / "examples" / "provider-usage-events-v1.jsonl").read_text().splitlines()[0])
        variants = (
            "x/C:Users/Alice/secret",
            "x/c:uSeRs/Alice/secret",
            r"x/C:Users\Alice\secret",
        )
        for value in variants:
            with self.subTest(value_kind="drive-relative"):
                event = copy.deepcopy(base)
                event["model_requested"] = value
                with self.assertRaisesRegex(MODULE.ContractError, "PRIVACY_VALUE_PROHIBITED"):
                    MODULE.validate_usage_event(event)

        escaped = copy.deepcopy(base)
        escaped["model_requested"] = r"x/C:Users\Alice\secret"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "embedded-drive-relative.jsonl"
            path.write_text(json.dumps(escaped) + "\n", encoding="utf-8")
            result = self._run_cli("validate-events", path)
            self.assertEqual(2, result.returncode, result.stdout)
            self.assertIn("PRIVACY_VALUE_PROHIBITED", result.stdout)
            self.assertNotIn("Alice", result.stdout)

    def test_r5_red_generic_drive_relative_components_are_r6_green_rejected(self):
        base = json.loads((ROOT / "examples" / "provider-usage-events-v1.jsonl").read_text().splitlines()[0])
        variants = (
            "x/C:Private/SENTINEL_DRIVE_SECRET",
            "C:Temp/SENTINEL_DRIVE_SECRET",
            r"x\c:pRiVaTe\SENTINEL_DRIVE_SECRET",
            "x/Ｃ：Ｐｒｉｖａｔｅ/SENTINEL_DRIVE_SECRET",
        )
        for value in variants:
            with self.subTest(value_kind="normalized-drive-relative"):
                event = copy.deepcopy(base)
                event["model_requested"] = value
                with self.assertRaisesRegex(
                    MODULE.ContractError,
                    "PRIVACY_VALUE_PROHIBITED",
                ) as caught:
                    MODULE.validate_usage_event(event)
                self.assertNotIn("SENTINEL_DRIVE_SECRET", str(caught.exception))

        event = copy.deepcopy(base)
        event["actor"]["role"] = r"prefix\C:Private\SENTINEL_JSON_ESCAPED_SECRET"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "drive-relative.jsonl"
            path.write_text(json.dumps(event) + "\n", encoding="utf-8")
            result = self._run_cli("validate-events", path)
            self.assertEqual(2, result.returncode, result.stdout)
            self.assertIn("reason=PRIVACY_VALUE_PROHIBITED", result.stdout)
            self.assertNotIn(
                "SENTINEL_JSON_ESCAPED_SECRET",
                result.stdout + result.stderr,
            )

    def test_r5_red_cli_errors_are_r6_green_stable_and_never_echo_input(self):
        base = json.loads((ROOT / "examples" / "provider-usage-events-v1.jsonl").read_text().splitlines()[0])
        schema_cases = []
        pattern = copy.deepcopy(base)
        pattern["project"] = "SENTINEL PATTERN SECRET"
        schema_cases.append(("pattern", "SENTINEL PATTERN SECRET", pattern))
        enum = copy.deepcopy(base)
        enum["event"] = "SENTINEL_ENUM_SECRET"
        schema_cases.append(("enum", "SENTINEL_ENUM_SECRET", enum))
        typed = copy.deepcopy(base)
        typed["seat_epoch"] = "SENTINEL_TYPE_SECRET"
        schema_cases.append(("type", "SENTINEL_TYPE_SECRET", typed))
        additional = copy.deepcopy(base)
        additional["SENTINEL_ADDITIONAL_SECRET"] = "opaque"
        schema_cases.append(
            ("additionalProperties", "SENTINEL_ADDITIONAL_SECRET", additional)
        )

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for validator, sentinel, event in schema_cases:
                with self.subTest(failure=validator):
                    path = root / f"{validator}.jsonl"
                    path.write_text(json.dumps(event) + "\n", encoding="utf-8")
                    result = self._run_cli("validate-events", path)
                    self.assertEqual(2, result.returncode, result.stdout)
                    self.assertIn(f"validator={validator}", result.stdout)
                    self.assertIn("reason=SCHEMA_VALIDATION_FAILED", result.stdout)
                    self.assertNotIn(sentinel, result.stdout + result.stderr)

            byte_cases = (
                (
                    "duplicate.jsonl",
                    b'{"SENTINEL_DUPLICATE_SECRET":1,"SENTINEL_DUPLICATE_SECRET":2}\n',
                    "SENTINEL_DUPLICATE_SECRET",
                    "JSON_DUPLICATE_KEY",
                ),
                (
                    "malformed.jsonl",
                    b'{"SENTINEL_MALFORMED_SECRET":\n',
                    "SENTINEL_MALFORMED_SECRET",
                    "JSON_MALFORMED",
                ),
                (
                    "nonfinite.jsonl",
                    b'{"SENTINEL_NONFINITE_SECRET":NaN}\n',
                    "SENTINEL_NONFINITE_SECRET",
                    "JSON_NONFINITE_NUMBER",
                ),
                (
                    "utf8.jsonl",
                    b'{"x":"SENTINEL_UTF8_SECRET"}\xff\n',
                    "SENTINEL_UTF8_SECRET",
                    "UTF8_INVALID",
                ),
            )
            for name, payload, sentinel, reason in byte_cases:
                with self.subTest(failure=reason):
                    path = root / name
                    path.write_bytes(payload)
                    result = self._run_cli("validate-events", path)
                    self.assertEqual(2, result.returncode, result.stdout)
                    self.assertIn(f"reason={reason}", result.stdout)
                    self.assertNotIn(sentinel, result.stdout + result.stderr)
                    report = json.loads(result.stdout)
                    self.assertEqual(1, len(report["errors"]))
                    self.assertRegex(
                        report["errors"][0],
                        r"^location=[^;]+;validator=[A-Za-z0-9.$_-]+;reason=[A-Z0-9_]+$",
                    )

        argument_sentinel = "SENTINEL_INVALID_COMMAND_SECRET"
        result = self._run_cli(argument_sentinel)
        self.assertEqual(2, result.returncode, result.stdout)
        self.assertIn("reason=CLI_ARGUMENT_INVALID", result.stdout)
        self.assertNotIn(argument_sentinel, result.stdout + result.stderr)

        missing_sentinel = "SENTINEL_MISSING_PATH_SECRET.json"
        result = self._run_cli("decide", Path(tempfile.gettempdir()) / missing_sentinel)
        self.assertEqual(2, result.returncode, result.stdout)
        self.assertEqual("", result.stderr)
        self.assertIn("reason=IO_ERROR", result.stdout)
        self.assertNotIn(missing_sentinel, result.stdout + result.stderr)

    def test_r6_red_resource_boundaries_are_r7_green_in_real_subprocesses(self):
        def assert_complexity(result):
            self.assertEqual(2, result.returncode, result.stdout)
            self.assertEqual("", result.stderr)
            self.assertIn("reason=JSON_COMPLEXITY_LIMIT", result.stdout)
            self.assertNotIn("Traceback", result.stdout)

        def assert_within_shape_limit(result):
            self.assertEqual(2, result.returncode, result.stdout)
            self.assertEqual("", result.stderr)
            self.assertNotIn("reason=JSON_COMPLEXITY_LIMIT", result.stdout)
            self.assertRegex(
                result.stdout,
                r"reason=(?:CONTRACT_INVALID|SCHEMA_VALIDATION_FAILED)",
            )

        snapshot_bytes = (ROOT / "examples" / "provider-admission-snapshot-v1.json").read_bytes()
        base_event = json.loads(
            (ROOT / "examples" / "provider-usage-events-v1.jsonl").read_text().splitlines()[0]
        )
        compact_event = json.dumps(base_event, separators=(",", ":")).encode("utf-8")

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            exact_input = root / "exact-input.json"
            exact_input.write_bytes(
                snapshot_bytes + b" " * (MODULE.MAX_INPUT_BYTES - len(snapshot_bytes))
            )
            accepted = self._run_cli("decide", exact_input)
            self.assertEqual(0, accepted.returncode, accepted.stdout)
            self.assertEqual("", accepted.stderr)
            over_input = root / "over-input.json"
            over_input.write_bytes(exact_input.read_bytes() + b" ")
            assert_complexity(self._run_cli("decide", over_input))

            exact_line = root / "exact-line.jsonl"
            exact_line.write_bytes(
                compact_event
                + b" " * (MODULE.MAX_JSONL_LINE_BYTES - len(compact_event))
                + b"\n"
            )
            accepted = self._run_cli("validate-events", exact_line)
            self.assertEqual(0, accepted.returncode, accepted.stdout)
            self.assertEqual("", accepted.stderr)
            over_line = root / "over-line.jsonl"
            over_line.write_bytes(exact_line.read_bytes()[:-1] + b" \n")
            assert_complexity(self._run_cli("validate-events", over_line))

            events = []
            for index in range(MODULE.MAX_JSONL_LINES + 1):
                event = copy.deepcopy(base_event)
                event["event_id"] = f"limit-event-{index:04d}"
                events.append(json.dumps(event, separators=(",", ":")))
            exact_lines = root / "exact-lines.jsonl"
            exact_lines.write_text(
                "\n".join(events[: MODULE.MAX_JSONL_LINES]) + "\n",
                encoding="utf-8",
            )
            accepted = self._run_cli("validate-events", exact_lines)
            self.assertEqual(0, accepted.returncode, accepted.stdout)
            self.assertEqual("", accepted.stderr)
            over_lines = root / "over-lines.jsonl"
            over_lines.write_text("\n".join(events) + "\n", encoding="utf-8")
            assert_complexity(self._run_cli("validate-events", over_lines))

            shape_twins = []
            exact_depth = "[" * (MODULE.MAX_JSON_DEPTH - 1) + "0" + "]" * (
                MODULE.MAX_JSON_DEPTH - 1
            )
            over_depth = "[" * MODULE.MAX_JSON_DEPTH + "0" + "]" * MODULE.MAX_JSON_DEPTH
            shape_twins.append(("depth", exact_depth, over_depth))

            exact_object = {f"k{index:03d}": 0 for index in range(MODULE.MAX_OBJECT_MEMBERS)}
            over_object = dict(exact_object)
            over_object["overflow"] = 0
            shape_twins.append(
                ("object-members", json.dumps(exact_object), json.dumps(over_object))
            )

            exact_array = [0] * MODULE.MAX_ARRAY_ITEMS
            over_array = exact_array + [0]
            shape_twins.append(
                ("array-items", json.dumps(exact_array), json.dumps(over_array))
            )

            def node_tree(total_nodes):
                list_count = 16
                scalar_count = total_nodes - 1 - list_count
                groups = []
                for _ in range(list_count):
                    width = min(MODULE.MAX_ARRAY_ITEMS, scalar_count)
                    groups.append([0] * width)
                    scalar_count -= width
                self.assertEqual(0, scalar_count)
                return groups

            shape_twins.append(
                (
                    "total-nodes",
                    json.dumps(node_tree(MODULE.MAX_TOTAL_NODES)),
                    json.dumps(node_tree(MODULE.MAX_TOTAL_NODES + 1)),
                )
            )

            for name, exact_payload, over_payload in shape_twins:
                with self.subTest(limit=name):
                    exact_path = root / f"exact-{name}.jsonl"
                    exact_path.write_text(exact_payload + "\n", encoding="utf-8")
                    assert_within_shape_limit(
                        self._run_cli("validate-events", exact_path)
                    )
                    over_path = root / f"over-{name}.jsonl"
                    over_path.write_text(over_payload + "\n", encoding="utf-8")
                    assert_complexity(self._run_cli("validate-events", over_path))

            deep_sentinel = "SENTINEL_1800_NESTING_SECRET"
            deep_path = root / "deep-1800.jsonl"
            deep_path.write_text(
                "[" * 1800 + json.dumps(deep_sentinel) + "]" * 1800 + "\n",
                encoding="utf-8",
            )
            deep_result = self._run_cli("validate-events", deep_path)
            assert_complexity(deep_result)
            self.assertNotIn(deep_sentinel, deep_result.stdout + deep_result.stderr)

    def test_r6_red_broken_schema_ref_is_r7_green_sanitized_in_subprocess(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tool_root = root / "tools"
            schema_root = root / "schemas"
            tool_root.mkdir()
            schema_root.mkdir()
            copied_tool = tool_root / MODULE_PATH.name
            shutil.copy2(MODULE_PATH, copied_tool)
            for schema_name in (
                "provider-admission-snapshot-v1.schema.json",
                "provider-usage-event-v1.schema.json",
            ):
                shutil.copy2(ROOT / "schemas" / schema_name, schema_root / schema_name)
            usage_schema = schema_root / "provider-usage-event-v1.schema.json"
            original_schema = usage_schema.read_text(encoding="utf-8")
            cases = (
                ("SENTINEL_BROKEN_REF_SECRET", "#/$defs/SENTINEL_BROKEN_REF_SECRET"),
                (
                    "SENTINEL_EXTERNAL_REF_SECRET",
                    "https://example.invalid/SENTINEL_EXTERNAL_REF_SECRET",
                ),
            )
            for sentinel, replacement in cases:
                with self.subTest(ref_kind=sentinel):
                    usage_schema.write_text(
                        original_schema.replace(
                            "#/$defs/nonNegativeOrUnknown",
                            replacement,
                        ),
                        encoding="utf-8",
                    )
                    result = subprocess.run(
                        [
                            sys.executable,
                            str(copied_tool),
                            "validate-events",
                            str(ROOT / "examples" / "provider-usage-events-v1.jsonl"),
                        ],
                        cwd=ROOT,
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                    self.assertEqual(2, result.returncode, result.stdout)
                    self.assertEqual("", result.stderr)
                    self.assertIn("reason=SCHEMA_REFERENCE_ERROR", result.stdout)
                    self.assertNotIn(sentinel, result.stdout + result.stderr)
                    self.assertNotIn(str(root), result.stdout + result.stderr)
                    self.assertNotIn("Traceback", result.stdout + result.stderr)

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
                    self.assertRegex(result.stdout, "JSON_DUPLICATE_KEY|JSON_NONFINITE_NUMBER")

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
                    self.assertRegex(result.stdout, "JSON_DUPLICATE_KEY|JSON_NONFINITE_NUMBER|UTF8_INVALID")

    def test_every_snapshot_date_time_is_explicitly_parsed(self):
        self.snapshot["active_leases"].append(
            self._lease(
                quota_domain_id="anthropic/hmac-sha256:ffffffffffffffffffffffffffffffff",
                process_status="dead",
                startup_fence_expires_at="not-a-date-time",
            )
        )
        with self.assertRaisesRegex(MODULE.ContractError, "SCHEMA_VALIDATION_FAILED|RFC3339_INVALID"):
            MODULE.decide(self.snapshot)

    def test_schema_or_validator_absence_fails_closed(self):
        MODULE._schema_validator.cache_clear()
        with mock.patch.object(MODULE, "jsonschema", None):
            with self.assertRaisesRegex(MODULE.ContractError, "SCHEMA_VALIDATOR_UNAVAILABLE"):
                MODULE.decide(self.snapshot)
        MODULE._schema_validator.cache_clear()
        with mock.patch.object(MODULE, "SCHEMA_ROOT", ROOT / "schemas-does-not-exist"):
            with self.assertRaisesRegex(MODULE.ContractError, "SCHEMA_UNAVAILABLE_OR_INVALID"):
                MODULE.decide(self.snapshot)
        MODULE._schema_validator.cache_clear()

    def test_r3_red_schema_bytes_use_r4_green_strict_decoder(self):
        original = (ROOT / "schemas" / "provider-admission-snapshot-v1.schema.json").read_bytes()
        decoded = original.decode("utf-8")
        cases = {
            "duplicate": decoded.replace(
                '"$schema":',
                '"$schema": "duplicate", "$schema":',
                1,
            ).encode("utf-8"),
            "nonfinite": decoded.replace('"title":', '"extension": NaN, "title":', 1).encode("utf-8"),
            "invalid-utf8": b"\xff",
        }
        with tempfile.TemporaryDirectory() as directory:
            schema_root = Path(directory)
            for name, payload in cases.items():
                with self.subTest(name=name):
                    (schema_root / "provider-admission-snapshot-v1.schema.json").write_bytes(payload)
                    MODULE._schema_validator.cache_clear()
                    with mock.patch.object(MODULE, "SCHEMA_ROOT", schema_root):
                        with self.assertRaisesRegex(
                            MODULE.ContractError,
                            "JSON_DUPLICATE_KEY|JSON_NONFINITE_NUMBER|UTF8_INVALID",
                        ):
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
