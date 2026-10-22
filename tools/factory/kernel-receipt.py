#!/usr/bin/env python3
"""kernel-receipt.py -- write `review/kernel-receipts/<row>.md` for one landed kernel subject.

Run at landing, after the `--no-ff` merge exists and before the ONE push that carries it (the receipt goes in the
DONE-row commit after the merge: a receipt inside the merge could not name the merge's own tree). It records:

  - the subject's block as declared in its brief (subject, kernel, profile, contract digest, products, key class);
  - the barred candidate commit and its tree OID, the landed merge and its tree OID, and `trees: equal|differ`;
  - K124: the identity it used. A subject that declares NO ```manifest is identified by code@r10's DEFAULT identity,
    "the git tree OID of the candidate commit as it will be delivered, after any merge": the landed merge's tree. It
    is credited only by the contract's `passes` count of green bar runs AT the landed merge (fewer is refused); runs
    at the barred commit are recorded, marked not counted, and never count toward its passes. Before K124 such a
    brief was refused, and the K121 adjudication found that no subject whose filter runs gate.py can hold a complete
    manifest (BACKLOG.md changes on every landing). The rest of this item is the manifest path;
  - with a declared manifest, the K3 identity under the rule `path manifest`. The receipt says the manifest is the
    DECLARER'S CLAIM: it does not derive what the acceptance checks read. It does require the bar-defining inputs
    declared -- each workflow the contract's `bar:` names, tools/run-tools-bar.py, and the `filter:` suite -- and
    refuses a manifest that leaves one out, a `bar:` naming no workflow, or a `filter:` naming no repository path
    (K121 adjudicator C, its mechanically checkable part). The manifest is the one DECLARED in the brief (a fenced
    ```manifest, before review). Per code@r10 (bus profiles/code.md, Subject identity) it is a set of repository
    INPUTS: it "includes every repository input the reviewed behaviour or acceptance checks depend on", so it may
    list unchanged inputs (a harness, a fixture, a workflow) beside the changed paths. The receipt derives the paths
    the packet changes (`git diff --name-only <merge>^1 <merge>`) united with the paths the barred candidate changed
    since it left master; `manifest: MATCH` needs every one of them declared (a changed path left undeclared reads
    DIFFER) and says how many declared inputs are unchanged. Identity = sha256 of the declared manifest's digest
    followed by each declared path's blob OID (or `absent`) in path order, joined by LF (kernel K3), computed at the
    barred commit and at the merge; and no commit in `<barred>..<merge>` may touch a declared path ("the intervening
    range must touch no declared path"): no non-merge commit, and no merge whose resolution changed one. `identity: MATCH` needs all three; anything else reads DIFFER.
    (K95: before it the manifest had to EQUAL the changed set -- a false alarm on a profile-shaped manifest.)
  - every run of the bar the caller names (`--run <workflow>/<id>=<conclusion>@<sha>:<runner name>`, repeated), each
    bound to its workflow, the commit it tested and the runner it ran on, as the caller read them (`gh run view <id>`):
    this tool contacts nothing. The caller
    reads the runner from the run's log (`gh run view <id> --log | grep "Runner name"`). K120: the bar workflows'
    `runs-on` resolves CI_RUNS_ON (today the self-hosted ultra-magnus runner), so a run is refused unless its runner
    is one the contract's `env:` names as `Runner name <name>`; an env that names no runner, or a run that names
    none, is refused -- the receipt never assumes where a run ran. A run at neither the barred commit nor
    the landed merge is refused. The receipt counts the runs AT the landed merge (the profile's re-run "green at the
    delivered tree"). `creditable: yes` needs identity MATCH, the contract's `passes` count of green runs at ONE sha
    (never summed across the two), and at least one green run at the landed merge; otherwise it says which is
    missing. A declared path that names nothing at both commits is refused (a misspelling is not an input).
    K124 round 3 (the K6 key's REJECT of 6576d42): a run's workflow must be one the contract's `bar:` names; the
    workflow that runs the `filter:` is decided mechanically (`filter_workflow`: tools/*.tests.py suites in
    run-tools-bar.py's REQUIRED run in tools-bar, a filter naming no tools/ path runs in product-bar, anything else is
    refused); only that workflow's green runs count toward the passes, on both identity paths, and every workflow
    the bar names needs a green run at the landed merge. Runs of other workflows are recorded, marked not counted;
  - the review ledger's path and whether the landed merge's tree holds it;
  - the K6 key: its class, its verdict line and the sha256 of the verdict file when there is one. The verdict line is
    END-ANCHORED (K118 revisions 3 and 4): the verdict file is the key's FINAL MESSAGE (`codex exec -o <file>`); a
    `codex exec` transcript (a line `OpenAI Codex v...` then `--------`) is refused, never parsed. The file's last
    non-blank line, stripped of ASCII spaces, tabs and CR and nothing else, must be exactly `VERDICT:
    ACCEPT|REJECT|REFUSE <the full landed merge sha>`; anything else, a closing code fence or a markdown marker
    included, is refused and no earlier line is consulted (K118 revisions 6 and 7: no fence or marker is stripped).
    `creditable: yes` needs ACCEPT for a non-pending key (K118:
    before it the FIRST `VERDICT:` line was recorded -- the K115 key's echoed `VERDICT: ACCEPT <merge>` template above
    its real REJECT -- and the verdict never reached `creditable`).
    K140: the final message alone does not say the key READ anything: tools/codex-review.py reads a run whose Windows
    sandbox failed as `not_run` (K135) and exits nonzero, but its final message may still read ACCEPT, and a caller
    who ignored the exit code got a receipt. `--key-result <file>` is REQUIRED for a Codex key class
    (`cross-family:codex` or `cross-family:codex-*`) and refused for any other (K6 key round 2: a pending, runner or
    human key, or another cross-family key, keeps the verdict file alone, as before K140): the file holding codex-review's stdout for the SAME run (its `last message:` line, its JSON
    result line, and anything a caller appended, such as `rc=0`). Every line starting `{` must be a JSON object and
    there must be exactly one; a codex exec transcript is refused; the file may not be the verdict file; a UTF-16
    file (a PowerShell 5.1 `>` redirect) is refused, saying to save it as UTF-8. The result must carry tier, exit,
    last_message, last_message_ok, last_message_sha256, sandbox_failure, role, actual_model, actual_effort and
    actual_sandbox, reviewed_head (a result from before K135 or K140 rounds 1-2 is refused) and is accepted only as codex-review exits 0
    on it: tier "ok", exit the integer 0, last_message_ok true, sandbox_failure
    null. Its last_message must be an absolute path naming the --key-verdict file itself (os.path.samefile), and
    (K6 key round 1) its last_message_sha256 must equal the sha256 of the --key-verdict file's bytes. One -o path is
    reused across runs (codex-review deletes and rewrites it each run), so the path alone let an earlier run's ok
    result vouch for a later run's ACCEPT. The digest proves equal bytes, not the same run (K6 key round 2): an ok
    result from a run on another tree matched a later not_run run's identical `VERDICT: ACCEPT <merge>`, so the
    result's reviewed_head (HEAD of the reviewed worktree, read by codex-review at the run's start) must be the landed
    merge's full sha. The result's role,
    actual_model, actual_effort and actual_sandbox must be the run the declared key class names, decided
    mechanically (`cross-family:codex-<tier>-<effort>` against tools/codex-review.py's ROLES, read-only; K180: the run's
    model FAMILY gpt-<version>-<tier> is compared, never a literal id, and the legacy `codex-gpt-<version>-<tier>-<effort>`
    is read as its tier and effort): `tier: ok`
    is relative to the role the run requested, so a swarm run's ok could key a sol-high subject. An unknown class is
    refused. The receipt records the reading and the file's sha256 (`- key run:`, `- key result sha256:`). Every
    refusal names the fix: pass codex-review's stdout for the one key run, or re-run the key until it reads ok.

Paths are read with `-c core.quotePath=false` (tools/kernel-subjects.py `git_argv`); a path git still quotes is
refused, never read as another.

K137: the project's constants -- the bar's runner and hosted-runner pattern, its two workflows and their name suffix,
tools/run-tools-bar.py's path, the receipts path -- come from tools/factory-config.json, read
once through tools/kernel-subjects.py (`KS.CONFIG`). A missing or malformed config is refused (exit 2), never
defaulted. K137 key round 1: the config NAMES; what decides credit is bound to the production artifact at the landed
merge. The REQUIRED list is read only from the script the tools-bar workflow's run step invokes (the configured path
must be that script), and a filter suite counts as run only if that script's own discovery glob finds it. The Codex
key class prefix is fleet kernel vocabulary in code, beside tools/codex-review.py's ROLES, never configured. The runner check reads each run's runner, as its log names it, against the
contract's env AND against the runner the config says the project's bar runs on (`bar.runner`, or a hosted runner
matching `bar.hosted_runner`): a config naming another runner refuses runs on this one.

It refuses (exit 2, nothing written) when the subject check (tools/kernel-subjects.py, receipt excepted) raises any
flag, when a declared manifest leaves out a bar-defining input, when a subject with no manifest has fewer green runs
at the landed merge than the contract's `passes:` count, when `--barred` is the merge or not an ancestor of the merge's second
parent, when fewer bar runs succeeded than the contract's `passes:` count, when no bar run is named, when a non-pending key class has no verdict
file, when a verdict file is given for a pending class, when the verdict file is a codex exec transcript, when a
Codex key class has no --key-result or any other class has one, when that result is missing, unparseable, not exactly
one JSON result line, UTF-16, a transcript, the verdict file itself, reads anything but ok, names another last
message, carries another last_message_sha256 than the verdict file's, reviewed another commit than the landed
merge, or is another role, model, effort or sandbox
than the key class names, and when a Codex key class names no tools/codex-review.py role (K140), and when the key's final line is not `VERDICT:
ACCEPT|REJECT|REFUSE` followed by the landed merge's full 40-hex sha. With `pending-cross-family` the receipt says the
subject is declared and receipted, NOT claimed closed: K6 is unmet.

    python tools/kernel-receipt.py --merge <sha> --barred <sha> --run tools-bar/37555813355=success@<sha>:ultra-magnus-cloudvore \
        [--run ...] \
        --ledger review/ledger-x.md [--key-verdict <final-message file> --key-result <codex-review stdout file>] \
        [--repo .] [--dry-run]
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import fnmatch
import re
import subprocess
import sys
from pathlib import Path

# Bus K154 review: the siblings load only from beside an ABSOLUTE __file__ that holds them. Run in-process by
# pin-runner (a pin without `with`), __file__ is the relative bus path, and with_name() would resolve it against the
# caller's cwd and execute an unpinned file from the caller's tree. Refuse instead (pin it as a group: --with).
_HERE = Path(__file__)
_MISSING = [n for n in ("kernel-subjects.py", "codex-review.py")
            if not (_HERE.is_absolute() and _HERE.with_name(n).is_file())]
if _MISSING:
    _MSG = (f"REFUSE kernel-receipt: {', '.join(_MISSING)} must sit beside this file ({__file__}); "
            "run it as a pinned group (pin-runner pin kernel-receipt --with kernel-subjects --with codex-review)")
    if __name__ == "__main__":
        print(_MSG, file=sys.stderr)
        sys.exit(2)
    raise ImportError(_MSG)
_SPEC = importlib.util.spec_from_file_location("cloudvore_kernel_subjects_for_receipt",
                                               Path(__file__).with_name("kernel-subjects.py"))
KS = importlib.util.module_from_spec(_SPEC)
try:
    _SPEC.loader.exec_module(KS)
except ValueError as _exc:                  # KS.ConfigError: tools/factory-config.json is missing or malformed (K137)
    if __name__ == "__main__":
        print(f"REFUSE kernel-receipt: {_exc}", file=sys.stderr)
        sys.exit(2)
    raise
_BAR = KS.CONFIG["bar"]
# K140 round 1: the key class decides the codex-review role mechanically, from codex-review's own ROLES and SANDBOX.
_CR_SPEC = importlib.util.spec_from_file_location("cloudvore_codex_review_for_receipt",
                                                  Path(__file__).with_name("codex-review.py"))
CR = importlib.util.module_from_spec(_CR_SPEC)
_CR_SPEC.loader.exec_module(CR)
# K137 key round 1 (finding 3): fleet kernel vocabulary, not project configuration. A configured prefix let a config
# reclassify cross-family:codex-gpt-6-sol-high as non-Codex and skip the K140 --key-result checks.
CODEX_CLASS = "cross-family:codex"
# K180 (R16.5): a Codex key class names a TIER and an effort, `cross-family:codex-<tier>-<effort>`; checks compare the run's
# model FAMILY (gpt-<version>-<tier>), never a literal id. The legacy literal class `codex-gpt-<version>-<tier>-<effort>`
# is read as its tier and effort, so every subject declared before K180 keeps its credit.
CODEX_KEY = re.compile(re.escape(CODEX_CLASS) + r"-(?:gpt-(\d+(?:\.\d+)*)-)?([a-z]+)-([a-z]+)", re.A)
MODEL_FAMILY = re.compile(r"gpt-(\d+(?:\.\d+)*)-([a-z]+)", re.A)

KEY_VERDICT = re.compile(r"VERDICT: (ACCEPT|REJECT|REFUSE) ([0-9a-f]{40})(?: (\S.*))?", re.A)
CODEX_BANNER = re.compile(r"OpenAI Codex v\S+")          # tools/codex-review.py `_BANNER_RE`
CODEX_SEPARATOR = "--------"
# K120 round 1: ONE runner-name domain for the run form and the env's declaration. Words of [0-9A-Za-z._-] joined by
# single spaces, because a hosted runner logs `Runner name: 'GitHub Actions 7'`; an env capture that stopped at the
# first space declared 'GitHub' and refused every run on the runner it named (seat repro at 27768313c).
RUNNER_WORDS = KS.RUNNER_WORDS
# K124 round 1 (seat A): a run id is the GitHub run's number, ASCII digits; it is compared by value, so `1` and `01`
# (one run) are one run, never two passes. K124 round 3 (the K6 key's REJECT of 6576d42): the run also names its
# WORKFLOW by file stem (`tools-bar`, `product-bar`); without it, three green product-bar runs met the passes of a
# subject whose filter runs only in the tools bar.
RUN = re.compile(r"^([a-z0-9][a-z0-9-]*)/([0-9]+)=([a-z_]+)@([0-9a-f]{12,40}):(" + RUNNER_WORDS + r")$")
OLD_RUN = re.compile(r"^[0-9A-Za-z._-]+=[a-z_]+@")           # the pre-round-3 form, which names no workflow
RUNNER_NAME = re.compile(r"\bRunner name ([^),;\n]*)")      # up to `)`, `;`, `,` or the end of the line
RUNNER_DOMAIN = re.compile(r"^" + RUNNER_WORDS + r"$")
RUN_FORM = ("`<workflow>/<id>=<conclusion>@<sha>:<runner name>` (the workflow's file stem as `gh run view <id>` names "
            "it, e.g. tools-bar; the run's numeric id; 12-40 hex of the commit it tested; the runner from its log)")
PASSES = re.compile(r"^passes: (\d+)\b", re.M)
PENDING = "pending-cross-family"
# K124: the bar-defining inputs a declared manifest must name. A workflow is named in `bar:` by its file
# (`.github/workflows/<name>.yml`) or by its name ending `-bar` (the default bar says "product-bar and tools-bar"); the
# `filter:` suite by a repository path with an extension (`tools/kernel-receipt.tests.py`).
WORKFLOW_PATH = re.compile(r"(?<![\w./-])\.github/workflows/[\w.-]+\.ya?ml(?![\w/-])")
# Round 1 (seat B): the lookahead once refused any following `.`, so a sentence ending "... and tools-bar." named no
# tools-bar workflow. A dot ends the word unless a word character follows it (`tools-bar.yaml2` is another name).
WORKFLOW_NAME = re.compile(r"(?<![\w./-])([a-z0-9][a-z0-9-]*" + re.escape(_BAR["workflow_suffix"])
                           + r")(?![\w/-]|\.\w)")
SUITE_PATH = re.compile(r"(?<![\w./-])((?:[\w.-]+/)+[\w-][\w.-]*\.[A-Za-z0-9]+)(?![\w/-])")
RUN_TOOLS_BAR = KS.CONFIG["paths"]["tools_bar_runner"]
BAR_INPUT_KINDS = f"the workflows the contract's `bar:` names, {RUN_TOOLS_BAR}, the `filter:` suite"
# K137: the runner the project's bar runs on (CI_RUNS_ON's self-hosted runner), or a hosted runner by its log name.
PROJECT_RUNNER = _BAR["runner"]
HOSTED_RUNNER = re.compile(_BAR["hosted_runner"])
DEFAULT_RULE = "default (code@r10: the git tree OID of the commit as delivered, after the merge); no manifest declared"
NOT_COUNTED = "not counted: the default identity counts runs at the landed merge only"


class Refused(Exception):
    pass


def is_codex_transcript(lines: list[str]) -> bool:
    """True when the file holds a `codex exec` transcript: a line `OpenAI Codex v<version>` followed by the line
    `--------` (tools/codex-review.py `_BANNER_RE`). Checked ANYWHERE in the file, not only at its first line:
    codex-review.py writes combined stdout and stderr, so a warning printed before the banner must not turn a
    transcript back into a "final message" whose last line could be the echoed prompt's tail."""
    stripped = [l.strip().lstrip("\ufeff") for l in lines]
    return any(CODEX_BANNER.fullmatch(stripped[i]) and stripped[i + 1] == CODEX_SEPARATOR
               for i in range(len(stripped) - 1))


