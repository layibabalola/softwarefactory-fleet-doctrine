"""candidate-flow is an ALARM: it must never gate, and never write."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOL = ROOT / "tools" / "candidate-flow.py"


def _run():
    return subprocess.run(
        [sys.executable, str(TOOL)],
        capture_output=True, text=True, timeout=180, check=False, cwd=str(ROOT),
    )


def test_exits_zero_even_with_a_deep_queue():
    # The whole point: a backlog is reported, never enforced. If this ever
    # returns non-zero the tool has become a gate and specs/mlv-app.md:372
    # applies -- withdraw it as a gate, retain it as an alarm.
    assert _run().returncode == 0


def test_reports_the_real_queue_and_says_it_is_an_alarm():
    out = _run().stdout
    depth = len(list((ROOT / "ruling-candidates").glob("*.md")))
    assert f"{depth} candidates" in out
    assert "ALARM ONLY" in out
    assert "ever removed" in out


def test_writes_nothing():
    before = subprocess.run(
        ["git", "-C", str(ROOT), "status", "--porcelain"],
        capture_output=True, text=True, check=False,
    ).stdout
    _run()
    after = subprocess.run(
        ["git", "-C", str(ROOT), "status", "--porcelain"],
        capture_output=True, text=True, check=False,
    ).stdout
    assert before == after
