#!/usr/bin/env python3
"""Is the universal factory kernel converging? Derived from refs, never from memory.

  kernel-convergence.py                 summary of the newest candidate revision on origin/master
  options: --no-fetch  --json  --repo <path>  --ref <ref>  --hygiene  --now <ISO8601>

Candidate: the highest `ruling-candidates/universal-factory-kernel-r<N>.md` on --ref. Budget (the
candidate's section 1): at most 8 `### UFK-n` clauses, at most 30 lines per clause section, at most 420
lines across the normative files (candidate + filing README + PROMPT K).

Filings: `adjudications/universal-factory-kernel/<stem>.md`, the current copy chosen exactly as
`tools/harvest-status.py` chooses it (origin/master plus origin/review/*). A filing COUNTS only if
its `project:` equals its filename stem, the project is known (a `specs/<project>.md` on --ref, or a
RECEIPTS.md heading "(<project>, ..." on the filing's own ref), and its `kernel_revision:` equals the
candidate's `r<N>`, and it has a non-empty `seats:` and an `## Adapter` section with an `artifact:`
line; anything else is listed under `ignored` with the reason. One filing per stem, so one per project.

Per clause (the candidate's UFK-8):
  eligible    ADOPT or ADOPT-WITH-CHANGE with PROOF from >=2 distinct non-author counting projects
              whose declared classes admit two DIFFERENT classes (one per project); not must_amend;
              and every REJECT-with-PROOF has a `UFK-<n> | <verdict>` answer line in a dispositions
              file whose `filing_blob:` names that filing's current blob.
  must_amend  DISTINGUISH or REJECT with PROOF from >=2 counting projects whose classes admit two
              different classes.
Universal: every clause eligible AND a non-author counting project declaring `judgment` adopts a clause.
PROOF counts only as "<command> -> <non-empty result>". The tool cannot authenticate PROOF or
project identity: eligibility is a prompt for non-author re-derivation, never a verdict.

Harvest due: >=3 counting filings UNHARVESTED/STALE, or >=1 and >=7 days since the
subject's newest `.dispositions.md` commit (or the candidate's first commit when there is none).

--hygiene (UFK-7, advisory): since the candidate's first commit on --ref, TRAPS.md sections with
neither "Test:" nor "ANECDOTE", and new ruling-candidates/ or specs/ files never mentioning supersession.

Over budget: nothing is eligible and universal is false. A missing normative companion is a tool error.
Identity, authorship, classes and PROOF are all self-asserted; nothing here authenticates them.

Exit 0 = measured and within budget; 1 = over budget; 2 = tool error.
"""
import argparse, datetime as dt, importlib.util, json, pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("harvest_status", HERE / "harvest-status.py")
hs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(hs)

SUBJECT = "universal-factory-kernel"
NORMATIVE = (f"adjudications/{SUBJECT}/README.md", "bootstrap/PROMPT-K-dogfood-kernel.md")
CLASSES = {"deterministic", "statistical", "attended", "judgment"}
ADOPTS = {"ADOPT", "ADOPT-WITH-CHANGE"}
DIVERGES = {"DISTINGUISH", "REJECT"}
BUDGET = {"clauses": 8, "clause_lines": 30, "normative_lines": 420}
CLAUSE_LINE = re.compile(
    r"^UFK-(\d+)\s*\|\s*(ADOPT-WITH-CHANGE|ADOPT|DISTINGUISH|REJECT|UNMEASURED)\s*\|\s*(.*?)\s*\|\s*PROOF:\s*(.*)$")
ANSWER_LINE = re.compile(r"^UFK-(\d+)\s*\|\s*(ADOPTED-CONDITIONAL|ADOPTED|REJECTED|ROUTED)\s*\|", re.M)
HEADER = re.compile(r"^([a-z_]+):\s*(.*)$")


