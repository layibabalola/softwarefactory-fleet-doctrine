#!/usr/bin/env bash
# Bounded reproduction instrument for multi-agent-branch-landing-protocol-r2.
#
# WHY THIS EXISTS. R1 of that candidate was REJECTED by an independent gate on the grounds that
# every measurement it carried was unpinned prose: "another seat cannot rerun or authenticate the
# measurements", failing the standing rule that a ruling without rerunnable evidence is an opinion
# with a timestamp. The gate named the remedy: pin the exact inputs, or carry a bounded reproduction
# instrument with positive AND negative controls. R2 does both. This is the second half.
#
# DEPENDENCIES, enumerated rather than hand-waved. R2 claimed "nothing but git and bash" and an
# independent gate refuted it: this script also calls mktemp, grep, awk, sort, uniq, wc, cat, sed
# and printf. All are POSIX utilities present in any coreutils environment (Linux, macOS, WSL, and
# Git-for-Windows' bundled bash). Required: git >= 2.30 (for `merge-tree --write-tree` in arm 5),
# bash >= 4, and coreutils. It depends on no repository, network, credential or provider. It creates a throwaway repository in a temp directory,
# plants each failure mode the protocol addresses, and demonstrates it. Every arm is paired: the
# defect must be SEEN, and the clean case must NOT be flagged - an arm that can only fire proves as
# little as one that cannot.
#
#   bash multi-agent-branch-landing-repro.sh
#
# Exit 0 = every arm behaved as the protocol claims. Exit 1 = a claim did not reproduce, which is a
# finding against the protocol and should be reported as one.
set -u

PASS=0; FAIL=0
ok()   { PASS=$((PASS+1)); printf '  [PASS] %s\n' "$1"; }
bad()  { FAIL=$((FAIL+1)); printf '  [FAIL] %s\n' "$1"; }
chk()  { if [ "$2" = "$3" ]; then ok "$1"; else bad "$1 (expected '$3', got '$2')"; fi; }

R="$(mktemp -d)"; trap 'rm -rf "$R"' EXIT
cd "$R" || exit 1
git init -q .; git config user.email r@example.invalid; git config user.name repro
git config commit.gpgsign false 2>/dev/null || true

echo "=== multi-agent branch-landing: reproduction ==="
echo "  scratch repo: $R"
echo

# ---------------------------------------------------------------------------------------------
# ARM 1 - A TIP MOVES BETWEEN CENSUS AND MERGE.
# The protocol's core claim: a tip read at census time may not be the tip at merge time, and
# merging the stale one can land content the owner has already superseded.
# ---------------------------------------------------------------------------------------------
echo "base" > f.txt; git add -A; git commit -qm base
BASE=$(git rev-parse HEAD)
git checkout -qb feature
echo "first attempt, contains a defect" > f.txt; git commit -qam "work v1"
CENSUS_TIP=$(git rev-parse HEAD)          # what a census would have recorded
echo "repaired after re-deriving" > f.txt; git commit -qam "work v2 - owner repaired it"
MERGE_TIP=$(git rev-parse HEAD)           # what the owner actually intends
git checkout -q master 2>/dev/null || git checkout -q main

chk "ARM1 a tip read at census differs from the tip at merge" \
    "$([ "$CENSUS_TIP" != "$MERGE_TIP" ] && echo moved || echo same)" "moved"
# POSITIVE CONTROL: merging the census tip really does land the superseded content.
git merge -q --no-edit "$CENSUS_TIP" 2>/dev/null
chk "ARM1 merging the CENSUS tip lands the defective content" \
    "$(grep -c 'contains a defect' f.txt)" "1"
git reset -q --hard "$BASE"
# NEGATIVE CONTROL: merging the owner-confirmed tip lands the repair.
git merge -q --no-edit "$MERGE_TIP" 2>/dev/null
chk "ARM1 NEGATIVE: merging the OWNER-CONFIRMED tip lands the repair" \
    "$(grep -c 'repaired' f.txt)" "1"
git reset -q --hard "$BASE"

# ---------------------------------------------------------------------------------------------
# ARM 2 - `git add -A` SWEEPS A CONCURRENT SEAT'S UNCOMMITTED WORK.
# Two agents share one working tree; one stages everything and captures the other's edit under
# its own commit and change-request number.
# ---------------------------------------------------------------------------------------------
echo "mine"  > a.txt
echo "PEER EDIT - not mine" > peer.txt      # a second seat's uncommitted work
git add -A && git commit -qm "seat A: git add -A"
chk "ARM2 'git add -A' captured the peer's uncommitted file" \
    "$(git show --stat --format= HEAD | grep -c peer.txt)" "1"
