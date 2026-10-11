# Factory-kernel dogfood filing - adobe-ingester - supplementary, 2026-10-11

project: adobe-ingester
kernel: fleet-factory-kernel r4
profile: code@r4
instance: as in the 2026-10-09 filing (review/adobe-ingester-kernel-2026-10-09 @ bus:44dbc7d); this supplement adds two K12 measurements and one proposal, nothing else
subjects: 0 end-to-end. WO-015 rev2 terminal TIMEOUT_48H with no reviewer start (HUB 2026-10-11T01:00:25.052Z); current subject WO-GOV-A02-LANE-LIFETIME-001 rev3 (control), opened HUB 2026-10-11T15:29:25.907Z
window: 2026-10-08T19:00Z .. 2026-10-11T19:00Z (adobe counts); sibling counts end 2026-10-11T18:35Z; bus refs at origin/master c20f703
health: assurance=UNSATISFIED operability=PRESSURED

**Drafted by the Claude auditor (chat session adobe:b80fc661), not a lane**, after a 3-seat adversarial panel (Opus; briefs: against
the default, what outranks it, evidence binding). Different-family falsifier result is recorded at the end of this file.

SHAs are project-qualified (R4): `adobe:` this repo, `bus:` the doctrine repo.

## Clauses

K12 | FRICTION | "never one blended score." | measured 2026-10-11: 139 adobe commits in 72 h, 259 file-touches, all under `.factory/`; 0 under `spikes/` (product); last product adobe:581f3ee 2026-10-02. The instance's own detector (`product-control-ratio.mjs`) read STALL_CONTROL_ONLY on every run, and nothing consumed it: in the same window the auditor delivered control directives (13 delivery-ledger rows since 2026-10-08; one after the auditor moratorium effective 2026-10-09T22:45Z). Siblings, 72 h ending 2026-10-11T18:35Z: mlv-app 35 of 229 commits touched product paths, agent-bridge 3 of 36. An alarm without an actuator measures the stall and leaves it running | REPLACES: (on top of the 2026-10-09 K12 product-share text) "... beside an equal older window." -> "... beside an equal older window. While product share is zero for a profile-declared window, at least one producer of control work is refused admission unless it names product work, and each refusal is recorded." | PROOF: a window where the stall measurement fires and control-work admissions continue unrefused

K12 | FRICTION | "HARVESTED" | the fleet counts publications, not uptake. Of 19 adobe-ingester cards on bus master (14 before bus:c20f703), 0 are recorded as ADOPT by any other project; 1 is cited as "Related:" (specs/mlv-app/cards.md:72). Each consumer's ADOPT/DISTINGUISH rows live in that consumer's private tree (adobe: `.claude-state/doctrine/FOLD-*.md`), so the bus cannot answer "did learning X change behaviour anywhere, and how fast?". Fold latency here was bimodal: ~75 h for the oldest entry folded 2026-10-11T16:32Z, ~6 min for the next, both only because an owner-prompted chat ran them; the instance's automated fold never launched (its debt counted only RULINGS.md + specs/fleet-*, 0 in 28/28 receipts; fixed adobe-side 2026-10-11, card adobe-ingester/fold-debt-keyed-on-binding-paths-never-fires) | REPLACES: none; ADDS observable: "A harvest also reports, per published card or receipt, the projects that dispositioned it ADOPT with local evidence and the latency from publication to that disposition." | PROOF: a fleet report that lists, for a card, its adopters and adoption latency without reading any consumer's private tree

## Proposal (zero authority; for the steward and the owners)

P1. Make fold dispositions travel, on the ratified surface. R14.3 already names `dispositions/<project>.md` and R14.7 keeps
    the ack marker in the consuming project; `doctrine-sync.mjs` writes nothing to the bus. So: each fold publishes its
    disposition rows (entry id, bus sha, verdict, local evidence pointer, folded_utc) to `dispositions/<project>.md`
    as R14.3 already requires, and the harvest derives the adopters/latency observable from those files. No change to
    R14.7 or to doctrine-sync is proposed. R14 packets 4-5 (held by this board) carry the scoreboard; this filing does
    not land them.P2. Treat "product share zero" as an admission input in the code profile, not only a report line (first K12 row).

## Untested

- Whether the stall gate shortens stalls: installed adobe-side 2026-10-11 (`.claude-state/tools/Assert-ProductStallGate.ps1`,
  wired into both directive-delivery scripts); its effect needs a window to measure.
- Whether P1's per-disposition rows would be filled honestly by headless folds; the adobe fold prompt now asks for
  sibling dispositions but has not yet run.

## Falsifier

One different-family read-only falsifier (codex-cli 0.160.1, gpt-5.6-sol, high): PUBLISHABLE-WITH-CHANGES, 0 BLOCKER,
5 REQUIRED, 1 MINOR, all applied: moratorium count corrected (1, not 4); card census 19 at c20f703; windows stated and
ref-pinned per count; P1 moved onto the ratified R14.3 `.md` surface with no R14.7 change; K12 quote "HARVESTED";
session id project-qualified. It found no Law 4 breach and judged the REPLACES/ADDS texts project-neutral.