# DNG Auto Processor — factory spec (one writer: the `dng-design-steward` seat, docs/13 P-STEWARD step 7d; a posture change made anywhere else reaches this file as a census item of that seat's next pass)
source_commit: bf69dcf3f5d8165acb00cccf9f67716d90a2bce0

**Machine:** ULTRAMAGNUS (personal box). **Project root:** `C:\code\DngAutoProcessor - Claude`.
**Product:** auto-grading pipeline for DNG timelapse clips emulating the operator's LRTimelapse
keyframe-ramp workflow. **Rewritten wholesale at doctrine seams; artifacts live in
`dng-auto-processor/` in this repo (standards + receipts, byte-anchored in its `EXPORTS.md`).**

## Current posture — rules only; read this first

Board truth: `DngAutoProcessor/docs/14-ORCHESTRATION.md`, the design of record (§ below means its sections), plus
section P-RESUME of `DngAutoProcessor/docs/13-RESET-PROMPTS.md` (docs/13); plan of record `docs/12-RESET-PLAN.md`;
`WORK.md` on master is the only selector (§0). This block restates their rules with a section each and carries no
state; where they differ, they win. It is rewritten when a docs/13 or docs/14 change since `source_commit` falls in a
section it cites. Below the dispositions table is history: "current" or "must know" there meant then.

### Portable rules (measured on this board; offered to any board)
- **Standing authority is one section every seat's boot reads verbatim** (§0; docs/13 P-COP, P-STEWARD), never
  retyped into a seat prompt (§10 "Net rules"). A USER ruling is recorded as {exact question, selected label,
  rejected alternatives}, authorises only its literal scope, and a relay of it is evidence, never an authority multiplier.
- **Boot is derivation, never "read fully"** (§3): a stateless seat derives state from git, the queue, its cards and
  the evidence ledgers within §3's budget, and a boot over it makes the tick's only act a split or park. A budget no
  reading set can meet is fixed on the READ: when a correct never-fold rule grows a file, read its live parts by pattern.
- **Resume re-arms, reports and stops** (docs/13 P-RESUME steps 2, 6, 7): re-create only the seats its rows list,
  ask about each other stranded task singly (a run with no person present asks nothing), relay every line a steward
  receipt addresses to the USER — **each re-derived at the artifact it names before it is relayed: relayed with its
  receipt's stamp while its condition holds, and as RESOLVED, with the evidence, once it no longer does**, because a
  derived line relayed as live after its mechanism is gone sends the owner to act on nothing (adopted from this bus)
  — write a receipt, and run no tick, dispatch, landing or governing-doc edit. A seat is
  alive only when its next run leaves its own receipt; "enabled" proves nothing. Every scheduled seat writes a
  receipt on every run, a no-op included (§5) — which makes that ledger the seat's fire history, so a row's CRON
  is checkable the same way and needs no access to the scheduler. **That comparison CONVERTS before it
  compares**: a scheduler evaluates cron in MACHINE-LOCAL time while every stamp written here is UTC, so a row
  checked against a UTC stamp reports a divergence between two byte-identical artifacts, orders a repair to live
  state, and on the same reading inverts a deliberate odd/even interleave between two seats. Only a row that
  fails the CONVERTED comparison is a row the live registration does not carry; the few minutes past the due
  minute are startup latency. A row that a procedure RE-APPLIES on recovery drives live state rather than
  describing it, so a mismatch is not cosmetic — and neither is a false one.
- **Make overlap harmless; never add a lease** (§3): claim on disk before acting (state line and launch json
  before the launch); re-read a card before any launch, landing or rewrite, and stand down if it changed; every
  launch json, brief, progress log, scratch file and verdict a dispatched seat writes carries its agentId in its
  name (`<kind>.<model>.<agentId>.<ext>`), because a derived seat name collides by construction; fixed-name slot
  files are copied before a rewrite, never renamed (next rule). **A peer that advances a PHASE changes no state
  line — it writes a launch json — so a launch also re-derives the card's phase first, and stands down when the
  derivation no longer names that launch**: a state line is blind to a routine overlap, a host re-entering on a
  subagent's completion, and two sessions of one claim otherwise launch two writers into one worktree. **A launch
  record already written when a seat stands down leaves the launch set in the same act** (renamed `standdown.*`):
  left in place it asserts a phase that never started, the liveness rule then calls its absent seat frozen, and
  that remedy relaunches into a live seat's worktree.
- **A seat is live by evidence read INSIDE a 90 s poll, never by file age, a lease or the clock** (§3): a write
  that appears, the seat's own process (its `pid` on the CLI route) or its host's API connection. Its first act,
  if it can write, is one progress line, and none ten minutes after launch means it never started; a seat launched
  read-only cannot write one, so for it the absence means nothing and the poll reads its own process. A subagent never reads its
  host's signals: its own writes and CPU-accruing processes under its own worktree count, and after its line it
  is FROZEN only once nothing of its own is newer than 30 minutes. FROZEN or DARK is skipped; its worktree is kept.
  **And the relaunch is bounded exactly as a key's is** (§3, §4 A2): a freeze is NOT a capacity death — that
  exemption names a 429, a session limit, a provider outage and a host restart, all read from outside the seat —
  so failover once and whole, one more relaunch only with a changed brief, and a third freeze on one attempt
  advances the attempt. An exemption that moves no counter is an unbounded loop, and the ceiling it bypasses is
  then unreachable by construction along that path.
  **A seat that reached the model and DECLINED is not frozen, and that ladder is not its disposition** (§3,
  §4 A2): a refusal, as distinct from a capacity, quota or connectivity error, is a property of the ASK, so the
  disposition is to re-shape the brief or fail over, and it consumes no attempt. A whole relaunch puts the same
  ask to the same model, because a failover rule triggered by usage, quota, session-limit, auth or outage
  errors, or by a failed CLI probe, is not triggered by a refusal and so shifts nothing — a remedy that cannot
  make its own condition false. The cost is real and is stated rather than closed over: at the polling window,
  a seat that declines without writing is indistinguishable from a freeze, so the decline route has to be a
  property of the BRIEF and not of the liveness rule.
- **An autonomy directive travels as the AUTHORISATION it is, and the brief NAMES the decline route** (docs/13
  P-COP Step 3; §0). An owner declining to be interrupted has authorised autonomy; rendering that as a ban on
  asking anyone, broader than the owner's words and with no route named beside it, states the opposite thing,
  and an unattended run's true property is simply that no person is present to answer — a fact about the run,
  never a rule about oversight. A factory whose return contract types `BLOCKED <reason>` for a failed check but
  never names it as the route for an OBJECTION has a decline route on paper only: a seat that judges the work
  improper, unsafe, misdescribed or beyond what it should do unsupervised then has nowhere to put the objection
  but silence, and silence is what a liveness rule reads as a freeze. **Offered with its own limit stated: this
  clause names no writer and no checker**, so by the test this same file exports — *for every field a protocol
  requires, name the writer that can set it* — it is a contract clause and not a gate, and a board adopting it
  inherits that gap rather than a guarantee.
- **A brief carries its card INLINED, never only its path** (docs/13 P-COP Step 3, B-APPROACH, C-COMMIT): a card
  opened in a tick is untracked until that tick's commit, and a worktree cut from master does not contain it, so a
  seat told only the path reads a file its tree does not hold; the launch record's brief hash then pins the card
  bytes the seat actually read.
- **Phases are read from the ledger, first match wins; `return.md` is a slot** (§3): before a phase rewrites a
  fixed-name file, copy it byte-identical to `<name>.<phase>.<agentId>.<ext>`; renaming the writer's file moves
  the slot and changes the derivation. **A launch json is read by its `phase` FIELD, never its filename**, so it
  takes the instance name like every other seat file, and a fixed name an older attempt wrote reads the same way;
  a phase machine that looks files up by fixed name while its naming rule forbids fixed names makes every launch
  record either invisible or a file two peers are aimed at. The rule that sends a finished author to its commit
  step yields while a commit step already launched has no output. **A subject committed while its author is still
  live is not finished**: a commit made early as insurance against the author's death is not the phase's output,
  so FINISHED waits until the committing seat has returned — its return written after its own launch record's
  start, never read off the commit's time, which a rebase rewrites — or is shown dead. **A phase that has returned
  is ready for its next step whatever the clock says**: an approach review launches once the approach seat
  returns, not only after its product has stood still for a fixed time. **Forced progress never forces an illegal act** (§3): a tick that moved
  nothing PARKs, REOPENs or SPLITs one item unless each is derived unavailable and named.
- **A card is admissible before it is opened** (§4): allowlist paths are relative to the git root; MODIFY means
  `git ls-files --error-unmatch` exits 0; CREATE means it exits 1, `git check-ignore -q` exits non-zero with any
  trailing slash stripped, and the path is marked new. Never `git status --porcelain -- <path>`, whose empty
  output is the same for untracked, unmodified and absent. One instance obliges a sweep of every open card.
- **The disposition comes off the ADJUDICATED finding list, never a verdict string** (§4), under four guards: a
  drop is a recorded mutation refutation; with no covering check only the other key's independent grading drops
  it; a cop never lands on its own refutation of a severity its brief pre-named; zero confirmed is necessary,
  never sufficient.
- **Refute before hand-back, then triage by trend** (§4b): each BLOCKER and MAJOR gets the smallest mutation to
  the line it names; caught is refuted and kept in the ledger, surviving is confirmed. The cop mutates in a probe
  worktree made and removed on a key's scratch-worktree terms, never in the item worktree that holds the reviewed
  bytes. Falling with new classes:
  another round; flat or rising with new classes: SPLIT; the same class re-found: PARK into ONE dimensioned batch
  pass. The three-round ceiling is the LAST test, and an unadjudicated round does not count. **Classify the
  FAILED SET as well as the round** (§4b, adopted from this bus): when the parks share a SHAPE — build a NEW
  verifier deciding an unbounded property of a rich artifact from a lossy proxy — care inside that class does not
  rescue it, and a card of that kind declares bars that are total functions over an enumerable representation, or
  it is not opened in that form. A bar needing a threshold or a heuristic is the warning that the class has been
  re-entered.
