#!/usr/bin/env python3
"""Print a validated current census with refreshed Git references, without writing.

Start from the committed current ledger. Preserve all dispositions, blockers,
candidate artifacts, proof receipts and population. A change to those claims
requires a separately reviewed edit; it is never inferred by this command.
"""
from contextlib import redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import sys

_spec = importlib.util.spec_from_file_location("refresh_epoch", Path(__file__).with_name("check_current_intake_epoch.py"))
E = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E)


def refreshed_census():
    E.verify_git_object_isolation()
    head = E.git("rev-parse", "HEAD").decode().strip()
    # Check the local control and historical integrity boundaries before any
    # checker import or candidate output. The existing census may be stale;
    # validate its refreshed copy below, not the old committed census.
    E.verify_control_seal(E.parse_manifest(E.blob(head, E.EPOCH_PATH)))
    E.verify_retained_current_artifacts()
    with redirect_stdout(io.StringIO()):
        E.verify_history()
    ledger_module = E.load("adoption_ledger")
    ledger = ledger_module.load_ledger(E.blob(head, E.CURRENT_LEDGER))
    ledger["census"]["baseCommit"] = head
    for row in ledger["projects"]:
        path = row["specPath"]
        # No path or claim is added, removed or reclassified here. The complete
        # validator below refuses unknown/missing projects and altered evidence.
        row["evidence"]["commit"] = E.git("log", "-1", "--format=%H", head, "--", path).decode().strip()
        row["evidence"]["gitBlobOid"] = E.git("rev-parse", f"{head}:{path}").decode().strip()
    with redirect_stdout(io.StringIO()):
        ledger_module.verify_ledger(ledger, head, current=True)
    if E.git("rev-parse", "HEAD").decode().strip() != head:
        raise E.IntakeError("REFRESH_HEAD_MOVED")
    return ledger


def main():
    if len(sys.argv) != 1:
        print("Usage: python tools/refresh_current_adoption_census.py (prints JSON; writes no files)", file=sys.stderr)
        return 2
    try:
        value = refreshed_census()
    except Exception as exc:
        print(f"REFRESH REFUSED: {type(exc).__name__}: {exc}; dispositions and proof claims require review", file=sys.stderr)
        return 1
    print(json.dumps(value, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
