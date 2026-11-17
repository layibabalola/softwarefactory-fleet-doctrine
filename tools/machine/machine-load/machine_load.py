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

Exit codes: 0 ok; 1 headroom: a machine is ABSENT, STALE, LOW-COVERAGE, DUPLICATED or MIXED-CODE (data you
cannot trust is never shown as spare capacity); 2 bad input or unreadable data; 3 publish failed.
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
BANDS = [(0, 4), (4, 8), (8, 12), (12, 16), (16, 20), (20, 24), (24, 28), (28, 33)]
FULL_DAY = 1440
LOW_COVERAGE = 1200          # minutes; a day with less is reported, never trusted as a typical day
QUIET_THREADS_FRACTION = 0.10  # FleetQuiet WaitQuiet treats CPU < 10 % as quiet
MEM_RESERVE_GB = 16.0
DISK_FLOOR_GB = 50.0         # owner rule 2026-10-11: never leave a volume below 50 GB
CLOCK_DROP = 0.90            # a load band whose clock is < 90 % of the light-load clock is where work slows
SSH_ALIAS = {"PC-MINI1": "pc-mini1", "PC-MINI2": "pc-mini2", "PC-MINI3": "pc-mini3"}


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


def load_projects():
    cfg = json.loads((HERE / "projects.json").read_text(encoding="utf-8"))
    return set(cfg.get("publish", []))


def public_label(label, allow):
    if label.startswith("~"):
        return label
    return label if label in allow else "~other-project"


