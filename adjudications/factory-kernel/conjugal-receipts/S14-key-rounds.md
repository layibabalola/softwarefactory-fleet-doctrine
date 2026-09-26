# S14 — key rounds, receipts (Conjugal, `S14-jev-evidence-shadow-beside-check-ordering`)

Subject: a Jev claim-versus-evidence shadow beside `coordination/kernel-dogfood/check-ordering.py`
(CJ-B8 of the fleet Jev shadow-mode standard; shadow only, logs hashes to a gitignored path, changes
no verdict). Declaration Conjugal `b8f78db0b` (author 2026-09-19T22:08:04-05:00), before any code.
Candidates on Conjugal `master`, each pushed: round 1 `f9ea1dc86` (tree `14a62a6b9e85eab245960c6e67aa75be03f660ab`),
round 2 `5185f08c5` (tree `e827e33e9b4e92f67d6047672ad0cdb9aa44f7a3`), round 3 `16eccf6df`
(tree `534e49da0ecacfeb9381930a9b4be14eef9904d7`). Key: class `codex-openai`, `gpt-6-astra`, high effort.

| Round | Verdict line (verbatim) | Rollout file under `%USERPROFILE%\.codex\sessions\` | Bytes | Rollout SHA-256 | Verdict-line SHA-256 |
|---|---|---|---|---|---|
| 1 | `REFUSE 14a62a6b9e85eab245960c6e67aa75be03f660ab` | `2026/09/19/rollout-2026-09-19T23-07-05-01a0bcff-06cb-73c1-a790-ea594ee6c744.jsonl` | 817,540 | `913a36deeff218b3a5d4dd454606badf2a2d815fe189f7586f40233845a595ef` | `0b8d435caf64d920ca2ea6b024d41ba0620378e0418f78c46f243cd303e55767` |
| 2 | `REFUSE e827e33e9b4e92f67d6047672ad0cdb9aa44f7a3` | `2026/09/20/rollout-2026-09-20T09-08-46-01a0bf25-e22f-7883-a1f0-9af71a8a706f.jsonl` | 1,285,618 | `9a8547d9cfd45e391d2517695c0e5e30d4b6f5ce0684431d611ae5bfc9f1a61b` | `06951e98ed29a2942edba4408401c92534db4e61f3c8c9e6eef8a76452183a9b` |
| 3 | none: `KEY_UNAVAILABLE_BY_PROVIDER` — the provider's cybersecurity filter terminated the review while it read the egress-screen test fixtures | `2026/09/20/rollout-2026-09-20T09-27-23-01a0bf36-ef0c-7610-8a53-d2cc32e9fd7e.jsonl` | 953,631 | `a29487162829fcc50bc3fa5d51a81deca6fb294cd0888c5a6876042ba2e18bfc` | n/a |

Mechanism, round 1: "Confine writes to a protected shadow destination, validate and allowlist every
logged response field, eliminate verdict-bearing stdout, and require evidence location independent of
the claim's own quotation." Round 2: "Confine every write to a protected shadow destination and exclude
the claim's own Outcome from every evidence-location route" (same mechanism, narrowed → the README's
patch-versus-narrow adjudication by three read-only panelists ran; all three: PATCH). Round 3 patched
both residuals (writes confined to `<repo>/scratchpad/` only; every `coordination/kernel-dogfood/S*.md`
excluded from evidence candidates on every route; located pairs 41 → 31) and received no verdict.

Disposition: **PARKED, K6 NOT OBTAINED, counts ZERO.** Wall: a `codex-openai` key cannot finish
reading an egress screen's own fixtures (secret-shaped strings, home paths, e-mail shapes). Resume
actor: a key of another independence class from the producer that the filter does not reach, or the
same class once authorised for security-adjacent review. A fourth round on this mechanism is not
authorised (ceiling, bus `639f454`). Second instance of the S8 r2 / S10 wall: a K6 route for subjects
whose fixtures look like secrets does not exist in this class.
