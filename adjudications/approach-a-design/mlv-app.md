project: mlv-app
subject: specs/conjugal-approach-a-v7.4.md (blob 11af78fa1aec05076b226e1fb59888fd6cf7bb4e)   test_bench: C:\!Layi Wkspc\MLV-App @ 9c63151e
providers: claude(fable,opus,sonnet,haiku) codex(sol,luna,astra) — all seven ids sentinel-verified on this machine 2026-09-14T18:05Z
seats: full conjugal-standard roster dispatched; effort high (codex `model_reasoning_effort=high`), claude `--permission-mode plan`
posture: conjugal-standard-PARTIAL (12/17 lanes; missing: Arbiter 0/1; Consolidator 0/1; Classifier 0/3)
cross_family: validated
rubric_id: b2f5862e9c0990d0e69e96862fba7ab4cc5e263151679ac336ab429187341c45
panel: 80.88 over 8/8 seats, 2 families (claude, codex), spread 20.17

<!--
Honest labelling, per RULINGS R9 and lane-orchestrator §3/§5. The posture line above is copied
verbatim from `tools/review-posture/review_posture.py posture`; it is NOT the conjugal-standard
posture. The Arbiter lane (codex/astra) returned a complete arbitration TWICE — surviving findings,
lint rulings and a losers table — and BOTH times stopped at the end of the ordered output contract
without emitting `LANE-COMPLETE`. The tool therefore scores it DID-NOT-RUN, which gated the
Consolidator and the Classifier swarm. No sentinel was manufactured. The consolidation below is the
ORCHESTRATOR's, not the Consolidator lane's, and is marked as such wherever it matters.
-->

## Design findings

§1 | "oversized evidence is a content-addressed blob referenced by payload" | An OID inside payload text is not a git reachability edge. Bench: 353 unreachable blobs already listed by `git fsck --unreachable`; `gc.auto` and `gc.pruneExpire` both unset; 4,255 loose objects; 10,918/106,363 `.claude-state` ledger lines exceed 3500 B (10.26%), max line 4,342,710 B in `closeout/audits/audits.jsonl`. | REPLACES: "oversized evidence is a content-addressed blob referenced by payload" to "oversized evidence is a blob anchored by a ref under `refs/oracle/journal-blob/<lane>/<seq>`, retained under the cursor invariant" | PROOF: anchor an oversize payload only from a frame in the bench object store, `git gc --prune=now`, then replay through the acknowledged head.

§4 | "every live floor in `helper_floors` sweeps outstanding requests every `15 min (clock_domain=real)`" | Fallback cannot meet a 15-minute p95 after 120 s helper and adopter executions. Bench `closeout.config.json:283` sets `finalizeTimeoutMs: 1800000` and `:285` `adapterHeartbeatSeconds: 30` — the working system supervises two orders of magnitude tighter than the sweep it would have to fall back on. | REPLACES: "every live floor in `helper_floors` sweeps outstanding requests every `15 min (clock_domain=real)`" to "every live floor sweeps outstanding requests every 30 s (clock_domain=real)" | PROOF: kill immediate dispatch, inject requests uniformly across sweep intervals, require READY-to-adoption p95 at most 15 min.

§14 | "The document must start with `# Approach A v7.4` and contain at most 13,000 whitespace-delimited words" | Orchestrator re-derivation, not a lane finding. Both clauses turn on whether the bus header is part of "the document", and it is 9 words either way: whole file = 13,009 words and starts with `<!-- bus header:`; from line 3 = 12,972 words and starts with the required heading. §14 is self-referential and admits both readings, so Scenario 67 cannot be evaluated as written. | REPLACES: "The document must start with `# Approach A v7.4`" to "Excluding any transport header, the document must start with `# Approach A v7.4`, and that same excluded-header body is what the 13,000-word cap measures" | PROOF: run the §11 row 67 audit against both readings of the current file; exactly one passes, which is the defect.

The following two were kept by one of the two arbitrations and rejected as a loser by the other. Neither is filed as settled; both are recorded with the disagreement.

