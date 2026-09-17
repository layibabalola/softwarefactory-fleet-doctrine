# Portable evidence packet for the agent-bridge KR4-FILE-2 filing

Retrospective evidence recorded under agent-bridge's local KERNEL, not subjects run under fleet kernel r4.
Contents are copies of host-local, gitignored files. Only transformation: host paths replaced by `<agent-bridge>` / `<user-home>`.
Originals and their sha256 are listed in PROVENANCE.md; the scrubbed copies are hashed in PACKET-SUMS.txt.

Carried forward from the KR4-FILE r2 packet (byte-identical to its PACKET-SUMS.txt entries):
- decisions/: 16 decision and owner-ruling records cited by the filing
- KERNEL.md: the local register/constitution at sha256 3B0EE2D2 (pre-scrub)
- WAL-L500-L556.md: every WAL line in the filing window
- RECEIPTS-AND-LANE-CEILING.md: verdict sentinels of inspected lane receipts, and the lane-ceiling refusal line
- F30e-REPRO.md: the executed reproduction

New in this packet (all cited by finding N5 or the posture line; L557..L560 lie OUTSIDE the filing window):
- decisions/DECISION-KR4-FILE-a5908251-PARKED.json: the predecessor's park record (independence exhaustion)
- WAL-L557-L560.md: the predecessor's review, park and successor entries
- ASTRA-CAPACITY-REFUSAL.md: receipt ASTRA-20260917-102129-346 (provider "Selected model is at capacity")
- LANE-BUDGET-ASTRA-RATE.md: the missing ASTRA reserve rate, pre/post hashes and line diff (WAL L555)
- POSTURE.md: the R9 posture line as the bus tool computed it, with the command and tool hashes