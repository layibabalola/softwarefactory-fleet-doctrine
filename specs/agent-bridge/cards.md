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
