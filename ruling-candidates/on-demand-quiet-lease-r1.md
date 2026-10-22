# Ruling candidate: on-demand quiet lease R1

Status: **PROPOSED ONLY. NOT YET A RATIFIED RULING OR PROJECT RUNTIME AUTHORITY.**

Filed 2026-10-22 by Cloudvore on BACHELOR, at the owner's request.

## Problem

A benchmark or other timing-sensitive job needs a quiet shared machine. On BACHELOR, MLV-App's bench legs count only
when machine CPU is at or below 20 % at leg start.

The first proposal was a fixed daily window (12:00-14:00 UTC, with no new admissions from 11:30). It failed on
measurement:

- **The sampled hourly averages show no reliably quiet clock window.** Heavy-slot use by projects other than MLV, measured from the gate's shadow log over
  2026-10-15..22, was flat at 0.7-1.0 slot-hours in every hour of the day. The agent factories run around the clock.
- **The cutoff misses long runs.** A fixed cutoff does not stop a long run admitted just before it. A key review
  admitted at 11:26 UTC, 4 minutes before the proposed cutoff, held a slot until 13:24 UTC.
- **It costs too much.** The window plus its lead time takes 5 slot-hours a day from every other project (2.5 h on
  2 slots), whether the benchmark has work or not. The benchmark's own holds averaged about 2 slot-hours a day.
- **Demand was invisible.** The benchmark agent probed the gate's `status` every minute and never queued a ticket.
  Its gate log (as read by a review agent) shows status timeouts at 13:31-13:50 and 16:20-17:40 UTC. Two plausible
  contributors: its task runs at BelowNormal priority, and the status path made unbounded `tasklist` and
  `nvidia-smi` calls.

## Proposed portable law

A job that needs a quiet machine **requests a lease from the machine's admission gate when it has work**. It never
relies on a clock window.

1. **The lease is an exclusive queue ticket, never a side file the gate does not read.**
   - Wrappers that honour exclusive holders refuse to join an active lease.
   - Waiters running an older copy of the gate still apply the old pass-window rule, and may be admitted past a
     pending lease for up to 20 minutes. A project that pins a copy of the gate must move to the version that
     closes this (heavy-slot 2.4.1 on BACHELOR) before relying on the lease.
2. **While pending, no normal-priority shared ticket queued behind the lease is admitted past it.**
   - The pass window does not apply to a lease ticket.
   - Running holders finish normally and are never killed.
   - Tickets the gate already ranks first are still served first. On BACHELOR these are `--priority high`, key
     reviews while a kernel hold exists, and shared tickets that have waited longer than 45 minutes.
   - The request gives up after a bounded pending time and exits with the gate's standard refusal code.
3. **While active, no new top-level run is admitted.**
   - Runs nested inside any current holder (the lease's own legs, or a holder that started before the lease) pass
     through, as nested runs always do.
   - The holder renews on a heartbeat. A lease is exclusive only while its pid is alive, its process creation time
     matches the recorded value, the last renewal is fresh, and the expiry has not passed. Otherwise it is demoted
     to an ordinary holder.
   - Liveness by pid alone is wrong: the requesting agent lives for days.
4. **Hard caps live in one config file:** maximum lease length, maximum pending time, cooldown between leases,
   maximum share of any 3-hour period, and renewal staleness.
   - A missing or invalid config disables the lease and leaves everyone else unchanged.
   - `"enabled": false` ends an active lease within seconds.
   - The agent-side hook reads the same file for its caps.
5. **Agents cooperate through an advisory flag.**
   - A tool-call hook stats one flag file. While the lease is active, it refuses direct heavy commands (builds, test
     suites, mutation harnesses, review agents) and tells the agent to queue them in the background through the gate.
   - It bounds the lease by the time remaining, not the time since the request, so a lease that waited in pending
     is still honoured.
   - It fails open on every error, stale renewal, dead holder or expiry. It is a courtesy, not enforcement.
   - The gate's refusal to admit is the enforcement, and the benchmark keeps its own CPU check at each leg start.
6. **Status reads are bounded.** They raise their own priority to Normal, run each external probe under a deadline
   without draining its pipes, cache within the call, and print only after everything is computed.

The trade-off adopters accept: the blocking the lease itself imposes on normal shared work queued behind it is
bounded nominally by the pending cap plus the lease length (30 + 45 minutes on BACHELOR). Total admission delay can
be longer, because existing holders, priority work and thermal gates still apply. Only work behind the lease waits, and only while a
benchmark actually has work.

## Measured on BACHELOR, 2026-10-22

- **heavy-slot 2.4.0:** 7 of 9 full runs of six test files were green (178 checks per run). Runs 2 and 6 each failed
  one selftest timing check under machine load; the A/B below shows the same check failing on 2.4.0 itself under load.
  `status` output without a lease was byte-identical to 2.3.1 on sandbox fixtures and in one diff on live state.
  One live `status` call under load took 2.8 s.
- **A live lease exposed a gap.** A pending live lease, requested at 21:02 UTC, inherited the gate's 20-minute pass
  window. A shared run joined past it at 21:10 UTC, and the lease was refused with the standard code at its
  600-second pending limit.
- **heavy-slot 2.4.1 fixes it:** a lease ticket is never passable. Its pin test fails on 2.4.0 and passes on 2.4.1.
  An A/B run of the timing-sensitive test files on 2.4.0 and 2.4.1 under the same load was incomplete (round 1 of
  both, round 2 of 2.4.0). Some failure kinds also occur on 2.4.0 itself (selftest admit-timeout window,
  short-exclusive overrun timing, lease renew); 2.4.1 also failed one status-lifetime check (8.18 s against 8 s).
  Load sensitivity is plausible; a regression is not ruled out.
- **Agent hook:** 52 cases passed. Its cost over the previous dispatcher with the check installed, measured
  in-process with no flag, was 0.68 ms (light commands) and 0.08 ms (heavy). A second pin test proves a lease that
  waited 10 minutes in pending is honoured, and fails on the first version of the hook.
- **Live check of 2.4.1 (22:22-22:52 UTC):** a 5-minute lease request with a 30-minute pending limit; the renewal
  loop slept 50 s between iterations (recorded renewals were 56-73 s apart). The only run admitted while it was pending was the one already queued ahead of it, so nothing passed
  the lease. The lease never went active: a shared run that had held the other slot since 21:31 UTC was still running
  at the pending limit, and the request was refused cleanly with its flag removed. The active path is covered only by
  the sandbox tests so far. **A lease cannot drain a holder that runs longer than its pending limit;** the remedy is
  the gate's existing rule of one admission per unit of work, not a longer pending cap.

Note: the gate's shadow log names a field `utc` that actually holds local time. The lease events carry epoch `ts`.

## Adoption check another project can run

1. Request a short lease while the machine holds a shared run.
2. Queue a second normal-priority shared run behind it.
3. Assert that the second run is not admitted until the lease ends or is refused.
4. Keep the first run going beyond the pending limit, then assert that the lease is refused with the standard code.
5. Assert that `status` output without a lease is byte-identical to the previous version.

## Not covered

Load that never goes through the gate: orphaned processes, antivirus scanning, scheduled guardians, and interactive
agent shells. Lowering that floor is a separate job.
