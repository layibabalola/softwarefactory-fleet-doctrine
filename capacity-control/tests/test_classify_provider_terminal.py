from __future__ import annotations

import importlib.util
import pathlib
import sys
import unittest


MODULE = pathlib.Path(__file__).parents[1] / "reference" / "classify_provider_terminal.py"
SPEC = importlib.util.spec_from_file_location("classify_provider_terminal", MODULE)
assert SPEC and SPEC.loader
classifier = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = classifier
SPEC.loader.exec_module(classifier)


class ClassifierTests(unittest.TestCase):
    def test_claude_session_limit_and_reset_are_typed(self):
        result = classifier.classify(
            "anthropic",
            "You've reached your session limit. Your limit resets 2026-08-18T20:00:00Z.",
        )
        self.assertEqual("QUOTA_BLOCKED", result["terminal"])
        self.assertEqual("SESSION_LIMIT", result["reason"])
        self.assertEqual("2026-08-18T20:00:00Z", result["reset_at"])

    def test_model_qualified_session_limit_is_recognized(self):
        result = classifier.classify("anthropic", "Reached your Fable 5 session limit; try later")
        self.assertEqual("QUOTA_BLOCKED", result["terminal"])

    def test_structured_429_wins_without_provider_specific_prose(self):
        result = classifier.classify("xai", '{"error":{"status":429,"code":"capacity"}}')
        self.assertEqual("QUOTA_BLOCKED", result["terminal"])
        self.assertEqual("HTTP_429", result["reason"])

    def test_auth_is_not_misclassified_as_quota(self):
        result = classifier.classify("moonshot", "Authentication required")
        self.assertEqual("REFUSED", result["terminal"])
        self.assertEqual("AUTH_REQUIRED", result["reason"])

    def test_unknown_output_is_unevaluable_and_raw_text_is_not_returned(self):
        raw = "unexpected transport costume"
        result = classifier.classify("openai", raw)
        self.assertEqual("UNEVALUABLE", result["terminal"])
        self.assertNotIn(raw, str(result))
        self.assertEqual(64, len(result["raw_sha256"]))

    def test_input_is_bounded(self):
        with self.assertRaisesRegex(classifier.ClassificationError, "bounded"):
            classifier.classify("anthropic", "x" * 262_145)


if __name__ == "__main__":
    unittest.main(verbosity=2)
