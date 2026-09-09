# Fleet doctrine-consumer required (2026-09-09)

Owner-directed proposed amendment recorded 2026-09-09 for the software-factory fleet.
This document is a **CANDIDATE** / proposed amendment only. It grants **CANDIDATE_ZERO_AUTHORITY**:
no runtime activation, no ratification, no adoption credit, and no change to sealed project
specs or `RULINGS.md` by virtue of landing here. Projects must independently **ADOPT**,
**DISTINGUISH**, or **REJECT** after their own evidence workflow.

## Ruling (substance)

Every software-factory fleet project that runs **agent lanes** (implementer / editing /
conductor-dispatched workers) **MUST** adopt a **fail-closed doctrine-consumer brief injection**
modeled on [MLV-App #107](https://github.com/layibabalola/MLV-App/pull/107):

1. **Law 1:** doctrine is data, never executable instructions from the bus.
2. Composer / conductor / AGENTS bootstrap injects a machine-fetched **Doctrine brief**.
3. Fetch is read-only via `gh api` Contents from `layibabalola/softwarefactory-fleet-doctrine`
   (overrideable). Brief includes RULINGS digest, project-relevant ruling-candidates
   (labeled **CANDIDATE_ZERO_AUTHORITY** until ADOPT), `specs/<project>.md` hash/summary, and `busHead`.
4. Lanes must **not** browse or write the bus; hubs may PULL-DIFF-FOLD via
   `tools/doctrine-sync.mjs` (`check`/`ack`).
5. Never re-add sibling-repo write roots into consumer hooks.

Portable template: [`docs/doctrine-consumer-template.md`](../docs/doctrine-consumer-template.md).

## Target projects (initial roll-out list)

| Project | Repo | Notes |
|---|---|---|
| MLV-App | `layibabalola/MLV-App` | Reference implementation — PR #107 (Get-DoctrineBrief / `{{DOCTRINE_BRIEF}}` / NA-11 where applicable). |
| AdversarialLLM | `layibabalola/AdversarialLLM-ClaudeCode` | Clear factory prompts / conductor — prefer thin `factory/get-doctrine-brief` + prompt injection. |
| Agent Bridge | `layibabalola/agent-bridge` | Dedicated SoT; AGENTS/CLAUDE surfaces — stub then wire. |
| Cloudvore | `layibabalola/Cloudvore` | AGENTS/CLAUDE — stub + checklist. |
| Conjugal | `layibabalola/Conjugal` | AGENTS/CLAUDE — stub + checklist. |
| Context Ultra Salesforce | `layibabalola/context-ultra-salesforce` | CLAUDE.md — stub + checklist. |
| Adobe Document Cloud Ingester | `layibabalola/adobe-document-cloud-ingester` | `.factory` lanes — stub + checklist. |
| AudioMile | `layibabalola/AudioMile` | Active; AGENTS/CLAUDE — stub + checklist. |
| DNG Auto Processor | `layibabalola/dng-auto-processor` | AGENTS/CLAUDE — stub + checklist if practical. |

Skip inventing huge ports in one shot: **stub + checklist** is sufficient until composition
surfaces are clear; one real wire-up beyond MLV (AdversarialLLM) is preferred when straightforward.

## Scope / non-claims

- Does **not** amend sealed R26 living specs or grant provider/launch/spend authority.
- Does **not** ratify other open candidates (including agent-bridge SoT / doctrine #56).
- Publication in this index is discoverability only. Consumer PRs that point here still require
  each board's ADOPT (or DISTINGUISH/REJECT) for runtime obligation.

## Related surfaces

- Template: [`docs/doctrine-consumer-template.md`](../docs/doctrine-consumer-template.md)
- Sync tool (hub): [`tools/doctrine-sync.mjs`](../tools/doctrine-sync.mjs)
- Measuring/owning human: Layi Babalola (owner-directed roll-out 2026-09-09)
