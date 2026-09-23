#!/usr/bin/env python3
"""Keep the claude and codex CLIs on their latest release, and report new models (fleet standard
specs/fleet-cli-currency.md, owner ruling R13, 2026-09-23).

    cli-currency.py                  check only: print drift, change nothing
    cli-currency.py --apply          upgrade every drifted install, smoke-test it, roll back on failure
    cli-currency.py --json           machine-readable result on stdout
    cli-currency.py --resolve sol    print the newest Codex slug of a tier and exit

Runs every six hours from each machine's scheduler. Machine-scoped: one version per CLI per box.

Design facts this relies on, each measured rather than assumed:

1. NO "WAIT UNTIL IDLE" GATE. On Windows, `npm install -g` moves the old package directory aside
   and installs the new one while a process of the old binary is still running; the running
   process keeps its binary and npm leaves a `.codex-XXXX` trash directory it could not unlink
   (measured 2026-09-23, BACHELOR, codex 0.154.0 -> 0.156.1 under a live `codex app-server`).
   Claude's native installer renames a running `claude.exe` aside the same way. An idle gate is
   not needed, and the fleet measured what one costs: TRAPS.md "A CLI updater that waits until
   'no process of that CLI is running' never updates Claude...". Trash dirs are swept once free.

2. EVERY INSTALL ON PATH, NOT JUST THE FIRST. A stale second install behind the first is the
   wrong-shim trap (measured on BACHELOR: npm codex 0.154.0 first on PATH, winget 0.144.6 behind).

3. SMOKE IN ISOLATION, ROLL BACK ONLY ON EVIDENCE. The Claude smoke loads no user settings and no
   hooks: a user SessionStart hook on BACHELOR can open a login window and a browser on account
   drift, which an unattended probe must never do. A failure is blamed on the upgrade only when
   the previous version passes the same smoke; the rejected version is then held until npm
   `latest` moves past it, so a bad release is not reinstalled every six hours. If both versions
   fail, the new one stays and the run exits 1 for a human to look.

4. NEW MODELS ARE REPORTED, NOT ADOPTED HERE. Claude seats dispatched by alias pick up a new model
   with the CLI; Codex seats resolve their tier at launch with --resolve. Anything that pins an
   exact id is listed in the receipt's `new_models` so its owner can re-pin.

5. OUTPUT IS PARSED FROM STDOUT ONLY. npm prints warnings on stderr; merged, a warning line became
   the "npm prefix" and a trailing CLI warning broke the smoke's JSON parse (adversarial review,
   2026-09-23, reproduced in simulation before this version).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import pathlib
import platform
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time

HOME = pathlib.Path.home()
STATE = pathlib.Path(os.environ.get("CLI_CURRENCY_STATE") or HOME / ".claude" / "cli-currency")
HOLD_FILE = pathlib.Path(__file__).resolve().parent.parent / "policy" / "cli-currency-hold.json"
NO_NEW_UPGRADE_AFTER_S = 30 * 60   # worst case after this is ~60 min; the task limit is 2 h
RECEIPTS_MAX_BYTES = 5 * 1024 * 1024
WIN = os.name == "nt"
PACKAGES = {"claude": "@anthropic-ai/claude-code", "codex": "@openai/codex"}
READY = "READY"
PROMPT = f"Reply with exactly the word {READY} and nothing else."
CLAUDE_MODEL_RE = re.compile(rb"claude-(?:fable|opus|sonnet|haiku)-\d+(?:-\d+)*(?:-\d{8})?")
CLAUDE_SMOKE_ISOLATION = ["--setting-sources", "local", "--settings", '{"disableAllHooks":true}',
                          "--no-session-persistence"]
BAD = {"ROLLED-BACK", "ROLLBACK-FAILED", "UPGRADE-FAILED", "UPGRADED-SMOKE-FAILED-NO-ROLLBACK",
       "UPGRADED-ENVIRONMENT-SMOKE-FAILED", "CHECK-FAILED"}
PRIORITY = ["ROLLBACK-FAILED", "ROLLED-BACK", "UPGRADE-FAILED", "UPGRADED-SMOKE-FAILED-NO-ROLLBACK",
            "UPGRADED-ENVIRONMENT-SMOKE-FAILED", "HELD", "DRIFT-UNMANAGED", "DRIFT", "WINGET-LAGS-NPM",
            "UPGRADED", "SKIPPED-DEADLINE"]


# ---------------------------------------------------------------- pure helpers (unit-tested)

def parse_version(text: str) -> tuple[int, ...] | None:
    m = re.search(r"(\d+)\.(\d+)\.(\d+)", text or "")
    return tuple(int(x) for x in m.groups()) if m else None


def vstr(v: tuple[int, ...] | None) -> str | None:
    return ".".join(map(str, v)) if v else None


def classify(path: str, npm_prefix: str | None) -> str:
    """Which mechanism owns this executable: npm, native (Claude's own installer), winget, other."""
    p = os.path.normcase(os.path.abspath(path))
    if npm_prefix and p.startswith(os.path.normcase(os.path.abspath(npm_prefix)) + os.sep):
        # On POSIX a Homebrew prefix can equal npm's; only a link into node_modules is npm's.
        if WIN or "node_modules" in os.path.realpath(path).split(os.sep):
            return "npm"
    local = os.path.normcase(str(HOME / ".local"))
    if p.startswith(local + os.sep) and os.path.basename(p).startswith("claude"):
        return "native"
    if os.sep + "winget" + os.sep in p.lower():
        return "winget"
    return "other"


def rollup(statuses: set[str]) -> str:
    return next((s for s in PRIORITY if s in statuses), "CURRENT")


def diff_models(before: list[str], after: list[str]) -> list[str]:
    seen = set(before)
    return [m for m in after if m not in seen]


def claude_models_in(blob: bytes) -> list[str]:
    """Model ids a Claude Code binary names. A heuristic, used only to notice NEW ids."""
    return sorted({m.decode() for m in CLAUDE_MODEL_RE.findall(blob)})


def resolve_tier(slugs: list[str], tier: str) -> str | None:
    """Newest Codex slug of a tier (`sol`, `luna`, `astra`, `terra`): the highest version number among
    `gpt-<version>-<tier>` slugs. Codex has no floating alias, so a lane that pins `gpt-5.6-sol`
    never folds in `gpt-6-sol`; resolving the tier at launch does."""
    best = None
    for s in slugs:
        m = re.fullmatch(r"gpt-(\d+(?:\.\d+)*)-" + re.escape(tier), s)
        if m:
            v = tuple(int(x) for x in m.group(1).split("."))
            if best is None or v > best[0]:
                best = (v, s)
    return best[1] if best else None


def codex_smoke_model(slugs: list[str]) -> str | None:
    """The cheapest current Codex tier, resolved (see resolve_tier)."""
    return resolve_tier(slugs, "luna")


def claude_smoke_ok(rc: int, stdout: str) -> tuple[bool, str | None]:
    """Parse the first JSON object on stdout; tolerate anything printed after it."""
    i = stdout.find("{")
    if rc != 0 or i < 0:
        return False, None
    try:
        d, _ = json.JSONDecoder().raw_decode(stdout[i:])
    except ValueError:
        return False, None
    ok = str(d.get("result", "")).strip() == READY and not d.get("is_error")
    return ok, next(iter(d.get("modelUsage") or {}), None)


def held(cli: str, version: str, state: dict, hold: dict) -> str | None:
    """Why `version` must not be installed: rejected by this machine's smoke, or held fleet-wide."""
    if (state.get("rejected") or {}).get(cli) == version:
        return "rejected by this machine's smoke"
    if version in (hold.get(cli) or []):
        return "held fleet-wide (policy/cli-currency-hold.json)"
    return None


def path_dirs(path_env: str) -> list[str]:
    out, seen = [], set()
    for d in path_env.split(os.pathsep):
        d = d.strip().strip('"').rstrip("\\/")
        if d and os.path.normcase(d) not in seen:
            seen.add(os.path.normcase(d))
            out.append(d)
    return out


# ---------------------------------------------------------------- process helpers

def _kill_tree(p: subprocess.Popen) -> None:
    """Kill the child WE started and its descendants, by our own child's pid. Never by name."""
    try:
        if WIN:
            subprocess.run(["taskkill", "/T", "/F", "/PID", str(p.pid)], capture_output=True,
                           timeout=30, creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            os.killpg(p.pid, signal.SIGKILL)
    except (OSError, subprocess.SubprocessError):
        p.kill()


def run(cmd: list[str], timeout: int = 300, stdin: str | None = None,
        env: dict | None = None) -> tuple[int, str, str]:
    kw = dict(stdin=subprocess.PIPE if stdin is not None else subprocess.DEVNULL,
              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8",
              errors="replace", env=env)
    if WIN:
        kw["creationflags"] = subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        kw["start_new_session"] = True
    try:
        p = subprocess.Popen(cmd, **kw)
    except OSError as exc:
        return 127, "", f"{exc.__class__.__name__}: {exc}"
    try:
        out, err = p.communicate(stdin, timeout=timeout)
        return p.returncode, out or "", err or ""
    except subprocess.TimeoutExpired:
        _kill_tree(p)
        try:
            out, err = p.communicate(timeout=30)
        except subprocess.TimeoutExpired:
            out, err = "", ""
        return 124, out or "", (err or "") + f"\ntimeout after {timeout}s"


def npm_cmd() -> str | None:
    return shutil.which("npm")


def npm_prefix() -> str | None:
    npm = npm_cmd()
    if not npm:
        return None
    rc, out, _ = run([npm, "prefix", "-g"], 60)
    lines = [ln.strip() for ln in out.splitlines() if ln.strip()]
    return lines[-1] if rc == 0 and lines and os.path.isdir(lines[-1]) else None


def latest(pkg: str) -> tuple[int, ...] | None:
    npm = npm_cmd()
    if not npm:
        return None
    rc, out, _ = run([npm, "view", pkg, "version"], 90)
    return parse_version(out) if rc == 0 else None


def installs(name: str) -> list[str]:
    """Every executable named `name` on PATH, in resolution order, one per directory."""
    exts = [e.lower() for e in os.environ.get("PATHEXT", ".EXE;.CMD").split(";") if e] if WIN else [""]
    found = []
    for d in path_dirs(os.environ.get("PATH", "")):
        for e in exts:
            p = os.path.join(d, name + e)
            if os.path.isfile(p) and (WIN or os.access(p, os.X_OK)):
                found.append(p)
                break
    return found


def installed_version(path: str) -> tuple[int, ...] | None:
    rc, out, _ = run([path, "--version"], 60)
    return parse_version(out) if rc == 0 else None


def upgrade_cmd(cli: str, kind: str, path: str, target: str) -> list[str] | None:
    if kind == "npm":
        return [npm_cmd() or "npm", "install", "-g", f"{PACKAGES[cli]}@{target}", "--no-fund", "--no-audit"]
    if kind == "native" and cli == "claude":
        return [path, "install", target]
    if kind == "winget" and cli == "codex":
        return ["winget", "upgrade", "--id", "OpenAI.Codex", "--exact", "--silent",
                "--accept-source-agreements", "--accept-package-agreements", "--disable-interactivity"]
    return None


# ---------------------------------------------------------------- smoke tests

def codex_slugs() -> list[str]:
    try:
        d = json.loads((HOME / ".codex" / "models_cache.json").read_text(encoding="utf-8"))
        return [m.get("slug") for m in d.get("models", []) if m.get("slug")]
    except (OSError, ValueError, AttributeError):
        return []


def shim_check(path: str) -> bool | None:
    """npm on Windows also installs an extensionless sh shim that bash-launched lanes resolve; the
    fleet has seen that shim broken while codex.cmd worked. None when there is nothing to check."""
    shim, bash = os.path.splitext(path)[0], shutil.which("bash")
    if not (WIN and bash and os.path.isfile(shim)):
        return None
    rc, out, _ = run([bash, shim, "--version"], 60)
    return rc == 0 and parse_version(out) == installed_version(path)


def smoke(cli: str, path: str, kind: str = "") -> dict:
    t0 = time.time()
    env = dict(os.environ, CLI_CURRENCY_SMOKE="1")
    if cli == "claude":
        rc, out, err = run([path, "-p", PROMPT, "--model", "haiku", "--output-format", "json",
                            *CLAUDE_SMOKE_ISOLATION], 180, env=env)
        ok, model = claude_smoke_ok(rc, out)
    else:
        model = codex_smoke_model(codex_slugs())
        fd, last = tempfile.mkstemp(prefix="cli-currency-codex-", suffix=".txt")
        os.close(fd)
        try:
            cmd = [path, "exec", "--ephemeral", "--skip-git-repo-check", "--sandbox", "read-only",
                   "-c", "model_reasoning_effort=low", "-o", last] + (["-m", model] if model else []) + ["-"]
            rc, out, err = run(cmd, 300, stdin=PROMPT, env=env)
            reply = pathlib.Path(last).read_text(encoding="utf-8", errors="replace").strip()
        except OSError:
            reply = ""
        finally:
            pathlib.Path(last).unlink(missing_ok=True)
        ok = rc == 0 and reply == READY   # the final message only; stderr echoes the prompt
    shim = shim_check(path) if kind == "npm" else None
    ok = ok and shim is not False
    return {"ok": ok, "rc": rc, "model": model, "shim_ok": shim, "seconds": round(time.time() - t0, 1),
            "tail": None if ok else (out + err).strip()[-400:]}


# ---------------------------------------------------------------- state and lock

def load_json(p: pathlib.Path) -> dict:
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def sweep_npm_trash(prefix: str | None) -> list[str]:
    """Remove npm's moved-aside package dirs once nothing holds them (see design fact 1)."""
    if not prefix:
        return []
    root = pathlib.Path(prefix) / ("node_modules" if WIN else "lib/node_modules")
    swept = []
    for scope, stem in (("@openai", ".codex-"), ("@anthropic-ai", ".claude-code-")):
        for d in (root / scope).glob(stem + "*") if (root / scope).is_dir() else []:
            shutil.rmtree(d, ignore_errors=True)
            if not d.exists():
                swept.append(str(d))
    return swept


def pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    if WIN:
        import ctypes
        k = ctypes.windll.kernel32
        h = k.OpenProcess(0x1000, False, pid)          # PROCESS_QUERY_LIMITED_INFORMATION
        if not h:
            return False
        code = ctypes.c_ulong()
        k.GetExitCodeProcess(h, ctypes.byref(code))
        k.CloseHandle(h)
        return code.value == 259                        # STILL_ACTIVE
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def acquire_lock(lock: pathlib.Path) -> bool:
    """A lock is stale only when the pid in it is dead; nobody removes a live run's lock."""
    lock.parent.mkdir(parents=True, exist_ok=True)
    for _ in range(2):
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode())
            os.close(fd)
            return True
        except FileExistsError:
            try:
                holder = int(lock.read_text().strip() or 0)
            except (OSError, ValueError):
                holder = 0
            if pid_alive(holder):
                return False
            lock.unlink(missing_ok=True)
    return False


def release_lock(lock: pathlib.Path) -> None:
    try:
        if lock.read_text().strip() == str(os.getpid()):
            lock.unlink()
    except OSError:
        pass


def append_receipt(receipt: dict) -> None:
    STATE.mkdir(parents=True, exist_ok=True)
    p = STATE / "receipts.jsonl"
    if p.exists() and p.stat().st_size > RECEIPTS_MAX_BYTES:
        lines = p.read_text(encoding="utf-8").splitlines(keepends=True)
        p.write_text("".join(lines[len(lines) // 2:]), encoding="utf-8")
    with open(p, "a", encoding="utf-8") as f:
        f.write(json.dumps(receipt) + "\n")


# ---------------------------------------------------------------- main

def process_cli(cli: str, apply: bool, prefix: str | None, state: dict, hold: dict, t0: float) -> dict:
    target_v = latest(PACKAGES[cli])
    res = {"cli": cli, "latest": vstr(target_v), "installs": []}
    if not target_v:
        res["status"] = "CHECK-FAILED"
        return res
    target = vstr(target_v)
    for path in installs(cli):
        kind = classify(path, prefix)
        before = installed_version(path)
        entry = {"path": path, "kind": kind, "before": vstr(before), "after": vstr(before)}
        res["installs"].append(entry)
        if before and before >= target_v:
            entry["status"] = "CURRENT"
            continue
        cmd = upgrade_cmd(cli, kind, path, target)
        why = held(cli, target, state, hold)
        if not cmd:
            entry["status"] = "DRIFT-UNMANAGED"
        elif why:
            entry.update(status="HELD", reason=why)
        elif not apply:
            entry["status"] = "DRIFT"
        elif time.time() - t0 > NO_NEW_UPGRADE_AFTER_S:
            entry["status"] = "SKIPPED-DEADLINE"
        else:
            upgrade_one(cli, kind, path, before, target, cmd, entry, state)
    res["status"] = "NOT-INSTALLED" if not res["installs"] else rollup({i["status"] for i in res["installs"]})
    return res


def upgrade_one(cli, kind, path, before, target, cmd, entry, state) -> None:
    rc, out, err = run(cmd, 900)
    after = installed_version(path)
    entry.update(after=vstr(after), upgrade_rc=rc)
    if rc == 0 and after and before and after == before and kind == "winget":
        entry["status"] = "WINGET-LAGS-NPM"   # winget's manifest has not caught up; not a failure
        return
    if not after or after <= (before or (0,)):
        entry.update(status="UPGRADE-FAILED", tail=(out + err).strip()[-400:])
        return
    s = smoke(cli, path, kind)
    entry["smoke"] = s
    if s["ok"]:
        entry["status"] = "UPGRADED"
        return
    back = upgrade_cmd(cli, kind, path, vstr(before)) if before and kind != "winget" else None
    if not back:
        entry["status"] = "UPGRADED-SMOKE-FAILED-NO-ROLLBACK"
        return
    brc, bout, berr = run(back, 900)
    now = installed_version(path)
    entry.update(rollback_rc=brc, after=vstr(now))
    if now != before:
        entry.update(status="ROLLBACK-FAILED", tail=(bout + berr).strip()[-400:])
        return
    old = smoke(cli, path, kind)
    entry["rollback_smoke"] = old
    if old["ok"]:
        entry["status"] = "ROLLED-BACK"
        state.setdefault("rejected", {})[cli] = target
        return
    run(cmd, 900)   # both versions fail: the environment is the cause, keep the new one
    entry.update(status="UPGRADED-ENVIRONMENT-SMOKE-FAILED", after=vstr(installed_version(path)))


def model_inventory(claude_path: str | None) -> dict:
    inv = {"codex": codex_slugs(), "claude": []}
    if claude_path and (not WIN or claude_path.lower().endswith(".exe")):
        try:
            inv["claude"] = claude_models_in(pathlib.Path(claude_path).resolve().read_bytes())
        except OSError:
            pass
    return inv


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--resolve", metavar="TIER", help="print the newest Codex slug of TIER and exit")
    a = ap.parse_args()
    if a.resolve:
        slug = resolve_tier(codex_slugs(), a.resolve)
        if not slug:
            print(f"[cli-currency] no gpt-*-{a.resolve} model in ~/.codex/models_cache.json", file=sys.stderr)
            return 2
        print(slug)
        return 0

    lock = STATE / "run.lock"
    if not acquire_lock(lock):
        print("[cli-currency] another live run holds the lock; skipping")
        return 0
    try:
        return run_once(a)
    except Exception as exc:   # a run that dies still leaves a receipt saying so
        append_receipt({"at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
                        "host": platform.node(), "mode": "apply" if a.apply else "check",
                        "error": f"{exc.__class__.__name__}: {exc}"})
        raise
    finally:
        release_lock(lock)


def run_once(a) -> int:
    t0 = time.time()
    prev = load_json(STATE / "latest.json")
    hold = load_json(HOLD_FILE)
    state = {"rejected": {k: v for k, v in (prev.get("rejected") or {}).items()}}
    prefix = npm_prefix()
    started = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    clis = [process_cli(c, a.apply, prefix, state, hold, t0) for c in ("claude", "codex")]
    for c in clis:   # a rejection lapses once npm latest has moved past it
        if c["latest"] and state["rejected"].get(c["cli"]) not in (None, c["latest"]):
            del state["rejected"][c["cli"]]
    inv = model_inventory(next(iter(installs("claude")), None))
    prev_inv = prev.get("models") or {}
    new_models = {k: diff_models(prev_inv.get(k, []), v) for k, v in inv.items() if prev_inv.get(k)}
    receipt = {"at": started, "host": platform.node(), "mode": "apply" if a.apply else "check",
               "clis": clis, "models": inv, "new_models": {k: v for k, v in new_models.items() if v},
               "rejected": state["rejected"], "swept": sweep_npm_trash(prefix) if a.apply else [],
               "seconds": round(time.time() - t0, 1)}
    STATE.mkdir(parents=True, exist_ok=True)
    append_receipt(receipt)
    (STATE / "latest.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    if a.json:
        print(json.dumps(receipt, indent=2))
    else:
        for c in clis:
            parts = [f"{pathlib.Path(i['path']).parent.name}/{i['kind']} {i['before']}->{i['after']} {i.get('status')}"
                     for i in c["installs"]]
            print(f"[cli-currency] {c['cli']} latest={c['latest']} {c['status']}: " + "; ".join(parts))
        for k, v in receipt["new_models"].items():
            print(f"[cli-currency] NEW {k} models: {', '.join(v)}")
    return 1 if any(c["status"] in BAD for c in clis) else 0


if __name__ == "__main__":
    sys.exit(main())
