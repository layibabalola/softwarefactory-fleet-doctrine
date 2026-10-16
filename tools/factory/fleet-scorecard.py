#!/usr/bin/env python3
"""fleet-scorecard: one mechanical daily health row per fleet project (no model calls).

Owner goal 2026-10-16: every fleet project publishes a DAILY scorecard to the bus so a weekly fleet-wide
review can read trends. This tool MEASURES and PUBLISHES; it never gates (metrics/README.md law 1): no
field value ever changes the exit code, and nothing may cite a row as authority or grade a lane on it.

Each row (schema fleet/scorecard-row/v1, documented in README.md "Fleet scorecard") carries, per field,
the value, the command that produced it and, when the value is null, why. A missing tool, file or
config section yields a null field, never a failure.

Other bus tools are CALLED, never reimplemented, and only through the project's pins
(`<pins dir>/pin-runner.py run <tool>`; bus Law 1: bus bytes run only after review + pin). An
unpinned tool is a null field with error NOT_PINNED. Project commands named in the project's own
config run in the project root (the project's own reviewed code).

Config (JSON, schema fleet/scorecard-config/v1; default <root>/factory-pins/fleet-scorecard.config.json,
an absent file means built-in defaults): either ONE project object or {"projects": [...]}, each project:
  name, root (default: --root), config (a file in that root whose project object overrides this one),
  census_root, branch, remote, rule_tags{config,project}, fold{marker,queue,status_field,
  queued_states,pending_states,queued_field,expires_field}, outbox{argv|pinned,args,regex,zero_regex},
  evidence_dumps{same source spec}, kernel{ref,delivered_regex,refused_regex,window_hours},
  pins (pins file, default <root>/factory-pins/factory-pins.json)
See tools/factory/fixtures/fleet-scorecard/ for the three projects' configs.

Run:
  python tools/factory/fleet-scorecard.py --root . --project <name> [--config F] [--bus DIR]
         [--publish] [--out FILE] [--now ISO] [--json]
  python factory-pins/pin-runner.py run fleet-scorecard -- --root . --project <name> --publish

Exit: 0 rows produced (and published or already present when --publish); 2 usage/config error, or a
row refused by the publish screen; 3 the bus clone is unavailable or the push failed after retries.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROW_SCHEMA = "fleet/scorecard-row/v1"
CONFIG_SCHEMA = "fleet/scorecard-config/v1"
OUTPUT = "metrics/scorecard-daily.jsonl"
GENERATOR = "tools/factory/fleet-scorecard.py"
DEFAULT_CONFIG = "factory-pins/fleet-scorecard.config.json"
DEFAULT_PINS = "factory-pins/factory-pins.json"
TIMEOUT = 300
FIELDS = ("tool_census", "rule_tags", "evidence_dumps", "product_share", "doctrine_fold", "outbox_unsent",
          "commits_no_remote", "master_vs_origin", "kernel_24h", "pin_stale")

# The publish screen (bus Law 4: no coordination surfaces, transcripts, credentials or addresses travel).
# A row is refused, never edited, when any pattern matches its serialized bytes.
SCREEN = (
    ("email address", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),
    ("account/org uuid", re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", re.I)),
    ("bearer/API token", re.compile(r"\b(sk-ant-|pk1:|gh[pousr]_[A-Za-z0-9]{20,}|Bearer\s+[A-Za-z0-9._-]{20,})")),
    ("user home path", re.compile(r"(?:[A-Za-z]:[\\/]+Users[\\/]+|/Users/|/home/)[^\s\\/\"]+", re.I)),
    ("project coordination path", re.compile(r"coordination[\\/]")),
    ("HUB heartbeat", re.compile(r"\bHUB\.md\b")),
)


class ConfigError(Exception):
    pass


class Unavailable(Exception):
    pass


# ---------- small helpers ----------

def utc(t: dt.datetime) -> str:
    return t.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_ts(s: str) -> dt.datetime:
    t = dt.datetime.fromisoformat(s.strip().replace("Z", "+00:00"))
    return t if t.tzinfo else t.replace(tzinfo=dt.timezone.utc)


def blob_id(data: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def git(repo, *args, check=False) -> subprocess.CompletedProcess:
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0")
    for k in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"):
        env.pop(k, None)
    p = subprocess.run(["git", "--no-optional-locks", "-C", str(repo), *args], capture_output=True,
                       text=True, encoding="utf-8", errors="replace", env=env, timeout=TIMEOUT)
    if check and p.returncode != 0:
        raise Unavailable(f"git {' '.join(args[:2])} failed: {p.stderr.strip()[:200]}")
    return p


def git_out(repo, *args) -> str | None:
    p = git(repo, *args)
    return p.stdout.strip() if p.returncode == 0 else None


class Ctx:
    """Placeholder rendering: a recorded command names <root>, <bus>, <pins>, never a machine path."""

    def __init__(self, root: Path, bus: Path | None, pins: Path | None, config: Path | None,
                 own_pins: Path | None = None):
        # pins = the EXECUTOR's pins (whose review authorizes running bus tools); own_pins = the measured
        # project's pins (pin_stale). They differ when one project's steward measures a sibling.
        self.root, self.bus, self.pins, self.config = root, bus, pins, config
        self.own_pins = own_pins or pins

    def render(self, parts) -> str:
        subs = [(str(p), tag) for p, tag in ((self.pins.parent if self.pins else None, "<pins>"),
                                             (self.own_pins.parent if self.own_pins and self.own_pins != self.pins
                                              else None, "<own-pins>"),
                                             (self.bus, "<bus>"), (self.config, "<config>"),
                                             (self.root, "<root>"), (Path(sys.executable), "python")) if p]
        subs.sort(key=lambda x: -len(x[0]))
        out = []
        for a in parts:
            s = str(a)
            for raw, tag in subs:
                for form in {raw, raw.replace("\\", "/")}:
                    s = s.replace(form, tag)
            if "<" in s:
                s = s.replace("\\", "/")
            out.append(s if (s and " " not in s) else json.dumps(s))
        return " ".join(out)

    def scrub(self, text: str) -> str:
        return self.render([text]).strip('"')[:240]


def field(value=None, cmd: str = "", error: str | None = None) -> dict:
    return {"value": value, "cmd": cmd, "error": error}


def run_cmd(argv: list[str], cwd: Path) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if k.upper() not in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE")}
    return subprocess.run(argv, cwd=str(cwd), capture_output=True, text=True, encoding="utf-8",
                          errors="replace", env=env, timeout=TIMEOUT)


# ---------- pinned bus tools ----------

def pinned_argv(ctx: Ctx, tool: str) -> list[str] | None:
    """argv prefix that runs a pinned tool through the project's runner, or None when it is not pinned."""
    if not ctx.pins or not ctx.pins.is_file():
        return None
    runner = ctx.pins.parent / "pin-runner.py"
    try:
        pins = json.loads(ctx.pins.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if tool not in (pins.get("tools") or {}) or not runner.is_file():
        return None
    argv = [sys.executable, "-I", str(runner), "--pins", str(ctx.pins)]
    if ctx.bus:
        argv += ["--bus", str(ctx.bus)]
    return argv + ["run", tool, "--"]


def source_argv(ctx: Ctx, spec: dict) -> tuple[list[str] | None, str | None]:
    """A config source spec -> (argv, error). {"pinned": tool, "args": [...]} or {"argv": [...]}."""
    def sub(a):
        return str(a).replace("{root}", str(ctx.root)).replace("{bus}", str(ctx.bus or "")).replace(
            "{python}", sys.executable)
    if spec.get("pinned"):
        pre = pinned_argv(ctx, spec["pinned"])
        if pre is None:
            return None, "NOT_PINNED"
        return pre + [sub(a) for a in spec.get("args") or []], None
    if spec.get("argv"):
        argv = [sub(a) for a in spec["argv"]]
        if argv[0] == "python":
            argv[0] = sys.executable
        return argv, None
    return None, "NOT_CONFIGURED"


def parse_output(spec: dict, p: subprocess.CompletedProcess):
    """Number from a command's stdout: {"json": "a.b"} | {"regex": r"(\\d+)", "zero_regex": r"..."}."""
    out = p.stdout or ""
    if spec.get("json"):
        node = json.loads(out)
        for k in spec["json"].split("."):
            node = node[k]
        return node
    if spec.get("zero_regex") and re.search(spec["zero_regex"], out):
        return 0
    if spec.get("regex"):
        m = re.search(spec["regex"], out)
        if m:
            return int(m.group(1))
        raise ValueError("output matched neither regex nor zero_regex")
    raise ValueError("source has no json or regex parse")


def from_source(ctx: Ctx, spec: dict | None, name: str = "") -> dict:
    if not spec:
        return field(error="NOT_CONFIGURED")
    argv, err = source_argv(ctx, spec)
    if argv is None:
        return field(cmd=f"pinned:{spec.get('pinned')}" if spec.get("pinned") else "", error=err)
    # A pinned bus tool's command is published as run. A project command names project-internal paths
    # (Law 4 keeps them off the bus), so the row cites the config key that holds it; config_sha256 pins it.
    cmd = ctx.render(argv) if spec.get("pinned") else f"fleet-scorecard --field {name} (runs config argv; cwd <root>)"
    try:
        p = run_cmd(argv, ctx.root)
    except (OSError, subprocess.TimeoutExpired) as e:
        return field(cmd=cmd, error=f"FAILED: {ctx.scrub(str(e))}")
    ok = set(spec.get("ok_exit", [0, 1]))
    if p.returncode not in ok:
        return field(cmd=cmd, error=f"FAILED: exit {p.returncode}: {ctx.scrub((p.stderr or p.stdout).strip()[-160:])}")
    try:
        return field(parse_output(spec, p), cmd)
    except (ValueError, KeyError, TypeError, IndexError) as e:
        return field(cmd=cmd, error=f"FAILED: unparseable output ({ctx.scrub(str(e))})")


# ---------- the fields ----------

def f_tool_census(ctx: Ctx, proj: dict) -> dict:
    pre = pinned_argv(ctx, "tool-census")
    if pre is None:
        return field(cmd="pinned:tool-census", error="NOT_PINNED")
    if not ctx.bus:
        return field(cmd="pinned:tool-census", error="ABSENT: no bus clone")
    argv = pre + ["--json", "--config", str(ctx.bus / "tools" / "tool-census.config.json"),
                  "--baseline", str(ctx.bus / "metrics" / "tool-census-baseline.json")]
    cmd = ctx.render(argv)
    try:
        p = run_cmd(argv, ctx.bus)
        rep = json.loads(p.stdout)
    except (OSError, subprocess.TimeoutExpired, ValueError) as e:
        return field(cmd=cmd, error=f"FAILED: {ctx.scrub(str(e))[:160]}")
    name = proj.get("census_root") or proj["name"]
    copies = [c for f in rep.get("families") or [] for c in f.get("copies") or [] if c.get("root") == name]
    baseline = None
    try:
        baseline = json.loads((ctx.bus / "metrics" / "tool-census-baseline.json").read_text(encoding="utf-8")).get("total")
    except (OSError, ValueError):
        pass
    return field({"project_copies": len([c for c in copies if not c.get("canonical")]),
                  "fleet_total": rep.get("total"), "baseline_total": baseline,
                  "measured": name in (rep.get("measuredRoots") or []),
                  "absent_roots": rep.get("absentRoots") or []}, cmd)


def f_rule_tags(ctx: Ctx, proj: dict) -> dict:
    rt = proj.get("rule_tags")
    if not rt:
        return field(error="NOT_CONFIGURED")
    pre = pinned_argv(ctx, "check-rule-tags")
    if pre is None:
        return field(cmd="pinned:check-rule-tags", error="NOT_PINNED")
    cfg = (ctx.root / rt["config"]) if rt.get("config") else (ctx.bus / "tools" / "rule-tags.config.json" if ctx.bus else None)
    if cfg is None or not cfg.is_file():
        return field(cmd="pinned:check-rule-tags", error="NOT_CONFIGURED: no rule-tags config")
    argv = pre + ["--config", str(cfg), "--project", rt.get("project") or proj["name"], "--root", str(ctx.root),
                  "--report", "--json"]
    cmd = ctx.render(argv)
    try:
        p = run_cmd(argv, ctx.root)
    except (OSError, subprocess.TimeoutExpired) as e:
        return field(cmd=cmd, error=f"FAILED: {ctx.scrub(str(e))}")
    if p.returncode != 0:
        return field(cmd=cmd, error=f"FAILED: exit {p.returncode}: {ctx.scrub(p.stderr.strip()[-160:])}")
    try:
        counts = json.loads(p.stdout.strip().splitlines()[0])["counts"]
    except (ValueError, KeyError, IndexError) as e:
        return field(cmd=cmd, error=f"FAILED: unparseable output ({e})")
    return field({k: counts.get(k) for k in ("bullets", "backed", "prose", "untagged", "dangling", "mixed")}, cmd)


def f_product_share(ctx: Ctx, proj: dict) -> dict:
    path = ctx.bus / "metrics" / "product-share-lines.jsonl" if ctx.bus else None
    cmd = ctx.render(["read", str(path or "<bus>/metrics/product-share-lines.jsonl"),
                      f"last-row project={proj.get('census_root') or proj['name']}"])
    if path is None or not path.is_file():
        return field(cmd=cmd, error="ABSENT")
    last = None
    want = proj.get("census_root") or proj["name"]
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if r.get("project") == want:
            last = r
    if last is None:
        return field(cmd=cmd, error="ABSENT: no row for this project")
    return field({"product_share": last.get("product_share"), "product_lines_per_week": last.get("product_lines_per_week"),
                  "window_days": last.get("window_days"), "measured_at": last.get("ts")}, cmd)


def f_doctrine_fold(ctx: Ctx, proj: dict, now: dt.datetime) -> dict:
    fo = proj.get("fold") or {}
    marker = ctx.root / (fo.get("marker") or ".codex-state/doctrine/last-seen.json")
    cmd = f"fleet-scorecard --field doctrine_fold (reads config fold.marker{', fold.queue' if fo.get('queue') else ''})"
    val = {"marker_age_hours": None, "queued": None, "oldest_queued_age_days": None, "overdue": None, "adopt_pending": None}
    errs = []
    try:
        m = json.loads(marker.read_text(encoding="utf-8"))
        val["marker_age_hours"] = round((now - parse_ts(m["lastSeenAt"])).total_seconds() / 3600, 1)
    except (OSError, ValueError, KeyError) as e:
        errs.append(f"marker ABSENT ({type(e).__name__})")
    if fo.get("queue"):
        sf, qf, ef = fo.get("status_field", "status"), fo.get("queued_field", "queued"), fo.get("expires_field", "expires")
        qs, ps = set(fo.get("queued_states", ["QUEUED"])), set(fo.get("pending_states", ["ADOPT-PENDING"]))
        try:
            rows = [json.loads(l) for l in (ctx.root / fo["queue"]).read_text(encoding="utf-8").splitlines() if l.strip()]
            queued = [r for r in rows if r.get(sf) in qs]
            val["queued"] = len(queued)
            val["adopt_pending"] = sum(1 for r in rows if r.get(sf) in ps)
            dates = [dt.date.fromisoformat(r[qf][:10]) for r in queued if r.get(qf)]
            val["oldest_queued_age_days"] = (now.date() - min(dates)).days if dates else None
            val["overdue"] = sum(1 for r in queued if r.get(ef) and dt.date.fromisoformat(r[ef][:10]) < now.date())
        except (OSError, ValueError) as e:
            errs.append(f"queue ABSENT ({type(e).__name__})")
    else:
        errs.append("queue NOT_CONFIGURED")
    if all(v is None for v in val.values()):
        return field(cmd=cmd, error="; ".join(errs))
    return field(val, cmd, "; ".join(errs) or None)


def f_commits_no_remote(ctx: Ctx, proj: dict) -> dict:
    args = ["rev-list", "--count", "--branches", "--not", "--remotes"]
    cmd = ctx.render(["git", "-C", str(ctx.root), *args])
    out = git_out(ctx.root, *args)
    return field(int(out), cmd) if out and out.isdigit() else field(cmd=cmd, error="FAILED")


def f_master_vs_origin(ctx: Ctx, proj: dict) -> dict:
    br, rem = proj.get("branch", "master"), proj.get("remote", "origin")
    args = ["rev-list", "--left-right", "--count", f"refs/heads/{br}...refs/remotes/{rem}/{br}"]
    cmd = ctx.render(["git", "-C", str(ctx.root), *args])
    out = git_out(ctx.root, *args)
    if not out or len(out.split()) != 2:
        return field(cmd=cmd, error="ABSENT: branch or remote-tracking ref missing")
    a, b = out.split()
    return field({"ahead": int(a), "behind": int(b)}, cmd)


def f_kernel(ctx: Ctx, proj: dict, now: dt.datetime) -> dict:
    k = proj.get("kernel")
    if not k:
        return field(error="NOT_CONFIGURED")
    hours = int(k.get("window_hours", 24))
    since = now - dt.timedelta(hours=hours)
    args = ["log", f"--since={utc(since - dt.timedelta(days=7))}", "--format=%aI%x09%s", k.get("ref", "HEAD")]
    cmd = ctx.render(["git", "-C", str(ctx.root), *args]) + f" | author-date >= now-{hours}h; delivered/refused by config kernel regexes"
    p = git(ctx.root, *args)
    if p.returncode != 0:
        return field(cmd=cmd, error="FAILED")
    sets = {"delivered": set(), "refused": set()}
    try:
        rx = {n: re.compile(k[f"{n}_regex"]) for n in sets if k.get(f"{n}_regex")}
    except re.error as e:
        return field(cmd=cmd, error=f"FAILED: bad regex ({e})")
    for line in p.stdout.splitlines():
        when, _, subj = line.partition("\t")
        try:
            if parse_ts(when) < since:
                continue
        except ValueError:
            continue
        for n, r in rx.items():
            m = r.search(subj)
            if m:
                sets[n].add(m.group(1) if m.groups() else subj)
    return field({n: len(v) for n, v in sets.items()}, cmd)


def f_pin_stale(ctx: Ctx, proj: dict) -> dict:
    own = ctx.own_pins
    if not own or not own.is_file() or not (own.parent / "pin-runner.py").is_file():
        return field(error="ABSENT: no pins or pin runner")
    argv = [sys.executable, "-I", str(own.parent / "pin-runner.py"), "--pins", str(own)]
    if ctx.bus:
        argv += ["--bus", str(ctx.bus)]
    argv.append("status")
    cmd = ctx.render(argv) + " | count '*** STALE ***'"
    try:
        p = run_cmd(argv, ctx.root)
    except (OSError, subprocess.TimeoutExpired) as e:
        return field(cmd=cmd, error=f"FAILED: {ctx.scrub(str(e))}")
    if p.returncode != 0 or "UNAVAILABLE" in p.stdout:
        return field(cmd=cmd, error=f"FAILED: exit {p.returncode}")
    return field(sum(1 for l in p.stdout.splitlines() if "*** STALE ***" in l), cmd)


# ---------- config, bus, row ----------

def load_config(root: Path, path: str | None, project: str | None) -> tuple[list[dict], Path | None, str | None]:
    cfg_path = Path(path) if path else root / DEFAULT_CONFIG
    if not cfg_path.is_absolute():
        cfg_path = (Path.cwd() / cfg_path).resolve()
    if not cfg_path.is_file():
        if path:
            raise ConfigError(f"config not found: {path}")
        if not project:
            raise ConfigError("no config file: --project is required")
        return [{"name": project}], None, None
    data = cfg_path.read_bytes()
    try:
        cfg = json.loads(data.decode("utf-8"))
    except ValueError as e:
        raise ConfigError(f"config {cfg_path.name}: {e}")
    if cfg.get("schema") != CONFIG_SCHEMA:
        raise ConfigError(f"config {cfg_path.name}: schema is not {CONFIG_SCHEMA}")
    projects = cfg.get("projects") or [{k: v for k, v in cfg.items() if k != "schema"}]
    for p in projects:
        if not p.get("name"):
            raise ConfigError("every project needs a name")
    if project:
        projects = [p for p in projects if p["name"] == project]
        if not projects:
            raise ConfigError(f"project {project!r} is not in the config")
    return projects, cfg_path, hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def project_root(p: dict, default_root: Path, cfg_path: Path | None) -> Path:
    r = p.get("root")
    if not r or r == ".":
        return default_root
    r = Path(r)
    return r if r.is_absolute() else ((cfg_path.parent if cfg_path else default_root) / r).resolve()


def overlay(p: dict, root: Path) -> dict:
    """A project's own config file (p["config"], in its root) overrides the entry that names it."""
    if not p.get("config"):
        return p
    f = root / p["config"]
    try:
        own = json.loads(f.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return p
    if own.get("schema") != CONFIG_SCHEMA:
        return p
    own = (own.get("projects") or [own])
    match = next((o for o in own if o.get("name") == p["name"]), None)
    if not match:
        return p
    merged = {**p, **{k: v for k, v in match.items() if k not in ("root", "schema")}}
    merged["_own_config"] = p["config"]
    return merged


def find_bus(arg: str | None, pins: Path | None) -> Path | None:
    cands = []
    if arg:
        cands = [arg]
    elif os.environ.get("FACTORY_BUS_CLONE"):
        cands = [os.environ["FACTORY_BUS_CLONE"]]
    elif pins and pins.is_file():
        # Never this script's own checkout: a publish target is always named explicitly (a test run
        # once published a fixture row to the real bus through that fallback, 2026-10-16).
        try:
            bc = json.loads(pins.read_text(encoding="utf-8")).get("bus_clone") or []
            base = pins.parent.parent      # candidates are relative to the consumer root, as pin-runner reads them
            cands = [c if Path(c).is_absolute() else str((base / c).resolve()) for c in
                     ([bc] if isinstance(bc, str) else bc)]
        except (OSError, ValueError):
            pass
    for c in cands:
        if (Path(c) / "metrics").is_dir() and (Path(c) / ".git").exists():
            return Path(c).resolve()
    return None


def own_blob(pins: Path | None) -> str | None:
    f = Path(__file__)
    if f.is_absolute() and f.is_file():     # under the pin runner __file__ is the bus path, not a file
        return blob_id(f.read_bytes().replace(b"\r\n", b"\n"))
    try:
        return json.loads(pins.read_text(encoding="utf-8"))["tools"]["fleet-scorecard"]["blob"]
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return None


def build_row(p: dict, root: Path, bus: Path | None, pins: Path | None, cfg_path, cfg_sha, now: dt.datetime,
              own_pins: Path | None = None) -> dict:
    ctx = Ctx(root, bus, pins, cfg_path, own_pins)
    fields = {
        "tool_census": f_tool_census(ctx, p),
        "rule_tags": f_rule_tags(ctx, p),
        "evidence_dumps": from_source(ctx, p.get("evidence_dumps"), "evidence_dumps"),
        "product_share": f_product_share(ctx, p),
        "doctrine_fold": f_doctrine_fold(ctx, p, now),
        "outbox_unsent": from_source(ctx, p.get("outbox"), "outbox_unsent"),
        "commits_no_remote": f_commits_no_remote(ctx, p),
        "master_vs_origin": f_master_vs_origin(ctx, p),
        "kernel_24h": f_kernel(ctx, p, now),
        "pin_stale": f_pin_stale(ctx, p),
    }
    return {
        "schema": ROW_SCHEMA,
        "date": now.astimezone(dt.timezone.utc).date().isoformat(),
        "ts": utc(now),
        "project": p["name"],
        "project_head": git_out(root, "rev-parse", "HEAD"),
        "bus_commit": git_out(bus, "rev-parse", "refs/remotes/origin/master") if bus else None,
        "generator": {"path": GENERATOR, "blob": own_blob(pins)},
        "config_sha256": cfg_sha,
        "own_config": p.get("_own_config"),
        "fields": fields,
    }


def screen(row: dict) -> str | None:
    text = json.dumps(row, ensure_ascii=False)
    for name, rx in SCREEN:
        m = rx.search(text)
        if m:
            return f"{name}: {m.group(0)[:24]!r}"
    return None


# ---------- publish ----------

def existing_keys(text: str) -> set:
    keys = set()
    for line in text.splitlines():
        try:
            r = json.loads(line)
            keys.add((r.get("project"), r.get("date")))
        except ValueError:
            pass
    return keys


def publish(bus: Path, rows: list[dict], retries: int = 5, remote: str = "origin", branch: str = "master") -> list[str]:
    """Append rows not yet on <remote>/<branch> (idempotency key: project + date) through a private
    temporary worktree of the bus clone; the clone's own checkout is never touched. Fast-forward only:
    a rejected push re-reads the remote and re-appends; nothing is ever forced. Returns lines of report."""
    report = []
    work = Path(tempfile.mkdtemp(prefix="fleet-scorecard-"))
    wt = work / "bus"
    try:
        for attempt in range(1, retries + 1):
            git(bus, "fetch", "-q", remote, branch, check=True)
            base = git_out(bus, "rev-parse", f"refs/remotes/{remote}/{branch}")
            if not base:
                raise Unavailable(f"no {remote}/{branch} in the bus clone")
            if wt.exists():
                git(bus, "worktree", "remove", "--force", str(wt))
            git(bus, "worktree", "add", "-q", "--detach", str(wt), base, check=True)
            target = wt / OUTPUT
            old = target.read_bytes() if target.is_file() else b""
            have = existing_keys(old.decode("utf-8", "replace"))
            new = [r for r in rows if (r["project"], r["date"]) not in have]
            if not new:
                report.append(f"[scorecard] already published for {', '.join(sorted({r['project'] for r in rows}))} "
                              f"on {rows[0]['date'] if rows else '?'}; nothing to push")
                return report
            if old and not old.endswith(b"\n"):
                old += b"\n"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(old + b"".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + b"\n"
                                              for r in new))
            git(wt, "add", "--", OUTPUT, check=True)
            msg = (f"metrics: fleet scorecard {new[0]['date']} - {', '.join(r['project'] for r in new)}\n\n"
                   f"Mechanical daily rows ({ROW_SCHEMA}) from {GENERATOR}; diagnostic only (metrics law 1).")
            git(wt, "commit", "-q", "-m", msg, check=True)
            p = git(wt, "push", "-q", remote, f"HEAD:refs/heads/{branch}")
            if p.returncode == 0:
                report.append(f"[scorecard] published {len(new)} row(s) to {OUTPUT} at bus "
                              f"{git_out(wt, 'rev-parse', 'HEAD')}")
                return report
            report.append(f"[scorecard] push attempt {attempt} rejected; re-reading {remote}/{branch}")
        raise Unavailable(f"push failed after {retries} attempts")
    finally:
        if wt.exists():
            git(bus, "worktree", "remove", "--force", str(wt))
        git(bus, "worktree", "prune")
        shutil.rmtree(work, ignore_errors=True)


# ---------- CLI ----------

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=".", help="the project root (default: cwd)")
    ap.add_argument("--project", help="project name (required without a config; filters a multi-project config)")
    ap.add_argument("--config", help=f"scorecard config (default <root>/{DEFAULT_CONFIG} when present)")
    ap.add_argument("--pins", help=f"the EXECUTOR's pins file whose runner runs pinned bus tools (default: each "
                                   f"project's own <root>/{DEFAULT_PINS}); pin_stale always reads the project's own")
    ap.add_argument("--bus", help="local bus clone (default $FACTORY_BUS_CLONE, the pins' bus_clone, or this script's repo)")
    ap.add_argument("--publish", action="store_true", help=f"append the rows to the bus {OUTPUT} (idempotent per project+date)")
    ap.add_argument("--out", help="also append the rows to this local file")
    ap.add_argument("--field", choices=FIELDS, help="print one field of each row (shows its command)")
    ap.add_argument("--now", help="ISO instant to measure at (tests)")
    a = ap.parse_args(argv)
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(errors="backslashreplace")
    root = Path(a.root).resolve()
    now = parse_ts(a.now) if a.now else dt.datetime.now(dt.timezone.utc)
    try:
        if not root.is_dir():
            raise ConfigError(f"root is not a directory: {a.root}")
        projects, cfg_path, cfg_sha = load_config(root, a.config, a.project)
    except ConfigError as e:
        print(f"fleet-scorecard: ERROR {e}", file=sys.stderr)
        return 2
    rows = []
    for p in projects:
        proot = project_root(p, root, cfg_path)
        if not proot.is_dir():
            print(f"fleet-scorecard: SKIP {p['name']}: root absent on this machine", file=sys.stderr)
            continue
        p = overlay(p, proot)
        own_pins = proot / (p.get("pins") or DEFAULT_PINS)
        pins = Path(a.pins).resolve() if a.pins else own_pins
        bus = Path(a.bus).resolve() if a.bus else find_bus(None, pins)
        rows.append(build_row(p, proot, bus, pins, cfg_path, cfg_sha, now, own_pins))
    refused = [(r["project"], why) for r in rows if (why := screen(r))]
    for proj, why in refused:
        print(f"fleet-scorecard: REFUSED row {proj}: publish screen ({why})", file=sys.stderr)
    rows = [r for r in rows if not screen(r)]
    for r in rows:
        if a.field:
            print(json.dumps({"project": r["project"], a.field: r["fields"][a.field]}, ensure_ascii=False))
        else:
            print(json.dumps(r, ensure_ascii=False, separators=(",", ":")))
    if a.out and rows:
        with open(a.out, "a", encoding="utf-8", newline="\n") as fh:
            for r in rows:
                fh.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
    if a.publish:
        bus = Path(a.bus).resolve() if a.bus else find_bus(None, Path(a.pins).resolve() if a.pins else root / DEFAULT_PINS)
        if bus is None:
            print("fleet-scorecard: UNAVAILABLE no bus clone (--bus, $FACTORY_BUS_CLONE or pins bus_clone)", file=sys.stderr)
            return 3
        if rows:
            try:
                for line in publish(bus, rows):
                    print(line, file=sys.stderr)
            except Unavailable as e:
                print(f"fleet-scorecard: UNAVAILABLE {e}", file=sys.stderr)
                return 3
    return 2 if refused else 0


if __name__ == "__main__":
    sys.exit(main())
