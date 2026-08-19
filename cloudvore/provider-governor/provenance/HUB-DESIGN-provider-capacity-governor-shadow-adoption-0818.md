# HUB DESIGN — Cloudvore provider-capacity governor SHADOW adoption

Status: **DESIGN ONLY / NOT ADOPTED / AUTOMATIC LAUNCH GATE CLOSED**  
Observed: 2026-08-18T23:14:17Z  
Scope: local Cloudvore adoption of the ratified fleet provider-capacity governor; no provider,
test, hosted, Git-ref, scheduler, auth, publication, or release action was performed.

## Answer first

The fleet has one ratified portable specification, but Cloudvore's lanes do **not** all conform to
it yet. Fleet doctrine explicitly records
`DISTINGUISH(224a6705d81dfbc670313cdcef4d825216f2b380,
PENDING_LOCAL_ADAPTER_AND_DRILLS)`. Current Claude and Codex launchers invoke their CLIs directly;
Kimi and Grok use strong provider-specific adapters, but none of the four provider families enters
through one pinned quota-domain supervisor, one evidence-capsule compiler, and one usage-event
contract. No Cloudvore inference-bearing scheduled task was found in the read-only Task Scheduler
inventory, which is a safe starting condition, not adoption evidence.

Universal alignment means every lane uses the same admission, identity, telemetry, idle, capsule,
and lifecycle laws. It does **not** mean making every model interchangeable or lowering a named
model/effort/reviewer requirement. Exact role cells and independent-provider gates remain binding.

## Immutable fleet authority

Accepted commit `224a6705d81dfbc670313cdcef4d825216f2b380`, tree
`569957a2b62eb0e2e99c1490a9cbec0002894e42`, parent
`fa8e19d0630b2a246bcb46a112f247b160e97c1f` is the only intake source. Installation must extract
bytes from that Git object, never trust a mutable checkout, and verify this complete tuple before
use:

| Accepted artifact | SHA-256 | Bytes |
|---|---:|---:|
| `.github/workflows/provider-capacity-governor.yml` | `99E90B944F7AF4360116B77F15C9B30AD36DAEA8DF54544C5CA8690133431462` | 2,092 |
| `.gitignore` | `6FEADED4E28EA86E001A6751B4E3D960E8B7C31B9616FF9936B79297086E809B` | 23 |
| `README.md` | `98E69C89D86AC02CB7170F85B7429C326F4406530B30FC4CEC609AEBF5BA78C5` | 2,904 |
| `metrics/README.md` | `D8F9E2202A220D42FEB2B59E99FBC80CECBDD0D1BF494DA2EEF139F34268871F` | 3,567 |
| `requirements-provider-capacity-governor.txt` | `228314F5E6E5464E6FB85BFE42E9DB5224EAD14F0AE753121C153DC0AB7234CB` | 185 |
| `requirements-provider-capacity-governor.lock.txt` | `01BB5B11588B8B9459700B65C3374B77A71C2EAAE29F8BF3693974D2F1537BF1` | 13,714 |
| `schemas/provider-admission-snapshot-v1.schema.json` | `2A88C79365E7DE29E109712D67F770990F73109845B3A61131F28E9DB63EB8A9` | 6,680 |
| `schemas/provider-usage-event-v1.schema.json` | `2C3C68D7B288CCE18DBF46FA5A1ED37E57EB21A1E1BEB9B9FFCF85CCCF29271F` | 6,183 |
| `examples/provider-admission-snapshot-v1.json` | `E6B1D902D6AC8101A64C3A98ABBCA16C45C93D667DF79DE2F974BECB95A58141` | 1,469 |
| `examples/provider-usage-events-v1.jsonl` | `9F32C4734FF40473C00B4E8F64C39CCEE351459740FA4DCDFA86D293C5543969` | 2,254 |
| `specs/fleet-provider-capacity-governor.md` | `D0F50349080910BF1026AB29BAB16822511B80A860CAD4865EEEE4C04A29B244` | 21,695 |
| `tools/provider_capacity_governor.py` | `EDDECC5C6DC66C04F9949FCCC911DF75B0DE58B615C29F73DA8C8C9535130266` | 36,346 |
| `tests/test_provider_capacity_governor.py` | `B40CFE7FBAAA15BFE7F08B60721257909447BB9B0E8B3683D88BFB24EE4094DD` | 37,316 |