WHITESPACE = " \t\r"                                 # the only characters stripped from the verdict line


def key_verdict_line(text: str, merge: str, where: object) -> tuple[str, str]:
    """(the verdict word, the verdict line): the LAST non-blank line of the file, which is the key's final message
    and must be exactly `VERDICT: ACCEPT|REJECT|REFUSE <the full landed merge sha>` (ASCII; text after the sha only
    for REFUSE) once ASCII spaces, tabs and CR are stripped, and nothing else. No earlier line is ever
    consulted. A `codex exec` transcript is refused outright: pass the final-message file (`codex exec -o`).

    K118 history: the FIRST `VERDICT:` line was the echoed template (K115's key output: ACCEPT at line 39, REJECT at
    2829). Round 1: a strict line filter skipped a final bold/lowercase/indented verdict and fell back to an earlier
    strict ACCEPT. Round 2: a loose `verdict:` filter did the same for a heading, bullet, `VERDICT :`, `Verdict -` or a
    lookalike colon. Revision 3 read the end of the transcript's last `codex` message; round 3 and the K6 key's REJECT
    of bee1842 found that the turn marks (`codex`, `exec`, `thinking`, `user`, `tokens used`) are ordinary lines a
    prompt or an answer can contain: a bare `codex` line in a crafted prompt became the answer (a false ACCEPT), and a
    standalone `exec` line in a real answer refused it. Revision 4 parses no transcript (K96 parks a refused packet
    as key unavailable). Revisions 3 and 5 stripped a closing code fence after the verdict; the K6 key's REJECTs of
    cda59bc (a stray or info-string fence) and 64a0393 (an indented code line taken for an opener) were false
    ACCEPTs. Revision 6 strips no fence: a fenced verdict is refused (the key is re-run), never green. Revision 7
    (the K6 key's REJECT of 7398b6a): `bare()` stripped markdown marker characters from both ends, so
    `VERDICT: ACCEPT <sha>` followed by any of # * _ - + ` > read ACCEPT, as did a fence info string
    "```VERDICT: ACCEPT <sha>". No marker is stripped: a wrapped, quoted, bulleted or numbered verdict is refused."""
    lines = text.split("\n")
    if is_codex_transcript(lines):
        raise Refused(f"{where} is a codex exec transcript, which is not a key verdict: pass the final-message file "
                      f"(`codex exec -o <file>`), which holds only the key's final message (K118 revision 4)")
    body = [l.strip(WHITESPACE) for l in lines if l.strip(WHITESPACE)]
    if not body:
        raise Refused(f"{where} has no final line from the key (the file is empty)")
    line = body[-1]
    m = KEY_VERDICT.fullmatch(line)
    if not m or (m.group(3) is not None and m.group(1) != "REFUSE"):
        raise Refused(f"{where}'s final line is not `VERDICT: ACCEPT|REJECT|REFUSE <full merge sha>` (text after the "
                      f"sha only for REFUSE): {ascii(line)}")
    if m.group(2) != merge:
        raise Refused(f"{where} does not name the landed merge {merge} on its final line (it names {m.group(2)})")
    return m.group(1), line


