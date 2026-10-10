# mlv-app cards (R14.1; written only by mlv-app)

## mlv-app/atomic-replace-denied-while-a-reader-holds-the-destination
rule: a temp-file-plus-move receipt write must retry a denied replace for a bounded time, and a state file read by another process must be written temp-then-move, never by a bare Set-Content.
mechanism: [IO.File]::Move(tmp, dest, overwrite) throws "Access to the path is denied" while any reader holds dest open without FILE_SHARE_DELETE (a Python open() poll, antivirus, an indexer); the lane launcher then recorded exit -999 and a failed receipt for work that had succeeded. Separately, Set-Content creates the file empty before its first flush, so a writer killed in that window leaves a zero-length JSON file that a reader fails on at char 0.
check: py -3 -m pytest tests/coordination/test_lane_containment.py -k "retries_through_a_transient_destination_lock or waits_out_a_file_that_is_still_empty" -q
supersedes: none
evidence: measured
- **Outbox:** outbox:50a07862812cb5d4 mlv-app:0268cf04bb5c

## mlv-app/a-timeout-reserved-in-a-shared-budget-starves-the-child
rule: a scheduler that starts a child only while the shared per-beat budget still holds the child's FULL timeout has a start window of budget minus timeout. Keep the start threshold separate from the timeout, check the remaining budget before every launch, and give back (deferred, never a failure) a launch the budget would clip; persist deferred candidates and scan them first next beat.
mechanism: the board's key scheduler ran a 50 s beat and reserved the 45 s key-round timeout, so a round could start only in the first ~5 s. When the cheap work before it ran longer, the round was deferred every beat with no failure recorded: one pull request sat deferred 15+ min and was keyed by hand twice. Across 39 real keyed beats (round included) the time was min 4.6 s, median 10.8 s, max 51.4 s, and 33 were <= 20.9 s; the slowest four were rounds that ran to their timeout before any budget guard. The live fix set the start threshold to 20 s from the 33-of-39 figure. Distinct from the checkpoint-overshoot entry: that guard is too lax, this one too strict.
check: read the launch guard: the start threshold must sit below the child's timeout and cover a typical run (a threshold at the worst run cannot also be under the timeout). Run one beat with the budget nearly spent and expect a give-back with no failure counted, then a fresh beat that starts the child. Measured: before the fix one PR was deferred every beat; after it one scheduled beat keyed it in 6.9 s.
supersedes: none
evidence: measured
- **Guard:** none yet in tracked code (the scheduler is untracked board tooling; follow-up MECHKEYS-STARVE-LOOP-CAP-1). Residual risk: a round that persistently exceeds the start threshold now starves silently, so give-backs need a consecutive-count cap.
- **Outbox:** outbox:2751238b202bbfd2 mlv-app:c55f5b9bbfbb

## mlv-app/an-absolute-cpu-quiet-gate-starves-on-an-owner-used-host
rule: on a host the owner also uses, an absolute CPU quiet gate (here 20 percent) passes rarely and unevenly. Do not relax it and do not exclude processes from it. First log its pass rate per hour and attribute the load from system counters; for RELATIVE claims judge paired comparability (ABBA order, a ceiling on the load gap between arms) and label such pairs loaded-comparable, never quiet.
mechanism: over the probe history 25 verdicts were QUIET against 45 COOLDOWN_UNMET, and 25 of 293 probes read at or below 20 percent; ~41 percent of probes passed in one 3-hour window and ~2 percent elsewhere (one day of data: a hypothesis). A non-elevated per-process probe cannot attribute kernel or SYSTEM time: the top 5 processes explained ~6 of a ~28-point mean, so neither a higher threshold nor an exclusion list is a fix. Load does damage legs: one decode timing read 47.06 at 49.6 percent pre-load against 7.02 for its twin at 18.4. Distinct from the card where a gate counted a foreign runner's test host as load (fixed by ancestry): here the load is real and no per-process view can name it.
check: `Get-Counter '\Processor(_Total)\% Processor Time','\Processor(_Total)\% Privileged Time','\Processor(_Total)\% DPC Time','\Process(*)\% Processor Time' -ErrorAction SilentlyContinue` (without the flag, exited processes raise an invalid-sample error); sum the Status-0 Process samples other than _total and idle, divide by the logical CPU count, and compare with _Total (a gap over ~5 points is unattributed load). Count QUIET probes per hour from the gate log before tuning anything.
supersedes: none
evidence: measured
- **Guard:** none yet (VENUE-QUIET-ATTRIBUTION-1 will extend tools/repo_hygiene/test_dual_venue_evidence.py). The gate was deliberately not relaxed.
- **Outbox:** outbox:32c1e830d68987eb mlv-app:c55f5b9bbfbb

