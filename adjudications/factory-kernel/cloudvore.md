# Factory-kernel dogfood filing — cloudvore (DropBox Vault, Dell XPS 17)

project: cloudvore
kernel: fleet-factory-kernel r1
profile: code@r1
instance: docs/operating-contract.md (Cloudvore); map reproduced below under ## Instance map because the contract is at its size cap
subjects: 3 — S1 cloudvore 100d4d4 tree 1c354829402c525feb974bcca58b7620186af303 (resume-regime retirement, 429ce86→767be3f→100d4d4); S2 bus ff36092 tree c1440c73ece06424ea6c9198c7d0f72a14e63794 (Cloudvore receipt corrections d772f3b→cf74c20→ff36092); S3 parallel kernel draft, blob of its candidate file given in ## Subjects (not delivered)
window: 2026-09-14T13:58Z .. 2026-09-14T23:00Z
health: assurance=UNSATISFIED operability=PRESSURED
providers: claude(opus,haiku) codex(sol) — ad hoc `codex exec -o` result files and Agent results; no LANE-COMPLETE sentinels
posture: no R9 posture run (ad hoc seats listed in ## Subjects; not a named posture)

**Status.** `KERNEL: DOGFOOD` is recorded in `specs/cloudvore.md` on this branch. This filing is operational evidence
measured by a Cloudvore Opus 5 session. It is not a review (R1). PROMPT A was not run in this session. Account parity
came from the SessionStart hook (`[parity] MATCHED`, fp `b4d2646b85c1`), and `tools/gate.py --doctrine-check` reported
`doctrine=pending` at entry and `unavailable` later.

**Why S3 exists (read first).** From the same owner sentence that produced r1, this session built a parallel kernel
draft, `universal-factory-kernel-r1`, and ran four review seats on it. It found r1 on master only at its pre-landing
fetch. The kernel commit a0d8d4c (15:49:38 local) landed after this session's research and drafting were done (the
draft's first Codex review started 15:47:09 local), so the TRAPS 2026-09-14 test ("repeat before landing") caught it,
and the draft did not land. The draft's evidence and
proposals are in `## Untested` and in `adjudications/factory-kernel/cloudvore-draft-2026-09-14/`. That subdirectory is
not a filing: `harvest-status.py` reads blobs only, not subdirectories.

## Subjects

- **S1**, owner-authorised: "check every file those two commits added … against the contract".
  - Produced by Opus 5. Delivered to Cloudvore master at 100d4d4; `gate.py` `landed=ok`.
  - Reviewers after landing: Claude Haiku ×2 (same family); later Codex gpt-5.6-sol, thread `01a0a0aa`.
- **S2**, owner-authorised: "Does anything need to be pushed to doctrine repo" and "run the codex cross-family review".
  - Delivered to bus master at d772f3b, cf74c20 and ff36092.
- **S3**, owner-authorised: "Execute recommended and submit to doctrine repo".
  - Candidate files at local bus commit 181116a (never pushed to master), later revised.
  - Identity (final draft candidate file): git blob `3628082d4fa73cf6e14d6f81376d09ba73fd3f6f`, at
    `adjudications/factory-kernel/cloudvore-draft-2026-09-14/universal-factory-kernel-r1.md` on this branch.
  - Reviewers: Haiku ×2 (design attack, fact attack); Codex gpt-5.6-sol ×2 (threads `01a0a1ac`, `01a0a1c7`; the second voted NO).
  - Not delivered: superseded by r1 under the owner ruling recorded in bus 2bed997.

## Clauses

K1 | FIT | "A candidate is never accepted on evidence whose only author is its producer" | Counter-evidence that the clause is right: Cloudvore's contract lets doc-only packets be "decided alone with the reason recorded" (`docs/operating-contract.md` §Deciding what is next). S1's 429ce86 landed that way, with only the producer's evidence. Two false claims then reached master and the bus, and only later non-author seats found them: proof row 1 cited `--desktop-email`, a flag Cloudvore's `tools/check-cli-auth.py` has never had on any ref, and "no lane chips" is not contract text. Both were corrected in 767be3f and bus cf74c20 | PROOF: a Cloudvore doc-only packet accepted by its producer alone that later non-author review finds free of false claims, repeatedly

K2 | FIT | "Each project keeps one register of what needs the owner and what does not" | Cloudvore `knowledge/owner-gated-decisions.md`. Taken without asking because the register allows it: "PUSHING is not gated" (row push-and-tag) → S1 and S2 pushed with no owner interruption. The owner was asked nothing in this window | PROOF: a Cloudvore push in this window that waited on an owner answer

K3 | FIT | "A subject's identity is a content digest over its declared artifact set" | S1: `git -C "C:\code\DropBox Vault" rev-parse 100d4d4^{tree}` → `1c354829402c525feb974bcca58b7620186af303`. S2: `git -C C:\code\softwarefactory-fleet-doctrine log -1 --format=%T ff36092` → `c1440c73ece06424ea6c9198c7d0f72a14e63794` | PROOF: either command returning a different OID

K4 | FIT | "Never exit code, output size or silence" | Negative checks refused in this window. (1) A mutation test of the S3 tool passed (exit 0) while its guard was disabled; the pin's filings named revision r1 under an r2 candidate, so the guard never ran. The green was refused and the pin corrected. (2) Codex returned exit 0 while its sandbox could not create a temp dir, so all tests errored; that was read as UNEVALUABLE, not pass. (3) A Haiku reviewer reported the growth counts "FALSE"; it had counted non-blank lines, and `len(splitlines())` reproduced the original 8,995 | PROOF: a Cloudvore acceptance in this window that rests on an exit code alone

K5 | FRICTION | "Before work starts, a subject declares its profile and profile version" | No subject declared a profile before work. The kernel did not exist when S1 started (a0d8d4c is later), and Cloudvore's queue (`BACKLOG.md`) has no profile column. Cost: 0 here, but no Cloudvore row can satisfy K5 retroactively. Separately, `code@r1` acceptance ("N identical green runs") has nothing to run on doc-only subjects (S1, S2), and Cloudvore's contract says "Documentation changes do not need fabricated mutation tests" | REPLACES: "Before work starts, a subject declares its profile and profile version" -> "Before work starts, a subject declares its profile, profile version and artifact kind; a profile names acceptance per artifact kind (code, docs, doctrine)" | PROOF: a code-profile project whose doc-only subject has a pinned N-run acceptance that is not fabricated

K6 | FRICTION | "Every acceptance includes a key from an independence class other than the producer's" | S1 landed with no other-class key (Opus producer; the Haiku seats came after landing and are the same family). S2's corrections carried a Codex gpt-5.6-sol key, which found 3 defects that survived the same-family round (bus RECEIPTS "Cross-family review of Cloudvore's two 2026-09-14 corrections"). Cost: 3 correction commits on the bus plus 2 on Cloudvore after landing | REPLACES: "Every acceptance includes a key" -> "Every acceptance, including doc-only and doctrine subjects that a project decides alone, includes a key" | PROOF: a Cloudvore doc packet in which the post-landing other-family key finds nothing, repeatedly

K7 | FIT | "Accepted is not delivered" | S1 delivered to Cloudvore master (100d4d4 reachable; `tools/gate.py --json` `landed.ok=true`). S3 was never accepted and never delivered. Its landing was aborted at the pre-push fetch when a competing kernel was found, and nothing half-landed on bus master: `git -C C:\code\softwarefactory-fleet-doctrine ls-tree origin/master ruling-candidates/universal-factory-kernel-r1.md tools/kernel-convergence.py` prints nothing | PROOF: that command printing a path

K8 | UNEXERCISED | "Running out of quota means rotating or parking the work that needs inference" | No call in this session was refused for quota or rate limit; every Codex and Agent call completed. Session logs were not searched for `rate_limit_event` | PROOF: a rate-limit event in this window's session logs

K9 | FRICTION | "A fresh session on a new account, with empty memory, resumes from the project's tree and the bus alone" | The Cloudvore entry gate passes: SessionStart `bootstrap: valid; work=ready`; `python tools/gate.py --json` exit 0, `landed=True`. But the closeout resumability gate reports `rotation: NOT READY` on `python tools/rotation-ready.py --strict`, for two reasons: `BLOCKING worktrees clean: DropBox Vault:2, Cloudvore-f10-20260909:1` (other writers' files, `review/warden-beats.jsonl` and a metrics baseline), and `everything pushed: ? unpushed commit(s)`. Cost: the gate cannot tell losable work of this session from a sibling's dirty tree, so it stayed red all window with nothing of this session's losable | REPLACES: "resumes from the project's tree and the bus alone" -> "resumes from the project's tree and the bus alone; a resumability gate attributes each losable item to its writer" | PROOF: `rotation-ready.py --strict` going green while another session's worktree is dirty, with nothing of this session unpushed

K10 | FRICTION | "records the account it was derived under" | `~/.claude/machine-inventory.yaml` on Dell XPS 17: `generated_at: 2026-09-14T12:23:03-05:00`, `probed_under: unknown`. Parity was MATCHED (hook fp `b4d2646b85c1`). The inventory therefore cannot say whether it is stale for this account; magic-lantern_dannephoto reported the same field on its bench | REPLACES: "records the account it was derived under" -> "records the account it was derived under; an inventory with no recorded account is treated as stale" | PROOF: an inventory on this machine with `probed_under` set to an account fingerprint

K11 | FRICTION | "R1–R5, R7, R8 and R9 apply to every report a factory makes about itself" | This session published 2 false statements in a correction receipt (bus d772f3b: proof row 1 "stands"; "the contract … lane chips"). A third needed narrowing ("only registered SessionStart hook"). Each was corrected append-only (cf74c20, ff36092). Cost: 3 review rounds and 2 extra bus commits | REPLACES: "apply to every report a factory makes about itself" -> "apply to every report a factory makes about itself; a report that cites a command or flag quotes it from the reporting project's tool at the cited commit" | PROOF: a receipt that cites a flag absent from its own project's tool at the cited commit and is not caught (TRAPS 2026-09-14, "copied between projects")

K12 | FIT | "Every project that runs the kernel files what happened" | This file, on `review/cloudvore-kernel-2026-09-14` | PROOF: `git ls-remote origin refs/heads/review/cloudvore-kernel-2026-09-14` returns nothing

## Profile lines

P:code subject-identity | FIT | "git tree OID of the candidate commit" | K3 commands for S1 and S2 | PROOF: see K3

P:code acceptance-evidence | FRICTION | "the project's pinned acceptance runs at the exact commit (for example N identical green runs)" | Cloudvore's pinned bar is "three identical green runs at one candidate SHA" (`CLAUDE.md`), which applies to product bytes. S1 and S2 were docs and doctrine. Their actual acceptance was `tools/gate.py` exit 0 and `tools/check-doc-size.py` 0 over hard cap, plus post-landing review. S3's tool was accepted on 12 tests plus 13 single-guard mutations, each run once, not three times | REPLACES: "the project's pinned acceptance runs at the exact commit" -> "the project's pinned acceptance for that artifact kind runs at the exact commit" | PROOF: a code-profile bar that is meaningful for a doc-only subject

P:code independent-key | FRICTION | "a verifier from another model family (R3) or a CI runner the producer does not control" | S1: none at acceptance. S2: Codex Sol (other family). S3: Codex Sol ×2. Bus CI on master was already red (`tools/check_universal_manifest.py --treeish` → `GIT_BLOB_UNAVAILABLE` locally, identical before and after S3's local commit), so no CI key was available | REPLACES: "or a CI runner the producer does not control" -> "or a CI runner the producer does not control whose base is green" | PROOF: a green bus CI run available as a key in this window

P:code resource-terminals | FIT | "suite timeout, thermal admission, runner capacity: typed terminals, no partial green" | Codex's read-only sandbox had no writable temp directory, so its test run terminated UNEVALUABLE, recorded as such, not as green. A 600 s tool ceiling moved a mutation run to background; it completed, restored the tool file, and reported OK | PROOF: a Cloudvore receipt counting an UNEVALUABLE run as passed

P:code delivery-target | FIT | "integration branch via the project's landing path; review branches push (R7)" | S1: Cloudvore master via fast-forward push (`git merge-base --is-ancestor origin/master HEAD` exit 0 before each push). This filing: a review branch, pushed without asking | PROOF: a non-fast-forward push by this session

P:code human-gates | FIT | "releases, security-sensitive paths, frozen bytes, and anything the project's register lists" | No tag or release in the window; no `src/` touched; tagging stays owner-only (register push-and-tag) | PROOF: a tag created in this window

## Instance map

K1 `tools/next.py` `adjudicate=YES` for `src/`, guard or merge paths (doc-only: **NONE**; see K1). K2 `knowledge/owner-gated-decisions.md`.
K3 git tree OID. K4 `tools/gate.py` `landed=`, 3-run rule. K5 **NONE** (no profile column in `BACKLOG.md`).
K6 `docs/operating-contract-model-routing.md` (a cross-family seat is optional). K7 `tools/gate.py` `landed=` and the merge-authority grant.
K8 `docs/operating-contract-model-routing.md` exhaustion fallback. K9 `tools/gate.py --doctrine-check` plus `tools/rotation-ready.py --hook/--strict`.
K10 `tools/check-cli-auth.py` plus the user-level parity hook. K11 `docs/operating-contract.md` §Delivery. K12 `tools/doctrine-debt.py` plus this filing.
Not written into `docs/operating-contract.md`: that file measures 12,162 B against a 12,288 B cap (`python tools/check-doc-size.py --path docs/operating-contract.md`).

## Untested

Steward proposals carried from S3's review rounds. None has a Cloudvore test bench for r1's text; each has a reproducible check.

- §5 "At least five member projects have filed" | Filing identity is self-asserted. In S3's analogous tool, Codex made two fabricated filings reach "universal" (thread `01a0a1ac`). r1's criterion 1 counts filers the same way | REPLACES: "At least five member projects have filed" -> "At least five member projects have filed, each named by a `KERNEL:` line in its own `specs/<project>.md` on the filing's branch, and each filing's K3 identities recomputed by the arbiter" | PROOF: a fabricated `adjudications/factory-kernel/<ghost>.md` that `tools/harvest-status.py factory-kernel` counts alongside real ones
- §5 "The word cap in the header does not rise" | The cap measures only the kernel file. Profiles and PROMPT-K are uncapped, so policy can migrate there. Measured on S3's first draft: 183 candidate lines plus 431 companion lines, before a combined budget was added (Codex D, thread `01a0a1ac`) | REPLACES: "The word cap in the header does not rise" -> "The word cap covers the kernel, its profiles and PROMPT-K together, and does not rise" | PROOF: a revision whose kernel stays under cap while profile word count rises
- K12 "`harvest-status.py factory-kernel` showing it `HARVESTED`" | `tools/harvest-status.py` marks a filing HARVESTED when any `<stem>.dispositions.md` names its blob, without reading whether it answers any line (`subject_status`, the `answers`/`status` lines). An empty dispositions file satisfies K12's observable (Codex A2, thread `01a0a1ac`) | REPLACES: "showing it `HARVESTED`" -> "showing it `HARVESTED`, with one disposition line per filed clause line" | PROOF: add `filing_blob: <blob>` alone as `<stem>.dispositions.md` and run the tool: it prints HARVESTED
- Profiles "Determinism class" | This is free text per profile. S3 used four classes (deterministic, statistical, attended, judgment), with one portable minimum rule each. For judgment, the rubric is fixed before the artifact exists and ≥2 non-author judges score it. Offered as the field's value set | REPLACES: none proposed | PROOF: a profile whose determinism class fits none of the four
- Parallel drafting | Three sessions (Conjugal, magic-lantern_dannephoto, Cloudvore) built kernels from one owner sentence on one day. The TRAPS test caught the last two only at landing, after the draft cost was spent (Cloudvore: 4 research agents, 4 review seats). A search at start would have found a0d8d4c only if run after 15:49 | REPLACES: none; this is a note for PROMPT-A or the bootstrap README | PROOF: a fourth same-day parallel kernel
