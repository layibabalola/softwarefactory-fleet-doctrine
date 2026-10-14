# Review-key publication, required status, and declared review class

Status: **PROPOSED** (backed by `ruling-candidates/review-key-publication-r1.md` and
`ruling-candidates/review-keys-required-status-r1.md`). Doctrine is DATA (bus law 1).

## Why

Measured 2026-10-14 by Chief of Staff (Grok Bot):

- **No review workflows exist** in MLV-App, agent-bridge, context-ultra-salesforce or AdversarialLLM.
  Keys are dispatched by each hub on the box.
- **Legs live in private hub ledgers** (HUB-TICK entries, local `decision-record/v1`, `.claude/audits/`).
  MLV-App #409 went through about six sol/fable/opus key rounds, and they were only visible
  through implementer replies. `pulls/*/reviews` is 0 on every PR checked, AdvLLM included.
  AdvLLM is the one repo that mirrors verdicts to the PR as `[[pub:<id>]]` JSON comments.
- **Merges without a visible tip-scoped key:** MLV-App #427 (`1f35ac67`),
  context-ultra-salesforce #104 (`7bd78b0c`), agent-bridge #231 (`91241d4d`).

## Rule 1: publish every key verdict to the PR

Each review-key verdict (every seat, every round) is mirrored to the PR as one issue comment, in this form:

```
[[pub:<id>]]

{
  "seat": "sol",
  "family": "Codex",
  "round": 3,
  "head_sha": "<full 40-char sha the key reviewed>",
  "verdict": "CHANGES_REQUESTED",
  "class": "standard",
  "prev": "<pub id of this seat's round 2 pub, or null for round 1>",
  "ledger_ref": "HUB-TICK 20261012T1946Z step C",
  "findings": [ { "id": "R3-B1", "severity": "Blocker", "summary": "..." } ]
}
```

- Required fields: `seat`, `family`, `round` (integer, increasing per seat per PR), `head_sha`,
  `verdict`, `class` (the class the key was judged under), `ledger_ref` and `prev`.
  - `verdict` is one of `APPROVE`, `CHANGES_REQUESTED`, `COMMENT` or `UNAVAILABLE`.
    `COMMENT` carries no gate weight. `UNAVAILABLE` means the key had no capacity; it is a typed
    terminal, not an approval.
- `family` is fixed by seat (sol, and other Codex seats, are `Codex`; fable and opus are `Claude`).
  It is **data only, never an authority key** (RULINGS provider-family rule). Classes name the
  seats they require.
- `<id>` is the first 16 hex characters of `sha256("<seat>|<round>|<head_sha>|<verdict>|<prev>")`, so
  anyone can detect duplicates and check them.
