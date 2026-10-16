#!/usr/bin/env python3
"""kernel-subjects.py -- is a Cloudvore packet a declared kernel subject, declared before its first byte?

The fleet's software factory kernel (bus `specs/fleet-factory-kernel.md` r5, profile `code`) credits a project
only for subjects closed end to end, and KERNEL-1 (bus RULINGS) asks for the subject entry "before the first byte"
(K5). Cloudvore's brief-first rule (docs/operating-contract-swarm-rules.md, pre-flight item 0) nearly is that
already. This tool reads git and says, for one landing merge or one branch, whether it is:

  - BRIEF:    a `review/briefs/*.md` file committed in the packet's range carries a `## Kernel subject` block;
  - WELL-FORMED: the block names every field (subject, kernel, profile, contract, key, delivery, identity; and
              optionally products, default `src/ tests/`), its fenced ```contract text names, in order, bar,
              filter, passes, env, harness-limits, seats, review-scope, rounds, planted-edits and charter, and an
              optional fenced ```manifest lists the declared identity paths, one per line (K124: with none, the
              subject takes the profile's default identity, the landed merge's tree; `block` then says
              `identity: default`, and tools/kernel-receipt.py credits it by the passes at the landed merge);
  - DIGEST:   the declared `contract: sha256:<hex>` recomputes from that fenced text;
  - UNCHANGED: at EVERY commit of the range that touches ANY brief carrying the block, the block's terms (declared
              digest, recomputed digest, products, key class) equal the tip's -- one contract judges every round, and a
              contract changed and changed back, or a second brief with other terms, is still a change; the declared
              manifest, once first declared, is a compared term too (K95);
  - ORDERED:  the commit that first carried the block is a strict ancestor of EVERY non-merge commit in the range
              that touches a declared product path (ancestry, never dates: a rebase rewrites dates);
  - RECEIPTED (landings only): `review/kernel-receipts/<row>.md` exists at the `--at` ref and names this merge.

`src/` and `tests/` are ALWAYS products; `products:` adds to them and never narrows them. Every path the range's own
commits touch must be a product or under `review/` (briefs, ledgers, evidence); any other reads PRODUCTS-UNDECLARED.
A tooling packet therefore declares `products: tools/ docs/` (or whatever it changes), and its ordering is real.

Paths are read with `-c core.quotePath=false`: git's default quotes a non-ASCII path (`"src/caf\\303\\251.cs"`), which
then matches no prefix and no tree entry (round 1, seat A: a false OK and a false MATCH). A path git still quotes (a
control character, a quote or a backslash in it) is refused as unreadable, never read as some other path.

    python tools/kernel-subjects.py check <landing-merge-or-branch> [--base origin/master] [--at origin/master] [--json]
    python tools/kernel-subjects.py advisory [--ref master] [--json]     # gate.py --doctrine-check calls this
    python tools/kernel-subjects.py block --row H200 --filter "..." --bus-sha <sha>

A two-parent target is a landing (first parent = base, second = the packet) unless it merged a line INTO a packet
branch (K170: a brief on its first parent's first-parent line, none on its second's; `--base` never decides it); that
tip is read as the branch it is, against `--base` and the merged line, and like any branch tip it refuses a `--base`
that does not resolve (exit 2), the default origin/master included. A landing never reads `--base`.

`check` exits 1 when any flag is raised, 0 when none, 2 when git did not answer (never read as a verdict).
`advisory` exits 0 whenever it answered, whatever it found (it reports; it never refuses), and 2 when git did not.
Read-only: every git call is `git --no-optional-locks -C <repo>`, in an environment with no GIT_TRACE*, no
variable that relocates the repository, and GIT_NO_REPLACE_OBJECTS=1.

K137: the project's constants (the subject prefix, the row and branch patterns, the delivery, the briefs, review and
receipts paths, the default products, the bar's runner and workflows, the runner script's path and the default
contract text) are read from ONE committed config, factory-config.json beside this file (or the file
$FACTORY_KERNEL_CONFIG names, the form a pinned run through tools/factory/pin-runner.py uses), which
tools/kernel-receipt.py reads through this module. A missing, unreadable or malformed config is refused (exit 2,
`REFUSE kernel-subjects: ...`), never defaulted: `load_config` names the key that is wrong.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

CONFIG_NAME = "factory-config.json"
# Bus K154: run by pin (tools/factory/pin-runner.py) the tool sits in a private directory, so the project names its
# config in FACTORY_KERNEL_CONFIG (a path; relative resolves against the caller's cwd). Unset or empty: beside this
# file, as a project copy has always read it. Either way the file is loaded strictly below, never defaulted.
CONFIG_ENV = "FACTORY_KERNEL_CONFIG"
CONFIG_PATH = (Path(os.environ[CONFIG_ENV]) if os.environ.get(CONFIG_ENV)
               else Path(__file__).with_name(CONFIG_NAME))
CONFIG_SCHEMA = 1                     # the config layout this code reads
# K120 round 1 (tools/kernel-receipt.py): the one runner-name domain, words of [0-9A-Za-z._-] joined by single spaces.
RUNNER_WORDS = r"[0-9A-Za-z._-]+(?: [0-9A-Za-z._-]+)*"
# Round 1, seat B: code@r10 binds before work the declared environment, the harness limits, the review scope and the
# key's charter (execution or static review, declared before dispatch), beside the checks and the round rule.
CONTRACT_KEYS = ("bar", "filter", "passes", "env", "harness-limits", "seats", "review-scope", "rounds",
                 "planted-edits", "charter")
_STR, _DIRS, _REGEX, _DIR, _FILE, _RUNNER, _PREFIX = (
    "a nonempty string", "a nonempty list of distinct repository directories", "a regular expression",
    "a repository directory (relative, forward slashes, ending in /)", "a repository file (relative, forward slashes)",
    "a runner name", "an ASCII subject prefix ending in /")
# Review round 1 (seat A): a repository path is relative ASCII segments joined by `/`; no drive letter, no `.` or `..`
# segment, no backslash, no space. A directory ends in `/`, a file does not.
_PATH_FORM = re.compile(r"[A-Za-z0-9._-]+(?:/[A-Za-z0-9._-]+)*/?")
_PREFIX_FORM = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*/")
# a workflow's file stem as a run names it (tools/kernel-receipt.py RUN): lower-case ASCII, digits and dashes
_WORKFLOW_FORM = re.compile(r"[a-z0-9][a-z0-9-]*")
# K137 key round 2 (integrator closure 1): the product-bearing roots the tools hard-code (the products default, the
# receipt's product-suite rule, the tools bar's discovery directory). A review path over or inside one would exempt
# product changes from the ordering check.
_PRODUCT_ROOTS = ("src/", "tests/", "tools/")
# K137 key round 2 (integrator closure 4): a hosted runner's log name is a literal prefix and a number
_HOSTED_FORM = re.compile(r"[A-Za-z0-9 _-]+\[0-9\]\+")
# Every key the config must carry, and nothing else: (section, key) -> what its value must be.
_CONFIG_KEYS = {
    "subject": {"prefix": _PREFIX, "row": _REGEX, "branch_prefix": _STR, "delivery": _STR, "default_products": _DIRS},
    "paths": {"briefs": _DIR, "review": _DIR, "receipts": _DIR, "subjects_tool": _FILE, "tools_bar_runner": _FILE},
    "bar": {"runner": _RUNNER, "hosted_runner": _REGEX, "tools_workflow": _STR, "product_workflow": _STR,
            "workflow_suffix": _STR},
    "contract_defaults": {k: _STR for k in CONTRACT_KEYS if k != "filter"},
}


class ConfigError(ValueError):
    """The config is missing, unreadable or malformed: refused, never defaulted (K137)."""


def row_in_subject(row: str) -> re.Pattern:
    """The merge-subject pattern built from `subject.row`; load_config compiles this very form (review round 1)."""
    return re.compile(r"\((" + row + r")\)\s*$")


def load_config(path: Path) -> dict:
    """The parsed config at `path`, every key checked; ConfigError naming the file and the key otherwise."""
    where = f"{path}"
    try:
        raw = path.read_bytes()
    except FileNotFoundError:
        raise ConfigError(f"the config {where} is missing: the kernel tools read their project constants from it "
                          f"and never default them (K137)") from None
    except OSError as exc:
        raise ConfigError(f"the config {where} could not be read: {exc}") from None
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        raise ConfigError(f"the config {where} is not UTF-8") from None
    if text.startswith("\ufeff") or "\x00" in text:
        raise ConfigError(f"the config {where} is not UTF-8 without a byte-order mark")
    def once(pairs):
        # Review round 1 (seat A): json keeps the last of a repeated key, so a second `runner` would win silently.
        seen = {}
        for k, v in pairs:
            if k in seen:
                raise ConfigError(f"the config {where} repeats the key {k!r}")
            seen[k] = v
        return seen
    try:
        data = json.loads(text, object_pairs_hook=once)
    except ConfigError:
        raise
    except ValueError as exc:
        raise ConfigError(f"the config {where} is not valid JSON: {exc}") from None
    if not isinstance(data, dict):
        raise ConfigError(f"the config {where} is not a JSON object")
    want = {"schema", "about", *_CONFIG_KEYS}
    for key in sorted(want - set(data)):
        raise ConfigError(f"the config {where} has no {key}")
    for key in sorted(set(data) - want):
        raise ConfigError(f"the config {where} has an unknown key {key}")
    if type(data["schema"]) is not int or data["schema"] != CONFIG_SCHEMA:
        raise ConfigError(f"the config {where} has schema {data['schema']!r}, not {CONFIG_SCHEMA!r}")
    if not isinstance(data["about"], str):
        raise ConfigError(f"the config {where} has about that is not a string")
    for section, keys in _CONFIG_KEYS.items():
        node = data[section]
        if not isinstance(node, dict):
            raise ConfigError(f"the config {where} has {section} that is not an object")
        for key in sorted(set(keys) - set(node)):
            raise ConfigError(f"the config {where} has no {section}.{key}")
        for key in sorted(set(node) - set(keys)):
            raise ConfigError(f"the config {where} has an unknown key {section}.{key}")
        for key, kind in keys.items():
            _check_value(where, f"{section}.{key}", node[key], kind)
    # Review round 1 (seat A): a pattern valid alone can fail where the tools embed it (inline flags not at the start)
    try:
        row_in_subject(data["subject"]["row"])
    except re.error as exc:
        raise ConfigError(f"the config {where} has subject.row {data['subject']['row']!r}, which does not compile "
                          f"where the tools embed it: {exc}") from None
    bar = data["bar"]
    # Review round 1 (seat A): keys that contradict each other are refused, not reconciled
    for key in ("tools_workflow", "product_workflow"):
        name = bar[key]
        if not (_WORKFLOW_FORM.fullmatch(name) and name.endswith(bar["workflow_suffix"])
                and len(name) > len(bar["workflow_suffix"])):
            raise ConfigError(f"the config {where} has bar.{key} {name!r}, which is not a workflow stem "
                              f"([a-z0-9-]) ending in bar.workflow_suffix {bar['workflow_suffix']!r}")
    if bar["product_workflow"] == bar["tools_workflow"]:
        raise ConfigError(f"the config {where} has bar.product_workflow equal to bar.tools_workflow")
    if "Runner name {runner}" not in data["contract_defaults"]["env"]:
        raise ConfigError(f"the config {where} has contract_defaults.env naming no runner: it must say "
                          "`Runner name {runner}` (tools/kernel-receipt.py reads the env's declared runner)")
    # K137 key round 2 (integrator closure 2): briefs and receipts lie strictly inside the review path
    paths = data["paths"]
    review = paths["review"]
    for key in ("briefs", "receipts"):
        if not (paths[key].startswith(review) and paths[key] != review):
            raise ConfigError(f"the config {where} has paths.{key} {paths[key]!r}, which is not strictly inside "
                              f"paths.review {review!r}")
    # K137 key round 2 (integrator closure 1): review paths never overlap product paths
    for root in _PRODUCT_ROOTS:
        if root.startswith(review) or review.startswith(root):
            raise ConfigError(f"the config {where} has paths.review {review!r}, which overlaps the product root "
                              f"{root!r} the tools hard-code: review paths never exempt product changes")
    for product in data["subject"]["default_products"]:
        for key in ("review", "briefs", "receipts"):
            if product.startswith(paths[key]) or paths[key].startswith(product):
                raise ConfigError(f"the config {where} has subject.default_products {product!r}, which overlaps "
                                  f"paths.{key} {paths[key]!r}")
    # K137 key round 2 (integrator closure 4): the hosted-runner pattern names hosted runners only
    hosted = bar["hosted_runner"]
    if not _HOSTED_FORM.fullmatch(hosted):
        raise ConfigError(f"the config {where} has bar.hosted_runner {hosted!r}, which is not a literal prefix "
                          "followed by [0-9]+ (e.g. `GitHub Actions [0-9]+`)")
    if re.fullmatch(hosted, bar["runner"]):
        raise ConfigError(f"the config {where} has bar.hosted_runner {hosted!r}, which matches bar.runner "
                          f"{bar['runner']!r}")
    return data


def _check_value(where: str, name: str, value, kind: str) -> None:
    def bad() -> ConfigError:
        return ConfigError(f"the config {where} has {name} {value!r}, which is not {kind}")
    if kind == _DIRS:
        if not isinstance(value, list) or not value or len(set(map(str, value))) != len(value):
            raise bad()
        for item in value:                  # review round 1 (seat A): each item is a directory, checked as one
            _check_value(where, name, item, _DIR)
        return
    if not isinstance(value, str) or not value or value != value.strip():
        raise bad()
    if kind == _REGEX:
        try:
            re.compile(value)
        except re.error:
            raise bad() from None
    elif kind in (_DIR, _FILE):
        if not _PATH_FORM.fullmatch(value) or {".", ".."} & set(value.rstrip("/").split("/")) or \
                value.endswith("/") != (kind == _DIR):
            raise bad()
    elif kind == _PREFIX:
        if not _PREFIX_FORM.fullmatch(value):
            raise bad()
    elif kind == _RUNNER:
        if not re.fullmatch(RUNNER_WORDS, value):
            raise bad()


try:
    CONFIG = load_config(CONFIG_PATH)
except ConfigError as _exc:
    if __name__ == "__main__":
        print(f"REFUSE kernel-subjects: {_exc}", file=sys.stderr)
        sys.exit(2)
    raise
_SUBJECT, _PATHS, _BAR = CONFIG["subject"], CONFIG["paths"], CONFIG["bar"]
SUBJECT_PREFIX = _SUBJECT["prefix"]

HEADING = re.compile(r"^## Kernel subject[ \t]*$", re.M)
NEXT_HEADING = re.compile(r"^## ", re.M)
FIELD = re.compile(r"^- ([a-z-]+): (.*?)[ \t]*$")
FENCE = re.compile(r"^```contract[ \t]*\n(.*?)^```[ \t]*$", re.S | re.M)
MANIFEST_FENCE = re.compile(r"^```manifest[ \t]*\n(.*?)^```[ \t]*$", re.S | re.M)
FIELDS = ("subject", "kernel", "profile", "contract", "key", "delivery", "identity")
OPTIONAL_FIELDS = ("products",)
PRODUCT_TOKEN = re.compile(r"^[A-Za-z0-9._-][^\s]*$")
SUBJECT = re.compile(r"^" + re.escape(SUBJECT_PREFIX) + r"([A-Za-z0-9][A-Za-z0-9-]*)$")
KERNEL = re.compile(r"^r\d+$")
PROFILE = re.compile(r"^code@r\d+ \(bus [0-9a-f]{7,40}\)$")
DIGEST = re.compile(r"^sha256:([0-9a-f]{64})$")
# K6 key classes. `pending-cross-family` is the honest default: Cloudvore's review seats are Claude, so a subject
# declared with it is declared and receipted, never claimed closed (kernel K6; brief "K6: do not fake it").
KEY = re.compile(r"^(pending-cross-family|cross-family:[A-Za-z0-9._-]+|ci-runner:[A-Za-z0-9._-]+|human:[A-Za-z0-9._-]+)$")
DELIVERY = _SUBJECT["delivery"]
# K124: `path manifest` when the block declares a ```manifest, else `default` (code@r10's default identity: the landed
# merge's tree, every pass of the bar there). tools/kernel-receipt.py keys off the manifest fence and says which it used.
IDENTITY = re.compile(r"^(path manifest|default)\b")
IDENTITY_MANIFEST = "path manifest (declared below before review; tools/kernel-receipt.py compares it)"
IDENTITY_DEFAULT = ("default (the landed merge's tree, the contract's passes all run there; no manifest declared; "
                    "tools/kernel-receipt.py says which identity it used)")

PRODUCT_PREFIXES = tuple(_SUBJECT["default_products"])   # what a block that declares no `products:` orders against
BRIEFS = _PATHS["briefs"]
REVIEW = _PATHS["review"]           # briefs, ledgers and evidence: never a product, never undeclared
RECEIPTS = _PATHS["receipts"]
TOOL_PATH = _PATHS["subjects_tool"]
ADVISORY_WINDOW = 10          # newest landings the advisory checks per run; older ones are counted, not read
RECEIPT_MERGE = re.compile(r"^- landed merge: ([0-9a-f]{40})\b", re.M)
ROW_IN_SUBJECT = row_in_subject(_SUBJECT["row"])
BRANCH_IN_SUBJECT = re.compile(r"^Merge (?:branch '?)?(?:" + re.escape(_SUBJECT["branch_prefix"]) + r")?([A-Za-z0-9]+)")

# The order flags are reported in; a result's status is its first flag, else OK.
FLAGS = ("NO-BRIEF", "NO-BLOCK", "AMBIGUOUS", "MALFORMED", "CONTRACT-MISMATCH", "CONTRACT-CHANGED",
         "PRODUCTS-UNDECLARED", "ORDER-VIOLATION", "NO-RECEIPT", "RECEIPT-MISMATCH")

_LOCATORS = ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY",
             "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_COMMON_DIR", "GIT_NAMESPACE")


class GitFailed(Exception):
    """git did not answer what it was asked: a non-zero exit, or anything on stderr beside its stdout."""


def _env() -> dict:
    env = {k: v for k, v in os.environ.items()
           if not (k.upper().startswith("GIT_TRACE") or k.upper() in _LOCATORS)}
    env["GIT_NO_REPLACE_OBJECTS"] = "1"
    return env


def git_argv(repo: Path, *args: str) -> list[str]:
    """Every git call, both tools: read-only, and paths printed as their bytes (round 1, seat A)."""
    return ["git", "--no-optional-locks", "-c", "core.quotePath=false", "-C", str(repo), *args]


def listed_paths(text: str) -> list[str]:
    """Paths git listed one per line. A path git quoted even with quotePath off (a control character, a double
    quote or a backslash in its name) is refused: read as written it would be some other path, never this one."""
    paths = [l for l in text.split("\n") if l.strip()]
    for p in paths:
        if p.startswith('"'):
            raise GitFailed(f"git quoted a path it would not print plainly: {p[:80]}")
    return paths


def git(repo: Path, *args: str, binary: bool = False):
    p = subprocess.run(git_argv(repo, *args), capture_output=True, env=_env(), timeout=60)
    if p.returncode != 0 or p.stderr.strip():
        raise GitFailed(f"git {' '.join(args[:3])}: exit {p.returncode}: "
                        f"{p.stderr.decode('utf-8', 'replace').strip()[:200]}")
    return p.stdout if binary else p.stdout.decode("utf-8", "replace").replace("\r\n", "\n")


def rev(repo: Path, spec: str) -> str:
    return git(repo, "rev-parse", "--verify", "--end-of-options", f"{spec}^{{commit}}").strip()


def path_at(repo: Path, commit: str, path: str) -> str | None:
    """The file's text at `commit`, or None when the commit holds no such file -- a stated negative: `ls-tree`
    exits 0 and lists nothing for a path that is not there."""
    listed = git(repo, "ls-tree", "--name-only", commit, "--", path).strip()
    if listed != path:
        return None
    return git(repo, "cat-file", "blob", f"{commit}:{path}", binary=True).decode("utf-8", "replace").replace("\r\n", "\n")


# ---- the block -----------------------------------------------------------------------------------------------------

def canonical(raw: str) -> str:
    """The contract's canonical text: LF line ends, trailing blanks off every line, no trailing empty lines, one
    final LF. Its sha256 is the declared digest."""
    lines = [line.rstrip() for line in raw.replace("\r\n", "\n").split("\n")]
    while lines and not lines[-1]:
        lines.pop()
    while lines and not lines[0]:
        lines.pop(0)
    return "\n".join(lines) + "\n"


def digest(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def section(text: str) -> str | None:
    m = HEADING.search(text)
    if not m:
        return None
    rest = text[m.end():]
    # the fenced contract holds `key: value` lines only, so a `## ` inside it would itself be malformed
    n = NEXT_HEADING.search(rest)
    return rest[:n.start()] if n else rest


def parse_block(text: str) -> dict | None:
    """None when the text carries no `## Kernel subject` heading; else the fields, the canonical contract text,
    its recomputed digest, and every problem that makes the block MALFORMED."""
    body = section(text.replace("\r\n", "\n"))
    if body is None:
        return None
    fields: dict = {}
    problems: list = []
    fence = FENCE.search(body)
    manifest_fence = MANIFEST_FENCE.search(body)
    outside = body
    for f in sorted((x for x in (fence, manifest_fence) if x), key=lambda x: -x.start()):
        outside = outside[:f.start()] + outside[f.end():]
    for line in outside.splitlines():
        m = FIELD.match(line)
        if m and m.group(1) in FIELDS + OPTIONAL_FIELDS:
            if m.group(1) in fields:
                problems.append(f"{m.group(1)} declared twice")
            fields[m.group(1)] = m.group(2)
    products = PRODUCT_PREFIXES
    if "products" in fields:
        tokens = tuple(fields["products"].split())
        bad = [t for t in tokens if not PRODUCT_TOKEN.match(t) or ".." in t.split("/") or t.startswith("/")]
        if not tokens or bad or len(set(tokens)) != len(tokens):
            problems.append(f"products is not a list of distinct repository paths: {fields['products']!r}")
        else:
            # Round 2, seat A: a block may ADD products, never narrow them. A late block declaring `products: zzz/`
            # left nothing to order (OK, first-product=none, and a MATCH receipt); src/ and tests/ always count.
            products = PRODUCT_PREFIXES + tuple(t for t in tokens if t not in PRODUCT_PREFIXES)
    manifest = None
    if manifest_fence:
        manifest = [l.strip() for l in manifest_fence.group(1).replace("\r\n", "\n").split("\n") if l.strip()]
        if not manifest or len(set(manifest)) != len(manifest) or any(
                p.startswith(("/", '"')) or ".." in p.split("/") for p in manifest):
            problems.append("the manifest is not a nonempty list of distinct repository paths")
    for name in FIELDS:
        if name not in fields:
            problems.append(f"no {name} field")
    checks = (("subject", SUBJECT), ("kernel", KERNEL), ("profile", PROFILE), ("contract", DIGEST), ("key", KEY),
              ("identity", IDENTITY))
    for name, pattern in checks:
        if name in fields and not pattern.search(fields[name]):
            problems.append(f"{name} is not well-formed: {fields[name]!r}")
    if "delivery" in fields and fields["delivery"] != DELIVERY:
        problems.append(f"delivery is not {DELIVERY!r}: {fields['delivery']!r}")
    contract = recomputed = None
    if not fence:
        problems.append("no ```contract fence")
    else:
        contract = canonical(fence.group(1))
        recomputed = digest(contract)
        keys = []
        for line in contract.splitlines():
            m = re.match(r"^([a-z-]+): (\S.*)$", line)
            if not m:
                problems.append(f"contract line is not `key: value`: {line!r}")
                continue
            keys.append(m.group(1))
        if tuple(keys) != CONTRACT_KEYS:
            problems.append(f"contract keys are {keys}, not {list(CONTRACT_KEYS)} in that order")
    m = SUBJECT.match(fields.get("subject", ""))
    return {"fields": fields, "row": m.group(1) if m else None, "contract_text": contract,
            "recomputed": recomputed, "products": products, "manifest": manifest, "problems": problems}


def terms(block: dict) -> tuple:
    """What may not change once declared: the declared digest, the digest the text recomputes to, the products, and
    the K6 key class (round 2: a key class swapped after work began read unchanged)."""
    return (block["fields"].get("contract"), block["recomputed"], tuple(block["products"]),
            block["fields"].get("key"))


def manifest_changes(versions: list, with_block: list, tip: str) -> list[str]:
    """K95: the declared manifest is a compared term once declared. Its FIRST declaration may follow the block (the
    profile asks for it before review, which this tool cannot see), so versions carrying no manifest before it are
    not a change; after it, every version of every brief carrying the block, and the tip's, must declare the same
    set of paths. A manifest changed, dropped, or changed and changed back reads CONTRACT-CHANGED."""
    seq = [(c_sha, p, b["manifest"]) for _i, c_sha, p, b in versions] + [(tip, p, b["manifest"]) for p, b in with_block]
    first = next(((c_sha, p, m) for c_sha, p, m in seq if m is not None), None)
    if first is None:
        return []
    want = sorted(first[2])
    seen = False
    out = []
    for c_sha, p, m in seq:
        if not seen:
            seen = (c_sha, p, m) == first
            continue
        if m is None or sorted(m) != want:
            out.append(f"{p} at {c_sha[:9]} declares manifest "
                       f"{'none' if m is None else ' '.join(sorted(m))}; first declared at {first[0][:9]} as "
                       f"{' '.join(want)}")
    return out


# K120: the bar workflows' `runs-on` is `${{ vars.CI_RUNS_ON != '' && fromJSON(vars.CI_RUNS_ON) || 'windows-latest' }}`
# (.github/workflows/tools-bar.yml, product-bar.yml). Since 2026-09-07 CI_RUNS_ON sends both to the self-hosted runner
# the config names (run logs: "Runner name: '<bar.runner>'"). Before K120 the default block said "hosted windows-latest"
# as a fact, so every subject declared an environment its bars never ran in. The env names the runner as
# `Runner name <name>`: tools/kernel-receipt.py refuses a run whose runner is not one the env names.
BAR_RUNNER = _BAR["runner"]
# K137: the default contract text is the config's; its env names the runner as `Runner name {runner}`.
DEFAULTS = {k: (v.replace("{runner}", BAR_RUNNER) if k == "env" else v)
            for k, v in CONFIG["contract_defaults"].items()}


def default_contract(filter_: str, **given: str | None) -> str:
    values = {**DEFAULTS, "filter": filter_,
              **{k.replace("_", "-"): v for k, v in given.items() if v is not None}}
    return canonical("\n".join(f"{k}: {values[k]}" for k in CONTRACT_KEYS))


def render_block(row: str, filter_: str, bus_sha: str, kernel: str = "r5", profile: str = "code@r10",
                 key: str = "pending-cross-family", products: str | None = None,
                 manifest: list[str] | None = None, **contract: str | None) -> str:
    text = default_contract(filter_, **contract)
    return ("## Kernel subject\n\n"
            f"- subject: {SUBJECT_PREFIX}{row}\n"
            f"- kernel: {kernel}\n"
            f"- profile: {profile} (bus {bus_sha})\n"
            f"- contract: {digest(text)}\n"
            f"- key: {key}\n"
            f"- delivery: {DELIVERY}\n"
            f"- identity: {IDENTITY_MANIFEST if manifest else IDENTITY_DEFAULT}\n"
            + (f"- products: {products}\n" if products else "")
            + "\n```contract\n" + text + "```\n"
            + ("\n```manifest\n" + "".join(p + "\n" for p in manifest) + "```\n" if manifest else ""))


# ---- one packet ----------------------------------------------------------------------------------------------------

def range_commits(repo: Path, base: str, tip: str, also: tuple = ()) -> list[dict]:
    """The commits `tip` has and `base` (and every commit in `also`) has not, oldest first (topo order), each with the
    paths it touched. Merge commits list no paths: a merge of master into the branch carries master's bytes, not
    the packet's."""
    out = git(repo, "log", "--reverse", "--topo-order", "--no-renames", "--name-only",
              "--format=%x01%H %P", f"{tip}", f"^{base}", *(f"^{x}" for x in also), "--")
    commits = []
    for record in out.split("\x01")[1:]:
        lines = record.split("\n")
        head = lines[0].split()
        commits.append({"sha": head[0], "parents": len(head) - 1, "paths": listed_paths("\n".join(lines[1:]))})
    return commits


