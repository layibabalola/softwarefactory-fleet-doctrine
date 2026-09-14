# Lane orchestrator — cross-family design review

*Not pasted by hand. PROMPT B spawns a chip pointed here.*

Paste this into ONE session. That session is the orchestrator: it seats no lane itself, it
drives the lanes over the provider CLIs and consolidates what they return.

PROMPT A must have run. This refuses to start without a synced doctrine and an inventory.

---

## 0. Bind the subject — fail closed

Before anything else, state these three bindings out loud. If you cannot derive one from the
repository, **stop and ask**. Do not substitute a placeholder and continue.

- `PROJECT` — the project short name (used in the output path).
- `SUBJECT` — the exact files under review, as repo-relative paths. Not "the design", not
  "the specs": a list of paths you have confirmed exist with Glob or ls.
- `REPO` — absolute path to the repository the subject lives in.

A review whose subject is unbound reviews nothing and reports success. That failure is silent,
so the binding is checked here rather than discovered later.

## 1. Preflight

Run these and report each result. Any FAIL stops the run.

```bash
# doctrine freshness + parity — receipt written by PROMPT A
cat .claude/doctrine-sync.json
```
Require `status: "SYNCED"` and a `synced_at` within the last 24 hours. **Absence of this file
is a FAIL, not a pass** — it means the sync never ran, which is indistinguishable from a stale
doctrine unless you insist on the receipt.

```bash
python tools/check-cli-auth.py      # Claude family
codex login status                  # Codex family  (NOT `codex auth status` — no such subcommand)
git -C "$REPO" rev-parse --abbrev-ref HEAD
git -C "$REPO" status --short -- <SUBJECT paths only>
```

Resolve the inventory, in this order, and say which answered:

1. `./.claude/machine-inventory.yaml` — a project override, if this project needs one.
2. `~/.claude/machine-inventory.yaml` — the machine inventory, derived by PROMPT A.
3. Neither → **stop** and run `<doctrine>/tools/probe-machine-inventory.sh`, then retry.

Providers and model ids are a property of the **machine**, not the project. Most projects
should have no inventory of their own; a per-project copy is a second place for the same model
table to go stale, and the first symptom of that drift is a lane that dispatches to a retired
id and reports clean.

Take the `-m` / `--model` values from whichever file answered. **Do not type a model id from
memory or from this prompt** — the inventory's ids were confirmed by live sentinel challenge,
and a remembered one has no such standing.

Route per `dispatch-trigger-standard.md`:

- **Both families available** → the full posture, §2 below: every role in
  `tools/review-posture/roles.json`, not a subset you judge sufficient (RULINGS **R9**).
- **One family available** → degraded: run what that family can seat and let the tool's posture
  line say `-PARTIAL` with the missing roles named, and `cross_family: NO-CROSS-FAMILY-VALIDATION`.
  Never label it with the posture's name.
- **Neither available** → **FAIL with a constraint violation report. Do not wait, do not
  downgrade, do not review solo.** A wait is not a fallback.

## 2. Run the full posture with the tool, in ONE call

**Do not hand-write a runner.** Every hand-written runner on this bus has dropped something. The
first version of this section dispatched 5 of the posture's 17 lanes (no consolidator, no panel, no
classifier, and an arbiter that never saw lint), and the filings it produced still carried the
`conjugal-standard` label. Another interpolated the subject path into a double-quoted heredoc and
sent every lane the literal text `…doctrine$SUBJECT`. Neither failure is visible to the sentinel,
because the lanes still answer. The role list now lives in data (`tools/review-posture/roles.json`)
and the tool is tested (`tests/test_review_posture.py`, including a check that fails if that role
list and `specs/posture-templates-conjugal-standard.md` drift apart).

Shell variables and background jobs do **not** survive between tool calls, so run all four stages in
a single invocation:

```bash
export RP_REPO="<abs path of the repo holding the subject>"
export RP_SUBJECT="<abs path of the subject file>"      # must exist; every prompt is checked to name it
export RP_BENCH="<abs path of YOUR repo, the test bench>"
export RP_OUT="<abs output dir outside the bus>"         # raw lane output never travels (Law 4)
# export RP_RUBRIC="<rubric json>"  # default tools/review-posture/rubrics/approach-a-r15.json (Conjugal R15)
bash "<doctrine>/tools/review-posture/run.sh" --dry-run   # generate + binding-check prompts, dispatch nothing
bash "<doctrine>/tools/review-posture/run.sh"             # stages A-D; ends with the posture measurement
```

| stage | role lanes (ids from the machine inventory, never from memory) | reads |
|---|---|---|
| A | Designer-Scope (opus), Designer-Verify (sol), Lint-Consistency (haiku + luna) | the subject, the bench |
| B | Arbiter (astra) **in parallel with** the blinded Panel (fable, opus, sonnet×3, astra, sol, luna) | arbiter: designers **and** lint; panel: the subject only |
| C | Consolidator (fable) | the arbitration |
| D | Classifier swarm (haiku×3, 2-of-3) | consolidated findings, panel scores, seat-stripped panel blockers |

