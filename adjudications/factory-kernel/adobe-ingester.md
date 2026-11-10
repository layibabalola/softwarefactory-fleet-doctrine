# Factory-kernel dogfood filing - adobe-ingester (Adobe Document Cloud Ingester) - re-run, 2026-11-10

project: adobe-ingester
kernel: fleet-factory-kernel r5
profile: code@r11
instance: NOT the governed-lane factory. That instance is PARKED: scheduled task AdobeIngesterFactory-SolExec has been Disabled since 2026-11-09T05:18Z (adobe:.claude-state/continuity/FACTORY-PARKED-20261109.md, machine-local), with branch agent/software-factory-hardening at adobe:abf45ab and no HUB heading after 2026-10-22T04:33:40Z. The instance measured here is the direct product route under the owner ruling of 2026-10-24: the Claude auditor session implements in the product repository layibabalola/adobe-document-cloud-ingester (clone adobe-ingester-split-session) and squash-merges each PR when it has a 3-seat review, a Codex falsifier SAFE on the final diff, targeted and full suites, and a live check if the PR touches the live path.
subjects: 3 accepted and delivered, all test-only, all in layibabalola/adobe-document-cloud-ingester:
- PR #31: head product:f51763ce, merged as product:a123e3fa at 2026-11-10T01:48:07Z.
- PR #32: head product:894bca57, merged as product:d32f36bf at 04:02:05Z.
- PR #33: head product:b33ce2b2, merged as product:05eb2c53 at 15:33:16Z.
window: 2026-11-09T05:18Z .. 2026-11-10T18:10Z
health: assurance=UNSATISFIED operability=PRESSURED
providers: anthropic (implementer and review seats, claude-opus-5-5, auditor session af70e674); openai (Codex CLI 0.160.1 falsifier, gpt-6.1-sol, sessions 01a1c307-3071-7312-b5ea-335bf10e034f, 01a1c388-9e17-7e33-acdf-999f84bc05a8, 01a1c5f8-2429-7a43-bbb1-5a70434191e9)
posture: conjugal-standard-PARTIAL (0/17 lanes; missing: Designer-Scope 0/1; Designer-Verify 0/1; Lint-Consistency 0/2; Arbiter 0/1; Consolidator 0/1; Panel 0/8; Classifier 0/3); cross_family: NO-CROSS-FAMILY-VALIDATION.
- Computed with `python tools/review-posture/review_posture.py posture <new empty scratch dir>` from bus:b194726, Python 3.14.3, exit 1. The tool's sha256 starts 6418F59D. Bus `git status --porcelain` showed 0 entries.
- Model review contributed to all three subjects (Claude seats and the Codex key) outside every posture role.

**Drafted by the Claude auditor, chat session af70e674, which is not a lane. No falsifier reviewed this filing.**

**Prefixes.** SHAs carry their project: `product:` is layibabalola/adobe-document-cloud-ingester, `adobe:` is the factory repository, `bus:` is this repository.

**Carry-forward.** `tools/harvest-status.py factory-kernel` shows every earlier adobe-ingester filing as HARVESTED (current blob efe2ed91), so no finding is left without a disposition, and none is carried.

**Why this instance changed.** The kernel itself did not cause the change. The parked instance's governance preflight was blocking its own repair; see Proposals P1.

## Instance map

| Clause | Mechanism in the direct route |
|---|---|
| K1 | Claude subagent seats; Codex falsifier (openai) |
| K2 | owner ruling 2026-10-24, kept in machine-local auto-memory `owner-ruling-auto-merge-product-prs.md` and the user CLAUDE.md. NONE in the product tree. |
| K3 | `gh pr merge --squash --match-head-commit <sha>`; the auditor lease in adobe:.claude-state/continuity/AUDITOR-HANDOFF-CURRENT.md |
| K4 | TRX files with sha256, and per-PR mutants |
| K5 | NONE: no pre-work profile line or contract digest per subject |
| K6 | Codex CLI 0.160.1, gpt-6.1-sol, read-only |
| K7 | squash merge to `main`; the 10-minute tick lists open PRs |
| K8 | rotation PREP and HOLD protocol (~/.claude/ROTATION.md) |
| K9 | adobe:.claude-state/RESUME.md, the handoff lease and auto-memory, all machine-local |
| K10 | NONE: no inventory records `probed_under` |
| K11 | merge records, with gate tables on the PR |
| K12 | this filing |

## Clauses

