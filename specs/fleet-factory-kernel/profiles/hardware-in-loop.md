# Profile: hardware-in-loop - Firmware and software whose acceptance needs physical hardware

**Profile of** `specs/fleet-factory-kernel.md` r1. **Profile revision:** r1. **Status:** `BENCHED`. **Benches:** magic-lantern_dannephoto (Canon 5D Mark III firmware), airmypc (release gate on live hardware).
A profile defines what acceptance means in its domain. It never weakens a kernel clause (kernel §5). File evidence against it as `P:hardware-in-loop <field>` lines in `adjudications/factory-kernel/<project>.md`.

| Field | Rule |
|---|---|
| Subject identity (K3) | git tree of the source plus the digest of the built image that was flashed or run |
| Artifact store | git for source; built images kept with their digests beside the hardware receipt |
| Determinism class | physical: results vary with device state, so a receipt records device, firmware and conditions |
| Acceptance evidence (K5) | emulator runs (for example QEMU) are necessary but never sufficient; acceptance needs a hardware receipt from the declared rig for the exact image digest |
| Independent key (K6) | the hardware rig or the human operating it; a model never supplies this key |
| Resource terminals (K5) | device unavailable, battery or thermal limits, operator absent: typed terminals; the subject waits and nothing is inferred |
| Delivery target (K7) | flashed or released image, published with its digest and hardware receipt |
| Human gates (K2) | every hardware session (the operator is the owner or someone the register names); operations that risk bricking the device |
| Budgets | operator sittings per week; device wear |
| Stress on the kernel | the independent key is a scarce human sitting, so K6 and K7 throughput is bounded by attendance, not compute; emulator results tempt substitution |

Rules from the bench: "Never claim a build/QEMU/hardware result without real evidence"; "Hardware evidence comes only from the owner's camera" (magic-lantern_dannephoto CLAUDE.md).
