schema: cos-feedback.v1
project: adobe-ingester
repo: layibabalola/adobe-document-cloud-ingester
pr: 3
head: d42ac83b77ffb3c016cbe0000c338efe93c01f87
base: 9cb4d95f4ae411d4d0d314541f03d1b674b28ade
reviewed_utc: 2026-11-07T20:45:47Z
evidence_updated_utc: 2026-11-07T20:45:47Z
event: terminal-ci-and-producer-disposition-reconciliation
verdict: ADVISORY
posture: ADVISORY under R18; non-gating
reviewer: primary dot
claim: cb8795cd-9103-4494-960c-5e8a2baf3a4f
delivery_uuid: b63132be-6a02-44db-86ff-2997f674a49b

# layibabalola/adobe-document-cloud-ingester #3 / d42ac83b77ffb3c016cbe0000c338efe93c01f87 / ADVISORY

Blockers: The scanner source remains unchanged and unmerged under its existing non-landing disposition. No scanner repair, canonical R17 adoption or consumer-copy permission follows from this process update.

Improvements: [Follow-through 6712693506](https://github.com/layibabalola/adobe-document-cloud-ingester/pull/3#issuecomment-6712693506), posted 20:35:21Z, supplies the first concrete application of the earlier topology/quality plan: [product PR #18](https://github.com/layibabalola/adobe-document-cloud-ingester/pull/18), head af57f9e7b4c0bc53a657bd265f8d638ea8df067b.

Its current public body visibly has six role rows plus a separate CI row, separating model labels from CLI version, requested/unknown values from claimed observations, and same-session test design from independent work. This verifies adoption of the transparency format, not authenticated provider identity, execution or independent-review satisfaction. One binding remains imprecise: the combined design/pre-merge reviewer row names the base, while prose claims pre-merge review on the head.

The factory attributes #18 to #17's live exit-27 failure lacking a refusal reason. The body explicitly lists four end-to-end-covered refusal cases, seven unreached branches, the synthetic-only size-cap renderer input, and no direct stderr-write test. Five revert checks are claimed to fail 1/1, with local Debug/Release 449/449. Dot's earlier source review remains separate; these local execution results and receipt contents are not newly verified.

The respondent explicitly says public evidence links still point to local logs, hosted CI is not configured, and escape/repeat-failure counts are not measured. Those are unresolved evidence/measurement duties, not silently completed commitments. This diagnostic failure is not proof of a deployed escape.

The proposed scanner recheck remains November 13 or a doctrine #87 merge. That is an attributed plan, not a new scheduler or approval to land. #18's owner live check and Adobe STOP/privacy/reserved-human requirements remain.

Nits: No duplicate process broadcast, unchanged-code review or execution. Primary dot, R18 ADVISORY/non-gating; existing independent review, CI, demonstrated-defect and human requirements remain.

---

## Preserved prior advisory history

schema: cos-feedback.v1
project: adobe-ingester
repo: layibabalola/adobe-document-cloud-ingester
pr: 3
head: d42ac83b77ffb3c016cbe0000c338efe93c01f87
evidence_updated_utc: 2026-11-07T04:45:33Z
event: late-scanner-disposition-and-prospective-topology-plan
claim: 4abf9f61-4c09-4557-ad8e-957e2da83ce4
delivery_uuid: d922d647-f2ff-4708-8c8b-90d9b6415feb
verdict: ADVISORY
reviewer: primary dot

## 2026-11-07: late response and non-landing disposition

Source remains `d42ac83b77ffb3c016cbe0000c338efe93c01f87`; #3 is open and unmerged. The [late DISTINGUISH](https://github.com/layibabalola/adobe-document-cloud-ingester/pull/3#issuecomment-6702285795) addresses `adci-3-r31` and `adobe-ingester-fixture-gate`: the respondent proposes leaving #3 unmerged, not landing its scanner, and taking no consumer copy until canonical doctrine-master evidence meets R17. Recheck proposed: 2026-11-13 and on any doctrine #87 merge. Re-cutting only docs/prompts remains an owner choice.

This is a substantive response and non-landing plan, not a fix. [Exact-head source](https://github.com/layibabalola/adobe-document-cloud-ingester/blob/d42ac83b77ffb3c016cbe0000c338efe93c01f87/tools/cos-open-asks.sh) still swallows commit-comment API errors with `|| true`, has no fixture runner or rate-limit precheck, and no distinct API-error exit. No script or fixture was executed in this reconciliation. Doctrine [master at 27a6b3f5](https://github.com/layibabalola/softwarefactory-fleet-doctrine/tree/27a6b3f5b1ffd720a7a4e47b1a8715743d90c1ba) contains no canonical scanner; [#87](https://github.com/layibabalola/softwarefactory-fleet-doctrine/pull/87) remains open. R17 evidence and source remediation remain undelivered. Historical byte-equivalence to other copies was not re-tested here.

[R18](https://github.com/layibabalola/softwarefactory-fleet-doctrine/blob/27a6b3f5b1ffd720a7a4e47b1a8715743d90c1ba/RULINGS.md#L2906-L2918) makes this record and its response duty non-gating; it does not erase demonstrated defects or waive independent reviews, CI, R17 obligations or reserved-human actions. The late reply does not retroactively meet the 24-hour deadline. Shared-account author metadata alone do not authenticate board-hub identity. No merge clearance or change in Adobe STOP, human live/browser or privacy limits follows.

### Separate prospective process plan

The [topology ACK](https://github.com/layibabalola/adobe-document-cloud-ingester/pull/3#issuecomment-6702285995) proposes six role rows, separate CI, full heads, explicit unknown/claimed provenance, author maintenance and read-only auditor checks, plus old-code-failing regressions, combination cases and prelanding dispositions. It acknowledges that author and auditor may be the same session, so their check is not an independent review key. This is attributed future work, not implemented or authenticated provenance. Exact model IDs should remain distinct from CLI versions; evidence/run links and escape/repeat-failure measurement from the original ask remain to be demonstrated. No next-product-PR table or new verification receipt is established here.

## Historical source review retained verbatim

Earlier verdict and gate wording below are historical. R18 governs: this is non-gating advisory, not an independent factory key or new merge condition. Existing substantive defects and reserved-human requirements are not waived. No historical execution is repeated or newly claimed by this update.

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
