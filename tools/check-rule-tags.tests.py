#!/usr/bin/env python3
"""Tests for tools/check-rule-tags.py. Run: python tools/check-rule-tags.tests.py

Every case drives main() (the CLI entry point) over a disposable project, so the exit status a caller
gates on is what is asserted."""
import contextlib
import datetime
import importlib.util
import io
import json
import os
import pathlib
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("check_rule_tags", HERE / "check-rule-tags.py")
crt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(crt)

DOC = """# Project

## Non-negotiables

- **Gate one.** Refused by the check. [enforced: tools/gate.py]
- **Two lines.** First line
  continues here. [prose]
- **Both checks.** [enforced: tools/gate.py] [enforced: tools/other.py]

## Next section

- Not a rule of the census section.
"""


class Census(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="rule-tags-")
        self.root = os.path.join(self.tmp, "proj")
        os.makedirs(os.path.join(self.root, "tools"))
        for p in ("tools/gate.py", "tools/other.py"):
            open(os.path.join(self.root, p), "w").close()
        self.write(DOC)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def write(self, text, crlf=False):
        with open(os.path.join(self.root, "RULES.md"), "w", encoding="utf-8", newline="\r\n" if crlf else "\n") as fh:
            fh.write(text)
        cfg = {"schema": crt.SCHEMA, "projects": [{"name": "p", "root": self.root, "files": [
            {"path": "RULES.md", "section": "## Non-negotiables", "bullet": "^- "}]}]}
        self.cfg = os.path.join(self.tmp, "cfg.json")
        with open(self.cfg, "w", encoding="utf-8") as fh:
            json.dump(cfg, fh)

    def run_cli(self, *extra):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = crt.main(["--config", self.cfg, *extra])
        return rc, out.getvalue(), err.getvalue()

    def counts(self):
        rc, out, _ = self.run_cli("--json", "--report")
        self.assertEqual(rc, 0)
        return json.loads(out.splitlines()[0])["counts"]

    def test_all_tagged_passes_and_counts(self):
        rc, out, _ = self.run_cli()
        self.assertEqual(rc, 0, out)
        self.assertIn("rule-tags p: 3 rules, 2 backed, 1 prose, 0 untagged, 0 dangling, 0 mixed", out)

    def test_section_bounds_and_continuation_lines(self):
        c = self.counts()
        self.assertEqual(c["bullets"], 3)          # the next section's bullet is not counted
        self.assertEqual(c["prose"], 1)            # the tag on a continuation line belongs to its bullet

    def test_untagged_refuses_and_report_measures(self):
        self.write(DOC.replace(" [prose]", ""))
        rc, out, _ = self.run_cli()
        self.assertEqual(rc, 1)
        self.assertIn("UNTAGGED p RULES.md:6", out)
        rc, out, _ = self.run_cli("--report")
        self.assertEqual(rc, 0)
        self.assertIn("1 untagged", out)

    def test_dangling_path_refuses(self):
        self.write(DOC.replace("tools/other.py", "tools/gone.py"))
        rc, out, _ = self.run_cli()
        self.assertEqual(rc, 1)
        self.assertIn("DANGLING", out)
        self.assertIn("tools/gone.py", out)

    def test_mixed_tags_refuse(self):
        self.write(DOC.replace("[enforced: tools/gate.py]", "[enforced: tools/gate.py] [prose]", 1))
        rc, out, _ = self.run_cli()
        self.assertEqual(rc, 1)
        self.assertIn("MIXED", out)

    def test_crlf_file_reads_the_same(self):
        self.write(DOC, crlf=True)
        self.assertEqual(self.counts()["backed"], 2)

    def test_missing_section_or_root_is_exit_2_never_zero(self):
        self.write(DOC.replace("## Non-negotiables", "## Renamed"))
        self.assertEqual(self.run_cli()[0], 2)
        self.assertEqual(self.run_cli("--report")[0], 2)
        self.write(DOC)
        self.assertEqual(self.run_cli("--project", "p", "--root", os.path.join(self.tmp, "nope"))[0], 2)

    def test_root_override(self):
        other = os.path.join(self.tmp, "copy")
        shutil.copytree(self.root, other)
        os.remove(os.path.join(other, "tools", "gate.py"))
        rc, out, _ = self.run_cli("--project", "p", "--root", other)
        self.assertEqual(rc, 1)
        self.assertIn("DANGLING", out)

    def test_tag_inside_code_span_is_not_a_tag(self):
        # A rule that only MENTIONS the tag syntax in a code span carries no tag of its own.
        self.write(DOC.replace(" [prose]", " Write `[prose]` or `[enforced: tools/gate.py]` on each rule."))
        rc, out, _ = self.run_cli()
        self.assertEqual(rc, 1, out)
        self.assertIn("UNTAGGED p RULES.md:6", out)
        self.write(DOC.replace("[prose]", "``[prose]`` [prose]"))      # a real tag beside a quoted one still counts
        self.assertEqual(self.counts()["prose"], 1)

    def test_path_escaping_the_root_is_dangling(self):
        open(os.path.join(self.tmp, "outside.py"), "w").close()
        for cited in ("../outside.py", os.path.join(self.tmp, "outside.py"), "tools/../../outside.py"):
            self.write(DOC.replace("tools/other.py", cited))
            rc, out, _ = self.run_cli()
            self.assertEqual(rc, 1, (cited, out))
            self.assertIn("DANGLING", out)

    def test_directory_is_not_a_check(self):
        for cited in ("tools", "tools/", "."):
            self.write(DOC.replace("tools/other.py", cited))
            rc, out, _ = self.run_cli()
            self.assertEqual(rc, 1, (cited, out))
            self.assertIn("DANGLING", out)


# ---------------------------------------------------------------------------------------------------
# v2: sidecar map, judgement/record kinds, fences, command-position invocation proof, location-keyed anchors
# and fan-in, distinct ids, fail-closed requirement, git-hook placement, rising floor with checked-only backing,
# emit-map. Rounds 2 and 3 added the negatives for each reviewer finding (comment-only mention, namesake file,
# own unit test, unwired hook, fan-in by overlapping anchors, echo/heredoc/exit mentions, unchecked floor backing).

MAPDOC = """# Project

## Rules

- **Alpha.** Refused by the gate.
- **Beta.** A reviewer
  decides this one.
- **Gamma.** History as written.
- **Delta.** Plain prose rule.
"""
ALPHA = "**Alpha.** Refused by the gate."
BETA = "**Beta.** A reviewer decides this one."
GAMMA = "**Gamma.** History as written."
DELTA = "**Delta.** Plain prose rule."
HOOK = [".githooks/*"]
ANC = "ANCHOR_MAIN"


def hashlib_id(text):
    import hashlib
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def enf(path, anchor=ANC):
    return {"kind": "enforced", "enforcer": path, "anchor": anchor}


