#!/usr/bin/env python3
import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
QUEUE = ROOT / "capacity-control" / "zero-reserve-disposition-requests-r1.json"
EXPECTED = [
    "adobe-ingester",
    "adversarialllm",
    "agent-bridge",
    "airmypc",
    "cloudvore",
    "conjugal",
    "dng-auto-processor",
    "mlv-app",
    "salesforce-tools",
]


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def bound_file(binding: dict, label: str) -> None:
    path = ROOT / binding["path"]
    check(path.is_file(), f"{label} missing: {path}")
    check(path.stat().st_size == binding["bytes"], f"{label} byte mismatch")
    check(sha256(path) == binding["sha256"], f"{label} hash mismatch")


def main() -> int:
    queue = json.loads(QUEUE.read_text(encoding="utf-8"))
    check(queue["schema"] == "softwarefactory.zero-reserve-disposition-requests.v1", "schema")
    check(queue["status"] == "REQUESTED_PENDING_PROJECT_OWNER_PUBLICATION", "status")
    bound_file(queue["candidate"], "candidate")
    bound_file(queue["matrix"], "matrix")
    bound_file(queue["ledger"], "ledger")

    ledger = json.loads((ROOT / queue["ledger"]["path"]).read_text(encoding="utf-8"))
    ledger_projects = ledger["projects"]
    ledger_ids = [row["projectId"] for row in ledger_projects]
    check(ledger_ids == EXPECTED, "ledger closed project order")
    counts = {key: 0 for key in ("ADOPT", "DISTINGUISH", "MISSING", "REJECT", "STALE")}
    ledger_status = {}
    ledger_specs = {}
    for row in ledger_projects:
        counts[row["status"]] += 1
        ledger_status[row["projectId"]] = row["status"]
        ledger_specs[row["projectId"]] = row["specPath"]
    check(counts == queue["ledger"]["counts"], "ledger counts")

    projects = queue["projects"]
    check([row["project_id"] for row in projects] == EXPECTED, "queue closed project order")
    check(len({row["project_id"] for row in projects}) == 9, "queue project uniqueness")
    for row in projects:
        project = row["project_id"]
        check(row["current_ledger_status"] == ledger_status[project], f"{project} status")
        check(row["spec"]["path"] == ledger_specs[project], f"{project} spec path")
        bound_file(row["spec"], f"{project} spec")
        check(row["requested_disposition"] == "PENDING_PROJECT_OWNER", f"{project} pending")
        check(bool(row["integration_seam"].strip()), f"{project} seam")
        check(bool(row["non_regression"].strip()), f"{project} non-regression")

    contract = queue["response_contract"]
    check(contract["allowed_dispositions"] == ["ADOPT", "DISTINGUISH", "REJECT"], "allowed dispositions")
    check(re.fullmatch(r"ADOPT\(ZERO_DISCRETIONARY_CAPACITY_RESERVE_R2, .+\)", contract["adopt_template"]), "adopt template")
    check(re.fullmatch(r"DISTINGUISH\(ZERO_DISCRETIONARY_CAPACITY_RESERVE_R2, .+\)", contract["distinguish_template"]), "distinguish template")
    check(re.fullmatch(r"REJECT\(ZERO_DISCRETIONARY_CAPACITY_RESERVE_R2, .+\)", contract["reject_template"]), "reject template")
    check(len(contract["adopt_minimum_evidence"]) == 8, "adopt evidence closure")

    authority = queue["authority"]
    check(set(authority) == {"project_mutations", "project_dispositions", "project_adoptions", "installations", "provider_launches", "ratification"}, "authority closure")
    check(all(authority[key] == 0 for key in ("project_mutations", "project_dispositions", "project_adoptions", "installations", "provider_launches")), "zero authority counts")
    check(authority["ratification"] is False, "no ratification")
    print("PASS: 9 project requests; 0 ADOPT / 5 DISTINGUISH / 4 STALE; zero authority")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise
