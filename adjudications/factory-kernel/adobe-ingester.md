# Factory-kernel dogfood filing - adobe-ingester (Adobe Document Cloud Ingester) - re-run, 2026-10-09

project: adobe-ingester
kernel: fleet-factory-kernel r4
profile: code@r4
instance: the four governed lanes of FACTORY.md (Sol hub/adjudicator and Luna implementer on Codex; Opus and Sonnet reviewers on Claude), ADOPT of kernel r4 / code@r4 recorded at HUB 2026-09-16T02:34Z; owner authority in .factory/prompts/sol.md OWNER DIRECTIVE entries
subjects: 0 end-to-end. Product work orders ran but none was accepted or delivered: WO-PROD-PDF-INTAKE-IMPORT-CLOSURE-013 rev2 (two valid Opus PASS_WITH_NONBLOCKING_FINDINGS, no countable Sonnet report, TIMEOUT_48H at HUB 2026-10-04T09:51:29.006Z); -014 rev1 (TIMEOUT_48H at HUB 2026-10-06T20:04:29.381Z, no reviewer report); -015 rev2 (REVIEWING, review order r4 opened HUB 2026-10-09T22:07:48.551Z). Not counted: WO-G0-A01 rev13, accepted 2026-09-23T09:58:44.307Z by direct owner ruling on reviews published before the kernel existed (no K5 declaration possible; materialized adobe:e3fcc1b)
window: 2026-09-17T19:34:05Z .. 2026-10-09T23:01:18Z
health: assurance=UNSATISFIED operability=PRESSURED
providers: openai (Sol and Luna lanes; e.g. contained Sol step receipt "completed, root exit 0" at HUB 2026-10-09T22:34:03.811Z), anthropic (Opus and Sonnet reviewer lanes; countable publications, e.g. Sonnet PASS_WITH_NONBLOCKING_FINDINGS and Opus FAIL in DISPOSITION WO-PROD-PDF-INTAKE-IMPORT-PROOF-012 rev2, HUB 2026-10-02T07:59:36.276Z)
posture: conjugal-standard-PARTIAL (0/17 lanes; missing: Designer-Scope 0/1; Designer-Verify 0/1; Lint-Consistency 0/2; Arbiter 0/1; Consolidator 0/1; Panel 0/8; Classifier 0/3); cross_family: NO-CROSS-FAMILY-VALIDATION. Computed: `python tools/review-posture/review_posture.py posture <new empty scratch dir>` from the bus root, Python 3.14.3, exit 1, tool sha256 6418F59D..., bus `git status --porcelain` 0 entries before and after. Model review contributed to the product work orders (Opus, Sonnet), outside every posture role.

**Drafted by the Claude auditor (chat session 040a9469), not a lane.** Reviewed by one adversarial different-family read-only falsifier (codex-cli 0.160.1,
gpt-5.6-sol high): PUBLISHABLE-WITH-CHANGES, 0 BLOCKER, 2 REQUIRED, both applied verbatim. Precedent: the 2026-09-17 filing (bus blob 5e285849) was drafted the same way.

Revisions. The instance adopted kernel r4 / code@r4 and its work orders declare `code@r4`; a later revision is "a new
decision, not an automatic upgrade" (sol.md lines 1894-1895). The bus is at kernel r5 (blob 6821c4c3, since bus:5d1d0d9,
2026-09-17T20:17:25Z) and code r10 (blob 5511ccb3). Clause quotes below are from those current texts. Two contradictions
on `specs/adobe-ingester.md` at bus origin/master (blob c66c2229): line 878 still reads `KERNEL: DOGFOOD-PENDING ·
kernel r4 · code@r4` and line 881 `ADOPT: not recorded`, while its 2026-09-25 MEASURED section records the HUB ADOPT;
and its 2026-09-20 addendum pins the r4 declaration to blob 6821c4c3, which is the **r5** text (the r4 blob is
79fc893c at bus:da4e920).

SHAs are project-qualified (R4): `adobe:` for this repo, `bus:` for the doctrine repo. HUB times are heading times.

## Clauses

