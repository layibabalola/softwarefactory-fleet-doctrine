# airmypc cards (R14.1)

Cards filed by AirMyPC. Each card's check runs in the AirMyPC repository unless it says otherwise.

## airmypc/dotnet10-comwrappers-duplicate-holder-slot
rule: in a .NET 10 WinUI/WinRT app, never hand the same long-lived managed object to an object-typed WinRT property or call over and over; cache the WinRT result, or skip the call when the value has not changed.
mechanism: each ComWrappers.GetOrCreateComInterfaceForObject on the same managed object appends a duplicate ManagedObjectWrapperHolder slot to that object's holder list and never trims it, so a 5 s refresh loop grows the private bytes of a 12 h soak without bound while the managed heap looks flat. Reproduced outside the app on .NET 10.0.12. The triggers were theme-dictionary lookups, button Content and ToolTip, and GetWindowHandle(this).
check: dotnet test tests/AudioMile.GateTests --filter "FullyQualifiedName~ComWrappersHolderGrowthCanaryTests"
supersedes: none
evidence: measured

## airmypc/interned-literal-is-one-process-lifetime-object
rule: when a value you marshal to native code is a C# string literal, marshal an owned copy (new string(span)), not the literal itself.
mechanism: string literals are interned, so every assignment of "Stop" or "Connecting..." is the SAME managed object, alive for the life of the process. Any per-object native bookkeeping, such as the ComWrappers holder list above, therefore accumulates on it forever. Skipping unchanged values is not enough when a label toggles: holder lists went 48, 95, 143 over 12 h. An owned copy dies with its holder list.
check: dotnet test tests/AudioMile.GateTests --filter "FullyQualifiedName~ComWrappersHolderSourcePinTests"
supersedes: none
evidence: measured

## airmypc/winui3-dies-in-ssh-session-0
rule: launch a WinUI 3 app on a remote Windows box through a one-shot scheduled task with an interactive logon type, never directly from an SSH or WinRM shell.
mechanism: an sshd child runs in session 0, which has no interactive desktop; Microsoft.UI.Xaml.dll fails fast with 0xc000027b before any app code logs. A remote soak started over SSH therefore dies at startup and looks like an app crash. The task needs the absolute path of the launcher, because a Store-installed pwsh is not on the task's PATH (0x80070002).
check: on the remote box, `powershell -c "[Diagnostics.Process]::GetCurrentProcess().SessionId"` run over SSH prints 0, and the same command logged by the scheduled task prints 1 or more
supersedes: none
evidence: measured

## airmypc/gcdump-cannot-follow-an-object-across-dumps
rule: judge a heap-growth gate across .gcdump files only on identity-free aggregates (total count, list count, the longest list), never on per-object growth.
mechanism: a dotnet-gcdump node's only key is its type, size and address. A compacting GC moves objects, and equal-sized objects are interchangeable, so "the same object grew" cannot be shown between two dumps. A per-key growth clause either fails on churn or passes on a relocated leak. Set each bound from at least three admissible runs of the fixed build (max observed plus 100%), recorded before the certifying run.
check: pwsh -NoProfile -File tests/row46-verdict/Test-AudioMileRow46Verdict.SelfTest.ps1
supersedes: none
evidence: measured

## airmypc/retire-shared-tool-copies-agent-bridge
rule: delete agent-bridge tools/session-checkpoint.py and its SessionStart and Stop entries in .claude/settings.json; give tools/check_doc_size.py a CONFIG ... END CONFIG block or retire it; converge tools/doctrine-triage.mjs and AirMyPC tools/fold-triage.mjs onto one implementation run from one place.
mechanism: the user settings already run ~/.claude/hooks/session-checkpoint.py (v4, 553 lines) on both events, so the 116-line project copy (v2) runs a second time per event and writes an older record. check_doc_size.py has no shared section to hash, so its drift from the AirMyPC and MLV-App ports cannot be measured. If the project copy does something v4 does not, move that into v4 first.
applies: agent-bridge
check: in the bus clone, node tools/tool-census.mjs --json shows no agent-bridge double registration and no agent-bridge session-checkpoint copy
supersedes: none
evidence: measured

## airmypc/retire-shared-tool-copies-mlv-app
rule: delete MLV-App tools/session-checkpoint.py (with tools/repo_hygiene/test_session_checkpoint.py, or retarget that test at the shared hook) and its Stop and SessionStart entries in .claude/settings.json; converge tools/coordination/doctrine_outbox.py with the bus and AirMyPC versions onto one implementation.
mechanism: the user settings already run ~/.claude/hooks/session-checkpoint.py (v4, 553 lines) on both events, so the 214-line project copy (v3) runs a second time per event. doctrine_outbox.py exists in three versions (bus 449, AirMyPC 1,099, MLV-App 1,520 lines), so a fix in one never reaches the others. If the project copy does something v4 does not, move that into v4 first.
applies: mlv-app
check: in the bus clone, node tools/tool-census.mjs --json shows no mlv-app double registration and no mlv-app session-checkpoint copy
supersedes: none
evidence: measured