KEY_RESULT_FIELDS = ("tier", "exit", "last_message", "last_message_ok", "last_message_sha256", "sandbox_failure",
                     "role", "actual_model", "actual_effort", "actual_sandbox", "reviewed_head")


def is_codex_key(key: str) -> bool:
    """K140 round 2: --key-result and its checks apply to Codex key classes only; tools/kernel-subjects.py also
    accepts cross-family:*, ci-runner:* and human:* keys, which keep the verdict file alone."""
    return key == CODEX_CLASS or key.startswith(CODEX_CLASS + "-")


def key_role(key: str) -> tuple[tuple[str, ...], str, str, str]:
    """K140 round 1 (the K6 key's finding 2): `tier: ok` is relative to the role the run requested, so the declared key
    class names the run it needs: `cross-family:codex-<tier>-<effort>` (or the legacy literal
    `cross-family:codex-gpt-<version>-<tier>-<effort>`, read as its tier and effort), matched against
    tools/codex-review.py's ROLES, in its read-only SANDBOX. (roles, tier, effort, sandbox): `roles` are the ROLES that
    name that tier and effort (several roles may share one); any other class is unknown and refused."""
    m = CODEX_KEY.fullmatch(key)
    roles = tuple(r for r, pair in sorted(CR.ROLES.items()) if m and pair == (m.group(2), m.group(3)))
    if not roles:
        known = ", ".join(sorted({f"{CODEX_CLASS}-{t}-{ef}" for t, ef in CR.ROLES.values()}))
        raise Refused(f"the key class {key} names no tools/codex-review.py role (one of: {known}, or the legacy "
                      f"{CODEX_CLASS}-gpt-<version>-<tier>-<effort> of the same tiers): declare the class of the "
                      "codex-review run that keys this subject")
    tier, effort = CR.ROLES[roles[0]]
    return roles, tier, effort, CR.SANDBOX


def key_run_reading(want: tuple[tuple[str, ...], str, str, str], res: dict) -> str:
    resolved = f"resolved {res['actual_model']}"
    selector = res.get("model_requested")
    if isinstance(selector, str):                       # R16.2: the receipt records the selector AND the resolved model
        resolved += f"; selector {selector}"
    return (f"tier ok, exit 0, last_message_ok true, sandbox_failure null; role {res['role']}, model family "
            f"gpt-<version>-{want[1]} ({resolved}), effort {want[2]}, sandbox {want[3]} (the key class); its last "
            "message is the key verdict file and last_message_sha256 is that file's; reviewed_head is the landed merge "
            "(tools/codex-review.py's result line)")


def key_result_reading(raw: bytes, result: Path, verdict: Path, verdict_sha: str,
                       want: tuple[tuple[str, ...], str, str, str], merge: str) -> dict:
    """K140: refuse unless `raw` (tools/codex-review.py's stdout for the key run) holds exactly one JSON result line
    reading ok -- the conditions under which codex-review exits 0 -- whose last_message is the `verdict` file, whose
    last_message_sha256 is `verdict_sha` (the verdict file's bytes), and whose role, model family, effort and sandbox are
    `want`, the run the declared key class names (round 1; K180: the model's FAMILY gpt-<version>-<tier>, never a
    literal id). Returns the result line."""
    try:
        if os.path.samefile(result, verdict):
            raise Refused(f"--key-result is the --key-verdict file ({verdict}); pass the file holding tools/codex-review.py's "
                          "stdout for the key run as --key-result")
    except OSError:
        pass                                   # a missing result file is refused when it is read
    if raw.startswith((b"\xff\xfe", b"\xfe\xff")) or b"\x00" in raw:
        raise Refused(f"{result} is UTF-16 (a byte-order mark or NUL bytes), not UTF-8: a PowerShell 5.1 `>` redirect "
                      "writes UTF-16; save codex-review's stdout as UTF-8 (`| Out-File -Encoding utf8`, or `>` under "
                      "bash or PowerShell 7) and pass that file")
    lines = raw.decode("utf-8", "replace").splitlines()
    if is_codex_transcript(lines):
        raise Refused(f"{result} is a codex exec transcript, which is not a key verdict: pass the final-message file "
                      f"(`codex exec -o <file>`) as --key-verdict and codex-review's stdout as --key-result")
    found = []
    for n, line in enumerate(lines, 1):
        bare = line.strip().lstrip("\ufeff")
        if not bare.startswith("{"):
            continue
        try:
            obj = json.loads(bare)
        except ValueError:
            obj = None
        if not isinstance(obj, dict):
            raise Refused(f"{result} line {n} starts with '{{' but is not a JSON object (the result is unparseable): pass "
                          "tools/codex-review.py's stdout for the key run unedited")
        found.append(obj)
    if not found:
        raise Refused(f"{result} holds no tools/codex-review.py result line (a JSON object): pass the file holding "
                      "codex-review's stdout for the key run")
    if len(found) > 1:
        raise Refused(f"{result} holds {len(found)} result lines; pass a file holding the result of the one key run")
    res = found[0]
    missing = [f for f in KEY_RESULT_FIELDS if f not in res]
    if missing:
        raise Refused(f"{result} lacks {', '.join(missing)}: not a result of the current tools/codex-review.py "
                      "(K135, K140); re-run the key with the current tools/codex-review.py")
    if res["tier"] != "ok":
        raise Refused(f"the key run read tier {res['tier']!r}, not 'ok' (tools/codex-review.py, {result}): its "
                      "verdict is not credited, whatever the final message says; re-run the key until it reads ok")
    if type(res["exit"]) is not int or res["exit"] != 0:
        raise Refused(f"in the key run codex exited {res['exit']!r}, not 0 ({result}); re-run the key until it reads ok")
    if res["last_message_ok"] is not True:
        raise Refused(f"the key run's last_message_ok is {res['last_message_ok']!r}, not true ({result}); re-run the key "
                      "until it writes its final message")
    if res["sandbox_failure"] is not None:
        raise Refused(f"the key run's sandbox_failure is {res['sandbox_failure']!r}, not null: the sandbox failed "
                      f"and the key read nothing ({result}); re-run the key until it reads ok")
    roles, tier, effort, sandbox = want
    rerun = f"re-run the key as tools/codex-review.py --role {roles[0]}"
    if res["role"] not in roles:
        raise Refused(f"the key run's role {res['role']!r} is not one of {', '.join(roles)}, which the declared key "
                      f"class names ({result}): `tier: ok` is relative to the role the run requested; {rerun}")
    seen = res["actual_model"]
    family = MODEL_FAMILY.fullmatch(seen) if isinstance(seen, str) else None
    if family is None or family.group(2) != tier:
        raise Refused(f"the key run's model {seen!r} is not in the family gpt-<version>-{tier}, which the declared key "
                      f"class names ({result}): `tier: ok` is relative to the role the run requested; {rerun}")
    for field, value in (("effort", effort), ("sandbox", sandbox)):
        seen = res["actual_" + field]
        if seen != value:
            raise Refused(f"the key run's {field} {seen!r} is not {value!r}, which the declared key class names "
                          f"({result}): `tier: ok` is relative to the role the run requested; {rerun}")
    named = res["last_message"]
    if not isinstance(named, str) or not os.path.isabs(named):
        raise Refused(f"the key run's last_message {named!r} is not an absolute path ({result}); pass the result of the "
                      "run whose final message is --key-verdict")
    try:
        same = os.path.samefile(named, verdict)
    except OSError:
        raise Refused(f"the key run's last_message {named} names no file; pass the result of the run whose final "
                      "message is --key-verdict") from None
    if not same:
        raise Refused(f"the key run's last_message {named} is not the key verdict file {verdict}: one run's result "
                      "cannot vouch for another run's final message; pass that run's own result as --key-result")
    if res["last_message_sha256"] != verdict_sha:
        raise Refused(f"the key run's last_message_sha256 {res['last_message_sha256']!r} is not the key verdict file's "
                      f"({verdict_sha}; {result}): the result is from another run, or the file changed after the run; "
                      "pass that run's own result, or re-run the key")
    if res["reviewed_head"] != merge:            # K140 round 2: equal bytes are not the same run
        raise Refused(f"the key run's reviewed_head {res['reviewed_head']!r} is not the landed merge {merge} ({result}): "
                      "equal final-message bytes are not the same run; re-run the key with --cd at the landing merge")
    return res


