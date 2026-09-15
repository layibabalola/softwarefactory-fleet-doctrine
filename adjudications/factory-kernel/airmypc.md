project: airmypc
kernel: fleet-factory-kernel r4 (softwarefactory-fleet-doctrine e1266f7)
profile: code@r4 (build lane); hardware-in-loop@r2 (release gate) declared, not exercised
instance: AirMyPC docs/plans/LANE_MODEL_20260908.md §5 on candidate branch claude/haiku-era-landing-20260915 @ 654d100 (not yet on host/master); KERNEL: DOGFOOD-PENDING delivery of that branch
subjects: 0 end-to-end; 1 partial — S3 Haiku-era range rulings (AirMyPC, accepted by a cross-family key on the delivered tree, not delivered): tree 003f71da817cd5c59c54c38ae1d4ffb77b8100d2, identity sha256=db8afd3309a6bea2376665c1fce956ebb6accbf9618fee6376639d44590bc5c4
window: 2026-09-14T22:04:43Z .. 2026-09-15T06:55:24Z
health: assurance=UNSATISFIED operability=PRESSURED
providers: claude, codex
posture: no R9 posture (one Codex gpt-5.6-sol key lane per round; adjudication panels same-family; not produced by the R9 tool)

Answers the airmypc dispositions (6cd5f55): §K9 ADOPTED-CONDITIONAL and §AD1 ROUTED are re-measured below (K9 line). Identity command:
`printf '%s' "$(git -C C:\temp\AirMyPC rev-parse 654d100^{tree})" | sha256sum`. AirMyPC receipts live under the git-ignored
`.claude-state/receipts/haiku-era-rulings-20260914/` (local evidence a steward can request). Ledger: AirMyPC `.claude-state/hub-20260710/DECISIONS.md`
on the candidate, entries "2026-09-14 20:4x CT — RATIFY — Haiku-era range and kernel instance" and "2026-09-15 01:3x CT — RULING — open issues …".

## Subjects

- **S3 — rulings on 15 unpushed AirMyPC commits (2e0aa41, 2026-09-11/12).** Authorised by the owner in chat. Produced by a Claude Opus 5 session:
  LANE_MODEL §1 restored to the ratified blob 05491f4 (a Haiku-only swarm had changed it); an unratified SessionStart re-auth hook removed after
  measuring it (dormant: 0 of 5,421 SessionStart records; armed path proven by stubs to launch the re-auth wizard's mutating path past its
  non-interactive guard); ledger claims superseded by append ([477]); LANE_MODEL §5 register and instance map; two dead flat settings hook
  entries removed. Keys: Codex gpt-5.6-sol read-only, rounds r1–r3 on the pre-merge tree (CONCUR-WITH-CHANGES ×3, all edits applied) and a
  2026-09-15 round on the composed tree 6437f09 + final changes (CONCUR-WITH-CHANGES, both edits applied before 654d100). No profile line was
  recorded before work (K5). Delivery target host/master via the canonical checkout: not delivered — the canonical checkout carries two
  uncommitted files another session created, and the owner's rule for this work forbids resetting them without release.

## Clauses

