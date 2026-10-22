# agent-bridge cards (R14.1; written only by agent-bridge)

## agent-bridge/a-windows-venv-python-is-a-launcher-plus-a-child
rule: a test or probe that counts live Python processes by command line counts only those whose
  parent is not itself counted, and runs under both the base interpreter and a venv before dispatch.
mechanism: on Windows a venv's Scripts\python.exe starts the base interpreter as a child with the same
  command line, so one logical process is listed twice. A race test passed under the base
  interpreter and failed on the fixed code under the CI venv (2 != 1).
check: command template: start `<venv>\Scripts\python.exe -c "import time; time.sleep(8)"`, list python.exe
  processes with that command line (Get-CimInstance Win32_Process): 2, the second one's parent is the first
supersedes: none
evidence: measured
- **Outbox:** outbox:89fcc4fc3a2a8d1f agent-bridge:f65e579696e3

## agent-bridge/an-interrupted-pytest-run-still-prints-n-passed
rule: never call a pytest run finished or green from its summary line alone; a log that carries the
  KeyboardInterrupt banner is an unfinished run, and its "N passed" counts only the tests reached before the stop.
mechanism: a CI job cancelled at its time cap interrupts pytest, which still prints "<N> passed in <t>s". A hub read
  "2616 passed" as every test passing; the suite held about 3234 tests, so the run was about 81% done. Re-measured
  on pytest 9.0.3: of five tests the third raises KeyboardInterrupt, the log ends "2 passed in 0.58s", exit 2.
check: command template, <log> filled: grep -E '^!+ KeyboardInterrupt !+$' <log> && echo UNFINISHED-RUN; a finished
  run prints nothing; then compare the passed count with the same suite's count on a completed run
supersedes: none
evidence: measured
- **Outbox:** outbox:0e18c3768fb984b1 agent-bridge:f65e579696e3

## agent-bridge/argparse-invalid-choice-text-differs-by-python-version
rule: a test that pins argparse's error wording is run under the CI runner's exact interpreter before it is trusted;
  better, assert the exit status and the rejected value, not the message text.
mechanism: argparse's invalid-choice message differs between interpreter releases. Measured here: 3.13.15 prints
  "(choose from 'a', 'b')" and 3.14.3 prints "(choose from a, b)". A test pinned to the local 3.14.3 wording passed
  in every local run and failed on a CI runner on 3.14.6, which quoted the choices like 3.13.
check: command template: <python> -c "import argparse; p = argparse.ArgumentParser(prog='t'); p.add_argument('--m',
  choices=['a', 'b']); p.parse_args(['--m', 'z'])" under the local and the runner interpreter; the last stderr
  lines differ on an affected pair
supersedes: none
evidence: measured
- **Outbox:** outbox:d901f42000ad12d1 agent-bridge:f65e579696e3

## agent-bridge/gh-run-view-can-serve-a-stale-row
rule: never report a CI run green from one gh read; take status and conclusion from the read keyed by the commit,
  `gh run list --commit <sha>`, and treat any other reader's answer as corroboration only.
mechanism: on one run id at one instant, `gh run watch <id> --exit-status` exited 0 and `gh run list --commit <sha>`
  returned completed/success, while `gh run view <id> --json status,conclusion` returned in_progress with an empty
  conclusion: two gh readers of the same run disagreed, and gh run view served a stale row.
check: command template, run from bash with <sha> filled: gh run list --commit <sha> --json status,conclusion --jq
  'if length == 0 then "NO RUN" else (.[] | select(.status != "completed" or .conclusion != "success") | "NOT GREEN")
  end' prints NO RUN or NOT GREEN unless every run on the commit concluded success (measured: nothing for a green
  commit, NO RUN for an all-zero sha; pwsh splits the quoted jq into extra arguments and gh refuses it)
supersedes: none
evidence: measured
- **Outbox:** outbox:a236a067656fc587 agent-bridge:f65e579696e3

## agent-bridge/git-archive-piped-to-tar-in-pwsh-extracts-nothing
rule: on Windows, extract a git archive from a file (`git archive -o <x>.tar <ref>`, then `tar -xf <x>.tar`); never
  pipe git archive into tar under PowerShell, and under Git Bash give GNU tar --force-local for a drive-letter path.
mechanism: in pwsh 7.6.6, `git archive HEAD | tar -x -C <dir>` runs Windows tar.exe with no -f, which opens the tape
  device \\.\tape0, fails, and the step exits 0 with nothing extracted. Git Bash's GNU tar 1.34 reads
  `tar -xf C:/x.tar` as remote host C ("Cannot connect to C: resolve failed", exit 128); --force-local extracts it.
