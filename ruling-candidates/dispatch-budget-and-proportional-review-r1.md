# Dispatch budget and proportional review R1

Portable amendment from Agent Bridge, September 7, 2026. Project-local adoption
and fleet publication are separate. This document grants no runtime authority
to another project and does not change any account, subscription or spending
authorization. Adopters must record their own ADOPT, DISTINGUISH or REJECT.

## Measured failure

Agent Bridge's local driver refused at 24 launches in a rolling 24-hour window,
with only 45 minutes charged against a four-hour runtime limit, no active
drivers, and $26.12 in estimated/reported/reserved accounting against $40.
The refusal was `DAILY-DISPATCH-CAP`, not a GitHub capacity limit or an observed
provider exhaustion. A four-review publication quorum consumed four launch
allowances per changed subject. Finishing a reviewer freed concurrency but did
not remove its launch from the rolling day. Rotating an account could not
change that project-local history.

The owner instructed Agent Bridge to remove the delivery throttle, implement
bounded work and proportional review, obtain hub ratification, then publish the
result here. Existing failed receipts and review dissent remain evidence.

## Portable rules

1. **Name the limiting authority.** A refusal identifies local policy, native
   provider/account capacity, incremental spending authority, concurrency,
   operational approval or CI. Do not describe a local counter as provider
   exhaustion. Report the observed quantity, its source and next checkpoint.
2. **Explicit owner opt-out is distinct from missing policy.** When the owner
   disables aggregate launch/runtime proxies, preserve explicit null as off.
   Missing fields, invalid types and invalid finite limits remain errors.
   All parser, admission, projected-reservation and reporting paths must agree.
3. **Retain task bounds.** Use one named owner and exact subject, bounded input,
   per-run resource limits and wall time, finite concurrency, cancellation and
   terminal receipts. Preserve failure/unknown usage and the kill switch.
   No-work selection is deterministic and consumes no model launch.
4. **Use the correct account's native capacity.** A Claude sample cannot gate
   Codex, and a retired account cannot gate its replacement. Stale, malformed,
   missing and foreign samples are UNKNOWN. Each project must explicitly define
   whether UNKNOWN permits one bounded attended CLI attempt or refuses its
   autonomous admission path. Neither policy may claim UNKNOWN proves capacity.
   Respect actual provider refusal/reset; do not loop through unchanged failures.
5. **Separate subscription capacity, resource accounting and cash.** Tokens,
   runtime and API-equivalent `costUsd` are not proof of incremental billing.
   Do not silently remove a spending protection merely because an account is
   described as subscribed. Prove the selected billing route and paid-overage
   posture through supported evidence before changing its spend policy. No
   purchase, new credit, API fallback or credential rotation is authorized here.
6. **Review risk, not the mere fact of publication.** Local mechanical changes
   receive hub diff/validation review. Standard reversible delivery receives a
   hub plus one independent reviewer from the other model family. Critical
   storage/auth/security/wake/provider/dependency/CI/governance/spending changes
   retain the project's full independent quorum and any separate owner gates.
   Highest applicable class wins; uncertainty escalates. A worker or remote
   label cannot lower its own classification.
7. **Keep exact delivery gates.** All required tests, CI steps/artifacts,
   reviewed subject/tree, remote/base/head and ordinary matched-head merge checks
   remain. Verify actual post-merge CI before completion. A changed subject
   requires current approval, even if the review focuses on a bounded delta.
8. **Do not let an amendment approve itself.** Ratify governance changes using
   the currently authorized quorum. A direct owner instruction may remove a
   local proxy throttle to let that unchanged quorum run; record that authority
   separately from the later policy decision. It grants no publication vote.
9. **Bound remediation.** Preserve the original failure and test a regression
   when possible. At most three distinct repair hypotheses precede renewed
   hub/wisdom adjudication. Retain existing decision-round limits. A renamed task
   does not reset an exhausted attempt. Unresolved work records owner, reason
   and next meaningful checkpoint.

## Relation to existing fleet work

This amendment removes aggregate launch/runtime proxies when explicitly
authorized. It does not silently adopt or replace
[zero discretionary capacity reserve R1](zero-discretionary-capacity-reserve-r1.md),
which concerns quota-window reserve percentages. It neither grants runtime
authority to the universal-provider reference implementation nor weakens its
request reservations, protected directories, telemetry bindings or adoption
requirements. A project using those stricter admission contracts must preserve
them or obtain its own explicit amendment.

Agent Bridge retains its conservative $40 accounting guard and two-driver
concurrency limit. Its current native preflight covers active-account Claude
five-hour/weekly samples; Codex native quota availability remains UNKNOWN in
that local driver. The existing bounded CLI/provider-refusal boundary remains,
and the protected remote-message/local-confirmation invariants are unchanged.

## Required evidence for adoption

Agent Bridge's implementation subject is
`abd58979e56d7619d6a55f1f2fb3d9510809927c` in
[`layibabalola/agent-bridge`](https://github.com/layibabalola/agent-bridge).
Its full local gate passed 1,040 tests and 121 subtests, with Ruff and mypy,
Python 3.14.3, separately assigned user TEMP/TMP, UTF-8 and wrapper timeout
scale 4. The installed gate SHA-256 is
`b25c141187d2e9defbf717d8ae3aea9a10c674c74ad252117f14022743149f8d`;
the budget SHA-256 is
`3721a1c407620db43a948eba4e2e670162d5efcaa2d2830aeee992af13454cac`.
Post-install admission reported 24 retained launches, 2,700 retained lane
seconds and $26.12 accounting, with both aggregate proxies explicitly off.
The publication decision must carry exact artifact and full-quorum vote hashes;
this implementation evidence alone is not ratification or fleet adoption.

This standalone amendment preserves the sealed R26 project spec and intake
ledger bytes. It is discoverable through the repository index; changing a
sealed project disposition requires that separate intake's evidence workflow.

Pin exact old/new gate and policy hashes, source commit and review artifact.
Prove old explicit-null refusal and corrected admission on the same fixture.
Prove missing/invalid fields, finite caps, projected spending, concurrency,
kill switch, account/provider isolation and retained receipts. Exercise real
preview/apply/rollback failure paths in disposable directories. Verify the
installed hashes and actual gate result without rewriting historical receipts.
Retain the current full quorum on this amendment, and record each project's
subsequent disposition. Publication alone earns no fleet-wide compliance claim.
