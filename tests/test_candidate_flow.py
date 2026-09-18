"""candidate-flow is an ALARM: it must never gate, and never write."""
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "candidate-flow.py"


def run():
    return subprocess.run([sys.executable, str(TOOL)], capture_output=True, text=True,
                          timeout=300, check=False, cwd=str(ROOT))


class CandidateFlowIsAnAlarmTests(unittest.TestCase):
    def test_exits_zero_even_with_a_deep_queue(self):
        # The whole point: a backlog is reported, never enforced. If this ever returns non-zero
        # the tool has become a gate and specs/mlv-app.md:372 applies -- withdraw it as a gate,
        # retain it as an alarm.
        self.assertEqual(run().returncode, 0)

    def test_reports_the_real_queue_and_says_it_is_an_alarm(self):
        out = run().stdout
        depth = len(list((ROOT / "ruling-candidates").glob("*.md")))
        self.assertIn("{} candidates".format(depth), out)
        self.assertIn("ALARM ONLY", out)
        self.assertIn("ever removed", out)

    def test_writes_nothing(self):
        def status():
            return subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain"],
                                  capture_output=True, text=True, check=False).stdout
        before = status()
        run()
        self.assertEqual(before, status())


if __name__ == "__main__":
    unittest.main()