K1 | INSTANCE-FAILURE | "Producer, verifier, adjudicator and owner are distinct roles." | all 1,622 HUB headings in the window are written by SOL. Sol produced and adjudicated control generation reviewer-dispatch-start-claim-v1: its edits were "preserved edits from the interrupted earlier Sol wake" with a Sol DESIGN block (HUB 2026-10-03T11:24:17.965Z), and Sol marked it CONSUMED at adobe:ddb657d (HUB 2026-10-03T22:37:25.742Z). A different-family key did exist (falsifier request 48 returned UNSAFE with two blocking findings, HUB 2026-10-03T17:48:00.851Z, remediated before consumption), so "only author" held; role separation did not. Compliance was possible here: Luna implements and Opus/Sonnet review governance work orders such as WO-GOV-REVIEWER-ADMISSION-AUTOMATION-001 | PROOF: a control generation whose bytes were written by Luna (or another non-adjudicator) and consumed by Sol
K2 | FRICTION | "A register entry beats a memory note, a charter or a handoff." | register: FACTORY.md plus OWNER DIRECTIVE entries in .factory/prompts/sol.md plus staged files in .claude-state/coordination/owner-directives/. Autonomous decision the register allowed: OWNER_ITEMs routed to the auditor under directive 30d, not the owner (7 headings say ROUTED, e.g. HUB 2026-10-01T16:40:46.192Z); owner-reserved presence (AC-07) was escalated (3 PRESENCE headings). Cost: 74 final OWNER-DIRECTIVE files in 22 days; distinct directive ids in sol.md rose from 38 (adobe:6051264) to 110 (adobe:2218c90); 64 DELIVERED and 4 OWNER_DIRECTIVE_REFUSED headings; 50 OWNER_ITEM headings. A consumed one-time grant never leaves the register | REPLACES: "A register entry beats a memory note, a charter or a handoff." -> "A register entry beats a memory note, a charter or a handoff. A one-time grant leaves the register once consumed, keeping a pointer to its record." | PROOF: a window where consumed grants are retired and the register read by every wake still grows with directive volume
K3 | INSTANCE-FAILURE | "One claimant holds a subject at a time" | WO-013 rev2 r5: a cadence invocation at 2026-10-03T09:04:54.712Z launched a second Sonnet model process after the first terminal receipt; the HUB root cause says "the runner mutex enforced only concurrent single-flight" with no durable per-dispatch start claim (heading HUB 2026-10-03T09:30:05.476Z, DUPLICATE START BREACH). The repair (durable start claim, adobe:ddb657d) then failed on its own store: WO-014 r1 TERMINAL REFUSAL, CLAIM-STORE INITIALIZATION FAILURE (HUB 2026-10-04T21:56:14.449Z). Identity half held: WO-013's pre-start entry names the recompute command `Get-FileHash` (HUB 2026-10-02T09:29:06.399Z) | PROOF: a second cadence invocation that reads the durable claim and does not start a model
K4 | FIT | "Never exit code, output size or silence." | negative checks this window: a Sonnet run that completed and proposed PASS_WITH_NONBLOCKING_FINDINGS was refused at strict publication admission and counted NOT_PUBLISHED (heading HUB 2026-09-26T23:36:29.211Z); the duplicate WO-013 Sonnet run's SUCCEEDED PASS was held NONCOUNTABLE (heading HUB 2026-10-03T09:30:05.476Z); 17 headings record a publication refusal or nonpublication. The cost of those refusals is the instance's publication grammar, not this clause | PROOF: a vote counted from a run whose report failed admission
K5 | UNEXERCISED | "Before work starts, a subject declares its profile and profile version." | no product subject reached acceptance, so the acceptance-receipt half has no instance. Exercised: `Profile: code@r4` existed before IMPLEMENTING on WO-013 (HUB pre-start 2026-10-02T09:29:06.399Z), WO-014 (in its creating commit adobe:03e2f26, 2026-10-04T17:47:41Z; IMPLEMENTING 17:55:49.950Z) and WO-015 (adobe:903e55d, 2026-10-06T20:59:29Z; IMPLEMENTING 22:28:03.572Z). Only WO-013 has a HUB pre-start entry with a recompute command. Resource stops were typed with zero credit: WO-013 TIMEOUT_48H despite two valid Opus PASS reports; WO-014 TIMEOUT_48H | PROOF: an acceptance receipt bound to the same identity as a pre-work profile line
K6 | UNEXERCISED | "Every acceptance includes a key from an independence class other than the producer's." | no acceptance. Keys were issued on product candidates: producer Luna (openai), keys Opus and Sonnet (anthropic). WO-013 rev2 held a valid cross-family Opus PASS (HUB 2026-10-02T19:59:34.223Z, and r5 per HUB 2026-10-04T09:51:29.006Z) and still timed out, because the instance requires both Claude reports. 8 DISPOSITION headings: Opus FAIL 7, BLOCKED_BY_MISSING_EVIDENCE 1; Sonnet FAIL 4, PASS_WITH_NONBLOCKING_FINDINGS 1, NOT_PUBLISHED 2, NOT_STARTED 1 | PROOF: an accepted subject whose receipt names each key's class
K7 | UNEXERCISED | "Acceptance and delivery are separate states." | no product subject accepted, so none could deliver. The one acceptance in the window (WO-G0-A01, pre-kernel) is recorded as "terminal local acceptance only. No integration" (HUB 2026-09-23T09:58:44.307Z); making it durable needed an empty temporary hooks directory after the unchanged hook path exceeded the 2,400 s Sol wall (HUB 2026-09-23T14:39:02.344Z) | PROOF: an accepted product subject and the record that detects it undelivered
K8 | FIT | "Reset events update capacity telemetry. They never open a gate by themselves." | last quota event: Q-039 rev2 parked QUOTA-DORMANT waiting for a named reset (HUB 2026-09-17T20:35:41.939Z, 2026-09-17T22:59:05.768Z); CAPACITY RESUMED did not open the gate, "SONNET START HELD" (HUB 2026-09-18T06:19:30.696Z); last quota-named heading HUB 2026-09-20T06:14:45.946Z. The prior filing's K8 INSTANCE-FAILURE (no dormant terminal) is cured; directive 2026-09-17e is the remedy | PROOF: a quota refusal followed by repeated failing wakes with no dormant terminal
K9 | FIT | "A fresh session on a new account, with empty memory, resumes from the project's tree and the bus alone." | every Sol wake resumes filesystem-first: 324 HUB body lines in the window begin `FILESYSTEM_FIRST`; interrupted-wake edits were recovered from the tree and acted on (HUB 2026-10-03T11:24:17.965Z). Gate and last passing output: contained step-1 governance PASS with receipt SHA-256 097A8332... (HUB 2026-10-09T22:34:03.811Z). Wake wall budgets rose in the same period; attributing them to resume cost is not established (## Untested) | PROOF: a wake that needed chat memory or an unrecorded handoff to continue
K10 | INSTANCE-FAILURE | "it records the account it was derived under." | provider work ran all window (reviewer dispatches; 17 headings name ACCOUNT checks) with no inventory recording `probed_under`. Sol's own adopt directive requires it ("probed_under must name the CURRENT account", sol.md line 1899). Search boundary: `rg probed_under` over `.factory/` matched only sol.md; over `.claude-state/tools/` matched nothing. The account-match gate is parity evidence, not an inventory | PROOF: an inventory file whose probed_under names the account a dispatched reviewer ran under
K11 | INSTANCE-FAILURE | "R1–R5, R7, R8 and R9 apply to every report a factory makes about itself" | R5 "Provider and model inventory is machine-scoped and probe-derived." is not met (see K10). R2 met (see K4). R9 met by this filing's computed posture line; the prior filing was flagged POSTURE-NOT-R9-COMPUTED. 76 SOL CORRECTION headings in the window record reports later corrected on the ledger, e.g. a dispatch age of 565 superseded by 265 minutes (HUB 2026-10-09T13:00:59.956Z). R7 and R8 bind at landing, which has not happened | PROOF: a probe-derived inventory, and a correction rate that falls
K12 | FRICTION | "never one blended score." | the observable now holds for the prior filing: `tools/harvest-status.py factory-kernel` shows adobe-ingester HARVESTED, blob 5e285849, 19 findings, dispositions bound. This project then filed nothing for 22 days (PROMPT K asks weekly). Cost: the ordered pair reads UNSATISFIED / PRESSURED both on 09-17 and now, and cannot show that 1,092 of 1,093 window commits touched `.factory/` and 16 touched `spikes/` (product), 0 of 225 in the last 72 h, 7.41 days since the last product commit. No kernel clause measures product versus control output. Same instrument proposed in bus `ruling-candidates/product-share-is-the-fixpoint-instrument-r1.md` (dng-auto-processor) | REPLACES: "never one blended score." -> "never one blended score. Each filing also reports product share: commits (or the profile's unit) touching a declared product path set, over all, beside an equal older window." | PROOF: a window where product share falls while assurance and operability both stay unchanged, and the harvest still cannot tell

## Profile lines

P:code subject-identity | FIT | "a key on a different subject identity does not transfer." | each review dispatch binds candidate_manifest_sha256 and reviewed_commit (state.yaml banked_review_dispatch_* blocks); WO-015 records "No WO-014 review publication is reusable"; WO-015 rev2 reopened its review order r1 to r4 rather than reuse keys | PROOF: a publication counted across differing manifest digests
P:code resource-terminals | FIT | "retain the stopped candidate's bytes and receipts before rollback" | WO-013 and WO-014 ended TIMEOUT_48H with "NO DISPOSITION" and zero credit; WO-015 names WO-014's "21-entry candidate" as its unaccepted baseline (.factory/work/WO-PROD-PDF-INTAKE-IMPORT-CLOSURE-015.md) | PROOF: a successor that re-implements because the stopped bytes were discarded
P:code claims | INSTANCE-FAILURE | "identifies the live holder rather than a short-lived claim-writing helper." | the WO-013 start allowance lived "only in process memory" of the runner, so a later cadence process could not see it (see K3) | PROOF: see K3
P:code independent-key | UNEXERCISED | "a CI runner the producer does not control" | `.github/workflows/release-validation.yml` (last changed adobe:66f5e6e, 2026-08-02) runs on push to main or pull request; the local remote-tracking ref origin/agent/software-factory-hardening is adobe:0afc246 and HEAD is 1,819 commits ahead (ref not fetched for this filing), so no window commit reached CI | PROOF: a CI run on a window product commit
P:code budgets | FIT | "plus window counts of subjects accepted, delivered, parked and closed undelivered" | product subjects in window: accepted 0, delivered 0, closed undelivered 2 (WO-013, WO-014 TIMEOUT_48H), in review 1 (WO-015 rev2); state.yaml acceptance_status values include 7 NOT_ACCEPTED_NO_INDEPENDENT_REVIEWS (banked reviews for earlier product orders); accepted-undelivered 0 | PROOF: a count above that state.yaml or HUB contradicts
P:code dispatch-preflight | INSTANCE-FAILURE | "retains its result, the inventory snapshot and digest, and account-parity evidence" | provider work ran throughout the window, but no dispatch-bound inventory recorded probed_under (K10); launcher diagnostics did survive ("Stdout SHA-256 ...; stderr empty", HUB 2026-10-09T22:34:03.811Z), with 455 HUB body lines mentioning stderr and 33 headings recording pin/CLI preflight refusals | PROOF: a dispatch-bound inventory snapshot whose probed_under names the account used by that reviewer

## Carry-forward (prior filing blob 5e285849; dispositions bus blob 435f9f12)

- §K1 REJECTED(unexercised): **exercised, failed** on a control generation (K1 above). Still unexercised for product subjects.
- §K2 ROUTED(adobe admission-grammar bench): **unchanged.** 4 OWNER_DIRECTIVE_REFUSED headings (2026-09-17F, 09-30E,
  10-05F, 10-07F) and 2 redelivery files (`...20260930e-redelivery2.md`, `...20261007f-redelivery.md`); the grammar is
  still checked by the reader, not machine-checked at staging.
- §K6 ROUTED(adobe alternate-key bench): **half resolved.** Ballot failures are now diagnosable from retained output (see
  P:code dispatch-preflight). No second qualified key backend: every reviewer key is Opus or Sonnet.
- §K9 ROUTED(adobe interrupted-effect bench): **exercised.** Wall-interrupted effects were recovered from preserved tree
  bytes (K9 above; HUB 2026-09-23T14:01:54.818Z "STAGED TRANSACTION PRESERVED", durable at 14:39:02.344Z). Supports
  the routing; no kernel text needed from this.
- §K10 REJECTED(unexercised): **exercised, failed** (K10 above).
- §K12 REJECTED(unexercised): **resolved.** HARVESTED with blob-bound dispositions.
- §P:code independent-key ROUTED: **unchanged** (line above).
- §Untested-1 product subject ROUTED: **partly exercised.** 15 product work orders appear in window headings; 16 commits
  touched `spikes/`; none accepted (subjects line).
- §Untested-2 Astra advisory ROUTED: **unchanged.** 11 ASTRA headings, last HUB 2026-09-27T02:40:51.655Z; 0 HUB lines in
  the window cite directive 2026-09-15d clause 6.
- HEADER POSTURE-NOT-R9-COMPUTED: **resolved** in this filing.
- Prior K4 (CRLF vote-line verifier): **not re-measured.** 1 HUB line in the window names ballot-owner-postpublication;
  no conclusion drawn.

## Instance pathology (MEASURED only)

**Control versus product.** Window: 1,093 commits; 1,092 touched `.factory/`; 16 touched `spikes/` (1.46 %). Older equal
window (2026-08-26T16:06:52Z .. 2026-09-17T19:34:05Z): 609 commits, 1 touched `spikes/`. Last 72 h: 225 commits, 0
product. Last 14 days: 14 product commits, all on or before adobe:581f3ee (2026-10-02T13:09:35Z), 7.41 days before window
end. `.claude-state/escalation/ESCALATION-CURRENT.md` (raised 2026-10-09T22:41:08Z) reports
`days_since_last_product_commit=7.4 (limit 7)`, consistent with git.

**Append-only directive remediation.** 74 final OWNER-DIRECTIVE files are dated in the window (72 named 2026-09-18 ..
10-09, plus 2026-09-17e and 09-17f), against 16 product commits; 18 are named 2026-10-07 .. 10-09, against 0 product
commits in the last 72 h. Each lands in sol.md and none leaves it:

| sol.md at | commit | bytes | distinct directive ids |
|---|---|---|---|
| 2026-09-17T17:03Z (pre-window) | adobe:6051264 | 190,926 | 38 |
| 2026-09-25T21:49Z | adobe:e09c690 | 237,527 | - |
| 2026-09-27T20:08Z | adobe:3e8c2bf | 272,590 | - |
| 2026-10-03T03:39Z | adobe:0f5e2a6 | 440,961 | - |
| 2026-10-07T11:14Z | adobe:192cc6f | 568,694 | - |
| 2026-10-09T17:39Z | adobe:2218c90 (last before window end) | 686,946 | 110 |

59 commits touched sol.md in the window.

**sol.md growth against WALL BUDGET.** Headings naming WALL BUDGET: 10 over 2026-09-17 .. 10-06 (20 calendar dates), 22 over
10-07 .. 10-09 (3 calendar dates: 10 on 10-07, 12 on 10-09). Across the window, 33 headings name TIMEOUT and 24 name HOST
CONTENDED or HOST LOAD. The rise co-occurs with sol.md above 568 KB; no control separates prompt size from host load,
so no cause is claimed.

**Review flow.** WO-015 rev2's review order was reopened twice on 2026-10-09 with no reviewer attempt (PRE-MODEL STALE
REOPEN, HUB 15:43:54.133Z and 22:05:36.796Z). WO-013 reached two valid Opus PASS reports and a noncountable duplicate
Sonnet PASS, then closed TIMEOUT_48H.

