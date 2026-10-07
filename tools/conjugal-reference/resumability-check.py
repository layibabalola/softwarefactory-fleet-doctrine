"""Resumability gate: can a fresh session on a NEW account resume this workstream from the tree alone, right now?

Run at every landing seam (after sync + commit), before any expensive launch, on the status tick, and on the first
429 from any provider. Refuses (exit 1) on any failure — a gate that warns has failed open.

Checks (all derived from the tree, never from memory or chat):
  1. DIRT     - no file under the workstream path differs from HEAD by CONTENT (autocrlf phantoms ignored).
  2. CLASSES  - every artifact file in <ws>/rounds/ matches a class the entry file's derivation rule names, so the
                next session can place it in the loop (an unnamed class is a step nobody can find).
  3. PROMPTS  - every design/panel/lint output in rounds/ has its prompt or template committed under <ws>/prompts/
                (a running agent can die; its prompt must not).
  4. ENTRY    - the entry file names no live values (SHA-like tokens or 'composite <n>' outside code fences).

Usage: python resumability-check.py [--ws docs/architecture/approach-a] [--entry RESUME.md] [--rev <commit>] [--json]
       python resumability-check.py pre-push     (git hook: ref lines on stdin; exit 1 = push refused)

--rev judges CLASSES/PROMPTS/ENTRY on that commit's tree, not the worktree, and judges DIRT only when the
commit is the worktree's HEAD (dirt beside some other commit says nothing about it). Tree mode also refuses a
failed git read (GIT-UNREADABLE) and paths a Windows checkout would fold onto the workstream (CASE-VARIANT).

pre-push is the landing-seam wiring, spliced into .git/hooks/pre-push by `doctrine_outbox.py session-start`.
It gates only a push to refs/heads/master whose tree change touches the workstream path, and it judges the
pushed tip's tree without DIRT (worktree dirt is not what lands), so a red state is fixed forward by a follow-up
commit, never by rewriting history.
"""
import argparse
import io
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Artifact classes the entry file must name, as (regex over filename, token that must appear in the entry file).
CLASSES = [
    (r"^round\d+-blockers\.txt$", "blockers"),
    (r"^d\d+-[a-z0-9]+(-family)?\.md$", "d1N-*.md"),
    (r"^d\d+-haiku-classification\.md$", "classification"),
    (r"^synth-[a-z]+\.md$", "synth-"),
    (r"^astra-(arbitrate|deep|lead)[-a-z0-9.]*\.md$", "astra-"),
    (r"^consolidate-r\d+-report\.md$", "consolidate-r"),
    (r"^lint\d*[-a-z]*-out\.txt$", "lint"),
    (r"^round\d+-[a-z0-9]+-out\.txt$", "round<N>-<seat>-out.txt"),
    (r"^APPROACH-A-V[\d.]+.*\.md$", "APPROACH-A-V"),
    (r"^design-of-design-evidence\.md$", "evidence"),
    (r"^update_evidence_r\d+\.py$", "evidence"),
    (r"^[a-z0-9-]+-family(-inputs)?\.md$", "family"),
    (r"^f\d+-[a-z0-9-]+\.(md|txt)$", "f<N>-"),
]

# Artifacts produced by a SCRIPT, not by a model seat. They have no prompt by construction, so
# demanding one is a false positive -- and a gate that cries wolf gets switched off, which is worse
# than the gap it was guarding. Distinguishing these is the only honest way to keep the prompt rule
# strict for everything else.
#
# Added 2026-09-15 after Round F4 landed `f4-anchor-check.txt` (emitted by
# coordination/harvest/harvest_runner.py) and turned this gate red across the fleet -- it is
# exported to every project by harvest-config.json `conjugal_export`.
SCRIPT_GENERATED = [
    r"^f\d+-anchor-check\.txt$",      # harvest runner's pre-flight anchor census
    r"^f\d+-inputs\.md$",             # harvested filing population
    r"^f\d+-filing\d+\.txt$",         # verbatim sibling filings, copied from the bus
    r"^round\d+-blockers\.txt$",      # derived round summary
    r"^stage-s-[0-9A-Za-z-]+\.(txt|json)$",   # execution gate receipts, emitted by stage_s.py
]
PROMPT_OF = [  # output filename regex -> prompt filename candidates (any one suffices)
    (r"^(d\d+)-([a-z0-9]+)\.md$", ["{0}-{1}.txt", "design-swarm-r{n}-template.txt", "design-swarm-r{n}-claude-template.txt"]),
    (r"^round(\d+)-([a-z0-9]+)-out\.txt$", ["round{0}-{1}-prompt.txt", "round{0}-claude-panel-template.txt"]),
    (r"^lint(\d+)-([a-z]+)-out\.txt$", ["lint{0}-{1}-prompt.txt", "lint-template.txt"]),
    (r"^astra-arbitrate-r(\d+)\.md$", ["astra-arbitrate-r{0}-prompt.txt"]),
    (r"^consolidate-r(\d+)-report\.md$", ["consolidate-r{0}-prompt.txt"]),
    (r"^f(\d+)-([a-z]+-[a-z]+)(-report|-out)?\.(md|txt)$", ["f{0}-{1}-prompt.txt"]),
]
SHA_RE = re.compile(r"\b[0-9a-f]{9,40}\b")
LIVE_RE = re.compile(r"(?i)\b(composite|score)\s*[:=]?\s*\d{2}\.\d\b")