K1 | INSTANCE-FAILURE | "Producer, verifier, adjudicator and owner are distinct roles." | Session af70e674 was both producer and adjudicator: it wrote each change and decided each merge. The three review seats are subagents of that same session (claude-opus-5-5). The one key from a different actor is the Codex falsifier (openai). "Only author" therefore held, because Codex returned SAFE for #31 r1, #32 r7 and #33 r2; role separation did not. The owner's 2026-10-24 ruling authorises agent-landing. Compliance was still possible, because a second session or the owner could take the merge decision | PROOF: a delivered subject whose merge was decided by an actor other than its producer
K2 | FRICTION | "A register entry beats a memory note, a charter or a handoff." | The rule that let #33 merge without asking (the 2026-10-24 auto-merge ruling) exists only as a machine-local auto-memory note and in the user-scope CLAUDE.md. The product clone has neither CLAUDE.md nor AGENTS.md (Test-Path False, 2026-11-10). So for this instance the register is a memory note. Cost: a session started in the product checkout alone could not find its own authority. The incoming dedicated machines make this a migration item | REPLACES: "Each project keeps one register of what needs the owner and what does not." -> "Each project keeps one register of what needs the owner and what does not, inside every repository its instance writes to." | PROOF: an instance whose single tracked register sits in a sibling repository, with no session ever failing to find it
K3 | FIT | "A subject's identity is a content digest over its **declared artifact set**." | Each delivered tree equals its reviewed head tree, using profile code's sha256 of the tree OID text:
- #31: tree 841d18f0, id e98c2771...
- #32: tree 7d3ab457, id 83584f83...
- #33: tree 821281de, id 424f113d...

Recompute with `git rev-parse <merge>^{tree}`, then sha256 of the lowercase hex. Each merge was pinned with `--match-head-commit <full head sha>`. Claim: the handoff lease names holder af70e674 and expiry 2026-11-10T21:00Z, and another session may take it after expiry | PROOF: a merge whose delivered tree differs from the reviewed head tree with no re-run
K4 | FIT | "Never exit code, output size or silence." | Receipts are TRX files with sha256, for example #33 full Release 463/463 `90F1456D...F32C76`.

