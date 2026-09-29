# CANDIDATE r1: the threat model for memoising schema self-validation (zero runtime authority)

Status: PROPOSED 2026-09-29 by a bus-auditor chat session (record only).

## Why this needs a ruling and not another patch

Profiling shows that `validate_contract` in `tools/universal_provider_control.py` re-checks 27 distinct
schemas about 9,748 times per Windows anchor. That is 35-44% of anchor wall time. The anchors and the
125-test shard sit at 84-100% of the Windows budget, which is about 709 s. So a memo of the successful
schema self-check (Fix A) is the largest single margin lever that keeps every check executing.

A cross-family key (Codex gpt-6-sol) refused Fix A twice for the same mechanism:
- round 1: the memo key omitted `FORMAT_CHECKER`;
- round 2: the key fingerprinted the jsonschema remote registry by identity, and an in-place mutation of a
  meta-schema resource went undetected.

In both rounds the key's oracle was: "a direct `check_schema` and `validate_contract` must agree under any
in-process mutation of jsonschema state."

A three-seat adjudication (wf_cc533fca-dba) reproduced that NO memo can satisfy that oracle. Patching library
code such as `jsonschema._keywords.equal` changes the verdict of any later uncached check, including a private
snapshot, while a cached verdict stands. The fork is therefore about the threat model, not about the code.

## Proposal

The self-check verdict is a pure function of (schema content, the jsonschema and referencing libraries as
imported at process start). In-process mutation of jsonschema or referencing internals after import (module
globals, class attributes, registry resources) is outside this control's threat model. Findings of that
class are graded HARDENING, not BLOCKER, under the bus severity contract.

If this is ratified:
- land the simple content-keyed memo (the 96aa465 shape, not the 114-line fingerprint of fedf9c4) as a
  K1/K6 subject;
- the key checks equivalence with an uncached check under UNMUTATED library state;
- the key checks that failures are never cached and that instance validation runs on every call.

If this is rejected, Fix A stays parked, and margin comes from work that caches nothing: removing duplicate
`validate_contract` calls at the caller, and `git cat-file --batch` for immutable objects.

## Interim action (no ratification needed)

Fix B lands alone as a K1/K6 subject. It resolves the frozen graph's git dir once per open, and every
binding/member hash check still runs. The Fix A record is kept on local branch
`k1/subject2-part1-anchor-cost`, commits 96aa465 and fedf9c4.
