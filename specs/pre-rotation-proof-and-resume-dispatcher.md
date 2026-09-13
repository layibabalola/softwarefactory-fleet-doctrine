# Pre-rotation proof and the resume dispatcher — prove continuity BEFORE you rotate (conjugal, 2026-09-13, Bachelor)

**Status:** PROPOSED portable pattern; zero runtime authority until a project adopts or distinguishes it (law 2).
**Extends, does not replace:** `account-rotation-and-project-continuity.md` (Adobe: four-layer continuity, lifecycle) and
`cli-credential-rotation-automation.md` (Conjugal: CLI/desktop credential sync). Those say *what* survives a rotation.
This spec adds (a) a dispatcher that turns one phrase into a seated chip with the owner's four choices, (b) a SessionStart
hook whose evidence line can never be hidden, and (c) a **three-check proof you run before rotating**, on real sessions,
without touching auth. All three were measured on 2026-09-13 (receipt in RECEIPTS.md).

## 1. The resume dispatcher (project `CLAUDE.md`, any model)

When the owner says "resume our work" (or "resume", "pick up where we left off"):

0. Run the auth/parity checker with the live probe **yourself, first**; on non-zero paste its output verbatim and stop
   (the owner runs the printed remedy; a limit is never fixed by re-authing). Fully qualified path, Bash timeout ≥150 s.
1. Ask ONE four-part question: (a) which workstream (table of workstream → entry file → recommended model, plus "other");
   (b) chip model, recommendation pre-selected; (c) update cadence (5-min cron / milestones / none); (d) posture
   (autonomous with escalation only on deadlock/novel/high-risk — the standing default — or confirm-before-acting).
2. Spawn a chip with a **pointer-only** prompt: entry file, model, cadence, posture, "say which thread you are resuming
   before acting", the workstream's own procedure. Never paste SHAs, scores, verdicts or a prose state summary.
3. Report the chip. The dispatcher claims no seat and starts no work.

Entry files carry **procedures only** and derive state with commands (`tail scores.csv`, `ls rounds/`, `git log`), and
state the step-derivation rule explicitly ("newest artifact class present → resume at the first missing step; if the
stopping rule fired, next is the hand-off file, not another round").

## 2. SessionStart hook that cannot hide its own red

A hook exiting non-zero has its output suppressed — exactly when a red verdict matters. Wrap the checker:

```python
# coordination/tools/session-start-auth.py — always exit 0; carry the checker's exit code in the printed line
p = subprocess.run([sys.executable, CHECKER], capture_output=True, text=True, timeout=30, encoding="utf-8", errors="replace")
print(f"[session-start] CLI auth/parity, identity-only (exit {p.returncode}): {(p.stdout or p.stderr).strip()}")
if p.returncode: print("[session-start] NON-ZERO: paste the line above into chat before deriving anything; re-run: python \"<abs path>\" --allow-live-probe")
return 0
```

Reconfigure stdout to UTF-8 first (`sys.stdout.reconfigure(encoding="utf-8", errors="replace")`) — a cp1252 console
raised `UnicodeEncodeError` on the checker's em-dashes, which would have hidden the line a second way. Keep the hook
identity-only (~1–3 s); the live probe (5–6 s from a terminal or a fresh session, 53–89 s from a Bash call inside a
desktop-app session) belongs in dispatcher step 0. Register in `.claude/settings.json` under `hooks.SessionStart`.

## 3. The three-check proof (run before rotating; ~1 minute; touches no credentials)

| # | Proves | Command | Pass looks like |
|---|---|---|---|
| 1 | Mismatch detection + remedy branch | `python "<abs>\check-cli-auth.py" --desktop-email someone.else@example.com` | exit 1; parity block; remedy with the `&` PowerShell call operator and `auth login --claudeai --email …` pre-filled; re-check line fully qualified |
| 2 | Hook line reaches a fresh session | `printf '%s\n' "Print verbatim every line in your context that starts with [session-start]; else print NO HOOK LINE RECEIVED." \| claude -p --model haiku --max-turns 1` | both `[session-start]` lines printed |
| 3 | Dispatcher path in a real fresh session | `claude -p --model haiku --max-turns 8 --allowedTools "Read,Bash,Glob,Grep" < prompt.txt` where prompt.txt = "resume our work" + a harness note (no AskUserQuestion/spawn_task available; print the four-part question instead; do not edit) | step 0 ran and PASSed; the four-part question printed with the right recommended model; no spawn, no edits |

Plus the no-memory derivation check: a cheap agent told "resume our work" with tools **mandatory** (≥6 calls, one
quoted line per file, "missing" proven only by Read/`git ls-files`) must land on the same next step you expect.
Its first run without that rule made zero tool calls and declared a tracked entry file missing (TRAPS.md 2026-09-13).

Traps met (TRAPS.md, 2026-09-13): `claude -p` rejects a positional prompt after flags — pipe it on stdin; a flag that
only ever existed on a replaced git lineage; relative paths in printed commands (owner rule: fully qualified, quoted).

## 5. Resumability cadence — rotate WITHOUT warning (owner rule 2026-09-13, measured failure the same day)

The failure: Conjugal's durable state (sync globs, the entry file's step-derivation order, committed prompts for the
Claude seats) was built only after the owner warned that usage was depleting; a gate then found 27 outputs whose prompts
had never been committed. Readiness must be an **invariant checked by a tool at the moments spend happens**:

| When | What | Why |
|---|---|---|
| every landing seam | sync + exact-path commit + `resumability-check` PASS; the commit is not done until it passes | an artifact nobody can place is a step nobody can resume |
| before every expensive launch (>5 min or >100k tokens) | run the gate — checkpoint before spend | a cut hurts most mid-agent |
| first 429 / rate-limit from any provider | stop launching inference, checkpoint, print ONE `ROTATE_REQUEST` line, park only inference-needing work | the session applies the same latch doctrine it designs for the factory |
| status tick while a loop runs (≤15 min) | run the gate | backstop for seams that were missed |
| weekly, per project | the §3 three-check proof; receipt on the bus with timings | mechanisms rot silently (a flag that existed only on a replaced lineage) |

Gate contract (Conjugal reference: `coordination/tools/resumability-check.py`, ~150 lines, refuses on): content-dirt
under the workstream path (CRLF phantoms ignored); an artifact class in `rounds/` that the entry file's derivation rule
does not name; an output with no committed prompt or per-round template under `prompts/`; SHA-like tokens or scores
in the entry file outside code fences. Pre-gate history is named in an explicit allowlist that is closed once the
gate exists — never silently skipped.

## 4. Adopt-or-distinguish checklist for a sibling project

- Does your `CLAUDE.md` resume trigger ask the four questions and spawn a pointer-only chip? If it seats work in the
  dispatching session, distinguish and say why.
- Is your entry file procedures-only with a stated step-derivation rule? If it carries SHAs/scores, it is stale by construction.
- Does your SessionStart hook exit 0 and print a verdict line? Test it with a forced red.
- Run the three checks; file the receipt (date, machine, timings) in RECEIPTS.md.
- Adopt the §5 cadence: a resumability gate for your workstream path, wired at landing seams, before spend, on first 429,
  on the tick, and rehearsed weekly. If you have no gate yet, say so in `specs/<project>.md` — that is a distinguish, not silence.
