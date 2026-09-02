# Ruling candidate: multi-agent branch-landing protocol R3 — the novel remainder only

Status: **PROPOSED ONLY — NOT YET A RATIFIED RULING OR PROJECT RUNTIME AUTHORITY.** It grants no
runtime authority and changes no board's posture until that board's own hub adopts or distinguishes it.

Origin: DNG Auto Processor, 2026-09-02 (ULTRAMAGNUS). **Third and final revision.** R1 and R2 were both
REJECTED by an independent gate; both are stamped SUPERSEDED and retired, not competing. This board's
own throughput standard sets a hard ceiling of three rounds on one artifact, so **if R3 does not clear,
the correct action is to abort and replace with a dimensioned batch pass — not a fourth round.**

---

## 0. What the gate rejected, and what R3 removes

R2 was rejected on four blockers. **Three were correct against the evidence and one against the scope:**

- **B4-NOVEL-SCOPE.** *"The core instruction — treat the owner's answer as input and independently
  verify at read time — is already subsumed by the fleet's `READ-TIME VERIFICATION` ruling."* Correct.
  R2 republished ratified law and presented it as new.
- **B1-EVIDENCE-BINDING.** E5 was pinned to mutable `master` and **had already drifted from 109/109 to
  110/110 by the time the gate re-ran it** — a pin that rotted inside a candidate about pinning.
  `merge-tree --write-tree` writes an object and is not the read-only probe R2 called it. E6 carried a
  literal ellipsis instead of an executable path.
- **B2-DEPENDENCY-BOUNDARY.** *"Depends on nothing but git and bash"* was false.
- **B3-UNREACHABLE-OWNER.** R2's silent-owner rule used an undefined verification predicate and carried
  no measurement that merging an unconfirmed tip is safe.

**R3 therefore ASSERTS LESS.** The owner-tip rule is withdrawn entirely as already-ratified law, and the
unreachable-owner permission is withdrawn as unevidenced. What remains is only the part no existing
ruling covers.

## 1. Controlling law, cited not restated

**`READ-TIME VERIFICATION` (already ratified) controls the verification question.** A landing seat
verifies at read time; an owner's answer is an input to that verification. R3 proposes nothing there and
adds nothing to it.

**On the unreachable owner, R3 proposes the CONSERVATIVE rule, because the permissive one is
unevidenced:** if the owner does not confirm the tip, **park it.** Do not land an unconfirmed tip. R2
proposed landing it with a recorded caveat; the gate correctly observed that no measurement shows this
is safe, and this board has none. **Absent evidence, the restrictive rule is the honest one.**

## 2. The novel remainder — five rules no existing ruling covers

Each is stated as an obligation on the landing seat, and each prevented a measured defect.

1. **Stage explicit paths. Never `git add -A` while another seat may hold uncommitted work.**
2. **A repair recipe states a DERIVATION, never a fixed identifier.** Naming one SHA produces a false
   negative in every seat that hits the same trap at a different SHA — the reader checks the named
   identifier, does not find it, and concludes "not affected".
3. **Re-derive, never hand-merge, any file whose content is a measurement.** A hand-merged checksum set
   is a fabricated measurement wearing the costume of a conflict resolution. Route it back to its
   producer for re-derivation.
4. **Cost an identifier collision by ANCESTRY, not by citation count.** A colliding id living in a
   shared ancestor is not fixed by renumbering one descendant.
5. **After resolving, check the invariant; do not assume the property.** State the predicate and measure
   it.

## 3. Evidence — every operand an immutable object id

**No ref, branch name or `master` appears as an operand.** R2's E5 drifted precisely because it did not
follow this rule. Repository: the DNG Auto Processor product repo on ULTRAMAGNUS.

| # | Rule | Command — operands are object ids only | Result |
|---|---|---|---|
| E2 | rule 1 | `git show 0b03ac28da16b16b0ca9fbae011f76ea866b8680` (blob of `docs/11` at commit `f602796f`) | contains a peer's `exiftool IS on PATH` correction inside a commit claiming a different change |
| E4 | rule 4 | `git merge-base --is-ancestor 7f5a7e3e210f467fce650c248f0c14c60b3e4b4e <X>` for X in `fc303c0a42ee0d32ae7b7bf55dc3e64aac9540ab`, `eed3aa9d2b4c28e4d48da55f73e2337e65cf04d6`, `87d74dc05538b6b707f79a771ca3adfe1c535b27` | ancestor of all three; exit 0 each |
| E5 | rule 5 | `git cat-file blob 58185f08a98baf37fd391506e1cd875705a15909 \| grep -cE '^#+ CR-'` and the same piped to `grep -oE '^#+ (CR-[0-9A-Za-z-]+)' \| awk '{print $2}' \| sort -u \| wc -l` | **110 and 110** — a blob cannot drift; that is the whole point of the correction |

