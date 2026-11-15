# tools/machine/fleet-mini: bootstrap a headless Windows mini PC to the fleet baseline

A **machine tool**: one table of the settings every fleet mini PC shares, a read-only check, and an
apply step. A new mini gets the whole baseline from one command; an existing one proves it still has it.
It replaces the machine-local parity probe and one-shot baseline script that lived only in
`~/.claude/machine/` on individual machines, where a new machine could not find them.

Law 1 holds: nothing here runs anywhere until a machine's owner runs it from a commit they reviewed.

## Why it exists (the trap that started it, 2026-11-14)

On a headless mini (no mouse or keyboard plugged in, display = HDMI emulator or capture device), **no
window could be resized** by dragging its edge over TeamViewer. Plugging in a real monitor seemed to fix
it, but the real variable was input: with no mouse attached Windows reports `SM_MOUSEPRESENT=0`, hides
the pointer, and remote-control input never becomes an edge drag (keyboard sizing, Alt+Space > Size,
still worked). Turning on **Mouse Keys** makes Windows treat the session as having a pointing device:
`SM_MOUSEPRESENT` went 0 -> 1 and edge dragging worked again on all three minis. The same symptom is
reported for Jump Desktop, Mouse Without Borders and HP remote graphics on headless machines.

## Run it

```powershell
# read-only, this machine or any others by ssh alias (exit 0 = all OK, 1 = drift, 2 = unreadable host)
pwsh -NoProfile -File <bus>\tools\machine\fleet-mini\Test-FleetMini.ps1 [-Hosts alias1,alias2] [-Json]

# on the mini itself: dry run first, then apply (OWNER runs -Apply from an elevated shell)
pwsh -NoProfile -File <bus>\tools\machine\fleet-mini\Initialize-FleetMini.ps1
pwsh -NoProfile -File <bus>\tools\machine\fleet-mini\Initialize-FleetMini.ps1 -Apply
```

An ssh key login of an admin account is already elevated, so the owner can also run `-Apply` from
another fleet machine with `ssh <alias> pwsh -NoProfile -File ...`. Per-user items still land in the
person signed in at the console: Mouse Keys is set through a one-shot Interactive task in the console
session (deleted at once), because a `SystemParametersInfo` call from the ssh session would change the
wrong session. If no one is signed in at the console, only the stored value changes and the receipt
says `STORED ONLY`. The Mouse Keys check reads the stored value of the account running it, so run the
check as the account that signs in at the console. Every applied change is written to a JSON receipt with its before and after values
(`%ProgramData%\fleet\fleet-mini\receipts\` when elevated).

## The baseline

| id | class | what | why |
|---|---|---|---|
| mouse-keys | user | Mouse Keys on, keypad mouse while Num Lock is on | headless remote control cannot drag window edges otherwise |
| git-longpaths | user | `git config --global core.longpaths true` | deep worktrees fail to check out |
| sleep-never, hibernate-never | admin | AC sleep and hibernate timeouts 0 | a sleeping mini drops ssh, lanes and remote control |
| fast-startup-off | admin | `HiberbootEnabled=0` | a shutdown is otherwise a hibernate; restarts lie |
| long-paths | admin | `LongPathsEnabled=1` | paths over 260 characters |
| w32time-auto | admin | Windows Time Automatic | ledgers and receipts compare clocks across machines |
| exec-policy | admin | LocalMachine RemoteSigned in both pwsh 7 and Windows PowerShell 5.1 | fleet scripts run locally under both |
| sshd, ssh-default-shell | admin | OpenSSH server Running/Automatic, default shell pwsh 7 | how every other machine drives this one |
| smart-app-control-off | owner | Smart App Control off | it blocks freshly built test DLLs at random |
| auto-sign-in | owner | AutoAdminLogon=1, password as an LSA secret, never plaintext | after a restart there must be a desktop to attach to |
| display-present | owner | an active display (HDMI emulator or capture device) | otherwise Windows falls back to a tiny virtual screen |
| remote-control, tailscale | owner | TeamViewer service Automatic; Tailscale installed | graphical access before sign-in; ssh off the LAN |
| ssh-authorized-keys | owner | `%ProgramData%\ssh\administrators_authorized_keys` | admin accounts read keys from there, not `~/.ssh` |
| tool-* | owner | git, pwsh, gh, node, python, dotnet, claude, codex on PATH (python must answer `-V`: the WindowsApps Store alias does not count) | every lane assumes the same toolchain |

Mouse Keys value: `Flags=31` is copied from what the Settings page stored with "Only use mouse keys when
Num lock is on" ticked (measured). `MKF_REPLACENUMBERS` (0x80) is clear in it, although the documented
meaning of that bit reads the other way round.

**Classes.** `user` is applied for the signed-in account without elevation. `admin` is applied only
from an elevated shell, which is the owner's. `owner` is never applied: it covers security settings,
credentials, installs and accounts, and the script prints the exact step instead. Agents may run the
read-only check and the dry run; they do not run `-Apply` elevated.

## New mini, in order (owner)

1. Windows set up and signed in; plug in the HDMI emulator or capture device.
2. Install the toolchain (`winget install Git.Git Microsoft.PowerShell GitHub.cli OpenJS.NodeJS
   Python.Python.3.14 Microsoft.DotNet.SDK.10 Tailscale.Tailscale TeamViewer.TeamViewer`), then
   `npm install -g @anthropic-ai/claude-code @openai/codex`, and sign in to each.
3. Enable OpenSSH server (`Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0`), clone the
   doctrine bus, and run `Initialize-FleetMini.ps1 -Apply` from an elevated pwsh.
4. Do the owner items it prints: Smart App Control, Autologon, TeamViewer unattended access, the ssh
   key mesh.
5. From any other fleet machine, run `Test-FleetMini.ps1 -Hosts <new alias>` and expect exit 0.

Project-specific machine setup (each project's scheduled tasks, hooks, CI runners) stays with that
project; this tool covers only what every mini shares.

## Measured on the current fleet (2026-11-14)

All 24 items OK on all three minis, read with `Test-FleetMini.ps1` from one of them. Seen on the minis
but **not** in the baseline because they differ today: power plan (Balanced on one, High performance on
two), monitor-off timeout (15 or 30 min), and the Windows Update policy
`NoAutoRebootWithLoggedOnUsers=1`, set on one mini only. That last one is a candidate: an update restart
kills running lanes, so it may belong in the baseline once the owner decides.

## Tests

`pwsh -NoProfile -File tools/machine/fleet-mini/Test-FleetMini.tests.ps1`: no Pester, no elevation,
changes nothing. Covers parsing, the table's shape (owner items never carry a fix), the Mouse Keys
judgement, a real read of the machine, the dry run changing nothing, `-Apply` skipping owner, OK and
unreadable items, admin items skipped when not elevated, and a law-4 scan of the shipped files.