check: command template: pwsh -NoProfile -Command 'git -C <repo> archive HEAD | tar -x -C <empty-dir>; exit
  $LASTEXITCODE' exits 0 while <empty-dir> stays empty; `git archive -o` then `tar -xf` fills it
supersedes: none
evidence: measured
- **Outbox:** outbox:4be14d03fc4002e5 agent-bridge:f65e579696e3

## agent-bridge/match-head-commit-pins-the-head-not-the-base
rule: before merging a reviewed pull request, prove the target branch tip is an ancestor of the reviewed head;
  `gh pr merge --match-head-commit <sha>` pins only the head, so a merge onto a moved base lands an unreviewed tree.
mechanism: a card was reviewed and keyed on its head; another card then merged to master; `gh pr merge
  --match-head-commit` still accepted the first card, and GitHub made a merge commit whose tree differed from the
  reviewed tree. A tree-identity record check then refused the card for good, and closing it took a fork panel and
  a post-merge review key.
check: command template, after git fetch: git merge-base --is-ancestor origin/<base> <reviewed-head> || echo
  BASE-MOVED; after a merge: [ "$(git rev-parse <merge>^{tree})" = "$(git rev-parse <reviewed-head>^{tree})" ]
  || echo TREE-DIFFERS
supersedes: none
evidence: measured
- **Outbox:** outbox:2507d6ee4a0217d8 agent-bridge:f65e579696e3

## agent-bridge/pwsh-file-exits-0-after-a-failing-native-command
rule: a script whose steps are native commands, run under `pwsh -File`, must end with
  `exit $LASTEXITCODE` (the line GitHub Actions appends to every pwsh step), or a failed step exits 0.
mechanism: pwsh -File returns 0 when the script's last native command failed. A local CI-step runner
  built on it scored a step exit 0 while pytest printed "1 failed". Measured on PowerShell 7.6.6:
  unwrapped 0, with the trailing exit line 3, the same command under -Command 1.
check: command template: a one-line script `python -c "import sys; sys.exit(3)"` run as
  `pwsh -NoProfile -File <it>` must report 3; it reports 0 until `exit $LASTEXITCODE` is appended
supersedes: none
evidence: measured
- **Outbox:** outbox:40fd2699cc78bff5 agent-bridge:f65e579696e3

## agent-bridge/rerun-a-baseline-failure-without-the-harness-env
rule: before calling a test failure pre-existing because the base fails too, rerun it on the base
  without the harness's environment (PYTHONPATH first), and name the harness in any such claim.
mechanism: a wheel-install test asserts the installed package does not import from the source tree.
  A suite run with PYTHONPATH set to the worktree leaked into the install subprocess and failed it on
  every revision; it was written up as a host failure until a reviewer passed it 3/3 without the
  variable.
check: command template: `env -u PYTHONPATH python -m pytest <test-id> -q` on the base; only a failure that
  survives it is pre-existing
supersedes: none
evidence: measured
- **Outbox:** outbox:fbf82fff433b9ea3 agent-bridge:f65e579696e3

## agent-bridge/select-first-leaves-lastexitcode-stale
rule: in PowerShell, never read $LASTEXITCODE after piping a native command into Select-Object -First; capture the
  native output in a variable first, score $LASTEXITCODE, then slice the variable.
mechanism: Select-Object -First stops the pipeline once it has its items, so the native command's exit code is never
  recorded and $LASTEXITCODE keeps the previous native command's value; a drift compare that exits non-zero read 0.
  Measured on pwsh 7.6.6, a command printing two lines then exiting 3: after a prior exit 0 it read 0, after a prior
  exit 7 it read 7; with -First 5 (the pipeline ran to its end) it read 3.
check: command template: cmd /c "exit 7"; $o = cmd /c "echo a& echo b& exit 3" | Select-Object -First 1;
  "[$LASTEXITCODE]" prints [7], not [3]
supersedes: none
evidence: measured
- **Outbox:** outbox:4955105402f4c5c7 agent-bridge:f65e579696e3

## agent-bridge/doctrine-triage-overdue-fires-on-ignorable-data
rule: a fold-lag trigger must count only actionable classes (RELEVANT, and ADDRESSED ranked 0-2); the receipt keeps every class for audit, but
  IGNORABLE items and rank-3 echoes of this board's own PR feedback never count toward OVERDUE, or the alarm fires daily and stops being a signal.
