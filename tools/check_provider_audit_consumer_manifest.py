#!/usr/bin/env python3
"""Verify the deployment-inert R46 provider audit-consumer manifest."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PurePosixPath("manifests/provider-audit-consumer-provenance-r46.json")
EXPECTED_PARENT_COMMIT = "0da4a20f9e62a47414f42a8780c695865f1633a0"
EXPECTED_PARENT_TREE = "058fc80c346840701eb7fdb5b551f8ee0d68ed54"
EXPECTED_SUBJECTS = (
    "schemas/provider-audit-consumer-provenance-v1.schema.json",
    "specs/provider-audit-consumer-provenance.md",
    "tests/test_provider_audit_consumer_provenance.py",
    "tools/check_provider_audit_consumer_manifest.py",
    "tools/provider_audit_consumer_provenance.py",
)
EXPECTED_LAWS = (
    "terminal-authenticated-provider-identity",
    "exact-byte-create-new-final-opinion",
    "actual-shell-preclaim-wrapper-self-test",
    "explicit-read-command-allowlist-zero-failures",
    "immutable-non-suppressing-provider-diagnostics",
    "resource-limit-spent-no-verdict-lineage",
    "explicit-provider-substitution",
    "postflight-dominates-substantive-text",
    "classification-is-not-execution-authority",
    "r45-remains-immutable",
)
ZERO_SHA256 = "sha256:" + "0" * 64


class ManifestError(ValueError):
    pass


def _git(*args: str, input_bytes: bytes | None = None) -> str:
    result = subprocess.run(
        ["git", "-C", str(ROOT), *args],
        input=input_bytes,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode:
        raise ManifestError(result.stderr.decode("utf-8", errors="replace").strip())
    return result.stdout.decode("ascii").strip()


def _mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ManifestError(f"{name} must be an object")
    return value


def _canonical_self_sha256(manifest: Mapping[str, Any]) -> str:
    value = copy.deepcopy(dict(manifest))
    self_row = _mapping(value.get("manifestSelf"), "manifestSelf")
    self_row["canonicalSha256"] = ZERO_SHA256
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _subject_oid(path: str, raw: bytes) -> str:
    return _git("hash-object", "--path", path, "--stdin", input_bytes=raw)


def verify_manifest() -> Mapping[str, Any]:
    manifest_file = ROOT / MANIFEST_PATH
    raw_manifest = manifest_file.read_bytes()
    manifest = _mapping(json.loads(raw_manifest.decode("utf-8")), "manifest")
    if manifest.get("schema") != "fleet-provider-audit-consumer-provenance-candidate/v1":
        raise ManifestError("manifest schema mismatch")
    if manifest.get("round") != "R46" or manifest.get("status") != "CANDIDATE_ZERO_AUTHORITY":
        raise ManifestError("R46 status mismatch")
    parent = _mapping(manifest.get("parent"), "parent")
    if parent.get("commit") != EXPECTED_PARENT_COMMIT or parent.get("tree") != EXPECTED_PARENT_TREE:
        raise ManifestError("R45 parent identity mismatch")
    if _git("rev-parse", f"{EXPECTED_PARENT_COMMIT}^{{tree}}") != EXPECTED_PARENT_TREE:
        raise ManifestError("R45 object database identity mismatch")
    if _git("rev-parse", "HEAD") != EXPECTED_PARENT_COMMIT and _git(
        "merge-base", "--is-ancestor", EXPECTED_PARENT_COMMIT, "HEAD"
    ):
        raise ManifestError("R46 worktree does not descend from exact R45")

    authority = _mapping(manifest.get("authority"), "authority")
    required_false = (
        "providerExecution",
        "processSpawnResumeKill",
        "workloadExecution",
        "adoption",
        "score",
        "merge",
        "push",
        "automaticSubstitution",
    )
    if any(authority.get(field) is not False for field in required_false):
        raise ManifestError("manifest grants forbidden authority")
    if authority.get("activationRequiresSeparateAdjudication") is not True:
        raise ManifestError("separate adjudication boundary missing")
    if tuple(manifest.get("laws", ())) != EXPECTED_LAWS:
        raise ManifestError("law inventory mismatch")

    subjects = manifest.get("subjectFiles")
    if not isinstance(subjects, list) or tuple(row.get("path") for row in subjects) != EXPECTED_SUBJECTS:
        raise ManifestError("subject sequence is not exact")
    for row in subjects:
        path = str(PurePosixPath(row["path"]))
        raw = (ROOT / PurePosixPath(path)).read_bytes()
        if row.get("bytes") != len(raw):
            raise ManifestError(f"subject byte-count mismatch: {path}")
        if row.get("sha256") != "sha256:" + hashlib.sha256(raw).hexdigest():
            raise ManifestError(f"subject SHA-256 mismatch: {path}")
        if row.get("gitBlobOid") != _subject_oid(path, raw):
            raise ManifestError(f"subject Git blob OID mismatch: {path}")

    self_row = _mapping(manifest.get("manifestSelf"), "manifestSelf")
    if self_row.get("path") != str(MANIFEST_PATH):
        raise ManifestError("manifest self path mismatch")
    if self_row.get("canonicalSha256") != _canonical_self_sha256(manifest):
        raise ManifestError("manifest canonical self SHA-256 mismatch")
    return {
        "schema": "fleet-provider-audit-consumer-provenance-check/v1",
        "outcome": "PASS",
        "round": "R46",
        "parentCommit": EXPECTED_PARENT_COMMIT,
        "parentTree": EXPECTED_PARENT_TREE,
        "subjects": len(EXPECTED_SUBJECTS),
        "laws": len(EXPECTED_LAWS),
        "providerExecution": False,
        "workloadExecution": False,
        "authority": False,
        "manifestCanonicalSha256": self_row["canonicalSha256"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="emit compact JSON")
    args = parser.parse_args(argv)
    try:
        report = verify_manifest()
    except (ManifestError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"REFUSE: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, sort_keys=True, separators=(",", ":") if args.json else None, indent=None if args.json else 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
