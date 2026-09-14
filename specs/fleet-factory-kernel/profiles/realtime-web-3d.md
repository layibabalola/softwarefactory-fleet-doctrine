# Profile: realtime-web-3d - Browser 3D and realtime web (three.js, WebGL, WebGPU)

**Profile of** `specs/fleet-factory-kernel.md` r1. **Profile revision:** r1. **Status:** `DRAFT - NO BENCH`. **Benches:** none.
A profile defines what acceptance means in its domain. It never weakens a kernel clause (kernel §5). File evidence against it as `P:realtime-web-3d <field>` lines in `adjudications/factory-kernel/<project>.md`.

| Field | Rule |
|---|---|
| Subject identity (K3) | git tree plus digests of 3D assets and the built bundle |
| Artifact store | git (LFS for large models and textures) |
| Determinism class | code is deterministic; rendering varies by GPU, driver and browser, so visual checks use a tolerance |
| Acceptance evidence (K5) | unit tests plus visual regression screenshots within a declared pixel tolerance, and a frame-time and memory budget on a declared device class, for the exact bundle |
| Independent key (K6) | a headless or device rig the producer does not control, or a human visual check for subjective scenes |
| Resource terminals (K5) | GPU or runner unavailable, browser-matrix timeout: typed terminals |
| Delivery target (K7) | deployed bundle version with its digest |
| Human gates (K2) | visual design sign-off where the scene is subjective |
| Budgets | rig minutes, bundle size |
| Stress on the kernel | pixel-exact comparison fails spuriously across GPUs, so tolerance and device class belong in the profile, not the kernel |