def derived_manifest(repo: Path, merge: str, barred: str) -> list[str]:
    """The paths the landing changes on master, UNION the paths the barred candidate changed from where it left
    master. The union matters: a packet path that master overwrote after the bar lands with master's bytes, drops
    out of the landing's own diff, and a manifest of the landing's diff alone would read MATCH over reviewed bytes
    that never landed."""
    landed = KS.listed_paths(KS.git(repo, "diff", "--name-only", "--no-renames", f"{merge}^1", merge, "--"))
    fork = KS.git(repo, "merge-base", barred, f"{merge}^1").strip()
    reviewed = KS.listed_paths(KS.git(repo, "diff", "--name-only", "--no-renames", fork, barred, "--"))
    return sorted(set(landed) | set(reviewed))


def blob(repo: Path, commit: str, path: str) -> str:
    """The path's blob OID at `commit`, or `absent` -- a stated negative: `ls-tree` lists nothing for no such path."""
    listed = KS.git(repo, "ls-tree", commit, "--", path).strip()
    if not listed:
        return "absent"
    meta, _tab, name = listed.partition("\t")
    if name != path or len(meta.split()) != 3:
        raise Refused(f"git listed {listed!r} for {path!r} at {commit[:9]}")
    return meta.split()[2]


def identity(repo: Path, commit: str, paths: list[str]) -> str:
    """K3 under the path-manifest rule: the manifest digest, then each path's blob OID in path order."""
    manifest_digest = hashlib.sha256(("\n".join(paths) + "\n").encode("utf-8")).hexdigest()
    components = [manifest_digest] + [blob(repo, commit, p) for p in paths]
    return "sha256:" + hashlib.sha256("\n".join(components).encode("utf-8")).hexdigest()


def tree(repo: Path, commit: str) -> str:
    return KS.git(repo, "rev-parse", "--verify", f"{commit}^{{tree}}").strip()


def is_ancestor(repo: Path, a: str, b: str) -> bool:
    """`merge-base --is-ancestor`: exit 0 is yes and 1 is no; anything else is no answer, never a no."""
    p = subprocess.run(KS.git_argv(repo, "merge-base", "--is-ancestor", a, b), capture_output=True, env=KS._env(),
                       timeout=60)
    if p.returncode in (0, 1) and not p.stderr.strip():
        return p.returncode == 0
    raise KS.GitFailed(f"git merge-base --is-ancestor: exit {p.returncode}")


def passes_required(contract_text: str) -> int:
    """The count the contract's `passes:` line starts with (`3 identical green passes ...`)."""
    m = PASSES.search(contract_text or "")
    if not m:
        raise Refused("the contract's `passes:` line names no count of passes")
    n = int(m.group(1))
    if n < 1:
        raise Refused("the contract's `passes:` line names no pass at all")
    return n


def parse_runs(runs: list[str]) -> list[tuple[str, str, str, str]]:
    """(`<workflow>/<id>`, conclusion, sha as given, runner). K95: each run is bound to the commit it tested (12 to 40
    hex of it). K120: and to the runner it ran on; a run that names no runner is refused, never assumed hosted. K124
    round 3: and to its workflow, as the caller read it (`gh run view <id>`); this tool contacts nothing. A GitHub run
    id is unique across workflows, so a duplicate is refused by the id's value whatever workflow each names."""
    out = []
    for r in runs or []:
        m = RUN.match(r)
        if not m:
            if OLD_RUN.match(r):
                raise Refused(f"bar run {r!r} names no workflow; since K124 round 3 a bar run is {RUN_FORM}, e.g. "
                              f"tools-bar/{r}")
            raise Refused(f"a bar run is {RUN_FORM}, not {r!r}")
        num = str(int(m.group(2)))                     # by value: `01` is run 1
        if any(i.split("/", 1)[1] == num for i, _c, _s, _n in out):
            raise Refused(f"bar run {num} is named more than once: each pass of the bar is its own run")
        out.append((f"{m.group(1)}/{num}", m.group(3), m.group(4), m.group(5)))
    if not out:
        raise Refused(f"no run of the bar was named (--run {RUN_FORM}, once per run)")
    return out


def declared_runners(contract_text: str) -> list[str]:
    """K120: the runner names the contract's `env:` line declares (`Runner name <name>`). None is a refusal: an env
    that names no runner cannot be checked against where the runs ran (before K120 every default env said `hosted
    windows-latest` while CI_RUNS_ON sent the bars to the self-hosted ultra-magnus runner)."""
    envs = [l for l in (contract_text or "").splitlines() if l.startswith("env:")]
    if len(envs) > 1:                                  # round 1 note 3: never read the first of two and ignore one
        raise Refused(f"the contract declares `env:` {len(envs)} times; one env, one runner declaration")
    names = []
    for raw in RUNNER_NAME.findall(envs[0] if envs else ""):
        name = raw.strip().rstrip(".").strip()         # `(Runner name X)`, `Runner name X;`, `... Runner name X.`
        if not RUNNER_DOMAIN.match(name):
            raise Refused(f"the contract's `env:` declares runner {raw.strip()!r}, which is not a runner name a run "
                          "can carry (words of [0-9A-Za-z._-] joined by single spaces)")
        names.append(name)
    if not names:
        raise Refused("the contract's `env:` names no runner (`Runner name <name>`, as the bar's run log prints it): "
                      "the receipt cannot check that the runs ran where the contract says")
    return names


def project_runner(name: str) -> bool:
    """K137: a runner the project's bar runs on, by the config: `bar.runner` exactly, or a hosted runner's log name
    matching `bar.hosted_runner` in full (CI_RUNS_ON unset sends the bars to windows-latest)."""
    return name == PROJECT_RUNNER or HOSTED_RUNNER.fullmatch(name) is not None


def check_runners(runs: list[tuple[str, str, str, str]], allowed: list[str]) -> None:
    """K120: every run ran on a runner the env declares, matched by exact name. K137: and on a runner the project's
    bar runs on (`project_runner`); each run's own runner, as its log names it, is what both compare."""
    for i, _c, _s, n in runs:
        if n not in allowed:
            raise Refused(f"bar run {i} ran on {n!r}; the contract's env declares runner "
                          + " or ".join(repr(a) for a in allowed))
        if not project_runner(n):
            raise Refused(f"bar run {i} ran on {n!r}, which is not a runner this project's bar runs on "
                          f"({KS.CONFIG_NAME} bar.runner {PROJECT_RUNNER!r}, or a hosted runner matching bar.hosted_runner "
                          f"{HOSTED_RUNNER.pattern!r})")


def wf_of(run_id: str) -> str:
    """The workflow a parsed run names (`tools-bar/123` -> `tools-bar`)."""
    return run_id.split("/", 1)[0]


def bind_runs(runs: list[tuple[str, str, str, str]], barred: str, merge: str) -> list[tuple[str, str, str, str]]:
    """(id, conclusion, `barred`|`landed`, runner). A run that tested any other commit is not evidence for this
    subject."""
    out = []
    for i, c, sha, n in runs:
        if merge.startswith(sha):
            out.append((i, c, "landed", n))
        elif barred.startswith(sha):
            out.append((i, c, "barred", n))
        else:
            raise Refused(f"bar run {i} tested {sha}, which is neither the barred commit {barred[:12]} nor the "
                          f"landed merge {merge[:12]}")
    return out


def range_touches(repo: Path, barred: str, merge: str, paths: list[str]) -> list[str]:
    """The commits in `<barred>..<merge>` that touch a declared path (code@r10: "the intervening range must touch no
    declared path"): every non-merge commit that changes one, and every merge whose RESOLUTION changed one against
    every parent (`diff-tree --cc`). `--full-history` is load-bearing: without it git follows a merge's TREESAME
    parent and prunes master's side (K95 revision 1). The merges are load-bearing too: with non-merge commits only,
    an input changed in one merge's conflict resolution and restored in a later one left the range empty, and the
    receipt read MATCH and creditable (K95 round 1: Codex finding 2 and the Claude seat's probe 1b)."""
    touched = KS.git(repo, "--literal-pathspecs", "rev-list", "--full-history", "--no-merges", f"{barred}..{merge}",
                     "--", *paths).split()
    for m in KS.git(repo, "rev-list", "--merges", f"{barred}..{merge}").split():
        if KS.git(repo, "--literal-pathspecs", "diff-tree", "--no-commit-id", "--cc", "-r", "--name-only", m,
                  "--", *paths).strip():
            touched.append(m)
    return touched


def contract_value(contract_text: str, key: str) -> str:
    """The value of the contract's `key:` line ('' when there is none; parse_block refuses a duplicate key)."""
    for l in (contract_text or "").splitlines():
        if l.startswith(f"{key}: "):
            return l[len(key) + 2:]
    return ""


def bar_inputs(contract_text: str) -> list[str]:
    """K124 (the K121 adjudicator C rule, its mechanically checkable part): the inputs that define the bar, which a
    declared manifest must name: each workflow the contract's `bar:` names, tools/run-tools-bar.py, and each
    repository path the `filter:` names (its suite). A bar naming no workflow, or a filter naming no path, is refused:
    the receipt cannot say what such a manifest must hold, and the default identity (no manifest) needs neither."""
    bar = contract_value(contract_text, "bar")
    workflows = set(WORKFLOW_PATH.findall(bar)) | {f".github/workflows/{n}.yml" for n in WORKFLOW_NAME.findall(bar)}
    if not workflows:
        raise Refused("the contract's `bar:` names no workflow (`.github/workflows/<file>.yml` or `<name>-bar`): a "
                      "declared manifest must name the bar's workflows; or declare no manifest (the default identity)")
    suites = sorted(set(SUITE_PATH.findall(contract_value(contract_text, "filter"))))
    if not suites:
        raise Refused("the contract's `filter:` names no repository path (its suite): a declared manifest must name "
                      "the filter's suite; or declare no manifest (the default identity)")
    out = sorted(workflows) + [RUN_TOOLS_BAR]
    return out + [s for s in suites if s not in out]


