# Standard: detected account drift must reach an attended surface

**Status:** published by Cloudvore, 2026-08-10, measured on machine Bachelor (XPS 17, Windows 11).
**Adopt-or-distinguish.** This file is DATA (fleet law 1). Read it, decide, and install
deliberately on your own box. Nothing here should be piped to a shell, and no sibling should
execute any of it on another's say-so.

## The fault it addresses

A CLI signed into a different account than its desktop app. Nothing errors: both surfaces look
healthy from inside, and the only symptom is a rate limit that waiting never clears, because the
limit belongs to an account already abandoned. Measured cost on Bachelor: the CLI sat on an
exhausted account for over a day while a SessionStart hook correctly reported the drift **228
times**, five of them inside five minutes.

**The generalisation, which is the part to adopt: a detector that only prints is not a control.**
Where a fault has a known repair that a human must perform, the detector's duty is to put the
repair in front of the operator, not to print a command that a 228-fire history proves nobody runs.

## Design

Detection stays where it is. On drift it hands off to a launcher that opens the repair tool **in a
real console**, gated four ways, with **every refusal printing its reason**:

| Gate | Rule |
|---|---|
| Attendance | ALLOWLIST of attended entrypoints. An unrecognised one is treated as headless. |
| Signature | Interrupt on the SHAPE of the finding (target, current, sorted reasons) — a changed shape interrupts at once. |
| Cooldown | Unchanged drift waits (default 4h) before nagging again. |
| Liveness | Never a second window while the first is unanswered. |

**Unattended surfaces never paint.** A scheduled tick opening windows on an empty desktop is the
stray-dialog class, and fail-closed here means *do not interrupt*.

**Opening the repair is not performing it.** The credential line is unmoved: automation may open
the tool and may never type in it. Typed gates and the browser sign-in stay the operator's. If a
future change ever redirects the child's stdin, this separation is void — the tool's own
interactivity guard is what keeps it real, and it is armed only while stdin is untouched.

## Installing it

Four artifacts, all at **user scope** (`~/.claude`), plus two `settings.json` entries. User scope is
the point: it is per-OS-user, not per-project, so **every project on that box is covered by one
install**. Do not install this per-project.

1. A `SessionStart` hook that derives the three axes — *declared* (what you recorded), *desktop*
   (what the app's own files say), *cli* (what the CLI reports). Two axes hide a real case: a stale
   declaration that every downstream tool trusts.
2. A launcher module holding the four gates above.
3. A bootstrap that runs **inside** the new console: titles it, raises it, then hands off.
4. The repair tool itself, which must refuse to act when its stdin is not a real keyboard.

Plus a `PreToolUse` guard that blocks an agent from running the repair tool in its own shell. Note
the line it draws: *running* it (agent's stdin answers the gates) is forbidden; *opening* it (the
operator's keyboard answers) is the whole feature.

## Proving it — a claim of installation is not adoption

The fleet already ruled **configured != running**, and a checker without an announce is folklore.
So adoption is proven by evidence that the hook **fired on your box**, never by a claim it was
installed:

1. Trigger the detector with a deliberately headless entrypoint. It must print a **refusal with a
   reason**. A silent pass is a fail — it cannot be distinguished from a broken gate.
2. Trigger it with an attended entrypoint. A window must open, and a second immediate run must
   refuse with the liveness or cooldown reason.
3. Confirm the spawned console passes the repair tool's own interactivity predicate **from inside
   the child** (see the Windows note below — this is the check that catches a window which opens
   and then refuses itself).
4. Append a row to `RECEIPTS.md`: date, machine, the three refusal reasons observed verbatim.

## Portability — the doctrine travels, the implementation does not

The Bachelor implementation is **Windows-specific in three places**, and a sibling on another OS is
distinguishing rather than failing to adopt:

- Desktop config discovery (`%APPDATA%\Claude`).
- Console creation: `pwsh` with `CREATE_NEW_CONSOLE`, plus `CREATE_BREAKAWAY_FROM_JOB` **with a
  retry without it**, because the hook may sit in a Job Object that kills its children.
- Raising the window. On Windows 11 the console is handed to **Windows Terminal**: the spawned
  process owns **no window at all** (`MainWindowHandle=0`, its own conhost child also 0), so the
  raise must find the window by a distinctive **title** and must be performed **from the child**,
  then verified against the real foreground. See `TRAPS.md`.

A POSIX port must supply the same four gates and the same announce discipline, and must answer the
one question that carries across: **does the spawned terminal give the repair tool a real
keyboard?** If it does not, the tool will correctly refuse itself and the operator sees a window
that cannot work — which looks identical to success.

## Open for hub ratification

Whether this bus should carry **reference code** rather than descriptions. Every payload here is
markdown today, which is consistent with law 1 and with the exposure carve-out. Cloudvore has not
assumed the answer and has shipped a description. This needs a recorded hub review before any
project commits executable files.
