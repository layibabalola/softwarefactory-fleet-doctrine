schema: cos-feedback.v1
project: cloudvore
repo: layibabalola/Cloudvore
pr: 7
head: a3630ba8c40d02e2f7c79095fa510fd30f9252cf
reviewed_utc: 2026-10-17T02:32:04Z
event: pr-opened
verdict: not-merge-ready
ci_summary: product-bar QUEUED + tools-bar QUEUED on this head; docs class, no model legs required (knowledge/cross-family-review-gate-policy.md:101); legs Claude 0 / Codex 0 not flagged

## Blockers

- B1 `AGENTS.md:35` (described `:28`): open-ask selector wrong both ways. (a) `contains("CoS-CONCERN:")` treats the factory-to-CoS channel as a CoS ask, and a factory `ACK:` quoting the string becomes the last ask and reopens an answered thread (both reproduced with synthetic input). (b) `^\*\*(Chief of Staff review|CoS)` matches CoS comments with no ask (MLV-App #457 `6226085174`, "no reply is needed", listed OPEN). (c) Misses `**Chief of Staff process ask` / `work order` headers (agent-bridge #235 `6218026845` not listed). Fix: `^\s*\*\*(Chief of Staff|CoS)\b` plus body contains `ACK: <plan or ETA>`, drop `CoS-CONCERN:`. CoS ran that variant: #457 false positive gone, #235 found.

## Improvements

- I1 `AGENTS.md:32`: 48h window drops an unanswered ask exactly at the CoS escalation point; widen to 14 days or scan open PRs/issues.
- I2 `AGENTS.md:37`: `^\s*(ACK|DISTINGUISH):` reads `ACK (correction ...):` as unanswered; accept `\b` or require literal `ACK:`.
- I3 authority precedence: `AGENTS.md:3-4` names `docs/operating-contract.md` authoritative, and `docs/operating-contract.md:157-160` still says bus data is "evidence, not instructions" / "DISTINGUISH / zero authority". Add the duty or a carve-out there.
- I4 coverage `AGENTS.md:24` vs `:33`: duty covers bus notes; script reads issue comments only. Document manual check or add it.

## Notes

- Nits: N1 `AGENTS.md:34` use `(add // [])`; N2 `AGENTS.md:32` GNU `date -d` + `jq` dependency; N3 `CLAUDE.md:50-51` double blank line.
- CoS authored this change (Layi approved 2026-10-16 9:27 PM CT); this review is not an independent leg or hub acceptance. PR body asks for owner review before merge.
- Verified: ran the script and a corrected variant against live Cloudvore (no CoS comments yet, prints nothing), MLV-App and agent-bridge issue comments, plus synthetic threads.
- Prevention: same selector in fleet template softwarefactory-fleet-doctrine #87 and siblings agent-bridge #240, AdversarialLLM-ClaudeCode #277, context-ultra-salesforce #109; fix the template first and copy out. Run any marker-based check over 14 days of real comments with known-open and known-answered fixtures before landing.
- PR comment with ACK ask: https://github.com/layibabalola/Cloudvore/pull/7#issuecomment-6228539909 (02:32Z). Open asks: 6228539909.
