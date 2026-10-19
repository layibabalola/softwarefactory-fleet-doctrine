#!/usr/bin/env python3
"""session-checkpoint: the fleet's one machine-local session checkpoint hook (canonical; config by data).

Run from pinned bus bytes, never copied (tools/factory/README.md). One command serves every event,
which it reads from the hook payload's hook_event_name (else the positional EVENT argument):

    python -I "$CLAUDE_PROJECT_DIR/factory-pins/pin-runner.py" --never-block run session-checkpoint -- \
        --config "$CLAUDE_PROJECT_DIR/factory-pins/session-checkpoint.config.json"

  SessionStart  keep an account rotation as a marker and print its notice while it stands; snapshot
                this session's starting dirt; re-seed ~/.claude/ROTATION.md from the repo's tracked
                runbook when missing; with a "doctrine" block, print the bus commits the session has
                not been shown; list dirty or ahead worktrees (parallel, under a deadline); list the
                newest checkpoints.
  Stop          write ~/.claude/session-checkpoints/<repo-slug>/SESSION-<id>.md: a pointer-only record of
                branch, HEAD, account and the files this session dirtied and has not committed (dirty now,
                not dirty at SessionStart). Machine-local, outside the repo; survives an account rotation.
  PreToolUse    with a "doctrine" block only: the periodic doctrine re-check for long-running sessions
                (formerly tools/doctrine-periodic.py; Conjugal's 2026-09-20 mechanism). A tick, never a
                gate: throttled per session, prints hookSpecificOutput.additionalContext only when there is
                something new or the check failed.

Never blocks, never runs a git write, always exits 0: an internal error is printed into the delivered output
(a hook that exits non-zero delivers none of what it printed). stdout is UTF-8. Stdlib only; Windows and POSIX.

Config (JSON, schema "session-checkpoint.v1"; every key optional; "_"-prefixed keys are comments; a
relative path resolves against the config file's directory, "~" against the user's home). An unusable
config is reported in the output and the defaults are used, so the checkpoint is still written.
  deadline_seconds    bound on the SessionStart git work, so the hook ends inside its own timeout (40)
  runbook_candidates  repo-relative tracked runbooks; the first present re-seeds ~/.claude/ROTATION.md
  nested_repo_search  when the session cwd is not a git repository, use the child directory that is one,
                      ranked: the child the folder is named after, then non-dotted, then by name (false)
  rotation            {"resume_receipts": DIR, "receipt_pattern": REGEX, "resume_hint": TEXT, "receipt_writer": TEXT}
                      Without resume_receipts the notice is printed at the next SessionStart and then
                      cleared (the marker is written before the account moves, so a crash cannot lose it).
                      With it, the notice repeats at every SessionStart until a file in DIR whose name
                      fully matches receipt_pattern (default (\\d{8}-\\d{4})\\.md, group 1 = UTC
                      yyyymmdd-hhmm) is stamped after the minute the rotation was recorded. resume_hint
                      (default "resume our work" in quotes) and receipt_writer (default "the resume") name,
                      in the notice, what to run and what writes the receipt.
  doctrine            absent = no doctrine view and no periodic tick. Keys:
                      bus_clone (required), label, steward_receipts (newest receipts' last
                      `doctrineFoldedThrough: <sha>` is the board's fold cursor), fold_marker (a JSON file
                      whose lastSeen is the fallback cursor), sweep_log (the box sweep's log: staleness and
                      failed pull/heartbeat steps are reported), sweep_stale_hours (3), periodic_minutes (60;
                      env DOCTRINE_RECHECK_MIN wins), hub_dir (the periodic tick speaks only in sessions whose
                      cwd is this directory; default the main checkout of the cwd's repository).

Lineage: v2 is the copy the ROTATION install prompt pasted into each project; DNG's v3 (2026-09-28) kept the
rotation as a marker until a resume receipt (v2 printed a character a cp1252 hook stdout cannot encode, exited 1
on every rotation and had already consumed the notice), bounded the worktree scan (v2 outran the 60 s hook
timeout under load) and added the doctrine view. With no config this file prints what v2 printed.
"""
from __future__ import annotations

import argparse
import calendar
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

