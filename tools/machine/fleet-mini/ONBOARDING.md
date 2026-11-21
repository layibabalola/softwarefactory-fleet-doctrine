# First contact: onboarding a NEW Windows mini so the fleet can reach it

`README.md` here covers the baseline and the check that proves it. This runbook covers the step before that,
which the baseline tool cannot do: **a fresh Windows install has no SSH server**, so no other fleet machine can
reach it. Until something runs on its own console, the mini has no remote way in at all.

Written 2026-11-20 from onboarding the fourth fleet mini. Every trap in the table below happened on that run
and cost time; the procedure is ordered so none of them can happen again. Law 1 holds: nothing here runs on a
machine until its owner runs it from a commit they reviewed. Placeholders: `<new-mini>` (its ssh alias),
`<fleet-lan-profile>` (the Windows network profile name the existing minis use for the home LAN),
`<tailnet>` (the tailnet's DNS suffix), `<admin-user>` (the account that signs in at the console).

## The path

The owner pays attention twice (one paste, then a TeamViewer reconnect); the wall clock is about 15 minutes.

1. **Owner, on the new mini:** Windows set up, signed in as `<admin-user>` (a local administrator), HDMI emulator
   or capture device plugged in, TeamViewer installed with unattended access. Connect to it over TeamViewer.
2. **Agent, on an existing mini (the driver):** on every existing mini, add a `Host <new-mini>` stanza to
   `~/.ssh/config` with the LAN address for now, **above** any tool-managed block, after a `.bak-<UTC>` copy.
   Start a watcher that polls TCP 22 on the LAN address AND the tailnet address and runs the check in step 5
   when either opens: a PowerShell loop run in the background, not a shell `sleep` loop.
3. **Owner, on the new mini:** open PowerShell **with Run as administrator** and paste the first-contact script
   (one block wrapped in `& { }`, so it runs as one command and `return` works). It does, in this order:
   1. sets the `<fleet-lan-profile>` network profile to **Private**;
   2. installs the toolchain (below) **before** sshd, so the default shell can be the machine pwsh 7;
   3. removes a GitHub-preview OpenSSH MSI if present, then installs the **Windows built-in** OpenSSH server with
      `dism.exe`, sets it Automatic, opens firewall rule `OpenSSH-Server-In-TCP` on **all** profiles, and sets
      `HKLM\SOFTWARE\OpenSSH\DefaultShell` to `C:\Program Files\PowerShell\7\pwsh.exe`;
   4. appends the fleet's public keys to `%ProgramData%\ssh\administrators_authorized_keys` (ACL: Administrators
      and SYSTEM only) and to `~/.ssh/authorized_keys`, and makes this machine's own fleet key;
   5. applies the baseline values from `FleetMini.psm1` (it is the owner's elevated console, so this is the
      owner's apply step) and the TeamViewer panel setting (below);
   6. ends with a **PASS** or a red **FAIL** list. It must refuse to say PASS unless something listens on 22,
      sshd is the built-in binary, and its start mode is Auto.
4. **Owner:** if it says so, `tailscale up` and sign in to the fleet tailnet.
5. **Agent:** the watcher fires. From **every** existing mini: a BatchMode login to `<new-mini>`, then
   `Test-FleetMini.ps1 -Hosts <new-mini>`; read the TeamViewer values back; then the reverse mesh (the new mini's
   public key into each existing mini's `administrators_authorized_keys`, after a backup; stanzas for the existing
   minis in the new mini's `~/.ssh/config`), and a login from the new mini to each. Expect every `user` and
   `admin` item OK from every mini. Then switch the stanzas to `<new-mini>.<tailnet>` so a DHCP change cannot
   break them.
6. **Owner items the check still lists** (never automated): Smart App Control off, Autologon (LSA secret),
   `claude auth login`, `codex login`, `gh auth login`, Developer Mode.
7. Add the new mini's public key to the key list the next first-contact paste carries.

**Toolchain, exact winget ids** (as on the existing minis): `Microsoft.PowerShell` **with
`--installer-type wix --scope machine`**, `Git.Git`, `GitHub.cli`, `OpenJS.NodeJS.LTS`, `Microsoft.DotNet.SDK.10`,
`Python.PythonInstallManager` then `py install 3.14`, `Tailscale.Tailscale`, `TeamViewer.TeamViewer`; then
`npm install -g @anthropic-ai/claude-code @openai/codex`.

**TeamViewer parity.** "The TeamViewer panel did not minimize when I connected" is
`HKCU\Software\TeamViewer\AutoHideServerControl = 1` in the console user's hive (with `MinimizeToTray = 1`).
Measured equal on the existing minis; it takes effect from the next connection. TeamViewer version and
`Security_ActivateDirectIn` differ across minis today and are not part of parity.

## Traps hit, and the rule each one became

| # | symptom | cause | rule |
|---|---|---|---|
| T1 | port 22 stayed closed after the first paste, though Tailscale came up | `Get-WindowsCapability` / `Add-WindowsCapability` threw **"Class not registered"** (broken DISM PowerShell module) and the script carried on | install with **`dism.exe /Online /Add-Capability /CapabilityName:OpenSSH.Server~~~~0.0.1.0`**, which worked; the script ends in FAIL unless 22 listens |
| T2 | fallback `winget install Microsoft.OpenSSH.Preview` worked, but ssh sessions had **no user PATH** (npm globals and Python "missing"; the check reported DRIFT) | the GitHub preview build of sshd | never install the preview; remove it if present. The built-in server loads the user PATH like the other minis |
| T3 | `dism.exe` run from an ssh session: **Error 5**, at High integrity | DISM servicing refuses an ssh network logon | run DISM from the owner's console, or from a one-shot SYSTEM scheduled task |
| T4 | after DISM ran while the preview sshd was live: `sc config sshd` -> **1072 "marked for deletion"**, start mode stuck at Manual | the capability deleted and re-registered the `sshd` service while the preview process held it; the next stop or reboot would leave **no** sshd | stop sshd and uninstall the preview **before** DISM. Repair a machine already in that state from a SYSTEM task that: backs up `%ProgramData%\ssh`, stops sshd, uninstalls the preview, DISM remove + add, restores missing files from the backup, sets Auto, and reinstalls the preview from its cached MSI only if nothing listens on 22 |
| T5 | LAN ssh timed out while tailnet ssh worked | the capability's firewall rule is **Private-only**, and the Wi-Fi profile was **Public**; Public still blocked with the rule widened to Any | set `<fleet-lan-profile>` to Private, as on the other minis, AND the rule to `-Profile Any` |
| T6 | `pwsh` reported installed, but `C:\Program Files\PowerShell\7` did not exist; DefaultShell stayed 5.1 | winget picked the Store / MSIX package | `winget install Microsoft.PowerShell --installer-type wix --scope machine` |
| T7 | the user PATH vanished from ssh sessions after an agent added one directory | `[Environment]::SetEnvironmentVariable('Path', ..., 'User')` rewrites `HKCU\Environment\Path` as **REG_SZ** | write it with `Set-ItemProperty -Type ExpandString` in `%USERPROFILE%` form; never the .NET setter for Path |
| T8 | the watcher's fan-out check hung forever at its second mini | ssh started from a background task waits on an inherited stdin that never closes | start ssh with `Start-Process`, stdin redirected from an **empty file**, stdout to a file, and a hard timeout (see `TRAPS.md`, 2026-10-16) |
| T9 | every report line failed with "Cannot locate the history for command line" | a helper function named `R`; `r` is PowerShell's built-in alias for `Invoke-History`, and aliases beat functions | never name a function after a built-in alias (`r`, `h`, `sc`, `gc`, `ls`, ...) |
| T10 | the driver's own key file was not updated, and the report line was empty | `administrators_authorized_keys` needs elevation; the driver's shell was not elevated | write it through a peer mini (a fleet key login of an admin is elevated); report NOT CONFIRMED unless the write said it happened |
| T11 | `winget` "not recognized" over ssh | the App Installer alias is not on an ssh session's PATH | call `C:\Program Files\WindowsApps\Microsoft.DesktopAppInstaller_*_x64__8wekyb3d8bbwe\winget.exe` by full path |
| T12 | first-contact script lines that worked in one shell failed in the other | PowerShell 5.1 vs 7 differences: top-level `return` in a paste, `-N '""'` to a native exe, `if { } \| Tee-Object` (5.1 parse error) | wrap the paste in `& { }`; pass native arguments through `Start-Process -ArgumentList`; parse-check under BOTH 5.1 and 7 before handing it to the owner |
| T13 | a local guard refused a scheduled task whose action was `cmd.exe` | it would open a visible console | task action `conhost.exe --headless <exe> ...` |

## Verify by hand (read-only)

```powershell
pwsh -NoProfile -File <bus>\tools\machine\fleet-mini\Test-FleetMini.ps1 -Hosts <new-mini>
ssh -n -o BatchMode=yes <new-mini> "(Get-CimInstance Win32_Service -Filter \"Name='sshd'\").PathName"   # ...\System32\OpenSSH\sshd.exe
ssh -n -o BatchMode=yes <new-mini> "Get-NetConnectionProfile | % { `$_.NetworkCategory }"              # Private
```

## Not on the bus yet

The first-contact script and the fan-out check script exist machine-local on the driver mini. They carry the
fleet's public keys and network profile name, so a bus copy needs those turned into parameters read from a
machine-local file first. That port, and a check item for the network profile, are follow-ups; this runbook is
the procedure either implementation must follow.
