# `cos-feedback.v1` — field meanings

Each live feedback file is Markdown at `cos-feedback/<project-slug>/pr-<N>.md`.

The first lines are a **frontmatter-ish header**: plain `key: value` lines (no YAML fences
required). Blank line, then Markdown sections.

## Header fields

| Field | Required | Meaning |
|---|---|---|
| `schema` | yes | Must be `cos-feedback.v1`. |
| `project` | yes | Fleet board slug (same id as `specs/<project>.md`, e.g. `mlv-app`). |
| `repo` | yes | GitHub `owner/name` of the project repository under review. |
| `pr` | yes | Pull request number (integer). Must match the filename `pr-<N>.md`. |
| `head` | yes | Full or short SHA of the commit tip that was reviewed. Consumers compare to PR HEAD. |
| `reviewed_utc` | yes | When CoS completed this review, UTC RFC3339 (e.g. `2026-09-10T11:30:00Z`). |
| `event` | yes | Why this rewrite happened. One of: `pr-opened` \| `pr-pushed` \| `review-requested`. |
| `verdict` | yes | CoS summary posture. One of: `merge-ready` \| `merge-when-ci-green` \| `not-merge-ready` \| `info`. |
| `ci_summary` | yes | One line on CI / checks state as observed at review time (or `unknown` / `n/a`). |

### `event` values

- `pr-opened` — first CoS pass after the PR appeared.
- `pr-pushed` — rewrite after a new head was pushed to an existing PR.
- `review-requested` — rewrite triggered by an explicit review request (human or hub).

### `verdict` values

- `merge-ready` — CoS sees no open blockers in the reviewed head (does **not** override CI or humans).
- `merge-when-ci-green` — content looks mergeable once required checks pass.
- `not-merge-ready` — one or more items under `## Blockers` should be addressed first.
- `info` — notes only; no merge posture claimed.

`verdict` is **data**, not authority. Branch protection, required checks, and project owners decide merge.

## Body sections

After the header blank line, use these Markdown headings (omit a section only if empty and
the verdict does not require blockers):

### `## Blockers`

Merge-blocking or CI-blocking items. Each item should be actionable: what failed / what is
wrong, where (path, check name, log hint), and a concrete fix hint. Prefer bullets.

### `## Improvements`

Non-blocking but actionable code or CI improvements CoS recommends for this head.

### `## Notes`

Non-blocking context: observations, links to related PRs/issues (numbers only if public),
scope limits of this review.

## Example shape

```markdown
schema: cos-feedback.v1
project: mlv-app
repo: layibabalola/mlv-app
pr: 123
head: abcdef0123456789
reviewed_utc: 2026-09-10T16:00:00Z
event: pr-pushed
verdict: merge-when-ci-green
ci_summary: unit green; e2e pending on ubuntu-latest

## Blockers

(none)

## Improvements

- `src/foo.ts`: prefer early return over nested else in `parseRow` (lines 40–52).

## Notes

- Review scoped to diff vs base; did not re-audit unrelated modules.
```

## Law 4 carve-out (what may appear)

Allowed: PR numbers, SHAs, check names, file paths, line ranges, concrete fix hints,
public issue/PR references.

Forbidden: credentials, tokens, secrets, raw transcripts, customer data, private payloads.

## Versioning

- `schema: cos-feedback.v1` is the only version defined here.
- Additive optional header keys may appear later; unknown keys are ignorable by readers.
- Breaking renames require a new `cos-feedback.vN` and an update to this document.
