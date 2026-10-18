"""Fixture-repo tests for tools/kernel-subjects.py. Run directly: `python tools/kernel-subjects.tests.py`.

Every verdict here is read from a real git repository built in a temporary directory. The planted cases the brief
names are pinned beside their controls: a brief committed AFTER the first src commit fails (ORDER-VIOLATION), a brief
with no block fails (NO-BLOCK), and the same packet built the right way reads OK.
"""
from __future__ import annotations

import functools
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

TOOL = Path(__file__).with_name("kernel-subjects.py")
SPEC = importlib.util.spec_from_file_location("cloudvore_kernel_subjects", TOOL)
KS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(KS)

BUS = "99a1354"
FILTER = "tools/x.tests.py"
ENV = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.invalid", "GIT_COMMITTER_NAME": "t",
       "GIT_COMMITTER_EMAIL": "t@example.invalid", "GIT_AUTHOR_DATE": "2026-10-06T00:00:00+00:00",
       "GIT_COMMITTER_DATE": "2026-10-06T00:00:00+00:00"}


def block(row: str = "H900", filter_: str = FILTER, products: str | None = None,
          manifest: list[str] | None = None, **contract) -> str:
    return KS.render_block(row, filter_, BUS, products=products, manifest=manifest, **contract)


def brief(row: str = "H900", with_block: bool = True, products: str | None = None,
          manifest: list[str] | None = None, **contract) -> str:
    text = f"# Brief: {row}\n\nWhat to build.\n\n"
    if with_block:
        text += block(row, products=products, manifest=manifest, **contract) + "\n"
    return text + "## Constraints\n\nExplicit paths.\n\n## State\n\n- started\n"


class _Template:
    """The owner a fixture template is built for: never a test, so no test's cleanup removes the template; its
    temporary directory is removed when the process exits."""

    def addCleanup(self, *_args, **_kwargs) -> None:
        pass


_TEMPLATES: dict = {}      # (builder, its arguments) -> what the builder returned for a _Template


def fixture(build):
    """Build each distinct call of `build` once per process, into a template no test is ever handed, and give every
    caller its own copy: `shutil.copytree` of the template repository into the caller's own temporary directory.

    A fixture repository costs one git process per step, and the suites built the same history again for every
    test; on Windows each git.exe start is also a Defender scan (2026-10-09: about 37 starts every 15 s for over 20
    minutes, the package at 87-94 C). A copy carries the template's objects and refs, so every commit id a test
    reads is the one the builder made, and whatever the test then writes, commits or checks out happens in its copy
    alone."""
    @functools.wraps(build)
    def cached(test, *args, **kwargs):
        key = (build.__module__, build.__qualname__, repr(args), repr(sorted(kwargs.items())))
        if key not in _TEMPLATES:
            _TEMPLATES[key] = build(_Template(), *args, **kwargs)
        made = _TEMPLATES[key]
        if isinstance(made, Repo):
            return made.copy(test)
        if not isinstance(made, tuple) or sum(isinstance(x, Repo) for x in made) != 1:
            raise TypeError(f"a fixture returns one Repo, alone or in a tuple: {build.__qualname__} gave {made!r}")
        return tuple(x.copy(test) if isinstance(x, Repo) else x for x in made)
    return cached


class Repo:
    def __init__(self, test: unittest.TestCase):
        self._open(test)
        shutil.copytree(_blank().root, self.root, symlinks=True)

    def _open(self, test) -> None:
        self._d = tempfile.TemporaryDirectory()
        test.addCleanup(self._d.cleanup)
        self.root = Path(self._d.name) / "repo"

    def copy(self, test) -> "Repo":
        """A new repository in `test`'s own temporary directory, byte for byte this one."""
        r = Repo.__new__(Repo)
        r._open(test)
        shutil.copytree(self.root, r.root, symlinks=True)
        return r

    def git(self, *args: str) -> str:
        env = {**os.environ, **ENV}
        for k in list(env):
            if k.upper().startswith("GIT_TRACE") or k.upper() in KS._LOCATORS:
                env.pop(k)
        p = subprocess.run(["git", "-C", str(self.root), *args], capture_output=True, text=True, env=env)
        if p.returncode:
            raise AssertionError(f"git {args}: {p.stderr}")
        return p.stdout.strip()

    def write(self, path: str, text: str) -> None:
        f = self.root / path
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(text.encode("utf-8"))

    def commit(self, msg: str, *paths: str) -> str:
        self.git("add", "--", *(paths or ("README.md",)))
        self.git("commit", "-q", "-m", msg)
        return self.head()

    def head(self) -> str:
        """HEAD's commit id read from .git, as `rev-parse HEAD` would print it: HEAD names a loose ref or holds the id
        itself. Anything else (a packed ref, another ref backend) asks git."""
        dot = self.root / ".git"
        try:
            value = (dot / "HEAD").read_text(encoding="ascii").strip()
            if value.startswith("ref: refs/"):
                value = (dot / value[5:]).read_text(encoding="ascii").strip()
            if re.fullmatch("[0-9a-f]{40}", value):
                return value
        except (OSError, UnicodeDecodeError):
            pass
        return self.git("rev-parse", "HEAD")

    def branch(self, name: str, at: str = "master") -> None:
        self.git("checkout", "-q", "-b", name, at)

    def land(self, name: str, row: str = "H900") -> str:
        self.git("checkout", "-q", "master")
        self.git("merge", "-q", "--no-ff", "-m", f"Merge claude/{name} at x: thing ({row})", name)
        return self.head()

    def receipt(self, row: str, merge: str) -> str:
        self.write(f"review/kernel-receipts/{row}.md", f"# Kernel receipt\n\n- landed merge: {merge} (tree x)\n")
        return self.commit(f"{row} landed: receipt", f"review/kernel-receipts/{row}.md")


_BLANK: list = []


def _blank() -> Repo:
    """The template every Repo is copied from, built once: master with one commit of README.md."""
    if _BLANK:
        return _BLANK[0]
    r = Repo.__new__(Repo)
    r._open(_Template())
    r.root.mkdir()
    r.git("init", "-q", "-b", "master")
    r.git("config", "core.autocrlf", "false")
    r.write("README.md", "base\n")
    r.commit("base")
    _BLANK.append(r)
    return r


@fixture
def packet(t: unittest.TestCase, order: str = "brief-first", row: str = "H900", with_block: bool = True,
           receipted: bool = True) -> tuple[Repo, str]:
    """One landed packet. `order`: brief-first | src-first | same-commit | no-brief | tools-only."""
    r = Repo(t)
    r.branch("h900-thing")
    b = f"review/briefs/{row.lower()}.md"
    if order == "brief-first":
        r.write(b, brief(row, with_block)); r.commit("brief", b)
        r.write("src/a.cs", "a\n"); r.commit("src", "src/a.cs")
        r.write("tests/a.cs", "t\n"); r.commit("test", "tests/a.cs")
    elif order == "src-first":
        r.write("src/a.cs", "a\n"); r.commit("src", "src/a.cs")
        r.write(b, brief(row, with_block)); r.commit("brief", b)
    elif order == "same-commit":
        r.write(b, brief(row, with_block)); r.write("src/a.cs", "a\n"); r.commit("brief and src", b, "src/a.cs")
    elif order == "no-brief":
        r.write("src/a.cs", "a\n"); r.commit("src", "src/a.cs")
    elif order == "tools-only":
        r.write(b, brief(row, with_block)); r.commit("brief", b)
        r.write("tools/x.py", "x\n"); r.commit("tool", "tools/x.py")
    merge = r.land("h900-thing", row)
    if receipted:
        r.receipt(row, merge)
    return r, merge


