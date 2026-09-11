# Rotation Continuity Strategy: Account Rotation Without Interruption

**Source:** Cloudvore (commit a939f7c, 2026-09-11)  
**Pattern:** Multi-account project continuity through project-scoped entry chains and automation recreation scripts  
**Portable Finding:** Yes — applicable to any fleet project with persistent factory/automation infrastructure

## The Problem

Account rotation (planned or emergency) happens with **zero warning** and can strand:
- Uncommitted operational state (telemetry, diagnostics)
- Scheduler automation configuration (user-local, not tracked in git)
- New account doesn't know where to resume work
- Wake-up phrase "resume our work" may be hardcoded globally instead of project-scoped

This creates a gap: new account must manually recover state before resuming autonomous work.

## The Solution: Three Layers

### Layer 1: Project-Scoped Resume Binding

**In each project's CLAUDE.md**, add a resume trigger that overrides global binding:

```markdown
## Resume: "resume our work" (project-scoped)

When in this directory, type **"resume our work"**:

**→ Read [AGENTS.md](AGENTS.md) → Read [docs/operating-contract.md](docs/operating-contract.md) → Execute.**

This binding wins per ~/.claude/CLAUDE.md resolution order (item 1: cwd binding wins).
```

**Why it works:**
- User's muscle-memory phrase works the same way
- Resolution order already built into global ~/.claude/CLAUDE.md
- No new user training needed

### Layer 2: Rotation Prep (Before Rotation)

**Pre-rotation checklist:**

1. **Commit operational state**
   - `git add <accumulated-telemetry>` (e.g., `warden-beats.jsonl`)
   - `git add <new-portable-findings>` (findings from this session)
   - Commit with message: "Rotation prep: [reason]"
   - Rationale: New account inherits clean tracked state

2. **Document scheduler/automation**
   - Identify any user-local automation/config (e.g., `~/.codex/automations/`, `~/.scheduler/`)
   - Create a recreation script: `tools/create-<automation>.ps1` or `.sh`
   - Script should auto-create the automation from tracked documentation
   - Commit script: "Add [automation] recreation script for post-rotation"
   - Rationale: User-local config is LOST on rotation; script enables unattended recovery

3. **Verify entry chain**
   - Run `python tools/gate.py --json --doctrine-check`
   - Run `python tools/next.py`
   - Ensure both work without local state (they should)
   - Rationale: New account must be able to derive state from git alone

### Layer 3: New Account Recovery (Post-Rotation)

**Recovery procedure:**

```bash
# 1. Clone repo
git clone <your-repo>
cd <your-project-dir>

# 2. Use project resume binding (same phrase as always)
resume our work

# What happens:
# - Local CLAUDE.md binding is detected (per resolution order)
# - Entry chain executes: AGENTS.md → operating-contract.md
# - State derived from BACKLOG.md + git
# - Next work selected via tools/next.py
# - Ready to resume autonomous work

# 3. (Optional) Recreate scheduler if needed
.\tools\create-<automation>.ps1   # 5-min manual setup
```

**Why it's fast:**
- No manual state reconstruction
- Entry chain is fully tracked in git
- Automation scripts are documented and automated
- New account is productive in minutes

## Proof: Cloudvore Implementation

**Commits implementing this pattern:**
- **4cd3c85:** Rotation prep — commit warden-beats + portable findings
- **a0bc548:** Create O03 automation recreation script
- **a939f7c:** Add project-scoped resume binding to CLAUDE.md

**Entry chain (tracked):**
- CLAUDE.md (project-level, resume binding + safety rules)
- AGENTS.md (authority register)
- docs/operating-contract.md (workflow contract, scheduler config, model routing)

**Recovery test:** Simulated new account can run:
```bash
git clone https://github.com/layibabalola/Cloudvore
cd "C:\code\DropBox Vault"
resume our work
→ Executes factory, selects next work, ready to drain
```

## Adoption Checklist

For any fleet project to adopt this pattern:

- [ ] Add project-scoped resume binding to project CLAUDE.md
  ```markdown
  ## Resume: "resume our work" (project-scoped)
  → Read [entry-point] and execute
  ```

- [ ] Before rotation, commit accumulated state:
  ```bash
  git add <telemetry/findings>
  git commit -m "Rotation prep: [reason]"
  ```

- [ ] Document and script any user-local automation:
  ```bash
  # Create tools/create-<automation>.ps1
  # Document in docs/<automation>-config.md
  ```

- [ ] Verify entry chain works without local state:
  ```bash
  python tools/gate.py --json
  python tools/next.py
  ```

- [ ] Test recovery on new account clone:
  ```bash
  git clone <repo>
  cd <project>
  resume our work
  ```

## Why This Pattern Matters

1. **Zero coordination needed** — Account rotation is unannounced; strategy must work autonomously
2. **Preserves user workflow** — Existing "resume our work" phrase works unchanged
3. **Minimal new tooling** — Leverages existing entry chains + simple scripts
4. **Scales across fleet** — Same pattern works for Magic Lantern, Conjugal, any new projects
5. **Automation recovery is explicit** — Scripts document HOW to recreate, not just WHAT was lost

## Example: Magic Lantern

Magic Lantern can adopt this by:

1. Adding resume binding to `C:\code\magic-lantern_dannephoto\CLAUDE.md`:
   ```markdown
   ## Resume: "resume our work" (project-scoped)
   → Read `roadmap\HANDOFF.md` and execute resume-runbook
   ```

2. Creating `tools\create-lantern-automation.ps1` if Magic Lantern has scheduled tasks
3. Committing lane state before rotation
4. Same recovery on new account: `resume our work` → lane handoff executes

## References

- **Source:** Cloudvore commit a939f7c (project-scoped resume binding)
- **Related:** Cloudvore rotation prep commits 4cd3c85, a0bc548
- **Foundation:** ~/.claude/CLAUDE.md resolution order (item 1: cwd binding wins)
- **Companion pattern:** Doctrine publication (findings published automatically on rotation)

## Attribution

Developed during Cloudvore 2026-09-11 rotation continuity audit. Proven by 4-agent swarm investigating:
- Uncommitted state audit (when to commit before rotation)
- Automation reproducibility (how to auto-recover)
- Entry chain validation (new account can bootstrap from git alone)
- Adjudication (final strategy synthesis)

Portable for all fleet projects with persistent autonomous infrastructure.