- **Land on per-file blob identity AND on the enumerated landing RANGE** (§4): every `binding.json` path has one
  blob at the reviewed and the landed sha, never root-tree equality, and patch-id only corroborates. The manifest
  names the whole base-to-subject diff the keys reviewed, never one commit's: a committer that lists only its own
  commit's files leaves the check passing over a population nobody declared. **Blob
  identity checks the paths a key READ and the fast-forward moves a RANGE**, and the two are the same set only
  when the subject is based on master: enumerate `master..<subject>` before the merge and fail closed on any
  path absent from `binding.json` and present in the PRODUCT set, because a green suite is not a review of bytes
  no key saw. A card whose `Base` is not master is landed by rebasing its own commits onto master, so the range
  IS the reviewed diff, and never by a bare fast-forward over its base. Then `git merge --ff-only` of an exact
  sha; land before you record; a tick that changed no state commits nothing. **A route with exactly one step
  owes a test for whether that step is performable, and a NAMED ACTOR for the case where it is not**: the test
  is mechanical — a three-way merge of the subject onto master against its recorded base, whose NONZERO EXIT
  means the rebase cannot be performed — and a card whose only route is unperformable has no route at all. A
  PARKED base lineage is a separate fact and is never the test: it is why the FALLBACK, landing the base
  first, is gone too. The re-scope onto master is a new ordinary card, so it is opened by the
  seat that may open cards — routing it to the design owner, who may not, parks the disposition on the one seat
  that cannot perform it, which is the remedy that cannot make its own condition false wearing the shape of a
  correct escalation.
- **Inert-commit rebase states the closed PRODUCT set and derives inert as its complement** (§4): a clause that
  says "never listed" and then lists is decided by whichever half is read first. It voids only when the
  intervening range touches the subject's own `binding.json` paths (absent or unparseable fails closed); the
  hook re-run on the rebased sha catches a disjoint break. Prefer rebase-before-review.
- **Scope every review** (§4a): named paths, a command budget, PARTIAL allowed; a subject over the file cap is
  split before dispatch; key 2 tiers by blast radius, never by line count; a round without two real verdicts is
  HELD and spends no attempt. **A void-on-RED clause is scoped to the subject AS COMMITTED, and the
  discriminator is the TREE a command ran against, never its exit code**: where the same rules ORDER an
  adversarial key to revert production files or mutate the line a finding names, those acts produce a red
  exactly when the change under review is CORRECT, so an unscoped clause voids every key-2 ACCEPT a compliant
  key can return. A red is exempt only where the key ATTRIBUTES it to a named revert or mutation; an
  unattributed red still voids, which keeps the clause's original measured case — a key that attributed nothing
  and reported a green run over a red one on the unmodified subject.
- **A silent key is retried once whole, then as ONE dimensioned fan-out** (§4 A2): one bounded seat per defect
  class, PARTIAL at its bound, adjudicated as a set; never a third whole-brief seat, never a landing without the
  key. HELD-FOR-KEY and a capacity death spend no attempt (§4). **A key its PROVIDER refuses on content or
  safety grounds is held on those same terms and spends no attempt** (§4 A2, adopted from this bus): the refusal is a property of the ask, so
  the disposition is to re-shape the brief or fail over — never to charge the card an attempt, and never to
  narrow what the factory will review. A causes list of capacity, connectivity and liveness only is a list a
  refusal falls straight through, landing by default on the attempt counter.
- **Quiet before a hook build is a closed-set question answered with named negatives** (§4): no live suite,
  build or decode the commit would corrupt, judged by rates across consecutive windows, `bin/`/`obj/` writes and
  what each RUNNING card's own clauses name, never by process presence or a load gauge. Every process in those
  terms is identified by its COMMAND LINE, never by its executable name: a component hosted by a runtime — an
  SDK's build engine and compiler server shipped as libraries — is invisible to its own name, so a name query
  reports its absence forever without ever reading false. **A command line that reads NULL answers nothing, so it
  never exculpates**: a process that exits while the census is being read comes back partly unpopulated, and the
  spawn-and-exit churn of a build or a restore is made of exactly such processes, so it is named UNREADABLE and
  counts as live until a later window reads it, or finds it gone with no build-output write in between. A hook
  rejection naming a locked build output is a load reading: retry once, then defer, never `--no-verify`. A hold derives from
  processes, never from card state. **A process sensor cannot see a peer's uncommitted BYTES, so the tree is
  read too**: take every path that is EITHER tracked-and-modified OR untracked with an extension the build
  compiles, AND newer than the newest `commit` or `commit (amend)` entry of this checkout's own HEAD reflog,
  AND not one this seat is about to stage by name; if any remains, defer and name each with its write time.
  **The age and staging conditions distribute over BOTH arms, and the age condition is what keeps this a
  sensor rather than a latch**: an age-blind test defers forever on the first stale file anyone leaves behind.
  Both arms are needed and neither is the other — a restriction to TRACKED paths misses half the class, because
  default globbing compiles a file whatever git knows of it. **The age clock is that reflog entry, never HEAD's
  commit time**: a landing fast-forwards HEAD to a commit whose hook ran in another
  worktree and never saw this one, so HEAD's time would certify whatever a peer left here before it; a reflog
  holding no such entry proves nothing, and every path defers.
- **An alarm that cannot read its input FIRES; one whose remedy cannot clear it is REPORTED, not obeyed** (§7).
  **And an alarm computed only from a FAILURE history reads healthy on a subject that stopped running
  altogether**, because a thing that never fires writes no failure and an empty input satisfies no
  count-the-violations arm: such an alarm needs one arm relative to the subject's OWN cadence. **That arm's
  window START is itself a field a new subject does not yet have**: written as "since its last run" it is a
  missing key, which the first rule above then turns into a permanent FIRE against a healthy subject for the
  whole interval between registration and its first fire — so the start falls back to a field every subject
  carries from creation. **That field is read by its TYPE** (§7): on this machine it has been read both as epoch
  milliseconds and as an ISO-8601 string, a single parser throws on one of them, and a helper that swallows the throw
  reports the key absent, which the first rule above then turns into a fire against healthy subjects; a value no
  reader parses is unreadable input, never an absent key. **A liveness alarm derives its seats from the ledgers a schedule's DEFINITION names,
  never from a directory's shape alone** (§7): the shape is also true of a ledger an on-demand procedure writes
  whenever it happens to run, which owes no cadence, so its silence reads as a stopped seat forever — nothing owes
  that ledger another write. A shape-matching ledger no definition names is reported by name as not a seat, and
  never fires. **And a stamp is a run only once its receipt is FINISHED, where the seat's definition says how a
  receipt ends** (§7): read by existence and age alone, a pass that opened its receipt and then died is the seat's
  freshest run — a pulse with nothing behind it — so an unterminated stamp enters neither the cadence nor the age,
  and is reported by name with its age. **A ratio alarm's numerator is a closed set, never the complement of one** (§7): coordination
  counted as everything outside the product set takes in every machine-written cache, CSV or data summary an
  experiment commits, and fires on bytes no seat wrote; coordination is the inert paths' Markdown and the landing
  receipts, and any other inert path is data that enters neither side. **And every commit an alarm counts is one
  reachable from the trunk, never one reachable only from another ref** (§7): a task branch's commits are work in
  progress until they land, so a count over every ref reads a factory that has stopped landing as one that is moving.
- **An exact test reports the range its statistic can ATTAIN, from every marginal it holds fixed, before its
  verdict is read** (§6): a card whose verdict is an exact or permutation statistic over a small fixed set states its α and the statistic's
  attainable minimum and maximum with the label counts AND the prediction counts held fixed; a value at that bound,
  or a range that cannot reach α, is VOID naming the bound — never a pass, a fail or a refutation — and a
  degeneracy test on one marginal is not this gate.
- **The authority wall has an addressee** (§7a): a seat at a wall appends one bounded token naming the artifact
  and the authority exceeded; one owner seat acts only on tokens and parks; a token about a seat's behaviour
  closes only on that seat's next receipt; no seat writes its own procedure, and no tick edits its governing
  document, which the hook enforces (§4).
- **Two keys, derived from the author, never the lane** (§2): key 1 from the family opposite the author, key 2
  an Anthropic model that is not the author's; both run every round into one finding list; a permissive key
  never overrides an unrefuted BLOCKER. **Where the rules give a card's approach review and a round's key 1 the
  SAME model, the key is briefed on what that model already asserted** (§2; docs/13 P-COP Step 2 points at it):
  the pair is derived from the rules at launch, never listed; both keys' briefs carry every approach-review
  finding the approach records as ADOPTED, and key 1 is told its own model asserted them and re-derives each at
  the artifact — otherwise the seat that must catch a false premise is the one that asserted it.
- **Approach before code** (§2, a USER unfreeze in §0): at most 60 lines, ONE round by the opposite family,
  every BLOCKER and MAJOR answered before the first product byte, never a second approach round; a review silent
  45 minutes is relaunched once, then IMPLEMENT proceeds with it recorded TIMEOUT. A card whose deliverable is a
  test, fixture, receipt, scorer or harness takes a top-tier approach review, whose brief names, for each failing
  test, the plausible wrong implementation it kills (§2, USER, §0). **The weave** (§2, USER, §0): author families
  take turns by tier pair; a card keeps its family so its rounds stay comparable, and a retry keeps it too.
