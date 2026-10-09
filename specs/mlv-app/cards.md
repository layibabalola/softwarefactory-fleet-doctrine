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