class V2(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="rule-tags2-")
        self.addCleanup(shutil.rmtree, self.tmp, True)
        # git must not see the developer's own configuration or a hook caller's GIT_* variables
        envp = mock.patch.dict(os.environ, {"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"})
        envp.start()
        self.addCleanup(envp.stop)
        for k in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_PREFIX", "GIT_COMMON_DIR",
                  "GIT_CONFIG_COUNT", "GIT_CONFIG_KEY_0", "GIT_CONFIG_VALUE_0"):
            os.environ.pop(k, None)
        self.root = os.path.join(self.tmp, "proj")
        for d in ("tools", ".githooks", ".github/workflows", "factory", "legacy"):
            os.makedirs(os.path.join(self.root, d))
        os.makedirs(os.path.join(self.tmp, "outside"))
        for p in ("tools/gate.py", "tools/orphan.py", "legacy/gate.py", "tools/pre-commit.py"):
            self.put(p, ANC + " = 1\n")
        self.put("../outside/gate.py", ANC + " = 1\n")
        self.proj = {"name": "p", "root": self.root, "rule_map": "factory/rule-map.json",
                     "files": [{"path": "RULES.md", "section": "## Rules", "bullet": "^- "}]}
        self.doc(MAPDOC)

    def put(self, rel, text):
        full = os.path.normpath(os.path.join(self.root, rel))
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)

    def doc(self, text):
        self.put("RULES.md", text)

    def cfg(self, **over):
        proj = {k: v for k, v in dict(self.proj, **over).items() if v is not None}
        self.cfgpath = os.path.join(self.tmp, "cfg.json")
        with open(self.cfgpath, "w", encoding="utf-8") as fh:
            json.dump({"schema": crt.SCHEMA, "projects": [proj]}, fh)

    def mapfile(self, rules):
        self.put("factory/rule-map.json", json.dumps({"schema": "rule-map.v1", "rules": rules}))

    def rid(self, text):
        return crt.rule_id(text)

    def run_cli(self, *extra, **over):
        self.cfg(**over)
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = crt.main(["--config", self.cfgpath, *extra])
        return rc, out.getvalue(), err.getvalue()

    def census_json(self, *extra, **over):
        rc, out, err = self.run_cli("--json", "--report", *extra, **over)
        self.assertEqual(rc, 0, err)
        return json.loads(out.splitlines()[0])

    def counts(self, *extra, **over):
        return self.census_json(*extra, **over)["counts"]

    def git(self, *args):
        subprocess.run(["git", "-C", self.root, *args], check=True, capture_output=True)

    def map_alpha(self, enforcer="tools/gate.py", anchor=ANC):
        self.mapfile({self.rid(ALPHA): enf(enforcer, anchor)})

    # ---- id
    def test_id_is_stable_under_rewrap_and_marker_style(self):
        a = crt.rule_id("- **Beta.** A reviewer\n  decides this one.")
        self.assertEqual(a, crt.rule_id("* **Beta.**   A reviewer decides this one.  "))
        self.assertEqual(a, hashlib_id(BETA))
        self.assertEqual(len(a), 12)
        self.assertNotEqual(a, crt.rule_id("- **Beta.** A reviewer decides this one!"))
        self.assertEqual(crt.rule_id("3. numbered rule"), crt.rule_id("- numbered rule"))

    # ---- sidecar map
    def test_map_classifies_without_editing_prose(self):
        self.mapfile({self.rid(ALPHA): {"kind": "enforced", "enforcer": "tools/gate.py"},
                      self.rid(BETA): {"kind": "judgement"}, self.rid(GAMMA): {"kind": "record"},
                      self.rid(DELTA): {"kind": "prose"}})
        j = self.census_json()                       # no invocation_surfaces: the legacy, unchecked regime
        c = j["counts"]
        self.assertEqual((c["bullets"], c["backed"], c["judgement"], c["record"], c["prose"], c["untagged"]), (4, 1, 1, 1, 1, 0))
        self.assertEqual(j["coverage"], {"backed": 1, "denominator": 2, "pct": 50.0})

    def test_inline_tag_wins_over_the_map(self):
        self.doc(MAPDOC.replace("Plain prose rule.", "Plain prose rule. [prose]"))
        self.mapfile({self.rid(DELTA + " [prose]"): {"kind": "record"}})
        c = self.counts()
        self.assertEqual((c["prose"], c["record"]), (1, 0))

    def test_stale_entry_counted_printed_and_fatal_only_when_strict(self):
        self.mapfile({self.rid(DELTA): {"kind": "prose"},
                      "deadbeef0000": {"kind": "prose", "source": "RULES.md", "line_hint": 9, "text_head": "reworded rule"}})
        self.assertEqual(self.counts()["stale"], 1)
        rc, out, _ = self.run_cli("--report")
        self.assertIn("STALE p map deadbeef0000 RULES.md:9 reworded rule", out)
        self.assertEqual(self.run_cli("--check")[0], 0)
        self.assertEqual(self.run_cli("--check", "--strict-map")[0], 1)

    def test_reworded_rule_goes_stale_and_untagged(self):
        self.mapfile({self.rid(DELTA): {"kind": "prose"}})
        self.assertEqual(self.counts()["stale"], 0)
        self.doc(MAPDOC.replace("Plain prose rule.", "Plain prose rule, reworded."))
        c = self.counts()
        self.assertEqual((c["stale"], c["prose"]), (1, 0))

    def test_missing_or_malformed_map_is_exit_2_never_zero(self):
        self.assertEqual(self.run_cli("--report")[0], 2)          # rule_map configured, file absent
        self.put("factory/rule-map.json", "{not json")
        self.assertEqual(self.run_cli("--report")[0], 2)
        self.mapfile({"abc": {"kind": "enforced"}})                # enforced without an enforcer
        self.assertEqual(self.run_cli("--report")[0], 2)
        self.mapfile({"abc": {"kind": "bogus"}})
        self.assertEqual(self.run_cli("--report")[0], 2)
        self.put("factory/rule-map.json", json.dumps({"schema": "rule-map.v9", "rules": {}}))
        self.assertEqual(self.run_cli("--report")[0], 2)

    def test_enforcer_missing_or_escaping_is_dangling_in_the_map(self):
        for bad in ("tools/gone.py", "../outside.py", "tools"):
            self.mapfile({self.rid(ALPHA): {"kind": "enforced", "enforcer": bad}})
            self.assertEqual(self.counts()["dangling"], 1, bad)

    def test_rule_map_cli_override(self):
        other = os.path.join(self.tmp, "other-map.json")
        with open(other, "w", encoding="utf-8") as fh:
            json.dump({"schema": "rule-map.v1", "rules": {self.rid(DELTA): {"kind": "prose"}}}, fh)
        self.assertEqual(self.counts("--rule-map", other)["prose"], 1)

    # ---- judgement / record / denominator / gaming guard
    def test_inline_judgement_and_record_are_excluded_from_the_denominator(self):
        self.doc("## Rules\n- a [enforced: tools/gate.py]\n- b [judgement]\n- c [record]\n- d [prose]\n- e [prose]\n")
        j = self.census_json(rule_map=None)
        c = j["counts"]
        self.assertEqual((c["bullets"], c["backed"], c["judgement"], c["record"], c["prose"]), (5, 1, 1, 1, 2))
        self.assertEqual(j["coverage"], {"backed": 1, "denominator": 3, "pct": 33.3})
        rc, out, _ = self.run_cli("--report", rule_map=None)
        self.assertIn("coverage 1/3 = 33.3% (enforced 1, judgement 1, record 1, prose 2;", out)

    def test_two_kinds_on_one_rule_is_mixed(self):
        self.doc("## Rules\n- a [judgement] [record]\n- b [prose] [judgement]\n")
        self.assertEqual(self.counts(rule_map=None)["mixed"], 2)

    def test_reclassifying_over_half_warns_and_half_does_not(self):
        self.doc("## Rules\n- a [judgement]\n- b [record]\n- c [judgement]\n- d [prose]\n")
        rc, out, _ = self.run_cli("--report", rule_map=None)
        self.assertIn("WARNING p: judgement+record = 3 of 4 rules (over 50%)", out)
        self.doc("## Rules\n- a [judgement]\n- b [record]\n- c [prose]\n- d [prose]\n")      # exactly 50%: silent
        rc, out, _ = self.run_cli("--report", rule_map=None)
        self.assertNotIn("WARNING", out)

    # ---- fences
    def test_heading_inside_a_fence_does_not_cut_the_section(self):
        self.doc("## Rules\n- before\n\n```\n# NEVER a heading\n## Rules2\n```\n\n- after the fence\n\n## Next\n- outside\n")
        self.assertEqual(self.counts(rule_map=None)["bullets"], 2)

    def test_bullet_inside_a_fence_is_not_a_rule_and_tilde_fences_work(self):
        self.doc("## Rules\n- real\n```\n- fake in backticks\n```\n~~~sh\n- fake in tildes\n~~~\n- real two\n")
        self.assertEqual(self.counts(rule_map=None)["bullets"], 2)

    def test_a_fence_ends_a_bullet_and_a_shorter_fence_does_not_close_a_longer(self):
        self.doc("## Rules\n- a rule\n```\ncode line\n```\n- two\n````\n```\n- still fenced\n```\n````\n- three\n")
        j = self.census_json(rule_map=None)
        self.assertEqual(j["counts"]["bullets"], 3)
        self.assertNotIn("code line", json.dumps(j))

    def test_a_fence_never_closed_is_not_a_fence_and_the_rules_after_it_count(self):
        self.doc("## Rules\n- one\n```\n- swallowed\n")
        rc, out, _ = self.run_cli("--report", rule_map=None)
        self.assertIn("never closed", out)
        self.assertIn("2 rules", out)                     # one and the "swallowed" rule: counted, not hidden
        self.assertIn("treated as NOT a fence", out)

    def test_a_fence_inside_a_list_item_that_ends_first_does_not_hide_the_next_top_level_rule(self):
        # Codex round-2 repro: an unclosed fence in a list item must not swallow the rule after the list item
        self.doc("## Rules\n- keep [prose]\n\n  ```text\n  sample\n\n- untagged outside list\n")
        j = self.census_json(rule_map=None)
        self.assertEqual((j["counts"]["bullets"], j["counts"]["untagged"]), (2, 1))
        self.assertTrue(any("never closed" in w for w in j["warnings"]))
        rc, out, _ = self.run_cli(rule_map=None)
        self.assertEqual(rc, 1, out)                       # the lost rule is now visible and fatal
        self.assertIn("UNTAGGED p RULES.md:7", out)

    def test_a_later_fence_cannot_close_a_fence_whose_list_item_already_ended(self):
        # the dedent ends the container: a LATER, unrelated fence pair must not pair up with the stale opener and
        # hide the top-level rule in between
        self.doc("## Rules" + chr(10) + "- keep [prose]" + chr(10) + chr(10) + "  ```text" + chr(10) + "  sample" + chr(10) + chr(10)
                 + "- untagged outside list" + chr(10) + chr(10) + "```" + chr(10) + "code" + chr(10) + "```" + chr(10))
        j = self.census_json(rule_map=None)
        self.assertEqual((j["counts"]["bullets"], j["counts"]["untagged"]), (2, 1))

    def test_a_closed_fence_inside_a_list_item_still_masks_its_contents(self):
        self.doc("## Rules\n- keep [prose]\n\n  ```text\n  - fake\n  ## Not a heading\n  ```\n- two [prose]\n")
        c = self.counts(rule_map=None)
        self.assertEqual((c["bullets"], c["prose"]), (2, 2))

    def test_closing_fence_with_trailing_text_does_not_close(self):
        self.doc("## Rules\n- one\n```\n- x\n``` not a closer\n- y\n```\n- two\n- three\n")
        self.assertEqual(self.counts(rule_map=None)["bullets"], 3)          # one, two, three: y stayed fenced

    def test_backtick_in_a_backtick_fence_info_string_is_not_an_opener_but_is_for_tildes(self):
        self.doc("## Rules\n- one\n```not a fence```\n- two\n")
        self.assertEqual(self.counts(rule_map=None)["bullets"], 2)          # no fence opened: nothing masked
        self.doc("## Rules\n- one\n~~~ a`b\n- hidden\n~~~\n- two\n")
        self.assertEqual(self.counts(rule_map=None)["bullets"], 2)          # a tilde fence may carry a backtick

    def test_fence_indented_four_spaces_is_code_not_a_fence(self):
        self.doc("## Rules\n- keep [prose]\n\n    ```\n\n- lost untagged rule\n")
        j = self.census_json(rule_map=None)
        self.assertEqual((j["counts"]["bullets"], j["counts"]["untagged"]), (2, 1))
        self.doc("## Rules\n- keep [prose]\n\n   ```\n   code\n   ```\n- two [prose]\n")      # 3 spaces still opens
        self.assertEqual(self.counts(rule_map=None)["bullets"], 2)
        self.doc("## Rules\n- a [prose]\n```\n- x\n    ```\n- y\n```\n- z [prose]\n")        # 4 spaces cannot close
        self.assertEqual(self.counts(rule_map=None)["bullets"], 2)

    # ---- comments (round 3): block comments and docstrings anywhere
    def test_code_lines_strip_block_comments_and_docstrings_anywhere(self):
        def code(text):
            return [l.strip() for _n, l in crt.code_lines(text)]
        self.assertEqual(code("const x = 1; /* tools/gate.py */"), ["const x = 1;"])
        self.assertEqual(code("const x = 1; /*\n tools/gate.py\n*/ y"), ["const x = 1;", "y"])
        self.assertEqual(code("a <# b #> c"), ["a   c"])
        self.assertEqual(code("x = 1  <!-- c --> y"), ["x = 1    y"])
        self.assertEqual(code('def f():\n    """tools/gate.py"""\n    return 1'), ["def f():", "return 1"])
        self.assertEqual(code("x = '''\ntools/gate.py\n''' + y"), ["x =", "+ y"])
        self.assertEqual(code("rm -rf tmp/*\nls tools/**"), ["rm -rf tmp/*", "ls tools/**"])    # a glob is not a comment
        self.assertEqual(code("http://x/y # note"), ["http://x/y"])
        self.assertEqual(code("REM c\n:: c\nrem\nreal"), ["real"])
        self.assertEqual(code("ok $# ${#a}"), ["ok $# ${#a}"])

    # ---- invocation: a command in executable position, not a mention
    def invoked(self, enforcer="tools/gate.py", surfaces=HOOK, **over):
        self.map_alpha(enforcer)
        return self.counts(invocation_surfaces=surfaces, **over)

    def backed_by(self, rel, text, enforcer="tools/gate.py", **over):
        """1 if a surface file `rel` holding `text` invokes the enforcer, else 0."""
        self.put(rel, text)
        return self.invoked(enforcer, surfaces=[rel], **over)["backed"]

    def test_existing_but_never_invoked_enforcer_is_not_backed(self):
        self.put(".githooks/pre-commit", "python tools/gate.py\n")        # invokes gate.py, not orphan.py
        c = self.invoked("tools/orphan.py")
        self.assertEqual((c["backed"], c["uninvoked"]), (0, 1))
        rc, out, _ = self.run_cli(invocation_surfaces=HOOK)
        self.assertEqual(rc, 1)
        self.assertIn("ENFORCED-UNINVOKED p RULES.md:", out)
        self.assertIn("coverage 0/4", out)

    def test_command_forms_that_invoke(self):
        for i, text in enumerate((
                "python tools/gate.py\n", "python3 ./tools/gate.py --flag\n", "py -3 tools/gate.py\n",
                "exec python tools/gate.py\n", "FOO=1 BAR=2 python tools/gate.py\n", "if python tools/gate.py; then\n  :\nfi\n",
                "set -e\ntools/gate.py\n", "bash tools/gate.py\n", ". tools/gate.py\n", "source tools/gate.py\n",
                "echo start && python tools/gate.py\n", "false || python tools/gate.py\n", "x=$(python tools/gate.py)\n",
                "node --check tools/gate.py\n", "pwsh -NoProfile -File tools/gate.py -Run\n", "python tools/gate.py 2>&1 | tee log\n",
                'python "tools/gate.py"\n', "python 'tools/gate.py'\n", "cd . && python tools/gate.py > out.txt\n",
                "  python tools/gate.py\n", "python tools/gate.py \\\n   --more\n", "python \\\n   tools/gate.py\n")):
            self.assertEqual(self.backed_by(f".githooks/c{i}.sh", text), 1, text)

    def test_mentions_and_non_command_positions_do_not_invoke(self):
        for i, text in enumerate((
                "echo python tools/gate.py\n", "echo tools/gate.py\n", "printf '%s\\n' tools/gate.py\n", "X=tools/gate.py\n",
                "export X=tools/gate.py\n", "Y=tools/gate.py echo hi\n", "python tools/other.py tools/gate.py\n",
                "python -m pytest tools/gate.py\n", "dotnet test tools/gate.py\n", "cat tools/gate.py\n", "grep x tools/gate.py\n",
                "ls tools/gate.py\n", "[ -f tools/gate.py ] && echo ok\n", "test -x tools/gate.py\n", "echo hi > tools/gate.py.log\n",
                "see also tools/gate.py\n", "# python tools/gate.py\n", "python tools/gate.pyc\n", "python xgate.py\n",
                "python tools/gate.py.disabled\n")):
            self.put("tools/gate.py.disabled", ANC + "\n")
            self.assertEqual(self.backed_by(f".githooks/m{i}.sh", text), 0, text)
        self.put(".githooks/ps.ps1", "Write-Host tools/gate.py\nWrite-Output 'python tools/gate.py'\n")
        self.assertEqual(self.invoked(surfaces=[".githooks/ps.ps1"])["backed"], 0)
        self.put(".githooks/ps.ps1", "Write-Host hi\n& tools/gate.py\n")
        self.assertEqual(self.invoked(surfaces=[".githooks/ps.ps1"])["backed"], 1)

    def test_heredoc_bodies_never_count(self):
        for i, text in enumerate(("cat <<EOF\npython tools/gate.py\nEOF\n", ": <<'EOF'\npython tools/gate.py\nEOF\n",
                                  "cat <<-DOC\n\tpython tools/gate.py\n\tDOC\n", ": <<\"X\"\ntools/gate.py\nX\n")):
            self.assertEqual(self.backed_by(f".githooks/h{i}.sh", text), 0, text)
        self.assertEqual(self.backed_by(".githooks/h9.sh", "cat <<EOF\ntext\nEOF\npython tools/gate.py\n"), 1)     # after the body
        self.assertEqual(self.backed_by(".githooks/h8.sh", "# cat <<EOF\npython tools/gate.py\n"), 1)            # a comment opens none
        self.assertEqual(self.backed_by(".githooks/h7.sh", "cat <<< word\npython tools/gate.py\n"), 1)            # here-string, no body

    def test_nothing_after_an_unconditional_top_level_exit_counts(self):
        self.assertEqual(self.backed_by(".githooks/e1.sh", "exit 0\npython tools/gate.py\n"), 0)
        self.assertEqual(self.backed_by(".githooks/e2.sh", "echo x\nexit\npython tools/gate.py\n"), 0)
        self.assertEqual(self.backed_by(".githooks/e3.sh", "python tools/gate.py\nexit 0\n"), 1)              # before the exit
        self.assertEqual(self.backed_by(".githooks/e4.sh", 'if [ -n "$X" ]; then\n  exit 0\nfi\npython tools/gate.py\n'), 1)
        self.assertEqual(self.backed_by(".githooks/e5.sh", '[ -z "$X" ] && exit 0\npython tools/gate.py\n'), 1)
        self.assertEqual(self.backed_by(".githooks/e6.sh", "f() {\n  exit 1\n}\npython tools/gate.py\n"), 1)
        self.assertEqual(self.backed_by(".githooks/e7.sh", "for a in 1; do\n  exit 1\ndone\npython tools/gate.py\n"), 1)

    def test_only_script_surfaces_are_read_and_yaml_only_through_run(self):
        self.assertEqual(self.backed_by(".githooks/README.md", "python tools/gate.py\n"), 0)
        self.assertEqual(self.backed_by(".githooks/notes.txt", "python tools/gate.py\n"), 0)
        self.assertEqual(self.backed_by(".githooks/x.py", "python tools/gate.py\n"), 0)
        self.assertEqual(self.backed_by(".githooks/x.cs", 'Run("python tools/gate.py");\n'), 0)
        self.assertEqual(self.backed_by(".githooks/w.yml", "steps:\n  - name: python tools/gate.py\n    uses: x\n"), 0)
        self.assertEqual(self.backed_by(".githooks/w.yml", "steps:\n  - env:\n      X: python tools/gate.py\n"), 0)
        self.assertEqual(self.backed_by(".githooks/w.yml", "steps:\n  - run: echo hi # python tools/gate.py\n"), 0)
        self.assertEqual(self.backed_by(".githooks/w.yml", "steps:\n  - run: python tools/gate.py\n"), 1)
        self.assertEqual(self.backed_by(".githooks/w.yml", "steps:\n  - run: |\n      echo hi\n      python tools/gate.py\n"), 1)
        self.assertEqual(self.backed_by(".githooks/w.yml", "steps:\n  - run: |\n      echo python tools/gate.py\n"), 0)
        self.assertEqual(self.backed_by(".githooks/w.yml", "jobs:\n  a:\n    steps:\n      - name: x\n        run: >\n          python tools/gate.py\n"), 1)
        self.assertEqual(self.backed_by(".githooks/w.yml", "steps:\n  - run: |\n      echo hi\n  - name: python tools/gate.py\n"), 0)

    def test_namesake_in_another_directory_does_not_back_the_enforcer(self):
        self.assertEqual(self.backed_by(".githooks/n1.sh", "python legacy/gate.py\n"), 0)         # legacy/gate.py exists
        self.assertEqual(self.backed_by(".githooks/n2.sh", "cd tools && python gate.py\n"), 0)   # resolves beside the hook
        self.assertEqual(self.backed_by(".githooks/n3.sh", "python ../outside/gate.py\n"), 0)

    def test_paths_relative_to_the_surface_and_to_the_root_resolve(self):
        self.assertEqual(self.backed_by("tools/run.sh", "python gate.py\n"), 1)                  # beside the surface
        self.assertEqual(self.backed_by(".githooks/p1.sh", "python ../tools/gate.py\n"), 1)
        self.assertEqual(self.backed_by(".githooks/p2.sh", "python tools\\gate.py\n"), 1)         # backslashes
        absolute = self.root.replace("\\", "/") + "/tools/gate.py"
        self.assertEqual(self.backed_by(".githooks/p3.sh", f"python {absolute}\n"), 1)           # absolute, inside the repo
        outside = os.path.join(self.tmp, "outside", "gate.py").replace("\\", "/")
        self.assertEqual(self.backed_by(".githooks/p4.sh", f"python {outside}\n"), 0)            # absolute, outside the repo
        self.assertEqual(self.backed_by(".githooks/p5.sh", "python /tools/gate.py\n"), 0)        # not repo-relative: absolute

    def test_variable_prefixes_resolve_only_from_the_allowlist(self):
        for i, text in enumerate(('python "$ROOT/tools/gate.py"', 'python "${ROOT}/tools/gate.py"',
                                  'python "$(git rev-parse --show-toplevel)/tools/gate.py"',
                                  'python "$GITHUB_WORKSPACE/tools/gate.py"', 'python "${{ github.workspace }}/tools/gate.py"')):
            self.assertEqual(self.backed_by(f".githooks/v{i}.sh", text + "\n"), 1, text)
        self.assertEqual(self.backed_by("tools/run2.sh", 'python "$PSScriptRoot/../tools/gate.py"\n'), 1)     # surface dir's parent
        for i, text in enumerate(('python "$UNSET/tools/gate.py"', 'python $HOME/tools/gate.py', 'python "$(dirname "$0")/../tools/gate.py"',
                                  'python "%ROOT%\\tools\\gate.py"', 'python "${OTHER}/tools/gate.py"', "python ~/tools/gate.py")):
            self.assertEqual(self.backed_by(f".githooks/u{i}.sh", text + "\n"), 0, text)
        # root_vars narrows or widens the allowlist
        self.put(".githooks/r.sh", 'python "$REPO/tools/gate.py"\n')
        self.assertEqual(self.invoked(surfaces=[".githooks/r.sh"])["backed"], 0)
        self.assertEqual(self.invoked(surfaces=[".githooks/r.sh"], root_vars=["$REPO"])["backed"], 1)
        self.put(".githooks/r.sh", 'python "$ROOT/tools/gate.py"\n')
        self.assertEqual(self.invoked(surfaces=[".githooks/r.sh"], root_vars=["$REPO"])["backed"], 0)

    def test_a_comment_only_mention_is_not_an_invocation(self):
        cases = {".githooks/a.sh": ("# TODO call tools/gate.py\n", "python tools/gate.py # run it\n"),
                 ".githooks/b.sh": ("   #!/bin/sh tools/gate.py\n", "python tools/gate.py\n"),
                 ".githooks/c.cmd": ("REM python tools/gate.py\n", "call tools/gate.py\n"),
                 ".githooks/d.cmd": (":: python tools/gate.py\n", "python tools/gate.py\n"),
                 ".githooks/e.yml": ("steps:\n  - run: echo hi # tools/gate.py\n", "steps:\n  - run: python tools/gate.py\n"),
                 ".githooks/f.ps1": ("<#\npython tools/gate.py\n#>\n", "<#\nnote\n#>\npython tools/gate.py\n"),
                 ".githooks/g.sh": ("echo ok; /* python tools/gate.py */\n", "echo ok; /* c */ python tools/gate.py\n"),
                 ".githooks/h.sh": ("echo ok; /*\npython tools/gate.py\n*/\n", "echo ok; /*\nc\n*/ python tools/gate.py\n"),
                 ".githooks/i.sh": ('x=1 """\npython tools/gate.py\n"""\n', '"""\ndoc\n"""\npython tools/gate.py\n'),
                 ".githooks/j.sh": ("true <# python tools/gate.py #>\n", "true <# c #> ; python tools/gate.py\n")}
        for rel, (dead, live) in cases.items():
            self.assertEqual(self.backed_by(rel, dead), 0, (rel, dead))
            self.assertEqual(self.backed_by(rel, live), 1, (rel, live))                  # positive control: uncommented

    def test_the_enforcers_own_unit_test_is_not_its_invoker(self):
        for name in ("gate.tests.sh", "gate.test.ps1", "test_gate.sh", "gate_test.cmd", "Gate.Tests.ps1"):
            self.assertEqual(self.backed_by("tools/" + name, "python tools/gate.py\n"), 0, name)
        self.assertEqual(self.backed_by("tools/other.tests.sh", "python tools/gate.py\n"), 1)     # another checker's test still counts
        # round-3 finding N5/N6: a NON-test surface sharing the enforcer's stem is a legitimate invoker
        self.assertEqual(self.backed_by(".github/workflows/gate.yml", "steps:\n  - run: python tools/gate.py\n"), 1)
        self.put("tools/pre-commit.py", ANC + " = 1\n")
        self.assertEqual(self.backed_by(".githooks/pre-commit", "python tools/pre-commit.py\n", "tools/pre-commit.py"), 1)
        # a different test file's mention of the enforcer's TEST file is not a command either
        self.put("tools/gate.tests.py", "x\n")
        self.assertEqual(self.backed_by("tools/cli.tests.sh", "see also gate.tests.py\n", "tools/gate.tests.py"), 0)

    def test_is_test_file_and_test_stem_unit(self):
        for name in ("foo.tests.sh", "foo.test.ps1", "test_foo.sh", "foo_test.cmd", "FooTests.cs", "Foo.Tests.ps1"):
            self.assertTrue(crt.is_test_file(name), name)
        for name in ("gate.yml", "pre-commit", "gate.sh", "latest.sh", "Contests.cs", "attest.sh", "testing.sh", "protest.ps1"):
            self.assertFalse(crt.is_test_file(name), name)
        for name, stem in (("foo.tests.py", "foo"), ("FooTests.cs", "foo"), ("test_foo.py", "foo"), ("foo-test.sh", "foo"),
                           ("foo.py", "foo"), ("latest.py", "latest"), ("Contest.cs", "contest")):
            self.assertEqual(crt.test_stem(name), stem, name)

    def test_enforcer_never_invokes_itself_and_excluded_surfaces_are_ignored(self):
        self.put("tools/gate.sh", ANC + "=1\ntools/gate.sh\n")
        self.assertEqual(self.invoked("tools/gate.sh", surfaces=["tools/*.sh"])["uninvoked"], 1)
        self.put(".githooks/x.frozen-1.sh", "python tools/gate.py\n")
        self.assertEqual(self.invoked()["uninvoked"], 0)
        self.assertEqual(self.invoked(invocation_exclude=["*.frozen-*"])["uninvoked"], 1)

    def test_a_reference_outside_every_surface_does_not_count(self):
        self.put("NOTES.md", "python tools/gate.py\n")
        self.assertEqual(self.invoked()["uninvoked"], 1)
        self.put(".github/workflows/ci.yml", "steps:\n  - run: python tools/gate.py\n")
        self.assertEqual(self.invoked(surfaces=[".githooks/*", ".github/workflows/*.yml"])["backed"], 1)

    @unittest.skipUnless(os.name == "nt", "case-insensitive filesystem")
    def test_windows_path_comparison_is_case_insensitive(self):
        self.assertEqual(self.backed_by(".githooks/w.sh", "python TOOLS\\GATE.PY\n"), 1)

    # ---- the requirement covers inline tags and fails closed
    def test_inline_tags_obey_the_requirement_by_default_when_surfaces_are_configured(self):
        self.doc("## Rules\n- a [enforced: tools/orphan.py]\n")
        self.put(".githooks/pre-commit", "python tools/gate.py\n")
        surf = {"invocation_surfaces": HOOK, "rule_map": None}
        self.assertEqual(self.counts(**surf)["uninvoked"], 1)                          # default is all
        self.assertEqual(self.counts("--require-invoked", **surf)["uninvoked"], 1)     # bare flag = all
        self.assertEqual(self.counts("--require-invoked", "all", **surf)["uninvoked"], 1)
        self.assertEqual(self.counts("--require-invoked", "map", **surf)["backed"], 1)  # map-only mode skips inline
        self.assertEqual(self.counts("--require-invoked", "off", **surf)["backed"], 1)
        self.doc("## Rules\n- a [enforced: tools/gate.py]\n")                          # positive control: wired inline tag
        self.assertEqual(self.counts(**surf)["backed"], 1)

    def test_inline_readme_cannot_back_a_rule_and_the_floor(self):
        self.doc("## Rules\n- never push to main [enforced: README.md]\n")
        self.put("README.md", "x\n")
        rc, out, _ = self.run_cli("--check", "--today", "2026-10-16", rule_map=None, invocation_surfaces=HOOK,
                                  floor_schedule=[{"date": "2026-10-16", "backed": 1}])
        self.assertEqual(rc, 1, out)
        self.assertIn("BELOW FLOOR", out)

    def test_echo_of_the_enforcer_cannot_meet_a_floor(self):
        # Codex round-2 repro: `echo tools/gate.py` is a mention, not a run
        self.put(".githooks/pre-commit", "echo tools/gate.py\n")
        self.doc("## Rules\n- a [enforced: tools/gate.py]\n")
        rc, out, _ = self.run_cli("--check", "--today", "2026-10-16", rule_map=None, invocation_surfaces=HOOK,
                                  floor_schedule=[{"date": "2026-10-16", "backed": 1}])
        self.assertEqual(rc, 1, out)

    def test_require_invoked_off_lifts_map_entries_too(self):
        self.map_alpha("tools/orphan.py")
        self.assertEqual(self.counts(invocation_surfaces=HOOK)["uninvoked"], 1)
        c = self.counts("--require-invoked", "off", invocation_surfaces=HOOK)
        self.assertEqual((c["backed"], c["uninvoked"]), (1, 0))

    def test_no_surfaces_and_no_explicit_mode_behaves_as_before_and_says_unchecked(self):
        self.mapfile({self.rid(ALPHA): {"kind": "enforced", "enforcer": "tools/orphan.py"}})
        rc, out, _ = self.run_cli("--report")
        self.assertIn("INVOCATION UNCHECKED p:", out)
        self.assertEqual(self.counts()["backed"], 1)          # existence alone backs it, as in v1
        self.assertEqual(self.run_cli("--check")[0], 0)       # no floor configured: nothing to miss
        rc, out, _ = self.run_cli("--report", invocation_surfaces=HOOK)
        self.assertNotIn("INVOCATION UNCHECKED", out)

    def test_explicit_requirement_without_surfaces_fails_closed(self):
        self.doc("## Rules\n- a [enforced: tools/gate.py]\n")
        for mode in (("--require-invoked",), ("--require-invoked", "all")):
            for surfaces in (None, []):
                c = self.counts(*mode, rule_map=None, invocation_surfaces=surfaces)
                self.assertEqual((c["backed"], c["uninvoked"]), (0, 1), (mode, surfaces))
                rc, out, _ = self.run_cli("--check", *mode, rule_map=None, invocation_surfaces=surfaces)
                self.assertEqual(rc, 1, (mode, surfaces, out))
                self.assertIn("INVOCATION REQUIRED p:", out)
        self.map_alpha()                                         # explicit map mode, no surfaces, map entry
        self.doc(MAPDOC)
        rc, out, _ = self.run_cli("--check", "--require-invoked", "map")
        self.assertEqual(rc, 1, out)
        self.assertEqual(self.counts("--require-invoked", "map")["backed"], 0)
        self.doc("## Rules\n- a [prose]\n")                      # zero enforced rules cannot pass a requirement it cannot evaluate
        self.assertEqual(self.run_cli("--check", "--require-invoked", rule_map=None)[0], 1)
        self.doc("## Rules\n- a [enforced: tools/gate.py]\n")    # negative control: no explicit flag = legacy regime
        self.assertEqual(self.run_cli("--check", rule_map=None)[0], 0)
        self.assertEqual(self.counts(rule_map=None)["backed"], 1)

    # ---- unchecked backing never counts toward a floor (round 3, item 3)
    def test_unchecked_backing_never_counts_toward_a_floor(self):
        floor = [{"date": "2026-10-16", "backed": 1}]
        self.doc("## Rules\n- a [enforced: README.md]\n")
        self.put("README.md", "x\n")
        self.put(".githooks/pre-commit", "python tools/gate.py\n")
        for label, extra, over in (("no surfaces", (), {}), ("off", ("--require-invoked", "off"), {"invocation_surfaces": HOOK}),
                                   ("map mode inline", ("--require-invoked", "map"), {"invocation_surfaces": HOOK})):
            rc, out, _ = self.run_cli("--check", "--today", "2026-10-16", *extra, rule_map=None, floor_schedule=floor, **over)
            self.assertEqual(rc, 1, (label, out))
            self.assertIn("FLOOR-UNCHECKED-BACKING p: 1 backed rule(s)", out)
            self.assertIn("BELOW FLOOR", out)
            self.assertEqual(self.counts(*extra, rule_map=None, floor_schedule=floor, **over)["backed"], 1, label)   # still reported as backed
        # the message is informational when the floor is met by checked backing
        self.doc("## Rules\n- a [enforced: README.md]\n- b [enforced: tools/gate.py]\n")
        rc, out, _ = self.run_cli("--check", "--today", "2026-10-16", "--require-invoked", "map", rule_map=None,
                                  floor_schedule=floor, invocation_surfaces=HOOK)
        self.assertEqual(rc, 1, out)                 # map mode checks only map entries: both inline tags are unchecked
        # negative control: invocation-checked backing meets the floor and prints no warning
        self.doc("## Rules\n- b [enforced: tools/gate.py]\n")
        rc, out, _ = self.run_cli("--check", "--today", "2026-10-16", rule_map=None, floor_schedule=floor, invocation_surfaces=HOOK)
        self.assertEqual(rc, 0, out)
        self.assertNotIn("FLOOR-UNCHECKED-BACKING", out)
        # map entries are checked in map mode, so they still count there
        self.doc(MAPDOC)
        self.map_alpha()
        rc, out, _ = self.run_cli("--check", "--today", "2026-10-16", "--require-invoked", "map", floor_schedule=floor,
                                  invocation_surfaces=HOOK)
        self.assertEqual(rc, 0, out)

    # ---- git-hook placement is verified against the effective hooks directory
    def hook_case(self, hooks_path, name="pre-commit"):
        self.git("init", "-q")
        if hooks_path:
            self.git("config", "core.hooksPath", hooks_path)
        self.put(f".githooks/{name}", "#!/bin/sh\necho ANCHOR_MAIN\n")
        self.map_alpha(f".githooks/{name}")
        return self.run_cli("--report", invocation_surfaces=HOOK, placement_invoked=[f".githooks/{name}"])

    def test_placement_is_backed_only_when_git_runs_that_directory(self):
        rc, out, _ = self.hook_case(".githooks")
        self.assertIn("coverage 1/4", out)
        self.assertNotIn("PLACEMENT UNWIRED", out)

    def test_placement_with_hooks_path_unset_uses_git_hooks_and_is_not_wired(self):
        rc, out, _ = self.hook_case(None)                       # default .git/hooks; the enforcer lives in .githooks
        self.assertIn("coverage 0/4", out)
        self.assertIn("PLACEMENT UNWIRED p: .githooks/pre-commit", out)

    def test_placement_with_hooks_path_elsewhere_is_not_wired(self):
        rc, out, _ = self.hook_case(".review-disabled-hooks")
        self.assertIn("coverage 0/4", out)
        self.assertIn("PLACEMENT UNWIRED", out)

    def test_placement_in_a_directory_that_is_not_a_git_repo_is_not_wired(self):
        self.put(".githooks/pre-commit", "#!/bin/sh\necho ANCHOR_MAIN\n")
        self.map_alpha(".githooks/pre-commit")
        rc, out, _ = self.run_cli("--report", invocation_surfaces=HOOK, placement_invoked=[".githooks/pre-commit"])
        self.assertIn("coverage 0/4", out)

    def test_placement_is_not_fooled_by_a_git_config_environment_override(self):
        self.git("init", "-q")
        self.git("config", "core.hooksPath", ".githooks")
        self.put(".githooks/pre-commit", "#!/bin/sh\necho ANCHOR_MAIN\n")
        self.map_alpha(".githooks/pre-commit")
        over = {"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "core.hooksPath", "GIT_CONFIG_VALUE_0": ".review-disabled-hooks"}
        with mock.patch.dict(os.environ, over):
            rc, out, _ = self.run_cli("--report", invocation_surfaces=HOOK, placement_invoked=[".githooks/pre-commit"])
        self.assertIn("coverage 0/4", out)

    def test_a_placement_glob_alone_does_not_back_a_file_outside_the_hooks_directory(self):
        self.git("init", "-q")
        self.git("config", "core.hooksPath", ".githooks")
        self.map_alpha("tools/gate.py")
        rc, out, _ = self.run_cli("--report", invocation_surfaces=HOOK, placement_invoked=["tools/gate.py"])
        self.assertIn("coverage 0/4", out)

    def test_only_real_git_hook_names_can_be_placement_invoked(self):
        rc, out, _ = self.hook_case(".githooks", name="notahook.sh")          # wired directory, but not a hook name
        self.assertIn("coverage 0/4", out)
        for name in ("pre-push", "commit-msg", "post-commit", "update", "reference-transaction"):
            self.assertIn(name, crt.GIT_HOOKS)
        for name in ("notahook.sh", "pre-commit.sample", "README", "pre-commit.frozen-1"):
            self.assertNotIn(name, crt.GIT_HOOKS)
        shutil.rmtree(os.path.join(self.root, ".git"), ignore_errors=True)
        rc, out, _ = self.hook_case(".githooks", name="pre-push")             # positive control: another real hook name
        self.assertIn("coverage 1/4", out)

    # ---- anchors: claims keyed by enforcement LOCATION
    def test_checked_map_entry_without_an_anchor_is_exit_2(self):
        self.mapfile({self.rid(ALPHA): {"kind": "enforced", "enforcer": "tools/gate.py"}})
        self.put(".githooks/pre-commit", "python tools/gate.py\n")
        self.assertEqual(self.run_cli("--report", invocation_surfaces=HOOK)[0], 2)
        self.mapfile({self.rid(ALPHA): enf("tools/gate.py", "")})
        self.assertEqual(self.run_cli("--report", invocation_surfaces=HOOK)[0], 2)

    def test_anchor_must_occur_on_a_non_comment_line_of_the_enforcer(self):
        self.put(".githooks/pre-commit", "python tools/gate.py\n")
        self.put("tools/gate.py", "# ANCHOR_ONLY_IN_A_COMMENT\nx = 1  # ANCHOR_TRAILING\nANCHOR_REAL = 1\n"
                                  "'''\nANCHOR_IN_DOCSTRING\n'''\n/* ANCHOR_IN_BLOCK */\n")
        for anchor, backed in (("ANCHOR_REAL", 1), ("ANCHOR_ONLY_IN_A_COMMENT", 0), ("ANCHOR_TRAILING", 0),
                               ("ANCHOR_IN_DOCSTRING", 0), ("ANCHOR_IN_BLOCK", 0), ("ABSENT_ANCHOR", 0)):
            self.map_alpha(anchor=anchor)
            c = self.counts(invocation_surfaces=HOOK)
            self.assertEqual((c["backed"], c["dangling"]), (backed, 1 - backed), anchor)

    def test_anchor_must_be_on_exactly_one_line_and_at_least_eight_chars(self):
        self.put(".githooks/pre-commit", "python tools/gate.py\n")
        self.put("tools/gate.py", "ANCHOR_TWICE = 1\ny = ANCHOR_TWICE\nSHORT7 = 1\nEIGHT888 = 1\n")
        self.map_alpha(anchor="ANCHOR_TWICE")
        c = self.counts(invocation_surfaces=HOOK)
        self.assertEqual((c["backed"], c["ambiguous"], c["dangling"]), (0, 1, 0))
        rc, out, _ = self.run_cli(invocation_surfaces=HOOK)
        self.assertEqual(rc, 1)
        self.assertIn("ANCHOR-AMBIGUOUS p RULES.md:", out)
        self.assertIn("lines 1, 2", out)
        self.map_alpha(anchor="SHORT7")                                  # 6 non-space chars
        self.assertEqual(self.counts(invocation_surfaces=HOOK)["dangling"], 1)
        self.map_alpha(anchor="SHORT7 =")                                # 7 non-space chars even with a space
        self.assertEqual(self.counts(invocation_surfaces=HOOK)["backed"], 0)
        self.map_alpha(anchor="EIGHT888")                                # exactly 8
        self.assertEqual(self.counts(invocation_surfaces=HOOK)["backed"], 1)
        self.map_alpha(anchor="  x  ")
        self.assertEqual(self.counts(invocation_surfaces=HOOK)["backed"], 0)

    def test_one_enforcer_cannot_back_many_rules_with_one_anchor(self):
        self.put(".githooks/pre-commit", "python tools/gate.py\n")
        self.put("tools/gate.py", "ANCHOR_ONE = 1\nANCHOR_TWO = 2\n")
        self.mapfile({self.rid(ALPHA): enf("tools/gate.py", "ANCHOR_ONE"), self.rid(BETA): enf("tools/gate.py", "ANCHOR_ONE"),
                      self.rid(GAMMA): enf("tools/gate.py", "ANCHOR_TWO"), self.rid(DELTA): enf("tools/gate.py", "ANCHOR_ONE")})
        j = self.census_json(invocation_surfaces=HOOK)
        self.assertEqual((j["counts"]["backed"], j["counts"]["dup_anchor"]), (2, 2))     # Alpha and Gamma; Beta, Delta duplicate
        self.assertEqual(j["fanin"], {"tools/gate.py": {"backed": 2, "anchors": ["ANCHOR_ONE@1", "ANCHOR_TWO@2"]}})
        rc, out, _ = self.run_cli(invocation_surfaces=HOOK)
        self.assertEqual(rc, 1)
        self.assertIn("ANCHOR-DUPLICATE p RULES.md:", out)
        self.assertIn("fan-in p: tools/gate.py backs 2 rule(s): ANCHOR_ONE@1 | ANCHOR_TWO@2", out)

    def test_overlapping_anchors_on_one_line_back_exactly_one_rule(self):
        # Opus F2: substrings of ONE hook line, each a different string, each unique on that line
        self.put(".githooks/pre-commit", "python tools/gate.py\n")
        self.put("tools/gate.py", "GATE_REFUSED_TEXT = 'exit 1 refused'\nOTHER_LINE_HERE = 2\n")
        names = ["GATE_REFUSED_TEXT", "GATE_REFUSED", "REFUSED_TEXT", "exit 1 refused", "TEXT = 'exit"]
        self.doc("## Rules\n" + "".join(f"- rule {i}\n" for i in range(5)))
        self.mapfile({self.rid(f"rule {i}"): enf("tools/gate.py", a) for i, a in enumerate(names)})
        j = self.census_json(invocation_surfaces=HOOK)
        self.assertEqual((j["counts"]["backed"], j["counts"]["dup_anchor"]), (1, 4))
        rc, out, _ = self.run_cli("--check", "--today", "2026-10-16", invocation_surfaces=HOOK,
                                  floor_schedule=[{"date": "2026-10-16", "backed": 5}])
        self.assertEqual(rc, 1, out)

    def test_near_duplicate_rule_texts_cannot_share_a_line(self):
        # Opus G2: a one-character rewording gets a new id, but not a new enforcement location
        self.put(".githooks/pre-commit", "python tools/gate.py\n")
        self.put("tools/gate.py", "echo gate refused!\n")
        self.doc("## Rules\n- rule b\n- rule b.\n")
        self.mapfile({self.rid("rule b"): enf("tools/gate.py", "gate refused"), self.rid("rule b."): enf("tools/gate.py", "e refused!")})
        c = self.counts(invocation_surfaces=HOOK)
        self.assertEqual((c["backed"], c["dup_anchor"]), (1, 1))
        rc, out, _ = self.run_cli("--check", "--today", "2026-10-16", invocation_surfaces=HOOK,
                                  floor_schedule=[{"date": "2026-10-16", "backed": 2}])
        self.assertEqual(rc, 1, out)

    def test_prefix_anchors_of_one_line_cannot_meet_dng_style_floors(self):
        # Codex round-2 repro shape: prefixes of one existing line as 46 different anchors
        line = 'echo "SKIPPED build and test: every staged path is one of the three governing docs"'
        self.put(".githooks/pre-commit", "python tools/gate.py\n")
        self.put("tools/gate.py", line + "\nSECOND_LINE_OF_CODE = 1\n")
        self.doc("## Rules\n" + "".join(f"- rule {i}\n" for i in range(46)))
        self.mapfile({self.rid(f"rule {i}"): enf("tools/gate.py", line[:12 + i]) for i in range(46)})
        c = self.counts(invocation_surfaces=HOOK)
        self.assertEqual((c["backed"], c["dup_anchor"]), (1, 45))

    def test_distinct_lines_each_back_one_rule(self):
        # negative control for the location key: genuinely different lines are different enforcement points
        self.put(".githooks/pre-commit", "python tools/gate.py\n")
        self.put("tools/gate.py", "REFUSE_ALPHA = 1\nREFUSE_BETA = 2\nREFUSE_GAMMA = 3\n")
        self.mapfile({self.rid(ALPHA): enf("tools/gate.py", "REFUSE_ALPHA"), self.rid(BETA): enf("tools/gate.py", "REFUSE_BETA"),
                      self.rid(GAMMA): enf("tools/gate.py", "REFUSE_GAMMA")})
        self.assertEqual(self.counts(invocation_surfaces=HOOK)["backed"], 3)

    def test_inline_anchor_syntax_and_the_one_per_enforcer_cap(self):
        self.put(".githooks/pre-commit", "python tools/gate.py\n")
        self.put("tools/gate.py", "ANCHOR_ONE = 1\nANCHOR_TWO = 2\n")
        surf = {"invocation_surfaces": HOOK, "rule_map": None}
        self.doc("## Rules\n- a [enforced: tools/gate.py]\n- b [enforced: tools/gate.py]\n")      # unanchored: one only
        c = self.counts(**surf)
        self.assertEqual((c["backed"], c["dup_anchor"]), (1, 1))
        self.doc("## Rules\n- a [enforced: tools/gate.py#ANCHOR_ONE]\n- b [enforced: tools/gate.py#ANCHOR_TWO]\n")
        self.assertEqual(self.counts(**surf)["backed"], 2)
        self.doc("## Rules\n- a [enforced: tools/gate.py#ANCHOR_ONE]\n- b [enforced: tools/gate.py#ANCHOR_ONE]\n")
        self.assertEqual(self.counts(**surf)["dup_anchor"], 1)
        self.doc("## Rules\n- a [enforced: tools/gate.py#ANCHOR_NOPE]\n")
        self.assertEqual(self.counts(**surf)["dangling"], 1)

    def test_legacy_unchecked_regime_keeps_unanchored_inline_tags_uncapped(self):
        self.doc("## Rules\n- a [enforced: tools/gate.py]\n- b [enforced: tools/gate.py]\n")
        self.assertEqual(self.counts(rule_map=None)["backed"], 2)

    # ---- distinct ids, duplicates reported
    def test_twenty_copies_of_one_backed_rule_count_once_and_miss_a_floor_of_twenty(self):
        self.put(".githooks/pre-commit", "python tools/gate.py\n")
        self.doc("## Rules\n" + "- same rule [enforced: tools/gate.py]\n" * 20)
        rc, out, _ = self.run_cli("--check", "--today", "2026-10-23", rule_map=None, invocation_surfaces=HOOK,
                                  floor_schedule=[{"date": "2026-10-23", "backed": 20}])
        self.assertEqual(rc, 1, out)
        self.assertIn("BELOW FLOOR", out)
        j = self.census_json(rule_map=None, invocation_surfaces=HOOK)
        self.assertEqual((j["counts"]["backed"], j["counts"]["duplicates"], j["counts"]["bullets"]), (1, 19, 20))
        self.assertEqual(len(j["duplicates"]), 19)
        self.assertEqual(j["coverage"], {"backed": 1, "denominator": 1, "pct": 100.0})
        self.assertIn("DUPLICATE p RULES.md:", self.run_cli("--report", rule_map=None)[1])

    def test_duplicate_texts_are_not_counted_in_any_kind_and_distinct_rules_still_are(self):
        self.doc("## Rules\n- a [prose]\n- a [prose]\n- b [judgement]\n- b [judgement]\n- c [prose]\n")
        c = self.counts(rule_map=None)
        self.assertEqual((c["bullets"], c["prose"], c["judgement"], c["duplicates"]), (5, 2, 1, 2))

    # ---- floor
    FLOORS = [{"date": "2026-10-16", "backed": 1}, {"date": "2026-10-23", "backed": 2}, {"date": "2026-11-06", "backed": 3}]
    LETTERS = "ABCDEFGH"

    def floor_case(self, today, backed_rules, floors=None):
        """A project whose invocation is checked: `backed_rules` anchored inline rules plus one prose rule."""
        self.put(".githooks/pre-commit", "python tools/gate.py\n")
        self.put("tools/gate.py", "".join(f"RULE_ANCHOR_{self.LETTERS[i]} = {i}\n" for i in range(8)))
        self.doc("## Rules\n" + "".join(f"- r{i} [enforced: tools/gate.py#RULE_ANCHOR_{self.LETTERS[i]}]\n"
                                         for i in range(backed_rules)) + "- p [prose]\n")
        return self.run_cli("--check", "--today", today, rule_map=None, invocation_surfaces=HOOK,
                            floor_schedule=floors or self.FLOORS)

    def test_floor_fails_below_and_passes_at_or_above(self):
        rc, out, _ = self.floor_case("2026-10-23", 1)
        self.assertEqual(rc, 1, out)
        self.assertIn("BELOW FLOOR", out)
        rc, out, _ = self.floor_case("2026-10-23", 2)
        self.assertEqual(rc, 0, out)
        self.assertIn("floor p: required 2 backed (since 2026-10-23), have 2: OK", out)
        self.assertEqual(self.floor_case("2026-10-23", 3)[0], 0)

    def test_floor_uses_the_latest_due_entry_and_prints_the_next(self):
        rc, out, _ = self.floor_case("2026-10-22", 1)
        self.assertEqual(rc, 0, out)
        self.assertIn("next floor 2 backed on 2026-10-23", out)
        rc, out, _ = self.floor_case("2026-12-01", 2)
        self.assertEqual(rc, 1, out)
        self.assertIn("required 3 backed (since 2026-11-06)", out)
        self.assertIn("no later floor", out)

    def test_floor_before_the_first_date_requires_nothing(self):
        rc, out, _ = self.floor_case("2026-10-01", 0)
        self.assertEqual(rc, 0, out)
        self.assertIn("required none due yet", out)

    def test_floor_is_enforced_only_by_check_and_report_never_fails(self):
        self.doc("## Rules\n- p [prose]\n")
        self.assertEqual(self.run_cli("--today", "2026-12-01", rule_map=None, floor_schedule=self.FLOORS)[0], 0)
        self.assertEqual(self.run_cli("--check", "--report", "--today", "2026-12-01", rule_map=None, floor_schedule=self.FLOORS)[0], 0)
        self.assertEqual(self.run_cli("--check", "--today", "2026-12-01", rule_map=None, floor_schedule=self.FLOORS)[0], 1)

    def test_check_still_fails_on_dangling_and_bad_today_is_exit_2(self):
        self.doc("## Rules\n- a [enforced: tools/gone.py]\n")
        self.assertEqual(self.run_cli("--check", rule_map=None)[0], 1)
        self.assertEqual(self.run_cli("--check", "--today", "soon", rule_map=None)[0], 2)

    def test_default_today_is_the_utc_date(self):
        real = datetime.datetime

        class FakeDT(real):
            @classmethod
            def now(cls, tz=None):
                if tz is None:
                    return real(2026, 10, 23, 1, 0)                           # local clock already on the 23rd
                return real(2026, 10, 22, 23, 30, tzinfo=tz)                  # UTC is still the 22nd

        floors = [{"date": "2026-10-22", "backed": 1}, {"date": "2026-10-23", "backed": 5}]
        with mock.patch.object(datetime, "datetime", FakeDT):
            self.put(".githooks/pre-commit", "python tools/gate.py\n")
            self.put("tools/gate.py", "RULE_ANCHOR_A = 1\n")
            self.doc("## Rules\n- p [enforced: tools/gate.py#RULE_ANCHOR_A]\n")
            rc, out, _ = self.run_cli("--check", rule_map=None, invocation_surfaces=HOOK, floor_schedule=floors)
        self.assertEqual(rc, 0, out)
        self.assertIn("required 1 backed (since 2026-10-22)", out)

    def test_invalid_floor_schedules_are_exit_2_even_in_report_mode(self):
        bad = {
            "negative": [{"date": "2026-10-16", "backed": -1}],
            "fractional": [{"date": "2026-10-16", "backed": 2.9}],
            "bool": [{"date": "2026-10-16", "backed": True}],
            "string": [{"date": "2026-10-16", "backed": "3"}],
            "bad date": [{"date": "2026-1-5", "backed": 1}],
            "compact date": [{"date": "20261016", "backed": 1}],
            "missing key": [{"date": "2026-10-16"}],
            "decreasing floors": [{"date": "2026-10-16", "backed": 20}, {"date": "2026-10-23", "backed": 0}],
            "equal dates": [{"date": "2026-10-16", "backed": 1}, {"date": "2026-10-16", "backed": 2}],
            "out of order dates": [{"date": "2026-10-23", "backed": 1}, {"date": "2026-10-16", "backed": 2}],
        }
        for label, sched in bad.items():
            self.assertEqual(self.run_cli("--report", rule_map=None, floor_schedule=sched)[0], 2, label)
            self.assertEqual(self.run_cli("--check", rule_map=None, floor_schedule=sched)[0], 2, label)
        flat = [{"date": "2026-10-16", "backed": 2}, {"date": "2026-10-23", "backed": 2}]      # non-decreasing is fine
        self.assertEqual(self.run_cli("--report", rule_map=None, floor_schedule=flat)[0], 0)
        self.assertEqual(self.run_cli("--report", rule_map=None, floor_schedule=[{"date": "2026-10-16", "backed": 0}])[0], 0)

    # ---- emit-map
    def test_emit_map_writes_every_rule_as_prose_and_round_trips(self):
        outp = os.path.join(self.tmp, "emitted.json")
        rc, out, _ = self.run_cli("--emit-map", outp)
        self.assertEqual(rc, 0, out)
        with open(outp, encoding="utf-8") as fh:
            doc = json.load(fh)
        self.assertEqual(doc["schema"], "rule-map.v1")
        self.assertEqual(len(doc["rules"]), 4)
        self.assertEqual({e["kind"] for e in doc["rules"].values()}, {"prose"})
        beta = doc["rules"][self.rid(BETA)]
        self.assertEqual((beta["source"], beta["line_hint"], beta["text_head"]), ("RULES.md", 6, BETA))
        c = self.counts("--rule-map", outp)
        self.assertEqual((c["prose"], c["untagged"]), (4, 0))

    def test_emit_map_to_stdout(self):
        rc, out, _ = self.run_cli("--emit-map")
        self.assertEqual(json.loads(out)["schema"], "rule-map.v1")

    def test_emit_map_to_an_unwritable_path_is_exit_2_not_a_traceback(self):
        for bad in (os.path.join(self.tmp, "no", "such", "dir", "out.json"), self.tmp):       # missing dir, a directory
            rc, out, err = self.run_cli("--emit-map", bad)
            self.assertEqual(rc, 2, (bad, out, err))
            self.assertIn("cannot write", err)

    def test_emit_map_and_root_need_exactly_one_matching_project(self):
        proj2 = dict(self.proj, name="q")
        two = os.path.join(self.tmp, "two.json")
        with open(two, "w", encoding="utf-8") as fh:
            json.dump({"schema": crt.SCHEMA, "projects": [dict(self.proj), proj2]}, fh)
        for extra in (["--emit-map"], ["--root", self.root], ["--rule-map", "x.json"]):
            err = io.StringIO()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                rc = crt.main(["--config", two, *extra])
            self.assertEqual(rc, 2, extra)
            self.assertIn("exactly one --project", err.getvalue())
        err = io.StringIO()                                          # naming one project passes the guard
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
            self.assertEqual(crt.main(["--config", two, "--project", "q", "--emit-map"]), 0)
        rc, _, _ = self.run_cli("--emit-map", "--project", "nope")   # an unknown project fails differently
        self.assertEqual(rc, 2)

    def test_text_head_is_at_most_60_chars(self):
        self.doc("## Rules\n- " + "x" * 200 + "\n")
        out = os.path.join(self.tmp, "e.json")
        self.run_cli("--emit-map", out)
        with open(out, encoding="utf-8") as fh:
            self.assertEqual([len(e["text_head"]) for e in json.load(fh)["rules"].values()], [60])

    # ---- root_candidates then root
    def bus_cfg(self, proj):
        bus = os.path.join(self.tmp, "bus")
        os.makedirs(os.path.join(bus, "tools"), exist_ok=True)
        cfgp = os.path.join(bus, "tools", "c.json")
        with open(cfgp, "w", encoding="utf-8") as fh:
            json.dump({"schema": crt.SCHEMA, "projects": [proj]}, fh)
        return cfgp

    def run_root(self, cfgp):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            rc = crt.main(["--config", cfgp, "--report", "--json"])
        return rc, (json.loads(out.getvalue())["root"] if rc == 0 else None)

    def test_root_candidates_come_first_in_order_then_root(self):
        sib = os.path.join(self.tmp, "sibling")
        shutil.copytree(self.root, sib)
        other = os.path.join(self.tmp, "other")
        shutil.copytree(self.root, other)
        base = dict(self.proj, rule_map=None)
        rc, root = self.run_root(self.bus_cfg(dict(base, root=self.root, root_candidates=[os.path.join(self.tmp, "absent"), "../sibling"])))
        self.assertEqual(os.path.realpath(root), os.path.realpath(sib))
        rc, root = self.run_root(self.bus_cfg(dict(base, root=self.root, root_candidates=[other, "../sibling"])))
        self.assertEqual(os.path.realpath(root), os.path.realpath(other))
        rc, root = self.run_root(self.bus_cfg(dict(base, root=self.root, root_candidates=[os.path.join(self.tmp, "absent2")])))
        self.assertEqual(os.path.realpath(root), os.path.realpath(self.root))
        rc, root = self.run_root(self.bus_cfg(dict(base, root=os.path.join(self.tmp, "absent"), root_candidates=[os.path.join(self.tmp, "absent2")])))
        self.assertEqual(rc, 2)

    # ---- BOM and encodings
    def test_utf8_bom_before_a_line_one_heading_does_not_hide_the_section(self):
        with open(os.path.join(self.root, "RULES.md"), "wb") as fh:
            fh.write(b"\xef\xbb\xbf## Rules\n- a [prose]\n- b [prose]\n")
        self.assertEqual(self.counts(rule_map=None)["prose"], 2)
        cfg = os.path.join(self.tmp, "bom.json")
        with open(cfg, "wb") as fh:
            fh.write(b"\xef\xbb\xbf" + json.dumps({"schema": crt.SCHEMA, "projects": [dict(self.proj, rule_map=None)]}).encode("utf-8"))
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(crt.main(["--config", cfg, "--report"]), 0)

    def test_a_file_that_is_not_utf8_is_exit_2_with_a_message_never_a_traceback(self):
        with open(os.path.join(self.root, "RULES.md"), "wb") as fh:
            fh.write(b"## Rules\n- caf\xe9 [prose]\n")                    # latin-1 byte
        for extra in (("--report",), ("--check",), ("--emit-map",)):
            rc, out, err = self.run_cli(*extra, rule_map=None)
            self.assertEqual(rc, 2, (extra, out, err))
            self.assertIn("not valid UTF-8", err)
        self.doc(MAPDOC)                                                  # a latin-1 map and config too
        self.put("factory/rule-map.json", "")
        with open(os.path.join(self.root, "factory", "rule-map.json"), "wb") as fh:
            fh.write(b'{"schema": "rule-map.v1", "rules": {"a": {"kind": "prose", "text_head": "caf\xe9"}}}')
        self.assertEqual(self.run_cli("--report")[0], 2)
        cfg = os.path.join(self.tmp, "bad.json")
        with open(cfg, "wb") as fh:
            fh.write(b'{"schema": "fleet/rule-tags/v1", "x": "\xe9"}')
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(crt.main(["--config", cfg, "--report"]), 2)

    # ---- the shipped DNG entry
    def test_shipped_dng_entry_matches_the_spec_and_its_regex_takes_bold_numbered_and_dash_units(self):
        cfg = crt.load_config(str(HERE / "rule-tags.config.json"))
        dng = next(p for p in cfg["projects"] if p["name"] == "dng-auto-processor")
        self.assertEqual([f["path"] for f in dng["files"]], ["docs/14-ORCHESTRATION.md", "AGENTS.md"])
        self.assertEqual(dng["rule_map"], "factory/rule-map.json")
        self.assertEqual(dng["root_candidates"][0], "C:/code/DngAutoProcessor - Claude/DngAutoProcessor")
        self.assertEqual(dng["invocation_surfaces"], [".githooks/*", ".github/workflows/*.yml"])
        self.assertEqual([(f["date"], f["backed"]) for f in dng["floor_schedule"]],
                         [("2026-10-16", 3), ("2026-10-23", 20), ("2026-10-30", 35), ("2026-11-06", 46)])
        crt.parse_floors(dng)
        self.doc("- dash\n1. numbered\n**Bold-led.** paragraph\nnot a rule\n\nplain\n")
        c = self.counts(rule_map=None, files=[{"path": "RULES.md", "bullet": dng["files"][0]["bullet"]}])
        self.assertEqual(c["bullets"], 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