§5 (arbitration 1 KEPT / arbitration 2 REJECTED) | "The reducer admits the configured safety-eligible executor count, `executors=5 (provisional)`, from the first real minute" | Uncalibrated fan-out multiplies prompt deaths. Bench `tools/coordination/Invoke-Workstream.ps1:9-20` records one dispatch dying `prompt_too_long` after 1,956,254 cache-creation tokens and $51.61; the identical card at run 2, reshaped, cost 40,759 tokens and $1.18. | REPLACES: "from the first real minute" to "after bounded prompt/input preflight; excess work remains queued" | PROOF: offer five oversized bench prompts; none may launch beyond qualified context and slot capacity. | COUNTER (arbitration 2): §5 expressly requires five safety-eligible admissions subject to seat feasibility and Scenario 59 requires five subjects to start; one oversized bench prompt does not establish that this fan-out exceeds capacity.

§1 (arbitration 2 KEPT / arbitration 1 REJECTED) | "Only changed dependent subjects are recomputed; after six dependency losses they are split out so independent subjects publish." | Bench `.git/packed-refs` holds 108 refs (27 heads), so `pack-refs` has already run with `gc.auto` defaulted. Once `pending/*` and `claim/*` pack, each emptying or retirement rewrites `packed-refs` under one repo-global lock, serializing unrelated subjects. | REPLACES: "so independent subjects publish" to "so independent subjects publish, with `refs/oracle/*` excluded from pack-refs and `gc.auto=0`" | PROOF: pack `refs/oracle/*` in a bench clone, run Scenario 49's 50 racing claims, count `unable to lock` on unrelated subjects. | COUNTER (arbitration 1): advancing a pending ref to an empty-set object does not require deleting a packed ref.

## Untested

§4 | "This predicate is the only readiness (Scenario 42a)." | §4's adoption transaction adds conditions absent from `ready_effective` — closed-gate OID, empty `pending/<lane>/<S>` and `pending/reducer/<S>`, unchanged dependency gate OIDs — so a MISMATCH admitted while a gate is CLOSED leaves the predicate true. No bench gate ledger reproduces this. | REPLACES: "This predicate is the only readiness" to "`ready_effective` additionally requires empty pending refs for the pinned challenger membership and `reducer`, and the gate at its captured generation" | PROOF: admit a MISMATCH to `pending/reducer/<S>` while the gate is CLOSED, then evaluate the predicate alone. | Kept by both arbitrations.

## Cross-section contradictions

Both independent arbitrations ruled identically on all nine lint items: six from LINT-CLAUDE dropped, LINT-CODEX 1 KEPT, LINT-CODEX 2 and 3 dropped.

§0 vs §§4/6/13 | KEPT. §0 "requires exact genesis membership and checker digests" and fails "any swap, omission, duplication or mislabel"; §4 "Replacing an unavailable principal or checker increments only attest_epoch"; §6 "enrolling an attestation helper (§4) is a QUALIFY"; §13 requires a §6 QUALIFY to enroll a replacement after a family loses its helpers. A newly qualified replacement checker necessarily differs from the exact genesis digests §0 demands at every amendment. | Winner (both arbitrations): permit the explicitly authorized §6 replacements. | This defeats LINT-CLAUDE's blanket `NONE`.

LINT-CLAUDE returned `NONE` over six section pairs. Recorded as a lane result, not as a conclusion — it is overturned by the item above.

## Arbiter losers

Every counterexample below was checked by the orchestrator against the subject text; each rests on a premise the subject actually contains (`one shared Windows checkout, C:\code\Conjugal`; `acceptance_spec_sha`; `An item is one subject first receiving an authorized ADOPTED record for its exact candidate`; `four concurrent clones with overlapping reruns and interrupted recovery` — all verified verbatim). No loser was rejected on a premise the subject lacks.

