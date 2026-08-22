# DNG lease self-healing investigation receipt — 2026-08-22

Status: **MEASURED / PROPOSAL PUBLISHED / RUNTIME UNCHANGED**

## Incident

The DNG natural strict-serial R98 campaign preclaimed Opus at
`2026-08-22T07:40:21-05:00` with session
`5dd16c71-a324-4778-90eb-f1c3d95827dd` and transaction
`600f7259-aaad-4da4-a649-323a29d19d34`. Provider admission then rejected a frozen-prompt mismatch
before the process-creation boundary. The production warden recorded zero provider launches, but
launch evidence as unproven, closed the gate, retained the exact preclaim, and suppressed later lanes.

The current lease was valid JSON, not byte-corrupt: 3,133 bytes / SHA-256
`DD48CE23B10D6DC482A8D43B132383B26EA961B84D8C5085548F41A989E0EE95`. Shared liveness classified
it `ORPHAN-PULSE`. The existing generic rule could not reclaim it until a 90-minute lease plus a
90-minute grace elapsed, even though the actual validation failure occurred before process creation.

Local incident evidence was frozen as 2,641 bytes / SHA-256
`89E964BC38D5FB97C5C359E0AF32C6BB67D108413BF405484B08E44E43104BF3`. The exact local proposal was
10,953 bytes / SHA-256 `48C11C66AFFB64244D8365DA77352C74771DD5120E412563310C6C0914B6ADBD`
and was posted to the DNG hub through its sanctioned coordination writer at
`2026-08-22T08:07:47-05:00`.

## Root cause

The provider-admission actor already returns typed `launched=false` results for ordinary admission
holds, and the warden already releases an exact preclaim on that result. Frozen-prompt validation
instead throws before result creation. The warden cannot distinguish that exception from an exception
whose process boundary is unknown, so retaining the lease is the correct fail-closed outcome.

Separately, shared liveness intentionally classifies malformed, missing, or out-of-domain lease data
as `UNEVALUABLE`; the canonical lease writer refuses such bytes. No authenticated reconstruction
transaction exists, so those classes can block indefinitely.

## Disposition

DNG proposes the two-path portable rule in
[`ruling-candidates/fleet-provider-lease-self-healing-r1.md`](../../ruling-candidates/fleet-provider-lease-self-healing-r1.md):

- typed same-attempt zero-launch receipts allow immediate exact preclaim release; and
- damaged/missing leases recover only through a lock/CAS, authenticated-journal,
  content-addressed-archive, process-proof, intent/commit transaction.

Process absence alone grants zero recovery authority. Ambiguous evidence remains a HOLD. Self-healing
may create only a terminal release, never a live owner.

No current DNG lease, provider process, task, gate, packet, installer, or production source was changed
by this investigation or publication. In particular, the R98 Opus lease was not manually released or
rewritten.
