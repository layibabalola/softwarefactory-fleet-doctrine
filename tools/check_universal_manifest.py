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
MANIFEST = "manifests/universal-provider-control-reconciliation-r21.json"
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
    """Verify the exact R15-R21 linear subjects and ordered canonical-master merges."""

    reconciliation = manifest.get("reconciliation")
    if not isinstance(reconciliation, dict):
        raise ManifestError("RECONCILIATION_INVALID")
    base_names = (
        "r15Base", "r16PreMaster", "r16FrozenBeforeLatestMaster",
        "canonicalFleetMaster", "r16MasterMerge",
    )
    r17_names = ("r16Final", "r17Wip", "r17CanonicalMaster", "r17MasterMerge")
    r18_names = ("r17ManifestFreeze", "r17Final", "r18Wip")
    r19_names = (
        "r18Final", "r19Wip", "r19Evidence", "r19CanonicalMaster", "r19MasterMerge",
    )
    r20_names = ("r19Final", "r20Wip", "r20Evidence")
    r21_names = ("r20Final", "r21Wip", "r21Evidence")
    if all(name in reconciliation for name in r21_names):
        names = base_names + r17_names + r18_names + r19_names + r20_names + r21_names
    elif all(name in reconciliation for name in r20_names):
        names = base_names + r17_names + r18_names + r19_names + r20_names
    elif all(name in reconciliation for name in r19_names):
        names = base_names + r17_names + r18_names + r19_names
    elif all(name in reconciliation for name in r18_names):
        names = base_names + r17_names + r18_names
    elif all(name in reconciliation for name in r17_names):
        names = base_names + r17_names
    else:
        names = base_names
    if set(reconciliation) != set(names):
        raise ManifestError("RECONCILIATION_INVALID")
    for name in names:
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
    frozen = reconciliation["r16FrozenBeforeLatestMaster"]
    canonical = reconciliation["canonicalFleetMaster"]
    merged = reconciliation["r16MasterMerge"]
    if (
        pre_master["orderedParents"] != [r15["commit"]]
        or frozen["orderedParents"] != ["a0786f2eee16770632a2a947f65db64e60dd9820"]
        or merged["orderedParents"] != [frozen["commit"], canonical["commit"]]
    ):
        raise ManifestError("RECONCILIATION_ORDER_INVALID")
    terminal = merged
    if all(name in reconciliation for name in r17_names):
        r16_final = reconciliation["r16Final"]
        r17_wip = reconciliation["r17Wip"]
        r17_master = reconciliation["r17CanonicalMaster"]
        r17_merge = reconciliation["r17MasterMerge"]
        if (
            r16_final["orderedParents"] != [merged["commit"]]
            or r17_wip["orderedParents"] != [r16_final["commit"]]
            or r17_merge["orderedParents"] != [r17_wip["commit"], r17_master["commit"]]
        ):
            raise ManifestError("RECONCILIATION_ORDER_INVALID")
        terminal = r17_merge
    if all(name in reconciliation for name in r18_names):
        r17_freeze = reconciliation["r17ManifestFreeze"]
        r17_final = reconciliation["r17Final"]
        r18_wip = reconciliation["r18Wip"]
        if (
            r17_freeze["orderedParents"] != [terminal["commit"]]
            or r17_final["orderedParents"] != [r17_freeze["commit"]]
            or r18_wip["orderedParents"] != [r17_final["commit"]]
        ):
            raise ManifestError("RECONCILIATION_ORDER_INVALID")
        terminal = r18_wip
    if all(name in reconciliation for name in r19_names):
        r18_final = reconciliation["r18Final"]
        r19_wip = reconciliation["r19Wip"]
        r19_evidence = reconciliation["r19Evidence"]
        r19_master = reconciliation["r19CanonicalMaster"]
        r19_merge = reconciliation["r19MasterMerge"]
        if (
            r18_final["orderedParents"] != [terminal["commit"]]
            or r19_wip["orderedParents"] != [r18_final["commit"]]
            or r19_evidence["orderedParents"] != [r19_wip["commit"]]
            or r19_merge["orderedParents"]
            != [r19_evidence["commit"], r19_master["commit"]]
        ):
            raise ManifestError("RECONCILIATION_ORDER_INVALID")
        terminal = r19_merge
    if all(name in reconciliation for name in r20_names):
        r19_final = reconciliation["r19Final"]
        r20_wip = reconciliation["r20Wip"]
        r20_evidence = reconciliation["r20Evidence"]
        if (
            r19_final["orderedParents"] != [terminal["commit"]]
            or r20_wip["orderedParents"] != [r19_final["commit"]]
            or r20_evidence["orderedParents"] != [r20_wip["commit"]]
        ):
            raise ManifestError("RECONCILIATION_ORDER_INVALID")
        terminal = r20_evidence
    if all(name in reconciliation for name in r21_names):
        r20_final = reconciliation["r20Final"]
        r21_wip = reconciliation["r21Wip"]
        r21_evidence = reconciliation["r21Evidence"]
        if (
            r20_final["orderedParents"] != [terminal["commit"]]
            or r21_wip["orderedParents"] != [r20_final["commit"]]
            or r21_evidence["orderedParents"] != [r21_wip["commit"]]
        ):
            raise ManifestError("RECONCILIATION_ORDER_INVALID")
        terminal = r21_evidence
    if treeish != ":":
        run = subprocess.run(
            ["git", "merge-base", "--is-ancestor", terminal["commit"], treeish],
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