SCHEMA = "session-checkpoint.v1"
START = time.monotonic()
DEFAULTS = {
    "deadline_seconds": 40,
    "runbook_candidates": ["docs/ops/ROTATION.md", "knowledge/ROTATION.md", "roadmap/handoff/ROTATION.md",
                           "docs/ROTATION.md"],
    "nested_repo_search": False,
}
DOCTRINE_LABEL = "bus law 3 / fleet candidate R15.5"
RECEIPT_PATTERN = r"(\d{8}-\d{4})\.md"
TOP_KEYS = {"schema", "deadline_seconds", "runbook_candidates", "nested_repo_search", "rotation", "doctrine"}
ROTATION_KEYS = {"resume_receipts", "receipt_pattern", "resume_hint", "receipt_writer"}
DOCTRINE_KEYS = {"bus_clone", "label", "steward_receipts", "fold_marker", "sweep_log", "sweep_stale_hours",
                 "periodic_minutes", "hub_dir"}
DOCTRINE_PATHS = ("bus_clone", "steward_receipts", "fold_marker", "sweep_log", "hub_dir")


class ConfigError(Exception):
    pass


# --- config ------------------------------------------------------------------------------------
def _path(base: Path, value, key: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"{key} must be a non-empty path string")
    p = Path(os.path.expanduser(value))
    return p if p.is_absolute() else (base / p)


def _keys(obj, allowed: set, where: str) -> dict:
    if not isinstance(obj, dict):
        raise ConfigError(f"{where} must be an object")
    extra = {k for k in obj if not k.startswith("_")} - allowed
    if extra:
        raise ConfigError(f"{where} has unknown key(s) {sorted(extra)}")
    return obj


def load_config(path: str | None) -> dict:
    """The effective config: DEFAULTS overlaid by the file. An unreadable file or a wrong schema raises ConfigError (all
    defaults then). Otherwise each top-level key is judged ON ITS OWN: an unusable or unknown key costs only itself (its
    default is used) and is reported in cfg["_warnings"], so one typo cannot switch off nested_repo_search and with it
    the checkpoint of a workspace whose folder is not the repository."""
    cfg = {**DEFAULTS, "rotation": _rotation({}, Path(".")), "doctrine": None, "_warnings": []}
    if not path:
        return cfg
    p = Path(os.path.expanduser(path))
    try:
        raw = json.loads(p.read_text(encoding="utf-8-sig"))
    except Exception as exc:  # OSError, ValueError, RecursionError (a deeply nested file), ...
        raise ConfigError(f"{p}: {exc.__class__.__name__}: {str(exc)[:120]}") from None
    if not isinstance(raw, dict):
        raise ConfigError("the config must be a JSON object")
    if raw.get("schema", SCHEMA) != SCHEMA:
        raise ConfigError(f"schema must be {SCHEMA!r}")
    base = p.resolve().parent
    warn = cfg["_warnings"]
    for k in sorted(k for k in raw if not k.startswith("_")):
        if k not in TOP_KEYS:
            warn.append(f"unknown key {k!r} ignored")
            continue
        if k == "schema":
            continue
        try:
            cfg[k] = _JUDGE[k](raw[k], base)
        except Exception as exc:  # ConfigError, and what validation itself can raise: 10**400 (OverflowError), a
            # receipt pattern nested past the regex parser's limit (RecursionError), ...
            warn.append(f"{k}: {exc.__class__.__name__}: {str(exc)[:160]}; the default is used")
    return cfg


def _deadline(d, _base):
    if type(d) not in (int, float) or not math.isfinite(d) or not 1 <= d <= 600:
        raise ConfigError("deadline_seconds must be a number from 1 to 600")
    return d


def _runbooks(rc, _base):
    if not isinstance(rc, list) or not all(
            isinstance(c, str) and c and not os.path.isabs(c) and not c.startswith(("/", "\\")) and ":" not in c
            and ".." not in re.split(r"[\\/]", c) for c in rc):
        raise ConfigError("runbook_candidates must be a list of repo-relative paths (no drive, root or '..')")
    return rc


def _nested(nr, _base):
    if type(nr) is not bool:
        raise ConfigError("nested_repo_search must be true or false")
    return nr


def _rotation(raw, base):
    rot = dict(_keys(raw, ROTATION_KEYS, "rotation"))
    if "resume_receipts" in rot:
        rot["resume_receipts"] = _path(base, rot["resume_receipts"], "rotation.resume_receipts")
    try:
        rot["receipt_pattern"] = re.compile(rot.get("receipt_pattern", RECEIPT_PATTERN))
    except (re.error, TypeError) as exc:
        raise ConfigError(f"rotation.receipt_pattern: {exc}") from None
    if rot["receipt_pattern"].groups < 1:
        raise ConfigError("rotation.receipt_pattern needs a group capturing the UTC yyyymmdd-hhmm stamp")
    for k in ("resume_hint", "receipt_writer"):
        if k in rot and not (isinstance(rot[k], str) and rot[k].strip()):
            raise ConfigError(f"rotation.{k} must be non-empty text")
    return rot


