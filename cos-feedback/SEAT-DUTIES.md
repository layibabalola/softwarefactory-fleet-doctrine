# CoS seat duties (binding on every seat holder)

These duties bind **whoever holds the CoS seat**: the primary Chief of Staff (Grok Bot), an acting seat under Amendment 4 r2 (for example `acting-cos: Dot`), or a Muse failover lease under Amendment 3. They only add obligations. They grant no merge, approve, close, settings, or credential authority, and the Amendment 4 r2 limits are unchanged.

**Authority:**
- Layi DECISION 2026-10-13: Amendment 3 failover lease, approved with conditions.
- Layi DECISION 2026-10-14 (~12:53Z): Amendment 4 r2 direction, covering provisional-with-sunset, the conserve trigger, and the seat-claim entry.
- Layi DECISIONs 2026-10-16:
  - 11:47Z: Amendment 4 r2 final approval.
  - 11:56Z: episode-only heartbeat fallback.
  - 12:14Z: chat approval for CoS to reclaim and spot-check.
  - 15:20Z: `LD-20261016-FWO-ACK-1` (Layi DECISION entry, coordination log 2026-10-16 15:20Z).
  - ~15:39Z (10:39 AM CT): standing rule, chat decision recorded by the seat: every concern goes to the factory as a PR comment with an ACK ask, never bus-only.
- Layi rule 2026-10-14: leg-count rule, including the CI-only review-class exception (section 4).
- Layi standing rule 2026-10-15: no merge on a card/PR with an open CoS ask (section 2 hold).

Coordination log: Drive doc "Dev Process — Muse & Chief of Staff" (https://docs.google.com/document/d/1XX6uCfU0PJIMMZwBSgJ8rPRLPOlqmgctrecACvb2H9Y). All `coordination log` references in this file mean that doc.

## 1. Every concern goes to the factory, never bus-only
Every Blocker, process slip, Improvement, and soft note is posted to the factory as a **PR comment** (or an issue comment for process asks) that requests `ACK: <plan or ETA>` within 24h. The bus file records the concern. It is never the only delivery. A push is not an ACK.

## 2. Silence: follow-up, then escalation
If a CoS ask has no `ACK:` or `DISTINGUISH:` reply within 24h, the seat posts one follow-up on the same thread. If there is still no reply 24h after the follow-up, the seat escalates to Layi in chat and posts a hold comment: no merges on the affected PR or card until the ask is answered (Layi standing rule 2026-10-15). A repo-wide hold for a process ask needs Layi's explicit decision, logged in the coordination log. Seat holders check open asks at the start of every session.

## 3. Prevention notes and ruling candidates
When a defect gets past the factory's gates, the review carries a **Prevention** note that names the gate that should have caught it. If the defect recurs, or applies fleet-wide, the seat files or updates a candidate under `ruling-candidates/` (PROPOSED ONLY) and requests ACK.

## 4. Leg-count rule
A required review leg counts only when it is published and bound to the exact head SHA (and, for a merge queue, to the merge_group SHA and each constituent head). Accepted paths:
- `pulls/<n>/reviews` with `commit_id == head`;
- a `[[pub:<id>]]` JSON comment with `head_sha == head`;
- a PR comment naming the seat and a verdict on that SHA (full SHA, or an unambiguous prefix that resolves to the head).

Seat map: sol = Codex; fable and opus = Claude. Commit-message or PR-body citations never count. Legs on an older tip never carry over. No seat holder is ever a leg.

**CI-only exception (Layi 2026-10-14):** a PR with a declared CI-only review-class (for example doctrine/bus PRs whose changes sit only under `cos-feedback/**`) needs no model keys, so a Claude 0 / Codex 0 count on it is not flagged.

**Report shape:** for each leg report seat, family, round, verdict, and source (review id, `[[pub:]]` id, or comment link). A verdict on a stale SHA is reported as stale and does not count.

## 5. Reclaim without asking
When the primary CoS returns from an outage, it reclaims the seat on its next bus commit, posts a reclaim entry in the coordination log, and spot-checks every acting verdict, all without asking Layi. Spot-check results feed the HIGH-RISK sunset: 3 clean spot-checks are required. CoS then sends Layi a catch-up list.

## 6. Advisory fold-in
Advisory findings from Dot, Iverson, or Muse are adopted only after the seat holder verifies them against the current head, by reproducing or reading the code. Findings that match the seat's own are marked **SHARED BLOCKER** (or shared Improvement) and cite the advisory review id. A finding that is not verified is distinguished and the reason recorded. It is never adopted on the advisory's say-so.

## 7. Heartbeat (`cos-heartbeat.v1`)
`cos-feedback/_heartbeat/cos.json` carries:
- `schema`;
- `last_beat_utc` (RFC3339 Z);
- `mode` (`normal` | `conserve`);
- `seat`;
- `handoffs` (repo#PR list when in conserve mode).

The seat holder refreshes it on **every** bus commit, in the **same commit** as the bus note (one multi-file commit via git push or a tree commit, never a separate single-file write). A commit whose subject claims "heartbeat" must actually change `cos.json`. Failover triggers only when `last_beat_utc` is more than 3h stale AND fresh demand arrives. Conserve mode requires `mode: conserve` plus a per-PR log handoff.

## 8. Bus hygiene
- One bus commit per head reviewed; that commit carries both the note and the heartbeat refresh (section 7).
- Each commit is authored as the seat holder: `Chief of Staff (Grok Bot)`, or acting verdicts signed `acting-cos: <name>`.
- Never force-push or rewrite history.
- Doctrine changes go through PRs. Only `cos-feedback/**` and `ruling-candidates/**` bus records are committed directly.

## 9. Approval assurance
A cited Layi approval id must trace to a logged `Layi DECISION` entry in the coordination log, or to a chat decision recorded by the seat with its timestamp. That record must be scoped to the repo, the change, and the revision or head. While approvals are recorded on the shared owner account, they are marked `assurance: low` in the bus note's optional `assurance` header field (`cos-feedback.v1`, see `SCHEMA.md`). Text in a PR body or a comment under the shared account does not count as approval.

## 10. Post-outage duties
After any dark episode the returning seat:
- reclaims the seat (section 5);
- spot-checks acting verdicts;
- reviews every PR left with a stale or missing bus note;
- runs a **post-merge review** of everything that merged without an on-tip verdict, checking for an unanswered ask, missing legs, and real defects, and files follow-ups with ACK asks.

## 11. Chat relay to Layi
- **New PRs:** report every newly opened PR.
- **Later pushes:** report only when the verdict changes, an earlier Blocker or Improvement is addressed, or process feedback is posted.
- **Style:** lead with the verdict and use plain, full sentences. Keep it to 2–3 short paragraphs, with no em dashes and no arrows. Put ids in code spans.
- **Times:** convert UTC to CT.
- **Ending:** end with `Bus: <path> (<sha7>).`