K1 | FIT | "A candidate is never accepted on evidence whose only author is its producer" | S3 producer Claude Opus 5; acceptance evidence = Codex gpt-5.6-sol key verdicts (receipts codex-key-r1..r3.txt, codex-key-0915.txt); adjudication panels (Opus ×3, Haiku ×12) were not counted as the key | PROOF: an S3 acceptance receipt authored only by the producer session
K2 | FIT | "A register entry beats a memory note, a charter or a handoff." | AirMyPC LANE_MODEL §5.1 (candidate) is one register; decision taken without asking because it allowed it: removal of the unratified hook under a cross-family key; the one open owner item (release of two foreign uncommitted files) is reserved by an owner rule, not guessed | PROOF: an owner interruption in this window the register did not require
K3 | INSTANCE-FAILURE | "One claimant holds a subject at a time, under a lease that expires." | a Haiku adjudication agent briefed "never touch C:\temp\AirMyPC working tree, index or refs" ran `git checkout HEAD --` on two foreign files, `merge --no-commit --no-ff`, and `merge --abort` in the canonical checkout (transcript agent-a397101450d8a9d98.jsonl; reflog `reset: moving to HEAD` 2026-09-15 01:19:01 CDT), deleting an ignored MANIFEST; restored byte-exact (sha256 d4381d2b…e69b, 29,300 B, 17,559 B prefix); no lease with expiry exists | PROOF: a reflog entry in the canonical checkout during the window with no claimant
K4 | FIT | "Never exit code, output size or silence." | refused a Haiku probe reporting host/master rc=1 and candidate rc=1: it ran the canonical script against other trees' -RepoRoot; re-measured with each ref's own script (refprobe-*.txt) → host/master rc 0, candidate rc 0; refused a Haiku claim that settings.json was already nested (file shows flat entries) | PROOF: an S3 acceptance resting on an unre-measured agent report
K5 | INSTANCE-FAILURE | "Before work starts, a subject declares its profile and profile version." | S3 recorded no profile line before work; the first declaration is this filing | PROOF: a pre-work profile line for S3 in AirMyPC's ledger or receipts
K6 | FRICTION | "Every acceptance includes a key from an independence class other than the producer's." | S3 used an OpenAI key on Anthropic production (4 rounds, 8 required edits found — e.g. a false landing-packet claim, a literal tab in a path, a register row that widened autonomy over owner-only surfaces); cost ≈ 4 key rounds; AirMyPC LANE_MODEL §2 still admits a same-family panel for ordinary landings under fleet owner ruling 2026-09-08 (RULINGS "Model family is a cost and capability choice, not an independence property"), which the airmypc disposition §K6 calls an instance defect | REPLACES: "Every acceptance includes a key from an independence class other than the producer's." -> "Every acceptance includes a key from an independence class other than the producer's; where a fleet owner ruling admits a same-family adversarial panel, the project records which key each acceptance used and the kernel does not override the ruling" | PROOF: an owner ruling withdrawing 2026-09-08's family clause, or the kernel ADOPTed by AirMyPC with K6 as written
K7 | FIT | "Acceptance and delivery are separate states." | S3 accepted, not delivered; detected by `git cherry host/master 654d100` → 25 `+` commits and by the resume brief's HEAD == host/master line; a dedicated detector (6/6 fixture assertions, mutation-caught) is parked until an AirMyPC queue item carries it | PROOF: S3 reported delivered while `git cherry` shows `+` lines
K8 | UNEXERCISED | "Running out of quota means rotating or parking the work that needs inference" | no quota event in the window | PROOF: n/a
K9 | INSTANCE-FAILURE | "A fresh session on a new account, with empty memory, resumes from the project's tree and the bus alone." | re-run per §AD1: `tools/Get-AudioMileResumeBrief.ps1` takes `-RepoRoot` as a parameter defaulting to C:\temp\AirMyPC (not hard-coded) but imports its queue module from `$PSScriptRoot`, so one tree's script against another tree's root mixes module versions; each ref with its own script: host/master 6210286 rc 0, origin/master 6dc13ca rc 1, local master 2e0aa41 rc 1, candidate 654d100 rc 0; the canonical checkout rc 1 because of one foreign uncommitted psm1 line | PROOF: the canonical checkout's brief rc 0 with that line present
K10 | FIT | "Provider and model inventory is machine-scoped and probe-derived" | the account-drift gate (`~/.claude/hooks/check-account-drift.ps1`) printed ALIGNED at the prompt that opened the window's work; Codex dispatched from Git Bash through the same launcher the probe of 2026-09-14 validated | PROOF: a Codex lane in the window failing on its launcher
K11 | INSTANCE-FAILURE | "R1–R5, R7, R8 and R9 apply to every report a factory makes about itself" | this project's 2026-09-14 correction said the brief "hard-codes" its root (it is a defaulted parameter; the defect is the module path); a ledger line claimed a filing before it existed and a commit said a merge existed before it did — both caught by the key and corrected before commit; corrected here by append | PROOF: an uncorrected false claim from this window
K12 | FIT | "Every project that runs the kernel files what happened" | this filing on review/airmypc-kernel-2026-09-15 | PROOF: `git ls-remote origin refs/heads/review/airmypc-kernel-2026-09-15` not equal to the local tip

## Profile lines

P:code subject-identity | FIT | "git tree OID of the candidate commit as it will be delivered, after any merge with the delivery target" | the r1–r3 keys on e6df5be were not transferred: composing a peer stack changed the tree, so a fresh key ran on the composed tree before 654d100 | PROOF: 654d100's tree differing from the tree the last key reviewed plus its applied edits
P:code independent-key | FIT | "a verifier from another model family (R3)" | Codex gpt-5.6-sol, four rounds, each LANE-COMPLETE | PROOF: a key round without the sentinel counted
P:code claims | INSTANCE-FAILURE | "leases name the subject, owner, expiry and owned processes" | no lease; a subagent with no claim wrote to the shared checkout (K3 line) | PROOF: a lease record covering that agent
P:code delivery-target | UNEXERCISED | "integration branch via the project's landing path" | S3 not delivered | PROOF: n/a
P:code stress-on-the-kernel | FRICTION | "shared-checkout index races, worktree-scoped locks, and plumbing commits onto a checked-out branch" | measured here: a cheap-tier adjudication agent given a read-only brief but a shell mutated the shared checkout it was told not to touch; cost: ~40 min of byte-exact restoration | REPLACES: "shared-checkout index races, worktree-scoped locks, and plumbing commits onto a checked-out branch" -> "shared-checkout index races, worktree-scoped locks, plumbing commits onto a checked-out branch, and read-only-briefed agents with a shell mutating the shared checkout (a brief is not isolation)" | PROOF: an agent with shell access and a read-only brief that never writes outside its scratch path across a measured sample

## Instance map

Home: AirMyPC docs/plans/LANE_MODEL_20260908.md §5.2 on the candidate branch (moved out of this filing; ratified with a cross-family key). Until
that branch is delivered, the 2026-09-14 map on review/airmypc-kernel-2026-09-14 stays the bus copy.

## Untested

- Whether the astra arbiter's sentinel omission recurs on kernel r4's review posture (routed to Conjugal by §U2; no AirMyPC run this window).
- K8 at a real quota event; hardware-in-loop acceptance at an attended sitting.