def _doctrine(raw, base):
    if raw is None:
        return None
    doc = dict(_keys(raw, DOCTRINE_KEYS, "doctrine"))
    if "bus_clone" not in doc:
        raise ConfigError("doctrine needs bus_clone")
    for k in DOCTRINE_PATHS:
        if k in doc:
            doc[k] = _path(base, doc[k], f"doctrine.{k}")
    for k, dflt in (("sweep_stale_hours", 3), ("periodic_minutes", 60)):
        v = doc.get(k, dflt)
        if type(v) not in (int, float) or not math.isfinite(v) or v <= 0:
            raise ConfigError(f"doctrine.{k} must be a positive number")
        doc[k] = v
    doc.setdefault("label", DOCTRINE_LABEL)
    if not isinstance(doc["label"], str):
        raise ConfigError("doctrine.label must be text")
    return doc


_JUDGE = {"deadline_seconds": _deadline, "runbook_candidates": _runbooks, "nested_repo_search": _nested,
          "rotation": _rotation, "doctrine": _doctrine}


# --- git (read-only) ---------------------------------------------------------------------------
class Ctx:
    """Per-run state: the config and the one deadline every bounded git call shares."""

    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.deadline = cfg["deadline_seconds"]

    def git(self, cwd, *args, deadline=False):
        """stdout of a read-only git call, "" on failure. With deadline=True the call is bounded by the
        deadline and returns None when the deadline cut it off, so the caller can say what it missed."""
        timeout = 60
        if deadline:
            timeout = self.deadline - (time.monotonic() - START)
            if timeout <= 0:
                return None
        try:
            p = subprocess.run(["git", "-C", str(cwd), "--no-optional-locks", *args],
                               capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
            return p.stdout.strip() if p.returncode == 0 else ""
        except subprocess.TimeoutExpired:
            return None if deadline else ""
        except Exception:
            return ""

    def dirt(self, cwd, deadline=False):
        """Modified tracked files (worktree vs index, and staged: index vs HEAD) plus untracked ones; None when the
        deadline cut any call off. v2 and v3 read the first and last only, so a staged-only file was in neither the
        snapshot nor the Stop inventory."""
        diff = self.git(cwd, "diff", "--name-only", deadline=deadline)
        staged = self.git(cwd, "diff", "--cached", "--name-only", deadline=deadline)
        others = self.git(cwd, "ls-files", "--others", "--exclude-standard", deadline=deadline)
        if diff is None or staged is None or others is None:
            return None
        return set(diff.splitlines()) | set(staged.splitlines()) | set(others.splitlines())

    def worktree_scan(self, repo):
        listing = self.git(repo, "worktree", "list", "--porcelain", deadline=True)
        if listing is None:
            return ["  (not scanned: the hook's deadline passed first; derive with `git worktree list`)"]
        paths = [l[9:] for l in listing.splitlines() if l.startswith("worktree ")]
        if not paths:
            return []
        main = self.git(paths[0], "symbolic-ref", "-q", "--short", "HEAD", deadline=True) or "HEAD"

        def one(p):
            dirty = self.dirt(p, deadline=True)
            ahead = self.git(p, "rev-list", "--count", f"{main}..HEAD", deadline=True) if p != paths[0] else "0"
            return None if dirty is None or ahead is None else (len(dirty), ahead)

        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(one, paths))
        out = [f"  {p}: dirty={r[0]} ahead-of-{main}={r[1] or '?'}"
               for p, r in zip(paths, results) if r and (r[0] or r[1] not in ("", "0"))]
        missed = sum(r is None for r in results)
        if missed:
            out.append(f"  ({missed} of {len(paths)} worktrees not scanned before the {self.deadline} s deadline; "
                       "derive them with `git worktree list` and `git -C <path> status`)")
        return out


def account_id():
    try:
        with open(Path.home() / ".claude.json", encoding="utf-8") as fh:
            d = json.load(fh)
        return str((d.get("oauthAccount") or {}).get("accountUuid") or "")[:8]
    except Exception:
        return ""


