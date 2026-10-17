schema: cos-feedback.v1
project: conjugal
repo: layibabalola/Conjugal
pr: 6
head: 0d3dbd282d04abeafe53ba2915ef67c11c3ad3d3
reviewed_utc: 2026-10-17T03:38:37Z
event: pr-pushed
verdict: not-merge-ready
ci_summary: health FAIL, suite IN_PROGRESS on 0d3dbd28 (run 38999372530); master 04437e61 also FAILURE (likely pre-existing jq install step; job log not readable, shared REST quota exhausted). MERGEABLE. Legs Claude 0 / Codex 0 on tip.
risk: HIGH-RISK by CoS judgement (agent entry instructions AGENTS.md + CLAUDE.md + session-start script tools/cos-open-asks.sh; no CI workflow or ruleset change)
reviewer: CoS (self-review: the CoS seat authored this PR; Layi's review is the merge gate)
post_merge: false
asks: https://github.com/layibabalola/Conjugal/pull/6#issuecomment-6229136424

# conjugal #6 CoS response duty + open-ask check (owner-authorized), r4 (commit says r3.1)

r4 makes legacy asks close on any later valid ACK/DISTINGUISH, lets one comment carry CLOSED and CoS-ASK, checks the no-reply phrase only in the last 400 chars, picks closed PRs by updatedAt, and adds a --classify fixture mode. The script (sha256 a63e582a) is byte-identical to doctrine #87 34698e2b, adobe #3 d42ac83b, Cloudvore #7 ab8def27, context-ultra-salesforce #109 2576514b, agent-bridge #240 d077f538, AdversarialLLM-ClaudeCode #277 b0479dbf. CoS ran it on Conjugal (exit 0, 0 open) and ran --classify on 5 synthetic bodies; MLV-App and agent-bridge re-runs hit HTTP 403 (shared layibabalola REST quota 0/5000 at 03:36Z, reset ~04:24Z), so the ACK's "MLV-App 4 legacy opens" claim is unverified.

## r3 disposition
- B1 over-corrected (new B1). B2 addressed for the CoS-ASK shape (verified CLOSE + ASK rows); legacy shape residual is I6. Quoted no-reply fix verified. I1-I4 not addressed; N1, N2 carried. r3 ask 6229083497 closed by the CLOSED line in review 6229136424.

## Blockers
- B1 AGENTS.md:86, tools/cos-open-asks.sh:74: any later ACK on a thread closes every earlier legacy ask there. Live miss: ACK 6229115728 cites only the already-closed r2 ask 6228571489 yet closes r3 ask 6229083497, so the scan says 0 open with r3 B2, I1-I4, N1, N2 unanswered. Fix: grandfather only legacy asks before a fixed r3 effective time; later legacy asks need citation; add a committed fixture.

## Improvements
- I1 (carried) PR body still r1.
- I2 (carried) AGENTS.md:78 depends on open doctrine #87 (master 6c8ba2c has no script); state merge order.
- I3 (carried) script:60 commit-comment scan still `|| true`.
- I4 (carried) AGENTS.md:80, script:74 CoS-ASK id unformatted, substring match.
- I5 new script:49-60: scan shares the one 5000/h REST budget; API error exits 1 like "asks open" with no OPEN or summary line (seen live on MLV-App and agent-bridge). Exit 2 + ERROR line; cut cost (GraphQL per repo or incremental). Share of exhaustion caused by the script not measured.
- I6 new script:38: legacy-shaped CoS review with CLOSED: but no CoS-ASK: is not an ask (verified); classify it or make the rule explicit in AGENTS.md:80.

## Nits
- N1 (carried) CLAUDE.md:81-83.
- N2 (carried) script:63 eta_re loose.

## Process
- Commit message claims "fixture test" but no fixture file is committed; --classify needs a jq binary Conjugal CI cannot install. ACK says CI jq failure is moot but health is still red on this head.

## Prevention
- Re-run the scan on the PR itself and one live sibling after any response-duty change and confirm every unanswered CoS ask still shows OPEN. Applies to doctrine #87 and all six siblings.

## Ask
- ACK ask: https://github.com/layibabalola/Conjugal/pull/6#issuecomment-6229136424 (CoS-ASK: conjugal-6-r4; posted 2026-10-17T03:38:37Z; follow-up due 24h later). Addressed to the author lane (CoS).
- CLOSED: https://github.com/layibabalola/Conjugal/pull/6#issuecomment-6229083497 (r3, superseded; CLOSED line in 6229136424).

## Notes
- Soft note: Conjugal master CI still red (04437e61); needs its own fix card.
- No Dot or Iverson advisory on this PR yet.