def newest_candidate(repo, ref):
    best = None
    for path in hs.git(repo, "ls-tree", "--name-only", ref, "ruling-candidates/").stdout.split():
        m = re.fullmatch(r"ruling-candidates/universal-factory-kernel-r(\d+)\.md", path)
        if m and (best is None or int(m.group(1)) > best[0]):
            best = (int(m.group(1)), path)
    if not best:
        raise hs.ToolError(f"no ruling-candidates/universal-factory-kernel-r<N>.md on {ref}")
    return best


def measure_candidate(text, companion_lines=0):
    lines = text.splitlines()
    heads = [i for i, l in enumerate(lines) if re.match(r"^### UFK-\d+\b", l)]
    clauses = []
    for i in heads:
        end = next((j for j in range(i + 1, len(lines)) if lines[j].startswith(("## ", "### "))), len(lines))
        clauses.append({"id": re.match(r"^### (UFK-\d+)", lines[i]).group(1), "lines": end - i})
    normative = len(lines) + companion_lines
    over = []
    if len(clauses) > BUDGET["clauses"]:
        over.append(f"clauses {len(clauses)} > {BUDGET['clauses']}")
    over += [f"{c['id']} {c['lines']} lines > {BUDGET['clause_lines']}" for c in clauses
             if c["lines"] > BUDGET["clause_lines"]]
    if normative > BUDGET["normative_lines"]:
        over.append(f"normative {normative} lines > {BUDGET['normative_lines']}")
    return {"clauses": clauses, "file_lines": len(lines), "normative_lines": normative, "over_budget": over}


def parse_filing(text):
    header, rows = {}, {}
    for line in text.splitlines():
        m = HEADER.match(line)
        if m and m.group(1) not in header:
            header[m.group(1)] = m.group(2).strip()
        c = CLAUSE_LINE.match(line.strip())
        if c and f"UFK-{c.group(1)}" not in rows:
            proof = c.group(4).strip()
            rows[f"UFK-{c.group(1)}"] = {"disposition": c.group(2), "mechanism": c.group(3),
                                         "proved": "->" in proof and bool(proof.split("->", 1)[0].strip())
                                         and bool(proof.split("->", 1)[1].strip())}
    classes = {x.strip().lower() for x in header.get("adapter_class", "").split(",")} & CLASSES
    adapter = re.search(r"^## Adapter[ \t]*\n((?:(?!## ).*(?:\n|$))*)", text, re.M)
    has_adapter = bool(adapter and re.search(r"^artifact:\s*\S", adapter.group(1), re.M))
    return {"project": header.get("project", ""), "classes": sorted(classes),
            "seats": header.get("seats", ""), "has_adapter": has_adapter,
            "author": header.get("author_of_candidate", "").lower() == "yes",
            "revision": header.get("kernel_revision", "").strip().lower(), "rows": rows}


def two_distinct_classes(projects):
    """projects: list of class-sets, one per distinct project. True if two projects can each
    contribute a different class."""
    for i, a in enumerate(projects):
        for b in projects[i + 1:]:
            if any(x != y for x in a for y in b):
                return True
    return False


def converge(clause_ids, filings):
    """filings: dicts from parse_filing plus 'name', 'answers' (set of clause ids answered)."""
    out, all_eligible = [], bool(clause_ids)
    for cid in clause_ids:
        adopters, divergers, blocking = {}, {}, []
        for f in filings:
            row = f["rows"].get(cid)
            if not row or not row["proved"] or not f["classes"]:
                continue
            if row["disposition"] in ADOPTS and not f["author"]:
                adopters[f["project"]] = set(f["classes"])
            if row["disposition"] in DIVERGES:
                divergers[f["project"]] = set(f["classes"])
                if row["disposition"] == "REJECT" and cid not in f["answers"]:
                    blocking.append(f["project"])
        must_amend = len(divergers) >= 2 and two_distinct_classes(list(divergers.values()))
        eligible = (len(adopters) >= 2 and two_distinct_classes(list(adopters.values()))
                    and not must_amend and not blocking)
        all_eligible &= eligible
        out.append({"id": cid, "adopters": sorted(adopters),
                    "adopter_classes": sorted({c for s in adopters.values() for c in s}),
                    "diverging": sorted(divergers), "unanswered_rejects": sorted(blocking),
                    "eligible": eligible, "must_amend": must_amend})
    judgment = any("judgment" in f["classes"] and not f["author"] and
                   any(r["disposition"] in ADOPTS and r["proved"] for r in f["rows"].values()) for f in filings)
    return {"clauses": out, "universal": all_eligible and judgment,
            "classes_covered": sorted({c for f in filings if not f["author"] for c in f["classes"]})}


