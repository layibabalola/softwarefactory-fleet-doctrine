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
