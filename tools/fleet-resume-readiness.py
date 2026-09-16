#!/usr/bin/env python
"""Derive whether the fleet actually has automatic resume prep, per roster member.

The owner's requirement is that resume prep is "fully implemented and tested and the entire fleet
is using it." Nothing on this bus could answer the last clause. `specs/pre-rotation-proof-and-
resume-dispatcher.md` carries the pattern as PROPOSED, and a proposal adopted by nobody is
indistinguishable from one adopted by everybody for as long as nothing counts. This tool counts.

It is the same construction as `tools/kernel-e2e.py`, applied to a different hole. That tool exists
because `harvest-status.py` enumerates filings that EXIST, so a member who never filed is invisible
to it -- which is how the steward's own filing sat three harvests unrouted. Adoption has the same
shape: a member that never installed the hook writes no checkpoint, and a survey that reads
checkpoints alone therefore cannot see it. So the roster comes from the kernel's §6 mapping and the
observations are subtracted from it, never the other way round.

FOUR EVIDENCE LAYERS, NEVER COLLAPSED. The fleet's standing rule is that capability, configuration,
enabled state and terminal execution are four different facts (kernel K4, RULINGS R6). For resume
prep they are:

    1 TOOL        a checkpoint script exists in the member's tree
    2 WIRED       its .claude/settings.json declares a Stop hook that invokes that script
    3 FIRING      a checkpoint file exists for that repo under the machine-local checkpoint root
    4 FRESH       the newest such checkpoint is younger than --max-age-hours

A member can satisfy 1 and 2 and still never have fired; that reads NOT-FIRING, not READY. This is
the distinction that let Conjugal believe for nine days that a hook named in its install prompt was
installed, while its newest checkpoint was four days stale.

REACHABILITY IS NOT COMPLIANCE. This bus is machine-local, and most roster members are not checked
out on any one host. A member whose working copy cannot be found is UNREACHABLE. It is never
counted as ready, and never counted as failing either, because absence of a checkout is not
evidence about adoption (K4: never exit code, output size or silence). Paths come from
`manifests/fleet-repo-paths.json` when present; a member absent from that map is UNREACHABLE and
says so, rather than being guessed at by scanning for a similar directory name.

Writes nothing. Exits 1 while any REACHABLE member is not READY, so a board can wire it into a
cycle it already runs. A reporter that always exits 0 is a warning, and a guard that warns has
failed open.

    python tools/fleet-resume-readiness.py
    python tools/fleet-resume-readiness.py --json
"""
import argparse
import io
import json
import os
import re
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KERNEL = os.path.join(ROOT, "specs", "fleet-factory-kernel.md")
PATHMAP = os.path.join(ROOT, "manifests", "fleet-repo-paths.json")

# Where the install prompt's project table puts the script, per repo shape.
SCRIPT_CANDIDATES = [
    "coordination/tools/session-checkpoint.py",
    "tools/hooks/session-checkpoint.py",
    "tools/roadmap/session-checkpoint.py",
    "tools/session-checkpoint.py",
]
SETTINGS = ".claude/settings.json"
DEFAULT_MAX_AGE_HOURS = 72
CHECKPOINT_PREFIX = "SESSION-"
CHECKPOINT_SUFFIX = ".md"
# Session ids reserved for proving a fresh install's wiring resolves. A checkpoint carrying one is
# evidence about the INSTALL, never about the host actually calling the hook, and the two must not
# be reported as the same thing.
INSTALL_SESSION_IDS = ("WIRECHECK", "INSTALLPROOF")

READY = "READY"
INSTALL_VERIFIED = "INSTALL-VERIFIED"
STALE = "STALE"
NOT_FIRING = "NOT-FIRING"
NOT_WIRED = "NOT-WIRED"
ABSENT = "ABSENT"
UNREACHABLE = "UNREACHABLE"

# Ordered worst-first, so a summary line leads with the thing worth acting on.
SEVERITY = [ABSENT, NOT_WIRED, NOT_FIRING, STALE, INSTALL_VERIFIED, READY, UNREACHABLE]


class Refused(SystemExit):
    def __init__(self, msg):
        sys.stderr.write("REFUSE fleet-resume-readiness: " + msg + "\n")
        SystemExit.__init__(self, 2)


def roster():
    """Projects from the kernel's §6 fleet mapping.

    Reads the SECTION, never spec filenames: topic documents on this bus are not projects, and
    taking a roster from filenames is what once made 30 of 30 members read as delinquent.
    """
    if not os.path.isfile(KERNEL):
        raise Refused("kernel spec not found at " + KERNEL)
    text = io.open(KERNEL, encoding="utf-8").read()
    m = re.search(r"^## 6\. Fleet mapping.*?(?=^## 7)", text, re.S | re.M)
    if not m:
        raise Refused("no '## 6. Fleet mapping' section; refusing to guess the roster")
    names = []
    for line in m.group(0).splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2 or not cells[0] or cells[0].startswith("---"):
            continue
        if cells[0].lower() == "project":
            continue
        # §6 annotates some rows, e.g. "name (no bus spec yet; mapped from ...)".
        name = cells[0].split("(")[0].strip().strip("`")
        if name:
            names.append(name)
    if not names:
        raise Refused("§6 parsed to an empty roster; refusing to report a clean fleet")
    return names