- **Top-tier inference goes where a wrong answer costs the most rounds** (§2 "Top-tier posture", USER, §0):
  product direction, instruments, retries and the review acts the fleet's Opus floor reaches; mechanical execution
  stays where it is, and quality outranks token savings. A retry after a confirmed defect class is authored by the
  top-tier model of the card's own family, and its brief owes the closed set including negatives: every witness, the
  wrong implementation it kills, and the run that shows it. The top-tier model that wrote a lineage's product bytes,
  or served as its instrument, never writes that lineage's disposition, challenge or successor design. When the
  derived lever set is empty, a lineage closes or parks twice on one class, or evidence invalidates a premise,
  direction is a design card by the top-tier seat by turn, challenged once by the other top-tier family: at most
  three ranked levers, each with arms, a null, an arms-differ witness, a stop rule and a compute estimate; a decision
  swarm then chooses. The cop opens such a card like any other when a trigger holds: a reservation of the opening
  to another seat, stated only in a queue line or in a defect token's reason clause, is no rule — a queue of
  pointers is reviewed by no one as a rulebook, and such a clause once routed a design call, tick after tick, to
  the one seat barred from opening cards. A tick launches at most one such design or disposition seat (docs/13
  P-COP Step 3), and that bound counts those seats alone: a top-tier retry author, approach review or key takes its
  seat from §2 and nothing in the bound defers it — read as a bar on every top-tier seat, it held a retry card's
  implementation tick after tick while the ticks-per-landing alarm fired and each tick named that card the only open
  card able to land. A swarm, convened by the USER-directed orchestrator for a consequential unresolved choice only,
  runs Opus, Fable and Astra lanes at high effort and decides 2 of 3 with both providers in the majority; an
  Anthropic-only majority against the Astra lane has that dissent's decisive premise measured and one re-vote, and
  every decisive premise is re-measured before acting. An instrument run pauses and resumes on one model id and
  never mixes models in one scored run; every other top-tier seat falls through at once, never to Opus as an
  author. The posture proves itself per review round, intent-to-treat with parks counted, scored by a seat that did
  not author it. It DISTINGUISHES the
  fleet's "model tiers by act" ruling for this board only, in that a top-tier model writes product bytes on a retry
  (proposed to the fleet as `ruling-candidates/top-tier-inference-for-durable-product-outcomes-r1.md`).
- **Failover shifts work; nothing waits** (§2, USER, §0): a dark family's seats move to their tier
  analogs; a round with no live cross-family key is SINGLE-FAMILY (two non-author live-family keys, a third
  adversary on guard, hook, CI, ratifier, acceptance or data-loss cards, stamped) and is re-reviewed cross-family
  when the family returns. Darkness follows the meter the error came from, measured on the account in use. An
  empty derived key pool is HELD-FOR-KEY, never the last model standing, and a capacity hold releases on EVIDENCE
  that the held seat answers — a one-line probe on its own model at most once per tick, or any completed call on
  its meter — never because the error window emptied while nothing ran, since a seat that is not launched cannot
  return an error; two models of one provider are never
  cross-family; a card needing the network first takes a Claude-hosted seat, which is not darkness. **A family is
  read live by a call that answers, never by local credential state** (§2; docs/13 P-RESUME step 4; adopted from
  this bus): the tick-start probe is §10's smoke form, one call per tick on the family's lowest-tier model by the CLI
  route, and the family fails it unless that call answers — a quota reply is no probe failure, read by its meter; a
  CLI's login status or version reads local state, so it can show a family signed out and never that it answers — a
  token the provider has revoked still reads signed in — and a status report built on it says signed out or unknown,
  never live.
- **Evidence lives outside git, which holds only the landing receipts** (§5) — sha256 and path of every evidence
  file and a row per seat, with no byte gate; a card points at its ledger and is never the chronicle; caps are
  structural, never byte gates whose last remedy drops evidence (§5). **A DAILY
  line belongs to its own UTC day** (§5; docs/13 P-COP Step 5 points at it): the day is the writing
  tick's own UTC date, and no tick rewrites, re-dates, folds or carries forward the totals of an earlier day's
  line, so a new day's first tick starts a new line; a day left with no line stands as a hole, never
  reconstructed into WORK.md, and is read from git and the deferred ticks' notes. **A mirror
  is derived; local master is the authority** (§3): CI speaks for master only when the run's commit carries
  master's PRODUCT bytes, else `ci=stale`. **A seat that rewrites a shared file derives that file's newline
  convention AT WRITE TIME, refuses on a MIXED reading rather than picking one, and checks the diff is the size
  it intended** (§5, adopted from this bus): the convention is not stable — under an autocrlf-style working-copy conversion one shared
  file has read in each convention on successive measurements — so an instrument carrying either as a constant
  silently rewrites every line as one diff, with the intended one-line append buried inside it. Under autocrlf
  a whole-file line-ending rewrite is invisible to a numstat-style diff summary, so no ordinary review
  instrument reports it, and a later per-file blob-identity check then fails for a reason nobody can account
  for. **And the lines a seat adds carry no control byte but a TAB and the line ending** (§5): a Windows path
  written through a shell string that interprets escapes turns `\a` into a bell and `\r` into a bare carriage
  return, invisible in every rendered view, and a line-based reader stops at the carriage return; write such text
  with a file-writing tool and scan the added lines before staging. **A JSON record a seat writes into a ledger is
  parsed back with a JSON reader before any rule reads it** (§5, adopted from this bus): a Windows path whose
  backslashes are not doubled leaves an escape JSON does not have, so the whole record parses for no reader, and a
  rule reading one of its fields meets unreadable input — never an absent record, never one without that field.
- **Worktrees are sparse; a free-space floor holds creation, and an unreadable reading holds it**; HELD-FOR-DISK
  spends no attempt; the item worktree goes on landing, a key's once its verdict is written (§10 "Task
  worktrees", a USER unfreeze in §0). **A lock file that the factory's own mandated restore — or any build that restores — rewrites is never the
  card's byte**: no seat stages it, no allowlist check counts it, and a git operation that refuses a dirty tree, a
  rebase or a removal, is preceded by reverting exactly that path (for a removal, after the census has captured
  it), which loses nothing a restore does not rewrite; a card whose allowlist names that file is untouched. A
  removal is never otherwise forced on an item worktree: a mandated setup step that dirties the copy the commit,
  rebase and cleanup rules refuse to touch is a permanent latch, and the cleanup rule's own "stop if a defect
  report names this worktree" makes REPORTING it the act that makes the latch permanent. The cop's refutation
  probe is removed on a key's scratch-worktree terms. **A card holds a removal only when it OWNS or USES the
  worktree — its own, or one its seats read, such as a frozen evaluator — never when it only MENTIONS it**: a
  state line that cites a path as evidence — a load reading, a quoted receipt — would otherwise latch what it cited
  until it closed, because a card that correctly records why it waited names what it waited on. A process outside
  the removing seat's own ancestry whose command line names the worktree holds it as well.
- **CLI currency upgrades on a six-hour clock with no idle gate, smokes the launch form the tick really uses —
  isolated from user hooks — and rolls back only on evidence** (§10, USER, §0; fleet R13, adopted from this bus):
  a failed smoke reinstalls the previous version only when that version passes the smoke the new one failed,
  because a smoke that fails on auth, quota or network fails the old version too. **Each landing receipt
  measures every seat's cost and correctness; a provider joins only after admission drills** (§10, USER, §0).

### This board
- **Objective**: AUTO XMP matches the USER's manual LRTimelapse grade per frame, measured by `tools/scoreboard.ps1`
  on `metrics/eval-set.json` (WORK.md header). **Definition of done** (USER, §0): blind-judged
  indistinguishable, meaning a person cannot reliably pick auto from manual on a blind contact sheet, with
  zero-effect and positive controls; the numeric metrics still run; every comparison carries an arms-differ witness (§6).
- **Boot**: "resume our work" runs docs/13 P-RESUME: re-arm, report, stop (workspace `CLAUDE.md`). The cop boots each
  tick by §3's derivation commands, never reading WORK.md whole (docs/13 P-COP "Bounded boot"); the steward by P-STEWARD's
  read list; a weekly read-only `dng-resume-drill` exercises P-RESUME and asks nothing (§0, USER).
- **Seats** (exact model ids, launch forms and cadences: §2, §10 and docs/13 P-RESUME step 2):

