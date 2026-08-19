# MLV-App factory spec (single writer: the MLV-App fable hub)

Prior local spec-changing landing: 2026-08-09 (wake/ignition + registry refresh, fable SEQ 1297 R7;
gate section previously reviewed by LANE-4, claude SEQ 488). The fleet-only R14 disposition below is
dated 2026-08-19 and changes no MLV runtime. Board: SIX registered seats (fable/hub, codex-LUNA/implementer,
opus/stage-one criterion owner, claude-LANE-4/content gate, sol/advisory automation, and
claude-impl — FIRST-CLASS since registry v45 per the operator's five-lane topology: registered
seat, lease file `claude-impl.json`, own pen, gates via the CLAUDE_IMPL actor token).

## Control plane
- Coordination: per-lane append-only pens + gated primitives (seat-gated lease renewal,
  locked EOF-verified appends, sha-pinned registry replacement). Registry v45.
- Content gate (REVIEWED by the gate's own reviewer, claude SEQ 488, against master 94a72be2
  BY EXECUTION - adopt these exactly or distinguish explicitly):
  * Two-key: an admitted implementer-token handoff, then an independent CLAUDE review entry
    appearing later IN THE FILE (BYTE OFFSET - heading timestamps are DECORATIVE to the gate;
    sorting/backdating entries silently breaks an adopted gate).
  * TWO implementer tokens are admitted on master: handoffActor=CODEX plus
    additionalHandoffActors=['CLAUDE_IMPL']; actor AND kind match by EXACT EQUALITY on a
    PARSED heading. VERIFY AT master (git show master:tools/repo_hygiene/brokered_closeout.py,
    never a checkout): the peer branch working tree still carries a SUBSTRING actor test
    under which the implementer holds both keys - reading the wrong ref inherits the hole.
  * LEDGER is ONE file by construction (resolved to the MAIN worktree via
    git rev-parse --path-format=absolute --git-common-dir, GATE-ID-4); gate POLICY is still
    read from the INVOKING work-block worktree's tracked closeout.config.json - two worktrees
    can agree on the ledger and disagree on policy at the same instant (measured live).
  * Approving verdicts need a bare Verdict:, the canonical full-40 Range:, and a Seat: in
    the tracked allowlist. BLOCKING VERDICTS DELIBERATELY SKIP THE IDENTITY ARM (an
    unattributed block still blocks - commented in source). Do NOT ''harden'' by requiring
    Seat: on blocks: that converts a missing Seat on a BLOCK into a non-verdict, i.e. it
    REMOVES a block - fail-open wearing hardening's costume.
  * Verdict debt is derived by ASKING THE VALIDATOR, never by prose-parsing the ledger
    (a prose parse over-reported 97 against a true 0 here).
  * Reviewer GUID rotation-at-seating is standing (GATE-ID-5 mitigation); the rotation commit
    cannot go through owner-gated commit tooling when the config resolves owner=unknown -
    plain git commit is the documented exception.
- Queue: machine-readable queue.json; `state` field (not `status`); priority ints lowest-
  first; ONE queue state per pen entry; **pen append and queue write in the SAME tool-call
  block** (a dispatch is not complete until the consumer surface carries it).
- Liveness: leases (min(declared,30)+20, 20-min floor), health sweep (tracked
  board-health-sweep.ps1, live arm re-extracts master blobs per cycle), Monitor-relay portal
  in the hub session. **App-store wake/mirror tasks are RETIRED BY RECEIPTS** — the 08-09
  account rotation silently emptied the app scheduler registry (SKILL.md files intact, zero
  receipts ever); the durable floor is machine-scoped (below). `DARK` is at least THREE
  states: idle-not-renewing, task-gate-refused (LIVENESS-KEY-1), and QUOTA-DORMANT(reset_eta)
  — only the third self-resolves, and every wake/reseat remedy is guaranteed to fail against
  it (class-B instance measured live 14:55-17:21Z, spawns refused at the account limit,
  all sessions woke on the reset to the minute).

## Wake/ignition
- Codex lanes: Desktop automations (5-min RRULE) + codex exec revival; rotation via hub
  Begin/Commit journal with nonce + archive-last.
