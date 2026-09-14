#!/usr/bin/env python3
"""Has every filing on a subject been harvested? Derived from refs, never from memory.

  harvest-status.py <subject>          e.g. approach-a-design (a directory under adjudications/)
  harvest-status.py --all              every subject, one summary line each
  options: --no-fetch  --json  --repo <path>

Population: every `adjudications/<subject>/<name>.md` on origin/master AND on every
origin/review/* branch (RULINGS R7.5). README.md, REVIEW-PROMPT.md and *.dispositions.md are not
filings. When one filing name exists at different blobs on different refs, the copy whose last
commit on that path is newest is current; the others are listed as superseded.

Harvested means `adjudications/<subject>/<name>.dispositions.md` exists on origin/master (or on a
review branch) and its `filing_blob:` line names the current filing's blob. A dispositions file
answering an older blob is STALE: the filer changed the filing after the harvest.

Exit 0 = every filing HARVESTED; 1 = at least one UNHARVESTED or STALE; 2 = tool/environment error.
"""
import argparse, json, pathlib, re, subprocess, sys

NOT_FILINGS = {"README.md", "REVIEW-PROMPT.md", "HARVESTS.md"}
HEADER_KEYS = ("project", "providers", "posture", "cross_family", "rubric_id", "panel",
               "kernel", "profile", "subjects", "health", "arbiter")
R9_POSTURE = re.compile(r"^\S+ COMPLETE \((\d+)/\1 lanes\)|^\S+-PARTIAL \(\d+/\d+ lanes|^no model review$")


class ToolError(Exception):
    pass


def git(repo, *args, check=True):
    try:
        p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=60,
                           env={**__import__("os").environ, "GIT_TERMINAL_PROMPT": "0", "GIT_OPTIONAL_LOCKS": "0"})
    except subprocess.TimeoutExpired:
        raise ToolError(f"git {' '.join(args)}: timed out")
    if check and p.returncode != 0:
        raise ToolError(f"git {' '.join(args)}: {p.stderr.strip()}")
    return p


def refs(repo):
    out = git(repo, "for-each-ref", "--format=%(refname)", "refs/remotes/origin/review/").stdout.split()
    if git(repo, "rev-parse", "--verify", "-q", "refs/remotes/origin/master", check=False).returncode != 0:
        raise ToolError("refs/remotes/origin/master missing; fetch first")
    return ["refs/remotes/origin/master", *sorted(out)]


def ls(repo, ref, subject):
    p = git(repo, "ls-tree", ref, f"adjudications/{subject}/", check=False)
    rows = {}
    for line in p.stdout.splitlines():
        meta, _, path = line.partition("\t")
        mode, kind, blob = meta.split()
        if kind == "blob":
            rows[pathlib.PurePosixPath(path).name] = blob
    return rows


def last_commit(repo, ref, path):
    out = git(repo, "log", "-1", "--format=%H %ct", ref, "--", path).stdout.split()
    return (out[0], int(out[1])) if out else ("", 0)


def parse_filing(text):
    header, findings, untested, section = {}, 0, 0, ""
    for line in text.splitlines():
        m = re.match(r"^([a-z_]+):\s*(.*)$", line)
        if m and m.group(1) in HEADER_KEYS and m.group(1) not in header:
            header[m.group(1)] = m.group(2).strip()
        if line.startswith("## "):
            section = line[3:].strip().lower()
        if line.startswith("§") or re.match(r"^(K\d+ |P:\S+[^|\n]*)\|", line):
            if section.startswith("untested"):
                untested += 1
            else:
                findings += 1
    flags = []
    posture = header.get("posture", "")
    if posture and not R9_POSTURE.match(posture):
        flags.append("POSTURE-NOT-R9-COMPUTED")
    if not header.get("providers"):
        flags.append("NO-PROVIDERS-HEADER")
    return header, findings, untested, flags


