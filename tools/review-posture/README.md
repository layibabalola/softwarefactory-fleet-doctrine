# review-posture — the full Conjugal-standard review, as a tested tool

Runs every role of `specs/posture-templates-conjugal-standard.md` over the provider CLIs and reports the posture as a
measurement. Procedure around it: `bootstrap/lane-orchestrator.md` §2. Binding: RULINGS R2, R3, R5, R9.

| file | what it is |
|---|---|
| `roles.json` | the posture's roles, stages and lanes as data; the test fails if it drifts from the spec's roles table |
| `rubrics/approach-a-r15.json` | Conjugal Round 15 dimensions and seat lenses (verbatim); write another of the same shape for other subjects |
| `review_posture.py` | prompts per stage (binding-checked), panel scoring, classifier 2-of-3 tally, posture measurement |
| `run.sh` | stages A→D in one invocation; `--dry-run`, `--from B|C|D`, `--retry-missing` (re-dispatch only lanes that did not clear the sentinel) |
| `../../tests/test_review_posture.py` | pins every failure below |
| `tests/run-tests.sh` | **the** offline gate: `bash -n`, the self-heal suite, then pytest if available |
| `tests/test-selfheal.sh` | the offline self-heal suite — fake CLIs, temp `PATH`, temp dirs whose names contain a space |

```bash
export RP_REPO=... RP_SUBJECT=... RP_BENCH=... RP_OUT=...     # all absolute; RP_OUT outside the bus
bash tools/review-posture/run.sh --dry-run && bash tools/review-posture/run.sh
```

`--dry-run` generates and binding-checks every prompt it can and dispatches nothing, so it has
measured no posture: it prints `posture: NOT-MEASURED (dry-run)` and **exits 0**. It exits
non-zero only on a real binding failure (no model ids, an unbound prompt, prompts that did not
land in `RP_OUT`). A real run exits 1 when the measured posture is PARTIAL. Paths may be
relative and may contain spaces; all four are absolutised at startup.

Outputs in `RP_OUT`: `<lane>.prompt|txt|rc|log`, `environment.json`, `panel.json`, `panel-summary.txt`,
`classifier.json`, `rubric.json`, `rubric_id`. Only the filing and `rubric.json` travel; raw lane output never does
(Law 4).

## `environment.json` — what the run actually ran under

Written at the start of every run and **rewritten after the last stage**, data only, **never a credential or token**:
bash path and version, `uname`, host, python version, the **resolved invocation and version for each CLI family**, the
repairs applied, whether the working path contains a space, effective `core.autocrlf` in `RP_BENCH` and `RP_REPO`,
bench HEAD, subject blob sha, and the per-lane dispatch record.

`lanes[]` keeps **four distinct facts** per lane — `planned`, `dispatched`, `retried`,
`completed_with_sentinel` — plus `model_planned`, `models_launched` and the timestamped events behind them (also in
`dispatch-events.tsv`). `planned` comes from `roles.json` and is true of every lane in a dry run, in a blocked stage,
and in a family whose CLI never resolved; only `dispatched` means a process was launched. The field this replaces,
`models_dispatched`, was built by walking `roles.json`, so it called all 17 lanes dispatched no matter what ran.
**Do not attribute a finding to a model on the strength of `planned`.**

It exists because environment drift changed results silently and no filing could say what it ran under. A filing
digests it into `## Provenance` (`bootstrap/lane-orchestrator.md` §1b). A family recorded unavailable carries a
**cause** — the fault code and whether its repair verified — so that an auth-shaped symptom with a PATH cause is
legible as such. A run from a path containing a space is supported and must not behave differently —
and so is a **relative** `RP_OUT`/`RP_SUBJECT`/`RP_BENCH`/`RP_REPO`: all four are made absolute at
startup, because `claude` lanes `cd` into the subject repo before their redirections resolve and a
relative `RP_OUT` silently ran zero claude lanes while every codex lane ran. On Windows with a
native python, the four are additionally normalised with `cygpath -m` so bash and python resolve
them identically; `path_dialect` records which dialect was used.

## `SENTINEL_RETRY` — one retry, never a manufactured sentinel

A lane that exits `rc=0` with more than zero bytes and **no sentinel** is retried **at most once**, with the same
prompt. The first attempt is preserved as `<lane>.attempt1.*` and never overwritten; the runner records
`SENTINEL_RETRY lane=<n> attempt1_bytes=<b> result=<RAN|DID-NOT-RUN>`.

A lane RAN iff the sentinel is the **last non-blank line** of its output — the contract says
"Then stop. Nothing after this item", and a match anywhere in the file accepted the sentinel
followed by pages of prose. `run.sh:ran()` and `review_posture.py:ran()` implement exactly this,
and the offline suite (H1) drives **both** against one fixture so they cannot drift apart. CR is
tolerated; trailing blank lines are tolerated; trailing prose is not.

All the misses in a stage are collected, dispatched together and waited on once — N misses used
to cost N × the stage timeout.

