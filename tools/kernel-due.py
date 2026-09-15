#!/usr/bin/env python3
"""Which fleet members owe a kernel filing? Derived from refs and the roster, never from memory.

  kernel-due.py                     every member, one line each
  kernel-due.py --json              machine contract
  options: --subject <name>  --cadence-days N  --repo <path>  --no-fetch

WHY THIS EXISTS (measured 2026-09-15, adobe-ingester, VIRTUAL-TEN)

`harvest-status.py` answers "has every filing been harvested?" - it enumerates filings that EXIST.
A member that has never filed is invisible to it, by construction. So is a filing that is current,
harvested and reports `subjects: 0`, which is the state every fleet member was in when the kernel
needed five end-to-end subjects to finalise. The dogfood prompt says "re-run once a week" and nothing
computes due-ness, so "due" lived in whoever remembered.

Two absences that look identical in silence and need different remedies (ruling-candidate
`kernel-dogfood-admission-and-clock-r1.md` R1.3):
  UNLANDED  - no filing anywhere. Fixable by the filer alone, and invisible to a filings-only census.
  EXCLUDED  - a filing exists but nothing may adjudicate it: the steward's own filing, which kernel
              §5 says a second project's arbiter or the owner must rule on. It sat three harvest runs.
              This tool routes it to the siblings that could take it, which is the routing defect the
              steward's own K12 finding names.

IT WRITES NOTHING. No new artifact, no new roster, no state file: the roster comes from
`fleet-membership.mjs` (the derived authority) and the filings from `harvest-status.py --json`, each
the single writer of its own answer. Exit non-zero is the whole output contract, so a board can wire
it into a scheduled cycle it already runs and let a FINDING exit surface it.

Exit 0 = nothing due · 1 = at least one member DUE · 2 = tool/environment error.
"""
import argparse, json, re, subprocess, sys
from pathlib import Path

STEWARD = "conjugal"  # kernel header: "Steward: Conjugal, as interim steward, until the owner names another"


def run(cmd, cwd):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if p.returncode not in (0, 1):  # harvest-status uses 1 for "something unharvested"
        raise RuntimeError(f"{' '.join(cmd)} exited {p.returncode}: {p.stderr.strip()[:300]}")
    return p.stdout


def roster(repo):
    """Members come from the kernel's own §6 fleet mapping - the steward's enumeration of PROJECTS.

    NOT from fleet-membership.mjs. That helper derives members from spec FILENAMES, which is right for
    what it does and wrong here: this bus carries topic specs beside project specs, so on its first run
    this tool reported `design-loop-protocol`, `phased-concurrent-review-pattern` and eleven other
    documents as delinquent fleet members - 30 of 30 DUE. A due-check that cries wolf is ignored by
    week two, which is the failure it exists to prevent. §6 also names the one document it excludes
    on purpose ("a git-hygiene pattern document, not a project"), so the steward has already drawn this
    line; this reads that line instead of guessing at it.
    """
    text = (repo / "specs" / "fleet-factory-kernel.md").read_text(encoding="utf-8", errors="replace")
    m = re.search(r"^## 6\. Fleet mapping.*?$(.*?)^## ", text, re.S | re.M)
    body = m.group(1) if m else ""
    members = []
    for line in body.splitlines():
        if not line.startswith("|") or line.startswith("|---") or "| Project " in line:
            continue
        cell = line.split("|")[1].strip()
        if not cell:
            continue
        # "magic-lantern_dannephoto (no bus spec yet; mapped from its repo's CLAUDE.md)" -> the id
        name = re.split(r"\s*\(", cell)[0].strip()
        if re.fullmatch(r"[a-z0-9][a-z0-9._-]{1,63}", name):
            members.append(name)
    if not members:
        raise RuntimeError("kernel §6 fleet mapping parsed to zero projects; refusing to report 'nothing due'")
    return sorted(set(members))


def kernel_revision(repo):
    """The current kernel revision, read from the spec's own status line."""
    text = (repo / "specs" / "fleet-factory-kernel.md").read_text(encoding="utf-8", errors="replace")
    m = re.search(r"CANDIDATE\s+r(\d+)", text)
    return int(m.group(1)) if m else None


def filed_revision(header):
    m = re.search(r"r(\d+)", str(header.get("kernel", "")))
    return int(m.group(1)) if m else None


def closed_subjects(header):
    """A subjects line counts only what it says is CLOSED end-to-end. '0 closed' and '0 end-to-end'
    both mean zero; anything else is reported verbatim for a human, never parsed into a score."""
    s = str(header.get("subjects", "")).strip()
    if not s:
        return None
    return 0 if re.match(r"^\s*(0|none)\b", s) or re.search(r"\b0 (closed|end-to-end|qualifying)", s) else None


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--subject", default="factory-kernel")
    ap.add_argument("--cadence-days", type=int, default=7)
    ap.add_argument("--repo", default=".")
    ap.add_argument("--no-fetch", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    repo = Path(a.repo).resolve()

    cmd = [sys.executable, str(repo / "tools" / "harvest-status.py"), a.subject, "--json"]
    if a.no_fetch:
        cmd.append("--no-fetch")
    status = json.loads(run(cmd, repo))
    by_filing = {f["filing"]: f for f in status.get("filings", [])}
    current_r = kernel_revision(repo)
    now = int(run(["git", "log", "-1", "--format=%ct"], repo).strip() or 0)

    rows = []
    for member in roster(repo):
        f = by_filing.get(member)
        if f is None:
            rows.append({"member": member, "due": True, "reason": "UNLANDED: no filing on master or any review ref",
                         "remedy": "the filer lands it; nothing else is blocked on anyone else"})
            continue
        age_days = round((now - int(f.get("committed_at") or now)) / 86400.0, 1)
        filed_r, closed = filed_revision(f.get("header", {})), closed_subjects(f.get("header", {}))
        reasons = []
        if f.get("status") != "HARVESTED":
            reasons.append(f"{f.get('status')}: filing not adjudicated")
        if current_r and filed_r and filed_r < current_r:
            reasons.append(f"filed against kernel r{filed_r}, current r{current_r}")
        if closed == 0:
            reasons.append("subjects: 0 closed end-to-end (kernel §5 criterion 1 counts closed subjects only)")
        if age_days > a.cadence_days:
            reasons.append(f"filing is {age_days}d old (cadence {a.cadence_days}d)")
        row = {"member": member, "due": bool(reasons), "reason": "; ".join(reasons) or "current",
               "status": f.get("status"), "filed_kernel_r": filed_r, "age_days": age_days}
        if member == STEWARD and f.get("status") != "HARVESTED":
            siblings = [m for m in roster(repo) if m != STEWARD]
            row["remedy"] = ("EXCLUDED: the steward may not adjudicate its own filing (kernel §5). "
                             "A second project's arbiter or the owner must rule and write its dispositions. "
                             f"Candidates on the roster: {', '.join(siblings)}")
        rows.append(row)

    due = [r for r in rows if r["due"]]
    if a.json:
        print(json.dumps({"schema": "kernel-due.v1", "subject": a.subject, "kernel_revision": current_r,
                          "due_count": len(due), "members": rows}, indent=2))
    else:
        print(f"kernel {a.subject}: r{current_r} · {len(due)} of {len(rows)} members DUE")
        for r in rows:
            print(f"  {'DUE ' if r['due'] else ' ok '} {r['member']:<28} {r['reason']}")
            if r.get("remedy"):
                print(f"        -> {r['remedy']}")
    return 1 if due else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # a due-check that crashes must not read as "nothing due"
        print(f"kernel-due: {exc}", file=sys.stderr)
        sys.exit(2)
