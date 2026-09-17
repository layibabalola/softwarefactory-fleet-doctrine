#!/usr/bin/env python3
"""Measure the ruling-candidate queue: arrivals vs services, and per-item age.

THIS IS AN ALARM, NOT A GATE. It always exits 0. It writes nothing, moves
nothing, and expires nothing -- disposing of a candidate is an owner act and
this tool has no opinion about it. The precedent is specs/mlv-app.md:372, where
a 1:1 closeout gate was "withdrawn as a gate, retained as an alarm" because a
blocking version was arbitrary and gameable.

Why it exists. `ruling-candidates/` records arrivals but not drains: the two
candidates that WERE dispositioned (RULINGS.md, 2026-09-08 and 2026-09-13) still
carry "PROPOSED ONLY -- NOT YET A RATIFIED RULING" in their own text. A queue
that does not record its own service is unfalsifiable from inside -- its depth
looks the same whether it is draining or drowning. Measured 2026-09-17: 33
candidates, 0 ever removed, ~2 ever ruled on. Arrival:service ~16:1.

Service is detected the only way that is falsifiable from here: the candidate's
slug appearing in RULINGS.md, which is where ratification is recorded. A
candidate the owner has never been asked to rule on is UNROUTED -- that is the
measured bottleneck, not owner latency. Both serviced candidates were ruled the
SAME DAY they were filed, so the decider is fast and rarely invoked.
"""
from __future__ import annotations

import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CANDIDATES = ROOT / "ruling-candidates"
RULINGS = ROOT / "RULINGS.md"
WINDOW_DAYS = 30


def _git(*args: str) -> str:
    try:
        return subprocess.run(
            ["git", "-C", str(ROOT), *args],
            capture_output=True, text=True, timeout=30, check=False,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def added_utc(path: Path) -> datetime | None:
    rel = path.relative_to(ROOT).as_posix()
    out = _git("log", "--diff-filter=A", "--follow", "--format=%aI", "--", rel)
    stamp = out.splitlines()[-1] if out else ""
    try:
        return datetime.fromisoformat(stamp).astimezone(timezone.utc)
    except ValueError:
        return None


def main() -> int:
    if not CANDIDATES.is_dir():
        print("candidate-flow: no ruling-candidates/ directory; nothing to measure.")
        return 0

    rulings = RULINGS.read_text(encoding="utf-8", errors="replace") if RULINGS.exists() else ""
    now = datetime.now(timezone.utc)
    rows = []
    for path in sorted(CANDIDATES.glob("*.md")):
        slug = path.stem
        when = added_utc(path)
        age = (now - when).days if when else None
        rows.append((slug, age, slug in rulings))

    if not rows:
        print("candidate-flow: queue is empty.")
        return 0

    # Drains: a candidate file that ever left the directory.
    removed = len([ln for ln in _git(
        "log", "--diff-filter=D", "--format=%H", "--name-only", "--", "ruling-candidates/"
    ).splitlines() if ln.startswith("ruling-candidates/")])

    arrivals = len([r for r in rows if r[1] is not None and r[1] <= WINDOW_DAYS])
    routed = [r for r in rows if r[2]]
    unrouted = [r for r in rows if not r[2]]
    oldest = max((r for r in rows if r[1] is not None), key=lambda r: r[1], default=None)

    print(f"queue            : {len(rows)} candidates in ruling-candidates/")
    print(f"arrivals/{WINDOW_DAYS}d     : {arrivals}")
    print(f"routed           : {len(routed)}  (slug cited in RULINGS.md)")
    print(f"unrouted         : {len(unrouted)}")
    print(f"ever removed     : {removed}")
    if oldest:
        print(f"oldest unserviced: {oldest[0]} ({oldest[1]}d)")
    if arrivals and len(routed):
        print(f"arrival:service  : {arrivals / max(len(routed), 1):.1f} : 1 over {WINDOW_DAYS}d")

    stale = sorted(
        (r for r in unrouted if r[1] is not None and r[1] > 7),
        key=lambda r: -r[1],
    )
    if stale:
        print(f"\nUNROUTED > 7d ({len(stale)}) -- nobody has been asked to rule on these:")
        for slug, age, _ in stale[:15]:
            print(f"  {age:4d}d  {slug}")
        if len(stale) > 15:
            print(f"  ... and {len(stale) - 15} more")

    print("\nALARM ONLY -- exit 0 by design. Routing a candidate is an owner act.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