# --- account rotation --------------------------------------------------------------------------
def rotation_notice(rot: dict, base: Path, home: Path, acct: str) -> tuple[str, bool]:
    """Keep an account change as a marker, and return (notice, clear_after_print). The marker is written
    before .account moves, so a hook that dies at any later point cannot lose the rotation. With resume
    receipts configured, only a receipt stamped after the marker clears it; without, printing does."""
    seen, marker = base / ".account", base / ".rotation-pending"
    receipts = rot.get("resume_receipts")
    if marker.exists() and receipts is not None:
        recorded = time.strftime("%Y%m%d-%H%M", time.gmtime(marker.stat().st_mtime))
        try:
            stamps = [m.group(1) for m in map(rot["receipt_pattern"].fullmatch, os.listdir(receipts)) if m and m.group(1)]
        except OSError:
            stamps = []
        if any(s > recorded for s in stamps):
            marker.unlink(missing_ok=True)          # a concurrent SessionStart may have cleared it first
    prev = seen.read_text(encoding="utf-8").strip() if seen.exists() else ""
    if prev and acct and prev != acct:
        chain = marker.read_text(encoding="utf-8").strip() if marker.exists() else prev
        marker.write_text(f"{chain} -> {acct}\n", encoding="utf-8")
    if acct:
        seen.write_text(acct, encoding="utf-8")
    if not marker.exists():
        return "", False
    chain = marker.read_text(encoding="utf-8").strip()
    if receipts is None:
        return f"ACCOUNT ROTATION DETECTED ({chain}): read {home / 'ROTATION.md'} section 4 before deriving anything.", True
    since = time.strftime("%Y-%m-%dT%H:%MZ", time.gmtime(marker.stat().st_mtime))
    hint = rot.get("resume_hint") or "\"resume our work\""
    return (f"ACCOUNT ROTATION DETECTED ({chain}, recorded {since}) and not yet resumed. In an attended session: "
            f"read {home / 'ROTATION.md'} section 4, then {hint}. Nothing reopens the previous account's sessions "
            f"on its own. This line repeats until {rot.get('receipt_writer') or 'the resume'} writes its receipt; a scheduled seat "
            "ignores it."), False


# --- doctrine view (bus law 3 / candidate R15.5) -----------------------------------------------
def session_tips() -> Path:
    return Path.home() / ".claude" / "session-checkpoints" / "doctrine-periodic"


def fold_cursor(doc: dict):
    """The board's fold cursor, from the artifact that advances it: the LAST `doctrineFoldedThrough` in the newest
    steward receipt that has one; the fold marker is the fallback. Returns (sha, source) or (None, reason)."""
    if doc.get("steward_receipts") is not None:
        try:
            rcpts = sorted((f for f in doc["steward_receipts"].glob("2*.md") if ".lane" not in f.name), reverse=True)[:6]
            for f in rcpts:
                ms = re.findall(r"doctrineFoldedThrough:\s*`?([0-9a-f]{40})", f.read_text(encoding="utf-8", errors="replace"))
                if ms:
                    return ms[-1], f"steward receipt {f.stem}"
        except OSError:
            pass
    mk = doc.get("fold_marker")
    if mk is not None and mk.exists():
        try:
            return json.loads(mk.read_text(encoding="utf-8")).get("lastSeen"), "doctrine-sync marker"
        except Exception:
            pass
    return None, "no fold cursor found"


def sweep_state(log: Path):
    """(hours since the box sweep last ran, last heartbeat step line, last pull step line) from the sweep's own log."""
    try:
        lines = log.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return None, "no sweep log", ""
    stamps = [ln.split(" ", 1)[0] for ln in lines if re.match(r"\d{4}-\d{2}-\d{2}T", ln)]
    hb = next((ln for ln in reversed(lines) if " step=heartbeat " in ln), "")
    pull = next((ln for ln in reversed(lines) if " step=pull " in ln), "")
    if not stamps:
        return None, "empty sweep log", pull
    last = calendar.timegm(time.strptime(stamps[-1], "%Y-%m-%dT%H:%M:%SZ"))
    return (time.time() - last) / 3600, hb, pull