The tool recomputes each panel composite from the dimension numbers (never a seat's own average),
pins `rubric_id = sha256(canonical scoring contract)` and writes that contract to `rubric.json`,
tallies the classifier at 2-of-3 from strict `HEADING: value` lines only (anything looser is recorded
as unparsed, never guessed), and ends with `posture:` and `cross_family:` lines computed from the
sentinels against `roles.json`. It exits 1 when the posture is PARTIAL.

`--from B|C|D` reuses earlier stages already in `RP_OUT`. Do that only after re-measuring that the
subject blob and the bench HEAD are unchanged, and disclose the reuse in the filing.

**On Windows, confirm which `bash` that is.** From PowerShell, `bash` can resolve to **WSL**, not
Git Bash — and WSL has its own filesystem and `PATH`, so it cannot see a Windows-installed
`claude` and resolves `C:/...` paths differently. The failure does not look like a shell
problem: an inventory that exists reads as absent, a model id that is present reads as
missing. Measured 2026-09-13 in a live run, where a WSL detour produced a false "inventory
lacks astra" conclusion that outlived the switch to Git Bash. Check with `command -v bash` or
`bash -c 'command -v claude'` before trusting anything the runner reads.

**Judge each lane on the sentinel, not on rc and not on size.** Measured, two lanes side by
side with one model id mistyped:

```
good    rc=0  bytes=359  RAN
bogus   rc=1  bytes=738  DID-NOT-RUN
```

The dead lane returned twice the bytes of the live one — the unrecognized-model error is longer
than the answer — so any size heuristic rates the empty seat the richer contributor. rc catches
*that* failure, but only if captured directly: `claude … | head` hands you `head`'s status, not
the CLI's. And rc misses the quiet failures entirely, where a lane exits 0 having refused,
truncated, or answered the wrong question. `LANE-COMPLETE` survives all of them because no
failure path can emit it. Report all three; let the sentinel decide.

## 2b. Verify what the lanes quoted before filing any of it

Lanes paraphrase, and a paraphrase filed inside quotation marks is a fabricated citation.
Before consolidating:

- **Every quoted phrase** is checked verbatim against the subject: `grep -F "<phrase>" <subject>`.
- **Every test-bench claim** — a path, a line number, a count — is re-measured on this repo.
  A lane that cites `file.py:3886` is asserting something checkable; check it.
- **Record what you did not re-measure** rather than letting it inherit the verified findings'
  standing.
- **Panel blockers carry quotes too** — check them the same way before quoting the panel.
- **When seats disagree on something checkable, re-derive it; never average or pick a side.**
  Measured 2026-09-14: one panel seat said §11's rows reproduce a stated 33,240 s, another said
  they sum to 33,540 s. Neither reproduced; the orchestrator's own sum settled it as an unresolved
  ambiguity in the subject, which is a finding in itself.
- **Read the arbiter's losers against the subject.** A loser rejected on a premise the subject does
  not contain is a lost finding. Each counterexample should point at text you can find.

Measured 2026-09-13: a cross-family run's lanes cited a test assertion at `factory-health.tests.py:3886`;
it was at `:501`. Every other quote held. One wrong line number in an otherwise sound filing is
the case that matters, because the filing is otherwise trustworthy enough that nobody re-reads it.

## 3. Consolidate — always

Write `adjudications/approach-a-design/<PROJECT>.md` from the consolidator's body and the tool's
`panel.json`, `classifier.json` and `rubric.json` (commit the rubric beside the filing as
`<PROJECT>.rubric.json`; a `rubric_id` whose contract is not retained has no comparability standing):

```
project: <PROJECT>
subject: <SUBJECT path (blob sha)>          test_bench: <path @ HEAD>
providers: <families and nicknames the inventory answered with>
posture: <copied verbatim from the tool's `posture:` line>
cross_family: <copied verbatim from the tool's `cross_family:` line>
rubric_id: <from the tool>                   panel: <composite> over <n>/8 seats, <families> families, spread <x>

## Design findings        (consolidator; one line each: § | "quote" | defect | REPLACES | PROOF)
## Untested
## Cross-section contradictions   (lint items the arbiter KEPT)
## Arbiter losers         (rejected, with counterexample — the fleet reads these before re-filing)
## Panel                  (score table, verified blocker quotes, any seat disagreement you re-derived)
## Classifier consensus   (per finding TEXT/DESIGN, GROUNDED, must-fix votes; STOPPING; ceilings; unparsed)
## Provenance             (every lane: stage, model, rc, bytes, sentinel; reuse disclosed; what you did not re-measure)
```

**Copy the `posture:` line from the tool; never type it.** It names the posture only when every lane
of every role in `roles.json` cleared the sentinel, and otherwise reads
`<posture>-PARTIAL (<n>/17 lanes; missing: …)`. Measured 2026-09-14: the posture line this section
used to derive checked only that one Claude and one Codex lane ran — so a run with no consolidator,
no panel and no classifier printed `posture: conjugal-standard`, and a filing went out under that
label with 16 findings the full posture later cut to 6 + 1.

Cross-family validation is a **separate** claim from posture completeness, and a run may make it
**only if at least one Claude lane and at least one Codex lane both cleared the sentinel.** Intent does not count, dispatch does not count, and a
lane that returned an auth error does not count. This project has already published one review
as `rubric_id: cross-family-validated` when no Codex process ran in its workspace at all; the
retraction is in the bus's RECEIPTS under 2026-09-13. A posture line that a human types is a
claim, and the same line computed from sentinels is a measurement — write the measurement.

**Write this file whether or not the lanes agreed, and whether or not the findings are
severe.** The findings are the product. A gate that records nothing unless the review came back
clean is a gate that deletes its own reason to exist — and it is the documented
conformance-fixpoint failure (`fleet-orchestrator-execute-posture.md` §1): perfect governance,
zero motion, every instrument green. Disagreement is recorded as disagreement, not as silence.

## 4. Land it

```bash
git -C "$REPO" checkout -b review/<PROJECT>-<date>
git -C "$REPO" add adjudications/approach-a-design/<PROJECT>.md
# append a RECEIPTS.md row; create the file with a header if it does not exist
git -C "$REPO" commit -m "cross-family review: <SUBJECT> (<n> findings, <posture>)"
git -C "$REPO" push -u origin review/<PROJECT>-<date>
test "$(git -C "$REPO" ls-remote origin refs/heads/review/<PROJECT>-<date> | cut -f1)" \
   = "$(git -C "$REPO" rev-parse review/<PROJECT>-<date>)" && echo PUSHED || echo PUSH-FAILED
```

Commit to a branch and **push that branch, without asking** (RULINGS **R7**, owner ruling
2026-09-14): a filing exists to be analysed by another project, and a local-only branch cannot be.
The push is complete only when `ls-remote` returns the local tip's SHA; otherwise the run is
`PUSH-FAILED`, not done. The grant is narrow: **never push to or merge into master, never
force-push** — the run is still unratified by construction. The bus is public: push the filing
and its RECEIPTS row only, never the raw lane outputs or prompts (Law 4).

If the checkout that holds `master` is shared, create the branch in its own worktree
(`git worktree add -b review/<PROJECT>-<date> <dir> master`) rather than switching the shared
checkout's branch under another session.

## 4b. Leave the bus synced — every time you touch it (RULINGS R8)

Your work with the doctrine repo is not finished until the shared checkout, `origin`, and your own
branches agree. Run this after every bus write — a review branch, a doctrine edit, anything:

```bash
git -C "$REPO" fetch origin
git -C "$REPO" status -sb | head -1          # shared checkout: expect "## master...origin/master" with no [behind N]/[ahead N]
git -C "$REPO" merge --ff-only origin/master # bring the shared checkout level; never reset/force/clean
git -C "$REPO" branch -vv --list 'review/*'  # every review branch: tracking origin, no [ahead N]
git -C "$REPO" worktree list                 # remove YOUR worktrees whose branch is pushed and clean
```

Doctrine edits to `master` follow the same shape: make them in a worktree detached at a freshly
fetched `origin/master`, push, verify with `ls-remote`, then fast-forward the shared checkout and
remove the worktree. A rejected (non-fast-forward) push means someone landed first — fetch, rebase
your commit onto `origin/master`, re-run any tests, push again. Never force.

Report it as one line: `bus: shared=<sha> origin=<sha> behind=0 ahead=0 review=<branch>@<sha> pushed worktrees-removed=<n>`.
Any non-zero `behind`/`ahead`, or an untracked file that blocks the fast-forward, is reported by
name, not smoothed over — and an untracked file another session left is theirs: never delete it.

## 5. Report

State: the tool's `posture:` and `cross_family:` lines verbatim, the per-role lane counts, per-lane
rc **and** bytes, the panel composite with seats and families scored, the classifier's STOPPING and
must-fix consensus, findings count (design / Untested / contradictions / losers), the adjudication
path, the branch name **and the remote SHA `ls-remote` returned** (or `PUSH-FAILED` with the error),
and anything a lane refused to do. If a lane came back empty, say which and say that its slice went
unreviewed — do not present four lanes as five, and never present a PARTIAL posture by its name.
Close with the §4b sync line.

---

**Authority:** `dispatch-trigger-standard.md` (routing, neither-family FAIL),
`posture-templates-conjugal-standard.md` (roles, disjoint slices, cross-family lint),
`tools/review-posture/` (roles as data, runner, scoring, consensus, posture measurement — tested),
RULINGS **R7** (push review branches), **R8** (leave the bus synced), **R9** (a posture is named only when complete),
`machine-inventory-schema.md` (availability), `cli-orchestration-standard.md` (invocation forms,
capture, model ids — PROPOSED, not ratified).