class BlockTests(unittest.TestCase):
    def test_the_rendered_block_parses_clean_and_its_digest_recomputes(self):
        parsed = KS.parse_block(block())
        self.assertEqual([], parsed["problems"])
        self.assertEqual(parsed["fields"]["contract"], parsed["recomputed"])
        self.assertEqual("H900", parsed["row"])
        self.assertEqual("pending-cross-family", parsed["fields"]["key"])

    def test_the_default_bar_and_env_state_the_runner_ci_runs_on_resolves_to_and_never_claim_hosted(self):
        """K120: the default env said `hosted windows-latest` as a fact while CI_RUNS_ON sent both bars to the
        self-hosted ultra-magnus runner; every subject declared an environment its bars never ran in."""
        contract = KS.parse_block(block())["contract_text"]
        lines = {l.split(":", 1)[0]: l for l in contract.splitlines()}
        for key in ("bar", "env"):
            with self.subTest(key=key):
                self.assertIn("CI_RUNS_ON", lines[key])
                self.assertNotIn("hosted windows-latest", lines[key])
                self.assertNotIn("hosted Windows", lines[key])
                self.assertNotIn("hosted run", lines[key])
        self.assertIn(f"self-hosted ultra-magnus runner (Runner name {KS.BAR_RUNNER}), else windows-latest",
                      lines["env"])
        self.assertEqual("ultra-magnus-cloudvore", KS.BAR_RUNNER)

    def test_both_bar_workflows_resolve_runs_on_from_ci_runs_on_as_the_default_env_says(self):
        """The default env's claim is about the workflows; if a workflow stops reading CI_RUNS_ON, this goes red."""
        root = Path(__file__).resolve().parent.parent
        want = "runs-on: ${{ vars.CI_RUNS_ON != '' && fromJSON(vars.CI_RUNS_ON) || 'windows-latest' }}"
        for wf in ("tools-bar.yml", "product-bar.yml"):
            with self.subTest(workflow=wf):
                text = (root / ".github" / "workflows" / wf).read_text(encoding="utf-8")
                runs_on = [l.strip() for l in text.splitlines() if l.strip().startswith("runs-on:")]
                self.assertEqual([want], runs_on)

    def test_no_heading_is_none_and_a_mention_in_prose_is_not_a_heading(self):
        self.assertIsNone(KS.parse_block("# Brief\n\nadd a `## Kernel subject` block\n"))

    def test_crlf_text_parses_and_digests_as_lf(self):
        parsed = KS.parse_block(block().replace("\n", "\r\n"))
        self.assertEqual([], parsed["problems"])
        self.assertEqual(parsed["fields"]["contract"], parsed["recomputed"])

    def test_each_missing_field_is_malformed(self):
        for name in KS.FIELDS:
            with self.subTest(field=name):
                text = "\n".join(l for l in block().splitlines() if not l.startswith(f"- {name}:")) + "\n"
                self.assertIn(f"no {name} field", KS.parse_block(text)["problems"])

    def test_a_contract_key_missing_or_out_of_order_is_malformed(self):
        text = block().replace("filter: ", "filters: ")
        self.assertTrue(any("contract keys" in p for p in KS.parse_block(text)["problems"]))
        lines = block().split("\n")
        i, j = next(n for n, l in enumerate(lines) if l.startswith("bar: ")), \
            next(n for n, l in enumerate(lines) if l.startswith("filter: "))
        lines[i], lines[j] = lines[j], lines[i]
        self.assertTrue(any("contract keys" in p for p in KS.parse_block("\n".join(lines))["problems"]))

    def test_an_edited_contract_no_longer_recomputes(self):
        parsed = KS.parse_block(block().replace("3 identical green passes", "2 identical green passes"))
        self.assertEqual([], parsed["problems"])
        self.assertNotEqual(parsed["fields"]["contract"], parsed["recomputed"])

    def test_values_that_are_not_well_formed_are_malformed(self):
        for old, new in (("cloudvore/H900", "H900"), ("- kernel: r5", "- kernel: 5"),
                         ("code@r10 (bus 99a1354)", "code@r10"), ("pending-cross-family", "claude"),
                         (KS.DELIVERY, "master")):
            with self.subTest(old=old):
                self.assertTrue(KS.parse_block(block().replace(old, new, 1))["problems"], new)
        for text in (block(), block(manifest=["src/a.cs"])):          # K124: either identity, made unreadable
            with self.subTest(identity=KS.parse_block(text)["fields"]["identity"]):
                ident = KS.parse_block(text)["fields"]["identity"]
                self.assertTrue(KS.parse_block(text.replace(f"- identity: {ident}", "- identity: tree"))["problems"])

    def test_a_block_with_no_manifest_declares_the_default_identity_and_never_implies_one_is_required(self):
        """K124 (acceptance 4): the block said `identity: path manifest (declared below before review; ...)` even
        when no manifest was declared, as if a manifest were required; the receipt now credits such a subject by
        the profile's default identity, the landed merge's tree."""
        parsed = KS.parse_block(block())
        self.assertEqual(([], None), (parsed["problems"], parsed["manifest"]))
        self.assertTrue(parsed["fields"]["identity"].startswith("default (the landed merge's tree"),
                        parsed["fields"]["identity"])
        self.assertNotIn("path manifest", parsed["fields"]["identity"])
        self.assertNotIn("declared below before review", parsed["fields"]["identity"])
        with_manifest = KS.parse_block(block(manifest=["src/a.cs"]))
        self.assertEqual([], with_manifest["problems"])
        self.assertTrue(with_manifest["fields"]["identity"].startswith("path manifest"))
        out = io.StringIO()
        with redirect_stdout(out), redirect_stderr(io.StringIO()):
            self.assertEqual(0, KS.main(["block", "--row", "H1", "--filter", "x", "--bus-sha", BUS]))
        self.assertIn("- identity: default (the landed merge's tree", out.getvalue())
        self.assertNotIn("```manifest", out.getvalue())

    def test_check_reads_a_default_identity_block_with_no_manifest_ok(self):
        r, merge = packet(self)
        got = KS.check(r.root, merge, at="master")
        self.assertEqual(("OK", None), (got["status"], got["manifest"]), got)
        brief_text = KS.path_at(r.root, merge, "review/briefs/h900.md")
        self.assertIn("- identity: default (the landed merge's tree", brief_text)

    def test_the_key_classes_that_are_not_pending_parse(self):
        for key in ("cross-family:codex", "ci-runner:github-hosted", "human:owner"):
            with self.subTest(key=key):
                self.assertEqual([], KS.parse_block(block().replace("pending-cross-family", key))["problems"])

    def test_the_contract_carries_env_harness_limits_review_scope_and_charter(self):
        """Round 1, seat B: code@r10 binds these before work; a contract without them is malformed."""
        parsed = KS.parse_block(block())
        keys = [l.split(":", 1)[0] for l in parsed["contract_text"].splitlines()]
        self.assertEqual(list(KS.CONTRACT_KEYS), keys)
        for key in ("env", "harness-limits", "review-scope", "charter"):
            with self.subTest(key=key):
                text = "\n".join(l for l in block().splitlines() if not l.startswith(f"{key}: ")) + "\n"
                self.assertTrue(any("contract keys" in p for p in KS.parse_block(text)["problems"]), key)

    def test_products_default_to_src_and_tests_and_parse_when_declared(self):
        self.assertEqual(("src/", "tests/"), tuple(KS.parse_block(block())["products"]))
        parsed = KS.parse_block(block(products="tools/ docs/"))
        self.assertEqual(([], ("src/", "tests/", "tools/", "docs/")), (parsed["problems"], tuple(parsed["products"])))
        self.assertEqual(("src/", "tests/"), tuple(KS.parse_block(block(products="src/ zzz/"))["products"])[:2])
        for bad in ("/abs/", "../up/", "tools/ tools/"):
            with self.subTest(products=bad):
                self.assertTrue(KS.parse_block(block().replace("- delivery:", f"- products: {bad}\n- delivery:"))
                                ["problems"])

    def test_every_git_call_prints_paths_unquoted_and_a_path_git_still_quotes_is_refused(self):
        self.assertIn("core.quotePath=false", KS.git_argv(Path("."), "log"))
        self.assertEqual(["src/café.cs"], KS.listed_paths("src/café.cs\n"))
        with self.assertRaises(KS.GitFailed):
            KS.listed_paths('src/a.cs\n"src/tab\\there.cs"\n')

    def test_a_declared_manifest_parses_and_a_duplicate_is_malformed(self):
        parsed = KS.parse_block(block(manifest=["review/briefs/h900.md", "src/a.cs"]))
        self.assertEqual(([], ["review/briefs/h900.md", "src/a.cs"]), (parsed["problems"], parsed["manifest"]))
        self.assertTrue(KS.parse_block(block(manifest=["src/a.cs", "src/a.cs"]))["problems"])
        self.assertIsNone(KS.parse_block(block())["manifest"])

    def test_the_block_command_takes_products_manifest_and_contract_keys(self):
        out = io.StringIO()
        with redirect_stdout(out), redirect_stderr(io.StringIO()):
            code = KS.main(["block", "--row", "H1", "--filter", "x", "--bus-sha", BUS, "--products", "tools/ docs/",
                            "--manifest", "tools/b.py", "--manifest", "tools/a.py", "--charter", "static review"])
        self.assertEqual(0, code)
        parsed = KS.parse_block(out.getvalue())
        self.assertEqual([], parsed["problems"])
        self.assertEqual((("src/", "tests/", "tools/", "docs/"), ["tools/a.py", "tools/b.py"]),
                         (parsed["products"], parsed["manifest"]))
        self.assertIn("charter: static review\n", parsed["contract_text"])

    def test_the_block_command_refuses_a_filter_that_breaks_the_contract(self):
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.assertEqual(2, KS.main(["block", "--row", "H1", "--filter", "", "--bus-sha", BUS]))
            self.assertEqual(0, KS.main(["block", "--row", "H1", "--filter", "x", "--bus-sha", BUS]))


