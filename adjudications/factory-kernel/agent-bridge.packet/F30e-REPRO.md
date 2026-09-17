REPRODUCED: YES

Live driver: Invoke-ClaudeLane.ps1  sha256=A3D9152F61E97067569C3ECCD81888B06207A645BFA22E1A452A837FCD1FEF2A (prefix A3D9152F confirmed)
Extraction anchors: '$timedOut = $false' (once, pre-loop) .. 'exit $exit' (final line), 11033 chars.

ARM 1 -- THROW (Test-LaneDispatchAllowed throws on its first in-loop call):
  harness exit code: 1  (watchdog fired: False)
  receipt written: False  outcome: 
  fake child alive after harness exit: True (pid 55512)
  fake grandchild alive after harness exit: True (pid 63004)
  stderr (first 300 chars): Exception: <user-home>\AppData\Local\Temp\F30e-repro-2d27c68ddc314182abdff3e3f8b91f4d\H-throw\harness.ps1:37
Line |
  37 |  … ]$InFlight) throw 'F30e harness: dispatch gate stub threw (simulated  …
     |                ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     | F30e

ARM 2 (CONTROL) -- DENY / kill switch (Test-LaneDispatchAllowed returns allowed=$false):
  harness exit code: 123  (watchdog fired: False)
  receipt written: True  outcome: STOPPED_BY_KILL_SWITCH
  fake child alive after harness exit: False (pid 49648)
  fake grandchild alive after harness exit: False (pid 15908)

Commands:
  Get-FileHash -LiteralPath '<agent-bridge>\.claude-state\coordination\automation\Invoke-ClaudeLane.ps1' -Algorithm SHA256
  Start-Process -FilePath $PWSH -ArgumentList '-NoProfile','-File','<harness.ps1>' (per-arm harness under $env:TEMP\F30e-repro-*)
  watchdog: 90s poll loop; Kill($true) + cleanup of throwaway root on completion.