TOOLS_BAR, PRODUCT_BAR = _BAR["tools_workflow"], _BAR["product_workflow"]
# The K6 key's REJECT of efdec35: what `dotnet test --filter` accepts, recognised conservatively: Property, operator,
# value, terms joined by | or & (no parentheses, no spaces).
_DOTNET_TERM = r"(?:FullyQualifiedName|Name|ClassName|Category|TestCategory|Priority)(?:=|!=|~|!~)[A-Za-z0-9_.+-]+"
DOTNET_FILTER = re.compile(_DOTNET_TERM + r"(?:[|&]" + _DOTNET_TERM + r")*")
DOTNET_FORM = ("Property=|!=|~|!~Value joined by | or &; properties FullyQualifiedName, Name, ClassName, Category, "
               "TestCategory, Priority")
# Integrator ruling after K137 key round 1: product-suite membership is the receipt's rule, in code as before K137,
# never configured. A configured prefix (review/) credited review/never.tests.py on product-bar runs (the efdec35
# shape). Binding it to the solution's real test-project layout is portability step 2 (row K153).
PRODUCT_PREFIX = "tests/"
# K137 key round 1 (finding 1): the tools bar's discovery is the runner's own glob, read from the runner at the merge:
# `glob.glob(os.path.join(repo, "<dir>", "<pattern>"))`, its string parts joined by `/`.
DISCOVERY = re.compile(r'glob\.glob\(os\.path\.join\(repo, ((?:"[^"\n]*", )*"[^"\n]*")\)\)')
# K137 key round 1 (finding 2): the python scripts a workflow's run steps invoke (`python <path>.py`)
# K137 key round 2 (integrator closure 3): the bar step's one command: the runner, then flags and plain values only
BAR_ARG = r'(?:-{1,2}[A-Za-z0-9][A-Za-z0-9-]*(?:=[A-Za-z0-9._/-]+)?|[A-Za-z0-9._/-]+|"\$[A-Za-z_][A-Za-z0-9_]*")'
BAR_COMMAND = re.compile(r"python3?[ \t]+" + re.escape(RUN_TOOLS_BAR) + r"(?:[ \t]+" + BAR_ARG + r")*[ \t]*")
RUN_STEP_SCRIPT = re.compile(r"(?m)^[ \t]*(?:-[ \t]+)?(?:run:[ \t]*)?python3?[ \t]+([A-Za-z0-9._/-]+\.py)(?![\w.-])")
REQUIRED_BLOCK = re.compile(r"^REQUIRED: set\[str\] = \{\n(.*?)^\}", re.S | re.M)
REQUIRED_ENTRY = re.compile(r'^\s*"([^"\n]+)",')


def bar_workflows(contract_text: str) -> list[str]:
    """K124 round 3: the workflows the contract's `bar:` names, by file stem (`tools-bar`, `product-bar`). None is a
    refusal on both identity paths: a run's workflow is checked against them."""
    bar = contract_value(contract_text, "bar")
    stems = {re.sub(r"\.ya?ml$", "", p.rsplit("/", 1)[1]) for p in WORKFLOW_PATH.findall(bar)}
    stems |= set(WORKFLOW_NAME.findall(bar))
    if not stems:
        raise Refused("the contract's `bar:` names no workflow (`.github/workflows/<file>.yml` or `<name>-bar`): the "
                      "receipt cannot say which runs are the bar")
    return sorted(stems)


def required_tools_suites(repo: Path, commit: str) -> set[str]:
    """The suite names tools/run-tools-bar.py's REQUIRED allowlist holds at `commit` (the tools bar's required tier,
    the tier the contract's bar names). Read as text: one string literal per line inside `REQUIRED: set[str] = {`."""
    text = KS.path_at(repo, commit, RUN_TOOLS_BAR)
    m = REQUIRED_BLOCK.search(text or "")
    if not m:
        raise Refused(f"{RUN_TOOLS_BAR} at {commit[:9]} holds no `REQUIRED: set[str] = {{` block: the receipt cannot "
                      "decide whether the tools bar runs the filter")
    return {e.group(1) for e in map(REQUIRED_ENTRY.match, m.group(1).split("\n")) if e}


def tools_bar_runner_bound(repo: Path, commit: str) -> None:
    """K137 key round 1 (finding 2): the configured runner path must be the one script the tools-bar workflow at
    `commit` invokes; otherwise the REQUIRED the receipt would read is not the bar's."""
    wf = f".github/workflows/{TOOLS_BAR}.yml"
    text = KS.path_at(repo, commit, wf)
    if text is None:
        raise Refused(f"{wf} is absent at {commit[:9]}: the receipt cannot bind {RUN_TOOLS_BAR} to the tools bar")
    scripts = sorted(set(RUN_STEP_SCRIPT.findall(text)))
    if scripts != [RUN_TOOLS_BAR]:
        raise Refused(f"{wf} at {commit[:9]} runs {', '.join(scripts) or 'no python script'}, not {RUN_TOOLS_BAR}: "
                      f"the receipt reads REQUIRED only from the script the tools bar runs ({KS.CONFIG_NAME} "
                      "paths.tools_bar_runner must name it)")
    # K137 key round 2 (integrator closure 3): a textual line is no binding (`if false; then` before it). The one step
    # naming the runner has a run block whose only command, blank lines and comments aside, invokes it with flags.
    steps = [s for s in workflow_steps(text) if any(RUN_TOOLS_BAR in line for line in s)]
    commands = run_commands(steps[0]) if len(steps) == 1 else None
    if commands is None or len(commands) != 1 or not bar_command(commands[0]):
        raise Refused(f"{wf} at {commit[:9]}: the step that runs {RUN_TOOLS_BAR} must have a `run:` block whose "
                      f"invocation of it, optionally with flags, must be its only command; found "
                      f"{len(steps)} step(s) naming it and the commands {commands!r}")
    # K137 key round 2, finding 3 (integrator ruling): outside the run block, nothing may skip the bar step or let it
    # fail green. The step and its job carry no `if:` and no `continue-on-error` but false; the step's directory is
    # the repo root; the job is the bar job, the one named as the workflow's stem.
    refusal = f"{wf} at {commit[:9]}: the bar step that runs {RUN_TOOLS_BAR}"
    jobs = [(name, lines) for name, lines in workflow_jobs(text) if any(RUN_TOOLS_BAR in ln for ln in lines)]
    if len(jobs) != 1 or jobs[0][0] != TOOLS_BAR:
        raise Refused(f"{refusal} is not in the bar job {TOOLS_BAR} (found in {[n for n, _l in jobs]!r})")
    for where, keys in ((f"its job {TOOLS_BAR}", top_keys(jobs[0][1])), ("the step", step_keys(steps[0]))):
        if "if" in keys:
            raise Refused(f"{refusal}: {where} carries `if:` ({keys.get('if')!r}), so the bar may not run")
        if keys.get("continue-on-error", "false").lower() != "false":
            raise Refused(f"{refusal}: {where} carries `continue-on-error: {keys['continue-on-error']}`, so a red "
                          "bar can read green")
    directory = step_keys(steps[0]).get("working-directory")
    if directory is not None and directory not in (".", "./"):
        raise Refused(f"{refusal}: the step carries `working-directory: {directory}`, not the repository root")


def workflow_jobs(text: str) -> list[tuple[str, list[str]]]:
    """Each job under the workflow's top-level `jobs:` as (its id, its lines), whole-line `#` comments dropped."""
    lines = [ln for ln in text.split("\n") if not ln.strip().startswith("#")]
    start = next((n for n, ln in enumerate(lines) if re.match(r"^jobs:[ \t]*$", ln)), None)
    jobs, indent, cur = [], None, None
    if start is None:
        return jobs
    for ln in lines[start + 1:]:
        if not ln.strip():
            if cur is not None:
                cur[1].append(ln)
            continue
        depth = len(ln) - len(ln.lstrip(" "))
        if depth == 0:
            break
        indent = depth if indent is None else indent
        m = re.match(r"^ {%d}([A-Za-z0-9_-]+):[ \t]*$" % indent, ln) if depth == indent else None
        if m:
            cur = (m.group(1), [])
            jobs.append(cur)
        elif cur is not None:
            cur[1].append(ln)
    return jobs


def top_keys(lines: list[str]) -> dict[str, str]:
    """The `key: value` pairs at the shallowest indentation of a block (a job's or a step's own keys), values unquoted."""
    body = [ln for ln in lines if ln.strip()]
    if not body:
        return {}
    depth = min(len(ln) - len(ln.lstrip(" ")) for ln in body)
    keys = {}
    for ln in body:
        m = re.match(r"^ {%d}([A-Za-z0-9_-]+):[ \t]*(.*?)[ \t]*$" % depth, ln)
        if m:
            keys[m.group(1)] = m.group(2).strip("'\"")
    return keys


def step_keys(step: list[str]) -> dict[str, str]:
    """A steps-list item's own keys (its first line's `- ` marker read as indentation)."""
    first = step[0]
    return top_keys([" " * (len(first) - len(first.lstrip(" ")) + 2) + first.lstrip(" ")[2:]] + step[1:])


