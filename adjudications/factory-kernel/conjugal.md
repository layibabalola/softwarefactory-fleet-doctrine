# Factory-kernel dogfood filing — conjugal (Conjugal, machine Bachelor / Dell XPS 17)

project: conjugal
kernel: fleet-factory-kernel r2
profile: code@r2
instance: NONE in Conjugal's tree (KERNEL: DOGFOOD-PENDING Sol); map reproduced below under ## Instance map
subjects: 0 end-to-end in this window (no owner-authorised subject was runnable by this seat; see ## Queue at filing)
window: 2026-09-14T17:23Z .. 2026-09-15T01:05Z
health: assurance=UNEVALUABLE operability=PRESSURED
providers: claude(claude-opus-5 validator) codex(gpt-5.6-sol validator) — both cleared `VALIDATION-COMPLETE`; filing validation only, no subject work
posture: no model review (the filing was checked by two ad hoc non-author seats; that is not a posture)

**Status.** Measured by a Conjugal Opus 5 session (effort high) in Conjugal worktree `stoic-burnell-2e0be3` at Conjugal
`1e8075df6`, reading the bus at `7938f05`. This is operational evidence, not a review (R1). **Steward rule (kernel §5):**
Conjugal is the steward and this is the steward's own filing. Conjugal does not write `conjugal.dispositions.md`; a
second project's arbiter or the owner rules on it. Conjugal's automated steward excludes it by configuration
(Conjugal `coordination/harvest/harvest-config.json`, factory-kernel `"exclude_filings": ["conjugal"]`).

**Why DOGFOOD-PENDING and not DOGFOOD.** PROMPT K §2 forbids the in-tree edit when files have exclusive owners or
adoption needs the project's own ratification. Both hold for Conjugal. Its operating contract says "Sol alone also writes
HUB Status, Decisions, and the Authority Source Index" (Conjugal `CLAUDE.md`). Every lane shares one checkout. The
contract file `CLAUDE.md` is 8,573 B, and `check-doc-size.py` rates it `entry WARN`. Adoption of bus doctrine in Conjugal
has always gone through a recorded distinction until the lanes prove the runtime (bus `specs/conjugal.md`:
`DISTINGUISH(224a6705…, PENDING_RUNTIME_ADOPTION)`). The ratifier is Sol. The adoption request travels as this filing and
the `KERNEL:` line; see K2 for why Conjugal has no in-project channel for this workstream.

## Queue at filing

- **Lane routes.** The newest floor wake says "IDLE NO-ROUTE, 0 eligible exact-verification routes" (Conjugal
  `1e8075df6`, Opus dead-man floor, 2026-09-14T23:26Z). This is testimony from the floor, not this seat's reduction.
  `derive-fleet-state.py` samples ledger advancement over 360 s and was cut off at this seat's 100 s timeout. Lane routes
  are claimed only by lane seats, and this session is not one.
- **Steward harvests** (real, owner-authorised: "I want harvest to be automated continuously", kernel §5). `python
  "C:\code\Conjugal\coordination\harvest\harvest_runner.py" status` showed `factory-kernel` open=5 and
  `approach-a-design` open=2. Run `20260914T230404Z-e19dbdce` (approach-a-design; filings agent-bridge and airmypc)
  returned `PARKED-CAPACITY` at 23:11:51Z, with `retry_utc` 2026-09-19T08:09:00Z. At 00:49:04Z the runner logged
  `PARK-CLEARED-ROTATION`. `~/.codex/auth.json` mtime is 2026-09-14 19:37:40-05:00; `~/.claude/.credentials.json` is
  unchanged since 16:17-05:00; Claude parity fp `b4d2646b85c1` is the same before and after. So the Codex account
  rotated. Run `20260915T004904Z-06b1bd96` spawned at 00:49:29Z. Its Astra seat wrote `LANE-COMPLETE` at 00:52:32Z. The
  `claude -p` session exited 0 at about 00:52:38Z, and its last output was "still waiting on Astra's arbitration …
  running in the background". The runner recorded `FAILED SESSION_NO_SENTINEL` (`detail: exit=0`), `backoff_until`
  01:22:40Z, and the scheduled task's LastTaskResult became 1. The runner is automated. A manual
  harvest would compete with it, and its arbiter seat (`gpt-6-astra`, per `coordination/harvest/prompts/harvest-session.md`)
  was the parked resource and then answered. **This seam is blocked, not a completed subject.** It is filed below as K4, K8 and K12 evidence,
  not as a K3–K7 subject.

## Clauses

K1 | FIT | "A candidate is never accepted on evidence whose only author is its producer" | Conjugal lane wire, `grep -rhE "^(READY\|REVIEWED\|VERIFIED\|CLOSED\|CLAIM) " coordination/lanes/`: 67 CLAIM / 28 READY / 99 REVIEWED / 11 VERIFIED / 6 CLOSED rows. The roles are split by lane file, and the steward's self-filing exclusion is in code (`harvest_runner.py` `eligible()` emits `SELF-FILING … needs another project's arbiter or the owner`). No completed subject was traced actor by actor in this window | PROOF: a CLOSED row in `coordination/lanes/` whose READY and VERIFIED rows are written by the same lane

K2 | FRICTION | "Each project keeps one register of what needs the owner and what does not" | Conjugal has no single register. Authority is spread across `CLAUDE.md` §Non-negotiables; `AGENTS.md` → `coordination/user-directive-2026-08-17-autonomous-blocker-remediation-v3.md` (107 lines); 37 `coordination/user-directive-*.md` files; `coordination/product/AUTHORITY.md` (43,932 B, `check-doc-size.py` `working BREACH`); and HUB Decisions (Sol-written). **Cost, measured here:** to decide whether the PROMPT A receipt and the instance map could go in-tree, this seat read 3 of those sources and still fell back on PROMPT A's "if you cannot tell" rule. No channel exists for the kernel-steward workstream. `coordination/comms/README.md` gives each lane one single-writer file. Its one seatless channel, `hub-kernel.md`, is "written only by the `hub-kernel` spec workstream", a different workstream. So this adoption request has no in-project carrier | REPLACES: "the register's path, and one decision the project took without asking" -> "the register's path, the command listing every other file that grants or reserves authority (expected empty), and one decision taken without asking" | PROOF: a single Conjugal file that every source above defers to

K3 | UNEXERCISED | "the identity string of one subject, and the command that recomputes it" | No subject ran. Instance: the wire rows cite a commit SHA (`CLOSED @ 1d772adaed78…`, "full subject SHA"), not the profile's tree OID | PROOF: n/a until a subject runs

K4 | FIT | "Never exit code, output size or silence" | Three negative cases, all in this repo. (0) Conjugal's harvest runner refused a `claude -p` harvest session that exited 0 without its sentinel: run `20260915T004904Z-06b1bd96`, `FAILED SESSION_NO_SENTINEL`, `detail: exit=0` (## Queue at filing). No partial harvest landed. (1) `python coordination/tools/check-doc-size.py 2>&1 \| tail -3; echo "exit=$?"` printed `exit=0` because the pipe reports `tail`'s status; the unpiped re-run exited **1**, with `BREACH coordination/product/AUTHORITY.md`. (2) `resumability-check.py` printed `PASS resumability (docs/architecture/approach-a @ 1e8075df6)`, a PASS scoped to one workstream by its `--ws` default and not counted as a hub resume proof (see K9) | PROOF: `check-doc-size.py` exiting 0 on this tree

K5 | UNEXERCISED | "Before work starts, a subject declares its profile and profile version" | No subject ran. Instance: NONE, since no Conjugal artifact records a profile line. A typed resource terminal did occur on the steward's blocked harvest (## Queue at filing); it is not claimed here because no profile line or identity was recorded before that work | PROOF: n/a

K6 | UNEXERCISED | "Every acceptance includes a key from an independence class other than the producer's" | No subject ran. Instance: VERIFIED rows are written by Sol (Codex) in `coordination/lanes/sol.md`, over Claude-lane production | PROOF: n/a

K7 | UNEXERCISED | "how the project detects an accepted subject that never delivered" | No subject ran. Instance: the delivery target is Conjugal's local `master`, which is 122 commits ahead of `origin/master` at `86a092fdf` (00:4xZ) and 123 ahead at `7bf1a92d2` (01:00Z) (`git rev-list --left-right --count master...origin/master` in `C:\code\Conjugal`); master moves during the window. Detector: NONE, since `git grep -l CLOSURE_INCOMPLETE -- coordination docs scripts` returns no Conjugal file | PROOF: a Conjugal tool that lists CLOSED subjects absent from master

K8 | FIT | "Work that needs no inference continues" | The last quota event was `PARKED-CAPACITY` at 2026-09-14T23:11:51Z (Codex usage limit on the harvest arbiter seat). After it, the steward kept ticking: `IDLE` at 23:19, 23:34, 23:49, 00:04, 00:19 and 00:34Z, and `Get-ScheduledTaskInfo Conjugal-Harvest-Steward` shows LastTaskResult 0. The park named its resume condition ("clears at the first tick after an account rotation", Conjugal `f1d9fa12a`), and that condition fired: a real Codex account rotation (auth.json mtime 00:37:40Z) cleared it at 00:49:04Z, 97 min after the park instead of the ~105 h `retry_utc`. Claude floors kept committing throughout (Conjugal `96810aa89`, `1e8075df6`). The scheduled task's non-zero result at 00:49Z comes from the session failure in K4, not from a capacity stall | PROOF: a harvest tick between 23:11:51Z and 00:49:04Z that did not fire, or a park that cleared with no auth-file change

K9 | FRICTION | "the resumability gate's command and its last passing output" | `python coordination/tools/resumability-check.py` → `PASS resumability (docs/architecture/approach-a @ 1e8075df6)`, exit 0. The gate covers the Approach A workstream by default (`--ws docs/architecture/approach-a`). The hub fleet resumes through `coordination/RESUME.md` and `derive-fleet-state.py`, whose 360 s sampling window does not fit a bounded session call (this seat's 100 s call was cut off). **Cost:** one gate per workstream, with no single command that proves the whole project resumable | REPLACES: "the resumability gate's command" -> "the resumability gate's command for every entry point the project's resume trigger can select" | PROOF: a Conjugal gate command that covers the hub fleet and the Approach A entry together and finishes under 120 s

K10 | FIT | "records the account it was derived under" | `python "C:\code\Conjugal\coordination\tools\check-cli-auth.py" --allow-live-probe` → `PASS inference answered in 6.3s; accounts match`, exit 0. The bus `tools/check-account-parity.py` → `[parity] MATCHED`, desktop and cli fp `b4d2646b85c1`. `~/.claude/machine-inventory.yaml` shows `probed_under: b4d2646b85c1`, generated 2026-09-14T19:38:54-05:00 | PROOF: an inventory `probed_under` that differs from the parity fingerprint at filing

K11 | FIT | "the quoted title line of each rule the project confirms it meets" | The quoted titles are under ## R1–R9. This seat is Opus 5 and is not below the floor (R1). The filing names no posture (R9). The branch is pushed and verified by ls-remote (R7) | PROOF: a rule below that this filing violates

K12 | FRICTION | "The steward harvests every filing and answers each one" | `python tools/harvest-status.py factory-kernel` → `open=5` (3 UNHARVESTED, 2 STALE). None was answered in this window: the steward was parked 23:11Z–00:49Z, and its first run after the park (approach-a-design) failed `SESSION_NO_SENTINEL` and backed off until 01:22:40Z. The steward's own filing (this one) is excluded by configuration, but **nothing routes it to the "second project's arbiter"**: another project's `harvest-status.py --all` lists open counts only for subjects whose spec that project owns (PROMPT A §4), so a sibling is never told | REPLACES: "A second project's arbiter, or the owner, rules on them" -> "A second project's arbiter, or the owner, rules on them; the steward names that arbiter in HARVESTS.md when the filing lands, and PROMPT A §4 surfaces it to the named project" | PROOF: a sibling's PROMPT A run that reports conjugal's kernel filing as awaiting its arbitration

P:code human-gates | FRICTION | "the register is reachable from every session checkout and classifies fleet-tool writes, including permitted locations" | No Conjugal authority source says where fleet tooling may write (the PROMPT A receipt, a PROMPT K instance map). This seat applied PROMPT A §2b's fallback and wrote the receipt to `C:\Users\layib\.claude\doctrine-sync\Conjugal.json` | REPLACES: none proposed; this is an instance gap, listed under ## Instance map | PROOF: a Conjugal register entry naming permitted fleet-tool write locations

P:code resource-terminals | FIT | "parked work names its resume condition, and work not requiring the unavailable resource continues" | Same evidence as K8: `retry_utc` plus a rotation clear, with ticks continuing | PROOF: as K8

P:code dispatch-preflight | FRICTION | "retains its result, the inventory snapshot and digest, and account-parity evidence" | Identity-only parity came first (SessionStart hook `[parity] MATCHED`, no inference). `check-cli-auth.py --allow-live-probe` is itself the first provider call ("explicitly authorize one live inference capacity probe"). No Conjugal dispatch tool retains the inventory digest. **Cost:** a manual step. This seat hashed it after the fact, `sha256(~/.claude/machine-inventory.yaml)=8b6cf0ab4b2c057e…`, and the PROMPT A receipt records only the path | REPLACES: none; this is an instance gap (no Conjugal spending tool retains the digest) | PROOF: a Conjugal dispatch receipt carrying an inventory digest

## Instance map

The in-tree edit was not made (DOGFOOD-PENDING Sol). Clause → the Conjugal mechanism, or NONE:

- K1 → per-lane wire `coordination/lanes/{sol,luna,fable,opus}.md`; the self-filing exclusion in `coordination/harvest/harvest_runner.py`
- K2 → **NONE** as one register (the fragments are listed in K2)
- K3 → CLAIM rows on the lane wire; `coordination/maintenance/quarantine-stale-commit-coordination-lease.ps1`; identity = commit SHA (the profile asks for a tree OID)
- K4 → dead-man floor wake logs and state under `coordination/deadman/`; harvest receipts via `harvest_runner.py status`
- K5 → **NONE** (no declared profile line per subject)
- K6 → Sol (Codex) VERIFIED rows against Claude-lane production
- K7 → CLOSED rows; delivery to local `master`; accepted-not-delivered detector **NONE**
- K8 → `harvest_runner.py` capacity park (identity-stamped rotation clear); the provider governor is DISTINGUISHed on the bus
- K9 → `coordination/tools/resumability-check.py` (Approach A); `coordination/RESUME.md` and `coordination/tools/derive-fleet-state.py` (hub)
- K10 → `coordination/tools/check-cli-auth.py --allow-live-probe`; `~/.claude/machine-inventory.yaml`
- K11 → PROMPT A §3 quoting (this filing); no Conjugal-local mechanism, so **NONE** in-tree
- K12 → `coordination/harvest/` and scheduled task `\Conjugal-Harvest-Steward`

## R1–R9

- "R1 - A session below the review floor does not review." Met: Opus 5 seat, no review claimed.
- "R2 - Completion is positive evidence from the lane, never absence of error." Met: see K4.
- "R3 - A cross-family claim is computed, not asserted." Met: both families' validator lanes cleared the sentinel (## Validation). The claim covers filing validation only.
- "R4 - Every project-scoped reference names its project." Met: SHAs are prefixed Conjugal or bus.
- "R5 - Provider and model inventory is machine-scoped and probe-derived." Met: see K10.
- "R6 — the invariant is binding; the implementation is not." Met: parity checked before any provider work.
- "R7: review branches always push" Met: `review/conjugal-kernel-2026-09-14` is pushed and verified by ls-remote.
- "R8: work with the bus is left synced" Met: see the report's sync line.
- "R9: a posture is named only when it ran in full" Met: `posture: no model review`.

## Validation

Question asked of both seats, verbatim: "find a claim, command or flag here that is false, copied from another project, or
never run in this repo". Both had fresh context, were not the author, and ran read-only. Prompts and raw outputs stay local
(R7.4).

- **claude-opus-5** (subagent): `VALIDATION-COMPLETE findings=7`.
- **codex gpt-5.6-sol** (`codex exec`, effort high, `-s read-only`, session `01a0a28b`): `VALIDATION-COMPLETE findings=10`.
- **Cross-family: YES, computed.** One lane from each family cleared the sentinel (R3).

Each finding was re-derived by the author before landing.

| # | Finding | Seat | Re-derived | Disposition |
|---|---|---|---|---|
| 1 | "parked … until 2026-09-19", but the park cleared at 00:49:04Z | both | receipts.jsonl `PARK-CLEARED-ROTATION`; auth.json mtime 00:37:40Z | fixed (Queue, K8, K12); the respawn failure added as K4 (0) and TRAPS |
| 2 | "122 ahead" measured at an unnamed commit | both | `1e8075df6…origin/master` = 121; master `86a092fdf` = 122, `7bf1a92d2` = 123 | fixed (K7 names both) |
| 3 | dispatch-preflight marked FIT with the digest missing | codex | code profile row says "snapshot and digest" | FIT → FRICTION |
| 4 | the live probe is itself a provider call | codex | `--help`: "one live inference capacity probe" | fixed |
| 5 | "no channel for a non-lane session" ignores `hub-kernel.md` | codex | comms README line 29 | narrowed to the steward workstream |
| 6 | the TRAPS row calls the reader "Paste A" | codex | `bootstrap/README.md` line 36 **B** | fixed to Paste B |
| 7 | the TRAPS worktree basename was inferred, not run | claude | `REPO` is a declared input, never assigned | marked "inferred from the text, not run" |
| 8 | the validation placeholder, providers line and R3 | both | true before landing | filled |
| 9 | R7 not pushed / R8 not synced | both | true before landing | closed by landing; ls-remote and sync line in the report |
| 10 | posture free text, not R9 tool output | claude | kernel §4: "else: no model review" | kept; the note says validation is not a posture |

## Untested

- Whether Conjugal's stale in-tree `.claude/doctrine-sync.json` (head `862df45`, untracked, not ignored) affects any
  Conjugal gate that censuses untracked paths. Its effect on paste B is measured and filed in TRAPS; its effect on
  Conjugal's own gates was not tested.
- `account_identity()` in `coordination/harvest/harvest_runner.py` hashes the whole `~/.claude/.credentials.json`, so
  an OAuth token refresh that rewrites that file would look like a rotation and clear a Codex park early. Not observed:
  in this window it was the Codex account id that changed.
