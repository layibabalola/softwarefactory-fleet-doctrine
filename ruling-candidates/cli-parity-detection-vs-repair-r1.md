# Ruling candidate: parity detection is shared, parity enforcement is local (R6.4)

Status: **PROPOSED — ZERO AUTHORITY**

Measured by Conjugal, 2026-09-15, Dell XPS 17. Evidence: RECEIPTS.md and TRAPS.md entries of the
same date; `tests/test_account_parity.py` (23 tests, hermetic).

## What R6 already binds

R6 binds the check-then-repair order and the refusal to proceed while drifted. It explicitly does
not bind an implementation. This candidate does not touch that. It proposes a distinction R6 leaves
open, which a measured failure showed matters.

## The proposal

**R6.4 — a surface that cannot be compared is not a surface that agrees, and the two must be
separately nameable.** A parity check reports at least three outcomes, never two: aligned, drifted,
and *unverifiable*. Where unverifiability has a specific, actionable cause — most commonly a CLI
that is signed out while the desktop app is signed in — that cause is named as its own verdict, so
a consumer can gate on it. Collapsing it into a generic "unknown" makes it unactionable, and
`MATCHED`-or-nothing reading makes it invisible.

**R6.4.1 — detection is shared; enforcement is local.** The shared hook detects and names. It never
mutates a credential, never blocks a session, and never launches an interactive login on a state it
cannot positively distinguish from a benign one. A project that runs unattended work on the
standalone binary installs its own gate at the spawn path, where failing closed is correct and where
a dark runner actually costs something. Rationale: the shared hook runs at user scope in every
project, and an unattended wake is itself a SessionStart — a repair armed there fires at machines
nobody is watching. The hook's own contract already says a parity checker that can block a session
is worse than the drift it detects.

**R6.4.2 — an identity cache learns from the healthy state, not only from the broken one.** Any
mapping used to pre-fill a repair must be written while the surfaces AGREE. Measured: a map
populated only on the drift path can, by construction, contain only accounts already departed, so
the lookup of the account being moved to is a guaranteed miss and the repair launches with no
pre-fill — inviting re-authentication onto the wrong account, the failure the tooling exists to
prevent. Because the credential store is shared by the app copy and the runner binary, one wrong
login rewrites credentials for every live lane at once.

**R6.4.3 — parity is identity, never entitlement, and a verdict says which it proved.** An aligned
pair of configuration files proves two files name the same account. It does not prove a valid
credential exists, and it does not prove the account may infer. A capacity probe passes cleanly on a
wrong-account binary, so capacity-proof can mask identity drift rather than reveal it. The two
claims are reported separately or not at all.

## What is being asked

Ratification of R6.4 through R6.4.3 as an extension of R6, appended rather than edited. The
implementation already shipped on `review/cli-parity-detection-vs-repair` is offered as evidence
that the distinction is implementable at zero blast radius, not as a claim on adoption authority.

## What is NOT being asked

No change to R6 itself. No authority to install anything in another project. No claim that the
shared hook should ever repair a state it cannot positively distinguish — the proposal to widen the
repair trigger was raised, adversarially reviewed by three seats, and rejected on the evidence.