| defect class | loser | counterexample | orchestrator note |
|---|---|---|---|
| Reducer identity scope | DESIGN-SCOPE: one reducer per ref store, not per checkout | §0 specifies one shared checkout; Scenario 34 tests aliases of that checkout, so seven linked bench worktrees are outside the stated topology | rejection sound on scope; the bench measurement itself (7 worktrees, one `.git`, worktree `.git` a 61-byte file) reproduced exactly |
| Journal byte preservation | DESIGN-SCOPE: `core.autocrlf` corrupts frames | §1 prescribes no filtered file ingestion; `hash-object --stdin` without `--path` applies no filters, so a tracked-Markdown CRLF comparison does not demonstrate journal-blob conversion | sound. The bench measurement held (`CLAUDE.md` worktree `3855db6` vs blob `f76eb93`, 169 CRLF lines, system gitconfig `core.autocrlf=true`); it just does not bind §1 |
| Executor concurrency | DESIGN-SCOPE: per-executor worktrees at `base_commit_oid` | §2 permits disjoint path allocations and never requires distinct bases; five subjects sharing a base can edit disjointly | sound |
| Reducer throughput | DESIGN-SCOPE: derive a larger `N_batch` | under the finding's own serial-read assumption, larger batches raise service time proportionally, leaving capacity near 22.7 rows/s | **the remedy is refuted, the defect is conceded.** Both the loser and the counterexample land at roughly 20-23 rows/s against Scenario 20's stated floor of 20 rows/s. Orchestrator re-measurement on the bench: 50 ms per `git show HEAD:CLAUDE.md` (10 reps) and 34 ms per `git rev-parse HEAD` (20 reps) — at one read per row, 100 rows = 5.0 s, i.e. 20 rows/s, no headroom at all. Recorded as a live throughput exposure that this run did not resolve |
| Product verification responsibility | DESIGN-VERIFY: require hosted tests and CodeQL in A checks | §2 binds subject-specific acceptance through `acceptance_spec_sha`; the subject does not adopt MLV-App's five hosted surfaces as its acceptance contract | sound. Bench citation `closeout.config.json:1166-1172` (`content-self`, `content-stranger-1`, `content-stranger-2`, `hosted-tests`, `hosted-codeql`) verified exact |
| Adoption semantics | DESIGN-VERIFY: bind adoption to an integrated target commit | §§4/9 define delivery as authorized adoption of the exact candidate; no target-merge contract is specified | sound. Bench citation verified: `brokered_closeout.py:6896` builds an integration worktree and `:6908` merges `--no-ff` |
| Reviewer independence | DESIGN-VERIFY: commit-then-reveal vote commitments | §§3/7 enforce distinct eligible signing lanes under a single-fault model; simultaneous dispatch does not establish shared sessions | rejection rests on the subject being **silent** on vote visibility. The gap is real even though the finding overstated it; bench citations verified (`docs/autonomous-golden-authority.md:32` mandates commit-then-reveal, `tools/repo_hygiene/test_candidate_acceptance.py:236-248` raises `duplicate-review-session`) |
| Initial admission | DESIGN-VERIFY: qualified-slot preflight | §5 requires five safety-eligible admissions and Scenario 59 requires five subjects to start | arbitration 1 KEPT this; see the disagreement recorded under Design findings |
| Test parallelism | DESIGN-VERIFY: `P_par=3`, not 4 | §10's `P_par` counts concurrent per-row fixture clones and Scenario 27 exercises four; an agent-remediation cap is not a clone cap | sound. Bench citation `closeout.config.json:1011` `"maxParallelAgents": 3` verified exact |
| Phase arithmetic | LINT-CODEX 3 | the §10-selected §11 rows total 77,100 + 10,800 = 87,900 s, already including all six MIXED rows | **settled by three independent derivations.** Orchestrator (Python, over the §11 table) and both arbitrations (PowerShell) agree: 1d = 33,240 s = 9.23 h over 49 STUB rows; 1d-extended = 87,900 s = 24.42 h over 14 SUBSTRATE (77,100 s) + 6 MIXED (10,800 s). Both §10 literals reproduce exactly. 98,700 s double-counts MIXED |
| Envelope fencing | LINT-CODEX 2 | §4 provides state-CAS envelope recovery outside SEAL while retaining stronger fences for the terminal SEAL transaction | sound; both quoted rows verified verbatim |
| Checker replacement consistency | LINT-CLAUDE: overall `NONE` | a newly qualified checker permitted by §§6/13 necessarily differs from §0's exact genesis digests | sound |

## Panel

Blinded, subject-only, 8 seats, both families. The tool recomputed every composite from the six dimension numbers; no seat's self-reported average was used.

