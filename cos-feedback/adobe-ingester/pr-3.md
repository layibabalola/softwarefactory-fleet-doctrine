schema: cos-feedback.v1
project: adobe-ingester
repo: layibabalola/adobe-document-cloud-ingester
pr: 3
head: 6eefc9c2f42628e11033c5b5d62efe08f85fc915
reviewed_utc: 2026-10-17T02:31:13Z
event: pr-opened
verdict: not-merge-ready
ci_summary: No checks configured on this repo; MERGEABLE/CLEAN against main 9cb4d95. Legs Claude 0 / Codex 0 on tip (docs-only owner PR; Layi's review reserved as the merge gate).
risk: docs only (AGENTS.md + CLAUDE.md added; no CI workflow, ruleset or code change)
reviewer: CoS (self-review: the CoS seat authored this PR)
post_merge: false
asks: https://github.com/layibabalola/adobe-document-cloud-ingester/pull/3#issuecomment-6228532654

# adobe-ingester #3 CoS response duty + open-ask check (owner-authorized), r1

Adds root AGENTS.md (CoS response duty, session-start gh api + jq open-ask lister keyed on body markers) and CLAUDE.md pointer. Same change as agent-bridge #240, AdversarialLLM-ClaudeCode #277, context-ultra-salesforce #109; fleet template doctrine #87. CoS ran the script verbatim against this repo (empty, exit 0) and against MLV-App's last 48h (362 comments); the rest is read-only.

## Blockers
- B1 AGENTS.md:19: selector `contains("CoS-CONCERN:")` treats the factory-to-CoS concern channel as CoS asks, and the `**CoS` marker branch matches CoS comments that need no reply. Live repro: MLV-App #457 comment 6226085174 (CoS answer to concern 6224672124, "no reply is needed") prints as OPEN. Fix: drop the CoS-CONCERN branch and exclude "no reply is needed" bodies (or require the `ACK: <plan` phrase, present in 94/102 CoS-marker comments). Same selector in #240, #277, #109.

## Improvements
- I1 .factory/BOOTSTRAP.md:92 and agents/doctrine-consumer.md:34 still say cos-feedback is "data only / zero authority"; .factory/prompts/ never reference AGENTS.md. Carve out CoS ACK asks there and point to AGENTS.md.
- I2 AGENTS.md:7 says bus-note asks need replies, but the script scans only issue comments. Add a bus check or narrow the sentence.

## Notes
- N1 AGENTS.md:14 `date -d` is GNU-only; add a pwsh/portable fallback.
- N2 Only the latest CoS comment per thread is checked; say that each CoS comment restates prior open asks.
- N3 CLAUDE.md:4-5 double blank line.
- Prevention: run any fleet-wide ask detector against MLV-App's last 48h before landing; require zero false OPEN lines on threads whose last CoS comment needs no reply.
- Ask 6228532654 is addressed to the author lane (CoS), since the factory did not author this PR.