def subject_status(repo, subject):
    all_refs = refs(repo)
    copies, answers = {}, {}
    for ref in all_refs:
        for name, blob in ls(repo, ref, subject).items():
            path = f"adjudications/{subject}/{name}"
            if name.endswith(".dispositions.md"):
                text = git(repo, "cat-file", "-p", blob).stdout
                m = re.search(r"^filing_blob:\s*([0-9a-f]{7,40})", text, re.M)
                answers.setdefault(name[: -len(".dispositions.md")], set()).add(m.group(1) if m else "")
            elif name.endswith(".md") and name not in NOT_FILINGS:
                sha, ct = last_commit(repo, ref, path)
                copies.setdefault(name[:-3], {}).setdefault(blob, (ct, ref, sha))
    rows = []
    for stem in sorted(copies):
        ranked = sorted(copies[stem].items(), key=lambda kv: kv[1][0], reverse=True)
        blob, (ct, ref, sha) = ranked[0]
        header, n, u, flags = parse_filing(git(repo, "cat-file", "-p", blob).stdout)
        got = answers.get(stem, set())
        status = ("HARVESTED" if any(a and blob.startswith(a) for a in got)
                  else "STALE" if got else "UNHARVESTED")
        rows.append({"filing": stem, "status": status, "blob": blob, "ref": ref.replace("refs/remotes/", ""),
                     "commit": sha, "committed_at": ct, "findings": n, "untested": u, "flags": flags,
                     "header": header, "superseded": [{"blob": b, "ref": r.replace("refs/remotes/", "")}
                                                      for b, (_, r, _) in ranked[1:]]})
    readme = ls(repo, all_refs[0], subject).get("README.md")
    owner_subject = ""
    if readme:
        m = re.search(r"Subject:\s*`([^`]+)`", git(repo, "cat-file", "-p", readme).stdout)
        owner_subject = m.group(1) if m else ""
    return {"subject": subject, "spec": owner_subject, "filings": rows}


def subjects(repo):
    names = set()
    for ref in refs(repo):
        p = git(repo, "ls-tree", "-d", "--name-only", ref, "adjudications/", check=False)
        names.update(pathlib.PurePosixPath(x).name for x in p.stdout.split())
    return sorted(names)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("subject", nargs="?")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--no-fetch", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--repo", default=str(pathlib.Path(__file__).resolve().parent.parent))
    a = ap.parse_args(argv)
    if bool(a.subject) == a.all:
        ap.error("give exactly one of <subject> or --all")
    try:
        if not a.no_fetch:
            git(a.repo, "fetch", "--quiet", "origin", "+refs/heads/master:refs/remotes/origin/master",
                "+refs/heads/review/*:refs/remotes/origin/review/*")
        reports = [subject_status(a.repo, s) for s in (subjects(a.repo) if a.all else [a.subject])]
    except ToolError as e:
        print(f"harvest-status: ERROR {e}", file=sys.stderr)
        return 2
    open_count = 0
    for r in reports:
        n_open = sum(f["status"] != "HARVESTED" for f in r["filings"])
        open_count += n_open
        if a.json:
            continue
        if a.all:
            print(f"{r['subject']}  spec={r['spec'] or '?'}  filings={len(r['filings'])}  open={n_open}")
            continue
        print(f"subject={r['subject']} spec={r['spec'] or '?'} filings={len(r['filings'])}")
        for f in r["filings"]:
            print(f"  {f['filing']:<28} {f['status']:<11} blob={f['blob'][:8]} ref={f['ref']} "
                  f"findings={f['findings']} untested={f['untested']} "
                  f"posture={f['header'].get('posture', '-')!r} flags={','.join(f['flags']) or '-'}")
            for s in f["superseded"]:
                print(f"      superseded copy blob={s['blob'][:8]} ref={s['ref']}")
        print(f"open={n_open}  (UNHARVESTED or STALE; 0 means every current filing has a disposition)")
    if a.json:
        print(json.dumps(reports if a.all else reports[0], indent=2))
    return 1 if open_count else 0


if __name__ == "__main__":
    sys.exit(main())
