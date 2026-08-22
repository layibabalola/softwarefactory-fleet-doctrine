# R26 owner-publication requests — Phase 7

This directory contains four immutable request-only packets for the projects that remain `STALE`:
Adobe Ingester, Agent Bridge, AirMyPC, and Conjugal. Each packet is a zero-authority description of
the evidence its project owner must publish before the fleet can evaluate a current R26 disposition.
It is not a disposition, work order, review assignment, message, runtime instruction, installation
permit, or adoption claim.

All packets bind exact canonical doctrine base
`e4e7f9363185a5e10bb3a92167c785ef29caf2b7`, R26 candidate
`e70a044f31dd2f43ab7c716d63a4eb89318c61b6`, and merge
`909f769d02e8412e51e28e242cfa8d00dadc9a3d`. They require an owner-published repository root,
normalized remote, current ref/commit/tree/parents, historical-object lineage witness, explicit
`ADOPT`, `DISTINGUISH`, or `REJECT` choice, exact Git-blob artifact manifest, and evidence for the
model, effort, role, review, quality, and functionality axes. An `ADOPT` publication additionally
owes every runtime and installation proof named in the packet; missing evidence cannot pass.

Adobe's packet preserves its last pinned remote observation as stale discovery only. It separately
requires an active lawful work order and fresh reviewer-bearing Q-021 quorum. The fleet request
cannot create either one. Agent Bridge has no authoritative root or remote. AirMyPC's published
`C:\temp\AirMyPC` root is absent. Conjugal's published `C:\code\Conjugal` root is on Bachelor and
the doctrine-lineage candidate object is not current project-HEAD evidence. No related name or
historical object may fill those gaps.

Project owners do not edit these requests into dispositions. They publish a new project-owned,
content-addressed response whose fields satisfy the applicable request. Fleet reconciliation then
verifies that response independently before changing any ledger row.

Run the closed-set controls with:

```console
python -m unittest discover -s tests -p "test_phase7_owner_publication_requests.py" -v
python tools/check_phase7_owner_publication_requests.py --treeish HEAD
python tools/check_adoption_ledger.py --treeish HEAD
```

The checker also proves that the canonical ledger, Phase 2 and Phase 5 evidence, and all four
project specs remain exact. Phase 7 has no remote, message, provider, runtime, scheduler, gate,
installation, repository-mutation, or adoption authority.
