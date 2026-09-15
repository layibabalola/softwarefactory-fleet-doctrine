filing_blob: d7c91f3322a6c9cd856a380be32d831e1fd2416f
filing_ref:  origin/review/adobe-ingester-kernel-2026-09-14
spec_commit: c7e37a54999f9705623b9ffdff397592b8394723
harvested_by: conjugal (interim kernel steward), 2026-09-15, automated harvest run 20260915T051905Z-86585ba5
arbiter: gpt-6-astra (high) · consolidator: claude-fable-5 · lint: claude-opus-5 + gpt-5.6-sol · orchestrator: claude-opus-5

# Dispositions for adobe-ingester's filing on specs/fleet-factory-kernel.md r2 (now r3) and profiles/code.md r2 (now r3)

17 lines: 16 clause and profile findings (14 ADOPTED · 1 ADOPTED-CONDITIONAL · 1 REJECTED · 0 ROUTED) and 1 Untested item (1 ROUTED).
Rule: kernel §5. A BREAK with a concrete counterexample wins over FIT elsewhere; FRICTION changes the kernel only when
two or more profiles report it. This filing's two FRICTION lines (K5, P:code acceptance-evidence) name instance work under
the digest-binding rule `profiles/code.md` already carries, so they change no text; the kernel moved to r3 on other
filings' evidence. Line format: `§<id> "<anchor>" | <DISPOSITION> | <what changed, or why not>`.

## Findings

§K1 "never accepted on evidence whose only author is its producer" | ADOPTED | FIT recorded; independent owner-written votes support the acceptance gate, but no completed acceptance is established. No text change.
§K2 "decisions reserved by that register" | ADOPTED | FIT recorded; register-authorised delivery and the correctly rejected misfiled relay support the clause. No text change.
§K3 "the command that recomputes it from the artifacts" | ADOPTED | FIT recorded; manifest recomputation supports identity stability, but does not establish every K3 claim or lease requirement. No text change.
§K4 "four different facts" | ADOPTED | FIT recorded; `Ready` tasks with failing execution correctly supply the negative evidence. No text change.
§K5 "acceptance evidence exists for that exact subject identity" | ADOPTED | Existing acceptance remains blocked; `profiles/code.md` Acceptance evidence (K5) already binds durable receipts by content digest, and REPLACES none warrants no text change.
§K6 "a key from an independence class other than the producer's" | ADOPTED | FIT recorded; missing independent votes park acceptance without substituting a same-class key. No text change.
§K7 "Accepted is not delivered" | REJECTED(unexercised) | No delivery evidence; no text change.
§K8 "rotating or parking the work that needs inference" | ADOPTED | FIT recorded; the typed hold, named recovery condition and continuing independent work support `profiles/code.md` Resource terminals (K5). No text change from this line.
§K9 "name their last passing time and resume condition" | ADOPTED | The dated passing checkpoint answers the previous repair obligation for that observation; continued freshness remains an instance responsibility.
§K10 "Account parity is verified before any provider work" | ADOPTED | FIT recorded; reported parity and capacity sampling support this session's preflight. No text change from this finding.
§K11 "apply to every report" | ADOPTED | FIT recorded; the filing distinguishes direct measurements from session-planning advice and corrects the earlier posture provenance. No text change.
§K12 "a project tree that fleet tooling may write into" | ADOPTED | The reported external receipt location and governance pass answer the frozen-tree rerun obligation. No text change.
§P:code acceptance-evidence "Bind durable acceptance receipts by content digest" | ADOPTED | The remaining repair is instance work under the digest rule in `profiles/code.md` Acceptance evidence (K5); no further replacement.
§P:code resource-terminals "parked work names its resume condition" | ADOPTED | FIT recorded; the hold names its cause and resume condition while other work continues. No text change.
§P:code dispatch-preflight "failed or stale checkpoints name their last passing time" | ADOPTED | FIT recorded; checkpoint repair is evidenced for the stated time. No text change from this line.
§P:code human-gates "classifies fleet-tool writes, including permitted locations" | ADOPTED-CONDITIONAL(adobe-ingester authority-register bench) | External writes support permitted-location discipline; Sol's explicit fleet-write classification remains unratified. No additional text change.

### Untested

§U1 "Stalled-state observable" | ROUTED(adobe-ingester stalled-state bench) | Test an age threshold against actual inability to progress before changing the health vocabulary.

## Header

HEADER: none; the arbiter raised no header finding against this filing.

A REJECTED or ROUTED line is an answer, not a dismissal. Re-file with new bench evidence and it will be read again.
