# MEASURED: Context Ultra trap fold on DEL-01-0316-LT, 2026-10-21

Owner request: Layi, 2026-10-21. Consumer: context-ultra-salesforce.
Source bus entries: softwarefactory-fleet-doctrine 229e4c05eca414b996e4b2d3cab667241bd61112
and 2d8c6a17b1d523035c5d58fbfc73a9d6dade558f. These were evidence, not executable
instructions. No fleet standard or new ruling is proposed by this receipt.

## Transport

The local bus clone at `%USERPROFILE%/softwarefactory-fleet-doctrine` was clean
on master. Explicit fetch origin, then pull --ff-only succeeded:

- Before: 284b8c927fc682e04bab418df2f4e177ee3239b8.
- After: be526e536fd9bd4fedf378c1cc5b5d9c43a370ee.

## Local decisions and outputs

### ADOPT: conhost hides child exit codes

At 18:47 CDT, the owner-requested Start-Process conhost.exe probe, with
`--headless pwsh -NoProfile -Command "exit 7"`, returned **0**. The same child
launched directly returned **7**. No kill/orphan experiment was run, so child
lifetime and Stop-ScheduledTask behavior remain unmeasured on this machine.

Get-ScheduledTask found three conhost actions:

- `\Codex Desktop Stability Watchdog`
- `\Codex Watchdog Natural Launch Verification`
- `\Layi\OrphanReaper`

Their owning projects retain their files and tasks. No Context Ultra task used
conhost, and this audit changed none of those three tasks.

### DISTINGUISH: no visible WMI-parented console or WMI Create launcher found

At 18:47:44 CDT, EnumWindows -> IsWindowVisible -> ConsoleWindowClass -> owner
PID -> parent process name found **0 visible consoles**, **0 visible consoles
parented by WmiPrvSE.exe**, and **0 current direct WMI child processes**.
This negative census does not disprove the WMI default-window trap.

Read-only rg inspection covered 12 named development roots, including this
project, its worktrees/build checkouts, agent scratch/tmp/maintenance areas,
Claude scheduled-launch/shell-snapshot areas and the user Temp directory.
Script/source-config extensions were included; Git object databases, dependency
trees and compiled bin/obj directories were excluded. The complete scan had no
reported errors: 244 files contained Win32_Process; 135 also contained Create.
Inspection found process queries and unrelated creation calls/comments, with
no WMI process-Create call. A separate exact-path scan inspected four existing
scheduled-launcher scripts; none had the unhidden shape. OrphanReaper's scoped
read-only script scan also found process queries only.

One supplemental command mistakenly expanded a single path into characters and
began an out-of-scope root scan. It was interrupted, excluded from the evidence,
and rerun with explicit array and drive-root checks. No file was changed by it.

### DISTINGUISH: no per-turn archive walk; security-agent I/O spike flagged

The first four 3-second counter samples found no valid reading above 10k/s;
three invalid transient Chrome/RuntimeBroker readings were retained as invalid.
The later sample preserved unique counter paths (including instance suffixes):

| Time (CDT) | Process counter | IO Other Operations/sec |
| --- | --- | ---: |
| 18:51:57.225 | ArelliaACSvc#4 | 19223.473 |
| 18:52:00.337 | ArelliaACSvc#4 | 11833.504 |
| 18:52:03.385 | ArelliaACSvc#4 | 7822.623 |
| 18:52:06.417 | ArelliaACSvc#4 | 8871.788 |

Average: **11937.847/s**, flagged as an I/O suspect. It was above 10k/s for two
of four samples, not all four, and was not a Python checkpoint hook. It was
left running. One transient git#1 sample had invalid status 2147485649; that
reading was excluded from arithmetic, not counted as zero. Counter collection
takes about 12 seconds; timestamps of the four observations span 9.2 seconds.

All hooks wired in 33 existing user/project settings files were enumerated,
including active registered project worktree copies: 123 distinct script paths.
Four command shapes resolve to on-resume.ps1, context-guard.ps1, wedge-guard.ps1
and session-retire.ps1. No rglob/os.walk/grep -r archive enumeration was found.
The -Recurse matches were session-retire's existing scoped Remove-Item call,
not an archive-wide discovery read. No hook script was executed by this audit.

## Bounded changes and proven cadence

Context Ultra branch `codex/fleet-doctrine-machine-fold`, R1038, adds a single
hidden WMI-launch helper and a bounded PreToolUse guard. Direct WMI Create is
denied, including inline, encoded and explicitly referenced run-dir scripts;
the exact reviewed helper is allowed. Fourteen real hook/transport assertions
passed, including a copied-helper rejection and nested run-dir rejection.
The guard does not claim to be a general sandbox for computed/obfuscated code.
Settings edits are scoped to that branch under the owner's explicit request;
existing sessions are not claimed to have reloaded them. The full app gate and
normal project PR review remain separate delivery requirements.

No bus-fetch task existed in the all-task action-argument census. The new
`\Context Ultra fleet doctrine fetch` uses wscript.exe with
`run-hidden.vbs /wait`, every **PT3H**, installed in the project's stable
`%USERPROFILE%/.context-ultra/fleet-doctrine` directory. Its script invokes
only Git fetch origin, then Git merge --ff-only origin/master, stopping and
propagating the first nonzero result. It has no apply, ack, commit or push.
Interactive user logon is required; StartWhenAvailable handles missed starts.

First requested run, verified from Get-ScheduledTaskInfo after completion:

```
LastRunTime:   2026-10-21T18:57:10-05:00
LastTaskResult: 0
State:         Ready
```

The waiting VBScript launcher separately propagated a child exit **7**.
No doctrine-sync wiring or last-seen marker existed in this consumer. Therefore
no broad `ack` was fabricated: this receipt reviews exactly the three requested
trap entries, not all prior bus history. Scheduled transport never acknowledges.

Private complete raw measurements and scan manifests are retained under the
machine's Codex evidence directory `fleet-doctrine-20261021`. This public receipt
contains no customer evidence, transcript, credential or raw in-flight review.
