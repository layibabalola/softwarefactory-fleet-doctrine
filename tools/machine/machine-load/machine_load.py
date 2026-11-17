#!/usr/bin/env python3
"""machine-load: daily rollup, bus publisher and headroom reader for the fleet machine-load sampler.

Subcommands
  rollup    --day YYYY-MM-DD           print one machine's day row (fleet/machine-load-day/v1) from local minute files
  publish   --bus <clone> [--dry-run]  append every completed, unpublished UTC day to
                                       machine-load/<MACHINE>/days-YYYY-MM.jsonl on the bus (one commit, ff-only push)
  summarize [--hours 1]               live JSON of the last hours on THIS machine (local only; carries process names)
  headroom  --bus <clone> [--days 7] [--live] [--json] [--expect PC-MINI1,...]
                                       the owner's view: per machine, what is used, what is spare, and what limits it

Diagnostic only (bus metrics law 1): rows are measurements; the verdict exists only in the reader's output.
What travels to the (public) bus: aggregates, project names from the allowlist in projects.json, and generic
bucket names. Never process names, command lines, paths or user names.

Exit codes: 0 ok; 1 headroom: a machine is ABSENT, STALE, LOW-COVERAGE, DUPLICATED, MISFILED, INVALID-ROW,
MIXED-CODE, LIVE-STALE or BUS-NOT-REFRESHED (data you cannot trust is never shown as spare capacity); 2 bad input or unreadable data;
3 publish failed; 4 publish succeeded but its receipt could not be written.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import os
import shutil
import socket
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

DAY_SCHEMA = "fleet/machine-load-day/v1"
MINUTE_SCHEMA = "fleet/machine-load-minute/v1"
BUS_DIR = "machine-load"
HERE = Path(__file__).resolve().parent
DEFAULT_DIR = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "MachineLoad"
HEAVYSLOT_LEDGER = Path(r"C:\ProgramData\HeavySlot\ledger.jsonl")
DATA_DIR = Path(r"C:\ProgramData\MachineLoad\data")     # written by the elevated sampler; ACL-locked, readable by Users
RECEIPT_DIR = DEFAULT_DIR                                # the non-elevated publisher's own receipts
BANDS = [(0, 4), (4, 8), (8, 12), (12, 16), (16, 20), (20, 24), (24, 28), (28, 33)]
FULL_DAY = 1440
FULL_MINUTE_SECS = 75.0     # one minute plus one 10 s sampling interval (a restart's first fragment); more = overlap
RESOURCE_COVERAGE = 0.90     # a full day also needs memory and disk readings in >= 90 % of its active minutes
LOW_COVERAGE = 1200          # minutes of a full 1,440; scaled down only for owner quiet windows (see full_day())
MIN_ACTIVE = 360             # a day needs at least this many non-quiet sampled minutes, whatever its quiet windows
FRESH_DAYS = 2               # the newest FULL day must be at most this old, or capacity figures are STALE
GIT_TIMEOUT_S = 120           # one git call; five push attempts stay well inside the 15-minute task limit
RETENTION_DAYS = 14          # the sampler keeps 14 days of minute files; publish considers all of them
QUIET_THREADS_FRACTION = 0.10  # FleetQuiet WaitQuiet treats CPU < 10 % as quiet
MEM_RESERVE_GB = 16.0
DISK_FLOOR_GB = 50.0         # owner rule 2026-10-11: never leave a volume below 50 GB
CLOCK_DROP = 0.90            # a load band whose clock is < 90 % of the light-load clock is where work slows
SSH_ALIAS = {"PC-MINI1": "pc-mini1", "PC-MINI2": "pc-mini2", "PC-MINI3": "pc-mini3"}


MAX_JOBS_PER_DAY = 2000   # HeavySlot spans walked per day (each walk is at most 1,440 minutes)


class Unavailable(Exception):
    pass


# ---------------------------------------------------------------- helpers

def pct(values, p):
    """Nearest-rank percentile of the non-None values; None when there are none."""
    v = sorted(x for x in values if x is not None)
    if not v:
        return None
    k = max(0, min(len(v) - 1, math.ceil(p / 100.0 * len(v)) - 1))
    return v[k]


def r(x, n=2):
    return None if x is None else round(x, n)


def utc_now():
    return dt.datetime.now(dt.timezone.utc)


class Allow(set):
    """Publishable project and bucket labels; .kinds holds the publishable HeavySlot job kinds."""
    kinds: frozenset = frozenset()


def load_projects():
    """The publish allowlist, plus the generic bucket names a '~' label may carry, plus publishable job kinds."""
    cfg = json.loads((HERE / "projects.json").read_text(encoding="utf-8"))
    allow = Allow(cfg.get("publish", []))
    allow |= {"~" + b for b in cfg.get("buckets", {})} | {"~other", "~other-project", "~machine-load"}
    allow.kinds = frozenset(cfg.get("publish_kinds", []))
    return allow


def public_label(label, allow):
    """Only allowlisted project names and known bucket names travel; anything else is '~other-project'.
    A '~' prefix alone is not trusted: a folder named '~client' captured by a '$1' rule must not leak."""
    return label if label in allow else "~other-project"



def public_kind(kind, allow):
    """Only allowlisted job kinds travel (projects.json publish_kinds); a syntactically tidy kind can still be a
    client, branch or user name, so syntax is not enough."""
    return kind if kind in getattr(allow, "kinds", ()) else "?"


def read_minutes(data_dir: Path, day: dt.date, dup_ts=None):
    """Rows for one UTC day, de-duplicated by minute. Returns (rows, duplicate_minutes, unparseable); each
    duplicated minute's ts is appended to dup_ts when given."""
    path = data_dir / f"minute-{day.isoformat()}.jsonl"
    by_ts, sids, dups, bad = {}, {}, 0, 0
    if not path.is_file():
        return [], 0, 0
    with path.open(encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except ValueError:
                bad += 1
                continue
            if row.get("schema") != MINUTE_SCHEMA or not str(row.get("ts", "")).startswith(day.isoformat()):
                bad += 1
                continue
            prev = by_ts.get(row["ts"])
            sid = session_of(row)
            if prev is None:
                by_ts[row["ts"]] = row
                sids[row["ts"]] = {sid}
                continue
            # A restart splits one minute between the old and the new sampler run: two different sampler
            # sessions (sid) whose measured seconds add up to at most one minute. Merge those halves. The same
            # session twice is a replay, and more than a minute of measured time means two samplers overlapped:
            # both count as a duplicate and the first write is kept. (Seconds, not sample counts: rows do not
            # say which -IntervalSec wrote them.)
            # Every session already merged into this minute is remembered, so A, B, then A again is a replay.
            if sid in sids[row["ts"]] or (prev.get("secs") or 0) + (row.get("secs") or 0) > FULL_MINUTE_SECS:
                dups += 1
                if dup_ts is not None:
                    dup_ts.append(row["ts"])
            else:
                by_ts[row["ts"]] = merge_fragments(prev, row)
                sids[row["ts"]].add(sid)
    rows = sorted(by_ts.values(), key=lambda x: x["ts"])
    return rows, dups, bad


def session_of(row):
    """The sampler run that wrote a row. Rows from before the sid field (builds up to 0a6ed3d1's parent, only on
    2026-11-16/17) carry no run identity; such a builds really did restart within a minute, so their identity is
    the row's own content: a byte-identical replay is a duplicate, a different fragment merges on the time bound."""
    if row.get("sid"):
        return row["sid"]
    return "legacy:" + json.dumps(row, sort_keys=True, separators=(",", ":"))


def merge_fragments(a, b):
    """One minute written in two parts by a restarting sampler: CPU-seconds add, means weight by duration,
    extremes take the extreme, and the later fragment's identity (code) wins."""
    wa, wb = (a.get("secs") or 0.0), (b.get("secs") or 0.0)
    w = wa + wb or 1.0
    m = json.loads(json.dumps(b if wb >= wa else a))
    m["n"] = (a.get("n") or 0) + (b.get("n") or 0)
    m["secs"] = round(wa + wb, 1)
    if "cpu_secs" in a or "cpu_secs" in b:
        m["cpu_secs"] = round((a.get("cpu_secs", wa) or 0) + (b.get("cpu_secs", wb) or 0), 1)
    m["code"] = b.get("code") or a.get("code")
    # Every measured field merges explicitly, so the shorter fragment's low memory or disk is never lost:
    # *_mean weights by duration, *_max / *_min take the extreme, c_free_gb takes the lower.
    for sect in ("cpu", "mem", "disk", "thermal"):
        da, db = a.get(sect) or {}, b.get(sect) or {}
        out = {}
        for k in set(da) | set(db):
            out[k] = merge_value(sect, k, da.get(k), db.get(k), wa, wb)
        m[sect] = out
    na, nb = a.get("net_mbps"), b.get("net_mbps")
    if na is not None and nb is not None:
        m["net_mbps"] = round((na * wa + nb * wb) / w, 3)
    for k in ("machine", "attributed", "residual"):
        va, vb = g(a, "cpu_s", k), g(b, "cpu_s", k)
        if va is not None or vb is not None:
            m["cpu_s"][k] = round((va or 0) + (vb or 0), 2)
    proj = defaultdict(float)
    for part in (a, b):
        for label, secs in (part.get("proj") or {}).items():
            proj[label] += secs
    m["proj"] = dict(proj)
    m["merged"] = True
    return m


def merge_value(sect, k, va, vb, wa, wb):
    """One field of two fragments of one minute."""
    num = lambda v: isinstance(v, (int, float)) and not isinstance(v, bool)
    if not num(va) or not num(vb):
        return vb if va is None else va      # one side missing: keep the other
    if sect == "thermal" and k == "n":
        return va + vb                       # Core Temp lines read in the two parts
    if k.endswith("_max") or k.endswith("_age_s"):
        return max(va, vb)
    if k.endswith("_min") or k == "c_free_gb":
        return min(va, vb)                   # the lower free memory / disk wins: never inflate headroom
    w = (wa + wb) or 1.0
    return round((va * wa + vb * wb) / w, 3)  # *_mean, busy_threads and other rates weight by duration


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def valid_day_row(row, today):
    try:
        return _valid_day_row(row, today)
    except (TypeError, AttributeError, KeyError, ValueError):
        return False      # a shape the checks below did not foresee is invalid, never a reader crash


def _valid_day_row(row, today):
    """A published day row the reader may use: a COMPLETED UTC day (before today; a wrong clock cannot make a
    row stay fresh), and EVERY figure the verdict or the report uses present, finite and physically bounded.
    Anything else is INVALID-ROW: ignored, never read as capacity."""
    try:
        d = dt.date.fromisoformat(str(row.get("date")))
    except ValueError:
        return False
    if d >= today:
        return False
    lp = row.get("lp")
    if not (_num(lp) and 1 <= lp <= 4096):
        return False
    cov, quiet = row.get("coverage_min"), row.get("quiet_min")
    if not (_num(cov) and _num(quiet) and 0 <= quiet <= cov <= FULL_DAY):
        return False
    active = cov - quiet

    def within(v, lo, hi, optional=False):
        return (optional and v is None) or (_num(v) and lo <= v <= hi)

    # shape first: every section the reader indexes is a dict, every key it indexes is present (null only where
    # the reader handles null), so a malformed row is INVALID-ROW, never a reader crash
    sections = ("cpu", "mem", "disk", "power", "cpu_core_h", "sampler", "hourly_utc")
    if not all(isinstance(row.get(s), dict) for s in sections):
        return False
    if "pkg_w_p95" not in row["power"] or "residual_pct" not in row["cpu_core_h"]:
        return False
    if not isinstance(row["cpu_core_h"].get("projects"), dict) or not all(isinstance(row["hourly_utc"].get(k), list) for k in ("cov", "busy_p95")):
        return False
    if not isinstance(row["cpu"].get("clock_by_load"), (dict, type(None))):
        return False
    if not isinstance(row.get("heavy_jobs"), (dict, type(None))):
        return False

    checks = [
        within(g(row, "cpu", "busy_threads_p95"), 0, lp), within(g(row, "cpu", "busy_threads_max"), 0, lp),
        within(g(row, "mem", "cov_min"), 0, active), within(g(row, "disk", "cov_min"), 0, active),
        within(g(row, "mem", "avail_gb_p05"), 0, 1e6), within(g(row, "disk", "c_free_gb_min"), 0, 1e9),
        within(g(row, "power", "pkg_w_p95"), 0, 1e4, optional=True),
        # a restart split may sum to 75 s in a minute (FULL_MINUTE_SECS), so integrated CPU is bounded by that, not 60 s
        within(g(row, "cpu_core_h", "machine"), 0, lp * 24 * FULL_MINUTE_SECS / 60), within(g(row, "cpu_core_h", "residual_pct"), -1e4, 100, optional=True),
        within(g(row, "sampler", "cpu_s"), 0, 86400 * lp),
    ]
    if not all(checks):
        return False
    if not all(within(v, 0, lp * 24 * FULL_MINUTE_SECS / 60) for v in row["cpu_core_h"]["projects"].values()):
        return False
    hourly = row["hourly_utc"]
    if not all(isinstance(hourly.get(k), list) and len(hourly[k]) == 24 for k in ("cov", "busy_p95")):
        return False
    if not all(within(c, 0, 60) for c in hourly["cov"]):
        return False
    # an hour with sampled minutes has a measured busy figure; null only for an hour with none
    if not all(within(b, 0, lp, optional=(c == 0)) for c, b in zip(hourly["cov"], hourly["busy_p95"])):
        return False
    for band in (g(row, "cpu", "clock_by_load") or {}).values():
        if not (isinstance(band, dict) and within(band.get("n"), 0, FULL_DAY) and within(band.get("perf_p50"), 1, 1000, optional=True)):
            return False
    return True

def full_day(row):
    """A day row is a full day when its NON-QUIET sampled minutes cover the day: at least LOW_COVERAGE of 1,440,
    scaled to the minutes outside owner quiet windows, and never fewer than MIN_ACTIVE; and memory and disk were
    read in at least RESOURCE_COVERAGE of those minutes. Quiet minutes do not
    count: the busy percentiles and memory floors are computed from active minutes only."""
    cov, quiet = row.get("coverage_min", 0) or 0, row.get("quiet_min", 0) or 0
    active = cov - quiet
    if not (active >= MIN_ACTIVE and active >= LOW_COVERAGE * (FULL_DAY - quiet) / FULL_DAY):
        return False
    # CPU coverage alone is not enough: a day whose memory or disk readings are mostly missing would otherwise
    # report its few readings as the machine's spare memory or disk.
    return all((g(row, sect, "cov_min") or 0) >= RESOURCE_COVERAGE * active for sect in ("mem", "disk"))


def valid_minute(row):
    """A minute counts as sampled only if CPU readings covered at least half of it (cpu_secs: time with a
    successful CPU read; rows written before that field fall back to secs)."""
    observed = row.get("cpu_secs", row.get("secs"))
    return g(row, "cpu", "busy_threads") is not None and isinstance(observed, (int, float)) and observed >= 30


def g(row, *keys):
    cur = row
    for k in keys:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(k)
    return cur


def busy_clock(row):
    """Clock while busy, % of nominal: % Processor Utility / % Processor Time. The _Total
    % Processor Performance counter averages idle cores in, so it barely moves with load."""
    u, t = g(row, "cpu", "util_pct_mean"), g(row, "cpu", "time_pct_mean")
    if u is None or t is None or t < 1.0:
        return None
    return 100.0 * u / t


def parse_iso(s):
    """'2026-11-17T00:04:18.3742500Z' (7 fraction digits, as .NET writes) -> aware UTC datetime."""
    s = s.strip().rstrip("Z")
    if "." in s:
        head, frac = s.split(".", 1)
        s = f"{head}.{frac[:6]}"
    return dt.datetime.fromisoformat(s).replace(tzinfo=dt.timezone.utc)


def parse_ts(s):
    return dt.datetime.strptime(s[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=dt.timezone.utc)


def heavy_jobs(day: dt.date, minutes_by_ts, allow):
    """HeavySlot admit/exit pairs that ENDED on this UTC day, by public 'project:kind'."""
    out = defaultdict(lambda: {"n": 0, "dur": [], "busy": []})
    if not HEAVYSLOT_LEDGER.is_file():
        return None
    admits, walked = {}, 0
    try:
        with HEAVYSLOT_LEDGER.open(encoding="utf-8", errors="replace") as fh:
            for line in fh:
                try:
                    ev = json.loads(line)
                    if not isinstance(ev, dict):
                        continue
                    if ev.get("event") == "admit":
                        admits[ev.get("ticket")] = ev
                        continue
                    if ev.get("event") != "exit" or ev.get("ticket") not in admits:
                        continue
                    a = admits.pop(ev["ticket"])
                    end = parse_iso(str(ev["at"]))
                    start = parse_iso(str(a["at"]))
                except (ValueError, KeyError, TypeError):
                    continue      # the ledger is writable by any user: one bad line must not stop a publish
                if end.date() != day:
                    continue
                if end < start or (end - start).total_seconds() > 2 * 86400:
                    continue      # any user can write the ledger: an impossible span is dropped, never walked or published
                walked += 1
                if walked > MAX_JOBS_PER_DAY:
                    # any user can write the ledger: the walk is bounded, and a truncated day publishes no job
                    # figures at all (partial counts or percentiles would read as the whole day's)
                    return None
                parts = str(a.get("label", "?:?")).split(":")
                key = f"{public_label(parts[0], allow)}:{public_kind(parts[1] if len(parts) > 1 else '?', allow)}"
                o = out[key]
                o["n"] += 1
                o["dur"].append((end - start).total_seconds())
                # walk only this UTC day's minutes (bounded at 1,440 whatever the ledger says)
                t = max(start, dt.datetime.combine(day, dt.time(), dt.timezone.utc)).replace(second=0, microsecond=0)
                busy = []
                while t <= end:
                    m = minutes_by_ts.get(t.strftime("%Y-%m-%dT%H:%M:00Z"))
                    if m is not None and g(m, "cpu", "busy_threads") is not None:
                        busy.append(g(m, "cpu", "busy_threads"))
                    t += dt.timedelta(minutes=1)
                if busy:
                    o["busy"].append(sum(busy) / len(busy))
    except OSError:
        return None
    return {k: {"n": v["n"], "dur_s_p50": r(pct(v["dur"], 50), 0), "dur_s_max": r(max(v["dur"]), 0),
                "busy_threads_during_p50": r(pct(v["busy"], 50), 1)} for k, v in sorted(out.items())}


# ---------------------------------------------------------------- rollup

def rollup(data_dir: Path, day: dt.date, allow=None):
    allow = load_projects() if allow is None else allow
    rows, dups, bad = read_minutes(data_dir, day)
    if not rows:
        return None
    by_ts = {x["ts"]: x for x in rows}
    rows = [x for x in rows if valid_minute(x)]
    if not rows:
        return None
    active = [x for x in rows if not x.get("quiet")]
    lp = rows[-1].get("lp") or 32

    busy = [g(x, "cpu", "busy_threads") for x in active]
    bands = {}
    for lo, hi in BANDS:
        perf = [busy_clock(x) for x in active
                if g(x, "cpu", "busy_threads") is not None and lo <= g(x, "cpu", "busy_threads") < hi]
        perf = [p for p in perf if p is not None]
        if perf:
            bands[f"{lo}-{min(hi, 32)}"] = {"n": len(perf), "perf_p50": r(pct(perf, 50), 1)}

    hourly = {"cov": [], "busy_p95": [], "busy_max": []}
    for h in range(24):
        hr = [x for x in active if int(x["ts"][11:13]) == h]
        hb = [g(x, "cpu", "busy_threads") for x in hr]
        hourly["cov"].append(len(hr))
        hourly["busy_p95"].append(r(pct(hb, 95), 1))
        hourly["busy_max"].append(r(pct(hb, 100), 1))

    proj, buckets = defaultdict(float), defaultdict(float)
    machine_s = attributed_s = 0.0
    for x in rows:
        machine_s += g(x, "cpu_s", "machine") or 0.0
        attributed_s += g(x, "cpu_s", "attributed") or 0.0
        for label, secs in (x.get("proj") or {}).items():
            lab = public_label(label, allow)
            (buckets if lab.startswith("~") else proj)[lab.lstrip("~")] += secs
    core_h = lambda s: round(s / 3600.0, 2)

    pkg = [g(x, "thermal", "pkg_w_mean") for x in active]
    pkg_max = [g(x, "thermal", "pkg_w_max") for x in active]
    core = [g(x, "thermal", "core_c_max") for x in active]
    restarts = sum(1 for a, b in zip(rows, rows[1:]) if (g(b, "sampler", "up_min") or 0) < (g(a, "sampler", "up_min") or 0))

    return {
        "schema": DAY_SCHEMA,
        "machine": rows[-1]["machine"].upper(),
        "date": day.isoformat(),
        "code": list(dict.fromkeys(x.get("code") for x in rows if x.get("code"))),   # first-seen order; last = newest build
        "lp": lp,
        "coverage_min": len(rows),
        "quiet_min": len(rows) - len(active),
        "duplicate_min": dups,
        "unparseable_rows": bad,
        "cpu": {
            "busy_threads_p50": r(pct(busy, 50), 1), "busy_threads_p90": r(pct(busy, 90), 1),
            "busy_threads_p95": r(pct(busy, 95), 1), "busy_threads_p99": r(pct(busy, 99), 1),
            "busy_threads_max": r(pct(busy, 100), 1),
            "min_ge_8": sum(1 for b in busy if b is not None and b >= 8),
            "min_ge_16": sum(1 for b in busy if b is not None and b >= 16),
            "min_ge_24": sum(1 for b in busy if b is not None and b >= 24),
            "clock_by_load": bands,
            "counter": "busy threads = Processor(_Total)\\% Processor Time x logical processors / 100; clock = Processor Information(_Total) % Processor Utility / % Processor Time",
        },
        "power": {
            "pkg_w_p50": r(pct(pkg, 50), 1), "pkg_w_p95": r(pct(pkg, 95), 1), "pkg_w_max": r(pct(pkg_max, 100), 1),
            "min_pkg_ge_70w": sum(1 for p in pkg if p is not None and p >= 70),
            "core_c_p95": r(pct(core, 95), 1), "core_c_max": r(pct(core, 100), 1),
            "feed_min": sum(1 for x in rows if (g(x, "thermal", "n") or 0) > 0),
        },
        "mem": {
            "cov_min": sum(1 for x in active if g(x, "mem", "avail_gb_min") is not None),
            "avail_gb_p05": r(pct([g(x, "mem", "avail_gb_min") for x in active], 5), 1),
            "avail_gb_min": r(pct([g(x, "mem", "avail_gb_min") for x in rows], 0.0001), 1),
            "commit_pct_p95": r(pct([g(x, "mem", "commit_pct_max") for x in active], 95), 1),
            "hard_faults_p95": r(pct([g(x, "mem", "hard_faults_mean") for x in active], 95), 1),
        },
        "disk": {
            "cov_min": sum(1 for x in active if g(x, "disk", "c_free_gb") is not None),
            "busy_pct_p95": r(pct([g(x, "disk", "busy_pct_mean") for x in active], 95), 1),
            "lat_ms_p95": r(pct([g(x, "disk", "lat_ms_max") for x in active], 95), 1),
            "c_free_gb_min": r(pct([g(x, "disk", "c_free_gb") for x in rows], 0.0001), 0),
        },
        "net_mbps_p95": r(pct([x.get("net_mbps") for x in active], 95), 1),
        "hourly_utc": hourly,
        "cpu_core_h": {
            "machine": core_h(machine_s), "attributed": core_h(attributed_s),
            "residual_pct": r(100.0 * (machine_s - attributed_s) / machine_s, 1) if machine_s > 0 else None,
            "projects": {k: core_h(v) for k, v in sorted(proj.items(), key=lambda kv: -kv[1])},
            "buckets": {k: core_h(v) for k, v in sorted(buckets.items(), key=lambda kv: -kv[1])},
        },
        "heavy_jobs": heavy_jobs(day, by_ts, allow),
        "sampler": {
            "cpu_s": r(sum(g(x, "sampler", "cpu_s") or 0 for x in rows), 1),
            "ws_mb_max": max((g(x, "sampler", "ws_mb") or 0) for x in rows),
            "restarts": restarts,
        },
    }


# ---------------------------------------------------------------- git / bus

def git(cwd, *args, check=False):
    # Repository selectors are stripped: an inherited GIT_DIR/GIT_INDEX_FILE would aim the temp worktree's
    # add/commit at another repository (an inherited GIT_DIR once turned a shared repo bare).
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env["GIT_TERMINAL_PROMPT"] = "0"   # never wait on a credential prompt in a hidden task
    try:
        p = subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True, encoding="utf-8", errors="replace",
                           env=env, timeout=GIT_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        # inside the task's 15-minute limit, so the failing receipt is still written
        raise Unavailable(f"git {' '.join(args[:2])}: no answer in {GIT_TIMEOUT_S} s")
    if check and p.returncode != 0:
        raise Unavailable(f"git {' '.join(args)}: {p.stderr.strip()[:300]}")
    return p


def bus_files(bus: Path, ref="refs/remotes/origin/master"):
    p = git(bus, "ls-tree", "-r", "-z", ref, "--", BUS_DIR + "/")
    if p.returncode != 0:
        raise Unavailable(f"cannot list {BUS_DIR}/ at {ref}: {p.stderr.strip()[:200]}")
    out = []
    for entry in p.stdout.split("\0"):
        meta, _, path = entry.partition("\t")
        # blobs only: a gitlink or other non-blob entry named *.jsonl cannot be read, and must not stop the fleet
        if path.endswith(".jsonl") and meta.split(" ")[1:2] == ["blob"]:
            out.append(path)
    return out


def bus_rows(bus: Path, ref="refs/remotes/origin/master", misfiled=None):
    """Day rows on the bus. A row whose machine is not its directory's (single writer per directory) is not
    that machine's data: it is left out and the directory's machine is added to `misfiled`."""
    rows = []
    for f in bus_files(bus, ref):
        parts = f.split("/")
        owner = parts[1].upper() if len(parts) >= 3 else None
        p = git(bus, "show", f"{ref}:{f}")
        if p.returncode != 0:
            raise Unavailable(f"cannot read {f} at {ref}: {p.stderr.strip()[:200]}")   # never read as "no rows"
        for line in p.stdout.splitlines():
            try:
                row = json.loads(line)
            except ValueError:
                continue
            if not isinstance(row, dict) or row.get("schema") != DAY_SCHEMA:
                continue
            if owner is None or not isinstance(row.get("machine"), str) or "date" not in row:
                continue      # not filed under machine-load/<MACHINE>/, or missing its key: not any machine's row
            if owner is not None and str(row.get("machine", "")).upper() != owner:
                if misfiled is not None:
                    misfiled.add(owner)
                continue
            rows.append(row)
    return rows


def tool_commit():
    """The bus commit this copy was installed from (bin/manifest.json), else the checkout's HEAD."""
    try:
        c = json.loads((HERE / "manifest.json").read_text(encoding="utf-8-sig")).get("bus_commit")
        if c:
            return str(c)[:12]
    except (OSError, ValueError):
        pass
    return git(HERE, "rev-parse", "HEAD").stdout.strip()[:12] or None


def publish(bus: Path, data_dir: Path, dry_run=False, retries=5, look_back_days=RETENTION_DAYS):
    machine = socket.gethostname().upper()
    allow = load_projects()
    today = utc_now().date()
    report = []
    work = Path(tempfile.mkdtemp(prefix="machine-load-"))
    wt = work / "bus"
    try:
        for attempt in range(1, retries + 1):
            git(bus, "fetch", "-q", "origin", "master", check=True)
            base = git(bus, "rev-parse", "refs/remotes/origin/master").stdout.strip()
            have = {(x["machine"], x["date"]) for x in bus_rows(bus)}
            rows = []
            # Every retained, completed day: the files on disk (the sampler keeps RETENTION_DAYS), not a fixed
            # short window, so a long publisher outage loses no day the machine still holds.
            days = set()
            for f in data_dir.glob("minute-*.jsonl"):
                try:
                    days.add(dt.date.fromisoformat(f.stem[len("minute-"):]))
                except ValueError:
                    continue
            days |= {today - dt.timedelta(days=i) for i in range(1, look_back_days + 1)}
            for day in sorted(d for d in days if d < today):
                if (machine, day.isoformat()) in have:
                    continue
                row = rollup(data_dir, day, allow)
                if row:
                    row["machine"] = machine
                    row["published_utc"] = utc_now().strftime("%Y-%m-%dT%H:%M:%SZ")
                    row["tool_commit"] = tool_commit()
                    rows.append(row)
            if not rows:
                report.append(f"[machine-load] {machine}: nothing new to publish (bus {base[:12]})")
                return 0, report, base
            if dry_run:
                for row in rows:
                    print(json.dumps(row, separators=(",", ":")))
                report.append(f"[machine-load] dry run: {len(rows)} row(s) for {machine}")
                return 0, report, base
            if wt.exists():
                git(bus, "worktree", "remove", "--force", str(wt))
            git(bus, "worktree", "add", "-q", "--detach", str(wt), base, check=True)
            touched = []
            for row in rows:
                rel = f"{BUS_DIR}/{machine}/days-{row['date'][:7]}.jsonl"
                target = wt / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                old = target.read_bytes() if target.is_file() else b""
                if old and not old.endswith(b"\n"):
                    old += b"\n"
                target.write_bytes(old + json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + b"\n")
                touched.append(rel)
            git(wt, "add", "--", *sorted(set(touched)), check=True)
            dates = ", ".join(x["date"] for x in rows)
            msg = (f"metrics: machine-load {machine} {dates}\n\n"
                   f"Mechanical daily rows ({DAY_SCHEMA}) from tools/machine/machine-load; diagnostic only (metrics law 1).")
            git(wt, "commit", "-q", "-m", msg, check=True)   # the bus clone's own identity; never a made-up one
            p = git(wt, "push", "-q", "origin", "HEAD:refs/heads/master")
            if p.returncode == 0:
                head = git(wt, "rev-parse", "HEAD").stdout.strip()
                report.append(f"[machine-load] published {len(rows)} row(s) for {machine} ({dates}) at bus {head[:12]}")
                return 0, report, head
            report.append(f"[machine-load] push attempt {attempt} rejected: {p.stderr.strip()[:200]}")
        raise Unavailable(f"push failed after {retries} attempts")
    finally:
        if wt.exists():
            git(bus, "worktree", "remove", "--force", str(wt))
        git(bus, "worktree", "prune")
        shutil.rmtree(work, ignore_errors=True)


# ---------------------------------------------------------------- live summary (local only)

def summarize(data_dir: Path, hours: float):
    now = utc_now()
    since = now - dt.timedelta(hours=hours)
    rows, dup_ts = [], []
    day = since.date()
    while day <= now.date():
        got, _, _ = read_minutes(data_dir, day, dup_ts)
        # usable minutes inside [since, now]: a minute stamped in the future (a clock that was ahead) is not a
        # live observation and must never make the machine look fresh
        rows += [x for x in got if since <= parse_ts(x["ts"]) <= now and valid_minute(x)]
        day += dt.timedelta(days=1)
    usable = {x["ts"] for x in rows}
    dups = len({ts for ts in dup_ts if ts in usable})      # duplication inside the window, among usable minutes
    rows.sort(key=lambda x: x["ts"])
    state = {}
    try:
        state = json.loads((data_dir / "sampler-state.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        pass
    newest = parse_ts(rows[-1]["ts"]) if rows else None
    top = defaultdict(float)
    proj = defaultdict(float)
    for x in rows:
        for name, secs in x.get("top") or []:
            top[name] += secs
        for label, secs in (x.get("proj") or {}).items():
            proj[label] += secs
    busy = [g(x, "cpu", "busy_threads") for x in rows]
    return {
        "machine": socket.gethostname().upper(), "now_utc": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "hours": hours,
        "minutes": len(rows), "duplicate_min": dups, "newest_age_s": round((now - newest).total_seconds()) if newest else None,
        "code": rows[-1].get("code") if rows else None, "sampler_pid": state.get("pid"),
        "busy_threads_now": busy[-1] if busy else None, "busy_threads_p95": r(pct(busy, 95), 1),
        "busy_threads_max": r(pct(busy, 100), 1),
        "clock_pct_now": r(busy_clock(rows[-1]), 0) if rows else None,
        "avail_gb_min": r(pct([g(x, "mem", "avail_gb_min") for x in rows], 0.0001), 1),
        "c_free_gb": g(rows[-1], "disk", "c_free_gb") if rows else None,
        "pkg_w_max": r(pct([g(x, "thermal", "pkg_w_max") for x in rows], 100), 1),
        "core_c_max": r(pct([g(x, "thermal", "core_c_max") for x in rows], 100), 1),
        "core_h_by_label": {k: round(v / 3600, 3) for k, v in sorted(proj.items(), key=lambda kv: -kv[1])[:10]},
        "top_processes_core_h": {k: round(v / 3600, 3) for k, v in sorted(top.items(), key=lambda kv: -kv[1])[:8]},
    }


# ---------------------------------------------------------------- headroom (reader)

def clock_onset(rows):
    """Combine clock-by-load bands over days. Returns (light_clock, onset_threads|None, max_band_seen, table,
    gap_lo|None). Bands are walked in order from 0: an unmeasured band (< 10 minutes) before the first drop is a
    gap, and gap_lo is its low edge (the onset could be anywhere in it, so nothing above it is claimed). No 0-4
    baseline at all is a gap at 0: without the light-load clock, a drop measured higher up cannot be ruled out."""
    acc = defaultdict(lambda: [0, 0.0])
    for row in rows:
        for band, v in (g(row, "cpu", "clock_by_load") or {}).items():
            if v.get("perf_p50") is None:
                continue
            acc[band][0] += v["n"]
            acc[band][1] += v["n"] * v["perf_p50"]
    table = []
    for lo, hi in BANDS:
        key = f"{lo}-{min(hi, 32)}"
        if key in acc and acc[key][0] >= 10:
            table.append((lo, min(hi, 32), acc[key][0], acc[key][1] / acc[key][0]))
    if not table:
        return None, None, None, table, 0
    if table[0][0] != 0:
        return None, None, table[-1][1], table, 0   # no light-load baseline: nothing at all is claimed
    light = table[0][3]
    expected_lo = table[0][1]
    for lo, hi, n, perf in table[1:]:
        if lo != expected_lo:
            return light, None, table[-1][1], table, expected_lo   # a band between was never measured
        if perf < CLOCK_DROP * light:
            return light, lo, table[-1][1], table, None
        expected_lo = hi
    return light, None, table[-1][1], table, None


def headroom(bus: Path, days: int, expect, live: bool):
    fetched = git(bus, "fetch", "-q", "origin", "master").returncode == 0
    misfiled = set()
    rows = bus_rows(bus, misfiled=misfiled)
    today = utc_now().date()
    window_start = today - dt.timedelta(days=days)
    # --expect names the fleet: a machine that once published but is no longer expected (retired) is left out,
    # so it cannot hold the exit code at 1 forever. An empty --expect reads every machine on the bus.
    machines = sorted(set(expect)) if expect else sorted({x["machine"] for x in rows})
    newest_code = {}
    out = []
    for m in machines:
        rec = {"machine": m, "states": ["MISFILED"] if m in misfiled else []}
        mine, seen_dates = [], set()
        for x in sorted((x for x in rows if x["machine"] == m), key=lambda x: str(x.get("date"))):
            if not valid_day_row(x, today):
                if "INVALID-ROW" not in rec["states"]:
                    rec["states"].append("INVALID-ROW")   # future-dated, malformed or missing a required figure
                continue
            if x["date"] in seen_dates:
                if "DUPLICATED" not in rec["states"]:
                    rec["states"].append("DUPLICATED")   # one (machine, date) published twice: never counted twice
                continue
            seen_dates.add(x["date"])
            mine.append(x)
        if not mine:
            rec["states"].append("ABSENT")
            out.append(rec)
            continue
        newest = mine[-1]
        rec["newest_date"] = newest["date"]
        if dt.date.fromisoformat(newest["date"]) < today - dt.timedelta(days=2):
            rec["states"].append("STALE")
        win = [x for x in mine if dt.date.fromisoformat(x["date"]) >= window_start]
        good = [x for x in win if full_day(x)]
        if not good:
            rec["states"].append("LOW-COVERAGE")
        elif dt.date.fromisoformat(good[-1]["date"]) < today - dt.timedelta(days=FRESH_DAYS) and "STALE" not in rec["states"]:
            # a recent partial day must not vouch for old full days: the capacity figures themselves are stale
            rec["states"].append("STALE")
        if any(x.get("duplicate_min") for x in win) and "DUPLICATED" not in rec["states"]:
            rec["states"].append("DUPLICATED")
        if good and "STALE" not in rec["states"]:
            # The build behind the figures actually used: the newest FULL day's newest build (an upgrade day
            # carries two). Only machines whose data is in use compare: a retired or stale machine left on an
            # old build must not void everyone else's verdict.
            newest_code[m] = (good[-1].get("code") or [None])[-1]
        rec["days_used"] = len(good)
        rec["days_low_coverage"] = len(win) - len(good)
        use = good
        if not use:
            rec["verdict"] = "UNKNOWN"   # partial days are never read as a typical day, so never as spare capacity
            out.append(rec)
            continue
        lp = newest.get("lp") or 32
        busy_p95 = max(x["cpu"]["busy_threads_p95"] or 0 for x in use)
        busy_max = max(x["cpu"]["busy_threads_max"] or 0 for x in use)
        light, onset, seen_max, table, gap_lo = clock_onset(use)
        if onset is not None:
            safe, basis = onset, f"clock falls below {round(CLOCK_DROP * 100)} % of its light-load value from {onset} busy threads (measured)"
        elif gap_lo == 0:
            safe = 0
            basis = ("ASSUMED 0: no light-load (0-4 busy threads) clock was measured, so no thread count is "
                     "claimed safe")
        elif gap_lo is not None:
            safe = min(gap_lo, lp // 2)
            basis = (f"ASSUMED {safe}: the {gap_lo}-{gap_lo + 4} busy-thread band was never measured, so no onset "
                     f"above it is claimed")
        else:
            safe = lp // 2
            basis = (f"ASSUMED one busy thread per physical core ({lp // 2}); the clock never fell "
                     f"{round((1 - CLOCK_DROP) * 100)} % up to {seen_max} busy threads in this window")
        avail = min((x["mem"]["avail_gb_p05"] for x in use if x["mem"]["avail_gb_p05"] is not None), default=None)
        disk = min((x["disk"]["c_free_gb_min"] for x in use if x["disk"]["c_free_gb_min"] is not None), default=None)
        pkg95 = max((x["power"]["pkg_w_p95"] for x in use if x["power"]["pkg_w_p95"] is not None), default=None)
        threads_spare = max(0.0, safe - busy_p95)
        mem_spare = None if avail is None else max(0.0, avail - MEM_RESERVE_GB)
        disk_spare = None if disk is None else max(0.0, disk - DISK_FLOOR_GB)
        # tightest = the resource closest to its ROOM threshold (4 threads, 16 GB, 100 GB), whatever the machine's size
        limits = {"cpu": threads_spare / 4.0, "memory": (mem_spare or 0) / 16.0, "disk": (disk_spare or 0) / 100.0}
        binding = min(limits, key=limits.get)
        if threads_spare >= 4 and (mem_spare or 0) >= 16 and (disk_spare or 0) >= 100:
            verdict = "ROOM"
        elif threads_spare > 0 and (mem_spare or 0) > 0 and (disk_spare or 0) > 0:
            verdict = "TIGHT"
        else:
            verdict = "FULL"
        quiet_h = []
        for h in range(24):
            # quiet means quiet on EVERY day used, so every day must have measured that hour (>= 30 minutes)
            if any(x["hourly_utc"]["cov"][h] < 30 or x["hourly_utc"]["busy_p95"][h] is None for x in use):
                continue
            vals = [x["hourly_utc"]["busy_p95"][h] for x in use]
            if max(vals) < lp * QUIET_THREADS_FRACTION:
                quiet_h.append(h)
        proj = defaultdict(float)
        for x in use:
            for k, v in x["cpu_core_h"]["projects"].items():
                proj[k] += v
        heavy = defaultdict(list)
        for x in use:
            for k, v in (x.get("heavy_jobs") or {}).items():
                heavy[k].append((x["date"], v))
        rec.update({
            "verdict": verdict, "binding": binding, "lp": lp,
            "busy_threads_p95": busy_p95, "busy_threads_max": busy_max,
            "safe_threads": safe, "safe_basis": basis, "threads_spare": round(threads_spare, 1),
            "clock_table": [{"band": f"{lo}-{hi}", "minutes": n, "clock_pct": round(p, 1)} for lo, hi, n, p in table],
            "mem_avail_gb_p05": avail, "mem_spare_gb": None if mem_spare is None else round(mem_spare, 1),
            "c_free_gb_min": disk, "disk_spare_gb": None if disk_spare is None else round(disk_spare),
            "pkg_w_p95": pkg95,
            "core_h_per_day": round(sum(x["cpu_core_h"]["machine"] for x in use) / len(use), 1),
            "residual_pct_mean": r(sum(x["cpu_core_h"]["residual_pct"] or 0 for x in use) / len(use), 1),
            "projects_core_h_per_day": {k: round(v / len(use), 1) for k, v in sorted(proj.items(), key=lambda kv: -kv[1])},
            "quiet_hours_utc": quiet_h,
            "heavy_jobs": {k: v for k, v in heavy.items()},
            "sampler_cpu_s_per_day": round(sum(x["sampler"]["cpu_s"] or 0 for x in use) / len(use)),
        })
        out.append(rec)
    if len(set(newest_code.values())) > 1:
        for rec in out:
            if rec["machine"] in newest_code:
                rec["states"].append("MIXED-CODE")
    if live:
        for rec in out:
            rec["live"] = live_summary(rec["machine"])
            lv = rec["live"] or {}
            age = lv.get("newest_age_s")
            if not _num(age) or age < 0 or age > 300 or lv.get("duplicate_min"):
                rec["states"].append("LIVE-STALE")   # no usable minute in 5 min, or the live minutes are doubled
    for rec in out:
        if not fetched:
            rec["states"].append("BUS-NOT-REFRESHED")   # rows are whatever the clone last fetched
        if rec["states"] and rec.get("verdict") not in (None, "UNKNOWN"):
            # Any doubt about the data voids the verdict: stale or doubled data must never read as spare capacity.
            rec["verdict_untrusted"] = rec["verdict"]
            rec["verdict"] = "UNKNOWN"
    return out


def live_summary(machine):
    me = socket.gethostname().upper()
    if machine == me:
        return summarize(DATA_DIR, 1.0)
    alias = SSH_ALIAS.get(machine, machine.lower())
    cmd = ["ssh", "-n", "-o", "BatchMode=yes", "-o", "ConnectTimeout=8", alias,
           r"python C:\ProgramData\MachineLoad\bin\machine_load.py summarize --hours 1"]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=60, encoding="utf-8", errors="replace")
        return json.loads(p.stdout) if p.returncode == 0 else {"error": (p.stderr or p.stdout).strip()[:200]}
    except (subprocess.TimeoutExpired, ValueError, OSError) as e:
        return {"error": str(e)[:200]}


def to_local_hours(hours_utc):
    # Display in Central time (owner's zone); the data stays UTC.
    try:
        from zoneinfo import ZoneInfo
        tz = ZoneInfo("America/Chicago")
        base = dt.datetime.now(dt.timezone.utc).replace(minute=0, second=0, microsecond=0)
        return sorted({(base.replace(hour=h)).astimezone(tz).hour for h in hours_utc})
    except Exception:
        return None


def print_report(recs, days):
    print(f"Machine headroom - last {days} day(s), compute only (NOT Claude/Codex account quota, NOT gate slots)")
    print("Headroom = what can be added before work already running slows; diagnostic, never authority (metrics law 1).\n")
    for rec in recs:
        states = " ".join(rec["states"]) or "OK"
        print(f"== {rec['machine']}  [{states}]")
        if rec.get("verdict", "UNKNOWN") == "UNKNOWN" and "verdict_untrusted" not in rec:
            print("   VERDICT UNKNOWN - no full day of data in the window; never shown as spare capacity\n")
            continue
        if "verdict_untrusted" in rec:
            print(f"   VERDICT UNKNOWN - the data is {', '.join(rec['states'])}; the figures below are NOT a capacity answer")
        if rec["verdict"] != "UNKNOWN":
            print(f"   VERDICT {rec['verdict']} (tightest: {rec['binding']}); {rec['days_used']} full day(s), {rec['days_low_coverage']} partial")
        print(f"   CPU     p95 {rec['busy_threads_p95']} / max {rec['busy_threads_max']} busy threads of {rec['lp']}; "
              f"safe up to {rec['safe_threads']} -> {rec['threads_spare']} threads spare at the busiest 5 % of minutes")
        print(f"           basis: {rec['safe_basis']}")
        if rec["clock_table"]:
            print("           clock vs load: " + ", ".join(f"{c['band']} thr {c['clock_pct']}% ({c['minutes']}m)" for c in rec["clock_table"]))
        print(f"   Memory  {rec['mem_avail_gb_p05']} GB free at p05 -> {rec['mem_spare_gb']} GB spare after a {MEM_RESERVE_GB:.0f} GB reserve")
        print(f"   Disk    C: {rec['c_free_gb_min']} GB free (lowest) -> {rec['disk_spare_gb']} GB above the {DISK_FLOOR_GB:.0f} GB floor")
        pw = "no Core Temp feed" if rec["pkg_w_p95"] is None else f"package p95 {rec['pkg_w_p95']} W"
        print(f"   Power   {pw} (all-core work holds ~74 W on these minis)")
        print(f"   Work    {rec['core_h_per_day']} core-hours/day; by project {rec['projects_core_h_per_day']} "
              f"(unattributed {rec['residual_pct_mean']} %)")
        local = to_local_hours(rec["quiet_hours_utc"])
        print(f"   Quiet hours (p95 < {int(QUIET_THREADS_FRACTION * 100)} % CPU every day): UTC {rec['quiet_hours_utc']}" + (f" = Central {local}" if local is not None else ""))
        for k, v in rec["heavy_jobs"].items():
            print(f"   Heavy job {k}: " + "; ".join(f"{d} n={x['n']} p50 {x['dur_s_p50']}s at {x['busy_threads_during_p50']} thr" for d, x in v[-7:]))
        if rec.get("live"):
            lv = rec["live"]
            if "error" in lv:
                print(f"   LIVE    unreadable: {lv['error']}")
            else:
                print(f"   LIVE    now {lv['busy_threads_now']} thr (1 h p95 {lv['busy_threads_p95']}), clock {lv['clock_pct_now']} %, "
                      f"newest row {lv['newest_age_s']} s old; top {lv['top_processes_core_h']}")
        print()


# ---------------------------------------------------------------- main

def write_receipt(data_dir: Path, rec):
    """Returns True when written. A receipt that cannot be written is reported, never silent: otherwise an older
    exit-0 receipt would stay the last word on a failed run."""
    try:
        data_dir.mkdir(parents=True, exist_ok=True)
        (data_dir / "publish-receipt.json").write_text(json.dumps(rec, indent=1), encoding="utf-8")
        with (data_dir / "publish-receipts.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, separators=(",", ":")) + "\n")
        return True
    except OSError as e:
        print(f"[machine-load] RECEIPT NOT WRITTEN in {data_dir}: {e}", file=sys.stderr)
        return False


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("rollup"); a.add_argument("--day", required=True); a.add_argument("--dir", type=Path, default=DATA_DIR)
    a = sub.add_parser("publish"); a.add_argument("--bus", type=Path, required=True); a.add_argument("--dir", type=Path, default=DATA_DIR); a.add_argument("--dry-run", action="store_true"); a.add_argument("--receipt-dir", type=Path, default=RECEIPT_DIR)
    a.add_argument("--launched-by", choices=["task", "hand"], default="hand")
    a = sub.add_parser("summarize"); a.add_argument("--hours", type=float, default=1.0); a.add_argument("--dir", type=Path, default=DATA_DIR)
    a = sub.add_parser("headroom"); a.add_argument("--bus", type=Path, required=True); a.add_argument("--days", type=int, default=7)
    a.add_argument("--live", action="store_true"); a.add_argument("--json", action="store_true")
    a.add_argument("--expect", default="PC-MINI1,PC-MINI2,PC-MINI3")
    args = ap.parse_args(argv)

    if args.cmd == "rollup":
        row = rollup(args.dir, dt.date.fromisoformat(args.day))
        if row is None:
            print(f"no minute rows for {args.day} in {args.dir}", file=sys.stderr)
            return 2
        print(json.dumps(row, indent=1))
        return 0
    if args.cmd == "summarize":
        print(json.dumps(summarize(args.dir, args.hours), indent=1))
        return 0
    if args.cmd == "publish":
        started = utc_now().strftime("%Y-%m-%dT%H:%M:%SZ")
        launched_by = args.launched_by
        try:
            code, report, head = publish(args.bus, args.dir, args.dry_run)
        except Unavailable as e:
            code, report, head = 3, [f"[machine-load] FAILED: {e}"], None
        except Exception as e:  # any crash still leaves a failing receipt, never an older exit-0 one as the last word
            code, report, head = 3, [f"[machine-load] CRASHED: {type(e).__name__}: {e}"], None
        for line in report:
            print(line)
        if not args.dry_run:
            if not write_receipt(args.receipt_dir, {"utc": started, "machine": socket.gethostname().upper(), "launched_by": launched_by,
                                                    "exit": code, "bus_head": head, "report": report}):
                return code or 4
        return code
    if args.cmd == "headroom":
        try:
            recs = headroom(args.bus, args.days, [m.strip().upper() for m in args.expect.split(",") if m.strip()], args.live)
        except Unavailable as e:
            print(f"UNEVALUABLE: {e}", file=sys.stderr)
            return 2
        if args.json:
            print(json.dumps(recs, indent=1))
        else:
            print_report(recs, args.days)
        return 1 if any(rec["states"] for rec in recs) else 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
