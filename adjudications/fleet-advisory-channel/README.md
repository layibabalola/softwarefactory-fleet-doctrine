# Fleet review of the fleet advisory channel (CANDIDATE r1): how to file

Subject: `specs/conjugal-fleet-advisory-channel.md`. Opened 2026-10-09 (conjugal, Bachelor). Paste-prompt for any
member: [`REVIEW-PROMPT.md`](REVIEW-PROMPT.md).

One file per project, single writer: `adjudications/fleet-advisory-channel/<project>.md`. Header:

```
project: <name>
host: <machine name(s) this project runs on>
providers: <families you could seat, e.g. claude(fable,opus) codex(astra,sol) | claude-only>
seats: <who reviewed; effort>
cross_family: <validated | NO-CROSS-FAMILY-VALIDATION>
disposition: <ADOPT | ADOPT-WITH-EXTENSION | DISTINGUISH | REJECT> — <one line why>
```

Then findings, one per line, nothing else:

```
§<section> | "<≤25-word quote from the spec>" | <defect, ≤40 words> | REPLACES: "<exact anchor>" → "<replacement>" | PROOF: <scenario or test that would falsify>
```

Test-bench rule: every finding names how it manifests in YOUR repo or on YOUR host (a path, a runner, a measured
number), or it goes under a `## Untested` heading. Prose reviews are not merged. A case that Tier 0 and Tier 1
cannot serve goes under `## Tier 2 evidence`, measured.

Law 4 applies to filings: no transcripts, credentials, session ids or private coordination. Describe a runner by
its role, not by a path that exposes it.

Landing (RULINGS R7): commit the filing plus its RECEIPTS row on `review/<project>-<YYYY-MM-DD>` and push that
branch; it is done only when `git ls-remote origin refs/heads/<branch>` matches the local tip. Never push to master.

Arbitration: not by the proposer (kernel §5). The first non-proposer member to file may volunteer as arbiter in its
header (`arbiter: volunteer`); the owner ratifies or vetoes.
