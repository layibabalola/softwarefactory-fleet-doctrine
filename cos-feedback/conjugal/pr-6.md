schema: cos-feedback.v1
project: conjugal
repo: layibabalola/Conjugal
pr: 6
head: 5422a3e7a87a53c5e25af7013c2927248ebbab0a
reviewed_utc: 2026-10-17T02:35:34Z
event: pr-pushed
verdict: not-merge-ready
ci_summary: health + suite FAIL on 5422a3e7 (run 38995275529), same curl (23) jq-install failure as master d21d69ae (run 38989533394), pre-existing. MERGEABLE vs master d21d69ae. Legs Claude 0 / Codex 0 on tip.
risk: HIGH-RISK by CoS judgement (agent entry instructions AGENTS.md + CLAUDE.md; docs only, no CI workflow or ruleset change)
reviewer: CoS (self-review: the CoS seat authored this PR; Layi's review is the merge gate)
post_merge: false
asks: https://github.com/layibabalola/Conjugal/pull/6#issuecomment-6228571489

# conjugal #6 CoS response duty + open-ask check (owner-authorized), r2

First CoS review on this PR (r1 647fdf91 was superseded 3 min later without a review). r2 makes the doctrine bus the source of truth for asks, scans all PR comments/reviews/inline comments paginated, and defines valid replies and closure. CoS ran the bash block verbatim against Conjugal (1 SKIP, exit 0) and against agent-bridge's 140 bus notes; counted bus ask formats and CoS author emails; tested the reply regex with jq.

## Blockers
- B1 AGENTS.md:80, :97-99: SCHEMA.md (cos-feedback.v1) defines no `## Ask` section. Only 2/140 agent-bridge notes have a `- ACK ask:` line; #239 lists its open asks 6228030239 and 6228531631 as `- r1:`/`- r2:` and the live run missed both (printed OPEN only for #238 and #240). Fix: define `## Ask` / `- ACK ask: <url>` / CLOSED in SCHEMA.md first, CoS backfills, PR depends on it.
- B2 AGENTS.md:80, :100-101: exact author-email pin. CoS used 8 author emails in 3 days (44/~119 cos-grok-bot@users.noreply.github.com). Live agent-bridge run: 135/140 notes SKIP "flag to Layi"; Conjugal pr-2.md SKIPs every session. Git author is self-asserted on a shared account, so it is a convention, not proof. Fix: CoS pins one email (done from this commit); check author only on notes with `## Ask`; reword; real authentication (signed commits or path rule) is Layi's call.

## Improvements
- I1: duty is PR-scoped but Conjugal lands by direct push (377 master commits in 7 days, no PR since #2). Define where asks on direct-push work live, or record as an open question for Layi.
- I2 AGENTS.md:110: standalone jq on Windows Git Bash; Conjugal CI cannot install jq right now. Use gh --jq only or fail loud when jq is missing.
- I3 AGENTS.md:111: `test("ETA"; "i")` matches "details"/"beta"/"metadata"; verified "ACK: I will check the details later" passes. Use case-sensitive `\bETA:`.

## Nits
- N1 CLAUDE.md:81-83 double blank line; pointer outside Non-negotiables list.
- N2 AGENTS.md:96-101 two API calls per note (~43 s on agent-bridge); filter on `## Ask` first.

## Prevention
- r2 moved detection to the bus without a schema change. Preventive check: any bus-parsing duty cites a SCHEMA.md section and its script runs against a live bus folder (agent-bridge) with zero false SKIPs and zero missed asks before push. B1, B2 and I3 apply to the same r2 text in agent-bridge #240, AdversarialLLM-ClaudeCode #277, context-ultra-salesforce #109, adobe-document-cloud-ingester #3, Cloudvore #7 and doctrine #87.

## Ask
- ACK ask: https://github.com/layibabalola/Conjugal/pull/6#issuecomment-6228571489 (posted 2026-10-17T02:35:34Z; follow-up due 24h later). Addressed to the author lane (CoS), since the factory did not author this PR.

## Notes
- Soft note: Conjugal master CI red since at least 00:37Z (runs 38987192802 to 38989533394) on the curl (23) jq-install step; needs its own fix card.
- No Dot or Iverson advisory on this PR yet.