def path_map():
    """Member -> working copy path. Absent members are UNREACHABLE, never guessed."""
    if not os.path.isfile(PATHMAP):
        return {}
    try:
        data = json.load(io.open(PATHMAP, encoding="utf-8"))
    except Exception as exc:
        raise Refused("could not read " + PATHMAP + ": " + str(exc))
    repos = data.get("repos", data)
    if not isinstance(repos, dict):
        raise Refused(PATHMAP + " must map member -> path")
    return repos


def checkpoint_root():
    return os.path.join(os.path.expanduser("~"), ".claude", "session-checkpoints")


def checkpoint_is_for(path, repo_path):
    """True when this checkpoint was written FOR this checkout, not merely filed under its name.

    The checkpoint root is keyed on a repository's DIRECTORY BASENAME, so two checkouts that happen
    to share one -- entirely ordinary on a machine full of worktrees and clones -- write into the
    same folder. A member whose hook is broken then reads READY by borrowing its neighbour's
    checkpoint (found by the independent acceptance key, 2026-09-16). The checkpoint records the
    absolute repo path it describes, so bind to that and the collision stops mattering.
    """
    try:
        text = io.open(path, encoding="utf-8", errors="replace").read(4096)
    except Exception:
        return False
    want = os.path.normcase(os.path.abspath(repo_path).replace("\\", "/").rstrip("/"))
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- repo:"):
            got = stripped.split(":", 1)[1].strip().replace("\\", "/").rstrip("/")
            return os.path.normcase(got) == want
    return False        # a checkpoint that does not say what it describes is not evidence


def newest_checkpoint_age_hours(repo_path):
    """(age_hours, provenance) for the newest real checkpoint, or (None, None) if none exists.

    Checkpoints are filed under the MAIN repo's directory name, so the lookup key is that name and
    not the member's roster name -- the two differ wherever a repo is checked out under a directory
    that is not its project name, which is the common case on this machine.

    TWO CORRECTIONS from the independent acceptance key, 2026-09-16, both of which had produced a
    FALSE GREEN:

    1. ONLY files matching the checkpoint naming convention count. Previously any file in the
       directory did, so a member whose hook exits 17 while an unrelated text file happens to sit
       in its checkpoint folder read READY. Trusting the hook's OUTPUT rather than its source text
       is what closes that: a broken script cannot write a real checkpoint, so requiring one is a
       stronger test than reading the script and hoping.

    2. Checkpoints written by INSTALL VERIFICATION are distinguished from checkpoints written by a
       real session ending. Verifying the configured command proves the wiring resolves; it does
       not prove the host calls it. Those are the two different facts this tool exists to keep
       apart, and collapsing them here would have been the same defect it reports on others.
    """
    name = os.path.basename(os.path.abspath(repo_path).rstrip("\\/"))
    for candidate in (name, name.replace(" ", "-")):
        d = os.path.join(checkpoint_root(), candidate)
        if not os.path.isdir(d):
            continue
        newest, provenance = None, None
        for entry in os.listdir(d):
            full = os.path.join(d, entry)
            if not os.path.isfile(full):
                continue
            if not (entry.startswith(CHECKPOINT_PREFIX) and entry.endswith(CHECKPOINT_SUFFIX)):
                continue        # not a checkpoint; an unrelated file is not evidence of firing
            if not checkpoint_is_for(full, repo_path):
                continue        # written for a DIFFERENT checkout that shares this basename
            session = entry[len(CHECKPOINT_PREFIX):-len(CHECKPOINT_SUFFIX)]
            kind = "install" if session.upper() in INSTALL_SESSION_IDS else "session"
            try:
                mtime = os.path.getmtime(full)
            except OSError:
                continue
            # A real session's checkpoint outranks an install-verification one regardless of age:
            # it is the stronger evidence, and the newest install stamp must not mask it.
            better = (newest is None
                      or (kind == "session" and provenance == "install")
                      or (kind == provenance and mtime > newest))
            if better:
                newest, provenance = mtime, kind
        if newest is not None:
            return max(0.0, (time.time() - newest) / 3600.0), provenance
    return None, None


def stop_hook_scripts(repo_path):
    """Every in-tree script a declared Stop hook actually invokes, resolved to a real path.

    The command string is the authority on what runs, so the script path is taken FROM it rather
    than guessed. Anything the command names that does not exist in the tree is skipped: a hook
    pointing at a missing file is not a capability.
    """
    settings = os.path.join(repo_path, SETTINGS)
    if not os.path.isfile(settings):
        return []
    try:
        data = json.load(io.open(settings, encoding="utf-8"))
    except Exception:
        return []
    # Configuration and ENABLED STATE are different facts (R6), and this switch turns every hook
    # in the project off while leaving the declaration in place -- so a survey reading only the
    # declaration reports a hook that provably cannot run (found by the key, 2026-09-16).
    if data.get("disableAllHooks") is True:
        return []
    found = []
    for group in (data.get("hooks") or {}).get("Stop") or []:
        for hook in (group or {}).get("hooks", []):
            command = str((hook or {}).get("command", ""))
            for token in re.findall(r"[^\s\"']+\.py", command):
                rel = token.replace("\\", "/")
                # Hook commands address the repo through a launcher variable; strip it to get a
                # tree-relative path.
                rel = re.sub(r"^\$?\{?CLAUDE_PROJECT_DIR\}?/?", "", rel)
                rel = re.sub(r"^%CLAUDE_PROJECT_DIR%/?", "", rel)
                full = os.path.join(repo_path, rel)
                if os.path.isfile(full):
                    found.append((rel, full))
    return found


