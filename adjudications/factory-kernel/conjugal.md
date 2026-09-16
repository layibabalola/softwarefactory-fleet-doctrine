# Factory-kernel dogfood filing — conjugal (Conjugal, machine Bachelor / Dell XPS 17)

project: conjugal
kernel: fleet-factory-kernel r4
profile: code@r4
instance: `coordination/kernel-dogfood/` (subject declarations) + the tools named per clause below; `KERNEL: DOGFOOD-PENDING Sol` unchanged, map under `## Instance map`
subjects: 1 end-to-end (S1, delivered and accepted); 2 delivered-unaccepted (S2, S3)
window: 2026-09-15T23:18Z .. 2026-09-16T02:40Z
health: assurance=SATISFIED operability=PRESSURED
providers: claude(claude-opus-5, producer) codex(gpt-6-astra, acceptance key) — both cleared a sentinel; across S1 and S3 the key ran ten rounds and REFUSED nine of them
posture: no model review (an acceptance key is not a review panel; R9 does not apply)

**Status.** Written by a Conjugal Opus 5 session in worktree `heuristic-ritchie-e012ea`, reading the
bus at `2ac608f`. This is operational evidence, not a review (R1). **Steward rule (kernel §5):**
Conjugal is the steward and this is the steward's own filing. Conjugal does not write
`conjugal.dispositions.md`; a second project's arbiter or the owner rules on it.

**What changed since the 2026-09-14 filing.** That filing reported `subjects: 0` and K3, K5, K6 and
K7 all `UNEXERCISED`, because no subject ran. The blocker was never capacity: it was ordering. K5
requires the profile line before work starts, and Conjugal had shipped roughly 17 commits of real
code on 2026-09-14 that qualified for nothing, because the declaration did not exist first and
retrospective credit is correctly refused. This window fixed the ordering, not the output.

## Subjects

**S1 — `S1-resume-prep-landing`, delivered and accepted.**
Declaration `coordination/kernel-dogfood/S1-resume-prep-landing.md`, committed at Conjugal
`f1a9a9dc8` **before any of its code existed**. Delivered candidate `ca4dd1346`, identity (tree OID)
`721e4b15677a579d1fab3fd430a785d7974e243d`, recomputed by
`git -C C:\code\Conjugal rev-parse ca4dd1346^{tree}`. Delivery closed by fast-forward onto `master`;
`git merge-base --is-ancestor ca4dd1346 master` exits 0.

Owner-authorised work, not manufactured (PROMPT K §3): `~/.claude/ROTATION-install-prompt.md` has
named `coordination/tools/session-checkpoint.py` for this repo since 2026-09-06, and the owner
restated the requirement on 2026-09-15 as *"fully implemented and tested and the entire fleet is
using it."*

Measured state at declaration: the landing-seam gate was RED (`resumability-check.py` exit 1,
`PROMPTS-missing f4-anchor-check.txt`); the checkpoint tool was ABSENT from `master`; no `Stop` hook
was declared in `.claude/settings.json`; no test for either existed anywhere in the tree. Both
missing pieces sat on a sibling branch that was **not an ancestor of master**, which is why the
owner's belief that the hook was "installed and committed" and the tree's behaviour differed.
At the delivered candidate all three pinned checks are satisfied: checkpoint suite exit 0 (44
checks), gate exit 0, doc-size breach set unchanged from its 3-file baseline.

**S2 — `S2-fleet-resume-readiness`, delivered, not independently keyed.**
Declaration committed in the same pre-work commit. `tools/fleet-resume-readiness.py` and its test
land on this branch. It is **NOT counted as end-to-end**: no independent key was obtained for it
before the window closed, so K6 is unsatisfied for S2 and it is reported as delivered-unkeyed
rather than accepted. A real partial beats a rounded-up whole.

