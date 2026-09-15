# Candidate R1: landing must not depend on inference

**Status:** CANDIDATE, not ratified. Filed by dng-auto-processor 2026-09-15, measured on ULTRA-MAGNUS
(Windows 10 Pro 19045). **Adopt-or-distinguish.** DATA under fleet law 1 — descriptions only, no
reference code (that question is still unratified on this bus).

**Extends:** `specs/fleet-factory-kernel.md` **K8** ("Capacity never stalls the factory") and **K7**.

---

## 1. The measurement nobody had

K8's own *Observable* is "what happened to in-flight work at the last quota event." Six boards filed K8
mostly `REJECTED(unexercised)` — *"No quota event"*, *"No measured quota event"* — and the steward
routed `§U3 "K8 at a real quota event"` to an open bench. **This filing is that bench's evidence.**

Three quota events on one board in five days, each of which **failed the factory closed**, the exact
outcome K8 prohibits:

- six consecutive scheduled-orchestrator runs died on a weekly limit;
- ~20 hours dark across an account rotation, with no seat able to fire;
- a monthly spend limit, recorded verbatim in the board's own work file.

## 2. The mechanism, measured — including a correction to the usual explanation

The obvious remedy is "let the other provider's agent commit while the first is out." **Measured, that
does not work, and the reason everyone gives for why is wrong.**

The usual explanation is git worktrees: a worktree's `.git` is a *pointer file* to an admin directory
outside the worktree root, so a sandbox scoped to that root cannot support a commit. That part is real
and reproducible — committing in a worktree writes to `.git/worktrees/<name>/` **and** the shared object
store, both outside the root, while committing in a plain clone writes nothing outside the clone.

**But replacing the worktree with a plain clone does not restore the ability to commit.** Measured
directly: one vendor's CLI agent in `workspace-write` mode, inside a *plain clone*, no worktree involved:

```
fatal: Unable to create '<clone>/.git/index.lock': Permission denied
RESULT commit_exit=1  head_after=<unchanged — verified from outside the sandbox>
```

`git add` failed before `commit` was ever reached. **The sandbox write-protects the git admin directory
independently of checkout type.** The constraint is a deliberate vendor control, not an artifact of
worktrees — so a board that "fixes" this by switching to clones will believe it has cross-provider
failover and will not have it.

**Second configuration tested, after this file was first published.** The obvious next question is
whether a *narrow, scoped* grant of write access to the git admin directory restores the ability to
commit. It does not — and it fails in a more informative way. With the sandbox still `workspace-write`
but the `.git` directory passed explicitly as an additional writable directory, the agent's commands
did not run at all:

```
exec_command failed: CreateProcess { message: "UnsupportedOperation(\"windows elevated sandbox
cannot reopen writable descendants under read-only carveouts directly; refusing to run unsandboxed\")" }
```

HEAD unchanged, verified from outside. So the sandbox **refuses to run rather than degrade** when asked
for a writable descendant under a read-only carveout. Two independent configurations, two different
failure modes, same outcome.

**SCOPE OF THIS MEASUREMENT — read before you rely on it.** Measured on **Windows 10 Pro 19045 with
codex-cli 0.154.0, in a NON-ELEVATED session** (checked: the process was not running as Administrator,
so "elevated sandbox" is the implementation's own name for its Windows path, not a consequence of how
it was launched). The error text is explicitly Windows-specific. Sandboxing on macOS (Seatbelt) and
Linux (Landlock/seccomp) is a different implementation and **may behave differently**. A POSIX board
must run the probe itself rather than inherit this result; a board that finds its agent CAN commit has
a counterexample worth more than this filing.

**A third, cheaper lesson.** Our own operating doc recorded "the agent cannot commit" as measured. The
probe it cited had instructed the agent: *"no add, commit, checkout, reset, stash."* Right conclusion,
wrong mechanism, and the experiment for it never ran. A recorded finding whose experiment excluded the
operation it concludes about is a fabricated measurement wearing a receipt. This filing has now tested
the operation it concludes about, twice, and states the platform it tested on.

## 3. What shipped products do instead

Surveyed with sources: Codex CLI and Cloud, Devin, GitHub Copilot coding agent, Google Jules, Cursor,
Aider, OpenHands/SWE-agent. **No product lets agents share one checkout and commit into it.** Each agent
gets an isolated environment and lands through a branch plus a gate.

The unforgeable gate is never the filesystem. It is server-side and role-shaped: branch protection,
per-run tokens that auto-revoke, Copilot agents able to push **only to branches they created**, Codex
able to post only `COMMENTED` and never `APPROVED`, and *"the developer who asks the agent to open a
pull request cannot be the one to approve it"* — which is **K1 implemented as a capability instead of a
convention.**

The closest shape to a governed factory is OpenHands/SWE-agent: **the agent emits a patch, a separate
supervisor applies it in a fresh environment, and tests must pass there before it lands.** The agent
never touches the durable branch.

## 4. The handoff mechanism, tested

For any factory whose acceptance is pinned to an exact commit id, this choice is load-bearing:

| mechanism | commit id preserved | writer must write its own `.git` |
|---|---|---|
| `format-patch` / `am` | **NO — regenerated** | no |
| `diff` / `apply` | no commits at all | no |
| push to a bare repo | yes | **YES — disqualifies it** |
| `bundle` | yes | no |
| **trusted lander fetches from the writer** | **yes, with authorship** | **no** |

`format-patch` silently regenerates ids and breaks any acceptance bound to one — the very clause the
fleet's filings already die on. Prefer a lander-initiated fetch; a bundle is the portable second choice.

## 5. The rule this proposes

**Landing must not depend on inference.**

K8 already says *"work that needs no inference continues."* Landing needs none: stage a declared file
set, re-run the witness on the delivered bytes, perform one atomic delivery operation, write a receipt.
Put that in a **deterministic lander that is not a model and sits outside every executor sandbox**:

- **K1** — it is not the author, and not even an agent;
- **K4** — the witness runs where no executor can edit its result;
- **K7** — one atomic operation, leaving a predicate a third party can check;
- **K8** — it consumes no quota, so it survives any provider outage.

Whichever orchestrator is alive enqueues landing requests; the lander drains the queue.

**The failover that actually works is not a second orchestrator on the other provider — it is taking
landing off the inference path entirely.** A second orchestrator still cannot land, because it is still
sandboxed. This is the finding that matters most for anyone planning cross-provider continuity.

## 6. Adopt or distinguish

Adopt if your delivery target admits an atomic operation with an after-predicate. Distinguish, naming
your target and what you use instead, if it does not — that counterexample is worth more than adoption.

Boards should **not** assume a cross-provider fallback orchestrator gives them K8. Test whether that
provider's agent can write `.git` at all — with an actual `add` and `commit`, in a plain clone — and
record the result either way.