class CheckTests(unittest.TestCase):
    def test_control_brief_first_landing_with_receipt_is_ok(self):
        r, merge = packet(self)
        got = KS.check(r.root, merge, at="master")
        self.assertEqual(("OK", []), (got["status"], got["flags"]), got)
        self.assertEqual("review/briefs/h900.md", got["brief"])
        self.assertIsNotNone(got["first_product"])
        self.assertEqual("review/kernel-receipts/H900.md", got["receipt"])

    def test_planted_brief_after_the_first_src_commit_fails(self):
        r, merge = packet(self, order="src-first")
        got = KS.check(r.root, merge, at="master")
        self.assertEqual("ORDER-VIOLATION", got["status"], got)
        self.assertEqual([got["first_product"]], got["violators"])

    def test_planted_brief_in_the_same_commit_as_the_first_src_byte_fails(self):
        r, merge = packet(self, order="same-commit")
        self.assertEqual("ORDER-VIOLATION", KS.check(r.root, merge, at="master")["status"])

    def test_planted_missing_block_fails(self):
        r, merge = packet(self, with_block=False)
        got = KS.check(r.root, merge, at="master")
        self.assertEqual(("NO-BLOCK", ["NO-BLOCK"]), (got["status"], got["flags"]))
        self.assertEqual("H900", got["name"])

    def test_no_brief_at_all_fails(self):
        r, merge = packet(self, order="no-brief")
        self.assertEqual("NO-BRIEF", KS.check(r.root, merge, at="master")["status"])

    def test_a_tools_only_packet_that_declares_no_products_is_undeclared(self):
        """Round 2 adjudication: before it, this packet read OK with nothing to order."""
        r, merge = packet(self, order="tools-only")
        got = KS.check(r.root, merge, at="master")
        self.assertEqual(("PRODUCTS-UNDECLARED", None, ["tools/x.py"]),
                         (got["status"], got["first_product"], got["undeclared"]))

    def test_a_landing_with_no_receipt_fails_and_one_naming_another_merge_fails(self):
        r, merge = packet(self, receipted=False)
        self.assertEqual("NO-RECEIPT", KS.check(r.root, merge, at="master")["status"])
        r.receipt("H900", "0" * 40)
        self.assertEqual("RECEIPT-MISMATCH", KS.check(r.root, merge, at="master")["status"])

    def test_the_receipt_is_read_at_the_at_ref_not_at_the_merge(self):
        r, merge = packet(self)
        self.assertEqual("NO-RECEIPT", KS.check(r.root, merge)["status"])        # the merge's own tree precedes it
        self.assertEqual("OK", KS.check(r.root, merge, at="master")["status"])

    def test_a_contract_edited_without_its_digest_fails(self):
        r = Repo(self); r.branch("h900-thing")
        r.write("review/briefs/h900.md", brief().replace("3 identical green passes", "1 green pass"))
        r.commit("brief", "review/briefs/h900.md")
        r.write("src/a.cs", "a\n"); r.commit("src", "src/a.cs")
        merge = r.land("h900-thing"); r.receipt("H900", merge)
        self.assertEqual("CONTRACT-MISMATCH", KS.check(r.root, merge, at="master")["status"])

    def test_a_contract_changed_after_the_block_was_declared_fails_even_when_it_recomputes(self):
        r = Repo(self); r.branch("h900-thing")
        r.write("review/briefs/h900.md", brief()); r.commit("brief", "review/briefs/h900.md")
        r.write("src/a.cs", "a\n"); r.commit("src", "src/a.cs")
        later = brief().replace(block(), block(filter_="tools/other.tests.py"))
        r.write("review/briefs/h900.md", later); r.commit("loosen the contract", "review/briefs/h900.md")
        merge = r.land("h900-thing"); r.receipt("H900", merge)
        got = KS.check(r.root, merge, at="master")
        self.assertEqual("CONTRACT-CHANGED", got["status"], got)
        self.assertEqual(got["contract"], got["recomputed"])

    def test_state_edits_to_the_brief_after_work_starts_do_not_move_the_block(self):
        r = Repo(self); r.branch("h900-thing")
        r.write("review/briefs/h900.md", brief()); first = r.commit("brief", "review/briefs/h900.md")
        r.write("src/a.cs", "a\n"); r.commit("src", "src/a.cs")
        r.write("review/briefs/h900.md", brief() + "- round 1 done\n"); r.commit("state", "review/briefs/h900.md")
        merge = r.land("h900-thing"); r.receipt("H900", merge)
        got = KS.check(r.root, merge, at="master")
        self.assertEqual(("OK", first), (got["status"], got["block_commit"]))

    def test_master_merged_into_the_branch_does_not_count_masters_src_commits(self):
        """The legitimate negative: landings merge master in, and master's own src commits are not the packet's."""
        r = Repo(self); r.branch("h900-thing")
        r.write("review/briefs/h900.md", brief()); r.commit("brief", "review/briefs/h900.md")
        r.git("checkout", "-q", "master")
        r.write("src/other.cs", "o\n"); r.commit("someone else's src", "src/other.cs")
        r.git("checkout", "-q", "h900-thing")
        r.git("merge", "-q", "--no-ff", "-m", "merge master in", "master")
        r.write("src/a.cs", "a\n"); r.commit("src", "src/a.cs")
        merge = r.land("h900-thing"); r.receipt("H900", merge)
        self.assertEqual("OK", KS.check(r.root, merge, at="master")["status"])

    def test_a_src_commit_on_a_side_line_made_before_the_block_is_a_violation(self):
        """Ancestry, not position: a src commit merged in from a side line that never saw the brief."""
        r = Repo(self); r.branch("side")
        r.write("src/early.cs", "e\n"); r.commit("early src", "src/early.cs")
        r.git("checkout", "-q", "master"); r.branch("h900-thing")
        r.write("review/briefs/h900.md", brief()); r.commit("brief", "review/briefs/h900.md")
        r.git("merge", "-q", "--no-ff", "-m", "merge the side line", "side")
        merge = r.land("h900-thing"); r.receipt("H900", merge)
        got = KS.check(r.root, merge, at="master")
        self.assertEqual("ORDER-VIOLATION", got["status"], got)

    def test_a_non_ascii_product_path_before_the_block_is_a_violation(self):
        """Round 1, seat A (P1): git quotes a non-ASCII path by default (a leading double quote and octal escapes),
        which does not start with `src/`, so the product commit was never seen and the packet read OK."""
        r = Repo(self); r.branch("h900-thing")
        r.write("src/café.cs", "a\n"); r.commit("src", "src/café.cs")
        r.write("review/briefs/h900.md", brief()); r.commit("brief", "review/briefs/h900.md")
        merge = r.land("h900-thing"); r.receipt("H900", merge)
        got = KS.check(r.root, merge, at="master")
        self.assertEqual("ORDER-VIOLATION", got["status"], got)

    def test_a_tooling_packet_that_declares_its_products_is_ordered_against_them(self):
        """Round 1: with only src/ and tests/ counted, a tools packet's ORDER was vacuous."""
        r = Repo(self); r.branch("h900-thing")
        r.write("tools/x.py", "x\n"); r.commit("tool first", "tools/x.py")
        r.write("review/briefs/h900.md", brief(products="tools/ docs/")); r.commit("brief", "review/briefs/h900.md")
        merge = r.land("h900-thing"); r.receipt("H900", merge)
        got = KS.check(r.root, merge, at="master")
        self.assertEqual(("ORDER-VIOLATION", ["src/", "tests/", "tools/", "docs/"]), (got["status"], got["products"]), got)
        # the control: the same tooling packet, brief first
        r = Repo(self); r.branch("h900-thing")
        r.write("review/briefs/h900.md", brief(products="tools/ docs/")); r.commit("brief", "review/briefs/h900.md")
        r.write("tools/x.py", "x\n"); tool = r.commit("tool", "tools/x.py")
        merge = r.land("h900-thing"); r.receipt("H900", merge)
        got = KS.check(r.root, merge, at="master")
        self.assertEqual(("OK", tool), (got["status"], got["first_product"]), got)

    def test_a_late_block_cannot_narrow_the_products_away_from_src(self):
        """Round 2, seat A (N1): product commits first, then a block declaring `products: zzz/` read OK with
        first-product=none. src/ and tests/ are always products, so the late block is an ORDER-VIOLATION."""
        r = Repo(self); r.branch("h900-thing")
        r.write("src/a.cs", "a\n"); r.write("tests/a.cs", "a\n"); first = r.commit("product first", "src/a.cs", "tests/a.cs")
        r.write("review/briefs/h900.md", brief(products="zzz/")); r.commit("late brief", "review/briefs/h900.md")
        merge = r.land("h900-thing"); r.receipt("H900", merge)
        got = KS.check(r.root, merge, at="master")
        self.assertEqual(("ORDER-VIOLATION", first), (got["status"], got["first_product"]), got)
        self.assertEqual(["src/", "tests/", "zzz/"], got["products"])

    def test_a_path_outside_the_products_and_review_is_undeclared(self):
        r = Repo(self); r.branch("h900-thing")
        r.write("review/briefs/h900.md", brief()); r.commit("brief", "review/briefs/h900.md")
        r.write("src/a.cs", "a\n"); r.write("tools/x.py", "x\n"); r.write("review/ledger-h900.md", "l\n")
        r.commit("work", "src/a.cs", "tools/x.py", "review/ledger-h900.md")
        merge = r.land("h900-thing"); r.receipt("H900", merge)
        got = KS.check(r.root, merge, at="master")
        self.assertEqual(("PRODUCTS-UNDECLARED", ["tools/x.py"]), (got["status"], got["undeclared"]), got)

    def test_a_key_class_changed_after_the_block_was_declared_is_a_change(self):
        r = Repo(self); r.branch("h900-thing")
        r.write("review/briefs/h900.md", brief()); r.commit("brief", "review/briefs/h900.md")
        r.write("src/a.cs", "a\n"); r.commit("src", "src/a.cs")
        r.write("review/briefs/h900.md", brief().replace("- key: pending-cross-family", "- key: human:owner"))
        r.commit("swap the key class", "review/briefs/h900.md")
        merge = r.land("h900-thing"); r.receipt("H900", merge)
        self.assertEqual("CONTRACT-CHANGED", KS.check(r.root, merge, at="master")["status"])

    def test_a_contract_changed_and_changed_back_is_still_changed(self):
        """Round 1, seat A (P3): only the first block and the tip were compared."""
        r = Repo(self); r.branch("h900-thing")
        r.write("review/briefs/h900.md", brief()); r.commit("contract A", "review/briefs/h900.md")
        r.write("src/a.cs", "a\n"); r.commit("src", "src/a.cs")
        r.write("review/briefs/h900.md", brief().replace(block(), block(filter_="tools/other.tests.py")))
        r.commit("contract B", "review/briefs/h900.md")
        r.write("review/briefs/h900.md", brief()); r.commit("contract A again", "review/briefs/h900.md")
        merge = r.land("h900-thing"); r.receipt("H900", merge)
        self.assertEqual("CONTRACT-CHANGED", KS.check(r.root, merge, at="master")["status"])

    def test_a_second_brief_with_other_terms_for_the_same_subject_is_a_change(self):
        """Round 1, seat A (P4)."""
        r = Repo(self); r.branch("h900-thing")
        r.write("review/briefs/h900.md", brief()); r.commit("brief", "review/briefs/h900.md")
        r.write("src/a.cs", "a\n"); r.commit("src", "src/a.cs")
        r.write("review/briefs/h900-v2.md", brief().replace(block(), block(filter_="tools/other.tests.py")))
        r.commit("second brief", "review/briefs/h900-v2.md")
        merge = r.land("h900-thing"); r.receipt("H900", merge)
        self.assertEqual("CONTRACT-CHANGED", KS.check(r.root, merge, at="master")["status"])

    def test_products_changed_after_the_block_was_declared_is_a_change(self):
        r = Repo(self); r.branch("h900-thing")
        r.write("review/briefs/h900.md", brief(products="tools/")); r.commit("brief", "review/briefs/h900.md")
        r.write("tools/x.py", "x\n"); r.commit("tool", "tools/x.py")
        r.write("review/briefs/h900.md", brief(products="docs/")); r.commit("narrow the products", "review/briefs/h900.md")
        merge = r.land("h900-thing"); r.receipt("H900", merge)
        self.assertEqual("CONTRACT-CHANGED", KS.check(r.root, merge, at="master")["status"])

    def test_a_manifest_added_before_review_is_not_a_change(self):
        r = Repo(self); r.branch("h900-thing")
        r.write("review/briefs/h900.md", brief()); r.commit("brief", "review/briefs/h900.md")
        r.write("src/a.cs", "a\n"); r.commit("src", "src/a.cs")
        r.write("review/briefs/h900.md", brief(manifest=["review/briefs/h900.md", "src/a.cs"]))
        r.commit("declare the manifest before review", "review/briefs/h900.md")
        merge = r.land("h900-thing"); r.receipt("H900", merge)
        got = KS.check(r.root, merge, at="master")
        self.assertEqual(("OK", ["review/briefs/h900.md", "src/a.cs"]), (got["status"], got["manifest"]), got)

    def test_a_manifest_changed_after_it_was_declared_is_a_change(self):
        """K95 (round 2, seat B finding C): the manifest was not a compared term; a later change raised no flag."""
        m1, m2 = ["review/briefs/h900.md", "src/a.cs"], ["review/briefs/h900.md", "src/a.cs", "tools/h.py"]
        cases = (("widened", [m1, m2]), ("dropped", [m1, None]), ("changed and changed back", [m1, m2, m1]))
        for why, seq in cases:
            with self.subTest(why=why):
                r = Repo(self); r.branch("h900-thing")
                r.write("review/briefs/h900.md", brief(manifest=seq[0])); r.commit("brief", "review/briefs/h900.md")
                r.write("src/a.cs", "a\n"); r.commit("src", "src/a.cs")
                for i, m in enumerate(seq[1:]):
                    r.write("review/briefs/h900.md", brief(manifest=m)); r.commit(f"manifest {i}", "review/briefs/h900.md")
                merge = r.land("h900-thing"); r.receipt("H900", merge)
                got = KS.check(r.root, merge, at="master")
                self.assertEqual("CONTRACT-CHANGED", got["status"], got)
                self.assertTrue(any("declares manifest" in p for p in got["problems"]), got["problems"])

    def test_a_manifest_changed_and_restored_inside_merge_resolutions_is_a_change(self):
        """K95 round 2 (Codex, probe_f1): merges listed no paths, so brief versions made in merge resolutions were
        never read and a manifest changed and restored through two merges read OK."""
        m1, m2 = ["review/briefs/h900.md", "src/a.cs"], ["review/briefs/h900.md", "src/a.cs", "tools/h.py"]
        r = Repo(self); r.branch("h900-thing")
        r.write("review/briefs/h900.md", brief(manifest=m1)); r.commit("brief", "review/briefs/h900.md")
        r.write("src/a.cs", "a\n"); r.commit("src", "src/a.cs")
        for i, m in enumerate([m2, m1]):
            r.git("checkout", "-q", "master"); r.write(f"m{i}.txt", "x\n"); r.commit(f"master {i}", f"m{i}.txt")
            r.git("checkout", "-q", "h900-thing")
            r.git("merge", "-q", "--no-commit", "--no-ff", "master")
            r.write("review/briefs/h900.md", brief(manifest=m)); r.git("add", "review/briefs/h900.md")
            r.git("commit", "-q", "-m", f"merge master {i} (resolution edits the manifest)")
        merge = r.land("h900-thing"); r.receipt("H900", merge)
        got = KS.check(r.root, merge, at="master")
        self.assertEqual("CONTRACT-CHANGED", got["status"], got)
        self.assertTrue(any("declares manifest" in p for p in got["problems"]), got["problems"])

    def test_a_brief_renamed_inside_a_merge_with_another_manifest_is_a_change(self):
        """K95 round 3 (Codex probe_f3 and the Claude seat's P1, each reproduced): a brief renamed inside one merge's
        resolution, carrying a widened manifest, and renamed back in a later merge, existed at no non-merge commit,
        so the brief walk never read it and the packet read OK."""
        m1, m2 = ["review/briefs/h900.md", "src/a.cs"], ["review/briefs/h900x.md", "src/a.cs", "tools/h.py"]
        r = Repo(self); r.branch("h900-thing")
        r.write("review/briefs/h900.md", brief(manifest=m1)); r.commit("brief", "review/briefs/h900.md")
        r.write("src/a.cs", "a\n"); r.commit("src", "src/a.cs")
        for i, (gone, here, m) in enumerate([("review/briefs/h900.md", "review/briefs/h900x.md", m2),
                                             ("review/briefs/h900x.md", "review/briefs/h900.md", m1)]):
            r.git("checkout", "-q", "master"); r.write(f"m{i}.txt", "x\n"); r.commit(f"master {i}", f"m{i}.txt")
            r.git("checkout", "-q", "h900-thing")
            r.git("merge", "-q", "--no-commit", "--no-ff", "master")
            r.git("rm", "-q", gone); r.write(here, brief(manifest=m)); r.git("add", here)
            r.git("commit", "-q", "-m", f"merge master {i} (resolution renames the brief)")
        merge = r.land("h900-thing"); r.receipt("H900", merge)
        got = KS.check(r.root, merge, at="master")
        self.assertEqual("CONTRACT-CHANGED", got["status"], got)

    def test_master_merged_in_with_another_packets_brief_is_not_a_change(self):
        """The control: a merge of master carrying another subject's brief reads only this packet's briefs."""
        r = Repo(self); r.branch("h900-thing")
        r.write("review/briefs/h900.md", brief(manifest=["review/briefs/h900.md", "src/a.cs"]))
        r.commit("brief", "review/briefs/h900.md")
        r.write("src/a.cs", "a\n"); r.commit("src", "src/a.cs")
        r.git("checkout", "-q", "master")
        r.write("review/briefs/h901.md", brief("H901", manifest=["src/b.cs"])); r.commit("h901", "review/briefs/h901.md")
        r.git("checkout", "-q", "h900-thing"); r.git("merge", "-q", "--no-ff", "-m", "merge master", "master")
        merge = r.land("h900-thing"); r.receipt("H900", merge)
        self.assertEqual("OK", KS.check(r.root, merge, at="master")["status"])

    def test_a_manifest_reordered_is_the_same_set_and_not_a_change(self):
        r = Repo(self); r.branch("h900-thing")
        r.write("review/briefs/h900.md", brief(manifest=["review/briefs/h900.md", "src/a.cs"]))
        r.commit("brief", "review/briefs/h900.md")
        r.write("src/a.cs", "a\n"); r.commit("src", "src/a.cs")
        r.write("review/briefs/h900.md", brief(manifest=["src/a.cs", "review/briefs/h900.md"]))
        r.commit("reorder", "review/briefs/h900.md")
        merge = r.land("h900-thing"); r.receipt("H900", merge)
        self.assertEqual("OK", KS.check(r.root, merge, at="master")["status"])

    def test_a_second_brief_with_another_manifest_is_a_change(self):
        r = Repo(self); r.branch("h900-thing")
        r.write("review/briefs/h900.md", brief(manifest=["review/briefs/h900.md", "src/a.cs"]))
        r.commit("brief", "review/briefs/h900.md")
        r.write("src/a.cs", "a\n"); r.commit("src", "src/a.cs")
        r.write("review/briefs/h900-v2.md", brief(manifest=["src/a.cs"])); r.commit("v2", "review/briefs/h900-v2.md")
        merge = r.land("h900-thing"); r.receipt("H900", merge)
        self.assertEqual("CONTRACT-CHANGED", KS.check(r.root, merge, at="master")["status"])

    def test_two_briefs_declaring_different_subjects_are_ambiguous(self):
        r = Repo(self); r.branch("h900-thing")
        r.write("review/briefs/h900.md", brief()); r.write("review/briefs/h901.md", brief("H901"))
        r.commit("briefs", "review/briefs/h900.md", "review/briefs/h901.md")
        merge = r.land("h900-thing"); r.receipt("H900", merge)
        self.assertIn("AMBIGUOUS", KS.check(r.root, merge, at="master")["flags"])

    def test_a_branch_tip_is_read_against_its_base_and_owes_no_receipt(self):
        r = Repo(self); r.branch("h900-thing")
        r.write("review/briefs/h900.md", brief()); r.commit("brief", "review/briefs/h900.md")
        r.write("src/a.cs", "a\n"); r.commit("src", "src/a.cs")
        got = KS.check(r.root, "h900-thing", base="master")
        self.assertEqual(("OK", False, None), (got["status"], got["landing"], got["receipt"]))

    def test_the_cli_exit_codes(self):
        r, merge = packet(self, order="src-first")
        good, gmerge = packet(self)
        with redirect_stdout(io.StringIO()) as out, redirect_stderr(io.StringIO()):
            self.assertEqual(1, KS.main(["--repo", str(r.root), "check", merge, "--at", "master"]))
            self.assertEqual(0, KS.main(["--repo", str(good.root), "check", gmerge, "--at", "master"]))
            self.assertEqual(2, KS.main(["--repo", str(good.root), "check", "no-such-ref"]))
            self.assertEqual(1, KS.main(["--repo", str(r.root), "check", merge, "--at", "master", "--json"]))
        self.assertIn("ORDER-VIOLATION", out.getvalue())

    def test_the_script_runs_as_a_child(self):
        r, merge = packet(self, with_block=False)
        p = subprocess.run([sys.executable, str(TOOL), "--repo", str(r.root), "check", merge, "--at", "master"],
                           capture_output=True, text=True)
        self.assertEqual((1, ""), (p.returncode, p.stderr))
        self.assertTrue(p.stdout.startswith("cloudvore/H900? NO-BLOCK landing="), p.stdout)


