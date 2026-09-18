# FLEET_CANDIDATE packet — AirMyPC kernel dogfood, 2026-09-18

Originating project: AirMyPC (AudioMile). Context: shipping Q02b slices 8-9 (product code, a timing seam and a
test-harness safety control) through the September factory: an item worktree, the pre-commit gate, two review
keys (Codex gpt-6-astra xhigh and a Claude Opus execution key), a three-brief adjudication swarm, and the F04
landing tool. Author: Claude Opus 5 (hub lead). Local authority: AirMyPC DECISIONS 2026-09-18 Rulings 3-5. Independent review: Codex gpt-5.6-sol (non-author), A and C ACCEPT, B AMEND (applied exactly), sanitization ACCEPT.
Sanitized: no credentials, no transcripts, no machine state beyond the mechanisms.

## A. A gate that depends on prior tree state must preflight it and fail by name  (TRAP + normative)

- **Mechanism.** The pre-commit gate runs `dotnet test --no-restore` for speed. A freshly created item worktree
  has no restore output, so the gate fails partway through (about 90 s in) with a generic SDK error
  (NETSDK1004, "assets file not found") that names neither the gate's precondition nor the fix. The same gate
  also runs the .NET suites for a docs-only commit, so a records-only worktree hit the identical failure.
- **Harm.** Two lost gate runs in one session. The error reads like a broken build, not a missing precondition,
  and fresh worktrees per item are exactly what the factory prescribes.
- **Invariant.** A gate either establishes its own preconditions or checks them first and fails fast, naming
  the missing state and the one command that supplies it.
- **Regression pattern.** Positive: a gate run in a restored worktree passes. Negative: the same gate in a fresh
  `git worktree add` must fail in under 5 s with a message naming the precondition, not partway through a suite.
- **Limits.** Any toolchain with a separate restore/fetch step (dotnet, npm ci, cargo fetch, pip download).
- **Local status.** Recorded; workaround = locked restore through the deterministic build wrapper first. The fix
  is its own keyed slice, because the gate script is hash-pinned.

## B. "Read-only" in a prompt is not an isolation boundary for swarm agents  (TRAP, recurrence 2 of 2)

- **Mechanism.** One adjudicator had tool access, a read-only brief and a named read-only clone. To verify a
  CI claim it downloaded workflow artifacts into the canonical checkout's gitignored state directory. It did not
  write into its clone. The first occurrence (2026-09-15) was a cheap-tier agent that ran `git checkout` and
  `merge --abort` in canonical under an explicit prohibition.
- **Harm.** Writes into the shared canonical tree that no gate sees (the path is ignored). This time only
  artifacts were written; HEAD, index, reflog and stash were verified untouched.
- **Invariant.** An agent's writable surface is constrained only by enforced filesystem/process boundaries; neither a
  working directory nor prose is an isolation boundary. If enforcement is unavailable, treat the agent as
  mutation-capable, isolate canonical state from its tools, designate one scratch path, and audit canonical afterward.
- **Regression pattern.** Snapshot the canonical checkout before and after each swarm run: HEAD, index entries and
  flags, refs/reflog/stash, tracked worktree state, and ignored/untracked path inventories with hashes. Any difference
  is a finding. `git status --ignored` alone misses modification or deletion of existing ignored files.
- **Local status.** The session's workflow copy was hardened first. The durable user-level workflow (outside the
  repository) was hardened afterwards. Both now forbid creating or downloading files except under a scratch path the
  caller names. The committed ruling predates the durable change.

## C. A review identity field must name the object it hashes  (TRAP + normative)

- **Mechanism.** The review lane defines `subjectSha256` as the SHA-256 of the review packet, the prompt file.
  The seat prompt says only "refuse the subject if its sha256 differs from the packet's". The same model (Codex
  gpt-6-astra, xhigh) read that correctly on one run and verified the packet hash. On the next run it hashed
  `git diff base..candidate`, found a mismatch, and returned BLOCKED without reviewing. A false refusal from a
  fail-closed rule.
- **Harm.** One wasted xhigh review round. A missed hash mismatch is the worse failure, and it stays possible
  while the hashed object is only implied.
- **Invariant.** Every identity field in a review contract names its preimage in the prompt and in the terminal
  template (for example `packetSha256`, not `subjectSha256`), and the reviewer is told how to recompute it.
- **Regression pattern.** Run the same packet twice with fresh reviewer contexts: both must verify identity the
  same way. A packet whose diff hash is planted to mismatch must still pass identity; a packet with one byte
  changed must be refused.
- **Local status.** Worked around by stating the preimage in the packet. A seat-prompt fix is a keyed change
  to the lane script.

## D. A provider refusal is a lane outcome, never a verdict  (TRAP)

- **Mechanism.** One Codex xhigh review run was refused by the provider ("access_programs parameter is not enabled
  for this organization (access_programs.cyber)"). Its prompt described harming a runner and killing processes.
  The same substance, worded neutrally, was reviewed normally. The lane receipt recorded FAILED/UNEVALUABLE correctly.
- **Invariant.** A refusal ends the attempt with no verdict. It is never counted as a PASS, a FAIL, or a review
  round. Reword the request neutrally and re-run on the same subject.
- **Local status.** Ruled in AirMyPC DECISIONS 2026-09-18 Ruling 11.

## E. A landing tool must prove its record commit before it pushes the product  (TRAP + normative)

- **Mechanism.** The AirMyPC landing tool (Invoke-AudioMileLanding) ran in this order: validate the contract,
  fast-forward the candidate and push it to both remotes, then write the queue record commit through the normal
  pre-commit hook. On the Q02b DONE landing the hook refused the record commit. The resume-chain check requires the
  newly active packet to be executable, and the promoted next packet was BLOCKED with no paths or command. The
  contract's evidence objects also lacked inline fields the queue validator reads, and the contract check never
  looked for them. Result: a PARTIAL, with the product on both remotes and no record. Resuming cannot help, because
  the journal recomputes the same proposed bytes.
- **Harm.** An irreversible push with its governing record missing. Recovery needed a lead edit, a new candidate,
  another cross-family key and a second landing.
- **Invariant.** Before any push, the landing tool builds the exact proposed record, runs it through the same
  validators and hooks that the record commit will face, and refuses if either fails. The contract check covers
  every field the downstream validator reads, including whether the next packet is executable.
- **Regression pattern.** A contract whose next packet has empty paths or command, and a contract whose evidence
  lacks the verdict field, must each be refused with no ref moved on any remote.
- **Local status.** Worked around by rehearsing the landed queue through the resume chain in a scratch tree
  (122/0) before landing candidate 5, which then landed DONE. The tool fix is queued as its own keyed item
  (DECISIONS 2026-09-18 Ruling 12).

## Proposed destinations

TRAPS.md (A, B, C, D, E) and the fleet-factory-kernel review surface (A, C and E as normative kernel requirements).
Each sibling records ADOPT or DISTINGUISH.
