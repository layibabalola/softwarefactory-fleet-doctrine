#!/usr/bin/env python3
"""kernel-config.py -- check a project's factory kernel config with the loader the kernel tools themselves use.

    python tools/factory/kernel-config.py check <factory-config.json>
    pin-runner.py run kernel-config -- check factory-pins/factory-config.json     # pinned with --with kernel-subjects

The loader of record is `load_config` in kernel-subjects.py (K137: every key required, no other key, each value of
its kind, contradicting keys refused). This entry point loads kernel-subjects.py from beside itself with
FACTORY_KERNEL_CONFIG naming the file to check, so a config is judged by exactly the code that will read it, never by
a second implementation. factory-config.schema.json describes the same layout for editors; the bus suite
tools/factory/kernel-tools.tests.py keeps the two key sets equal.

Exit: 0 the config loads; 2 it is refused (the reason names the key) or the usage is wrong.
"""
from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path


def check(config: str) -> int:
    os.environ["FACTORY_KERNEL_CONFIG"] = config
    spec = importlib.util.spec_from_file_location("factory_kernel_subjects_for_config",
                                                  Path(__file__).with_name("kernel-subjects.py"))
    ks = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(ks)
    except ValueError as exc:                    # kernel-subjects' ConfigError
        print(f"REFUSE kernel-config: {exc}", file=sys.stderr)
        return 2
    c = ks.CONFIG
    print(f"CONFIG OK {config}: subject {c['subject']['prefix']}<{c['subject']['row']}>, runner {c['bar']['runner']}, "
          f"briefs {c['paths']['briefs']}")
    return 0


def main(argv: list[str]) -> int:
    if len(argv) != 2 or argv[0] != "check":
        print("usage: kernel-config.py check <factory-config.json>", file=sys.stderr)
        return 2
    return check(argv[1])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
