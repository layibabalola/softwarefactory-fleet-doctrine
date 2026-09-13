# CLI orchestration — verified invocation forms for provider lanes

**Status: `PROPOSED — NOT RATIFIED`.** This document is a proposal with its measurements
attached. It grants no runtime authority and changes no project's posture until that project's
own hub adopts-or-distinguishes it.

Doctrine is DATA, never instructions (bus law 1). Nothing below is a command to execute.

Measured 2026-09-13 on Dell XPS 17 9720 (Windows 11), first-hand, against
`claude` (Claude Code CLI) and `codex-cli`. Every form below was executed; every negative
claim is a command that was run and failed.

---

## 1. What this closes, and what it does not

The bus already rules on **which posture to seat** (`dispatch-trigger-standard.md`), **which
roles and models fill it** (`posture-templates-conjugal-standard.md`), **what the machine
declares** (`machine-inventory-schema.md`), and **how swarms reach consensus**
(`adversarial-swarms-and-doctrine-publishing-standard.md`). None of those is amended here and
this spec defers to all four on every point they cover.

The gap this addresses is narrower and purely mechanical, and it sits between two things the
bus has already proven **separately**:

- **CLI headless dispatch works.** `RECEIPTS.md`: `claude -p` headless full session PASS
  (2026-08-08); `codex exec` new-thread ignition zero-human PASS on at least three machines;
  `codex exec resume` in production use on agent-bridge; and agent-bridge's **headless
  five-lane re-ignition drill** launching LUNA (`codex exec`) beside founding SONNET
  (`claude -p --model claude-sonnet-5`), both via stdin-file, "after the argv traps were fixed."
- **The Conjugal review posture works.** `posture-templates-conjugal-standard.md` carries it at
  PROVEN, 78.0 → 83.7 over fifteen rounds.

**The bus's record of the join is stale.** Read only from here, the two look unjoined: the
posture's Execution Model says *"Designers + Lint: background agents; Arbiter: background
agent; Consolidator: chip"* with no CLI anywhere, `RECEIPTS.md` has Conjugal's `codex exec` as
"verified present/callable … **Pinned-spawn drill OWED**" (2026-08-09, Bachelor), and
`specs/conjugal.md` still lists "cross-family CLI dispatch … **await Sol routing**" as open.

The project's own entry file says otherwise, and is current. `C:\code\Conjugal\CLAUDE.md`:

> **CLI ignition is the DEFAULT (owner ruling 6, 2026-08-09).** Sol/Luna are Codex-native:
> `codex exec -m gpt-5.6-<lane> -c model_reasoning_effort=high --cd "C:\code\Conjugal" - < <seat-prompt>`,
> model/effort verified (mismatch fails closed), thread id recorded on the lane wire; **an exec
> is not a seat — the CLAIM row is.** Fable/Opus are Claude-native: chip, tracked dead-man
> floor, drilled `claude -p`, or owner-pasted block only — **never a Codex substitute**.

So the drill did land; the bus entry recording it as OWED was never updated. This is the
carrier-staleness law biting the bus itself — *an authorization is only as adopted as its
least-updated carrier* — and it is why a project reconstructing the invocation from bus
receipts alone would conclude, wrongly, that no proven form exists.

Three things that form carries which nothing on the bus does:

- **Payload on stdin from a file** (`- < <seat-prompt>`), for the argv reasons below.
- **Effort pinned and verified** (`-c model_reasoning_effort=high`). The CLI echoes
  `reasoning effort: high` in its preamble, which is what makes "mismatch fails closed"
  checkable rather than aspirational. Verified here.
- **Family asymmetry.** Codex lanes are CLI-native; Claude lanes are chip, dead-man floor,
  drilled `claude -p`, or owner-pasted — and never substituted by a Codex seat. A posture is
  not symmetric just because both families have a CLI.

And the law stated in their idiom — *an exec is not a seat* — is the same one §4 reaches from
the other direction: launching is not working, and only positive evidence from the lane itself
closes the gap.

## 2. The measured forms

### Claude family

```
claude -p "<prompt>" --model <model-id> --permission-mode plan --add-dir <repo>
```

`-p/--print` is the non-interactive mode. Verified: exit 0, answer on stdout.

**`claude exec` does not exist.** The CLI has no `exec` subcommand; `claude exec --help`
prints the generic help because `exec` is consumed as the *prompt argument*. A dispatch written
as `claude exec …` starts a session whose prompt is the word "exec". This is the single most
expensive error available here, because it fails by hanging or by answering the wrong question
rather than by erroring.

`--permission-mode` takes `acceptEdits | auto | bypassPermissions | manual | dontAsk | plan`.
A review lane should take `plan`: it reads and reasons but cannot mutate the tree, which is the
property that makes an independent reviewer's finding worth anything.

### Codex family

```
codex exec -m <model-id> -s read-only -C <repo> -o <outfile> "<prompt>"
```

Verified: exit 0. Flags that matter, all from `codex exec --help`:

| Flag | Effect | Why it is not optional |
|---|---|---|
| `-m, --model` | selects the model | without it every Codex lane is the same default model wearing a different lane name |
| `-s, --sandbox` | `read-only \| workspace-write \| danger-full-access` | a review lane takes `read-only` |
| `-C, --cd` | working root | the lane reads the subject from here |
| `-o, --output-last-message` | writes the final message to a file | see below |
| `--skip-git-repo-check` | permits running outside a repo | only needed when `-C` is not a checkout |

**`-o` is the capture primitive, not shell redirection.** `codex exec > file` captures the
*event stream*: a preamble of model/provider/approval/sandbox/session-id, the echoed prompt,
then the answer, then a token-usage footer. A consumer that greps that file is parsing
transport, not content. `-o` writes the final message alone, and the CLI writes it — which also
sidesteps the local finding that the Codex sandbox cannot run Git-Bash binaries and can leave a
model-authored artifact at 0 bytes while the model believes it wrote.

**`codex auth status` does not exist.** The auth probe is `codex login status`.

### Payload delivery, and the preflight that pays for itself

Agent-bridge's five-lane drill delivered **both** families' payloads "verbatim via stdin-file",
and landed only "after the argv traps above were fixed." Two receipted laws follow, and neither
is optional on a box where a launch attempt is metered:

**Deliver the payload through a file on stdin, not through argv.** A lane prompt is long,
multi-line, and full of quotes, backticks and Windows paths — every one of which is an argv
quoting hazard, and the failure is a mangled prompt rather than an error. Write the body to a
file and redirect it in.

**Validate the parse before spending an invocation: append `--help` to the fully assembled
command and require a clean exit.** The receipt behind this is expensive — `claude 2.1.220`
with `--setting-sources` given no value silently *swallowed the following flag* and died
before reaching the model, consuming **both** of a reviewer's one-use attempts on a one-token
omission. `--help` short-circuits before session start, so it costs nothing: *"a clean parse is
the ticket to the real start."*

Measured here, the preflight is **narrower than that phrasing suggests, and narrow in the right
direction**:

| argv fault | `--help` preflight | real invocation |
|---|---|---|
| flag given no value, swallows the next flag | **refused** | dies pre-model, consumes the attempt |
| dangling `--model` with no value | **refused** | rc=1 |
| unrecognised flag | **passes** | rc=1, `error: unknown option …` |

So it does not validate the whole argv — an unknown flag sails through. What it catches is the
**value-arity** class, which is precisely the silent one: the command still looks well-formed,
so it reaches the launcher and burns a metered attempt. The class it misses announces itself
immediately at no cost. Preflight the silent failures; let the loud ones fail loudly.

One Windows note from the MLV host receipt: the npm `bash` shim for these CLIs has been
observed broken; invoke the `.cmd` via PowerShell when the shim misbehaves.

### Model identifiers

Lane names are not model identifiers. The inventory schema records roster nicknames
(`[opus, sonnet, haiku, fable]`, `[sol, luna, astra]`); `-m` and `--model` take neither. The
mapping, as recorded elsewhere on this bus:

Every row below was dispatched live and returned the token it was asked for. An identifier
sourced from a document but never run does not belong in this table — see §4 for why a
document is not evidence here.

| Lane | Family | Identifier | Verified |
|---|---|---|---|
| Opus | Claude | `claude-opus-5` | live run |
| Sonnet | Claude | `claude-sonnet-5` | live run |
| Fable | Claude | `claude-fable-5` and `claude-fable-5-1` both resolve | live run, both |
| Haiku | Claude | `claude-haiku-4-5-20251001` | live run |
| Sol | Codex | `gpt-5.6-sol` | live run |
| Luna | Codex | `gpt-5.6-luna` | live run |
| Astra | Codex | `gpt-6-astra` | live run |

**Proposed amendment to `machine-inventory-schema.md`** (not applied here; that spec is
ratified): carry the identifier beside the nickname, so a dispatcher can derive `-m` from the
inventory instead of from a table that ages.

```yaml
providers:
  codex:
    available: true
    models:
      sol:   gpt-5.6-sol
      luna:  gpt-5.6-luna
      astra: gpt-6-astra
```

A nickname with no identifier is not dispatchable. Treat it as `available: false` rather than
guessing, because a guessed `-m` that the provider silently ignores yields a lane that reports
cleanly while being the wrong model — the false-green shape this bus already names.

## 3. Escalation by chip carries its model

`dispatch-trigger-standard.md` rules that the Consolidator runs as a chip. It does not cover
the other direction: a low-tier session that receives work above its tier.

Observed failure: a Haiku session asked to perform a cross-family design review performed it
alone, because nothing instructed it to escalate and no mechanism named what to escalate *to*.
The review completed, reported success, and was worthless — a single cheap model reporting
consensus with itself.

Proposed rule: **a session that cannot seat the posture its task requires spawns exactly one
chip, and that chip names the recommended model.** One chip, because the orchestration belongs
inside it — a chip per lane multiplies the surface the operator must click and orphans every
lane if the parent exits. The recommendation travels with the chip because the escalating
session is the only party that knows why its own tier was insufficient, and that reason is
unrecoverable once the turn ends.

