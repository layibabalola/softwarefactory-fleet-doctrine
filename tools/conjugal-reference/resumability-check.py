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

Usage: python resumability-check.py [--ws docs/architecture/approach-a] [--entry RESUME.md] [--json]
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


def check_classes(ws, entry_text):
    rounds = os.path.join(ROOT, ws, "rounds")
    unnamed, unclassified = [], []
    for f in sorted(os.listdir(rounds)) if os.path.isdir(rounds) else []:
        if os.path.isdir(os.path.join(rounds, f)):
            continue  # fragmented children live in dirs named for the parent stem
        for rx, token in CLASSES:
            if re.match(rx, f):
                if token not in entry_text:
                    unnamed.append((f, token))
                break
        else:
            unclassified.append(f)
    return unnamed, unclassified


def check_prompts(ws):
    rounds, prompts = os.path.join(ROOT, ws, "rounds"), os.path.join(ROOT, ws, "prompts")
    have = set(os.listdir(prompts)) if os.path.isdir(prompts) else set()
    allow_path = os.path.join(prompts, "ALLOWLIST-historical.txt")
    allow = set()
    if os.path.isfile(allow_path):
        allow = {l.strip() for l in io.open(allow_path, encoding="utf-8") if l.strip() and not l.startswith("#")}
    missing = []
    for f in sorted(os.listdir(rounds)) if os.path.isdir(rounds) else []:
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


def check_entry(entry_path):
    text = io.open(entry_path, encoding="utf-8").read()
    body = re.sub(r"```.*?```", "", text, flags=re.S)
    shas = [s for s in SHA_RE.findall(body) if not s.isdigit()]
    live = LIVE_RE.findall(body)
    return text, shas, live


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ws", default="docs/architecture/approach-a")
    ap.add_argument("--entry", default="RESUME.md")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    entry_path = os.path.join(ROOT, a.ws, a.entry)
    if not os.path.isfile(entry_path):
        print(f"FAIL ENTRY: {entry_path} missing"); return 1
    entry_text, shas, live = check_entry(entry_path)
    dirty = check_dirt(a.ws)
    unnamed, unclassified = check_classes(a.ws, entry_text)
    missing = check_prompts(a.ws)
    fails = []
    if dirty: fails.append(("DIRT", dirty))
    if unnamed: fails.append(("CLASSES-unnamed-in-entry", unnamed))
    if unclassified: fails.append(("CLASSES-unknown-artifact", unclassified))
    if missing: fails.append(("PROMPTS-missing", missing))
    if shas or live: fails.append(("ENTRY-carries-live-values", shas + live))
    head = git("rev-parse", "--short", "HEAD").strip()
    if a.json:
        print(json.dumps({"head": head, "ws": a.ws, "pass": not fails, "fails": fails}, indent=1))
    elif fails:
        print(f"FAIL resumability ({a.ws} @ {head}): a fresh session could not resume from the tree alone")
        for name, items in fails:
            print(f"  {name}:")
            for it in items[:12]:
                print(f"    - {it}")
            if len(items) > 12:
                print(f"    ... {len(items) - 12} more")
    else:
        print(f"PASS resumability ({a.ws} @ {head}): tree-only resume possible; no live values in {a.entry}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
