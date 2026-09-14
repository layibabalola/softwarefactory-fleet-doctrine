#!/usr/bin/env python3
"""Factory-kernel conformance PROBE (proposed to the steward of specs/fleet-factory-kernel.md r1). Zero authority.

NOT DOCTRINE. Built as a parallel kernel draft (DRAFT-universal-factory-kernel.md beside this file) before r1 was
found on master; the owner ruled r1 is the kernel (2026-09-14). Its invariant ids K1-K11 are the DRAFT's, not r1's:
README.md maps each onto r1's clauses. Use `check --json` to attach machine-measured evidence to a PROMPT-K filing.

Checks a project against the draft's invariants (DRAFT-universal-factory-kernel.md) without replacing
the project's own machinery: an adapter manifest maps the project's native ledger, integration ref,
path classes and owner gates onto the kernel contract, and this tool measures what it can and says
UNKNOWN for the rest.

  kernel.py check    --manifest M [--window-days 14] [--json]
  kernel.py feedback --manifest M --doctrine D [--notes FILE] [--window-days 14]
                       -> D/feedback/factory-kernel/<project>/<UTC-timestamp>-<ref-head12>.json (single writer: that project)
  kernel.py harvest  --doctrine D [--out FILE]
                       -> invariant rates, coverage, demotions, promotion checklist (derived; never committed)

Every result is PASS | FAIL | WARN | UNKNOWN | N/A with the evidence that produced it. UNKNOWN is never
rounded to PASS: a kernel that cannot measure an invariant on a project has learned something about
the adapter, and the feedback record carries that forward.
"""
import argparse, datetime, hashlib, json, pathlib, re, subprocess, sys

KERNEL_VERSION = "0"
INVARIANTS = {
    "K1": "Integration ref is declared per project, resolves, and every adopted commit identity is reachable from it",
    "K2": "Checkout identity (locks, journals, leases) is one shared identity per substrate (git: the common dir)",
    "K3": "Admission is bounded by eligible work: zero eligible units admits zero executors",
    "K4": "Work originates from a recorded owner authority; nothing manufactures its own backlog",
    "K5": "Adoption cites execution evidence: a receipt binding command, exit status, candidate identity and a non-author verifier",
    "K6": "Adoption and delivery are separate counters; delivery is counted only with delivery evidence",
    "K7": "The governance-to-product ratio is measured over a window; all-governance motion raises the fixpoint alarm",
    "K8": "Doctrine honesty floor: a fresh doctrine sync receipt exists (R1-R9 bind reviews)",
    "K9": "Owner-reserved actions are enumerated",
    "K10": "Blocked work is visible: every blocked unit has a reason, and an owner channel exists",
    "K11": "A liveness floor is measured: a declared scheduler is enabled, or recent owner-interaction evidence exists",
}
STATES = ("PROPOSED", "ELIGIBLE", "CLAIMED", "CANDIDATE", "VERIFIED", "ADOPTED", "DELIVERED",
          "BLOCKED_OWNER", "BLOCKED_EXTERNAL", "BLOCKED_CAPACITY", "REJECTED")
DOMAIN_CLASSES = ("code", "firmware", "media-render", "game-engine", "mobile", "prose-creative", "strategy", "prose-strategy")
GOVERNANCE_ALARM = 0.9          # default; an adapter may declare paths.alarm_ratio
RECEIPT_MAX_AGE_H = 24 * 7      # K8 freshness
LIVENESS_DAYS = 14              # K11 owner-interaction evidence freshness
DEFAULT_WINDOW_DAYS = 14        # K7 window
PASSING_STATUS = {"0", "pass", "passed", "ok", "success"}
HEXSHA = re.compile(r"^[0-9a-f]{7,40}$")


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, encoding="utf-8", errors="replace")


def result(status, evidence, **data):
    return {"status": status, "evidence": evidence, **data}


def glob_to_regex(g):
    out, i = "", 0
    while i < len(g):
        if g.startswith("**/", i):
            out += "(?:.*/)?"; i += 3
        elif g.startswith("**", i):
            out += ".*"; i += 2
        elif g[i] == "*":
            out += "[^/]*"; i += 1
        else:
            out += re.escape(g[i]); i += 1
    return re.compile(out + r"\Z")


