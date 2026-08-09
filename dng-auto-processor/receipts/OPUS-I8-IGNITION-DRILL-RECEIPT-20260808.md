# OPUS receipt — I8 ignition refusal-drill package (route to sol)

**Lane:** `opus` (session `2bded0e6-5ccb-47fd-b1f7-a54ef20d3086`, Fable 5, orchestrator-hosted)
**Date:** 2026-08-08

## Binding inputs (size+SHA verified at read time, matched hub-cited tuples exactly)

- `evidence/FABLE-IGNITION-INDEPENDENCE-SYNTHESIS-R3-20260808.md` — 3,706 B / `9A3D35751B28DB3D81E5F8038BE186BC535B71D5C3C9C9F9C9721AB381E29491`
- `evidence/SOL-VERDICT-IGNITION-INDEPENDENCE-R3-ACCEPT-20260808.md` — 3,161 B / `872C4BC416D5C080CD4F69F50C58A3CC57E595938B2D29BF92D75A8D81CD9831`

## Package artifacts (exact bytes routed)

- `tools/ignition-launcher-check.ps1` — 20,259 B / `7FF44298E84CA10DFF4AAAF13530ABAE91EF0307FA2C21301D9EEC4AF1B7A85D`
  Drill-only I1–I8 precondition engine. NOT a production launcher: ignites nothing, claims nothing,
  writes zero bytes anywhere (receipt is stdout). Fail-closed: unevaluable input REFUSES; exit 90
  refusal / 92 unhandled-converted; dot-sourcing refused. Honors sol's interpretation bound: the I4
  canonical snapshot (hub path/size/SHA, lease SHA, exact beat line, owed pointer, restriction-register
  SHA, product digest) is proven by deterministic exact-byte serialization (fixed field order, LF-joined
  `key=value`, SHA-256 over UTF-8 bytes) + carrier identity — never prose classification. I1 is one
  byte-array capture that is both hashed and delivered; the path is never re-dereferenced (the two
  drill-only parameters -SimulateReRead / -AdversaryAfterCaptureFile exist solely so the drill can
  model the buggy launcher and the mid-window adversary, and are a declared reason this file may not
  be pointed at the real coordination root by anything but the drill). I2 prospective-only +
  router-independent; I3 route-vs-launch byte-identity with receipt-mapped deltas, any unexplained
  delta voids; I5 basis restricted to r3-need/schedule; recovery-scan mode proves the durable
  no-claim path read-only.

- `tools/test-ignition-refusal-drill.ps1` — 27,404 B / `0616271E5B58D5A374B50033A07AAF4F27C34DD276C130AECF9037B12466E70F`
  The I8 drill. Every row runs the real engine against a disposable sandbox coordination root under
  BOTH hosts via -EncodedCommand with `; exit $LASTEXITCODE` re-export. Zero-child-write is PROVEN per
  row by sandbox tree digest (sorted relpath|size|sha, hashed) before/after — the only exclusion is
  the TOCTOU adversary's own disclosed write target (`prompt.txt`) in the two adversary rows. Census
  asserted, not typed. All scratch roots removed and re-listed absent in the terminal path.

## Row inventory per host (census predicate: rows-executed-this-run)

- 3 POSITIVE: `green-allow` (engine can allow — refusal-only suites are vacuous in reverse);
  `explained-delta-allow` (receipted non-canonical carrier delta admitted — I3's receipt mapping is
  non-vacuous); `toctou-immune-allow` (adversary mutates prompt AFTER capture, delivered bytes still
  hash to the receipted SHA — sol's I1 drill mutant, positive half).
- 12 REFUSE rows over exactly the ELEVEN distinct arms, each RED by construction with zero child
  writes proven: prompt-hash-mismatch · capture-toctou · same-turn-self-artifact · foreign-live-target ·
  invoker-authored-child-evidence · missing-separation-event · router-selected-event (two fixtures:
  router-selected AND not-prospective schedule) · timing-steering · unexplained-carrier-delta ·
  partial-canonical-snapshot · mismatched-canonical-snapshot.
- 2 RECOVERY: `recovery-eligible-and-redrive` (deadline passed + owed item persisted durably +
  re-drive runs to ALLOW + invoker authored no child evidence + zero writes by scan AND re-drive);
  `recovery-refuses-invoker-evidence` (the recovery green can fail — negative control).
- 11 MUTANT rows: one per arm, the engine copy with that gate's `Refuse-Arm` neutralized
  (`$null =` substitution; setup precondition asserts the mutation actually changed bytes and the
  marker+line existed) must FAIL the arm's expectation — every arm proven load-bearing, zero-write
  still asserted under the mutant.

Total 28 rows/host, 56 rows/run, census asserted per host; a filtered (-Only) run can never print
CONTROL SET GREEN and never asserts the census.

## Runs (staged-as-production, both outer hosts)

- Outer pwsh 7: 56/56 OK, both CENSUS lines green, SCRATCH CLEAN, `CONTROL SET GREEN`, exit 0.
- Outer Windows PowerShell 5.1: 56/56 OK, both CENSUS lines green, SCRATCH CLEAN, `CONTROL SET GREEN`, exit 0.
- Both artifacts 100% ASCII by byte measurement (0 bytes > 127). Zero `igndrill-*` residue in %TEMP%
  after both runs (re-listed, count 0).

## Defects found and fixed during build (disclosed)

1. 5.1 `ConvertFrom-Json` emits a JSON array as ONE pipeline object, so `@()` wrapped the whole
   Object[] as a single element and every carrier row read as missing its `path` field under the 5.1
   inner host only. Fixed by enumerating through `ForEach-Object` at both JSON-array read sites;
   measured red-then-green.
2. The drill's gate-marker finder required an exact-match marker line; the `capture-toctou` marker
   carries trailing prose, so its mutant reported SETUP-FAILED (correctly, per the precondition rule —
   a mutation that did not happen is never a verdict). Finder corrected to boundary-anchored match.

## Boundaries honored

No product bytes under `DngAutoProcessor\`; no Apply/unfreeze/install/enable/start; no actual
ignition of any lane by any channel; no writes to other lanes' leases/inboxes; no merges. Production
autonomous ignition remains HOLD pending luna falsification + sol exact-package ruling on this
package, per the R3 ACCEPT.

## Brief (b) — orphan-write guard: NOT implemented, gate-blocked (mis-scope report)

The dispatch asked for implementation per `SOL-VERDICT-ORPHAN-WRITE-GUARD-ACCEPT-NARROWED-20260808.md`
(2,032 B / `524E723575A41C16C26182B81AA4302D21C0D7F8538B032E701B095D00293F69`). Read first, as
instructed: that verdict's own Next gate says "OWNER: luna falsifies this narrowed closed set BEFORE
implementation. If it survives, FABLE may assign a coordination-only implementer." No
`LUNA-FALSIFICATION-*ORPHAN*` artifact exists and no later hub entry closes that gate. Canonical
state over prompt state: implementing now would jump sol's gate, so (b) is returned as blocked, owed
first to luna (falsification), then to a fable implementation assignment.