def _git_bus(ctx: Ctx, *args):
    budget = ctx.deadline - (time.monotonic() - START) - 1
    if budget < 1:
        raise TimeoutError("hook time budget spent")
    r = subprocess.run(["git", "-C", str(ctx.cfg["doctrine"]["bus_clone"]), *args], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=budget)
    if r.returncode != 0:
        raise RuntimeError(((r.stderr or r.stdout).strip().splitlines() or [f"git {args[0]} rc={r.returncode}"])[-1])
    return r.stdout


def doctrine_view(ctx: Ctx, sid: str, periodic: bool):
    """Lines to show, and the bus tip they cover. SessionStart: from the OLDER of this session's last-shown tip and the
    board's fold cursor (nothing the steward folds between a session's events can slip past it). Periodic: from this
    session's last-shown tip only, and nothing at all when there is nothing new."""
    doc = ctx.cfg["doctrine"]
    out = []
    tip = _git_bus(ctx, "rev-parse", "--verify", "refs/remotes/origin/master").strip()
    cur, src = fold_cursor(doc)
    seen = None
    tp = session_tips() / f"{sid}.tip"
    if tp.exists():
        seen = tp.read_text(encoding="utf-8").strip() or None
        if seen is not None and not re.fullmatch(r"[0-9a-f]{40}", seen):
            seen = None                             # a torn or foreign tip file never fails every later check
        if seen is not None:
            try:
                _git_bus(ctx, "cat-file", "-e", f"{seen}^{{commit}}")
            except RuntimeError:
                seen = None                         # not in this clone (re-cloned bus): count from the fold cursor
    start, basis = None, ""
    if periodic and seen:
        start, basis = seen, "since this session was last shown the bus"
    elif cur and seen:
        try:
            _git_bus(ctx, "merge-base", "--is-ancestor", seen, cur)
            start, basis = seen, "since this session was last shown the bus (older than the board's fold cursor)"
        except RuntimeError:
            start, basis = cur, f"after the board's fold cursor {cur[:8]} ({src})"
    elif cur:
        start, basis = cur, f"after the board's fold cursor {cur[:8]} ({src})"
    elif seen:
        start, basis = seen, "since this session was last shown the bus"
    if start:
        _git_bus(ctx, "cat-file", "-e", f"{start}^{{commit}}")
        rng = f"{start}..{tip}"
    else:
        rng, basis = tip, f"{src}: full history counted"
    total = int(_git_bus(ctx, "rev-list", "--count", rng).strip() or 0)
    rulings = [ln for ln in _git_bus(ctx, "log", "--full-history", "--format=%h %ad %s", "--date=short", rng, "--",
                                     "RULINGS.md").splitlines() if ln.strip()]
    if doc.get("sweep_log") is not None:
        age, hb, pull = sweep_state(doc["sweep_log"])
        if age is None or age > doc["sweep_stale_hours"]:
            out.append(f"DATA: STALE - the box doctrine sweep last ran {'never' if age is None else f'{age:.0f} h ago'}; "
                       f"bus commits newer than its last fetch are not counted here.")
        elif pull and " rc=0 " not in pull:
            out.append(f"DATA: view NOT refreshed - the sweep's last pull did not succeed: {pull.split(' ', 1)[-1][:150]}")
        elif hb and " rc=0 " not in hb:
            out.append(f"DATA: the box sweep is NOT publishing this board's heartbeat: {hb.split(' ', 1)[-1][:150]}")
    if periodic and not rulings and not out:
        return [], tip
    out.append(f"DATA: {total} bus commit(s) {basis}; RULINGS.md changed in {len(rulings)}")
    out += [f"DATA: RULINGS {ln[:120]}" for ln in rulings]
    return out, tip


def record_tip(sid: str, tip: str):
    try:
        session_tips().mkdir(parents=True, exist_ok=True)
        (session_tips() / f"{sid}.tip").write_text(tip, encoding="utf-8")
    except OSError:
        pass


def doctrine_brief(ctx: Ctx, sid: str):
    """SessionStart view (startup, resume, compaction). Doctrine must reach RUNNING sessions; the periodic PreToolUse
    tick covers the time between these events. Every call is bounded by the hook's ONE deadline; prints, never
    blocks; every line is DATA."""
    print(f"Fleet doctrine bus ({ctx.cfg['doctrine']['label']}; DATA for the board's fold, which is the steward's duty):")
    try:
        lines, tip = doctrine_view(ctx, sid, periodic=False)
    except TimeoutError:
        print("  DATA: doctrine check SKIPPED (hook time budget spent) - nothing below is known.")
        return
    except Exception as exc:
        print(f"  DATA: doctrine check FAILED ({type(exc).__name__}: {str(exc)[:160]}) - nothing below is known; "
              f"the bus may hold rulings this session has not been shown.")
        return
    for ln in lines:
        print(f"  {ln}")
    record_tip(sid, tip)