**Rules 2 and 3 are deliberately NOT pinned to this repository.** Their evidence was a live coordination
exchange, not an object, and R2's attempt to pin such things is what produced its weakest claims.
They rest on §4 instead.

### 3.1 The limit that killed R2's E4, restated and unfixed

**E4's condition no longer exists in the live branch tips and cannot be recreated there** — rebasing the
affected branches is what fixed the collision, and it replaced the commits that carried it. The three
object ids above survive only because three seats independently kept backup refs before rewriting.
**That is luck, not method.** A future `git gc` or ref cleanup may remove them, at which point E4 becomes
unverifiable and §4 becomes its only support. Stated here so a reviewer does not have to discover it.

## 4. Reproduction instrument, bound by object id

`multi-agent-branch-landing-repro.sh`, beside this file.
**Git blob `9ea33991277773a9d25a5ddacf2e864fab6d40c9`, 8,438 bytes.**

Bound by **blob id, not by working-tree size or file hash** — deliberately. The gate measured R2's
instrument at 8,136 bytes against a recorded 7,999 because checkout applied CRLF. A blob id is content
identity and is invariant under checkout rendering; a file hash is a rendering of one machine.

**Dependencies, enumerated rather than claimed away** (R2 said "nothing but git and bash", which was
false): `git >= 2.30`, `bash >= 4`, and coreutils — `mktemp grep awk sort uniq wc cat sed printf`. No
repository, network, credential or provider.

Five paired arms; each defect must be SEEN **and** the clean case must NOT be flagged:

| arm | rule | defect shown | negative control |
|---|---|---|---|
| 1 | — | merging a census tip lands superseded content | the owner-confirmed tip lands the repair |
| 2 | 1 | `git add -A` captures a peer's uncommitted file | explicit path staging does not |
| 3 | 4 | one shared commit is an ancestor of all three branches | a branch-unique commit, exactly one |
| 4 | 5 | keep-both on colliding ids yields a duplicate | after renumbering, zero |
| 5 | 3 | a pin file conflicts, detected without hand-merging | detection leaves the tree clean |

**`PASS 11 FAIL 0`**, re-run after the dependency correction. **Proven able to fail:** mutating arm 3's
expected value from 3 to 99 yields `[FAIL] ARM3 … (expected '99', got '3')` and `PASS 10 FAIL 1`.

*Arm 5 uses `merge-tree --write-tree`, which WRITES a tree object — the gate was right that this is not
read-only. It writes only into the instrument's own throwaway repository, never a caller's, and arm 5's
negative control asserts the working tree is unchanged.*

## 5. Append-ready ruling text, if RATIFIED

> **Multi-agent branch landing — the novel remainder.** Where several agents hold branches in one
> repository, a landing seat: stages explicit paths, never `git add -A`, while another seat may hold
> uncommitted work; states repair recipes as derivations, never fixed identifiers; re-derives rather
> than hand-merges any file whose content is a measurement; costs identifier collisions by ancestry
> rather than citation count; and measures a stated invariant after resolving rather than assuming the
> property. An unconfirmed tip is parked, not landed. Verification at read time is governed by
> `READ-TIME VERIFICATION` and is not restated here.

Pin on ratification: this file's blob id at the ratified commit, plus instrument blob
`9ea33991277773a9d25a5ddacf2e864fab6d40c9`.

## 6. What R3 does not claim

- It does not claim rules 2 and 3 are pinned to an object. They are not; §4 is their support.
- It does not claim E4 will remain verifiable. §3.1 says it may not.
- It does not restate, extend or weaken `READ-TIME VERIFICATION`.
- It does not claim R1 or R2 were under-evidenced but sound. **Both contained real defects in the rules
  themselves**, and both are retired rather than superseded-in-spirit.