# ---- K170: a merge FROM master into a packet branch is not a landing ------------------------------------------------

# What a verdict is: every field `check` derives from the packet, beside the two that name the commit read.
VERDICT = ("status", "flags", "subject", "row", "brief", "block_commit", "first_product", "products", "undeclared",
           "violators", "contract", "recomputed", "receipt", "manifest", "landing", "base", "name")


def verdict(got: dict) -> dict:
    return {k: got[k] for k in VERDICT}


@fixture
def merged_from_master(t: unittest.TestCase, order: str = "brief-first",
                       direct_brief: bool = False) -> tuple[Repo, str, str]:
    """(repo, pre, tip): packet H900 on its branch (`order`: brief-first | src-first), then another packet H901
    declared, landed on master and receipted, then master merged INTO the H900 branch (first parent = the branch):
    the shape of H95's 4fde7af (master carrying H40's landing). `pre` is the branch tip before that merge.
    `direct_brief`: master's own first-parent line also gets a non-merge commit editing a brief (K170 key round 2,
    finding 1), after H901's receipt and before the merge into H900."""
    r = Repo(t); r.branch("h900-thing")
    if order == "src-first":
        r.write("src/a.cs", "a\n"); r.commit("src", "src/a.cs")
        r.write("review/briefs/h900.md", brief()); r.commit("brief", "review/briefs/h900.md")
    else:
        r.write("review/briefs/h900.md", brief()); r.commit("brief", "review/briefs/h900.md")
        r.write("src/a.cs", "a\n"); r.commit("src", "src/a.cs")
    pre = r.head()
    r.git("checkout", "-q", "master"); r.branch("h901-other")
    r.write("review/briefs/h901.md", brief("H901")); r.commit("brief", "review/briefs/h901.md")
    r.write("tools/y.py", "y\n"); r.commit("an undeclared tool", "tools/y.py")
    other = r.land("h901-other", "H901"); r.receipt("H901", other)
    if direct_brief:
        r.write("review/briefs/h901.md", brief("H901") + "- a State line written on master\n")
        r.commit("H901 State line, directly on master", "review/briefs/h901.md")
    r.git("checkout", "-q", "h900-thing")
    r.git("merge", "-q", "--no-ff", "-m", "Merge origin/master into h900-thing", "master")
    return r, pre, r.head()