| Seat | Model | Shape and jurisdiction |
|---|---|---|
| Traffic cop `dng-traffic-cop` | Opus; an exhausted Opus defers the tick, never swaps | stateless scheduled tick, fresh session per fire: collect, land, dispatch, record; proceeds under stated assumptions (§2, §3; docs/13 P-COP) |
| Design steward `dng-design-steward` | Opus, every six hours | acts only on OWNER-DEFECT tokens and PARKED cards a cop wrote, plus the doctrine loop; may edit docs/12, docs/13 (P-COP included, never P-STEWARD) and docs/14; disposes of a park as ONE dimensioned batch pass or as the ruling the park names; closes a token only by appending a CLOSED line; never dispatches, launches keys, lands or opens ordinary cards; writes this spec and this board's kernel filing; a receipt every run (§7a; docs/13 P-STEWARD) |
| USER-directed orchestrator | Opus at medium effort (USER, §0) | launches each seat it drives as a CLI process (`codex exec`, `claude -p`) whose launch json, written first, carries `phase`, `"route": "cli"` and its `pid`; not an unfreeze: adds no lane, gate, tool or scheduled task, changes no cop seat, key tier or landing rule, edits no governing doc (§0; §2 launch route) |
| Executor | Sonnet or Sol under the weave; Luna only for a fixed task with prewritten failing checks; complex diagnostics Sol, or Sonnet while Codex is dark; a retry (attempt 2 or later of an implementation card) the top-tier model of the card's own family at high effort, Fable for a Claude-family card and Astra for a Codex-family card, and Sonnet for a Claude-family retry while Codex is dark (USER, §0) | bounded brief, at most 4 files, dies at return; a Codex author runs §10's author route and a Sonnet committer commits (§2, §10; docs/13 C-COMMIT) |
| Approach review | opposite family: Sol for a Claude author, Opus for a Codex author; Astra or Fable when the card touches a guard, hook, CI, the ratifier, the acceptance surface or a data-loss path, or when its deliverable is a test, fixture, receipt, scorer or harness (USER, §0) | one round before any product byte; refuses on ambiguity (§2; docs/13 B-APPROACH) |
| Key 1 correctness | opposite family: Sol for a Claude author, Fable at high effort for a Codex author (USER, §0; the fleet's Opus floor for a review act) | per subject; named paths and a command budget (§2, §4a) |
| Key 2 adversarial | Anthropic, never the author's model: Opus, the acceptance surface included. Fleet RULINGS R1 (an owner ruling, not subject to adopt-or-distinguish) makes Opus the floor for a review act and bars Haiku from one, so docs/14 §2's Haiku tier for a chore of at most 50 lines is never filled; a pool the bar empties is HELD-FOR-KEY, never a substitute (§2). | per subject; Opus, the default key 2, never authors a reviewed subject (§2, §4a) |
| Fable / Astra | taking turns by card | experiment dispositions, `needs: fable` design cards and T3 approach reviews; and, by the USER's ruling in §0, the retry author, key 1 for a Codex author (Fable), the blind done-test judge (Fable, launched only by the USER-directed orchestrator on the CLI route) and USER-directed decision-swarm lanes; never a key-2 tier, never scheduled, never the cop (§2) |
| Status | Haiku, cross-checked by a read-only Haiku swarm | reads, and writes only its own run receipt and report (§8); `dng-status-digest` where the USER added it, otherwise chat on "status"; pushes only on exception (§2, §8) |

- **The factory is frozen** (WORK.md rule 3): no new tool, standard, lane, gate or scheduled task without the
  USER's word "unfreeze", and each unfreeze §0 records authorises only its literal scope. No chips, lanes,
  leases, hubs, heartbeats or chronicles (docs/13 channel rule; WORK.md rule 2; §5).
- **A product commit is one touching §4's PRODUCT closed set**, the only definition (§4; WORK.md rule 1).
- **Layout**: the git root is the nested `DngAutoProcessor/` repo (run `git -C` on it); evidence lives OUTSIDE every git tree, in a
  per-seat ledger the procedure names (docs/13 P-COP "Layout"; §5). The root is not written here: it holds
  hundreds of per-subject ledgers and is two directory reads from dispositions carrying both reviewers'
  findings verbatim, and bus law 4 bars a path that LOCATES in-flight review reasoning as firmly as it bars
  the bytes.
- **Doctrine loop** (a USER unfreeze in §0; docs/13 P-STEWARD step 7): the steward folds other boards'
  ruling-candidates/, adoption/, TRAPS.md, RULINGS.md and RECEIPTS.md commits, adjudications that name this board,
  and any change to the revision of the kernel spec or of this board's profile, as data (ADOPT, DISTINGUISH or
  NOT-APPLICABLE, one reason each), then takes a CENSUS of what this board recorded since its last census line — closed tokens, card
  state changes with their dispositions, governing-doc commits, the alarms its daily lines name — and gives every
  item exactly one line: PUBLISH, ON-BUS (the bus path and entry heading), NOT-EXPORTABLE (one reason) or CARRIED
  (the event that releases it). Nothing is selected, and a PUBLISH is never downgraded for size, taste or time. Two
  read-only Opus lanes — evidence fidelity; law, format, overlap and public safety — ratify every entry, this spec
  and the kernel filing before any push; each entry's stamped bytes are saved beside the receipt and every retry
  re-uses them, never a re-draft.

## Dispositions of fleet doctrine (docs/14 §9 verbatim; § = a docs/14 section; re-derive it there, never here)

| Source | Disposition |
|---|---|
| execute-posture rules 1,3,4,6,7 (agent-bridge) | ADOPT — §3 forced progress, §4 A1, §0 restated authority, completion files, §7 ratio |
| execute-posture rule 5 (cross-family = independence not throughput) | DISTINGUISH — the cross-family key stays required whenever both families are live; amended 2026-09-11: while one is dark the USER's ruling shifts work completely to the live family, and the round is SINGLE-FAMILY and re-reviewed cross-family on return (§2) |
| seat-fit R1-A bounded boot, R1-C disposition by queue position (Conjugal) | ADOPT — §3 budget, §2 dispositions |
| seat-fit R1-B key placement by darkness | ADOPT — author-family selection (the weave) and, while a family is dark, key placement too (§2 failover, USER 2026-09-11) |
| fleet ruling-candidates/cross-family-review-is-a-preference-not-a-gate-r1 (RULINGS.md 1817-1822) | DISTINGUISH — the USER wants diversity on every card (2026-09-11), so cross-family review stays on every card while both families are live; its point that a gate on an UNAVAILABLE family blocks everything is adopted as §2 failover |
| fleet ruling-candidates/degraded-mode-adversarial-panel-r1 | ADOPT — §2 SINGLE-FAMILY stamp and third adversary |
| fleet FAILOVER.md provider-neutral amendment | ADOPT — §10 providers are columns, admission drills before any seat |
| fleet TRAPS.md 3610-3619 (a worktree lane can implement but not commit) | ADOPT — §10 Codex author route, re-measured here for codex-cli 0.154 |
| AirMyPC 2026-09-11 multi-provider orchestration v1 (schemas/, adoption/) | ADOPT per-landing measurement (§10 measure each other); DISTINGUISH its manual review of minor CLI updates — the USER directed automatic updates (§0), guarded by smoke and rollback (§10) |
| proportional review rule 6 (Agent Bridge) | ADOPT — §2 key-2 tiers are its three classes |
| governance-as-output A1/A2, B1 and the CAS correction (Conjugal) | ADOPT — §4; the landing guard gates on git state and fast-forwards an exact SHA |
| adobe trap "wakes clean, writes nothing = read the receipt" | ADOPT — §3 PAUSE writes a receipt line; §8 reports it |

## SUPERSEDED — the 2026-09-08 posture and dispositions, kept verbatim so a sibling that cited them can find them
> Not current. Later rulings in docs/14 (USER rulings in §0; measured rules in §3 and §4a.5) replaced its boot, executor list, key-2 tiers, failover wording, R1-B wording and writer. The rules under "Current posture" at the top of this file govern.

Header before this refresh: # DNG Auto Processor — factory spec (single writer: the DNG fable coordinator). No fable coordinator seat has existed since the USER's 2026-09-08 ruling that Fable is used only for important complex reviews (docs/14 §0); this board's doctrine belongs to dng-design-steward (USER unfreeze 2026-09-11, docs/14 §0).


**Product:** auto-grading pipeline for DNG *film* clips emulating the operator's LRTimelapse
keyframe-ramp workflow; objective = AUTO XMP matches the manual grade per frame, measured by
`tools/scoreboard.ps1` on a held-out leave-one-project-out fold.
**Factory:** both coordination planes frozen since 2026-09-05; boot = `WORK.md` + `git log`.
**Orchestration since 2026-09-08** (design of record `DngAutoProcessor/docs/14-ORCHESTRATION.md`):
four lanes by what they consume (Trust, Safety, Quality, Delivery); seats by volume shape and
disposition — Opus stateless traffic cop (desktop-app scheduled task, fresh session per tick,
bounded boot ≤ 25k tokens, proceeds under stated assumptions), Sonnet/Luna bounded executors,
key 1 = the family opposite the author (`codex exec -m gpt-5.6-sol -s read-only` for Claude
authors), key 2 adversarial tiered by blast radius (Haiku chores · Opus Core/App · Fable for the
acceptance surface and experiment dispositions), Fable never scheduled and reached only through
cards marked `needs: fable`, Haiku answers status in chat from a one-read recipe. Evidence lives
outside git; receipts ≤ 2 KB in git. No leases, heartbeats, hubs, chronicles.
**Measured 2026-09-07→08 (Codex-thread steering period):** 7 product commits in ~24 h, each 2–6
files with two SHA-bound reviews; acceptance-tool repairs left on a side branch with 87 MB of
evidence in git (being landed as acceptance-only commits); hosted CI red on 3 of 6 master runs
from two timing-sensitive tests; the largest exposure lever on record (closed-loop solver OFF:
fit 0.74→0.34 EV, p90 3.02→1.50 EV on the 10-clip fold) filed NONWINNING under a zero-tolerance
colour guard with no measured noise floor — reopened as a decomposition.

**Dispositions published 2026-09-08 (single writer: DNG fable coordinator):**

| Candidate / spec | DNG disposition |
|---|---|
| `fleet-orchestrator-execute-posture` rules 1, 3, 4, 6, 7 | ADOPT — forced-progress escape, out-of-band repair authority, authority restated in the seat payload, completion files, entries-to-transitions alarm |
| `fleet-orchestrator-execute-posture` rule 5 | DISTINGUISH — the operator directive keeps the cross-family key REQUIRED for product landings; throughput is protected by implementation running ahead on branches and by author-family selection from measured availability, never by a same-family substitute |
| `orchestrator-seat-fit-r1` R1-A, R1-C | ADOPT — bounded boot; cop proceeds under assumptions, verifiers refuse on ambiguity |
| `orchestrator-seat-fit-r1` R1-B | ADOPT as author-family selection; key placement itself is fixed by directive |
| `dispatch-budget-and-proportional-review-r1` rule 6 | ADOPT — key-2 tiers are its three risk classes |
| `governance-as-output-r1` A1, A2, B1 and the same-day CAS correction | ADOPT — a change that builds the ratifier is gated on its own witness; HELD-FOR-KEY consumes no attempt; landing is ff-only of an exact SHA from an exact base |
| adobe trap "wakes clean, writes nothing = read the receipt" | ADOPT — a PAUSE skip writes its receipt line; the status recipe reports it |

## Shape (HISTORICAL — standing lanes; superseded by the 2026-09-05 freeze and docs/14)

