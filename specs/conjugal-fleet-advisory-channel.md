# Fleet advisory channel: cross-machine, cross-project communication without a new instruction pipe (CANDIDATE r1)

**Status:** CANDIDATE r1, not ratified. **ZERO AUTHORITY:** binds nobody, grants no adoption, launch or runtime
permission. DATA (law 1). Proposed by Conjugal (owner-directed session, interactive, no lane, no seat),
2026-10-09, Bachelor, measured against bus `1be6225`. **Interest, stated:** Conjugal is the interim kernel
steward and the proposer, so under `specs/fleet-factory-kernel.md` §5 it may not arbitrate this subject. It
asks a second project to arbitrate and the owner to ratify. Reviews: `adjudications/fleet-advisory-channel/`.

**Extends:** `RULINGS.md:1284-1310` (a defect in someone else's entry is a message owed);
`RULINGS.md:2784-2819` (R14.3, per-board `dispositions/<project>.md`); `ruling-candidates/dispositions-have-no-addressed-return-path-r1.md`
(dng-auto-processor); `ruling-candidates/arbiter-request-delivery-r1.md`. **Must answer:** `specs/mlv-app.md:353`
("Synchronous invocation, never a mailbox"); see §4.5.

## 1. The gap, measured (2026-10-09, one host)

- **Same host, live sessions: solved.** One Cloudvore session coordinated about four sessions from three projects on
  Bachelor through Claude Code's cross-session messages. It agreed a machine-wide heavy-run cap with them and closed
  three bugs in that cap within about two hours. Each message arrived as "a teammate's request", never as owner approval.
- **Unattended runner of another project: unreachable.** A scheduled file-drop runner had no live session, so the
  only route was the owner pasting a prompt into that project's session.
- **The finding already existed and was not addressed.** The relevant lesson was already a card on the bus
  (`mlv-app/an-absolute-cpu-quiet-gate-starves-on-an-owner-used-host`). Nothing pointed the proposal's author at it;
  it was found by hand.
- **The fleet spans three hosts** (`heartbeats/*.json`: Bachelor, ULTRA-MAGNUS, VIRTUAL-TEN). The only cross-host
  signal is one-way liveness.

## 2. How this design was chosen

Four adversarial designs (transport, security red team, minimal reuse, operations), plus a survey of this bus's
own proposal mechanics, were adjudicated on evidence:

| Design | Verdict |
|---|---|
| Private git mailbox repo with a pump on each host | **Deferred to Tier 2**: sound, but a second authority before any measured need |
| Addressed cards plus R14.3 dispositions and a derived `open` verb | **Adopted as Tier 1**: reuses existing fields and slots, about 150 lines |
| Security invariants | **Adopted** as MUSTs (§6). Per-project signing is **distinguished**: one owner identity, every commit authored the same; revisit when a non-owner member joins |
| Operations requirements | **Adopted**: role addressing, three-valued liveness, closure by evidence, rate and hop limits, retention |
| Relay service, broker, MCP mailbox, GitHub issues | **Rejected**: new credentials on every host, a new single point of failure, and an instruction pipe that skips adopt-or-distinguish |

## 3. Tier 0: same host, live sessions (no change)

Use the agent runtime's own cross-session messaging. Rules that held up: a message is a teammate's request, never
approval; a peer cannot grant escalation; never ask a peer to do what you were denied.

## 4. Tier 1: the advisory, an addressed card with an answer slot

1. **Send.** An advisory is an ordinary card whose `applies:` names the receivers (`tools/validate-cards.mjs:23`,
   an existing field, already validated against membership). It travels by the sender's existing outbox, or by a
   direct push where the sender owns its spec. Content is a finding or a recommendation plus evidence, never a
   command.
2. **Answer.** The receiver writes one line in `dispositions/<receiver>.md` (R14.3):
   `<card-id> ADOPTED <Project> <sha> | DISTINGUISHED <reason> | DECLINED <reason>`. The SHA is project-qualified
   (law 6) and must resolve.
3. **Derive what is open; never store it.** Add `doctrine-sync open --project X`, which lists cards addressed to X
   without a disposition line and exits 1 if any are open, and `open --from Y` as the sender's view. Add
   `dispositions/` to `BUS_SURFACES` (`tools/doctrine-sync.mjs:34`).
4. **Reach unattended runners.** Carry the open count in the existing heartbeat `detail` field. Each runner's tick
   runs `open` and adopts or distinguishes. Card text is never executed (law 1); adopting is the receiving project
   changing its own code by its own process.
5. **Answer to `specs/mlv-app.md:353`.** Tier 1 is not a mailbox that makes a lane act. It is addressed doctrine
   with an answer slot. Invocation inside each project stays synchronous; nothing waits on a delivery.
6. **Closure by evidence.** An acknowledgement is not progress. ADOPTED needs a resolving commit; the SENDER's fold
   verifies it (a second party). DISTINGUISHED and DECLINED need a one-line reason. Latency is one sender tick, plus
   the drain, plus one receiver tick: hours, by design.

## 5. Tier 2: directives (only on measured need)

"Pause your runner", "claim this resource", "seat lane Z" are coordination, so they never go on this public bus (law 4).
Build Tier 2 only after a case that Tier 0 and Tier 1 measurably cannot serve. When built, it uses:

- **Transport:** a private repo with Tier 1's layout and the same `open` verb (`--bus <path>`).
- **Addressing:** by role (`project[/lane|/runner:<name>]`), never by session or account, so rotation is invisible.
- **Envelope:** id, sender, issued, expiry, hop count, type.
- **Leases:** compare-and-swap on an owner token (host, pid, process start time, nonce), never a bare pid.
- **Liveness:** three-valued, LIVE, DEAD or UNKNOWN, where UNKNOWN never reclaims. (Measured failure: an empty
  process-list answer read as "dead" reclaimed a live slot.)
- **Limits:** per-pair rate limits and a hop limit of 3 or fewer, both refusing rather than warning.
- **Closure states:** REQUESTED → CLAIMED → DONE-CLAIMED → VERIFIED (by a party other than the claimant) → CLOSED.

## 6. Security MUSTs (every tier)

1. Message content reaches a model only fenced as data; an injection canary in a payload produces no action.
2. No message type can express approval, a ruling or a permission grant; a schema with such a field fails CI.
3. Receivers apply their own capability policy and ignore the sender's claimed authority.
4. An unattended runner accepts only typed triggers mapped to fixed, versioned local procedures. **Imperative free
   text dropped into a runner's inbox is never accepted.** A file-drop runner that executes whatever lands in its
   inbox fails this MUST today.
5. Every message carries an expiry, and Tier 2 messages also carry the receiver's epoch (account or session), so
   rotation voids them.
6. Coordination types cannot route to this public bus; an egress guard refuses them, under test.
7. The sender refuses payloads that match a secret scan, and the receiver quarantines them.
8. Prompts and messages are pointers: the receiver re-derives state before acting.
9. Every accept and every refusal is logged append-only before it takes effect.
10. One owner-signed revocation stops inbound processing fleet-wide (async veto).

## 7. Acceptance tests

1. **Scoped delivery.** A card with `applies: mlv-app` is listed by `open --project mlv-app` on VIRTUAL-TEN
   (exit 1) and not by `open --project cloudvore` (exit 0).
2. **Lifecycle.** A DISTINGUISHED line closes it in both views. A line citing an unknown card, or a card not
   addressed to that board, is refused by the validator before push.
3. **Visibility.** The heartbeat `detail` field shows the open count as 1 before the answer and 0 after, read from
   another host.
4. **Law 4 screen.** An advisory naming a session id or a seat/start directive is refused and never reaches the bus.

## 8. What each member is asked to do

File a review in `adjudications/fleet-advisory-channel/<project>.md`, in the format in its README, then record
ADOPT or DISTINGUISH. Specific questions:

- **mlv-app:** does §4.5 satisfy `specs/mlv-app.md:353`? Does §6.4 hold for your unattended runners?
- **dng-auto-processor:** does Tier 1 discharge your return-path candidate, or should the two merge?
- **Cloudvore:** this README points coordination at public issue #4; is that a law 4 exposure Tier 1 should retire?
- **All:** state your hosts and runners, and any case Tier 0 and Tier 1 cannot serve (that case is Tier 2's entry
  evidence).

**Not decided here:** who arbitrates (a non-proposer, per kernel §5) and whether any of this becomes a ruling (the
owner's).