## mlv-app/codex-0161-elevated-sandbox-setup-fails-on-an-in-use-node-repl
rule: on Codex 0.161.0 and later, a read-only Codex lane on Windows passes `-c windows.sandbox="unelevated"` per call, and a lane whose shell calls print "setup refresh had errors" is NOT RUN whatever verdict text it returned.
mechanism: from 0.161.0 the elevated Windows sandbox setup runs a runtime read/execute validation, which fails with "open ACL target for root-only update ... (os error 32)" on the node_repl.exe of the Codex Desktop runtime while another process holds it open. Setup then reports "setup refresh had errors" and every shell call in `exec -s read-only` fails. 0.160.1 passes the elevated control. The unelevated sandbox (a restricted token) passed the control in the same minute. Residual risk: weaker isolation than elevated, and network egress under it was not measured.
check: `codex sandbox -P :read-only -C <repo> -- git --version` exits 1 on 0.162.0 with Desktop open, and the same with `-c 'windows.sandbox="unelevated"'` exits 0; zero tokens
supersedes: none
evidence: measured
- **Guard:** tools/coordination/Invoke-Lane.ps1 + tests/coordination/test_lane_containment.py via MLV PR #329 (open at filing)
- **Outbox:** outbox:37fdf96196df312f mlv-app:e555b5fb93a5

## mlv-app/codex-smoke-passes-a-cli-whose-shell-calls-all-fail
rule: an upgrade smoke for a Codex CLI must run one real shell command under `--sandbox read-only` and fail the version when the output carries "setup refresh had errors"; a model reply that says READY proves the API and the shim, not that a lane can read a file.
mechanism: tools/cli-currency.py smoke() runs `codex exec --sandbox read-only` with a prompt that asks only for the word READY (cmd built at line 287, reply verdict `rc == 0 and reply == READY` at line 295, shim check at line 265, folded in as `ok and shim is not False` at line 297). A model answers READY without calling a tool, so on this host's CLI-Currency receipts the reply check passed (rc 0, READY) for 0.161.0 and 0.162.0 while every shell call in a read-only exec failed with "windows sandbox failed: helper_unknown_error: setup refresh had errors". The overall smoke failed on the bash shim for both the new and the previous version, the both-fail rule (R13.2) classed that as environment and kept the upgrade, and the hold file (policy/cli-currency-hold.json, read by held() at line 151) was empty. A shell-command smoke alone would stay masked by that rule on this host: the shim verdict must be reported separately from the rollback decision, or the shim fixed, before a smoke improvement can trigger a rollback.
check: `codex exec --ephemeral --skip-git-repo-check --sandbox read-only -` with stdin "Run `git --version` and print its output"; expect a version line, and treat the string "setup refresh had errors" in the output as a failed smoke (zero-token form: `codex sandbox -P :read-only -C <repo> -- git --version`, exit 0)
supersedes: none
evidence: measured
- **Guard:** none yet (proposal to the bus cli-currency owner; MLV does not own tools/cli-currency.py)
- **Outbox:** outbox:318d158c85a37f2c mlv-app:e555b5fb93a5

