#!/usr/bin/env python3
"""Run the factory kernel's own suites on the bus.   python tools/factory/kernel-suites.tests.py [suite ...]

kernel-subjects.tests.py, kernel-receipt.tests.py and codex-review.tests.py came from Cloudvore (origin/master
31315b2, bus K154) unchanged. They load their tool beside themselves and the tool reads factory-config.json beside
itself, so this harness stages each run in a private directory laid out as a project's tools/ directory: the three
tools, the three suites, and fixtures/kernel/cloudvore.factory-config.json as factory-config.json.
FACTORY_KERNEL_CONFIG is removed from the suites' environment (several suites copy a tool beside a config of their
own; the variable would override that copy's config).

A few tests read the project tree around tools/ (its workflows, docs, ledgers, evidence and real landing history).
They cannot run here and are EXCLUDED BY NAME below, each with the file it reads; they stay pins in the adopting
project's own run of these suites. An excluded name that no longer exists fails this harness (the list cannot go
stale), and the excluded count is printed, never folded into "OK".
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOLS = ("kernel-subjects.py", "kernel-receipt.py", "codex-review.py")
SUITES = ("kernel-subjects.tests.py", "kernel-receipt.tests.py", "codex-review.tests.py")
CONFIG = HERE / "fixtures" / "kernel" / "cloudvore.factory-config.json"

# suite -> {test id (Class.method): the project file outside tools/ it reads}
NEEDS_PROJECT_TREE: dict[str, dict[str, str]] = {
    "kernel-subjects.tests.py": {
        "BlockTests.test_both_bar_workflows_resolve_runs_on_from_ci_runs_on_as_the_default_env_says":
            ".github/workflows/{tools,product}-bar.yml",
    },
    "kernel-receipt.tests.py": {
        "KeyVerdictSemanticsTests.test_the_real_k115_key_transcript_is_refused_and_its_final_message_reads_reject":
            "review/evidence-k118-2026-10-08/k115-key-verdict.txt",
        "KeyVerdictSemanticsTests.test_the_prompt_builder_never_puts_the_merge_on_a_verdict_line":
            "review/evidence-k96-2026-10-07/build_prompt.py.txt",
        "FilterEvidenceTests.test_the_tools_bar_fails_when_a_required_suite_file_is_missing":
            "tools/run-tools-bar.py",
        "FilterEvidenceTests.test_every_required_suite_exists_in_this_tree":
            "tools/run-tools-bar.py",
        "StepAndJobKeyTests.test_the_real_tools_bar_binds_at_head_and_the_k132_and_k133_merges":
            ".github/workflows/tools-bar.yml at HEAD and at the project's K132 and K133 merges",
        "ExcludedCountTests.test_a_real_pre_k166_product_bar_log_reports_nothing":
            "review/evidence-h126-2026-10-12/landing/run-38351017597.log.txt",
        "FactoryConfigRunnerTests.test_the_real_k132_runs_refuse_under_a_config_naming_another_runner":
            "the project's git history (the K132 landing merge 5a5fbe99b)",
    },
    "codex-review.tests.py": {
        "RoleTableMatchesTheDocTests.test_doc_table_equals_tool_table_in_both_directions":
            "docs/operating-contract-model-routing.md",
        "RoleTableMatchesTheDocTests.test_mutating_one_table_entry_turns_this_red":
            "docs/operating-contract-model-routing.md",
    },
}

RUNNER = r'''
import importlib.util, json, sys, unittest
suite_file, excluded = sys.argv[1], json.loads(sys.argv[2])
spec = importlib.util.spec_from_file_location("suite_under_harness", suite_file)
mod = importlib.util.module_from_spec(spec)
sys.modules["suite_under_harness"] = mod
spec.loader.exec_module(mod)
loaded = unittest.defaultTestLoader.loadTestsFromModule(mod)
def flat(s):
    for t in s:
        if isinstance(t, unittest.TestSuite):
            yield from flat(t)
        else:
            yield t
tests = list(flat(loaded))
ids = {t.id().split(".", 1)[1] for t in tests}
stale = sorted(set(excluded) - ids)
if stale:
    print("HARNESS: excluded test(s) no longer exist: " + ", ".join(stale), file=sys.stderr)
    sys.exit(3)
keep = unittest.TestSuite(t for t in tests if t.id().split(".", 1)[1] not in excluded)
print(f"HARNESS: {len(tests)} discovered, {len(excluded)} excluded (need the project tree), "
      f"{keep.countTestCases()} run", file=sys.stderr)
r = unittest.TextTestRunner(verbosity=1).run(keep)
sys.exit(0 if r.wasSuccessful() else 1)
'''


def stage(work: Path) -> Path:
    tools = work / "tools"
    tools.mkdir(parents=True)
    for name in (*TOOLS, *SUITES):
        shutil.copyfile(HERE / name, tools / name)
    shutil.copyfile(CONFIG, tools / "factory-config.json")
    (work / "run_suite.py").write_text(RUNNER, encoding="utf-8")
    return tools


def main(argv: list[str]) -> int:
    chosen = argv or list(SUITES)
    unknown = [s for s in chosen if s not in SUITES]
    if unknown:
        print(f"unknown suite(s): {', '.join(unknown)}; choose from {', '.join(SUITES)}", file=sys.stderr)
        return 2
    env = {k: v for k, v in os.environ.items() if k != "FACTORY_KERNEL_CONFIG"}
    worst = 0
    with tempfile.TemporaryDirectory(prefix="kernel-suites-") as tmp:
        work = Path(tmp)
        tools = stage(work)
        for suite in chosen:
            print(f"== {suite}", flush=True)
            p = subprocess.run([sys.executable, str(work / "run_suite.py"), str(tools / suite),
                                json.dumps(sorted(NEEDS_PROJECT_TREE[suite]))], cwd=str(tools), env=env)
            print(f"== {suite}: exit {p.returncode}", flush=True)
            worst = max(worst, p.returncode)
    return worst


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
