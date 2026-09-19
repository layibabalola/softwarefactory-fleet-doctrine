#!/usr/bin/env python3
"""Doctrine outbox: findings reach the fleet bus by FILE, not by memory.

THE FAILURE THIS EXISTS FOR
---------------------------
The standing directive (owner, 2026-08-09) says cross-project findings go to the doctrine bus
the same day, at the landing seam. It lived in a session's head. Measured 2026-09-18: a real
fix (a parity checker minting a hard ACCOUNT_MISMATCH on a healthy host) was published only
because the owner asked "did you publish it?". A directive that a rotation forgets is not a
mechanism.

THE MECHANISM
-------------
1. The author writes the finding as a file in the SAME COMMIT as the fix:
       coordination/doctrine-outbox/<yyyymmdd>-<slug>.md
   with front matter (target, kind, source_commit, law4) and the body already in the bus
   file's entry grammar (a `### ` heading). See coordination/doctrine-outbox/README.md.
2. A commit that touches FINDING_PATHS (the places findings have historically come from) must
   carry a `Doctrine-Export:` trailer -- `none` (one line, explicit) or `outbox` (the commit
   adds an item). Enforced by the pre-push hook on Conjugal master, gate on exit status, LOCAL
   facts only -- no bus round-trip, so an ordinary push never becomes a two-repo transaction.
3. The harvest steward (the ONLY bus pusher; a second writer on an append-only tail is the
   2026-09-14 trap) drains unsent items on every 15-minute tick through its existing
   `publish_bus` seam: fetched tip, path census, byte-prefix append-only check, ls-remote
   proof. Each appended block carries an idempotency key; a key already on the bus tip is
   skipped, so a crash between bus push and the Conjugal-side move cannot double-append.
4. On success the item moves to `coordination/doctrine-outbox/sent/` with `bus_commit:` added,
   landed through the steward's commit gateway. `sent/` is the proof any session or sibling
   can read without the bus.
5. Law 4 (coordination surfaces, transcripts, addresses never travel) is enforced on the BODY
   mechanically -- an attestation line is not a screen. The 2026-09-18 receipt was about
   account identity and the evidence for it is exactly the material Law 4 bans, so a model-
   composed exporter would leak by construction. The author writes; the screen refuses.

No model decides "is this a finding". The author declares once; scripts check.
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys
import time
from datetime import datetime, timezone

OUTBOX_DIR = "coordination/doctrine-outbox"
SENT_DIR = OUTBOX_DIR + "/sent"
TARGETS = ("RECEIPTS.md", "TRAPS.md", "RULINGS.md")
KINDS = ("receipt", "trap", "ruling")
TRAILER = "Doctrine-Export"
TRAILER_VALUES = ("none", "outbox")
WORD_CAP = 450
ITEM_NAME_RE = re.compile(r"^\d{8}-[a-z0-9][a-z0-9-]{2,60}\.md$")
SHA_RE = re.compile(r"^[0-9a-f]{7,40}$")

# Where findings have historically come from. A commit here must SAY whether it exports.
# Deliberately narrow: floors emit hundreds of coord:/fable:/opus: commits under
# coordination/lanes and coordination/comms and those never carry a finding.
FINDING_PATHS = (
    re.compile(r"^coordination/tools/[^/]+\.py$"),
    re.compile(r"^coordination/harvest/[^/]+\.(py|ps1)$"),
    re.compile(r"^CLAUDE\.md$"),
)

# Law 4 screen on the body. Each pattern names the class it refuses; the screen prints which.
LAW4 = (
    ("email address", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),
    ("account/org uuid", re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", re.I)),
    ("lane wire path", re.compile(r"coordination/(lanes|comms)/")),
    ("HUB heartbeat", re.compile(r"\bHUB\.md\b")),
    ("owner transcript store", re.compile(r"loops\.json")),
    ("bearer/API token", re.compile(r"\b(sk-ant-|pk1:|gh[pousr]_[A-Za-z0-9]{20,}|Bearer\s+[A-Za-z0-9._-]{20,})")),
    # Law 4 surfaces beyond the lane wire, measured ACCEPTED 2026-09-18 before these existed:
    # prompt transcripts (state/), floor logs (coordination/deadman/), and any user-home path,
    # which names the account holder. "state/" is anchored so that "estate/" or "ratify-state/"
    # prose does not false-refuse.
    ("owner state dir", re.compile(r"(?<![A-Za-z0-9_./-])state/")),
    ("dead-man floor surface", re.compile(r"coordination/deadman/")),
    ("user home path", re.compile(r"(?:[A-Za-z]:\\Users\\|/Users/|/home/)[^\s\\/]+", re.I)),
)


class Refusal(Exception):
    def __init__(self, code, detail=""):
        super().__init__(f"{code}: {detail}" if detail else code)
        self.code, self.detail = code, detail


def git(repo, *args, check=True, binary=False, env=None):
    e = {**os.environ, "GIT_OPTIONAL_LOCKS": "0", **(env or {})}
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, env=e, timeout=120)
    out = p.stdout if binary else p.stdout.decode("utf-8", "replace")
    if check and p.returncode:
        raise Refusal("GIT_FAILED", f"git {' '.join(args)}: {p.stderr.decode('utf-8', 'replace').strip()}")
    return (p.returncode, out) if not check else (out.strip() if not binary else out)


# ---------- items ----------

def parse_item(text: str) -> dict:
    """Front matter + body. Refuses on any schema hole; never guesses a default."""
    if not text.startswith("---\n"):
        raise Refusal("ITEM_NO_FRONT_MATTER")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise Refusal("ITEM_UNTERMINATED_FRONT_MATTER")
    meta = {}
    for line in text[4:end].splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            raise Refusal("ITEM_BAD_FRONT_MATTER_LINE", line)
        k, v = line.split(":", 1)
        meta[k.strip()] = v.strip()
    body = text[end + 5:]
    for k in ("target", "kind", "source_commit", "law4"):
        if k not in meta:
            raise Refusal("ITEM_MISSING_FIELD", k)
    if meta["target"] not in TARGETS:
        raise Refusal("ITEM_BAD_TARGET", f"{meta['target']} not in {TARGETS}; specs are steward-owned")
    if meta["kind"] not in KINDS:
        raise Refusal("ITEM_BAD_KIND", meta["kind"])
    if meta["source_commit"] != "PENDING" and not SHA_RE.match(meta["source_commit"]):
        raise Refusal("ITEM_BAD_SOURCE_COMMIT", meta["source_commit"])
    if meta["law4"] != "attested":
        raise Refusal("ITEM_LAW4_NOT_ATTESTED", "law4: attested is required (and is then SCREENED, not trusted)")
    if meta["target"] == "RULINGS.md" and not meta.get("ratified_by"):
        raise Refusal("ITEM_RULING_UNRATIFIED", "a RULINGS.md item needs ratified_by: <RULINGS anchor>; sessions do not mint law")
    if not body.strip():
        raise Refusal("ITEM_EMPTY_BODY")
    if not body.lstrip().startswith("### "):
        raise Refusal("ITEM_BODY_NOT_AN_ENTRY", "body must start with a '### ' heading (bus entry grammar)")
    return {"meta": meta, "body": body}


def screen_law4(body: str) -> None:
    words = len(body.split())
    if words > WORD_CAP:
        raise Refusal("LAW4_OVER_CAP", f"{words} words > {WORD_CAP}")
    for name, rx in LAW4:
        m = rx.search(body)
        if m:
            raise Refusal("LAW4_REFUSED", f"{name}: {m.group(0)[:24]!r}")


def idempotency_key(source_commit: str, target: str, body: str) -> str:
    return hashlib.sha256(f"{source_commit}\n{target}\n{body}".encode("utf-8")).hexdigest()[:16]


def render_block(item: dict, source_commit: str, project: str) -> tuple[str, str]:
    key = idempotency_key(source_commit, item["meta"]["target"], item["body"])
    body = item["body"].rstrip("\n")
    block = f"{body}\n<!-- outbox:{key} {project}:{source_commit[:12]} -->\n"
    return key, block


# ---------- repository queries (committed bytes only, never the worktree) ----------

def added_in(repo, path: str) -> str | None:
    """The commit that ADDED this path on master, or None if it is not committed."""
    out = git(repo, "log", "--diff-filter=A", "--format=%H", "-n", "1", "master", "--", path)
    return out or None


def unsent_items(repo) -> list[dict]:
    """Items committed on master and not yet under sent/. Worktree-only files are invisible
    on purpose: the drain publishes committed bytes, so it reads them from master."""
    rc, out = git(repo, "ls-tree", "-r", "--name-only", "master", "--", OUTBOX_DIR, check=False)
    items = []
    for p in (out or "").splitlines():
        p = p.strip()
        name = p.rsplit("/", 1)[-1]
        if not p.startswith(OUTBOX_DIR + "/") or p.startswith(SENT_DIR + "/") or not ITEM_NAME_RE.match(name):
            continue
        text = git(repo, "show", f"master:{p}")
        try:
            item = parse_item(text + ("\n" if not text.endswith("\n") else ""))
        except Refusal as e:
            items.append({"path": p, "error": str(e)})
            continue
        src = item["meta"]["source_commit"]
        if src == "PENDING":
            src = added_in(repo, p) or "PENDING"
        items.append({"path": p, "item": item, "source_commit": src,
                      "added_at": commit_time(repo, added_in(repo, p))})
    return items


def commit_time(repo, sha) -> datetime | None:
    if not sha:
        return None
    out = git(repo, "show", "-s", "--format=%cI", sha)
    try:
        return datetime.fromisoformat(out).astimezone(timezone.utc)
    except ValueError:
        return None


def trailer_of(repo, sha) -> str | None:
    out = git(repo, "show", "-s", f"--format=%(trailers:key={TRAILER},valueonly)", sha)
    v = out.strip().splitlines()
    return v[0].strip().lower() if v and v[0].strip() else None


def files_of(repo, sha, diff_filter: str | None = None) -> list[str]:
    args = ["diff-tree", "--no-commit-id", "--name-only", "-r", "--root"]
    if diff_filter:
        args.append(f"--diff-filter={diff_filter}")
    return [x for x in git(repo, *args, sha).splitlines() if x]


def touches_finding_paths(paths: list[str]) -> list[str]:
    return [p for p in paths if any(rx.match(p) for rx in FINDING_PATHS)]


def check_commit(repo, sha) -> list[str]:
    """Refusals for one commit. Empty list = fine."""
    paths = files_of(repo, sha)
    # README.md documents the directory; everything else at the outbox root is an item and must
    # be shaped like one. (Measured on this mechanism's own first push: the README tripped it.)
    # Items are validated from ADDED/MODIFIED paths only: the steward's own sent/ move DELETES the
    # root item, and validating a deleted path ran `git show <sha>:<path>` on nothing -- the guard
    # refused the steward's landing commit on this mechanism's first live drain.
    present = set(files_of(repo, sha, "AM"))
    added = [p for p in paths if p in present and p.startswith(OUTBOX_DIR + "/")
             and not p.startswith(SENT_DIR + "/") and p != OUTBOX_DIR + "/README.md"]
    hits = touches_finding_paths(paths)
    trailer = trailer_of(repo, sha)
    problems = []
    if hits and trailer is None:
        problems.append(f"{sha[:10]} touches {hits[0]} and carries no '{TRAILER}:' trailer "
                        f"(write '{TRAILER}: none' or '{TRAILER}: outbox' + an item)")
    if trailer is not None and trailer not in TRAILER_VALUES:
        problems.append(f"{sha[:10]} '{TRAILER}: {trailer}' is not one of {TRAILER_VALUES}")
    if trailer == "outbox" and not added:
        problems.append(f"{sha[:10]} declares '{TRAILER}: outbox' but adds no {OUTBOX_DIR}/ item (declared-but-not-filed)")
    for p in added:
        name = p.rsplit("/", 1)[-1]
        if not ITEM_NAME_RE.match(name):
            problems.append(f"{sha[:10]} {p}: name must be <yyyymmdd>-<slug>.md")
            continue
        try:
            item = parse_item(git(repo, "show", f"{sha}:{p}"))
            screen_law4(item["body"])
        except Refusal as e:
            problems.append(f"{sha[:10]} {p}: {e}")
    return problems


def check_range(repo, rev_range: str) -> list[str]:
    rc, out = git(repo, "rev-list", rev_range, check=False)
    if rc:
        return [f"cannot enumerate {rev_range}"]
    problems = []
    for sha in out.split():
        problems.extend(check_commit(repo, sha))
    return problems


# ---------- drain (called by the harvest steward; the only pusher) ----------

def drain(cfg, hr, project: str = "conjugal") -> list[dict]:
    """Publish every unsent item through harvest_runner.publish_bus, then move it to sent/
    through harvest_runner.land_conjugal. `hr` is the imported harvest_runner module so this
    file owns no second pusher and no second commit gateway. Returns one row per item."""
    repo, bus = pathlib.Path(cfg["conjugal_repo"]), pathlib.Path(cfg["bus_repo"])
    rows = []
    items = unsent_items(repo)
    if not items:
        return rows
    hr.git(bus, "fetch", "--quiet", "origin", "+refs/heads/master:refs/remotes/origin/master")
    tip = hr.git(bus, "rev-parse", "refs/remotes/origin/master")
    for it in items:
        row = {"path": it["path"]}
        if "error" in it:
            row.update(result="OUTBOX_ITEM_INVALID", detail=it["error"])
            rows.append(row); continue
        item, src = it["item"], it["source_commit"]
        if src == "PENDING":
            row.update(result="OUTBOX_NOT_COMMITTED"); rows.append(row); continue
        try:
            screen_law4(item["body"])
        except Refusal as e:
            row.update(result=e.code, detail=e.detail); rows.append(row); continue
        target = item["meta"]["target"]
        key, block = render_block(item, src, project)
        on_bus = hr.blob_at(bus, tip, target) and f"outbox:{key}" in hr.git(bus, "show", f"{tip}:{target}")
        bus_commit = tip if on_bus else None
        run_dir = pathlib.Path(os.path.expandvars(cfg["state_dir"])) / f"outbox-{key}"
        run_dir.mkdir(parents=True, exist_ok=True)
        run = {"bus_wt": str(bus), "base_bus": tip, "run_dir": str(run_dir), "base_conj": hr.git(repo, "rev-parse", "master")}
        if not on_bus:
            try:
                bus_commit, _ = hr.publish_bus(cfg, {"spec_paths": []}, run, [], {target: block},
                                               f"outbox({project}): {it['path'].rsplit('/', 1)[-1][:-3]} -> {target}",
                                               cfg.get("publish_retries", 4))
            except hr.Refusal as e:
                row.update(result=e.code, detail=e.detail, retry=e.retry); rows.append(row); continue
        # Conjugal side: item -> sent/ with bus_commit recorded. Idempotent because a re-run
        # finds the key on the bus tip and only performs this move.
        name = it["path"].rsplit("/", 1)[-1]
        stage = run_dir / "conj"
        sent_rel = f"{SENT_DIR}/{name}"
        text = git(repo, "show", f"master:{it['path']}")
        stamped = text.replace("\n---\n", f"\nbus_commit: {bus_commit}\nsource_commit_resolved: {src}\n---\n", 1)
        (stage / sent_rel).parent.mkdir(parents=True, exist_ok=True)
        (stage / sent_rel).write_text(stamped, encoding="utf-8", newline="\n")
        run["conj_wt"] = str(stage)
        try:
            cand = hr.land_conjugal(cfg, run, [("A", sent_rel), ("D", it["path"])],
                                    f"coord(outbox): {name[:-3]} landed on bus {bus_commit[:12]}\n\n{TRAILER}: none\n")
        except hr.Refusal as e:
            row.update(result="OUTBOX_ON_BUS_MOVE_REFUSED", bus_commit=bus_commit, detail=f"{e.code} {e.detail}", retry=True)
            rows.append(row); continue
        row.update(result="OUTBOX_PUBLISHED", bus_commit=bus_commit, key=key, conjugal_commit=cand)
        rows.append(row)
    return rows


# ---------- CLI ----------

def debt_report(repo) -> tuple[int, str]:
    items = unsent_items(repo)
    if not items:
        return 0, "[outbox] no unsent doctrine items"
    now = datetime.now(timezone.utc)
    lines = [f"[outbox] {len(items)} unsent doctrine item(s) -- the harvest steward drains every 15 min; "
             f"'python coordination/harvest/harvest_runner.py status' shows why if one is old:"]
    for it in items:
        age = f"{int((now - it['added_at']).total_seconds() // 60)} min" if it.get("added_at") else "uncommitted"
        lines.append(f"  {it['path']}  ({it.get('error') or it['item']['meta']['target']}, {age})")
    return len(items), "\n".join(lines)


def check_backlog(repo, max_age_min: int = 60) -> tuple[list, str]:
    """Unsent items older than the window. The steward ticks every 15 min, so an item unsent for
    60 min has missed at least three drains: that names a stuck seam, not a queue. `debt` stays
    "any unsent = 1"; a gate needs this age form so a just-committed item is not a red bar."""
    items = unsent_items(repo)
    now = datetime.now(timezone.utc)
    stale = [it for it in items if it.get("added_at") and (now - it["added_at"]).total_seconds() > max_age_min * 60]
    _, text = debt_report(repo)
    if stale:
        text += (f"\n[outbox] REFUSED: {len(stale)} item(s) unsent for > {max_age_min} min -- "
                 f"the drain is not running or is refusing; read step=outbox receipts")
    return stale, text


def install_pre_push(repo) -> str:
    """Idempotently splice the outbox guard into .git/hooks/pre-push. Machine-local, so the
    SessionStart hook does this on every machine and every rotation without being asked."""
    # Resolve through git: in a linked worktree `.git` is a FILE and hooks live in the common dir;
    # `<repo>/.git/hooks/pre-push` raised FileNotFoundError from every worktree SessionStart.
    hook = pathlib.Path(git(repo, "rev-parse", "--path-format=absolute", "--git-path", "hooks/pre-push"))
    hook.parent.mkdir(parents=True, exist_ok=True)
    marker = "# doctrine-outbox-guard"
    snippet = (f"\n{marker}: findings reach the bus by file; a FINDING_PATHS commit must declare.\n"
               f"python \"$REPO_ROOT/coordination/tools/doctrine_outbox.py\" pre-push \"$REPO_ROOT\" \"$@\" || exit $?\n")
    current = hook.read_text(encoding="utf-8") if hook.exists() else "#!/bin/sh\nset -e\nREPO_ROOT=$(git rev-parse --show-toplevel)\n"
    if marker in current:
        return "present"
    lines = current.splitlines(True)
    # Before the LFS layer if it is there (LFS reads stdin, which we do not touch, but keep the
    # refusing guard ahead of a layer that may exit 2 for an unrelated reason).
    idx = next((i for i, l in enumerate(lines) if "git lfs pre-push" in l or "command -v git-lfs" in l), len(lines))
    lines.insert(idx, snippet)
    hook.write_text("".join(lines), encoding="utf-8", newline="\n")
    return "installed"


def cmd_pre_push(repo, argv) -> int:
    """git passes <remote> <url> as argv and ref lines on stdin: <local-ref> <local-sha> <remote-ref> <remote-sha>."""
    problems = []
    for line in sys.stdin.read().splitlines():
        parts = line.split()
        if len(parts) != 4:
            continue
        local_ref, local_sha, remote_ref, remote_sha = parts
        if remote_ref != "refs/heads/master" or set(local_sha) == {"0"}:
            continue
        rng = f"{remote_sha}..{local_sha}" if set(remote_sha) != {"0"} else local_sha
        problems.extend(check_range(repo, rng))
    if problems:
        print("[outbox] PUSH REFUSED -- doctrine export is declared per commit, not remembered:", file=sys.stderr)
        for p in problems:
            print("  " + p, file=sys.stderr)
        print(f"  see {OUTBOX_DIR}/README.md", file=sys.stderr)
        return 1
    return 0


def cmd_stop(repo) -> int:
    """Stop hook: block ONCE (stop_hook_active ends the loop) when a commit from the last 24 h on
    master would be refused at push. A nudge at the seam the session is standing on; the
    refusing gate is pre-push."""
    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}
    if data.get("stop_hook_active"):
        return 0
    since = int(time.time()) - 24 * 3600
    rc, out = git(repo, "rev-list", f"--since={since}", "master", check=False)
    problems = []
    for sha in (out or "").split():
        problems.extend(check_commit(repo, sha))
    if not problems:
        return 0
    print(json.dumps({"decision": "block",
                      "reason": ("A commit from the last 24 h will be refused at push by the doctrine-outbox guard. "
                                 "Fix it now (a follow-up commit is fine; never rewrite history): "
                                 + " | ".join(problems[:4]) + f" -- see {OUTBOX_DIR}/README.md")}))
    return 0


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__); return 0
    cmd, rest = argv[0], argv[1:]
    repo = pathlib.Path(rest[0]) if rest else pathlib.Path(__file__).resolve().parents[2]
    try:
        if cmd == "debt":
            n, text = debt_report(repo); print(text); return 1 if n else 0
        if cmd == "check":
            stale, text = check_backlog(repo, int(rest[1]) if len(rest) > 1 else 60)
            print(text); return 1 if stale else 0
        if cmd == "check-range":
            problems = check_range(repo, rest[1] if len(rest) > 1 else "origin/master..master")
            print("\n".join(problems) or "[outbox] range clean"); return 1 if problems else 0
        if cmd == "pre-push":
            return cmd_pre_push(repo, rest[1:])
        if cmd == "stop":
            return cmd_stop(repo)
        if cmd == "session-start":
            print(f"[outbox] pre-push guard: {install_pre_push(repo)}")
            n, text = debt_report(repo); print(text); return 0   # informational; never blocks a session start
        if cmd == "install-hooks":
            print(install_pre_push(repo)); return 0
    except Refusal as e:
        print(f"[outbox] {e}", file=sys.stderr); return 2
    print(f"unknown command {cmd}", file=sys.stderr); return 2


if __name__ == "__main__":
    sys.exit(main())