PROPOSAL (unratified): retire consumed one-time grants from sol.md behind a pointer (K2 REPLACES), and report product share in
the auditor's tick. Neither is a ruling; both are Sol-owned decisions for this instance.

## Untested

- **Opus and Sonnet as one independence class.** Kernel §1: "Two wrappers over one backend are one class." Both keys
  are anthropic models. If they are one class, this instance's second required key adds failure surface without
  independence; WO-013 is the measured cost. The kernel does not say whether two models on one provider are one class.
- **Control generations as kernel subjects.** K1 above treats one as a subject. If they are subjects, none of the 378
  CONTROL_GENERATION headings carries a K5 profile declaration. Not adjudicated here.
- **Wall budget from resume size.** K9's cost, if any, is unmeasured; the co-occurrence is in Instance pathology.
- **The bus spec's revision labels** (preamble): flagged for this project's own bus edit, not a kernel finding.

## Read receipt

- `specs/fleet-factory-kernel.md` (bus blob 6821c4c3, `CANDIDATE r5 — DOGFOODING`): "UNEXERCISED windows and quiet periods never count toward removal."
- `specs/fleet-factory-kernel/profiles/code.md` (blob 5511ccb3, r10): "Generated binaries are identified by the build receipt's output digests"
- `bootstrap/PROMPT-K-dogfood-kernel.md` (blob 4a78fde6): "Never create work so you have something to measure."
- Prior filing (blob 5e285849): "the product track has been frozen since 2026-09-07 behind a mechanical step."
- `adjudications/factory-kernel/adobe-ingester.dispositions.md` (blob 435f9f12): "Re-file after the grammar is machine-checked."
- `specs/adobe-ingester.md` (blob c66c2229), line 878: "KERNEL:   DOGFOOD-PENDING · kernel r4 · code@r4"
- `ruling-candidates/product-share-is-the-fixpoint-instrument-r1.md` (blob 3d501325): "Share is not a target."

