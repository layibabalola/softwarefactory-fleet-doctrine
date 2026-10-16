#!/usr/bin/env python3
"""Tests for tools/check-rule-tags.py. Run: python tools/check-rule-tags.tests.py

Every case drives main() (the CLI entry point) over a disposable project, so the exit status a caller
gates on is what is asserted."""
import contextlib
import importlib.util
import io
import json
import os
import pathlib
import shutil
import tempfile
import unittest

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
# v2: sidecar map, judgement/record kinds, fences, invocation, rising floor, emit-map.

MAPDOC = """# Project

## Rules

- **Alpha.** Refused by the gate.
- **Beta.** A reviewer
  decides this one.
- **Gamma.** History as written.
- **Delta.** Plain prose rule.
"""


def hashlib_id(text):
    import hashlib
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


class V2(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="rule-tags2-")
        self.root = os.path.join(self.tmp, "proj")
        for d in ("tools", ".githooks", ".github/workflows", "factory"):
            os.makedirs(os.path.join(self.root, d))
        for p in ("tools/gate.py", "tools/orphan.py"):
            open(os.path.join(self.root, p), "w").close()
        self.proj = {"name": "p", "root": self.root, "rule_map": "factory/rule-map.json",
                     "files": [{"path": "RULES.md", "section": "## Rules", "bullet": "^- "}]}
        self.doc(MAPDOC)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def put(self, rel, text):
        full = os.path.join(self.root, rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)

    def doc(self, text):
        self.put("RULES.md", text)

    def cfg(self, **over):
        proj = dict(self.proj, **over)
        proj = {k: v for k, v in proj.items() if v is not None}
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

    # ---- id
    def test_id_is_stable_under_rewrap_and_marker_style(self):
        a = crt.rule_id("- **Beta.** A reviewer\n  decides this one.")
        self.assertEqual(a, crt.rule_id("* **Beta.**   A reviewer decides this one.  "))
        self.assertEqual(a, hashlib_id("**Beta.** A reviewer decides this one."))
        self.assertEqual(len(a), 12)
        self.assertNotEqual(a, crt.rule_id("- **Beta.** A reviewer decides this one!"))
        self.assertEqual(crt.rule_id("3. numbered rule"), crt.rule_id("- numbered rule"))

    # ---- sidecar map
    def test_map_classifies_without_editing_prose(self):
        self.mapfile({
            self.rid("**Alpha.** Refused by the gate."): {"kind": "enforced", "enforcer": "tools/gate.py"},
            self.rid("**Beta.** A reviewer decides this one."): {"kind": "judgement"},
            self.rid("**Gamma.** History as written."): {"kind": "record"},
            self.rid("**Delta.** Plain prose rule."): {"kind": "prose"}})
        j = self.census_json()
        c = j["counts"]
        self.assertEqual((c["bullets"], c["backed"], c["judgement"], c["record"], c["prose"], c["untagged"]), (4, 1, 1, 1, 1, 0))
        self.assertEqual(j["coverage"], {"backed": 1, "denominator": 2, "pct": 50.0})

    def test_inline_tag_wins_over_the_map(self):
        self.doc(MAPDOC.replace("Plain prose rule.", "Plain prose rule. [prose]"))
        self.mapfile({self.rid("**Delta.** Plain prose rule. [prose]"): {"kind": "record"}})
        c = self.counts()
        self.assertEqual((c["prose"], c["record"]), (1, 0))

    def test_stale_entry_counted_printed_and_fatal_only_when_strict(self):
        self.mapfile({self.rid("**Delta.** Plain prose rule."): {"kind": "prose"},
                      "deadbeef0000": {"kind": "prose", "source": "RULES.md", "line_hint": 9, "text_head": "reworded rule"}})
        self.assertEqual(self.counts()["stale"], 1)
        rc, out, _ = self.run_cli("--report")
        self.assertIn("STALE p map deadbeef0000 RULES.md:9 reworded rule", out)
        # three rules are untagged here, so judge fatality through --check (untagged is not a --check failure)
        rc, out, _ = self.run_cli("--check")
        self.assertEqual(rc, 0, out)
        rc, out, _ = self.run_cli("--check", "--strict-map")
        self.assertEqual(rc, 1, out)

    def test_reworded_rule_goes_stale_and_untagged(self):
        self.mapfile({self.rid("**Delta.** Plain prose rule."): {"kind": "prose"}})
        self.assertEqual(self.counts()["stale"], 0)
        self.doc(MAPDOC.replace("Plain prose rule.", "Plain prose rule, reworded."))
        c = self.counts()
        self.assertEqual((c["stale"], c["prose"]), (1, 0))

    def test_missing_or_malformed_map_is_exit_2_never_zero(self):
        rc, _, err = self.run_cli("--report")          # rule_map configured, file absent
        self.assertEqual(rc, 2, err)
        self.put("factory/rule-map.json", "{not json")
        self.assertEqual(self.run_cli("--report")[0], 2)
        self.mapfile({"abc": {"kind": "enforced"}})     # enforced without an enforcer
        self.assertEqual(self.run_cli("--report")[0], 2)
        self.mapfile({"abc": {"kind": "bogus"}})
        self.assertEqual(self.run_cli("--report")[0], 2)
        self.put("factory/rule-map.json", json.dumps({"schema": "rule-map.v9", "rules": {}}))
        self.assertEqual(self.run_cli("--report")[0], 2)

    def test_enforcer_missing_or_escaping_is_dangling_in_the_map(self):
        rid = self.rid("**Alpha.** Refused by the gate.")
        for bad in ("tools/gone.py", "../outside.py", "tools"):
            self.mapfile({rid: {"kind": "enforced", "enforcer": bad}})
            self.assertEqual(self.counts()["dangling"], 1, bad)

    def test_rule_map_cli_override(self):
        other = os.path.join(self.tmp, "other-map.json")
        with open(other, "w", encoding="utf-8") as fh:
            json.dump({"schema": "rule-map.v1", "rules": {self.rid("**Delta.** Plain prose rule."): {"kind": "prose"}}}, fh)
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
        self.assertEqual(self.counts(rule_map=None)["bullets"], 2)     # before + after; the fenced heading did not end the scan

    def test_bullet_inside_a_fence_is_not_a_rule_and_tilde_fences_work(self):
        self.doc("## Rules\n- real\n```\n- fake in backticks\n```\n~~~sh\n- fake in tildes\n~~~\n- real two\n")
        self.assertEqual(self.counts(rule_map=None)["bullets"], 2)

    def test_a_fence_ends_a_bullet_and_a_shorter_fence_does_not_close_a_longer(self):
        self.doc("## Rules\n- a rule\n```\ncode line\n```\n- two\n````\n```\n- still fenced\n```\n````\n- three\n")
        j = self.census_json(rule_map=None)
        self.assertEqual(j["counts"]["bullets"], 3)
        self.assertNotIn("code line", json.dumps(j))

    def test_unclosed_fence_warns(self):
        self.doc("## Rules\n- one\n```\n- swallowed\n")
        rc, out, _ = self.run_cli("--report", rule_map=None)
        self.assertIn("unclosed code fence", out)
        self.assertIn("1 rules", out)

    # ---- invocation
    def invoked_setup(self, enforcer="tools/gate.py"):
        self.mapfile({self.rid("**Alpha.** Refused by the gate."): {"kind": "enforced", "enforcer": enforcer}})

    def test_existing_but_never_invoked_enforcer_is_not_backed(self):
        self.invoked_setup("tools/orphan.py")
        self.put(".githooks/pre-commit", "python tools/gate.py\n")        # invokes gate.py, not orphan.py
        c = self.counts(invocation_surfaces=[".githooks/*"])
        self.assertEqual((c["backed"], c["uninvoked"]), (0, 1))
        rc, out, _ = self.run_cli(invocation_surfaces=[".githooks/*"])
        self.assertEqual(rc, 1)
        self.assertIn("ENFORCED-UNINVOKED p RULES.md:", out)
        self.assertIn("coverage 0/4", out)

    def test_invoked_by_repo_path_or_basename_is_backed(self):
        self.invoked_setup()
        self.put(".githooks/pre-commit", "python tools/gate.py\n")
        self.assertEqual(self.counts(invocation_surfaces=[".githooks/*"])["backed"], 1)
        self.put(".githooks/pre-commit", "cd tools && python gate.py\n")
        self.assertEqual(self.counts(invocation_surfaces=[".githooks/*"])["backed"], 1)
        self.put(".githooks/pre-commit", "python tools/gate.pyc and xgate.py\n")      # near-misses are not references
        self.assertEqual(self.counts(invocation_surfaces=[".githooks/*"])["backed"], 0)

    def test_a_reference_outside_every_surface_does_not_count(self):
        self.invoked_setup()
        self.put("NOTES.md", "run tools/gate.py sometimes\n")
        self.assertEqual(self.counts(invocation_surfaces=[".githooks/*"])["uninvoked"], 1)
        self.put(".github/workflows/ci.yml", "run: python tools/gate.py\n")
        self.assertEqual(self.counts(invocation_surfaces=[".githooks/*", ".github/workflows/*.yml"])["backed"], 1)

    def test_enforcer_never_invokes_itself_and_excluded_surfaces_are_ignored(self):
        self.invoked_setup()
        self.put("tools/gate.py", "# usage: tools/gate.py\n")
        self.assertEqual(self.counts(invocation_surfaces=["tools/*.py"])["uninvoked"], 1)
        self.put(".githooks/pre-commit.frozen-20260905", "python tools/gate.py\n")
        self.assertEqual(self.counts(invocation_surfaces=[".githooks/*"])["uninvoked"], 0)
        self.assertEqual(self.counts(invocation_surfaces=[".githooks/*"], invocation_exclude=["*.frozen-*"])["uninvoked"], 1)

    def test_placement_invoked_enforcer_counts_without_a_reference(self):
        self.invoked_setup(".githooks/pre-commit")
        self.put(".githooks/pre-commit", "#!/bin/sh\nexit 0\n")
        self.assertEqual(self.counts(invocation_surfaces=[".githooks/*"])["uninvoked"], 1)
        self.assertEqual(self.counts(invocation_surfaces=[".githooks/*"], placement_invoked=[".githooks/pre-commit"])["backed"], 1)

    def test_no_surfaces_configured_behaves_as_before_and_says_unchecked(self):
        self.invoked_setup("tools/orphan.py")
        rc, out, _ = self.run_cli("--report")
        self.assertIn("INVOCATION UNCHECKED p:", out)
        self.assertEqual(self.counts()["backed"], 1)       # existence alone backs it, as in v1
        rc, out, _ = self.run_cli("--report", invocation_surfaces=[".githooks/*"])
        self.assertNotIn("INVOCATION UNCHECKED", out)

    def test_require_invoked_modes_for_inline_tags(self):
        self.doc("## Rules\n- a [enforced: tools/orphan.py]\n")
        surf = {"invocation_surfaces": [".githooks/*"], "rule_map": None}
        self.assertEqual(self.counts(**surf)["backed"], 1)                    # default: map entries only
        self.assertEqual(self.counts("--require-invoked", "all", **surf)["uninvoked"], 1)
        self.assertEqual(self.counts("--require-invoked", **surf)["uninvoked"], 1)   # bare flag = all
        self.assertEqual(self.counts("--require-invoked", "off", **surf)["backed"], 1)

    def test_require_invoked_off_also_lifts_map_entries(self):
        self.invoked_setup("tools/orphan.py")
        self.assertEqual(self.counts(invocation_surfaces=[".githooks/*"])["uninvoked"], 1)
        self.assertEqual(self.counts("--require-invoked", "off", invocation_surfaces=[".githooks/*"])["backed"], 1)

    # ---- rising floor
    FLOORS = [{"date": "2026-10-16", "backed": 1}, {"date": "2026-10-23", "backed": 2}, {"date": "2026-11-06", "backed": 3}]

    def floor_case(self, today, backed_rules):
        self.doc("## Rules\n" + "".join(f"- r{i} [enforced: tools/gate.py]\n" for i in range(backed_rules)) + "- p [prose]\n")
        return self.run_cli("--check", "--today", today, rule_map=None, floor_schedule=self.FLOORS)

    def test_floor_fails_below_and_passes_at_or_above(self):
        rc, out, _ = self.floor_case("2026-10-23", 1)               # floor 2, have 1
        self.assertEqual(rc, 1, out)
        self.assertIn("BELOW FLOOR", out)
        rc, out, _ = self.floor_case("2026-10-23", 2)               # at the floor
        self.assertEqual(rc, 0, out)
        self.assertIn("floor p: required 2 backed (since 2026-10-23), have 2: OK", out)
        rc, out, _ = self.floor_case("2026-10-23", 3)               # above
        self.assertEqual(rc, 0, out)

    def test_floor_uses_the_latest_due_entry_and_prints_the_next(self):
        rc, out, _ = self.floor_case("2026-10-22", 1)               # the 10-23 floor is not yet due
        self.assertEqual(rc, 0, out)
        self.assertIn("next floor 2 backed on 2026-10-23", out)
        rc, out, _ = self.floor_case("2026-12-01", 2)               # past the last: 3 required, no later floor
        self.assertEqual(rc, 1, out)
        self.assertIn("required 3 backed (since 2026-11-06)", out)
        self.assertIn("no later floor", out)

    def test_floor_before_the_first_date_requires_nothing(self):
        rc, out, _ = self.floor_case("2026-10-01", 0)
        self.assertEqual(rc, 0, out)
        self.assertIn("required none due yet", out)

    def test_floor_is_enforced_only_by_check_and_report_never_fails(self):
        self.doc("## Rules\n- p [prose]\n")
        self.assertEqual(self.run_cli("--today", "2026-12-01", rule_map=None, floor_schedule=self.FLOORS)[0], 0)      # default mode ignores the floor
        self.assertEqual(self.run_cli("--check", "--report", "--today", "2026-12-01", rule_map=None, floor_schedule=self.FLOORS)[0], 0)
        self.assertEqual(self.run_cli("--check", "--today", "2026-12-01", rule_map=None, floor_schedule=self.FLOORS)[0], 1)

    def test_check_still_fails_on_dangling_and_bad_today_or_schedule_is_exit_2(self):
        self.doc("## Rules\n- a [enforced: tools/gone.py]\n")
        self.assertEqual(self.run_cli("--check", rule_map=None)[0], 1)
        self.assertEqual(self.run_cli("--check", "--today", "soon", rule_map=None)[0], 2)
        self.assertEqual(self.run_cli("--check", rule_map=None, floor_schedule=[{"date": "x", "backed": 1}])[0], 2)

    # ---- emit-map, root candidates, DNG entry
    def test_emit_map_writes_every_rule_as_prose_and_round_trips(self):
        outp = os.path.join(self.tmp, "emitted.json")
        rc, out, _ = self.run_cli("--emit-map", outp)
        self.assertEqual(rc, 0, out)
        doc = json.load(open(outp, encoding="utf-8"))
        self.assertEqual(doc["schema"], "rule-map.v1")
        self.assertEqual(len(doc["rules"]), 4)
        self.assertEqual({e["kind"] for e in doc["rules"].values()}, {"prose"})
        beta = doc["rules"][self.rid("**Beta.** A reviewer decides this one.")]
        self.assertEqual((beta["source"], beta["line_hint"], beta["text_head"]), ("RULES.md", 6, "**Beta.** A reviewer decides this one."))
        c = self.counts("--rule-map", outp)
        self.assertEqual((c["prose"], c["untagged"]), (4, 0))

    def test_emit_map_to_stdout_and_needs_one_project(self):
        rc, out, _ = self.run_cli("--emit-map")
        self.assertEqual(json.loads(out)["schema"], "rule-map.v1")
        rc, _, err = self.run_cli("--emit-map", "--project", "nope")
        self.assertEqual(rc, 2)

    def test_text_head_is_at_most_60_chars(self):
        self.doc("## Rules\n- " + "x" * 200 + "\n")
        out = os.path.join(self.tmp, "e.json")
        self.run_cli("--emit-map", out)
        self.assertEqual([len(e["text_head"]) for e in json.load(open(out, encoding="utf-8"))["rules"].values()], [60])

    def test_root_candidates_first_existing_wins_and_relative_resolves_against_the_bus(self):
        bus = os.path.join(self.tmp, "bus")
        os.makedirs(os.path.join(bus, "tools"))
        sib = os.path.join(self.tmp, "sibling")
        shutil.copytree(self.root, sib)
        cfgp = os.path.join(bus, "tools", "c.json")
        proj = dict(self.proj, root=os.path.join(self.tmp, "absent"),
                    root_candidates=[os.path.join(self.tmp, "absent2"), "../sibling"], rule_map=None)
        with open(cfgp, "w", encoding="utf-8") as fh:
            json.dump({"schema": crt.SCHEMA, "projects": [proj]}, fh)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(crt.main(["--config", cfgp, "--report", "--json"]), 0)
        self.assertEqual(os.path.realpath(json.loads(out.getvalue())["root"]), os.path.realpath(sib))
        proj["root_candidates"] = [os.path.join(self.tmp, "absent2")]
        with open(cfgp, "w", encoding="utf-8") as fh:
            json.dump({"schema": crt.SCHEMA, "projects": [proj]}, fh)
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(crt.main(["--config", cfgp, "--report"]), 2)

    def test_shipped_dng_entry_matches_the_spec_and_its_regex_takes_bold_numbered_and_dash_units(self):
        cfg = crt.load_config(str(HERE / "rule-tags.config.json"))
        dng = next(p for p in cfg["projects"] if p["name"] == "dng-auto-processor")
        self.assertEqual([f["path"] for f in dng["files"]], ["docs/14-ORCHESTRATION.md", "AGENTS.md"])
        self.assertEqual(dng["rule_map"], "factory/rule-map.json")
        self.assertIn("C:/code/DngAutoProcessor - Claude/DngAutoProcessor", dng["root_candidates"])
        self.assertEqual(dng["invocation_surfaces"],
                         [".githooks/*", ".github/workflows/*.yml", "DngAutoProcessor.Tests/**/*.cs", "tools/**/*.tests.*"])
        self.assertEqual([(f["date"], f["backed"]) for f in dng["floor_schedule"]],
                         [("2026-10-16", 3), ("2026-10-23", 20), ("2026-10-30", 35), ("2026-11-06", 46)])
        self.doc("- dash\n1. numbered\n**Bold-led.** paragraph\nnot a rule\n\nplain\n")
        c = self.counts(rule_map=None, files=[{"path": "RULES.md", "bullet": dng["files"][0]["bullet"]}])
        self.assertEqual(c["bullets"], 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
