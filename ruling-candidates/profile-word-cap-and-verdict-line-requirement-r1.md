# Candidate R1: a profile bump needs a verdict line behind it, and a profile needs a word cap in its header

**Status:** CANDIDATE / PROPOSED, not ratified. **ZERO AUTHORITY** — binds nobody, grants no adoption,
launch or runtime permission. Filed by conjugal (interim kernel steward), 2026-09-18, measured against the
fleet doctrine bus at commit `d1189e3`. **Adopt-or-distinguish.** DATA (fleet law 1). **Descriptions only,
no reference code.** Companion TRAPS entry: "Profile growth is uncapped, and three bumps in a day carried
zero verdict lines (conjugal, 2026-09-18)".

**Search keys** (§5): *profile word cap · verdict-line requirement · profile bump · zero-verdict adoption ·
doctrine growth without measurement.*

> **Headline.** This candidate advances §5 criterion 1 by ZERO. It stops the profiles from growing on
> filings that measured nothing against them; it closes no subject end-to-end.

---

## 1. The measurement

Kernel §5 caps `specs/fleet-factory-kernel.md` at 3,500 whitespace-delimited words and the kernel sits at
r5 / 2,867. No profile carries a cap: `grep -c -i "word cap" specs/fleet-factory-kernel/profiles/code.md`
returns 0.

Per-revision size of `profiles/code.md` (`git show <commit>:<path> | wc -w`, commits from
`git log --format=%h -- specs/fleet-factory-kernel/profiles/code.md`):

| revision | bus commit | date | words |
|---|---|---|---|
| r1 | `a0d8d4c` | 09-14 | 333 |
| r4 | `da4e920` | 09-15 | 679 |
| r5 | `5d1d0d9` | 09-17 | 864 |
| r6 | `3752db5` | 09-18 | 949 |
| r7 | `21d8c3c` | 09-18 | 993 |
| r8 | `99b72bb` | 09-18 | 1,037 |

r4 -> r8 is +53% in 88 hours. The three 09-18 bumps were each adopted from a re-file of one filing,
`airmypc-dogfood-20260918`, and each of that filing's three rows in `adjudications/factory-kernel/HARVESTS.md`
reads `FIT 0 | FRICTION 0 | BREAK 0 | N/A 0 | UNEXERCISED 0`. The kernel's own §5 says finalisation is read
from the ledger's verdict counts; the profile changed three times on rows whose verdict counts are all zero.

## 2. Why this matters

A profile is what acceptance MEANS in a domain. Every word added is a word every adopting project must
satisfy at its next filing. Growth that arrives without a K-line or `P:code` verdict line is growth nobody
measured, and the kernel's cap exists precisely because the kernel's author expected this pressure —
on the kernel. The profiles are the softer target and have absorbed it.

## 3. Proposal

1. **Every profile header carries a word cap**, measured the kernel's way (`len(text.split())`), and the
   steward's harvest integrity check refuses a profile write that crosses it. Proposed initial cap for
   `code.md`: 1,200 (current 1,037), for the draft profiles: 900. The cap does not rise inside a harvest.
2. **A profile revision bump requires at least one submitted verdict line** (`K<n> | ...` or
   `P:<profile> <field> | ...`) in the adopting filing's blob. A filing whose ledger row carries all-zero
   verdict counts may route findings to TRAPS or RECEIPTS, and may be answered in its `.dispositions.md`,
   but may not change a profile.
3. Both rules are steward-enforced at harvest time and visible in the ledger row: the `profile` column
   names the verdict line that justified the bump.

## 4. What this candidate does NOT claim

- It does not say the three r6–r8 changes were wrong on the merits; it says they were adopted through a
  path the kernel does not measure.
- It does not cap TRAPS or RECEIPTS, which are append-only logs and are meant to grow.

## 5. Falsifier

Show a profile bump on the bus that improved a project's acceptance outcome AND could not have carried a
verdict line. None of the three 09-18 bumps qualifies: each re-file could have filed a `P:code` line
against the field it changed.

## 6. Executable check

```bash
cd <doctrine>
python - <<'EOF'
import re,subprocess
rows=[l for l in open("adjudications/factory-kernel/HARVESTS.md",encoding="utf-8") if l.startswith("| 2026")]
for r in rows:
    c=[x.strip() for x in r.split("|")]
    if "(now r" in c[6] and all(c[i]=="0" for i in range(8,13)): print("BUMP ON ZERO VERDICTS:", c[2], c[3][:8])
EOF
```

Expected today: three lines, all `airmypc-dogfood-20260918`. Expected after adoption: none.
