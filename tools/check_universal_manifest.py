#!/usr/bin/env python3
"""Verify the universal-control candidate manifest against canonical Git blob bytes."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "manifests/universal-provider-control-reconciliation-r16.json"
SELF_PATTERN = re.compile(
    rb'("canonicalGitBlobSha256"\s*:\s*"sha256:)([0-9a-f]{64})(")'
)


class ManifestError(ValueError):
    pass


def _pairs(values: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in values:
        if key in result:
            raise ManifestError("DUPLICATE_KEY")
        result[key] = value
    return result


def _git(spec: str, *, text: bool = False) -> bytes | str:
    run = subprocess.run(
        ["git", "show", spec], cwd=ROOT, check=False, capture_output=True,
        text=text, encoding="utf-8" if text else None,
    )
    if run.returncode != 0:
        raise ManifestError("GIT_BLOB_UNAVAILABLE")
    return run.stdout


def _blob_spec(treeish: str, path: str) -> str:
    return f":{path}" if treeish == ":" else f"{treeish}:{path}"


def _oid(treeish: str, path: str) -> str:
    spec = _blob_spec(treeish, path)
    run = subprocess.run(
        ["git", "rev-parse", spec], cwd=ROOT, check=False, capture_output=True, text=True,
        encoding="utf-8",
    )
    if run.returncode != 0 or re.fullmatch(r"[0-9a-f]{40,64}\n?", run.stdout) is None:
        raise ManifestError("GIT_BLOB_OID_UNAVAILABLE")
    return run.stdout.strip()


def _commit_tuple(commit: str) -> tuple[str, list[str]]:
    run = subprocess.run(
        ["git", "show", "-s", "--format=%T%n%P", commit], cwd=ROOT,
        check=False, capture_output=True, text=True, encoding="utf-8",
    )
    if run.returncode != 0:
        raise ManifestError("RECONCILIATION_OBJECT_UNAVAILABLE")
    lines = run.stdout.splitlines()
    if len(lines) != 2 or re.fullmatch(r"[0-9a-f]{40,64}", lines[0]) is None:
        raise ManifestError("RECONCILIATION_OBJECT_INVALID")
    parents = lines[1].split() if lines[1] else []
    if any(re.fullmatch(r"[0-9a-f]{40,64}", parent) is None for parent in parents):
        raise ManifestError("RECONCILIATION_OBJECT_INVALID")
    return lines[0], parents


def verify_reconciliation(manifest: dict[str, Any], treeish: str = "HEAD") -> None:
    """Verify the exact linear WIP and ordered canonical-master/R15 merge topology."""

    reconciliation = manifest.get("reconciliation")
    if not isinstance(reconciliation, dict):
        raise ManifestError("RECONCILIATION_INVALID")
    for name in ("r15Base", "r16PreMaster", "canonicalFleetMaster", "r16MasterMerge"):
        record = reconciliation.get(name)
        if not isinstance(record, dict) or set(record) != {
            "commit", "tree", "orderedParents", "orderedParentTrees"
        }:
            raise ManifestError("RECONCILIATION_INVALID")
        tree, parents = _commit_tuple(record["commit"])
        if tree != record["tree"] or parents != record["orderedParents"]:
            raise ManifestError("RECONCILIATION_COMMIT_MISMATCH")
        if len(parents) != len(record["orderedParentTrees"]):
            raise ManifestError("RECONCILIATION_PARENT_TREE_MISMATCH")
        actual_parent_trees = [_commit_tuple(parent)[0] for parent in parents]
        if actual_parent_trees != record["orderedParentTrees"]:
            raise ManifestError("RECONCILIATION_PARENT_TREE_MISMATCH")
    r15 = reconciliation["r15Base"]
    pre_master = reconciliation["r16PreMaster"]
    canonical = reconciliation["canonicalFleetMaster"]
    merged = reconciliation["r16MasterMerge"]
    if (
        pre_master["orderedParents"] != [r15["commit"]]
        or merged["orderedParents"] != [pre_master["commit"], canonical["commit"]]
    ):
        raise ManifestError("RECONCILIATION_ORDER_INVALID")
    if treeish != ":":
        run = subprocess.run(
            ["git", "merge-base", "--is-ancestor", merged["commit"], treeish],
            cwd=ROOT, check=False, capture_output=True,
        )
        if run.returncode != 0:
            raise ManifestError("RECONCILIATION_NOT_ANCESTOR")


def canonical_self_sha256(raw: bytes) -> str:
    """Return the zeroed-field self digest over canonical Git blob bytes only."""

    matches = list(SELF_PATTERN.finditer(raw))
    if len(matches) != 1:
        raise ManifestError("MANIFEST_SELF_INVALID")
    zeroed = SELF_PATTERN.sub(lambda match: match.group(1) + b"0" * 64 + match.group(3), raw)
    return "sha256:" + hashlib.sha256(zeroed).hexdigest()


def check(treeish: str) -> int:
    raw = _git(_blob_spec(treeish, MANIFEST))
    assert isinstance(raw, bytes)
    try:
        manifest = json.loads(raw.decode("utf-8", errors="strict"), object_pairs_hook=_pairs)
    except (UnicodeDecodeError, json.JSONDecodeError, ManifestError) as exc:
        raise ManifestError("MANIFEST_INVALID") from exc
    if manifest.get("schema") != "fleet-universal-provider-control-candidate-manifest/v2":
        raise ManifestError("MANIFEST_SCHEMA_INVALID")
    verify_reconciliation(manifest, treeish)
    subjects = manifest.get("subjectFiles")
    if not isinstance(subjects, list) or not subjects:
        raise ManifestError("MANIFEST_SUBJECTS_INVALID")
    seen: set[str] = set()
    for subject in subjects:
        if not isinstance(subject, dict) or set(subject) != {"path", "gitBlobOid", "sha256", "bytes"}:
            raise ManifestError("MANIFEST_SUBJECT_INVALID")
        path = subject["path"]
        if not isinstance(path, str) or path in seen or path == MANIFEST:
            raise ManifestError("MANIFEST_SUBJECT_INVALID")
        seen.add(path)
        blob = _git(_blob_spec(treeish, path))
        assert isinstance(blob, bytes)
        expected_sha = "sha256:" + hashlib.sha256(blob).hexdigest()
        if subject["sha256"] != expected_sha or subject["bytes"] != len(blob):
            raise ManifestError("MANIFEST_SUBJECT_MISMATCH")
        if subject["gitBlobOid"] != _oid(treeish, path):
            raise ManifestError("MANIFEST_BLOB_OID_MISMATCH")
    self_binding = manifest.get("manifestSelf")
    if not isinstance(self_binding, dict) or self_binding.get("path") != MANIFEST:
        raise ManifestError("MANIFEST_SELF_INVALID")
    if self_binding.get("bytes") != len(raw):
        raise ManifestError("MANIFEST_SELF_SIZE_MISMATCH")
    expected_self = canonical_self_sha256(raw)
    if self_binding.get("canonicalGitBlobSha256") != expected_self:
        raise ManifestError("MANIFEST_SELF_MISMATCH")
    print(f"MANIFEST_PASS subjects={len(subjects)} self=PASS treeish={treeish}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--treeish", default="HEAD")
    args = parser.parse_args()
    try:
        return check(args.treeish)
    except ManifestError as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
