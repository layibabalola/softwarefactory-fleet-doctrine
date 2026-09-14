# Profile: code - Software source code (desktop, web, services, tooling)

**Profile of** `specs/fleet-factory-kernel.md` r1. **Profile revision:** r1. **Status:** `BENCHED`. **Benches:** cloudvore, conjugal, salesforce-tools, adversarialllm, agent-bridge, adobe-ingester, airmypc (build lane).
A profile defines what acceptance means in its domain. It never weakens a kernel clause (kernel §5). File evidence against it as `P:code <field>` lines in `adjudications/factory-kernel/<project>.md`.

| Field | Rule |
|---|---|
| Subject identity (K3) | git tree OID of the candidate commit; generated binaries identified by the build receipt's output digests |
| Artifact store | git (shared checkout or worktrees); build outputs are not the subject |
| Determinism class | deterministic by default; flaky suites are declared per test, never silently retried |
| Acceptance evidence (K5) | the project's pinned acceptance runs at the exact commit (for example N identical green runs), executed or authenticated; replay agreement alone is not acceptance (Approach A Round F1, cluster C3) |
| Independent key (K6) | a verifier from another model family (R3) or a CI runner the producer does not control |
| Resource terminals (K5) | suite timeout, thermal admission, runner capacity: typed terminals, no partial green |
| Delivery target (K7) | integration branch via the project's landing path; review branches push (R7) |
| Human gates (K2) | releases, security-sensitive paths, frozen bytes, and anything the project's register lists |
| Budgets | wall time per suite, provider calls per subject |
| Stress on the kernel | shared-checkout index races, worktree-scoped locks, and plumbing commits onto a checked-out branch (all three measured in Round F1) |

**Reference instance:** Conjugal Approach A v7.5 (`specs/conjugal-approach-a-v7.4.md`), a design that has not been built. Its map to the kernel: K1 §0 tiers and §3 committee; K3 §2 claims, leases and fences; K4 §1 receipts and journals; K5 §14 and §4 acceptance runs; K6 §3 cross-family proofs and §4 attestation helpers; K7 §4 adoption and §5 authorised landing; K8 §5 capacity and rotation; K12 §12 Tier 0 and fleet F-rounds.
