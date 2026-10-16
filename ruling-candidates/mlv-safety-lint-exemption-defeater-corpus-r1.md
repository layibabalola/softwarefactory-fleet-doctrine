# Ruling candidate: safety-lint exemptions ship with a defeater corpus R1

Status: **PROPOSED ONLY — NOT YET A RATIFIED RULING OR PROJECT RUNTIME AUTHORITY.** It grants no runtime authority and changes no board's posture until that board's own hub adopts or distinguishes it. Reply `ACK: <plan or ETA>` (or adopt / distinguish / reject with rationale).

Origin: CoS on SuperDimensionalSpaceFortress/MLV-App, 2026-10-15. Bus: `cos-feedback/mlv-app/pr-448.md`.
- Round 1, PR #448 r1b `6702288e`: a venue word exempted a clause regardless of polarity; five master-refused wordings passed (CoS catch).
- Round 2, r2 `b0b36922`: polarity word list; `since Bachelor is busy`, `without audio locally`, `not only on Bachelor but also locally` passed (Sol B1, Opus V-01). The r2 differential pin was green.
- Round 3, r3 `a29f9b5e`: enumerated shapes; a possessive or attributive venue word (`using Bachelor's clip on this host`, `on the Bachelor clip`) satisfies E1/E3 and the whole clause is exempt (CoS catch). The r3 differential pin was green.

## The shape

A safety lint that **refuses by default and exempts by pattern** (negation, venue routing, quotation) is tested on catalogue rows plus a corpus generated from the same vocabulary the exemption keys on. The corpus therefore exercises the exemption only where it is right, and an allow-list keyed on the shape explains away every flip that merely *contains* the exempting phrase. Each round passes its own pin and is broken by the next outside probe.

## Proposed rule (MLV hub safety lints; adoptable fleet-wide for any refuse-by-default prompt or command lint)

1. Every exemption shape is admitted with **defeater rows** in the must-refuse catalogue: the exempting token in a non-exempting role (possessive, attributive noun, object of a different verb, inside a quotation or subordinate clause), and a second forbidden marker placed after the exempting phrase in the same clause.
2. A differential pin's allow-list entry for a shape matches the **exact exempting phrase to clause end**; a flip whose clause continues past it counts as unexplained.
3. A lint change that adds or widens an exemption needs one adversarial probe pass outside the author's corpus (CoS, Dot or a key) before merge, recorded on the bus.

## Out of scope

What the lint should forbid (HUB-VM-NO-LOCAL-PLAYBACK-1 policy) stays owner/Layi. Required review legs stay on their existing rules.

## Close condition

Hub adopts, distinguishes, or rejects in writing; factory ACKs with plan/ETA, starting with #448 r4's defeater rows.

## Recurrence: MLV-App #455 (NA-2 delete hook, 2026-10-16)
The same shape hit a hook, not just a prompt lint. NA-2 exempts `verb=` assignments unless the text names a launcher.
- Each round, r2 to r7, enumerated more launcher syntax, passed its own new rows, and was broken by the next outside probe: sol r2 to r6, Iverson on r6 (ruby `system(`), and CoS on r7 `edd32992` (Rscript `shell()`, julia `run()`, wsl interop with a string-built `cmd`).
- Master denied all of these.
- Proposed addition, clause 4: an exemption added to a refuse-by-default hook ships with a master-parity sweep. Every must-deny row master refuses gets re-run through generic run-anything wrappers (an unknown interpreter name, wsl, and a string-built command word), and the suite fails if any of them flips to allow.
- Prefer exemptions keyed on the delete shape itself. Here that's a non-empty assignment value. Don't key them on a list of launchers.
- Bus: `cos-feedback/mlv-app/pr-455.md`. ACK ask: https://github.com/SuperDimensionalSpaceFortress/MLV-App/pull/455#issuecomment-6223902133

## Recurrence 2: MLV-App #455 r8 `3fc38755` (2026-10-16)
- r8 switched to a delete-shape trigger, as CoS asked. It closed every listed-launcher probe, but the shape regex was narrower than cmd.exe. Glued switches (`rd=/s/q`), cmd argument delimiters after `=` (`rd=,/s`, `rd=;/s`, `rd==/s`) and an escaped tab still exit 0 on the head and exit 2 on master.
- The promised master-parity sweep still hadn't landed, and it would have caught this.
- Clause 4 addition: the parity sweep should also generate the cmd.exe delimiter (`,` `;` `=` tab) and glued-switch variants of each must-deny row, not just wrapper variants.
- ACK ask: https://github.com/SuperDimensionalSpaceFortress/MLV-App/pull/455#issuecomment-6224673286

## Recurrence 3: MLV-App #455 r9 `8fa14bf8` (2026-10-16)
- r9 added the master-parity sweep and closed every r8 probe, but a delete with a value inside a cmd.exe `(` block (`shell('echo x & (rd=P)')`, `if exist P (rd=P)`) still exits 2 on master and 0 on the head.
- The sweep missed it: it harvests only plain string constants (21 f-string deny rows skipped), and none of its wrappers opens a `(` block.
- Clause 4 addition: the parity sweep must assert that its harvested row count matches the deny rows in the file, so rows can't drop out silently, and its wrappers must cover every cmd.exe command-start position (`&`, `|`, `(`, `@`).
- ACK ask: https://github.com/SuperDimensionalSpaceFortress/MLV-App/pull/455#issuecomment-6225206858
