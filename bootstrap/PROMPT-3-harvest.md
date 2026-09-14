# PROMPT 3 — Harvest (run by the project that OWNS the subject spec)

The other prompts make a project *file* findings. This one closes the loop: the project that
owns the subject spec reads every filing, adjudicates between them, and rewrites the spec.

Binding (owner ruling 2026-09-13): *a filing is read by the subject's owning project, which
harvests every filing, adjudicates conflicts between them, and rewrites the spec.* A filing
nobody harvests is a report written into a drawer, and nothing else in the fleet would notice.

For `specs/conjugal-approach-a-v7.4.md`, the owning project is Conjugal.

---

## 1. Enumerate the population before reading any of it

```bash
python tools/harvest-status.py approach-a-design      # fetches; exit 1 while any filing lacks a disposition
```

**Not `ls adjudications/…`.** Filings live on `origin/review/*` branches until merged (R7.5), and one
project can hold different copies on master and on its review branch. Measured 2026-09-14
(Conjugal harvest): `ls` saw one filing; the population was two, and DropBox Vault's master copy
(26 findings, claude-only) was superseded by a 39-finding cross-family copy on its review branch.
The tool picks the newest copy per project, lists superseded copies, counts findings and
`## Untested` lines, and flags a `posture:` line not in R9's computed form.

Count them, and say the count before you start. This bus's own law: *enumerate the population
or make no causal claim*. A harvest that reads "the filings" without first knowing how many
exist cannot tell the difference between a project that found nothing and a project that never
filed — and those need opposite responses.

## 2. Read each filing's header before its findings

```
project:   who filed
providers: which families actually produced sentinel-complete lanes
seats:     which models, at what effort
rubric_id: scored, or unscored
```

**The header determines the weight, and it is not decoration.** A `claude-only` filing is one
family's opinion; `cross-family` means two independent families converged. Under R3 that line
is computed from sentinels, not typed, so you may rely on it — but a filing whose header claims
cross-family while its provenance section lists lanes from one family is a defect in the filing,
and should be sent back rather than harvested.

## 3. Adjudicate ACROSS projects, not within one

Within a filing, the project's own arbiter already picked winners. Your job is the layer above:

- **Convergent** — two or more projects, independently, on different repos, found the same
  defect. This is the strongest evidence the bus produces and it is why filings exist. Adopt.
- **Kernel exception.** For `adjudications/factory-kernel/`, no single bench wins. Apply `specs/fleet-factory-kernel.md`
  §5 instead: a BREAK with a concrete counterexample wins; FRICTION changes the kernel only when two or more profiles
  report it; the steward's own filing is dispositioned by another project or the owner; and append the harvest to
  `adjudications/factory-kernel/HARVESTS.md`.
- **Divergent** — one project's finding is contradicted by another's test bench. Do not average
  and do not merge. Decide which bench the spec is actually written for, say so, and record the
  loser with its reason.
- **Singular** — one project found it and no other bench exercises that path. Adopt as
  conditional, scoped to the conditions that bench establishes. Do not generalise it to the
  fleet on one repo's evidence.
- **Untested** — findings a project filed under `## Untested` because it could not ground them
  locally. These are hypotheses, not findings. Route them to a bench that *can* test them.

The test-bench rule is what makes this layer worth anything: every finding names a path, tool or
measured number in the filing project's own repo, so a disagreement between filings is a
disagreement between two real environments — not two opinions.

## 4. Rewrite the spec

Apply the adopted findings. Each carries a `REPLACES: "<anchor>" -> "<replacement>"`, so the
edit is mechanical; the judgement was in step 3. Where several findings hit one anchor, resolve
them into a single replacement rather than layering.

The spec is the deliverable. A harvest that produces a report about the spec, and not a new
spec, has not run.

## 5. Give every filing a disposition — this is what keeps projects filing

For each filing, record per finding: `ADOPTED`, `ADOPTED-CONDITIONAL(<bench>)`, `REJECTED(<reason>)`,
or `ROUTED(<bench>)`. **One place, so "was this harvested?" is a command, not a search:**
`adjudications/<subject>/<filing>.dispositions.md`, written only by the subject's owner, starting with

```
filing_blob: <full blob sha of the filing copy you harvested, from harvest-status.py>
filing_ref:  <ref that copy was read from>
spec_commit: <bus commit that carries the rewritten spec>
```

then one line per finding, in the filing's order: `§<n> "<anchor, ≤10 words>" | <DISPOSITION> | <reason>`.
Add a one-line RECEIPTS.md row pointing at the dispositions files. `harvest-status.py` reads
`filing_blob:` — if the filer later changes the filing, its status turns `STALE` by itself.
Filing-header defects (a `posture:` not copied from R9's tool, a cross-family claim the provenance
contradicts) go in the dispositions file as `HEADER: <defect>`; harvest what the provenance supports
rather than discarding the findings.

Skipping this is the failure that ends the loop. A project that files findings into silence
files once. The cost of a disposition line is trivial next to the cost of the fleet going quiet,
and a rejection with a stated reason is worth more to the filer than an adoption without one.

## 5b. Automate it

A subject owner should not run this prompt by hand; filings arrive at any hour. Conjugal's continuous steward
(`C:\code\Conjugal\coordination\harvest\README.md`; Conjugal commit f03390c3f) is one implementation. A scheduled
gate spawns a model only when `harvest-status.py` shows an eligible filing (it waits 30 minutes after the filing's last
commit). The session edits only worktrees. A deterministic runner refuses any path outside the subject's allowlist,
any non-append edit to an append-only file, and dispositions citing the wrong blob. It publishes by replaying onto the
fresh tip and counts success only when `harvest-status.py` reports `HARVESTED`. Quota refusals park until reset;
failures back off; two failures on the same open set raise `ATTENTION`. Portable parts: the gate, runner and census
shape. Local parts: paths, cadence and posture.

## 6. Report

`python tools/harvest-status.py <subject>` exiting 0 after your push is the completion proof —
paste its output. Filings read (and the count), convergent findings adopted, divergences and which bench won,
singular findings and their scope, what was routed and where, the spec's new commit, and —
plainly — **which projects have not filed**. That last line is the fleet's coverage metric: a
spec hardened against three benches is not a universal factory, and only the harvest can see
how far short of universal it currently is.

---

**Relation to the internal design loop.** Conjugal built this spec through rounds of its own —
designers on disjoint slices, lint, arbiter, consolidator, scored on six dimensions. Fleet
filings enter that same loop as a round, with one difference that is the entire point:
**internal rounds test the spec against itself; a fleet filing tests it against a real repo that
has to run it.** Weight them accordingly.