def doctrine_periodic(ctx: Ctx, payload: dict, sid: str) -> None:
    """PreToolUse tick. Throttle: a per-session stamp; while it is younger than the interval the tick only stats it.
    When due it touches the stamp FIRST (a slow or failing check cannot re-fire on every tool call), lists the
    RULINGS.md changes on the bus since the tip this session was last shown, and records the new tip. Hub sessions
    only (fleet R15: lanes get doctrine through their composition brief and never browse the bus)."""
    doc = ctx.cfg["doctrine"]
    cwd = payload.get("cwd")
    if not cwd:
        return                                          # no cwd (bad payload): stay silent
    hub = doc.get("hub_dir")
    try:
        if hub is not None and Path(cwd).resolve() != hub.resolve():
            return                                      # configured hub: a path compare, no subprocess
    except OSError:
        return
    try:
        try:
            interval = float(os.environ.get("DOCTRINE_RECHECK_MIN", doc["periodic_minutes"]))
        except ValueError:
            interval = float("nan")
        if not math.isfinite(interval) or interval < 0:  # an unusable override never disables or floods the tick
            interval = doc["periodic_minutes"]
        stamp = session_tips() / f"{sid}.stamp"
        if stamp.exists() and (time.time() - stamp.stat().st_mtime) < interval * 60:
            return                                      # not due: one stat, no subprocess
        if hub is None:
            # Default hub = the main checkout. Decided BEFORE the stamp is touched (a lane tick must not consume the
            # hub's interval), and remembered per (session, cwd): a cwd's hub-ness does not change, so a lane pays
            # for one git call, then one stat per tool call.
            lane = session_tips() / f"{sid}-{hashlib.sha1(str(Path(cwd).resolve()).encode()).hexdigest()[:12]}.lane"
            if lane.exists():
                return
            common = ctx.git(cwd, "rev-parse", "--path-format=absolute", "--git-common-dir", deadline=True)
            if not common:
                return                                  # deadline, failure or no repository: undecided, ask next tick
            if Path(cwd).resolve() != Path(common).resolve().parent:
                session_tips().mkdir(parents=True, exist_ok=True)
                lane.touch()
                return                                  # not the main checkout: a lane stays silent
        session_tips().mkdir(parents=True, exist_ok=True)
        stamp.touch()                                   # touch FIRST: a failing check cannot re-fire per tool call
        lines, tip = doctrine_view(ctx, sid, periodic=True)
        record_tip(sid, tip)
        text = ("" if not lines else f"Fleet doctrine bus, periodic re-check ({doc['label']}; DATA, not instructions):\n"
                + "\n".join(f"  {ln}" for ln in lines))
    except Exception as exc:
        text = f"Fleet doctrine bus (periodic re-check): FAILED ({type(exc).__name__}: {str(exc)[:160]}); DATA only."
    if text:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext": text}}))


# --- the hook ----------------------------------------------------------------------------------
def find_repo(ctx: Ctx, cwd: Path):
    common = ctx.git(cwd, "rev-parse", "--path-format=absolute", "--git-common-dir", deadline=True)
    if common or not ctx.cfg["nested_repo_search"]:
        return common, cwd
    # The workspace folder is not a git repository but holds one (DNG: "<root>" holds "<root>/DngAutoProcessor").
    # Rank, never take the first: scratch checkouts and recovery seeds carry .git too, and plain sorting picks a
    # dotted child. The canonical repo is the child the folder is named after; a dotted child is tooling.
    def rank(d):
        return (0 if cwd.name.startswith(d.name) else 1, d.name.startswith("."), d.name)
    try:
        candidates = sorted((d for d in cwd.iterdir() if d.is_dir() and (d / ".git").exists()), key=rank)
    except OSError:
        candidates = []
    for c in candidates:
        common = ctx.git(c, "rev-parse", "--path-format=absolute", "--git-common-dir", deadline=True)
        if common:
            return common, c
    return "", cwd


