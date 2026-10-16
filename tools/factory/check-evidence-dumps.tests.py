#!/usr/bin/env python3
"""Fixture tests for tools/factory/check-evidence-dumps.py (throwaway git repos; stdlib only).

    python tools/factory/check-evidence-dumps.tests.py
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL = HERE / "check-evidence-dumps.py"
FIX = HERE / "fixtures" / "check-evidence-dumps"

CFG = {
    "schema": "factory-check-evidence-dumps.v1",
    "scope": ["review/*", "notes/*"],
    "exclude": ["review/fixtures/*"],
    "evidence_dirs": ["review/evidence-*"],
    "raw_patterns": ["*.log", "*.out", "*.dump", "*mutant*.json", "*.jsonl"],
    "large_text": {"patterns": ["*.txt"], "max_bytes": 100},
    "allowed_in_evidence_dir": ["*.md"],
    "max_file_bytes": 200,
    "max_dir_bytes": 400,
}


def git(repo: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(repo), "-c", "user.email=t@example.invalid", "-c", "user.name=t",
                        "-c", "core.autocrlf=false", "-c", "commit.gpgsign=false", *args],
                       check=True, capture_output=True)
    return p.stdout.decode().strip()


class Repo:
    def __init__(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        git(self.root, "init", "-q", "-b", "master")
        self.put("README.md", b"x\n")
        self.commit("init")

    def put(self, rel: str, data: bytes) -> None:
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
        git(self.root, "add", "--", rel)

    def rm(self, rel: str) -> None:
        git(self.root, "rm", "-q", "--", rel)

    def commit(self, msg: str) -> str:
        git(self.root, "commit", "-q", "-m", msg)
        return git(self.root, "rev-parse", "HEAD")

    def run(self, *extra: str, cfg: dict | Path = CFG) -> tuple[int, str]:
        if isinstance(cfg, dict):
            cp = self.root.parent / (self.root.name + ".cfg.json")
            cp.write_text(json.dumps(cfg), encoding="utf-8")
        else:
            cp = cfg
        p = subprocess.run([sys.executable, str(TOOL), "--config", str(cp), "--repo", str(self.root), *extra],
                           capture_output=True)
        return p.returncode, (p.stdout + p.stderr).decode("utf-8", "replace")

    def close(self) -> None:
        self._tmp.cleanup()


def sums(files: dict[str, bytes]) -> bytes:
    return "".join(f"{hashlib.sha256(v).hexdigest()}  {k}\n" for k, v in files.items()).encode()


RAW = {"run.log": b"line\n" * 50, "mutants.json": b'{"m": 1}\n'}


class T(unittest.TestCase):
    def setUp(self) -> None:
        self.r = Repo()

    def tearDown(self) -> None:
        self.r.close()

    def evidence_branch(self, files=RAW, path="review/evidence-a"):
        """Raw bytes on branch evidence/a, then back to master."""
        git(self.r.root, "checkout", "-q", "-b", "evidence/a")
        for k, v in files.items():
            self.r.put(f"{path}/{k}", v)
        sha = self.r.commit("evidence")
        git(self.r.root, "checkout", "-q", "master")
        return sha

    def test_clean_tree_passes(self):
        self.r.put("review/plan.md", b"plan\n")
        self.r.commit("c")
        rc, out = self.r.run("--tree")
        self.assertEqual(rc, 0, out)

    def test_raw_log_refused_anywhere_in_scope(self):
        self.r.put("notes/session.log", b"x\n")
        self.r.commit("c")
        rc, out = self.r.run("--tree")
        self.assertEqual(rc, 1, out)
        self.assertIn("RAW notes/session.log", out)

    def test_out_of_scope_and_excluded_ignored(self):
        self.r.put("src/app.log", b"x\n")
        self.r.put("review/fixtures/sample.log", b"x\n")
        self.r.commit("c")
        rc, out = self.r.run("--tree")
        self.assertEqual(rc, 0, out)

    def test_large_text_refused_small_text_ok(self):
        self.r.put("notes/small.txt", b"x" * 100)
        self.r.commit("c")
        self.assertEqual(self.r.run("--tree")[0], 0)
        self.r.put("notes/big.txt", b"x" * 101)
        self.r.commit("c2")
        rc, out = self.r.run("--tree")
        self.assertEqual(rc, 1, out)
        self.assertIn("LARGE_TEXT notes/big.txt", out)

    def test_convention_verified_against_local_ref(self):
        self.evidence_branch()
        self.r.put("review/evidence-a/SHA256SUMS", sums(RAW))
        self.r.put("review/evidence-a/EVIDENCE-REF", b"ref: refs/heads/evidence/a\n")
        self.r.put("review/evidence-a/summary.md", b"two files, both green\n")
        self.r.commit("c")
        rc, out = self.r.run("--tree")
        self.assertEqual(rc, 0, out)
        self.assertIn("VERIFIED review/evidence-a/: 2 sums", out)

    def test_ref_resolves_through_origin_remote_name(self):
        sha = self.evidence_branch()
        git(self.r.root, "update-ref", "refs/remotes/origin/evidence/a", sha)
        git(self.r.root, "branch", "-q", "-D", "evidence/a")
        self.r.put("review/evidence-a/SHA256SUMS", sums(RAW))
        self.r.put("review/evidence-a/EVIDENCE-REF", b"ref: refs/heads/evidence/a\n")
        self.r.commit("c")
        rc, out = self.r.run("--tree")
        self.assertEqual(rc, 0, out)
        self.assertIn("VERIFIED", out)

    def test_hash_mismatch_refused(self):
        self.evidence_branch()
        bad = dict(RAW, **{"run.log": b"different\n"})
        self.r.put("review/evidence-a/SHA256SUMS", sums(bad))
        self.r.put("review/evidence-a/EVIDENCE-REF", b"ref: evidence/a\n")
        self.r.commit("c")
        rc, out = self.r.run("--tree")
        self.assertEqual(rc, 1, out)
        self.assertIn("SUMS_MISMATCH review/evidence-a/run.log", out)

    def test_blob_missing_on_ref_refused(self):
        self.evidence_branch({"run.log": RAW["run.log"]})
        self.r.put("review/evidence-a/SHA256SUMS", sums(RAW))
        self.r.put("review/evidence-a/EVIDENCE-REF", b"ref: evidence/a\n")
        self.r.commit("c")
        rc, out = self.r.run("--tree")
        self.assertEqual(rc, 1, out)
        self.assertIn("BLOB_MISSING review/evidence-a/mutants.json", out)

    def test_pointer_path_and_commit_pin(self):
        sha = self.evidence_branch(path="raw/a")
        self.r.put("review/evidence-a/SHA256SUMS", sums(RAW))
        self.r.put("review/evidence-a/EVIDENCE-REF", f"ref: evidence/a\npath: raw/a\ncommit: {sha}\n".encode())
        self.r.commit("c")
        git(self.r.root, "branch", "-q", "-D", "evidence/a")  # the commit object stays: pinned by sha
        rc, out = self.r.run("--tree")
        self.assertEqual(rc, 0, out)
        self.assertIn("VERIFIED", out)

    def test_unavailable_ref_unverified_unless_required(self):
        self.r.put("review/evidence-a/SHA256SUMS", sums(RAW))
        self.r.put("review/evidence-a/EVIDENCE-REF", b"ref: refs/heads/evidence/elsewhere\n")
        self.r.commit("c")
        rc, out = self.r.run("--tree")
        self.assertEqual(rc, 0, out)
        self.assertIn("UNVERIFIED review/evidence-a/", out)
        rc, out = self.r.run("--tree", "--require-ref")
        self.assertEqual(rc, 1, out)
        self.assertIn("REF_UNAVAILABLE", out)

    def test_missing_pointer_refused(self):
        self.r.put("review/evidence-a/SHA256SUMS", sums(RAW))
        self.r.commit("c")
        rc, out = self.r.run("--tree")
        self.assertEqual(rc, 1, out)
        self.assertIn("NO_POINTER review/evidence-a/", out)

    def test_sums_dir_outside_evidence_globs_is_an_evidence_dir(self):
        self.r.put("notes/k3/patches/SHA256SUMS", sums({"M1.patch": b"p\n"}))
        self.r.put("notes/k3/patches/M1.patch", b"p\n")
        self.r.commit("c")
        rc, out = self.r.run("--tree")
        self.assertEqual(rc, 1, out)
        self.assertIn("NOT_ALLOWED notes/k3/patches/M1.patch", out)
        self.assertIn("NO_POINTER notes/k3/patches/", out)

    def test_evidence_dir_without_sums_refused_and_raw_inside(self):
        self.r.put("review/evidence-b/sub/trace.log", b"x\n")
        self.r.put("review/evidence-b/sub/script.py", b"print(1)\n")
        self.r.commit("c")
        rc, out = self.r.run("--tree")
        self.assertEqual(rc, 1, out)
        self.assertIn("RAW review/evidence-b/sub/trace.log", out)
        self.assertIn("NOT_ALLOWED review/evidence-b/sub/script.py", out)
        self.assertIn("NO_SUMS review/evidence-b/", out)

    def test_size_caps(self):
        self.evidence_branch()
        self.r.put("review/evidence-a/SHA256SUMS", sums(RAW))
        self.r.put("review/evidence-a/EVIDENCE-REF", b"ref: evidence/a\n")
        self.r.put("review/evidence-a/summary.md", b"s" * 201)
        self.r.commit("c")
        rc, out = self.r.run("--tree")
        self.assertEqual(rc, 1, out)
        self.assertIn("TOO_BIG review/evidence-a/summary.md", out)
        self.r.put("review/evidence-a/summary.md", b"s" * 150)
        self.r.put("review/evidence-a/more.md", b"s" * 150)
        self.r.commit("c2")
        rc, out = self.r.run("--tree")
        self.assertEqual(rc, 1, out)
        self.assertIn("DIR_TOO_BIG review/evidence-a/", out)

    def test_range_checks_only_added_paths(self):
        self.r.put("notes/legacy.log", b"old\n")
        base = self.r.commit("legacy dump")
        self.r.put("review/plan.md", b"ok\n")
        self.r.commit("clean")
        rc, out = self.r.run("--range", f"{base}..HEAD")
        self.assertEqual(rc, 0, out)
        self.r.put("notes/new.out", b"new\n")
        self.r.commit("dump")
        rc, out = self.r.run("--range", f"{base}..HEAD")
        self.assertEqual(rc, 1, out)
        self.assertIn("RAW notes/new.out", out)
        self.assertNotIn("legacy.log", out)

    def test_range_deleting_a_dump_passes(self):
        self.r.put("notes/legacy.log", b"old\n")
        base = self.r.commit("legacy")
        self.r.rm("notes/legacy.log")
        self.r.commit("shrink")
        self.assertEqual(self.r.run("--range", f"{base}..HEAD")[0], 0)

    def test_bad_config_exit_2(self):
        rc, out = self.r.run("--tree", cfg={"schema": "nope"})
        self.assertEqual(rc, 2, out)
        rc, out = self.r.run("--tree", cfg=dict(CFG, bogus=1))
        self.assertEqual(rc, 2, out)

    def test_not_a_repo_exit_2(self):
        with tempfile.TemporaryDirectory() as d:
            cp = Path(d) / "c.json"
            cp.write_text(json.dumps(CFG), encoding="utf-8")
            p = subprocess.run([sys.executable, str(TOOL), "--config", str(cp), "--repo", d, "--tree"],
                               capture_output=True, cwd=d)
            self.assertEqual(p.returncode, 2)

    def test_fixture_configs_load(self):
        for f in sorted(FIX.glob("*.config.json")):
            rc, out = self.r.run("--tree", cfg=f)
            self.assertEqual(rc, 0, f"{f.name}: {out}")


if __name__ == "__main__":
    unittest.main(verbosity=1)
