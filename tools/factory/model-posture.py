#!/usr/bin/env python3
"""Fleet model-posture telemetry (CANDIDATE, specs/fleet-model-posture/spec.md). Stdlib only, deterministic.

Which model and effort did each project's seats ACTUALLY run, against what it declared and what the owner
posture (policy/model-posture.json) says? Raw per-call rows stay in the project; only aggregates travel.

  reduce   local per-call rows (provider-usage-event-v1 JSONL) -> one weekly shard on stdout
  view     declared vs actual vs owner posture, advisory codes; printed, NEVER stored; exit never depends on values
  publish  screen + budget a weekly shard, write metrics/<project>/posture-YYYY-Www.jsonl in a bus checkout
  prune    weekly -> monthly after 8 weeks, monthly -> yearly after 12 months; one commit per roll-up that only
           adds (or replaces) the rollup and deletes its sources, after byte-identical recomputation

Records conform to schemas/model-posture-rollup-v1.schema.json (additionalProperties:false everywhere). Every
record is screened by the union of the bus scorecard SCREEN and Conjugal's doctrine-outbox LAW4 plus a field
whitelist; a breach is REFUSED, never edited and never warned past. Metrics are diagnostic (metrics/README.md
law 1): nothing here is a gate.

Exit: 0 ok (view: always, whatever it finds), 2 refused/usage error (code on stderr).
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import os
import pathlib
import re
import subprocess
import sys

SCHEMA = "fleet/model-posture-rollup/v1"
POLICY_SCHEMA = "fleet/model-posture-policy/v1"
TOOL_PATH = "tools/factory/model-posture.py"
MEASURES = ("input_tokens", "cached_input_tokens", "reasoning_tokens", "output_tokens", "active_seconds")
OUTCOMES = ("WIP", "COMPLETED", "APPROVED", "CHANGES_REQUESTED", "BLOCKED", "REFUSED", "QUOTA_DORMANT",
            "NO_ACTIONABLE_WORK", "FAILED", "UNKNOWN")
ACCEPT = ("APPROVED", "COMPLETED")
KEY = ("provider", "model_requested", "model_effective", "effort_effective", "role")
FALLBACK_CODE = re.compile(r"(?:^|_)FALLBACK(?:_|$)")
# soft, hard bytes per shard grain; one project's posture-* files together never exceed PROJECT_CAP.
BUDGET = {"week": (8 * 1024, 16 * 1024), "month": (30 * 1024, 60 * 1024), "year": (30 * 1024, 60 * 1024)}
PROJECT_CAP = 256 * 1024
WEEKS_BEFORE_MONTHLY = 8
MONTHS_BEFORE_YEARLY = 12

PROJECT_RX = re.compile(r"^[a-z0-9][a-z0-9._-]{0,79}$")
NAME_RX = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:+/-]{0,119}$")   # provider-usage-event-v1 model pattern
EFFORT_RX = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,39}$")
ROLE_RX = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,79}$")
PROVIDER_RX = re.compile(r"^[a-z0-9-]{2,40}$")
WEEK_RX = re.compile(r"^(\d{4})-W(\d{2})$")
MONTH_RX = re.compile(r"^(\d{4})-(\d{2})$")
YEAR_RX = re.compile(r"^(\d{4})$")
SHARD_RX = re.compile(r"^posture-(\d{4}(?:-W\d{2}|-\d{2})?)\.jsonl$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")

# The union of bus tools/factory/fleet-scorecard.py SCREEN and Conjugal coordination/tools/doctrine_outbox.py
# LAW4 (2026-10-22), plus classes this data plane adds. Applied to every serialized record.
SCREEN = (
    ("email address", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),
    ("account/org uuid", re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", re.I)),
    ("bearer/API token", re.compile(r"\b(sk-ant-|sk-|pk1:|gh[pousr]_[A-Za-z0-9]{20,}|Bearer\s+[A-Za-z0-9._-]{20,})")),
    ("user home path", re.compile(r"(?:[A-Za-z]:[\\/]+Users[\\/]+|/Users/|/home/)[^\s\\/\"]+", re.I)),
    ("project coordination path", re.compile(r"coordination[\\/]")),
    ("lane wire path", re.compile(r"coordination/(lanes|comms)/")),
    ("HUB heartbeat", re.compile(r"\bHUB\.md\b")),
    ("owner transcript store", re.compile(r"loops\.json")),
    ("owner state dir", re.compile(r"(?<![A-Za-z0-9_./-])state/")),
    ("dead-man floor surface", re.compile(r"coordination/deadman/")),
    ("project subject id", re.compile(r"\bS\d+\b")),
    ("project-internal identifier", re.compile(r"\bpairprog_\w*", re.I)),
    # This data plane's own never-publish classes.
    ("per-call timestamp", re.compile(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}")),
    ("windows drive path", re.compile(r"\b[A-Za-z]:[\\/]")),
    ("quota/utilization field", re.compile(r"(?i)quota|utiliz|window_pct|_pct\b")),
    ("session/account field", re.compile(r"(?i)session|account|org_id|email")),
)


class Refused(Exception):
    def __init__(self, code, detail=""):
        super().__init__(f"{code}: {detail}" if detail else code)
        self.code, self.detail = code, detail


# ---------- periods ----------

def week_of(ts: str) -> str:
    t = dt.datetime.fromisoformat(ts.strip().replace("Z", "+00:00"))
    t = (t if t.tzinfo else t.replace(tzinfo=dt.timezone.utc)).astimezone(dt.timezone.utc)
    y, w, _ = t.isocalendar()
    return f"{y}-W{w:02d}"


def week_thursday(week: str) -> dt.date:
    m = WEEK_RX.match(week)
    if not m:
        raise Refused("PERIOD_INVALID", week)
    return dt.date.fromisocalendar(int(m.group(1)), int(m.group(2)), 4)


def month_of_week(week: str) -> str:
    """An ISO week belongs to the month of its Thursday (the ISO rule that also decides its year)."""
    d = week_thursday(week)
    return f"{d.year}-{d.month:02d}"


def grain_of(period: str) -> str:
    if WEEK_RX.match(period):
        week_thursday(period)
        return "week"
    if MONTH_RX.match(period) and 1 <= int(period[5:]) <= 12:
        return "month"
    if YEAR_RX.match(period):
        return "year"
    raise Refused("PERIOD_INVALID", period)


def parent_period(period: str) -> str:
    g = grain_of(period)
    if g == "week":
        return month_of_week(period)
    if g == "month":
        return period[:4]
    raise Refused("PERIOD_INVALID", f"{period} has no parent")


def shard_name(period: str) -> str:
    grain_of(period)
    return f"posture-{period}.jsonl"


# ---------- statistics ----------

def nearest_rank(values: list[int], q: float) -> int:
    s = sorted(values)
    return s[max(0, math.ceil(q * len(s)) - 1)]


def weighted_median(pairs: list[tuple[int, int]]) -> int:
    """Deterministic: the value at which cumulative weight first reaches half (ties broken by value)."""
    pairs = sorted((v, w) for v, w in pairs if w > 0)
    if not pairs:
        return 0
    total, acc = sum(w for _, w in pairs), 0
    for v, w in pairs:
        acc += w
        if 2 * acc >= total:
            return v
    return pairs[-1][0]


def stat(values: list[int]) -> dict:
    if not values:
        return {"known": 0, "sum": 0, "p50": 0, "p90": 0}
    return {"known": len(values), "sum": sum(values), "p50": nearest_rank(values, 0.5), "p90": nearest_rank(values, 0.9)}


def merge_stat(parts: list[dict]) -> dict:
    """Roll-up: counts and sums add exactly; p50/p90 become the known-weighted median of the parts' values
    (spec: percentile_basis 'weighted-shard-percentiles'). Deterministic, so recomputation is byte-identical."""
    return {"known": sum(p["known"] for p in parts), "sum": sum(p["sum"] for p in parts),
            "p50": weighted_median([(p["p50"], p["known"]) for p in parts]),
            "p90": weighted_median([(p["p90"], p["known"]) for p in parts])}


# ---------- generator identity ----------

def blob_id(data: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def generator() -> dict:
    data = pathlib.Path(__file__).read_bytes().replace(b"\r\n", b"\n")
    return {"path": TOOL_PATH, "blob": blob_id(data)}


# ---------- reduce ----------

def _int_or_none(v):
    if isinstance(v, bool):
        return None
    if isinstance(v, int) and v >= 0:
        return v
    return None


def _clean(v, rx, field):
    if v is None or v == "":
        return None
    if not isinstance(v, str) or not rx.match(v):
        raise Refused("INPUT_FIELD_INVALID", f"{field}={str(v)[:40]!r}")
    return v


def reduce_events(events: list[dict], project: str, week: str, gen: dict | None = None) -> list[dict]:
    """provider-usage-event-v1 TERMINAL events of one ISO week -> sorted aggregate records. Every other event
    kind is ignored (it is not a call). Grouping fields never travel: task_id_hash only counts rounds."""
    if not PROJECT_RX.match(project):
        raise Refused("PROJECT_INVALID", project)
    if grain_of(week) != "week":
        raise Refused("PERIOD_INVALID", f"reduce needs an ISO week, got {week}")
    groups: dict[tuple, list[dict]] = {}
    for i, e in enumerate(events):
        if not isinstance(e, dict):
            raise Refused("INPUT_ROW_INVALID", f"row {i} is not an object")
        if e.get("event") != "TERMINAL":
            continue
        if e.get("project") != project:
            raise Refused("INPUT_PROJECT_MISMATCH", f"row {i}: {str(e.get('project'))[:40]!r}")
        try:
            if week_of(str(e.get("ts", ""))) != week:
                continue
        except ValueError:
            raise Refused("INPUT_ROW_INVALID", f"row {i}: ts unparseable") from None
        actor = e.get("actor") if isinstance(e.get("actor"), dict) else {}
        key = (_clean(e.get("provider"), PROVIDER_RX, "provider"),
               _clean(e.get("model_requested"), NAME_RX, "model_requested"),
               _clean(e.get("model_effective"), NAME_RX, "model_effective"),
               _clean(e.get("effort_effective"), EFFORT_RX, "effort_effective"),
               _clean(actor.get("role"), ROLE_RX, "actor.role"))
        if key[0] is None:
            raise Refused("INPUT_FIELD_INVALID", f"row {i}: provider missing")
        groups.setdefault(key, []).append({**e, "_i": i})
    gen = gen or generator()
    out = []
    for key in sorted(groups, key=lambda k: tuple("" if v is None else v for v in k)):
        rows = groups[key]
        meas = {m: [] for m in MEASURES}
        hist = {o: 0 for o in OUTCOMES}
        fallback = 0
        tasks: dict[str, list[dict]] = {}
        for r in rows:
            mm = r.get("measurement") if isinstance(r.get("measurement"), dict) else {}
            for m in MEASURES:
                v = _int_or_none(mm.get(m))
                if v is not None:
                    meas[m].append(v)
            o = r.get("outcome")
            hist[o if o in OUTCOMES else "UNKNOWN"] += 1
            codes = r.get("reason_codes") if isinstance(r.get("reason_codes"), list) else []
            req, eff = r.get("model_requested"), r.get("model_effective")
            if any(isinstance(c, str) and FALLBACK_CODE.search(c) for c in codes) or (req and eff and req != eff):
                fallback += 1
            t = r.get("task_id_hash") or f"row:{r['_i']}"
            tasks.setdefault(str(t), []).append(r)
        rounds = [len(v) for v in tasks.values()]
        first_pass = 0
        for v in tasks.values():
            first = min(v, key=lambda r: (str(r.get("ts")), r["_i"]))
            if first.get("outcome") in ACCEPT:
                first_pass += 1
        out.append({
            "schema": SCHEMA, "grain": "week", "period": week, "project": project,
            **dict(zip(KEY, key)),
            "calls": len(rows), "tasks": len(tasks),
            "measurement": {m: stat(meas[m]) for m in MEASURES},
            "rounds": stat(rounds),
            "outcome": {o: n for o, n in hist.items() if n},
            "first_pass_accept": first_pass, "fallback_count": fallback,
            "percentile_basis": "calls", "generator": gen,
        })
    return out


def merge_records(records: list[dict], project: str, period: str, sources: list[dict], gen: dict | None = None) -> list[dict]:
    grain = grain_of(period)
    groups: dict[tuple, list[dict]] = {}
    for r in records:
        if r.get("project") != project:
            raise Refused("SOURCE_PROJECT_MISMATCH", str(r.get("project"))[:40])
        groups.setdefault(tuple(r.get(k) for k in KEY), []).append(r)
    gen = gen or generator()
    out = []
    for key in sorted(groups, key=lambda k: tuple("" if v is None else v for v in k)):
        rows = groups[key]
        hist: dict[str, int] = {}
        for r in rows:
            for o, n in r["outcome"].items():
                hist[o] = hist.get(o, 0) + n
        out.append({
            "schema": SCHEMA, "grain": grain, "period": period, "project": project,
            **dict(zip(KEY, key)),
            "calls": sum(r["calls"] for r in rows), "tasks": sum(r["tasks"] for r in rows),
            "measurement": {m: merge_stat([r["measurement"][m] for r in rows]) for m in MEASURES},
            "rounds": merge_stat([r["rounds"] for r in rows]),
            "outcome": {o: hist[o] for o in OUTCOMES if hist.get(o)},
            "first_pass_accept": sum(r["first_pass_accept"] for r in rows),
            "fallback_count": sum(r["fallback_count"] for r in rows),
            "percentile_basis": "weighted-shard-percentiles", "generator": gen,
            "sources": sources,
        })
    return out


def serialize(records: list[dict]) -> bytes:
    return "".join(json.dumps(r, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n"
                   for r in records).encode("ascii")


# ---------- validation: the field whitelist (mirrors schemas/model-posture-rollup-v1.schema.json) ----------

STAT_KEYS = {"known", "sum", "p50", "p90"}
TOP_REQUIRED = {"schema", "grain", "period", "project", *KEY, "calls", "tasks", "measurement", "rounds", "outcome",
                "first_pass_accept", "fallback_count", "percentile_basis", "generator"}


def _nonneg(v) -> bool:
    return isinstance(v, int) and not isinstance(v, bool) and v >= 0


def validate(r: dict) -> None:
    def bad(why):
        raise Refused("RECORD_INVALID", why)
    if not isinstance(r, dict):
        bad("not an object")
    allowed = TOP_REQUIRED | {"sources"}
    extra = set(r) - allowed
    if extra:
        bad(f"field not in whitelist: {sorted(extra)[0]}")
    missing = TOP_REQUIRED - set(r)
    if missing:
        bad(f"missing {sorted(missing)[0]}")
    if r["schema"] != SCHEMA:
        bad("schema")
    if not isinstance(r["period"], str) or r["grain"] != grain_of(r["period"]):
        bad("grain/period")
    if not isinstance(r["project"], str) or not PROJECT_RX.match(r["project"]):
        bad("project")
    if not isinstance(r["provider"], str) or not PROVIDER_RX.match(r["provider"]):
        bad("provider")
    for k, rx in (("model_requested", NAME_RX), ("model_effective", NAME_RX), ("effort_effective", EFFORT_RX), ("role", ROLE_RX)):
        if r[k] is not None and (not isinstance(r[k], str) or not rx.match(r[k])):
            bad(k)
    for k in ("calls", "tasks", "first_pass_accept", "fallback_count"):
        if not _nonneg(r[k]):
            bad(k)
    if r["first_pass_accept"] > r["tasks"] or r["fallback_count"] > r["calls"] or r["tasks"] > r["calls"]:
        bad("counts inconsistent")
    m = r["measurement"]
    if not isinstance(m, dict) or set(m) != set(MEASURES):
        bad("measurement keys")
    for s in [*m.values(), r["rounds"]]:
        if not isinstance(s, dict) or set(s) != STAT_KEYS or not all(_nonneg(s[k]) for k in STAT_KEYS):
            bad("stat shape")
    if not isinstance(r["outcome"], dict) or not set(r["outcome"]) <= set(OUTCOMES) or not all(_nonneg(v) for v in r["outcome"].values()):
        bad("outcome")
    if sum(r["outcome"].values()) != r["calls"]:
        bad("outcome histogram does not sum to calls")
    if r["percentile_basis"] not in ("calls", "weighted-shard-percentiles"):
        bad("percentile_basis")
    g = r["generator"]
    if not isinstance(g, dict) or set(g) != {"path", "blob"} or g["path"] != TOOL_PATH or not HEX40.match(str(g["blob"])):
        bad("generator")
    if r["grain"] == "week":
        if "sources" in r:
            bad("a weekly record has no sources")
    else:
        src = r.get("sources")
        if not isinstance(src, list) or not src:
            bad("a rollup needs sources")
        for s in src:
            if not isinstance(s, dict) or set(s) != {"path", "blob"} or not HEX40.match(str(s["blob"])):
                bad("source shape")
            pm = re.match(r"^metrics/([a-z0-9][a-z0-9._-]{0,79})/(posture-[0-9W-]+\.jsonl)$", str(s["path"]))
            if not pm or pm.group(1) != r["project"] or not SHARD_RX.match(pm.group(2)):
                bad("source path")


def screen(data: bytes) -> None:
    text = data.decode("ascii")
    for name, rx in SCREEN:
        m = rx.search(text)
        if m:
            raise Refused("SCREEN_REFUSED", f"{name}: {m.group(0)[:24]!r}")
    for line in text.splitlines():
        r = json.loads(line)
        hexes = [s for s in re.findall(r"\b[0-9a-f]{40}\b", line)]
        legal = {r["generator"]["blob"], *(s["blob"] for s in r.get("sources", []))}
        if any(h not in legal for h in hexes):
            raise Refused("SCREEN_REFUSED", "a 40-hex value outside generator.blob/sources[].blob")


def check_shard(data: bytes, project: str, period: str) -> None:
    """Whitelist + screen + budget. Refuses; never truncates, never edits."""
    if not data:
        return
    for line in data.decode("ascii").splitlines():
        try:
            r = json.loads(line)
        except ValueError:
            raise Refused("RECORD_INVALID", "unparseable line") from None
        validate(r)
        if r["project"] != project or r["period"] != period:
            raise Refused("RECORD_INVALID", "record outside this shard's project/period")
    screen(data)
    soft, hard = BUDGET[grain_of(period)]
    if len(data) > hard:
        raise Refused("SHARD_OVER_BUDGET", f"{shard_name(period)} {len(data)} B > {hard} B hard cap")


def budget_note(data: bytes, period: str) -> str | None:
    soft, _ = BUDGET[grain_of(period)]
    return f"SHARD_OVER_SOFT_BUDGET {len(data)} B > {soft} B" if len(data) > soft else None


def project_total(project_dir: pathlib.Path, replacing: dict[str, int]) -> int:
    total = 0
    names = set(replacing)
    if project_dir.is_dir():
        for p in project_dir.iterdir():
            if SHARD_RX.match(p.name):
                names.add(p.name)
    for n in names:
        if n in replacing:
            total += replacing[n]
        else:
            total += (project_dir / n).stat().st_size
    return total


# ---------- inputs ----------

def read_events(path: str) -> list[dict]:
    text = sys.stdin.read() if path == "-" else pathlib.Path(path).read_text(encoding="utf-8")
    out = []
    for n, line in enumerate(text.splitlines(), 1):
        if line.strip():
            try:
                out.append(json.loads(line))
            except ValueError:
                raise Refused("INPUT_ROW_INVALID", f"line {n} unparseable") from None
    return out


def read_records(paths: list[str]) -> list[dict]:
    out = []
    for p in paths:
        for line in pathlib.Path(p).read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                validate(r)
                out.append(r)
    return out


# ---------- view ----------

def load_policy(path: str) -> dict:
    try:
        pol = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise Refused("POLICY_UNREADABLE", f"{path}: {e.__class__.__name__}") from None
    if pol.get("schema") != POLICY_SCHEMA:
        raise Refused("POLICY_INVALID", "schema")
    for k in ("reassess_by", "providers", "roles", "fallback_rate_high", "fallback_min_calls"):
        if k not in pol:
            raise Refused("POLICY_INVALID", f"missing {k}")
    return pol


def _matches(entry: dict, row: dict) -> bool:
    if entry.get("provider") != row["provider"]:
        return False
    model = row["model_effective"] or row["model_requested"] or ""
    rx = entry.get("model_pattern")
    if rx and not re.fullmatch(rx, model) and not re.fullmatch(rx, row["model_requested"] or ""):
        return False
    if "effort" in entry and row["effort_effective"] not in (entry["effort"], None):
        return False
    return True


def view(records: list[dict], pol: dict, declared: dict | None, today: dt.date) -> dict:
    advisories = []
    roles = pol["roles"]
    by_role: dict[str, list[dict]] = {}
    tokens: dict[str, int] = {}
    for r in records:
        by_role.setdefault(r["role"] or "default", []).append(r)
        tokens[r["provider"]] = tokens.get(r["provider"], 0) + sum(
            r["measurement"][m]["sum"] for m in ("input_tokens", "reasoning_tokens", "output_tokens"))
    for role in sorted(by_role):
        rows = by_role[role]
        rp = roles.get(role) or roles.get("default") or {}
        allowed = rp.get("allowed", [])
        calls = sum(r["calls"] for r in rows)
        for r in rows:
            if allowed and not any(_matches(a, r) for a in allowed):
                advisories.append({"code": "OFF_OWNER_POSTURE", "role": role, "provider": r["provider"],
                                   "model": r["model_effective"] or r["model_requested"],
                                   "effort": r["effort_effective"], "calls": r["calls"]})
        for cap in rp.get("max_share", []):
            n = sum(r["calls"] for r in rows if _matches(cap, r))
            if calls and n / calls > cap["share"]:
                advisories.append({"code": "OFF_OWNER_POSTURE", "role": role, "model_pattern": cap["model_pattern"],
                                   "share": round(n / calls, 3), "max_share": cap["share"]})
        fb = sum(r["fallback_count"] for r in rows)
        if calls >= pol["fallback_min_calls"] and fb / calls > pol["fallback_rate_high"]:
            advisories.append({"code": "FALLBACK_RATE_HIGH", "role": role, "rate": round(fb / calls, 3),
                               "threshold": pol["fallback_rate_high"], "calls": calls})
        want = ((declared or {}).get("roles") or {}).get(role)
        if want:
            top = max(rows, key=lambda r: (r["calls"], r["model_effective"] or ""))
            got = top["model_effective"] or top["model_requested"]
            if got != want.get("model") or (want.get("effort") and top["effort_effective"] not in (want["effort"], None)):
                advisories.append({"code": "DRIFT_DECLARED_VS_ACTUAL", "role": role,
                                   "declared": {"model": want.get("model"), "effort": want.get("effort")},
                                   "actual": {"model": got, "effort": top["effort_effective"], "calls": top["calls"]}})
    if dt.date.fromisoformat(pol["reassess_by"]) <= today:
        advisories.append({"code": "REASSESS_DUE", "reassess_by": pol["reassess_by"]})
    total = sum(tokens.values())
    return {"view": "model-posture", "stored": False, "records": len(records),
            "provider_token_share": {p: round(n / total, 4) for p, n in sorted(tokens.items())} if total else {},
            "advisories": advisories}


# ---------- git helpers (publish/prune act on a bus checkout) ----------

def git(repo, *args, binary=False, check=True):
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True)
    if check and p.returncode != 0:
        raise Refused("GIT_FAILED", f"git {args[0]}: {p.stderr.decode('utf-8', 'replace').strip()[:200]}")
    return p.stdout if binary else p.stdout.decode("utf-8", "replace").strip()


def head_blob(bus, rel: str) -> bytes:
    return git(bus, "show", f"HEAD:{rel}", binary=True)


def head_shards(bus, project: str) -> dict[str, str]:
    out = git(bus, "ls-tree", "--name-only", "HEAD", f"metrics/{project}/")
    names = {}
    for line in out.splitlines():
        name = line.rsplit("/", 1)[-1]
        m = SHARD_RX.match(name)
        if m:
            names[m.group(1)] = line
    return names


def plan_prune(periods: list[str], today: dt.date) -> list[tuple[str, list[str]]]:
    """[(target_period, [source periods])] in a deterministic order: all weekly->monthly first, then monthly->yearly."""
    y, w, _ = today.isocalendar()
    this_monday = dt.date.fromisocalendar(y, w, 1)
    cutoff_week = this_monday - dt.timedelta(weeks=WEEKS_BEFORE_MONTHLY)
    month_groups: dict[str, list[str]] = {}
    for p in periods:
        if grain_of(p) == "week":
            month_groups.setdefault(month_of_week(p), []).append(p)
    plans = []
    for month in sorted(month_groups):
        weeks = sorted(month_groups[month])
        # the whole month rolls only once every week whose Thursday falls in it is >= 8 weeks old
        yy, mm = int(month[:4]), int(month[5:])
        last_day = dt.date(yy + mm // 12, mm % 12 + 1, 1) - dt.timedelta(days=1)
        last_thursday = last_day - dt.timedelta(days=(last_day.weekday() - 3) % 7)
        if last_thursday - dt.timedelta(days=3) <= cutoff_week:
            plans.append((month, ([month] if month in periods else []) + weeks))
    cutoff_month = (today.year * 12 + today.month - 1) - MONTHS_BEFORE_YEARLY
    year_groups: dict[str, list[str]] = {}
    months_after = {p for p in periods if grain_of(p) == "month"} | {t for t, _ in plans}
    for p in sorted(months_after):
        if int(p[:4]) * 12 + int(p[5:]) - 1 < cutoff_month:
            year_groups.setdefault(p[:4], []).append(p)
    for year in sorted(year_groups):
        plans.append((year, ([year] if year in periods else []) + sorted(year_groups[year])))
    return plans


def rollup_bytes(bus, project: str, target: str, sources: list[str], pending: dict[str, bytes]) -> bytes:
    recs, srcs = [], []
    for p in sorted(sources, key=lambda s: shard_name(s)):
        rel = f"metrics/{project}/{shard_name(p)}"
        data = pending[rel] if rel in pending else head_blob(bus, rel)
        for line in data.decode("ascii").splitlines():
            r = json.loads(line)
            validate(r)
            recs.append(r)
        srcs.append({"path": rel, "blob": blob_id(data)})
    return serialize(merge_records(recs, project, target, srcs))


def prune(bus, project: str, today: dt.date, commit: bool) -> list[dict]:
    periods = list(head_shards(bus, project))
    plans = plan_prune(periods, today)
    done = []
    pending: dict[str, bytes] = {}
    for target, sources in plans:
        rel_t = f"metrics/{project}/{shard_name(target)}"
        data = rollup_bytes(bus, project, target, sources, pending)
        if rollup_bytes(bus, project, target, sources, pending) != data:   # determinism, before anything is written
            raise Refused("ROLLUP_NOT_REPRODUCIBLE", rel_t)
        check_shard(data, project, target)
        rels = [f"metrics/{project}/{shard_name(s)}" for s in sources]
        deletes = sorted(r for r in rels if r != rel_t)
        row = {"target": rel_t, "sources": sorted(rels), "bytes": len(data)}
        if not commit:
            done.append({**row, "result": "PLANNED"})
            pending[rel_t] = data
            continue
        if git(bus, "diff", "--cached", "--name-only"):
            raise Refused("INDEX_NOT_CLEAN", "something is already staged; a roll-up commits only its own paths")
        replacing = {pathlib.PurePosixPath(rel_t).name: len(data), **{pathlib.PurePosixPath(d).name: 0 for d in deletes}}
        if project_total(pathlib.Path(bus) / "metrics" / project, replacing) > PROJECT_CAP:
            raise Refused("SHARD_OVER_BUDGET", f"metrics/{project}/ would exceed {PROJECT_CAP} B")
        (pathlib.Path(bus) / rel_t).write_bytes(data)
        blob = git(bus, "hash-object", "-w", "--", rel_t)
        git(bus, "update-index", "--add", "--cacheinfo", f"100644,{blob},{rel_t}")
        if deletes:
            git(bus, "rm", "-q", "--", *deletes)
        staged = sorted(git(bus, "diff", "--cached", "--name-status", "--no-renames").splitlines())
        want = sorted([f"{'M' if rel_t in rels else 'A'}\t{rel_t}"] + [f"D\t{d}" for d in deletes])
        if staged != want:
            raise Refused("ROLLUP_CENSUS_MISMATCH", ";".join(staged)[:200])
        git(bus, "commit", "-q", "-m", f"metrics({project}): roll {len(sources)} posture shard(s) into {shard_name(target)}\n\n"
            f"Generated by {TOOL_PATH} prune; recompute from the parent's sources reproduces the rollup byte for byte.")
        # Post-commit proof against the committed parent: recompute from HEAD^'s blobs, compare to HEAD's.
        again = serialize(merge_records(
            [json.loads(l) for s in sorted(sources, key=shard_name)
             for l in git(bus, "show", f"HEAD^:metrics/{project}/{shard_name(s)}", binary=True).decode("ascii").splitlines()],
            project, target,
            [{"path": f"metrics/{project}/{shard_name(s)}",
              "blob": git(bus, "rev-parse", f"HEAD^:metrics/{project}/{shard_name(s)}")} for s in sorted(sources, key=shard_name)]))
        if again != head_blob(bus, rel_t):
            raise Refused("ROLLUP_NOT_REPRODUCIBLE", f"{rel_t} at HEAD does not recompute from HEAD^")
        done.append({**row, "result": "COMMITTED", "commit": git(bus, "rev-parse", "HEAD")})
    return done


# ---------- CLI ----------

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="model-posture.py", description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("reduce", help="per-call provider-usage-event-v1 JSONL -> weekly shard on stdout")
    r.add_argument("--input", required=True, help="JSONL file, or - for stdin")
    r.add_argument("--project", required=True)
    r.add_argument("--week", required=True, help="ISO week, e.g. 2026-W43")
    v = sub.add_parser("view", help="declared vs actual vs owner posture (printed, never stored)")
    v.add_argument("shards", nargs="+")
    v.add_argument("--policy", required=True)
    v.add_argument("--declared", help="JSON {roles:{role:{model,effort}}}: the project's own declared posture")
    v.add_argument("--today", help="YYYY-MM-DD (default: UTC today)")
    p = sub.add_parser("publish", help="write a screened weekly shard into a bus checkout (does not commit)")
    p.add_argument("--bus", required=True)
    p.add_argument("--shard", required=True)
    p.add_argument("--project", required=True)
    p.add_argument("--week", required=True)
    q = sub.add_parser("prune", help="roll aged shards up; --commit makes one commit per roll-up")
    q.add_argument("--bus", required=True)
    q.add_argument("--project", required=True)
    q.add_argument("--today", help="YYYY-MM-DD (default: UTC today)")
    q.add_argument("--commit", action="store_true")
    a = ap.parse_args(argv)
    today = lambda s: dt.date.fromisoformat(s) if s else dt.datetime.now(dt.timezone.utc).date()  # noqa: E731
    try:
        if a.cmd == "reduce":
            data = serialize(reduce_events(read_events(a.input), a.project, a.week))
            check_shard(data, a.project, a.week)
            note = budget_note(data, a.week)
            if note:
                print(note, file=sys.stderr)
            out = getattr(sys.stdout, "buffer", None)   # bytes, so a Windows console never rewrites LF to CRLF
            out.write(data) if out else sys.stdout.write(data.decode("ascii"))
        elif a.cmd == "view":
            pol = load_policy(a.policy)
            declared = json.loads(pathlib.Path(a.declared).read_text(encoding="utf-8")) if a.declared else None
            print(json.dumps(view(read_records(a.shards), pol, declared, today(a.today)), indent=2, sort_keys=True))
        elif a.cmd == "publish":
            data = pathlib.Path(a.shard).read_bytes().replace(b"\r\n", b"\n")
            if not data:
                raise Refused("SHARD_EMPTY", "a week with no calls publishes nothing")
            check_shard(data, a.project, a.week)
            rel = f"metrics/{a.project}/{shard_name(a.week)}"
            dest = pathlib.Path(a.bus) / rel
            if dest.exists() and dest.read_bytes().replace(b"\r\n", b"\n") != data:
                raise Refused("SHARD_EXISTS", f"{rel} exists with different bytes; a published week is never rewritten")
            if project_total(dest.parent, {dest.name: len(data)}) > PROJECT_CAP:
                raise Refused("SHARD_OVER_BUDGET", f"metrics/{a.project}/ would exceed {PROJECT_CAP} B")
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            print(json.dumps({"result": "WRITTEN", "path": rel, "bytes": len(data), "note": budget_note(data, a.week)}))
        elif a.cmd == "prune":
            print(json.dumps({"prune": prune(a.bus, a.project, today(a.today), a.commit)}, indent=2))
    except Refused as e:
        print(f"[model-posture] REFUSED {e.code}: {e.detail}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