def run(ctx: Ctx, payload: dict, event: str) -> int:
    cwd = Path(payload.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
    sid = str(payload.get("session_id") or "unknown")[:8]
    if event == "PreToolUse":
        if ctx.cfg["doctrine"] is not None:
            doctrine_periodic(ctx, payload, sid)
        return 0
    if event not in ("SessionStart", "Stop"):
        return 0
    common, cwd = find_repo(ctx, cwd)
    if not common:
        return 0
    repo = Path(common).parent
    home = Path.home() / ".claude"
    base = home / "session-checkpoints" / repo.name.replace(" ", "-")
    base.mkdir(parents=True, exist_ok=True)
    snap = base / f".snap-{sid}.json"
    acct = account_id()
    if event == "SessionStart":
        notice, clear = rotation_notice(ctx.cfg["rotation"], base, home, acct)
        dirty = ctx.dirt(cwd, deadline=True)
        if dirty is not None:
            snap.write_text(json.dumps(sorted(dirty)), encoding="utf-8")
        if not (home / "ROTATION.md").exists():
            for c in ctx.cfg["runbook_candidates"]:
                if (repo / c).exists():
                    shutil.copyfile(repo / c, home / "ROTATION.md")
                    break
        if notice:
            print(notice)
            sys.stdout.flush()
            if clear:
                (base / ".rotation-pending").unlink(missing_ok=True)
        if ctx.cfg["doctrine"] is not None:
            doctrine_brief(ctx, sid)
        scan = ctx.worktree_scan(repo)
        if scan:
            print(f"Worktrees of {repo.name} with uncommitted or unintegrated work:")
            print("\n".join(scan))
        files = sorted(base.glob("SESSION-*.md"), key=lambda p: p.stat().st_mtime, reverse=True)[:5]
        if files:
            print(f"Session checkpoints for {repo.name} (newest first, pointer-only, machine-local):")
            for f in files:
                print(f"  {f}")
        return 0
    dirty = ctx.dirt(cwd) or set()
    before = set(json.loads(snap.read_text(encoding="utf-8"))) if snap.exists() else set()
    owned = sorted(dirty - before)
    branch = ctx.git(cwd, "symbolic-ref", "-q", "--short", "HEAD") or "(detached)"
    head = ctx.git(cwd, "rev-parse", "--short", "HEAD")
    subject = ctx.git(cwd, "log", "-1", "--format=%s")[:120]
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    out = base / f"SESSION-{sid}.md"
    lines = [f"# SESSION-{sid} checkpoint (pointer-only, written mechanically at every turn end)", "",
             f"- written: {ts}", f"- account: {acct or 'unknown'}", f"- repo: {repo}", f"- cwd: {cwd}",
             f"- branch: {branch} @ {head}", f"- last commit: {subject}",
             f"- files this session dirtied and has NOT committed ({len(owned)}):"]
    lines += [f"  - {p}" for p in owned] or ["  - none"]
    lines += ["", "Resume: read the repo entry file, then `git log -5 <branch>`; the list above is what a rotation would lose."]
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    if owned:
        print(f"checkpoint: {len(owned)} uncommitted file(s) from this session recorded at {out}")
    return 0


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdin, sys.stdout):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    try:
        ap = argparse.ArgumentParser(description=__doc__.splitlines()[0], allow_abbrev=False)
        ap.add_argument("event", nargs="?", default="", help="used when the payload names no hook_event_name")
        ap.add_argument("--config", help=f"a {SCHEMA} JSON file (default: no file, every default)")
        a = ap.parse_args(sys.argv[1:] if argv is None else argv)
        try:
            payload = json.load(sys.stdin)
            payload = payload if isinstance(payload, dict) else {}
        except Exception:
            payload = {}
        event = payload.get("hook_event_name") or a.event
        try:
            cfg = load_config(a.config)
        except ConfigError as exc:
            cfg = load_config(None)
            cfg["_warnings"] = [f"unusable ({exc}); running with every default (no doctrine view)"]
        if event != "PreToolUse":
            for w in cfg["_warnings"]:
                print(f"session-checkpoint: config {w}")
        return run(Ctx(cfg), payload, event)
    except SystemExit as exc:
        if exc.code not in (0, None):
            print("session-checkpoint: bad arguments; nothing done")
        return 0
    except Exception as exc:
        # A non-zero exit makes the harness drop everything already printed (how v2 lost its rotation notice),
        # so the error travels inside the delivered output and the exit stays 0.
        print(f"session-checkpoint failed ({type(exc).__name__}: {exc}); "
              "whatever it would have printed or written after that point is missing")
        return 0


if __name__ == "__main__":
    sys.exit(main())
