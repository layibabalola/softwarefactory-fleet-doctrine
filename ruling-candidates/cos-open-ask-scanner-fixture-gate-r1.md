# CANDIDATE r1: open-ask scanners ship with fixtures and a hand-classified live run (zero runtime authority)

Status: PROPOSED 2026-10-17 by the Chief of Staff (record only; needs Layi's ruling and the authors' ACK).

## Evidence

- The CoS response-duty scanner (`tools/cos-open-asks.sh`, canonical on doctrine #87 head `e7481339`, copied
  into AdversarialLLM #277, Conjugal #6 and adobe-ingester #3) has shipped three rounds, each with selector
  defects found only by a CoS live run: r1 missed asks behind a 48h window and unlisted headers and counted
  `CoS-CONCERN:` answers as asks; r3 reports 14 of 15 already-answered MLV-App asks as OPEN, skips issue
  threads (AdversarialLLM issue #168 ask `6178913692`), and lets a `CLOSED:` line hide a new ask in the same
  comment (cos-feedback/adversarialllm/pr-277.md, cos-feedback/conjugal/pr-6.md).
- A false OPEN costs a factory a re-answer before other work; a false close lets a card merge with an ask open.

## Proposal

Any change to an open-ask scanner or its reply rule (doctrine #87 and every consumer copy) carries in its PR body:

1. A fixture file of comment bodies with expected classifications, at least: a legacy ask answered without an
   id, a review that closes one ask and raises another, a `CoS answer to CoS-CONCERN` reply, a `CoS-CONCERN:`
   comment, an issue-thread ask, a commit-comment ask, and an ACK with no dated ETA.
2. Its output on MLV-App and agent-bridge with every OPEN line hand-classified, and zero already-answered asks.

Consumers copy the scanner only from a doctrine-master commit that passed both checks.