def workflow_steps(text: str) -> list[list[str]]:
    """Each `steps:` list item of a workflow as its lines (whole-line `#` comments dropped), the item's first line
    with its `- ` marker. A deliberately small reader: list items at one indentation under `steps:`."""
    lines = [ln for ln in text.split("\n") if not ln.strip().startswith("#")]
    steps, i = [], 0
    while i < len(lines):
        m = re.match(r"^( *)steps:[ \t]*$", lines[i])
        i += 1
        if not m:
            continue
        base, item, cur = len(m.group(1)), None, None
        while i < len(lines):
            ln = lines[i]
            if ln.strip():
                ind = len(ln) - len(ln.lstrip(" "))
                if ind <= base:
                    break
                if ln.lstrip(" ").startswith("- ") and (item is None or ind == item):
                    item, cur = ind, [ln]
                    steps.append(cur)
                    i += 1
                    continue
            if cur is not None:
                cur.append(ln)
            i += 1
    return steps


def run_commands(step: list[str]) -> list[str] | None:
    """The shell commands of a step's `run:` value: blank lines and `#` comments dropped, backslash continuations
    joined. None when the step has no `run:` key at its own indentation."""
    first = step[0]
    key_indent = len(first) - len(first.lstrip(" ")) + 2
    lines = [" " * key_indent + first.lstrip(" ")[2:]] + step[1:]
    for n, ln in enumerate(lines):
        m = re.match(r"^ {%d}run:[ \t]*(.*)$" % key_indent, ln)
        if not m:
            continue
        value = m.group(1).strip()
        if value in ("|", "|-", "|+", ">", ">-", ">+"):
            body = []
            for b in lines[n + 1:]:
                if b.strip() and len(b) - len(b.lstrip(" ")) <= key_indent:
                    break
                body.append(b.strip())
        else:
            body = [value]
        commands, pending = [], ""
        for b in body:
            if not b or b.startswith("#"):
                continue
            if b.endswith("\\"):
                pending += b[:-1].rstrip() + " "
                continue
            commands.append(pending + b)
            pending = ""
        if pending:
            commands.append(pending.rstrip())
        return commands
    return None


def bar_command(command: str) -> bool:
    """`python <runner> [flags]`: flags and their plain values only, no shell operator, no second command."""
    return BAR_COMMAND.fullmatch(command) is not None


def tools_bar_glob(repo: Path, commit: str) -> str | None:
    """K137 key round 1 (finding 1): the runner's discovery glob at `commit` (`tools/*.tests.py`), or None when the
    runner is absent there (then no path is a tools suite). A runner with no glob, or more than one, is refused."""
    text = KS.path_at(repo, commit, RUN_TOOLS_BAR)
    if text is None:
        return None
    found = DISCOVERY.findall(text)
    if len(found) != 1:
        raise Refused(f"{RUN_TOOLS_BAR} at {commit[:9]} holds {len(found)} discovery globs "
                      "(`glob.glob(os.path.join(repo, ...))`), not one: the receipt cannot say which suites it runs")
    return "/".join(re.findall(r'"([^"]*)"', found[0]))


def discovered(path: str, pattern: str) -> bool:
    """`path` is what glob.glob(`pattern`) finds, by the pattern's own segments: one fnmatch per `/` segment (so `*`
    never crosses a directory), case-sensitive (conservative), and a wildcard never matching a leading dot."""
    segs, pats = path.split("/"), pattern.split("/")
    return len(segs) == len(pats) and all(
        fnmatch.fnmatchcase(s, p) and (not s.startswith(".") or p.startswith(".")) for s, p in zip(segs, pats))


def filter_workflow(repo: Path, commit: str, contract_text: str, workflows: list[str]) -> tuple[str, str]:
    """K124 round 3 (the K6 key's REJECT of 6576d42): (the workflow that runs the contract's `filter:`, why). Decided
    mechanically and conservatively: a filter naming `tools/<name>.tests.py` suites runs in the tools bar, and only
    if every one is in run-tools-bar.py's REQUIRED at `commit` (the required tier runs nothing else) and its file is
    in `commit`'s tree; a filter that is a dotnet test filter expression naming no path, or names only paths under
    tests/ that exist at `commit`, runs in the product bar (efdec35 REJECT). Anything else -- a filter mixing tools/
    and other paths, a tools/ path the tools bar does not discover, a path outside tools/ and tests/, prose -- is
    refused, as is a workflow `bar:` does not name."""
    suites = sorted(set(SUITE_PATH.findall(contract_value(contract_text, "filter"))))
    if suites and KS.path_at(repo, commit, RUN_TOOLS_BAR) is not None:
        tools_bar_runner_bound(repo, commit)          # before anything is read from the configured runner path
    pattern = tools_bar_glob(repo, commit) if suites else None
    tools_dir = pattern.rsplit("/", 1)[0] + "/" if pattern and "/" in pattern else ""
    tools = [s for s in suites if pattern is not None and s.startswith(tools_dir)]
    if tools:
        if len(tools) != len(suites):
            raise Refused("the contract's `filter:` names tools/ suites and other paths: the receipt cannot decide "
                          "which one workflow runs it")
        names = []
        for s in tools:
            if not discovered(s, pattern):
                raise Refused(f"the contract's `filter:` names {s}, which {RUN_TOOLS_BAR} does not discover "
                              f"(it runs {pattern}): the receipt cannot decide which workflow runs it")
            names.append(s.rsplit("/", 1)[-1])
        required = required_tools_suites(repo, commit)
        missing = [n for n in names if n not in required]
        if missing:
            raise Refused(f"the filter's suite(s) {', '.join(missing)} are not in {RUN_TOOLS_BAR}'s REQUIRED at "
                          f"{commit[:9]}: the tools bar's required tier does not run them")
        # The K6 key's REJECT of efdec35: a name in REQUIRED is not proof the suite ran -- the tools bar runs the
        # REQUIRED names it discovers. The suite file must be in the tree the runs tested.
        absent = [s for s in tools if blob(repo, commit, s) == "absent"]
        if absent:
            raise Refused(f"the filter's suite {', '.join(absent)} is absent from the landed merge's tree "
                          f"({commit[:9]}): the tools bar cannot have run it")
        wf, why = TOOLS_BAR, f"{', '.join(tools)} in {RUN_TOOLS_BAR}'s REQUIRED at the landed merge"
    else:
        # The K6 key's REJECT of efdec35: any filter naming no tools/ path was taken to run in product-bar, so
        # `review/never.tests.py` was credited on product-bar runs (`dotnet test DropboxVault.sln`). Now only a
        # dotnet test filter expression naming no path, or paths that all exist under tests/ at the landed merge.
        text = contract_value(contract_text, "filter").strip()
        if suites:
            for s in suites:
                if not s.startswith(PRODUCT_PREFIX):
                    raise Refused(f"the contract's `filter:` names {s}, which is not under tests/: a product-bar "
                                  "filter is a dotnet test filter expression or paths under tests/")
                if blob(repo, commit, s) == "absent":
                    raise Refused(f"the filter's path {s} is absent from the landed merge's tree ({commit[:9]})")
            why = (f"{', '.join(suites)} under tests/ at the landed merge; the product bar builds and tests the "
                   "whole solution")
        elif DOTNET_FILTER.fullmatch(text):
            why = "a dotnet test filter expression"
        else:
            raise Refused(f"the contract's `filter:` {text!r} is not a dotnet test filter expression ({DOTNET_FORM}) "
                          "and names no repository path: the receipt cannot say the product bar runs it. A creditable "
                          "filter is one of: tools/<name>.tests.py suites in tools/run-tools-bar.py's REQUIRED "
                          "(run by tools-bar); paths under tests/ that exist at the landed merge (product-bar); or a "
                          "dotnet test filter expression such as `Category!=Integration` (product-bar). Prose is "
                          "never a filter")
        wf = PRODUCT_BAR
    if wf not in workflows:
        raise Refused(f"the filter runs in {wf} ({why}), which the contract's `bar:` does not name "
                      f"(it names {', '.join(workflows)})")
    return wf, why


def absent_everywhere(repo: Path, barred: str, merge: str, paths: list[str]) -> list[str]:
    """Declared paths that name nothing at either end. Such a path read `absent` twice, counted as an unchanged
    input and matched, so a misspelled input (wrong case) let a change to the real file through (round 1, probe 1g)."""
    return [p for p in paths if blob(repo, barred, p) == "absent" and blob(repo, merge, p) == "absent"]


# K166: the product bar prints, per pass and assembly, the test cases its Category!=Integration filter EXCLUDED, counted
# by discovery (tools/product-bar-results.py `excluded_line`). The receipt reads that line from the run's log, as
# `gh run view <id> --log` wrote it (each line prefixed by job, step and timestamp), and records the counts. A log
# from before K166 carries no such line and reads `excluded: not reported by this bar`; a line that names the bar's
# excluded marker but is not the bar's exact form is refused, never read as absent.
# Key round 1 (finding 3): the marker is LOOSE -- any spacing, any case, excluded or discovery -- so a near-miss
# spelling (`pass 1 excluded :`) is refused by the strict forms below instead of reading as "not reported".
EXCLUDED_MARK = re.compile(r"pass\s*\d+\s*(?:excluded|discovery)\s*:", re.I)
DISCOVERY_LINE = re.compile(r"(?:^|\s)pass ([1-9][0-9]*) discovery: discovered = included \+ excluded for each "
                            r"assembly; the excluded cases \(Category=Integration\) were listed, never executed; ")
EXCLUDED_LINE = re.compile(r"(?:^|\s)pass ([1-9][0-9]*) excluded: (DropboxVault\.App\.Tests|DropboxVault\.Core\.Tests) "
                           r"discovered=(\d+) included=(\d+) excluded=(\d+) executed=(\d+) passed=(\d+) failed=(\d+) "
                           r"skipped=(\d+) filter=Category=Integration commit=([0-9a-f]{40})$")