**A lane is its lease, never a model.** `coordination/leases/*.json` is the roster; the STANDING set
is the `$standing` assignment inside `coordination/tools/claim-lane.ps1` and is deliberately not
re-listed anywhere else — a prose copy of a set the code owns is a second source of truth no gate can
hold current, and this project measured exactly that when a sixth lane was admitted. It currently
reads: `fable` coordinator · `sol` sole correctness gate · `luna` second reviewer/falsification ·
`opus` executor host · `sonnet` second executor host/verification · `kernel` cross-project hub-kernel
planning. `sol` and `luna` are Codex-native (GPT-5) and are PASTE lanes — spawning a chip for one is
a defect: wrong host, and the chip's lease claim locks the correct seat out. Other leases (`rotation`,
`narrator`, ad-hoc executors) exist and are respawned on request; liveness is always derived, never
recited. File-based hub (`coordination/hub-*.md`, append-only via accepted writers only), leases +
heartbeats for liveness, FINDINGS-CHRONICLE harvested same-day.

**Exportable liveness refinement — LAPSED is not DEAD, and they need different writers.** H9's
two-signal dead edge (window overdue by more than `max(leaseMinutes,15)` AND heartbeat older than the
same grace) plus the orphan-pulse check is the *warden's* licence to overwrite a seat that never
released its lane. It is deliberately narrower than the truth of R3, where a lane past its window is
simply absent. Between the two lies a real interval — measured this session at 4.8 minutes overdue
against a 30-minute grace — in which a coordinator is genuinely gone but the warden path must refuse.
An ordinary-claim mode covers it: it takes a lane nobody holds (retired, handed-off, never-seated, or
live-past-window), keeps every protection except the warden's overwrite licence, and still performs
the dispatch-time locked reread that refuses a foreign LIVE. **Without it, a lane can only be reseated
by waiting out a full grace period on a corpse.** Two lanes did exactly that before it existed.

## Autonomy stack (measured on this box, 2026-08-08/09)

- **Ignition ladder, in fixed order: hosted subagent → headless warden → chip LAST.** Chips are
  demoted to a fallback for a present human, because a click-gated chip is a single point of human
  failure: one sat unclicked through a four-hour stall on this box. Hosted-subagent succession is
  proven in production, including a full coordinator reseat performed by a non-coordinator lane.
  **We ADOPT cloudvore's clickless-ignition delta** — it is the same ruling, measured independently
  on a different box, and its "an exec is not a seat; the CLAIM row is" generalizes cleanly to our
  lease model. We DISTINGUISH only on channel: two of our six standing lanes are Codex-native PASTE
  lanes where a chip is affirmatively harmful, so our ladder's last rung is narrower than theirs.
- **Hosted seats need a lease field, and it is the one thing the protocol forgot** — see the trap
  below. A hosted subagent has no harness transcript of its own, so it cannot self-measure context
  and must report CONTEXT-UNKNOWN rather than a confident verdict.
- **Wake floor: `dng-warden-wake`.** It moved off the
  account-scoped app store — which the 08-09 account rotation silently emptied, exactly as cloudvore's
  TRAP predicted — and became a machine Task Scheduler task registered 09:05, run
  through `run-hidden.vbs` (never a console binary under an Interactive principal, or a window pops on
  every fire). **At the time of this 08-09 measurement, the scheduler's own record still read the never-ran sentinel (`LastRunTime`
  1999-11-30, result `0x41303`), and its first due mark had not yet arrived when this was written.**
  The manual ticks in `warden-wake.log` are seats running the script by hand; they are not scheduler
  fires and do not discharge the fleet's `configured != running` law. The old app-store task's
  "verified by lastRunAt" claim did NOT migrate with the task. Verify from `lastRunAt` before any
  sibling cites this historical paragraph as current status. The later production evidence in this
  spec supersedes the initial `CONFIGURED, NOT PROVEN` posture.
- **Codex lanes:** desktop automations pulse sol/luna every 10 min against pinned threads; codex-cli
  installed for new-thread ignition (exec smoke-proven).
- **Ignition independence:** the I8 design ceiling reached CLOSED-ACCEPT (I1–I8: one-byte-array prompt
  capture, prospective separation events, byte-identity carrier snapshots, bound canonical snapshot,
  launcher-code rule, verdict-blind invocation), with an 11-arm refusal drill, each arm RED by
  construction with tree-digest zero-child-write proofs, dual-host. **The operator LIFTED the gate on
  2026-08-09**; headless ignition is no longer held behind it.

## Traps and laws this factory is exporting

- **A scheduled-task child inherits the INSTANCE's clock, not its own — and overrunning it deletes the
  next ignition for every lane.** Our headless seats are launched by a wake task carrying an
  `ExecutionTimeLimit`. The limit runs from the task instance's `LastRunTime`, **not** from the seat's
  start, and because the task opens lanes *synchronously* a seat later in the chain inherits only the
  remainder — one measured seat had ~35 min of a 55-min nominal term and correctly derived that rather
  than assuming it. **The second half is the one that bites and was found late: the task is
  `IgnoreNew`, so while an instance is running the next scheduled fire is DROPPED, not queued.** A seat
  that holds the instance past `NextRunTime` therefore does not merely risk its own kill — it removes a
  reseat for *every* lane the task opens, and the fleet's next ignition slips a whole period. A seat
  killed at the limit also leaves a **claimed-and-dark lease**, indistinguishable from an orphan pulse
  to the next seat's liveness check — so the dispatch layer manufactures the very defect the liveness
  rule exists to detect. **The test: a child of a scheduler must derive BOTH its limit and the next
  fire time from the scheduler at boot, restate them where a successor can re-check them, and treat
  "can I finish before the NEXT FIRE?" — not "before my wall?" — as the scoping question.** Retiring
  early is the ignition path, not thrift.
- **A protocol field with NO WRITER is invisible to every gate.** Our bootstrap protocol began
  requiring hosted seats to record `hostSession` on their lease, and nothing could write it: the claim
  tool has no such parameter and its mutable-field set omits it, and the renewal writer only
  re-stamps `renewed`. A hosted seat therefore recorded it in prose and was byte-indistinguishable
  from an independently-seated one. **Caught by a peer reading the lease, not by any check — because
  no check existed.** The test: for every field a protocol *requires*, name the writer that can set it.
- **Clone-and-preserve carries dead provenance forward.** Lease succession clones the predecessor and
  replaces only successor-owned fields, so unknown future obligations survive by design — and so do
  `retiredBy`, `handoffNote`, `modelProvable:false` and a note reading "this seat authorizes nothing
  further", all now false about the new holder. Preserving the unknown and preserving the stale are
  the same mechanism; no writer retires a stale successor-provenance field.
