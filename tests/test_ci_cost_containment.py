import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_DIR = ROOT / ".github" / "workflows"
# Derived from disk, never hand-listed. A hand-maintained tuple once omitted
# .github/workflows/disposition-intake.yml, which made the path-scoping rule's
# domain accidentally equal to the matrix rule's domain: the one workflow that
# violated path scoping was the one excluded from the test that enforces it.
ALL_WORKFLOWS = tuple(sorted(WORKFLOW_DIR.glob("*.yml")))

# The trimmed pull-request matrix is a cost control for workflows that run one.
# Exemptions are named, justified and checked to exist.
MATRIX_EXEMPT = {
    # Sealed by the R26 intake epoch; CI-COST-CONTROL.md grants it the full
    # four-job matrix because it is the fleet's integrity gate.
    "disposition-intake.yml",
    # A single trivial offline Node job; it declares no matrix at all.
    "doctrine-sync.yml",
}

MATRIX_RE = re.compile(
    r"matrix: \$\{\{ fromJSON\(github\.event_name == 'pull_request' && "
    r"'(?P<pr>\{.*?\})' \|\| '(?P<landing>\{.*?\})'\) \}\}"
)
PR_SCOPED_RE = re.compile(r"(?ms)^  pull_request:\s+paths(-ignore)?:")
PUSH_SCOPED_RE = re.compile(r"(?ms)^  push:\s+branches: \[master\]\s+paths(-ignore)?:")


def _text(path):
    return path.read_text(encoding="utf-8")


def _auto_triggered(path):
    text = _text(path)
    return bool(re.search(r"(?m)^  (pull_request|push):", text))


def _uses_allowlist(path):
    # paths: admits only what it lists; paths-ignore: runs on everything else.
    return bool(re.search(r"(?m)^    paths:", _text(path)))


class CiCostContainmentTests(unittest.TestCase):
    def test_workflow_set_is_discovered_and_exemptions_still_exist(self):
        self.assertTrue(ALL_WORKFLOWS, "no workflows discovered")
        names = {path.name for path in ALL_WORKFLOWS}
        # A renamed or deleted workflow must not carry its exemption forward.
        self.assertLessEqual(MATRIX_EXEMPT, names)

    def test_pr_and_landing_matrices_are_exact(self):
        expected_pr = {"os": ["ubuntu-latest"], "python-version": ["3.14"]}
        expected_landing = {
            "os": ["windows-latest", "ubuntu-latest"],
            "python-version": ["3.13", "3.14"],
        }
        for path in ALL_WORKFLOWS:
            if path.name in MATRIX_EXEMPT:
                continue
            with self.subTest(path=path.name):
                match = MATRIX_RE.search(_text(path))
                self.assertIsNotNone(match)
                self.assertEqual(json.loads(match.group("pr")), expected_pr)
                self.assertEqual(json.loads(match.group("landing")), expected_landing)

    def test_every_workflow_cancels_superseded_work(self):
        for path in ALL_WORKFLOWS:
            with self.subTest(path=path.name):
                text = _text(path)
                self.assertIn("cancel-in-progress: true", text)
                self.assertIn("workflow_dispatch:", text)

    def test_automatic_pr_and_master_events_are_path_scoped(self):
        # Every automatically triggered workflow states which changes concern
        # it, by allowlist or by ignore list. Without this the R26 gate ran on
        # all 100 of its last 100 runs, 93 of them for commits it never reads.
        for path in ALL_WORKFLOWS:
            if not _auto_triggered(path):
                continue
            with self.subTest(path=path.name):
                text = _text(path)
                self.assertRegex(text, PR_SCOPED_RE)
                self.assertRegex(text, PUSH_SCOPED_RE)

    def test_each_workflow_change_revalidates_its_own_contract(self):
        for path in ALL_WORKFLOWS:
            if not _auto_triggered(path):
                continue
            with self.subTest(path=path.name):
                text = _text(path)
                listed = re.compile(
                    r"""(?m)^ {6}- ["']\.github/workflows/"""
                    + re.escape(path.name)
                    + r"""["']$"""
                )
                if _uses_allowlist(path):
                    # Named on both triggers, so editing it re-runs it.
                    self.assertGreaterEqual(len(listed.findall(text)), 2)
                else:
                    # An ignore list must never ignore the workflow itself,
                    # or a change to it would land unvalidated.
                    self.assertEqual(listed.findall(text), [])


if __name__ == "__main__":
    unittest.main()
