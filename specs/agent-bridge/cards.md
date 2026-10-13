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
