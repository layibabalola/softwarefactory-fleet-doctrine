import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = (
    ROOT / ".github" / "workflows" / "fleet-usage-control.yml",
    ROOT / ".github" / "workflows" / "provider-capacity-governor.yml",
    ROOT / ".github" / "workflows" / "adoption-ledger.yml",
)

# Path-scoping is a rule about EVERY automatically-triggered workflow, but the matrix assertions
# above are specific to the three that share the conditional-matrix shape. Keeping one tuple for
# both made the rule's domain accidentally equal to the matrix's domain, and
# `disposition-intake.yml` -- which has a plain matrix and so was never added here -- sat outside
# the only test enforcing path-scoping while becoming 93 of the last 100 runs and roughly $100 of a
# $124 monthly bill. The guard was not wrong; its domain was narrower than the rule it encoded.
PATH_SCOPED_WORKFLOWS = WORKFLOWS + (
    ROOT / ".github" / "workflows" / "disposition-intake.yml",
)
MATRIX_RE = re.compile(
    r"matrix: \$\{\{ fromJSON\(github\.event_name == 'pull_request' && "
    r"'(?P<pr>\{.*?\})' \|\| '(?P<landing>\{.*?\})'\) \}\}"
)


class CiCostContainmentTests(unittest.TestCase):
    def test_pr_and_landing_matrices_are_exact(self):
        expected_pr = {"os": ["ubuntu-latest"], "python-version": ["3.14"]}
        expected_landing = {
            "os": ["windows-latest", "ubuntu-latest"],
            "python-version": ["3.13", "3.14"],
        }
        for path in WORKFLOWS:
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                match = MATRIX_RE.search(text)
                self.assertIsNotNone(match)
                self.assertEqual(json.loads(match.group("pr")), expected_pr)
                self.assertEqual(json.loads(match.group("landing")), expected_landing)

    def test_every_workflow_cancels_superseded_work(self):
        for path in WORKFLOWS:
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertIn("cancel-in-progress: true", text)
                self.assertIn("workflow_dispatch:", text)

    def test_automatic_pr_and_master_events_are_path_scoped(self):
        """Both `paths:` and `paths-ignore:` scope a trigger; the rule is that one of them exists.

        An allowlist is right where a workflow's inputs are enumerable. An ignore list is right
        where they are not -- it fails safe, skipping only when every changed file matches, so an
        unlisted path still runs the gate rather than silently bypassing it.
        """
        for path in PATH_SCOPED_WORKFLOWS:
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertRegex(text, r"(?ms)^  pull_request:\s+paths(-ignore)?:")
                self.assertRegex(
                    text,
                    r"(?ms)^  push:\s+branches: \[master\]\s+paths(-ignore)?:",
                )

    def test_each_workflow_change_revalidates_its_own_contract(self):
        for path in WORKFLOWS:
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                expected = f'      - ".github/workflows/{path.name}"'
                self.assertGreaterEqual(text.count(expected), 2)


if __name__ == "__main__":
    unittest.main()
