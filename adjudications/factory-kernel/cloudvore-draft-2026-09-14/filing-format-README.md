# Dogfooding the universal factory kernel — how to file

Subject: `ruling-candidates/universal-factory-kernel-r1.md` (later revisions keep this directory).
Owner: Cloudvore (DropBox Vault). Opened 2026-09-14. Harvest: `bootstrap/PROMPT-3-harvest.md`.
Open filings: `python tools/harvest-status.py universal-factory-kernel`. Eligibility and harvest-due:
`python tools/kernel-convergence.py`.

One file per project, single writer: `adjudications/universal-factory-kernel/<project>.md`. The tool
ignores a filing unless all of these hold:
- its filename stem equals `project:`;
- the project is known to the bus: a `specs/<project>.md`, or a RECEIPTS.md heading `(<project>, …`
  on the filing's own branch;
- `kernel_revision:` names the current revision;
- `seats:` is filled;
- `## Adapter` has an `artifact:` line. Run the whole session
from `bootstrap/PROMPT-K-dogfood-kernel.md`.

## Header (exact keys)

```
project: <same as the filename stem; as in specs/<project>.md where one exists>
domain: <one line, e.g. "Windows .NET desktop app", "fantasy novel", "Unreal Engine 5 game">
adapter_class: <deterministic | statistical | attended | judgment>[, <another class> ...]
kernel_revision: <r1 | r2 ...  — must equal the candidate revision you measured, or it counts for nothing>
author_of_candidate: <yes | no>
providers: <families you could seat, e.g. claude(opus,haiku) codex(sol) | claude-only>
seats: <who measured and who reviewed; model and effort; say "no posture run" if none ran>
cross_family: <validated | NO-CROSS-FAMILY-VALIDATION>
```

- **Posture (R9).** If you ran any review posture, add `posture:` with the line copied verbatim from
  `review_posture.py`, including a `-PARTIAL (n/N lanes; missing: …)` result (R9.1, R9.2). If you ran
  none, claim none: omit `posture:` and say "no posture run" in `seats:`.
- **Cross-family (R3, R9.3).** Write `validated` only if a seat from a different model family
  produced evidence recorded in `seats:`.
- **Author filings.** A filing with `author_of_candidate: yes` is harvested but never counts toward
  eligibility (RULINGS.md:1192).

## Clause table (one line per clause, all eight)

```
UFK-<n> | <ADOPT | ADOPT-WITH-CHANGE | DISTINGUISH | REJECT | UNMEASURED> | <your mechanism: path or tool> | PROOF: <command you ran> -> <result you observed>
```

| Disposition | Meaning | PROOF must show |
|---|---|---|
| `ADOPT` | the project already satisfies the clause as written | the clause's **Check** run in your repo (UFK-7 and UFK-8 in a bus scratch worktree) |
| `ADOPT-WITH-CHANGE` | it holds with a wording change | the Check run in your repo; also add a finding line (below) with `REPLACES` |
| `DISTINGUISH` | the clause does not fit your project | why, and what you do instead |
| `REJECT` | the clause is wrong | a scenario in your repo where following it causes harm |
| `UNMEASURED` | you did not run the check | nothing; it counts for nothing and is never a pass |

`PROOF` must be something you ran or observed **in your own repo, on your own machine**. A command
copied from another project's filing without re-running it is the trap recorded in TRAPS.md
(2026-09-14, "A receipt copied between projects carried the source project's CLI flags").

## Findings (same `§` shape as other adjudication subjects, so `harvest-status.py` counts them)

```
§UFK-<n> | "<≤25-word quote from the candidate>" | <defect, ≤40 words> | REPLACES: "<exact anchor>" -> "<replacement>" | PROOF: <scenario or test>
```

Findings not grounded in your repo go under a `## Untested` heading. Prose reviews are not harvested.

## Adapter declaration (required)

```
## Adapter
artifact: <kind> | class: <class>[+<class>] | executed_by: <tool, role or human> | evidence_identity: <commit | sha256+store | attestation record | rubric scores+judges>
```

One line per artifact kind. A `judgment` adapter also names its rubric file and when that rubric was
fixed.

## Dispositions (harvester)

`<project>.dispositions.md` carries `filing_blob: <blob>`, `spec_commit: <sha>`, and one line per clause
that answers the filing:

```
UFK-<n> | <ADOPTED | ADOPTED-CONDITIONAL | REJECTED | ROUTED> | <reason>
```

A REJECT-with-PROOF with no matching `UFK-<n>` answer line keeps that clause ineligible.

## Landing

Commit the filing plus one RECEIPTS.md row on `review/<project>-<YYYY-MM-DD>`, and push that branch
without asking (R7). It is done only when `git ls-remote origin refs/heads/<branch>` matches the local
tip. Never push a filing to master.
