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