def merge_brief_paths(repo: Path, sha: str) -> list[str]:
    """The briefs a merge's result differs on against ANY of its parents (`diff-tree -m`, one section per parent)."""
    listed = listed_paths(git(repo, "diff-tree", "--no-commit-id", "-r", "-m", "--no-renames", "--name-only", sha,
                              "--", BRIEFS))
    return sorted(set(listed))


def is_product(path: str, products) -> bool:
    return any(path == t or path.startswith(t if t.endswith("/") else t + "/") for t in products)


def subject_name(repo: Path, sha: str) -> str:
    """A name for a landing with no block: `(H171)` at the end of the merge subject, else the branch's leading token."""
    subject = git(repo, "log", "-1", "--format=%s", sha).strip()
    m = ROW_IN_SUBJECT.search(subject)
    if m:
        return m.group(1)
    m = BRANCH_IN_SUBJECT.match(subject)
    return m.group(1).upper() if m else sha[:9]


def is_ancestor(repo: Path, a: str, b: str) -> bool:
    """`a` is `b` or an ancestor of it: `merge-base --is-ancestor` exit 0 yes, 1 no; anything else is GitFailed."""
    p = subprocess.run(git_argv(repo, "merge-base", "--is-ancestor", a, b), capture_output=True, env=_env(),
                       timeout=60)
    if p.returncode not in (0, 1) or p.stderr.strip():
        raise GitFailed(f"git merge-base --is-ancestor: exit {p.returncode}: "
                        f"{p.stderr.decode('utf-8', 'replace').strip()[:200]}")
    return p.returncode == 0