The local installer manifest must pin all thirteen rows, the accepted commit/tree/parent, each
Cloudvore extension blob, policy hash, provider adapter manifest, Python executable/version, and
hash-locked dependency environment. A partial pin is a refusal. The workflow, README files, and
examples are doctrine/reference inputs rather than runtime executables, but remain in the intake
tuple so a project cannot claim a selectively copied contract.

## Current seams and the gap

| Family / lanes | Current observed launch seam | Existing token-safety value | Missing universal contract |
|---|---|---|---|
| Anthropic: Opus, Fable, Sonnet | Per-dispatch `review/run-claude-*.ps1`; latest inspected R2 wrapper SHA `1D3921F3A15BB3CA08C011FFF0025E06FFE53389B51AB8DB31262EA0FC10342B` | Exact model/effort, frozen inputs, bounded 5,400-second root, stream terminal and model usage | No host-wide quota-domain claimant, capacity adapter, common capsule/event schema, deterministic idle receipt, or bypass inventory |
| OpenAI: Hub, Sol, Luna | Per-dispatch direct `codex exec`; inspected R5 wrapper SHA `A12262DD43C77D91C837E6F29C3808BBAA995942305A26541F03930AE71D0505` | Exact model/effort/tier; `turn.completed` exposes input, cached input, output, and reasoning | No common governor/capacity/reserve/idle path; usage is not normalized into fleet events |
| Moonshot: Kimi implementation/review cells | `Invoke-KimiLane.ps1` SHA `40F92619194ED2970AF4ACF8EE18C29BD1F0BDE7BE0B7051E14EAC5381B0C909`; inspected R5 caller SHA `0FAC41DBBBB04EFCE4FB6B1A3801CB6FF67B4B2B15CD7D9E131FD85230BD9516` | Pointer-only charter, bounded `MaxTurns`, durable session/claim correlation, exact profile | Claim is adapter-local rather than host-wide quota-domain admission; no common capacity, capsule, or usage normalization |
| xAI: admitted WSL Grok cells | `Invoke-GrokLane.ps1` SHA `FB175B43E3DA8657170F732F7A16D216A812AC0C42185A121C4A12CCFFFDCE1F` through `Invoke-GrokWslBoundary.ps1` SHA `46B64C4E81D49F3B24A050880E9B0F60C4F9D81756DB61833E6382F40EA79747` | Exact WSL/inventory boundary, bounded turns, session terminal, usage digest | No common quota-domain supervisor/capsule/event normalization; usage digest alone is not token telemetry |
| Deterministic planner | `tools/provider-router.py` SHA `48E2161522D70F95DFE99BB334927103A9E3D2A1088FA11C9775BB52AB2E5021` | Read-only provider health/route plan; invokes no model | It is not the live admission supervisor and must not be relabelled as one |
| Windows scheduled roots | No Cloudvore inference-bearing task observed; Cloudvore tasks were thermal/test-admission controls | No unattended model task is silently consuming quota | No installed manifest/bypass watcher yet proves this remains true |

The eleven `claude.exe` process rows observed locally cannot be assigned to Cloudvore merely by
name. Under the universal law they are **ambiguous**, must not be killed, and cannot authorize a
takeover. Process ID plus immutable start time, registered/observed session hash, provider/model,
seat epoch, registry, and progress must agree.

## Minimal SHADOW architecture

```text
frozen dispatch + lane cursor + exact subject
                    |
          deterministic capsule compiler
                    | capsule SHA / bounded pointers
                    v
        Cloudvore shadow supervisor (no spawn authority)
          | snapshot + counterfactual decision + events
          |-- Claude normalizer  <- existing Claude stream JSON
          |-- Codex normalizer   <- turn.completed usage
          |-- Kimi normalizer    <- adapter/session + /usage when exposed
          `-- Grok normalizer    <- end-event usage / stable cache identity
                    |
       machine-local raw evidence and append-only JSONL
                    |
       reviewed aggregate receipt only (no raw identity/prose)
