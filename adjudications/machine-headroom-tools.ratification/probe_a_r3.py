"""Probes for candidate A (machine-load). Imports A's own module and its test helpers from a temp
export of origin/machine/machine-load-20261116; builds every world it needs in a temp dir.
Usage: python -I probe_a.py <prop> <A source dir>"""
import datetime as dt, importlib.util, json, os, re, shutil, subprocess, sys, tempfile, time
from pathlib import Path

prop, src = sys.argv[1], Path(sys.argv[2])
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
ml = load("machine_load", src / "machine_load.py")
T = load("ml_tests", src / "machine_load.tests.py")
ml = T.ml
CLEAN = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
tmp = Path(tempfile.mkdtemp(prefix="merit-a-"))

def run(*a, cwd): subprocess.run(a, cwd=cwd, env=CLEAN, check=True, capture_output=True)
def fake_bus():
    base = Path(tempfile.mkdtemp(dir=tmp)); origin, bus = base / "origin.git", base / "bus"
    run("git", "init", "-q", "--bare", "-b", "master", str(origin), cwd=tmp)
    run("git", "clone", "-q", str(origin), str(bus), cwd=tmp)
    run("git", "config", "user.email", "t@t", cwd=bus); run("git", "config", "user.name", "t", cwd=bus)
    (bus / "README.md").write_text("x"); run("git", "add", ".", cwd=bus); run("git", "commit", "-qm", "i", cwd=bus); run("git", "push", "-q", "origin", "HEAD:master", cwd=bus)
    return bus
def put_rows(bus, machine, rows):
    p = bus / ml.BUS_DIR / machine / "days-x.jsonl"; p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a") as fh: fh.write("\n".join(json.dumps(r) for r in rows) + "\n")
    run("git", "add", ".", cwd=bus); run("git", "commit", "-qm", machine, cwd=bus); run("git", "push", "-q", "origin", "HEAD:master", cwd=bus)
def headroom(bus, expect=()):
    old = os.environ.copy(); os.environ.clear(); os.environ.update(CLEAN)
    try: return {r["machine"]: r for r in ml.headroom(bus, 7, list(expect), live=False)}
    finally: os.environ.clear(); os.environ.update(old)
yday = ml.utc_now().date() - dt.timedelta(days=1)

try:
    if prop == "failclosed":
        bus = fake_bus(); data = tmp / "d"
        T.write_day(data, yday, T.full_day(yday, machine="PARTIAL")[:600])          # 10 h of a perfect quiet day
        put_rows(bus, "PARTIAL", [ml.rollup(data, yday, allow={"airmypc"})])
        recs = headroom(bus, expect=["ABSENTBOX", "PARTIAL"])   # RATIFIER FIX: A's --expect names the fleet (default PC-MINI1..3, machine_load.py:941); an unexpected machine is omitted by design
        print(f"VERDICT partial-10h={recs['PARTIAL'].get('verdict')} absent={recs['ABSENTBOX'].get('verdict', 'none')} states={recs['PARTIAL']['states']}")
    elif prop == "timeverdict":
        bus = fake_bus(); data = tmp / "d"
        T.write_day(data, yday, T.full_day(yday, machine="FRESH")[:720])           # a fresh install: 12 h of perfect data
        put_rows(bus, "FRESH", [ml.rollup(data, yday, allow={"airmypc"})])
        print(f"VERDICT_AFTER_12H={headroom(bus)['FRESH'].get('verdict')}")
    elif prop in ("thru", "gate"):
        out = {}
        for case in (("flat", "slow") if prop == "thru" else ("gate",)):
            bus = fake_bus(); data = tmp / f"d-{case}"
            rows = []
            for i in range(1440):
                ts = f"{yday.isoformat()}T{i // 60:02d}:{i % 60:02d}:00Z"
                if prop == "thru":
                    # RATIFIER FIX: visit every band (2/6/10 busy threads) so no band between is unmeasured (A refuses to
                    # claim an onset above a never-measured band since d5f8c347); the clock falls only in the 8-12 band.
                    busy = (2.0, 6.0, 10.0)[i % 3]
                    t = busy / 32 * 100
                    util = t * 1.8 if (case == "flat" or busy < 8) else t * 1.0   # slow: the clock falls to 55 % when busy
                else:
                    busy = (2.0, 6.0)[i % 2]; util = busy / 32 * 100 * 1.8   # RATIFIER FIX: idle CPU over two contiguous measured bands, flat clock, so CPU alone reads ROOM
                rows.append(T.minute(ts, busy=busy, util=util, machine=case.upper(), up=i))
            T.write_day(data, yday, rows)
            if prop == "gate":   # the HeavySlot gate held 70 % of the day, every ticket waited 20 min
                led = tmp / "ledger.jsonl"; lines = []
                start = dt.datetime.combine(yday, dt.time(0, 30), tzinfo=dt.timezone.utc)
                for k in range(24):
                    a = start + dt.timedelta(minutes=60 * k); e = a + dt.timedelta(minutes=42)
                    lines.append({"at": a.strftime("%Y-%m-%dT%H:%M:%S.0000000Z"), "event": "admit", "ticket": f"t{k}", "label": "airmypc:gate:x", "class": "exclusive", "waitedMs": 1200000})
                    lines.append({"at": e.strftime("%Y-%m-%dT%H:%M:%S.0000000Z"), "event": "exit", "ticket": f"t{k}", "label": "airmypc:gate:x", "source": "child", "code": 0})
                led.write_text("\n".join(json.dumps(x) for x in lines) + "\n"); ml.HEAVYSLOT_LEDGER = led
            put_rows(bus, case.upper(), [ml.rollup(data, yday, allow={"airmypc"})])
            out[case] = headroom(bus)[case.upper()]
        if prop == "thru":
            print(f"VERDICT_FLAT={out['flat'].get('verdict')} VERDICT_SLOW={out['slow'].get('verdict')} safe_slow={out['slow'].get('safe_threads')} basis_slow={out['slow'].get('safe_basis')}")
        else:
            r = out["gate"]
            flag = [k for k in r if re.search(r"slot|gate|contention|queue", k, re.I) and re.search(r"TIGHT|FULL|BOUND", json.dumps(r[k]), re.I)]
            print(f"VERDICT={r.get('verdict')} GATE_FLAG={'yes:' + ','.join(flag) if flag else 'none'} heavy_jobs_reported={bool(r.get('heavy_jobs'))}")
    elif prop == "privacy":
        today = ml.utc_now().date()
        row = ml.rollup(ml.DATA_DIR, today, ml.load_projects()) if ml.DATA_DIR.is_dir() else None
        if not row: print("PRECONDITION-MISSING no local minute rows today"); sys.exit(3)
        s = json.dumps(row)
        leaks = re.findall(r"[A-Za-z]:\\\\|\\\\Users\\\\|" + re.escape(os.environ.get("USERNAME", "zz-none")) + r"|\.exe|\.ps1|-File", s, re.I)
        print(f"RECORD_BYTES={len(s)} LEAKS={len(leaks)} {sorted(set(leaks))[:5]}")
    elif prop == "lockreader":   # argv[3] = ledger path: read it in a loop for 10 s, as the publisher does
        ml.HEAVYSLOT_LEDGER = Path(sys.argv[3]); n = 0; t0 = time.time()
        while time.time() - t0 < 10: ml.heavy_jobs(ml.utc_now().date(), {}, set()); n += 1
        print(f"ITER {n}")
finally:
    shutil.rmtree(tmp, ignore_errors=True)