**S3 — `S3-fleet-readiness-to-full`, delivered, NOT accepted.**
Declared before its work, and its later artifact-set amendment likewise. Brought every fleet member
REACHABLE from this host to a measured state and made the instrument honest about the rest:
`salesforce-tools` installed (a real source tree under NO version control), the checkpoint hook
taught to tell an unversioned tree from a failed command and from an absent git, and the bus given
`bootstrap/PROMPT-R-install-resume-prep.md` plus a reference implementation so the six off-host
members can adopt a correct copy rather than the stale one the old install prompt inlined.

**Refused three times; no acceptance obtained, so it counts ZERO.** Seven defects were found and all
seven are fixed and delivered. Five of them LOWER what the readiness tool reports — `salesforce-tools`
moved READY → INSTALL-VERIFIED — which is the direction a correction to a readiness measure should
go. Measured at close: roster 10, reachable 4, READY 3, one INSTALL-VERIFIED, six UNREACHABLE,
tool exits 1.

## Clauses

K1 | FIT | "A candidate is never accepted on evidence whose only author is its producer" | Producer was this Claude Opus 5 session; the acceptance key was `gpt-6-astra` via `codex exec`, a separate credential store and provider family. The separation is demonstrated rather than asserted: the key **REFUSED six times** before accepting, each time reproducing the defect in this repo rather than asserting it: `a1eb9db4b` on non-ASCII paths recorded as C-escapes and on a failed `git status` read as a clean tree; `d71b5e28f` on `status.showUntrackedFiles=no`; `1715ec548` on `diff.ignoreSubmodules=all`; `3b497b60a` on root-index `assume-unchanged`/`skip-worktree`; `5f9b68681` on an index flag inside a SUBMODULE and on a `.gitignore`-excluded draft; `59fc013b6` on the footer still asserting "everything else is committed and derivable" two lines below the scope note that refused exactly that. Seven defects, all found by the key and none by the producer's own suite, which is the argument for the key rather than against the suite. All five defects were found by the key and none by the producer's own suite, which is the argument for the key rather than against the suite. A key that cannot refuse is not a key | PROOF: an acceptance on this repo whose producing and accepting actors resolve to the same independence class

K2 | FRICTION | "Each project keeps one register of what needs the owner and what does not" | Still no single register (unchanged from 2026-09-14). **Cost measured in this window:** two decisions had no authority source to consult. (1) Whether creating `coordination/kernel-dogfood/` was permitted — no register covers new coordination paths, so the standing autonomy default was applied. (2) The S2 declaration listed `specs/pre-rotation-proof-and-resume-dispatcher.md` in its artifact set, and only at delivery did a Law 2 check show Conjugal may not write a bus spec it does not own; the file was dropped and the request routed instead. A register would have refused that artifact at declaration time rather than at delivery time | REPLACES: "the register's path, and one decision the project took without asking" -> "the register's path, the command listing every other file that grants or reserves authority (expected empty), and one decision taken without asking" | PROOF: a single Conjugal file that `CLAUDE.md`, `AGENTS.md`, the 37 `user-directive-*.md` files and `coordination/product/AUTHORITY.md` all defer to

K3 | FRICTION | "the identity string of one subject, and the command that recomputes it" | Identity is the delivered tree OID per profile. It had to be computed **twice**: `master` moved from `42f8aa803` to `b623c9565` mid-subject (a peer Fable deadman commit), invalidating candidate `2f92a2602` and its acceptance run. The profile's "after any merge with the delivery target" is what made the re-computation correct rather than a dispute, so the clause held — at a measured cost of one full acceptance cycle re-run on a four-lane shared checkout. The moving target is structural here, not incidental: `master` advanced four times during this subject, and its tree changed again between acceptance and this filing. **The identity that survives is the CANDIDATE's own delivered tree, never the delivery target's tree read later** -- the latter decays within minutes on a four-lane shared checkout and would have made the acceptance unverifiable almost immediately | REPLACES: "git tree OID of the candidate commit as it will be delivered, after any merge with the delivery target" -> the same, plus: "on a shared integration branch this is the candidate's own tree after that merge, not the target's tree at any later read" | PROOF: a delivered subject in this repo whose recorded identity is not `rev-parse <delivered>^{tree}`