def dispositions_answers(repo, stem, blob):
    """Clause ids answered by `<stem>.dispositions.md` (on any ref) whose filing_blob names blob."""
    answered = set()
    for ref in hs.refs(repo):
        for name, dblob in hs.ls(repo, ref, SUBJECT).items():
            if name != f"{stem}.dispositions.md":
                continue
            text = hs.git(repo, "cat-file", "-p", dblob).stdout
            m = re.search(r"^filing_blob:\s*([0-9a-f]{7,40})", text, re.M)
            if m and blob.startswith(m.group(1)):
                answered.update(f"UFK-{n}" for n, _ in ANSWER_LINE.findall(text))
    return answered


def known_project(repo, ref, filing_ref, project):
    """Friction, not authentication: the project has a spec on ref, or RECEIPTS.md on the filing's
    own ref carries a heading whose parenthetical starts with it."""
    if hs.git(repo, "cat-file", "-e", f"{ref}:specs/{project}.md", check=False).returncode == 0:
        return True
    rec = hs.git(repo, "show", f"refs/remotes/{filing_ref}:RECEIPTS.md", check=False).stdout
    return bool(re.search(rf"^## .*\({re.escape(project)},", rec, re.M))


def load_filings(repo, ref, revision):
    status = hs.subject_status(repo, SUBJECT)["filings"]
    counting, ignored = [], []
    for r in status:
        f = parse_filing(hs.git(repo, "cat-file", "-p", r["blob"]).stdout)
        f.update({"name": r["filing"], "status": r["status"], "ref": r["ref"]})
        if f["project"] != r["filing"]:
            ignored.append({"name": r["filing"], "reason": f"project '{f['project']}' != filename stem"})
        elif not known_project(repo, ref, r["ref"], f["project"]):
            ignored.append({"name": r["filing"], "reason": "unknown project: no specs/<project>.md and no "
                                                           "RECEIPTS.md heading '(<project>, ...' on its ref"})
        elif f["revision"] != revision:
            ignored.append({"name": r["filing"], "reason": f"kernel_revision '{f['revision']}' != {revision}"})
        elif not f["seats"] or not f["has_adapter"]:
            ignored.append({"name": r["filing"], "reason": "missing seats: or a '## Adapter' section with an artifact: line"})
        else:
            f["answers"] = dispositions_answers(repo, r["filing"], r["blob"])
            counting.append(f)
    return status, counting, ignored


def harvest_due(repo, ref, candidate, counting, now):
    open_n = sum(f["status"] != "HARVESTED" for f in counting)
    stamps = []
    for rf in hs.refs(repo):
        for name in hs.ls(repo, rf, SUBJECT):
            if name.endswith(".dispositions.md"):
                stamps.append(hs.last_commit(repo, rf, f"adjudications/{SUBJECT}/{name}")[1])
    if not stamps:
        out = hs.git(repo, "log", "--diff-filter=A", "--format=%ct", ref, "--", candidate).stdout.split()
        stamps = [int(out[-1])] if out else [int(now.timestamp())]
    days = (now.timestamp() - max(stamps)) / 86400
    return {"open": open_n, "days_since_last_harvest": round(days, 2),
            "due": open_n >= 3 or (open_n >= 1 and days >= 7)}


