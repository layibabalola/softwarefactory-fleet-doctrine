#!/usr/bin/env python3
"""Verify the frozen zero-authority fleet reserve census."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CENSUS_PATH = ROOT / "capacity-control" / "fleet-zero-reserve-census-r1.json"
QUEUE_PATH = ROOT / "capacity-control" / "zero-reserve-disposition-requests-r1.json"
POLICY_PATH = ROOT / "capacity-control" / "policy" / "default-v1.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def main() -> None:
    census = json.loads(CENSUS_PATH.read_text(encoding="utf-8"))
    queue = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
    policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))

    require(census["schema"] == "softwarefactory.fleet-zero-reserve-census.v1", "census schema")
    require(census["status"] == "ZERO_AUTHORITY_EVIDENCE_SNAPSHOT", "census status")
    require(census["subject"]["candidate_id"] == "ZERO_DISCRETIONARY_CAPACITY_RESERVE_R2", "candidate id")
    require(census["subject"]["disposition_request_queue_sha256"] == sha256(QUEUE_PATH), "request queue hash")
    require(census["shared_hub_policy"]["sha256"] == sha256(POLICY_PATH), "shared policy hash")
    require(census["shared_hub_policy"]["bytes"] == POLICY_PATH.stat().st_size, "shared policy bytes")
    require(census["shared_hub_policy"]["reserve_fraction_by_priority"] == policy["reserve_fraction_by_priority"], "shared reserve values")
    require(census["shared_hub_policy"]["classification"] == "EXPLICIT_NONZERO_SHARED_DEFAULT_NOT_PROJECT_ADOPTION", "shared policy classification")

    expected = {
        "adobe-ingester",
        "adversarialllm",
        "agent-bridge",
        "airmypc",
        "cloudvore",
        "conjugal",
        "dng-auto-processor",
        "mlv-app",
        "salesforce-tools",
    }
    projects = census["projects"]
    require(len(projects) == 9, "nine project rows")
    require({row["project_id"] for row in projects} == expected, "exact project set")
    require(all(row["requested_disposition"] == "PENDING_PROJECT_OWNER" for row in projects), "all census dispositions pending")
    require(len(queue["projects"]) == 9, "queue has nine projects")
    require({row["project_id"] for row in queue["projects"]} == expected, "queue project set")
    require(all(row["requested_disposition"] == "PENDING_PROJECT_OWNER" for row in queue["projects"]), "queue remains pending")

    counts = {
        "EXPLICIT_ZERO_RESERVE_SOURCE_WITH_CLOSED_LIVE_GATE": 1,
        "EXPLICIT_NONZERO_RESERVE_IN_REMOTE_SOURCE": 1,
        "NO_DECLARED_RESERVE_TOKEN_FOUND_REMOTE_SOURCE_RUNTIME_UNPROVEN": 3,
        "UNMOUNTED_RUNTIME_UNPROVEN": 4,
    }
    for classification, expected_count in counts.items():
        require(sum(row["classification"] == classification for row in projects) == expected_count, f"classification count {classification}")

    dng = next(row for row in projects if row["project_id"] == "dng-auto-processor")
    adversarial = next(row for row in projects if row["project_id"] == "adversarialllm")
    require(dng["declared_reserve_percent"] == 0, "DNG declared zero reserve")
    require(dng["live_gate_state"] == "closed", "DNG captured gate closed")
    require(adversarial["declared_reserve_percent"] == 25, "Adversarial declared 25 percent reserve")
    require(adversarial["policy_git_blob_oid"] == "f8fe4f425913ebdd4a5ba5c88e416c23e8f6a04a", "Adversarial exact policy blob")
    require(census["summary"] == {
        "project_count": 9,
        "explicit_zero_source_with_live_gate": 1,
        "explicit_nonzero_remote_source": 1,
        "no_declared_reserve_token_remote_runtime_unproven": 3,
        "unmounted_runtime_unproven": 4,
        "zero_reserve_project_dispositions": 0,
        "fleetwide_zero_reserve_proven": False,
    }, "summary is exact")
    require(census["authority"] == {
        "provider_launches": 0,
        "project_mutations": 0,
        "runtime_mutations": 0,
        "project_dispositions": 0,
        "project_adoptions": 0,
        "doctrine_ratification": False,
        "fleet_adoption": False,
    }, "zero-authority boundary")

    print("PASS: fleet reserve census 1 zero / 1 nonzero / 3 remote-unproven / 4 unmounted-unproven; 0 dispositions")


if __name__ == "__main__":
    main()