EXCLUDED_ASSEMBLIES = ("DropboxVault.App.Tests", "DropboxVault.Core.Tests")
NOT_REPORTED = "excluded: not reported by this bar"
BAR_LOG_FORM = "`<workflow>/<id>=<file>` (a run named by --run; the file `gh run view <id> --log` wrote)"


def excluded_counts(text: str, where: str) -> dict | None:
    """{'passes': n, 'commit': sha, 'counts': {assembly: (discovered, included, excluded)}} from a product-bar log, or
    None when the log carries no excluded line (a bar from before K166). Every pass must report both assemblies with
    identical counts, each closing discovered = included + excluded, all at one commit."""
    seen: dict[int, dict[str, tuple[int, int, int]]] = {}
    sentences: set[int] = set()
    commits = set()
    for raw in text.splitlines():
        line = raw.rstrip("\r")
        if not EXCLUDED_MARK.search(line):
            continue
        sentence = DISCOVERY_LINE.search(line)
        if sentence:
            sentences.add(int(sentence.group(1)))
            continue
        m = EXCLUDED_LINE.search(line)
        if not m:
            raise Refused(f"{where}: {line.strip()!r} is not the bar's excluded line (pass <n> excluded: <assembly> "
                          "discovered=.. included=.. excluded=.. executed=.. passed=.. failed=.. skipped=.. "
                          "filter=Category=Integration commit=<sha>) or the bar's discovery sentence")
        number, name = int(m.group(1)), m.group(2)
        d, i, e = (int(m.group(k)) for k in (3, 4, 5))
        if d != i + e:
            raise Refused(f"{where}: pass {number} {name}: discovered {d} != included {i} + excluded {e}")
        if name in seen.setdefault(number, {}):
            raise Refused(f"{where}: pass {number} reports {name} excluded twice")
        seen[number][name] = (d, i, e)
        commits.add(m.group(10))
    if sentences - set(seen):
        raise Refused(f"{where}: the bar's discovery sentence names pass(es) {sorted(sentences - set(seen))} with no "
                      "excluded lines: a K166 bar's log must carry them")
    if not seen:
        return None
    if sorted(seen) != list(range(1, len(seen) + 1)):
        raise Refused(f"{where}: the excluded lines name passes {sorted(seen)}, not 1..{len(seen)}")
    for number, got in sorted(seen.items()):
        if sorted(got) != list(EXCLUDED_ASSEMBLIES):
            raise Refused(f"{where}: pass {number} reports excluded counts for {sorted(got)}, not both of "
                          f"{', '.join(EXCLUDED_ASSEMBLIES)}")
        if got != seen[1]:
            raise Refused(f"{where}: the excluded counts of pass {number} differ from pass 1")
    if len(commits) != 1:
        raise Refused(f"{where}: the excluded lines name {len(commits)} commits")
    return {"passes": len(seen), "commit": commits.pop(), "counts": seen[1]}


def read_bar_logs(bar_logs: list[str], runs_read: list[tuple[str, str, str, str]]) -> dict[str, str]:
    """K166: {product-bar run id: its receipt line}, for every product-bar run named; a run with no --bar-log says so."""
    by_id = {i: s for i, _c, s, _n in runs_read}
    given: dict[str, Path] = {}
    for item in bar_logs or []:
        rid, sep, file = item.partition("=")
        m = re.fullmatch(r"([a-z0-9][a-z0-9-]*)/([0-9]+)", rid)
        if not sep or not file or not m:
            raise Refused(f"a bar log is {BAR_LOG_FORM}, not {item!r}")
        rid = f"{m.group(1)}/{int(m.group(2))}"
        if rid not in by_id:
            raise Refused(f"--bar-log names {rid}, which no --run names")
        if wf_of(rid) != PRODUCT_BAR:
            raise Refused(f"--bar-log names {rid}: only a {PRODUCT_BAR} run prints the excluded counts")
        if rid in given:
            raise Refused(f"--bar-log names {rid} twice")
        given[rid] = Path(file)
    out = {}
    for rid, sha in by_id.items():
        if wf_of(rid) != PRODUCT_BAR:
            continue
        if rid not in given:
            out[rid] = "excluded: not read (no --bar-log for this run)"
            continue
        text = given[rid].read_bytes().decode("utf-8", "replace")
        read = excluded_counts(text, f"--bar-log {rid}")
        if read is None:
            if sha not in text:
                raise Refused(f"--bar-log {rid} never names the commit {sha} the run tested: not that run's log")
            out[rid] = NOT_REPORTED
            continue
        if not read["commit"].startswith(sha):
            raise Refused(f"--bar-log {rid}: the excluded lines name commit {read['commit'][:12]}, but the run "
                          f"tested {sha}")
        c = read["counts"]
        out[rid] = ("excluded: " + ", ".join(f"{a} {c[a][2]}" for a in EXCLUDED_ASSEMBLIES)
                    + " (Category=Integration, discovery only, never executed; discovered "
                    + " and ".join(str(c[a][0]) for a in EXCLUDED_ASSEMBLIES)
                    + f" = included + excluded in each of {read['passes']} pass(es))")
    return out