def classify(path, globs):
    return any(r.match(path) for r in globs)


def parse_utc(s):
    try:
        return datetime.datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except Exception:
        return None


# ---------------------------------------------------------------- native ledgers -> kernel units
UNIT_FIELDS = ("id", "state", "commit", "evidence", "reason", "author", "verifier", "delivery_evidence")


def load_units(m, repo):
    """-> ({"units": [...], "meta": {...}}, note) or (None, note). A unit has UNIT_FIELDS (state already mapped)."""
    led = m.get("ledger") or {"kind": "none"}
    kind = led.get("kind", "none")
    if kind == "none":
        return None, "manifest declares no native ledger"
    if kind == "json-tasks":
        p = repo / led["path"]
        if not p.exists():
            return None, f"ledger file missing: {led['path']}"
        doc = json.loads(p.read_text(encoding="utf-8"))
        rows = doc
        for k in (led.get("list") or "").split(".") if led.get("list") else []:
            rows = rows[k]
        smap = {k.lower(): v for k, v in led.get("state_map", {}).items()}
        field = lambda r, key, default=None: r.get(led[key]) if led.get(key) else default
        units = []
        for r in rows:
            native = str(r.get(led.get("status", "status"), "")).lower()
            ev = field(r, "evidence") or []
            units.append({"id": str(r.get(led.get("id", "id"))), "native_state": native, "state": smap.get(native, "UNMAPPED"),
                          "commit": field(r, "commit"), "evidence": ev if isinstance(ev, list) else [ev],
                          "reason": field(r, "reason"), "author": field(r, "author"), "verifier": field(r, "verifier"),
                          "delivery_evidence": field(r, "delivery_evidence")})
        meta = {"authority": doc.get(led["authority"]) if led.get("authority") and isinstance(doc, dict) else None,
                "updated": doc.get(led["updated"]) if led.get("updated") and isinstance(doc, dict) else None}
        return {"units": units, "meta": meta}, f"json-tasks {led['path']} ({len(units)} units)"
    if kind == "command":
        # Contract (spec §5): stdout is {"units": [{id, state (a kernel STATE), commit?, evidence[], reason?, author?,
        # verifier?, delivery_evidence?}], "meta": {authority?, updated?}}; non-zero exit or bad JSON is UNKNOWN.
        try:
            p = subprocess.run(led["argv"], cwd=repo, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
            if p.returncode:
                return None, f"ledger command failed rc={p.returncode}: {p.stderr.strip()[:200]}"
            doc = json.loads(p.stdout)
            units = [dict({f: None for f in UNIT_FIELDS}, native_state=u.get("state"), **u) for u in doc["units"]]
            for u in units:
                if u["state"] not in STATES:
                    u["state"] = "UNMAPPED"
                u["evidence"] = u["evidence"] or []
            return {"units": units, "meta": doc.get("meta", {})}, f"command {' '.join(led['argv'])} ({len(units)} units)"
        except Exception as e:
            return None, f"ledger command unusable: {e}"
    return None, f"unsupported ledger kind {kind!r}"


# ---------------------------------------------------------------- evidence helpers
def evidence_files(repo, ref, path):
    """Files under an evidence path, from the integration ref first, else the working tree."""
    path = str(path).rstrip("/")
    listed = git(repo, "ls-tree", "-r", "--name-only", ref, "--", path).stdout.splitlines() if ref else []   # paths may contain spaces
    if listed:
        return [("ref", f) for f in listed]
    p = repo / path
    if p.is_file():
        return [("tree", path)]
    if p.is_dir():
        return [("tree", str(q.relative_to(repo)).replace("\\", "/")) for q in p.rglob("*") if q.is_file()]
    return []


def read_file(repo, ref, where, f):
    if where == "ref":
        return git(repo, "show", f"{ref}:{f}").stdout
    try:
        return (repo / f).read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def same_identity(a, b):
    a, b = str(a or "").strip().lower(), str(b or "").strip().lower()
    return bool(a) and bool(b) and (a == b or (HEXSHA.match(a) and HEXSHA.match(b) and (a.startswith(b) or b.startswith(a))))


# ---------------------------------------------------------------- invariants
def check(m, window_days=DEFAULT_WINDOW_DAYS):
    repo = pathlib.Path(m["repo"])
    ref = m.get("integration_ref")
    substrate = (m.get("checkout") or {}).get("substrate", "git")
    res, metrics = {}, {}
    led, led_note = load_units(m, repo)
    units = led["units"] if led else []
    count = lambda *s: sum(1 for u in units if u["state"] in s)
    ref_ok = bool(ref) and git(repo, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}").returncode == 0

    # K1 -- never assume master; never PASS on zero readable units
    if not ref:
        res["K1"] = result("FAIL", "manifest declares no integration_ref (a kernel must never assume master)")
    elif not ref_ok:
        res["K1"] = result("FAIL", f"integration_ref {ref!r} does not resolve in {repo}")
    elif not led:
        res["K1"] = result("UNKNOWN", f"{ref} resolves, but no adopted units are readable ({led_note})")
    else:
        adopted = [u for u in units if u["state"] in ("ADOPTED", "DELIVERED")]
        commits = [u for u in adopted if u.get("commit") and HEXSHA.match(str(u["commit"]).lower())]
        other = [u["id"] for u in adopted if u not in commits]
        unreachable = [u["id"] for u in commits if git(repo, "merge-base", "--is-ancestor", u["commit"], ref).returncode != 0]
        default = next((b for b in ("master", "main") if not git(repo, "rev-parse", "--verify", "--quiet", b).returncode), None)
        ahead = git(repo, "rev-list", "--count", f"{default}..{ref}").stdout.strip() if default and default != ref else None
        ev = (f"{ref} resolves; {len(commits)} adopted commit identities checked, {len(unreachable)} unreachable; "
              f"{len(other)} adopted units with non-commit identity (bound by K5 receipts)" + (f"; {ref} is {ahead} ahead of {default}" if ahead else ""))
        status = "FAIL" if unreachable else ("PASS" if commits else ("N/A" if not adopted else "UNKNOWN"))
        res["K1"] = result(status, ev, unreachable=unreachable, non_commit=other)

    # K2 -- one shared identity per substrate
    declared = (m.get("checkout") or {}).get("lock_identity")
    if substrate != "git":
        res["K2"] = result("PASS" if declared else "UNKNOWN", f"substrate={substrate}; declared identity={declared!r} (git checks not applicable)")
    else:
        common = git(repo, "rev-parse", "--path-format=absolute", "--git-common-dir").stdout.strip()
        wts = [l for l in git(repo, "worktree", "list", "--porcelain").stdout.splitlines() if l.startswith("worktree ")]
        ev = f"git common dir {common}; {len(wts)} worktrees; lock_identity={declared!r}"
        metrics["worktrees"] = len(wts)
        if declared == "git-common-dir":
            res["K2"] = result("PASS", ev)
        elif declared == "single-writer-process":
            res["K2"] = result("PASS" if len(wts) <= 1 else "WARN", ev + " (identity is process discipline; worktrees can bypass it)")
        elif declared is None:
            res["K2"] = result("UNKNOWN" if len(wts) <= 1 else "WARN", ev + " (undeclared; a per-worktree identity splits locks)")
        else:
            res["K2"] = result("FAIL" if len(wts) > 1 else "WARN", ev + " (identity other than the common dir)")

    # K3 -- admission bounded by eligible work (declared floor, plus an observed executor count when available)
    adm = m.get("admission") or {}
    if not led:
        res["K3"] = result("UNKNOWN", f"no ledger: {led_note}")
    else:
        eligible, active = count("ELIGIBLE"), count("CLAIMED", "CANDIDATE")
        floor, observed = adm.get("configured_min_executors"), None
        if adm.get("observed_executors_argv"):
            try:
                observed = int(subprocess.run(adm["observed_executors_argv"], cwd=repo, capture_output=True, text=True, timeout=60).stdout.strip())
            except Exception:
                observed = None
        ev = f"eligible={eligible} active={active} configured_min_executors={floor} observed_executors={observed}"
        metrics.update(eligible=eligible, active=active, observed_executors=observed)
        if floor is None and observed is None:
            res["K3"] = result("UNKNOWN", ev + " (neither an admission floor nor an executor probe is declared)")
        elif (floor or 0) > 0 and eligible == 0:
            res["K3"] = result("FAIL", ev + " -> executors would be admitted with nothing eligible")
        elif observed is not None and observed > eligible + active:
            res["K3"] = result("FAIL", ev + " -> more executors observed than eligible or active units")
        else:
            res["K3"] = result("PASS" if observed is not None else "WARN" if active else "PASS", ev +
                               ("" if observed is not None else " (declared floor only; no executor probe)"))

    # K4 -- recorded owner authority (recorded, not authenticated, in shadow mode)
    if not led:
        res["K4"] = result("UNKNOWN", f"no ledger: {led_note}")
    else:
        auth = (led.get("meta") or {}).get("authority")
        exists = bool(auth) and (repo / str(auth)).exists()
        res["K4"] = result("PASS" if exists else ("WARN" if auth else "UNKNOWN"),
                           f"ledger authority={auth!r} exists_in_repo={exists} (recorded, not authenticated)")

    # K5 -- execution evidence: receipts, exit status, identity, non-author verifier
    if not led:
        res["K5"] = result("UNKNOWN", f"no ledger: {led_note}")
    else:
        status_rx = glob_to_regex((m.get("ledger") or {}).get("evidence_status_glob", "**/*.status"))
        adopted = [u for u in units if u["state"] in ("ADOPTED", "DELIVERED")]
        no_ev, missing, self_verified, failing_status, bad_receipts, receipted = [], [], [], [], [], []
        for u in adopted:
            paths = [e for e in u["evidence"] if e]
            if not paths:
                no_ev.append(u["id"]); continue
            if same_identity(u.get("author"), u.get("verifier")):
                self_verified.append(u["id"])
            good = False
            for e in paths:
                files = evidence_files(repo, ref if ref_ok else None, e)
                if not files:
                    missing.append(f"{u['id']}:{e}"); continue
                for where, f in files:
                    if f.endswith(".receipt.json"):
                        try:
                            rc = json.loads(read_file(repo, ref, where, f))
                            ok = (str(rc.get("exit_status")) == "0" and rc.get("command")
                                  and (not u.get("commit") or same_identity(rc.get("candidate_identity"), u["commit"]))
                                  and rc.get("verifier") and not same_identity(rc.get("verifier"), rc.get("author") or u.get("author")))
                            (receipted if ok else bad_receipts).append(f"{u['id']}:{f}")
                            good = good or bool(ok)
                        except Exception:
                            bad_receipts.append(f"{u['id']}:{f}:unparseable")
                    elif status_rx.match(f):
                        val = read_file(repo, ref, where, f).strip().lower()
                        if val and val not in PASSING_STATUS:
                            failing_status.append(f"{u['id']}:{f}={val[:12]}")
            u["_receipted"] = good
        unreceipted = [u["id"] for u in adopted if u["evidence"] and not u.get("_receipted")]
        metrics.update(k5_receipted=len(adopted) - len(unreceipted) - len(no_ev), k5_failing_status_files=len(failing_status))
        ev = (f"{len(adopted)} adopted: {len(no_ev)} cite no evidence, {len(missing)} evidence paths absent, "
              f"{len(unreceipted)} without a passing receipt, {len(failing_status)} failing status files, "
              f"{len(self_verified)} verified by their author, {len(bad_receipts)} failing/invalid receipts")
        if not adopted:
            res["K5"] = result("N/A", ev)
        elif no_ev or missing or self_verified:
            res["K5"] = result("FAIL", ev)
        elif unreceipted or failing_status or bad_receipts:
            res["K5"] = result("WARN", ev + " -> evidence exists but does not prove a passing execution")
        else:
            res["K5"] = result("PASS", ev)
        res["K5"].update(no_evidence=no_ev, missing=missing[:20], self_verified=self_verified, unreceipted=unreceipted[:20],
                         failing_status=failing_status[:20], bad_receipts=bad_receipts[:20])

    # K6 -- delivery counted only with delivery evidence
    rule = (m.get("ledger") or {}).get("delivery")
    if not led:
        res["K6"] = result("UNKNOWN", f"no ledger: {led_note}")
    elif not rule:
        res["K6"] = result("FAIL", f"no delivery rule; adopted={count('ADOPTED', 'DELIVERED')} would be the only counter")
    else:
        rx = re.compile(rule["id_regex"]) if rule.get("id_regex") else None
        in_class = [u for u in units if u["state"] == "DELIVERED" or (rx and rx.search(u["id"]))]
        reached = [u for u in in_class if u["state"] == "DELIVERED" or u["state"] == rule.get("when_state", "ADOPTED")]
        with_ev = [u["id"] for u in reached if u.get("delivery_evidence")]
        without_ev = [u["id"] for u in reached if not u.get("delivery_evidence")]
        pending = [u["id"] for u in in_class if u not in reached]
        adopted_n = count("ADOPTED", "DELIVERED")
        metrics.update(adopted=adopted_n, delivered=len(with_ev), delivery_pending=pending, delivery_without_evidence=without_ev)
        ev = (f"adopted={adopted_n} delivered={len(with_ev)} pending={pending} claimed-without-delivery-evidence={without_ev} "
              f"(rule: {rule.get('describe', rule)}; evidence field declared={bool((m.get('ledger') or {}).get('delivery_evidence'))})")
        if without_ev:
            res["K6"] = result("FAIL", ev + " -> delivery counted without delivery evidence")
        elif not (m.get("ledger") or {}).get("delivery_evidence"):
            res["K6"] = result("WARN", ev + " -> no delivery_evidence field mapped; a future delivery could not be proven")
        else:
            res["K6"] = result("PASS", ev)

    # K7 -- governance ratio (commit-level and file-level)
    paths = m.get("paths") or {}
    gov = [glob_to_regex(g) for g in paths.get("governance", [])]
    prod = [glob_to_regex(g) for g in paths.get("product", [])]
    alarm = float(paths.get("alarm_ratio", GOVERNANCE_ALARM))
    if substrate != "git":
        res["K7"] = result("UNKNOWN", f"substrate={substrate}: commit classification needs a substrate adapter")
    elif not ref_ok or not gov or not prod:
        res["K7"] = result("UNKNOWN", "a resolving integration_ref, governance globs and product globs are all required")
    else:
        since = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=window_days)).strftime("%Y-%m-%d")
        log = git(repo, "log", f"--since={since}", "--no-merges", "--name-only", "--format=@@%H", ref).stdout
        commits, cur = [], None
        for line in log.splitlines():
            if line.startswith("@@"):
                cur = []; commits.append(cur)
            elif line.strip() and cur is not None:
                cur.append(line.strip())
        g = p_ = o = gf = pf = 0
        for files in commits:
            gf += sum(1 for f in files if classify(f, gov) and not classify(f, prod))
            pf += sum(1 for f in files if classify(f, prod))
            if any(classify(f, prod) for f in files):
                p_ += 1
            elif files and all(classify(f, gov) for f in files):
                g += 1
            else:
                o += 1
        ratio = round(g / (g + p_), 3) if (g + p_) else None
        file_ratio = round(gf / (gf + pf), 3) if (gf + pf) else None
        metrics.update(window_days=window_days, commits=len(commits), governance_commits=g, product_commits=p_, other_commits=o,
                       governance_ratio=ratio, governance_file_ratio=file_ratio)
        ev = (f"{len(commits)} commits on {ref} in {window_days}d: governance={g} product={p_} other={o} ratio={ratio} "
              f"file-ratio={file_ratio} alarm>={alarm}; eligible={metrics.get('eligible')}")
        if not commits:
            res["K7"] = result("WARN", ev + " (no motion at all in the window)")
        elif (ratio is not None and ratio >= alarm) or (p_ == 0 and g > 0):
            res["K7"] = result("WARN", ev + " -> CONFORMANCE-FIXPOINT ALARM")
        else:
            res["K7"] = result("PASS", ev)

    # K8 -- doctrine receipt freshness
    if m.get("doctrine_receipt") is False:
        res["K8"] = result("N/A", "manifest declares this project is the doctrine bus itself")
    else:
        rc = repo / (m.get("doctrine_receipt") or ".claude/doctrine-sync.json")
        if not rc.exists():
            res["K8"] = result("FAIL", f"no doctrine sync receipt at {rc}")
        else:
            d = json.loads(rc.read_text(encoding="utf-8"))
            at = parse_utc(d.get("synced_at"))
            age_h = (datetime.datetime.now(datetime.timezone.utc) - at).total_seconds() / 3600 if at else None
            ok = d.get("status") == "SYNCED" and age_h is not None and age_h <= RECEIPT_MAX_AGE_H
            res["K8"] = result("PASS" if ok else "WARN", f"receipt status={d.get('status')} age_h={None if age_h is None else round(age_h, 1)} max={RECEIPT_MAX_AGE_H}")

    # K9 -- owner-reserved actions enumerated
    owner = m.get("owner_reserved") or []
    res["K9"] = result("PASS" if owner else "FAIL", f"{len(owner)} owner-reserved actions declared: {owner} (declared, not authenticated)")

    # K10 -- blocked visibility; an owner channel is required whether or not anything is blocked today
    chan = m.get("owner_channel")
    chan_ok = bool(chan) and (repo / chan).exists()
    if not led:
        res["K10"] = result("UNKNOWN" if chan_ok else "FAIL", f"no ledger ({led_note}); owner_channel={chan!r} exists={chan_ok}")
    else:
        blocked = [u for u in units if u["state"].startswith("BLOCKED")]
        no_reason = [u["id"] for u in blocked if not u.get("reason")]
        metrics.update(blocked=len(blocked), ledger_updated=(led.get("meta") or {}).get("updated"))
        ev = f"{len(blocked)} blocked; {len(no_reason)} without a reason; owner_channel={chan!r} exists={chan_ok}"
        res["K10"] = result("PASS" if (not no_reason and chan_ok) else "FAIL", ev, no_reason=no_reason)

    # K11 -- liveness floor: any declared probe live, or recent owner-interaction evidence
    live = m.get("liveness") or {}
    probes = live.get("probes") or ([{"argv": live["probe"], "ok": live.get("ok", [])}] if live.get("probe") else [])
    seen = []
    for pr in probes:
        try:
            out = subprocess.run(pr["argv"], capture_output=True, text=True, timeout=60).stdout.strip()
            seen.append((out, out in pr.get("ok", [])))
        except Exception as e:
            seen.append((f"probe error: {e}", False))
    evp = live.get("evidence_path")
    last = git(repo, "log", "-1", "--format=%cI", ref, "--", evp).stdout.strip() if (evp and ref_ok) else ""
    last_at = parse_utc(last) if last else None
    fresh = bool(last_at) and (datetime.datetime.now(datetime.timezone.utc) - last_at).days <= LIVENESS_DAYS
    ev = f"probes={[s for s, _ in seen]} owner-interaction evidence {evp!r} last={last or None} (fresh<= {LIVENESS_DAYS}d: {fresh})"
    if any(ok for _, ok in seen):
        res["K11"] = result("PASS", ev)
    elif live.get("mode") == "owner-interactive":
        res["K11"] = result("PASS" if fresh else "WARN", ev + ("" if fresh else " -> owner-interactive declared without recent evidence"))
    elif probes:
        res["K11"] = result("FAIL", ev + " -> no declared floor is live")
    else:
        res["K11"] = result("UNKNOWN", "manifest declares neither a scheduler probe nor owner-interactive mode")

    unmapped = sorted({str(u.get("native_state")) for u in units if u["state"] == "UNMAPPED"})
    for u in units:
        u.pop("_receipted", None)
    tally = {s: sum(1 for r in res.values() if r["status"] == s) for s in ("PASS", "FAIL", "WARN", "UNKNOWN", "N/A")}
    return {"kernel_version": KERNEL_VERSION, "project": m["project"], "domain_class": m.get("domain_class"),
            "domain_class_known": m.get("domain_class") in DOMAIN_CLASSES, "adapter": m.get("adapter"),
            "manifest_sha256": hashlib.sha256(json.dumps(m, sort_keys=True).encode()).hexdigest(),
            "measured_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
            "integration_ref": ref, "ref_head": git(repo, "rev-parse", ref).stdout.strip() if ref_ok else None,
            "ledger": led_note, "unmapped_native_states": unmapped, "invariants": res, "metrics": metrics, "tally": tally}