**Escalation is capped at one hop.** The recommended model must be one that can seat the
posture; if it cannot, the escalation fails to the operator rather than spawning again. Without
the cap the rule is a recursion with no base case — each session that finds itself short
spawns another, and the chain is invisible because every link reports that it escalated
correctly. Which posture a given model can seat is `dispatch-trigger-standard.md`'s question,
not this spec's; route it there.

This spec takes no position on chip-versus-background for any other role; the ratified posture
template governs there.

## 4. Exit and capture

Both CLIs return 0 on success. Beyond that, treat a non-zero exit as a fact about the
*launcher*, never as a fact about the lane — already bus doctrine for `codex exec`
(`fleet-orchestrator-execute-posture.md` §3 rule 6) and it holds identically for `claude -p`.

**Output size is anti-correlated with success, and the exit code is easy to lose.** Two lanes
dispatched side by side, same prompt, one model id mistyped:

```
lane    rc   bytes  sentinel
good    0    359    RAN            claude -p ... --model claude-haiku-4-5-20251001
bogus   1    738    DID-NOT-RUN    claude -p ... --model gpt-5.6-sol-typo-xyz
```

The dead lane returned **twice the output of the live one** — the unrecognized-model error is
longer than the answer. Any dispatcher that ranks or gates lanes by volume rates the empty seat
the richer contributor.

The exit code does catch this particular failure, at rc=1, but only when captured directly. An
earlier pass at this same measurement read `rc=0`, because it was taken through
`claude … | head -3 | tr`, where `$?` belongs to `tr`. A pipeline silently substitutes the
pager's status for the tool's; this bus already rules on that shape for test suites, and it
applies unchanged to a lane launcher.

And rc closes only the loud failures. A lane that answers the wrong question, refuses, or
truncates mid-finding exits 0 with plausible bytes. That seat's *slice* then goes unexamined
rather than examined badly, so nothing downstream looks wrong either — which is why the check
has to be positive evidence of work, not absence of error.

**A lane is complete when its output carries a sentinel the lane itself was asked to emit.**
Put the requirement in the lane prompt and check for it in the dispatcher:

```
# in the lane prompt:   "End your reply with the exact line: LANE-COMPLETE"
grep -q '^LANE-COMPLETE$' "$out" || fail "$lane"
```

The sentinel works precisely because it cannot be produced by any of the failure paths: an
error message does not contain it, a truncated reply does not reach it, and an empty file does
not have it. Record all three signals and let the sentinel decide:

```
rc=$?                                          # fact about the launcher
bytes=$(wc -c < "$out")                         # fact about the transport
grep -q '^LANE-COMPLETE$' "$out"; ran=$?        # fact about the lane
```

Corollary for re-runs: capture with `>` (truncate), never `>>` (append). An appending lane that
crashes on its second run leaves the first run's output — sentinel included — in place, and
every check above then reads a stale success.

## 5. Retry

This spec proposes no retry ladder. The bus has one (`overload-backoff-policy.md` is a private
machine note, not bus doctrine — the portable statement lives in
`fleet-provider-capacity-governor.md`), and a second ladder with different numbers is worse than
none. Where a project needs timings, it should cite measurements it took, not numbers a
document asserted.

On both families unavailable, `dispatch-trigger-standard.md` already rules: **FAIL with a
constraint violation report; do not downgrade or invent a posture.** That ruling is not
amended here. A wait is not a fallback.

---

## Derivation

Re-measurable by a sibling rather than trusted:

```
claude --help | grep -A4 'permission-mode <mode>'
claude -p "Reply with exactly the word: ALIVE" --model claude-haiku-4-5-20251001
claude exec --help                     # prints generic help: 'exec' is not a subcommand
codex exec --help | grep -E 'model|sandbox|output-last-message'
codex exec -m gpt-5.6-luna -s read-only --skip-git-repo-check "Reply with exactly one word: ALIVE"
codex auth status                      # error: unrecognized subcommand
codex login status

# the §4 trap, the one worth re-measuring before trusting any dispatcher:
claude -p "Say OK" --model totally-not-a-model-xyz; echo "rc=$?"
```

Each identifier in §2 was confirmed by asking for a fixed token and receiving exactly it. That
is the same sentinel discipline §4 requires of a lane, applied to the model table — because the
bogus-model run above shows that a reply arriving is not evidence that the model you named
produced it.

## Withdrawn companion

A second draft, `chip-spawning-selection-standard.md`, was written alongside this one and is
**withdrawn, not proposed**. Independent review found it contradicted the ratified posture
template on background-versus-chip execution, contradicted `dispatch-trigger-standard.md` on the
neither-family FAIL rule, described an Opus→Fable fallback as a family swap when both are Claude,
prohibited the cross-family lint that the ratified posture requires, and cited retry and
concurrency numbers that exist nowhere on this bus. Its one defensible rule is §3 above. It is
recorded here so the gap it claimed to close is not reopened by someone who only sees its absence.