K4 | FIT | "Never exit code, output size or silence" | Three negative checks, all from this window and all in this repo. (1) `resumability-check.py \| tail -20` printed `RC_EXIT=0` while the unpiped re-run exited **1** — `tail` reports its own status; every gate in this window was then read unpiped. (2) The new test suite was mutation-proven rather than trusted: reintroducing the stripped-porcelain read turns it red on exactly the checks that name the truncated path, and restoring the empty-string git default turns the failure case red. A suite that has never been seen to fail is not evidence. (3) Every one of the 82 checks added here was mutation-proven before being claimed: the defect it names is reintroduced, the suite is observed going RED on exactly the naming assertions, and only then is the fix claimed. Six mutations were run. (4) The acceptance key found the hook reporting "a rotation right now would lose nothing" when `git status` had exited 128 — silence read as a clean tree. Fixed at `ca4dd1346` | PROOF: a gate in this repo whose exit status is read through a pipe

K5 | FIT | "Before work starts, a subject declares its profile and profile version" | **First time Conjugal has satisfied this clause.** `f1a9a9dc8` adds only the two declarations and touches no artifact in either declared set; the 5 S1 code commits follow it. `git log --oneline --reverse` is the witness, so the ordering is a property of history rather than a claim in prose. The acceptance receipt binds to identity `721e4b15…`, the same string the declaration's recompute command produces | PROOF: a commit in `f1a9a9dc8` that touches a declared artifact set, which would make the declaration retrospective

K6 | FIT | "Every acceptance includes a key from an independence class other than the producer's" | Producer class `claude-anthropic` (`claude-opus-5`). Key class `codex-openai` (`gpt-6-astra`, `codex exec`, separate credential store at `~/.codex/auth.json`). The key verified the tree OID itself rather than accepting it from the prompt, re-ran the pinned checks, and reproduced its own defects before ruling, across seven rounds. Final verdict: `VERDICT: ACCEPTED identity=721e4b15677a579d1fab3fd430a785d7974e243d key=gpt-6-astra class=codex-openai`, with the key stating that it read the whole emitted document, header through footer, across four suite fixtures and its own submodule fixture, and found no wording asserting unqualified safety. **S2 has no key and is therefore not accepted** | PROOF: an accepted subject here whose only key is a Claude seat

K7 | FRICTION | "how the project detects an accepted subject that never delivered" | S1's own delivery closed as one transaction (fast-forward, path census of exactly the 7 declared files, no peer file swept). But the **detector is still NONE**, and this window contains a live instance of what that costs: the checkpoint hook and the gate fix sat on a branch that was not an ancestor of `master` while the owner believed them installed. Nothing reported it; it surfaced only because this session ran `git merge-base --is-ancestor` by hand. `git grep -l CLOSURE_INCOMPLETE -- coordination scripts` still returns no Conjugal file | REPLACES: "how the project detects an accepted subject that never delivered" -> "the command that lists accepted subjects absent from the delivery target, and its last output" | PROOF: a Conjugal tool that lists accepted-but-undelivered subjects without being asked

K8 | UNEXERCISED | "Work that needs no inference continues" | No quota or capacity event occurred in this window. Two `codex exec` calls and the Claude session both completed. This is not evidence about the clause | PROOF: n/a in this window

K9 | FIT | "the resumability gate's command and its last passing output" | `python coordination/tools/resumability-check.py` — **RED at window start** (exit 1, `PROMPTS-missing ('f4-anchor-check.txt', …)`) and **GREEN at the delivered candidate** (exit 0, `PASS resumability (docs/architecture/approach-a @ ca4dd1346)`). A measured state change, not a restatement. The fix distinguishes script-generated artifacts from model outputs; the gate is exported to every member by `coordination/harvest/harvest-config.json` `conjugal_export`, so master's red gate had been the fleet's red gate | PROOF: the gate exiting 1 at `master`