class K170MergeFromMasterTests(unittest.TestCase):
    """K170 (H95's builder at 4fde7af, H208's builder after it): `check` read ANY two-parent tip as a landing, first
    parent = base, second = the packet, so a branch tip that merged master in reported master's newest landing
    (`cloudvore/H40 PRODUCTS-UNDECLARED landing=...`). Builders merge master normally, so every such merge tripped it."""

    def test_master_merged_into_the_branch_reads_the_packets_own_verdict(self):
        r, pre, tip = merged_from_master(self)
        self.assertEqual([pre, KS.rev(r.root, "master")], r.git("log", "-1", "--format=%P", tip).split())
        before = KS.check(r.root, pre, base="master")
        got = KS.check(r.root, tip, base="master")
        self.assertEqual(("OK", "cloudvore/H900", False), (before["status"], before["subject"], before["landing"]))
        self.assertEqual(verdict(before), verdict(got), got)
        self.assertEqual(tip, got["tip"])

    def test_master_merged_into_a_flagged_branch_keeps_the_branchs_own_flags(self):
        """Not only OK survives: a packet ordered wrong still reads its own ORDER-VIOLATION, never H901's flags."""
        r, pre, tip = merged_from_master(self, order="src-first")
        before = KS.check(r.root, pre, base="master")
        got = KS.check(r.root, tip, base="master")
        self.assertEqual(("ORDER-VIOLATION", "cloudvore/H900"), (before["status"], before["subject"]))
        self.assertEqual(verdict(before), verdict(got), got)

    def test_the_cli_at_the_merged_tip_prints_the_branch_reading(self):
        r, _pre, tip = merged_from_master(self)
        with redirect_stdout(io.StringIO()) as out, redirect_stderr(io.StringIO()):
            code = KS.main(["--repo", str(r.root), "check", tip, "--base", "master"])
        self.assertEqual(0, code, out.getvalue())
        self.assertTrue(out.getvalue().startswith(f"cloudvore/H900 OK branch={tip[:9]} "), out.getvalue())

    def test_a_real_landing_reads_as_a_landing_whatever_base_is_named(self):
        """The control: master's first parent and the packet second, on master or on a land ref not yet pushed,
        with the base resolvable (master, origin/master) or not (no origin/master: today's fixture default)."""
        r, merge = packet(self)
        want = verdict(KS.check(r.root, merge, at="master"))          # the default base: no origin/master here
        self.assertEqual(("OK", True), (want["status"], want["landing"]))
        r.git("update-ref", "refs/remotes/origin/master", "master")
        for base in ("master", "origin/master", merge):
            with self.subTest(base=base):
                self.assertEqual(want, verdict(KS.check(r.root, merge, base=base, at="master")))
        # a landing being made on a land ref: its first parent is the base's tip, its second the packet
        r.git("checkout", "-q", "-b", "h902-thing", "master")
        r.write("review/briefs/h902.md", brief("H902")); r.commit("brief", "review/briefs/h902.md")
        r.write("src/c.cs", "c\n"); r.commit("src", "src/c.cs")
        r.git("checkout", "-q", "-b", "land/h902", "master")
        r.git("merge", "-q", "--no-ff", "-m", "Merge claude/h902-thing at x: thing (H902)", "h902-thing")
        land = r.head()
        got = KS.check(r.root, land, base="origin/master")
        self.assertEqual((True, "cloudvore/H902", "NO-RECEIPT"), (got["landing"], got["subject"], got["status"]))

    def test_a_merge_of_two_packet_branches_reads_as_today(self):
        """Recorded, not changed: a branch merging ANOTHER packet's unlanded branch is read, as before K170, as a
        landing of the second parent (neither side is in the base)."""
        r = Repo(self); r.branch("h901-other")
        r.write("review/briefs/h901.md", brief("H901")); r.commit("brief", "review/briefs/h901.md")
        r.write("src/b.cs", "b\n"); r.commit("src", "src/b.cs")
        r.git("checkout", "-q", "master"); r.branch("h900-thing")
        r.write("review/briefs/h900.md", brief()); r.commit("brief", "review/briefs/h900.md")
        first = r.head()
        r.git("merge", "-q", "--no-ff", "-m", "merge the other packet", "h901-other")
        got = KS.check(r.root, r.head(), base="master")
        self.assertEqual((True, "cloudvore/H901", first, KS.rev(r.root, "h901-other"), ["NO-RECEIPT"]),
                         (got["landing"], got["subject"], got["base"], got["tip"], got["flags"]), got)

    def test_an_octopus_merge_reads_as_today(self):
        """Recorded, not changed: three parents were never a landing; the tip is read against the base."""
        r = Repo(self)
        for side in ("side-a", "side-b"):
            r.git("checkout", "-q", "master"); r.branch(side)
            r.write(f"src/{side}.cs", "s\n"); r.commit(side, f"src/{side}.cs")
        r.git("checkout", "-q", "master"); r.branch("h900-thing")
        r.write("review/briefs/h900.md", brief()); r.commit("brief", "review/briefs/h900.md")
        r.git("merge", "-q", "--no-ff", "-m", "octopus", "side-a", "side-b")
        got = KS.check(r.root, r.head(), base="master")
        self.assertEqual((False, "cloudvore/H900", "ORDER-VIOLATION", KS.rev(r.root, "master")),
                         (got["landing"], got["subject"], got["status"], got["base"]), got)

    def test_the_advisory_reads_every_first_parent_merge_as_a_landing(self):
        """Reader domain (weak-pin shape c): the advisory walks `ref`'s first-parent merges, every one a landing. A
        local master whose newest first-parent merge brought in a line origin/master already holds (first parent
        not in origin/master, second parent in it) is still read as that line's landing, never as a branch tip."""
        r = Repo(self); r.branch("k1-tool")
        r.write("review/briefs/k1.md", brief("K1", products="tools/")); r.commit("brief", "review/briefs/k1.md")
        r.write(KS.TOOL_PATH, "# the tool\n"); r.commit("tool", KS.TOOL_PATH)
        tool = r.land("k1-tool", "K1"); r.receipt("K1", tool)
        r.branch("h2-good")
        r.write("review/briefs/h2.md", brief("H2")); r.commit("brief", "review/briefs/h2.md")
        r.write("src/b.cs", "b\n"); r.commit("src", "src/b.cs")
        r.git("update-ref", "refs/remotes/origin/master", "h2-good")
        r.git("checkout", "-q", "master"); r.write("local.txt", "l\n"); r.commit("a local commit", "local.txt")
        good = r.land("h2-good", "H2"); r.receipt("H2", good)
        # the topology the pin needs: the landing's first parent is not in origin/master, its second parent is
        is_in = lambda a: subprocess.run(["git", "-C", str(r.root), "merge-base", "--is-ancestor", a,  # noqa: E731
                                          "origin/master"]).returncode == 0
        self.assertEqual((False, True), (is_in(f"{good}^1"), is_in(f"{good}^2")))
        got = KS.advisory(r.root, "master")
        self.assertEqual((tool, 2, 2, []), (got["since"], got["landings"], got["checked"], got["flagged"]), got)


@fixture
def landed_beside_a_pushed_line(t: unittest.TestCase) -> tuple[Repo, str, str]:
    """(repo, tool, good): K170 key round 1, finding 1. K1 (this tool) landed and receipted; H2 declared on its branch,
    which origin/master already holds; local master gained a commit origin/master lacks; then H2 landed on local
    master and was receipted. The landing's second parent is in origin/master and its first parent is not."""
    r = Repo(t); r.branch("k1-tool")
    r.write("review/briefs/k1.md", brief("K1", products="tools/")); r.commit("brief", "review/briefs/k1.md")
    r.write(KS.TOOL_PATH, "# the tool\n"); r.commit("tool", KS.TOOL_PATH)
    tool = r.land("k1-tool", "K1"); r.receipt("K1", tool)
    r.branch("h2-good")
    r.write("review/briefs/h2.md", brief("H2")); r.commit("brief", "review/briefs/h2.md")
    r.write("src/b.cs", "b\n"); r.commit("src", "src/b.cs")
    r.git("update-ref", "refs/remotes/origin/master", "h2-good")
    r.git("checkout", "-q", "master"); r.write("local.txt", "l\n"); r.commit("a local commit", "local.txt")
    good = r.land("h2-good", "H2"); r.receipt("H2", good)
    return r, tool, good


@fixture
def landed_with_its_brief_off_its_first_parent_line(t: unittest.TestCase) -> tuple[Repo, str]:
    """(repo, merge): a reader-domain fixture. K1 (this tool) landed; H3's brief reached its branch through a merge of
    a side branch (no non-merge commit on H3's first-parent line touches a brief), and master's own first-parent line
    gained a non-merge commit touching another brief before H3 landed. Read by its parents alone, this landing has a
    brief on its first parent's side and none on its second's: the shape of a branch that merged master in. A reader
    that names the landing (the advisory, the receipt) must still read it as H3's landing."""
    r = Repo(t); r.branch("k1-tool")
    r.write("review/briefs/k1.md", brief("K1", products="tools/")); r.commit("brief", "review/briefs/k1.md")
    r.write(KS.TOOL_PATH, "# the tool\n"); r.commit("tool", KS.TOOL_PATH)
    tool = r.land("k1-tool", "K1"); r.receipt("K1", tool)
    r.branch("h3-brief")
    r.write("review/briefs/h3.md", brief("H3")); r.commit("brief", "review/briefs/h3.md")
    r.git("checkout", "-q", "master"); r.branch("h3-thing")
    r.git("merge", "-q", "--no-ff", "-m", "take the brief", "h3-brief")
    r.write("src/c.cs", "c\n"); r.commit("src", "src/c.cs")
    r.git("checkout", "-q", "master")
    r.write("review/briefs/old.md", "# Brief: old\n\n## State\n\n- a State line\n")
    r.commit("an old brief's State line, on master", "review/briefs/old.md")
    merge = r.land("h3-thing", "H3"); r.receipt("H3", merge)
    return r, merge