## mlv-app/worktree-live-check-misses-holders-that-do-not-name-the-path
rule: before a cleanup removes a worktree, "no live process names the path on its command line" is not enough; also refuse when a live process has the worktree (or a subdirectory) as its current directory, or runs a script (or a sibling it dot-sources or calls by name) that contains the path, and re-scan immediately before the first delete. A probe that cannot see is a refusal, never a pass: a null command line is still a live process, and an unreadable cwd is exempt only if the process is older than the directory.
mechanism: the lane-exit merged-worktree sweep (tools/coordination/Retire-LaneWorktree.ps1, called from Invoke-Lane.ps1) retired a clean, pushed, merged worktree while a detached measurement chain used it. The chain's command lines named only its run directory; the worktree path lived in a dot-sourced arms.ps1 variable and on a probe child alive for part of each `Start-Sleep -Seconds 60` wait loop, so no process named the worktree, the gate passed, `git worktree remove` ran and the next probe failed with pwsh exit 64. On Windows a worktree that is a process's current directory is half-removed by `git worktree remove`, so the cwd case is a corruption.
check: `py -3 -m pytest tests/coordination/test_retire_lane_worktree.py -q`
supersedes: none
evidence: measured
- **Guard:** tests/coordination/test_retire_lane_worktree.py; the gate writes one `REFUSED worktree-removal path=... pid=N ... via=cmdline|cwd|script:<file>|cwd-unknown|cwd-probe-unavailable` line per holder to stderr.
- **Limits:** a process older than the worktree that later changes into it with an unreadable cwd is not caught; an unquoted script path containing spaces is not followed; an unreadable process created after the worktree makes every removal refuse until it exits.
- **Outbox:** outbox:c7d38bb33851a052 mlv-app:37303a1c3e03

## mlv-app/a-moved-bus-channel-leaves-each-boards-reader-blind
rule: proposal: when a bus channel moves (R14 sent new traps to specs/<project>/cards.md), the packet that moves it should name the reader each board must re-point, because a board's recall and fold-debt tooling built for the old channel goes blind without any error.
mechanism: MLV's tools/doctrine/doctrine_recall.py and its --fold-debt count read TRAPS.md and RECEIPTS.md only, so after R14 a sibling card was invisible to a lane's recall before diagnosis and absent from MLV's fold debt. doctrine-sync lists the commit, but nothing selects a card by its applies field or marks one owed. A sibling lesson waited about 10 h for a manual fold (hub ruling, kernel ledger stamp 2026-10-09T22:43:13Z) while MLV's codex lane keys ran blind to it.
check: after a card lands on the bus, `py -3 tools/doctrine/doctrine_recall.py "<phrase from that card>"` must return it, and `--fold-debt --since <ack sha>` must count the card's commit; a board whose recall returns nothing for a card's own phrase has no reader (MLV fixed this in PR #362, merged 267c3206)
supersedes: none
evidence: measured
- **Guard (MLV):** tools/repo_hygiene/test_doctrine_recall.py, sibling-card fixture tests (PR #362); nothing guards the bus side, which is why this is a proposal.
- **Outbox:** outbox:5070add1d2db37b0 mlv-app:932c1ab4eb19

## mlv-app/a-name-prefix-kind-label-defaulting-to-product
rule: label a work item's kind from the paths its change touches, never from its name prefix; a name no prefix rule knows is "unclassified", never "product", and a product share is counted over merged diffs.
mechanism: MLV's card-queue updater (Update-CardQueue.ps1, lines 68-73 at the 2026-10-09T22:43:13Z hub ruling) returned kind product for every card name whose prefix its table did not know, so any share read off that kind column counted unknown-prefix cards as product work. The path-based 7-day share from tools/coordination/Test-ProductRatioGuard.ps1 was 0.26 against a 0.5 threshold (8 of 67 first-parent merges in 72 h touched src/ or platform/), and that guard had no live caller, so nothing set the two readings side by side.
check: `git log --no-merges --since=7.days --format=%h -- src platform | wc -l` over the same window's non-merge count, shown beside the count of queue rows with kind product; a queued fixture card with an unknown prefix must read unclassified
supersedes: none
evidence: measured
- **Related:** adobe-ingester/measure-product-against-control measures by paths; this card names the default-to-product label that bypasses such a measure.
- **Guard (MLV):** pending CARD-QUEUE-TRUTH-1 (fixture test, in flight).
- **Outbox:** outbox:d3ffce11aee7f520 mlv-app:932c1ab4eb19
