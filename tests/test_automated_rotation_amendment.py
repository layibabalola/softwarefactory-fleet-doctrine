from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "schemas" / "automated-rotation-window-v1.schema.json").read_text(encoding="utf-8"))
CANDIDATE = (ROOT / "ruling-candidates" / "automated-bounded-rotation-r1.md").read_text(encoding="utf-8")


def sample() -> dict[str, object]:
    return {
        "window_id": "48d9f765-055d-4b87-9208-d4f4d4555fc9",
        "project": "agent-bridge",
        "provider_family": "anthropic",
        "quota_identity_hash": "A" * 64,
        "policy_sha256": "B" * 64,
        "candidate_subject_sha256": "C" * 64,
        "authorized_lanes": ["FABLE", "OPUS", "SONNET"],
        "issued_at": "2026-08-19T04:30:00Z",
        "expires_at": "2026-08-20T04:30:00Z",
        "max_runs": 288,
        "max_wall_seconds": 1800,
        "max_turns": 16,
        "max_context_tokens": 100000,
        "min_interval_seconds": 60,
        "signature_hmac_sha256": "D" * 64,
        "authority": "LOCAL_OWNER_AUTOMATION_WINDOW_ZERO_ADOPTION_AUTHORITY",
        "schema_version": 1,
    }


class AutomatedRotationAmendmentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = Draft202012Validator(SCHEMA, format_checker=FormatChecker())

    def test_exact_window_passes(self) -> None:
        self.assertEqual([], list(self.validator.iter_errors(sample())))

    def test_extra_fields_duplicate_lanes_and_excess_ceilings_fail(self) -> None:
        for mutation in (
            {"unexpected": True},
            {"authorized_lanes": ["FABLE", "FABLE"]},
            {"max_runs": 289},
            {"max_wall_seconds": 1801},
            {"max_turns": 17},
            {"max_context_tokens": 100001},
            {"min_interval_seconds": 59},
        ):
            value = sample()
            value.update(mutation)
            self.assertTrue(list(self.validator.iter_errors(value)), mutation)

    def test_candidate_is_explicitly_zero_authority_and_no_auto_renew(self) -> None:
        normalized_candidate = " ".join(CANDIDATE.split())
        for required in (
            "CANDIDATE / ZERO AUTHORITY / NO DEPLOYMENT",
            "one inference-bearing root per quota domain",
            "may not extend a window, auto-renew it, increase concurrency",
            "Planning is not launch authority",
            "every provider-bearing automatic gate remains",
            "3dc9100507c35e3724200dabaa3df6ffd2eb3cd0",
            "Neither project-local mechanism ratifies the other",
        ):
            self.assertIn(required, normalized_candidate)


if __name__ == "__main__":
    unittest.main()