def line_briefs(repo: Path, side: str, other: str) -> set[str]:
    """The briefs touched by a non-merge commit on `side`'s FIRST-PARENT line that `other` does not hold. A packet
    branch's own commits (its brief among them) sit on its first-parent line; master's first-parent line beyond a
    branch point is landing merges (which list no paths) and direct commits, and other packets' briefs reach it only
    through those merges' second parents. The commits `other` holds are read from a full walk (`rev-list side
    ^other`), never from how --first-parent treats the negative side."""
    inside = set(git(repo, "rev-list", side, f"^{other}").split())
    out = git(repo, "log", "--first-parent", "--no-renames", "--name-only", "--format=%x01%H %P", side, f"^{other}",
              "--")
    found = set()
    for record in out.split("\x01")[1:]:
        lines = record.split("\n")
        head = lines[0].split()
        if head[0] not in inside or len(head) > 2:
            continue
        found |= {p for p in listed_paths("\n".join(lines[1:])) if p.startswith(BRIEFS) and p.endswith(".md")}
    return found


def is_landing(repo: Path, parents: list[str]) -> bool:
    """A two-parent merge is a landing (first parent = base, second = the packet), EXCEPT a line merged INTO a packet
    branch (K170): a brief on its FIRST parent's first-parent line (`line_briefs`) and none on its second's. Builders
    merge master into their branch, and that tip was read as the landing of whatever master carried (H95 at 4fde7af
    read H40). Decided from the merge's own two sides, never from `--base` (key round 1: a base read for freshness
    misread a landing whose second parent origin/master held, and a merge of a master ahead of the base). A real
    landing carries the packet's brief on its second parent's line; a merge of two packet branches carries one on
    each; a merge with a brief on neither line says nothing: those stay landings, as before K170. Three or more
    parents never were."""
    if len(parents) != 2:
        return False
    return not (line_briefs(repo, parents[0], parents[1]) and not line_briefs(repo, parents[1], parents[0]))


