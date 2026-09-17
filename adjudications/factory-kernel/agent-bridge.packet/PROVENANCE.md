# PROVENANCE - KR4-FILE-3 terminal filing candidate (CARD:KR4-FILE-3)

Author: one fresh Claude (Fable 5.1) subagent under hub session 8b82e3d8, 2026-09-17, the single TERMINAL round of card KR4-FILE-3 (successor of KR4-FILE-2 r2). Nothing pushed; no bus file changed; r2 untouched; outputs written only under `evidence/KR4-FILE-3-20260917/`.
Paths are relative to the agent-bridge project root or `<bus>` (softwarefactory-fleet-doctrine).

## Frozen bar and what this round did

The bar is `.claude-state/coordination/decisions/DECISION-KR4-LINEAGE-20260917-wfe74fd5a5.json` (sha256 B72B1BBE1E543A824D409DA393A4618D3593987725B20AABD61A0361BC78BCA7, 1739 bytes; the hub reported its first write failed and the file appeared after this author started, with the same items the dispatch prompt carried). Items (i)-(iii) are the three edits; (iv) is "every other byte identical to r2".

| bar item | r3 FILING.md edit | r2 line | r3 line | bytes r2 -> r3 |
|---|---|---|---|---|
| (i) | P:code acceptance-evidence REPLACES anchor widened to the whole acceptance-run clause of the code.md cell (ending "executed or authenticated"); the replacement repeats the clause with "commit" -> "subject identity (commit, or runtime manifest digest)" and appends the contract sentences after it, so the interpreter and TEMP/TMP qualifiers stay tied to the acceptance run | 59 | 59 | 969 -> 1203 |
| (i)+(ii) | P:code independent-key REPLACES anchor widened to the whole code.md cell; the replacement is that cell with "whose class has not become a producer of the subject" after "(R3)", so the CI-runner and attended-human alternatives stay in the eligible list; the material-contribution sentence ("A reviewer's class joins ... in any words; correcting ... does not") is removed from the REPLACES. The line stays FRICTION: its measured cost (the KR4-FILE park, one successor card, 0.52 USD) is unchanged and a REPLACES without the rule is still needed, so no reclassification under kernel section 4 | 61 | 61 | 749 -> 777 |
| (ii) | new bullet under ## Untested carrying the material-contribution question for the steward, PROOF: two profiles hitting the same independence exhaustion; N5 (r2 line 83) keeps its evidence unchanged | - | 88 (inserted) | 0 -> 244 (+1 LF) |
| (iii) | Authorship line rewritten: withdraws round 2's "a codex key covers all of it" by name; discloses that the Codex reviewers (SOL, ASTRA) materially contributed the designs at r2 lines 53-61 and 81-83 through the hub's defect list; states a Codex key covers the other lines and the accuracy of the disclosure (K11). The round-2 method sentence is shortened to a pointer to r2 PROVENANCE (its content is in this file's r2 hash table row) | 91 | 92 | 714 -> 442 |

Everything else is byte-identical to r2: `DIFF-vs-r2.patch` (6809 bytes, 27 lines, git diff --no-index, relative paths) has two hunks, three `-`/`+` line pairs and one `+` line, all inside the rows above. The r3 title line, the Scope paragraph's `packet = evidence/KR4-FILE-2-20260917/r2/packet/` address and N5's "Evidence, test, text: P:code independent-key" pointer are unchanged under (iv); the r3 packet is a byte-identical copy of that r2 packet (below), and the "test" now sits in the Untested bullet rather than in the independent-key REPLACES. That residual pointer is outside the bar and is reported to the hub, not edited.

## Byte cap: measured conflict with bar item (iv), reported, not resolved in-file

The dispatch prompt said "Keep the file under 16,384 bytes". r2 FILING.md is 16,351 bytes (33 bytes of headroom). Measured on the r3 text: line 59 +234 (the 117-byte retained suffix must appear in both anchor and replacement for the REPLACES to apply literally), line 61 +28, the Untested bullet +245, the Authorship line -272. r3 FILING.md is 16586 bytes, 202 over the cap. No wording satisfies both (iv) and the cap: the two anchor widenings alone cost +262 bytes against 33 of headroom before the two required additions, and the tightest honest Untested and Authorship texts were used (an earlier draft of the Authorship line at 547 bytes was cut to 442). Adjudicated by three adversarial Opus briefs (against-the-default, what-outranks, post-mortem): the frozen 3-of-3 quorum bar outranks a cap that appears in no ratified record and that this author may not verify (no repository search); trimming bytes outside the three edit areas would break (iv) and change the subject the quorum scoped; the overage is reported to the hub before review as the one out-of-bar item (a finding outside the bar opens a follow-up, not a block). The post-mortem brief's cheaper line-59 forms (quoting the suffix once with a notation) were rejected because the bar requires the anchor and replacement to apply literally.

## Clean-room method, stated as it happened

This author did NOT open: any file named `VERDICT-*`; anything under `evidence/KR4-FILE-20260917/` or the round-1 files of KR4-FILE-2; lane prompts, lane receipts, the live KERNEL.md, cards, scripts, `<bus>/RULINGS.md`; the r2 packet files other than through the byte-identical copy and their hashes (no packet file was read for content this round; the three edits need only r2 FILING.md, the bar and code.md). No repository-wide search was run; one `Select-String` over `<bus>/specs/fleet-factory-kernel.md` located the K6 cell and section 4, and one over that file for a byte cap found none. Three adversarial briefs were run as text-only subagents with no file access; their inputs were this author's measurements, not repository content.

## Files read (sha256 of the original at read time)

| sha256 | bytes | file |
|---|---|---|
| B72B1BBE1E543A824D409DA393A4618D3593987725B20AABD61A0361BC78BCA7 | 1739 | .claude-state/coordination/decisions/DECISION-KR4-LINEAGE-20260917-wfe74fd5a5.json (the frozen bar) |
| 3B3E1D31E7F41330E0A528C307B33DEE199821C46D38818234B066A84DBD6EEE | 16351 | evidence/KR4-FILE-2-20260917/r2/FILING.md (the subject edited) |
| A42FC5D2962D5143862C0A351298918AED081A4E38AF0510FE8498AAF4C62BF4 | 12640 | evidence/KR4-FILE-2-20260917/r2/PROVENANCE.md |
| 9FB490199624B8B39F710C59F594C83011CF7AD2A5972A6B1C68538F007DB411 | 245 | evidence/KR4-FILE-2-20260917/r2/SUBJECT-SUMS.txt |
| AE947E2954674BEDC0DB235532FE6CE3CE7F03F7E400AF114D4B31BFD46EB6A6 | 2859 | evidence/KR4-FILE-2-20260917/r2/packet/PACKET-SUMS.txt |
| 0370514FACF85974D74CEA521D589EB06C78F59DF3B3833CEC0BF4818CE9E7C0 | 4594 | <bus>/specs/fleet-factory-kernel/profiles/code.md (anchor target; same digest as r2 PROVENANCE) |
| 10589B79D96AA1EC15B4309DA1C9CB959286622EF988C4ACEEA1DEC92E42C2F3 | 19527 | <bus>/specs/fleet-factory-kernel.md (K6 cell, lines 85-87, and section 4, lines 151-186; same digest as r2 PROVENANCE) |

## Packet

`evidence/KR4-FILE-3-20260917/packet/`: the 28 hashed files plus PACKET-SUMS.txt copied forward from r2 byte-identical; every hash in PACKET-SUMS.txt re-verified on the copy (0 of 28 differ). PACKET-SUMS.txt sha256 AE947E2954674BEDC0DB235532FE6CE3CE7F03F7E400AF114D4B31BFD46EB6A6 (equal to r2).

## Anchor proof

`ANCHOR-PROOF.txt`: both widened anchors occur exactly once in code.md; literal String.Replace on a copy yields the two rows shown before and after; the environment qualifiers follow "and declared environment" on the acceptance-run sentence and the "replay agreement" clause follows the contract sentences (line 59); the CI-runner and attended-human alternatives follow the (R3) verifier and the rule text is absent (line 61); no other row of code.md changes.

## Subject sums

`SUBJECT-SUMS.txt` binds FILING.md, PROVENANCE.md and packet/PACKET-SUMS.txt (r2 format). FILING.md: LF only, no host paths, 16586 bytes.