## Re-derivation commands

Shell: PowerShell 7. `$r="C:\!Layi Wkspc\Adobe Document Cloud Ingester"`, `$b="C:\!Layi Wkspc\softwarefactory-fleet-doctrine"`,
`$s='2026-09-17T19:34:05Z'`, `$e='2026-10-09T23:01:18Z'`. Bus reads at origin/master bus:1342569 after `git -C $b fetch -q origin`.

- Commits: `git -C $r log HEAD --since=$s --until=$e --format=%H [-- spikes/ | -- .factory/] | Measure-Object`; 72 h uses
  `--since=2026-10-06T23:01:18Z`; older window `--since=2026-08-26T16:06:52Z --until=$s`; last product commit
  `git -C $r log HEAD -1 --format='%h %cI' -- spikes/`.
- HUB window headings (file has NUL bytes, so Select-String): `Select-String -Path $r\.factory\coordination\HUB.md -Pattern '^### \[(20\d\d-\d\d-\d\dT[^\]]+)\]'`,
  filtered to $s..$e by parsing group 1 (1,622 headings), then counted by regex: `WALL[ _-]BUDGET`, `TIMEOUT`,
  `HOST[ _-](CONTENDED|LOAD)`, `(?i)OWNER[ _]ITEM` (and `ROUTED`, `PRESENCE` within those), `(?i)OWNER[ _]DIRECTIVES?[ _]DELIVERED`,
  `OWNER_DIRECTIVE_REFUSED`, `CONTROL[ _]GENERATION`, `\] SOL — (LEDGER_)?CORRECTION`, `ASTRA`, `ACCOUNT`,
  `PUBLICATION REFUSAL|NONPUBLICATION|PUBLICATION_REFUSED|REVIEW_REFUSAL|TERMINAL REFUSAL`,
  `PIN DRIFT|PIN REFRESH|CLI-SERVICING|CLI-CURRENCY|EXECUTABLE PIN`, `\] SOL — DISPOSITION WO`; actor check `\] (SOL|sol) `.
