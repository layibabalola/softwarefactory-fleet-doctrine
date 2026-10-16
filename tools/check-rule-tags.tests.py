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


if __name__ == "__main__":
    unittest.main(verbosity=2)