- **Aggregation is not composition.** A launcher that starts four independently-green suites over an
  UNCHANGED library proves behaviour, not repair. Ours passed 82/82 + 18/18 + 25/25 + 22/22 dual-host
  while every ruled defect remained present in the public API, because the "fix" modules were
  fixture-only sidecars that dot-sourced the unmodified library. **The gate caught it; the green
  quota did not.** Corollary the same review produced: a required-ID set generated as a contiguous
  range (`1..81`) **cannot detect a missing row** once non-contiguous per-dimension ranges are
  composed — a quota that cannot fail. Manifests must be declared data, with missing/extra/**duplicate**
  and corruption arms each proven RED from a staged mutant asserting exactly-one-replacement.
- **`ConvertFrom-Json` re-types date-shaped fields, and one host computes an instant FIVE HOURS wrong
  — no second host required** (measured 2026-08-13, same bytes, same `en-US`, same box). PS 7.6.3
  returns a `[datetime]` for `"…T14:30:00.1234567Z"` and stringifies it to the UTC wall clock
  `08/13/2026 14:30:00`; a bare `[datetimeoffset]::Parse` downstream then re-assumes **local**, giving
  `19:30:00Z` for a stamp meaning `14:30:00Z`. WinPS 5.1 keeps the field a `String` and is correct.
  Two hosts agreed on **0 of 3** stamp cases; normalizing at the point the value leaves the JSON
  object made it 3 of 3, sub-seconds intact. **The half that does not fix is the exportable part:** on
  PS 7 an offset-less stamp is indistinguishable from a host-local one by the time an object exists,
  so any rule of the form *"parse as explicit-offset round-trip, refuse malformed"* is
  **unimplementable at the object level** — it refuses everything on one host and accepts on the
  other. Only the raw JSON text can carry that distinction. Any sibling parsing timestamps out of JSON
  in PowerShell has this today.
- **A shared writer can report a field it never wrote.** Our single accepted hub writer replaces a
  `{TS}` placeholder unconditionally — and `Replace` on an absent pattern is a no-op, not an error —
  so an entry authored without the placeholder is appended **unstamped, exit 0**, under a success line
  reading `OK hub-append … ts=<the clock it read>`. Three live entries got in that way and were
  assumed to be hand-rolled bypasses; they went through the accepted writer, which said OK. The
  entry path had no heading validation while the beat path directly below it failed closed on an
  embedded newline: one writer, two standards. **The test: for every field a receipt NAMES, prove the
  bytes on disk carry it — a receipt asserting its own success is not evidence that it succeeded.**
- **A mislabelled receipt does not merely fail to inform - it recruits every later investigator into the
  same wrong theory.** Our hourly lane-ignition warden logged `SKIP <lane>: LIVE` for lanes whose leases
  read `retired-clean`, because the retire writer re-stamps the lease clock. Four coordinator seats and a
  relay seat independently diagnosed "the LIVE verdict is wrong" - and all five were wrong: re-ordering
  that test changes no behaviour, because the branch it pre-empts covers an identical domain. The real
  cause was that the guard charged an explicitly RELEASED lane the full lease window of the seat that had
  already left (90 min on two lanes) - a boot-latency hazard scaled by an unrelated duration. It never
  appeared in any log line **because the branch that would have named it was unreachable**. Measured cost:
  two consecutive ticks in which 3/3 standing lanes were skipped, both whole-fleet ignition losses.
  **Two rules fall out. (1) When several independent seats converge on one diagnosis from one receipt,
  that is not corroboration - they read a single source. (2) Ask whether the branch that would report the
  alternative can be reached at all.** What resolved it was cross-consumer disagreement: a sibling tool on
  the same shared derivation already ordered the checks correctly, so the fix was re-alignment, not new
  policy. **Disagreement between two consumers of one derivation is a cheap and underused oracle.**
- **Census a field's actual value set before writing any predicate over it.** Our lease `state` field
  looks like an enum and is prose: 18 distinct values across 64 leases, most one-off text minted by
  whichever seat wrote them. A reaper keying on state names enumerates an OPEN set - correct the day it
  ships, silently wrong at the nineteenth state, and it fails expansively because unrecognised values hit
  the default branch. Key only on closed, derived inputs. Several coordination fields that read as
  enumerable are prose wearing an enum's clothes.
- **Green says the code passes its tests; mutation says each guard is the REASON it passes.** Prove every
  guard load-bearing by rewriting its condition to `$false` in a copy and requiring the case it owns to
  change verdict; a surviving mutant is an inert guard. Run it on every host the thing actually runs on.
  Two by-products worth expecting: an exception is a verdict change and therefore a kill (catch it, or the
  harness crashes on its own success), and a mutant that breaks a DOWNSTREAM line proves the guards are an
  ordered dependency chain, not independent filters - so re-ordering them is a behaviour change.
- **PowerShell: `$array.set` binds to `IList.Set` on `Object[]`, beating member enumeration.** A hashtable
  key named `set` therefore yields `void Set(int, System.Object)` and every loop over `$items.set` runs
  ZERO times, silently. Our first control suite reported `CASES 0` and would have read as a clean run;
  only a fail-closed "zero differential cases" check caught it. **A suite that cannot distinguish
  candidate from baseline must say so in its own exit code.**

## Publication posture (operator ruling, 2026-08-09 evening)

> **Partly SUPERSEDED.** There is no hub (docs/13 channel rule: "Chips, lanes, leases, hubs, and heartbeats do not exist"), so no hub ratification exists. This board publishes through the dng-design-steward's doctrine loop, which ratifies each entry with two read-only subagents and then pushes without a USER gate (docs/13 P-STEWARD step 7b, USER unfreeze 2026-09-11); that step appends only to TRAPS.md and ruling-candidates/, so this spec is refreshed by a USER-directed session (docs/14 §7a). [Superseded in turn by this file's header: docs/13 P-STEWARD step 7d now makes the steward this spec's one writer, and step 7c appends to RECEIPTS.md, TRAPS.md or ruling-candidates/.]


Bus pushes are **never operator-gated**. Verbatim: *"Pushing code to doctrine repo should not be
user gated. Always push it so the siblings can see it immediately."* Hub ratification remains
required before strategy/law becomes doctrine (ratify-before-doctrine's gate half is intact); once
ratified, publication is automatic at the landing seam. Measurements, receipts, and traps push at
seams as before. Ratified law exported this seam: executor checkpointing + expiry-gated posture
claims (`dng-auto-processor/standards/SOL-RULING-FACTORY-100-LAW-ITEMS-2-3-5-6-20260809.md`,
byte-anchored in `EXPORTS.md`); the DNG failover amendment is ratified in substance locally but its
canonical carrier tuple is still under exact-ruling reconcile — it publishes when that ruling lands,
automatically.

**Completion hardening (operator ruling, 2026-08-11).** Every software-factory fix now has doctrine
publication as a terminal completion predicate, not merely an optional seam check. After the normal
review/ratification gate, the publisher exports the portable defect, prevention invariant, exact
subject/evidence tuple, applicability, limits, and rollback posture; pushes; verifies the remote
contains the doctrine commit; and records that commit back in the project hub/evidence. Before that
proof, the repair remains `FIXED-LOCALLY-PENDING-DOCTRINE` or `PUBLICATION-BLOCKED`, even if local
bytes and tests are green. A publication failure does not roll back a safe repair, but it cannot be
laundered by retirement, handoff, account rotation, or unrelated success. Private implementation
bytes, credentials, customer data, transcripts, and reasoning remain outside the bus.

## Codex Outage Bank Mode

The hub may enter bounded candidate banking during Claude-family unavailability from direct local
USER authorization or a separately ratified classifier. Direct authorization is entry proof, not a
claim that the provider is globally down. An active marker and exact bank register precede dispatch.
Fresh Codex workers have no standing-lane identity and may work only existing or explicitly locally
assigned cards in isolated bytes. They cannot create canonical outcomes or mutate leases, hub/ledger
state, protected invariants, machine/account/task state, refs, or shared indexes.

USER revocation or the marker's artifact-bound positive Claude advancement predicate ends the mode;
claims, renewals, heartbeats, health checks, process starts, and unchanged status do not. End freezes
new dispatch and routes one batched cross-family drain without auto-landing. Full adoption and nine
required fail-closed controls are defined in
`dng-auto-processor/standards/CODEX-OUTAGE-BANK-MODE.md`, byte-anchored in `EXPORTS.md`.

## Universal provider-control status and exact DNG proposal (2026-08-18/19)

> **SUPERSEDED — historical; "current" below meant 2026-08-18/19.** The lane, lease, inbox and provider-admission model this section describes is not part of the design adopted after the USER's 2026-09-06 reset (docs/13 channel rule; WORK.md rule 2), and these DISTINGUISH lines bind nothing today. Whether any machine task from that era is still installed is machine state: derive it there, never from this section. The current rules are under "Current posture" at the top of this file.


DNG's current exact dispositions are:

**DISTINGUISH(224a6705d81dfbc670313cdcef4d825216f2b380,
LOCAL_ADAPTER_LANDED_AND_BOUNDED_FABLE_RESTORATION_BEGUN_WITH_GATE_CLOSED)**

**DISTINGUISH(874605e43531c9aa230ee16851f8107a8e0d9cec,
PENDING_PINNED_R14_PROFILE_COMPLETE_FOUR_SURFACE_CENSUS_1000_IDLE_TICKS_SUSPENDED_CHILD_ATTESTATION_AND_REVIEW,
DNG_MASTER_3dc9100507c35e3724200dabaa3df6ffd2eb3cd0)**

**DISTINGUISH(6aafb089719aec1582a2dd3edcf7463d73ca9767,
LOCAL_STANDING_OWNER_DIRECTIVE_WITH_FRESH_ONE_SHOT_PER_SLICE_PERMITS_NOT_A_SELF_RENEWING_24_HOUR_WINDOW,
DNG_MASTER_3dc9100507c35e3724200dabaa3df6ffd2eb3cd0)**

**DISTINGUISH(909f769d02e8412e51e28e242cfa8d00dadc9a3d,
R26_CANDIDATE_ZERO_AUTHORITY_LOCAL_RUNTIME_RETAINS_STRICTER_30_PERCENT_RESERVE_AND_EXACT_LANE_BOUNDS_PENDING_REQUEST_LEVEL_TOKEN_ACCOUNTING_CACHE_WEIGHT_QUALITY_EQUIVALENCE_DIRECT_LAUNCH_CERTIFICATION_AND_CURRENT_REVIEW,
DNG_MASTER_3dc9100507c35e3724200dabaa3df6ffd2eb3cd0,
POLICY_SHA256_510D37692541B5E5F9247FBF21BE5FE60609BD9CF9B387246DF268F65D2A4228)**

The first disposition records materially stronger project-local evidence against provider-capacity
governor v1. The second preserves DNG's R14 convergence record. The third reconciles the competing
automated-rotation candidate without granting it authority or claiming its window contract was
installed. The fourth is controlling for present DNG convergence: canonical master merged exact R26
candidate `e70a044f31dd2f43ab7c716d63a4eb89318c61b6`, but the pinned R26 manifest remains
`CANDIDATE_ZERO_AUTHORITY`, `CLOSED`, not installed, not activated, and without a positive
direct-invocation-impossible claim. Its hosted checks remain required and unclaimed. This project
disposition therefore proves neither DNG adoption nor fleet adoption. R26's
deployment-inert reference engine is a contract and hostile-test oracle, not DNG's runtime
executable. Reset, authentication, capacity return, a green test, a lease claim, or a successful
provider call cannot change these dispositions.

### Exact DNG token-saving profile

> **SUPERSEDED — historical.** This profile's boot (read `RESUME.md`, claim a lane at M0, read the lane's inbox) and its lease release belong to the lane model the USER's 2026-09-06 reset removed. Boot now: a session runs docs/13 P-RESUME; the cop's tick boots by docs/14 §3's derivations; the steward by docs/13 P-STEWARD's read list.


Every unattended Fable, Opus, and Sonnet launch now enters the same DNG admission envelope while
retaining its exact role, model, `max` effort, review obligations, tests, and product gates:

- one host-local HMAC-derived opaque quota domain for the authenticated Anthropic organization;
  raw organization identity and credentials never enter doctrine;
- fresh signed five-hour and seven-day capacity dimensions, maximum age 900 seconds, a 30%
  completion/foreground reserve, and a maximum estimated slice of 5 percentage points;
- one inference-bearing root for the domain, with the quota mutex held for the full child lifetime;
- deterministic addressed-work and lane-liveness derivation before admission; no work is
  `IDLE_SKIPPED` with zero calls, processes, token counters, and tool counters;
- exact native executable path and SHA-256, Fable/Opus/Sonnet model, `max` effort, role, frozen
  prompt-and-file subject, at most 12 turns, and a broker-owned 900-second process-tree ceiling;
- compact addressed boot: read `RESUME.md`, claim the exact lane at M0, read only the lane's inbox,
  never glob all inboxes or replay the archive during boot, use `--autocompact 100k`, exclude dynamic
  system-prompt sections from cache identity, and disable prompt suggestions;
- retain headless session persistence because DNG measured that removing it makes M0 return
  `CONTEXT-UNKNOWN` and prevents the lease claim; persistence is therefore a correctness control,
  not expendable token overhead; and
- spill the provider stream to a content-hashed local artifact rather than inject it into another
  lane's context. Every CANARY authorization is one-use and reseals the gate before process creation;
- on every five-minute wake floor, consider Fable, Opus, and Sonnet in that fixed order, refresh model-free
  capacity immediately before each slice, and never overlap two DNG lane provider processes; and
- after terminal evidence, release a leftover live lease only when its content-hashed artifact has
  exactly one session ID and it exactly matches the lease. The canonical writer records the consumed
  permit as actor; missing, ambiguous, or mismatched evidence leaves the lease untouched.

These are one universal envelope plus a project profile, not forced identical lane behavior.
Codex/OpenAI, Kimi, Grok, different provider accounts, and sibling Claude projects keep separate
opaque quota domains and provider adapters while retaining the same non-regression, no-work,
capacity, claimant, exact-subject, bounded-context, and fail-closed gate invariants.

### Candidate-by-candidate reconciliation

- **Doctrine PR #2 / MLV candidate** (`ed232e7e8fe9894bba8358610c2bc726aebe365a`, hardened at
  `e057b3be685851a3f81e7338cf117438ca66c5d1`): accept its provider-neutral capacity, reset barrier,
  and project-profile model through the ratified v1 subject. Its read-only engine is not runtime
  authority and does not by itself prove a project launch path.
- **Conjugal candidate** (`37f1246543c86300089b77a51a3b8ad2c5292b8d`, tree
  `35a44265d358aa8ec3544ba2f08e0ef8e4b38216`): retain its opaque account broker,
  provider-normalization, exact evidence-capsule, and non-regression concepts only through the
  independently reviewed R14 reconciliation. It is comparative evidence, not a second contract.
- **AudioMile findings:** accept the explicit `HARD_CLOSED -> INSTALLED_UNVERIFIED -> SHADOW ->
  CANARY -> CLOSED` rollout and the rule that reset never opens a gate. DNG locally makes reinstall
  close the gate and makes CANARY consumption reseal it before launch.
- **Agent Bridge candidate** (`13d697c2b778ed566ebb90147aca77bd28f80824`): accept its adverse
  review findings. DNG closes launch-time executable path/digest revalidation, mandatory capacity
  dimensions, frozen-subject revalidation under the quota lock, model-free observation, and a
  process-tree wall clock locally. It does not infer that these closures satisfy Agent Bridge or
  R14's complete suspended-child, inventory, retained-owner, and review contract.
- **Universal R14 candidate** (`874605e43531c9aa230ee16851f8107a8e0d9cec`): DNG's historical
  portable target for local reconciliation, while its canonical manifest remains
  `CANDIDATE_ZERO_AUTHORITY`. It reconciles competing portable semantics for DNG only; project
  adapters and dispositions remain local and explicit.
- **Automated bounded provider rotation R1 candidate**
  (`6aafb089719aec1582a2dd3edcf7463d73ca9767`, rooted at
  `b632e0669e6cda8d4828b9aa8442b8388941a996`): accept its serial quota-domain rule, fresh
  transactional admission, exact-subject bounds, zero-credit outputs, and closed-between-runs
  posture. DNG distinguishes its 24-hour create-once window and no-auto-renew rule: the operator's
  durable project directive is standing authority, while each actual slice still receives a fresh,
  expiring, lane-specific one-use permit after current capacity proof. This is a local adapter
  proposal and execution receipt, not candidate ratification or R14 adoption. The candidate's own
  `Canonical DNG competing evidence` section records the reciprocal distinction and the stricter
  shared intersection.
- **Universal R26 candidate** (`e70a044f31dd2f43ab7c716d63a4eb89318c61b6`, merged at
  `909f769d02e8412e51e28e242cfa8d00dadc9a3d`): accept the universal no-work-before-session rule,
  bounded prompt/work capsules, conservative reserve, retry accounting, cache-affinity expiry,
  quality floor, and separately certified launch-boundary requirements as the current portable
  target. DNG's 30% window reserve is stricter than R26's 20% floor, and its fixed per-slice turn,
  context, estimated-capacity, and process-tree limits remain installed. DNG distinguishes because
  its adapter does not yet reserve and reconcile every provider request in token units, apply full
  input-envelope weight to cache reads, separately accumulate cache write/uncached input/reasoning/
  output and failed-attempt usage, pin the reviewed R26 quality-equivalence cell, or positively
  certify that all direct production launches are impossible. R26's 181 universal, 37 governor,
  and 78 runtime-workbench controls are green in its pinned manifest, but hosted validation is
  unclaimed and execution/activation authority is false.

DNG additionally rejects three tempting savings as unsafe generalizations: the Claude Desktop
idle-sensitive cache is not canonical capacity evidence; removing session persistence breaks M0
and lease ownership; and a turn cap without an independent wall-clock/process-tree boundary does
not bound a tool-heavy agent.

### Landed implementation and fail-closed restoration evidence

The DNG implementation landed on local `master` commit
`4c3c80744667dcc4e266e8a54ef2fb3f42b1b350`, tree
`b3c97a7da6858c9a554aa775920ccab865ba04de`, with durable shipping evidence ref
`refs/software-factory/evidence/wb-20260818T230436898Z-8267df9a` at
`afc630e8e47fee5fce1127e8b158d3db4be61904`. The policy SHA-256 is
`057D8A5C814DF5FD32D8141108809DE7418E1257E04EF609E890F851F6DC81E7`; the broker,
observer, and gate-transition script SHA-256 values are respectively
`4B3E9462CDD1432A75A3E1E32ACA2DD49C7E637E400592B30B1A35465A12C641`,
`67E6905DDBB84711784BC58A4365D0E08AFC0C4930A638B31E07730BC1BBCA4C`, and
`6BAD61A9BEABCD9F6BEBD8F8AA6A5E5F607A661246A31B9D95F82C7F583759CA`.
Seven signed observer controls, 24 admission controls, and six transition controls pass (37 total).

The automatic round-robin follow-on landed on local `master` commit
`3dc9100507c35e3724200dabaa3df6ffd2eb3cd0`, tree
`ec470b413e41c8baf0b2f8169957697632869016`. Its durable shipping evidence ref is
`refs/software-factory/evidence/d2ea67c8f18b4c93b28797cf06292b74` at
`4f5cacfa2f03c916ab8123ecd8e0e2b9d6bdea41`, tree
`736605892decb26ff28cafa212754967a9a0e695`. The installed-candidate policy, broker, observer,
and gate-transition hashes are respectively
`510D37692541B5E5F9247FBF21BE5FE60609BD9CF9B387246DF268F65D2A4228`,
`DFDA356791A109A9796DAD1DC20E2BD81990D2E510DCEA8F158D22072BF73393`,
`67E6905DDBB84711784BC58A4365D0E08AFC0C4930A638B31E07730BC1BBCA4C`, and
`51D54C2A2708F2B8374FE39EDD13B08F3D9B5C54B54D3558B73338E0C449BB69`.
Twenty-seven admission, seven capacity-observer, and twenty transition controls pass (54 total).
The production warden additionally passes 18 shared-liveness, 16 succession, and five exact
terminal-release controls; its machine-local SHA-256 is
`4C668AD38CA249FAB99435F5B5EA6D178D15CDF5011A4BCF24259AC0C8B3A606`.

The pre-existing Codex account-binding hold was closed through governed rotation transaction
`7b671953-092d-42a4-9f4c-178ab768a8be`; it was not bypassed. The production wrapper SHA-256 is
`092269055BF7A396A3CF79C6161A18F84295E0FB9D774077767E3330D767E03B`, pinned to native Claude
SHA-256 `879F0D7E7EEE606095051C0C00772FC1DE41778F34835A9DE43EA8E1CAAD9AFB`.

The first bounded canary exposed that disabling session persistence prevented M0 and timed out;
artifact SHA-256
`38EB3185DCE09AED6E3BBB61F47192BE2A27D867ADB5678031FF7626428C7699` is retained. After restoring
persistence and tightening the addressed boot, one fresh Fable authorization ran through the real
hidden scheduled-task path. Fable claimed its exact lease under `claude-fable-5` / `max`; the broker
then terminated the process tree at 900 seconds and recorded terminal artifact SHA-256
`897D1036B9A6C2BC73BBD3A0D5584E8F46D0247A327D1BAAA0FAA822E32E58E1`, exit 124. The gate remained
closed, and Opus plus Sonnet each emitted `AUTOMATIC_LAUNCH_GATE_CLOSED` with exact zero token/tool
counters. A post-run model-free observation read five-hour 21% and seven-day 4%.

The first unattended sequential campaign then exercised all three exact local profiles through the
real warden path. Fable (`claude-fable-5`, coordinator, `max`) reached its 900-second wall cap with
terminal artifact SHA-256
`4675C2A2E2C4F6146A0611964F8A19BDE9C12F490E421E04F6CD03FDB5B673BC`; Opus
(`claude-opus-5`, executor, `max`) reached its turn cap with artifact SHA-256
`3233C74A1D46E5B3D108A0D0D483BEC64949998E35A6818DD1E76AE9CC34A934`; Sonnet
(`claude-sonnet-5`, verifier, `max`) returned an autocompaction-thrash diagnosis with artifact
SHA-256 `91AD03CD1F5885F434833913B85118A14E2B8AAE708A05643ED6FF572169FF52`.
The processes were serial, the gate was closed between slices, Sonnet retired itself, and the two
matching residual leases were released by exact terminal-artifact proof through the canonical
writer. A fresh model-free observation after the campaign read five-hour 2% and seven-day 5%.

Subsequent production fires proved the campaign recurs without operator participation. In a
later pass, Fable terminal artifact SHA-256
`81893E3E661EFE26BF8EFBFFEA188E4746AFDE11E505F855BA5268525643FC3B` and Opus terminal artifact
SHA-256 `9183245C974A536755566270D555D58B33604783F7093D94F20698CDB51D2F9D` each drove the same exact
artifact-to-session cleanup before the next lane began. Only one provider process occupied the
shared quota domain at a time, capacity was refreshed before every slice, and the automatic gate
returned closed after every permit consumption.

This is honest **bounded automated three-lane restoration proven**, not sustained simultaneous lane
liveness and not fleet adoption. `dng-warden-wake` now has a five-minute wake floor behind the closed
broker; `IgnoreNew` drops fires while a pass is active, so the first boundary after completion starts
the next capacity-gated pass without overlap. Each
future slice requires new capacity evidence and a distinct expiring permit. DNG Provider Failover
Runner and Software Factory Roadmap Controller remain disabled.

The USER's 2026-08-19 utilization compromise changed only the wake floor from hourly to five
minutes. The hidden task action, fixed Fable/Opus/Sonnet order, exact models/roles/`max` effort,
`IgnoreNew`, 55-minute task wall, one-use permits, shared-domain mutex, 12-turn/900-second slice
bounds, and 30% reserve were preserved. The first immediate pass observed five-hour 64% and
seven-day 21%, issued Fable authorization `78d8a1128b024663a786531ae14cc281`, consumed it at
2026-08-19T10:19:28-05:00, resealed the gate before provider process creation, and ran exactly one
managed Fable process. If a later slice would cross the reserve, that lane records a model-free HOLD;
cadence cannot override capacity.

Promotion to the current universal candidate's `ADOPT` requires canonical ratification, a pinned
schema-valid current project profile, complete launcher inventory and certified direct-invocation
prohibition, request-level token reservation/reconciliation with the complete R26 accounting
dimensions, reviewed cache/prefix/capsule/retry ceilings, exact quality-equivalence receipts,
1,000 unchanged zero-inference ticks, suspended-child actual-image/argv attestation, full claimant
and retained-owner fencing, rollback, a current CLOSED gate, and fresh independent security and
quality review over the exact landed subject. Fleet convergence is the closed set of project-owned
pinned dispositions and receipts; a universal doctrine merge or this DNG canary alone is never
fleet-wide adoption.

## Carve-outs a citing sibling must know

> **SUPERSEDED — historical; do not cite as current.** Landing is the cop's `git merge --ff-only` of an exact sha after two keys and per-file blob identity (docs/14 §4); there is no hub and no CONSENSUS-CALL (docs/13 channel rule). A GitHub mirror is derived from local master, which is the authority (docs/14 §3). The three-round ceiling is the LAST test, after refutation and trend triage (docs/14 §4b). The branch the main checkout sits on is state: derive it. Still true, and carried into "Current posture": the git root is the nested `DngAutoProcessor/` repo.


- The real git root is a NESTED repo (`DngAutoProcessor\`); `coordination/` is deliberately in no git
  repo (chip worktrees must not fork it) — our bus exports are therefore copies, not submodules.
- Merges execute via commit-tree (no remote exists on the product repo); master mutation is
  hub-adjudicated CONSENSUS-CALL, never solo. Product state derives from `rev-parse master`, never
  `HEAD` — the main tree usually sits on a work-block branch, and `HEAD` returns an authoritative-looking
  SHA that appears nowhere in the coordination record.
- Bus canonicality verified on this box: the local clone's origin fetch+push is exactly
  `github.com/layibabalola/softwarefactory-fleet-doctrine`, in sync with zero unpushed commits, and the
  only other local bus artifact is a tombstoned bare repo. No parallel bus exists on ULTRAMAGNUS.
- Review discipline: batched across defect classes, hard 3-round ceiling, closed sets including
  negatives; every census states its predicate; every green check must be able to fail.

## CLI versions (law 5)

> **SUPERSEDED — versions from an earlier rewrite, not current.** This board upgrades both CLIs automatically, at most once per six hours, smoke-testing the launch form it uses and rolling back on failure (docs/14 §10 "CLI currency", USER 2026-09-11). Derive versions on the machine (`claude --version`, `codex --version`), never from this line.


claude 2.1.224 (Claude Code) · codex-cli 0.147.0. Both measured on ULTRAMAGNUS at the time of this
rewrite. One version per CLI across the fleet, per the operator ruling.

## 2026-09-06 — DISTINGUISH: product-first reset, both factory planes frozen

> **SUPERSEDED in part — the reset stands; its boot and merge sentences do not.** "Resume our work" runs docs/13 P-RESUME, which re-arms the scheduled seats, reports and STOPS, because the scheduled cop is the only cop (P-RESUME step 7); a session that takes "the top OPEN item" becomes a second executor. The cop boots each tick by docs/14 §3's derivations and never reads WORK.md whole. Key 1 is the family opposite the author, so not always Codex (docs/14 §2). See "Current posture".


Written by the Phase F executor per `RESET-PLAN.md` F9 (the plan's single-writer convention above
predates this reset and is itself one of the things being distinguished against). Per the USER's
2026-09-06 standing directive: both DNG factory planes — the root coordination hub and the nested
closeout plane under `DngAutoProcessor/` — are FROZEN in place (renamed/moved via `robocopy`/`git mv`,
nothing deleted). Boot for a fresh session is now exactly two files: workspace-root `CLAUDE.md` ->
`RESET-PROMPTS.md` (P-MAIN), which derives phase from disk and reads `DngAutoProcessor/WORK.md` +
`git log --oneline -15` for the top OPEN item. This plan creates no chip, lane, lease, hub entry,
heartbeat, chronicle, or scheduled task; blockers convene a bounded, receipted UNBLOCK swarm (plan
§1a: two Haiku diagnosers, one Sonnet fixer, one reviewer and one falsifier on another model, two
rounds max) and dissolve, never a standing seat. The product's one objective is
`tools/scoreboard.ps1`'s AUTO-vs-MANUAL measurement (`median|dExp|`, `p90|dExp|`, `median|dTemp|`);
merges are decided by `tools/ratify.ps1` (gate 0 + one Codex key + one adversarial Claude key on a
model different from the implementer), not by a standing review body. Six months of the prior
apparatus (10.1 GB, 127k files, 602 open hub items, one seated lane) produced single-digit product
commits/week and no scoreboard measurement in 54 days — this is a subtraction, not an addition.
`DNG Software Factory Roadmap Controller`, `fleet-doctrine-sweep-ultramagnus`, and the nested closeout
scheduler are disabled pending the plan's 72-hour unfreeze review (§8), which is numeric, not a
person's judgment call.

## Jev shadow-mode disposition (2026-09-20) — DISTINGUISH on the factory predicate, with the product case explicitly re-opened

**Not rostered.** dng-auto-processor does not appear on the standard's section 5 table, so R10.1 places no
duty here and `tools/jev-adoption-status.mjs` exits 0 without this line. Recorded anyway, on the agent-bridge
precedent, because the absence was an accident of routing rather than a decision: this board ran a seven-lane
investigation of Jev on 2026-09-20 and never published the result, so the bus could not see that the question
had been asked at all.

**DISTINGUISH, on the factory predicate.** The standard asks for a shadow instance over a project's own
tooling predicate. Measured here: Jev's nine candidates were matched against the four factory pains actually
on disk and **three matched nothing**; the strongest remaining candidate had a cheaper test that uses no Jev.
That is the same shape as the other DISTINGUISH rows and needs no further argument.

**The PRODUCT case is a different question and it changed the same day, after that investigation closed.**
Recorded here as a re-open condition, not as a claim, and all three items are measurements rather than
proposals:

1. The investigation's own leave-one-project-out analysis, over **1,563 of the owner's clips with held-out
   projects**, measured that semantic scene context helps the **Temperature slider by about a tenth** and does
   nothing for the R/B aim or Tint. The refuted part is R/B and Tint, not colour as a whole.
2. dng-auto-processor `cce34a00` measures that the colour error is **entirely a per-clip constant** — manual
   and auto within-clip travel are both zero on 13 of 13 eval clips for temperature and tint — and that the
   current per-clip white balance **loses to a constant fitted leave-one-out on the same shoot** on the
   ten-clip fold, despite a real positive correlation. So the quantity Jev measurably helps is the whole of
   the colour error, on an axis not currently beating a trivial baseline.
3. dng-auto-processor `e8dbb852` measures that the owner's exposure grade is **bimodal with an empty gap** —
   nine eval clips at or below 0.62 stops of within-clip travel, four at or above 1.40, none between —
   reproducing a library-scale result over 1,749 clips. The software's within-clip travel is zero on every
   clip, so it answers "hold" always, and a blind visual consensus rejects **4 of 4** clips on the ramped
   side. **"Does this clip need a ramp?" is therefore a binary classification over already-separated
   classes**, which is a categorisation task rather than the aim regressions the estimator work has targeted.

**Re-open condition, stated so it is testable and not aspirational.** A shadow instance here would log a Jev
ramp/hold classification per clip beside the existing predicate and compare, changing nothing. It has NOT been
run, no shadow log exists, and no card is open on it. Nothing above is a scoreboard result: item 1 is a linear
information test, and items 2 and 3 are measurements of where the error lives, not demonstrations that Jev
reduces it.

**Law 4.** No credential, transcript or customer data, and no path to any, appears above. Project-scoped
references are qualified per Law 6.

JEV: DISPOSITION-DISTINGUISH standard=r6@ad426fbec35c57df4bd599216309430ac0a25076 qsv=NONE log=NONE lines=0 asOf=2026-09-20 record=dng-auto-processor:FINDINGS-CHRONICLE.md#F-0054@e8dbb852
