# S16 — key rounds, receipts (Conjugal, `S16-jev-opt-in-vote-salvage-shadow`)

Subject: an opt-in, shadow-only Jev reading beside the vote-salvage regex in `scripts/tally-votes.sh`
(CJ-A3 of the fleet Jev shadow-mode standard, product path — the first product-path subject; two of
every three declarations target a product path per the README rule). Declaration Conjugal `5dafef1a3`
(author 2026-09-20T16:23:42-05:00), before any code; `PRIVACY.md` was amended by the owner's ruling in
the same declaration commit to "does not phone home unless you opt in … off unless you set
`PAIRPROG_JEV=1` **and** provide an `AI_GATEWAY_API_KEY`". Candidates on Conjugal `master`, each
fast-forwarded and pushed: round 1 `20158cff0` (author 17:04:48, tree `404920cd2413ccabe0c62c592d64bf1a42040a4d`),
round 2 `a587f2a18` (author 19:18:49, tree `61617bab5aa5d8d191718732162e4e6341c5d339`), round 3
`4d9baf1de` (author 20:17:12, tree `b924b639dd9261697ae9e7af704c8ccaa906a630`), post-round-3 delivery
fix `f0c9485a1` (author 21:36:21, unkeyed, identity `698526a798e78a9ab653c0f53bcc581385c02625`,
recomputable via `git -C C:\code\Conjugal rev-parse f0c9485a1^{tree}`). Key: class `codex-openai`,
`gpt-6-astra`, high effort, each round a detached OS process bound per-command; ordering witnessed by
`coordination/kernel-dogfood/check-ordering.py` against AUTHOR dates.

| Round | Tree | Verdict line (verbatim) | Rollout under `%USERPROFILE%\.codex\sessions\2026\09\20\` | Rollout SHA-256 | Verdict-line SHA-256 |
|---|---|---|---|---|---|
| 1 | `404920cd2413ccabe0c62c592d64bf1a42040a4d` | `REFUSE 404920cd2413ccabe0c62c592d64bf1a42040a4d` | `rollout-2026-09-20T17-10-16-01a0c0de-b7d5-7020-9f0c-c2672d125e62.jsonl`, 827,589 bytes | `e7666d27f5c3214b05fb27e1295f2a4f507d4ea7a6b0d1a11c408762a51161c0` | `7c868c86dd107a22e90b4496dc2a2eb096195a0f6d67911b974b5163243ff7ea` |
| 2 | `61617bab5aa5d8d191718732162e4e6341c5d339` | `REFUSE 61617bab5aa5d8d191718732162e4e6341c5d339` | `rollout-2026-09-20T19-19-22-01a0c154-e975-7ef0-9701-2f212104a855.jsonl`, 920,420 bytes | `77e661a1933a409310864f84372ed3ee87b62b947e34bbb7476c6a77cacfa9a3` | `0736bbfa37a8914a8217e8bb68d00070cdd0e4294896631882353043a1cc0d8c` |
| 3 | `b924b639dd9261697ae9e7af704c8ccaa906a630` | `REFUSE b924b639dd9261697ae9e7af704c8ccaa906a630` | `rollout-2026-09-20T20-17-27-01a0c18a-16e3-7040-b133-256544c7bace.jsonl`, 881,366 bytes | `9c8a22e2ae88e2d66fb1eef765182e05f14fdd681810f18534482a2c0301a87e` | `4a66a3c17eb56baf2bc553cc4998e3f3aa670f29c0e73182fe8cc590fdbda3ac` |

Every verdict line was confirmed byte-present in its rollout before hashing. No round was terminated by
the provider filter.

**Mechanism per round (one line each; every finding reproduced by the key and fixed in the next
commit).** Round 1: unvalidated log destinations and response fields, a non-equivalent Law-4 port, and
an unbounded sidecar call (five findings; the round-1 suite had also never reached its fake sidecar —
disclosed in round 2). Round 2: normalize filesystem identities and reject every containing repository;
reject active stdout/log aliases; validate every NDJSON line; allowlist response-map keys — the same
mechanism narrowed from round 1, so the patch-versus-narrow adjudication ran: two read-only panelists,
one for PATCH with a verified diff, one for PARK and re-scope to a Python helper (recorded as the
fallback). Round 3 patched all four round-2 residuals and was refused on two narrower ones — a
two-object sidecar response leaking its first `code`, and an existing log missing a final newline
corrupting NDJSON on append — both fixed in `f0c9485a1` and pinned by 65 test assertions, unkeyed.

**Wall named:** a bash-resident write path on a msys/Windows hybrid namespace cannot be made
handle-authoritative; every round closed the demonstrated attacks and the next round found a narrower
alias. **Resume actor:** S17 — the product hook delegates all I/O to a Python helper reusing S15's
`secure_open_for_append`, `sanitize_response`, and the imported `screen_law4`, declared before code with
a K3 set that includes the helper.

**Bars, measured on the round-3 tree (producer; the key confirmed 1, 3, 4, 6 and refuted the
alias/validation residuals now closed):**

| Bar | Status |
|---|---|
| 1. opt-out no-op, three ways | met: byte-identical to `git show 5dafef1a3:scripts/tally-votes.sh` over the fixtures, no file under a fake HOME |
| 2. the vote never changes | met: opposite-pick fake at 1.0 → output identical, `agree:false` logged |
| 3. egress tested | met: the real `doctrine_outbox.screen_law4` via python, fail closed; the key's single-backslash path and newline-split bearer bypasses closed in round 2 |
| 4. nothing reads the log | met on the scoped census |
| 5. live fidelity, opt-in | met and it is the product finding: 20 packets through the real hook, 20 lines, 0 fallback, 18 agree, 2 disagree — the two known salvage reversals at confidence 1.00 and 0.96 — $0.0008 |
| 6. mutation proof | met: gate, screen, pick-mutation guards RED in isolation; controls GREEN |

**Disposition: PARKED, K6 NOT OBTAINED after three rounds, counts ZERO.** The measured deliverable
stands regardless — the product finding: 2 of 20 salvaged votes read the other way at confidence ≥ 0.96,
reporting only, no vote changed.