| seat | family | Timeline | Contract | Cross-Family | Autonomy | Throughput | Risk | composite |
|---|---|---|---|---|---|---|---|---|
| panel-sonnet1 | claude | 78 | 84 | 91 | 88 | 82 | 90 | 85.50 |
| panel-fable | claude | 82 | 80 | 90 | 88 | 84 | 87 | 85.17 |
| panel-sol | codex | 79 | 76 | 89 | 91 | 85 | 90 | 85.00 |
| panel-sonnet2 | claude | 78 | 79 | 90 | 86 | 83 | 89 | 84.17 |
| panel-opus | claude | 82 | 80 | 89 | 84 | 79 | 85 | 83.17 |
| panel-sonnet3 | claude | 75 | 74 | 87 | 84 | 80 | 88 | 81.33 |
| panel-astra | codex | 76 | 70 | 84 | 80 | 74 | 80 | 77.33 |
| panel-luna | codex | 60 | 42 | 82 | 78 | 58 | 72 | 65.33 |
| **composite** | | | | | | | | **80.88** |

Spread 20.17. The dissent is Contract Completeness: `luna`, the Codex implementer lens, scored it 42 against a 74-84 band from every other seat. Its stated reason is that 1b-build covers custody, two checkers, crash recovery and the quota adapter inside "16–24 engineering hours (provisional)" with no measured critical path, and that the quota adapter has no concrete CLI versions, JSON pointers or fixtures despite requiring a "versioned per-provider, per-CLI-version mapping". Both quotes verified verbatim. Cross-Family Safety is the one dimension no seat scored below 82.

All 24 panel blocker quotes were checked verbatim against the subject with `grep -F`; all 24 matched. Selected blockers, seat-stripped:

- "floor" is load-bearing (24 occurrences: helper starts, wakes, sweeps) yet defined nowhere; §0 says only "floors able to start each helper; hosting confers nothing".
- `P_pub` is "derived, never literal, from measured `clock_domain=real` durations" but has no provisional value before Scenario 68, so the 1b-build/1c reducer cannot compute it.
- BLOCKED-CAPACITY wakes only on "a successful ROLE_CAPACITY_PROBE, LATCH_CLEARED, ROTATION_COMPLETE or a policy amendment"; ATTEST_REHABILITATED and V_REHABILITATED are omitted, so helper-loss blocks never self-clear.
- Joint allocation consumes "Q_l the lane's remaining reserved service microseconds" but no section says when reservations decrement or release, so §3 load is uncodeable.
- "T_m = max(48, 100 / (m × b)) h" sizes Phase 2 windows from `b`, unmeasured until Scenario 63-0's 336 h baseline completes.
- "A private index builds the state tree" has no OS mechanism or cleanup contract, though relay and reducer both rely on it for crash-safe handoff.
- Header claims "Round 15 composite 83.7, stopping rule fired" while §12's ledger row reads `| R15 | Same shape, J1–J10 (this document) | pending | — |`. **Orchestrator: both strings verified verbatim; this is a live internal contradiction in the subject.** The panel's own 8-seat composite here is 80.88, but under a different `rubric_id` and so non-comparable by §12's own comparability rule — it neither confirms nor refutes 83.7.

## Classifier consensus

**Did not run.** The Classifier swarm (haiku x3, 2-of-3) is stage D and was gated behind the Consolidator, which was gated behind the Arbiter sentinel. There is therefore **no TEXT/DESIGN split, no GROUNDED vote, no must-fix consensus and no STOPPING determination** in this filing. That slice went unreviewed; nothing here should be read as carrying classifier standing.

## Provenance

