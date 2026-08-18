from __future__ import annotations

import datetime as dt
import importlib.util
import json
import pathlib
import sys
import tempfile
import unittest

import jsonschema


ROOT = pathlib.Path(__file__).parents[1]
FORMAT = jsonschema.FormatChecker()


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def module(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    assert spec and spec.loader
    value = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = value
    spec.loader.exec_module(value)
    return value


class SchemaTests(unittest.TestCase):
    def assert_valid(self, instance: dict, schema_name: str) -> None:
        jsonschema.Draft202012Validator(
            load(f"schema/{schema_name}"), format_checker=FORMAT
        ).validate(instance)

    def test_request_snapshot_and_policy_fixtures(self) -> None:
        self.assert_valid(load("fixtures/request-product-work.json"), "admission-request-v1.schema.json")
        self.assert_valid(load("fixtures/snapshot-healthy.json"), "capacity-snapshot-v1.schema.json")
        self.assert_valid(load("fixtures/policy-default.json"), "policy-v1.schema.json")
        self.assertEqual(load("policy/default-v1.json"), load("fixtures/policy-default.json"))

    def test_real_broker_decision_matches_decision_schema(self) -> None:
        broker = module("schema_broker", "reference/fleet_capacity_broker.py")
        request = load("fixtures/request-product-work.json")
        snapshot = load("fixtures/snapshot-healthy.json")
        policy = load("fixtures/policy-default.json")
        now = dt.datetime(2026, 8, 18, 16, 0, tzinfo=dt.timezone.utc)
        with tempfile.TemporaryDirectory() as folder:
            instance = broker.Broker(pathlib.Path(folder) / "state.sqlite3")
            try:
                decision = instance.decide(request, snapshot, policy, now)
            finally:
                instance.close()
        self.assert_valid(decision, "admission-decision-v1.schema.json")

    def test_real_normalized_usage_matches_usage_schema(self) -> None:
        normalizer = module("schema_normalizer", "reference/normalize_usage.py")
        metadata = {
            "ts": "2026-08-18T16:00:00Z",
            "project": "cloudvore",
            "quota_domain": "anthropic:sha256:" + "a" * 64,
            "requested_model": "claude-opus-5",
            "requested_effort": "max",
            "terminal": "SUCCESS",
            "useful": True,
            "evidence_digest": "sha256:" + "e" * 64,
        }
        event = {
            "timestamp": "2026-08-18T16:00:00Z",
            "type": "assistant",
            "sessionId": "session-fixture",
            "message": {
                "id": "message-fixture",
                "model": "claude-opus-5",
                "usage": {"input_tokens": 2, "output_tokens": 1},
            },
        }
        result = normalizer.normalize("anthropic", [json.dumps(event)], metadata)
        self.assert_valid(result, "usage-event-v1.schema.json")


if __name__ == "__main__":
    unittest.main(verbosity=2)