class K170KeyRound1Tests(unittest.TestCase):
    """K170 key round 1 (REJECT 44302df): deciding branch-vs-landing by whether a parent is in `--base` misread both
    ways: (1) a real landing whose second parent origin/master already holds and whose first parent it does not (local
    master ahead of origin) read as a branch tip, NO-BRIEF; (2) a branch that merged a master AHEAD of `--base` (a stale
    base) still read as a landing of master's side, the original PRODUCTS-UNDECLARED. Neither may depend on how fresh
    `--base` is."""

    def test_a_real_landing_whose_second_parent_the_base_holds_reads_as_a_landing(self):
        r, _tool, good = landed_beside_a_pushed_line(self)
        is_in = lambda a: subprocess.run(["git", "-C", str(r.root), "merge-base", "--is-ancestor", a,  # noqa: E731
                                          "origin/master"]).returncode == 0
        self.assertEqual((False, True), (is_in(f"{good}^1"), is_in(f"{good}^2")))
        got = KS.check(r.root, good, at="master")                       # the CLI's default base: origin/master
        self.assertEqual((True, "cloudvore/H2", "OK", r.git("rev-parse", f"{good}^1"), r.git("rev-parse", f"{good}^2")),
                         (got["landing"], got["subject"], got["status"], got["base"], got["tip"]), got)
        for base in ("master", "origin/master", good, "no-such-ref"):
            with self.subTest(base=base):
                self.assertEqual(verdict(got), verdict(KS.check(r.root, good, base=base, at="master")))
        with redirect_stdout(io.StringIO()) as out, redirect_stderr(io.StringIO()):
            code = KS.main(["--repo", str(r.root), "check", good, "--at", "master"])
        self.assertEqual(0, code, out.getvalue())
        self.assertTrue(out.getvalue().startswith(f"cloudvore/H2 OK landing={good[:9]} "), out.getvalue())

    def test_a_branch_that_merged_a_master_ahead_of_the_base_reads_its_own_verdict(self):
        r, pre, tip = merged_from_master(self)
        stale = r.git("merge-base", pre, "master")          # the master the branch started from, before H901 landed
        r.git("update-ref", "refs/remotes/origin/master", stale)
        is_in = lambda a: subprocess.run(["git", "-C", str(r.root), "merge-base", "--is-ancestor", a,  # noqa: E731
                                          "origin/master"]).returncode == 0
        self.assertEqual((False, False), (is_in(f"{tip}^1"), is_in(f"{tip}^2")))
        before = KS.check(r.root, pre)                       # the CLI's default base: origin/master, stale
        got = KS.check(r.root, tip)
        self.assertEqual(("OK", "cloudvore/H900", False), (before["status"], before["subject"], before["landing"]))
        self.assertEqual(verdict(before), verdict(got), got)
        with redirect_stdout(io.StringIO()) as out, redirect_stderr(io.StringIO()):
            code = KS.main(["--repo", str(r.root), "check", tip])
        self.assertEqual(0, code, out.getvalue())
        self.assertTrue(out.getvalue().startswith(f"cloudvore/H900 OK branch={tip[:9]} "), out.getvalue())

    def test_a_branch_that_merged_master_refuses_an_unresolvable_base_as_its_pre_merge_tip_does(self):
        """K170 key round 2, finding 2: a git failure is never a verdict (exit 2). A misspelled `--base` at a merged
        tip refused nothing and read OK (the merged line stood in for the base); the pre-merge tip refuses it. With the
        DEFAULT base absent (no origin/master in this fixture) both refuse too: the branch reading needs a base."""
        r, pre, tip = merged_from_master(self)
        self.assertEqual("", r.git("for-each-ref", "refs/remotes/"))
        for argv in (["--base", "no-such-ref"], []):
            for target in (pre, tip):
                with self.subTest(argv=argv, target="pre" if target == pre else "tip"):
                    with redirect_stdout(io.StringIO()) as out, redirect_stderr(io.StringIO()) as err:
                        code = KS.main(["--repo", str(r.root), "check", target, *argv])
                    self.assertEqual((2, ""), (code, out.getvalue()), err.getvalue())
                    self.assertTrue(err.getvalue().startswith("REFUSE kernel-subjects: git did not answer"),
                                    err.getvalue())
        with self.assertRaises(KS.GitFailed):
            KS.check(r.root, tip, base="no-such-ref")

    def test_a_merge_of_master_with_a_direct_brief_edit_on_its_line_reads_as_a_landing_recorded_limit(self):
        """Recorded, a stated limit (K170 key round 2, finding 1): master's own first-parent line carries a non-merge
        commit editing a brief, so BOTH lines of the merge into H900 touched briefs and the merge reads, as before
        K170, as a landing of master's side: H901's subject, the false alarm (loud, never a credit). 0 such master
        commits in 1822 first-parent commits (ledger)."""
        r, _pre, tip = merged_from_master(self, direct_brief=True)
        got = KS.check(r.root, tip, base="master")
        self.assertEqual((True, "cloudvore/H901", ["PRODUCTS-UNDECLARED", "RECEIPT-MISMATCH"]),
                         (got["landing"], got["subject"], got["flags"]), got)

    def test_the_advisory_reads_a_landing_with_its_brief_off_its_first_parent_line_as_that_landing(self):
        """Reader domain (weak-pin shape c): every first-parent merge on the walked ref is a landing, however its two
        sides look."""
        r, _merge = landed_with_its_brief_off_its_first_parent_line(self)
        got = KS.advisory(r.root, "master")
        self.assertEqual((2, 2, []), (got["landings"], got["checked"], got["flagged"]), got)

    def test_the_cli_reads_a_landing_with_its_brief_off_its_first_parent_line_as_a_branch_recorded_limit(self):
        """Recorded, a stated limit (ledger, Key round 1 fix): `check` with no reader naming the landing decides from
        the two sides, and this landing's sides look like master merged INTO a branch, so it reads as a branch tip
        (key round 2: read against the master it landed on, merge^1, its range holds only the merge: NO-BRIEF). The
        advisory and the receipt name it."""
        r, merge = landed_with_its_brief_off_its_first_parent_line(self)
        got = KS.check(r.root, merge, base=f"{merge}^1", at="master")
        self.assertEqual((False, "NO-BRIEF", []), (got["landing"], got["status"], got["briefs"]), got)
        named = KS.check(r.root, merge, at="master", named_landing=True)
        self.assertEqual((True, "OK", "cloudvore/H3"), (named["landing"], named["status"], named["subject"]), named)


class FixtureIsolationTests(unittest.TestCase):
    """`fixture` builds a history once and copies it per caller: a copy must never be the template or another
    test's repository, and nothing a test does may reach the next caller."""

    def test_every_call_is_its_own_repository_and_nothing_a_test_does_reaches_the_next(self):
        a, merge_a = packet(self)
        built = len(_TEMPLATES)
        b, merge_b = packet(self)
        self.assertEqual(built, len(_TEMPLATES))                             # the second call built nothing
        self.assertEqual(merge_a, merge_b)
        self.assertNotEqual(a.root, b.root)
        templates = [t.root for made in _TEMPLATES.values()
                     for t in (made if isinstance(made, tuple) else (made,)) if isinstance(t, Repo)]
        for r in (a, b):
            self.assertNotIn(r.root, templates)
        tip = b.git("rev-parse", "master")                                  # the receipt commit, after the merge
        self.assertEqual(tip, a.git("rev-parse", "master"))
        a.write("README.md", "changed in a\n")                             # a tracked file, written in place
        a.write("leak.txt", "a\n"); moved = a.commit("only in a", "README.md", "leak.txt")
        a.git("checkout", "-q", "-b", "a-only")
        self.assertEqual(tip, b.git("rev-parse", "master"))
        self.assertFalse((b.root / "leak.txt").exists())
        self.assertEqual(b"base\n", (b.root / "README.md").read_bytes())
        self.assertEqual("", b.git("branch", "--list", "a-only"))
        c, merge_c = packet(self)                                           # after a's writes: still the template
        self.assertEqual((merge_a, tip), (merge_c, c.git("rev-parse", "master")))
        self.assertFalse((c.root / "leak.txt").exists())
        self.assertEqual(b"base\n", (c.root / "README.md").read_bytes())
        self.assertEqual("", c.git("branch", "--list", "a-only"))
        self.assertNotEqual(moved, c.git("rev-parse", "master"))

    def test_head_reads_what_rev_parse_prints_on_a_branch_detached_and_with_packed_refs(self):
        r = Repo(self)
        r.write("x.txt", "x\n")
        made = r.commit("x", "x.txt")
        self.assertEqual(r.git("rev-parse", "HEAD"), made)
        r.git("checkout", "-q", "--detach", "master~1")
        self.assertEqual(r.git("rev-parse", "HEAD"), r.head())
        r.git("checkout", "-q", "master"); r.git("pack-refs", "--all")      # no loose ref left: git is asked
        self.assertFalse((r.root / ".git" / "refs" / "heads" / "master").exists())
        self.assertEqual(r.git("rev-parse", "HEAD"), r.head())
        r.write("y.txt", "y\n")
        made = r.commit("y", "y.txt")
        self.assertEqual(r.git("rev-parse", "HEAD"), made)

    def test_a_plain_repo_starts_from_one_base_commit_and_is_its_own(self):
        a, b = Repo(self), Repo(self)
        self.assertNotEqual(a.root, b.root)
        a.write("x.txt", "x\n"); a.commit("x", "x.txt")
        self.assertEqual("base", b.git("log", "-1", "--format=%s", "master"))
        self.assertEqual("1", b.git("rev-list", "--count", "master"))
        self.assertFalse((b.root / "x.txt").exists())
        self.assertEqual("1", Repo(self).git("rev-list", "--count", "master"))


class AdvisoryTests(unittest.TestCase):
    def landed_tool(self) -> tuple[Repo, str]:
        """A repository whose master took this tool in through a declared, receipted landing."""
        r = Repo(self); r.branch("k1-tool")
        r.write("review/briefs/k1.md", brief("K1", products="tools/")); r.commit("brief", "review/briefs/k1.md")
        r.write(KS.TOOL_PATH, "# the tool\n"); r.commit("tool", KS.TOOL_PATH)
        merge = r.land("k1-tool", "K1"); r.receipt("K1", merge)
        return r, merge

    def test_before_the_tool_lands_nothing_is_owed(self):
        r, _merge = packet(self)
        got = KS.advisory(r.root, "master")
        self.assertEqual((True, None, 0), (got["ok"], got["since"], got["landings"]))
        self.assertIn("not on master", got["note"])

    def test_it_reads_the_tools_own_landing_and_every_landing_after_it(self):
        r, tool_merge = self.landed_tool()
        r.branch("h2-good")
        r.write("review/briefs/h2.md", brief("H2")); r.commit("brief", "review/briefs/h2.md")
        r.write("src/b.cs", "b\n"); r.commit("src", "src/b.cs")
        good = r.land("h2-good", "H2"); r.receipt("H2", good)
        r.branch("h3-bare")
        r.write("review/briefs/h3.md", brief("H3", with_block=False)); r.commit("brief", "review/briefs/h3.md")
        r.write("src/c.cs", "c\n"); r.commit("src", "src/c.cs")
        bare = r.land("h3-bare", "H3")
        got = KS.advisory(r.root, "master")
        self.assertEqual((tool_merge, 3, 3, 0), (got["since"], got["landings"], got["checked"], got["unchecked"]))
        self.assertEqual([{"merge": bare, "name": "H3", "status": "NO-BLOCK", "flags": ["NO-BLOCK"]}], got["flagged"])

    def test_landings_before_the_tool_are_not_read(self):
        r, _ = packet(self, with_block=False)                 # an undeclared landing that predates the tool
        r.git("checkout", "-q", "master")
        r.branch("k1-tool")
        r.write("review/briefs/k1.md", brief("K1", products="tools/")); r.commit("brief", "review/briefs/k1.md")
        r.write(KS.TOOL_PATH, "# the tool\n"); r.commit("tool", KS.TOOL_PATH)
        merge = r.land("k1-tool", "K1"); r.receipt("K1", merge)
        got = KS.advisory(r.root, "master")
        self.assertEqual((1, []), (got["landings"], got["flagged"]), got)

    def test_past_the_window_landings_are_counted_not_read(self):
        r, _tool = self.landed_tool()
        for n in range(3):
            r.branch(f"h{n}-bare")
            r.write(f"src/{n}.cs", "x\n"); r.commit("src", f"src/{n}.cs")
            r.land(f"h{n}-bare", f"H{n}")
        got = KS.advisory(r.root, "master", window=2)
        self.assertEqual((4, 2, 2), (got["landings"], got["checked"], got["unchecked"]))
        self.assertEqual(["NO-BRIEF", "NO-BRIEF"], [f["status"] for f in got["flagged"]])

    def test_the_advisory_exits_0_whatever_it_finds_and_2_when_git_does_not_answer(self):
        r, _tool = self.landed_tool()
        r.branch("h3-bare"); r.write("src/c.cs", "c\n"); r.commit("src", "src/c.cs"); r.land("h3-bare", "H3")
        p = subprocess.run([sys.executable, str(TOOL), "--repo", str(r.root), "advisory", "--json"],
                           capture_output=True, text=True)
        self.assertEqual(0, p.returncode, p.stderr)
        self.assertEqual(["H3"], [f["name"] for f in json.loads(p.stdout)["flagged"]])
        p = subprocess.run([sys.executable, str(TOOL), "--repo", str(r.root), "advisory", "--ref", "nope"],
                           capture_output=True, text=True)
        self.assertEqual((2, ""), (p.returncode, p.stdout))


