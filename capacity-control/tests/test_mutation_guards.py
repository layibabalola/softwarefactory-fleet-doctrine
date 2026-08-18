from __future__ import annotations

import datetime as dt
import json
import pathlib
import sys
import types
import unittest


ROOT = pathlib.Path(__file__).parents[1]
SOURCE_PATH = ROOT / "reference" / "fleet_capacity_broker.py"
SOURCE = SOURCE_PATH.read_text(encoding="utf-8")
NOW = dt.datetime(2026, 8, 18, 16, 0, tzinfo=dt.timezone.utc)
DOMAIN = "anthropic:sha256:" + "a" * 64


def load_mutant(old: str, new: str, name: str):
    count = SOURCE.count(old)
    if count != 1:
        raise AssertionError(f"mutation {name} expected one site, found {count}")
    mutated = SOURCE.replace(old, new)
    module = types.ModuleType(name)
    module.__file__ = str(SOURCE_PATH)
    sys.modules[name] = module
    try:
        exec(compile(mutated, str(SOURCE_PATH), "exec"), module.__dict__)
    except BaseException:
        sys.modules.pop(name, None)
        raise
    return module


def policy() -> dict:
    return json.loads((ROOT / "policy" / "default-v1.json").read_text(encoding="utf-8"))


def request(priority: str = "PRODUCT_WORK", owner_override: bool = False) -> dict:
    return {
        "schema": "fleet-capacity-admission-request/v1",
        "request_id": "mutation-0001",
        "project": "cloudvore",
        "lane": "mutation-sentinel",
        "subject_digest": "sha256:" + "1" * 64,
        "role": "IMPLEMENT",
        "priority": priority,
        "profile": {
            "provider": "anthropic",
            "quota_domain": DOMAIN,
            "independence_class": "anthropic",
            "requested_model": "claude-opus-5",
            "requested_effort": "max",
            "transport": "fixture",
        },
        "issued_at": "2026-08-18T15:59:55Z",
        "expires_at": "2026-08-18T16:05:00Z",
        "budget": {
            "max_wall_seconds": 300,
            "max_turns": 8,
            "max_context_tokens": 100000,
            "window_estimates": {"five-hour": 0.15},
        },
        "quality_contract": {"requires_exact_profile": True, "role_cell_evidence": "fixture"},
        "owner_override": owner_override,
    }


def snapshot(used: float = 0.2, observed: str = "2026-08-18T15:59:50Z", started: str = "2026-08-18T15:00:00Z") -> dict:
    return {
        "schema": "fleet-capacity-snapshot/v1",
        "provider": "anthropic",
        "quota_domain": DOMAIN,
        "observed_at": observed,
        "windows": [{"name": "five-hour", "used_fraction": used, "resets_at": "2026-08-18T20:00:00Z", "window_started_at": started}],
        "source": {"kind": "fixture", "artifact_sha256": "2" * 64},
    }


class GuardMutationTests(unittest.TestCase):
    def test_removing_concurrency_guard_creates_double_admission_counterexample(self):
        mutant = load_mutant(
            'if len(active_leases) >= int(policy["max_concurrent_leases_per_domain"]):',
            'if False and len(active_leases) >= int(policy["max_concurrent_leases_per_domain"]):',
            "mutant_concurrency",
        )
        active = [{"window_estimates_json": '{"five-hour":0.01}'}]
        self.assertEqual("ADMIT", mutant.evaluate(request(), snapshot(), policy(), active, NOW).status)

    def test_removing_reserve_guard_spends_critical_work_reserve(self):
        mutant = load_mutant(
            "elif projected > 1.0 - reserve and not owner_override:",
            "elif False and projected > 1.0 - reserve and not owner_override:",
            "mutant_reserve",
        )
        self.assertEqual("ADMIT", mutant.evaluate(request(), snapshot(used=0.65), policy(), [], NOW).status)

    def test_removing_hard_cap_guard_lets_owner_override_exceed_cap(self):
        mutant = load_mutant(
            "if projected > 1.0:",
            "if False and projected > 1.0:",
            "mutant_hard_cap",
        )
        self.assertEqual(
            "ADMIT",
            mutant.evaluate(request("OWNER_FOREGROUND", True), snapshot(used=0.9), policy(), [], NOW).status,
        )

    def test_removing_staleness_guard_admits_old_meter(self):
        mutant = load_mutant(
            'elif age > int(policy["snapshot_max_age_seconds"]):',
            'elif False and age > int(policy["snapshot_max_age_seconds"]):',
            "mutant_stale",
        )
        old = snapshot(observed="2026-08-18T15:00:00Z")
        self.assertEqual("ADMIT", mutant.evaluate(request(), old, policy(), [], NOW).status)

    def test_removing_reset_quiet_guard_recreates_reset_burst(self):
        mutant = load_mutant(
            'request["priority"] == "BACKGROUND"',
            'False and request["priority"] == "BACKGROUND"',
            "mutant_quiet",
        )
        recent = snapshot(started="2026-08-18T15:59:30Z")
        self.assertEqual("ADMIT", mutant.evaluate(request("BACKGROUND"), recent, policy(), [], NOW).status)


if __name__ == "__main__":
    unittest.main(verbosity=2)
