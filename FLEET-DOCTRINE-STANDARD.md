# FLEET COMMONS — git-as-bus doctrine exchange (replaces the USER as store-and-forward)

**USER directive 2026-08-08:** the factories must self-improve without improvements being stuck in
one project; siblings get parity — automatically, not via daily hand-carried packets.

## The design, derived from the fleet's own laws

- **Git is the bus.** One shared repo (`softwarefactory-fleet-doctrine`), one directory per project. Cross-machine
  parity comes from an ordinary private remote; every carrier property the fleet already trusts —
  append-only history, byte identity, diffs, pull-based reads — comes free. (A sync folder like
  Dropbox was considered and rejected: no history, no merge semantics, silent conflict files —
  exactly the un-receipted mutation class our standards exist to kill.)
- **Export is a side effect of landing, never a snapshot ceremony.** A daily generated .md is a
  hand-maintained summary — the class the bootstrap protocol says rots. Instead: when a project
  lands a fleet-relevant standard, drill receipt, or incident postmortem (its own state-currency /
  chronicle-as-you-go moment), its coordinator commits the artifact here in the same turn. No
  landing ⇒ no commit ⇒ nothing to read. Event-driven by construction.
- **Import is a wake duty.** Each coordinator's wake includes `git pull` + a delta scan of the other
  projects' directories (cheap: `git log --since` + changed paths). Adoption stays a per-project
  judgment — **adopt-or-distinguish, never auto-apply**: a sibling's law is evidence, not authority,
  and each hub rules its own adoption (several projects have local carve-outs a blind sync would
  trample — exposure rules, sandbox bans, pinned-hash control planes).
- **What travels:** standards/doctrine (whole files, byte-anchored) · drill receipts · incident
  postmortems · install traps. **What never travels:** product code, reviewer reasoning, transcripts,
  anything a blind-review carve-out covers, secrets/auth. One-way-glass and independence laws are
  unaffected — doctrine is not reviewer exposure.

## Layout

```
softwarefactory-fleet-doctrine/
  softwarefactory-fleet-doctrine-STANDARD.md      (this file)
  <project-slug>/
    EXPORTS.md                   (index: artifact → size/SHA → one-line hook; newest first)
    standards/…  receipts/…  incidents/…   (the artifacts, committed on landing)
```

## Per-project duties (three lines to adopt)

1. On landing a fleet-relevant artifact: copy it into your directory here + one EXPORTS.md line +
   commit/push, same turn.
2. On wake: pull; scan siblings' deltas; adopt-or-distinguish with a one-line record in your own hub.
3. Never edit another project's directory. Commits are receipts; force-push is forbidden.
