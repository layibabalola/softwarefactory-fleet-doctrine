# Ruling candidate: tests fake failures by patching the call, look up environment values, and fail on the pre-change code R1

Status: **PROPOSED ONLY. NOT YET A RATIFIED RULING OR PROJECT RUNTIME AUTHORITY.** For Layi to rule on and for Dot (primary CoS seat) to review. It grants no runtime authority, is not a merge gate under R18, and changes no board's posture until Layi rules and each board's hub adopts or distinguishes it.

Who replies: **now**, Dot reviews this candidate on this PR with `ACK: <plan or ETA>` or `DISTINGUISH: <reason>`, and Layi rules. Factories and board hubs do not need to reply yet. **After Layi rules**, each board's hub adopts or distinguishes it, and each factory replies `ACK: <plan or ETA>` or `DISTINGUISH: <reason>` once the rule is adopted into its briefs.

Origin: advisory Claude and Codex reviews run by Iverson, relayed by Grok CoS at Layi's request on 2026-10-25 (about 12:30 AM CT). The review records are local, unpublished files on the shared agent machine, not GitHub comments:
- `/workspace/advisory-reviews/agent-bridge/pr-270-5db5a5ea.md` (layibabalola/agent-bridge #270 at `5db5a5ea6d950df2d4804e6a617f788217f6ceae`, about 11:30 PM CT Oct 24; both models raise the chmod fault injection as a shared Blocker).
- `/workspace/advisory-reviews/AdversarialLLM-ClaudeCode/pr-310-73c3fa08.md` (layibabalola/AdversarialLLM-ClaudeCode #310 at `73c3fa084bcc40637791ec47e990a54aaacfd95f`, about 12:15 AM CT Oct 25; the guessed 8.3 aliases are a shared Improvement, Codex says they can pass vacuously and Claude rates it a nit).
- Index: `/workspace/advisory-reviews/ledger.tsv`. The exact models behind those runs are unverified. Filed by Grok CoS as a coordination item under the 2026-10-24 7:13 AM CT ruling; no seat claim.

## Evidence

- Incident 1: layibabalola/agent-bridge #270 (`DASH-FG-STOPPED-TMP`), head `5db5a5ea6d950df2d4804e6a617f788217f6ceae`. The new tests force a write failure with `os.chmod(runtime_path, stat.S_IREAD)` and rely on the following rename then failing. On POSIX a rename onto a read-only file succeeds, so the failure branch never runs: on Linux T1 to T3 fail and T4 passes without exercising anything. CI is Windows-only, so it stayed green, and the PR merged at that head. Asks: Grok CoS comment `6393440232`, Dot comment `6393449551`.
- Incident 2: layibabalola/AdversarialLLM-ClaudeCode #310 (`CI-FAILURES-FIXTURE-SPLIT`), head `73c3fa084bcc40637791ec47e990a54aaacfd95f`. The 8.3 alias cases in `factory/ci-contract.test.mjs` hard-code guessed short names (`CI-CON~1`, `OUTSI~1`) instead of looking them up. `outside` is already a valid 8.3 name, so it normally has no separate short name, and `CI-CON~1` only exists where short-name generation is on and no sibling took that alias. The assertion accepts either outcome, so both cases pass whether or not the code under test handles aliases. Ask: Grok CoS comment `6393915848` (Grok CoS missed this on its first pass; the advisory reviews caught it).
- Related prior shape: `ci-matrix-covers-declared-runtime-floor-r1.md` (agent-bridge #233, three incidents of tests and product code that only held on the Windows CI host).

## The shape

A test proves a failure path or an environment-dependent path by changing real OS state (file modes, locks, short-name tables, locale, clocks) or by guessing an environment value, instead of controlling the one call under test. The test then depends on how one OS behaves, passes vacuously or fails on another runner, and nobody checks that it would have failed before the change it guards.

## Proposed doctrine text

1. **Fake failures at the call.** A test that needs an operation to fail makes that call fail directly, for example by patching `os.replace` or `Path.replace` to raise `PermissionError`, or by injecting a stub. It does not change file permissions, ownership, locks or other OS behavior to make the failure happen. A test that genuinely needs real OS behavior is gated to the platforms where that behavior holds, with a stated reason (for example `skipUnless(sys.platform == "win32", ...)`).
2. **Look up environment values.** A test reads environment-dependent values (8.3 short names, temp paths, home directories, path separators, drive letters, case rules) from the system at run time, for example `GetShortPathNameW` or `cmd /c dir /x` for short names. When the lookup returns nothing (for example 8.3 generation is disabled), the test skips with a visible reason. It never hard-codes a guessed value.
3. **Fail first.** Every new or changed test must fail on the pre-change code. The PR body records that RED run (command, base SHA, and the failing assertion), or states why the test cannot be red at base (for example a pure refactor guard).
4. **Assert one expected outcome.** A test asserts the specific result for its case, not "either A or B", unless it also checks which branch ran. This does not narrow rule 3 of `ci-matrix-covers-declared-runtime-floor-r1.md`: an outcome-class assertion is still allowed when the test is keyed to the runtime version or platform and the case states which class it expects there. What this rule forbids is a bare "either A or B" with no version key and no branch check, as in #310.

## How it would be checked

- **Builder self-review before open or push.** The builder reviews only the test changes once and answers three questions in the PR body: does each new test fail on the old code, does it run on any OS the repo supports, and does it rely on any guessed value.
- **Review legs.** Claude and Codex review legs and CoS reviews flag permission or OS-state fault injection, hard-coded environment values, either-or assertions, and a missing RED record as Improvements, or as Demonstrated defects when the test passes without exercising its claim.
- **Mechanical spot check (optional, per board).** A lint or grep over changed test files for `chmod` or `S_IREAD` used to cause failure, and for literal `~1` style short names, reported as advisory findings only.
- **Cross-OS run.** Where a board runs a Linux CI job (see the separate Layi-approved work order for agent-bridge and AdversarialLLM-ClaudeCode), non-portable tests show up there. That job is a `.github/**` change and needs Layi's normal Layi-Approval in each repo; this candidate does not authorize it.

## Out of scope

Review-leg counting, HIGH-RISK class rules, R18 and the R26 evidence workflow are unchanged. This does not ask any board to support a platform it does not already declare, and it does not change any CI workflow, ruleset or merge gate.

## Supersedes or touches

Touches `ci-matrix-covers-declared-runtime-floor-r1.md` rule 3 (behavior that differs by platform), and extends it from runtime versions to fault injection and environment values. Supersedes nothing.

## Close condition

Layi rules (ratify, amend or reject). If ratified, each board's hub adopts or distinguishes in writing, and the agent-bridge and AdversarialLLM-ClaudeCode factories ACK with a plan and ETA for the #270 and #310 tests.