- Verdict pairs: `Select-String HUB.md -Pattern '^opus:\s*(\S+)\s+sonnet:\s*(\S+)'` with LineNumber >= 32741, plus the
  disposition at heading 2026-09-28T11:53:27.009Z (Opus FAIL valid, Sonnet NOT_PUBLISHED). Body counts: `^FILESYSTEM_FIRST`, `stderr`, from line 32741.
- Directives: `Get-ChildItem $r\.claude-state\coordination\owner-directives -Filter 'OWNER-DIRECTIVE-*'`, date from
  `(\d{8})([a-z]?)\.md$`; sol.md ids: `git -C $r show <h>:.factory/prompts/sol.md | Select-String 'OWNER DIRECTIVE (2026-\d\d-\d\d[a-z]?)' -AllMatches`, unique, lower-cased.
- sol.md sizes: `git -C $r log --since=$s --until=$e --format='%h %cI' -- .factory/prompts/sol.md`, then `git -C $r cat-file -s <h>:.factory/prompts/sol.md`.
- Profile lines: `git -C $r log --reverse --format='%h %cI' -S 'Profile: `code@r4`' -- .factory/work/<WO>.md`.
- Acceptance status: `Select-String $r\.factory\state.yaml -Pattern '^\s+acceptance_status:\s*(\S+)'`, grouped.
- probed_under: `rg probed_under $r\.factory` and `$r\.claude-state\tools` (the search boundary).
- Posture and harvest: from `$b`, `python tools/review-posture/review_posture.py posture <empty dir>` and
  `python tools/harvest-status.py factory-kernel`; `git -C $b status --porcelain` before and after.
- Bus blobs: `git -C $b rev-parse origin/master:<path>`; r4 kernel blob `git -C $b rev-parse da4e920:specs/fleet-factory-kernel.md`.
