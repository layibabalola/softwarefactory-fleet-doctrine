# Profile: mobile-app - iOS and Android applications

**Profile of** `specs/fleet-factory-kernel.md` r1. **Profile revision:** r1. **Status:** `DRAFT - NO BENCH`. **Benches:** none yet; salesforce-tools has a KMP Android scaffold lane.
A profile defines what acceptance means in its domain. It never weakens a kernel clause (kernel §5). File evidence against it as `P:mobile-app <field>` lines in `adjudications/factory-kernel/<project>.md`.

| Field | Rule |
|---|---|
| Subject identity (K3) | git tree plus the signed build artifact digest (APK, AAB or IPA) per track |
| Artifact store | git; signed artifacts in the build system with digests; signing keys never in the repo |
| Determinism class | code checks are deterministic; results across the device and OS matrix are statistical |
| Acceptance evidence (K5) | unit and UI suites plus a device-farm or physical-device run on the declared OS/device matrix, for the exact signed artifact |
| Independent key (K6) | a device farm or tester the producer does not control; store review is an external key for release only |
| Resource terminals (K5) | device-farm quota, signing unavailable, store review pending: typed terminals |
| Delivery target (K7) | store track (internal, beta, production) with the artifact digest |
| Human gates (K2) | signing, store submission, production rollout percentage, privacy and permission changes |
| Budgets | device-farm minutes; store review latency is outside the factory's clock |
| Stress on the kernel | delivery latency is external (store review), so K7 must tolerate a long pending state without blocking unrelated deliveries |