def check(repo: Path, target: str, base: str = "origin/master", at: str | None = None,
          named_landing: bool = False) -> dict:
    """Read one landing merge (two parents: base = first parent, tip = second) or one branch tip (base = `base`).
    A two-parent tip that merged a line INTO a packet branch is a branch tip (K170, `is_landing`), its range what the
    tip has that both `base` and the merged line do not; a `base` that does not resolve is refused (GitFailed), as
    at any branch tip. `named_landing`: the caller names a landing (the advisory, the receipt), so every two-parent
    target is read as one, undecided."""
    sha = rev(repo, target)
    parents = git(repo, "log", "-1", "--format=%P", sha).split()
    landing = len(parents) == 2 and (named_landing or is_landing(repo, parents))
    also: tuple = ()
    if landing:
        base_sha, tip = parents[0], parents[1]
    elif len(parents) == 2:
        # K170: the merged line is never the packet's, whatever `base` holds. A base that does not resolve (misspelled,
        # or the default origin/master absent) refuses here exactly as at the pre-merge tip: a git failure is never a
        # verdict (key round 2, finding 2: the merged line once stood in for it and read OK).
        also, tip = (parents[1],), sha
        base_sha = rev(repo, base)
    else:
        base_sha, tip = rev(repo, base), sha
    out = {"target": sha, "landing": landing, "base": base_sha, "tip": tip, "flags": [], "subject": None,
           "row": None, "brief": None, "block_commit": None, "first_product": None, "violators": [],
           "contract": None, "recomputed": None, "receipt": None, "products": list(PRODUCT_PREFIXES),
           "manifest": None, "undeclared": [], "problems": []}
    commits = range_commits(repo, base_sha, tip, also)
    out["commits"] = len(commits)

    def product_commits(products) -> list[str]:
        return [c["sha"] for c in commits if c["parents"] <= 1 and any(is_product(p, products) for p in c["paths"])]

    product = product_commits(PRODUCT_PREFIXES)
    out["first_product"] = product[0] if product else None
    briefs = sorted({p for c in commits for p in c["paths"] if p.startswith(BRIEFS) and p.endswith(".md")})
    out["briefs"] = briefs
    if not briefs:
        out["flags"].append("NO-BRIEF")
        return finish(repo, out, sha, landing)
    with_block = []
    for path in briefs:
        text = path_at(repo, tip, path)
        block = parse_block(text) if text is not None else None
        if block is not None:
            with_block.append((path, block))
    if not with_block:
        out["flags"].append("NO-BLOCK")
        return finish(repo, out, sha, landing)
    subjects = {b["fields"].get("subject") for _p, b in with_block}
    if len(subjects) > 1:
        out["flags"].append("AMBIGUOUS")
        out["problems"].append(f"briefs declare different subjects: {sorted(s or '?' for s in subjects)}")
    # Every version of every brief in the range: each commit that touches a brief, read at that commit. The block's
    # first commit is the earliest that carries it in any brief; the terms are compared at every one (round 1, seat
    # A's P3 and P4: a contract changed and changed back, or a second brief with other terms, read unchanged).
    # K95 round 2 (Codex): merges list no paths in `range_commits`, so a brief changed inside one merge's resolution
    # and restored in a later one was never read, and a manifest changed and restored through merges read OK. Every
    # merge in the range is read too, at each brief whose blob differs from ANY parent's.
    versions = []                                       # (index in range, commit, brief, parsed block)
    merge_versions = set()                              # (index, brief) read at a merge: never the block's first commit
    for i, c in enumerate(commits):
        # at a merge, only the packet's own briefs: master merged in carries other packets' briefs, never this one's.
        # K95 round 3 (Codex and the Claude seat, each reproduced): a brief RENAMED inside a merge exists at no
        # non-merge commit, so a path filter on `briefs` never read it; the packet's own brief is the one whose block
        # declares this packet's subject, at whatever path a merge gives it.
        paths = c["paths"] if c["parents"] <= 1 else merge_brief_paths(repo, c["sha"])
        for path in paths:
            if path.startswith(BRIEFS) and path.endswith(".md"):
                text = path_at(repo, c["sha"], path)
                parsed = parse_block(text) if text is not None else None
                if parsed is not None and c["parents"] > 1 and path not in briefs                         and parsed["fields"].get("subject") not in subjects:
                    continue
                if parsed is not None:
                    versions.append((i, c["sha"], path, parsed))
                    if c["parents"] > 1:
                        merge_versions.add((i, path))
    chosen = {p: b for p, b in with_block}
    first_at = {}
    for i, c_sha, path, parsed in versions:
        if path in chosen and path not in first_at and (i, path) not in merge_versions:
            first_at[path] = (i, c_sha)
    path, block = min(with_block, key=lambda pb: first_at.get(pb[0], (len(commits), ""))[0])
    out["brief"], out["subject"], out["row"] = path, block["fields"].get("subject"), block["row"]
    out["contract"], out["recomputed"] = block["fields"].get("contract"), block["recomputed"]
    out["products"], out["manifest"] = list(block["products"]), block["manifest"]
    out["problems"] += block["problems"]
    if block["problems"]:
        out["flags"].append("MALFORMED")
    if block["recomputed"] and out["contract"] and DIGEST.match(out["contract"]) and out["contract"] != block["recomputed"]:
        out["flags"].append("CONTRACT-MISMATCH")
    want = terms(block)
    changed = [(c_sha, p, terms(b)) for _i, c_sha, p, b in versions if terms(b) != want]
    changed += [(tip, p, terms(b)) for p, b in with_block if terms(b) != want]
    manifest_moves = manifest_changes(versions, with_block, tip)
    if changed or manifest_moves:
        out["flags"].append("CONTRACT-CHANGED")
        for c_sha, p, t in changed[:5]:
            out["problems"].append(f"{p} at {c_sha[:9]} declares contract {t[0]}, recomputing to {t[1]}, products "
                                   f"{' '.join(t[2])}, key {t[3]}; the tip's brief declares {want[0]}, {want[1]}, "
                                   f"{' '.join(want[2])}, key {want[3]}")
        out["problems"] += manifest_moves[:5]
    product = product_commits(block["products"])
    out["first_product"] = product[0] if product else None
    # Every path the packet's own commits touch is a product, a brief, or review evidence (round 2 adjudication):
    # a path outside all three is work the block never declared, and ORDER could not have seen it.
    undeclared = sorted({p for c in commits if c["parents"] <= 1 for p in c["paths"]
                         if not is_product(p, block["products"]) and not p.startswith(REVIEW)})
    out["undeclared"] = undeclared
    if undeclared:
        out["flags"].append("PRODUCTS-UNDECLARED")
        out["problems"].append("paths outside the products and review/: " + ", ".join(undeclared[:5])
                               + (f", +{len(undeclared) - 5} more" if len(undeclared) > 5 else ""))
    starts = [first_at[p] for p in first_at]
    if starts:
        block_sha = min(starts)[1]
        out["block_commit"] = block_sha
        if product:
            after = set(git(repo, "rev-list", "--ancestry-path", f"{block_sha}..{tip}").split())
            out["violators"] = [p for p in product if p not in after]
            if out["violators"]:
                out["flags"].append("ORDER-VIOLATION")
    else:
        # the block is at the tip, but no commit in the range that touched the brief carried it: it came in
        # through a merge, which this tool cannot place before anything
        out["flags"].append("ORDER-VIOLATION")
        out["problems"].append("the block reached the tip through a merge; no commit of the range carries it")
    return finish(repo, out, sha, landing, at)