```

SHADOW is an observation sidecar. Existing attended launchers keep their present launch semantics;
the sidecar cannot spawn, block, enable, kill, resume, retry, select, or substitute a provider. It
evaluates the frozen snapshot with the exact reference engine, records whether the future gate would
admit or deny, and correlates already-produced terminal/usage receipts. Its local envelope must say
`mode=SHADOW`, `enforced=false`, and `launch_effect=none`; those fields do not get injected into the
fleet schemas. `automatic_launch_gate` remains `closed`.

The next implementation slice should add, on an isolated branch, exact accepted copies of the
reference engine, schemas, requirements, examples, and tests; a Cloudvore-only deterministic
capsule/compiler and four receipt normalizers; a strict install-manifest verifier; and tests. Raw
runtime state belongs under `%LOCALAPPDATA%\Cloudvore\provider-governor\`, outside Git. Tracked
files contain no account identifier, credential, raw prompt, command line, or provider prose.

After the sidecar itself is ratified, each newly generated per-dispatch wrapper calls `shadow begin`
immediately before its unchanged provider invocation and `shadow terminal` after the existing
terminal verifier. A `shadow idle` entrypoint is separate and model-free. Historical wrappers are
evidence, not retrofit targets. Containment later replaces these advisory calls with one canonical
supervisor-owned launch seam; SHADOW must not claim that boundary early.

## Evidence capsule v1

Cloudvore's extension is canonical UTF-8 JSON, recursively key-sorted, LF-terminated, with a SHA-256
over the payload excluding its self-hash. It contains only:

1. schema/project/lane/role/seat epoch and exact provider/model/effort requested;
2. exact base, head, tree, changed-path set, focused-diff digest, and candidate cleanliness receipt;
3. derived state and the exact addressed work strictly after the lane cursor;
4. controlling ruling and protected-invariant identifiers with project-relative path/hash pointers;
5. bounded test/error summaries and content-addressed pointers to full local evidence;
6. required output artifact/ledger paths and explicit authority exclusions; and
7. compiler version, policy hash, capsule byte count, and source-ref hashes.

Initial Cloudvore canary bound: 65,536 payload bytes and 64 references. These are project policy,
not fleet truth. Required evidence is never silently truncated: overflow returns
`CAPSULE_REQUIRED_EVIDENCE_OVERFLOW` and no model invocation. Optional history is excluded rather
than summarized by inference. A targeted deterministic expansion produces a new capsule/hash and
records the predecessor; a compacted or resumed session receives the same functional requirements
and evidence hashes.

This saves tokens for every lane by eliminating repeated corpus orientation, spilling large output
to content-addressed artifacts, and preventing unchanged-idle calls. It does not save tokens by
skipping review, downgrading models, hiding required evidence, or treating a budget stop as a pass.

## Universal lane behavior

| Cell | Token/capacity behavior after staged adoption |
|---|---|
| Opus / Fable / Sonnet | Preserve exact Claude model and effort; normalize stream usage into input, cache-read, cache-write, reasoning, and output; use bounded resumable turns and stable capsule prefix; reserve Claude capacity for required review/finish work. |
| Hub / Sol / Luna | Preserve exact Codex model, effort, tier, and role; normalize `turn.completed`; checkpoint/compact at phase boundaries; deterministic hub status, lease, hashing, and idle work never invoke Codex. |
| Kimi cells | Keep pointer transport and bounded turns; add provider `/usage` or honest estimated/unknown context fields, milestone `/compact`, bounded transient attempts, and the same capsule hash. Kimi never gains review or hub credit merely by being cheaper. |
| Grok cells | Keep admitted WSL boundary, stable conversation/cache identity and append-only prompt prefix; normalize cached/reasoning/output/cost when exposed; retain bounded max turns. Unknown CLI fields stay `unknown`. |
| Every cell | Same opaque quota-domain key, completion reserve, exact-profile requirement, changed idle fingerprint, claimant fence, event sequence, evidence limits, and checkpoint-not-verdict law. |

## Capacity and usage events

The only fleet event vocabulary is the accepted schema:
`ADMISSION_REQUESTED`, `ADMISSION_ADMITTED`, `ADMISSION_DENIED`, `PROCESS_STARTED`,
`USAGE_OBSERVED`, `CHECKPOINTED`, `TERMINAL`, `CAPACITY_BLOCKED`, `RESET_OBSERVED`,
`IDLE_SKIPPED`, and `UNPARSEABLE`.

SHADOW stores the reference decision plus a non-publishable enforcement envelope. Published
aggregate events may carry only opaque HMAC quota/host identities and reviewed project-relative
hash pointers. Missing counters are `unknown`, never zero. `IDLE_SKIPPED` is special: request,
input, cached input, cache write, reasoning, output, and tool-call counters must all be explicit
integer zero, and the deterministic input fingerprint must be present. Any provider process or
tool call makes the idle claim invalid.

A reset creates `RESET_OBSERVED` and updates capacity telemetry only. It never opens the automatic
gate, enables a task, creates a process, retries work, or drains the queue. A quota refusal creates
`CAPACITY_BLOCKED`; retries are scheduled deterministically and remain subject to the same gate.

## Required install and test bar

The local manifest verifier must refuse missing, extra, wrong-size, wrong-hash, reparse-point,
non-regular, writable-substitution, wrong-Python, unlocked-dependency, schema, adapter, policy, or
install-root drift. Installation is staged with the provider unavailable or fakes only; no reset
is needed.

Minimum author evidence before SHADOW review:

- accepted 37/37 reference tests, Python compilation, both example CLI paths, hash-locked install,
  workflow YAML parse, and exact manifest reproduction;
- three identical green runs of Cloudvore capsule, manifest, normalizer, idle, and sidecar suites;
- fake Claude/Codex/Kimi/Grok receipts covering exact usage, honest `unknown`, quota/refusal,
  empty/partial terminal, effective-model mismatch, budget checkpoint, and terminal outcomes;
- deterministic capsule repeatability, irrelevant-history exclusion, required-evidence overflow,
  targeted expansion linkage, privacy/no-echo, strict JSON, and resource bounds;
- unchanged idle fingerprint with an invocation spy proving zero provider processes, requests,
  tokens, and tool calls; changed actionable input produces a request but SHADOW still has no launch
  effect;
- stale/future/unknown capacity, reserve boundary, exact-profile unavailable, duplicate claimant,
  distinct quota domains, dead/fresh lease, live/stale lease, startup/cooldown, orphan watcher,
  ambiguous identity/no-kill, reset-quiet, and direct-launch inventory controls;
- Task Scheduler inventory proving every Cloudvore inference root is in the exact manifest and no
  task was enabled/disabled/created; current expected inference-task allowlist is empty; and
- at least one independent non-author mutation for each of: manifest pin, idle zero, capsule hash,
  freshness, reserve, claimant identity, exact profile, reset quiet, and SHADOW no-effect.

`SHADOW_PASS` additionally requires bounded attended receipts for every provider family intended to
remain admitted, but no lane needs to be launched merely to finish installation. A missing provider
queues its receipt; it is not simulated into live credit. Claude restoration should start with one
attended exact-profile canary only after the fake/no-inference bar and independent review, while the
automatic gate remains closed.

## Lifecycle and authority boundaries

`DESIGN -> IMPLEMENTED_UNRATIFIED -> SHADOW_PASS -> CONTAINMENT_PASS -> CAPACITY_PASS ->
CONTEXT_PASS -> ROUTING_PASS` is monotonic only through exact commit/tree, manifest, policy,
tests/mutations, independent review, and dated receipts. Evidence for one stage never inherits into
the next by assertion.

- `SHADOW_PASS`: decisions/events/capsules are truthful; launch behavior unchanged.
- `CONTAINMENT_PASS`: one host-wide claimant, startup/cooldown/orphan fencing, canonical launch seam,
  and structural direct-invocation refusal are enforced.
- `CAPACITY_PASS`: fresh provider capacity and completion reserve affect unattended admission.
- `CONTEXT_PASS`: capsules and bounded continuations pass frozen replay with no missed blocker,
  severity loss, dropped work, or authority drift.
- `ROUTING_PASS`: any model/effort change has blinded role-specific non-inferiority evidence.

Until Cloudvore reaches the applicable stage, its fleet disposition remains `DISTINGUISH`, not
`ADOPT(reference)`. This design grants no provider launch, process kill, auth/credential action,
scheduled-task mutation, automatic-gate opening, model substitution, reviewer credit, test lease,
hosted run, Git mutation, landing, push, publication, release, score, or doctrine-write authority.
Only the Cloudvore hub may later adjudicate local adoption, and fleet publication must carry the
accepted local commit/tree, manifest/policy hashes, stage receipt hashes, adverse evidence, and the
continuing no-authority boundaries.

## Smallest execution order

1. Freeze a Cloudvore implementation charter from this design and the exact fleet tuple; reserve
   one writer and a closed path set.
2. Install and verify the read-only reference core plus local manifest/capsule/normalizer code.
3. Run fake/no-inference author bars and mutations; do not touch current live wrappers yet.
4. Obtain independent executable and static review; repair until exact-head acceptance.
5. Instrument newly generated Claude/Codex/Kimi/Grok wrappers in SHADOW mode only; preserve exact
   models, efforts, roles, tools, and terminal gates.
6. Collect bounded attended receipts, ratify `SHADOW_PASS`, then separately design containment.
7. Publish the Cloudvore disposition to fleet doctrine only after local ratification; do not claim
   fleetwide operational conformity before every project has its own accepted adoption receipt.

