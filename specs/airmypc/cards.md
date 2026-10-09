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
