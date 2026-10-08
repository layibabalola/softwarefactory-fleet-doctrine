# adobe-ingester cards (R14.1; written only by adobe-ingester)

## adobe-ingester/headless-lanes-fire-pretooluse
rule: a user-scope hook that shows bus content (e.g. an R15 re-check) must exit silently inside governed lanes.
mechanism: headless `claude -p` lanes still fire PreToolUse (not SessionStart), so a cwd-scoped hook keyed only on
  the repo path also reaches reviewer lanes started in that repo, breaking R15.2 and reviewer independence.
check: node C:/Users/obabalola/.claude/hooks/doctrine-recheck-r15.tests.mjs (case "R15.2: FACTORY_LANE set")
supersedes: none
evidence: reported

## adobe-ingester/regex-parens-are-groups
rule: a parser that must match literal parentheses needs a fixture where text outside them would also match.
mechanism: `/(([^()]*))/g` is two capture groups, not literal parens; it matched any paren-free run, so an
  out-of-parenthesis date could win attribution. Author tests passed; only a falsifier executing the code caught it.
check: node tools/traps-index.tests.mjs (attribution regression cases), bus commit 413d0f9
supersedes: none
evidence: measured

## adobe-ingester/stale-threshold-vs-sequential-review
rule: size a review order's dispatch-staleness threshold to the measured sequential review; a fixed 120 min goes STALLED
  before the second reviewer can start when reviewers start only after a host-admission chain.
mechanism: adobe-ingester Test-FactoryDispatch.ps1 reads stale_after_minutes per order from state.yaml and returns STALLED
  once any lane is missing and age >= it. WO-015 r5 opened 05:51:00.149Z; Opus published 07:56Z (125 min); the Sonnet
  start was refused at 129 min, and reopening after a publication would orphan the Opus report.
check: adobe-ingester HUB 2026-10-08T08:01:04.572Z; `Select-String .factory/tools/Test-FactoryDispatch.ps1 stale_after_minutes`
supersedes: none
evidence: measured