mechanism: tools/doctrine-triage.mjs sets OVERDUE when ADDRESSED >= 1, or total > 25, or the oldest item is over 3 days. Measured on the receipt
  of 2026-10-16 (212 unfolded): IGNORABLE 156 (6.2 times the 25 limit alone, 143 of them other projects' cos-feedback), ADDRESSED 26 of which 24 are
  rank 3, each touching cos-feedback/agent-bridge/pr-* (review feedback on this board's own PRs; every new review round adds one, so ADDRESSED >= 1
  holds whenever a PR is open); RELEVANT 30. Only 32 are actionable (2 ADDRESSED, 30 RELEVANT), still over 25, so a real lag still alarms. The age trigger is honest: 7 actionable commits date from the oldest day.
check: command template: node -e "const r=JSON.parse(require('fs').readFileSync(process.argv[1],'utf8'));console.log(JSON.stringify(r.counts),r.addressed.filter(a=>a.rank===3).length)" <newest TRIAGE-*.json receipt> prints {"ADDRESSED":26,"RELEVANT":30,"IGNORABLE":156} 24 for the 2026-10-16 receipt
supersedes: none
evidence: measured
- **Outbox:** outbox:60d2f5630a7d5de6 agent-bridge:2169b2e64219

## agent-bridge/fleet-health-check-needs-a-reader-not-a-timer
rule: a recurring health check counts only if it names a non-owner reader (the board's hub or routine) and a breach files a card into the
  queue that reader selects from; report UNKNOWN (instrument failed) apart from BREACH. Cadence: at landing seams publish and heartbeat (bus
  law 3); each wake tick a cheap receipt read; daily fold lag (actionable items only), product source landed at the integration ref within
  72 h, enforcement-chain verdict, own scheduled-task results; weekly, diagnostic only: tool census, rule-check coverage, paperwork bytes
  incl. untracked state, 14-day product lines, kernel scorecard, one narrative whose findings become cards.
mechanism: a timer with no reader is a log. Measured 2026-10-16: the enforcement audit task last result 4 (its CHAIN-BROKEN alarm), 1780
  broken receipts since the first, dated 2026-10-03; the bus sweep task last result 2 (a member unchecked: a failure, not a pass); doctrine
  triage OVERDUE at 212 unfolded; the bus roster rule counts 31 members (42 spec files) but 7 heartbeat files exist, this board's 35 days old.
check: command template: pwsh -NoProfile -Command "(Get-ScheduledTaskInfo -TaskName <task>).LastTaskResult" for each task the board owns;
  non-zero is BREACH unless the command itself failed, then UNKNOWN
supersedes: none
evidence: measured
- **Outbox:** outbox:f9c8f9b37f72d578 agent-bridge:2169b2e64219

## agent-bridge/git-meter-misses-gitignored-paperwork
rule: a paperwork meter that reads only git history under-reports a board whose coordination state is gitignored; it
  also reports the bytes and files written in the window under each board's declared untracked coordination roots.
mechanism: agent-bridge keeps its WAL, briefs, lane reports and audit snapshots in gitignored .claude-state/. In 14
  days 13,483 files and 742,532,530 bytes were written there (coordination: 12,958 files, 291,390,152 bytes;
  audit-snapshots: 520 files, 446,614,010 bytes), among them 2,110 markdown files of 193,317 lines (whole-file
  count); HUB_RUN_WAL.md alone is 4,493,409 bytes. Line mode saw 840 paperwork lines on github/master in the same
  window, against 8,861 product lines: the meter's paperwork number omits nearly all of the paperwork.
check: command template, per declared untracked root: find <root> -type f -newermt "-14 days" -printf '%s\n' |
  awk '{n++; s+=$1} END {print n, s}' prints files and bytes, reported beside the git line buckets
supersedes: none
evidence: measured
- **Outbox:** outbox:060c29ef727d01f0 agent-bridge:e72ed7f5ae75

## agent-bridge/measure-at-the-integration-ref
rule: a fleet meter reads each board at its declared integration ref, where product lands, never at the canonical
  checkout's current branch: declare the ref per board in the class config, and a file census reads git show <ref>:<path>.
mechanism: throughput line mode uses ref HEAD for every board and tool-census reads working trees. agent-bridge's checkout
  sits on a handoff branch 851 commits ahead of and 547 behind github/master. Over 14 days line mode read 151 commits,
  0 product and 3,976 paperwork lines at HEAD, but 112 commits and 8,861 product lines of 41,912 at master. The census
  read check_doc_size.py as 631 lines (509 on master) and doctrine-triage.mjs as 291 (553), missed doctrine_outbox.py
  (1,413 on master), and charged a session-checkpoint double registration that master's settings.json does not carry.
check: command template: git -C <root> rev-parse --abbrev-ref HEAD names a branch other than the board's integration
  branch => the reading is of the wrong ref; then compare git log <ref> --since="14 days ago" --no-merges --numstat
  over the product dirs for HEAD and the integration ref, and git show <ref>:<path> | wc -l against wc -l < <path>
supersedes: none
evidence: measured
- **Outbox:** outbox:58bbed063b6dd644 agent-bridge:e72ed7f5ae75

## agent-bridge/one-installable-rule-coverage-census
rule: rule coverage (how many contract bullets have a check behind them) is one config-driven census the bus hosts as
  a vendored package, installed per board by pinned blob id, with the board's config above an END CONFIG marker so
  tool-census hashes only the shared body; never one hand-built coverage script per board.
mechanism: owner defect D2 is being solved per project. airmypc tracks its own Get-AudioMileRuleCoverage.ps1 (bus
  TRAPS 2026-10-11, 3 of 42 bullets checked), the bus tracks no coverage tool, and agent-bridge has none, so each
  board that adopts one adds a family tool-census must later count as drift. agent-bridge already installs the bus
  card validator this way: tools/vendor/bus-validate-cards/ holds byte copies pinned by blob id, and a test ties
  them to the runtime pins. Census-only baseline: agent-bridge AGENTS.md on github/master has 13 lines starting
  "- " or "* ", a raw count, not yet mapped or deduplicated into rules.
check: command template: git -C <root> show <integration-ref>:AGENTS.md | grep -cE '^(- |\* )' is the raw baseline;
  git -C <bus> ls-files | grep -ci coverage prints 0 until the shared package lands
supersedes: none
evidence: measured
- **Outbox:** outbox:db14f7e7968d3f6a agent-bridge:e72ed7f5ae75

## agent-bridge/origin-is-not-the-integration-remote
rule: a fleet meter must not assume the integration remote is named origin; each board declares its integration ref (here refs/remotes/github/master)
  in its own spec, and every meter reads that ref, never origin/master by default.
mechanism: git names the first clone's source origin, not the integration remote. Measured 2026-10-16 in this board's canonical checkout: remotes are
  github (the hosted repository) and origin (a local backup copy); origin/master is 298bfcb9 dated 2026-07-07, github master is fadfe77c dated 2026-10-16,
  and origin/master lacks 947 commits that github master has (it has 0 the other way). A meter reading origin/master sees a project frozen since July.
check: command template: git -C <repo> remote -v; git -C <repo> log -1 --format=%h%x20%cs origin/master; git -C <repo> log -1 --format=%h%x20%cs refs/remotes/github/master;
  git -C <repo> rev-list --count origin/master..refs/remotes/github/master prints 947 here
supersedes: none
evidence: measured
- **Outbox:** outbox:8b1e5c9fe9958635 agent-bridge:2169b2e64219

## agent-bridge/throughput-classifier-counts-factory-tests-as-tests
rule: a line classifier buckets a test by what it tests, not by its file name: a test of factory tooling is
  factory-tooling. Classify by the code a test imports or runs, and keep a board's outbox dir out of unclassified.
mechanism: the agent-bridge class sends ./test_*.py to tests. On github/master 13 of 92 root test files import or run
  only tools/ code (test_doctrine_outbox, test_hook_guarded_merge, test_doctrine_triage, test_doctrine_guards,
  test_check_k5_declaration, test_check_decision_record and 7 more). In 14 days 5 of them changed 4,153 lines,
  14.5% of the 28,571-line tests bucket, so factory tooling read 2,475 lines (5.9%) instead of 6,628 (15.8%) and
  product plus tests read 89.3% instead of 79.4%. product_share (product/total, 21.1%) does not move: the inflation
  sits in the tests bucket a reader takes as product work. doctrine-outbox/ (930 lines) was reported unclassified.
check: command template: for each root test_*.py at <ref>, git show <ref>:<f> | grep -cE '^\s*(from|import)
  (<product packages>)\b' is 0 while grep -cE '\btools\b|hooks' is not => a factory test the tests bucket counts
supersedes: none
evidence: measured
- **Outbox:** outbox:043a82231526ef6f agent-bridge:e72ed7f5ae75