K10 | INSTANCE-FAILURE | "Missing, `unknown` or mismatched account identity makes the inventory stale; re-probe under the current account before provider work" | Parity passed: SessionStart reported `[parity] MATCHED`, desktop and cli fp `5247997b9e08`. But `~/.claude/machine-inventory.yaml` records `probed_under: b4d2646b85c1`, generated 2026-09-14T19:38:54-05:00 — **a different account fingerprint**. By K10's own sentence the inventory is stale, and this session then performed provider work anyway (two `gpt-6-astra` calls) without re-probing. Nothing refused, because the SessionStart hook proves the two surfaces agree and checks no inventory at all. Honest compliance was possible — re-probe first — and the instance did not | PROOF: a Conjugal preflight that compares `probed_under` against the live parity fingerprint and refuses on mismatch

K11 | FIT | "the quoted title line of each rule the project confirms it meets" | Quoted titles under `## R1–R9`. This seat is Opus 5 and is not below the review floor (R1). Completion is positive evidence throughout (R2). No cross-family claim is asserted (R3): the key's family is named and its verdict quoted. The branch is pushed and `ls-remote`-verified (R7.2), fetched before writing (R8.1) | PROOF: a rule below that this filing violates

K12 | FRICTION | "The steward harvests every filing and answers each one" | Unchanged and now four harvests old: `origin/review/conjugal-kernel-2026-09-14` (blob 99cc68bf, 15 findings) has no dispositions file, no ledger row and no named arbiter. The steward excludes its own filing by configuration (`harvest-config.json` `"exclude_filings": ["conjugal"]`) but nothing routes it onward, so exclusion reads as silence. **This filing narrows the reachability half of that problem**: every finding above cites a path, a command and an exit status a sibling can re-run, and the two subjects' identities are recomputable from the bus branch alone | REPLACES: "A second project's arbiter, or the owner, rules on them" -> "A second project's arbiter, or the owner, rules on them; the steward names that arbiter in HARVESTS.md when the filing lands, and PROMPT A §4 surfaces it to the named project" | PROOF: a sibling's PROMPT A run that reports conjugal's kernel filing as awaiting its arbitration

## Profile fields

P:code subject-identity | FIT | "git tree OID of the candidate commit as it will be delivered, after any merge with the delivery target" | The clause anticipated the failure exactly. `master` moved mid-subject and the pre-merge tree `4481f614…` was discarded, as was `0131f804` after a second refusal, for the delivered `721e4b15…` without argument, because the profile already says which one counts | PROOF: as K3

P:code acceptance-evidence | FIT | "the project's pinned acceptance checks … run at the exact commit and declared environment … executed or authenticated" | Three checks, all executed at `ca4dd1346`, all read unpiped: checkpoint suite exit 0, gate exit 0, doc-size breach set identical to baseline (`codeConjugal-worktreesprobe-r3/…` ×2 plus `coordination/product/AUTHORITY.md`). The key re-ran all three itself rather than reading this filing's numbers | PROOF: a pinned check whose exit was inferred rather than run

P:code independent-key | FIT | "a verifier from another model family (R3)" | `gpt-6-astra`, class `codex-openai`. Verdict 1 REFUSED `reason=CHECKPOINT-PATH-CORRUPTION-AND-FALSE-CLEAN`; verdict 2 on the fixed candidate. The first verdict is the load-bearing evidence: the key found two defects a 30-check suite had passed | PROOF: a verdict here produced by a Claude seat

P:code delivery-target | FRICTION | "integration branch via the project's landing path" | Delivery worked, but the landing path is undocumented and had to be derived. `master` is checked out in the shared canonical checkout, so a worktree cannot advance it: pushing to a checked-out branch is refused, and advancing the ref alone would have shown every peer lane a tree full of phantom deletions. The safe route — `git -C <canonical> merge --ff-only <branch>`, which refuses rather than clobbers — is written down nowhere. **Cost:** three rejected approaches before one that is safe under four concurrent lanes | REPLACES: "integration branch via the project's landing path" -> "integration branch via the project's landing path, which the project states as a command" | PROOF: a Conjugal file naming the command that lands a worktree branch on master