# ---- K137: the Cloudvore constants live in one committed config -------------------------------------------------------

CONFIG = TOOL.with_name("factory-config.json")
# Every tool that reads the config, copied beside a config the test writes (kernel-receipt loads codex-review.py).
CONFIG_READERS = ("kernel-subjects.py", "kernel-receipt.py", "codex-review.py")
# Values the two tools once hard-coded; none may appear in their code again, only in the config (K137).
CLOUDVORE_LITERALS = ("ultra-magnus-cloudvore", "cloudvore/", "claude/", "review/briefs/", "review/kernel-receipts/",
                      "master via --no-ff landing")
# Values kept in code by ruling, though a config value spells the same: the receipt's product-suite rule `tests/`
# (integrator ruling after key round 1) is not the products default `tests/` (subject.default_products).
KEPT_IN_CODE = {("kernel-receipt.py", "tests/"),
                # key round 2 (integrator closure 1): the product roots a review path may not overlap
                ("kernel-subjects.py", "src/"), ("kernel-subjects.py", "tests/")}


def config_data() -> dict:
    """The committed config, parsed from its bytes (the bar checks out CRLF: JSON reads either)."""
    return json.loads(CONFIG.read_bytes().decode("utf-8"))


def config_leaves(node, out=None) -> list:
    out = [] if out is None else out
    if isinstance(node, dict):
        for v in node.values():
            config_leaves(v, out)
    elif isinstance(node, list):
        for v in node:
            config_leaves(v, out)
    elif isinstance(node, str):
        out.append(node)
    return out


def tool_copy(test: unittest.TestCase, mutate=None, config: bool = True, raw: bytes | None = None) -> Path:
    """A tools/ directory holding copies of the config's readers and, unless `config` is False, a config: `raw` bytes
    as given, else the committed config with `mutate(data)` applied. The copy is what a project vendoring the kit
    gets: the same code, its own config."""
    d = tempfile.TemporaryDirectory()
    test.addCleanup(d.cleanup)
    tools = Path(d.name) / "tools"
    tools.mkdir()
    for name in CONFIG_READERS:
        shutil.copyfile(TOOL.with_name(name), tools / name)
    if config:
        if raw is None:
            data = config_data()
            if mutate:
                mutate(data)
            raw = json.dumps(data, indent=2).encode("utf-8")
        (tools / "factory-config.json").write_bytes(raw)
    return tools


def load_copy(tools: Path, name: str = "kernel-subjects.py"):
    spec = importlib.util.spec_from_file_location(f"k137_copy_{name.replace('-', '_')}_{id(tools)}", tools / name)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def string_constants(path: Path) -> list:
    """Every string constant in a module's code, docstrings excluded (prose may name a path; code may not)."""
    import ast
    tree = ast.parse("\n".join(path.read_bytes().decode("utf-8").splitlines()))
    docs = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)) and node.body:
            first = node.body[0]
            if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant):
                docs.add(id(first.value))
    return [n.value for n in ast.walk(tree)
            if isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in docs]


def _drop(path):
    def f(data):
        node = data
        for k in path[:-1]:
            node = node[k]
        del node[path[-1]]
    return f


def _put(path, value):
    def f(data):
        node = data
        for k in path[:-1]:
            node = node[k]
        node[path[-1]] = value
    return f


def _paths_products(products, **paths):
    def f(data):
        data["subject"]["default_products"] = products
        data["paths"].update(paths)
    return f


def _paths_bar(**bar):
    def f(data):
        data["bar"].update(bar)
    return f


def repeated_runner() -> bytes:
    """The committed config with `bar.runner` given twice, the second value another runner (review round 1, seat A)."""
    text = CONFIG.read_bytes().decode("utf-8")
    old = '"runner": "ultra-magnus-cloudvore",'
    assert text.count(old) == 1
    return text.replace(old, old + ' "runner": "evil",').encode("utf-8")


def repeated_subject() -> bytes:
    """The committed config with an empty `subject` section before the real one (review round 1, seat A)."""
    text = CONFIG.read_bytes().decode("utf-8")
    old = '"schema": 1,'
    assert text.count(old) == 1
    return text.replace(old, old + ' "subject": {},').encode("utf-8")


