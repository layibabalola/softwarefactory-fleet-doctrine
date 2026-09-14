# Profile: 3d-render - 3D scene and render production (Blender and similar)

**Profile of** `specs/fleet-factory-kernel.md` r1. **Profile revision:** r1. **Status:** `DRAFT - NO BENCH`. **Benches:** none (dng-auto-processor and mlv-app are the nearest measured-objective benches).
A profile defines what acceptance means in its domain. It never weakens a kernel clause (kernel §5). File evidence against it as `P:3d-render <field>` lines in `adjudications/factory-kernel/<project>.md`.

| Field | Rule |
|---|---|
| Subject identity (K3) | digest of the .blend or scene file plus a manifest of linked assets, add-on versions and render settings |
| Artifact store | large-binary store (git LFS or an asset store); renders in an output store keyed by input digest |
| Determinism class | render output is not byte-reproducible across hardware and versions, so acceptance compares within a tolerance or by human review |
| Acceptance evidence (K5) | a render of the declared frames at the declared settings, checked against a reference within tolerance or by an art-direction receipt, bound to the scene digest and the reviewed output digests; delivery must ship exactly those outputs |
| Independent key (K6) | an art director or reviewer other than the producer; a perceptual metric only when the instance declares one |
| Resource terminals (K5) | GPU or render-farm time, VRAM, disk: typed terminals; a partial frame range earns no credit |
| Delivery target (K7) | delivered frames or assets in the output store, with digests |
| Human gates (K2) | art direction, final delivery to a client |
| Budgets | GPU hours per subject |
| Stress on the kernel | claims on binary scene files must be exclusive; renders cost so much that K5 must allow sampled-frame acceptance, declared up front and never chosen after seeing results |
