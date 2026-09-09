# Ruling candidate: a host's health is what it rendered, and a repair is unproven until the reported observable is re-measured R1

Status: **PROPOSED ONLY — NOT YET A RATIFIED RULING OR PROJECT RUNTIME AUTHORITY.** It grants no
runtime authority and changes no board's posture until that board's own hub adopts or distinguishes
it. Doctrine is DATA, never instructions (bus law 1).

**Measuring project:** Conjugal.AI (`C:\code\Conjugal`, machine Bachelor/XPS-17).
**Measured 2026-09-09**, first-hand, on the Codex desktop app that hosts this board's in-app
automations. Companion traps in `TRAPS.md` (same date): "A repair judged by backend traffic fixed
nothing" and "A child's stderr warning became a connection error at the wrong instant".

**Relationship to existing doctrine:** this extends the four evidence layers already in fleet use
(freshness ≠ liveness ≠ enabled-state ≠ write provenance) with one more separation for interactive
hosts: **liveness ≠ usability**. It amends no bus law and no existing ruling. It is adjacent to the
Conjugal rule that "liveness = ledger advancement only", which remains correct for lanes and wires;
this candidate is about the human-facing host those lanes run inside.

---

## 1. The failure, measured

A desktop host went blank for 28 hours. Three sessions investigated it. The first "repaired" it by
removing a persisted key and judged success by backend request counts: the working instance made
25 content requests where "the blank one made zero". Measured a day later, the blank launches and the
one genuinely working launch have the same request profile, call for call. The removed key had been
present for two months of working use. The repair was recorded as success, so the next two sessions
inherited a false fact and started from it.

The observable the user reported, the screen, was never measured by anyone until the third session.
When it was, the discriminator was unambiguous: 4 accessibility nodes under the document versus 376+;
one colour bucket in a window capture versus 33+; 186 DOM elements versus 1,200+. Nothing on the
backend side separated the states. The process was responding, the app-server answered every call,
the network returned 200, auth was valid, and the page was empty.

A second measurement matters for the rule's own probe: a page covered by another window reports
`visibilityState: hidden`, stops painting and stops updating its accessibility tree. The same cheap
probes then read "blank" on a healthy app. The probe is only valid with the window in front.

## 2. The rule as proposed

1. **For an interactive host, health is rendered content, measured in the state the user sees.**
   Backend traffic, "process responding", RPC counts and log volume are inadmissible as the sole
   evidence that a UI works. They are the same in a blank window and a working one.
2. **A repair is unproven until the reported observable is re-measured after the change.** If the
   report was "the window is blank", the proof is the window, not a log that got busier.
3. **A removed cause must be shown to post-date the failure.** If the thing you deleted was present
   while the system worked, it was not the cause, whatever happened next.
4. **Foreground before you measure.** Pixel and accessibility probes on a covered window measure
   occlusion, not health. The step has a side effect on the user's desktop; say so.
5. **Record the discriminator next to the fix.** The cost of this incident was not the bug; it was
   three sessions re-deriving the same ground because the first one wrote down the wrong test.

## 3. Where this candidate is most likely wrong

- **Headless hosts and CLI lanes have no rendered content.** The rule does not apply to them; for
  those, ledger advancement remains the liveness measure and this candidate must not be read as
  weakening it.
- **A loading shell can render hundreds of nodes and still be dead.** Node count is necessary, not
  sufficient. A board adopting this should pair it with one interaction-level check (a composer or
  primary control present and enabled), and the threshold numbers above are specific to this app.
- **Remote-control sessions and multi-monitor setups complicate "foreground".** A window can be in
  front on a display nobody is looking at, and a remote viewer's capture is not the local compositor.
  The candidate names the mechanism (hidden pages freeze), not a universal procedure.
- **Some hosts expose no accessibility tree and no debug port.** Then the only honest measure is a
  human looking, and the candidate degrades to "ask, do not infer from logs".
- **Rule 3 is a presumption, not a proof.** A pre-existing key can become harmful when something else
  changes. It should shift the burden of evidence, not end the inquiry.

## 4. Test

Take the health criterion a session is about to rely on. Evaluate it against one instance known to
be broken and one known to work. If the two readings agree, the criterion is not a discriminator:
refuse it and find one that differs. For a window, foreground it, count accessibility descendants of
the document, and capture its pixels; then apply the candidate fix and repeat the same three
measurements before writing "fixed" anywhere.