def git(*args):
    return subprocess.run(["git", "--no-optional-locks", *args], cwd=ROOT, capture_output=True, text=True,
                          encoding="utf-8", errors="replace").stdout


class GitReadError(Exception):
    """A git read failed. In tree mode that is a refusal: an empty listing must never read as a clean one."""


def git_checked(*args):
    r = subprocess.run(["git", "--no-optional-locks", *args], cwd=ROOT, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise GitReadError(f"git {' '.join(args)}: exit {r.returncode}: {r.stderr.strip()[:200]}")
    return r.stdout


class Tree:
    """Reads the workstream from the worktree (rev=None) or from one commit's tree."""

    def __init__(self, rev=None):
        self.rev = rev

    def listdir(self, rel):
        """[(name, is_dir)] directly under rel; [] when rel is absent."""
        if self.rev is None:
            d = os.path.join(ROOT, rel)
            return [(f, os.path.isdir(os.path.join(d, f))) for f in os.listdir(d)] if os.path.isdir(d) else []
        out = []
        for rec in git_checked("ls-tree", "-z", self.rev, "--", rel.rstrip("/") + "/").split("\0"):
            if "\t" in rec:
                meta, path = rec.split("\t", 1)
                out.append((path.rsplit("/", 1)[-1], meta.split()[1] == "tree"))
        return out

    def read(self, rel):
        """Text of rel, or None when absent."""
        if self.rev is None:
            path = os.path.join(ROOT, rel)
            return io.open(path, encoding="utf-8").read() if os.path.isfile(path) else None
        if not git_checked("ls-tree", "-z", self.rev, "--", rel):
            return None
        return git_checked("show", f"{self.rev}:{rel}")

    def case_variants(self, ws):
        """Tree paths that Windows folds onto ws, rounds/ or prompts/ although git keeps them apart
        (`Approach-A/`, `Rounds/`). Case-exact tree reads would never see them, so each one refuses."""
        wsl, out = ws.lower() + "/", []
        for p in git_checked("ls-tree", "-r", "-z", "--name-only", self.rev).split("\0"):
            if not p.lower().startswith(wsl):
                continue
            top = p[len(ws) + 1:].split("/", 1)[0]
            if not p.startswith(ws + "/") or (top.lower() in ("rounds", "prompts") and top not in ("rounds", "prompts")):
                out.append(p)
        return out


def check_dirt(ws):
    out = git("status", "--porcelain", "--", ws)
    dirty = []
    for line in out.splitlines():
        code, path = line[:2], line[3:].strip().strip('"')
        if code.strip() == "??":
            dirty.append(("untracked", path)); continue
        # content test: ignore CRLF-only phantoms
        diff = subprocess.run(["git", "--no-optional-locks", "diff", "--ignore-cr-at-eol", "--quiet", "--", path],
                              cwd=ROOT).returncode
        if diff != 0:
            dirty.append(("modified", path))
    return dirty


def check_classes(tree, ws, entry_text):
    unnamed, unclassified = [], []
    for f, is_dir in sorted(tree.listdir(f"{ws}/rounds")):
        if is_dir:
            continue  # fragmented children live in dirs named for the parent stem
        for rx, token in CLASSES:
            if re.match(rx, f):
                if token not in entry_text:
                    unnamed.append((f, token))
                break
        else:
            unclassified.append(f)
    return unnamed, unclassified


def check_prompts(tree, ws):
    have = {f for f, _ in tree.listdir(f"{ws}/prompts")}
    allow_text = tree.read(f"{ws}/prompts/ALLOWLIST-historical.txt") or ""
    allow = {l.strip() for l in allow_text.splitlines() if l.strip() and not l.startswith("#")}
    missing = []
    for f, _ in sorted(tree.listdir(f"{ws}/rounds")):
        if f in allow:
            continue  # explicitly recorded as pre-gate history, not reproducible
        if any(re.match(rx, f) for rx in SCRIPT_GENERATED):
            continue  # emitted by a script; no model prompt exists to commit
        for rx, cands in PROMPT_OF:
            m = re.match(rx, f)
            if not m:
                continue
            g = m.groups()
            n = g[0].lstrip("d") if g else ""
            names = [c.format(*g, n=n) for c in cands]
            if not any(c in have for c in names):
                missing.append((f, names[0]))
            break
    return missing


def check_entry(text):
    body = re.sub(r"```.*?```", "", text, flags=re.S)
    shas = [s for s in SHA_RE.findall(body) if not s.isdigit()]
    live = LIVE_RE.findall(body)
    return text, shas, live


DEFAULT_WS = "docs/architecture/approach-a"
ZERO = re.compile(r"^0+$")


def evaluate(ws, entry, rev=None, dirt=True):
    """(label, fails). rev=None judges the worktree; else that commit's tree, with DIRT only at HEAD.
    dirt=False judges only what a commit carries (pre-push: unpushed dirt is not what lands)."""
    tree = Tree(rev)
    head = git("rev-parse", "HEAD").strip()
    label = git("rev-parse", "--short", rev or "HEAD").strip()
    try:
        entry_text = tree.read(f"{ws}/{entry}")
        if entry_text is None:
            return label, [("ENTRY-missing", [f"{ws}/{entry}"])]
        variants = tree.case_variants(ws) if rev else []
        unnamed, unclassified = check_classes(tree, ws, entry_text)
        missing = check_prompts(tree, ws)
    except GitReadError as e:
        return label, [("GIT-UNREADABLE", [str(e)])]
    _, shas, live = check_entry(entry_text)
    dirty = check_dirt(ws) if dirt and (rev is None or rev == head) else []
    fails = []
    if variants: fails.append(("CASE-VARIANT-paths", variants))
    if dirty: fails.append(("DIRT", dirty))
    if unnamed: fails.append(("CLASSES-unnamed-in-entry", unnamed))
    if unclassified: fails.append(("CLASSES-unknown-artifact", unclassified))
    if missing: fails.append(("PROMPTS-missing", missing))
    if shas or live: fails.append(("ENTRY-carries-live-values", shas + live))
    return label, fails


def report(ws, entry, label, fails, out=None):
    out = out or sys.stdout
    if fails:
        print(f"FAIL resumability ({ws} @ {label}): a fresh session could not resume from the tree alone", file=out)
        for name, items in fails:
            print(f"  {name}:", file=out)
            for it in items[:12]:
                print(f"    - {it}", file=out)
            if len(items) > 12:
                print(f"    ... {len(items) - 12} more", file=out)
    else:
        print(f"PASS resumability ({ws} @ {label}): tree-only resume possible; no live values in {entry}", file=out)


def touches(ws, remote_sha, local_sha):
    """True when the push changes anything under ws. A new remote ref, or a remote tip this clone
    cannot read, counts as touching: the gate judges the tip rather than skip what it cannot see.
    The pathspec is case-insensitive: `Approach-A/` lands inside approach-a/ on a Windows checkout."""
    if ZERO.match(remote_sha):
        return True
    r = subprocess.run(["git", "--no-optional-locks", "diff", "--quiet", remote_sha, local_sha, "--", f":(icase){ws}"],
                       cwd=ROOT, capture_output=True)
    return r.returncode != 0   # 0 = no change under ws; 1 = changed; anything else = unreadable, so judge it


def cmd_pre_push(stdin_text, ws=DEFAULT_WS, entry="RESUME.md"):
    """git passes ref lines on stdin: <local-ref> <local-sha> <remote-ref> <remote-sha>."""
    refused = 0
    for line in stdin_text.splitlines():
        parts = line.split()
        if len(parts) != 4:
            continue
        _, local_sha, remote_ref, remote_sha = parts
        if remote_ref != "refs/heads/master" or ZERO.match(local_sha) or not touches(ws, remote_sha, local_sha):
            continue
        label, fails = evaluate(ws, entry, rev=local_sha, dirt=False)
        if fails:
            print("[resumability] PUSH REFUSED -- this push lands a workstream state a fresh session could not "
                  "resume from. Fix forward with a follow-up commit (never rewrite history):", file=sys.stderr)
            report(ws, entry, label, fails, out=sys.stderr)
            refused = 1
    return refused


def main():
    if sys.argv[1:2] == ["pre-push"]:
        return cmd_pre_push(sys.stdin.read())
    ap = argparse.ArgumentParser()
    ap.add_argument("--ws", default=DEFAULT_WS)
    ap.add_argument("--entry", default="RESUME.md")
    ap.add_argument("--rev", default=None, help="judge this commit's tree instead of the worktree")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    rev = None
    if a.rev:
        rev = git("rev-parse", "--verify", "-q", f"{a.rev}^{{commit}}").strip()
        if not rev:
            print(f"FAIL REV: {a.rev} is not a commit"); return 1
    label, fails = evaluate(a.ws, a.entry, rev)
    if rev is None and fails[:1] and fails[0][0] == "ENTRY-missing":   # the pre-tree-mode text, kept for fleet consumers
        print(f"FAIL ENTRY: {os.path.join(ROOT, a.ws, a.entry)} missing"); return 1
    if a.json:
        print(json.dumps({"head": label, "ws": a.ws, "pass": not fails, "fails": fails}, indent=1))
    else:
        report(a.ws, a.entry, label, fails)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
