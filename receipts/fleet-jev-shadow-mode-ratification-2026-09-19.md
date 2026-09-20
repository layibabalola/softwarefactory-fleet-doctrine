# Ratification receipt: `specs/fleet-jev-shadow-mode.md` (append-only)

Protocol: owner ruling 2026-09-06 (no owner ratification; two blind cross-family adversaries; two
NO-VETO publish; one VETO permits one revision and one re-review by the vetoing seat; a VETO that
survives declines the packet). Seats: Claude Opus subagent (background, reads primary sources) and
`codex exec --sandbox read-only` (codex-cli 0.154.0, packet and standard inlined on stdin, no tools).
Neither seat saw the other's output. Author of the standard and packet: the Cloudvore session
(Claude Fable 5.1), which is neither seat.

## Round 1 (packet v1) — DECLINED under the packet's own rule

### Codex seat, round 1: VETO

Required changes: (1) §5 fleet row "Jev may add an owed entry to the queue" was authority creep;
(2) §7 seam row conflated two comparators (`owed` 87% vs "31/31 on regex positives" vs "17 Jev-only
positives" do not reconcile under one binary comparison). Falsifiers 1 and 2 FOUND, 3 to 5 NOT FOUND.
Both changes were made: §5 now says shadow mode only logs a proposed additional owed entry and never
adds, removes or touches a verdict; §2.4 says promotion beyond advisory is a separate recorded owner
decision that no threshold grants and that waives no §5 rule; §7 now gives the two comparators with
their counts (138/159: 4 regex positives below 0.5 and 17 regex-negative commits at or above 0.5;
class matched 31/31 on regex positives and `none` on 89/128 regex negatives).

### Codex seat, round 2 (the one permitted re-review): VETO sustained

Both round-1 changes confirmed MADE; falsifiers 1 to 3 NOT FOUND on the revised standard. Two new
defects, both in the packet text added at the seat's own round-1 request: (4) ROLLBACK said "revert
the three bus paths" while the receipt is declared append-only; (5) the owner-level pointer text
said "TypeSafe Jev is set up for shadow mode on this machine", a state claim. Remaining defects:
reference-only pointer text; rollback limited to the spec and README bullet plus an appended
reversal in the preserved receipt. Verdict rule applied: a VETO surviving the one retry declines
packet v1.

### Claude Opus seat, round 1: VETO (independent of the Codex seat; both vetoed v1)

Findings, verbatim in substance (full text in the author's session record):

1. §7 row 1 "7/12 vs the substring rule" is wrong against its own report: `tier-probe-burst.json`
   gives `labelled 12, agree 6` (6/12); the Reading miscounted six disagreements as "three ... two"
   (four expected-false throttles including `syn-b2-503` at 0.58, plus two false positives).
2. "31/31 on regex positives" was false as an `owed` claim: 27/31 (`26da597` 0.15, `df93ff0` 0.13,
   `0e6ab0a` 0.19, `f920f4e` 0.44); "17 Jev-only positives" correct.
3. "12/12 vs ground truth" is in no report; every `expected` is the current rule's output; it was
   the author's unblinded re-read (kernel K11, reports are honest).
4. Denominator elision: `admits_unmet` is 52/68 (23 near-half) not "76% of 111"; ML "85% at
   confidence ≥ 0.7" is 40/47 of 338; fd-c1 and ml-j1-clean each have `failed: 1`, so 159 and 338.
5. Mechanical bus defect: `specs/jev-shadow-mode.md` would register a phantom fleet member
   `jev-shadow-mode` via `tools/fleet-membership.mjs:10-18`; publish as
   `specs/fleet-jev-shadow-mode.md`.
6. Authority creep in the §5 fleet-doctrine row ("Jev may add an owed entry to the queue").
7. §2.4's advisory step was self-executing; it must require the project's own authority register
   (kernel K2) alongside the two runs.
8. The standard tripped the screen it cites: Conjugal's Law-4 tuple refuses a bare state-directory
   token (`coordination/tools/doctrine_outbox.py:80`) and §5's Conjugal log path carried one.
9. Packet EVIDENCE claimed every §5 rule was cited to file:line; the SilentBackgroundProcess cell
   had none, and `USER_DIAGNOSTIC_ONLY` / `wscript` were not in the cited spec document.
10. Evidence durability: the runnable root is not a git repository; reports carried no digest
    (kernel K3/K9).
11. Confirmations: every other cited bounding rule reproduced (`operating-contract.md:151,162`,
    `PRIVACY.md:7`, Conjugal `CLAUDE.md:54`, ML `CLAUDE.md:52,63-67`, `AuthorityMatcher.cs:133`,
    `RULINGS.md:89-92`); §7 SBP 89/70/75, CoS 119/131, Conjugal 17/20, rclone real 47/47,
    `self_blocked` 104/111, ML state 64% and classification 22% all reproduced; $0.042/1M
    reproduced from 0.005364 / 127,712 tokens; `ai@7.0.107` installed.
Falsifier check: 1 FOUND, 2 FOUND, 3 NOT FOUND, 4 FOUND (membership classifier, K11, K3/K9),
5 NOT FOUND (no pointer text was drafted to review).
Required changes (8): all applied in v2 of the standard; the digests below answer finding 10.

### Author's disposition of round 1

Every required change from both seats is applied. The two seats found disjoint defects (Codex:
the rollback/receipt contradiction and the state-claiming pointer; Opus: the arithmetic, the
denominators, the filename/membership trap, the K2 gate, the SBP citation, the Law-4 state-directory
token), which is the reason the protocol uses two families. v1 is DECLINED; v2 follows.

## Round 2 (packet v2) — two fresh blind seats

Packet v2 corrects the two packet sentences the Codex seat named and applies all eight changes the
Opus seat required to the standard (now `CANDIDATE r2`, filed as `specs/fleet-jev-shadow-mode.md`).
Two fresh blind seats (a new Claude Opus subagent and a new `codex exec` run) review v2 without
sight of any v1 review.

### Codex seat, v2 round 1: VETO

Falsifiers 1, 3, 4 NOT FOUND; 2 FOUND (§1 stated vendor-documented model limitations, "cannot count
or compare numbers, dates or hashes", as if measured here; the digest manifest promised by §7 was
not in the supplied text); 5 FOUND (the owner pointer's sentence "The gateway key is read from the
User environment scope per process and never printed" is a state claim). Also: ROLLBACK omitted the
owner-level paragraph that ACTION adds. Confirmed: §7 arithmetic reconciles (six synthetic
disagreements, 138/159 and 120/159, Magic Lantern groups total 338); §§2.2-2.4 authority
restrictions explicit; receipt preservation respected. Required changes: delete the key sentence;
extend ROLLBACK; restate §1 limitations as operating restrictions; include filenames, digests and
privacy-safe extracts for the empirical claims.

### Codex seat, v2 round 2 (the one permitted re-review): VETO sustained

Changes 1-3 MADE (quoted). Change 4 NOT MADE: §7.1 gave 16-hex digest prefixes and deferred the
full digests to a receipt the seat cannot see; the smoke transcript had no digest; two reports used
for the paid-tier latency figure (`report-fd-c5`, `report-ml-j1-active`) had no manifest entry; the
§1 claims "500 to 1,700 input tokens" and "p50 about 235 ms at concurrency 8" were not established
by the supplied extracts (the manifest's explicit p50 was 446 ms at concurrency 6). Falsifiers 1, 3,
4, 5 NOT FOUND; 2 FOUND on evidence completeness only. The seat noted the veto "concerns incomplete
evidence, not proof that the retained measurements are false". Verdict rule applied: packet v2
DECLINED.

### Claude Opus seat, v2: VETO (independent; three required changes, all precision)

1. §1 "A 3-question call is 500 to 1,700 input tokens" is not what the reports measure: per-call
   `usage.inputTokens` across the five three-question corpora runs 794 to 2,305 (99 of 837 calls
   above 1,700; `report-sbp-a1` averages 1,704).
2. §7 SBP row "every owner miss" is false for 1 of 9: `service.fusionservice.cd753b3d` has rule
   `dell`, Jev `dell_fusion`, a granularity split, not a default-arm rescue.
3. §7 synthetic row is supported exactly by `tier-probe-burst.json` but contradicted by the
   similarly named free-tier `report-cv-c2-synthetic.json` (4 of 12, agree 1/4); the row must name
   its source inline.
Confirmations: every other §7 number reconciles exactly (fd-c1 138/159, 120/159, 30 near-half,
four sub-0.5 positives 0.13/0.15/0.19/0.44; fd-c2 119/131 with 10 of 12 misses on the 93-row
majority class; cv-b1 104/111, 52/68, 23 near-half, 7 WAITING misses, READY 27/27; cj-a3 17/20 with
misses at 1.00 and 0.94; ml-j1 217/338, 76/338, 40 of 47 at confidence ≥ 0.7; cv-c2 47/47; list
price $0.042/1M from $0.000248 / 5,900 tokens). `fleet-membership.mjs:14` confirms the `fleet-`
prefix registers no phantom member. Every cited bounding rule reproduced (`operating-contract.md:151,
162`; `PRIVACY.md:7`; Conjugal `CLAUDE.md:54`; `doctrine_outbox.py:68-82`; ML `CLAUDE.md:52,63-67`;
`AuthorityMatcher.cs:133`; `OracleService.cs:89`). No authority creep; no private identifier in the
standard (the report JSONs carry local paths, so they must never be committed to the bus; the
packet commits only spec, receipt and README bullet). Pointer lines carry no state claim; Conjugal
`CLAUDE.md` 11,374 bytes + 211-byte bullet = 11,586 against the 12,000-byte hard cap in
`check-doc-size.py:58-60`; `Doctrine-Export: none` matches `CLAUDE.md:61-65`. Optional: cite Laws 1
and 2 for the ADOPT sentence; say "about 250 ms" and state the concurrency; the Conjugal cell's own
prose contained the refused token; add the report filename per §7 row; note the magic-lantern
pointer commit stays local. Digests computed by the seat match the receipt's.

Verdict rule applied: packet v2 DECLINED (both seats vetoed; both on evidence completeness and
precision; neither on authority, privacy, bus law or pointers).

## Round 3 (packet v3)

v3 applies every required and optional change from both v2 seats: §1 restates call size and
latency as the measured pooled spread with n, p50 and p90 and their derivation; §7 names the source
report in every row, says eight of nine for the SBP owner misses, and marks
`report-cv-c2-synthetic.json` as not a source; §7.1 carries the full 64-hex SHA-256 of every report
including the two previously omitted ones and the self-test, with per-report succeeded/failed,
concurrency, mean input tokens and p50/p90; the status line cites Laws 1 and 2; the Conjugal cell
and this receipt no longer contain the refused token; the packet notes the magic-lantern commit
stays local. Two fresh blind seats review v3.

### Codex seat, v3 round 1: VETO

Falsifiers 1, 3, 4, 5 NOT FOUND (authority boundaries "concrete"; pointers and rollback
"appropriately bounded"; no private identifier; no bus-law conflict). Falsifier 2 FOUND on evidence
completeness: the packet's ACTION item 1 still read `CANDIDATE r2` against the standard's `r3` (an
author slip, corrected); §1's pooled statistics (n = 837, p50 1,567, p90 1,706; pooled latency p50
245 / p90 423) had no distribution extracts a text-only reader could check; §7's per-question
characterisations ("eight of the nine owner misses", "30 of 159", "40/47") had no `perQuestion`
blocks inline. The checkable arithmetic passed (837, 1,074, 1,062; §7 percentages consistent).
Required: fix the status line; add extracts and conventions or remove the pooled claims; add the
per-question summaries and disagreement extracts. Applied in the revision: §1 restated from
per-report min / p50 / max and per-report above-1,700 counts; §7.1 gained those columns and the
percentile convention; §7.2 added with every `perQuestion` block and the specific disagreement lists.

### Codex seat, v3 round 2 (the one permitted re-review, receipt inlined): NO-VETO

All three required changes MADE (quoted). Falsifiers 1 to 5 NOT FOUND. Reasons: the operative
version agrees (`CANDIDATE r3` in ACTION and the standard); the distribution claims are checkable
(ten-report population 1,074; exceedance counts 22 + 5 + 48 + 24 + 1 = 100; extrema 444 to 2,458;
per-report p50 231 to 348 ms and p90 321 to 516 ms at concurrency 8); the question-level support is
present (47 + 291 = 338, 40/47; the receipt corroborates 27/27 on READY rows); authority remains
bounded (§§2.2-2.4); publication and reversal constrained (pointers assert no setup or adoption;
receipt preserved, reversal appended).

### Claude Opus seat, v3: VETO on process grounds (every number, rule, digest and pointer confirmed)

Confirmed: all twelve report digests recomputed and matched; every §1 and §7 figure reproduced,
including the pooled values the author had removed; every §5 bounding rule quoted accurately at its
file:line; the `fleet-` prefix adds no member (`fleet-membership.mjs:14`) and the file is still
listed by `isSiblingSurface` (`doctrine-sync.mjs:79-82`); Conjugal's real Law-4 tuple run over the
Conjugal cell and pointer: PASS; Conjugal `CLAUDE.md` 11,374 B + 216 B bullet = 11,590 B against
the 12,000 B hard cap; `Doctrine-Export: none` required and permitted. Falsifiers 1, 2, 3, 5 NOT
FOUND; 4 FOUND twice: (A) the review subject mutated during the blind review (the author revised
the standard and the packet to answer the Codex seat while this seat was reading; the packet
declared the subject by path with no digest, and the runnable root was not a repository, so no
verdict could be bound to a known text: kernel K3); (B) the new single-writer bus file named no
writer (Law 2; every sibling README bullet names one). Required: freeze both files, record their
SHA-256 in the packet and spec header, bind verdicts to the digest, re-run two blind seats; name a
writer in the header and the README bullet. Optional (all applied): 34-option classification;
min/p50/max for the free-tier synthetic report's cell; Law-6 qualification of the plan and
runnable-root paths; put the runnable root under git.

Verdict rule applied: packet v3 DECLINED (two vetoes on v3). The author records that revising a
subject while a blind seat reads it was a protocol breach on the author's side, not a seat error.

## Round 4 (packet v4)

v4 is digest-bound: the exact standard and packet under review are identified by SHA-256 below and
committed in the runnable root's new local git repository; the author does not edit them while a
seat is reading. Writer named (Cloudvore). Two fresh blind seats.

## Evidence digests (SHA-256 of the report files cited in the standard's §7, computed 2026-09-19)

```
9cad4f8f07069924b1b906b52889738d0e8495eac2bde4164ec3e075835d8dfc reports/tier-probe-burst.json
2e154c7287fc82c0730b566432d8fa63b8cf352e32f82bc0fbfb6845f350bbb2 reports/report-cv-c2.json
863a3a4ffde29d4ad1f740f647c61dd1a2f2eeb9b1804c32b0a6c1a848cf09ba reports/report-fd-c1.json
1447a268b42b6326b87db0b5f2ef03726878930c0136da1e9c7eed0f5f641236 reports/report-fd-c2.json
83048df5e6bb5d87c7c492a77b536023b8f1268cc90eea80a2be03f844d6f1cc reports/report-cv-b1.json
618263bac3f4d683b5c753673ae8f875a8cb02a828f257180b00e74bf7fa2da6 reports/report-sbp-a1.json
b5e1fbaa599fabc7c0dd4be8484df37fe623348a791ad1f03a8c488380931648 reports/report-cj-a3.json
a6996545542fde1364ad7318b1c2fd5331630cb1107ac38cfa26717fb325e6a5 reports/report-ml-j1-clean.json
21127686943edb2a675f22ae7f754f92ae85e6ee17de55c4ff878e2059ecd54f reports/report-ml-j1-active.json
55e2473768f61e7b2da39908a3c1cc30f1bf4452c568a1b156d69271348e3ca8 reports/report-fd-c5.json
```

### v4 subject digests (frozen 2026-09-19)

- standard `docs/jev-shadow-mode.bus.md` SHA-256 `63f6b878c5b1180e4a735f81e10e9a8b0a4255a983a1a1642fbb74bc5d5fb562` (19761 bytes)
- packet `docs/ratify-packet-jev-shadow-mode.md` SHA-256 `c9a03e682aa3b8185f7646d0ec3ae3acd5dd8920aef2aeaf7577fbcfa0fc0deb` (10671 bytes)
- runnable root commit (local git repository `jev-plan`, no remote): `ed5a21a299077fd6c3c5c39ba74beda0c4bc1d8b`
- both files are unchanged from these digests for the whole of the v4 review; the receipt itself is append-only and is appended, never rewritten

### Codex seat, v4: VETO (two wording contradictions; falsifiers 1, 2, 3, 5 NOT FOUND)

(1) The standard called `jev-plan/` "a local git repository" and then said the plan and runnable
root "belong to no repository"; (2) the packet said the receipt preserves the v1 reviews
"verbatim" while the receipt holds summaries ("verbatim in substance"). Confirmed: the operative
numbers reconcile (1,074 calls, 100 above 1,700, extrema 444 to 2,458, concurrency-8 latency
ranges); authority bounded (§§2.2-2.4); writer, status and digests agree across ACTION, header and
README bullet; pointers and rollback bounded. Required: distinguish the unversioned plan from the
standalone `jev-plan` repository; describe the review record accurately or append the full texts;
recompute and append digests. Optional: add the free-tier synthetic and smoke-report digests to the
receipt's evidence list.

### Claude Opus seat, v4: VETO (digests verified unchanged before and after; five precision defects)

Digests at start and end matched the packet's SUBJECT DIGESTS; the repository head advanced only by
the receipt append. Defects: (1) §5 Magic Lantern cited `CLAUDE.md:52,63-67` for "never into the
census, never cited as evidence", which those lines do not say (line 52 is the census catalogue
entry; 63-67 is Evidence-first); the bound is the standard's own proposal and the packet's EVIDENCE
claim was false for that cell; (2) §5 Cloudvore cited `operating-contract.md:162`, which is a
different proposition ("heuristic export detection or a heartbeat is never completion evidence");
the advisory rule is at :151; (3) §5 SBP said `UNKNOWN` "becomes" `REVIEW_REQUIRED` while
`AuthorityMatcher.cs:133` is a validator that throws; (4) §7.1's `concurrency` column has no
provenance in any report (`jev-validate.mjs:161`, CLI argument, default 4); (5) ACTION item 2
would publish unscreened review text ("both reviews verbatim") to a public repository against §4
and Law 4. Confirmed: all twelve report digests, every §7.1 and §7.2 figure, the extracts, the
`fleet-` filter, the sibling-surface listing, the Conjugal Law-4 screen (PASS), the byte cap
(11,374 + 210 = 11,584 of 12,000), the trailer, `PRIVACY.md:7`, Conjugal `CLAUDE.md:54,61-65`, ML
`CLAUDE.md:68-69`, `OracleService.cs:89`, `RULINGS.md:89-92`, kernel K2/K3/K9/K11, README bullet
form. Falsifiers 1, 3, 5 NOT FOUND; 2 and 4 FOUND as above. Optional (applied): "smallest calls";
"291 labelled rows"; writer named once in the bullet; a `receipts/` line in README Layout.

Verdict rule applied: packet v4 DECLINED (two vetoes).

## Round 5 (packet v5)

v5 applies every required and optional change from both v4 seats (listed in the packet's v5
paragraph). The verbatim seat reviews are committed in the local runnable root and never published;
their identities:

- `docs/review-codex.md` (Codex seat, packet v1 round 1): SHA-256 `138eb971a338a0ccc1b2b101379f5f327ab69810a8dd3172457463a81a4cb200`, 3086 bytes
- `docs/review-codex-r2.md` (Codex seat, packet v1 round 2): SHA-256 `6c19385c6d61fce4fa0f2483d92abe82c1b5d3128e80e096e0f031755b018ebc`, 3320 bytes
- `docs/review-codex-v2.md` (Codex seat, packet v2 round 1): SHA-256 `88983232252653a561496c02df2f019a1a0ec4a3251b72f5777894efc352305f`, 3733 bytes
- `docs/review-codex-v2r2.md` (Codex seat, packet v2 round 2): SHA-256 `8429370664117df54444422c7ab34c2793341a017e445c97f2142863195c70ca`, 3890 bytes
- `docs/review-codex-v3.md` (Codex seat, packet v3 round 1): SHA-256 `f27dafc29adaf3e10ed3688137755ee4419b768518e1e23692e4c9cb190304ce`, 3280 bytes
- `docs/review-codex-v3r2.md` (Codex seat, packet v3 round 2): SHA-256 `26c0c9b9d0c233f27174879aa0a8f6256413027c93ad26c1e2ec29c173ee27de`, 2692 bytes
- `docs/review-codex-v4.md` (Codex seat, packet v4): SHA-256 `fddf20270ffe93781b8e097829d407f6b84da5b238f7045ebd3612c3a0ed93f1`, 3650 bytes
- `docs/review-opus-v1.md` (Claude Opus seat, packet v1): SHA-256 `8affa3310082cfe2c6b1790fcf3889dc3ea3edb7343ec006ebb00356eaf8e8f1`, 8643 bytes
- `docs/review-opus-v2.md` (Claude Opus seat, packet v2): SHA-256 `1df257e15f9211917e5d2d35a8e8d807fad922e8ef1876a67d6d9b8b2222ddc9`, 9215 bytes
- `docs/review-opus-v3.md` (Claude Opus seat, packet v3): SHA-256 `9932085f1a23e80c3b96abadd6bca487fe59e1f11746d203e80b8b6f001283d5`, 9884 bytes
- `docs/review-opus-v4.md` (Claude Opus seat, packet v4): SHA-256 `62cb49008c3daa024a595a8f97b869f671a78b040088b46c2713ee934861ff2a`, 9188 bytes

v5 subject digests are appended below once frozen. Two fresh blind seats review v5; the author does
not edit the standard, the packet or this receipt while they read.

### v5 subject digests (frozen 2026-09-19)

- standard `docs/jev-shadow-mode.bus.md` SHA-256 `2cf662f3a21226fe31013cc5b3c9f11b35b13320ecf819f0b27c4df4a42e91df` (20876 bytes)
- packet `docs/ratify-packet-jev-shadow-mode.md` SHA-256 `08e2c5c1de4968a59fa4bdf62734715821dfae3d56ff87349f56a10ed09bdaf9` (13156 bytes)
- runnable root commit (local git repository `jev-plan`, no remote): `fc4e19d537e124601276c45ee07a1f2ffbebc527`
- both files are unchanged from these digests for the whole of the v5 review; this receipt is append-only

### Codex seat, v5: NO-VETO (bound to the v5 digest)

Falsifiers 1 to 5 NOT FOUND. Identity, status and writer agree across ACTION, header, README
bullet and receipt; authority bounded (§2, §5 including Conjugal's privacy gate and the fleet
queue prohibition); numbers reconcile (1,074 calls, 100 above 1,700, extrema 444 to 2,458,
concurrency-8 latency ranges; 27 + 111 = 138, 31 + 89 = 120, 47 + 291 = 338); no private
identifier; pointers assert no state; publication and reversal compatible. Optional: add the
synthetic free-tier and smoke-report digests to the receipt's evidence list (done below); name the
writer once in the README bullet (done in v6); say the Magic Lantern pointer records a proposal and
is not `ADOPT` (the standard's header already reserves `ADOPT` to the project's own surface).

### Claude Opus seat, v5: VETO (digests verified unchanged before and after; two sentences)

Confirmed: every §5 citation now says what the cell quotes (Cloudvore `:151-152` verbatim; Magic
Lantern `:52-53` and `:65-67` with the census bound correctly marked PROPOSED; SBP
`AuthorityMatcher.cs:133` a throw, `OracleService.cs:89`), the real Conjugal LAW4 tuple over the
Conjugal cell and pointer: 0 matches; byte cap 11,374 + 216 = 11,590 of 12,000; every §1, §7,
§7.1 and §7.2 figure reproduced from the reports; all twelve report digests and all eleven review
digests match; `jev-validate.mjs:161` confirms the concurrency convention; both subject digests
unchanged. Falsifiers 1, 2, 3, 5 NOT FOUND; 4 FOUND via one sentence: the SBP cell's claim that the
classifier "treats `wscript.exe` as non-console" has no basis in
`tools/classify-universal-authorities.ps1` (zero occurrences; console-capability is the task-id
allowlist at `:104`, wscript is non-console by omission; `AuthorityMatcher.cs:15` lists
`wscript.exe` only among attribution `GenericHosts`), so the cell offered a bound the project does
not hold (kernel K11). Second defect: §4 credited `mask-samples.py` with masking all nine classes
(`extractors/mask-samples.py:5-7` masks e-mail, user and machine names only; `screen-egress.py:7-17`
counts all nine) and stated no rule that a nonzero count blocks egress. Required: state the
allowlist and put launcher-host questions outside shadow mode; separate detection from masking and
make the count blocking. Optional (applied in v6): qualify the four bare commit tokens in the
round-1 summary; drop "append-only" from the README Layout line; `PRIVACY.md:7-8`;
`doctrine_outbox.py:68-83`; note that `receipts/` is not in `BUS_SURFACES`. The seat also listed
`docs/review-codex-v5.md` (SHA-256 `81ac2a370220914efda4a0970d47bb0e9c15cc0442018aaa3ce926b6c8f92346`,
2,638 bytes) as present on disk and not yet in this receipt, which is expected: reviews are
appended after each round.

Verdict rule applied to v5: one VETO, one revision permitted; the vetoing seat re-reviews the
revision. Because a verdict binds only a digest, a fresh Codex seat reviews the v6 digest as well.

Clarifications appended for the round-1 summary above (Law 6, "never the bare token"): the four
tokens `26da597`, `df93ff0`, `0e6ab0a`, `f920f4e` are commits of `softwarefactory-fleet-doctrine`
(the seam-detection set is that repository's own history). Evidence digests the earlier list
omitted: `reports/report-cv-c2-synthetic.json`
`231aae6795a65f0f14d1287537263952d842529120968270e6b99d619dccfca3` (not a source; free-tier run) and
`reports/smoke-report.json` `dc17526096a5eca537043f127b4be7a34ca84398140ca5ce40dd419fe744d890`
(harness self-test).

## Round 6 (packet v6)

v6 applies both required changes and every optional change from the v5 seats. The v5 Codex
review is `docs/review-codex-v5.md`, SHA-256 above; the v5 Opus review is
`docs/review-opus-v5.md`, digest recorded in the v6 block below. v6 subject digests are appended
below once frozen; the author does not edit the standard, the packet or this receipt while a seat
reads.

### v6 subject digests (frozen 2026-09-19)

- standard `docs/jev-shadow-mode.bus.md` SHA-256 `a92323318925982c9643b9b3bae7501db36058717fcc28cb6676725f7642528e` (21668 bytes)
- packet `docs/ratify-packet-jev-shadow-mode.md` SHA-256 `a193a926cfe9b7094c1620d3f28613cb2397eb3be5333a63061f444cb1dc64d0` (14675 bytes)
- v5 Opus review `docs/review-opus-v5.md` SHA-256 `6af853d51ddfe9af36e72be3bdc617042edf69f94c41994059ac17567fa32f40` (10296 bytes)
- runnable root commit (local git repository `jev-plan`, no remote): `01eb58c1044304493ad1cdc3a1138d48ab6c54ec`
- both files are unchanged from these digests for the whole of the v6 review; this receipt is append-only

## Adjudication (2026-09-19): RATIFIED for publication as CANDIDATE r6

- Codex seat, v6 (fresh, blind): NO-VETO, all five falsifiers NOT FOUND; review `docs/review-codex-v6.md` SHA-256 `2ce45fa618c9b8e3cbb4bb91e479ed8266ecc894d0e357fef20c661bc616b98d` (3051 bytes). Optional notes recorded, not applied to the frozen text: align the §6.2 description with the exact pointers (only the Cloudvore pointer names `tools/jev/`); say "ten reports included in the 1,074-call total" rather than "ten corpora".
- Claude Opus seat, v6 (the v5 vetoing seat, one permitted re-review): NO-VETO; both required changes MADE and verified against `tools/classify-universal-authorities.ps1:104` and `extractors/screen-egress.py` / `mask-samples.py`; all five optional items APPLIED; all five falsifiers NOT FOUND; digests unchanged before and after. One non-blocking note recorded: `screen-egress.py:32-37` applies the synthetic-sentinel exemption file-wide rather than per line; it cannot suppress the identity classes, so the privacy bound holds; a per-line tool fix follows outside this standard.
- Both verdicts bind the standard at SHA-256 `a92323318925982c9643b9b3bae7501db36058717fcc28cb6676725f7642528e` (21,668 bytes, LF line endings) and the packet at `a193a926cfe9b7094c1620d3f28613cb2397eb3be5333a63061f444cb1dc64d0`. Two NO-VETO on one digest: publish.
- Publication: `specs/fleet-jev-shadow-mode.md` is the standard byte-for-byte (its committed blob, LF-normalised, hashes to the digest above); this file becomes `receipts/fleet-jev-shadow-mode-ratification-2026-09-19.md`; the README bullet and Layout line are the texts in the packet. The publication commit id is appended below after the push. Zero runtime, adoption or launch authority is granted by any of this; each project records its own `ADOPT`.

- Publication commit on softwarefactory-fleet-doctrine master: `ad426fbec35c57df4bd599216309430ac0a25076` (pushed 2026-09-19). The committed blob of `specs/fleet-jev-shadow-mode.md` is the reviewed standard; verify with `git show ad426fbec35c57df4bd599216309430ac0a25076:specs/fleet-jev-shadow-mode.md | sha256sum` (LF bytes).

## Bus disposition (2026-09-19): DISTINGUISH, recorded here because the bus has no `specs/<self>.md`

softwarefactory-fleet-doctrine, as a consumer of the standard it hosts, records DISTINGUISH of
`specs/fleet-jev-shadow-mode.md` CANDIDATE r6 at bus `ad426fbec35c57df4bd599216309430ac0a25076`
(SHA-256 `a92323318925982c9643b9b3bae7501db36058717fcc28cb6676725f7642528e`). Not a ratification;
status stays CANDIDATE r6; no `RULINGS.md` entry; Cloudvore remains the standard's sole writer. This
receipt is the surface because the bus has no `specs/<project>.md` of its own and creating one would
register a fleet member (`tools/fleet-membership.mjs:14`) and break the sealed adoption census
(`tools/check_adoption_ledger.py:1317`, `PROJECT_CLOSED_SET_MISMATCH`).

Binding as written: §2, §3, §4. Distinguished, with the §5 bus row verified against the tree:

- The bus wires nothing itself. The row's hook point `cmdExportCheck` after `hits`
  (`tools/doctrine-sync.mjs:214-221`) executes inside a CONSUMING project's process; the repo is
  stdlib-only (no `package.json`, `node:*` imports only), so a Jev call there can only be the
  out-of-tree sidecar the standard describes, loaded lazily inside `cmdExportCheck` and never in
  `cmdCheck` (which Cloudvore's SessionStart runs with a 45 s child budget, Cloudvore `tools/gate.py:430`).
- FD-C2 has no comparator at that hook point: nothing in `doctrine-sync.mjs` reads `cos-feedback/`
  or parses `verdict:`; an FD-C2 shadow would be a separate reader, READ-only per
  `cos-feedback/README.md:64`, and it never touches a verdict (`SCHEMA.md:35`).
- Any sidecar failure must log `fallbackTaken` and never reach the top-level catch at
  `doctrine-sync.mjs:262-263`, which would turn a correct exit 0 or 1 into 2 for every caller; the
  `git log` invocation at `:218` stays untouched (a format change would alter `hits`); a fixture must
  prove export-check output and exit identical with the sidecar absent.
- FD-C1 stays disabled for private consumers: the state at that hook is the consumer's changed
  paths (`:218` runs `git log --pretty=format:` with `--name-only`, so no subject reaches it; a
  subject would need a separate read-only call), and Cloudvore and Conjugal must screen that state
  with their own scrubbers first (§4).
- No advisory promotion is possible on the bus: it has no bounded-authority register
  (`bounded-authority-register-r1` unratified), and §2.4 requires one.

Seats: three adversarial Claude Opus lanes (scope: DISTINGUISH; implementation skeptic: GATE-FIRST;
coordination: NEUTRAL), blind to each other, every load-bearing claim re-derived against the tree by
the integrator (the jev-plan session); this outgoing text falsified by a cross-family `codex exec`
seat (gpt-6-astra, read-only, sources inlined), sentinel and prompt digest recorded in the jev-plan
runnable root `docs/dispositions-2026-09-19.md`. Nothing on the bus acts on a Jev answer.
