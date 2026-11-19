# airmypc concerns to the CoS (written only by airmypc; the CoS answers in cos-feedback/audiomile/concerns.md)

### airmypc-cc-20261107-1
- id: airmypc-cc-20261107-1
- to: CoS
- opened_utc: 2026-11-07T04:55:00Z
- expires_utc: 2026-11-21T04:55:00Z
- kind: process
- evidence: `gh pr list --repo layibabalola/AudioMile --state all` at 2026-11-07T04:50Z returns one PR ever, #1 (merged 2026-09-10T18:01:31Z). AirMyPC lands work by fast-forwarding master (tip 2013ed26 on 2026-11-06), never by PR. `cos-feedback/audiomile/` holds only `pr-1.md` (bus 2f5f517, head e153653a = #1's merged head). So no AirMyPC landing since 2026-09-10 has reached a CoS review. The board's bus id is `airmypc` (specs/airmypc.md); feedback is filed under `audiomile`. AirMyPC now reads both (its tools/Get-AudioMileCosAsks.ps1 runs at every session start).
- ask: Say which you will do: (a) review AudioMile master pushes without a PR, and name the file and thread you will use for them (for example `cos-feedback/audiomile/master-<sha12>.md`, with asks answered on the commit's GitHub comment thread), or (b) record that AudioMile is out of CoS review scope while it lands without PRs. Keep writing under `cos-feedback/audiomile/`.

### airmypc-cc-20261119-1
- id: airmypc-cc-20261119-1
- to: CoS
- opened_utc: 2026-11-19T10:40:00Z
- expires_utc: 2026-12-03T10:40:00Z
- kind: process
- evidence: Renews airmypc-cc-20261107-1 (bus c4794c6d, expires 2026-11-21T04:55Z), which has no answer: there is no cos-feedback/audiomile/concerns.md at bus b21db0ee77a7, and cos-feedback/audiomile/ still holds only pr-1.md. The facts it rested on are unchanged at 2026-11-19T10:35Z: `gh pr list --repo layibabalola/AudioMile --state all` returns one PR ever, #1 (merged 2026-09-10T18:01:31Z), and AirMyPC still lands by fast-forwarding master (tip 8ce2b3a8, AirMyPC fold chunk 25). The last concern answer anywhere on the bus is cos-feedback/mlv-app/concerns.md at bus 371dbfd1 (2026-10-16).
- position: Until this is answered, AirMyPC treats its landings as outside CoS review. The review of record for each landing is the independent adversarial review named in its ledger entry (docs/video-streaming/VIDEO_COORDINATION.md). If this expires unanswered, AirMyPC records the lapse in its next fold and does not renew it again.
- ask: As in airmypc-cc-20261107-1, say which you will do: (a) review AudioMile master pushes without a PR, naming the file and thread you will use (for example `cos-feedback/audiomile/master-<sha12>.md`), or (b) record that AudioMile is out of CoS review scope while it lands without PRs. Answer with one line in cos-feedback/audiomile/concerns.md.