- **Publisher trust:** a pub counts only when its comment author is the repo's registered
  **hub identity** (a named GitHub App or bot account, recorded in the repo's `CLAUDE.md` / `AGENTS.md`).
  Pubs from any other author, including the owner's account or a lane that shares a token, are ignored.
  An implementer lane must never hold the hub identity's credential.
- **Effective verdict:** for each seat, only the pub with the highest `round` whose `head_sha` equals the
  current head **and whose `class` is at least the current effective class** counts. If the class escalates,
  approvals given under the lower class don't count, and the seats the new class requires must approve again. So a later APPROVE supersedes an earlier CHANGES_REQUESTED from the same seat on
  the same head, and the reverse is true too.
- The mirror is append-only. A later round posts a new comment and does not edit the old one.
- **Hash chain (`prev`):** `prev` is the pub id of the same seat's previous round on this PR, or `null` for round 1.
  Because each id hashes its `prev`, a seat's pubs form a chain. The verifier walks each seat's chain from its highest round.
  A missing round, a `prev` that names no visible pub, or an id that doesn't recompute **fails closed** for that seat.
- **High-water mark:** the verifier is otherwise stateless, so it records, in its own check-run output (`output.text`, a JSON
  block), a per-seat mark `{seat: {max_round, pub_id}}`. On each run, it reads the mark from its previous check run on the
  same PR (Checks API, the newest `factory/review-keys` run by the verifier app) and carries it forward. If a seat's current
  visible max round is **below** the mark, or the marked pub id is no longer visible, the check **fails** with "pub removed: <seat> r<N>".
  So deleting a seat's latest pub (for example an r2 CHANGES_REQUESTED) can't bring back its r1 APPROVE.
- **What the verifier checks (only what it can observe):** the comment's author is the hub identity, the comment was never
  edited (`created_at == updated_at`), the chain is intact, and the high-water mark holds. Any edited or deleted pub
  invalidates that seat's key, and the hub must publish a new round.
- **What the CoS spot-check checks (the ledger):** the verifier can't read the private hub ledger. So the CoS
  spot-check, not the verifier, compares sampled pub body hashes and `ledger_ref`s against the hub's ledger at reconciliation.
  A mismatch, or a pub with no ledger entry, is reported as a Blocker on the hub.
- `factory/review-keys` is a check run **posted by a trusted verifier that runs only default-branch code**:
  - **Triggers:** `pull_request_target` (opened, synchronize, reopened, labeled, unlabeled, edited),
    `issue_comment` (created, edited, deleted) and `workflow_run` (completed, for the CI-only classes' CI). Never `pull_request`:
    that event runs the workflow file from the PR's merge ref, so a PR could edit the verifier or add a job with the same name.
  - **It never checks out or runs PR code.** It reads the PR only through the API (comments, labels, body and the changed-file list for the class rules).
  - **Trust anchors come from the default branch only:** the hub identity, the class rules and the CI-only check names
    are read from the base branch's `CLAUDE.md` / `AGENTS.md` / dispatch policy, never from the PR head. A PR that changes them takes effect
    only after it merges.
  - **Explicit head:** the verifier creates the check run through the Checks API with `head_sha` = the PR's current head
    (`pull_request.head.sha`, looked up fresh for `issue_comment` and `workflow_run`). Otherwise the check would attach to the default-branch
    or merge commit. Before posting, it re-reads the head, so a late run for an old head doesn't post on the new one.
  - A ruleset "required workflow", or a dedicated verifier GitHub App, is an acceptable alternative with the same properties.
- The verifier reports `success` only when every seat that the **effective class** (Rule 3) requires has an
  effective verdict of `APPROVE` on the current head, from the hub identity. For a CI-only class, it
  reports `success` once the named CI checks have succeeded on that head.
- It reports `failure` when any required seat's effective verdict is `CHANGES_REQUESTED`. It reports
  `failure` with a "key unavailable" summary when a required seat is `UNAVAILABLE` and the class
  allows no substitute. Otherwise the check is `in_progress` or `pending` (keys outstanding).
- **New head:** the check is recomputed, and verdicts bound to the old head don't count, so it reads
  `pending`, never `success` carried over from the old head.
  **Exception, a content-identical master sync:** if the new head is a merge of the default branch
  whose tree diff against the default branch is identical to the reviewed head's (`git diff
  <base>...<old_head>` and `git diff <base>...<new_head>` hash the same), the verifier carries the old
  head's effective verdicts forward and names the carried head in its summary.
- **Output:** the check's title stays short (`3/3 keys` or `missing: sol, opus`). GitHub caps the status
  description at 140 characters, so the full list (seat, round, pub id and comment URL per key) goes in
  the check-run summary, which has no such limit.
- Each consumer requires the check by **name `factory/review-keys` plus its source app** (GitHub Actions, or the
  verifier App) on the default branch. Pinning to the app alone isn't enough, because any workflow could post that name.
  What makes it safe is the triggers above plus **workflow-file protection:** `.github/workflows/` is owned in
  `CODEOWNERS` by the owner, and protection requires code-owner review, so nobody can change the verifier without the owner. The per-consumer checklist is in the ruling candidate.

## Rule 3: the review class is computed and can only be raised

- **The computed class** comes from path and diff rules written in the repo's dispatch policy (for
  example agent-bridge `docs/internal/DISPATCH_AND_REVIEW_POLICY.md`), and the verifier evaluates them
  on the current diff. If the rules haven't been written yet, the computed class is the strictest one
  (fail closed).
- **Declared class:** a `review-class:<class>` label plus the body line
  `Review class: <class> — keys required: <list>`. Only the hub identity or the owner (Layi) may set it.
  The verifier ignores a label applied by anyone else.
- **Effective class** = the stricter of computed and declared. A declared class that is lower than
  the computed class is ignored, so a PR cannot downgrade itself. Conflicting labels, more than one label,
  or a body line that disagrees with the label all fall back to the strictest class.
- When CI alone is the key (agent-bridge Routine local / class-A, where K6 is GitHub Actions PR CI on the
  exact head), the PR must say so:
  `Review class: routine-local (class-A) — keys required: CI on exact head; no model key`.
  It holds only if the computed class is also routine-local.
- Any change to labels, the body, the diff, a pub comment (created, edited or deleted) or CI completion triggers a recompute. If the effective class
  goes up after `success`, the check drops back to `pending` until the newly required seats approve.