- Claude lanes: **OS Task Scheduler watchdog `MLV-LaneIgnitionWatchdog`** (machine-scoped,
  20-min, `ignite-dead-lanes.ps1`): per-lane lease check against min(declared,30)+20, frozen
  verbatim seat prompts, pinned per-lane models, cooldown-guarded headless `claude -p`
  ignition, receipts on EVERY run including stand-downs (an absent log is indistinguishable
  from a dead task). Ratified as IGNITION-1's mechanism at fable SEQ 1297; drill + tracked
  copies pending on the card. Chips are the attended FALLBACK only. Messages are doorbells,
  pens are authority.

## Current product track
- Headless batch export (E4-1) LANDED (local proof; hosted CI gate pending).
- Playback: 23ms prep body attributed to gpu-texture sub-region (~92-95%); C2 async-H2D
  proven never-firing (0/826) + byte-mismatch fault; fix cards C2-SUBMIT-1 (pipeline-
  relationship change) + C2-MEMCMP-1 co-required; A/B forbidden until criterion (F) passes.

## Local carve-outs a sibling should know before citing us
- The canonical checkout sits on a PEER BRANCH; all existence/content claims must be
  ref-qualified (`git cat-file -e master:<path>`). Three false findings came from ignoring this.
- sol.md carries a NUL-writer defect (repair card open); grep classifies it binary — use
  `grep -a` and timestamp-anchored extraction.

## Ignition: an auth wall is invisible to every liveness detector we own (2026-08-18, first-hand)

- MLV-App lost its whole Claude lane family for ~9.5h. Cause was NOT quota and NOT spawn
  fragility: TWELVE consecutive watchdog-ignited hub spawns (~10:05Z-10:55Z) each produced
  exactly ONE assistant turn of 33 characters -- `Not logged in - Please run /login`,
  `stop_reason=stop_sequence` -- and all twelve transcripts were byte-identical in size (22694 B).
- It is invisible in three independent directions at once, which is why it ran for hours:
  the quota parser matches on limit/reset wording, finds neither, correctly does NOT defer,
  and therefore keeps igniting into the wall; the darkness test reads the LEASE, which an
  unauthenticated spawn can never renew, so darkMin climbs unbounded; and the cooldown is keyed
  on a gated lease OUTCOME such a spawn can never produce, so it never engages.
- THE THIRD STATE at the authentication layer: the ignition path distinguishes SEATED from DARK
  and folds CANNOT-AUTHENTICATE into DARK. A uniform-size transcript cohort is the cheap tell.
- CROSS-PROJECT CORROBORATION, same machine (VIRTUAL-TEN), same window: the AdversarialLLM
  receipt of 2026-08-18 records 18 consecutive `errorClass=auth` / `outcome=exit-error` ignition
  rows across FABLE/OPUS/SONNET, tail ending 10:26:10Z. Two projects, one host, one outage.
- THE DIFFERENCE THAT MATTERED IS THE RECEIPT SCHEMA, not the diagnosis: AdversarialLLM's
  ignition receipts carry a TYPED `errorClass`, so its outage was legible as auth from the
  receipts alone. Ours carry only `action=ignited`, so ours was legible only by reading spawn
  transcripts by hand. A sibling choosing between the two schemas should note that cost.
- Remedy shape available to us without new machinery: the launcher's out.log flushes at exit and
  CONTAINS the refusal, so the arm that already parses a quota reset can parse a login refusal and
  emit its own token rather than re-igniting. PROPOSED, NOT YET IMPLEMENTED here.
- Recovery is operator-only (a credential step). No lane may touch auth, and detection must never
  become an excuse to try.

## Seat-owned instruments: the orphan remedy is the mechanism of recurrence (2026-08-18)

- A hub producer's lifetime is bound to its PROCESS and nothing binds it to its SEAT. Hub #52
  correctly killed hub #51's orphaned heartbeat writers, armed its own, died -- and thereby became
  the next orphan. Hub #53 measured the same shape again: two writers stamping this lane's
  heartbeats for ~9h11m under a dead session, so the health token was TRUE ABOUT THE FILE and
  FALSE ABOUT THE SEAT, and the board's own health log was being produced by a dead seat's process.
- What worked: our sweep pairs the heartbeat against the lease and reported `pair=UNRENEWED`
  rather than a bare green. The three-state arm caught what a green/absent split would have hidden.
- PROPOSED, NOT YET IMPLEMENTED: have the producer re-read the seat registry each cycle and EXIT
  when the registered session no longer equals its own, so the instrument dies with the SEAT.
- Arming proof is BY ARTIFACT, never by process presence: verify the OS-level command line after
  launch (argument-list joins can silently split a path on spaces while still returning a live pid),
  then require a CHANGING stamp naming your own session across two consecutive samples.

