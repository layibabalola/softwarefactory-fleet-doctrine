# OPUS receipt — I8 R1 repair: 8.3/long-path identity in the drill harness

**Lane:** `opus` (hosted seat `1d57e7a1-1830-497a-bea2-dfc20cd82778`, guarded dispatch per `SOL-CLAUDE-OUTAGE-DEGRADED-MODE-RULING-20260809.md`)
**Date:** 2026-08-09
**Verdict consumed:** `evidence/SOL-VERDICT-I8-R1-REVISE-83-PATH-IDENTITY-20260808.md`, 2,826 B / `8D6F7DC612926EA79F520736E0F825F195D0C8D7428F6BE5F219AAB45FA0C9DE` — size+SHA verified at read time before acting.

## Tuple (route candidate)

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `coordination/tools/ignition-launcher-check.ps1` (ENGINE, **byte-unchanged**) | 20,259 | `7FF44298E84CA10DFF4AAAF13530ABAE91EF0307FA2C21301D9EEC4AF1B7A85D` |
| `coordination/tools/test-ignition-refusal-drill.ps1` (HARNESS, revised) | 33,943 | `DDBD73280BDE38FB7C8883FC9DE79433A354908617CEA97FC28AC5B6BDBE88C7` |

Prior harness identity superseded: 27,404 B / `0616271E5B58D5A374B50033A07AAF4F27C34DD276C130AECF9037B12466E70F`.

## Repair, clause by clause against the narrow return

1. **Engine bytes unchanged** — re-hashed identical before and after every run (table above).
2. **One filesystem identity before relativization.** `Get-TreeDigest` now canonicalizes the root AND every enumerated child through Win32 `GetLongPathNameW` (`Get-CanonicalPath`, fail-closed on API failure), then performs a guarded `StartsWith` + `Substring(rootCanon.Length+1)`; a child not under the canonical root is a thrown harness error, never a silent mis-relativization. No raw string-length subtraction across potentially aliased spellings remains on any verdict path. No caller-forced long root is required or used.
3. **Both-host 8.3-root control** — `control-83-alias-root`, one row per host, three stages:
   - SETUP PRECONDITION: `GetShortPathNameW(scratch)` must differ from `GetLongPathNameW(scratch)` (case-insensitive), AND enumeration from the short-spelled sandbox must return spellings that do not start with the short root verbatim — otherwise SETUP-FAILED (a red row), never a pass. Proven satisfiable here: `C:\Users\OBABAL~1\...` vs `C:\Users\obabalola\...`.
   - RED: `Get-TreeDigestNaive` — a source-derived verbatim copy of the pre-repair derivation — run over a short-root sandbox around a real engine invocation of the `toctou-immune-allow` arm with `Excl=prompt.txt` must report the measured false-red (digest delta despite the exclusion). Reproduced on both hosts, both outers.
   - GREEN: the repaired `Get-TreeDigest` over the same sandbox holds digest-equal and the engine exits ALLOW.
4. **Everything preserved.** All prior 28 rows/host intact: 3 positive, 12 refusal rows over exactly the 11 distinct I8 arm tokens, 2 recovery, 11 load-bearing mutants with setup preconditions. Census asserted per host (now 29 rows/host including the control), filtered runs still non-certifying, zero-write assertions and zero scratch residue verified by re-listing.
5. **Runs executed (all exit 0):**
   - Full suite, default scratch root, outer pwsh 7: 58/58 OK, census both hosts, SCRATCH CLEAN, CONTROL SET GREEN.
   - Full suite, default scratch root, outer Windows PowerShell 5.1: 58/58 OK, same terminal set.
   - Targeted TOCTOU (`toctou-immune-allow`, `arm-capture-toctou`, `mutant-capture-toctou`) from short root `C:\Users\OBABAL~1\AppData\Local\Temp`: 6/6 both hosts, under BOTH outers.
   - Full suite from the short root, outer pwsh 7 AND outer 5.1: 58/58 each, census both hosts, SCRATCH CLEAN, CONTROL SET GREEN.

## Hygiene

Harness re-measured pure ASCII (0 bytes >127 or forbidden controls), uniform LF (556 LF / 0 CRLF, matching the prior revision's convention — no mixed EOL introduced).

## Boundaries held

Drill only. No production launcher, no ignition of any lane, production autonomous ignition remains HOLD. No product bytes under `DngAutoProcessor\`; no writes to other lanes' leases or inboxes; no merges. Writes this seat made: its own lease (claim/renew via `claim-lane.ps1`/`post-entry.ps1`), its own beats, hub entries, the harness file, this receipt, and session-scratchpad temporaries.

## What remains, with whom

- Corrected-path refalsification of this exact tuple — OWNER: luna.
- Exact-package ruling — OWNER: sol.
