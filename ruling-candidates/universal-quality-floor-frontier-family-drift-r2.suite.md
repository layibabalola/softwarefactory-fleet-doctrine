# r2 companion: the two suite errors, named and root-caused

Companion to `ruling-candidates/universal-quality-floor-frontier-family-drift-r2.md`, finding 9.
**Zero authority**, like the candidate it accompanies. It proposes no change and asks for no
adoption. It exists because finding 9 records that the suite is red and a finding that names no
cause silently licenses another round.

**This is not a quality-floor defect.** It was found while measuring the quality floor, it is the
same *defect class* (a recorded identity the tree moved out from under), and it is reported here
rather than folded into the candidate so that an adjudicator can dispose of the two separately.

## The two errors

`python -m unittest tests.test_universal_provider_control` on the r2 bound subject
(`62aa8b9ccbeec07f2e67b05bd8589273509275f0`): **252 tests, FAILED (errors=2)**. Both are in
`tests.test_universal_provider_control.ReviewResourceAdmissionR29Tests`:

1. `test_current_descriptor_pipeline_is_closed_anchored_and_exact`
2. `test_current_manifest_checker_is_metadata_derived_and_successor_safe`

Both surface `check_universal_manifest.ManifestError: MANIFEST_SUBJECT_MISMATCH`. Neither name is
taken from a local run alone — CI names the same two tests in the same class on the same head, so
this is not a Windows-checkout artifact.

## Root cause, derived not guessed

`MANIFEST_SUBJECT_MISMATCH` is raised at `tools/check_universal_manifest.py:2978`, inside
`_verify_subjects_and_self`, when a manifest's recorded `sha256`/`bytes` for a subject file do not
match the git blob at the candidate commit. Reproduced directly, without the test harness:

```
python tools/check_universal_manifest.py --treeish HEAD    # prints MANIFEST_SUBJECT_MISMATCH, exits 1
```

The failing layer is the CURRENT_CANDIDATE one,
`manifests/universal-provider-control-reconciliation-r45.json`. **One of its seven subjects
mismatches:**

| subject | recorded in r45 | at HEAD | delta |
|---|---|---|---|
| `README.md` | 22,781 B | 23,651 B | **+870** |

The other six verify. Reproduce by hashing each `subjectFiles` entry's blob
(`git show HEAD:<path> | sha256sum`) against its recorded `sha256` — blob bytes, not a CRLF
worktree checkout, which is the distinction `test_r12_01_manifest_self_uses_canonical_git_blob_under_crlf_checkout`
exists to hold and which still passes.

## When it broke, and what has landed since

| event | commit | time |
|---|---|---|
| r45 re-pinned to `README.md` @ 22,781 B — *"manifests(r45): re-pin the README.md subject binding"* | `22640ed` | 2026-09-18 11:19 |
| last **green** *Provider capacity governor contracts* run on master | `4adb9530` | 2026-09-19 10:27 |
| `README.md` → 23,445 B — **pin broken** | `ad426fb` | 2026-09-19 12:06 |
| `README.md` → 23,651 B | `2d30df9` | 2026-09-19 23:24 |

`4adb9530` is an ancestor of `ad426fb`, so the last green run is the one immediately before the
break — 1 h 39 m earlier. The workflow has not been green since.

**Measured exposure: the gate has been red for 52.5 hours, and 174 commits have landed on master
in that window** (`git rev-list --count ad426fb..origin/master`). Of the last 100 governor-workflow
runs on master, 54 are `failure` and **none is `success`**.

The checker is wired into CI (`.github/workflows/provider-capacity-governor.yml` runs
`check_universal_manifest`), so this is not an unwired control — it is a wired control that is
firing correctly, and the firing is not stopping anything.

## Why this belongs next to the candidate

The r45 manifest was re-pinned on 2026-09-18 **specifically to fix this subject binding**, and was
broken again by the next README edit, 25 hours later. That is the third instance in this pass of one
defect:

| instance | recorded identity | what moved | detected after |
|---|---|---|---|
| r1's bound subject | `12b0a56` + three file digests | all three files | 19 days |
| r2 finding 8 | `FRONTIER_HIGH_MODEL` generation list | `gpt-6-astra`, `claude-fable-5-1` entered `specs/` | 13 / 8 days |
| this | r45 `README.md` subject pin | `README.md` | 52.5 h, still open |

In all three, a *correct* value was written down, the artifact it described moved, and nothing
connected the two. r1's own remedy for its case is the template and it is already in the repo's law
(`RULINGS.md`, adversarialllm 2026-09-02): point at derived state, never bake an identity into it.
A manifest cannot do that — pinning bytes is its whole job — so the repair for this instance is not
a better pin but a **trigger**: the edit that moves a pinned subject must re-freeze the manifest in
the same commit, which is the same shape as r1's proposition clause 5.

## What is NOT claimed here

- That the two errors touch the quality floor. They do not, on the evidence above, and r2 records
  that relationship as UNEVALUATED.
- That `README.md` should be un-edited or reverted. The README changes are ordinary doctrine work;
  the manifest is what went stale.
- That this should be repaired now. Re-freezing r45 changes a pinned governance artifact, and this
  repo does that through adjudication, not through a passing commit. **No repair is attempted in
  this branch.** The purpose of this file is that the next seat inherits a named cause and a
  measured window instead of a red check it has to re-derive.
