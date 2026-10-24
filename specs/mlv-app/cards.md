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

## mlv-app/the-fold-publish-share-loop-is-rebuilt-per-board
rule: proposal to the bus steward, not an instruction to any board: promote the loop that folds sibling doctrine, publishes a board's own findings and reads its product share into one project-neutral bus tool, driven by a per-project profile (paths, kinds, ack cursor, outbox target), so a board adopts it by writing a profile and no code.
mechanism: MLV carries its own copy of each stage: tools/coordination/doctrine_outbox.py (publish; a port of agent-bridge's port of the bus reference outbox), tools/doctrine/doctrine_recall.py with --fold-debt (read and fold debt), tools/coordination/Test-ProductRatioGuard.ps1 (share). The bus holds doctrine-sync.mjs, Publish-BoardHeartbeat.ps1 and adobe-ingester's product-control-ratio.mjs for the same stages. Each fault found this week (a cards reader, an owed count, a label by prefix) had to be fixed once per board.
check: falsifier: a second board gets fold debt, outbox drain and product share by committing one profile file; if adoption needs a code edit, the profile boundary is drawn in the wrong place
supersedes: none
evidence: measured
- **Guard:** none yet (proposal; the stage copies listed above are the measured part, the shared tool is untested).
- **Outbox:** outbox:7af13027354f9eaf mlv-app:932c1ab4eb19

## mlv-app/designed-fix-lost-on-partial
rule: a round that ends PARTIAL names its successor card in the same tick that reads it; a card whose design names fix rows codes them in the next round instead of re-measuring; a queued fix idle past 72 h, or one whose blocker has merged, is re-armed or closed by a ruling; a standing sweep lists every designed or partly built card with no merged PR and nothing in flight.
mechanism: a playback stall fix was designed with named fix rows, then spent four measure-only rounds and never coded it. The work kept stopping on infrastructure rather than on the code: a guard refused the design write, a provider quota cut the first round, a producer died around a host restart, and a worktree was removed under a live chain. Nothing re-armed it, and the defect stayed in the product for two days until the owner saw it. A first sweep the same day listed 58 stalled cards out of 341, in several leak shapes: re-measure instead of code, PARTIAL on infrastructure, queued and never re-read, and unblocked by a merge but never re-armed.
check: the sweep prints one STALLED line per designed or partly built card with no merged or open PR, no live lane and no closing ruling whose newest activity is older than the stale threshold (default 24 h); younger cards count as in flight and are not printed; each tick triages the oldest two
supersedes: none
evidence: measured
- **Outbox:** outbox:5bdea2ac2e523d8d mlv-app:3f241eb9893d

## mlv-app/telemetry-collected-but-never-read
rule: every quality field a run already records gets a standing reader that runs each tick, flags it against an owner-visible bar, and needs a live fix card for every flag kind; a session reads that view before it reports any benchmark, and treats a long-frame or hitch number as a finding, never as tool noise.
mechanism: a board reads only the metric each card was built to measure. Every playback receipt for a day carried present-gap and present-setup-stall fields (84 of 98 legs over the bar, periodic stalls of roughly 100-300 ms on two GPU hosts), and a session even reported p99 of 700-1300 ms as tool noise. The owner found the stutter on screen first.
check: a scan over the newest receipts prints one FLAG line per leg over the bar, and the tick summary names which live card covers each flag kind; a flag kind with no covering card must have one declared in that same tick
supersedes: none
evidence: measured
- **Outbox:** outbox:8bd518a5ad4c4b21 mlv-app:3f241eb9893d

## mlv-app/adopt-without-guard-is-not-adopted
rule: an ADOPT of a bus card closes only when a tracked guard with a RED fixture (an input the check must fail) has merged; a deploy that lives only in untracked board tooling, or a ledger line, stays recorded as unenforced and keeps the card owed.
mechanism: a fold marks a card adopted when the lesson is written down or a local script is deployed, so the count of adopted cards says nothing about whether the failure can still recur unnoticed. On this board 24 queued ADOPTs resolved as 8 merged PRs, 10 untracked board tooling only and 6 still ledger lines, while the tracked guard registry held 4 entries.
check: for each ADOPT row compute the state merged-with-RED-fixture | untracked-tooling | ledger-only, and the ratio of tracked guards to ADOPTs; a row in either unenforced state carries a guard card and is not counted as closed. The registry size is the REGISTRY tuple in tools/repo_hygiene/test_doctrine_guards.py.
supersedes: none
evidence: measured
- **Outbox:** outbox:57a61ca854b4fdf1 mlv-app:6b6f8e017b31

## mlv-app/guard-only-in-the-hub-shell
rule: a never-authorized rule is enforced on every surface that can act on it (the hub shell, venue job scripts, lane wrappers and CI), and each surface carries its own RED fixture; a guard on one surface is not evidence for the others.
mechanism: the rule was checked only in the hub shell, so the same action stayed possible from any other process that could reach the target, and the existing guard gave a false sense of coverage. A rule that can be dodged by changing the launching surface is a convention on those other surfaces.
check: list the surfaces that can perform the action; each row names its guard and its RED fixture, and a surface with no fixture is a finding. The count of surfaces without a fixture is printed with the rule.
supersedes: none
evidence: reported
- **Outbox:** outbox:c9d49a5525397e63 mlv-app:6b6f8e017b31

## mlv-app/known-but-unenforced-incident
rule: every new incident is first recalled against the existing traps, cards and memory; a hit files a guard card for the knowledge that already exists, and does not file a new lesson.
mechanism: of 8 incidents on one day, 6 were already described by an existing trap, card or memory that had no enforcing guard: a never-authorized rule checked only in the hub shell, a silent waiter, foreground suites burning their time bounds, double keying, a PARTIAL round losing a designed fix, and a frozen display read as healthy. Another, a GPU wake artifact of the vendor query tool, was found independently the same day by this board and by conjugal (bus c1ba15e): duplicated discovery, not propagation.
check: each incident record carries a recall result of HIT <card or trap id> | MISS | UNKNOWN; report the share of incidents that were already known, and treat UNKNOWN as unrecalled, never as MISS.
supersedes: none
evidence: measured
- **Outbox:** outbox:b96cc2a65dfb3eed mlv-app:6b6f8e017b31

## mlv-app/meter-fails-open
rule: any meter, waiter or scan reports exactly one of OK | DUE | UNKNOWN | GAVE-UP; an unknown reading is never read as zero, and an UNKNOWN that lasts past 2 beats is reported as DUE.
mechanism: the fold-debt meter treated a failed recall (exit 4, no result) as nothing owed, so the meter read clean at the moment it could not see. A reading of zero and a reading that could not be taken look identical to the next consumer unless the output type separates them.
check: a canary input that forces the probe to fail must make the meter print UNKNOWN and exit non-zero; a per-meter unknown-streak counter is printed beside the reading and the meter turns DUE when it passes 2.
supersedes: none
evidence: measured
- **Outbox:** outbox:02dfa3bd68ab6e65 mlv-app:6b6f8e017b31

## mlv-app/product-share-starved-by-factory-work
rule: a receipt: a board that wants product progress reserves a producer slot for a declared product card and sets a share floor on merged product work; factory cards take a slot only when no product card is due or they name the product subject they unblock. MLV is trialling this remedy.
mechanism: in 72 hours 9 of 68 first-parent merges (13 percent) touched product paths, while the hub counted more factory rows than product rows in its queue; with no reserved slot the loop kept choosing work on itself.
check: git log refs/remotes/fork/master --first-parent --merges --since="72 hours ago" counts the merges; classify each by whether it touches product source paths and report the share against the floor.
supersedes: none
evidence: measured
- **Outbox:** outbox:6844e245740a300d mlv-app:6b6f8e017b31

## mlv-app/published-card-without-sibling-disposition
rule: a proposal to the bus: a published card asks every subscribed project for ADOPT, DISTINGUISH or ACK within a stated deadline, and a subscriber whose heartbeat is stale is surfaced beside the card instead of being read as silence.
mechanism: this board published 11 cards to its cards file and none has a confirmed sibling ADOPT (one possible uncited match: a dng-auto-processor spec commit, bus dd5fb97, beside the codex-smoke card). A sibling advisory channel records an MLV card as already existing and not addressed, found by hand. A card with no requested disposition has no reader who owes an answer.
check: per published card, the share with a sibling disposition of ADOPT | DISTINGUISH | ACK, and the list of subscribers whose heartbeat is older than the deadline; a card past its deadline with no disposition is printed as UNANSWERED.
supersedes: none
evidence: measured
- **Outbox:** outbox:228200c2232a81f5 mlv-app:6b6f8e017b31

## mlv-app/codex-ignored-config-key-is-not-the-requested-mode
rule: a launcher that passes a containment setting to codex as `-c <key>=<value>` must not record that value as the mode the lane ran; when codex's stderr preamble says the key was ignored, the receipt records `requested-<value>-ignored-by-codex` with the matched line, never the requested value.
mechanism: codex 0.162.0 accepts an unknown `-c` key with exit 0 (sol, PR #329 r1), prints "warning: Codex is ignoring N unrecognized configuration setting(s)" plus one indented "<source>: `<key>` is ignored." line, and runs on its default. Invoke-Lane.ps1 recorded `authority.windowsSandbox` from its own argv, so a build without the key would yield a receipt claiming `unelevated`. The fix scans only codex's preamble: it stops at the first bare `codex` turn line (a transcript can quote a nested run) and skips the echoed prompt BY POSITION, the span after codex's `user` marker line, cut once. Removing the prompt as a substring is itself a trap: `windows.sandbox`, `windows` or the warning block as the prompt also occurs inside the genuine warning, erasing the evidence (sol, PR #407 r1). No zero-token probe prints the warning (0.162.1).
check: run the lane with stderr carrying the warning block naming `windows.sandbox` and read the receipt: `authority.windowsSandbox` must be `requested-unelevated-ignored-by-codex` with `windowsSandboxIgnoredDetail` quoting the line; with no such line (or only `cli_auth` ignored) it must stay the requested mode; a prompt overlapping the warning text must not mask a genuine one.
supersedes: none
evidence: measured
- **Guard:** tests/coordination/test_lane_containment.py `test_codex_receipt_never_claims_a_windows_sandbox_mode_codex_ignored` (RED on fork/master 29f52739) and the `test_codex_receipt_keeps_the_requested_windows_sandbox_*` rows; `test_codex_receipt_keeps_genuine_ignored_evidence_*` (RED on 53b786f5)
- **Outbox:** outbox:474c9a9566eb3ea1 mlv-app:53b786f5cc37

## mlv-app/pinned-codex-cli-can-silently-exclude-a-newer-model
rule: a pinned Codex CLI is proven only for the models its promotion exec-probed; a lane whose resolved model is not on that list runs on the unpinned CLI, with the receipt naming `PIN_MODEL_UNPROBED`, never on the pin by default.
mechanism: the models cache is one file shared by every Codex CLI on the machine, and each CLI rewrites it with the catalogue its own version was offered. Measured 2026-10-12: its `client_version` read 0.160.1 (the pin) at one read and 0.162.0 (the global CLI) at the next, minutes apart. A tier resolved from it can name a model the pinned CLI was never offered or never ran, and nothing errors at resolution. The promotion that wrote the pin had probed one model (the luna tier) while the sol tier had moved to `gpt-6.1-sol`; 103 sol lanes ran it on the pin with no probe behind them.
applies: mlv-app
check: set the pin's `probedModels` to `["gpt-6-luna"]` and launch a read-only sol lane: the receipt's `codexExe.pinState` must read `PIN_MODEL_UNPROBED`, its path must be the global CLI, and one `[codex-pin]` line must say why. Re-promote with every lane tier and the same lane must read `PINNED`.
supersedes: none
evidence: measured
- **Guard:** tests/coordination/test_lane_containment.py `test_codex_pin_runs_the_global_cli_when_the_resolved_model_was_never_probed` and `test_codex_pin_promoter_refuses_the_whole_pin_when_one_tier_model_cannot_exec`
- **Outbox:** outbox:cf9a86a7bbbd3d60 mlv-app:e1fd3bb47c6d

## mlv-app/queue-without-age-limits-starves-owner-waiting-card
rule: every queued-and-due card carries an age limit by priority, and a card the owner has asked about is marked owner-waiting and drained first; "queued" without an age check is not a state, it is a place work goes to be forgotten.
mechanism: card-queue rows are built from the ledger and a queue-drain launch has a hub tick pick a few rows per beat when capacity allows. Measured 2026-10-15: 410 open rows, 85 queued and due plus 236 P6 backlog, producers 6 against a cap of 3, host commit at the 60 GiB ceiling. A P3 product round (Vision 50D r2, hub ruling 17:32Z) sat behind about 85 due rows with no age limit and no owner-waiting signal, queued in the ledger but never armed. A same-day scan found 28 cards queued with no action, run directory or live process; all 28 were queue rows, none invisible. Sources: ledger 2026-10-15T20:32:36Z; project-memory self-heal-stuck-items-strategy-20261015.md.
applies: mlv-app
check: from the MLV-App repo root, `python tools/coordination/stuck_queue_checks/queue_starvation_check.py --impl naive` exits 1 (RED) and `python tools/coordination/stuck_queue_checks/queue_starvation_check.py --impl aged` exits 0 (GREEN); any Python 3, stdlib only, pushed at SuperDimensionalSpaceFortress/MLV-App @c5739ef23f09 (PR 454). Fixture: 50 due P1/P2 rows plus one P3 row aged 25 h and owner-waiting, capacity 3; GREEN needs that row reported starved, bumped to P2 and drained. A board checks its own drain by passing its command line to --drain-cmd (stdin {capacity, rows}, stdout {drained, starved, bumped}); a command that fails or prints no JSON exits 2, never GREEN
supersedes: none
evidence: measured
- **Guard:** the fix is pending -- card STUCK-RECONCILER-1 (starvation limits P1 2 h / P2 6 h / P3 24 h / P4-5 72 h, owner-waiting escalation, prompt-ready fast path, throughput line); the check above already runs against any drain
- **Outbox:** outbox:8acc254fd591aaee mlv-app:5dba0591763f

## mlv-app/unlocked-action-list-rewrite-drops-a-just-armed-action
rule: every writer of the pending-action list takes one lock around a fresh read and its write, never held across slow work, and the arming command re-reads the list after writing and fails loudly if its own entry is missing.
mechanism: the autopilot beat reads the pending-action list, works, then writes its in-memory copy back through a temp file and a move (Write-Actions, no lock). The arming command does its own read-modify-write with no shared lock. Measured 2026-10-15: the lintscope-r11b action added at 19:25:52Z was missing from the file; an autopilot beat had rewritten it at 19:25:59Z from its own earlier read, 7 s after the add. A hub session re-added the same id at 19:36:23Z, verified present after 20 s. A temp-file-and-rename write is atomic against a torn file, not against a lost update. Sources: ledger 2026-10-15T19:37:23Z; project-memory self-heal-stuck-items-strategy-20261015.md S2 (7 s).
applies: mlv-app
check: from the MLV-App repo root, `python tools/coordination/stuck_queue_checks/action_list_lost_update_check.py --impl naive` exits 1 (RED) and `python tools/coordination/stuck_queue_checks/action_list_lost_update_check.py --impl locked` exits 0 (GREEN); any Python 3, stdlib only, pushed at SuperDimensionalSpaceFortress/MLV-App @c5739ef23f09 (PR 454). Each of 50 trials runs the arming command between the beat's read and its write; GREEN needs no armed entry lost and a forced loss to make the arming command exit non-zero. A board checks its own writers with --impl-module and the path of a file defining arm and beat_save; a writer that raises exits 2, never GREEN
supersedes: none
evidence: measured
- **Guard:** the fix is pending -- card STUCK-RECONCILER-1 item 1 (named mutex around every read+write; post-write re-read; lost-action re-add from the arming log); the check above already runs against any writer pair
- **Outbox:** outbox:9f85ea170b859842 mlv-app:5dba0591763f

## mlv-app/every-merge-path-needs-the-same-fail-closed-gate
rule: every merge or enqueue path calls one fail-closed decision function and all other paths are retired; it reads only structured sources (legs are head-bound commit statuses `review/<seat>` with run id and report hash, CoS asks come only from the CoS bus record, `.github/` approvals only from a hub-owned record bound to repo, PR, head and blob hash) and re-checks right before the merge: CoS scan always re-run (never cached), approvals record and file and blob reads first, leg statuses the LAST external read before the merge call.
mechanism: PRs 452, 453, 454 and 460 went through an enqueue script that read neither legs nor open CoS asks (ACK 6216909806). The first replacement parsed PR comment text. Three Codex review rounds of that parser found 7, 6 and 6 blockers, each a new false-ALLOW class in free text under one shared account: quoted or fenced blocks accepted, one commenter supplying both families and the approval, a reposted old approval outranking a newer CHANGES_REQUESTED, any author's ACK answering an ask, a stale evaluation consumed at merge. One account writes every comment, so hardening moves the hole; the parser was stopped on PR 454 (comment 6220283608), left in shadow, and replaced by the sources above (card MERGE-GATE-STATUS-CHECKS-1). Two ungated scripts were made to refuse. The gate's own review found the ordering fault twice (stale statuses, cached scan); both fixed before approval.
check: gh api repos/SuperDimensionalSpaceFortress/MLV-App/issues/comments/6220283608 --jq .body prints the stop decision and the design; legs: see card local-review-keys-are-not-legs-until-published.
supersedes: none
evidence: reported
- **Guard:** grep the repo for every call of the merge or enqueue command; each routes through the one function, and one hostile test per hole (incl. a failure posted during the scans) is RED against the old gate
- **Outbox:** outbox:ccf7877fdab4df20 mlv-app:e56701410c03

## mlv-app/launcher-scoring-per-sentence-exempts-an-unrouted-second
rule: a lint that exempts a launcher because it is routed to a remote venue scores every launcher occurrence on its own, and bounds pattern gaps at clause separators (`;`, `then`, `or`, and the next launcher token); a lazy gap alone still crosses `;`.
mechanism: scoring per sentence lets the first launcher's venue routing exempt a second, unrouted launcher in the same sentence. Chief of Staff follow-up on PR 448 (comment 6216180502) reproduced a pass for a routed launcher, a semicolon, then a plain second launcher. The per-launcher fix on PR 465 closed that shape, and the Chief of Staff shared blocker on its first head (comment 6218718347) found the gap still open when the first launcher did not match on its own: the lazy gap reached the second launcher and the merged span took the first clause's routing. Revision r1 of PR 465 carried 98 test rows, all red-green. It was the seventh round in which an outside probe found an exemption bypass.
check: after PR 465 merges, `python -m pytest tools/repo_hygiene/test_hub_vm_no_local_playback.py -q` passes from the merge commit and its rows include one second-launcher case per separator. 75cb00e1 is the measured r1 SHA (historical); until PR 465 merges, its current tip is the live head.
supersedes: none
evidence: measured
- **Guard:** one RED row per separator and per launcher token in the lint's must-refuse corpus, plus a row where the venue text belongs to the second launcher
- **Outbox:** outbox:5f284c9b9db24d46 mlv-app:e56701410c03

## mlv-app/lint-that-screens-prompts-refuses-its-own-repro-quotes
rule: when a safety lint also screens agent prompts, a dispatch prompt points at the source comment that holds the bypass repros (by comment id) and never quotes the repro lines.
mechanism: the lint refuses any prompt whose text matches the shapes it exists to block, and a bypass repro is by construction such a shape. On PR 465 the dispatch that quoted the repro lines was refused; it succeeded once the prompt referenced the Chief of Staff comment (6216180502, which holds the repros) and described the fix in words. The refusal is correct, not a lint bug, so the fix belongs in the prompt writer, not in an exemption. The refused dispatch is recorded only in private run state.
check: none (reported only; the refusal is in private run state). Public part: gh api repos/SuperDimensionalSpaceFortress/MLV-App/issues/comments/6216180502 --jq .body shows the repro lines a prompt should cite instead of copy.
supersedes: none
evidence: reported
- **Guard:** the prompt template for lint-fix cards carries a line "see comment <id>", and a test shows a prompt with an inline repro is refused
- **Outbox:** outbox:1b1f84fca96133ff mlv-app:e56701410c03

## mlv-app/local-review-keys-are-not-legs-until-published
rule: a review key is a leg only as a commit status `review/<seat>` on the full head SHA (success = APPROVE, failure = CHANGES_REQUESTED, description names run id and report hash); a local run folder or a PR comment is not a leg, and the newest status per seat wins.
mechanism: on 2026-10-16 the Chief of Staff counted 0 of 2 legs on PRs 452, 453, 454, 460, 451 and 442, though each merged head had two tip-bound APPROVE keys that existed only in local run folders. Counting seat comments is also wrong: it has no head or verdict filter, so PR 466 showed 2 comment legs while both were CHANGES_REQUESTED on its superseded first head. A hub once published the wrong attempt (PR 455). Sources: ask 6215617998, ACK 6216909806 on PR 454; legs 6216853212, 6216854389 on PR 452; PR 455: 6216913104 (the wrong-attempt publication), 6216900141 (hub ACK correctly reporting sol r6 attempt 2 CHANGES_REQUESTED, per 6216953191).
check: gh api --paginate --slurp "repos/SuperDimensionalSpaceFortress/MLV-App/commits/<full head sha>/statuses?per_page=100" | jq 'add|[.[]|select(.context|startswith("review/"))]|group_by(.context)|map(max_by([.created_at,.id]))|map(select(.state=="success")|.context|ltrimstr("review/")|if .=="fable" or .=="opus" or .=="sonnet" then "claude" elif .=="sol" or .=="luna" then "codex" else empty end)|unique|length' counts families with a newest-success leg (all pages; a same-second tie goes to the larger status id); the bar is 2. Measured: merged PR 462 head 1ae9cd0ad46e090b9a7ef7d7919ecd06c0248e16 prints 2; PR 466 first head e56701410c03a34f1756e40321d57b506c953214 prints 0.
supersedes: none
evidence: measured
- **Guard:** each review run posts its status on finish against the full head SHA; the merge decision counts only statuses on the head it merges
- **Outbox:** outbox:1fd36b6a87fec8e2 mlv-app:e56701410c03

## mlv-app/pass-pr-bodies-as-files-not-inline
rule: write a PR body or comment to a file with the file-write tool and pass it with `--body-file`; never inline `--body` text, and search with a structured search tool rather than a shell grep when the pattern holds redirect characters.
mechanism: command-line guards scan the whole command string, so inline body text containing backticks, `>>>` or `<<<` is read as a redirect or write path and the command is denied. Lane reports on PR 464 (PR create denied) and PR 457 (a shell grep with such a pattern denied) show both shapes; both completed once the body came from a file and the search ran through the structured tool. Guards differ by project, so the general rule is to keep free text out of command lines.
check: none (reported only; the denials are in private lane reports). Public part: gh pr view 464 --repo SuperDimensionalSpaceFortress/MLV-App --json body --jq .body shows a body that was created from a file.
supersedes: none
evidence: reported
- **Guard:** the lane prompt template states "gh pr create --body-file <path>" and forbids inline --body
- **Outbox:** outbox:b385e4fa904e54f1 mlv-app:e56701410c03

## mlv-app/response-duty-scanner-must-read-merged-and-closed-prs
rule: a response-duty scanner covers merged and closed PRs as well as open ones, and an ask is a comment that requests `ACK:`; a verdict or review note that merely mentions ACK is not an ask.
mechanism: the scanner skipped merged PRs, so asks posted after merge went unseen: post-merge asks on PRs 448, 451 and 454 were found by hand, and the ask on PR 409 sat unanswered for two days before an overdue ACK (comment 6218422209). Overdue ACKs on PR 427 (6217656028) are the same shape. The opposite error also cost work: a scanner that counted a verdict as an ask raised false positives, for example PR 446, whose review note says there is no open ask but mentions ACK and DISTINGUISH; the hub answered with a DISTINGUISH (6218423910) only to clear the thread. The false-positive count (11) is in a private hub ledger.
check: gh api repos/SuperDimensionalSpaceFortress/MLV-App/issues/409/comments --jq '.[]|select(.body|startswith("ACK: overdue"))|.id' prints 6218422209 and gh pr view 409 --repo SuperDimensionalSpaceFortress/MLV-App --json state --jq .state prints MERGED. A scanner that listed no open ask on 409 before that comment is the finding.
supersedes: none
evidence: measured
- **Guard:** scan every PR with a comment in the window regardless of state; a fixture holds one merged-PR ask (must be found) and one verdict mentioning ACK (must not be)
- **Outbox:** outbox:4e47df0db2d87265 mlv-app:e56701410c03

## mlv-app/two-hubs-on-one-board-duplicate-outward-actions
rule: before any outward action (a PR comment, a dispatch), a hub reads the other hub's record of that action on the same target, and dispatch claims are keyed per card so a second claim is refused.
mechanism: an unattended hub tick and an interactive hub both worked the same Chief of Staff asks; about a minute apart they answered the same 12 asks, two answers conflicted, and a duplicate gate card was started and then cancelled. The public trace is PR 455: the first hub's ACK 6216900141 at 13:47:29Z, which correctly reported sol r6 attempt 2 as CHANGES_REQUESTED; a second ACK 6216913104 at 13:48:12Z, the wrong one, saying the Codex seat had no verdict; and a correction 6216953191 at 13:50:22Z confirming the first ACK. A second duplicate pair is on PR 458. The count of 12 and the cancelled card are in private hub state.
check: gh api repos/SuperDimensionalSpaceFortress/MLV-App/issues/455/comments --jq '[.[]|select(.id==6216900141 or .id==6216913104 or .id==6216953191)|.created_at]' lists three timestamps within about three minutes. Two ACKs from different hubs inside a minute on one PR is the finding.
supersedes: none
evidence: measured
- **Guard:** an outward-action ledger keyed by (target, kind) read before posting, and a claim file per card that a second dispatcher refuses
- **Outbox:** outbox:cd47139dcd62e7d8 mlv-app:e56701410c03

## mlv-app/one-config-driven-doctrine-outbox-for-the-fleet
rule: the fleet carries ONE doctrine_outbox.py, in the bus at tools/factory/, pinned by each project through factory-pins; every project value sits in doctrine-outbox.config.json at the project root. A project never edits the tool, and keeps its local copy until OUTBOX-PIN-AWARE-TOOL-AT-REF-1 ships, because the installed push hook and debt checks still read that path.
mechanism: tool-census hashes whole files: the outbox was copied and edited per project (3 versions: bus reference 449 lines, airmypc 1099, mlv-app 1635), so each fix drifted. The mlv-app copy is the candidate for tools/factory/doctrine_outbox.py: the config-driven superset that also answers the old hook commands (check, check-range, pre-push, stop, session-start, install-hooks).
applies: mlv-app, airmypc, agent-bridge, conjugal
check: on the bus run `node tools/tool-census.mjs`; once projects run the file by pin from tools/factory/ and drop their copies, the doctrine-outbox family reads 1 distinct version.
supersedes: none
evidence: measured
- **Adopt:** bus steward adds tools/coordination/doctrine_outbox.py from MLV-App PR 468 as tools/factory/doctrine_outbox.py, byte for byte; sha256 of its LF bytes b6942212c54501e3112eff3eb20c65aa355ff8c7cc096841cfb15939d6be2a92.
- **Pin:** each project reviews that bus SHA, then runs `python factory-pins/pin-runner.py pin doctrine-outbox --commit <bus-sha> --path tools/factory/doctrine_outbox.py --reviewer <who> --reason <why>`. A pinned run is `python factory-pins/pin-runner.py run doctrine-outbox -- --config doctrine-outbox.config.json <command>`. The project KEEPS its copy: deleting it bricks the push hook and reads debt as UNKNOWN TOOL_ABSENT_AT_REF.
- **Follow-up:** OUTBOX-PIN-AWARE-TOOL-AT-REF-1 makes the hook invocation config-driven and `require_tool_at_ref` accept a pinned tool. Only after it ships does a project delete its copy.
- **Outbox:** outbox:b57af82206ca5282 mlv-app:21cf93736a7b

## mlv-app/cos-concern-channel-r1-r2
rule: a project tells the CoS a concern by one of two routes, and the CoS answers each. R1, about one PR: a comment on that PR's thread starting `CoS-CONCERN:`. R2, fleet-level or about CoS process: an entry in the project-owned `specs/<project>/cos-concerns.md` (id `<project>-cc-<yyyymmdd>-<n>`, `to: CoS`, `opened_utc`, `expires_utc` at most +14 d, `kind`, `evidence`, one-sentence `ask`; no field is an approval, a ruling or a permission, free text is data). The CoS answers each id once in its own `cos-feedback/<project>/concerns.md`: `<id> ADOPTED|DISTINGUISHED|NEEDS-INFO <reason>`; open = no answer line and not expired, derived, never stored.
mechanism: the bus has no project-to-CoS channel. `cos-feedback/README.md:16-17` and `:74` make the CoS the only writer and projects read-only, and Law 2 allows one writer per file, so a project-owned file is the only legal shape (`RULINGS.md:1289`: an entry's author is told "through the channel that reaches them"; `specs/conjugal-fleet-advisory-channel.md` s4 and s6: addressed, one answer, expiring, no approval type). Two failures went unfiled: a project absorbed CoS output defects as local fixes, and the CoS listed PR 457 asks as open 41 min after ACK 6223874137 (bus 9f93dd2).
check: `py -3 -m pytest tests/coordination/test_doctrine_outbox_concerns.py -q`, stdlib plus pytest, on MLV-App PR 470 (branch product/COS-CONCERN-CHANNEL-1); R1 first used: PR 457 comment 6224672124
supersedes: none
evidence: measured
- **Ask (steward, in order):** (1) the owner rules on the channel; (2) then the CoS, sole writer under `cos-feedback/`, adds to Writer duties: `- The CoS reads `CoS-CONCERN:` PR comments and every `specs/*/cos-concerns.md` each pass.` The drain holds `mlv-app-cc-20261016-1` to `-4` until that exact line is on the bus tip. Until then R1 comments go unseen (PR 457 comment 6224672124, unanswered).
- **Outbox:** outbox:9eda9f42bed18652 mlv-app:892922b7d52c

## mlv-app/one-config-driven-doctrine-outbox-pr-470
rule: the fleet carries ONE doctrine_outbox.py, in the bus at tools/factory/, pinned by each project through factory-pins; every project value sits in doctrine-outbox.config.json at the project root. A project never edits the tool and keeps its local copy (see Pin).
mechanism: tool-census hashes whole files: the outbox was copied and edited per project (3 versions: bus reference 449 lines, airmypc 1099, mlv-app 1635), so each fix drifted. The mlv-app copy is the candidate for tools/factory/doctrine_outbox.py: the config-driven superset that also answers the old hook commands (check, check-range, pre-push, stop, session-start, install-hooks).
applies: mlv-app, airmypc, agent-bridge, conjugal
check: on the bus run `node tools/tool-census.mjs`; once projects run the file by pin from tools/factory/ and drop their copies, the doctrine-outbox family reads 1 distinct version.
supersedes: mlv-app/one-config-driven-doctrine-outbox-for-the-fleet (its PR 468 digest)
evidence: measured
- **Adopt:** bus steward adds tools/coordination/doctrine_outbox.py from MLV-App PR 470 as tools/factory/doctrine_outbox.py, byte for byte; sha256 of its LF bytes 9e6f2b55c2a646db7c218cf460851b55bb0eeff2390c4473ed358ad1b98eaabf.
- **Pin:** each project reviews that bus SHA, then runs `python factory-pins/pin-runner.py pin doctrine-outbox --commit <bus-sha> --path tools/factory/doctrine_outbox.py --reviewer <who> --reason <why>`. A pinned run is `python factory-pins/pin-runner.py run doctrine-outbox -- --config doctrine-outbox.config.json <command>`. The project KEEPS its copy: deleting it bricks the push hook and reads debt as UNKNOWN TOOL_ABSENT_AT_REF.
- **Follow-up:** OUTBOX-PIN-AWARE-TOOL-AT-REF-1 makes the hook invocation config-driven and `require_tool_at_ref` accept a pinned tool. Only after it ships does a project delete its copy.
- **Outbox:** outbox:1adde01acdc7f693 mlv-app:21cf93736a7b

## mlv-app/git-fsmonitor-daemons-outlive-lane-worktrees
rule: when shared repo config sets core.fsmonitor=true, every linked worktree inherits it and its first `git status` starts a detached `git fsmonitor--daemon` that nothing stops. Per lane worktree, set core.fsmonitor=false in config.worktree (only if extensions.worktreeConfig is already on; without it `--worktree` either errors or, on a git that allows it, writes the SHARED config and switches the main checkout off too, so the helper skips) and run `git fsmonitor--daemon stop` before `worktree remove`. Never kill the daemons by name or pid.
mechanism: on the MLV-App host (git 2.40.0.windows.1) 65 daemons ran for 64 worktrees, the oldest 17 h old, 3.2 GiB private in total, with host commit at 61-64 GiB against a 60 GiB dispatch gate that then refused lanes for hours. A daemon's cwd is the profile dir, so cwd cannot map pid to worktree; `git -C <wt> fsmonitor--daemon status` maps worktree to daemon. Hooks that run `git status` over every worktree start one daemon each.
check: `py -3 -m pytest tools/coordination/test_coordination_guardrails.py -k fsmonitor -q`
supersedes: none
evidence: measured
- **Guard:** tools/coordination/lane-fsmonitor.ps1, called from Invoke-Lane.ps1, Invoke-Workstream.ps1, Invoke-WorkstreamLoop.ps1 and Retire-LaneWorktree.ps1; both helpers refuse the main checkout.
- **Order:** the disable (and a stop of any daemon already running there) runs BEFORE the first git command that reads the worktree's index, on every path that reuses an existing worktree, including the continuation branch that refuses a dirty tree. Pinned by an order test.
- **Limits:** a daemon started in a live lane by something other than the lane keeps running until the lane ends; the helper skips when the extension is off. `Retire -WhatIf` writes the worktree-scoped setting (the sweep already stamped config).
- **Outbox:** outbox:bbee54a0b3de8308 mlv-app:d754de31bf5d

## mlv-app/pin-runner-cache-never-repairs-same-size-corruption
rule: a blob cache that is re-verified on read must also be repaired on write: when the bus clone supplies verified bytes, `cache_put` replaces a cached file that is present but not the pinned bytes, whatever its size.
mechanism: bus tools/factory/pin-runner.py (pin 28fc1ee1; vendored at MLV-App factory-pins/pin-runner.py:312-331): `cache_get` ignores a cached blob that fails its hash, `pinned_bytes` then reads the bus and calls `cache_put`, which returns early when the cached file has the same size as the new bytes. A same-size corrupt entry (one flipped byte) survives every bus-backed run. Measured 2026-10-18: a run with a bus clone exits 0 and leaves the entry corrupt; the next run with no clone exits 3 UNAVAILABLE although the pin had run cleanly on that box. Never wrong bytes (the failure is loud), but the docstring promise that a seen pin keeps running without the clone does not hold.
check: `py -3 -m pytest tests/coordination/test_check_doc_size_by_pin.py -k same_size_corrupt -q` asserts the safe half (corrupt bytes never run). The repair is the bus owner's: in `cache_put`, skip only when the cached file passes `check_bytes`; then re-pin.
supersedes: none
evidence: measured
- **MLV meanwhile:** it edits no pinned bus artifact. A corrupt entry costs one offline failure (exit 3, nothing runs); cure: delete `%LOCALAPPDATA%/factory-pins/blobs/<blob id>`, run once with the clone present (docs/22 "Pinned runs").
- **Origin:** CoS #491 I1, folded into CHECK-DOC-SIZE-SINGLE-SOURCE-1.
- **Outbox:** outbox:eee5adb67a4d6939 mlv-app:577aff6fd4af

## mlv-app/smb-listing-that-opens-files-feeds-the-av-scanner
rule: Never list a large SMB directory with a tool that stats every entry (Git for Windows `ls -t`, `ls -l`, `find -newer`); enumerate names and times from the directory listing (.NET `EnumerateFileSystemInfos`), keep the newest N, and rotate mailbox directories into dated archive folders.
mechanism: The MSYS coreutils stat opens each file to read its times, and real-time antivirus scans every open, file by file over the network. A directory enumeration returns the same metadata without opening anything. A process-name exclusion for git.exe does not cover usr\bin\ls.exe. Measured 2026-10-17: `ls -t` of a 20.7k-file job mailbox ran over 10 minutes at about 48 s of scan time per minute; the enumeration listed it in about 2.5 s.
check: pwsh -NoProfile -File tools/testing/test-agent-share-rotation.ps1 (MLV-App; bounded lister plus whole-job rotation)
supersedes: none
evidence: measured
- **Outbox:** outbox:9a30098636db2db4 mlv-app:d22b6cf2ba5d

## mlv-app/pin-aware-doctrine-outbox-hook-and-ref-check
rule: a project that runs doctrine_outbox.py by pin sets `tool_pin` in doctrine-outbox.config.json; the installed pre-push hook then runs the pin through factory-pins/pin-runner.py and the debt and drain ref check accepts the pin, so the project can drop its local copy.
mechanism: the hook ran `$REPO_ROOT/<tool_rel>` and require_tool_at_ref demanded `tool_rel` at the ref, so a project that pinned the shared outbox and deleted its copy bricked its own pushes (CoS repro on a4480947). A config without `tool_pin` behaves exactly as before. The file changed, so the digest below replaces the earlier card's.
applies: mlv-app, airmypc, agent-bridge, conjugal
check: `py -3 -m pytest -q tests/coordination/test_doctrine_outbox_hooks.py -k pin` in MLV-App: the fixture pins the tool, holds no copy, installs the hook and pushes through it.
supersedes: mlv-app/one-config-driven-doctrine-outbox-pr-470 (its digest; the tool gained `tool_pin`)
evidence: measured
- **Adopt:** bus steward adds tools/coordination/doctrine_outbox.py from the MLV-App PR OUTBOX-PIN-AWARE-TOOL-AT-REF-1 as tools/factory/doctrine_outbox.py, byte for byte; sha256 of its LF bytes 980884caa698efd4352e776300876d90edfd65c39dfbd8ad38627ecd9b5bb10a.
- **Pin:** each project reviews that bus SHA, then runs `python factory-pins/pin-runner.py pin doctrine-outbox --commit <bus-sha> --path tools/factory/doctrine_outbox.py --reviewer <who> --reason <why>`. A pinned run is `python factory-pins/pin-runner.py run doctrine-outbox -- --config doctrine-outbox.config.json <command>`. Then set `"tool_pin": "doctrine-outbox"` in the config and run `install-hooks` through that pinned command once.
- **Follow-up:** OUTBOX-PIN-AWARE-TOOL-AT-REF-1 shipped the hook and ref check. Only after the bus holds the file and the project's pin is reviewed does that project delete its copy.
- **Outbox:** outbox:1f4aecacdff90fe5 mlv-app:f5015de9fb77

## mlv-app/one-config-driven-doctrine-outbox-ruling-supersedes-1
rule: the fleet carries ONE doctrine_outbox.py, in the bus at tools/factory/, pinned by each project through factory-pins; every project value sits in doctrine-outbox.config.json. A project never edits the tool; it sets `tool_pin` in its config once its pin is reviewed.
mechanism: per-project copies drift under tool-census. The mlv-app copy is the candidate: a config-driven superset of the old hook commands, a pin-aware hook and ref check (doctrine-outbox/README.md), and a `validate` refusal of a ruling candidate with no `touches/supersedes:` list of rule ids or bus paths at the bus tip. No `tool_pin` behaves as before.
applies: mlv-app, airmypc, agent-bridge, conjugal
check: on the bus run `node tools/tool-census.mjs`; once projects pin and drop their copies, the family reads 1 distinct version. In MLV-App `py -3 -m pytest -q tests/coordination/test_doctrine_outbox_hooks.py -k pin` pushes through the hook with no copy.
supersedes: mlv-app/one-config-driven-doctrine-outbox-pr-470 (its digest), mlv-app/pin-aware-doctrine-outbox-hook-and-ref-check (its digest)
evidence: measured
- **Adopt:** bus steward adds tools/coordination/doctrine_outbox.py as tools/factory/doctrine_outbox.py, byte for byte; sha256 of its LF bytes 2b50558037d2d0d472162676d04ed077e0c09bd191d7cce85391e75e7a9fa84e.
- **Pin:** each project reviews that bus SHA, then runs `python factory-pins/pin-runner.py pin doctrine-outbox --commit <bus-sha> --path tools/factory/doctrine_outbox.py --reviewer <who> --reason <why>`, runs it as `python factory-pins/pin-runner.py run doctrine-outbox -- --config doctrine-outbox.config.json <command>`, sets `"tool_pin": "doctrine-outbox"`, runs `install-hooks` that way once. OUTBOX-PIN-AWARE-TOOL-AT-REF-1 shipped the pin-aware hook; only after the pin is reviewed does a project delete its copy. Without `tool_pin` it KEEPS it.
- **Outbox:** outbox:73caf5cfc6ef728c mlv-app:cee9631abe0a

## mlv-app/one-config-driven-doctrine-outbox-exercise-3
rule: the fleet carries ONE doctrine_outbox.py, in the bus at tools/factory/, pinned by each project through factory-pins; every project value sits in doctrine-outbox.config.json at the project root. A project never edits the tool and keeps its local copy (see Pin).
mechanism: tool-census hashes whole files, so per-project copies drift. The mlv-app copy is the candidate for tools/factory/doctrine_outbox.py: the config-driven superset of the hook commands, with a fail-closed `validate --exercise` (routes are checked in a scratch clone, never the live bus; the clone and read-only git routes run with no host git config, filter or hook; the rest are existence-checked).
applies: mlv-app, airmypc, agent-bridge, conjugal
check: on the bus run `node tools/tool-census.mjs`; once projects pin tools/factory/ and drop their copies, the family reads 1 distinct version.
supersedes: mlv-app/one-config-driven-doctrine-outbox-pr-470 (its digest; same file plus route check)
evidence: measured
- **Adopt:** bus steward adds tools/coordination/doctrine_outbox.py from MLV-App card CARD-ROUTE-EXERCISE-3 as tools/factory/doctrine_outbox.py, byte for byte; sha256 of its LF bytes 5967e137cdfbc39893d8e1f8fc624a50fe0ef75e5776a4595245418fcf9c1ad1.
- **Pin:** each project reviews that bus SHA and runs `python factory-pins/pin-runner.py pin doctrine-outbox --commit <bus-sha> --path tools/factory/doctrine_outbox.py --reviewer <who> --reason <why>`. A pinned run is `python factory-pins/pin-runner.py run doctrine-outbox -- --config doctrine-outbox.config.json <command>`. KEEP the local copy: deleting it bricks the push hook and reads debt as UNKNOWN TOOL_ABSENT_AT_REF.
- **Follow-up:** OUTBOX-PIN-AWARE-TOOL-AT-REF-1 makes the hook config-driven and `require_tool_at_ref` accept a pinned tool; a project deletes its copy only after it ships.
- **Outbox:** outbox:74c853f5d2e30823 mlv-app:1a4a9e7b65ce

## mlv-app/a-cited-verdict-is-not-a-review-leg
rule: a review verdict cited in a commit message, a PR body or a ledger line is never a leg; only a `review/<seat>` status on the exact head SHA, a `[[pub:]]` JSON comment whose `head_sha` equals the head, or a GitHub review whose `commit_id` equals the head counts, a merge needs one Claude-family and one Codex-family leg (two same-family legs are not two), and no summary or ACK says "keyed" or "APPROVE" for a PR without one of the three on its current head.
mechanism: factory ACKs promised fresh legs on the final head while the open PRs showed 0 of 2 published legs on their current heads; on PR 462 the r2 keys were cited only in commit messages and r3 had none published. A push moves the head, so a verdict cited for an earlier head is not a leg for the current one. Sources: CoS ask 6219052910 and hub ACK 6223438673 on PR 454. Extends card local-review-keys-are-not-legs-until-published, which defines the status form; this one names the citation shape and the two other accepted forms.
check: gh api repos/SuperDimensionalSpaceFortress/MLV-App/issues/comments/6223438673 --jq .body prints the rule under item 3. For any open PR, a head SHA with a cited verdict and none of the three published forms is the finding.
supersedes: none
evidence: measured
- **Guard:** the board-local merge-enqueue hub tool refuses a merge or enqueue unless the status gate (rule TIP_LEGS) finds the legs on the head, counting only the `review/<seat>` status form (a head with only a `[[pub:]]` comment or GitHub review is REFUSED_LEGS); it is untracked, so the tracked copy of the rule is in agents/orchestration-tiering.md
- **Outbox:** outbox:00323059bb1a8141 mlv-app:3130b70210d3

## mlv-app/new-write-roots-need-a-defender-exclusion-alert
rule: a change that creates a new heavy-write root (scratch or worktree parent, build tree, temp prefix, per-test LOCALAPPDATA folder) registers it in a machine manifest; a session-start check prints ONE copy-paste elevated command for every unacknowledged root. Agents never add exclusions: a security setting, and unreadable without elevation.
mechanism: a 16-core host sat at 91-100% CPU with Defender at 1.3-1.7 cores despite a long exclusion list. A 60 s Defender performance recording traced the scans to roots created after the list: a test scratch tree moved to a new top-level folder, a `-state` sibling of an excluded tool folder, per-test LOCALAPPDATA folders, and the 8.3 form of an excluded temp path. Image-name process exclusions missed Git's `ls.exe`/`grep.exe`. After the owner added the roots and the unbounded share listing was stopped, Defender fell to about 0.2 core.
check: owner, elevated, `New-MpPerformanceRecording -RecordTo $env:TEMP\mp.etl -Seconds 60; Get-MpPerformanceReport -Path $env:TEMP\mp.etl -TopProcesses 20 -TopFiles 40`; a project write root in TopFiles is the finding.
supersedes: none
evidence: measured
- **Guard:** PROPOSED in softwarefactory-fleet-doctrine PR #89 at `tools/machine/fleet-defender/`, pending merge. Once #89 merges, the code that creates a root runs `Register-DefenderRoot.ps1 -Path <root> -Project <name>` (unelevated, one manifest row); an owner-installed SYSTEM task excludes allowlisted roots (long and 8.3 forms) and a SessionStart hook prints ONE elevated command for the rest. After #89 merges, install once per machine, owner elevated: `pwsh -NoProfile -File <bus>\tools\machine\fleet-defender\Install-FleetDefenderRoots.ps1 -LocalPolicy <machine policy>`.
- **Do not:** list a network share unbounded (`ls -t`): Defender scans each file over SMB, measured at 48 s of scan per 60 s on a 20k-file folder.
- **Outbox:** outbox:8c6f55491f950f35 mlv-app:a809fb24a1c7

## mlv-app/one-config-driven-doctrine-outbox-markup-forms-1
rule: the fleet carries ONE doctrine_outbox.py, in the bus at tools/factory/, pinned by each project through factory-pins; every project value sits in doctrine-outbox.config.json. A project never edits the tool; it sets `tool_pin` in its config once its pin is reviewed.
mechanism: per-project copies drift under tool-census. The mlv-app copy is the candidate: a config-driven superset of the old hook commands, a pin-aware hook and ref check (doctrine-outbox/README.md), and a `validate` refusal of a ruling candidate with no `touches/supersedes:` list of rule ids or bus paths at a given bus clone's tip, read once per item. No `tool_pin` behaves as before.
applies: mlv-app, airmypc, agent-bridge, conjugal
check: on the bus run `node tools/tool-census.mjs`; once projects pin and drop their copies, the family reads 1 distinct version. In MLV-App `py -3 -m pytest -q tests/coordination/test_doctrine_outbox_hooks.py -k pin` pushes through the hook with no copy.
supersedes: mlv-app/one-config-driven-doctrine-outbox-ruling-supersedes-1 (its digest)
evidence: measured
- **Adopt:** bus steward adds tools/coordination/doctrine_outbox.py as tools/factory/doctrine_outbox.py, byte for byte; sha256 of its LF bytes 3fe7827b4908b50d6fdda0fe98cdf3d2c31f4f44d44ed448efd82cd13c19f8ca.
- **Pin:** each project reviews that bus SHA, then runs `python factory-pins/pin-runner.py pin doctrine-outbox --commit <bus-sha> --path tools/factory/doctrine_outbox.py --reviewer <who> --reason <why>`, runs it as `python factory-pins/pin-runner.py run doctrine-outbox -- --config doctrine-outbox.config.json <command>`, sets `"tool_pin": "doctrine-outbox"`, runs `install-hooks` that way once. OUTBOX-PIN-AWARE-TOOL-AT-REF-1 shipped the pin-aware hook; only after the pin is reviewed does a project delete its copy. Without `tool_pin` it KEEPS it.
- **Outbox:** outbox:438c85d9a9a914d8 mlv-app:1edef88f0792

## mlv-app/dot-is-advisory-factory-quality-compensates
rule: In mlv-app, CoS (Dot) review is advisory, never a merge precondition: the fleet CoS merge-gate is DISTINGUISHED here. Merge bar: two authenticated exact-head keys, green hosted CI, CLEAN, not draft, plus a third adversarial key on HIGH-RISK paths. The 24 h ACK/DISTINGUISH reply duty stays.
mechanism: Owner ruling 2026-10-20, verbatim: "I dont want dot to be a blocker. Dot's review is a nice to have but the software factory should be shipping good code. Id rather improve factory's quality than let dot be a blocker. Lets update the posture so we keep throughput and quality somehow". Compensation: (1) key3, primed with the key attack catalogue and the Dot record as data, on HIGH-RISK paths; (2) Dot findings naming a concrete defect become a fix round (open PR) or a P1 fix card plus revert card (merged PR); (3) 7-day escape metric, Dot-demonstrated defects on merged PRs plus reverts: above 2 widens the catalogue and the key3 path list.
check: git grep -n -i "never merge a card" -- CLAUDE.md AGENTS.md returns nothing
supersedes: none
evidence: reported
- **Outbox:** outbox:b71720954432baa5 mlv-app:b1230561f724

## mlv-app/per-turn-hook-tree-walks-grow-the-kernel-pool
rule: A hook or heartbeat that runs every turn or every few minutes must never walk the whole board tree. Govern git-ignored state through an explicit allowlist of roots (an unlisted tree is enumerated zero times, reported by name) and prune wholly exempt directories BEFORE descending. Bound receipt scans by a recency window on the receipt FILE's own mtime, never its directory's: on NTFS an in-place rewrite does not move the parent directory's mtime. Gate commits on RAM plus pagefile maximum, not RAM alone.
mechanism: Host up 6.8 days: paged pool 13.2 GB, nonpaged 5.0 GB (normal 1-2 GB) with 21.7 GB RAM free, while a `RAM - 4` commit gate refused lanes. A 3-minute xperf FILE_IO trace ranked the board heartbeat (4.47M file events), the Stop-hook doc-size check (6.1M) and a checkpoint run (5.2M) first; the heartbeat and doc-size check walked the whole board incl. its git-ignored state tree; the checkpoint scan was already bounded to run dirs at depth 0/1. Counted in-process 2026-10-22 (Python touches, not xperf events): doc-size 837,710 paths per run, 155,544 after pruning exempt trees, 47,215 after the allowlist; project tools/session-checkpoint.py 114,055 per Stop event (~4,700 opens), then 102,566 touches but 663 opens with a per-file 72 h filter (a directory-mtime filter reached 25,896 but lost a receipt rewritten in an older run dir). That project copy is not wired in any settings file today and who launched it in the trace is UNKNOWN; the live per-turn hook is user-scope ~/.claude/hooks/session-checkpoint.py, unchanged.
check: py -3 -m unittest tools.repo_hygiene.test_check_doc_size_walk tools.repo_hygiene.test_session_checkpoint_receipt_window (MLV-App). Elsewhere: read `\Memory\Pool Paged Bytes`; over about 4 GB, run the elevated FILE_IO trace and count `File*` events per process.
supersedes: none
evidence: measured
- **Outbox:** outbox:8d66845b16a4e41b mlv-app:75fe23b853ec

## mlv-app/one-config-driven-doctrine-outbox-sent-item-guard-1
rule: the fleet carries ONE doctrine_outbox.py, in the bus at tools/factory/, pinned by each project through factory-pins; every project value sits in doctrine-outbox.config.json. A project never edits the tool; it sets `tool_pin` in its config once its pin is reviewed.
mechanism: per-project copies drift under tool-census. The mlv-app copy is the candidate, with a pin-aware hook (doctrine-outbox/README.md). New: `check-commits` and the pre-push guard refuse a commit that edits an outbox item whose key the sent ledger records (SENT_ITEM_EDITED), since the new key republishes it. A new item naming it, as a complete token, on a `supersedes:` line is the one allowed edit; no ledger or one with no readable key is the typed skip sent-ledger-absent or sent-ledger-unreadable.
applies: mlv-app, airmypc, agent-bridge, conjugal
check: on the bus run `node tools/tool-census.mjs`; once projects pin and drop their copies, the family reads 1 distinct version.
supersedes: mlv-app/one-config-driven-doctrine-outbox-markup-forms-1 (its digest)
evidence: measured
- **Adopt:** bus steward adds tools/coordination/doctrine_outbox.py as tools/factory/doctrine_outbox.py, byte for byte; sha256 of its LF bytes e1951f901ab8ab30b81ecfd1777df6c9d351278a929faa969bbb2ec1009d4891.
- **Pin:** each project reviews that bus SHA, then runs `python factory-pins/pin-runner.py pin doctrine-outbox --commit <bus-sha> --path tools/factory/doctrine_outbox.py --reviewer <who> --reason <why>`, runs it as `python factory-pins/pin-runner.py run doctrine-outbox -- --config doctrine-outbox.config.json <command>`, sets `"tool_pin": "doctrine-outbox"`, runs `install-hooks` that way once. OUTBOX-PIN-AWARE-TOOL-AT-REF-1 shipped the pin-aware hook; only after the pin is reviewed does a project delete its copy. Without `tool_pin` it KEEPS it.
- **Outbox:** outbox:47de696f362d3324 mlv-app:34f0f4a88405

## mlv-app/one-config-driven-doctrine-outbox-sent-ledger-read-1
rule: the fleet carries ONE doctrine_outbox.py, in the bus at tools/factory/, pinned by each project through factory-pins; every project value sits in doctrine-outbox.config.json. A project never edits the tool; it sets `tool_pin` in its config once its pin is reviewed.
mechanism: per-project copies drift under tool-census. The mlv-app copy is the candidate, pin-aware (doctrine-outbox/README.md). One strict sent-ledger read now serves the drain, the kernel drain, debt and the SENT_ITEM_EDITED guard: no ledger is the skip sent-ledger-absent; one that cannot be stat-ed, opened or decoded exits 2 as sent-ledger-unreadable; any row without a 16-hex `key` exits 2 as sent-ledger-partial; a ledger with no rows is the skip.
applies: mlv-app, airmypc, agent-bridge, conjugal
check: on the bus run `node tools/tool-census.mjs`; once projects pin and drop their copies, the family reads 1 distinct version.
supersedes: mlv-app/one-config-driven-doctrine-outbox-sent-item-guard-1 (its digest)
evidence: measured
- **Adopt:** bus steward adds tools/coordination/doctrine_outbox.py as tools/factory/doctrine_outbox.py, byte for byte; sha256 of its LF bytes 20805eb68f1e678201bd382efee4a09a50206b8ee961aa1e925512f6287cefc9.
- **Pin:** each project reviews that bus SHA, then runs `python factory-pins/pin-runner.py pin doctrine-outbox --commit <bus-sha> --path tools/factory/doctrine_outbox.py --reviewer <who> --reason <why>`, runs it as `python factory-pins/pin-runner.py run doctrine-outbox -- --config doctrine-outbox.config.json <command>`, sets `"tool_pin": "doctrine-outbox"`, runs `install-hooks` that way once. OUTBOX-PIN-AWARE-TOOL-AT-REF-1 shipped the pin-aware hook; only after the pin is reviewed does a project delete its copy. Without `tool_pin` it KEEPS it.
- **Outbox:** outbox:a0695837f576726a mlv-app:c975f3c362ce

## mlv-app/one-config-driven-doctrine-outbox-comment-history-1
rule: the fleet carries ONE doctrine_outbox.py, in the bus at tools/factory/, pinned by each project through factory-pins; every project value sits in doctrine-outbox.config.json. A project never edits the tool; it sets `tool_pin` in its config once its pin is reviewed.
mechanism: per-project copies drift under tool-census. The mlv-app copy is the candidate, pin-aware (doctrine-outbox/README.md). This revision changes comments only: the round history and two commented-out `candidates.extend(...)` lines in `_remote_default_base` become one invariant line, so the single source carries no dead code. Behaviour is unchanged.
applies: mlv-app, airmypc, agent-bridge, conjugal
check: on the bus run `node tools/tool-census.mjs`; once projects pin and drop their copies, the family reads 1 distinct version.
supersedes: mlv-app/one-config-driven-doctrine-outbox-sent-ledger-read-1 (its digest)
evidence: measured
- **Adopt:** bus steward adds tools/coordination/doctrine_outbox.py as tools/factory/doctrine_outbox.py, byte for byte; sha256 of its LF bytes 2b772034ce668f18e8776933ecded511e325cdc20f5dee674ec4194523dcca4c.
- **Pin:** each project reviews that bus SHA, then runs `python factory-pins/pin-runner.py pin doctrine-outbox --commit <bus-sha> --path tools/factory/doctrine_outbox.py --reviewer <who> --reason <why>`, runs it as `python factory-pins/pin-runner.py run doctrine-outbox -- --config doctrine-outbox.config.json <command>`, sets `"tool_pin": "doctrine-outbox"`, runs `install-hooks` that way once. OUTBOX-PIN-AWARE-TOOL-AT-REF-1 shipped the pin-aware hook; only after the pin is reviewed does a project delete its copy. Without `tool_pin` it KEEPS it.
- **Outbox:** outbox:a9e0139d6d31cb0f mlv-app:d9a4160e9ebb

## mlv-app/agent-bridge-stop-hook-whole-tree-doc-size-sweep-25s
rule: agent-bridge owns this; MLV-App does not edit it. Its per-turn Stop hook must not run the full doc-size sweep. Check only documents changed this turn, or cache verdicts by (mtime, size), or run the full sweep at pre-push or on a schedule. Keep any walk pruned of exempt trees before descending (precedent mlv-app/per-turn-hook-tree-walks-grow-the-kernel-pool), and compare size before reading a 1 MiB prefix per file.
mechanism: Measured 2026-10-22, read-only, agent-bridge 3760d5de. `.claude/settings.local.json:27` registers `hook_doc_size.py --stop` as a Stop hook; `tools/hook_doc_size.py:117` runs `check_doc_size.py --sweep --quiet-ok`. One sweep: 23.6 s in-process, 25.4 to 26.3 s over three timed runs; 600,174 IO-Other ops (about 25,400/s), 501 MB read, 0 written; 7,276 files governed, 6,539 from an unpruned `rglob` of the git-ignored state tree (`tools/check_doc_size.py:424`). It exits 1, so `--quiet-ok` prints a 39 KB report each time. By code reading the cost is `is_wal_copy` (:238-263, opens every file, reads up to 1 MiB) and `nested_checkout_root` (:292). A host census ranked it first for IO Other at 23,676 ops/s.
check: run agent-bridge `check_doc_size.py --sweep --quiet-ok` in-process under `py -3 -I -B`, read `psutil.Process().io_counters()` and wall time. Fixed means under about 5 s and 100,000 other-ops per Stop event.
applies: agent-bridge, mlv-app
supersedes: none
evidence: measured
- **Outbox:** outbox:2a57003ad2dbd9f7 mlv-app:821102adca3d

## mlv-app/one-config-driven-doctrine-outbox-nlf-old-git-refuse-1
rule: the fleet carries ONE doctrine_outbox.py, in the bus at tools/factory/, pinned by each project through factory-pins; every project value sits in doctrine-outbox.config.json. A project never edits the tool; it sets `tool_pin` in its config once its pin is reviewed.
mechanism: per-project copies drift under tool-census. The mlv-app copy is the candidate, pin-aware (doctrine-outbox/README.md). This revision makes the bus read refuse, by name, a git that ignores GIT_NO_LAZY_FETCH (older than 2.44, or a version it cannot read) when the bus clone is a partial (promisor) clone, so a ruling-target check can never lazy-fetch from the bus's remote mid-lookup; a full bus clone, or a git that honours the variable, reads as before.
applies: mlv-app, airmypc, agent-bridge, conjugal
check: on the bus run `node tools/tool-census.mjs`; once projects pin and drop their copies, the family reads 1 distinct version.
supersedes: mlv-app/one-config-driven-doctrine-outbox-comment-history-1 (its digest)
evidence: measured
- **Adopt:** bus steward adds tools/coordination/doctrine_outbox.py as tools/factory/doctrine_outbox.py, byte for byte; sha256 of its LF bytes 4e29138114f4f6a04484605d11fcd3502f639eada1f6a84599b4a1f518411fa5.
- **Pin:** each project reviews that bus SHA, then runs `python factory-pins/pin-runner.py pin doctrine-outbox --commit <bus-sha> --path tools/factory/doctrine_outbox.py --reviewer <who> --reason <why>`, runs it as `python factory-pins/pin-runner.py run doctrine-outbox -- --config doctrine-outbox.config.json <command>`, sets `"tool_pin": "doctrine-outbox"`, runs `install-hooks` that way once. OUTBOX-PIN-AWARE-TOOL-AT-REF-1 shipped the pin-aware hook; only after the pin is reviewed does a project delete its copy. Without `tool_pin` it KEEPS it.
- **Outbox:** outbox:93777e2ae83d182e mlv-app:3582f955ad95

## mlv-app/check-doc-size-prune-before-descent-and-extra-roots
rule: A per-turn doc-size gate must not walk what it will never govern. In a worktree scan, prune a directory before descending when an exempt glob of the form <dir>/** or <dir>/* covers its whole subtree (an extra root at or below such a dir included), and let a config name extra_roots so only those directories plus the top-level files are walked.
mechanism: bus tools/factory/check-doc-size.py (c82bddb) enters every directory and filters by exempt afterwards: in mlv-app's own doc-size walk 837,710 paths per run, 155,544 pruned, 47,215 with roots. Pruning is verdict-neutral (fnmatch star crosses slash); other glob shapes still walk. extra_roots is a non-empty list, scan worktree only (else exit 2); a bad root is a typed note, never a crash.
applies: mlv-app, conjugal, cloudvore
check: git apply the pinned patch (see Adopt) to bus c82bddb, run tools/factory/check-doc-size.tests.py: old tool red 8 of 31, patched green 31 of 31; the 3 fixture configs print byte-identical output (sha256 pinned in the tests).
supersedes: none
evidence: measured
- **Adopt:** bus steward applies the 20744-byte patch (LF sha256 bcf0b273d00d8bb8143f6555b891ec185c71abaa6f3f6ba430cd2d2626d2e1b5), blob doctrine-outbox/20261023-bus-check-doc-size-predescent-prune-extra-roots-r3.patch at mlv-app commit 223a06460de78c819fb93d27738a9d51502977bc (not in the outbox: an item is a .md card of at most 2000 bytes), to bus c82bddbac001bfeb488493dc8910402753904ed8: check-doc-size.py git blob 62485339 to 10ecdde7, its tests git blob 71f36aed to e4d8b571.
- **Outbox:** outbox:baedc47635ca8347 mlv-app:56e990a4f1af

## mlv-app/worktree-remover-must-see-detached-drivers
rule: a remover that frees a lane worktree asks one shared live-reference guard right before it removes, and refuses on a live process naming the path (path-prefix match: lane-X-1 is never named by lane-X-10), on a live pid recorded in a run dir (pid file, child record, receipt pid) whose command line names the worktree or that run dir while the run dir names the worktree, and on any census failure (unknown is never free): a run-dir record or tie file that exists but cannot be read (a real lock, access denied, anything but "gone") refuses as rundir-census-failed naming the file and error class, and a tie scan that hits its file cap refuses the same way naming the run dir and the files read, never as absent evidence. Run-dir files are opened sharing ReadWrite|Delete: a log a live lane or detached driver merely holds open for writing is read, never refused, so an unrelated live run dir leaves other worktrees free. One typed REFUSED line, with reason=, per refusal.
mechanism: 2026-10-24 06:02Z a retention pass removed a worktree under a detached venue driver whose command line named only its run dir; the lane that launched it had exited (receipt complete). A command-line regex and a running-receipt check both read it as idle; the driver then logged "not measured" every 5 min for 40 min. In Invoke-VenueChain only, a missing driver script is now typed (VENUE_DRIVER_SCRIPT_MISSING path=) and stops the chain; lane-local drivers are not yet wired.
applies: mlv-app
check: in mlv-app, pytest tests/coordination/test_retire_lane_worktree.py -k "live_refusal or live_driver or prefix_sibling or census or dead_driver" (28 cases; the refusal cases were RED before their fix, the dead-driver, gone-record, other-worktree and write-held-log cases pin no over-refusal).
supersedes: none
evidence: measured
- **Outbox:** outbox:ae01969234b6ce0b mlv-app:3bb3ba38b0d5

## mlv-app/worktree-guard-unknown-holder-and-encoded-driver
rule: the shared live-reference guard a worktree remover calls is fail-closed on the holders it cannot read, not only on the ones it can: a live candidate whose cwd cannot be read (probe unavailable, or unreadable and not exempt by creation time or service owner) or whose -EncodedCommand does not decode refuses with a typed reason (cwd-unknown / cwd-probe-unavailable), and a run-dir driver's tie to its run dir is read over its command line with every -EncodedCommand argument decoded, so a run dir named only inside the base64 is a live driver. Only a remover that renames the root first (the rename settles an unreadable cwd) may defer the unreadable-cwd case; one that removes directly may not. Every tracked launch site that starts PowerShell from base64 or detaches a process is listed in a census test with the reason the guard still sees it.
mechanism: 2026-10-24 Dot reconciliation of PR #654: the guard built a list of unknown holders and never read it (FREE), and matched run dirs against the raw command line only, while agent tools and the lane job host launch `pwsh -EncodedCommand`. The census found one encoded lane launch on master (Invoke-Lane's Claude job host), safe because its child names the run dir through --settings and is recorded in <run dir>\<lane>-NNN.child.json.
applies: mlv-app
check: in mlv-app, pytest tests/coordination/test_retire_lane_worktree.py -k "b1_ or b2_ or launcher_census" (11 cases; the 6 refusal cases were RED before their fix, the older-than-worktree and other-worktree cases pin no over-refusal).
supersedes: none
evidence: measured
- **Outbox:** outbox:09193157673a89ba mlv-app:8ee5c0614305

## mlv-app/pr-provenance-is-a-receipt-bound-record-not-a-footer
rule: a PR states which provider and exact model played each role (implementer, fixer, reviewer keys, third key, verifier, execution agent) from the lane receipts, not from an authorship footer: provider from the receipt engine, the resolved model id (or "claimed: <requested>" when none was resolved), and the full 40-hex SHA each row is bound to (a key's subject_sha, a producer's DONE sha), with "unbound" when it cannot be derived and "stale (other head)" when it names an older head. A footer is "claimed by footer, unverified". CI is listed apart as not a model. The section is record-only: a missing or stale one prints one advisory WARN line and never blocks a merge.
mechanism: 2026-10-24 the owner asked (dot notice on MLV-App #660) for provider and model per role on every PR, because a Co-Authored-By footer names whatever the committer typed and says nothing about who reviewed which head. The receipts already carry engine, resolved model and effort; a key's verdict JSON carries subject_sha. tools/coordination/pr_topology.py renders, splices and checks the block (check always exits 0).
applies: mlv-app
check: in mlv-app, py -3 -m unittest tests.coordination.test_pr_topology (27 cases: render roles and stale rows, claimed/unreadable receipts, idempotent splice, check exit 0 on every input, malformed markers plus a stale head never read as ok).
supersedes: none
evidence: measured
- **Outbox:** outbox:cb67bfd80ac211a5 mlv-app:345bc296ccc3
