#!/usr/bin/env python
"""Proof for tools/arbitration-queue.py.

The tool's value is that it ADDRESSES a duty rather than listing a shelf, so the test is mostly
about the four states it refuses to collapse and about the two false answers that matter:

  * telling a project it owes nothing when it owes something (the duty stays invisible, which is
    the state five harvests were already in);
  * telling a project it owes something that is actually answered, or that nobody assigned to it.

It also pins the refusal behaviour: an unparseable or empty ledger must REFUSE, never report an
empty queue, because "nothing owed" and "I could not read the ledger" are different facts.
"""
from __future__ import annotations

import importlib.util
import io
import json
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL = HERE / "arbitration-queue.py"

FAILURES = []


def check(label, condition, detail=""):
    if condition:
        print("  ok   " + label)
    else:
        print("  FAIL " + label + ((" -- " + detail) if detail else ""))
        FAILURES.append(label)


def load():
    spec = importlib.util.spec_from_file_location("arbitration_queue", TOOL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    io.open(path, "w", encoding="utf-8", newline="\n").write(text)


def filing(project):
    return ("# Factory-kernel dogfood filing -- " + project + "\n\n"
            "project: " + project + "\n"
            "kernel: fleet-factory-kernel r4\n")


LEDGER = """# Factory-kernel harvest ledger

| date | harvest | filing |
|---|---|---|

## Steward status -- test

**Arbiter named for `conjugal`, per K12 and section 5.**

- **PRIMARY: `airmypc`.** Its posture line reports a Codex key lane.
- **ALTERNATE: `dng-auto-processor`.** Named second.

**Arbiter named for `mlv-app`.**

- **PRIMARY: `cloudvore`.**
"""


def run_case(tmp):
    mod = load()
    root = tmp / "bus"
    fdir = root / "adjudications" / "factory-kernel"
    fdir.mkdir(parents=True, exist_ok=True)
    for p in ("conjugal", "airmypc", "mlv-app", "cloudvore", "adobe-ingester"):
        write(fdir / (p + ".md"), filing(p))
    # Not a filing: it sits in the directory but has no `project:` header.
    write(fdir / "README.md", "# How filings work\n\nSome prose.\n")
    write(fdir / "HARVESTS.md", LEDGER)

    mod.ROOT = str(root)
    mod.LEDGER = str(fdir / "HARVESTS.md")
    mod.FILINGS_DIR = str(fdir)
    mod._filings_on_review_branches = lambda: set()   # no git in this fixture

    print("case: README.md is not a filing, because a filing is known by its header")
    present = mod.filings_present()
    check("README is excluded", "readme" not in present, str(sorted(present)))
    check("real filings are included", "conjugal" in present, str(sorted(present)))

    print("case: the named arbiter is TOLD, and the tool refuses while it is owed")
    rc = mod.main(["airmypc", "--json"])
    check("exits non-zero while a filing is owed", rc == 1, "rc=" + str(rc))
    owed = [r for r in mod.rows() if r["state"] == mod.OWED and r["arbiter"] == "airmypc"]
    check("conjugal is owed to airmypc", [r["filing"] for r in owed] == ["conjugal"], str(owed))

    print("case: a project owes nothing unless it was named")
    rc = mod.main(["adobe-ingester", "--json"])
    check("an unnamed project exits 0", rc == 0, "rc=" + str(rc))

    print("case: an answered filing is not owed to anyone")
    write(fdir / "conjugal.dispositions.md", "arbiter: airmypc\n")
    rc = mod.main(["airmypc", "--json"])
    check("a disposition clears the duty", rc == 0, "rc=" + str(rc))
    states = dict((r["filing"], r["state"]) for r in mod.rows())
    check("it reads ANSWERED, not OWED", states.get("conjugal") == mod.ANSWERED, str(states))
    os.remove(str(fdir / "conjugal.dispositions.md"))

    print("case: UNASSIGNED is the steward's move, and is not charged to a sibling")
    states = dict((r["filing"], r["state"]) for r in mod.rows())
    check("a filing with no naming reads UNASSIGNED",
          states.get("adobe-ingester") == mod.UNASSIGNED, str(states))
    check("it is not OWED to anybody", states.get("adobe-ingester") != mod.OWED, str(states))

    print("case: an arbiter named but never filed is flagged, not assumed workable")
    write(fdir / "HARVESTS.md", LEDGER.replace("`cloudvore`", "`ghostproject`"))
    rows = mod.rows()
    ghost = [r for r in rows if r["arbiter"] == "ghostproject"]
    check("reads UNREACHABLE-ARBITER",
          ghost and ghost[0]["state"] == mod.UNREACHABLE_ARBITER, str(ghost))
    check("and is therefore not counted as owed",
          all(r["state"] != mod.OWED for r in ghost), str(ghost))
    write(fdir / "HARVESTS.md", LEDGER)

    print("case: a LATER naming block supersedes an earlier one")
    write(fdir / "HARVESTS.md", LEDGER + """
## Steward status -- later

**Arbiter named for `conjugal`.**

- **PRIMARY: `cloudvore`.** Replaces the earlier naming.
""")
    named = mod.namings(io.open(str(fdir / "HARVESTS.md"), encoding="utf-8").read())
    check("the newest naming wins",
          named.get("conjugal") == [("PRIMARY", "cloudvore")], str(named.get("conjugal")))
    rc = mod.main(["airmypc", "--json"])
    check("the superseded arbiter no longer owes it", rc == 0, "rc=" + str(rc))
    write(fdir / "HARVESTS.md", LEDGER)

    print("case: a NON-EMPTY file that is not a ledger REFUSES (key defect D1)")
    write(fdir / "HARVESTS.md", "this is not a ledger\n")
    try:
        mod.rows()
        check("garbage that is merely non-empty refuses", False, "returned NOTHING OWED instead")
    except SystemExit as exc:
        check("garbage that is merely non-empty refuses", exc.code == 2, "exit=" + str(exc.code))
    write(fdir / "HARVESTS.md", LEDGER)

    print("case: a placeholder disposition does NOT clear the duty (key defect D3)")
    write(fdir / "conjugal.dispositions.md", "")
    rc = mod.main(["airmypc", "--json"])
    check("an empty dispositions file leaves the duty standing", rc == 1, "rc=" + str(rc))
    write(fdir / "conjugal.dispositions.md", "# TODO: rule on this\n")
    rc = mod.main(["airmypc", "--json"])
    check("a dispositions file with no arbiter line leaves the duty standing",
          rc == 1, "rc=" + str(rc))
    write(fdir / "conjugal.dispositions.md", "arbiter: airmypc\n")
    rc = mod.main(["airmypc", "--json"])
    check("a real disposition still clears it", rc == 0, "rc=" + str(rc))
    os.remove(str(fdir / "conjugal.dispositions.md"))

    print("case: a filing is found wherever its header sits, and a quoted example is not one (D4)")
    write(fdir / "latefiling.md", ("\n" * 45) + filing("latefiling"))
    write(fdir / "README.md",
          "# How filings work\n\nEvery filing opens like this:\n\n```\n"
          + filing("exampleproject") + "```\n")
    present = mod.filings_present()
    check("a header below line 40 is still a filing", "latefiling" in present, str(sorted(present)))
    check("a fenced example in the README is not a filing",
          "readme" not in present and "exampleproject" not in present, str(sorted(present)))
    os.remove(str(fdir / "latefiling.md"))
    write(fdir / "README.md", "# How filings work\n\nSome prose.\n")

    print("case: the documented UNDECORATED naming form is read (key defect D5)")
    plain = LEDGER.replace("- **PRIMARY: `airmypc`.**", "- PRIMARY: `airmypc`.")
    named = mod.namings(plain)
    check("an undecorated PRIMARY line still names an arbiter",
          ("PRIMARY", "airmypc") in named.get("conjugal", []), str(named.get("conjugal")))
    check("prose merely containing the word PRIMARY names nobody",
          mod.NAMING_RE.search("the primary reason: airmypc was busy") is None, "matched prose")

    print("case: precedence is the steward DATE, not file position (key defect D6)")
    dated = ("## Steward status -- 2026-09-16\n\n"
             "**Arbiter named for `conjugal`.**\n\n"
             "- **PRIMARY: `airmypc`.**\n\n"
             "## Steward status -- 2026-09-15\n\n"
             "**Arbiter named for `conjugal`.**\n\n"
             "- **PRIMARY: `cloudvore`.** Older block, appended last.\n")
    named = mod.namings(dated)
    check("an older block appended last does NOT override a newer one",
          named.get("conjugal") == [("PRIMARY", "airmypc")], str(named.get("conjugal")))
    named = mod.namings(dated.replace("2026-09-16", "2026-09-14"))
    check("and when the appended block IS the newer one, it wins",
          named.get("conjugal") == [("PRIMARY", "cloudvore")], str(named.get("conjugal")))

    print("case: a named filing the inventory cannot see is NOT silently dropped (key defect D2)")
    os.remove(str(fdir / "mlv-app.md"))
    rows = mod.rows()
    lost = [r for r in rows if r["filing"] == "mlv-app"]
    check("it appears as FILING-NOT-FOUND, not as nothing",
          lost and lost[0]["state"] == mod.FILING_NOT_FOUND, str(lost))
    rc = mod.main(["cloudvore", "--json"])
    check("and its named arbiter still gets a non-zero exit", rc == 1, "rc=" + str(rc))
    write(fdir / "mlv-app.md", filing("mlv-app"))

    print("case: an unreadable ledger REFUSES; it never reports an empty queue")
    write(fdir / "HARVESTS.md", "   \n")
    try:
        mod.rows()
        check("an empty ledger refuses", False, "returned instead of refusing")
    except SystemExit as exc:
        check("an empty ledger refuses", exc.code == 2, "exit=" + str(exc.code))
    os.remove(str(fdir / "HARVESTS.md"))
    try:
        mod.rows()
        check("a missing ledger refuses", False, "returned instead of refusing")
    except SystemExit as exc:
        check("a missing ledger refuses", exc.code == 2, "exit=" + str(exc.code))


def run_discovery_case(tmp):
    """Key defect D7: review-branch discovery was stubbed out in every case, so a mutation that
    disabled it entirely left the suite green. This case drives a REAL git repository.

    It also pins the failure direction that matters: when git cannot answer, the tool must REFUSE
    (exit 2). Returning an empty set made a broken instrument read as an absent duty, which is the
    one answer this tool exists to prevent.
    """
    import subprocess

    mod = load()
    root = tmp / "busrepo"
    fdir = root / "adjudications" / "factory-kernel"
    fdir.mkdir(parents=True, exist_ok=True)

    def git(*args):
        return subprocess.run(["git", "-C", str(root)] + list(args),
                              capture_output=True, text=True)

    if subprocess.run(["git", "--version"], capture_output=True).returncode != 0:
        check("git is available to test discovery", False, "git --version failed")
        return

    git("init", "-q")
    git("config", "user.email", "test@example.invalid")
    git("config", "user.name", "test")
    write(fdir / "onmaster.md", filing("onmaster"))
    write(fdir / "HARVESTS.md", LEDGER)
    git("add", "-A")
    git("commit", "-q", "-m", "master filing")
    git("checkout", "-q", "-b", "reviewbranch")
    write(fdir / "onreviewonly.md", filing("onreviewonly"))
    write(fdir / "README.md",
          "# not a filing\n\n```\n" + filing("quotedexample") + "```\n")
    git("add", "-A")
    git("commit", "-q", "-m", "review-branch filing")
    git("update-ref", "refs/remotes/origin/review/onreviewonly-kernel", "reviewbranch")
    git("checkout", "-q", "master")

    mod.ROOT = str(root)
    mod.LEDGER = str(fdir / "HARVESTS.md")
    mod.FILINGS_DIR = str(fdir)

    print("case: a filing on an unmerged review branch is still a filing (R7.5), proven on real git")
    found = mod._filings_on_review_branches()
    check("discovery finds a filing that exists only on origin/review/*",
          "onreviewonly" in found, str(sorted(found)))
    check("and does not admit a fenced example from that branch's README",
          "readme" not in found and "quotedexample" not in found, str(sorted(found)))
    check("the local filing is still present too",
          "onmaster" in mod.filings_present(), str(sorted(mod.filings_present())))

    print("case: discovery reads blobs BY OID, never as a combined <rev>:<path> argument")
    seen_args = []
    real_run_probe = subprocess.run

    def recording_run(cmd, *a, **kw):
        seen_args.append(list(cmd))
        return real_run_probe(cmd, *a, **kw)

    mod.subprocess.run = recording_run
    try:
        mod._filings_on_review_branches()
    finally:
        mod.subprocess.run = real_run_probe
    combined = [c for c in seen_args
                for arg in c if arg.startswith("refs/") and ":" in arg]
    check("no git call joins a ref and a path with a colon",
          not combined,
          "git stats that combined string and, on Windows under a deep checkout, aborts with "
          "ENAMETOOLONG -- every review-branch filing then reads as absent: " + str(combined[:1]))
    check("and the blob is fetched by object id instead",
          any("cat-file" in c and "blob" in c for c in seen_args),
          str(seen_args[-1] if seen_args else []))

    print("case: when git cannot answer, discovery REFUSES -- it never returns an empty set (D2)")
    mod.ROOT = str(tmp / "not-a-repo")
    (tmp / "not-a-repo").mkdir(parents=True, exist_ok=True)
    try:
        mod._filings_on_review_branches()
        check("a non-repository refuses", False, "returned instead of refusing")
    except SystemExit as exc:
        check("a non-repository refuses", exc.code == 2, "exit=" + str(exc.code))

    real_run = subprocess.run

    def exploding_run(*a, **kw):
        raise OSError("git is not on PATH")

    mod.ROOT = str(root)
    mod.subprocess.run = exploding_run
    try:
        mod._filings_on_review_branches()
        check("git missing from PATH refuses", False, "returned instead of refusing")
    except SystemExit as exc:
        check("git missing from PATH refuses", exc.code == 2, "exit=" + str(exc.code))
    finally:
        mod.subprocess.run = real_run


def main():
    if not TOOL.exists():
        print("FAIL: tool not found at " + str(TOOL))
        return 1
    with tempfile.TemporaryDirectory(prefix="arbitration-queue-test-") as raw:
        out = io.StringIO()
        real = sys.stdout
        try:
            sys.stdout = out
            run_case(Path(raw))
            run_discovery_case(Path(raw))
        finally:
            sys.stdout = real
        for line in out.getvalue().splitlines():
            if line.startswith("  ok ") or line.startswith("  FAIL") or line.startswith("case:"):
                print(line)
    if FAILURES:
        print("\nFAIL arbitration-queue: " + str(len(FAILURES)) + " check(s) failed")
        for f in FAILURES:
            print("  - " + f)
        return 1
    print("\nPASS arbitration-queue")
    return 0


if __name__ == "__main__":
    sys.exit(main())
