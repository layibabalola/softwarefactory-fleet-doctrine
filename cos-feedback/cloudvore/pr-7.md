schema: cos-feedback.v1
project: cloudvore
repo: layibabalola/Cloudvore
pr: 7
head: ab8def27d6b506b80f21af2716833fcfc33c310f
reviewed_utc: 2026-10-17T03:40:54Z
event: pr-pushed
verdict: not-merge-ready
ci_summary: product-bar QUEUED + tools-bar QUEUED on this head; docs class, no model legs required (knowledge/cross-family-review-gate-policy.md:101); legs Claude 0 / Codex 0 not flagged

## Blockers

- B1 `tools/cos-open-asks.sh:59-60` (doctrine #87 B4 carried): `|| true` swallows a failed commit-comments call (fail-open as \"no open asks\"). Fix: drop `|| true`; distinct error exit; non-zero holds merge.
- B2 `tools/cos-open-asks.sh:73-74` / AGENTS legacy rule (doctrine #87 B5): no cutoff on legacy asks, so a reply citing only an older ask also closes a newer legacy ask on the same thread. Fixture: two LEGACY + one ACK citing first -> 0 OPEN. Fix: grandfather only before a fixed r3 effective timestamp; after that require citing reply.

## Improvements

- I1 `tools/cos-open-asks.sh:63` (doctrine I8): ETA regex matches `file:line` and bare dates. Fixture: `ACK: ... lint.ps1:594 later` closes ask. Require `ETA:` label + date/time.
- I2 (r3 I3 residual): `docs/operating-contract.md:160-162` still evidence / DISTINGUISH / zero authority; PR does not edit it while `AGENTS.md:3-4` names it authoritative.
- I3 (r3 I4 residual): `ACK (correction):` still not REPLY (`:31` literal `ACK:`/`DISTINGUISH:` only).
- I4 classify-only fixture (`:46-48`); no closing-loop fixture / CI step. Ship closing-loop fixtures in doctrine #87, then copy.

## Notes

- r3 B1/B2/I1/I2 addressed (quoted no-reply last-400; CLOSED+CoS-ASK independent; legacy any-later-reply; closed PRs by updatedAt). r3 I3/I4/N1-N3 residual as I2/I3/Nits.
- Nits: N1 CLAUDE.md:50-51 double blank; N2 writer-duty paragraph omitted; N3 PR body still r1 design.
- Script sha256 a63e582a4af2cdb0… byte-identical to doctrine #87 tip 34698e2b and adobe #3 / agent-bridge #240 / AdversarialLLM #277 / context-ultra #109 tips.
- Checked: --classify + closure fixtures (B1/B2/B5/I8/ACK-correction); live GraphQL Cloudvore #5/#6/#7 -> 1 OPEN (cloudvore-7-r3) then superseded; REST quota blocked full MLV-App/agent-bridge live runs. No Dot/Iverson advisory.
- CoS authored (Layi approved 2026-10-16 9:27 PM CT); not an independent leg. PR body asks for owner review before merge.
- Process: r3 ask unanswered (push is not ACK); superseded.
- Prevention: grandfather rule needs fixture where older ask answered and newer unmarked ask on same thread stays OPEN. Fix template first.
- PR comment with ACK ask: https://github.com/layibabalola/Cloudvore/pull/7#issuecomment-6229157485 (CoS-ASK: cloudvore-7-r4). CLOSED: 6229099208 / cloudvore-7-r3. Open asks: cloudvore-7-r4.
