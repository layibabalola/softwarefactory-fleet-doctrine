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
import platform
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
          "commits_no_remote", "master_vs_origin", "kernel_24h", "pin_stale",
          "rule_coverage", "bus_publish", "fold_lag", "kernel_filing", "bus_ci")
MASTER = "refs/remotes/origin/master"
DEFAULT_MARKER = ".codex-state/doctrine/last-seen.json"
# Health thresholds (diagnostic flags, never a gate): shipped beside this script, so a run judges by the
# thresholds of the reviewed checkout it runs from. Schema fleet/health-thresholds/v1.
THRESHOLDS = "metrics/fleet-health-thresholds.json"
THRESHOLDS_SCHEMA = "fleet/health-thresholds/v1"
# The doctrine-bearing bus surfaces a consumer folds: tools/doctrine-sync.mjs BUS_SURFACES verbatim (the
# tests assert parity). A bus commit counts toward fold lag when it touches one of them other than the
# project's own specs/<p>.md - exactly what `doctrine-sync check` lists - minus the CoS heartbeat pulse.
DOCTRINE_SURFACES = ("specs/", "TRAPS.md", "RULINGS.md", "RECEIPTS.md", "cos-feedback/")
FOLD_EXCLUDE = ("cos-feedback/_heartbeat/",)
# --fleet runs as the bus itself: these bus tools run from the checkout that holds this script (as CI runs
# them), not through a project's pins. Project mode keeps Law 1 pins.
BUS_TOOLS = {"tool-census": ("node", "tools/tool-census.mjs"),
             "check-rule-tags": ("python", "tools/check-rule-tags.py"),
             "check-evidence-dumps": ("python", "tools/factory/check-evidence-dumps.py")}
