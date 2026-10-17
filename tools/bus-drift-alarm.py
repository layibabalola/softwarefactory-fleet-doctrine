#!/usr/bin/env python3
"""Bus drift alarm: make a red sealed-pin check on master loud even when nobody watches CI.

Runs the two sealed-pin drift checkers CI runs, in check mode, on the checked-out master tip:

    r45  python tools/check_universal_manifest.py --treeish HEAD
    R26  python tools/check_adoption_ledger.py --current --treeish HEAD

On a failure it names the commit(s) that introduced the drift (the first commit after the pin's last
re-pin that changed a drifting covered path, with author), and prints the exact approved refresh
procedure -- the same text `hooks/pre-push-bus-tests.py` prints when it refuses a push, read from that
file so the two never diverge. With --issue it opens or updates ONE tracking issue (found by its exact
title) while red, and comments and closes it when green.

It never refreshes and never writes a tracked file (Law 1): a refresh is a reviewed commit. Exit 0 when
the alarm did its job (red or green); exit 2 when the alarm itself could not run.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TITLE = "Bus master drift: a sealed-pin check is red"
MARKER = "<!-- bus-drift-alarm -->"
HOOK = ROOT / "hooks" / "pre-push-bus-tests.py"


def git(*args: str) -> str:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    return subprocess.run(["git", *args], cwd=ROOT, env=env, check=True, capture_output=True,
                          text=True, encoding="utf-8").stdout.strip()


def load_hook():
    spec = importlib.util.spec_from_file_location("bus_tests_hook", HOOK)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def show(path: str, rev: str = "HEAD"):
    return json.loads(git("show", f"{rev}:{path}"))


def blob(rev: str, path: str) -> str | None:
    try:
        return git("rev-parse", "--verify", "--quiet", f"{rev}:{path}")
    except subprocess.CalledProcessError:
        return None


def introducers(pin: str, paths: list[str]) -> list[dict]:
    """First commit per drifting path after the pin file's last change (the last re-pin)."""
    repin = git("log", "-1", "--format=%H", "HEAD", "--", pin)
    found = {}
    for path in paths:
        commits = git("log", "--reverse", "--format=%H", f"{repin}..HEAD", "--", path).split()
        if not commits:
            continue
        sha = commits[0]
        author, subject = git("show", "-s", "--format=%an%x00%s", sha).split("\x00", 1)
        found.setdefault(sha, {"sha": sha, "author": author, "subject": subject, "paths": []})["paths"].append(path)
    return list(found.values())


def drifting_paths(name: str) -> list[str]:
    if name == "r45-manifest":
        manifest = show("manifests/universal-provider-control-reconciliation-r45.json")
        return [row["path"] for row in manifest["subjectFiles"] if blob("HEAD", row["path"]) != row["gitBlobOid"]]
    census = show("adoption/current-token-control-r26.json")
    paths = [row["specPath"] for row in census["projects"]
             if blob("HEAD", row["specPath"]) != row["evidence"]["gitBlobOid"]]
    known = {row["specPath"] for row in census["projects"]} | set(census["census"]["nonProjectSpecs"])
    top = [p for p in git("ls-tree", "--name-only", "HEAD", "specs/").splitlines()
           if p.endswith(".md") and p.count("/") == 1]
    return paths + sorted(set(top) - known) + sorted(known - set(top))


def check(hook, head: str) -> list[dict]:
    results = []
    for entry in hook.DEFAULT_DRIFT:
        argv = [sys.executable if a == "{python}" else a for a in entry["argv"]]
        run = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
        out = (run.stdout + run.stderr).strip()
        row = {"name": entry["name"], "pin": entry["pin"], "rc": run.returncode,
               "tail": "\n".join(out.splitlines()[-3:])[:600]}
        if run.returncode != 0:
            row["note"] = hook.drift_note(entry, out, head)
            try:
                row["introducers"] = introducers(entry["pin"], drifting_paths(entry["name"]))
            except Exception as error:  # attribution is best effort; the red verdict is not
                row["introducers"] = []
                row["attribution_error"] = repr(error)
        results.append(row)
    return results


