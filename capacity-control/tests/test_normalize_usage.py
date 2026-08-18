from __future__ import annotations

import importlib.util
import json
import pathlib
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
MODULE = ROOT / "reference" / "normalize_usage.py"
SPEC = importlib.util.spec_from_file_location("normalize_usage", MODULE)
assert SPEC and SPEC.loader
normalizer = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = normalizer
SPEC.loader.exec_module(normalizer)


META = {
    "ts": "2026-08-18T16:00:00Z",
    "project": "fixture",
    "quota_domain": "provider:sha256:" + "a" * 64,
    "requested_model": "requested",
    "requested_effort": "high",
    "terminal": "SUCCESS",
    "useful": True,
}


def lines(*values):
    return [json.dumps(value) for value in values]


class NormalizeTests(unittest.TestCase):
    def test_anthropic_deduplicates_message_snapshots(self):
        event = {"timestamp":"2026-08-18T16:00:00Z","type":"assistant","sessionId":"s1","message":{"id":"m1","model":"claude-opus-5","usage":{"input_tokens":2,"cache_creation_input_tokens":100,"cache_read_input_tokens":200,"output_tokens":10,"output_tokens_details":{"thinking_tokens":4}}}}
        result = normalizer.normalize("anthropic", lines(event, event), META)
        self.assertEqual(102, result["usage"]["input_tokens"])
        self.assertEqual(200, result["usage"]["cached_input_tokens"])
        self.assertEqual(1, result["usage"]["turns"])
        self.assertEqual("claude-opus-5", result["effective_profile"]["model"])

    def test_openai_uses_latest_cumulative_total(self):
        first = {"timestamp":"2026-08-18T16:00:00Z","type":"event_msg","payload":{"type":"token_count","info":{"total_token_usage":{"input_tokens":10,"cached_input_tokens":5,"output_tokens":2,"reasoning_output_tokens":1},"last_token_usage":{}}}}
        second = {"timestamp":"2026-08-18T16:00:01Z","type":"event_msg","payload":{"type":"token_count","info":{"total_token_usage":{"input_tokens":30,"cached_input_tokens":20,"output_tokens":5,"reasoning_output_tokens":3},"last_token_usage":{}}}}
        result = normalizer.normalize("openai", lines(first, second), META)
        self.assertEqual(30, result["usage"]["input_tokens"])
        self.assertEqual(20, result["usage"]["cached_input_tokens"])
        self.assertEqual(2, result["usage"]["turns"])

    def test_moonshot_counts_only_usage_record_not_duplicate_step_end(self):
        record = {"type":"usage.record","model":"kimi-code/k3","usage":{"inputOther":10,"output":3,"inputCacheRead":20,"inputCacheCreation":2},"usageScope":"turn","time":1000}
        duplicate = {"type":"context.append_loop_event","event":{"type":"step.end","usage":record["usage"]},"time":1001}
        result = normalizer.normalize("moonshot", lines(record, duplicate), META)
        self.assertEqual(12, result["usage"]["input_tokens"])
        self.assertEqual(20, result["usage"]["cached_input_tokens"])
        self.assertEqual(1, result["usage"]["turns"])

    def test_xai_uses_latest_cumulative_turn_completed(self):
        def event(ts, input_tokens, turns):
            return {"timestamp":ts,"params":{"sessionId":"g1","update":{"sessionUpdate":"turn_completed","usage":{"inputTokens":input_tokens,"outputTokens":5,"cachedReadTokens":7,"reasoningTokens":2,"numTurns":turns,"modelUsage":{"grok-4.5-build":{}}}}}}
        result = normalizer.normalize("xai", lines(event(1000, 50, 1), event(1001, 90, 2)), META)
        self.assertEqual(90, result["usage"]["input_tokens"])
        self.assertEqual(2, result["usage"]["turns"])
        self.assertEqual("grok-4.5-build", result["effective_profile"]["model"])

    def test_missing_native_fields_remain_unknown_or_zero_not_invented(self):
        result = normalizer.normalize("openai", lines({"type":"event_msg","payload":{"type":"token_count","info":None}}), META)
        self.assertIsNone(result["effective_profile"]["model"])
        self.assertEqual(0, result["usage"]["input_tokens"])
        self.assertEqual("unknown", result["session_id"])


if __name__ == "__main__":
    unittest.main()