def read_minutes(data_dir: Path, day: dt.date):
    """Rows for one UTC day, de-duplicated by minute. Returns (rows, duplicate_minutes, unparseable)."""
    path = data_dir / f"minute-{day.isoformat()}.jsonl"
    rows, seen, dups, bad = [], set(), 0, 0
    if not path.is_file():
        return rows, 0, 0
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
            if row["ts"] in seen:
                dups += 1
                continue
            seen.add(row["ts"])
            rows.append(row)
    rows.sort(key=lambda x: x["ts"])
    return rows, dups, bad


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
    admits = {}
    try:
        with HEAVYSLOT_LEDGER.open(encoding="utf-8", errors="replace") as fh:
            for line in fh:
                try:
                    ev = json.loads(line)
                except ValueError:
                    continue
                if ev.get("event") == "admit":
                    admits[ev.get("ticket")] = ev
                elif ev.get("event") == "exit" and ev.get("ticket") in admits:
                    a = admits.pop(ev["ticket"])
                    end = parse_iso(ev["at"])
                    if end.date() != day:
                        continue
                    start = parse_iso(a["at"])
                    parts = str(a.get("label", "?:?")).split(":")
                    key = f"{public_label(parts[0], allow)}:{parts[1] if len(parts) > 1 else '?'}"
                    o = out[key]
                    o["n"] += 1
                    o["dur"].append((end - start).total_seconds())
                    t = start.replace(second=0, microsecond=0)
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
        "code": sorted({x.get("code") for x in rows if x.get("code")}),
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
            "avail_gb_p05": r(pct([g(x, "mem", "avail_gb_min") for x in active], 5), 1),
            "avail_gb_min": r(pct([g(x, "mem", "avail_gb_min") for x in rows], 0.0001), 1),
            "commit_pct_p95": r(pct([g(x, "mem", "commit_pct_max") for x in active], 95), 1),
            "hard_faults_p95": r(pct([g(x, "mem", "hard_faults_mean") for x in active], 95), 1),
        },
        "disk": {
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
    p = subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if check and p.returncode != 0:
        raise Unavailable(f"git {' '.join(args)}: {p.stderr.strip()[:300]}")
    return p


def bus_files(bus: Path, ref="refs/remotes/origin/master"):
    p = git(bus, "ls-tree", "-r", "--name-only", ref, "--", BUS_DIR + "/")
    if p.returncode != 0:
        raise Unavailable(f"cannot list {BUS_DIR}/ at {ref}: {p.stderr.strip()[:200]}")
    return [f for f in p.stdout.splitlines() if f.endswith(".jsonl")]


def bus_rows(bus: Path, ref="refs/remotes/origin/master"):
    rows = []
    for f in bus_files(bus, ref):
        p = git(bus, "show", f"{ref}:{f}")
        for line in p.stdout.splitlines():
            try:
                row = json.loads(line)
            except ValueError:
                continue
            if row.get("schema") == DAY_SCHEMA:
                rows.append(row)
    return rows


def publish(bus: Path, data_dir: Path, dry_run=False, retries=5, look_back_days=10):
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
            for i in range(look_back_days, 0, -1):
                day = today - dt.timedelta(days=i)
                if (machine, day.isoformat()) in have:
                    continue
                row = rollup(data_dir, day, allow)
                if row:
                    row["machine"] = machine
                    row["published_utc"] = utc_now().strftime("%Y-%m-%dT%H:%M:%SZ")
                    row["tool_commit"] = git(HERE, "rev-parse", "HEAD").stdout.strip()[:12] or None
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
    rows = []
    for day in {since.date(), now.date()}:
        rows += [x for x in read_minutes(data_dir, day)[0] if parse_ts(x["ts"]) >= since]
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
        "minutes": len(rows), "newest_age_s": round((now - newest).total_seconds()) if newest else None,
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
    """Combine clock-by-load bands over days. Returns (light_clock, onset_threads|None, max_band_seen, table)."""
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
        return None, None, None, table
    light = table[0][3]
    onset = next((lo for lo, hi, n, perf in table[1:] if perf < CLOCK_DROP * light), None)
    return light, onset, table[-1][1], table


def headroom(bus: Path, days: int, expect, live: bool):
    git(bus, "fetch", "-q", "origin", "master")
    rows = bus_rows(bus)
    today = utc_now().date()
    window_start = today - dt.timedelta(days=days)
    machines = sorted({x["machine"] for x in rows} | set(expect))
    newest_code = {}
    out = []
    for m in machines:
        mine = sorted((x for x in rows if x["machine"] == m), key=lambda x: x["date"])
        rec = {"machine": m, "states": []}
        if not mine:
            rec["states"].append("ABSENT")
            out.append(rec)
            continue
        newest = mine[-1]
        rec["newest_date"] = newest["date"]
        if dt.date.fromisoformat(newest["date"]) < today - dt.timedelta(days=2):
            rec["states"].append("STALE")
        win = [x for x in mine if dt.date.fromisoformat(x["date"]) >= window_start]
        good = [x for x in win if x.get("coverage_min", 0) >= LOW_COVERAGE]
        if not good:
            rec["states"].append("LOW-COVERAGE")
        if any(x.get("duplicate_min") for x in win):
            rec["states"].append("DUPLICATED")
        newest_code[m] = tuple(newest.get("code") or [])
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
        light, onset, seen_max, table = clock_onset(use)
        if onset is not None:
            safe, basis = onset, f"clock falls below {int(CLOCK_DROP * 100)} % of its light-load value from {onset} busy threads (measured)"
        else:
            safe = lp // 2
            basis = (f"ASSUMED one busy thread per physical core ({lp // 2}); the clock never fell "
                     f"{int((1 - CLOCK_DROP) * 100)} % up to {seen_max} busy threads in this window")
        avail = min((x["mem"]["avail_gb_p05"] for x in use if x["mem"]["avail_gb_p05"] is not None), default=None)
        disk = min((x["disk"]["c_free_gb_min"] for x in use if x["disk"]["c_free_gb_min"] is not None), default=None)
        pkg95 = max((x["power"]["pkg_w_p95"] or 0 for x in use), default=None)
        threads_spare = max(0.0, safe - busy_p95)
        mem_spare = None if avail is None else max(0.0, avail - MEM_RESERVE_GB)
        disk_spare = None if disk is None else max(0.0, disk - DISK_FLOOR_GB)
        limits = {"cpu": threads_spare / max(1, safe), "memory": (mem_spare or 0) / 94.0, "disk": (disk_spare or 0) / 2000.0}
        binding = min(limits, key=limits.get)
        if threads_spare >= 4 and (mem_spare or 0) >= 16 and (disk_spare or 0) >= 100:
            verdict = "ROOM"
        elif threads_spare > 0 and (mem_spare or 0) > 0 and (disk_spare or 0) > 0:
            verdict = "TIGHT"
        else:
            verdict = "FULL"
        quiet_h = []
        for h in range(24):
            vals = [x["hourly_utc"]["busy_p95"][h] for x in use if x["hourly_utc"]["cov"][h] >= 30 and x["hourly_utc"]["busy_p95"][h] is not None]
            if vals and max(vals) < lp * QUIET_THREADS_FRACTION:
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
            age = (rec["live"] or {}).get("newest_age_s")
            if age is None or age > 300:
                rec["states"].append("LIVE-STALE")
    return out


def live_summary(machine):
    me = socket.gethostname().upper()
    if machine == me:
        return summarize(DEFAULT_DIR, 1.0)
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
        if rec.get("verdict", "UNKNOWN") == "UNKNOWN":
            print("   VERDICT UNKNOWN - no full day of data in the window; never shown as spare capacity\n")
            continue
        print(f"   VERDICT {rec['verdict']} (tightest: {rec['binding']}); {rec['days_used']} full day(s), {rec['days_low_coverage']} partial")
        print(f"   CPU     p95 {rec['busy_threads_p95']} / max {rec['busy_threads_max']} busy threads of {rec['lp']}; "
              f"safe up to {rec['safe_threads']} -> {rec['threads_spare']} threads spare at the busiest 5 % of minutes")
        print(f"           basis: {rec['safe_basis']}")
        if rec["clock_table"]:
            print("           clock vs load: " + ", ".join(f"{c['band']} thr {c['clock_pct']}% ({c['minutes']}m)" for c in rec["clock_table"]))
        print(f"   Memory  {rec['mem_avail_gb_p05']} GB free at p05 -> {rec['mem_spare_gb']} GB spare after a {MEM_RESERVE_GB:.0f} GB reserve")
        print(f"   Disk    C: {rec['c_free_gb_min']} GB free (lowest) -> {rec['disk_spare_gb']} GB above the {DISK_FLOOR_GB:.0f} GB floor")
        print(f"   Power   package p95 {rec['pkg_w_p95']} W (all-core work holds ~74 W on these minis)")
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
    try:
        data_dir.mkdir(parents=True, exist_ok=True)
        (data_dir / "publish-receipt.json").write_text(json.dumps(rec, indent=1), encoding="utf-8")
        with (data_dir / "publish-receipts.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, separators=(",", ":")) + "\n")
    except OSError:
        pass


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("rollup"); a.add_argument("--day", required=True); a.add_argument("--dir", type=Path, default=DEFAULT_DIR)
    a = sub.add_parser("publish"); a.add_argument("--bus", type=Path, required=True); a.add_argument("--dir", type=Path, default=DEFAULT_DIR); a.add_argument("--dry-run", action="store_true")
    a.add_argument("--launched-by", choices=["task", "hand"], default="hand")
    a = sub.add_parser("summarize"); a.add_argument("--hours", type=float, default=1.0); a.add_argument("--dir", type=Path, default=DEFAULT_DIR)
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
        for line in report:
            print(line)
        if not args.dry_run:
            write_receipt(args.dir, {"utc": started, "machine": socket.gethostname().upper(), "launched_by": launched_by,
                                     "exit": code, "bus_head": head, "report": report})
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