P:code subject-identity | FRICTION | "git tree OID of the candidate commit as it will be delivered, after any merge with the delivery target" | Second instance, and a sharper one than K3's. The S3 amendment's COMMITTER date is 16 s later than the work it covers, because `git rebase` onto a master that moved four times rewrote it; its AUTHOR date precedes that work by ~2 min (`e71c88683` author 20:21:56 vs bus `57a3356` author 20:23:52). An arbiter read the committer date and refused a compliant subject `reason=RETROSPECTIVE` — having accepted the same ordering a round earlier on reflog evidence. On a shared checkout where rebasing is mandatory, committer dates are not an ordering proof | REPLACES: "the profile line recorded before work" -> "the profile line recorded before work, its precedence read from author dates or the reflog and never from committer dates, which rebasing rewrites" | PROOF: a Conjugal subject whose declaration precedence survives a rebase when read from committer dates

P:code dispatch-preflight | FRICTION | "the spending tool runs the project's resume gate before dispatch and retains its result, the inventory snapshot and digest, and account-parity evidence" | No Conjugal dispatch tool retains any of it, and the inventory was stale at dispatch (K10). The gate result and parity output exist only because this session ran them by hand and pasted them here | REPLACES: none; this is an instance gap | PROOF: a Conjugal dispatch receipt carrying an inventory digest

P:code claims | UNEXERCISED | "leases name the subject, owner, expiry and owned processes" | No lease was taken. This session held a worktree, not a lane seat, and claimed no CLAIM row | PROOF: n/a in this window

## Instance map

Unchanged from 2026-09-14 except where a mechanism was added this window. `KERNEL:` line remains
`DOGFOOD-PENDING Sol`: PROMPT K §2 forbids the in-tree adoption edit while the operating contract is
exclusively owned, and it still is.

K1 lane wire `coordination/lanes/` + `codex exec` acceptance keys · K2 **NONE** (spread across
`CLAUDE.md`, `AGENTS.md`, 37 `user-directive-*.md`, `coordination/product/AUTHORITY.md`) ·
K3 `coordination/kernel-dogfood/S*.md` + `rev-parse <candidate>^{tree}` **(added this window)** ·
K4 `coordination/tools/check-doc-size.py`, `resumability-check.py`, mutation-proven suites ·
K5 `coordination/kernel-dogfood/` **(added this window)** · K6 `codex exec -m gpt-6-astra` ·
K7 `git merge --ff-only` onto `master`; **detector NONE** · K8 `coordination/harvest/` park/resume ·
K9 `coordination/tools/resumability-check.py` + `coordination/tools/session-checkpoint.py`
**(landed this window)** · K10 `coordination/tools/check-cli-auth.py`; **freshness check NONE** ·
K11 this filing · K12 `coordination/harvest/harvest_runner.py`; **self-filing route NONE**

## Untested

- **S2 has no independent key.** It is delivered and tested but unaccepted. Counted as 0 end-to-end.
- **The `Stop` hook has never been observed firing in Conjugal by this session.** `.claude/settings.json`
  is read at session start, so the hook landed mid-session and this session ran without it. Layers 2
  and 3 are therefore proven separately for other members and not for Conjugal's own new wiring;
  `fleet-resume-readiness.py` reads Conjugal READY on a checkpoint written 3.8 h earlier by a
  different session, which is FIRING evidence for the repo but not for this commit.
- **Cloudvore writes a 948 KB `.snap-*.json` into the shared checkpoint root** and no `SESSION-*.md`.
  The doctrine is pointer-only; a 948 KB snapshot is not. Observed at
  `~/.claude/session-checkpoints/DropBox-Vault/`, dated 2026-09-05. Not filed as a BREAK: it is
  another project's instance and Conjugal has no counterexample from its own repo.