def render(r):
    lines = [f"factory-kernel v{r['kernel_version']} shadow check: {r['project']} ({r['domain_class']}, adapter {r['adapter']})",
             f"ref {r['integration_ref']} @ {str(r['ref_head'])[:12]}; ledger: {r['ledger']}"]
    for k in INVARIANTS:
        v = r["invariants"].get(k)
        if v:
            lines.append(f"  {k:<4} {v['status']:<8} {v['evidence']}")
    if r["unmapped_native_states"]:
        lines.append(f"  unmapped native states: {r['unmapped_native_states']}")
    lines.append("  tally: " + " ".join(f"{k}={v}" for k, v in r["tally"].items()))
    return "\n".join(lines)


# ---------------------------------------------------------------- feedback + harvest
def feedback(m, doctrine, notes, window_days):
    r = check(m, window_days)
    r["notes"] = pathlib.Path(notes).read_text(encoding="utf-8") if notes else ""
    r["manifest"] = m
    stamp = r["measured_at"].replace(":", "").replace("+0000", "Z")
    out = pathlib.Path(doctrine) / "feedback" / "factory-kernel" / m["project"] / f"{stamp}-{str(r['ref_head'] or 'noref')[:12]}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        raise SystemExit(f"refusing to overwrite an existing record: {out}")
    out.write_text(json.dumps(r, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out, r


PROMOTION = {"projects": 5, "domain_classes": 3, "days_span": 14, "invariant_pass_rate": 0.8, "coverage": 0.8}
DEMOTION = {"projects": 3, "days_span": 14, "pass_rate_below": 0.5}


def landed_amendments(doctrine):
    root = pathlib.Path(doctrine)
    out = []
    for p in sorted((root / "feedback" / "factory-kernel" / "proposals").glob("*.md")):
        t = p.read_text(encoding="utf-8", errors="replace")
        st = re.search(r"^status:\s*(\S+)", t, re.M | re.I)
        lc = re.search(r"^landing_commit:\s*([0-9a-f]{7,40})", t, re.M | re.I)
        if st and st.group(1).upper() == "LANDED" and lc and \
                git(root, "merge-base", "--is-ancestor", lc.group(1), "HEAD").returncode == 0:
            out.append(p.name)
    return out


def harvest(doctrine, out_file=None):
    root = pathlib.Path(doctrine) / "feedback" / "factory-kernel"
    recs = []
    for p in sorted(root.glob("*/*.json")):
        if p.name == "manifest.json" or p.parent.name == "proposals":
            continue
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
            if "invariants" in d and str(d.get("kernel_version")) == KERNEL_VERSION:
                recs.append(d)
        except Exception:
            continue
    latest = {}
    for d in recs:
        if d["project"] not in latest or d["measured_at"] > latest[d["project"]]["measured_at"]:
            latest[d["project"]] = d
    classes = sorted({str(d.get("domain_class")) for d in latest.values()})
    dates = sorted(d["measured_at"][:10] for d in recs)
    span = (datetime.date.fromisoformat(dates[-1]) - datetime.date.fromisoformat(dates[0])).days if dates else 0
    rows, rates, coverage, demote = [], {}, {}, []
    for k, text in INVARIANTS.items():
        st = {p: d["invariants"].get(k, {}).get("status", "UNKNOWN") for p, d in latest.items()}
        measured = [s for s in st.values() if s in ("PASS", "FAIL", "WARN")]
        rate = round(measured.count("PASS") / len(measured), 2) if measured else None
        rates[k] = rate
        applicable = [p for p in st if st[p] != "N/A"]           # N/A never counts against coverage
        coverage[k] = round(len(measured) / len(applicable), 2) if applicable else 1.0
        per_domain = all(any(latest[p].get("domain_class") == c and st[p] in ("PASS", "FAIL", "WARN") for p in applicable)
                         for c in classes if any(latest[p].get("domain_class") == c for p in applicable))
        if len(measured) >= DEMOTION["projects"] and span >= DEMOTION["days_span"] and rate is not None and rate < DEMOTION["pass_rate_below"]:
            demote.append(k)
        vals = list(st.values())
        rows.append(f"| {k} | {vals.count('PASS')} | {vals.count('FAIL')} | {vals.count('WARN')} | {vals.count('UNKNOWN')} | "
                    f"{vals.count('N/A')} | {rate} | {coverage[k]} | {'yes' if per_domain else 'no'} | {text} |")
        coverage[k + "_per_domain"] = per_domain
    amend = landed_amendments(doctrine)
    crit = {
        f">= {PROMOTION['projects']} projects filing": len(latest) >= PROMOTION["projects"],
        f">= {PROMOTION['domain_classes']} domain classes": len(classes) >= PROMOTION["domain_classes"],
        f">= {PROMOTION['days_span']} days of records": span >= PROMOTION["days_span"],
        f"every invariant PASS rate >= {PROMOTION['invariant_pass_rate']} where measured":
            bool(latest) and all(v is not None and v >= PROMOTION["invariant_pass_rate"] for v in rates.values()),
        f"every invariant measured on >= {PROMOTION['coverage']} of projects and on >= 1 project per domain":
            bool(latest) and all(coverage[k] >= PROMOTION["coverage"] and coverage[k + "_per_domain"] for k in INVARIANTS),
        ">= 1 amendment LANDED with a landing_commit reachable from the bus": len(amend) >= 1,
        "no invariant due for demotion": not demote,
    }
    proj = [f"| {d['project']} | {d.get('domain_class')} | {d['measured_at'][:10]} | {d['tally']} | "
            f"{d['metrics'].get('governance_ratio')} | {d['metrics'].get('adopted')} / {d['metrics'].get('delivered')} |"
            for d in sorted(latest.values(), key=lambda x: x["project"])]
    md = [f"# Factory kernel v{KERNEL_VERSION} — dogfood harvest (derived; regenerate, do not commit)", "",
          f"{len(recs)} records, {len(latest)} projects, {len(classes)} domain classes ({', '.join(classes)}), {span} days; "
          f"landed amendments: {amend or 'none'}.", "",
          "| project | domain | latest | tally | governance ratio | adopted / delivered |", "|---|---|---|---|---|---|", *proj, "",
          "| K | PASS | FAIL | WARN | UNKNOWN | N/A | pass rate | coverage | every domain | invariant |",
          "|---|---|---|---|---|---|---|---|---|---|", *rows, "",
          f"Due for demotion (§8): {demote or 'none'}", "", "## v1 promotion criteria (§9)", "",
          *[f"- [{'x' if v else ' '}] {k}" for k, v in crit.items()], "",
          f"**Promotion: {'ELIGIBLE for owner ratification' if all(crit.values()) else 'NOT YET'}.**"]
    text = "\n".join(md) + "\n"
    if out_file:
        pathlib.Path(out_file).write_text(text, encoding="utf-8")
    return text, crit


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check"); c.add_argument("--manifest", required=True); c.add_argument("--window-days", type=int, default=DEFAULT_WINDOW_DAYS); c.add_argument("--json", action="store_true")
    f = sub.add_parser("feedback"); f.add_argument("--manifest", required=True); f.add_argument("--doctrine", required=True); f.add_argument("--notes"); f.add_argument("--window-days", type=int, default=DEFAULT_WINDOW_DAYS)
    h = sub.add_parser("harvest"); h.add_argument("--doctrine", required=True); h.add_argument("--out")
    a = ap.parse_args()
    if a.cmd == "check":
        r = check(json.loads(pathlib.Path(a.manifest).read_text(encoding="utf-8")), a.window_days)
        print(json.dumps(r, indent=2) if a.json else render(r))
    elif a.cmd == "feedback":
        out, r = feedback(json.loads(pathlib.Path(a.manifest).read_text(encoding="utf-8")), a.doctrine, a.notes, a.window_days)
        print(render(r)); print(f"feedback record: {out}")
    else:
        text, crit = harvest(a.doctrine, a.out)
        print(text)


if __name__ == "__main__":
    main()