git reset -q --hard "$BASE"; rm -f a.txt peer.txt
# NEGATIVE CONTROL: explicit staging leaves the peer's work alone.
echo "mine" > a.txt; echo "PEER EDIT - not mine" > peer.txt
git add -- a.txt && git commit -qm "seat A: explicit path"
chk "ARM2 NEGATIVE: explicit staging did NOT capture it" \
    "$(git show --stat --format= HEAD | grep -c peer.txt)" "0"
git reset -q --hard "$BASE"; rm -f a.txt peer.txt

# ---------------------------------------------------------------------------------------------
# ARM 3 - A REWRITTEN COMMIT IS AN ANCESTOR OF SEVERAL BRANCHES.
# The claim R1 asserted and could not pin: renumbering one branch does not fix a collision that
# lives in shared ANCESTRY. Costing it by citation count understates the graph.
# ---------------------------------------------------------------------------------------------
git checkout -q -b shared "$BASE"
echo "card ID-07 = alpha" > ledger.md; git add -A; git commit -qm "shared: defines ID-07"
SHARED=$(git rev-parse HEAD)
for b in br1 br2 br3; do
  git checkout -q -b "$b" "$SHARED"
  echo "$b extra" > "$b.txt"; git add -A; git commit -qm "$b work"
done
N=0
for b in br1 br2 br3; do git merge-base --is-ancestor "$SHARED" "$b" && N=$((N+1)); done
chk "ARM3 one shared commit is an ancestor of all three branches" "$N" "3"
# NEGATIVE CONTROL: a commit unique to one branch is an ancestor of only that branch.
ONLY=$(git rev-parse br1)
M=0
for b in br1 br2 br3; do git merge-base --is-ancestor "$ONLY" "$b" 2>/dev/null && M=$((M+1)); done
chk "ARM3 NEGATIVE: a branch-unique commit is an ancestor of exactly one" "$M" "1"

# ---------------------------------------------------------------------------------------------
# ARM 4 - AN APPEND-STRUCTURED LEDGER IS NOT SAFE TO 'KEEP BOTH' WHEN IDS COLLIDE.
# Union-merging two sides that define the SAME id yields duplicate headings, which any tool
# keying on the id then resolves to two different records.
# ---------------------------------------------------------------------------------------------
git checkout -q master 2>/dev/null || git checkout -q main
git checkout -q -b sideA "$SHARED"; printf '## ID-07 alpha\n## ID-08 beta\n' > ledger.md; git commit -qam sideA
git checkout -q -b sideB "$SHARED"; printf '## ID-07 GAMMA\n## ID-09 delta\n' > ledger.md; git commit -qam sideB
# simulate a keep-both resolution
cat <(git show sideA:ledger.md) <(git show sideB:ledger.md) > merged.md
DUP=$(grep -oE '^## (ID-[0-9]+)' merged.md | awk '{print $2}' | sort | uniq -d | wc -l)
chk "ARM4 keep-both on colliding ids produces a duplicate id" "$DUP" "1"
# NEGATIVE CONTROL: after renumbering one side, keep-both is safe.
git checkout -q sideB; printf '## ID-37 GAMMA\n## ID-09 delta\n' > ledger.md; git commit -qam "sideB renumbered"
cat <(git show sideA:ledger.md) <(git show sideB:ledger.md) > merged2.md
DUP2=$(grep -oE '^## (ID-[0-9]+)' merged2.md | awk '{print $2}' | sort | uniq -d | wc -l)
chk "ARM4 NEGATIVE: after renumber, keep-both yields zero duplicates" "$DUP2" "0"

# ---------------------------------------------------------------------------------------------
# ARM 5 - A CONFLICT INSIDE A FILE WHOSE CONTENT IS A MEASUREMENT.
# Hand-merging a checksum file composes a checksum set no tool computed. The instrument shows the
# conflict is detectable WITHOUT mutating anything, so it can be routed for re-derivation instead.
# ---------------------------------------------------------------------------------------------
git checkout -q master 2>/dev/null || git checkout -q main
git checkout -q -b pinA "$BASE"; echo "aaaa  docs/x.md" > sums.txt; git add -A; git commit -qm pinA
git checkout -q -b pinB "$BASE"; echo "bbbb  docs/x.md" > sums.txt; git add -A; git commit -qm pinB
if git merge-tree --write-tree pinA pinB >/dev/null 2>&1; then C=0; else
  C=$(git merge-tree --write-tree pinA pinB 2>&1 | grep -c '^CONFLICT')
fi
chk "ARM5 the pin file conflicts, detected read-only via merge-tree" "$C" "1"
DIRTY=$(git status --porcelain | wc -l)
chk "ARM5 NEGATIVE: detection mutated nothing (tree still clean)" "$DIRTY" "0"

echo
echo "PASS $PASS  FAIL $FAIL"
[ "$FAIL" -eq 0 ] || exit 1
exit 0