def is_checkpoint_script(full_path):
    """A checkpoint script is one that writes into the checkpoint root -- a CAPABILITY, not a name.

    Members implement this doctrine under different filenames: Conjugal's is
    `coordination/tools/session-checkpoint.py`, Cloudvore's is `tools/rotation-ready.py --hook`.
    A survey keyed on the filename reports the second as ABSENT while it is in fact firing, which
    is a false negative that would understate adoption and send someone to install a duplicate.
    Detect the behaviour instead: the script names the shared checkpoint directory.
    """
    try:
        text = io.open(full_path, encoding="utf-8", errors="replace").read()
    except Exception:
        return False
    return "session-checkpoints" in text


def assess(member, repo_path, max_age_hours):
    if not repo_path:
        return UNREACHABLE, "no path recorded in manifests/fleet-repo-paths.json"
    if not os.path.isdir(repo_path):
        return UNREACHABLE, "not checked out on this machine: " + repo_path
    # Layers 1 and 2 together: a Stop hook that invokes an in-tree script which can checkpoint.
    wired_rel = None
    for rel, full in stop_hook_scripts(repo_path):
        if is_checkpoint_script(full):
            wired_rel = rel
            break
    if wired_rel is None:
        # Distinguish "never installed" from "installed but not wired". They need different
        # actions, so reporting both as one state would make the remedy a guess.
        present = [c for c in SCRIPT_CANDIDATES
                   if os.path.isfile(os.path.join(repo_path, c))
                   and is_checkpoint_script(os.path.join(repo_path, c))]
        if present:
            return NOT_WIRED, present[0] + " exists but no Stop hook invokes it"
        return ABSENT, "no Stop hook invokes a checkpoint-capable script in this tree"
    script_rel = wired_rel
    age, provenance = newest_checkpoint_age_hours(repo_path)
    if age is None:
        return NOT_FIRING, "wired at " + script_rel + " but no checkpoint has ever been written"
    if provenance == "install":
        # Deliberately NOT ready. The install was verified; the host has not been observed calling
        # the hook. Converts to READY on its own the first time a real session ends here.
        return (INSTALL_VERIFIED,
                "wiring verified at " + script_rel + " (%.1f h ago) but no REAL session has "
                "written a checkpoint yet; a verified command is not an observed call" % age)
    if age > max_age_hours:
        return STALE, "newest checkpoint is %.1f h old (limit %g h)" % (age, max_age_hours)
    return READY, "newest checkpoint %.1f h old" % age


def main(argv=None):
    ap = argparse.ArgumentParser(description="Derive fleet resume-prep readiness from §6.")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--max-age-hours", type=float, default=DEFAULT_MAX_AGE_HOURS,
                    help="a checkpoint older than this reads STALE (default %d)"
                         % DEFAULT_MAX_AGE_HOURS)
    args = ap.parse_args(argv)

    members = roster()
    paths = path_map()
    rows = []
    for member in members:
        repo_path = paths.get(member)
        state, detail = assess(member, repo_path, args.max_age_hours)
        rows.append({"member": member, "path": repo_path or "",
                     "state": state, "detail": detail})

    reachable = [r for r in rows if r["state"] != UNREACHABLE]
    ready = [r for r in reachable if r["state"] == READY]
    failing = [r for r in reachable if r["state"] != READY]

    if args.json:
        json.dump({
            "roster": len(rows),
            "reachable": len(reachable),
            "ready": len(ready),
            "failing": len(failing),
            "max_age_hours": args.max_age_hours,
            "rows": rows,
        }, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
    else:
        print("fleet resume-prep readiness, derived from kernel §6")
        print("  roster %d | reachable %d | READY %d | not ready %d"
              % (len(rows), len(reachable), len(ready), len(failing)))
        print("  a member not checked out here is UNREACHABLE: absence of a checkout is not")
        print("  evidence of adoption, and is never counted as ready.")
        print("")
        order = dict((s, i) for i, s in enumerate(SEVERITY))
        for r in sorted(rows, key=lambda r: (order.get(r["state"], 99), r["member"])):
            print("  %-28s %-12s %s" % (r["member"], r["state"], r["detail"]))
        print("")
        print("VERDICT: " + ("ALL REACHABLE MEMBERS READY" if not failing
                             else "%d REACHABLE MEMBER(S) NOT READY" % len(failing)))
    return 1 if failing else 0


if __name__ == "__main__":
    sys.exit(main())
