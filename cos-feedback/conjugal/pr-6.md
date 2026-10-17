schema: cos-feedback.v1
project: conjugal
repo: layibabalola/Conjugal
pr: 6
head: ad17a5ba66685eeb8b5d1b412561a768b06e9f5c
reviewed_utc: 2026-10-17T03:33:12Z
event: pr-pushed
verdict: not-merge-ready
ci_summary: health + suite FAIL on ad17a5ba (run 38998907709) in the "Toolchain inventory and jq" step, same step red on master (runs 38995954664, 38998725125), pre-existing. MERGEABLE, 3 ahead / 3 behind master ce17dfd5. Legs Claude 0 / Codex 0 on tip.
risk: HIGH-RISK by CoS judgement (agent entry instructions AGENTS.md + CLAUDE.md + new session-start script tools/cos-open-asks.sh; no CI workflow or ruleset change)
reviewer: CoS (self-review: the CoS seat authored this PR; Layi's review is the merge gate)
post_merge: false
asks: https://github.com/layibabalola/Conjugal/pull/6#issuecomment-6229083497

# conjugal #6 CoS response duty + open-ask check (owner-authorized), r3

r3 makes the GitHub thread the source of truth (CoS-ASK marker plus legacy header detection), requires id-cited ACK/DISTINGUISH or CLOSED, adds a portable bounded tools/cos-open-asks.sh (gh --jq only) that also scans commit comments for direct pushes, and states the shared-account authority limit. CoS ran the script from this head against Conjugal (1 OPEN, correct), agent-bridge (20 OPEN, 29 s) and MLV-App (15 OPEN, 41 s) and hand-checked the MLV-App OPEN threads; ran the extracted classify filter and eta_re on synthetic bodies; confirmed the script is byte-identical to doctrine #87 head e7481339 and absent from doctrine master.

## r2 disposition
- B1, B2 moot (bus lookup and author-email check dropped). I1 addressed (commit-comment asks, AGENTS.md:94). I2 addressed (gh --jq only). I3 addressed (real-ETA test; see N2). N2 addressed. N1 carried. r2 ask 6228571489 closed by CoS comment 6229084992 (CLOSED line; script confirms it no longer lists it).

## Blockers
- B1 AGENTS.md:80, :86; tools/cos-open-asks.sh:63: already-answered legacy asks become permanent OPEN lines because old ACKs don't cite id/URL/sha. Verified MLV-App: #437 6166842975, 6170291818, 6170907965, 6180236263 (ACK 6186593425), #447 6219217054 (ACK 6219433784), #458 6215607741 (ACK 6216902325), #461 6220462049 (ACK 6220585903, sha typo): 7 of 15 OPEN. Fix: grandfather pre-r3 legacy asks to the old any-later-ACK rule, require citation only for CoS-ASK and post-date legacy asks, CoS posts CLOSED for leftovers, re-run on MLV-App and agent-bridge.
- B2 tools/cos-open-asks.sh:30-34: CLOSED is checked before ASK, so a review that closes the last round's ask and raises a new one yields only a CLOSE row. Verified with the extracted filter. Fix: emit CLOSE and ASK rows independently; add a fixture.

## Improvements
- I1 PR body still describes r1 (48h window, CoS-CONCERN as marker, bus folder). Rewrite for r3.
- I2 AGENTS.md:78, script:2: canonical text and script exist only on open doctrine #87. Declare dependency / merge order.
- I3 script:48: commit-comment scan ends in `|| true`, so a failure on the direct-push path prints 0 open, exit 0. Fail loud.
- I4 AGENTS.md:80, script:63: CoS-ASK id has no format and is matched by substring; short ids like B1 collide across rounds and with prose; CLOSED: B1 closes both. Read-only finding. Fix: unique id format, whole-token match.

## Nits
- N1 (carried) CLAUDE.md:81-83 double blank line; pointer outside Non-negotiables.
- N2 script:51 eta_re loose: "Markdown 2", "Maybe 3", "1:1689" all pass as ETA (verified). Anchor to an ETA: label.

## Prevention
- r3 changed the reply rule without testing against existing replies. Preventive check: run any response-duty script against MLV-App and agent-bridge and hand-classify every OPEN line (zero already-answered asks), plus a fixture file of comment bodies (close + new ask, legacy ask with uncited ACK, short CoS-ASK ids). B1, B2, I3, I4, N2 apply to doctrine #87 and every sibling copy.

## Ask
- ACK ask: https://github.com/layibabalola/Conjugal/pull/6#issuecomment-6229083497 (posted 2026-10-17T03:32:38Z; follow-up due 24h later). Addressed to the author lane (CoS).
- CLOSED: https://github.com/layibabalola/Conjugal/pull/6#issuecomment-6228571489 (r2, superseded; CoS comment 6229084992).

## Notes
- Soft note: Conjugal master CI still red on the jq install step (latest failure run 38998725125 on 0d4312ba); needs its own fix card.
- No Dot or Iverson advisory on this PR yet.