class FactoryConfigTests(unittest.TestCase):
    """K137 (portability step 1): tools/kernel-subjects.py and tools/kernel-receipt.py read Cloudvore's constants
    from ONE committed config, tools/factory-config.json. A missing or malformed config is refused, never defaulted."""

    def test_the_config_is_committed_and_the_tools_take_their_constants_from_it(self):
        data = config_data()
        self.assertEqual(CONFIG.resolve(), KS.CONFIG_PATH.resolve())
        self.assertEqual(data, KS.CONFIG)
        self.assertEqual(data["bar"]["runner"], KS.BAR_RUNNER)
        self.assertEqual(data["paths"]["briefs"], KS.BRIEFS)
        self.assertEqual(data["paths"]["review"], KS.REVIEW)
        self.assertEqual(data["paths"]["receipts"], KS.RECEIPTS)
        self.assertEqual(data["paths"]["subjects_tool"], KS.TOOL_PATH)
        self.assertEqual(data["subject"]["delivery"], KS.DELIVERY)
        self.assertEqual(tuple(data["subject"]["default_products"]), KS.PRODUCT_PREFIXES)

    def test_neither_tool_hard_codes_a_cloudvore_constant_in_its_code(self):
        """The config is the one writer: a value it holds, or a Cloudvore literal, back in code is a second one."""
        leaves = set(config_leaves(config_data())) - {""}
        for name in ("kernel-subjects.py", "kernel-receipt.py"):
            for value in string_constants(TOOL.with_name(name)):
                with self.subTest(tool=name, value=value[:60]):
                    if (name, value) not in KEPT_IN_CODE:
                        self.assertNotIn(value, leaves)
                    for lit in CLOUDVORE_LITERALS:
                        self.assertNotIn(lit, value)

    def test_the_ranker_and_evidence_sections_are_optional_and_absent_means_off(self):
        """Bus K154 packet 2 (coordinator ruling 2026-10-18): another project's config without `ranker` or
        `evidence` loads, and nothing is defaulted in; the tool answers exit 0 with no evidence or ranker output."""
        for drop in (["ranker"], ["evidence"], ["ranker", "evidence"]):
            with self.subTest(absent=drop):
                def strip(data, drop=drop):
                    for section in drop:
                        del data[section]
                tools = tool_copy(self, strip)
                ks = load_copy(tools)
                for section in drop:
                    self.assertNotIn(section, ks.CONFIG)
                p = subprocess.run([sys.executable, str(tools / "kernel-subjects.py"), "block", "--row", "H1",
                                    "--filter", FILTER, "--bus-sha", BUS], capture_output=True, text=True)
                self.assertEqual(0, p.returncode, p.stderr)
                for word in ("evidence-store", "starvation"):
                    self.assertNotIn(word, p.stdout)

    def test_a_changed_config_value_changes_what_the_tool_does(self):
        """The production wiring, not a helper: a copy of the tool beside a config naming another project's briefs
        directory, subject prefix, delivery and runner reads a Cloudvore packet as unbriefed, and renders its own."""
        def acme(data):
            data["paths"]["review"] = "docs/"                  # key round 2: briefs lie inside review
            data["paths"]["receipts"] = "docs/receipts/"
            data["paths"]["briefs"] = "docs/briefs/"
            data["subject"]["prefix"] = "acme/"
            data["subject"]["delivery"] = "main via squash"
            data["bar"]["runner"] = "acme-runner-1"
        ks = load_copy(tool_copy(self, acme))
        text = ks.render_block("H1", FILTER, BUS)
        self.assertIn("- subject: acme/H1\n", text)
        self.assertIn("- delivery: main via squash\n", text)
        self.assertIn("(Runner name acme-runner-1)", text)
        self.assertEqual([], ks.parse_block(text)["problems"])
        self.assertIn("subject is not well-formed: 'cloudvore/H1'", "\n".join(ks.parse_block(block("H1"))["problems"]))
        r, merge = packet(self)
        self.assertEqual("OK", KS.check(r.root, merge, at="master")["status"])         # the control
        self.assertEqual("NO-BRIEF", ks.check(r.root, merge, at="master")["status"])   # review/briefs/ is not docs/briefs/

    def test_every_constant_follows_its_config_key(self):
        """K137 mutants: each constant kernel-subjects.py takes from the config follows its key; a constant put back
        as a literal (even one built so no string in the code equals it) keeps Cloudvore's value and fails here."""
        def other(data):
            data["subject"].update(prefix="acme/", row="ACME[0-9]+", branch_prefix="feat/", delivery="main via squash",
                                   default_products=["lib/", "spec/"])
            data["paths"].update(briefs="docs/briefs/", review="docs/", receipts="docs/receipts/",
                                 subjects_tool="kit/kernel-subjects.py")
            data["bar"]["runner"] = "acme-runner-1"
            data["contract_defaults"]["seats"] = "one seat"
        ks = load_copy(tool_copy(self, other))
        self.assertEqual(("acme/", "main via squash", ("lib/", "spec/")),
                         (ks.SUBJECT_PREFIX, ks.DELIVERY, ks.PRODUCT_PREFIXES))
        self.assertEqual(("docs/briefs/", "docs/", "docs/receipts/", "kit/kernel-subjects.py", "acme-runner-1"),
                         (ks.BRIEFS, ks.REVIEW, ks.RECEIPTS, ks.TOOL_PATH, ks.BAR_RUNNER))
        self.assertTrue(ks.SUBJECT.match("acme/H1"))
        self.assertIsNone(ks.SUBJECT.match("cloudvore/H1"))
        self.assertEqual("ACME12", ks.ROW_IN_SUBJECT.search("Merge x (ACME12)").group(1))
        self.assertIsNone(ks.ROW_IN_SUBJECT.search("Merge x (K137)"))
        self.assertEqual("k9", ks.BRANCH_IN_SUBJECT.match("Merge branch 'feat/k9-x'").group(1))
        self.assertEqual("one seat", ks.DEFAULTS["seats"])
        self.assertIn("(Runner name acme-runner-1)", ks.DEFAULTS["env"])

    def test_a_missing_config_is_refused_loudly_by_both_tools(self):
        tools = tool_copy(self, config=False)
        with self.assertRaisesRegex(ValueError, "factory-config.json"):
            load_copy(tools)
        for name, args in (("kernel-subjects.py", ["advisory"]),
                           ("kernel-receipt.py", ["--merge", "x", "--barred", "y", "--ledger", "z"])):
            with self.subTest(tool=name):
                p = subprocess.run([sys.executable, str(tools / name), "--repo", str(tools), *args],
                                   capture_output=True, text=True)
                self.assertEqual((2, ""), (p.returncode, p.stdout), p.stderr)
                self.assertIn(f"REFUSE {name[:-3]}: ", p.stderr)
                self.assertIn("factory-config.json", p.stderr)
                self.assertIn("missing", p.stderr)
                self.assertNotIn("Traceback", p.stderr)

    def test_a_config_error_refuses_the_receipt_as_a_program_too(self):
        """Review round 1 (seat A): a repeated key and a pattern that fails only embedded are refused by
        kernel-receipt.py as well, `REFUSE kernel-receipt:` and exit 2, never a traceback or exit 1."""
        cases = (("a repeated key", dict(raw=repeated_runner()), "repeats the key 'runner'"),
                 ("an embedded row pattern", dict(mutate=_put(["subject", "row"], "(?i)[A-Z]+\\d+")), "subject.row"))
        for why, kw, says in cases:
            with self.subTest(why):
                tools = tool_copy(self, **kw)
                p = subprocess.run([sys.executable, str(tools / "kernel-receipt.py"), "--merge", "x", "--barred", "y",
                                    "--ledger", "z"], capture_output=True, text=True)
                self.assertEqual((2, ""), (p.returncode, p.stdout), p.stderr)
                self.assertIn("REFUSE kernel-receipt: ", p.stderr)
                self.assertIn(says, p.stderr)
                self.assertNotIn("Traceback", p.stderr)

    def test_a_malformed_config_is_refused_naming_what_is_wrong(self):
        cases = (
            ("not JSON", dict(raw=b'{"schema": '), "not valid JSON"),
            ("UTF-16", dict(raw='{}'.encode("utf-16")), "UTF-8"),
            ("a list", dict(raw=b"[]"), "not a JSON object"),
            ("no runner", dict(mutate=_drop(["bar", "runner"])), "bar.runner"),
            ("no briefs", dict(mutate=_drop(["paths", "briefs"])), "paths.briefs"),
            ("an unknown key", dict(mutate=_put(["paths", "brief"], "review/briefs/")), "paths.brief"),
            ("a number for a path", dict(mutate=_put(["paths", "receipts"], 7)), "paths.receipts"),
            ("an empty runner", dict(mutate=_put(["bar", "runner"], "")), "bar.runner"),
            ("a runner no run can carry", dict(mutate=_put(["bar", "runner"], "a/b")), "bar.runner"),
            ("a bad row pattern", dict(mutate=_put(["subject", "row"], "[A-Z")), "subject.row"),
            ("bar.tools_suite, removed (key round 1)", dict(mutate=_put(["bar", "tools_suite"], "tools/(x)")),
             "unknown key bar.tools_suite"),
            ("bar.tools_suite_prefix, removed (key round 1)", dict(mutate=_put(["bar", "tools_suite_prefix"], "tools/")),
             "unknown key bar.tools_suite_prefix"),
            ("bar.product_suite_prefix, removed (integrator ruling after key round 1)",
             dict(mutate=_put(["bar", "product_suite_prefix"], "tests/")), "unknown key bar.product_suite_prefix"),
            ("the key section, removed (key round 1)",
             dict(mutate=_put(["key"], {"codex_class": "cross-family:codex"})), "unknown key key"),
            ("products not a list", dict(mutate=_put(["subject", "default_products"], "src/")),
             "subject.default_products"),
            ("an env naming no runner", dict(mutate=_put(["contract_defaults", "env"], "anywhere")),
             "contract_defaults.env"),
            ("a contract default missing", dict(mutate=_drop(["contract_defaults", "seats"])),
             "contract_defaults.seats"),
            ("another schema", dict(mutate=_put(["schema"], "factory-config/2")), "schema"),
            # K151: the ranker's starvation window is a positive integer, never defaulted
            ("a ranker that is not an object", dict(mutate=_put(["ranker"], 4)),
             "has ranker that is not an object"),
            ("no window", dict(mutate=_drop(["ranker", "starvation_window"])), "ranker.starvation_window"),
            ("a zero window", dict(mutate=_put(["ranker", "starvation_window"], 0)), "ranker.starvation_window"),
            ("a string window", dict(mutate=_put(["ranker", "starvation_window"], "4")), "ranker.starvation_window"),
            ("a boolean window", dict(mutate=_put(["ranker", "starvation_window"], True)), "ranker.starvation_window"),
            ("a float window", dict(mutate=_put(["ranker", "starvation_window"], 4.0)), "ranker.starvation_window"),
            ("an unknown ranker key", dict(mutate=_put(["ranker", "window"], 4)), "unknown key ranker.window"),
            # K137 mutants (ledger, Mutants): each case below kills a loader break the cases above let through
            ("a boolean schema", dict(mutate=_put(["schema"], True)), "schema True"),
            ("an unknown top-level key", dict(mutate=_put(["extra"], 1)), "unknown key extra"),
            ("a section missing", dict(mutate=_drop(["paths"])), "has no paths"),
            ("about not a string", dict(mutate=_put(["about"], 7)), "has about that is not a string"),
            ("a section that is not an object", dict(mutate=_put(["bar"], [])), "has bar that is not an object"),
            ("a backslash in a path", dict(mutate=_put(["paths", "review"], "review\\")), "paths.review"),
            ("a parent step in a path", dict(mutate=_put(["paths", "review"], "../review/")), "paths.review"),
            ("products repeated", dict(mutate=_put(["subject", "default_products"], ["src/", "src/"])),
             "subject.default_products"),
            ("a value padded with a space", dict(mutate=_put(["subject", "delivery"], "main via squash "),),
             "subject.delivery"),
            ("a UTF-8 byte-order mark", dict(raw=b"\xef\xbb\xbf" + CONFIG.read_bytes()), "byte-order mark"),
            # K137 key round 2 (integrator closures 1, 2 and 4)
            ("the key's case: review over a product root",
             dict(mutate=_paths_products(["tools/"], review="src/", briefs="src/briefs/", receipts="src/receipts/")),
             "paths.review 'src/'"),
            ("a review path inside a product root",
             dict(mutate=_paths_products(["lib/"], review="tools/review/", briefs="tools/review/briefs/",
                                         receipts="tools/review/receipts/")), "paths.review 'tools/review/'"),
            ("a product overlapping the review path",
             dict(mutate=_put(["subject", "default_products"], ["src/", "review/"])), "subject.default_products"),
            ("a product inside the briefs path",
             dict(mutate=_put(["subject", "default_products"], ["src/", "review/briefs/x/"])),
             "subject.default_products"),
            ("briefs outside review", dict(mutate=_put(["paths", "briefs"], "docs/briefs/")), "paths.briefs"),
            ("briefs equal to review", dict(mutate=_put(["paths", "briefs"], "review/")), "paths.briefs"),
            ("receipts outside review", dict(mutate=_put(["paths", "receipts"], "kernel-receipts/")),
             "paths.receipts"),
            ("a hosted pattern matching everything", dict(mutate=_put(["bar", "hosted_runner"], ".*")),
             "bar.hosted_runner"),
            ("a hosted pattern reaching the self-hosted runner",
             dict(mutate=_put(["bar", "hosted_runner"], "ultra-.*")), "bar.hosted_runner"),
            ("a hosted pattern with a metacharacter in its prefix",
             dict(mutate=_put(["bar", "hosted_runner"], "GitHub.Actions [0-9]+")), "bar.hosted_runner"),
            ("a hosted pattern that matches bar.runner",
             dict(mutate=_paths_bar(runner="build 7", hosted_runner="build [0-9]+")), "bar.hosted_runner"),
            # K137 review round 1 (seat A): a repeated key, an embedded regex, paths, lists, keys that disagree
            ("a key repeated in a section", dict(raw=repeated_runner()), "repeats the key 'runner'"),
            ("a section repeated at top level", dict(raw=repeated_subject()), "repeats the key 'subject'"),
            ("a row pattern with flags it cannot carry embedded", dict(mutate=_put(["subject", "row"], "(?i)[A-Z]+\\d+")),
             "subject.row"),
            ("a drive letter", dict(mutate=_put(["paths", "review"], "C:/x/")), "paths.review"),
            ("a ./ prefix", dict(mutate=_put(["paths", "review"], "./review/")), "paths.review"),
            ("a directory without its slash", dict(mutate=_put(["paths", "briefs"], "review/briefs")), "paths.briefs"),
            ("a file path ending in a slash", dict(mutate=_put(["paths", "subjects_tool"], "tools/")),
             "paths.subjects_tool"),
            ("a product padded", dict(mutate=_put(["subject", "default_products"], [" src/", "tests/"])),
             "subject.default_products"),
            ("a product outside the repository", dict(mutate=_put(["subject", "default_products"], ["src/", "../x/"])),
             "subject.default_products"),
            ("a tools workflow without the suffix", dict(mutate=_put(["bar", "tools_workflow"], "tools-ci")),
             "bar.tools_workflow"),
            ("a product workflow without the suffix", dict(mutate=_put(["bar", "product_workflow"], "product-ci")),
             "bar.product_workflow"),
            ("one workflow for both bars", dict(mutate=_put(["bar", "product_workflow"], "tools-bar")),
             "bar.product_workflow"),
            ("a subject prefix not ASCII", dict(mutate=_put(["subject", "prefix"], "cl\u00f6udvore/")), "subject.prefix"),
            # K179: the evidence store's branch and worktree are NAMES, checked as names
            ("an evidence section that is not an object", dict(mutate=_put(["evidence"], "evidence-store")),
             "has evidence that is not an object"),
            ("an evidence branch with a slash", dict(mutate=_put(["evidence", "branch"], "claude/evidence")),
             "evidence.branch"),
            ("an evidence branch that is the delivery branch", dict(mutate=_put(["evidence", "branch"], "master")),
             "evidence.branch"),
            ("an evidence worktree that is a path", dict(mutate=_put(["evidence", "worktree"], "../store")),
             "evidence.worktree"),
            ("an evidence worktree with a separator", dict(mutate=_put(["evidence", "worktree"], "a/b")),
             "evidence.worktree"),
            ("an evidence key the store does not read", dict(mutate=_put(["evidence", "limit_bytes"], "16384")),
             "unknown key evidence.limit_bytes"),
        )
        for why, kw, says in cases:
            with self.subTest(why):
                tools = tool_copy(self, **kw)
                with self.assertRaisesRegex(ValueError, re.escape(says)):
                    load_copy(tools)
                p = subprocess.run([sys.executable, str(tools / "kernel-subjects.py"), "advisory"],
                                   capture_output=True, text=True)
                self.assertEqual((2, ""), (p.returncode, p.stdout), p.stderr)
                self.assertIn("REFUSE kernel-subjects: ", p.stderr)
                self.assertIn(says, p.stderr)


if __name__ == "__main__":
    unittest.main()
