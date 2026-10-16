#!/usr/bin/env python3
"""Fixture tests for tools/factory/check-doc-size.py against the three fleet tier tables.

    python tools/factory/check-doc-size.tests.py

Each case builds a throwaway git repository, writes markdown of exact sizes, and asserts the exit
code and per-file state the project's own (retired) rewrite produced for the same input. The
configs are tools/factory/fixtures/check-doc-size/<project>.config.json, generated from each
rewrite's module constants on 2026-10-16 (live-tree parity was measured the same day).
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL = HERE / "check-doc-size.py"
FIX = HERE / "fixtures" / "check-doc-size"


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), "-c", "user.email=t@example.invalid", "-c", "user.name=t",
                    "-c", "core.autocrlf=false", *args], check=True, capture_output=True)


class Repo:
    def __init__(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        git(self.root, "init", "-q")

    def write(self, rel: str, size: int, track: bool = True, newline_every: int = 0) -> None:
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        if newline_every:
            line = b"x" * (newline_every - 1) + b"\n"
            data = (line * (size // newline_every + 1))[:size]
        else:
            data = b"x" * size
        p.write_bytes(data)
        if track:
            git(self.root, "add", "--", rel)

    def run(self, config: str | Path, *extra: str) -> tuple[int, dict]:
        cfg = config if isinstance(config, Path) else FIX / f"{config}.config.json"
        p = subprocess.run([sys.executable, str(TOOL), "--config", str(cfg), "--repo", str(self.root), "--json", *extra],
                           capture_output=True, text=True)
        try:
            body = json.loads(p.stdout)
        except ValueError:
            body = {"stdout": p.stdout, "stderr": p.stderr}
        return p.returncode, body

    def state(self, body: dict, rel: str) -> str | None:
        return next((r["state"] for r in body.get("rows", []) if r["path"] == rel), None)

    def close(self) -> None:
        self._tmp.cleanup()


class Base(unittest.TestCase):
    def setUp(self) -> None:
        self.r = Repo()

    def tearDown(self) -> None:
        self.r.close()


class Conjugal(Base):
    def test_entry_tier_hard_cap_is_12000(self):
        self.r.write("CLAUDE.md", 12_000)
        self.assertEqual(self.r.run("conjugal")[0], 0)
        self.r.write("CLAUDE.md", 12_001)
        rc, body = self.r.run("conjugal")
        self.assertEqual((rc, self.r.state(body, "CLAUDE.md")), (1, "BREACH"))

    def test_nested_readme_is_entry_and_unmatched_is_working(self):
        self.r.write("a/README.md", 9_000)
        self.r.write("src/notes.md", 39_000)
        rc, body = self.r.run("conjugal")
        self.assertEqual((rc, self.r.state(body, "a/README.md"), self.r.state(body, "src/notes.md")), (0, "WARN", "WARN"))

    def test_deferred_ledger_is_measured_never_gated_and_strict_gates_it(self):
        self.r.write("coordination/HUB.md", 900_000)
        rc, body = self.r.run("conjugal")
        self.assertEqual((rc, self.r.state(body, "coordination/HUB.md")), (0, "DEFER"))
        self.assertEqual(self.r.run("conjugal", "--strict")[0], 1)

    def test_baseline_ratchet_holds_then_refuses_growth(self):
        rel = "docs/00-overview/03-glossary.md"
        self.r.write(rel, 17_278)
        rc, body = self.r.run("conjugal")
        self.assertEqual((rc, self.r.state(body, rel)), (0, "held"))
        self.r.write(rel, 17_279)
        rc, body = self.r.run("conjugal")
        self.assertEqual((rc, self.r.state(body, rel)), (1, "GREW"))

    def test_exempt_and_untracked_are_not_governed(self):
        self.r.write("x/fixtures/big.md", 500_000)
        self.r.write("scratch.md", 500_000, track=False)
        rc, body = self.r.run("conjugal")
        self.assertEqual((rc, body["rows"]), (0, []))

    def test_path_mode_checks_an_untracked_file(self):
        self.r.write("new.md", 40_001, track=False)
        self.assertEqual(self.r.run("conjugal", "--path", "new.md")[0], 1)
        self.assertEqual(self.r.run("conjugal", "--path", "new.md", "--warn-only")[0], 0)


class Cloudvore(Base):
    def test_worktree_walk_governs_untracked_review(self):
        self.r.write("review/plan.md", 41_000, track=False)
        rc, body = self.r.run("cloudvore")
        self.assertEqual((rc, self.r.state(body, "review/plan.md")), (1, "BREACH"))

    def test_kib_caps_and_crlf_normalised_size(self):
        # 8,100 LF bytes in 81 lines govern as 8,181 CRLF bytes: under the 8 KiB entry cap (8,192).
        self.r.write("CLAUDE.md", 8_100, newline_every=100)
        rc, body = self.r.run("cloudvore")
        self.assertEqual((rc, self.r.state(body, "CLAUDE.md")), (0, "WARN"))
        # 8,150 LF bytes in 82 lines -> 8,231 governed: over, although the disk size is under.
        self.r.write("CLAUDE.md", 8_150, newline_every=100)
        rc, body = self.r.run("cloudvore")
        self.assertEqual((rc, self.r.state(body, "CLAUDE.md")), (1, "BREACH"))

    def test_index_tier_and_skip_dirs(self):
        self.r.write("knowledge/INDEX.md", 4_097)
        self.r.write("node_modules/pkg/README.md", 900_000)
        rc, body = self.r.run("cloudvore")
        self.assertEqual((rc, self.r.state(body, "knowledge/INDEX.md"), len(body["rows"])), (1, "BREACH", 1))

    def test_newest_dated_handoff_is_entry_older_is_ledger(self):
        self.r.write("review/HANDOFF-2026-09-01.md", 9_000, track=False)
        self.r.write("review/HANDOFF-2026-10-01.md", 9_000, track=False)
        rc, body = self.r.run("cloudvore")
        tiers = {r["path"]: r["tier"] for r in body["rows"]}
        self.assertEqual(rc, 1)
        self.assertEqual((tiers["review/HANDOFF-2026-10-01.md"], tiers["review/HANDOFF-2026-09-01.md"]), ("entry", "ledger"))

    def test_path_outside_domain_refuses(self):
        self.r.write("tools/x.py", 10, track=False)
        self.assertEqual(self.r.run("cloudvore", "--path", "tools/x.py")[0], 2)
        self.assertEqual(self.r.run("cloudvore", "--headroom", ".venv/a.md")[0], 2)

    def test_headroom_reports_breach(self):
        self.r.write("README.md", 9_000)
        rc, body = self.r.run("cloudvore", "--headroom", "README.md")
        self.assertEqual((rc, body["headroom"] < 0), (1, True))


class MagicLantern(Base):
    def test_upstream_markdown_is_exempt(self):
        self.r.write("doc/upstream.md", 100_000)
        git(self.r.root, "commit", "-qm", "upstream")
        git(self.r.root, "update-ref", "refs/remotes/origin/master", "HEAD")
        self.assertEqual(self.r.run("magic-lantern")[0], 0)
        self.r.write("roadmap/new.md", 40_001)
        rc, body = self.r.run("magic-lantern")
        self.assertEqual((rc, self.r.state(body, "roadmap/new.md")), (1, "BREACH"))

    def test_no_origin_governs_everything(self):
        self.r.write("doc/upstream.md", 100_000)
        self.assertEqual(self.r.run("magic-lantern")[0], 1)

    def test_ledger_tier_and_frozen_corpus(self):
        self.r.write("audit-packet/45-workplan-evidence.md", 59_000)
        self.r.write("Claude - Audit & Documentation/huge.md", 900_000)
        rc, body = self.r.run("magic-lantern")
        self.assertEqual((rc, self.r.state(body, "audit-packet/45-workplan-evidence.md"), len(body["rows"])), (0, "WARN", 1))


class Config(Base):
    def _cfg(self, obj) -> Path:
        p = self.r.root / "cfg.json"
        p.write_text(json.dumps(obj), encoding="utf-8")
        return p

    def test_unknown_key_refuses(self):
        cfg = json.loads((FIX / "conjugal.config.json").read_text(encoding="utf-8"))
        cfg["exmept"] = ["**"]
        self.assertEqual(self.r.run(self._cfg(cfg))[0], 2)

    def test_wrong_schema_and_bad_tier_refuse(self):
        self.assertEqual(self.r.run(self._cfg({"schema": "nope"}))[0], 2)
        bad = {"schema": "factory-check-doc-size.v1", "tiers": {"working": {"soft": 9, "hard": 5, "globs": []}},
               "tier_order": ["working"]}
        self.assertEqual(self.r.run(self._cfg(bad))[0], 2)

    def test_missing_config_refuses(self):
        self.assertEqual(self.r.run(self.r.root / "absent.json")[0], 2)


if __name__ == "__main__":
    unittest.main(verbosity=1)
