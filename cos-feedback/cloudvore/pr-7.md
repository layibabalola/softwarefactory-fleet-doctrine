schema: cos-feedback.v1
project: cloudvore
repo: layibabalola/Cloudvore
pr: 7
head: 762ca1d3ec7c84538e1fe32477af3ce583397cdd
reviewed_utc: 2026-10-17T03:34:31Z
event: pr-pushed
verdict: not-merge-ready
ci_summary: product-bar QUEUED + tools-bar QUEUED on this head; docs class, no model legs required (knowledge/cross-family-review-gate-policy.md:101); legs Claude 0 / Codex 0 not flagged

## Blockers

- B1 `tools/cos-open-asks.sh:35-36`: no-reply exclusion tests the whole body, so a legacy ask that quotes `no reply is needed` is dropped. Live: unanswered r1 ask `6228539909` on this PR was not listed (Cloudvore self-test failed, 0 OPEN). Fix: positive `ACK: <plan` / ask-footer signal wins; apply no-reply exemption only when absent; add fixture.
- B2 `tools/cos-open-asks.sh:30-34`: `CLOSED:` matched before `CoS-ASK:` in one elif chain, so a comment carrying both loses its new ask. Code-confirmed. Fix: emit CLOSE and ASK rows independently.

## Improvements

- I1 Legacy asks already answered under the old rule resurface as OPEN (no time cutoff, `AGENTS.md:34`). Spot-check 3/3 MLV-App OPEN lines (`6184755870`, `6170291818`, `6220773118`) had later `ACK:` replies citing time/plan/SHA, not id. Fix: later ACK/DISTINGUISH closes legacy asks; strict id cite only for `CoS-ASK:`; or one-time CLOSED sweep.
- I2 `tools/cos-open-asks.sh:41` / `AGENTS.md:38`: `gh pr list --state closed` does not order by `updatedAt` (MLV-App skips recently updated `#428`/`#409`). Sort by updatedAt or fix the doc.
- I3 (r1 residual): `docs/operating-contract.md:157-160` still says evidence / DISTINGUISH / zero authority; PR does not edit it while `AGENTS.md:3-4` names it authoritative. Add duty carve-out or pointer.
- I4 (r1 I2 residual): `ACK (correction):` still not REPLY (`:32` requires literal `ACK:`/`DISTINGUISH:`).

## Notes

- r1 B1 (three clauses), I1, I4, N1, N2 addressed (CoS-CONCERN skipped; MLV-App #457 `6226085174` not listed; agent-bridge #235 `6218026845` found; open+closed scan; GitHub-thread SoT; portable gh --jq). r1 I2/I3/N3 residual as I4/I3/N1 above.
- Nits: N1 `CLAUDE.md:50-51` double blank; N2 consumer AGENTS omits doctrine writer-duty paragraph; N3 PR body still describes r1 (48h / CoS-CONCERN as ask marker).
- Script byte-identical to doctrine #87 head `e7481339` and adobe-ingester #3 / agent-bridge #240 siblings. Same B1/B2/I1/I2 found on adobe-ingester #3 r3 (CoS-verified independently here).
- CoS authored (Layi approved 2026-10-16 9:27 PM CT); not an independent leg or hub acceptance. PR body asks for owner review before merge.
- Prevention: r1 measured false OPEN only; ship fixtures beside canonical script in doctrine #87 (quoted no-reply, CLOSED+CoS-ASK one body, CoS-CONCERN, valid/invalid ACKs, process-ask header), then copy out.
- PR comment with ACK ask: https://github.com/layibabalola/Cloudvore/pull/7#issuecomment-6229099208 (CoS-ASK: cloudvore-7-r3). CLOSED: 6228539909 superseded. Open asks: cloudvore-7-r3.