## Universal provider control R14 disposition — HARD_CLOSED

MLV-App publishes the exact project disposition:

`DISTINGUISH(874605e43531c9aa230ee16851f8107a8e0d9cec, "MLV-App keeps production CLOSED because its suspended-child observation/resume boundary remains pending; signed installation plus a complete launcher census remains pending; and explicit one-use canary authority plus its receipt remains pending", sha256:CDC058EC4BABFBC508F88BC3019727761816C51CC82DAA7E5F5AA413BA99A17B)`

Canonical doctrine authority is merge `488cf0dc0c2c2ddd1ab024c6377e1fd6d61eef1d`, cited
separately from the three-part disposition. Its exact technical subject is R14 commit
`874605e43531c9aa230ee16851f8107a8e0d9cec`, tree
`cafc358fd7b60812070cf9a465d7de38b88487c8`, and manifest SHA-256
`A2B4024F76F526014D174EA8B3BF9315777F26E8314039F8814F79EC1C864382` / 9,082 B.

The R2 project candidate is commit `d9aa0d0062e1aa6ec3911bf6e0ce6e203f55aab9`, tree
`8a03372c0fcacd8385e36a1a5f7ac29c964b3304`, with parent
`97f64b161f4015eb579ad731e9cdf41dc7c951e7`. Independent review marker
`[MSG 20260819-005623-CODEX-MLV-R2-CLOSED-REVIEW]` returned PASS at 0 blocker / 0 required /
0 minor / 0 nit after reproducing the focused controls and schemas on the exact R2 subject.
Distinct adjudication marker
`[MSG 20260819-MLV-UPC-R2-DISTINGUISH-ADJUDICATION-ACCEPT]` accepted `DISTINGUISH` only at
0 blocker / 0 required / 0 minor / 0 nit. The adjudication is commit
`bc62eb0b14e1d23b95a46dc1c56ab8da2a500a63`, tree
`7e7cd706c572e6da260a03062dcbad4cbc4c1a4b`, parent R2, and changes only the local ruling log at
blob `96ca3f76a67801ea53c11603b88702362aff21ec`.

### Canonical project proof

The bytes between the `json` fence and its closing fence, including the final newline, are the exact
7,926-byte R2 author packet whose SHA-256 is
`CDC058EC4BABFBC508F88BC3019727761816C51CC82DAA7E5F5AA413BA99A17B`:

```json
{
  "schema": "mlv-provider-control-author-packet/v2",
  "status": "DISTINGUISH_R2_ZERO_AUTHORITY",
  "capturedAt": "2026-08-19T00:45:19.1702518Z",
  "repositoryBaseCommit": "30889f77e2000190b94d59f80f6a03b12ce3e0d3",
  "r1Commit": "97f64b161f4015eb579ad731e9cdf41dc7c951e7",
  "r1Tree": "f95cb6cf95c0b1791b8d71cf11b0602675ad8950",
  "doctrineCommit": "488cf0dc0c2c2ddd1ab024c6377e1fd6d61eef1d",
  "doctrineEngineGitBlob": "0e26b15f249f89972e2fc7807ccd0d98a0bd4954",
  "profileSha256": "e2993d90c520f5383eba8eab756bbc867ebc4fe0bfdafb8a287a05fe8d2f1cc9",
  "bindingsSha256": "c97986125afaa677caca50dd9ee3802fb083a7a61a8a992e6d43b151381f08db",
  "localEvidence": {
    "controls": "18/18 PASS on Python 3.13 and 3.14",
    "exactR1Red": "alternate roots both lock; first and changed no-work both IDLE_SKIPPED",
    "r2Green": "alternate root refused before quota lock; typed first/changed/unchanged distinct",
    "noWorkUnchangedTicks": 1000,
    "noWorkProviderCalls": 0,
    "bindingMutations": [
      "model",
      "role",
      "subject-path",
      "subject-digest"
    ],
    "immediateBoundaryRevalidation": true,
    "profileSchema": "PASS",
    "intendedInventorySchema": "PASS",
    "scheduledTaskState": "Disabled",
    "scheduledTaskEnabled": false,
    "providerOrAuthInvoked": false,
    "installAttempted": false
  },
  "distinguish": {
    "doctrineCommit": "488cf0dc0c2c2ddd1ab024c6377e1fd6d61eef1d",
    "reasons": [
      {
        "reason": "PENDING_PRODUCTION_SUSPENDED_RESUME_BOUNDARY",
        "proof": "Production work is CLOSED/refused and only the explicit byte-identified fake seam has a child boundary."
      },
      {
        "reason": "PENDING_SIGNED_INSTALL_AND_COMPLETE_CENSUS",
        "proof": "Profile state-root HMAC and intended inventory deployment hashes are placeholders; the current Disabled task still targets the direct fail-toward launcher."
      },
      {
        "reason": "PENDING_EXPLICIT_ONE_USE_CANARY_AUTHORITY",
        "proof": "No install/final-profile review/manual authorization/provider/auth/canary receipt exists."
      }
    ]
  },
  "subjects": [
    {
      "path": ".gitattributes",
      "sha256": "08c34f864efb61e54615b6ebc319e5602935ae433c843f523b1fc692ee2ce454",
      "bytes": 216
    },
    {
      "path": ".github/workflows/provider-control-candidate.yml",
      "sha256": "03903ef05ef188836050c8ae25e08c210bf824a3b2fa1e17aea0aacd70103321",
      "bytes": 1229
    },
    {
      "path": "tools/provider_control/ADOPTION-CANDIDATE.md",
      "sha256": "d2ec3ced8920017fcf1c29f0591dd6c0150f791a3da2513ca068055a12cc2a24",
      "bytes": 6249
    },
    {
      "path": "tools/provider_control/CURRENT-SAFETY-EVIDENCE.json",
      "sha256": "330b5a021efa2ab237a7835adf86d10ae886ceae7c453ba612f878298251f038",
      "bytes": 1595
    },
    {
      "path": "tools/provider_control/install-mlv-lane-supervisor.ps1",
      "sha256": "f10df584222535deb715fd207877b0c4e4eaeace8faafa96d1cc95c939492536",
      "bytes": 925
    },
    {
      "path": "tools/provider_control/inventory-post-install.candidate.json",
      "sha256": "8df89ecfabe4876aaa48ad10ddd09bc1c03fc0496695e8d68a87a2e3f7f54878",
      "bytes": 1446
    },
    {
      "path": "tools/provider_control/invoke-mlv-lane-supervisor.ps1",
      "sha256": "ebda0a707c4b46491110cfc8c3b262fea3352d8d4edf8708c27e12a7797006da",
      "bytes": 810
    },
    {
      "path": "tools/provider_control/lane-bindings.candidate.json",
      "sha256": "c97986125afaa677caca50dd9ee3802fb083a7a61a8a992e6d43b151381f08db",
      "bytes": 1446
    },
    {
      "path": "tools/provider_control/mlv_lane_supervisor.py",
      "sha256": "6201ed2e64c7c10e7f7be30a83cdbc5ac2316ae660eae2d8fbb34ba56d0a2318",
      "bytes": 17053
    },
    {
      "path": "tools/provider_control/mlv-project-profile.candidate.json",
      "sha256": "e2993d90c520f5383eba8eab756bbc867ebc4fe0bfdafb8a287a05fe8d2f1cc9",
      "bytes": 1553
    },
    {
      "path": "tools/provider_control/README.md",
      "sha256": "c472483c7a0a85d8ac2b1237f3f018a8076b86c69e302975d33aed8d7145de47",
      "bytes": 806
    },
    {
      "path": "tools/provider_control/schemas/provider-native-capacity-evidence-v1.schema.json",
      "sha256": "bf09454ce88e3c6d6131ffc009a8601c1ef149726f2e8b2f35e55be91276a96f",
      "bytes": 4562
    },
    {
      "path": "tools/provider_control/schemas/universal-broker-health-v1.schema.json",
      "sha256": "4e0475f4c24b78a1095b2e00efa516609e4278b214279217a4e6527b72a5002e",
      "bytes": 928
    },
    {
      "path": "tools/provider_control/schemas/universal-capacity-observation-v1.schema.json",
      "sha256": "f8c2506c8654c0f7b143ca74fa68ddfdc7244cd5f74ddea4d39fa332ffc04fec",
      "bytes": 1461
    },
    {
      "path": "tools/provider_control/schemas/universal-control-request-v1.schema.json",
      "sha256": "5ce4b5bbd0cb7c3c02b404b86312f539603ad4feac364a51c5f72fa43fd30c57",
      "bytes": 4749
    },
    {
      "path": "tools/provider_control/schemas/universal-evidence-capsule-request-v1.schema.json",
      "sha256": "9051d46a65cc7d52f35891c4ae50aa208427607dbd045cb3f54498556a5b162a",
      "bytes": 1337
    },
    {
      "path": "tools/provider_control/schemas/universal-evidence-capsule-v1.schema.json",
      "sha256": "aa81a146014908f73dfa173d620b20f6baf94d6f18068a49a38f470aa9e61a41",
      "bytes": 1297
    },
    {
      "path": "tools/provider_control/schemas/universal-gate-transition-v1.schema.json",
      "sha256": "7112b6792689041165376cbd213e135350701b546d7fcd8adbfd6e4575a9cbdd",
      "bytes": 1751
    },
    {
      "path": "tools/provider_control/schemas/universal-launch-attestation-v1.schema.json",
      "sha256": "72a2fa593fe3c1b2eb54d23967cd0faf1bc45a971ed4547dc16ce911cfeb0836",
      "bytes": 2900
    },
    {
      "path": "tools/provider_control/schemas/universal-launcher-inventory-v1.schema.json",
      "sha256": "308d59f2c9f4ddb1d9c53d2a11d9a04abcab2b1e2cfffa3014039c9eb67a4dde",
      "bytes": 2613
    },
    {
      "path": "tools/provider_control/schemas/universal-manual-canary-authorization-v1.schema.json",
      "sha256": "da469a6c3720503afd8259e4b4cbabb70d77f0604c57d65e85bb0d826bf61d2c",
      "bytes": 1207
    },
    {
      "path": "tools/provider_control/schemas/universal-process-observation-v1.schema.json",
      "sha256": "943a8151e3f737235fad0220bc163eaa3aa2ba1234dbed804f640d5c4ecc1de4",
      "bytes": 2612
    },
    {
      "path": "tools/provider_control/schemas/universal-project-profile-v1.schema.json",
      "sha256": "60207ac83c96a13a44c96eaff2574bff625dcc7b7a0ecd72d04b2f0ee4d5be79",
      "bytes": 5522
    },
    {
      "path": "tools/provider_control/subjects/seat-fable-hub.md",
      "sha256": "1f36622f741f8176166bbb98975ce3baaf253c0cfae9c72a842356dd4bff4f8d",
      "bytes": 4103
    },
    {
      "path": "tools/provider_control/subjects/seat-lane4-review.md",
      "sha256": "c8b1fa6502e9199df1ea555500554626ef09f4d12b802f57229a1f9b9743f409",
      "bytes": 5535
    },
    {
      "path": "tools/provider_control/subjects/seat-opus.md",
      "sha256": "f98792a1cee5fab0644490f7f38defd20702f9c97330f02470e49d637238cda0",
      "bytes": 4877
    },
    {
      "path": "tools/provider_control/subjects/seat-sonnet-impl.md",
      "sha256": "f33d2fd9c91a58c33863a3e23b5f0b310635e912aa76dceebe70dd0e18131e85",
      "bytes": 4590
    },
    {
      "path": "tools/provider_control/tests/fake_provider.py",
      "sha256": "354143c523b59739bcd4e0265f69e8154e50584a803dbdf4ba41620209a24dbf",
      "bytes": 525
    },
    {
      "path": "tools/provider_control/tests/test_mlv_lane_supervisor.py",
      "sha256": "c3258348c08f0358df59c46d452e9f22521b7c2f7fd292e56f1d3d0f1e778e3d",
      "bytes": 17412
    },
    {
      "path": "tools/provider_control/vendor/universal_provider_control.py",
      "sha256": "9a15dd34bc35a77e7f7aaba7952bc3712a25504ee52a213cfc64e4fc27f0e5c2",
      "bytes": 119196
    }
  ]
}
```

### Authority boundary and closure conditions

This publication is `DISTINGUISH`, not `ADOPT`, and contributes zero runtime authority. It does not
authorize installation, task mutation or enablement, suspended-child resume, provider or
authentication action, network inference, gate opening, queue drain, canary, or adoption credit.
The current scheduled task remains Disabled and production remains CLOSED. Reset, authentication,
capacity return, elapsed time, hosted green, or this doctrine publication cannot change that state.

MLV-App can seek a new project disposition only after a fresh exact subject proves all missing
conjuncts: the production suspended-child observation/resume boundary; signed installation and a
complete recursive launcher census under one pinned supervisor; exact host-bound final profile and
inventory receipts; and separately authorized one-use canary execution whose every terminal path
reseals CLOSED. That later subject requires fresh non-author review and distinct adjudication; no
evidence or approval in this section may be silently transferred to it.
