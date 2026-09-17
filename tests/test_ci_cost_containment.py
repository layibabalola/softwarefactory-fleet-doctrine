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
        for path in WORKFLOWS:
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertRegex(text, r"(?ms)^  pull_request:\s+paths:")
                self.assertRegex(
                    text,
                    r"(?ms)^  push:\s+branches: \[master\]\s+paths:",
                )

    def test_each_workflow_change_revalidates_its_own_contract(self):
        for path in WORKFLOWS:
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                expected = f'      - ".github/workflows/{path.name}"'
                self.assertGreaterEqual(text.count(expected), 2)


if __name__ == "__main__":
    unittest.main()