def hygiene(repo, ref, candidate):
    first = hs.git(repo, "log", "--diff-filter=A", "--format=%H", ref, "--", candidate).stdout.split()
    if not first:
        return {"since": None}
    base = first[-1]
    traps = hs.git(repo, "diff", f"{base}..{ref}", "--", "TRAPS.md").stdout
    sections = re.split(r"^\+## ", traps, flags=re.M)[1:]
    untested = sum("Test:" not in s and "ANECDOTE" not in s for s in sections)
    added = hs.git(repo, "diff", "--name-only", "--diff-filter=A", f"{base}..{ref}", "--",
                   "ruling-candidates/", "specs/").stdout.split()
    silent = [p for p in added if not re.search(r"supersed", hs.git(repo, "show", f"{ref}:{p}").stdout, re.I)]
    return {"since": base[:12], "traps_added": len(sections), "traps_without_test": untested,
            "new_docs_without_supersession": silent}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default=str(HERE.parent))
    ap.add_argument("--ref", default="refs/remotes/origin/master")
    ap.add_argument("--no-fetch", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--hygiene", action="store_true")
    ap.add_argument("--now", help="ISO8601 clock override (tests)")
    a = ap.parse_args(argv)
    repo = pathlib.Path(a.repo)
    now = dt.datetime.fromisoformat(a.now) if a.now else dt.datetime.now(dt.timezone.utc)
    try:
        if not a.no_fetch:
            hs.git(repo, "fetch", "--quiet", "origin", "+refs/heads/master:refs/remotes/origin/master",
                   "+refs/heads/review/*:refs/remotes/origin/review/*")
        n, candidate = newest_candidate(repo, a.ref)
        companions = 0
        for p in NORMATIVE:
            got = hs.git(repo, "show", f"{a.ref}:{p}", check=False)
            if got.returncode != 0:
                raise hs.ToolError(f"normative companion {p} missing on {a.ref}")
            companions += len(got.stdout.splitlines())
        cand = measure_candidate(hs.git(repo, "show", f"{a.ref}:{candidate}").stdout, companions)
        status, counting, ignored = load_filings(repo, a.ref, f"r{n}")
        result = {"candidate": candidate, "revision": f"r{n}", "ref": a.ref, **cand,
                  "filings": [{k: f[k] for k in ("name", "classes", "author", "status")} for f in counting],
                  "ignored": ignored, "harvest": harvest_due(repo, a.ref, candidate, counting, now),
                  **converge([c["id"] for c in cand["clauses"]], counting)}
        if cand["over_budget"]:
            for c in result["clauses"]:
                c["eligible"] = False
            result["universal"] = False
        if a.hygiene:
            result["hygiene"] = hygiene(repo, a.ref, candidate)
    except hs.ToolError as e:
        print(f"kernel-convergence: {e}", file=sys.stderr)
        return 2
    if a.json:
        print(json.dumps(result, indent=2))
    else:
        el = sum(c["eligible"] for c in result["clauses"])
        print(f"{candidate}: {len(result['clauses'])} clauses, normative {result['normative_lines']} lines; "
              f"{len(counting)} counting filing(s), {len(ignored)} ignored; eligible {el}/{len(result['clauses'])}; "
              f"classes {','.join(result['classes_covered']) or 'none'}; universal={result['universal']}; "
              f"harvest_due={result['harvest']['due']}")
        for o in result["over_budget"]:
            print(f"  OVER BUDGET  {o}")
        for i in ignored:
            print(f"  IGNORED      {i['name']}: {i['reason']}")
        for c in result["clauses"]:
            flag = "ELIGIBLE" if c["eligible"] else ("MUST-AMEND" if c["must_amend"] else "open")
            print(f"  {c['id']:<6} {flag:<10} adopters={len(c['adopters'])} [{','.join(c['adopter_classes'])}] "
                  f"diverging={len(c['diverging'])} unanswered_rejects={len(c['unanswered_rejects'])}")
        print("  eligibility is a prompt for non-author re-derivation of PROOF, not a verdict")
        if a.hygiene:
            print(f"  hygiene: {result['hygiene']}")
    return 1 if result["over_budget"] else 0


if __name__ == "__main__":
    sys.exit(main())
