# Factory-kernel dogfood filing — agent-bridge (K12-FILE-R6)

project: agent-bridge
kernel: fleet-factory-kernel r5 (bus 50ee077, blob 6821c4c3; unchanged since 6060669)
profile: code@r10 (specs/fleet-factory-kernel/profiles/code.md, blob 5511ccb3 at bus 50ee077)
instance: docs/internal/FACTORY_KERNEL_INSTANCE.md at github/master 5aa853a5 (blob fe54fe39, the same blob as at 35bcd122; its header still reads "Profile: `code` **r9**" (register:3) while every window declaration but one reads code@r10; all 12 rows of its K1..K12 instance map read PARTIAL)
subjects: 0 closed end-to-end. AFPM-MSG-DEBT-1 (subject e02bb0fbd92b7b435bfada9d506e0a21b42eeea1, keyed and delivered tree d2732828420647bd5b8cf43b11a4ee74c32c5175, merge 5aa853a5f0190dfa3cc9cd0faa1b1dbd92375c8c, PR #200; product code) is an examined delivery: it meets S22 (a), (b), (c) and (e), and (d) in tree form only. Under the S22 text as written it counts 0; a separate ruling on tree-form delivery is requested (## Request to the arbiter). Also examined, not claimed: HARNESS-SERVER-INVOKE-1 ((f) recorded only in the producer's report), AFPM-MSG-1 (parked, never merged), AFPM-MSG-1N (closed undelivered; its change is what AFPM-MSG-DEBT-1 delivered), and from r2 DOCTRINE-GUARDS-1N and K5-PROFILE-PARAM. Not examined beyond tree identity (K3, K7) and class (K2, all class C): CALLER-BIND-1-R3, STORAGE-INSPECT-GUARD-R2, CALLER-BIND-2N (gate id CALLER-BIND-2-R5)
window: 2026-10-07T00:01Z .. 2026-10-07T13:10Z = WAL L3003..L3113 (DGUARDS-K5-1b426829 .. AFPMDEBT-DONE-1b426829)
health: assurance=UNSATISFIED operability=PRESSURED
providers: codex (gpt-6.1-sol; sentinel = receipt `VERDICT:` line; 20 window receipts SOL-20261006-190106-125 .. SOL-20261007-073959-517, 6 of them carrying `identity=<tree>`, 5 K5-EXEMPT; one, SOL-20261006-203403-390 (k5.cards STORAGE-INSPECT-GUARD), carries the declaration `kernel: r5, profile: code@r9` from a card declared before the window)
posture: conjugal-standard-PARTIAL (0/17 lanes; missing: Designer-Scope 0/1; Designer-Verify 0/1; Lint-Consistency 0/2; Arbiter 0/1; Consolidator 0/1; Panel 0/8; Classifier 0/3); cross_family: NO-CROSS-FAMILY-VALIDATION. Computed (`python tools/review-posture/review_posture.py posture <empty dir>`, bus 50ee077, Python 3.14.3, exit 1, bus `git status --porcelain` 0 entries before and after). Retained receipt: `.claude-state/coordination/evidence/KR4-ADOPT/posture-receipt-20261007-r3.txt` (sha256 0dd2b65b24e41379198d6b815ebdeca1183814ae234244cb1543581434d634ba, run 2026-10-07T13:13:49Z; tool sha256 6418f59d…, roles.json d9ad9776…, both unchanged from r2's receipt). No posture role ran. The AFPM-MSG-DEBT-1 SOL key and this filing's ratifying quorum ran outside those roles; this records what was measured.

**Scope and notation.** `L<n>` = line n of `.claude-state/HUB_RUN_WAL.md`, read through L3113 (prefix L1..L3113: 3,613,180 bytes, sha256 248335f674dafbe362defb7ea5feedd2236901a74b901d62deb4babb65ae9cdb). `X` = `.claude-state/coordination/evidence/AFPM-MSG-DEBT-1/`. `DX` = `.claude-state/coordination/decisions/DECISION-AFPM-MSG-DEBT-1-e02bb0fb.json`: as first written (13:10:04Z) sha256 06ecc4452abde573d1a49d3889e5c144e1666d375846d87ac584ba72748ef106, bytes not retained; as corrected (13:23:48Z) sha256 8b0dcd4f0744ca1236a130a78974b09c8346cee41797a5ccb7053821fb0aac3a (D6). `E` = `.claude-state/coordination/evidence/HARNESS-SERVER-INVOKE-1/`. `D` = `.claude-state/coordination/decisions/DECISION-HARNESS-SERVER-INVOKE-1-89768c2f.json` (sha256 1c7c7943…5929). `R <id>` = `.claude-state/coordination/lane-receipts/<id>.receipt.json`. `register:<n>` = line n of blob fe54fe39. Every digest below was recomputed by the drafter on 2026-10-07 (`Get-FileHash -Algorithm SHA256`, raw bytes). CI facts were re-read by the drafter with `gh run view <id> --json attempt,conclusion,headSha,event,createdAt,updatedAt` and `gh pr view 200` (exit 0). The interval L2254..L3002 is not examined and claims nothing; L3114 onward post-dates the window.

**Credit kinds.** *Key-authenticated*: the bytes existed before the key started and its record shows the check. *Hub-credited*: established by the hub after the key, witnessed by git or `gh`. *Producer-only*: only the producer's report records it.

## Subjects

| card | class | subject → merge (PR) | keyed tree / delivered tree | keys | PR CI / post-merge CI | WAL declared → verdicts → DONE |
|---|---|---|---|---|---|---|
| AFPM-MSG-DEBT-1 (examined; (d) tree form only) | B (register:84: hub + one independent other-family reviewer) | e02bb0fb → 5aa853a5 (#200) | d2732828… = d2732828… | SOL-20261007-073959-517 APPROVE `identity=d2732828…`, one round | 37619590526 attempt 1 success / 37623098181 success | AFPMDEBT-DECLARED (L3108) → AFPMDEBT-Q1 (L3110), AFPMDEBT-MERGED (L3111) → AFPMDEBT-DONE (L3113) |
| HARNESS-SERVER-INVOKE-1 (examined, not claimed) | A (register:83) + SOL by contract | 89768c2f → 35bcd122 (#195) | c38dbfb3… = c38dbfb3… | SOL-20261007-022421-842 CHANGES_REQUESTED, SOL-20261007-031324-342 APPROVE, both `identity=c38dbfb3…` | 37579617112 attempt 2 success (attempt 1 failure) / 37592712020 success | HSI1-DECLARED (L3064) → HSI1-R1V (L3070), HSI1-R2V (L3080) → HSI1-DONE (L3081) |
| AFPM-MSG-1 (not claimed) | B | c109b8cc (tree 699e3de2) → none (#197 closed unmerged) | 699e3de2 / none | SOL-20261007-051747-496 BLOCKER `identity=699e3de2…` | 37602307106 success / n/a | AFPMMSG-DECLARED (L3087) → AFPMMSG-PARKED (L3090) → AFPMMSG-LINEAGE NARROW 2-1 (L3091) |
| AFPM-MSG-1N (not claimed) | B | cdaf185f (tree c94a8e62), rebuilt 9c1f47de (tree d2732828) → none (#199 closed unmerged) | d2732828 / none | SOL-20261007-061903-013 APPROVE `identity=c94a8e62…`; SOL-20261007-070149-503 BLOCKER `identity=d2732828…` | 37609080316, 37613829957 success / n/a | AFPM1N-DECLARED (L3092) → AFPM1N-R1V (L3100), AFPM1N-RK1 (L3106) → AFPM1N-CLOSED (L3107) |
| DOCTRINE-GUARDS-1N (not claimed; r2) | C | 75bbf8de → 7a2acc8c (#193) | SOL: c73a1f0e = c73a1f0e; seats A/B/C: 837c8ce6 ≠ | 3 Sonnet APPROVE at d285849a; SOL re-key APPROVE at 75bbf8de, narrowed charter | 37561623849 a2 / 37566796091 success | DG1N-DECLARED (L3017) → DG1N-R2V (L3025), DG1N-REBUILD (L3036) → DG1N-DONE (L3046) |
| K5-PROFILE-PARAM (not claimed; r2) | C, runtime install | manifest digest 6e6b9af4… → merge none | stage C:/abwt/k5pp-stage-r1 | seats A/B/C + SOL-20261006-193858-717 (K5-EXEMPT, untracked-install) APPROVE | n/a | K5PP-DECLARED (L3013) → K5PP-DONE (L3016) |

### AFPM-MSG-DEBT-1 — examined, not claimed (counts 0 under S22 (d) as written)

**What it ships.** The `would_leave_no_active_pair` refusal now carries an additive `blocked_reason`, and its advice matches the cause (L3113). Diff c4340515..e02bb0fb: `agent_bridge/session_service.py`, `test_afpm_debt1_reaper_confirm.py`, `docs/internal/BRIDGE_PAIRING_INTENT_SPEC.md`, `USER_GUIDE.md`; 4 files, +349 −18.

**Origin.** The debt of the closed AFPM-MSG-1/1N lineage (L3107). The fork ruling `decisions/DECISION-FORK-20261007-KERNEL-CLOSURE.json` (2-1; adversary 3 dissented for tooling first, and its two cheapest checks were adopted by hand) ordered redelivery under a minimal contract cut to the arbiter's credit test (L3108).

**Recompute.** Identity: `git rev-parse e02bb0fb^{tree} 5aa853a5^{tree} 5aa853a5^2^{tree}` → all `d2732828420647bd5b8cf43b11a4ee74c32c5175`; `5aa853a5^1` = c4340515, `5aa853a5^2` = e02bb0fb; c4340515 is an ancestor of e02bb0fb. Contract: `X/CONTRACT.md` raw sha256 c9e0e6e311bd67aa8ab2be970c1f726698fdb85e07d6aeac3afa87ec25dc5f14, CRLF→LF and trim f118465a997d00fa148e1e7a2447390ee21f0f0e01f45a55b43bd4d3866564f5, the digest declared at L3108. Change identity: `git diff c4340515 e02bb0fb` and `git diff 35bcd122 cdaf185f`, index lines removed, are equal at 498 lines each.

**Credit test (tests at `adjudications/factory-kernel/conjugal.dispositions.md`:50-57; row form of S22 at :62; bus blob 571fb4d3).**

| S | (a) tree | (b) receipt reproduces | (c) full tree in verdict line | (d) delivered at identity | (e) contract | Ruling |
|---|---|---|---|---|---|---|
| AFPM-MSG-DEBT-1 | `d2732828…` yes | yes: R SOL-20261007-073959-517 `lastMessage` equals the `task_complete` record (85 of 85) of Codex rollout thread 01a11660-d6c3-73f0-a18a-26d705de8e20 (rollout sha256 accde207…, `turn_context` model gpt-6.1-sol); key Codex, producer Claude | yes (`VERDICT: APPROVE identity=d2732828420647bd5b8cf43b11a4ee74c32c5175`) | **no, as written**; tree form only: merge 5aa853a5, a github/master tip (local reflog `github/master@{2026-10-07T07:43:51-05:00}` c4340515→5aa853a5; `ls-remote`), has tree d2732828 = keyed tree and first parent c4340515 = the keyed base, master 9 s before the merge. The keyed commit e02bb0fb is the merge's second parent and was never itself a tip. Hub-credited | unchanged: f118465a declared at L3108 (a hub-written, minute-resolution stamp, D11) before the first card commit; recomputed by the key; one round | counts 0 under the text; ruling requested |

S22's text is categorical: "delivery at identity is witnessed only when the keyed commit itself was a pushed `origin/master` tip" (:55-56). The nearest precedent is S1 (:61): tree `721e4b15` was never a witnessed tip, and the arbiter ruled ADOPTED-CONDITIONAL (C5), not credited.

**Timeline (UTC; file times are locators, the WAL and `gh` are the record).** Contract last written 12:10:18Z; declaration L3108 (07:10 CDT = 12:10Z); card commits afa0f174 and e02bb0fb committed 12:11:38Z; PR run 37619590526 created 12:14:29Z, concluded by 12:38:15Z; `pr-run-1.json` written 12:38:59Z; `master-check-key.txt` 12:39:02Z; SOL invoked 12:39:59Z, completed 12:43:15Z; `master-check-merge.txt` 12:43:32Z; PR #200 merged 12:43:41Z; `delivery-tree.txt` 12:43:51Z; post-merge run 37623098181 created 12:43:44Z, concluded by 13:09:24Z; DX first written 13:10:04Z; first check 13:10:10Z; AFPMDEBT-DONE L3113 (08:10 CDT); after the window, DX corrected 13:23:48Z and the check re-run 13:28:54Z (D6).

**Key-authenticated** (SOL-20261007-073959-517, 12:39:59Z–12:43:15Z; per its events file `lane-receipts/SOL-20261007-073959-517.events.jsonl`, items 4 and 7, and its final message). Every item existed before the key started:
- the contract LF digest f118465a, and the raw sha256 of all 8 charter receipts: CONTRACT.md, SOL-CHARTER.md, pr-run-1.json, master-check-key.txt, IMPLEMENTER-REPORT-impl1.md, parity-claude-impl1.json, parity-claude-sol1.json, resume-gate-pre.txt;
- **execution acceptance:** `pr-run-1.json` (run 37619590526, attempt 1, conclusion success, headSha e02bb0fb, `EXIT_CODE=0`). Per the WAL and the implementer report ("CI not awaited") it is a hub-written transcription of `gh`, which rests on self-attested records (D4); the key authenticated it by sha256;
- the tree of e02bb0fb = d2732828, and c4340515 is its ancestor;
- the change identity (498 = 498 lines, the same 4 files) against the change SOL approved in AFPM-MSG-1N;
- every commit in c4340515..e02bb0fb carries `Dispatch-Id: impl1`;
- master = keyed base at 12:39:02Z (`master-check-key.txt`);
- statically, the incorporated promises M1, M2, M3′, M4, M5′ and H1-H3 of `evidence/AFPM-MSG-1N/CONTRACT.md` (LF 6aea569a).

SOL's message: "Pre-merge and post-merge delivery checks remain hub obligations."

**Health before the key** (among its 8 authenticated receipts): Claude parity per dispatch, pre-spend gate (D1).

**Hub-credited, after the key** (git/`gh`-witnessed; drafter re-read each):
- `master-check-merge.txt`: master still c4340515 at 12:43:32Z;
- the merge 5aa853a5 by Hub-MergeClassA with `--match-head-commit` (L3111), and its tree equality (`delivery-tree.txt`: "HUB-CREDITED post-merge fact (git-witnessed), not a key claim");
- post-merge run 37623098181, push, attempt 1, success at 5aa853a5;
- DX passing `check_decision_record`: on the first DX at 13:10:10Z (`decision-check-pre-correction.txt`) and on the corrected DX at 13:28:54Z (`decision-check.txt`); both PASS, `EXIT_CODE=0`, same bytes ce942f97…; flags rest on L3113 (D7);
- the landing gate (D6).

**Producer-only:** the implementer's own ruff, mypy and pytest runs (`IMPLEMENTER-REPORT-impl1.md`), which the contract does not use as acceptance.

Limits recorded against this delivery:
- **D1 — Codex-side parity not probed for this card.** `parity-claude-impl1.json` and `parity-claude-sol1.json` (`account-drift.v1`, ALIGNED, org prefix 2a6cf04d, `declared.ok:false`) compare Claude Desktop with Claude CLI only. The key ran on Codex; its receipt carries no account field.
- **D2 — the key is static.** SOL ran read-only with `networkAccess:false` and ran no tests. Execution acceptance is PR CI alone, on the register's class-A runner, which is "independent of the producer seat, not of the host" (register:83). The drafter's `gh run view` agrees with `pr-run-1.json`.
- **D3 — produced under the closed AFPM-MSG-1/1N lineage, re-delivered by cherry-pick** (afa0f174, e02bb0fb; L3110). The key verified diff identity and re-judged the promises statically. Tree d2732828 is the tree SOL BLOCKED at SOL-20261007-070149-503 on producer identity alone (L3107).
- **D4 — producer identity is self-attested.** afa0f174 and e02bb0fb carry the repository's git user as author and committer, the same identity the hub commits under (FORK adversary 3 measured this for cdaf185f and 9c1f47de). The distinction rests on the `Dispatch-Id: impl1` trailer, the implementer report and the WAL, which the producer and the hub wrote.
- **D5 — no DEBT-1 receipt shows the base failing.** PR CI collects the card tests (`windows-ci.yml:197`). The red/green exists only in the closed lineage (`evidence/AFPM-MSG-1N/redgreen-r1rk1.txt`, 8a44f83f…: base 27 failed, tree d2732828 27 passed, authenticated by a BLOCKER key); cited, not credited.
- **D6 — the landing gate receipt was overwritten after DX recorded it; DX was then corrected.** DX as first written (06ecc445…) bound `resume-gate-land.txt` as a6e62873…, bytes not retained. The file was re-run twice after that: at 13:10:37Z `NOT-READY` (the record's own correction names NO-MANIFEST and MEMORY-NOTE-STALE; the drafter saw `GAP MEMORY-NOTE-STALE … wal-line=3113`), `EXIT_CODE=1`, sha256 a18f1498…; at 13:12:05Z `READY`, `EXIT_CODE=0`, sha256 efbb685f…. After the drafter reported it, the hub rewrote DX at 13:23:48Z (8b0dcd4f…) with a `corrections` entry binding efbb685f…; all 14 of its `receiptDigests` now reproduce. The landing-gate credit therefore rests on the third run, kept after two that were not READY. The pre-spend gate (`resume-gate-pre.txt`, 12:10:40Z, `READY`, `EXIT_CODE=0`) was key-authenticated.
- **D7 — the decision check records no command.** `decision-check-pre-correction.txt` (13:10:10Z, on the first DX) and `decision-check.txt` (13:28:54Z, on the corrected DX) each hold one PASS line (actor split) and `EXIT_CODE=0`. Register:83: the checker checks "shape and actor split, not the CI facts"; the drafter re-read both runs.
- **D8 — (d) was missed by the merge method, not forced by the facts.** At 12:43:32Z master was c4340515, an ancestor of e02bb0fb, so e02bb0fb was fast-forwardable and could itself have become the tip. The landing path (`gh pr merge --match-head-commit`, Hub-MergeClassA) made merge commit 5aa853a5 instead. Whether the register or branch settings allow a fast-forward landing for class B was not examined. The contract itself paraphrases (d) in commit form ("the keyed commit was itself a pushed master tip"), while its A4 prescribes a merge with tree equality.
- **D9 — K5-PASS is from the substring checker** (W4); the evidence is the literal `profile: code@r10` at L3108 and in `k5.declaration`.
- **D10 — a hub path typo** failed one chain attempt before spend; no receipt (L3111).
- **D11 — the declaration time is hub-asserted.** "Before the first card commit" rests on the untracked, minute-resolution WAL stamp at L3108 (07:10 CDT) against commits at 12:11:38Z; no independent timestamp binds it. The contract bytes did not change after it: the key recomputed f118465a.

### HARNESS-SERVER-INVOKE-1 — examined, not claimed

Test-harness debt (L2975); contract c8592e87 declared at L3064 (05:51Z) before the only card commit 89768c2f (06:05:01Z). **Why 0:** contract check (f), a 3+3 PYTHONPATH matrix in the declared environment, is recorded only in the producer's own report, which no key authenticated. **Key-authenticated** (SOL-20261007-031324-342, done 08:15:26Z, events item_6): the head tree c38dbfb3, the contract, and seven hub receipts (hub-ci-r2 summary and HEAD, `pr-run.json`, gitless, flake, parity-3, resume-gate-pre), all in D `receiptDigests`. **Hub-credited after the key:** delivery (merge 35bcd122 at 08:16:45Z, tree c38dbfb3, post-merge 37592712020 success, L3081).

Limits (as r2): **L1** (f)'s precondition is false in a `.git` checkout (L3066); the charter question stated the hub's conclusion; both rounds ruled it in-contract on intent; the gitless receipt and hub CI record no environment. **L2** charter template gained a `{HUBCI}` field between rounds (L3079). **L3** a PR CI retry of a test declared only by file family. **L5** authenticated receipts are hub-written. **L8** K5 substring checker. **L10** the CI keys ran in `.git` trees where base also passes (inferred, `launch.py:8-28`). **L11** the hub edited `hub-ci.ps1` between rounds; bytes not retained (L3070). **L12** L17 audit short per dispatch (L3080). D's `deviations` omits L11 and L12. Also: parity Claude-only, producer self-attested, test-only debt, register header r9.

### AFPM-MSG-1 and AFPM-MSG-1N — examined, not claimed

- **AFPM-MSG-1** (L3087, contract 951e9c2a). SOL BLOCKER on tree 699e3de2 (SOL-20261007-051747-496): hub evidence gaps, M3 incomplete, no M5 docsize receipt (L3090). Its rule "a BLOCKER parks" fired; a three-Opus panel ruled NARROW 2-1, recording that "every finding is a hub-evidence or contract-wording gap" (L3091). PR #197 closed unmerged.
- **AFPM-MSG-1N** (L3092, contract 6aea569a, stop rule "a BLOCKER in either round CLOSES"). SOL APPROVE `identity=c94a8e62` (SOL-20261007-061903-013). Master moved; the hub merged master into the branch itself (9c1f47de, tree d2732828); the re-key SOL-20261007-070149-503 ruled BLOCKER on "never by the hub", every other check passing (L3107). Closed undelivered; PR #199 closed unmerged.

### DOCTRINE-GUARDS-1N — examined, not claimed (r2)

Held: contract f4738b02 bound before work (L3017), and the SOL key is on the delivered tree c73a1f0e. Failed: as listed under ## Corrections, plus no declared path manifest.

## Clauses

K1 | INSTANCE-FAILURE | "A candidate is never accepted on evidence whose only author is its producer" | held for AFPM-MSG-DEBT-1: DX names producer "K1 implementer dispatch impl1 (Sonnet subagent)", verifier SOL and adjudicator hub 1b426829; its PR CI receipt was hub-written before the key started and authenticated during its run; producer identity is self-attested (D4). Failed in window: HSI1 was accepted with contract check (f) recorded in its declared environment only in the producer's own report; the non-producer runs cannot stand in for it (L10) | PROOF: a non-producer, key-authenticated receipt of HSI1 (f)'s 3+3 at tree c38dbfb3 dated before 08:16Z

K2 | INSTANCE-FAILURE | "Escalation goes to the owner for decisions reserved by that register" | held for AFPM-MSG-DEBT-1: class B (register:84, hub + one other-family reviewer), register OID named at L3108 before work. Failed in window: four class-C merges while register:61-63 leaves class-C owner gates "an open question… this register does not resolve it permissively": CALLER-BIND-1-R3 0784b8dc (L3008), STORAGE-INSPECT-GUARD-R2 4594da24 (L3033), DOCTRINE-GUARDS-1N 7a2acc8c (L3043), each `class: C` in its decision record (`DECISION-CALLER-BIND-1-R3-da8616dd`, `-STORAGE-INSPECT-GUARD-R2-6d3b4410`, `-DOCTRINE-GUARDS-1N-75bbf8de`), and CALLER-BIND-2N c4340515 (L3098; DECLARED-CALLER-BIND-2N.md:54). 0 `lane=USER` entries in L3003..L3113 | PROOF: an owner ruling dated before 2026-10-07T03:27Z settling class-C hook/CI gates

K3 | INSTANCE-FAILURE | "under a claim an observer other than the claimant can decide stale and release" | identity held: all 6 window merges have `<merge>^{tree}` = `<merge>^2^{tree}` (0784b8dc, 4594da24, 7a2acc8c, 35bcd122, c4340515, 5aa853a5). Claim: HSI1's CONTRACT.md names an owner session, owned processes by role (no pids), an expiry and an observer-release rule, but its inflight manifest carries only `written_by`. AFPM-MSG-1 declared a claim expiry (L3087). AFPM-MSG-DEBT-1's minimal contract has no claim block; L3108 posts a non-binding advisory to routine hubs. L17 per dispatch not met (L12) and out of scope for DEBT-1 by its contract | PROOF: a window claim record naming owned pids and a release rule

K4 | FIT | "Never exit code, output size or silence." | AFPM-MSG-DEBT-1 accepted on run conclusion and headSha (`pr-run-1.json`), re-read with `gh`. SOL r1 on HSI1 refused a `summary.txt` not ending in `DONE` (L3070); PR attempt 1 red was not accepted (L3067); DG1N's Hub-GuardedMerge refused on red twice (L3029, L3039). Caveat: HSI1's r2 DONE sentinel was satisfied by the hub moving a line in its own unretained tool (L11), so a steward may score HSI1 lower here | PROOF: a window DONE with a non-success PR or post-merge run

K5 | INSTANCE-FAILURE | "Accepted means that profile's acceptance evidence exists for that exact subject identity" | held for AFPM-MSG-DEBT-1: profile line before work (L3108, 12:10Z, before the 12:11:38Z commits); PR CI and the key both at e02bb0fb / tree d2732828. HSI1: (f) not evidenced by a non-producer at the identity (K1). DG1N: 3 of 4 contract keys on 837c8ce6. Until K5PP-DONE (L3016) the launcher's checker defaulted to `code@r9`, so DGUARDS-1 was keyed through `-K5Exempt` twice (W3) | PROOF: every DG1N contract key, and a non-producer (f) receipt, at the delivered tree

K6 | FIT | "Every acceptance includes a key from an independence class other than the producer's." | AFPM-MSG-DEBT-1: Claude producer, Codex SOL key at the delivered tree. HSI1: Codex SOL key plus PR CI as the register's class-A key, which does not discriminate that change (L10). Receipts hard-code `independenceAttested: false` | PROOF: a window acceptance lacking a Codex receipt or a success PR run at its head

K7 | FIT | "Acceptance and delivery are separate states." | DONE was recorded only after post-merge success (L3019, L3040, L3046, L3081, L3101, L3113). All 6 window merges deliver their PR-head tree. AFPM-MSG-DEBT-1 keeps the two apart in its own records: the key's message leaves delivery to the hub, and `delivery-tree.txt` labels the tree equality hub-credited | PROOF: a window merge whose tree differs from its second parent's

K8 | UNEXERCISED | "Running out of quota means rotating or parking the work that needs inference" | 0 usage-limit or HTTP 429 events in L3003..L3113 (the one "429" substring, L3005, is inside run id 37538429234). The DG1N park was for memory pressure and a planned owner reboot (L3037) | PROOF: a window 429

K9 | INSTANCE-FAILURE | "Resumability is gated at landing seams, before expensive spend" | failed before L3060: the gate (`Test-RolloverReady`) read exit 1 on every routine fire (L3034, L3042, L3046) while spend continued; the cure was four canonical-closer records (L3060-L3063), not a mechanism (CLOSER-GRAMMAR-1 open). After: HSI1's gate files print READY but carry no exit code. AFPM-MSG-DEBT-1's pre-spend gate reads `READY`, `EXIT_CODE=0` (12:10:40Z, key-authenticated); its landing gate file was rewritten after DX hashed it and was observed first `NOT-READY` (`MEMORY-NOTE-STALE`, `EXIT_CODE=1`) and then `READY` (D6) | PROOF: a window dispatch after L3060 with the gate at exit 1

K10 | INSTANCE-FAILURE | "Account parity is verified before any provider work." | 20 window SOL receipts carry 0 account or `probed_under` fields. AFPM-MSG-DEBT-1 retained Claude-surface parity only (D1). Codex-side probes exist for AFPM-MSG-1 and 1N (`parity-codex-1/2.json`, `parity-codex-sol1/sol1rk1.json`) but are not bound into the receipts | PROOF: a window SOL receipt naming the account it ran under

K11 | INSTANCE-FAILURE | "apply to every report a factory makes about itself" | window self-reports that their own records refute:
- D lists three HSI1 deviations, omitting the hub-ci.ps1 edit (L11) and the L17 shortfall (L12);
- DX as first written bound `resume-gate-land.txt` to bytes since overwritten; corrected at 13:23:48Z after the drafter reported it (D6);
- this filing's r3 claimed AFPM-MSG-DEBT-1 as 1 closed subject against S22 (d)'s text (## Corrections);
- AFPM-MSG-DEBT-1's contract states S22 (d) more strictly than its delivery met it (D8);
- bus RECEIPT 3da63d1 overstated DG1N (## Corrections);
- DG1N-PARK named an owner reboot as its resume condition, which did not occur before resume (L3038);
- this filing's r1 claimed HSI1 CLOSED, and its r2 credited HSI1's delivery to a key that finished before the merge (## Corrections).

Self-corrections in window: HSI1's premise (L3066); the typed receipt id at AFPM1N-R1V (L3100) | PROOF: a further window self-report its record refutes, not corrected here

K12 | FIT | "The steward harvests every filing and answers each one." | blob f4a1cc37 HARVESTED (20261002T034934Z-375a810d, HARVESTS.md:527), 40 disposition lines (read at bus 6060669; no commit in 6060669..50ee077 touches `specs/`, `adjudications/` or `tools/review-posture/`) | PROOF: a finding of f4a1cc37 without a disposition

## Profile fields

P:code subject-identity | INSTANCE-FAILURE | "a key on a different subject identity does not transfer" | held for AFPM-MSG-DEBT-1 (one keyed head, delivered at its tree) and for AFPM-MSG-1N (the rebuilt head was re-keyed at the full charter, not carried, L3100). Failed for DG1N: seats carried from d285849a, with no pre-review manifest | PROOF: a pre-review path manifest for DG1N

P:code artifact-store | INSTANCE-FAILURE | "Register-permitted runtime subjects retain candidate, manifest and pre-state bytes" | K5PP's stage and manifest paths exist (presence only). Receipt bytes are overwritten in place: HSI1's hub-ci.ps1 (L11); AFPM-MSG-DEBT-1's `resume-gate-land.txt` after the first DX hashed it, and DX itself (first bytes not retained); the corrected DX reproduces (D6) | PROOF: a window receipt overwritten after a record hashed it, with its first bytes retained

P:code determinism-class | INSTANCE-FAILURE | "flaky suites are declared per test, never silently retried" | AFPM-MSG-DEBT-1's contract A3 declares three flakes by test id and no rerun was used (attempt 1). HSI1 declared by file family (L3). DG1N re-ran `test_dashboard_launcher_background_reuses_existing_supervisor` and `test_canonical_state_audit.py::test_moved_ref_gives_1` to green with no prior declaration (L3029, L3039). No retry was silent | PROOF: a tracked per-test declaration dated before L3029

P:code acceptance-evidence | INSTANCE-FAILURE | "executed or authenticated" | held for AFPM-MSG-DEBT-1: the one contract-required execution receipt (`pr-run-1.json`) was hub-written before the key started and authenticated during its run; discrimination of the change rests on a closed-lineage receipt (D5). HSI1: (f) executed in its declared environment only per the producer's report (K1); precondition misworded (L1); charter fields exceeded (L2); tool changed between rounds (L11). DG1N: narrowed re-key charter | PROOF: a non-producer receipt of (f)'s 3+3 at tree c38dbfb3 authenticated by a key before 08:16Z

P:code independent-key | INSTANCE-FAILURE | "static keys authenticate required execution receipts by digest against the exact subject" | held for AFPM-MSG-DEBT-1: the static key authenticated every contract-required execution receipt (one) at the exact subject. HSI1: the required (f) receipt was not among the seven SOL authenticated. DG1N: the re-key said "Not executed" and cited no digest | PROOF: HSI1's and DG1N's required receipts authenticated by their keys

P:code resource-terminals | INSTANCE-FAILURE | "parked work names its resume condition and the actor who can satisfy it. Owner-only resume conditions are sent through the register's escalation channel" | AFPM-MSG-1's park named a three-Opus lineage panel and was resolved by it (L3090-L3091). DG1N-PARK (L3037) named an owner reboot; DG1N-ADOPT-45510933 (L3038) records it "has NOT happened", yet the work resumed, and the owner-only condition was never escalated: 0 `lane=USER` entries in L3003..L3113 | PROOF: a window park resumed only after its named condition, or a `lane=USER` escalation for it

P:code delivery-target | FIT | "integration branch via the project's landing path" | #200 merged with `--match-head-commit` at e02bb0fb, 9 s after an `ls-remote` master check (L3111); #195 via Hub-MergeClassA at its head (L3081); #198 with `--match-head-commit` (L3098); #193 via Hub-GuardedMerge (named L3029, L3039), HEAD-UP-TO-DATE (L3043) | PROOF: a window PR whose headRefOid differs from its decision-record subject

P:code human-gates | INSTANCE-FAILURE | "anything the project's register lists" | as K2 | PROOF: as K2

P:code budgets | INSTANCE-FAILURE | "window counts of subjects accepted, delivered, parked and closed undelivered" | the instance writes no window count (DX's `window` block is card-scoped). Computed over L3003..L3113 from first brackets: DONE with a 40-hex merge 6 (L3019, L3040, L3046, L3081, L3101, L3113); DONE `merge=none` 1 (L3016); parked or narrowed 4 lineages (L3011, L3054, L3077, L3090-L3091), two of whose successors reached DONE (L3046, L3101); closed undelivered 1 (AFPM-MSG-1N, L3107), its change later delivered (L3113); park-resume 1 (L3037→L3038); accepted-undelivered 0; in flight FS-4b (L3105). The K12-FILE-AB filing card stopped and published nothing (L3086) | PROOF: an instance-written window count

P:code claims | INSTANCE-FAILURE | "leases name the subject, owner, expiry and owned processes" | as K3 | PROOF: as K3

P:code dispatch-preflight | INSTANCE-FAILURE | "the spending tool runs the project's resume gate before dispatch and retains its result… and account-parity evidence" | `Invoke-CodexLane.ps1` runs neither the resume gate nor a parity check. For AFPM-MSG-DEBT-1 the hub ran by hand Claude parity before each dispatch and the gate before first spend, not before the SOL dispatch. The receipts retain only the K5 component and `modelsCacheSha256` | PROOF: a window SOL receipt carrying gate and parity output

## Corrections (K11)

Bus RECEIPT 3da63d1 (RECEIPTS.md:12636-12644, routine hub 1be2a819) says, in its heading, "first change through the full kernel cycle under code@r10". Its body says "Round 2 was 4/4 APPROVE: three adversarial Sonnet seats and SOL (Codex CLI), with SOL re-keyed on the exact merge-parent head" and that the guarded merge "refused once on red (exit 5)". **Corrected:**
- Three of the four keys (seats A/B/C) bound subject d285849a, tree 837c8ce6f8a5ab2a91f762e08ff366ddf4d7a0ed, not the delivered tree c73a1f0e65ff1687100a21c150c3e49d47fb9163. They were carried by a range-diff rule (DG1N-REBUILD, L3036) that is not in DG1N's contract.
- The SOL re-key judged the delta under a narrowed charter (D8E3801B), not the contract, and its reply said "Not executed".
- The class-C owner gate is unresolved, and no parity evidence exists.
- The guarded merge refused on red twice: L3029 HUBCI-RED and L3039 PR-CI-NOT-GREEN (exit 5).
- Its "host load flake" was an undeclared flake at the time it was re-run.

DG1N therefore did not complete the kernel cycle, and "full kernel cycle" is withdrawn.

**This filing's earlier rounds** (not published):
- r1 (raw sha256 2bd61786…) claimed `1 closed end-to-end` for HSI1. Withdrawn (SOL-20261007-040153-083 BLOCKER).
- r2 (raw sha256 b92f12ea…) listed "delivery at that identity" for HSI1 among facts authenticated by SOL r2. SOL r2 completed at 08:15:26Z and merge 35bcd122 landed at 08:16:45Z, so that key could not have authenticated delivery (SOL-20261007-041422-720 BLOCKER, reproduced by seats A and B; stop record `DECISION-K12-FILE-AB-20261007-b92f12ea-stop.json`). Withdrawn: delivery is hub-credited throughout this text.
- r3 (raw sha256 d3a3f28c…) claimed `subjects: 1` for AFPM-MSG-DEBT-1, framing S22 (d) as open. SOL-20261007-082420-386 BLOCKER: (d) is categorical and e02bb0fb was never a tip. Withdrawn: `subjects: 0`, with a separate request.

## Carried forward from blob f4a1cc37 (dispositions at agent-bridge.dispositions.md)

- **§N1 (ROUTED).** Lineage rulings in window: L3012, L3057, L3077, L3091, L3107. Still one profile.
- **§N3 (ROUTED).** No freeze exception. `-K5Exempt` used five times: -190106-125 and -191817-597 (r9 pin, W3), -193858-717 (untracked-install), -040153-083 and -041422-720 (bus filing review).
- **§N4 (ROUTED, owner-authority bench).** Unresolved; four class-C merges in the window (K2).
- **§Untested-1/-2 (ROUTED).** No contribution comparison made.
- **§K12-benches (ROUTED).** `-K5Declaration` landed (K5PP); parity by hand, not by the launcher; `costBound=MEASURED` on all 20 receipts.
- **§AD-0750-d (ROUTED).** No window evidence.
- **§R5-U1 (ROUTED).** HSI1 stayed class A by forbidding a workflow line; AFPM-MSG-DEBT-1 was declared class B (register:84). No ruling.

## Window findings

- **W1 — a re-key narrower than the round charter.** DG1N's only key at the delivered identity judged the delta, not the contract. HSI1 and the AFPM cards fixed one charter for every round. HSI1's residue (L2): a charter naming a receipt path must carry that path as a field from round 1.
- **W2 — a resume gate that always fails is no gate.** From L3034 to L3046 the gate failed on every routine fire on closer-grammar mismatches while spend continued; the cure was four records (K9). It then read NOT-READY on AFPM-MSG-DEBT-1's own DONE line (MEMORY-NOTE-STALE, D6) until a later READY.
- **W3 — a profile revision strands instance gates that pin a literal revision (kernel feedback).** Bus commit d53bac1 (2026-10-02T04:16Z) moved `code` from r9 to r10. agent-bridge's launcher had no declaration parameter and its untracked gate scripts default to `code@r9` (`Test-K5Declaration.ps1:255`, `check_k5_declaration.py:158`), so the first code@r10 dispatch (L3001) was REFUSED (L3003). Cost: two exempt dispatches and a 4-key class-C card (K5PP, 17 min) whose own key was a third.
  - **Proposal (disposition requested; a finding, not a REPLACES):** P:code dispatch-preflight adds "the gate reads the profile revision from the subject's own declaration and compares it exactly; a profile revision lands on the bus with the bus commit instances resolve it from".
- **W4 — the K5 checker matches by substring (kernel feedback).** `code@r1` matches `code@r10` (K5-SUBSTRING-1, L3016), so every window `K5-PASS` is weaker than it reads (L8, D9).
  - **Proposal:** P:code dispatch-preflight requires the declared revision to be compared as a whole token.
- **W5 — execution receipts must be key-authenticated non-producer receipts (kernel feedback).** HSI1 is the failing case: its key authenticated seven hub-run receipts, but the check that discriminated the change ((f), declared environment) existed only as the producer's report. AFPM-MSG-DEBT-1 is the passing case: its contract named one execution receipt, a PR CI transcription, hub-written before the key started and authenticated by sha256 during its run.
  - **Proposal (disposition requested):** P:code acceptance-evidence adds "every contract-required execution check is evidenced by a receipt a non-producer ran, recording the run's environment and exit code, and a key authenticates each such receipt by digest; a producer's report is a locator, never acceptance evidence".
- **W6 — a key authenticates only what existed when it ran (kernel feedback).** This filing's r2 credited HSI1's delivery to a key that finished 79 s before the merge, and its ratifying SOL key refused it (L3086). AFPM-MSG-DEBT-1 built the rule in from the start: its contract labels merge-tree equality "a HUB-CREDITED post-merge fact … not a key claim", and its key's message leaves "pre-merge and post-merge delivery checks" to the hub. The merge, post-merge CI, the decision-record check and the landing gate all post-date that key.
  - **Proposal (disposition requested):** P:code acceptance-evidence adds "a key's credit covers only evidence whose bytes existed before the key started; facts that arise later (merge, post-merge CI, record checks) are credited by name to the actor that established them, or to a key that runs after them".
- **W7 — cut the contract to the arbiter's credit test (kernel feedback).** In this window three closures fired stop or park rules this hub declared itself, not kernel text: K12-FILE-AB (round-2 stop rule, L3086; its trigger was a real misattribution), AFPM-MSG-1 (a BLOCKER parks, L3090) and AFPM-MSG-1N ("never by the hub" plus "a BLOCKER in either round CLOSES", L3107). No key found a product defect in either AFPM card (L3091, L3107); HSI1 counted 0 on its own check (f). The fork ruling then cut AFPM-MSG-DEBT-1's contract to S22 (a)-(e), made parity, the gates and post-merge facts hub-credited health evidence, and put the earlier kit's self-added items out of scope. Measured: AFPM-MSG-1 and 1N ran 04:31-07:06 CDT and delivered nothing; AFPM-MSG-DEBT-1 ran from declaration (12:10Z) to merge (12:43:41Z) in about 34 minutes. The cost is visible in this filing: D1, D5 and D6 are health residue the lighter contract no longer stops on.
- **W8 — deliver by fast-forward so (d) passes strictly (lesson; kernel feedback).** AFPM-MSG-DEBT-1 lost (d) to a merge commit while its keyed head was fast-forwardable (D8; whether a fast-forward landing was permitted was not examined). **Lesson:** when master equals the keyed base, land the keyed commit itself as the new tip (fast-forward), so the keyed commit is the pushed tip; if master moved, the implementer rebuilds and the key re-keys.
  - **Proposal (disposition requested):** P:code delivery-target says which form witnesses delivery at identity: the keyed commit as tip (fast-forward), or also a merge whose tree equals the keyed tree.
  - **Proposal (disposition requested):** the profile states which acceptance clauses decide credit (the S22 tests), and says that any further rule a contract adds is health evidence, not a stop condition, unless the register lists it.

## Untested

§R6-U1 — Whether K10's "Account parity is verified before any provider work" requires, for a single-surface provider (Codex), a probe of the account the key ran under (D1). PROOF: a steward reading, or a Codex `probed_under` field accepted by an arbiter.

§R6-U2 — Whether a key's in-contract ruling that a misworded contract check is satisfied in intent counts as "the same contract judg[ing] every round" or as an amendment by the key (HSI1 L1). PROOF: an arbiter's reading on HSI1.

§R6-U3 — Whether a static key's digest authentication of a hub-written transcription of a CI run (`pr-run.json`, `pr-run-1.json`) satisfies "authenticate required execution receipts by digest" when the arbiter can re-read the run itself (L5, D2). PROOF: an arbiter's reading on AFPM-MSG-DEBT-1.

## Request to the arbiter (separate from the count)

agent-bridge asks for a ruling on whether **tree-form delivery** witnesses S22 (d): merge^{tree} equals the keyed tree; the keyed commit is the merge's second parent; master was unmoved from the keyed base, checked within 60 s before merging; the merge is pinned with `--match-head-commit`. AFPM-MSG-DEBT-1 is the instance (d2732828; 5aa853a5^2 = e02bb0fb; master c4340515 at 12:43:32Z; merged 12:43:41Z). The profile defines identity as the tree "as it will be delivered, after any merge with the delivery target"; the S22 text names the commit, and S1 (C5) was not credited. **Under the text as written AFPM-MSG-DEBT-1 counts 0, and this filing claims 0.** If the arbiter accepts the tree form, it would count 1 by a later arbiter confirmation, not by this filing. PROOF: an arbiter's ruling on AFPM-MSG-DEBT-1.

## Authorship

Drafted from read-only sources by a Claude (Opus) drafter seat for hub 1b426829, card KR4-ADOPT, on 2026-10-07. Round 4 revises r3 (d3a3f28c…) per its quorum (SOL BLOCKER accepted by the hub: `subjects: 0` plus a separate request; seats B and C findings applied). r3 started from r2 per the stop record's carryForward. Sources, claims and the r3 disposition table: `evidence/KR4-ADOPT/FILING-ANALYSIS-r3.md`. Bus 50ee077 was read locally, no fetch; the drafter wrote nothing to the bus. The hub lands this text wholesale on `review/agent-bridge-kernel-2026-10-07` after ratification (R7); the steward harvests it. Any `specs/agent-bridge.md` block or RECEIPTS/TRAPS rows are the hub's separate decision against freshly fetched bus master (R8.1).
