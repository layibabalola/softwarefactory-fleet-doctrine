# Profile: game-engine - Games on engines such as Unreal or Unity

**Profile of** `specs/fleet-factory-kernel.md` r1. **Profile revision:** r1. **Status:** `DRAFT - NO BENCH`. **Benches:** none.
A profile defines what acceptance means in its domain. It never weakens a kernel clause (kernel §5). File evidence against it as `P:game-engine <field>` lines in `adjudications/factory-kernel/<project>.md`.

| Field | Rule |
|---|---|
| Subject identity (K3) | source revision plus an asset manifest of content digests (large binaries via LFS or a depot), plus the cooked build digest |
| Artifact store | source control that handles large binaries (git LFS, Perforce); cooked builds outside source control |
| Determinism class | mixed: builds are mostly deterministic; gameplay, performance and visual output are statistical |
| Acceptance evidence (K5) | a successful cook and build, automated functional tests where they exist, a performance capture against budgets (frame time, memory) on target hardware, and a playtest receipt for subjects that affect gameplay |
| Independent key (K6) | a playtester or performance rig the producer does not control; model review may judge code but never how the game feels |
| Resource terminals (K5) | cook and build time, GPU or hardware availability, licence seats: typed terminals |
| Delivery target (K7) | a labelled build on the distribution channel (internal, platform store) with its digest |
| Human gates (K2) | gameplay and feel acceptance, platform certification, anything touching monetisation or ratings |
| Budgets | build-farm hours, playtest sessions |
| Stress on the kernel | binary assets cannot be text-merged, so K3 claims must be exclusive asset locks; multi-hour cooks make per-subject acceptance expensive, so batching rules belong in the instance |
