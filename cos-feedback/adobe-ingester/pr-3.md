schema: cos-feedback.v1
project: adobe-ingester
repo: layibabalola/adobe-document-cloud-ingester
pr: 3
head: d42ac83b77ffb3c016cbe0000c338efe93c01f87
reviewed_utc: 2026-10-17T03:38:33Z
event: pr-pushed
verdict: not-merge-ready
ci_summary: No checks configured on this repo; MERGEABLE/CLEAN, 0 behind main 9cb4d95. Legs Claude 0 / Codex 0 on tip (docs-only owner PR; Layi's review reserved as the merge gate).
risk: docs only plus helper script tools/cos-open-asks.sh (no CI workflow, ruleset or product code)
reviewer: CoS (self-review: the CoS seat authored this PR)
post_merge: false
asks: https://github.com/layibabalola/adobe-document-cloud-ingester/pull/3#issuecomment-6229136308

# adobe-ingester #3 CoS response duty + open-ask check (owner-authorized), r3.1

r3.1 fixes all r3 items: the no-reply exclusion reads only the last 400 chars and explicit ask phrases win; CLOSE and ASK rows are emitted independently; legacy asks close on any later valid reply; the closed-PR window sorts by updatedAt; double blank lines removed. Script blob db11507, byte-identical to doctrine #87 34698e2b, agent-bridge #240, AdversarialLLM-ClaudeCode #277, context-ultra-salesforce #109 and Cloudvore #7. CoS ran it on this repo (3 PRs, 0 OPEN, correct: ask adci-3-r3 answered by valid ACK 6229115578), ran the doctrine #87 fixture through --classify (5/5 rows match expected), and, because the shared account's REST core quota hit 0/5000 at 03:36Z, ran the script's classify jq and closure loop offline on GraphQL pulls of MLV-App #437, #432, #466, #457, #474 (21 legacy asks, all close, including the 7 flagged at r3). Doc edits read only.

## Blockers
- B1 tools/cos-open-asks.sh:59-60: commit-comments call ends in `|| true`, so API errors silently drop all commit-comment asks (the only home for asks on direct pushes, per Layi's Conjugal ruling) with exit 0. Same as doctrine #87 r3 B4; missed in CoS r3 review here. Fix: fail the run or print SCAN FAILED with non-zero exit.

## Improvements
- I1 tools/cos-open-asks.sh:21-22: a scan error exits 1, the same code as "open asks found". Live: MLV-App run at 03:36Z exited 1 with no OPEN lines (rate limit, set -e). Fix: exit 2 with a SCAN FAILED line; document in AGENTS.md:7.
- I2 AGENTS.md:7/:21: about 150 REST calls per run on an MLV-App-sized repo, required every session and every hub tick across lanes on one shared account; core quota at 0/5000 now. Fix: session start and pre-merge only; optionally one GraphQL query per PR.
- I3 Fixture (doctrine #87 only) checks kind/key only, has no runner, no closure-loop or OPEN cases; --classify needs a jq binary contrary to header :4. Fix: --selftest running classify plus closure and diffing OPEN lines.

## Notes
- r3 B1, B2, I1, I2, N1 addressed.
- N1 :40 a no-reply CoS answer saying "within 24 hours" counts as an ask (false OPEN, safe). N2 :70 CLOSE rows not time-ordered.
- Prevention: r3 fixture covered classification only, so the fail-open and exit-code clash passed it. Add --selftest plus an API-failure case expecting a non-zero, non-1 exit; carry to ruling candidate cos-open-ask-scanner-fixture-gate-r1 on doctrine #87.
- Ask adci-3-r31 (comment 6229136308) to the author lane (CoS). Ask adci-3-r3 closed by valid ACK 6229115578.
