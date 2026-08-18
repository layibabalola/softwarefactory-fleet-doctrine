from __future__ import annotations

import datetime as dt
import importlib.util
import json
import pathlib
import sys
import unittest


ROOT=pathlib.Path(__file__).resolve().parents[1]
MODULE=ROOT/"reference"/"normalize_capacity.py"
SPEC=importlib.util.spec_from_file_location("normalize_capacity",MODULE)
assert SPEC and SPEC.loader
normalizer=importlib.util.module_from_spec(SPEC); sys.modules[SPEC.name]=normalizer; SPEC.loader.exec_module(normalizer)
DOMAIN="anthropic:sha256:"+"a"*64


class CapacityTests(unittest.TestCase):
    def test_anthropic_percent_and_window_start(self):
        raw={"five_hour":{"utilization":43,"resets_at":"2026-08-18T20:20:00Z"},"seven_day":{"utilization":54,"resets_at":"2026-08-22T00:00:00Z"}}
        result=normalizer.normalize("anthropic",json.dumps(raw),DOMAIN,"2026-08-18T16:00:00Z","1"*64)
        self.assertEqual(.43,result["windows"][0]["used_fraction"])
        self.assertEqual("2026-08-18T15:20:00Z",result["windows"][0]["window_started_at"])

    def test_openai_uses_latest_rate_limit_snapshot(self):
        def row(used,reset): return json.dumps({"payload":{"type":"token_count","rate_limits":{"primary":{"used_percent":used,"window_minutes":300,"resets_at":reset}}}})
        result=normalizer.normalize("openai",row(10,1000)+"\n"+row(25,2000),"openai:sha256:"+"b"*64,"2026-08-18T16:00:00Z","2"*64)
        self.assertEqual(.25,result["windows"][0]["used_fraction"])
        self.assertEqual("primary",result["windows"][0]["name"])

    def test_missing_or_unsupported_capacity_is_unevaluable(self):
        with self.assertRaises(normalizer.CapacityError): normalizer.normalize("anthropic","{}",DOMAIN,"2026-08-18T16:00:00Z","1"*64)
        with self.assertRaises(normalizer.CapacityError): normalizer.normalize("moonshot","{}",DOMAIN,"2026-08-18T16:00:00Z","1"*64)


if __name__=="__main__": unittest.main()
