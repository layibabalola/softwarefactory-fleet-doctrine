# Cloudvore (DropBox Vault): current factory spec

source_commit: 3b7d5323fce52bc2ca512b04d0650d4ce830b4b4

Updated 2026-09-07. Source repository: https://github.com/layibabalola/Cloudvore. This spec is published only after the source commit reaches that repository's master. The former September 3 snapshot remains available in Git history; its hub/lanes/landing descriptions are historical, not the current entry route.

## Product and safety

Cloudvore is a Windows WPF application for backing up footage and verifying existing copies. The proof is the product. No surface may say SAFE TO WIPE unless the persisted IsSafeToWipe verdict permits it; false tamper alarms are also defects. Never kill rclone by name or in bulk. Probes use throwaway configuration, never live rclone.conf, provider authentication endpoints, or browser launches.

The completed kernel review has been consumed: S1-S4 are source-supported remediation items, with an additional quarantine finding S5. They remain reproduce-first defects, not fixes or new acceptance credit. Product release, tagging, and accepted product-safety deferral remain final owner decisions.

## Current execution route

Both AGENTS.md and CLAUDE.md point to docs/operating-contract.md. BACKLOG.md has one active queue with explicit task states and dependencies. Old knowledge/review artifacts are reference evidence, not a competing dispatch queue.

The owner authorized autonomous execution of the recovery using cheap, bounded delegates on September 7. This execution uses Luna at low effort for narrow implementation and review tasks, one writer per file, one integration owner, no persistent hub seats, and no recursive delegation. Tests and independent review decide acceptance. This does not constitute a fleet-wide model-role qualification or universal-controller adoption.

At entry and closeout, `python tools/gate.py --json --doctrine-check` checks the real entry route, active queue, execution checkout, and local prerequisites. Its doctrine result is separate and advisory for unrelated product work. Claude has one SessionStart command hook to the same implementation; its configured Bash command was invoked successfully on this host. The checker starts no model and never acknowledges doctrine. Repeated checks do not create new work. No new scheduled model loop or heartbeat was installed.

The existing 60-minute maximum run duration is preserved as a mandatory constraint. The previously malformed Cloudvore Run/Stall Enforcer tasks have not been repaired by this fleet slice; this spec does not claim that they enforce the limit. A successful worker exit without retained patch/review evidence is not completion.

Product behavior changes require three identical green runs at one candidate SHA, with a hosted Windows route when local thermal admission refuses. Review is tied to the product bytes; missing review is not approval. Push after commits, preserve unrelated dirty state, and integrate only within the granted scope.

## Explicit doctrine dispositions

| Subject | Cloudvore disposition and evidence |
|---|---|
| Canonical bus laws: data, local verification, single-writer custody, reviewed publication | ADOPT for this recovery. Implemented entry contract and exact publication checker; no bus text executes as authority by itself. |
| CIAA / parallel-launch resumption | DISTINGUISH for this finite loop. Bounded disjoint tasks can be delegated when useful; a boot does not launch all historical lanes. The prior field-test account is historical, not current installation evidence. |
| Autonomous checkpoint staging/cherry-picking | DISTINGUISH. Current boot derives Git state without checkout/add/cherry-pick. The old continuity spec's Cloudvore adoption claim is superseded by this explicit disposition; other projects decide separately. |
| Scheduled heartbeat adoption | DISTINGUISH for this recovery. Entry/closeout checks expose actual pending/unavailable state. Cloudvore has no published heartbeat; ABSENT must remain visible and must not be manufactured into healthy status. |
| R26 universal token controller | DISTINGUISH / CANDIDATE_ZERO_AUTHORITY remains unchanged. Publication is not runtime installation, provider authorization, or adoption proof. |
| Other historical proposals and sibling implementation details | Not adopted by this recovery. They remain source material for a separately scoped need; inspecting a catalog or moving a cursor is not blanket adoption. |

Reviewed initial bus subject: 7ebe429e3de100be5cb02faf8f35627586a17624, limited to the relevant laws, Cloudvore state, continuity proposals, and existing R26 disposition. Its catalog contains 16 specs (nine projects and seven cross-cutting protocols) and 16 candidate artifacts. Unadopted historical proposals remain reference material; none acquires runtime authority by moving the cursor. Subsequent tool fixes have their own evidence in RECEIPTS.md. Cloudvore's tracked task result records the exact reviewed cursor for recovery after machine-local marker loss.

R26 exact subject retained: **DISTINGUISH(909f769d02e8412e51e28e242cfa8d00dadc9a3d, CLOUDVORE_R26_CANDIDATE_ZERO_AUTHORITY_PENDING_LOCAL_PROOF)**. The historical project candidate is 3ea3a09230aff318caef30980bfa76d48f189874; no new activation or non-regression credit is claimed. The frozen R26 checker already returned PROJECT_SPEC_DRIFT at bus baseline 7ebe429; that failure remains visible and was not waived by this publication.

## Consumption and publication mechanics

Use the shared tools/doctrine-sync.mjs. Acknowledgement requires `ack --commit <reviewedSHA>` and validates reachability from the fetched bus master; a new remote commit arriving after review stays pending. Git children have finite deadlines and interactive prompts disabled.

A portable result remains FIXED-LOCALLY-PENDING-DOCTRINE until its review and exact publication evidence are recorded. Exact `export-check --source-commit <SHA> --publication-commit <SHA>` verifies both remote ancestry chains and this spec's single matching source_commit field at the named publication. It does not certify review or ratification. An unrelated commit naming Cloudvore or a heartbeat cannot close the obligation. Keep the result in the existing Cloudvore BACKLOG, not a second queue.

## Verification and limits

- Cloudvore entry-route suite: 13 passing tests; bootstrap: 10 passing tests, including invalid dependencies, misleading entry links, dirty primary preservation, separate worktree execution, and advisory timeout/error behavior.
- [Product bar at parent 2252219](https://github.com/layibabalola/Cloudvore/actions/runs/34147321023): 900 Core passed, 2 skipped; 1,150 App passed; five Integration files excluded. The source commit has identical src/ and product-workflow bytes. This is the automatic product floor, not a new three-pass product-change claim.
- [Corrected Cloudvore tools bar](https://github.com/layibabalola/Cloudvore/actions/runs/34149432914): 18/18 required suites passed at source 3b7d532, including 10 gate tests, 13 entry-route tests and 51 state tests; 218 seconds. The initial run exposed a Windows path fixture mismatch and multiline status rendering error; both remain required and have focused repairs. Automatic runs execute every required suite; manual tier=all retains informational diagnostics. The nine failing/timed-out informational suites in the initial run are not acceptance credit.
- [Doctrine sync CI](https://github.com/layibabalola/softwarefactory-fleet-doctrine/actions/runs/34148872025): passed at 179e527. Local sync fixtures also passed 20 cases, including the latest-head mutation and simulated child-timeout boundary. The membership fixture exercises both actual readers and excludes pinned protocol documents without moving their historical paths.
- Installed host versions observed September 7: codex-cli 0.144.6; Claude Code 2.1.259; Node v24.14.0. These are observations, not a claim that every fleet machine is aligned. No CLI upgrade was performed.

This fleet slice does not fix the product integrity findings, deploy thermal changes, enable new providers, release a package, or activate a universal governor. Those responsibilities remain explicit in Cloudvore's recovery plan.