def render(results: list[dict], head: str, repo: str, run_url: str) -> str:
    red = [r for r in results if r["rc"] != 0]
    lines = [MARKER, f"Master tip `{head[:12]}` ({repo}@{head}) fails {len(red)} sealed-pin drift check(s).",
             f"Alarm run: {run_url}", "",
             "Every writer that pushes to the bus should run the pinned pre-push layer "
             "(`hooks/pre-push-bus-tests.py`, install in `hooks/README.md` \"Bus writers\"); it refuses this "
             "before it reaches master. This issue closes itself when the checks pass on master.", ""]
    for r in red:
        lines += [f"### {r['name']} (`{r['pin']}`) -- exit {r['rc']}", "", "```", r["tail"], "```", ""]
        if r.get("introducers"):
            lines.append("Introduced by (first commit after the pin's last re-pin that changed a drifting path):")
            for c in r["introducers"]:
                lines.append(f"- {c['sha'][:12]} by **{c['author']}**: {c['subject']} -- "
                             f"{', '.join('`%s`' % p for p in c['paths'])}")
            lines.append("")
        elif "attribution_error" in r:
            lines += [f"Attribution failed: `{r['attribution_error']}`", ""]
        lines += ["Exact refresh:", "```", r["note"], "```", ""]
    return "\n".join(lines)


def gh(*args: str, stdin: str | None = None) -> str:
    return subprocess.run(["gh", *args], input=stdin, check=True, capture_output=True, text=True,
                          encoding="utf-8").stdout.strip()


def tracking_issue(repo: str):
    rows = json.loads(gh("issue", "list", "--repo", repo, "--state", "open", "--limit", "200",
                         "--json", "number,title,body"))
    rows = [r for r in rows if r["title"] == TITLE and MARKER in (r.get("body") or "")]
    return min(rows, key=lambda r: r["number"]) if rows else None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--issue", action="store_true", help="open/update/close the tracking issue via gh")
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", ""))
    args = parser.parse_args()
    try:
        hook = load_hook()
        head = git("rev-parse", "HEAD")
        results = check(hook, head)
    except Exception as error:
        print(f"BUS_DRIFT_ALARM_UNAVAILABLE: {error!r}", file=sys.stderr)
        return 2
    run_url = (f"{os.environ.get('GITHUB_SERVER_URL', 'https://github.com')}/{args.repo}/actions/runs/"
               f"{os.environ.get('GITHUB_RUN_ID', 'local')}")
    red = [r for r in results if r["rc"] != 0]
    for r in results:
        print(f"{'RED ' if r['rc'] else 'ok  '} {r['name']} rc={r['rc']}")
    body = render(results, head, args.repo, run_url) if red else ""
    if body:
        print(body)
    if not args.issue:
        return 0
    try:
        issue = tracking_issue(args.repo)
        if red and issue is None:
            print(gh("issue", "create", "--repo", args.repo, "--title", TITLE, "--body-file", "-", stdin=body))
        elif red:
            number = str(issue["number"])
            if f"`{head[:12]}`" not in (issue.get("body") or ""):
                gh("issue", "edit", number, "--repo", args.repo, "--body-file", "-", stdin=body)
                gh("issue", "comment", number, "--repo", args.repo, "--body-file", "-",
                   stdin=f"Still red at `{head[:12]}`. {run_url}")
            print(f"updated #{number}")
        elif issue is not None:
            number = str(issue["number"])
            gh("issue", "close", number, "--repo", args.repo, "--comment",
               f"Green: every sealed-pin drift check passes on master `{head[:12]}`. {run_url}")
            print(f"closed #{number}")
    except (subprocess.CalledProcessError, OSError, ValueError) as error:
        detail = getattr(error, "stderr", "") or repr(error)
        print(f"BUS_DRIFT_ALARM_ISSUE_FAILED: {detail}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
