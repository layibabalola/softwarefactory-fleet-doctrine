# Zero-reserve project disposition requests R1

The closed request queue is
[`zero-reserve-disposition-requests-r1.json`](zero-reserve-disposition-requests-r1.json). It binds the
exact proposed ruling, adoption matrix, canonical R26 ledger, and all nine sole-writer project specs.

This publication is the common notification surface. It asks every project owner to publish one
current `ADOPT`, `DISTINGUISH`, or `REJECT` line through `specs/<project>.md`; it does not write that
line for them. Unmounted projects remain unevaluated. An existing universal-token-control
`DISTINGUISH` is not automatically a response to this newer zero-reserve amendment.

`ADOPT` requires exact local policy/gate identities, the positive 100% boundary, above-100%
refusal, hostile capacity and concurrency controls, preserved model/effort/role/review/quality/
functionality, an independently accepted transaction, rollback/reinstall, and natural production
evidence. Publication of this queue grants no runtime, installation, disposition, ratification, or
adoption authority.

Run:

```text
python tools/check_zero_reserve_disposition_requests.py
```

The checker re-derives the closed project set, ledger counts/statuses, all bound file identities,
response syntax, and the zero-authority boundary.

The companion [`fleet-zero-reserve-census-r1.json`](fleet-zero-reserve-census-r1.json) separates
proven source/runtime reserve values from unmounted or otherwise unproven projects. In particular,
it records DNG's exact zero-reserve source plus closed live gate, AdversarialLLM's exact 25% remote
source policy, three remote trees with no declared reserve token under the frozen scan, and four
unmounted runtimes. Absence of a token is never promoted to zero-reserve or adoption evidence.
