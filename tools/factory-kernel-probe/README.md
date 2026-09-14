status: PROPOSED to the steward of `specs/fleet-factory-kernel.md` r1 (interim steward: Conjugal)
proposer: magic-lantern_dannephoto, 2026-09-14 — review branch only, never landed on master by the proposer

# factory-kernel-probe — machine-measured evidence for kernel filings

r1 makes every clause answerable by an *observable* that a project reports by hand in its PROMPT-K filing. This probe
measures the ones a tool can measure, from the project's native ledger and git history, and returns
PASS/FAIL/WARN/UNKNOWN/N/A with evidence. **UNKNOWN is never rounded up.** It was built and reviewed as part of a
parallel kernel draft (`DRAFT-universal-factory-kernel.md`, not doctrine). The owner ruled r1 is the kernel; this
directory is how the draft's useful parts reach r1's steward.

```bash
python tools/factory-kernel-probe/probe.py check --manifest tools/factory-kernel-probe/manifests/<project>.json [--json]
python -m pytest tests/test_factory_kernel_probe.py      # 19 tests
```

## Mapping onto r1

| probe | what it measures | r1 clause | kind |
|---|---|---|---|
| K1 | integration ref declared and resolving; every accepted commit reachable from it; UNKNOWN with no readable units | K7 (delivery target), K3 (identity) | measures an r1 observable |
| K2 | lock identity is the git common dir, so worktrees share one identity | K3 (one claimant, single writer) | instance detail for the `code` / `hardware-in-loop` profiles |
| K3 | admission bounded by eligible work; zero eligible admits zero executors; optional observed-executor probe | none; nearest K8 | **candidate new clause** (proposal P2 in the filing) |
| K4 | the ledger's owner-authority record exists (recorded, not authenticated) | K2 (register) | measures an r1 observable |
| K5 | a receipt binds command, exit 0, exact identity and a non-author verifier; failing status files flagged; existence alone is WARN | K4, K5, K6 | **sharpens r1 K5's "acceptance evidence exists"** (proposal P4) |
| K6 | adopted and delivered are separate counts; delivery needs delivery evidence | K7 | measures an r1 observable |
| K7 | governance-to-product commit ratio over 14 days; ≥ 0.9, zero product commits, or zero motion raises the fixpoint alarm | none; nearest K12 | **candidate new clause or K12 observable** (proposal P1) |
| K8 | doctrine sync receipt ≤ 7 days old | K10, K11 | measures an r1 observable |
| K9 | owner-reserved actions enumerated | K2 | measures an r1 observable |
| K10 | every blocked unit has a reason; an owner channel exists | K5 (typed terminals) | measures an r1 observable |
| K11 | a declared scheduler probe is live, or owner-interaction evidence is ≤ 14 days old | none; nearest K4 ("enabled state and actual execution are different facts") | **candidate observable** (proposal P3) |

## Files

- `probe.py`: the checker (feedback/harvest subcommands belong to the draft's own loop; r1 uses PROMPT-K and `harvest-status.py`).
- `manifests/`: adapter manifests for the two benches it has run on.
- `evidence/`: the probe's recorded output on those benches, 2026-09-14.
- `REVIEW.md` and `REVIEW.rubric.json`: the draft's full-posture self-review (17/17 lanes, panel 63.88) and the
  disposition of every finding.
- `rubrics/kernel-universality.json`: a domain-agnostic review rubric the steward may reuse for kernel proposals under R9.
- `DRAFT-universal-factory-kernel.md`: the superseded draft, kept as evidence only.