The three things it must never do: **append** a sentinel to a lane's output, accept a **near-miss**
(`LANE-COMPLETE.`, or the line with trailing text), or retry more than once. `SENTINEL_LINE` is byte-identical
across every prompt. R2 says completion is a sentinel the lane emitted; a sentinel the runner supplied is not
evidence of anything, and a retry that can run twice is a loop that eventually produces one by chance.

## `BEGIN DATA` / `END DATA` — pasted bodies are delimited, and the contract is restated after them

Every pasted lane or arbitration body in the arbiter, consolidator and classifier prompts is wrapped in explicit
`BEGIN DATA` / `END DATA` delimiters, and the output contract is restated **after** `END DATA` with the sentinel as
its **final numbered item**. The sentence that names the marker (*"The END DATA marker above closes the quoted
material"*) is emitted **only when a data block exists** — the designer, lint and panel prompts have no pasted
material, and telling them a marker sits above them is a false statement in the very sentence that draws the
data/instruction boundary.

Measured 2026-09-14 (MLV-App, VIRTUAL-TEN): the arbiter returned a complete, correct arbitration twice — `rc=0`,
8,554 B and 7,997 B — with no sentinel, and stage C blocked, correctly. The prompt had appended the sentinel request
immediately after the last pasted block with no closing delimiter, so the request read as the tail of quoted data the
prompt had told the model to treat as *not instructions*; the ordered contract `(1)(2)(3)` did not list the sentinel
at all. A literal-minded lane then completed the contract exactly as written and omitted it. Twelve other lanes
emitted the sentinel, which is what makes this a prompt-shape fault rather than a model fault. **Status: hypothesis,
structurally addressed** — the delimiters and the restated contract close the gap the evidence points at; the causal
claim is not independently confirmed.

## Offline test

```bash
bash tools/review-posture/tests/run-tests.sh     # no network, no real model calls
```

That file exists and is the whole offline gate: `bash -n` over every shipped script, then
`tests/test-selfheal.sh`, then `tests/test_review_posture.py` under pytest when one is
installed (reported SKIPPED, never as a pass, when it is not). It runs from the repo root, from
any other working directory, and from a path containing a space. `bootstrap/lane-orchestrator.md`
§1b names the same command.

Fake `claude` / `codex` / `node` on a temp `PATH`, under a temp directory **whose name contains a space**. Covers the
placeholder-`node` shim repairing and verifying; no node anywhere failing loudly with the family unavailable *and a
cause*; `run.sh --dry-run` from a spaced path getting real model ids; an `ids` failure exiting 2 rather than
proceeding; the single sentinel retry with `attempt1` preserved; a near-miss sentinel rejected; and the arbiter prompt
carrying the sentinel after `END DATA` as its last contract item.

**What proves the codex placeholder-`node` repair.** It was measured live once on VIRTUAL-TEN by a lane
(rc 127 → codex-cli 0.154.0) before another session removed the stray npm node package (fleet doctrine bus
`9eeba29`); no receipt of that run exists; the fault is no longer reproducible on this host; the standing
proof is the hermetic fake-shim test `tests/test-selfheal.sh` case **A1**. Read "self-heal" here as
"covered by A1/A2", not as "verified against the live fault" — nothing in this repo can claim the latter.
The same rule holds for `tests/test_review_posture.py`: its fakes pin `HOME`, `APPDATA` and `CLI_NODE` into
the temp tree precisely so the repair ladder cannot reach a real, installed CLI and quietly turn a
hermetic test into a live one.

## Failures this exists to prevent (all measured 2026-09-13/14)

- **A role missing from a hand-written runner is invisible.** The sentinel proves the lanes that ran; nothing noticed
  the 12 that were never written, and the run was filed as `conjugal-standard`. → `posture` counts against `roles.json`.
- **A prompt bound to nothing still gets an answer.** Bash interpolation sent `…doctrine$SUBJECT`. → prompts are built
  in Python and every one is checked to contain the subject path before it is written.
- **The arbiter never saw lint.** → stage B's arbiter prompt carries all four stage-A outputs and requires losers.
- **A seat's own average is not the composite.** In the measured run every stated composite matched to rounding, but
  one seat had to correct its own arithmetic mid-answer; a composite is data the tool can compute, so it does.
- **A blocked stage looked like four successful lanes.** A stage that blocks `break`s out of the loop, so the
  clearing that lived inside `run_stage` never ran and a *previous* run's files were counted RAN. → every lane of
  every stage in the run's `--from` order is cleared **before** the loop; never-dispatched is DID-NOT-RUN.
- **A model id was `eval`ed.** `eval "$(… ids)"` executed inventory content; `opus: x$(touch PWNED)y` ran that
  command. → strict `[A-Za-z0-9._-]+` in the python emitter **and** the bash consumer, and no `eval` anywhere in the
  ids path.
- **A fallback CLI rung accepted an impostor.** Any rc-0 banner verified, so a stray `codex.exe` that was really GNU
  `echo` was adopted and the run then blamed the account. → a fallback rung must prove identity (the family's own
  package entrypoint, or the family naming itself in its `--version` output); see `tools/lib/cli-resolve.sh`.
- **Permissive parsing guesses.** A loose regex read "78.73 (current) + 1.5 = 80.23" as a ceiling of 78.73 and ran a
  must-fix list past a newline into prose. → strict `HEADING: value` only; everything else is listed as `unparsed`.
- **`bash` can be WSL.** `shutil.which("bash")` on Windows returned WSL's, which cannot see `C:/` paths. → `run.sh`
  refuses a WSL bash **under any of its three names** — `…/Windows/System32/bash.exe`, the Store app-execution alias
  `…/WindowsApps/bash.exe` (on PATH by default, and missed by a System32-only pattern), and `wsl.exe`/`wsl` itself;
  the test resolves Git Bash explicitly.
- **`--from` could manufacture a COMPLETE posture.** Reusing stages B–D trusted sentinels the run could not attribute
  to any subject: change the subject and `--from C` still printed COMPLETE over lanes that reviewed the previous
  document. → every dispatched stage writes `bindings.env` (subject path and blob, bench HEAD, subject-repo HEAD,
  rubric id and rubric source blob, the git blobs of `run.sh` and `review_posture.py`, and which stages actually
  dispatched); `--from` re-derives all of them and **refuses, naming each mismatch**, before generating or clearing
  anything. A missing `bindings.env` is also a refusal — "no record" is not "match". There is no override flag: an
  operator who has re-measured can run from A.
- **A HEAD is not a tree state.** The bindings above pinned each tree's HEAD, so a bench with uncommitted edits — or
  a new untracked file the lanes read — reused stages measured against different bytes and still printed COMPLETE
  (Codex sol review, round X6). → `bindings.env` and `environment.json` also carry **`bench_worktree` /
  `repo_worktree`**: a deterministic digest over `git diff HEAD` (working files) **and `git diff --cached HEAD`**
  (the index) for tracked files, plus every **untracked, non-ignored** path with its content hash.
  `--from` and `--retry-missing` refuse on any change, **naming the tree, its path, and that the difference is
  uncommitted** rather than a commit. An `RP_OUT` nested inside the tree is excluded, since the run writes there as
  it runs. A non-git directory digests to the constant `not-a-git-tree`, which binds nothing — and a reuse that
  meets one prints a `DISCLOSURE:` line saying so.
- **The digest fails CLOSED, and an unmeasured input is never a match** (round F). The first version enumerated with
  `git ls-files` (no `-z`), which **C-quotes** any path holding a newline, a quote or a non-ASCII byte, so such a
  file was bound by its *quoted spelling* — stable while its bytes changed; and it hashed inside a brace group whose
  status came only from the final `hash-object --stdin`, with `2>/dev/null` on the parts that could fail, so a failed
  enumeration still produced a well-formed digest over **partial** text. → `-z` enumeration, NUL records,
  length-prefixed `<len> <hash> <path>` lines, one hash per exact path, every command guarded: **any** failure makes
  the whole digest `unknown`. And `unknown` (or empty) on **either** side of `bench_worktree`, `repo_worktree`,
  `bench_head`, `repo_head` or any `*_blob` is a **refusal** — `MISMATCH … could not be computed` — never a match,
  because two "unknown"s comparing equal is precisely how a binding stops binding. Consequence accepted knowingly:
  an unreadable or dangling untracked path makes a tree undigestable and therefore un-reusable until it is dealt with.
- **Ignored content is DISCLOSED, not ENFORCED** — deliberately. A live bench rewrites ignored state continuously:
  MLV-App's OS heartbeat rewrites `.claude-state\heartbeat\board-snapshot.md` every ten minutes, ledgers grow, and
  `RP_OUT` itself usually lives under `.claude-state`. An enforced ignored-content binding would refuse nearly every
  legitimate reuse, and a control that is always wrong is one operators route around — the bypass would then also
  cover the bindings that *do* hold. (`--exclude-standard` is also what bounds the digest: 177,449 ignored paths,
  4.7 s, measured on the MLV-App bench.) → every accepted `--from` / `--retry-missing` prints, records in
  `environment.json` (`invocation.reuse_disclosure`), and **appends to the posture line itself**:
  `REUSE: stages <list> reused; ignored content NOT bound -- lanes may have cited it`. A reused posture must never
  read as a pristine one.

## Not covered (yet)

- **Model fallback ladders and token/cost telemetry** live in `tools/lane-dispatch.sh` (Claude lanes only). This tool
  gives each lane **one dispatch at the inventory's id, plus at most one sentinel-miss retry** (same prompt, same
  run; a later `--retry-missing` invocation is a separate, bindings-checked run, not a second retry inside this one;
  same
  model, attempt 1 preserved as `<lane>.attempt1.*`, the decision logged as `SENTINEL_MISSING`/`SENTINEL_RETRY`).
  There is no *model* fallback: a lane that still misses the sentinel is reported DID-NOT-RUN and the posture is
  PARTIAL.
- **Filing assembly** is the orchestrator's job (lane-orchestrator §3): quote verification, re-deriving numbers seats
  disagree on, and reading the arbiter's losers against the subject are judgement, not parsing.
