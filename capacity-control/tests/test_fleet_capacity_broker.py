from __future__ import annotations

import datetime as dt
import contextlib
import importlib.util
import io
import json
import pathlib
import tempfile
import threading
import unittest
from unittest import mock


ROOT = pathlib.Path(__file__).resolve().parents[1]
MODULE = ROOT / "reference" / "fleet_capacity_broker.py"
SPEC = importlib.util.spec_from_file_location("fleet_capacity_broker", MODULE)
assert SPEC and SPEC.loader
broker = importlib.util.module_from_spec(SPEC)
import sys
sys.modules[SPEC.name] = broker
SPEC.loader.exec_module(broker)

NOW = dt.datetime(2026, 8, 18, 16, 0, tzinfo=dt.timezone.utc)
DOMAIN_A = "anthropic:sha256:" + "a" * 64
DOMAIN_B = "anthropic:sha256:" + "b" * 64


def policy() -> dict:
    value = json.loads((ROOT / "policy" / "default-v1.json").read_text(encoding="utf-8"))
    value["automatic_launch_gate"] = "open"
    return value


def request(request_id="req-0001", domain=DOMAIN_A, priority="PRODUCT_WORK", role="IMPLEMENT", **changes) -> dict:
    value = {
        "schema": broker.REQUEST_SCHEMA,
        "request_id": request_id,
        "project": "conjugal",
        "lane": "opus",
        "subject_digest": "sha256:" + "1" * 64,
        "role": role,
        "priority": priority,
        "profile": {
            "provider": "anthropic",
            "quota_domain": domain,
            "independence_class": "anthropic-claude",
            "requested_model": "claude-opus-5",
            "requested_effort": "max",
            "transport": "claude-code/2.1.233",
        },
        "issued_at": broker.iso(NOW - dt.timedelta(seconds=5)),
        "expires_at": broker.iso(NOW + dt.timedelta(minutes=2)),
        "budget": {
            "max_wall_seconds": 900,
            "max_turns": 16,
            "max_context_tokens": 100000,
            "window_estimates": {"five-hour": 0.15, "weekly": 0.02},
        },
        "quality_contract": {
            "requires_exact_profile": True,
            "role_cell_evidence": "conjugal:opus-max",
        },
        "owner_override": False,
    }
    value.update(changes)
    return value


def snapshot(domain=DOMAIN_A, used=0.2, observed=None, started=None, unknown=False) -> dict:
    observed = observed or NOW - dt.timedelta(seconds=10)
    started = started or NOW - dt.timedelta(hours=1)
    return {
        "schema": broker.SNAPSHOT_SCHEMA,
        "provider": "anthropic",
        "quota_domain": domain,
        "observed_at": broker.iso(observed),
        "windows": [
            {
                "name": "five-hour",
                "used_fraction": None if unknown else used,
                "resets_at": broker.iso(NOW + dt.timedelta(hours=4)),
                "window_started_at": broker.iso(started),
            },
            {
                "name": "weekly",
                "used_fraction": 0.3,
                "resets_at": broker.iso(NOW + dt.timedelta(days=4)),
                "window_started_at": broker.iso(NOW - dt.timedelta(days=3)),
            },
        ],
        "source": {"kind": "provider-api", "artifact_sha256": "2" * 64},
    }