Evidence refused:
- The #33 mutant m2 first produced no TRX (`m2-attribute-missing NO TRX (build failed?)`). It was not counted as caught; it was rewritten and re-run, and caught (`321E1F06...`).
- The #33 round-1 full Release run, 462/463 with `ProfilePurgeFailed` in an untouched test, was not accepted. The final head was re-gated: 463/463 in Debug and in Release | PROOF: a merge whose gate counted a run with no TRX
K5 | INSTANCE-FAILURE | "Before work starts, a subject declares its profile and profile version." | No subject recorded a profile line or an acceptance-contract digest before work. The contract (the ruling's gates) is applied the same way each time, but nothing binds it by digest per subject. Compliance needs only a one-line declaration in the PR body before the first gate | PROOF: a PR body whose first revision carries `profile: code@r11` and a contract digest that the final gate cites
K6 | FIT | "When the check is model judgment, the cross-family rule applies and the claim is computed, not asserted (R3)." | Producer class: anthropic, claude-opus-5-5. Key class: openai. The Codex CLI prints `model: gpt-6.1-sol` and `provider: openai` in each falsifier transcript (session ids in the header), and those printed lines are the measured basis. The R9 tool still reports NO-CROSS-FAMILY-VALIDATION because no posture role ran | PROOF: a falsifier transcript whose printed provider equals the producer's
K7 | FIT | "Acceptance and delivery are separate states." | Delivery target: `main` of layibabalola/adobe-document-cloud-ingester. Each delivery closed as one `gh pr merge` call, pinned to the head. The 10-minute auditor tick runs `gh pr list --state open` on every pass, which would surface a gated but unmerged PR. After #33, only the owner's thread PR #3 was open | PROOF: a gated PR left open across ticks with no tick reporting it
K8 | FIT | "Running out of quota means rotating or parking the work that needs inference, never failing the factory closed." | Last quota event in the window: the handoff lease records "rotation HOLD at 98% weekly" at 2026-11-09T14:25Z and "99%" at 17:14Z, "nothing in flight". The next session took the lease at 19:06Z and resumed product work (#26-#33 merged after that). Nothing failed closed.

Cost, recorded as operability and not as a kernel defect:
- The work was held for at least 4.7 h.
- The Claude account is shared with about 5 other fleet projects. At 2026-11-10T17:39Z, 31 claude.exe and 85 pwsh.exe processes were running and CPU sampled 53/47/56%.
- The handoff file holds 10 "rotation PREP/HOLD" and 23 "account rotation" mentions | PROOF: a quota event after which a product subject was refused rather than parked
K9 | INSTANCE-FAILURE | "with empty memory, resumes from the project's tree and the bus alone." | This session resumed after the 2026-11-09 rotation from adobe:.claude-state/RESUME.md, the handoff lease and auto-memory. All three are Git-excluded and machine-local: `.claude-state/` is excluded by design. A fresh machine with only the tree and the bus would not have them. Compliance was possible by keeping a tracked resume pointer in the product repository | PROOF: a cold resume on a new machine from a clone and the bus alone that reaches the next queued product item
K10 | INSTANCE-FAILURE | "it records the account it was derived under." | Provider work ran all window (3 Codex sessions, 9 Claude seats). No inventory file records `probed_under`: the 30 `.claude-state` files that match are prompts, logs and directives, none an inventory. Account parity rests on `check-account-drift.ps1` (ALIGNED, fp FEDF0C85, at session start), which is parity evidence, not an inventory | PROOF: an inventory whose probed_under names the account each key ran under
K11 | INSTANCE-FAILURE | "R1–R5, R7, R8 and R9 apply to every report a factory makes about itself" | Measured gaps:
- The per-seat and falsifier evidence for #31 and #32 was published on the PR threads at 2026-11-10T14:55:07Z and 14:55:05Z, 13 h and 11 h after the merges (01:48:07Z, 04:02:05Z), and only after a CoS reviewer flagged it. Before merging, the gate tables existed only in the PR bodies.
- On #33 the gate record was posted at 15:33:09Z, 7 s before the merge.
- The auditor's own chat reports had two slips:
  - one timestamp was estimated (9:05 AM stated while Get-Date read 9:03:14);
  - one count was mis-measured: "29 rotation-prep or hold entries", where the measured figure is 10 PREP/HOLD and 23 rotation mentions.
- R9 is met by this filing's computed posture line | PROOF: a delivered subject whose evidence is on its thread before the merge, with time for a reviewer to act
K12 | INSTANCE-FAILURE | "Every project that runs the kernel files what happened" | The previous filing was the 2026-10-11 supplement; this one comes 30 days later, and PROMPT K asks for weekly filings while the kernel is a CANDIDATE. The park on 2026-11-09 and the change of instance were seams that called for a filing at the time | PROOF: weekly filings through the next window

## Profile lines

P:code subject-identity | FIT | "the git tree OID of the candidate commit as it will be delivered" | 3 of 3 delivered trees equal the reviewed head trees (K3) | PROOF: a squash merge whose tree differs from the reviewed tree
P:code determinism-class | INSTANCE-FAILURE | "flaky suites are declared per test, never silently retried" | `ProfilePurgeFailed` hit untested-by-change tests in 3 full-suite runs:
- #31: Debug run, `AnAdobeLocalePageIsRefusedAndReportedByFamilyAndShapeOnly`;
- #33 r1: Release run, `ADownloadBeforeArmingIsAmbiguousAndDoesNotSpendTheGate`;
- one earlier FU4 hit.

They were handled by interleaved control runs and re-gating, not by a per-test declaration. Mechanism scoping (cause still unknown): adobe:.claude-state/product/PROFILEPURGE-FLAKE-SCOPING-20261110.md | PROOF: a per-test flake declaration in the product repository
P:code independent-key | FIT | "a verifier from another model family (R3) whose class has not become a producer of the subject" | Codex/openai never wrote product bytes in these subjects | PROOF: a subject in which the key's family authored a commit
P:code human-gates | INSTANCE-FAILURE | "the register is reachable from every session checkout" | see K2: the product checkout carries no register file | PROOF: a register file tracked in the product repository
P:code delivery-target | FIT | "integration branch via the project's landing path" | squash merges to `main`, each pinned to its head | PROOF: an unpinned merge
P:code budgets | FIT | "wall time per suite, provider calls per subject" | Measured on #33:
- full Debug 511 s, full Release 443 s;
- Codex rounds: #31 1, #32 7, #33 2;
- full Release run: 382 s of 438 s were spent in 22 tests bounded by fixed timeouts. | PROOF: a gate report without wall times

## Proposals

P1 | FRICTION | kernel §7 lists no gap for this | A fail-closed gate blocked its own repair, repeatedly. Evidence from adobe:.claude-state/continuity/ROOT-CAUSE-STALLS-20261021.md (machine-local):
- line 7: "One global fail-closed preflight (Test-FactoryGovernance) gates every mutation, including the mutations that would repair or roll back whatever made it fail";
- line 14: the same shape recurred 9 times from August to October;
- line 18: on 10-20, 38 of 48 Sol wakes were nomotion.

At the park on 2026-11-09, %LOCALAPPDATA%\AdobeIngesterFactory\evidence-quarantine\sol-exec held 1,223 `*nomotion*` wake directories (counted 2026-11-10). K8 forbids capacity from failing the factory closed. No clause forbids a governance gate from doing the same to its own remedy. The steward decides placement (K2 or K8) | REPLACES: "Work that needs no inference continues." -> "Work that needs no inference continues. No gate's failure may block the bounded repair or rollback of that gate; after K identical refusals, the gate escalates to the owner instead of repeating." | PROOF: an instance whose fail-closed gate repairs itself through a scoped remedy path without an owner act, and no fleet project with a recurrence after this text lands

## Untested

- **Contention as the flake's cause.** ProfilePurgeFailed may come from host contention (a shared host, measured above 47% CPU when idle for this project). Nothing records which of the three purge failure branches fires, so this is not established.
- **Dedicated machines.** The owner has ordered dedicated machines, one per fleet project, each with its own Claude and Codex accounts. The prediction is that K8 operability and flake rates become separable per project. That is untested until the machines run.
