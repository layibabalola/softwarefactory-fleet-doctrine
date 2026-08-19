from __future__ import annotations

import datetime as dt
import importlib.util
import json
import pathlib
import sys
import tempfile
import unittest

try:
    import jsonschema
except ImportError:  # pragma: no cover - portable stdlib broker remains usable
    jsonschema = None


ROOT = pathlib.Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "reference"
sys.path.insert(0, str(REFERENCE))
import fleet_capacity_broker as broker
import normalize_usage


@unittest.skipIf(jsonschema is None, "jsonschema package not installed")
class SchemaTests(unittest.TestCase):
    def load(self, relative):
        return json.loads((ROOT / relative).read_text(encoding="utf-8"))

    def test_fixtures_and_generated_decision_match_published_schemas(self):
        request = self.load("fixtures/request-product-work.json")
        snapshot = self.load("fixtures/snapshot-healthy.json")
        policy = self.load("fixtures/policy-default.json")
        for value, schema_path in (
            (request, "schema/admission-request-v1.schema.json"),
            (snapshot, "schema/capacity-snapshot-v1.schema.json"),
            (policy, "schema/policy-v1.schema.json"),
        ):
            jsonschema.validate(value, self.load(schema_path))
        with tempfile.TemporaryDirectory() as folder:
            instance = broker.Broker(pathlib.Path(folder) / "state.sqlite3")
            try:
                decision = instance.decide(
                    request, snapshot, policy,
                    dt.datetime(2026, 8, 18, 16, 0, 30, tzinfo=dt.timezone.utc),
                )
            finally:
                instance.close()
        jsonschema.validate(decision, self.load("schema/admission-decision-v1.schema.json"))

    def test_generated_usage_matches_published_schema(self):
        metadata = {
            "ts": "2026-08-18T16:00:00Z", "project": "fixture",
            "quota_domain": "anthropic:sha256:" + "a" * 64,
            "requested_model": "claude-opus-5", "requested_effort": "max",
            "terminal": "SUCCESS", "useful": True,
        }
        native = json.dumps({
            "timestamp": "2026-08-18T16:00:00Z", "type": "assistant", "sessionId": "s1",
            "message": {"id": "m1", "model": "claude-opus-5", "usage": {
                "input_tokens": 1, "cache_creation_input_tokens": 2,
                "cache_read_input_tokens": 3, "output_tokens": 4,
            }},
        })
        value = normalize_usage.normalize("anthropic", [native], metadata)
        jsonschema.validate(value, self.load("schema/usage-event-v1.schema.json"))


if __name__ == "__main__":
    unittest.main()