## adobe-ingester/codex-0161-readonly-sandbox-fails
rule: after a CLI upgrade, prove the different-family falsifier can execute a command before relying on its verdict.
mechanism: codex 0.161.0 `exec --sandbox read-only` fails every command on virtual-ten ("helper_unknown_error: setup
  refresh had errors"), so the falsifier returns UNSAFE with no evidence. Workaround used: danger-full-access under a
  strict read-only instruction, with `git status --porcelain` and HEAD captured before and after each round.
check: `echo "run Get-Date" | codex exec --sandbox read-only -` (expect the error on an affected host)
supersedes: none
evidence: measured

## adobe-ingester/pin-refresh-strands-built-scripts
rule: after any pin refresh, search every already-built script for the old pinned digest; a plan re-hash still passes.
mechanism: adobe-ingester 07f chain children (Invoke-WarmRead.ps1, Invoke-VerifyOnly.ps1) hard-coded the control-plane
  manifest digest 67792D7A...; a CLI-Currency Claude upgrade (2.1.287 -> 2.1.293) forced a pin refresh that replaced the
  manifest, so the pinned plan matched but the children would refuse at run time. A panel seat caught it; a rebuild
  wake was required (directive 2026-10-08a clause 3).
check: `Select-String <chain-dir>\children\*.ps1 -Pattern <old-manifest-sha>` returns no match before the run
supersedes: none
evidence: measured

## adobe-ingester/stale-unstarted-order-supersede-not-waive
rule: when a review order goes stale before any reviewer starts, supersede it pre-model and open a fresh order on the
  same candidate and deadline; never waive the staleness refusal and never reopen after a publication.
mechanism: a falsifier blocked an "age-only STALLED is not a refusal" waiver as weakening freshness; supersede plus fresh
  order (precedent adobe-ingester 673b185 for WO-012) restored freshness and was accepted for WO-015 r3->r4->r5.
check: adobe-ingester HUB 2026-10-08T05:42:43.930Z and 2026-10-08T05:51:00.149Z
supersedes: none
evidence: measured

## adobe-ingester/panel-transcript-binds-draft-sha
rule: an approval that cites reviewer transcripts must find the reviewed draft's path and SHA-256 in each transcript's
  first user message; a path alone does not bind the review to the bytes delivered.
mechanism: adobe-ingester Sol refused directive 2026-10-07f (HUB 2026-10-07T17:28:50.937Z, condition 27c 1(a)) because
  panel prompts named only the path; re-running the panel with path and SHA was accepted (HUB 2026-10-07T18:03:02.432Z).
check: the first `"type":"user"` line of each transcript contains the cited draft SHA-256
supersedes: none
evidence: measured

## adobe-ingester/measure-product-against-control
rule: every board measures product commits against control-plane commits each checkpoint; control churn with zero
  product commits over 48 h is a stall to name, never progress to report.
mechanism: adobe-ingester logged 169 control commits and 0 product commits in 72 h while every gate and directive
  "succeeded"; status reports counted gates passed, not code shipped (receipt at bus 5417cfe).
check: node specs/adobe-ingester/tools/product-control-ratio.mjs --repo <board repo> --product <paths> --control <paths>
  --hours 48 --all (exit 3 = STALL_CONTROL_ONLY)
supersedes: none
evidence: measured

## adobe-ingester/fix-self-tripping-gates-at-the-source
rule: when a gate refuses only because of the factory's own designed sequencing, correct the gate's parameter once at
  its source; do not answer each refusal with a per-incident waiver or directive.
mechanism: adobe-ingester spent three directives (08a, 08b, 08e) on gates that tripped solely on its own design: a
  dispatch staleness clock running while reviewers were disabled by design, a manifest digest hard-coded in built
  scripts, and a 120-minute window shorter than the designed sequential review. None guarded product or host risk.
check: for each refusal, ask "does this trip on product or host state, or only on our own sequencing?"; count
  directives per blocker class in the board's delivery ledger
supersedes: none
evidence: measured

## adobe-ingester/pin-falsifier-cli-privately
rule: run a different-family falsifier from a privately pinned CLI install, not the shared global one that lanes,
  sibling projects and the R13 updater also use.
mechanism: the shared global codex could not be swapped while lanes ran it (npm stalls on the locked native binary),
  and R13 reinstalls the newest version every 6 h. A private `npm install --prefix <dir> @openai/codex@0.160.1`
  restored a working read-only sandbox for the falsifier without touching any lane.
check: `node <prefix>\node_modules\@openai\codex\bin\codex.js --version` prints the pin and a read-only exec probe succeeds
supersedes: adobe-ingester/codex-0161-readonly-sandbox-fails (its danger-full-access workaround)
evidence: measured

## adobe-ingester/detector-replay-must-share-the-trigger-key
rule: a replay that certifies an event detector must load the detector's own trigger pattern, never a copy; a copied
  pattern drifts with the detector and certifies the same blind spot.
mechanism: adobe-ingester's auditor-wake detector (machine-local .claude-state/tools/Test-AuditorWakeCondition.ps1)
  matched OWNER_ITEM hand-offs only by heading phrasing ("OWNER_ITEM ... OPEN|ROUTED", "WAITING FOR DIRECTIVE"). Sol's
  heading "OWNER_ITEM <id> | STRICT POSTFLIGHT FAIL STOPPED" (HUB 2026-10-08T17:40:33.715Z) and its
  WAITING_FOR_GOVERNED_ACT re-posts matched neither, so for 4.9 h the detector reported an older answered item CLEARED
  while a routed item sat unanswered. The replay harness carried its own copy of the same regex, so it agreed.
check: run the replay with the detector's default pattern; the 17:40:33Z item must show OPEN at +25 min (it now does,
  with every older hand-off still CLEARED and 7 new matches, all genuine hand-offs)
supersedes: none
evidence: measured

## adobe-ingester/committed-hash-names-the-bytes
rule: any precondition that compares a recorded SHA-256 with "the committed file" must name the bytes: working-tree
  bytes, or the blob identity after git's clean filters. Raw blob bytes differ from both for text files under EOL
  normalization, which can make a precondition fail by construction.
mechanism: in adobe-ingester's WO-015 81-entry candidate manifest, 18 evidence files are stored LF and checked out
  CRLF, so raw-blob SHA-256 mismatches 19 entries, but the working tree mismatches only the one really stale entry.
  The strict gate compares working-tree SHA-256 and `git hash-object --path`. Draft directive 2026-10-08h r2 said
  "committed file's SHA-256" and would have stopped its own correction; the auditor's measurement and an independent
  Codex falsifier round found this separately. The delivered text names working-tree and git-filtered identity.
check: `git ls-files --eol <path>` shows i/lf w/crlf; compare Get-FileHash <path> with sha256 of `git cat-file blob HEAD:<path>`
supersedes: none
evidence: measured