def finish(repo: Path, out: dict, sha: str, landing: bool, at: str | None = None) -> dict:
    if landing and out["row"]:
        where = rev(repo, at) if at else sha
        receipt_path = f"{RECEIPTS}{out['row']}.md"
        text = path_at(repo, where, receipt_path)
        out["receipt"] = receipt_path if text is not None else None
        if text is None:
            out["flags"].append("NO-RECEIPT")
        else:
            m = RECEIPT_MERGE.search(text)
            if not m or m.group(1) != sha:
                out["flags"].append("RECEIPT-MISMATCH")
                out["problems"].append(f"{receipt_path} names merge {m.group(1)[:9] if m else 'none'}, not {sha[:9]}")
    out["flags"] = [f for f in FLAGS if f in out["flags"]]
    out["status"] = out["flags"][0] if out["flags"] else "OK"
    if out["row"] is None and landing:
        out["name"] = subject_name(repo, sha)
    else:
        out["name"] = out["row"] or sha[:9]
    return out


def line(r: dict) -> str:
    short = lambda s: s[:9] if s else "none"   # noqa: E731
    bits = [r["subject"] or f"{SUBJECT_PREFIX}{r['name']}?", r["status"],
            f"{'landing' if r['landing'] else 'branch'}={short(r['target'])}",
            f"brief={r['brief'] or (','.join(r['briefs']) if r.get('briefs') else 'none')}",
            f"block={short(r['block_commit'])}", f"first-product={short(r['first_product'])}",
            f"products={','.join(r['products'])}"]
    if r["contract"]:
        bits.append("contract=" + ("recomputes" if r["contract"] == r["recomputed"] else "MISMATCH"))
    if r["landing"]:
        bits.append(f"receipt={r['receipt'] or 'none'}")
    if len(r["flags"]) > 1:
        bits.append("flags=" + ",".join(r["flags"]))
    if r["violators"]:
        bits.append("before-block=" + ",".join(v[:9] for v in r["violators"]))
    return " ".join(bits)