| stage | lane | family | model | rc | bytes | sentinel |
|---|---|---|---|---|---|---|
| A | design-scope | claude | claude-opus-5 | 0 | 4779 | RAN |
| A | design-verify | codex | gpt-5.6-sol | 0 | 3855 | RAN |
| A | lint-claude | claude | claude-haiku-4-5-20251001 | 0 | 2071 | RAN |
| A | lint-codex | codex | gpt-5.6-luna | 0 | 935 | RAN |
| B | arbiter (attempt 1) | codex | gpt-6-astra | 0 | 8554 | **DID-NOT-RUN** (no `LANE-COMPLETE`) |
| B | arbiter (attempt 2) | codex | gpt-6-astra | 0 | 7997 | **DID-NOT-RUN** (no `LANE-COMPLETE`) |
| B | panel-fable | claude | claude-fable-5 | 0 | 700 | RAN |
| B | panel-opus | claude | claude-opus-5 | 0 | 754 | RAN |
| B | panel-sonnet1 | claude | claude-sonnet-5 | 0 | 612 | RAN |
| B | panel-sonnet2 | claude | claude-sonnet-5 | 0 | 683 | RAN |
| B | panel-sonnet3 | claude | claude-sonnet-5 | 0 | 757 | RAN |
| B | panel-astra | codex | gpt-6-astra | 0 | 640 | RAN |
| B | panel-sol | codex | gpt-5.6-sol | 0 | 673 | RAN |
| B | panel-luna | codex | gpt-5.6-luna | 0 | 668 | RAN |
| C | consolidator | claude | claude-fable-5 | NONE | 0 | **DID-NOT-RUN** (gated by the arbiter sentinel) |
| D | classifier-1/2/3 | claude | claude-haiku-4-5-20251001 | NONE | 0 | **DID-NOT-RUN** (gated by stage C) |

No stage was reused; `--from` was not used. Stage A dispatched 18:07:24Z, done 18:13:28Z; stage B done 18:17:39Z; arbiter attempt 2 dispatched separately on its identical tool-generated prompt. Raw lane outputs and prompts stay outside the bus (Law 4).

**What the orchestrator re-measured itself** (every number below was reproduced on this machine, not taken from a lane): the 1d and 1d-extended manifest sums; the §14 word counts; the header-vs-§12 `R15` contradiction; all 37 quoted phrases across stage A and the panel; and, on the bench, `git worktree list` (7), `--git-common-dir`, the 61-byte worktree `.git`, `core.autocrlf` origin, `CLAUDE.md` filtered and unfiltered hashes, the CRLF line count, loose-object and packed-ref counts, `gc.auto`/`gc.pruneExpire` absence, unreachable-blob count, the full `.claude-state` ledger line census, the max ledger line length, `git show`/`rev-parse` latency, and every cited line in `closeout.config.json`, `brokered_closeout.py`, `autonomous-golden-authority.md`, `test_candidate_acceptance.py` and `Invoke-Workstream.ps1`.

**What was NOT re-measured, and inherits no standing from the above:** every PROOF scenario (none was executed — they are proposed falsifiers, not results); the claim that `pack-refs` contention actually serializes unrelated `refs/oracle/*` subjects; and the assertion that a filtered `hash-object -w` would in fact be used for journal blobs.

**Two preflight defects found and worked around; both are reported to the bus because they silently corrupt other runs:**

1. `~/.claude/machine-inventory.yaml`, regenerated by PROMPT A at 12:32:52-05:00 today, recorded `codex: available: false` with all three ids `UNVERIFIED -- not dispatchable`. That was a **false negative**. `%APPDATA%\npm\node_modules\node\bin\node` on this machine contains the literal text `This file intentionally left blank` and is marked executable, so the stock `codex` Git Bash shim's `[ -x "$basedir/node" ]` branch execs it and every `codex` call from bash exits 127. The `claude` shim execs a native `.exe` and is unaffected, which is why only the Codex family looked dead. With a local PATH shim bypassing it, `probe-machine-inventory.sh` verified all seven ids by sentinel challenge. **Had this not been caught, this run would have been filed as a one-family degraded review with `cross_family: NO-CROSS-FAMILY-VALIDATION`, and the inventory's own `available: false` would have looked like the honest answer.**
2. `tools/review-posture/run.sh` cannot run from a path containing a space: `PY="python $HERE/review_posture.py"` is unquoted, so from `C:\!Layi Wkspc\...` Python receives `C:\!Layi`. `eval "$($PY ids)"` then swallows the failure — the command substitution is empty and `eval ""` returns 0 — so the runner proceeds with **no `MODEL_*` values at all**. Worked around by running from a space-free worktree; the guard `|| exit 2` does not fire and needs to.

Also noted: the machine inventory's probe command for the Claude family names `tools/check-cli-auth.py`, which does not exist in this repository.
