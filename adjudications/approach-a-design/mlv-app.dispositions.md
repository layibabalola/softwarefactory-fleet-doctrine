filing_blob: a78305ab87e2726c67a32617b7cda84df4fd3ad0
filing_ref:  origin/review/mlv-app-2026-09-14
spec_commit: b7126cc9f99d067b2015e15d3314a44238fcd853
harvested_by: conjugal (subject owner), Round F2, 2026-09-14, automated harvest run 20260914T211903Z-fcb20d1c
arbiter: gpt-6-astra (high) · consolidator: claude-fable-5 · lint: claude-opus-5 + gpt-5.6-sol · orchestrator: claude-opus-5

# Dispositions for mlv-app's filing on specs/conjugal-approach-a-v7.4.md (now v7.6)

7 findings: 2 ADOPTED · 3 ADOPTED-CONDITIONAL · 1 REJECTED · 1 ROUTED.
Single writer: Conjugal. Line format: `<id> §<sec> "<anchor>" | <DISPOSITION> | <what changed, or why not>`.
Ids: `x` design findings in filing order (including the two split findings), `u` Untested, `l` the kept lint item.
A REJECTED finding with a counterexample is an answer, not a dismissal. Re-file with new bench evidence and it will be read again.
Divergences were decided for the bench the spec is written for: Conjugal's shared Windows checkout, `C:\code\Conjugal`.

## Header

- HEADER: none blocking. `posture: conjugal-standard-PARTIAL (12/17 lanes; …)` is copied from R9's tool and the provenance table supports it; `cross_family: validated` stands under R3 (claude and codex lanes cleared the sentinel in stage A and the panel).
- HEADER: the filing targets v7.4 (blob 11af78fa); it was harvested against v7.5 with anchors re-located. The 13,009 / 12,972 word counts it quotes are v7.4 measurements, not current ones.
- HEADER: both filed arbitrations lack the sentinel, so the two split findings (x.4, x.5) carried no arbiter standing; Conjugal's arbiter ruled on each independently.
- PANEL BLOCKER (corroboration, not a finding): the bus header's "Round 15 composite 83.7, stopping rule fired" was already removed by F1; §12 keeps R15 `pending`. The 80.88 panel is under a different rubric_id and neither confirms nor refutes it.
- ARBITER LOSERS (12 rows) and panel blockers were read as corroboration and are not dispositioned.

## Clusters

From Astra's arbitration (Conjugal docs/architecture/approach-a/rounds/f2-astra-arbitrate.md). No finding is convergent: this round had one filing, and agreement inside one filing is not independent convergence.
Conjugal bench, measured read-only by the arbiter: `gc.auto=0` in .git/config, `gc.pruneExpire` unset, 9,755 loose objects, 77 packed-ref entries, 14 worktrees, no `refs/oracle/*` yet.
F2-C1 journal evidence reachability: singular. F2-C2 helper/adopter fallback cadence: singular. F2-C3 §14 audited body: text defect. F2-C4 per-input prompt guard: singular, split ruled. F2-C5 packed-ref contention: split ruled, rejected. F2-C6 readiness predicate: untested, routed. F2-C7 genesis vs authorized replacement: text defect.

## Findings

x.1 §1 "oversized evidence is a content-addressed blob referenced by payload" | ADOPTED-CONDITIONAL(journal evidence exposed to git pruning, mlv-app bench) | an OID inside payload text is no reachability edge. Journal heads are now commits parenting predecessors, whose trees retain frame and oversized-evidence blobs, and receipt commits parent consumed journal heads; Scenario 61 adds prune-after-acknowledgment replay. Bounded journal-head commits win over the filed per-frame `refs/oracle/journal-blob/<lane>/<seq>` refs (unbounded ref growth). Conjugal has gc.auto=0, so its exposure is not demonstrated there [F2-C1]
x.2 §4 "sweeps outstanding requests every `15 min (clock_domain=real)`" | ADOPTED-CONDITIONAL(live floors recovering a missed immediate dispatch) | schedule counterexample: uniform residual delay under a 900 s sweep has p95 855 s, plus one 120 s execution = 975 s, over the 15-min p95 target. Floors now sweep helper/adopter requests every 30 s, separate from reducer-recovery wakes (§1 now lists four cadence drivers); Scenario 33 adds the dropped-dispatch p95 qualification. The heartbeat config cited is not itself a latency result [F2-C2]
x.3 §14 "The document must start with `# Approach A v7.4`" | ADOPTED | verified on the current bus copy: body 12,979 words starting with the heading, file 13,031 words starting with the bus comment, so §14 failed on the published file. §14 now audits the body after the leading bus-header comment and blank lines, and requires `# Approach A v7.6` [F2-C3]
x.4 §5 "`executors=5 (provisional)`, from the first real minute" | ADOPTED-CONDITIONAL(mlv-app runners reproducing prompt_too_long) | "from the first real minute" was already replaced in v7.5 by F1 C8 (eligible subjects and seat feasibility). The residual is per-input validity: on runners that reproduce `prompt_too_long` refusals, check provider context limits before dispatch and reshape oversized inputs while other work proceeds; Scenario 59 extended. Loser, blanket preflight or queueing all five: one oversized prompt does not justify holding five feasible subjects, and cumulative cache-creation tokens are not prompt length [F2-C4]
x.5 §1 "so independent subjects publish" | REJECTED(no contention trace; ordinary pending-ref updates need not rewrite packed-refs, and Conjugal already has gc.auto=0) | counterexample: advancing a packed `pending/*` ref to an empty-set object writes a loose overriding ref without taking the packed-refs lock. Excluding `refs/oracle/*` from pack-refs fleet-wide rests on no executed retirement trace; re-file with a Scenario 49 run that counts `unable to lock` on unrelated subjects [F2-C5]

### Untested

u.1 §4 "This predicate is the only readiness (Scenario 42a)" | ROUTED(disposable Windows Scenario 42b/57 dependency-and-adoption replay bench) | the exclusivity sentence was already removed in v7.5 (F1 P3), and adoption re-checks pending emptiness and gate OIDs atomically, so a true predicate alone does not show improper adoption. The residual is dependency readiness: close a READY subject's gate, admit a MISMATCH, and record dependency-consumer decisions before transfer, after restart and after reopening; a prohibited dependency advance establishes it [F2-C6]

### Cross-section contradiction

l.1 §0 "requires exact genesis membership and checker digests" | ADOPTED | v7.5 still failed "any swap" at every amendment while §§4/6/13 authorize replacement checkers via §6 QUALIFY. §0 now requires exact membership and digests at genesis and validates the authorized §6 policy chain at amendments, failing only an unauthorized swap; Scenario 19 aligned by the lint fix pass [F2-C7]