SCRIPT_BUS = Path(__file__).resolve().parents[2]
# bus_ci: the latest master CI conclusion per bus workflow, read through `gh` (2026-10-17: four bus workflows
# were red on master for days and nobody saw it). Diagnostic only, never a gate (metrics law 1).
BUS_REPO = "layibabalola/softwarefactory-fleet-doctrine"
CI_RED = {"failure", "timed_out", "startup_failure", "action_required"}
CI_IGNORED = {"cancelled", "skipped", "stale"}   # a superseded or skipped run decides nothing
CI_LIMIT = 200

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
                 own_pins: Path | None = None, bus_direct: Path | None = None):
        # pins = the EXECUTOR's pins (whose review authorizes running bus tools); own_pins = the measured
        # project's pins (pin_stale). They differ when one project's steward measures a sibling.
        # bus_direct = --fleet: the bus checkout whose own tools run directly (BUS_TOOLS).
        self.root, self.bus, self.pins, self.config = root, bus, pins, config
        self.own_pins = own_pins or pins
        self.bus_direct = bus_direct
        self._data: Path | None = None

    def bus_file(self, rel: str) -> Path | None:
        """A bus data file as committed on the clone's origin/master, materialized in a private temp dir.
        The clone's own worktree may be stale or edited; the published line is what the fleet reads."""
        if not self.bus:
            return None
        if self._data is None:
            self._data = Path(tempfile.mkdtemp(prefix="fleet-scorecard-data-"))
        out = self._data / rel
        if out.is_file():
            return out
        p = subprocess.run(["git", "--no-optional-locks", "-C", str(self.bus), "show", f"refs/remotes/origin/master:{rel}"],
                           capture_output=True, timeout=TIMEOUT)
        if p.returncode != 0:
            return None
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(p.stdout)
        return out

    def cleanup(self):
        if self._data:
            shutil.rmtree(self._data, ignore_errors=True)

    def render(self, parts) -> str:
        subs = [(str(p), tag) for p, tag in ((self._data, "<bus@origin/master>"),
                                             (self.pins.parent if self.pins else None, "<pins>"),
                                             (self.own_pins.parent if self.own_pins and self.own_pins != self.pins
                                              else None, "<own-pins>"),
                                             (self.bus_direct if self.bus_direct != self.bus else None,
                                              "<bus-checkout>"),
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


def run_cmd(argv: list[str], cwd: Path, timeout: int = TIMEOUT, stdin: str | None = None) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if k.upper() not in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE")}
    return subprocess.run(argv, cwd=str(cwd), capture_output=True, text=True, encoding="utf-8",
                          errors="replace", env=env, timeout=timeout, input=stdin)


# ---------- pinned bus tools ----------

def pinned_argv(ctx: Ctx, tool: str) -> list[str] | None:
    """argv prefix that runs a pinned tool through the project's runner, or None when it is not pinned.
    Under --fleet (ctx.bus_direct) a BUS_TOOLS tool runs from that bus checkout instead."""
    if ctx.bus_direct and tool in BUS_TOOLS:
        interp, rel = BUS_TOOLS[tool]
        script = ctx.bus_direct / rel
        if script.is_file():
            return (["node"] if interp == "node" else [sys.executable]) + [str(script)]
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
        a = re.sub(r"\{bus:([^}]+)\}", lambda m: str(ctx.bus_file(m.group(1)) or m.group(0)), str(a))
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
            v = m.group(1)
            return int(v) if re.fullmatch(r"-?\d+", v) else float(v)
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

_CENSUS: dict = {}           # one fleet-wide census per run serves every project's row (99fab0c)


def schedule_max(baseline: dict | None, today: str) -> int | None:
    """The tool-census schedule max in force on 'today' (latest 'by' <= today; tool-census.mjs rule 5)."""
    passed = sorted((e for e in ((baseline or {}).get("schedule") or [])
                     if isinstance(e, dict) and isinstance(e.get("by"), str) and e["by"] <= today),
                    key=lambda e: e["by"])
    return passed[-1].get("max") if passed else None


def census_views(rep: dict, baseline: dict | None) -> list[dict]:
    """Per-view counts (tool-census.mjs rule 7): one count over each baseline view's fixed (roots x families)
    set, recomputed from the --json report the same way tool-census counts. A view whose roots are not all
    visible here is UNMEASURED (count null), never compared."""
    b = baseline or {}
    views = [{"name": "primary", "roots": b.get("roots"), "families": list((b.get("families") or {}).keys()) or None,
              "baseline": b.get("total")}]
    views += [{"name": v.get("name"), "roots": v.get("roots"), "families": v.get("families"), "baseline": v.get("total")}
              for v in (b.get("views") or []) if isinstance(v, dict)]
    measured = set(rep.get("measuredRoots") or [])
    out = []
    for v in views:
        roots, fams = v["roots"], v["families"]
        if not isinstance(roots, list) or not set(roots) <= measured:
            out.append({"name": v["name"], "count": None, "baseline": v["baseline"]})
            continue
        count = 0
        for f in rep.get("families") or []:
            if fams and f.get("name") not in fams:
                continue
            distinct = {c.get("hash") for c in f.get("copies") or [] if c.get("root") in roots}
            count += max(len(distinct) - 1, 0)
        count += sum(1 for d in rep.get("doubleRegistrations") or []
                     if d.get("project") in roots and (not fams or d.get("family") in fams))
        out.append({"name": v["name"], "count": count, "baseline": v["baseline"]})
    return out


def f_tool_census(ctx: Ctx, proj: dict, now: dt.datetime | None = None) -> dict:
    pre = pinned_argv(ctx, "tool-census")
    if pre is None:
        return field(cmd="pinned:tool-census", error="NOT_PINNED")
    if not ctx.bus:
        return field(cmd="pinned:tool-census", error="ABSENT: no bus clone")
    cfg, base = ctx.bus_file("tools/tool-census.config.json"), ctx.bus_file("metrics/tool-census-baseline.json")
    if cfg is None:
        return field(cmd="pinned:tool-census", error="ABSENT: no tool-census config on bus origin/master")
    # The census resolves '@bus' as its own script's parent; under the pin runner that is a temp dir (it
    # once walked all of %TEMP% for ten minutes). Name the clone in the materialized config (data) instead.
    try:
        cj = json.loads(cfg.read_text(encoding="utf-8"))
        for r in cj.get("roots") or []:
            if r.get("path") == "@bus":
                r["path"] = str(ctx.bus)
        cfg.write_text(json.dumps(cj), encoding="utf-8")
    except (OSError, ValueError, AttributeError) as e:
        return field(cmd="pinned:tool-census", error=f"FAILED: census config unreadable ({type(e).__name__})")
    argv = pre + ["--json", "--config", str(cfg)] + (["--baseline", str(base)] if base else [])
    cmd = ctx.render(argv)
    key = (str(ctx.pins), tuple(pre), str(ctx.bus), git_out(ctx.bus, "rev-parse", MASTER))
    try:
        if key not in _CENSUS:
            _CENSUS[key] = json.loads(run_cmd(argv, ctx.bus).stdout)
        rep = _CENSUS[key]
    except (OSError, subprocess.TimeoutExpired, ValueError) as e:
        return field(cmd=cmd, error=f"FAILED: {ctx.scrub(str(e))[:160]}")
    name = proj.get("census_root") or proj["name"]
    copies = [c for f in rep.get("families") or [] for c in f.get("copies") or [] if c.get("root") == name]
    baseline = None
    try:
        baseline = json.loads(base.read_text(encoding="utf-8"))
    except (OSError, ValueError, AttributeError):
        pass
    today = (now or dt.datetime.now(dt.timezone.utc)).astimezone(dt.timezone.utc).date().isoformat()
    smax = schedule_max(baseline, today)
    views = census_views(rep, baseline)
    primary = next((v for v in views if v["name"] == "primary"), {}).get("count")
    return field({"project_copies": len([c for c in copies if not c.get("canonical")]),
                  "project_doubles": sum(1 for d in rep.get("doubleRegistrations") or [] if d.get("project") == name),
                  "fleet_total": rep.get("total"), "baseline_total": (baseline or {}).get("total"),
                  "views": views,
                  "primary_count": primary,
                  "schedule_max": smax,
                  "schedule_next": next(({"by": e["by"], "max": e.get("max")} for e in sorted(
                      (e for e in ((baseline or {}).get("schedule") or []) if isinstance(e, dict)
                       and isinstance(e.get("by"), str) and e["by"] > today), key=lambda e: e["by"])), None),
                  # the schedule caps the PRIMARY view (the top-level baseline); unmeasurable here = None
                  "over_schedule": (primary > smax) if isinstance(primary, int) and isinstance(smax, int) else None,
                  "measured": name in (rep.get("measuredRoots") or []),
                  "absent_roots": rep.get("absentRoots") or []}, cmd)


def f_rule_tags(ctx: Ctx, proj: dict) -> dict:
    rt = proj.get("rule_tags")
    if not rt:
        return field(error="NOT_CONFIGURED")
    pre = pinned_argv(ctx, "check-rule-tags")
    if pre is None:
        return field(cmd="pinned:check-rule-tags", error="NOT_PINNED")
    cfg = (ctx.root / rt["config"]) if rt.get("config") else ctx.bus_file("tools/rule-tags.config.json")
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


def live_shares(bus_checkout: Path, names: list[str], window_days: int) -> dict:
    """--fleet --share live: ONE Get-ProductThroughput.ps1 -Lines run over the members cloned here that its
    class config declares. Returns {name: field}; an undeclared member is absent (falls back to the row)."""
    script = bus_checkout / "tools" / "Get-ProductThroughput.ps1"
    try:
        declared = {x.get("name") for x in json.loads(
            (bus_checkout / "tools" / "product-throughput-classes.json").read_text(encoding="utf-8")).get("projects") or []}
    except (OSError, ValueError):
        return {}
    want = [n for n in names if n in declared]
    if not want or not script.is_file():
        return {}
    argv = [shutil.which("pwsh") or "pwsh", "-NoProfile", "-File", str(script), "-Lines", "-AsJson",
            "-WindowDays", str(window_days), "-Project", ",".join(want)]
    cmd = " ".join(["pwsh", "-NoProfile", "-File", "<bus-checkout>/tools/Get-ProductThroughput.ps1", "-Lines", "-AsJson",
                    "-WindowDays", str(window_days), "-Project", ",".join(want)])
    try:
        p = run_cmd(argv, bus_checkout, timeout=1200)
        data = json.loads(p.stdout)
    except (OSError, subprocess.TimeoutExpired, ValueError) as e:
        return {n: field(cmd=cmd, error=f"FAILED: {type(e).__name__}") for n in want}
    out = {}
    for e in data.get("projects") or []:
        n = e.get("project")
        if n not in want:
            continue
        if e.get("error"):
            out[n] = field(cmd=cmd, error=f"FAILED: {str(e['error'])[:120]}")
        else:
            out[n] = field({"product_share": e.get("product_share"), "product_lines_per_week": e.get("product_lines_per_week"),
                            "window_days": window_days, "measured_at": data.get("until_utc"), "source": "live"}, cmd)
    return out


def f_product_share(ctx: Ctx, proj: dict) -> dict:
    if proj.get("_live_share"):
        return proj["_live_share"]
    path = ctx.bus_file("metrics/product-share-lines.jsonl")
    cmd = ctx.render(["read", "<bus@origin/master>/metrics/product-share-lines.jsonl",
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
                  "window_days": last.get("window_days"), "measured_at": last.get("ts"), "source": "row"}, cmd)


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


def _json_path(node, path: str):
    for k in path.split("."):
        node = node[k]
    return node


def f_rule_coverage(ctx: Ctx, proj: dict) -> dict:
    """The project's OWN rule-coverage census (a project command; config rule_coverage = a source spec plus
    an optional floor: a number, or floor_json {file, path} read from the project root)."""
    spec = proj.get("rule_coverage")
    if not spec:
        return field(error="NOT_CONFIGURED")
    f = from_source(ctx, spec, "rule_coverage")
    if f["value"] is None:
        return f
    floor, ferr = spec.get("floor"), None
    if floor is None and spec.get("floor_json"):
        fj = spec["floor_json"]
        try:
            floor = _json_path(json.loads((ctx.root / fj["file"]).read_text(encoding="utf-8-sig")), fj["path"])
        except (OSError, ValueError, KeyError, TypeError) as e:
            ferr = f"floor ABSENT ({type(e).__name__})"
    f["value"] = {"percent": f["value"], "floor": floor}
    f["error"] = ferr
    return f


def _log_rows(repo: Path, *args) -> list[tuple[str, str, str]] | None:
    """git log --format=%H%x09%cI%x09%s -> [(sha, committer ISO, subject)]; None when git failed."""
    p = git(repo, "log", "--format=%H%x09%cI%x09%s", *args)
    if p.returncode != 0:
        return None
    return [tuple((l.split("\t", 2) + ["", ""])[:3]) for l in p.stdout.splitlines() if l.strip()]


def _age_days(now: dt.datetime, iso: str) -> float:
    return round((now - parse_ts(iso)).total_seconds() / 86400, 1)


def f_bus_publish(ctx: Ctx, proj: dict, now: dt.datetime) -> dict:
    """Days since the newest origin/master commit ATTRIBUTED to the project. Attribution (single writer, law 2):
    a commit touching the project's own surfaces specs/<p>.md, specs/<p>/ or metrics/<p>/; or a commit to the
    shared append-only files TRAPS/RECEIPTS/RULINGS/DISCOVERIES whose subject names the project as a token.
    heartbeats/ (a pulse) and cos-feedback/ (CoS-written) are never a project publish."""
    if not ctx.bus:
        return field(error="ABSENT: no bus clone")
    names = proj.get("bus_names") or [proj["name"]]
    own = [s for n in names for s in (f"specs/{n}.md", f"specs/{n}/", f"metrics/{n}/")]
    shared = ["TRAPS.md", "RECEIPTS.md", "RULINGS.md", "DISCOVERIES.md"]
    cmd = (ctx.render(["git", "-C", str(ctx.bus), "log", "-1", "--no-merges", MASTER, "--", *own])
           + " ; newest subject-tagged commit to " + "/".join(shared))
    a = _log_rows(ctx.bus, "-1", "--no-merges", MASTER, "--", *own)
    b = _log_rows(ctx.bus, "-n", "400", "--no-merges", MASTER, "--", *shared)
    if a is None or b is None:
        return field(cmd=cmd, error="FAILED: git log on the bus clone")
    tag = re.compile(r"(?i)(?<![\w-])(?:" + "|".join(map(re.escape, names)) + r")(?![\w-])")
    cands = [(r, "own-surface") for r in a] + [(r, "subject-tag") for r in b if tag.search(r[2])][:1]
    if not cands:
        return field({"days_since": None, "commit": None, "via": None}, cmd)
    (sha, when, _), via = max(cands, key=lambda c: parse_ts(c[0][1]))
    return field({"days_since": _age_days(now, when), "commit": sha[:12], "via": via}, cmd)


def is_doctrine_surface(path: str, project: str) -> bool:
    """tools/doctrine-sync.mjs isSiblingSurface, minus the CoS heartbeat pulse."""
    if path == f"specs/{project}.md" or path.startswith(FOLD_EXCLUDE):
        return False
    return any(path.startswith(s) if s.endswith("/") else path == s for s in DOCTRINE_SURFACES)


def f_fold_lag(ctx: Ctx, proj: dict, now: dt.datetime) -> dict:
    """Doctrine-bearing bus commits after the project's fold cursor (its doctrine-sync ack, lastSeen) on
    origin/master: how many, and the age of the oldest, by committer date."""
    if not ctx.bus:
        return field(error="ABSENT: no bus clone")
    marker = (proj.get("fold") or {}).get("marker") or DEFAULT_MARKER
    cmd = ctx.render(["git", "-C", str(ctx.bus), "log", "--no-merges", "--name-only", f"<{marker}:lastSeen>..{MASTER}"]) \
        + " | doctrine-sync surfaces minus specs/<p>.md and cos-feedback/_heartbeat/"
    try:
        cursor = str(json.loads((ctx.root / marker).read_text(encoding="utf-8"))["lastSeen"])
    except (OSError, ValueError, KeyError, TypeError) as e:
        return field(cmd=cmd, error=f"ABSENT: no fold cursor ({type(e).__name__})")
    if not re.fullmatch(r"[0-9a-fA-F]{7,40}", cursor):
        return field(cmd=cmd, error="FAILED: fold cursor is not a commit id")
    if git(ctx.bus, "merge-base", "--is-ancestor", cursor, MASTER).returncode != 0:
        return field({"cursor": cursor[:12], "unfolded": None, "oldest_age_hours": None}, cmd,
                     "UNREACHABLE: the fold cursor is not on origin/master here")
    p = git(ctx.bus, "log", "--no-merges", "--name-only", "--format=%x00%H%x09%cI", f"{cursor}..{MASTER}")
    if p.returncode != 0:
        return field(cmd=cmd, error="FAILED: git log on the bus clone")
    name = (proj.get("bus_names") or [proj["name"]])[0]
    dates = []
    for chunk in p.stdout.split("\0")[1:]:
        lines = chunk.splitlines()
        if not lines:
            continue
        _, _, when = lines[0].partition("\t")
        if any(is_doctrine_surface(f.strip(), name) for f in lines[1:] if f.strip()):
            dates.append(parse_ts(when))
    oldest = round((now - min(dates)).total_seconds() / 3600, 1) if dates else None
    return field({"cursor": cursor[:12], "unfolded": len(dates), "oldest_age_hours": oldest}, cmd)


def f_kernel_filing(ctx: Ctx, proj: dict, now: dt.datetime) -> dict:
    """Days since the project's newest factory-kernel filing (adjudications/factory-kernel/<p>.md or <p>-*.md,
    case-insensitive, never *.dispositions.md) on origin/master or any origin/review/* branch (R7 filings
    land on review branches)."""
    if not ctx.bus:
        return field(error="ABSENT: no bus clone")
    names = proj.get("kernel_names") or [proj["name"]]
    review = (git_out(ctx.bus, "for-each-ref", "--format=%(refname)", "refs/remotes/origin/review/") or "").split()
    specs = [s for n in names for s in (f":(icase)adjudications/factory-kernel/{n}.md",
                                        f":(glob,icase)adjudications/factory-kernel/{n}-*.md")]
    specs.append(":(exclude,glob)adjudications/factory-kernel/*.dispositions.md")
    cmd = ctx.render(["git", "-C", str(ctx.bus), "log", "-1", MASTER, "refs/remotes/origin/review/*", "--", *specs])
    rows = _log_rows(ctx.bus, "-1", MASTER, *review, "--", *specs)
    if rows is None:
        return field(cmd=cmd, error="FAILED: git log on the bus clone")
    if not rows:
        return field({"days_since": None, "commit": None}, cmd)
    return field({"days_since": _age_days(now, rows[0][1]), "commit": rows[0][0][:12]}, cmd)


def gh_argv() -> list[str] | None:
    """The gh CLI argv prefix, or None when gh is not installed (tests patch this seam)."""
    gh = shutil.which("gh")
    return [gh] if gh else None


def _github_repo(url: str | None) -> str | None:
    m = re.search(r"github\.com[:/]+([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+?)(?:\.git)?/?$", (url or "").strip())
    return m.group(1) if m else None


def bus_ci_summary(runs: list[dict], now: dt.datetime, repo: str, branch: str) -> dict:
    """`gh run list --json workflowName,status,conclusion,headSha,createdAt,databaseId` rows -> per workflow the
    latest DECIDING conclusion (cancelled/skipped runs decide nothing) and, when red, since when it has been red
    (the oldest run of the unbroken red streak)."""
    by_wf: dict[str, list[dict]] = {}
    for r in runs:
        if isinstance(r, dict) and isinstance(r.get("workflowName"), str):
            by_wf.setdefault(r["workflowName"], []).append(r)
    workflows = {}
    for name, rs in sorted(by_wf.items()):
        rs.sort(key=lambda r: str(r.get("createdAt") or ""), reverse=True)
        decided = [r for r in rs if r.get("status") == "completed" and r.get("conclusion") not in CI_IGNORED]
        pending = sum(1 for r in rs if r.get("status") != "completed")
        if not decided:
            workflows[name] = {"conclusion": None, "head_sha": None, "run_id": None, "created_at": None,
                               "red_since": None, "in_progress": pending}
            continue
        latest = decided[0]
        red_since, truncated = None, False
        if latest.get("conclusion") in CI_RED:
            streak = 0
            for r in decided:
                if r.get("conclusion") not in CI_RED:
                    break
                red_since, streak = r.get("createdAt"), streak + 1
            truncated = streak == len(decided) and len(runs) >= CI_LIMIT
        workflows[name] = {"conclusion": latest.get("conclusion"), "head_sha": str(latest.get("headSha") or "")[:12],
                           "run_id": latest.get("databaseId"), "created_at": latest.get("createdAt"),
                           "red_since": red_since, "in_progress": pending}
        if truncated:
            workflows[name]["red_since_truncated"] = True
    red = [n for n, w in workflows.items() if w["conclusion"] in CI_RED]
    ages = [round((now - parse_ts(workflows[n]["red_since"])).total_seconds() / 3600, 1)
            for n in red if workflows[n]["red_since"]]
    return {"repo": repo, "branch": branch, "workflows": workflows, "red": red,
            "red_hours": max(ages) if ages else None}


def f_bus_ci(ctx: Ctx, proj: dict, now: dt.datetime) -> dict:
    """Latest bus master CI conclusion per workflow, read through `gh run list`. A null value with an error
    when gh is absent or fails; never a gate (metrics law 1). Repo: config bus_ci.repo, else the bus clone's
    GitHub origin, else the canonical bus."""
    cfg = proj.get("bus_ci") or {}
    origin = git_out(ctx.bus, "remote", "get-url", "origin") if ctx.bus else None
    repo = cfg.get("repo") or _github_repo(origin) or BUS_REPO
    branch = cfg.get("branch") or "master"
    args = ["run", "list", "-R", repo, "--branch", branch, "--limit", str(CI_LIMIT),
            "--json", "workflowName,status,conclusion,headSha,createdAt,databaseId"]
    cmd = " ".join(["gh", *args])
    gh = gh_argv()
    if not gh:
        return field(cmd=cmd, error="GH_UNAVAILABLE: gh is not installed")
    try:
        p = run_cmd([*gh, *args], ctx.root if ctx.root and Path(ctx.root).is_dir() else Path.cwd(), timeout=120)
    except (OSError, subprocess.TimeoutExpired) as e:
        return field(cmd=cmd, error=f"GH_FAILED: {type(e).__name__}")
    if p.returncode != 0:
        why = ((p.stderr or p.stdout or "").strip().splitlines() or ["no output"])[0]
        return field(cmd=cmd, error=f"GH_FAILED: exit {p.returncode}: {ctx.scrub(why)}")
    try:
        runs = json.loads(p.stdout or "[]")
    except ValueError:
        return field(cmd=cmd, error="GH_OUTPUT_INVALID: not JSON")
    if not isinstance(runs, list):
        return field(cmd=cmd, error="GH_OUTPUT_INVALID: not a list")
    return field(bus_ci_summary(runs, now, repo, branch), cmd)


# ---------- health (diagnostic flags; never a gate, never a target: metrics law 1) ----------

def load_thresholds(path: Path | None) -> tuple[dict | None, str | None]:
    f = path or (SCRIPT_BUS / THRESHOLDS)
    if not f.is_file():
        if path:
            raise ConfigError(f"thresholds not found: {path}")
        return None, None
    data = f.read_bytes()
    try:
        th = json.loads(data.decode("utf-8"))
    except ValueError as e:
        raise ConfigError(f"thresholds {f.name}: {e}")
    if th.get("schema") != THRESHOLDS_SCHEMA:
        raise ConfigError(f"thresholds {f.name}: schema is not {THRESHOLDS_SCHEMA}")
    return th, hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def health(fields: dict, th: dict, th_sha: str | None) -> dict:
    """RED when any duty is OVERDUE by the thresholds; GREEN when none is and at least one was measured;
    UNMEASURED when nothing judgeable was measured. Null is 'not measured', never 'fine'."""
    t = th.get("thresholds") or {}
    reasons, unmeasured = [], []

    def val(n):
        return (fields.get(n) or {}).get("value")

    c = val("tool_census")
    if c is None:
        unmeasured.append("census")
    elif c.get("over_schedule") and (c.get("project_copies") or c.get("project_doubles")):
        reasons.append(f"census primary view {c['primary_count']} > schedule max {c['schedule_max']} "
                       f"({c.get('project_copies')} copies, {c.get('project_doubles')} double registrations here)")
    rc = fields.get("rule_coverage") or {}
    if rc.get("value"):
        pc, fl = rc["value"].get("percent"), rc["value"].get("floor")
        if isinstance(pc, (int, float)) and isinstance(fl, (int, float)) and pc < fl:
            reasons.append(f"rule coverage {pc}% < own floor {fl}%")
    elif rc.get("error") != "NOT_CONFIGURED":
        unmeasured.append("coverage")
    if val("product_share") is None:
        unmeasured.append("product_share")
    for name, key, limit_key, unit, never in (
            ("bus_publish", "days_since", "bus_publish_days", "d", "no attributed bus publish"),
            ("kernel_filing", "days_since", "kernel_filing_days", "d", "no kernel filing")):
        v = val(name)
        if v is None:
            unmeasured.append(name)
        elif v.get(key) is None:
            reasons.append(never)
        elif isinstance(t.get(limit_key), (int, float)) and v[key] > t[limit_key]:
            reasons.append(f"{name.replace('_', ' ')} {v[key]}{unit} > {t[limit_key]}{unit}")
    fl = val("fold_lag")
    if fl is None or fl.get("unfolded") is None:
        unmeasured.append("fold_lag")
    elif fl.get("oldest_age_hours") is not None and isinstance(t.get("fold_oldest_unfolded_hours"), (int, float)) \
            and fl["oldest_age_hours"] > t["fold_oldest_unfolded_hours"]:
        reasons.append(f"fold lag {fl['unfolded']} unfolded, oldest {fl['oldest_age_hours']}h > "
                       f"{t['fold_oldest_unfolded_hours']}h")
    judged = {"census", "coverage", "bus_publish", "kernel_filing", "fold_lag"} - set(unmeasured)
    status = "RED" if reasons else ("GREEN" if judged else "UNMEASURED")
    return {"status": status, "reasons": reasons, "unmeasured": unmeasured, "thresholds_sha256": th_sha}


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
              own_pins: Path | None = None, bus_direct: Path | None = None, th: dict | None = None,
              th_sha: str | None = None) -> dict:
    ctx = Ctx(root, bus, pins, cfg_path, own_pins, bus_direct)
    try:
        row = _build_row(ctx, p, root, bus, pins, cfg_sha, now)
    finally:
        ctx.cleanup()
    if th is not None:
        row["health"] = health(row["fields"], th, th_sha)
    return row


def machine() -> str:
    return (os.environ.get("COMPUTERNAME") or platform.node() or "unknown").upper()


def unmeasured_row(name: str, now: dt.datetime, why: str) -> dict:
    """A derived member this box cannot measure (no local clone). Never published; listed, never skipped."""
    return {"schema": ROW_SCHEMA, "date": now.astimezone(dt.timezone.utc).date().isoformat(), "ts": utc(now),
            "project": name, "machine": machine(), "fields": {},
            "health": {"status": "UNMEASURED", "reasons": [why], "unmeasured": ["all"], "thresholds_sha256": None}}


def _build_row(ctx: "Ctx", p: dict, root: Path, bus: Path | None, pins: Path | None, cfg_sha, now: dt.datetime) -> dict:
    fields = {
        "tool_census": f_tool_census(ctx, p, now),
        "rule_tags": f_rule_tags(ctx, p),
        "evidence_dumps": from_source(ctx, p.get("evidence_dumps"), "evidence_dumps"),
        "product_share": f_product_share(ctx, p),
        "doctrine_fold": f_doctrine_fold(ctx, p, now),
        "outbox_unsent": from_source(ctx, p.get("outbox"), "outbox_unsent"),
        "commits_no_remote": f_commits_no_remote(ctx, p),
        "master_vs_origin": f_master_vs_origin(ctx, p),
        "kernel_24h": f_kernel(ctx, p, now),
        "pin_stale": f_pin_stale(ctx, p),
        "rule_coverage": f_rule_coverage(ctx, p),
        "bus_publish": f_bus_publish(ctx, p, now),
        "fold_lag": f_fold_lag(ctx, p, now),
        "kernel_filing": f_kernel_filing(ctx, p, now),
        "bus_ci": f_bus_ci(ctx, p, now),
    }
    return {
        "schema": ROW_SCHEMA,
        "date": now.astimezone(dt.timezone.utc).date().isoformat(),
        "ts": utc(now),
        "project": p["name"],
        "machine": machine(),
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

def row_key(r: dict) -> tuple:
    """Idempotency key: project + UTC date + measuring machine (two boxes may each measure a project)."""
    return (r.get("project"), r.get("date"), r.get("machine"))


def existing_keys(text: str) -> set:
    keys = set()
    for line in text.splitlines():
        try:
            keys.add(row_key(json.loads(line)))
        except (ValueError, AttributeError):
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
            new = [r for r in rows if row_key(r) not in have]
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



# ---------- fleet mode ----------

def fleet_members(bus: Path, checkout: Path) -> list[str]:
    """Members derived the way fleet-sweep derives them: specs/ on the bus origin/master through the ONE
    classifier, tools/fleet-membership.mjs (--stdin). No second roster."""
    names = git_out(bus, "ls-tree", "--name-only", MASTER, "specs/")
    if names is None:
        raise Unavailable("cannot list specs/ on the bus origin/master")
    p = run_cmd(["node", str(checkout / "tools" / "fleet-membership.mjs"), "--stdin"], checkout, stdin=names + "\n")
    if p.returncode != 0:
        raise Unavailable(f"fleet-membership failed: {(p.stderr or p.stdout).strip()[:160]}")
    members = json.loads(p.stdout).get("members") or []
    if not members:
        raise Unavailable("zero members derived from specs/ - refusing to report an empty fleet")
    return members


def load_roots(path: str | None) -> dict:
    """The machine-local member -> clone map fleet-sweep reads (schema fleet-roots.v1, default ~/.fleet-roots.json)."""
    f = Path(path) if path else Path.home() / ".fleet-roots.json"
    if not f.is_file():
        raise ConfigError(f"no machine-local roots map at {f} ({{\"schema\":\"fleet-roots.v1\",\"roots\":{{...}}}})")
    try:
        return json.loads(f.read_text(encoding="utf-8-sig")).get("roots") or {}
    except ValueError as e:
        raise ConfigError(f"roots map {f.name}: {e}")


def _cell(row: dict, name: str):
    return (row.get("fields", {}).get(name) or {}).get("value")


def table(rows: list[dict]) -> str:
    """--print: one line per measured member, then the UNMEASURED members on one line each reason."""
    hdr = ("project", "status", "census copies/primary/max", "cov%/floor", "share14", "publish d", "fold n/oldest h",
           "kernel d", "reasons")
    out = []
    for r in rows:
        h = r.get("health") or {}
        if h.get("status") == "UNMEASURED" and not r.get("fields"):
            continue
        c, rc, ps = _cell(r, "tool_census"), _cell(r, "rule_coverage"), _cell(r, "product_share")
        bp, fl, kf = _cell(r, "bus_publish"), _cell(r, "fold_lag"), _cell(r, "kernel_filing")
        dash = "-"
        out.append((r["project"], h.get("status", "?"),
                    (f"{c['project_copies']}/{c['primary_count'] if c.get('primary_count') is not None else 'UNMEAS'}/{c['schedule_max'] if c.get('schedule_max') is not None else dash}"
                     + (f" (next {c['schedule_next']['max']} by {c['schedule_next']['by'][5:]})" if c.get("schedule_next") else ""))
                    if c else "UNMEAS",
                    f"{rc['percent']}/{rc['floor'] if rc.get('floor') is not None else dash}" if rc else
                    ("NONE" if (r["fields"].get("rule_coverage") or {}).get("error") == "NOT_CONFIGURED" else "UNMEAS"),
                    f"{ps['product_share']:.3f}" if ps and isinstance(ps.get("product_share"), (int, float)) else "UNMEAS",
                    (str(bp["days_since"]) if bp.get("days_since") is not None else "never") if bp else "UNMEAS",
                    (f"{fl['unfolded']}/{fl['oldest_age_hours'] if fl.get('oldest_age_hours') is not None else dash}"
                     if fl and fl.get("unfolded") is not None else "UNMEAS"),
                    (str(kf["days_since"]) if kf.get("days_since") is not None else "never") if kf else "UNMEAS",
                    "; ".join(h.get("reasons") or [])))
    widths = [max(len(str(x[i])) for x in [hdr, *out]) for i in range(len(hdr) - 1)]
    lines = ["  ".join(str(v).ljust(widths[i]) for i, v in enumerate(x[:-1])) + "  " + x[-1] for x in [hdr, *out]]
    absent = [r["project"] for r in rows if (r.get("health") or {}).get("status") == "UNMEASURED" and not r.get("fields")]
    if absent:
        lines.append(f"UNMEASURED ({len(absent)}, no local clone on {machine()}): {', '.join(absent)}")
    return "\n".join(lines)


def fleet_rows(a, now: dt.datetime) -> list[dict]:
    if not a.bus:
        raise ConfigError("--fleet needs --bus <the bus clone> (a publish target is always named explicitly)")
    bus = Path(a.bus).resolve()
    checkout = SCRIPT_BUS
    if not a.no_fetch:
        git(bus, "fetch", "-q", "origin", "master")
    th, th_sha = load_thresholds(Path(a.thresholds).resolve() if a.thresholds else None)
    if th is None:
        raise ConfigError(f"no thresholds file at {checkout / THRESHOLDS}")
    roots = load_roots(a.roots)
    members = fleet_members(bus, checkout)
    if a.project:
        members = [m for m in members if m == a.project]
    present, rows = [], []
    for m in members:
        r = roots.get(m)
        if r and Path(r).is_dir():
            present.append((m, Path(r).resolve()))
    shares = live_shares(checkout, [m for m, _ in present], int(th.get("product_share_window_days", 14))) \
        if a.share == "live" else {}
    by_name = dict(present)
    for m in members:
        if m not in by_name:
            rows.append(unmeasured_row(m, now, "no local clone on this machine (fleet-roots map)"))
            continue
        proot = by_name[m]
        p = overlay({"name": m, "config": DEFAULT_CONFIG, **((th.get("projects") or {}).get(m) or {})}, proot)
        if m in shares:
            p["_live_share"] = shares[m]
        own_pins = proot / (p.get("pins") or DEFAULT_PINS)
        rows.append(build_row(p, proot, bus, own_pins, None, None, now, own_pins, checkout, th, th_sha))
    return rows


# ---------- CLI ----------

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=".", help="the project root (default: cwd)")
    ap.add_argument("--project", help="project name (required without a config; filters a multi-project config)")
    ap.add_argument("--config", help=f"scorecard config (default <root>/{DEFAULT_CONFIG} when present)")
    ap.add_argument("--pins", help=f"the EXECUTOR's pins file whose runner runs pinned bus tools (default: each "
                                   f"project's own <root>/{DEFAULT_PINS}); pin_stale always reads the project's own")
    ap.add_argument("--bus", help="local bus clone (default $FACTORY_BUS_CLONE, the pins' bus_clone, or this script's repo)")
    ap.add_argument("--fleet", action="store_true", help="measure EVERY derived member cloned on this box (roots map); "
                                                         "the rest are UNMEASURED rows. Needs --bus")
    ap.add_argument("--roots", help="--fleet: machine-local roots map (default ~/.fleet-roots.json, as fleet-sweep)")
    ap.add_argument("--thresholds", help=f"health thresholds (default {THRESHOLDS} beside this script)")
    ap.add_argument("--share", choices=("live", "row"), help="product share: live Get-ProductThroughput run "
                                                             "(--fleet default) or the last published row")
    ap.add_argument("--no-fetch", action="store_true", help="--fleet: do not fetch the bus clone first")
    ap.add_argument("--publish", action="store_true", help=f"append the rows to the bus {OUTPUT} (idempotent per "
                                                           f"project+date+machine; UNMEASURED members are never published)")
    ap.add_argument("--out", help="also append the rows to this local file")
    ap.add_argument("--dry-run", action="store_true", help="measure and print only: no --out write, no publish")
    ap.add_argument("--print", dest="print_table", action="store_true", help="human table instead of JSON rows")
    ap.add_argument("--json", action="store_true", help="JSON rows (the default; with --print, both)")
    ap.add_argument("--field", choices=FIELDS, help="print one field of each row (shows its command)")
    ap.add_argument("--bus-ci", action="store_true", help="print only the bus_ci field (bus master CI per workflow) "
                                                           "as one JSON object and exit 0; no project, config or publish")
    ap.add_argument("--now", help="ISO instant to measure at (tests)")
    a = ap.parse_args(argv)
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(errors="backslashreplace")
    root = Path(a.root).resolve()
    now = parse_ts(a.now) if a.now else dt.datetime.now(dt.timezone.utc)
    if a.bus_ci:
        bus = Path(a.bus).resolve() if a.bus else None
        ctx = Ctx(root, bus, None, None)
        print(json.dumps({"ts": utc(now), "bus_ci": f_bus_ci(ctx, {}, now)}, ensure_ascii=False))
        return 0
    if a.share is None:
        a.share = "live" if a.fleet else "row"
    rows = []
    try:
        if a.fleet:
            rows = fleet_rows(a, now)
        else:
            if not root.is_dir():
                raise ConfigError(f"root is not a directory: {a.root}")
            projects, cfg_path, cfg_sha = load_config(root, a.config, a.project)
            th, th_sha = load_thresholds(Path(a.thresholds).resolve() if a.thresholds else None)
            for p in projects:
                proot = project_root(p, root, cfg_path)
                if not proot.is_dir():
                    print(f"fleet-scorecard: SKIP {p['name']}: root absent on this machine", file=sys.stderr)
                    continue
                p = overlay(p, proot)
                own_pins = proot / (p.get("pins") or DEFAULT_PINS)
                pins = Path(a.pins).resolve() if a.pins else own_pins
                bus = Path(a.bus).resolve() if a.bus else find_bus(None, pins)
                rows.append(build_row(p, proot, bus, pins, cfg_path, cfg_sha, now, own_pins, None, th, th_sha))
    except ConfigError as e:
        print(f"fleet-scorecard: ERROR {e}", file=sys.stderr)
        return 2
    except Unavailable as e:
        print(f"fleet-scorecard: UNAVAILABLE {e}", file=sys.stderr)
        return 3
    refused = [(r["project"], why) for r in rows if (why := screen(r))]
    for proj, why in refused:
        print(f"fleet-scorecard: REFUSED row {proj}: publish screen ({why})", file=sys.stderr)
    rows = [r for r in rows if not screen(r)]
    if a.print_table:
        print(table(rows))
    if a.json or not a.print_table:
        for r in rows:
            if a.field:
                print(json.dumps({"project": r["project"], a.field: r["fields"].get(a.field)}, ensure_ascii=False))
            else:
                print(json.dumps(r, ensure_ascii=False, separators=(",", ":")))
    if a.dry_run:
        return 2 if refused else 0
    if a.out and rows:
        with open(a.out, "a", encoding="utf-8", newline="\n") as fh:
            for r in rows:
                fh.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
    if a.publish:
        bus = Path(a.bus).resolve() if a.bus else find_bus(None, Path(a.pins).resolve() if a.pins else root / DEFAULT_PINS)
        if bus is None:
            print("fleet-scorecard: UNAVAILABLE no bus clone (--bus, $FACTORY_BUS_CLONE or pins bus_clone)", file=sys.stderr)
            return 3
        measured = [r for r in rows if r.get("fields")]
        if measured:
            try:
                for line in publish(bus, measured):
                    print(line, file=sys.stderr)
            except Unavailable as e:
                print(f"fleet-scorecard: UNAVAILABLE {e}", file=sys.stderr)
                return 3
    return 2 if refused else 0


if __name__ == "__main__":
    sys.exit(main())
