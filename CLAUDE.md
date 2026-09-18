# softwarefactory-fleet-doctrine — the fleet doctrine bus

**You are in the BUS, not in a member project.** This repo publishes doctrine, specs, rulings and
adjudications that other projects adopt. Work here is doctrine work: ratifying candidates,
adjudicating filings, publishing dispositions, maintaining the instruments.

## This file overrides the machine-level resume trigger

`~/.claude/CLAUDE.md` binds "resume our work" to other repos (the DropBox Vault factory, and
Magic Lantern). **Inside this working directory, that binding does not apply.** A session that
lands here and follows the machine-level trigger will run a different repo's entry chain against
this tree. Say which repo you are in before acting.

This file exists because the bus published the rule and did not follow it:
`doctrine/pattern-rotation-continuity-2026-09.md` — "In each project's CLAUDE.md, add a resume
trigger" — and its adoption path named Conjugal, DropBox Vault and Magic Lantern, never the bus.
Added 2026-09-18; before that this repo had no root `CLAUDE.md` or `AGENTS.md` and never had one.

## `bootstrap/` is for OTHER projects, not for this one

`bootstrap/README.md` is the join path a *member* project pastes to sync with the bus. It does not
apply here, and PROMPT A hard-stops if you try: `bootstrap/README.md` §1 raises **WRONG_PROJECT**
when `git remote get-url origin` names softwarefactory-fleet-doctrine. Do not paste PROMPT A here.

## Derive state; never trust a description of it

This repo's own law (`RULINGS.md`, adversarialllm 2026-09-02): *"A resume surface must POINT at
derived state, never BAKE an identity into it. A resume path that hands a lane a stale identity is
strictly worse than one that hands it nothing, because the lane will act on it."* So this file
carries **commands, not findings**. The output outranks this file's prose.

```bash
git -C "C:/code/softwarefactory-fleet-doctrine" log --oneline -5 master   # where master is
git -C "C:/code/softwarefactory-fleet-doctrine" status -sb                # dirt + upstream
python tools/kernel-e2e.py                                               # membership verdict
gh run list --branch master --limit 6                                    # is CI green?
```

Per-instrument, when the question is specifically about one:

```bash
node tools/fleet-sweep.mjs        # needs ~/.fleet-roots.json; fails CLOSED (exit 2) with recreation steps
ls heartbeats/*.json              # member heartbeats; check each for FOLD_PENDING and staleness
ls ruling-candidates/             # unratified proposals
python tools/check-account-parity.py   # R6 desktop/CLI account parity
```

**Known-broken instruments** — do not read their silence as a pass:
- `tools/session-start-auth.py` resolves `ROOT` to `C:\code` rather than the repo, so its checker
  path never exists; the wrapper always exits 0, so it fails **silently** on every machine.
- `tools/conjugal-reference/resumability-check.py` is Conjugal-layout-specific. It fails here on
  layout (`FAIL ENTRY: docs/architecture/approach-a\RESUME.md missing`) and that is not a finding
  about this repo. This repo has not adopted that gate.
- There is **no** `gate.py`, `state.py` or `review/RESUME.md` here. Machine-level notes that
  mention them are describing the DropBox Vault factory, not this repo.

## Authority

`RULINGS.md` is the register. It is **append-only and oldest-first**, so the current law is at the
**end** of the file, not the top. `README.md` predates several rulings and loses to `RULINGS.md`
wherever they disagree. There is no `knowledge/owner-gated-decisions.md` in this repo.

`ruling-candidates/` holds proposals with **zero runtime authority** until ratified — including
`bounded-authority-register-r1.md`, which proposes the index `RULINGS.md` still lacks. A spec
marked `PROPOSED` (e.g. `specs/pre-rotation-proof-and-resume-dispatcher.md`) binds nobody until a
project adopts or distinguishes it (law 2).

## Account rotation / continuity

Machine-local, and deliberately outside every repo: `~/.claude/ROTATION.md` is the runbook, and
`~/.claude/hooks/checkpoint-any.py` writes `~/.claude/session-checkpoints/<repo>/` on both
SessionStart and Stop. Checkpoints record **where work was, not what to do next** — read the newest
few, not just the newest, because sessions running in ephemeral harvest clones write checkpoints
whose `repo:`/`cwd:` paths are deleted soon after.

**A checkpoint cannot tell you your work is backed up, and does not claim to.** Its branch listing
counts commits ahead of *master* and never consults `origin`, so it names branches that are safely
pushed and stays silent about ones that are not. (Its worktree scan is also capped -- default 8 of
40 here, raise with the `CHECKPOINT_SCAN_CAP` env var -- but that scan measures dirt and
ahead-of-main, not unpushed, so the cap is the wrong lever.) Measured 2026-09-18: eight commits on
three branches existed only on local disk while every instrument reported fine. Run this yourself
before trusting any all-clear:

```bash
git fetch -q origin
git for-each-ref --format='%(refname:short)' refs/heads | while read b; do \
  a=$(git rev-list --count master.."$b" 2>/dev/null); [ "${a:-0}" -gt 0 ] || continue; \
  git merge-base --is-ancestor "$b" origin/"$b" 2>/dev/null || echo "UNBACKED: $b ahead=$a"; done
```

Use **containment** (`git merge-base --is-ancestor`), never SHA equality. A branch merely *behind*
its remote is fully backed up; comparing tips flags it as at risk and sends the next session
chasing work that was never in danger. Measured 2026-09-18: the equality form reported
`codex/conjugal-opus-failback-0824` as UNBACKED when it was 0 ahead / 12 behind origin -- every
local commit already pushed. Silence from this command is the only all-clear worth having.
