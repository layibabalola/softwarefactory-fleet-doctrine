#!/usr/bin/env python3
"""Tests for delivery-at-identity.py (the K7 detector) against throwaway git repositories: a bare origin plus
the clone that pushes, every ref move stamped with GIT_COMMITTER_DATE so the reflog carries the times a
ruling read.

The predicate under test: the keyed tree was the delivery ref's tip at an instant at or after the key's
acceptance time, and the ref's next move recorded the subject's Outcome.

  test_s1_ruling_shape                tree was the tip 00:03:49Z..00:07:35Z, accepted 00:08:58.797Z (the S1
                                      timeline of the 2026-10-17 conjugal dispositions)  -> TIP-BEFORE-ACCEPTANCE
                                      (the old "was it ever a tip" predicate printed AT-IDENTITY: red there)
  test_delivered_after_acceptance     the S137 shape: accepted, pushed as itself, Outcome next -> AT-IDENTITY
  test_pushed_before_key_held_across  the S34/S22 shape: pushed before the key, still the tip at acceptance,
                                      Outcome next                                         -> AT-IDENTITY
  test_moved_before_outcome           tip at/after acceptance, but a peer push came before the Outcome
                                                                                           -> MOVED-BEFORE-OUTCOME
  test_same_second_is_not_proof       the ref moved in the acceptance's own second           -> TIP-BEFORE-ACCEPTANCE
  test_no_acceptance_time             a table row with no Receipts block                    -> ACCEPTANCE-UNPROVEN;
                                      the same with --accepted-at                           -> AT-IDENTITY
  test_tampered_receipt               the named rollout line does not hash to the receipt   -> ACCEPTANCE-UNPROVEN
  test_pending_outcome                the delivery chain's own call: still the tip, Outcome not yet written
                                                                                           -> AT-IDENTITY pending
  test_outcome_then_merge / test_never_delivered    the unchanged NOT-AT-IDENTITY classes
  test_zst_rollout                    a codex-compressed rollout (.jsonl.zst) is read when the stdlib can

Run:  python tools/factory/delivery-at-identity.tests.py      (DAI_TOOL=<path> runs it against another copy)
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL = Path(os.environ.get("DAI_TOOL") or HERE / "delivery-at-identity.py")
KD = "coordination/kernel-dogfood"


def ts(iso: str) -> int:
    return int(_dt.datetime.fromisoformat(iso.replace("Z", "+00:00")).timestamp())


class Repo:
    """A bare origin and the clone that pushes; ``at`` stamps the next ref move."""

    def __init__(self, root: Path):
        self.root = root
        self.origin, self.w = root / "origin.git", root / "w"
        self.home = root / "codex"
        self.when = ts("2026-09-01T00:00:00Z")
        subprocess.run(["git", "init", "-q", "--bare", "-b", "master", str(self.origin)], check=True)
        subprocess.run(["git", "clone", "-q", str(self.origin), str(self.w)], check=True, capture_output=True)
        self.g("config", "core.autocrlf", "false")
        self.g("checkout", "-q", "-b", "master")
        self.commit("README", "base\n", "base")
        self.push()

    def g(self, *args: str) -> str:
        env = dict(os.environ)
        env.update({"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
                    "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_NOSYSTEM": "1",
                    "GIT_AUTHOR_DATE": f"{self.when} +0000", "GIT_COMMITTER_DATE": f"{self.when} +0000"})
        p = subprocess.run(["git", "-C", str(self.w), *args], capture_output=True, text=True, env=env, check=True)
        return p.stdout.strip()

    def at(self, iso: str) -> "Repo":
        self.when = ts(iso)
        return self

    def commit(self, rel: str, text: str, msg: str) -> str:
        p = self.w / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "a", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        self.g("add", rel)
        self.g("commit", "-q", "-m", msg)
        return self.g("rev-parse", "HEAD")

    def push(self) -> None:
        self.g("push", "-q", "origin", "master")

    def tree(self, c: str) -> str:
        return self.g("rev-parse", c + "^{tree}")

    def rollout(self, name: str, accepted: str, verdict: str, tamper: bool = False, zst: bool = False) -> str:
        """A codex rollout whose line 2 is the final answer stamped ``accepted``; returns its Receipts block."""
        day = self.home / "sessions" / "2026" / "09" / "16"
        day.mkdir(parents=True, exist_ok=True)
        recs = [json.dumps({"timestamp": accepted, "type": "session_meta", "payload": {"id": name}}),
                json.dumps({"timestamp": accepted, "type": "response_item",
                            "payload": {"phase": "final_answer", "content": "all held\n\n" + verdict}})]
        raw = ("\n".join(recs) + "\n").encode()
        fa = hashlib.sha256(recs[1].encode()).hexdigest()
        if tamper:
            fa = hashlib.sha256(b"something else").hexdigest()
        f = day / f"rollout-{name}.jsonl"
        if zst:
            from compression import zstd
            f.with_name(f.name + ".zst").write_bytes(zstd.compress(raw))
        else:
            f.write_bytes(raw)
        return (f"**Receipts** (`~/.codex/sessions/2026/09/16/rollout-{name}.jsonl`,\n2 records, final answer on "
                f"line 2):\n- rollout file SHA-256 `{hashlib.sha256(raw).hexdigest()}`\n- final-answer record SHA-256 "
                f"`{fa}`\n- verdict line `{verdict}`, SHA-256\n  `{hashlib.sha256(verdict.encode()).hexdigest()}`\n")


def table_outcome(cand: str, tree: str, receipts: str = "") -> str:
    return ("\n## Outcome - ACCEPTED at round 1.\n\n| round | candidate | tree | verdict line |\n|---|---|---|---|\n"
            f"| 1 | `{cand[:9]}` | `{tree}` | `VERDICT: ACCEPT tree={tree}` |\n\n" + receipts)


def chain_outcome(cand: str, receipts: str) -> str:
    """The form deliver.py writes (QUEUE step 6): no table, a push line and a Receipts block."""
    return ("\n## Outcome - ACCEPTED 2026-09-16 on its first round; delivered at identity\n\nAll held.\n\n"
            f"**Delivered at identity (QUEUE step 6).** `git push origin {cand[:9]}:master` fast-forwarded "
            f"`0000000..{cand[:9]}`\nafter `git merge-base --is-ancestor origin/master {cand[:9]}` exited `0`. This "
            f"Outcome is a second push.\n\n{receipts}\n**Credit.** One.\n")


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="dai-"))
        self.r = Repo(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_tool(self, *extra: str):
        # the rollouts are found through $CODEX_HOME (not --codex-home) so the same call runs the old predicate
        p = subprocess.run([sys.executable, str(TOOL), "--repo", str(self.r.w), *extra], capture_output=True,
                           text=True, env={**os.environ, "CODEX_HOME": str(self.r.home)})
        rows = {ln.split()[0]: ln for ln in p.stdout.splitlines() if re.match(r"S\d+ ", ln)}
        return p.returncode, rows, p.stdout + p.stderr

    def declare(self, s: str, iso: str) -> str:
        rel = f"{KD}/{s}-subject.md"
        self.r.at(iso).commit(rel, f"# {s} declaration\n", f"{s} declare")
        return rel


class Predicate(Base):
    def test_s1_ruling_shape(self):
        # local master held the keyed tree 19:03:49..19:07:35 -0500; the key accepted at 19:08:58.797 -0500
        r = self.r
        rel = self.declare("S1", "2026-09-15T23:50:00Z")
        cand = r.at("2026-09-16T00:03:49Z").commit("src/one.py", "x = 1\n", "S1 candidate")
        r.at("2026-09-16T00:07:35Z").commit("coordination/lanes/luna.md", "peer\n", "peer heartbeat")
        rc_ = r.rollout("s1", "2026-09-16T00:08:58.797Z", f"VERDICT: ACCEPT tree={r.tree(cand)}")
        r.at("2026-09-16T00:20:00Z").commit(rel, table_outcome(cand, r.tree(cand), rc_), "S1 outcome")
        rc, rows, out = self.run_tool("--ref", "refs/heads/master", "--only", "S1")
        self.assertTrue(rows["S1"].startswith("S1 NOT-AT-IDENTITY TIP-BEFORE-ACCEPTANCE"), out)
        self.assertIn("accepted=2026-09-16T00:08:58.797Z", rows["S1"])
        self.assertEqual(rc, 1, out)

    def test_delivered_after_acceptance(self):
        r = self.r
        rel = self.declare("S137", "2026-10-17T10:00:00Z")
        r.push()
        cand = r.at("2026-10-17T10:05:00Z").commit("src/a.py", "a = 1\n", "S137 code")
        rc_ = r.rollout("s137", "2026-10-17T14:41:15.435Z", f"VERDICT: ACCEPT tree={r.tree(cand)}")
        r.at("2026-10-17T14:44:13Z").push()
        r.at("2026-10-17T14:44:52Z").commit(rel, chain_outcome(cand, rc_), "S137 Outcome")
        r.push()
        rc, rows, out = self.run_tool()
        self.assertTrue(rows["S137"].startswith("S137 AT-IDENTITY"), out)
        self.assertIn("(update by push)", rows["S137"])
        self.assertIn("receipt rollout-s137.jsonl:2", rows["S137"])
        self.assertEqual(rc, 0, out)

    def test_pushed_before_key_held_across(self):
        r = self.r
        rel = self.declare("S34", "2026-09-26T22:35:24Z")
        cand = r.at("2026-09-26T22:52:50Z").commit("src/b.py", "b = 1\n", "S34 round 2")
        r.at("2026-09-26T22:53:23Z").push()
        rc_ = r.rollout("s34", "2026-09-26T22:58:59.887Z", f"VERDICT: ACCEPT tree={r.tree(cand)}")
        r.at("2026-09-26T23:01:33Z").commit(rel, table_outcome(cand, r.tree(cand), rc_), "S34 Outcome")
        r.push()
        rc, rows, out = self.run_tool()
        self.assertTrue(rows["S34"].startswith("S34 AT-IDENTITY"), out)
        self.assertEqual(rc, 0, out)

    def test_moved_before_outcome(self):
        r = self.r
        rel = self.declare("S5", "2026-10-01T00:00:00Z")
        r.push()
        cand = r.at("2026-10-01T00:10:00Z").commit("src/c.py", "c = 1\n", "S5 code")
        rc_ = r.rollout("s5", "2026-10-01T01:00:00.000Z", f"VERDICT: ACCEPT tree={r.tree(cand)}")
        r.at("2026-10-01T01:01:00Z").push()
        r.at("2026-10-01T01:02:00Z").commit("peer.txt", "peer\n", "peer")
        r.push()
        r.at("2026-10-01T01:03:00Z").commit(rel, chain_outcome(cand, rc_), "S5 Outcome")
        r.push()
        rc, rows, out = self.run_tool()
        self.assertTrue(rows["S5"].startswith("S5 NOT-AT-IDENTITY MOVED-BEFORE-OUTCOME"), out)
        self.assertEqual(rc, 1, out)

    def test_same_second_is_not_proof(self):
        r = self.r
        rel = self.declare("S6", "2026-10-02T00:00:00Z")
        r.push()
        cand = r.at("2026-10-02T00:10:00Z").commit("src/d.py", "d = 1\n", "S6 code")
        r.push()
        rc_ = r.rollout("s6", "2026-10-02T00:20:00.400Z", f"VERDICT: ACCEPT tree={r.tree(cand)}")
        r.at("2026-10-02T00:20:00Z").commit(rel, table_outcome(cand, r.tree(cand), rc_), "S6 Outcome")
        r.push()
        rc, rows, out = self.run_tool()
        self.assertTrue(rows["S6"].startswith("S6 NOT-AT-IDENTITY TIP-BEFORE-ACCEPTANCE"), out)

    def test_no_acceptance_time(self):
        r = self.r
        rel = self.declare("S7", "2026-10-03T00:00:00Z")
        r.push()
        cand = r.at("2026-10-03T00:10:00Z").commit("src/e.py", "e = 1\n", "S7 code")
        r.at("2026-10-03T00:30:00Z").push()
        r.at("2026-10-03T00:31:00Z").commit(rel, table_outcome(cand, r.tree(cand)), "S7 Outcome")
        r.push()
        rc, rows, out = self.run_tool()
        self.assertTrue(rows["S7"].startswith("S7 NOT-AT-IDENTITY ACCEPTANCE-UNPROVEN"), out)
        self.assertEqual(rc, 1, out)
        rc, rows, out = self.run_tool("--accepted-at", "S7=2026-10-02T19:20:00-05:00")
        self.assertTrue(rows["S7"].startswith("S7 AT-IDENTITY"), out)
        self.assertEqual(rc, 0, out)
        rc, _, out = self.run_tool("--accepted-at", "S7=2026-10-03T00:20:00")
        self.assertEqual(rc, 2, "an acceptance time with no offset is refused")

    def test_tampered_receipt(self):
        r = self.r
        rel = self.declare("S8", "2026-10-04T00:00:00Z")
        r.push()
        cand = r.at("2026-10-04T00:10:00Z").commit("src/f.py", "f = 1\n", "S8 code")
        rc_ = r.rollout("s8", "2026-10-04T00:20:00.000Z", f"VERDICT: ACCEPT tree={r.tree(cand)}", tamper=True)
        r.at("2026-10-04T00:30:00Z").push()
        r.at("2026-10-04T00:31:00Z").commit(rel, chain_outcome(cand, rc_), "S8 Outcome")
        r.push()
        rc, rows, out = self.run_tool()
        self.assertTrue(rows["S8"].startswith("S8 NOT-AT-IDENTITY ACCEPTANCE-UNPROVEN"), out)
        self.assertIn("does not hash", rows["S8"])

    def test_pending_outcome(self):
        r = self.r
        self.declare("S9", "2026-10-05T00:00:00Z")
        r.push()
        cand = r.at("2026-10-05T00:10:00Z").commit("src/g.py", "g = 1\n", "S9 code")
        r.at("2026-10-05T00:30:00Z").push()
        rc, rows, out = self.run_tool("--only", "S9", "--extra", f"S9={cand}",
                                      "--accepted-at", "S9=2026-10-05T00:20:00.000Z")
        self.assertTrue(rows["S9"].startswith("S9 AT-IDENTITY"), out)
        self.assertIn("outcome=pending", rows["S9"])
        self.assertEqual(rc, 0, out)
        rc, rows, out = self.run_tool("--only", "S9", "--extra", f"S9={cand}")
        self.assertTrue(rows["S9"].startswith("S9 NOT-AT-IDENTITY ACCEPTANCE-UNPROVEN"), out)

    @unittest.skipUnless(sys.version_info >= (3, 14), "compression.zstd is stdlib from Python 3.14")
    def test_zst_rollout(self):
        r = self.r
        rel = self.declare("S10", "2026-10-06T00:00:00Z")
        r.push()
        cand = r.at("2026-10-06T00:10:00Z").commit("src/h.py", "h = 1\n", "S10 code")
        rc_ = r.rollout("s10", "2026-10-06T00:20:00.000Z", f"VERDICT: ACCEPT tree={r.tree(cand)}", zst=True)
        r.at("2026-10-06T00:30:00Z").push()
        r.at("2026-10-06T00:31:00Z").commit(rel, chain_outcome(cand, rc_), "S10 Outcome")
        r.push()
        rc, rows, out = self.run_tool()
        self.assertTrue(rows["S10"].startswith("S10 AT-IDENTITY"), out)


class UnchangedClasses(Base):
    def test_outcome_then_merge(self):
        r = self.r
        rel = self.declare("S2", "2026-10-07T00:00:00Z")
        r.push()
        r.g("checkout", "-q", "-b", "s2")
        cand = r.at("2026-10-07T00:10:00Z").commit("src/two.py", "y = 2\n", "S2 candidate")
        r.commit(rel, table_outcome(cand, r.tree(cand)), "S2 outcome")
        r.g("checkout", "-q", "master")
        r.commit("peer.txt", "peer\n", "peer commit")
        r.g("merge", "-q", "--no-ff", "-m", "merge s2", "s2")
        r.push()
        rc, rows, out = self.run_tool()
        self.assertTrue(rows["S2"].startswith("S2 NOT-AT-IDENTITY DESCENDANT-"), out)
        self.assertEqual(rc, 1)

    def test_never_delivered(self):
        r = self.r
        self.declare("S3", "2026-10-08T00:00:00Z")
        r.commit(f"{KD}/S3-subject.md", "## Outcome - moved to child\n", "S3 note")
        r.push()
        r.g("checkout", "-q", "-b", "s3")
        cand = r.commit("src/three.py", "z = 3\n", "S3 candidate")
        r.g("checkout", "-q", "master")
        r.commit(f"{KD}/S3-subject/outcome.md", table_outcome(cand, r.tree(cand)), "S3 outcome")
        r.push()
        rc, rows, out = self.run_tool()
        self.assertTrue(rows["S3"].startswith("S3 NOT-AT-IDENTITY NOT-DELIVERED"), out)
        rc, _, out = self.run_tool("--only", "S99")
        self.assertEqual(rc, 2)
        self.assertIn("REFUSE", out)


class NonAsciiPaths(unittest.TestCase):
    """git quotes a non-ASCII path unless core.quotepath is off, and a quoted path matches no prefix or glob.
    Every read goes through ``git()``, so the helper is what is pinned."""

    def test_git_helper_prints_non_ascii_paths_unquoted(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("delivery_at_identity", TOOL)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        root = Path(tempfile.mkdtemp(prefix="dai-quotepath-"))
        try:
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            subprocess.run(["git", "-C", str(root), "config", "core.quotepath", "true"], check=True)
            p = root / KD / "S1-café.md"
            p.parent.mkdir(parents=True)
            p.write_text("x\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "."], check=True)
            subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q",
                            "-m", "s1"], check=True)
            rc, out = mod.git(str(root), "log", "--name-only", "--format=", "HEAD")
            self.assertEqual((rc, out), (0, KD + "/S1-café.md"))
        finally:
            shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
