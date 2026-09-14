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
cat .claude/doctrine-sync.json \
  || cat "$HOME/.claude/doctrine-sync/$(basename "$REPO").json"   # out-of-tree receipt, PROMPT A §2b
```
Require `status: "SYNCED"` and a `synced_at` within the last 24 hours. **Absence of this file
is a FAIL, not a pass** — it means the sync never ran, which is indistinguishable from a stale
doctrine unless you insist on the receipt.

```bash
python "<doctrine>/tools/check-account-parity.py"   # Claude family (there is no check-cli-auth.py)
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

### 1b. Self-heal preflight — what the environment actually is, and what was repaired to get there

Some environment faults are recoverable and the tooling repairs them; a repair that is not
*recorded* is indistinguishable from a machine that never had the fault, and the next run on a
different box inherits a conclusion that was never true there. So before routing:

- **Run the tooling's own environment check** and read `$RP_OUT/environment.json` — bash path and
  version, uname, host, python, the **resolved invocation and version for each CLI family**,
  whether the path contains a space, effective `core.autocrlf` in `RP_BENCH` and `RP_REPO`, bench
  HEAD, subject blob sha, the git worktree layout of each tree (`--git-common-dir` /
  `--show-toplevel`, and whether it is a linked worktree), the **per-lane dispatch record**, the
  inventory file it came from and that inventory's `probed_under`, and the repairs applied.
- **Read the dispatch record as four separate facts, because it records four.** `lanes[]` in
  `environment.json` carries `planned`, `dispatched`, `retried` and `completed_with_sentinel`
  per lane, plus `model_planned`, the models actually launched, and the timestamped events
  behind them (`dispatch-events.tsv` in `RP_OUT`). `planned` is roles.json — it is true of every
  lane in a dry run, in a blocked stage, and in a family whose CLI never resolved. Only
  `dispatched` means a process was launched, and only `completed_with_sentinel` means the lane
  answered. **Never attribute a finding to a model on the strength of `planned`.** An earlier
  version of this file published a single `models_dispatched` list built by walking roles.json,
  so every lane read as dispatched at its planned model whether or not anything ran.
- **Read the inventory's `repairs:` list** as well — a repair applied while probing the machine
  and a repair applied during this run are different events, and the filing needs both.
- **A family marked unavailable must carry a cause.** `available: false` with no fault code is
  not a measurement, it is an absence of one; treat it as UNKNOWN and re-probe rather than
  routing on it. A fault whose repair reports `verified=no` is *also* a named cause — say which.
- **A repaired run says so in the filing.** Every repair goes in `## Provenance`: what fault, what
  repair, verified or not. A run that needed a repair to happen at all is not the same evidence as
  a run on a clean box, and a reader who cannot tell them apart will generalise the wrong one.
- **A path containing a space is supported, not a caveat.** If a run from such a path behaves
  differently from one without, that is a defect in the tooling, not a constraint on the
  operator — report it rather than relocating the repo to work around it.
- **Run the offline gate before the first dispatch of a session on a new box:**
  `bash tools/review-posture/tests/run-tests.sh` (no network, no model calls, no credentials).
  It is the same command `tools/review-posture/README.md` names. If it fails, the environment is
  the finding; do not spend a provider call to rediscover it.

**Two distinctions this preflight exists to keep straight**, because a 2026-09-14 MLV-App report
blurred both:

- **SUBJECT vs BENCH are not interchangeable.** The posture reviews the **subject document**; the
  **bench** is the repo whose measured behaviour *grounds* findings about it. A finding says "this
  defect in the subject manifests here, on this bench, thus". So **replication means the same
  posture over the same subject blob — not the same findings.** Two benches that agree on every
  finding have told you something about the benches, not about the subject; two that disagree
  have not failed to replicate. Record the subject blob sha and the bench HEAD separately, and
  never describe a bench measurement as a property of the subject.
- **Cross-family unavailability is a DEGRADED posture with a named cause — never silently
  one-family.** If a family cannot be seated, the run continues only as an explicitly degraded
  posture that carries *why*: the fault code, the attempted repair, and its verification result.
  "We ran Claude lanes" is a description; "Codex unavailable: shim interpreter is a placeholder
  file, repair verified=no" is a cause. A one-family run whose filing does not name the cause is
  indistinguishable from a one-family machine, and that is how an auth-shaped symptom with a PATH
  cause survives into someone else's inventory.

**A DEGRADED posture needs a NEXT ACTION, not just a label.** Naming the cause tells the reader
what happened; it does not tell the operator what to do, and a filing that stops at the label
leaves the same box broken for the next run. One imperative per cause class — take it before
filing, and record which one you took:

