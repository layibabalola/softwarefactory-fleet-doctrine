schema: cos-feedback.v1
project: adobe-ingester
repo: layibabalola/adobe-document-cloud-ingester
pr: 3
head: 873bce1373bcef38a98839aeb19d8d9f2333dfe8
reviewed_utc: 2026-10-17T03:31:37Z
event: pr-pushed
verdict: not-merge-ready
ci_summary: No checks configured on this repo; MERGEABLE/CLEAN, 0 behind main 9cb4d95. Legs Claude 0 / Codex 0 on tip (docs-only owner PR; Layi's review reserved as the merge gate).
risk: docs only plus helper script tools/cos-open-asks.sh (no CI workflow, ruleset or product code)
reviewer: CoS (self-review: the CoS seat authored this PR)
post_merge: false
asks: https://github.com/layibabalola/adobe-document-cloud-ingester/pull/3#issuecomment-6229072642

# adobe-ingester #3 CoS response duty + open-ask check (owner-authorized), r3

r3 makes the GitHub thread the source of truth, adds a portable tools/cos-open-asks.sh (gh --jq only; CoS-ASK marker plus legacy detection; id-cited ACK/DISTINGUISH or CLOSED), carves out the zero-authority labels and points all six lane prompts at the duty. The script is byte-identical (blob 19fd5df) to doctrine #87 head e7481339, agent-bridge #240, AdversarialLLM-ClaudeCode #277 and context-ultra-salesforce #109. CoS ran it against this repo (0 OPEN, exit 0) and MLV-App (48 PRs, 41 s, 15 OPEN), fed its classify jq synthetic comments, and hand-checked 7 MLV-App OPEN lines; doc edits read only.

## Blockers
- B1 tools/cos-open-asks.sh:36: the no-reply exclusion tests the whole body, so a legacy ask that quotes the phrase is dropped. Live: r1 ask 6228532654 on this PR (unanswered) was not listed; synthetic repro confirmed. Fix: an explicit `ACK: <plan` phrase wins; exclude only when absent; add a fixture.
- B2 tools/cos-open-asks.sh:30-34: CLOSED is matched before CoS-ASK in one elif chain, so a comment carrying both (the normal superseding review per writer duty, template line 134) loses its new ask. Synthetic repro confirmed. Fix: emit CLOSE and ASK rows independently.

## Improvements
- I1 Legacy asks already answered under the old rule resurface as OPEN (no time cutoff, AGENTS.md:17). 7 of 7 sampled MLV-App OPEN lines were answered by ACKs citing time or plan, not id/sha (#437 x4 merged, #432 x2, #466 merged). Fix: any later ACK/DISTINGUISH on the thread closes a legacy ask; strict id rule only for CoS-ASK asks; or a one-time CLOSED sweep.
- I2 tools/cos-open-asks.sh:41 / AGENTS.md:21: gh pr list --state closed orders by creation, not update (MLV-App skips recently updated #428, #409, #374). Sort by updatedAt or fix the doc.

## Notes
- r1 B1, I1, I2, N1, N2 addressed (CoS-CONCERN skipped; MLV-App #457 comment 6226085174 no longer listed; labels carved out; prompts point to duty; portable; per-id tracking). r1 N3 open.
- N1 CLAUDE.md:4-5 and six prompt files append double blank lines.
- Prevention: r1 check measured false OPEN only, so r3 passed while failing open. Ship a fixture test beside the canonical script in doctrine #87 (quoted no-reply phrase, CLOSED plus CoS-ASK in one body, CoS-CONCERN body, valid/invalid ACKs); carry to the #87 review.
- Ask adci-3-r3 (comment 6229072642) to the author lane (CoS). r1 ask 6228532654 closed as superseded in comment 6229073492.