class EvaluationTests(unittest.TestCase):
    def test_green_admission(self):
        self.assertEqual("ADMIT", broker.evaluate(request(), snapshot(), policy(), [], NOW).status)

    def test_closed_gate_and_policy_required_dimensions_refuse(self):
        closed = policy(); closed["automatic_launch_gate"] = "closed"
        self.assertIn("AUTOMATIC_LAUNCH_GATE_CLOSED", broker.evaluate(request(), snapshot(), closed, [], NOW).reasons)
        incomplete = request(); incomplete["budget"]["window_estimates"].pop("weekly")
        self.assertIn("WINDOW_ESTIMATE_MISSING", broker.evaluate(incomplete, snapshot(), policy(), [], NOW).reasons)

    def test_reserve_and_hard_cap(self):
        self.assertIn("RESERVE_FORECAST", broker.evaluate(request(), snapshot(used=0.65), policy(), [], NOW).reasons)
        self.assertIn("HARD_CAP_FORECAST", broker.evaluate(request(), snapshot(used=0.9), policy(), [], NOW).reasons)

    def test_owner_override_is_not_self_asserted(self):
        owner = request(priority="OWNER_FOREGROUND", owner_override=True)
        result = broker.evaluate(owner, snapshot(used=0.8), policy(), [], NOW)
        self.assertEqual("REFUSE", result.status)
        self.assertIn("OWNER_OVERRIDE_UNSUPPORTED", result.reasons)

    def test_stale_future_unknown_and_missing_refuse(self):
        stale = snapshot(observed=NOW - dt.timedelta(minutes=6))
        self.assertIn("SNAPSHOT_STALE", broker.evaluate(request(), stale, policy(), [], NOW).reasons)
        future = snapshot(observed=NOW + dt.timedelta(minutes=1))
        self.assertIn("SNAPSHOT_FROM_FUTURE", broker.evaluate(request(), future, policy(), [], NOW).reasons)
        self.assertIn("WINDOW_USAGE_UNKNOWN", broker.evaluate(request(), snapshot(unknown=True), policy(), [], NOW).reasons)
        missing = snapshot(); missing["windows"] = missing["windows"][1:]
        self.assertIn("WINDOW_MISSING", broker.evaluate(request(), missing, policy(), [], NOW).reasons)

    def test_background_observes_post_reset_quiet(self):
        req = request(priority="BACKGROUND")
        snap = snapshot(started=NOW - dt.timedelta(seconds=30))
        self.assertIn("POST_RESET_QUIET", broker.evaluate(req, snap, policy(), [], NOW).reasons)

    def test_request_expiry_and_future_refuse(self):
        expired = request(expires_at=broker.iso(NOW - dt.timedelta(seconds=1)))
        self.assertIn("REQUEST_EXPIRED", broker.evaluate(expired, snapshot(), policy(), [], NOW).reasons)
        future = request(issued_at=broker.iso(NOW + dt.timedelta(minutes=1)))
        self.assertIn("REQUEST_FROM_FUTURE", broker.evaluate(future, snapshot(), policy(), [], NOW).reasons)

    def test_quality_and_identity_are_required(self):
        bad = request(quality_contract={"requires_exact_profile": False, "role_cell_evidence": "x"})
        with self.assertRaisesRegex(broker.BrokerError, "exact profile"):
            broker.evaluate(bad, snapshot(), policy(), [], NOW)
        with self.assertRaisesRegex(broker.BrokerError, "quota domain"):
            broker.evaluate(request(), snapshot(domain=DOMAIN_B), policy(), [], NOW)
        wrong_provider_domain = request(domain="openai:sha256:" + "a" * 64)
        with self.assertRaisesRegex(broker.BrokerError, "provider prefix"):
            broker.evaluate(wrong_provider_domain, snapshot(domain=wrong_provider_domain["profile"]["quota_domain"]), policy(), [], NOW)

    def test_runtime_rejects_schema_drift(self):
        missing = request(); del missing["profile"]["transport"]
        with self.assertRaisesRegex(broker.BrokerError, "key set mismatch"):
            broker.evaluate(missing, snapshot(), policy(), [], NOW)
        extra = snapshot(); extra["unexpected"] = True
        with self.assertRaisesRegex(broker.BrokerError, "key set mismatch"):
            broker.evaluate(request(), extra, policy(), [], NOW)

    def test_file_intake_rejects_duplicate_keys_and_nonfinite_numbers(self):
        with tempfile.TemporaryDirectory() as folder:
            path = pathlib.Path(folder) / "value.json"
            path.write_text('{"a":1,"a":2}', encoding="utf-8")
            with self.assertRaisesRegex(broker.BrokerError, "DUPLICATE_JSON_KEY"):
                broker.read_json(path)
            path.write_text('{"a":NaN}', encoding="utf-8")
            with self.assertRaisesRegex(broker.BrokerError, "NONFINITE_JSON"):
                broker.read_json(path)

    def test_file_intake_pre_read_limit_and_cli_no_echo(self):
        with tempfile.TemporaryDirectory() as folder:
            path=pathlib.Path(folder)/"private-token.json"; path.write_text("{}",encoding="utf-8")
            with mock.patch.object(broker,"MAX_JSON_BYTES",1), self.assertRaisesRegex(broker.BrokerError,"JSON_TOO_LARGE"):
                broker.read_json(path)
            stderr=io.StringIO(); state=pathlib.Path(folder)/"state.sqlite3"
            with mock.patch.object(broker,"read_json",side_effect=broker.BrokerError("C:/private/token")), contextlib.redirect_stderr(stderr):
                code=broker.main(["decide","--request",str(path),"--snapshot",str(path),"--policy",str(path),"--state",str(state)])
            self.assertEqual(code,22); self.assertEqual(json.loads(stderr.getvalue()),{"error":"INPUT_REFUSED"}); self.assertNotIn("private",stderr.getvalue())


class TransactionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = pathlib.Path(self.temp.name) / "broker.sqlite3"
        initialized = broker.Broker(self.path)
        initialized.close()

    def tearDown(self):
        self.temp.cleanup()

    def open(self):
        return broker.Broker(self.path)

    def test_exact_replay_is_idempotent_and_conflict_refuses(self):
        instance = self.open()
        try:
            first = instance.decide(request(), snapshot(), policy(), NOW)
            second = instance.decide(request(), snapshot(), policy(), NOW + dt.timedelta(seconds=1))
            self.assertEqual(first, second)
            changed = request(); changed["lane"] = "fable"
            with self.assertRaises(broker.ConflictingReplay):
                instance.decide(changed, snapshot(), policy(), NOW)
        finally:
            instance.close()

    def test_same_domain_serializes_and_release_reopens(self):
        instance = self.open()
        try:
            first = instance.decide(request(), snapshot(), policy(), NOW)
            second = instance.decide(request("req-0002"), snapshot(), policy(), NOW)
            self.assertEqual("ADMIT", first["status"])
            self.assertEqual("HOLD", second["status"])
            self.assertIn("DOMAIN_CONCURRENCY_HELD", second["reason_codes"])
            self.assertTrue(instance.release(first["lease"]["lease_id"], "req-0001", "SUCCESS", at=NOW))
            third = instance.decide(request("req-0003"), snapshot(), policy(), NOW)
            self.assertEqual("ADMIT", third["status"])
        finally:
            instance.close()

    def test_distinct_accounts_run_independently(self):
        instance = self.open()
        try:
            self.assertEqual("ADMIT", instance.decide(request(), snapshot(), policy(), NOW)["status"])
            self.assertEqual("ADMIT", instance.decide(request("req-0002", DOMAIN_B), snapshot(DOMAIN_B), policy(), NOW)["status"])
        finally:
            instance.close()

    def test_expired_lease_reopens_without_manual_cleanup(self):
        short = policy(); short["lease_max_seconds"] = 1
        first_request = request()
        first_request["budget"]["max_wall_seconds"] = 1
        instance = self.open()
        try:
            self.assertEqual("ADMIT", instance.decide(first_request, snapshot(), short, NOW)["status"])
            later = NOW + dt.timedelta(seconds=2)
            req = request("req-0002", issued_at=broker.iso(later - dt.timedelta(seconds=1)), expires_at=broker.iso(later + dt.timedelta(minutes=1)))
            req["budget"]["max_wall_seconds"] = 1
            snap = snapshot(observed=later - dt.timedelta(seconds=1))
            for window in snap["windows"]:
                if window["window_started_at"]:
                    window["window_started_at"] = broker.iso(later - dt.timedelta(hours=1))
            self.assertEqual("ADMIT", instance.decide(req, snap, short, later)["status"])
        finally:
            instance.close()

    def test_sqlite_transaction_admits_only_one_concurrent_contender(self):
        barrier = threading.Barrier(2)
        statuses: list[str] = []
        errors: list[BaseException] = []

        def contender(index: int):
            instance = self.open()
            try:
                barrier.wait(timeout=5)
                result = instance.decide(request(f"req-000{index + 1}"), snapshot(), policy(), NOW)
                statuses.append(result["status"])
            except BaseException as exc:
                errors.append(exc)
            finally:
                instance.close()

        threads = [threading.Thread(target=contender, args=(i,)) for i in range(2)]
        for thread in threads: thread.start()
        for thread in threads: thread.join()
        self.assertFalse(errors)
        self.assertEqual(["ADMIT", "HOLD"], sorted(statuses))

    def test_budget_cannot_outlive_lease_or_request(self):
        instance = self.open()
        try:
            oversized = request()
            oversized["budget"]["max_wall_seconds"] = policy()["lease_max_seconds"] + 1
            refused = instance.decide(oversized, snapshot(), policy(), NOW)
            self.assertEqual("REFUSE", refused["status"])
            self.assertIn("BUDGET_EXCEEDS_LEASE_MAX", refused["reason_codes"])

            short_request = request("req-short")
            short_request["expires_at"] = broker.iso(NOW + dt.timedelta(seconds=30))
            admitted = instance.decide(short_request, snapshot(), policy(), NOW)
            self.assertEqual(broker.iso(NOW + dt.timedelta(seconds=30)), admitted["lease"]["expires_at"])
        finally:
            instance.close()

    def test_release_records_terminal_class_and_evidence(self):
        instance = self.open()
        try:
            admitted = instance.decide(request(), snapshot(), policy(), NOW)
            evidence = "sha256:" + "3" * 64
            self.assertTrue(instance.release(admitted["lease"]["lease_id"], "req-0001", "PAUSED_BUDGET", evidence, NOW))
            row = instance.db.execute(
                "SELECT payload_json FROM events WHERE event_kind='LEASE_RELEASED'"
            ).fetchone()
            payload = json.loads(row["payload_json"])
            self.assertEqual("PAUSED_BUDGET", payload["terminal_class"])
            self.assertEqual(evidence, payload["evidence_digest"])
            replay = instance.decide(request(), snapshot(), policy(), NOW + dt.timedelta(seconds=1))
            self.assertEqual("REFUSE", replay["status"])
            self.assertEqual(["TERMINAL_REQUEST_REPLAY"], replay["reason_codes"])
            self.assertIsNone(replay["lease"])
        finally:
            instance.close()


if __name__ == "__main__":
    unittest.main()