| cause class | how you know | do this |
|---|---|---|
| **PATH / tooling fault** — `fault=shim-interpreter-not-executable`, `rc126`, `rc127`, `not-on-path`, `repair=unresolved` | `environment.json` `clis.<family>.fault` is set and `verified` is `no`; inventory says `CLI-NOT-MEASURED` | **Re-run `tools/probe-machine-inventory.sh` and read its `repairs:` block.** If self-heal now verifies the family, re-run the posture — this is a recoverable fault and a degraded filing over it is a wasted run. If it still does not verify, file DEGRADED naming the fault code and the rung that failed. Never re-file the same PATH fault as a capability statement. |
| **UNKNOWN provider-call failure** — CLI resolves and answers `--version`, every model challenge fails | inventory `unavailable_cause: "UNKNOWN-PROVIDER-CALL-FAILURE …"`, plus its `challenge_evidence:` block (per-model `rc`, `output_empty`, `output_bytes`, redacted first line) | **Do not call this an auth failure.** The probe collects no auth evidence — it never reads a credential and never calls a login-status surface — and this same shape comes from PATH-at-exec, network/proxy, a provider outage, a config or sandbox denial, or a retired model id. In order: **(1) re-run the probe** (a transient failure is indistinguishable from a persistent one on a single sample); **(2) then a READ-ONLY auth check** (`python tools/check-account-parity.py`; `codex login status` where it is not owner-gated) — and only if that check itself reports a problem may the filing say "auth"; **(3) then capacity/quota.** Read `challenge_evidence` before doing any of it: an `rc` of 126/127 with empty output is a launcher fault wearing this costume. Never run `claude auth login\|logout` or `codex login` yourself. If a re-auth does turn out to be needed, the owner does it, and you re-probe and record the new `probed_under` fingerprint — an inventory derived under a different identity is a stale file, not a capability. |
| **Capacity** — challenges succeed intermittently, or lanes return rate-limit/quota errors | lane `.log` files carry the provider's own limit message; `--version` is fine | **Either file an explicitly degraded posture with the capacity cause, or wait and re-run the whole posture.** Do not mix: a run half-completed before a limit and half after is not one measurement. State which you chose. |
| **Unmeasured** — `available: false` with no fault code, or a family absent from the inventory entirely | no `unavailable_cause`, no `repairs:` entry | **Re-probe.** An absence of a measurement is not a measurement; treat the family as unmeasured and route on nothing until the probe says something. |

The three classes the probe itself can distinguish, and nothing more: **PATH fault** (the CLI never
ran — repair the launcher); **CLI-resolved-but-challenge-failed** (`UNKNOWN-PROVIDER-CALL-FAILURE` —
re-probe, *then* a read-only auth check, *then* capacity); **verified** (the model answered the
sentinel and is dispatchable). "Auth" is not one of them, because nothing in the probe measures it.
**Never tell an operator "auth" unless something actually proved auth.**

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

`--retry-missing` re-dispatches only the lanes that did not clear the sentinel, such as one arbiter that degenerated into a loop and exited 0 (TRAPS, 2026-09-14), instead of re-running every seat. Disclose retries in the filing. It reuses the lanes it keeps, so it is bound by the same `bindings.env` check as `--from`: a `--retry-missing` run over a changed subject, bench or tool refuses before it re-dispatches anything.

`--from B|C|D` reuses earlier stages already in `RP_OUT`, and **the tool now checks that rather than
asking you to**. Every dispatched stage writes `bindings.env` (subject path and blob sha, bench HEAD
**and bench working-tree digest**, subject-repo HEAD **and working-tree digest**, rubric id and
rubric source blob, the git blobs of `run.sh` and `review_posture.py`, and which stages actually
dispatched); a `--from` run re-derives all of them
first and **refuses, naming each mismatch**, before it generates, clears or dispatches anything. A
missing `bindings.env` is equally a refusal — "no record" is not "match". There is **no override
flag**, deliberately: reuse over a changed subject would print a COMPLETE posture assembled from
lanes that reviewed a document that no longer exists. Still disclose the reuse in the filing.

**The working-tree digests are there because a HEAD is not a tree state.** An uncommitted edit to a
tracked bench file, or a new untracked file the lanes read, leaves `bench_head` byte-identical while
changing what was actually reviewed — so the digest covers the tracked diff vs HEAD plus every
untracked non-ignored file's content, and a refusal names **the tree and its path**, telling you the
difference is uncommitted rather than sending you to look at commits. The digest covers the index
too (`git diff --cached HEAD`), and it **fails closed**: if it cannot be computed the value is
`unknown`, and `unknown` on either side of a worktree, HEAD or blob binding is a refusal that says
`could not be computed` — never a match. An `RP_OUT` nested inside the tree is excluded. Both
digests are published in `environment.json` under `git.worktree_digest`, so a filing can state
whether it was measured against a clean tree.

**Ignored content is disclosed, not enforced — so quote the disclosure.** A live bench rewrites
ignored state on its own (this fleet's own heartbeat rewrites a snapshot every ten minutes), so
binding it would refuse nearly every legitimate reuse. Instead every accepted `--from` /
`--retry-missing` prints, records in `environment.json` (`invocation.reuse_disclosure`), and appends
to the posture line: `REUSE: stages <list> reused; ignored content NOT bound -- lanes may have cited
it`. **Carry that line into the filing verbatim whenever you quote a reused posture** — a reused
posture is not a pristine one, and the posture line is what a reader takes away.

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
## Provenance             (every lane: stage, model, rc, bytes, sentinel; environment.json digest; every repair
                          (fault, repair, verified); any SENTINEL_RETRY; reuse disclosed; what you did not re-measure)
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
git -C "$REPO" worktree list                 # remove YOUR worktrees whose branch is pushed and clean; never the detached read copy <checkout>-origin (PROMPT A §1)
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