# ---- every landing since this tool landed ---------------------------------------------------------------------------

def advisory(repo: Path, ref: str = "master", window: int = ADVISORY_WINDOW) -> dict:
    """Every first-parent landing merge on `ref` from the one that brought this tool (included) onward. ADVISORY:
    it names what is undeclared; nothing refuses on it yet. The newest `window` are read; the rest are counted."""
    tip = rev(repo, ref)
    added = git(repo, "log", "--first-parent", "--diff-filter=A", "--format=%H", tip, "--", TOOL_PATH).split()
    out = {"ok": True, "ref": ref, "since": None, "landings": 0, "checked": 0, "flagged": [], "unchecked": 0}
    if not added:
        out["note"] = f"{TOOL_PATH} is not on {ref}"
        return out
    since = added[-1]
    out["since"] = since
    merges = git(repo, "rev-list", "--first-parent", "--merges", f"{since}..{tip}").split()
    if len(git(repo, "log", "-1", "--format=%P", since).split()) == 2:
        merges.append(since)                       # this packet's own landing is the first subject read
    out["landings"] = len(merges)
    for m in merges[:window]:
        # K170: every first-parent merge on the walked ref is a landing; the advisory names it one, so `is_landing`
        # never decides here, however the merge's two sides look: the advisory's domain, unchanged.
        r = check(repo, m, base=tip, at=tip, named_landing=True)
        out["checked"] += 1
        if r["status"] != "OK":
            out["flagged"].append({"merge": m, "name": r["name"], "status": r["status"], "flags": r["flags"]})
    out["unchecked"] = max(0, len(merges) - window)
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", default=".")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check")
    c.add_argument("target")
    c.add_argument("--base", default="origin/master")
    c.add_argument("--at", default=None, help="ref whose tree holds the receipt (default: the landing merge itself)")
    c.add_argument("--json", action="store_true")
    a = sub.add_parser("advisory")
    a.add_argument("--ref", default="master")
    a.add_argument("--json", action="store_true")
    b = sub.add_parser("block")
    b.add_argument("--row", required=True)
    b.add_argument("--filter", required=True)
    b.add_argument("--bus-sha", required=True)
    b.add_argument("--key", default="pending-cross-family")
    b.add_argument("--products", default=None, help="the packet's product paths, e.g. 'tools/ docs/' (default src/ tests/)")
    b.add_argument("--manifest", action="append", default=None, help="a declared identity path; repeat per path (none: the default "
                                                                    "identity, the landed merge's tree)")
    for key in CONTRACT_KEYS:
        if key != "filter":
            b.add_argument(f"--{key}", dest=key.replace("-", "_"), default=None)
    args = ap.parse_args(argv)
    repo = Path(args.repo).resolve()
    if args.cmd == "block":
        given = {k.replace("-", "_"): getattr(args, k.replace("-", "_")) for k in CONTRACT_KEYS if k != "filter"}
        text = render_block(args.row, args.filter, args.bus_sha, key=args.key, products=args.products,
                            manifest=sorted(args.manifest) if args.manifest else None, **given)
        parsed = parse_block(text)
        if parsed["problems"]:
            print("REFUSE kernel-subjects: the block would be malformed: " + "; ".join(parsed["problems"]),
                  file=sys.stderr)
            return 2
        sys.stdout.write(text)
        return 0
    try:
        if args.cmd == "check":
            r = check(repo, args.target, args.base, args.at)
            print(json.dumps(r, indent=2, sort_keys=True) if args.json else line(r))
            return 1 if r["flags"] else 0
        r = advisory(repo, args.ref)
        if args.json:
            print(json.dumps(r, indent=2, sort_keys=True))
        else:
            print(f"kernel advisory on {r['ref']}: since={(r['since'] or 'none')[:9]} landings={r['landings']} "
                  f"checked={r['checked']} unchecked={r['unchecked']} flagged={len(r['flagged'])}"
                  + (f" ({r['note']})" if r.get("note") else ""))
            for f in r["flagged"]:
                print(f"  {f['name']} {f['status']} merge={f['merge'][:9]} flags={','.join(f['flags'])}")
        return 0
    except (GitFailed, subprocess.TimeoutExpired, OSError) as exc:
        print(f"REFUSE kernel-subjects: git did not answer: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