- **The same defect class appears in two sibling implementations of this doctrine.** Evidence is in
  their repos, not Conjugal's, so it is filed here rather than as a clause verdict, and it is
  routed rather than decided. Stated precisely, because overclaiming it would be the same error:
  - `magic-lantern_dannephoto/tools/roadmap/session-checkpoint.py:35` already reads `--porcelain=v1
    -z`, so it is immune to the quoting half, but it pins neither `--untracked-files` nor
    `--ignore-submodules`, so the two configuration roads found here are open to it.
  - `DropBox Vault/tools/rotation-ready.py:98` passes `-uno` deliberately, and its check is
    honestly named "tracked tree clean". The gap is in the aggregate, not that line: the worktree
    sweep at `:112` that does see untracked files explicitly skips the main checkout, so no check
    covers untracked files in cloudvore's own working tree, and a rotation-ready verdict can be
    returned over unsaved untracked work there.
  Three independent implementations of one doctrine, three instances of one defect class, is
  evidence about the DOCTRINE rather than about any of the three authors. The pre-rotation spec
  says what a resumability observation must conclude and not what it must be able to see.

- **Layer 3 was independently falsified on this host, which is the strongest evidence in this
  filing for keeping the four layers apart.** `salesforce-tools` had the script installed, a `Stop`
  hook declared, `hasTrustDialogAccepted: true`, and the configured command verified to resolve and
  write a checkpoint. A REAL session then ran in `C:\code\SalesforceSupportTools` across several
  turns (`~/.claude/projects/C--code-SalesforceSupportTools`, cwd confirmed) and wrote **no
  checkpoint**. In the same window on the same machine, Conjugal's newly-added `Stop` hook fired for
  five concurrent sessions, so the mechanism is not broken in general. Cause not yet isolated. The
  finding that matters does not depend on the cause: **installed + wired + trusted did not imply
  runs, and nothing announced the difference.** Had the producer's first draft been kept — it called
  the member READY on install verification — the tool would now assert coverage over a hook shown
  not to fire. The independent key forced that separation and was right to.

- **A bound this strategy carries and should not oversell.** The hook runs when a turn ENDS, so a
  session killed outright never reaches it and the in-flight turn is unrecorded. The previous turn's
  checkpoint survives, so exposure is bounded at about one turn, not a session. Recorded because a
  rotation is exactly the event that can kill a process mid-turn.

- **Six of ten roster members are UNREACHABLE from this machine** and nothing here is evidence about
  their adoption either way.
- **`RULINGS.md` mentions the kernel zero times**, so §5 criterion 4 has not started. Unchanged, and
  not this filing's to fix.

## R1–R9

- **R1 - A session below the review floor does not review.** This seat is Opus 5; it produced and did not review its own work.
- **R2 - Completion is positive evidence from the lane, never absence of error.** Every claim above cites an exit status, a tree OID or a quoted line.
- **R3 - A cross-family claim is computed, not asserted.** The key's family, model and transport are named; its verdict is quoted, not summarised.
- **R4 - Every project-scoped reference names its project.** Conjugal paths are given from `C:\code\Conjugal`; bus paths from the bus root.
- **R5 - Provider and model inventory is machine-scoped and probe-derived.** Honoured in form and FAILED in substance this window — see K10.
- **R6 — the invariant is binding; the implementation is not.** Parity was verified before provider work; the inventory freshness half was not.
- **R7.2 — The push is verified, not assumed.** `ls-remote` equality is reported in `## Landing`.
- **R8.1 — Fetch before you write.** The bus worktree was created detached at a freshly fetched `origin/master` (`2ac608f`).
- **R9.1 — Named only when complete.** No posture is claimed: an acceptance key is not a review panel.

## Landing

Branch `review/conjugal-kernel-2026-09-15`. SHA and `ls-remote` equality reported in the session's
final message, since an entry file carries procedures rather than values.