def build(repo: Path, merge: str, barred: str, runs: list[str], ledger: str,
          key_verdict: Path | None, key_result: Path | None = None,
          bar_logs: list[str] | None = None) -> tuple[str, str]:
    runs_read = parse_runs(runs)
    excluded = read_bar_logs(bar_logs or [], runs_read)
    merge, barred = KS.rev(repo, merge), KS.rev(repo, barred)
    parents = KS.git(repo, "log", "-1", "--format=%P", merge).split()
    if len(parents) != 2:
        raise Refused(f"{merge[:9]} is not a two-parent landing merge")
    # Round 2: --barred was taken on trust; the merge itself, passed as the barred commit, read MATCH over bytes
    # nobody barred. It must be the branch's own history: an ancestor of (or equal to) merge^2, never the merge.
    if barred == merge:
        raise Refused("--barred is the landing merge itself; name the commit the bar ran at")
    if not is_ancestor(repo, barred, parents[1]):
        raise Refused(f"--barred {barred[:9]} is not an ancestor of the branch the merge brought in ({parents[1][:9]})")
    # K170: the receipt names the landing, so every two-parent merge accepted above is read as that landing; the
    # merge's two sides never decide it here (`KS.is_landing` is not asked): the receipt's domain, unchanged.
    subject = KS.check(repo, merge, base=parents[0], named_landing=True)
    flags = [f for f in subject["flags"] if f not in ("NO-RECEIPT", "RECEIPT-MISMATCH")]
    if flags:
        raise Refused(f"the subject check raised {','.join(flags)}: {KS.line(subject)}")
    brief = KS.path_at(repo, subject["tip"], subject["brief"])
    block = KS.parse_block(brief)
    fields = block["fields"]
    declared = block["manifest"]
    default = not declared            # K124: no manifest declared -> the profile's default identity
    key = fields["key"]
    if key == PENDING and key_verdict is not None:
        raise Refused("a key verdict was given for a pending-cross-family key; declare the key's class in the brief")
    if key != PENDING and key_verdict is None:
        raise Refused(f"the key class is {key}: its verdict file is required (--key-verdict)")
    codex = is_codex_key(key)                       # K140 round 2: the result belongs to Codex classes only
    if key == PENDING and key_result is not None:
        raise Refused("a key result was given for a pending-cross-family key; drop --key-result or declare the key's "
                      "class in the brief")
    if key != PENDING and not codex and key_result is not None:
        raise Refused(f"--key-result is for a Codex key class (cross-family:codex-*); the key class is {key}, whose "
                      "verdict file alone is read: drop --key-result")
    if codex and key_result is None:               # K140: required, so a credited receipt proves the run read the tree
        raise Refused(f"the key class is {key}: its codex-review result is required (--key-result): pass the file "
                      "holding tools/codex-review.py's stdout for the key run")
    if key_verdict is not None:
        raw = key_verdict.read_bytes()
        text = raw.decode("utf-8", "replace").replace("\r\n", "\n")
        verdict_word, verdict_line = key_verdict_line(text, merge, key_verdict)
        verdict_sha = "sha256:" + hashlib.sha256(raw).hexdigest()
        if codex:
            want = key_role(key)                                                # K140 round 1
            result_raw = key_result.read_bytes()
            res = key_result_reading(result_raw, key_result, key_verdict, verdict_sha, want, merge)  # K140
            key_run, result_sha = key_run_reading(want, res), "sha256:" + hashlib.sha256(result_raw).hexdigest()
        else:
            key_run, result_sha = "none (not a Codex key class: the verdict file only)", "none"
    else:
        verdict_word, verdict_line, verdict_sha = None, "none", "none"
        key_run, result_sha = "none", "none"
    barred_tree, landed_tree = tree(repo, barred), tree(repo, merge)
    if default:
        identity_ok = True
        identity_lines = (f"- identity rule: {DEFAULT_RULE}\n"
                          f"- identity: {landed_tree} (the landed merge's tree)\n")
    else:
        declared = sorted(declared)
        # K124: the manifest is the declarer's claim -- this tool does not derive what the checks read -- but the
        # inputs that define the bar are mechanically known, and a manifest that leaves one out is refused.
        required_inputs = bar_inputs(block["contract_text"])
        left_out = [p for p in required_inputs if p not in declared]
        if left_out:
            raise Refused(f"the manifest leaves out bar-defining input(s) it must declare ({BAR_INPUT_KINDS}): "
                          + ", ".join(left_out) + "; or declare no manifest (the default identity)")
        derived = derived_manifest(repo, merge, barred)
        undeclared = [p for p in derived if p not in declared]
        unchanged = [p for p in declared if p not in derived]
        manifest_ok = not undeclared                 # K95: unchanged declared inputs are what the profile asks for
        nowhere = absent_everywhere(repo, barred, merge, declared)
        if nowhere:
            raise Refused("declared path(s) name nothing at the barred commit or the landed merge (a misspelling or "
                          "wrong case reads as an unchanged input): " + ", ".join(nowhere))
        at_barred, at_landed = identity(repo, barred, declared), identity(repo, merge, declared)
        touching = range_touches(repo, barred, merge, declared)
        identity_ok = manifest_ok and at_barred == at_landed and not touching
        manifest_line = (f"MATCH ({len(declared) - len(unchanged)} changed, {len(unchanged)} unchanged declared "
                         "inputs)" if manifest_ok else "DIFFER (changed but undeclared: " + ", ".join(undeclared) + ")")
        range_line = ("no non-merge commit, and no merge whose result differs from every parent (git diff-tree --cc), "
                      "changes a declared path" if not touching else
                      f"{len(touching)} commit(s) touch declared paths: " + ", ".join(t[:9] for t in touching[:5]))
        identity_lines = (f"- identity rule: path manifest, {len(declared)} declared paths\n"
                          "- manifest claim: the declarer's claim, not derived (this receipt does not derive what the "
                          "acceptance checks read); bar-defining inputs required declared, all declared: "
                          + ", ".join(required_inputs) + "\n"
                          f"- manifest: {manifest_line}\n"
                          f"- identity at barred: {at_barred}\n"
                          f"- identity at landed: {at_landed}\n"
                          f"- intervening range: {range_line}\n"
                          f"- identity: {'MATCH' if identity_ok else 'DIFFER'}\n")
    runners = declared_runners(block["contract_text"])
    check_runners(runs_read, runners)
    # K124 round 3 (the K6 key's REJECT of 6576d42): each run names its workflow; only the workflow that runs the
    # filter counts toward the passes, and every workflow the bar names must be green at the landed merge.
    workflows = bar_workflows(block["contract_text"])
    for i, _c, _s, _n in runs_read:
        if wf_of(i) not in workflows:
            raise Refused(f"bar run {i} names workflow {wf_of(i)!r}, which the contract's `bar:` does not name "
                          f"(it names {', '.join(workflows)})")
    filter_wf, filter_why = filter_workflow(repo, merge, block["contract_text"], workflows)
    bound = bind_runs(runs_read, barred, merge)
    ledger_held = bool(KS.path_at(repo, merge, ledger) is not None)
    if key == PENDING:
        closed = "no -- K6 is pending-cross-family: this subject is declared and receipted, not claimed closed"
    else:
        closed = "not claimed by this tool -- the integrator reads the key's verdict against the contract"
    successes = sum(1 for _i, c, _w, _n in bound if c == "success")
    at_merge = [c for _i, c, w, _n in bound if w == "landed"]
    green_at_merge = at_merge.count("success")
    counted = [(i, c, w, n) for i, c, w, n in bound if wf_of(i) == filter_wf]
    filter_successes = sum(1 for _i, c, _w, _n in counted if c == "success")
    f_at_merge = [c for _i, c, w, _n in counted if w == "landed"]
    f_green_at_merge = f_at_merge.count("success")
    unrun = [x for x in workflows
             if not any(wf_of(i) == x and c == "success" and w == "landed" for i, c, w, _n in bound)]
    required = passes_required(block["contract_text"])
    # Round 1 (Codex finding 1): the contract's passes are identical green passes at ONE sha; summing across the
    # barred sha and the merge read two at one and one at the other as three. Round 3: of the filter's workflow.
    green_at = {w: sum(1 for _i, c, x, _n in counted if x == w and c == "success") for w in ("barred", "landed")}
    best = max(green_at.values())
    if default and green_at["landed"] < required:
        # K124: the default identity is the delivered tree, so only runs AT the landed merge tested it
        raise Refused(f"the default identity needs {required} green {filter_wf} run(s) at the landed merge; "
                      f"{green_at['landed']} there (runs at the barred commit do not count: {green_at['barred']} "
                      f"green there; runs of other workflows do not count: {filter_wf} runs the filter)")
    if default and unrun:
        raise Refused("the default identity needs a green run of every workflow the contract's `bar:` names at the "
                      "landed merge; none of " + ", ".join(unrun))
    every = "every bar workflow green there"
    if key != PENDING and verdict_word != "ACCEPT":
        creditable = f"no -- the K6 key did not accept ({verdict_line})"          # K118
    elif default:
        creditable = (f"yes -- default identity (the landed merge's tree), {green_at['landed']} green {filter_wf} "
                      f"run(s) at the landed merge; {every}")
    elif not identity_ok:
        creditable = "no -- identity DIFFER"
    elif not f_green_at_merge:
        creditable = (f"no -- no {filter_wf} run at the landed merge succeeded" if f_at_merge else
                      f"no -- no {filter_wf} run at the landed merge: acceptance has not re-run at the delivered tree")
    elif unrun:
        creditable = ("no -- no green run at the landed merge of " + ", ".join(unrun)
                      + ": every workflow the bar names must re-run at the delivered tree")
    elif best < required:
        creditable = (f"no -- {best} green {filter_wf} run(s) at any one sha (barred {green_at['barred']}, landed "
                      f"{green_at['landed']}); the contract's passes require {required} at one sha")
    else:
        creditable = (f"yes -- identity MATCH, {best} green {filter_wf} run(s) at one sha (barred "
                      f"{green_at['barred']}, landed {green_at['landed']}) and {f_green_at_merge} at the landed "
                      f"merge; {every}")
    if filter_successes < required:
        raise Refused(f"{filter_successes} successful {filter_wf} run(s) named; the contract's passes require "
                      f"{required} (runs of other workflows do not count: {filter_wf} runs the filter)")
    row = block["row"]

    def where(i: str, w: str) -> str:
        bits = [w]
        if wf_of(i) != filter_wf:
            bits.append(f"not counted toward the passes: {filter_wf} runs the filter")
        elif default and w == "barred":
            bits.append(NOT_COUNTED)
        return ", ".join(bits)

    text = (f"# Kernel receipt: {fields['subject']}\n\n"
            "Written by `tools/kernel-receipt.py` at landing. Read it with `tools/kernel-subjects.py check`.\n\n"
            f"- subject: {fields['subject']}\n"
            f"- kernel: {fields['kernel']}\n"
            f"- profile: {fields['profile']}\n"
            f"- contract: {fields['contract']}\n"
            f"- products: {' '.join(block['products'])}\n"
            f"- brief: {subject['brief']} (block first committed in {subject['block_commit']})\n"
            f"- first product commit: {subject['first_product'] or 'none (no commit touches the products)'}\n"
            f"- barred candidate: {barred} (tree {barred_tree}; as stated by the caller, checked to be on the branch)\n"
            f"- landed merge: {merge} (tree {landed_tree})\n"
            + identity_lines +
            f"- trees: {'equal' if barred_tree == landed_tree else 'differ'}\n"
            f"- declared runner: {' or '.join(runners)} (the contract's env)\n"
            f"- bar workflows: {', '.join(workflows)} (the contract's bar; each run's workflow as the caller read it)\n"
            f"- filter workflow: {filter_wf} ({filter_why}); only its runs count toward the passes\n"
            f"- bar runs: {len(bound)} named, {successes} success\n"
            + "".join(f"- bar run: {i} conclusion {c} at {barred if w == 'barred' else merge} ({where(i, w)}) on {n}\n"
                      for i, c, w, n in bound)
            + "".join(f"- bar run {i} {excluded[i]}\n" for i, _c, _w, _n in bound if i in excluded)
            + f"- re-run at the delivered tree: {len(at_merge)} run(s) at the landed merge, {green_at_merge} success\n"
            f"- creditable: {creditable}\n"
            + f"- review ledger: {ledger} ({'in' if ledger_held else 'not in'} the landed merge's tree)\n"
            f"- key class: {key}\n"
            f"- key verdict: {verdict_line}\n"
            f"- key verdict sha256: {verdict_sha}\n"
            f"- key run: {key_run}\n"
            f"- key result sha256: {result_sha}\n"
            f"- closed end to end: {closed}\n\n"
            + ("## Manifest\n\nnone declared: the default identity applies\n" if default else
               "## Manifest (declared)\n\n" + "".join(f"- {p}\n" for p in declared)))
    return f"{KS.RECEIPTS}{row}.md", text


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", default=".")
    ap.add_argument("--merge", required=True)
    ap.add_argument("--barred", required=True)
    ap.add_argument("--run", action="append", default=[],
                    help="<workflow>/<id>=<conclusion>@<sha>:<runner name>, once per bar run (workflow: its file stem, "
                         "e.g. tools-bar; sha: 12-40 hex of the commit it tested; runner: the run log's `Runner name`)")
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--key-verdict", type=Path, default=None)
    ap.add_argument("--key-result", type=Path, default=None,
                    help="tools/codex-review.py's stdout for the key run (its JSON result line); required with "
                         "--key-verdict (K140)")
    ap.add_argument("--bar-log", action="append", default=[],
                    help="<workflow>/<id>=<file>: a product-bar run's log as `gh run view <id> --log` wrote it; the "
                         "receipt records the excluded test-case counts it prints (K166)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    repo = Path(args.repo).resolve()
    try:
        rel, text = build(repo, args.merge, args.barred, args.run, args.ledger, args.key_verdict, args.key_result,
                          args.bar_log)
    except (Refused, KS.GitFailed, OSError) as exc:
        print(f"REFUSE kernel-receipt: {exc}", file=sys.stderr)
        return 2
    if args.dry_run:
        sys.stdout.write(text)
        return 0
    out = repo / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(text.encode("utf-8"))                 # binary, LF
    print(f"wrote {rel}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