## airmypc/retire-shared-tool-copies-adobe-ingester
rule: delete Adobe Document Cloud Ingester tools/session-checkpoint.py and its SessionStart and Stop entries in .claude/settings.json.
mechanism: the user settings already run ~/.claude/hooks/session-checkpoint.py (v4, 553 lines) on both events; the project copy is a different 229-line v3. Its entries are bare {type, command} objects directly under the event, not the matcher-group schema ({hooks: [...]}), so they may never have fired at all; deleting them removes both the double run and the doubt. If the project copy does something v4 does not, move that into v4 first.
applies: adobe-ingester
check: in the bus clone, node tools/tool-census.mjs --json shows no adobe-ingester double registration and no adobe-ingester session-checkpoint copy
supersedes: none
evidence: measured

## airmypc/retire-shared-tool-copies-airmypc
rule: retire the vendored tools/doctrine_outbox.py (and Invoke-AudioMileOutboxDrain.ps1's dependence on it) and tools/fold-triage.mjs in favour of one implementation run from the bus clone; keep tools/check-doc-size.py only with its section below END CONFIG equal to the shared one.
mechanism: AirMyPC carries the 1,099-line doctrine_outbox.py against the bus 449 and MLV-App 1,520; fold-triage.mjs (492 lines) and agent-bridge doctrine-triage.mjs (291) solve the same problem twice; check-doc-size.py differs from the MLV-App port below a CONFIG block both files call the only edited part.
applies: airmypc
check: in the bus clone, node tools/tool-census.mjs --json shows one version each for doctrine-outbox, doctrine-triage and check-doc-size
supersedes: none
evidence: measured

## airmypc/d1-d3-not-resolved-20261016
rule: a defect closes when a mechanism requires its number to fall by a date and an owner carries it; measuring it, ratcheting it or filing an unowned card is not a fix. Until then report it NOT RESOLVED, with the number.
mechanism: owner defects D1-D3 (2026-10-11) were measured, ratcheted and carded, then treated as handled. Adjudicated 2026-10-16, all NOT RESOLVED: D1 tool census 11 = baseline 11; D2 AirMyPC rule coverage 6/45 = 13.33% (tools\Get-AudioMileRuleCoverage.ps1 -Check); D3 AirMyPC 14-day product share 7.97% (Get-ProductThroughput.ps1 -Lines; diagnostic only, metrics law 1). Anti-pattern: measure and call it fixed; ratchets forbid worse, never require better; cards with no owner.
  Adopted: a census deadline (metrics/tool-census-baseline.json schedule, 11 -> 7 by 2026-10-23 -> 0 by 2026-11-06, enforced by --check); an AirMyPC rule-coverage rising floor; the retire-shared-tool-copies cards turned into owned AirMyPC queue items. The last two are AirMyPC-side and owed.
check: in the bus clone on a fleet box, node tools/tool-census.mjs --check exits 0 (1 = rose or over the current deadline, naming the families; 3 = UNMEASURED)
supersedes: none
evidence: measured

## airmypc/adobe-sessionstart-hook-runs-git-checkout-and-cherry-pick
rule: a SessionStart hook never changes the checkout (no git checkout, add or cherry-pick); resumption reads and reports state, and the session decides.
mechanism: Adobe tools/session-checkpoint.py at HEAD 7f31c0d (v3, 2343adf) sets AUTO_RESUME_ENABLED = True (line 15). At SessionStart, when the recorded account changed (line 161), auto_resume (call at 167) runs git checkout of the prior branch (78), git add of the recorded staged files, and git cherry-pick of its master..branch commits (91). A new account's first session thus moves the primary checkout before anyone reads the board. The user-level v4 ~/.claude/hooks/session-checkpoint.py already checkpoints both events and never writes to git. Adobe's entries are flat {type, command}, so they may not fire today; fixing that schema would arm this.
  Recommended: delete both .claude/settings.json entries, or set AUTO_RESUME_ENABLED = False. Evidence only; adobe-ingester owns the fix (R14.8).
applies: adobe-ingester
check: in the Adobe repo, git show HEAD:.claude/settings.json names no session-checkpoint.py, or git show HEAD:tools/session-checkpoint.py has no "AUTO_RESUME_ENABLED = True"
supersedes: none
evidence: measured
