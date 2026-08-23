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
MANIFEST = "manifests/universal-provider-control-reconciliation-r29.json"
R29_MANIFEST = MANIFEST
R26_MANIFEST = "manifests/universal-provider-control-reconciliation-r26.json"
R33_MANIFEST = "manifests/universal-provider-control-reconciliation-r33.json"
R34_MANIFEST = "manifests/universal-provider-control-reconciliation-r34.json"
R35_MANIFEST = "manifests/universal-provider-control-reconciliation-r35.json"
R36_MANIFEST = "manifests/universal-provider-control-reconciliation-r36.json"
R37_MANIFEST = "manifests/universal-provider-control-reconciliation-r37.json"
R38_MANIFEST = "manifests/universal-provider-control-reconciliation-r38.json"
REVIEW_SCHEMA = "schemas/universal-provider-review-admission-v1.schema.json"
FROZEN_CANDIDATE = "e70a044f31dd2f43ab7c716d63a4eb89318c61b6"
FROZEN_R29 = "fc76bf6d5ab52891d06b7f71eb2e993e413c124c"
FROZEN_R33 = "8e20b4a1652931af178e792eb62ab892a7d309fd"
FROZEN_R34 = "6a3803fd1543c1bd0944ec0013987f053852e3c4"
FROZEN_R35 = "64e6895c332a696af238007225148fd70582424f"
FROZEN_R36 = "d67b0781e1e926e1baebdb0ea9b7a0ef5c447d85"
FROZEN_R37 = "6568230545e473c6fac64bcd30166a284e712704"
SELF_PATTERN = re.compile(
    rb'("canonicalGitBlobSha256"\s*:\s*"sha256:)([0-9a-f]{64})(")'
)


class ManifestError(ValueError):
    pass


R27_BASE = {
    "commit": "8c7dc4f4339db82a8b3c2efd689bf5f72631ad6e",
    "tree": "5dcc00a7f9723a00992458ab9dd0d6b0fd373363",
    "orderedParents": [
        "e4e7f9363185a5e10bb3a92167c785ef29caf2b7",
        "53a48a6a0be5eade253ce1a508872d6874fd474a",
    ],
    "orderedParentTrees": [
        "5233fa0515fcef7b69e70a007f25e6bb78190c42",
        "b8501a0a285a417a8f3f55fff515d074fd55dd81",
    ],
}
R27_SOURCE = {
    "repository": "https://github.com/layibabalola/Cloudvore.git",
    "commit": "46674bf7ba004dd6c4cac69d5a26369ab11106c4",
    "tree": "bef6f545f773157807e81dcf71305cb13a25382e",
    "orderedParents": ["8dcd3393f5541aa1f7fe181c3869f4262b6e1a00"],
    "subjectFiles": [
        {"ordinal": 0, "path": "tools/provider-capacity-governor-shadow/provenance/HUB-DESIGN-provider-capacity-governor-shadow-adoption-0818.md", "gitBlobOid": "b18a478694439efa86d2015ebe13b0c97bc9d5dc", "sha256": "sha256:e2a08fbccee3542449778d12d35c7e446dc56bef1cd898643bda7341842929a7", "bytes": 31133},
        {"ordinal": 1, "path": "knowledge/provider-capacity-governor-shadow-profile-v1.json", "gitBlobOid": "9bd11a136528cced1fc16430688d089a3f80a36c", "sha256": "sha256:90c45346bc83a145547086434876168e2aad4db7d1e2b1baf95a2c14e443ebf3", "bytes": 21559},
        {"ordinal": 2, "path": "knowledge/provider-capacity-governor-shadow-profile-v1.schema.json", "gitBlobOid": "330228c8df279a6ab528d30da2bc7db7c88db2bc", "sha256": "sha256:a3239addf3872f8b08ee92bfc052a8274901075d741e718d10ad1b0a066656bd", "bytes": 23483},
        {"ordinal": 3, "path": "knowledge/provider-capacity-governor-shadow-proposal-manifest-v1.json", "gitBlobOid": "95b3304c46fd13c232781e4d7fff9f533624ade4", "sha256": "sha256:cf7fc691d04fd40388a772947b68504ccfca57c96f13182f0ac6acf25e566d88", "bytes": 2999},
        {"ordinal": 4, "path": "knowledge/provider-capacity-governor-shadow-proposal-manifest-v1.schema.json", "gitBlobOid": "880f776756eb45c9deef608300ba76e9befbb493", "sha256": "sha256:9e4b546b225a69e31a964a3c5294a806389d6310fadcca60d07281c097b190bf", "bytes": 3857},
        {"ordinal": 5, "path": "knowledge/provider-capacity-governor-shadow-proposal-receipt-2026-08-18.md", "gitBlobOid": "455415489bc98ae11c77702941a6bf42655b0d60", "sha256": "sha256:8d2d67c984b57243f05453c0897a930d745f7fd07fa600a38f98242922e0034b", "bytes": 11088},
        {"ordinal": 6, "path": "tools/provider-capacity-governor-shadow.tests.py", "gitBlobOid": "98191265e2e6b1878c0189d3fca8249f728c6543", "sha256": "sha256:d8657641168135afe09bacee8d1f55666890b9da4ecd3ae8281ec1218041c675", "bytes": 45023},
    ],
}
R28_BASE = {
    "commit": "f94cec826f8e3979a028b6e45516077895c44905",
    "tree": "08479b324dfcc1925d0b11794ca86098625c9f48",
    "orderedParents": ["8c7dc4f4339db82a8b3c2efd689bf5f72631ad6e"],
    "orderedParentTrees": ["5dcc00a7f9723a00992458ab9dd0d6b0fd373363"],
}
R28_IDENTITY = {
    "provider": "anthropic", "model": "claude-fable-5", "effort": "max",
    "serviceTier": "standard", "transport": "firstParty",
    "role": "INDEPENDENT_ADVERSARIAL_REVIEWER",
    "question": (
        "Review the exact seven-file Cloudvore provider-governor proposal for security, doctrine "
        "conformance, quality preservation, and fail-closed resource admission; return PASS or "
        "actionable findings with file and failure scenario."
    ),
    "nativeMaxOutputTokens": 64000, "substitutionAllowed": False,
    "loweringRequiresAcceptedNonInferiority": True,
}
R29_BASE = {
    "commit": "f2f71c2ca93f6c9dec934100dbd760b5643463a2",
    "tree": "6b81f2d9e40cfaac3e6b3efa9bdef3fc884e819a",
    "orderedParents": ["f94cec826f8e3979a028b6e45516077895c44905"],
    "orderedParentTrees": ["08479b324dfcc1925d0b11794ca86098625c9f48"],
}
R29_IDENTITY = R28_IDENTITY
R29_POLICY_DIGEST = "sha256:e7e3fde383f43972796b681023ff92d9b35365e275e6fc00d84cc2735de00c60"
R34_POLICY_DIGEST = "sha256:ebec57daeca11108b2ba2771471b92d7bedfac64f58f321c7c1752a6f8339b5f"
R35_POLICY_DIGEST = R34_POLICY_DIGEST
R36_POLICY_DIGEST = R35_POLICY_DIGEST
R37_POLICY_DIGEST = R36_POLICY_DIGEST
R38_POLICY_DIGEST = R37_POLICY_DIGEST
R33_BASE = {
    "commit": "55afee85ecf720eb857cea1980f511f331b9e86f",
    "tree": "6e58f77467320d53ced12906bf2be62b4fca3d56",
    "orderedParents": [
        "fc76bf6d5ab52891d06b7f71eb2e993e413c124c",
        "1f96975233bfa794dd039610c072bf67aa1d20ff",
    ],
    "orderedParentTrees": [
        "ce91367dda0365218def5e42f4439decf81ba92a",
        "fc54c4f9cb53a3dc272767dd4713b99b662368b5",
    ],
}
R33_SUBJECT_PATHS = [
    "README.md",
    "RECONCILIATION.md",
    REVIEW_SCHEMA,
    "specs/fleet-universal-provider-control-reconciliation.md",
    "tests/test_universal_provider_control.py",
    "tools/check_universal_manifest.py",
    "tools/universal_provider_control.py",
]
R34_BASE = {
    "commit": "edcbf5084e1c9cbb3b7654c683b91185cef1494b",
    "tree": "5b84b927f214c8f4834a4f665d1f2beebc9176ee",
    "orderedParents": [
        "8e20b4a1652931af178e792eb62ab892a7d309fd",
        "8149c3f06811f85b833b28940017f2d05448cf5d",
    ],
    "orderedParentTrees": [
        "bb740bd9434b417cd66a568b762f13a047a11abc",
        "1a8193ae7f8c9982bfe499d039e5c85ae74ea907",
    ],
}
R34_SUBJECT_PATHS = R33_SUBJECT_PATHS
R35_BASE = {
    "commit": "fbf53f59c18b6dc8d1cc404730b0d42a38496a07",
    "tree": "750b031a6793cec63d7eeaaf05eeb6a6c52a80d7",
    "orderedParents": [
        "6a3803fd1543c1bd0944ec0013987f053852e3c4",
        "7ae14db4506fb2869f0e84647785865e504c9af8",
    ],
    "orderedParentTrees": [
        "52378a42695fbf1e9376995493972153c83ab2df",
        "64f23fbe78ee6159a63fca7ff175a2cb4440dadf",
    ],
}
R35_SUBJECT_PATHS = R34_SUBJECT_PATHS
R36_BASE = {
    "commit": "64e6895c332a696af238007225148fd70582424f",
    "tree": "4a0baf72d925349a30aeae785b10391e10102000",
    "orderedParents": ["fbf53f59c18b6dc8d1cc404730b0d42a38496a07"],
    "orderedParentTrees": ["750b031a6793cec63d7eeaaf05eeb6a6c52a80d7"],
}
R36_SUBJECT_PATHS = R35_SUBJECT_PATHS
R37_BASE = {
    "commit": "d67b0781e1e926e1baebdb0ea9b7a0ef5c447d85",
    "tree": "53d91a85bcd0a09ef7b349bed477f5aac1be93cc",
    "orderedParents": ["64e6895c332a696af238007225148fd70582424f"],
    "orderedParentTrees": ["4a0baf72d925349a30aeae785b10391e10102000"],
}
R37_SUBJECT_PATHS = R36_SUBJECT_PATHS
R38_BASE = {
    "commit": FROZEN_R37,
    "tree": "aa7338aad75cf4bb12481439a776c5c174fe1a94",
    "orderedParents": [FROZEN_R36],
    "orderedParentTrees": ["53d91a85bcd0a09ef7b349bed477f5aac1be93cc"],
}
R38_SUBJECT_PATHS = R37_SUBJECT_PATHS
FROZEN_MANIFEST_LAYERS = (
    (R26_MANIFEST, FROZEN_CANDIDATE),
    (R29_MANIFEST, FROZEN_R29),
    (R33_MANIFEST, FROZEN_R33),
    (R34_MANIFEST, FROZEN_R34),
    (R35_MANIFEST, FROZEN_R35),
    (R36_MANIFEST, FROZEN_R36),
    (R37_MANIFEST, FROZEN_R37),
)
CURRENT_MANIFEST = R38_MANIFEST


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


def _is_ancestor(ancestor: str, descendant: str) -> bool:
    run = subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant], cwd=ROOT,
        check=False, capture_output=True,
    )
    if run.returncode not in (0, 1):
        raise ManifestError("MANIFEST_ANCESTRY_UNAVAILABLE")
    return run.returncode == 0


def _frozen_manifest_bytes(
    treeish: str,
    manifest_path: str = R26_MANIFEST,
    candidate: str = FROZEN_CANDIDATE,
) -> bytes:
    """Bind a checked descendant to one literal immutable candidate manifest."""

    descendant = "HEAD" if treeish == ":" else treeish
    if not _is_ancestor(candidate, descendant):
        raise ManifestError("MANIFEST_CANDIDATE_NOT_ANCESTOR")
    frozen = _git(_blob_spec(candidate, manifest_path))
    current = _git(_blob_spec(treeish, manifest_path))
    assert isinstance(frozen, bytes)
    assert isinstance(current, bytes)
    if current != frozen or _oid(treeish, manifest_path) != _oid(candidate, manifest_path):
        raise ManifestError("MANIFEST_FROZEN_BLOB_MISMATCH")
    return frozen


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
    """Verify the exact R15-R26 linear subjects and ordered canonical-master merges."""

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
    r21_names = ("r20Final", "r21Wip", "r21Evidence", "r21Doctrine")
    r22_names = (
        "r21Final", "r22Wip", "r22CanonicalMaster", "r22MasterMerge", "r22Evidence",
        "r22ManifestFreeze", "r22Repair",
    )
    r23_names = ("r22Final", "r23Wip", "r23Evidence")
    r24_names = ("r23Final", "r24Wip", "r24Evidence")
    r25_names = (
        "r24Final", "r25Wip", "r25CanonicalMaster", "r25MasterMerge", "r25Evidence",
        "r25FinalPreLatestMaster", "r25LatestCanonicalMaster",
        "r25LatestMasterMerge", "r25LatestEvidence",
    )
    r26_names = ("r25Final", "r26Evidence")
    if all(name in reconciliation for name in r26_names):
        names = (
            base_names + r17_names + r18_names + r19_names + r20_names
            + r21_names + r22_names + r23_names + r24_names + r25_names + r26_names
        )
    elif all(name in reconciliation for name in r25_names):
        names = (
            base_names + r17_names + r18_names + r19_names + r20_names
            + r21_names + r22_names + r23_names + r24_names + r25_names
        )
    elif all(name in reconciliation for name in r24_names):
        names = (
            base_names + r17_names + r18_names + r19_names + r20_names
            + r21_names + r22_names + r23_names + r24_names
        )
    elif all(name in reconciliation for name in r23_names):
        names = (
            base_names + r17_names + r18_names + r19_names + r20_names
            + r21_names + r22_names + r23_names
        )
    elif all(name in reconciliation for name in r22_names):
        names = (
            base_names + r17_names + r18_names + r19_names + r20_names
            + r21_names + r22_names
        )
    elif all(name in reconciliation for name in r21_names):
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
        r21_doctrine = reconciliation["r21Doctrine"]
        if (
            r20_final["orderedParents"] != [terminal["commit"]]
            or r21_wip["orderedParents"] != [r20_final["commit"]]
            or r21_evidence["orderedParents"] != [r21_wip["commit"]]
            or r21_doctrine["orderedParents"] != [r21_evidence["commit"]]
        ):
            raise ManifestError("RECONCILIATION_ORDER_INVALID")
        terminal = r21_doctrine
    if all(name in reconciliation for name in r22_names):
        r21_final = reconciliation["r21Final"]
        r22_wip = reconciliation["r22Wip"]
        r22_master = reconciliation["r22CanonicalMaster"]
        r22_merge = reconciliation["r22MasterMerge"]
        r22_evidence = reconciliation["r22Evidence"]
        r22_manifest_freeze = reconciliation["r22ManifestFreeze"]
        r22_repair = reconciliation["r22Repair"]
        if (
            r21_final["orderedParents"] != [terminal["commit"]]
            or r22_wip["orderedParents"] != [r21_final["commit"]]
            or r22_merge["orderedParents"] != [r22_wip["commit"], r22_master["commit"]]
            or r22_evidence["orderedParents"] != [r22_merge["commit"]]
            or r22_manifest_freeze["orderedParents"] != [r22_evidence["commit"]]
            or r22_repair["orderedParents"] != [r22_manifest_freeze["commit"]]
        ):
            raise ManifestError("RECONCILIATION_ORDER_INVALID")
        terminal = r22_repair
    if all(name in reconciliation for name in r23_names):
        r22_final = reconciliation["r22Final"]
        r23_wip = reconciliation["r23Wip"]
        r23_evidence = reconciliation["r23Evidence"]
        if (
            r22_final["orderedParents"] != [terminal["commit"]]
            or r23_wip["orderedParents"] != [r22_final["commit"]]
            or r23_evidence["orderedParents"] != [r23_wip["commit"]]
        ):
            raise ManifestError("RECONCILIATION_ORDER_INVALID")
        terminal = r23_evidence
    if all(name in reconciliation for name in r24_names):
        r23_final = reconciliation["r23Final"]
        r24_wip = reconciliation["r24Wip"]
        r24_evidence = reconciliation["r24Evidence"]
        if (
            r23_final["orderedParents"] != [terminal["commit"]]
            or r24_wip["orderedParents"] != [r23_final["commit"]]
            or r24_evidence["orderedParents"] != [r24_wip["commit"]]
        ):
            raise ManifestError("RECONCILIATION_ORDER_INVALID")
        terminal = r24_evidence
    if all(name in reconciliation for name in r25_names):
        r24_final = reconciliation["r24Final"]
        r25_wip = reconciliation["r25Wip"]
        r25_master = reconciliation["r25CanonicalMaster"]
        r25_merge = reconciliation["r25MasterMerge"]
        r25_evidence = reconciliation["r25Evidence"]
        r25_final_pre_latest = reconciliation["r25FinalPreLatestMaster"]
        r25_latest_master = reconciliation["r25LatestCanonicalMaster"]
        r25_latest_merge = reconciliation["r25LatestMasterMerge"]
        r25_latest_evidence = reconciliation["r25LatestEvidence"]
        if (
            r24_final["orderedParents"] != [terminal["commit"]]
            or r25_wip["orderedParents"] != [r24_final["commit"]]
            or r25_merge["orderedParents"] != [r25_wip["commit"], r25_master["commit"]]
            or r25_evidence["orderedParents"] != [r25_merge["commit"]]
            or r25_final_pre_latest["orderedParents"] != [r25_evidence["commit"]]
            or r25_latest_merge["orderedParents"]
            != [r25_final_pre_latest["commit"], r25_latest_master["commit"]]
            or r25_latest_evidence["orderedParents"] != [r25_latest_merge["commit"]]
        ):
            raise ManifestError("RECONCILIATION_ORDER_INVALID")
        terminal = r25_latest_evidence
    if all(name in reconciliation for name in r26_names):
        r25_final = reconciliation["r25Final"]
        r26_evidence = reconciliation["r26Evidence"]
        if (
            r25_final["orderedParents"] != [terminal["commit"]]
            or r26_evidence["orderedParents"] != [r25_final["commit"]]
        ):
            raise ManifestError("RECONCILIATION_ORDER_INVALID")
        terminal = r26_evidence
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


def canonical_policy_sha256(policy: dict[str, Any]) -> str:
    raw = (
        json.dumps(
            policy, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
        ).encode("utf-8")
        + b"\n"
    )
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def verify_r33(manifest: dict[str, Any], treeish: str) -> None:
    """Verify the literal integration base and exact current R33 policy instance."""

    if (
        manifest.get("status") != "CANDIDATE_ZERO_AUTHORITY"
        or manifest.get("subjectCoverage")
        != "R33_CANONICAL_R31_R32_INTEGRATION_ZERO_AUTHORITY"
    ):
        raise ManifestError("R33_STATUS_INVALID")
    if manifest.get("candidateBase") != R33_BASE:
        raise ManifestError("R33_BASE_INVALID")
    tree, parents = _commit_tuple(R33_BASE["commit"])
    if tree != R33_BASE["tree"] or parents != R33_BASE["orderedParents"]:
        raise ManifestError("R33_BASE_OBJECT_MISMATCH")
    if [_commit_tuple(parent)[0] for parent in parents] != R33_BASE["orderedParentTrees"]:
        raise ManifestError("R33_BASE_PARENT_TREE_MISMATCH")
    descendant = "HEAD" if treeish == ":" else treeish
    if not _is_ancestor(R33_BASE["commit"], descendant):
        raise ManifestError("R33_BASE_NOT_ANCESTOR")
    if manifest.get("authority") != {
        "providerExecution": False, "processSpawnResumeKill": False,
        "containmentOrCanaryCredit": False, "automaticGateState": "CLOSED",
        "runtimeImplementation": "NOT_INSTALLED_UNCONDITIONAL_REFUSE",
        "activationRequiresSeparateAdjudication": True, "authorRecused": True,
    }:
        raise ManifestError("R33_AUTHORITY_INVALID")
    policy = manifest.get("reviewAdmissionPolicy")
    if not isinstance(policy, dict) or policy.get("source") != R27_SOURCE:
        raise ManifestError("R33_SOURCE_SUBJECT_MISMATCH")
    if policy.get("identity") != R29_IDENTITY:
        raise ManifestError("R33_EXACT_PROFILE_MISMATCH")
    if policy.get("capacity", {}).get("requiredQuotaWindows") != ["session", "weekly"]:
        raise ManifestError("R33_QUOTA_WINDOWS_MISMATCH")
    if (
        manifest.get("reviewAdmissionPolicyDigest") != R29_POLICY_DIGEST
        or canonical_policy_sha256(policy) != R29_POLICY_DIGEST
    ):
        raise ManifestError("R33_POLICY_DIGEST_MISMATCH")
    subjects = manifest.get("subjectFiles")
    if (
        not isinstance(subjects, list)
        or [subject.get("path") for subject in subjects if isinstance(subject, dict)]
        != R33_SUBJECT_PATHS
    ):
        raise ManifestError("R33_CARRIER_SUBJECT_MISMATCH")
    try:
        import jsonschema

        schema_raw = _git(_blob_spec(FROZEN_R33, REVIEW_SCHEMA))
        assert isinstance(schema_raw, bytes)
        schema = json.loads(schema_raw.decode("utf-8"), object_pairs_hook=_pairs)
        jsonschema.Draft202012Validator.check_schema(schema)
        if next(jsonschema.Draft202012Validator(schema).iter_errors(policy), None) is not None:
            raise ManifestError("R33_POLICY_SCHEMA_INVALID")
    except ManifestError:
        raise
    except Exception as exc:
        raise ManifestError("R33_POLICY_SCHEMA_INVALID") from exc
    if manifest.get("validation") != {
        "universalProviderControl": {"required": True, "claimedGreen": False},
        "providerCapacityGovernor": {"required": True, "claimedGreen": False},
        "canonicalCapacityControl": {"required": True, "claimedGreen": False},
        "hosted": {"requiredFresh": True, "claimedGreen": False},
        "providerInvocation": False,
        "activation": False,
    }:
        raise ManifestError("R33_VALIDATION_AUTHORITY_INVALID")


def verify_r34(manifest: dict[str, Any], treeish: str) -> None:
    """Verify the literal phase6-16 integration base and exact current R34 instance."""

    if (
        manifest.get("status") != "CANDIDATE_ZERO_AUTHORITY"
        or manifest.get("subjectCoverage")
        != "R34_CACHE_ADMISSION_CAPABILITY_REPAIR_ZERO_AUTHORITY"
    ):
        raise ManifestError("R34_STATUS_INVALID")
    if manifest.get("candidateBase") != R34_BASE:
        raise ManifestError("R34_BASE_INVALID")
    tree, parents = _commit_tuple(R34_BASE["commit"])
    if tree != R34_BASE["tree"] or parents != R34_BASE["orderedParents"]:
        raise ManifestError("R34_BASE_OBJECT_MISMATCH")
    if [_commit_tuple(parent)[0] for parent in parents] != R34_BASE["orderedParentTrees"]:
        raise ManifestError("R34_BASE_PARENT_TREE_MISMATCH")
    descendant = "HEAD" if treeish == ":" else treeish
    if not _is_ancestor(R34_BASE["commit"], descendant):
        raise ManifestError("R34_BASE_NOT_ANCESTOR")
    if manifest.get("authority") != {
        "providerExecution": False, "processSpawnResumeKill": False,
        "containmentOrCanaryCredit": False, "automaticGateState": "CLOSED",
        "runtimeImplementation": "NOT_INSTALLED_UNCONDITIONAL_REFUSE",
        "activationRequiresSeparateAdjudication": True, "authorRecused": True,
    }:
        raise ManifestError("R34_AUTHORITY_INVALID")
    policy = manifest.get("reviewAdmissionPolicy")
    if not isinstance(policy, dict) or policy.get("source") != R27_SOURCE:
        raise ManifestError("R34_SOURCE_SUBJECT_MISMATCH")
    if policy.get("identity") != R29_IDENTITY:
        raise ManifestError("R34_EXACT_PROFILE_MISMATCH")
    if policy.get("cacheAdmissionMode") != "EXACTLY_BOUNDED_AND_CHARGED":
        raise ManifestError("R34_CACHE_ADMISSION_MODE_MISMATCH")
    if policy.get("capacity", {}).get("requiredQuotaWindows") != ["session", "weekly"]:
        raise ManifestError("R34_QUOTA_WINDOWS_MISMATCH")
    if (
        manifest.get("reviewAdmissionPolicyDigest") != R34_POLICY_DIGEST
        or canonical_policy_sha256(policy) != R34_POLICY_DIGEST
    ):
        raise ManifestError("R34_POLICY_DIGEST_MISMATCH")
    subjects = manifest.get("subjectFiles")
    if (
        not isinstance(subjects, list)
        or [subject.get("path") for subject in subjects if isinstance(subject, dict)]
        != R34_SUBJECT_PATHS
    ):
        raise ManifestError("R34_CARRIER_SUBJECT_MISMATCH")
    try:
        import jsonschema

        schema_raw = _git(_blob_spec(treeish, REVIEW_SCHEMA))
        assert isinstance(schema_raw, bytes)
        schema = json.loads(schema_raw.decode("utf-8"), object_pairs_hook=_pairs)
        jsonschema.Draft202012Validator.check_schema(schema)
        if next(jsonschema.Draft202012Validator(schema).iter_errors(policy), None) is not None:
            raise ManifestError("R34_POLICY_SCHEMA_INVALID")
    except ManifestError:
        raise
    except Exception as exc:
        raise ManifestError("R34_POLICY_SCHEMA_INVALID") from exc
    if manifest.get("validation") != {
        "universalProviderControl": {"required": True, "claimedGreen": False},
        "providerCapacityGovernor": {"required": True, "claimedGreen": False},
        "canonicalCapacityControl": {"required": True, "claimedGreen": False},
        "hosted": {"requiredFresh": True, "claimedGreen": False},
        "providerInvocation": False,
        "activation": False,
    }:
        raise ManifestError("R34_VALIDATION_AUTHORITY_INVALID")


def verify_r35(manifest: dict[str, Any], treeish: str) -> None:
    """Verify the repaired-canonical integration base and exact current R35 instance."""

    if (
        manifest.get("status") != "CANDIDATE_ZERO_AUTHORITY"
        or manifest.get("subjectCoverage")
        != "R35_CANONICAL_CI_INTEGRATION_REBIND_ZERO_AUTHORITY"
    ):
        raise ManifestError("R35_STATUS_INVALID")
    if manifest.get("candidateBase") != R35_BASE:
        raise ManifestError("R35_BASE_INVALID")
    tree, parents = _commit_tuple(R35_BASE["commit"])
    if tree != R35_BASE["tree"] or parents != R35_BASE["orderedParents"]:
        raise ManifestError("R35_BASE_OBJECT_MISMATCH")
    if [_commit_tuple(parent)[0] for parent in parents] != R35_BASE["orderedParentTrees"]:
        raise ManifestError("R35_BASE_PARENT_TREE_MISMATCH")
    descendant = "HEAD" if treeish == ":" else treeish
    if not _is_ancestor(R35_BASE["commit"], descendant):
        raise ManifestError("R35_BASE_NOT_ANCESTOR")
    if manifest.get("authority") != {
        "providerExecution": False, "processSpawnResumeKill": False,
        "containmentOrCanaryCredit": False, "automaticGateState": "CLOSED",
        "runtimeImplementation": "NOT_INSTALLED_UNCONDITIONAL_REFUSE",
        "activationRequiresSeparateAdjudication": True, "authorRecused": True,
    }:
        raise ManifestError("R35_AUTHORITY_INVALID")
    policy = manifest.get("reviewAdmissionPolicy")
    if not isinstance(policy, dict) or policy.get("source") != R27_SOURCE:
        raise ManifestError("R35_SOURCE_SUBJECT_MISMATCH")
    if policy.get("identity") != R29_IDENTITY:
        raise ManifestError("R35_EXACT_PROFILE_MISMATCH")
    if policy.get("cacheAdmissionMode") != "EXACTLY_BOUNDED_AND_CHARGED":
        raise ManifestError("R35_CACHE_ADMISSION_MODE_MISMATCH")
    if policy.get("capacity", {}).get("requiredQuotaWindows") != ["session", "weekly"]:
        raise ManifestError("R35_QUOTA_WINDOWS_MISMATCH")
    if (
        manifest.get("reviewAdmissionPolicyDigest") != R35_POLICY_DIGEST
        or canonical_policy_sha256(policy) != R35_POLICY_DIGEST
    ):
        raise ManifestError("R35_POLICY_DIGEST_MISMATCH")
    subjects = manifest.get("subjectFiles")
    if (
        not isinstance(subjects, list)
        or [subject.get("path") for subject in subjects if isinstance(subject, dict)]
        != R35_SUBJECT_PATHS
    ):
        raise ManifestError("R35_CARRIER_SUBJECT_MISMATCH")
    try:
        import jsonschema

        schema_raw = _git(_blob_spec(treeish, REVIEW_SCHEMA))
        assert isinstance(schema_raw, bytes)
        schema = json.loads(schema_raw.decode("utf-8"), object_pairs_hook=_pairs)
        jsonschema.Draft202012Validator.check_schema(schema)
        if next(jsonschema.Draft202012Validator(schema).iter_errors(policy), None) is not None:
            raise ManifestError("R35_POLICY_SCHEMA_INVALID")
    except ManifestError:
        raise
    except Exception as exc:
        raise ManifestError("R35_POLICY_SCHEMA_INVALID") from exc
    if manifest.get("validation") != {
        "universalProviderControl": {"required": True, "claimedGreen": False},
        "providerCapacityGovernor": {"required": True, "claimedGreen": False},
        "canonicalCapacityControl": {"required": True, "claimedGreen": False},
        "hosted": {"requiredFresh": True, "claimedGreen": False},
        "providerInvocation": False,
        "activation": False,
    }:
        raise ManifestError("R35_VALIDATION_AUTHORITY_INVALID")


def verify_r36(manifest: dict[str, Any], treeish: str) -> None:
    """Verify exact R35 base and the current integer-boundary R36 instance."""

    if (
        manifest.get("status") != "CANDIDATE_ZERO_AUTHORITY"
        or manifest.get("subjectCoverage")
        != "R36_EXACT_REVIEW_CAPACITY_ARITHMETIC_ZERO_AUTHORITY"
    ):
        raise ManifestError("R36_STATUS_INVALID")
    if manifest.get("candidateBase") != R36_BASE:
        raise ManifestError("R36_BASE_INVALID")
    tree, parents = _commit_tuple(R36_BASE["commit"])
    if tree != R36_BASE["tree"] or parents != R36_BASE["orderedParents"]:
        raise ManifestError("R36_BASE_OBJECT_MISMATCH")
    if [_commit_tuple(parent)[0] for parent in parents] != R36_BASE["orderedParentTrees"]:
        raise ManifestError("R36_BASE_PARENT_TREE_MISMATCH")
    descendant = "HEAD" if treeish == ":" else treeish
    if not _is_ancestor(R36_BASE["commit"], descendant):
        raise ManifestError("R36_BASE_NOT_ANCESTOR")
    if manifest.get("authority") != {
        "providerExecution": False, "processSpawnResumeKill": False,
        "containmentOrCanaryCredit": False, "automaticGateState": "CLOSED",
        "runtimeImplementation": "NOT_INSTALLED_UNCONDITIONAL_REFUSE",
        "activationRequiresSeparateAdjudication": True, "authorRecused": True,
    }:
        raise ManifestError("R36_AUTHORITY_INVALID")
    policy = manifest.get("reviewAdmissionPolicy")
    if not isinstance(policy, dict) or policy.get("source") != R27_SOURCE:
        raise ManifestError("R36_SOURCE_SUBJECT_MISMATCH")
    if policy.get("identity") != R29_IDENTITY:
        raise ManifestError("R36_EXACT_PROFILE_MISMATCH")
    if policy.get("cacheAdmissionMode") != "EXACTLY_BOUNDED_AND_CHARGED":
        raise ManifestError("R36_CACHE_ADMISSION_MODE_MISMATCH")
    if policy.get("capacity", {}).get("requiredQuotaWindows") != ["session", "weekly"]:
        raise ManifestError("R36_QUOTA_WINDOWS_MISMATCH")
    if (
        manifest.get("reviewAdmissionPolicyDigest") != R36_POLICY_DIGEST
        or canonical_policy_sha256(policy) != R36_POLICY_DIGEST
    ):
        raise ManifestError("R36_POLICY_DIGEST_MISMATCH")
    subjects = manifest.get("subjectFiles")
    if (
        not isinstance(subjects, list)
        or [subject.get("path") for subject in subjects if isinstance(subject, dict)]
        != R36_SUBJECT_PATHS
    ):
        raise ManifestError("R36_CARRIER_SUBJECT_MISMATCH")
    try:
        import jsonschema

        schema_raw = _git(_blob_spec(treeish, REVIEW_SCHEMA))
        assert isinstance(schema_raw, bytes)
        schema = json.loads(schema_raw.decode("utf-8"), object_pairs_hook=_pairs)
        jsonschema.Draft202012Validator.check_schema(schema)
        if next(jsonschema.Draft202012Validator(schema).iter_errors(policy), None) is not None:
            raise ManifestError("R36_POLICY_SCHEMA_INVALID")
    except ManifestError:
        raise
    except Exception as exc:
        raise ManifestError("R36_POLICY_SCHEMA_INVALID") from exc
    if manifest.get("validation") != {
        "universalProviderControl": {"required": True, "claimedGreen": False},
        "providerCapacityGovernor": {"required": True, "claimedGreen": False},
        "canonicalCapacityControl": {"required": True, "claimedGreen": False},
        "hosted": {"requiredFresh": True, "claimedGreen": False},
        "providerInvocation": False,
        "activation": False,
    }:
        raise ManifestError("R36_VALIDATION_AUTHORITY_INVALID")


def verify_r37(manifest: dict[str, Any], treeish: str) -> None:
    """Verify exact adverse R36 base and the current frozen-layer R37 rebind."""

    if (
        manifest.get("status") != "CANDIDATE_ZERO_AUTHORITY"
        or manifest.get("subjectCoverage")
        != "R37_FROZEN_R36_FULL_MATRIX_REBIND_ZERO_AUTHORITY"
    ):
        raise ManifestError("R37_STATUS_INVALID")
    if manifest.get("candidateBase") != R37_BASE:
        raise ManifestError("R37_BASE_INVALID")
    tree, parents = _commit_tuple(R37_BASE["commit"])
    if tree != R37_BASE["tree"] or parents != R37_BASE["orderedParents"]:
        raise ManifestError("R37_BASE_OBJECT_MISMATCH")
    if [_commit_tuple(parent)[0] for parent in parents] != R37_BASE["orderedParentTrees"]:
        raise ManifestError("R37_BASE_PARENT_TREE_MISMATCH")
    descendant = "HEAD" if treeish == ":" else treeish
    if not _is_ancestor(R37_BASE["commit"], descendant):
        raise ManifestError("R37_BASE_NOT_ANCESTOR")
    if manifest.get("authority") != {
        "providerExecution": False, "processSpawnResumeKill": False,
        "containmentOrCanaryCredit": False, "automaticGateState": "CLOSED",
        "runtimeImplementation": "NOT_INSTALLED_UNCONDITIONAL_REFUSE",
        "activationRequiresSeparateAdjudication": True, "authorRecused": True,
    }:
        raise ManifestError("R37_AUTHORITY_INVALID")
    policy = manifest.get("reviewAdmissionPolicy")
    if not isinstance(policy, dict) or policy.get("source") != R27_SOURCE:
        raise ManifestError("R37_SOURCE_SUBJECT_MISMATCH")
    if policy.get("identity") != R29_IDENTITY:
        raise ManifestError("R37_EXACT_PROFILE_MISMATCH")
    if policy.get("cacheAdmissionMode") != "EXACTLY_BOUNDED_AND_CHARGED":
        raise ManifestError("R37_CACHE_ADMISSION_MODE_MISMATCH")
    if policy.get("capacity", {}).get("requiredQuotaWindows") != ["session", "weekly"]:
        raise ManifestError("R37_QUOTA_WINDOWS_MISMATCH")
    if (
        manifest.get("reviewAdmissionPolicyDigest") != R37_POLICY_DIGEST
        or canonical_policy_sha256(policy) != R37_POLICY_DIGEST
    ):
        raise ManifestError("R37_POLICY_DIGEST_MISMATCH")
    subjects = manifest.get("subjectFiles")
    if (
        not isinstance(subjects, list)
        or [subject.get("path") for subject in subjects if isinstance(subject, dict)]
        != R37_SUBJECT_PATHS
    ):
        raise ManifestError("R37_CARRIER_SUBJECT_MISMATCH")
    try:
        import jsonschema

        schema_raw = _git(_blob_spec(treeish, REVIEW_SCHEMA))
        assert isinstance(schema_raw, bytes)
        schema = json.loads(schema_raw.decode("utf-8"), object_pairs_hook=_pairs)
        jsonschema.Draft202012Validator.check_schema(schema)
        if next(jsonschema.Draft202012Validator(schema).iter_errors(policy), None) is not None:
            raise ManifestError("R37_POLICY_SCHEMA_INVALID")
    except ManifestError:
        raise
    except Exception as exc:
        raise ManifestError("R37_POLICY_SCHEMA_INVALID") from exc
    if manifest.get("validation") != {
        "universalProviderControl": {"required": True, "claimedGreen": False},
        "providerCapacityGovernor": {"required": True, "claimedGreen": False},
        "canonicalCapacityControl": {"required": True, "claimedGreen": False},
        "hosted": {"requiredFresh": True, "claimedGreen": False},
        "providerInvocation": False,
        "activation": False,
    }:
        raise ManifestError("R37_VALIDATION_AUTHORITY_INVALID")


def verify_r38(manifest: dict[str, Any], treeish: str) -> None:
    """Verify exact adverse R37 base and the lifecycle-safe R38 rebind."""

    if manifest.get("status") != "CANDIDATE_ZERO_AUTHORITY" or manifest.get(
        "subjectCoverage"
    ) != "R38_FROZEN_LAYER_LIFECYCLE_REBIND_ZERO_AUTHORITY":
        raise ManifestError("R38_STATUS_INVALID")
    if manifest.get("candidateBase") != R38_BASE:
        raise ManifestError("R38_BASE_INVALID")
    tree, parents = _commit_tuple(R38_BASE["commit"])
    if tree != R38_BASE["tree"] or parents != R38_BASE["orderedParents"]:
        raise ManifestError("R38_BASE_OBJECT_MISMATCH")
    if [_commit_tuple(parent)[0] for parent in parents] != R38_BASE["orderedParentTrees"]:
        raise ManifestError("R38_BASE_PARENT_TREE_MISMATCH")
    descendant = "HEAD" if treeish == ":" else treeish
    if not _is_ancestor(R38_BASE["commit"], descendant):
        raise ManifestError("R38_BASE_NOT_ANCESTOR")
    if manifest.get("authority") != {
        "providerExecution": False, "processSpawnResumeKill": False,
        "containmentOrCanaryCredit": False, "automaticGateState": "CLOSED",
        "runtimeImplementation": "NOT_INSTALLED_UNCONDITIONAL_REFUSE",
        "activationRequiresSeparateAdjudication": True, "authorRecused": True,
    }:
        raise ManifestError("R38_AUTHORITY_INVALID")
    policy = manifest.get("reviewAdmissionPolicy")
    if not isinstance(policy, dict) or policy.get("source") != R27_SOURCE:
        raise ManifestError("R38_SOURCE_SUBJECT_MISMATCH")
    if policy.get("identity") != R29_IDENTITY:
        raise ManifestError("R38_EXACT_PROFILE_MISMATCH")
    if policy.get("cacheAdmissionMode") != "EXACTLY_BOUNDED_AND_CHARGED":
        raise ManifestError("R38_CACHE_ADMISSION_MODE_MISMATCH")
    if policy.get("capacity", {}).get("requiredQuotaWindows") != ["session", "weekly"]:
        raise ManifestError("R38_QUOTA_WINDOWS_MISMATCH")
    if manifest.get("reviewAdmissionPolicyDigest") != R38_POLICY_DIGEST or canonical_policy_sha256(
        policy
    ) != R38_POLICY_DIGEST:
        raise ManifestError("R38_POLICY_DIGEST_MISMATCH")
    subjects = manifest.get("subjectFiles")
    if not isinstance(subjects, list) or [
        subject.get("path") for subject in subjects if isinstance(subject, dict)
    ] != R38_SUBJECT_PATHS:
        raise ManifestError("R38_CARRIER_SUBJECT_MISMATCH")
    try:
        import jsonschema
        schema_raw = _git(_blob_spec(treeish, REVIEW_SCHEMA))
        assert isinstance(schema_raw, bytes)
        schema = json.loads(schema_raw.decode("utf-8"), object_pairs_hook=_pairs)
        jsonschema.Draft202012Validator.check_schema(schema)
        if next(jsonschema.Draft202012Validator(schema).iter_errors(policy), None) is not None:
            raise ManifestError("R38_POLICY_SCHEMA_INVALID")
    except ManifestError:
        raise
    except Exception as exc:
        raise ManifestError("R38_POLICY_SCHEMA_INVALID") from exc
    if manifest.get("validation") != {
        "universalProviderControl": {"required": True, "claimedGreen": False},
        "providerCapacityGovernor": {"required": True, "claimedGreen": False},
        "canonicalCapacityControl": {"required": True, "claimedGreen": False},
        "hosted": {"requiredFresh": True, "claimedGreen": False},
        "providerInvocation": False, "activation": False,
    }:
        raise ManifestError("R38_VALIDATION_AUTHORITY_INVALID")


def verify_r29(
    manifest: dict[str, Any], treeish: str, *, verify_objects: bool = True
) -> None:
    """Verify R29 base, exact seven-row instance, generic schema, and zero authority."""

    if (
        manifest.get("status") != "CANDIDATE_ZERO_AUTHORITY"
        or manifest.get("subjectCoverage")
        != "R29_GENERIC_SUBJECT_CARDINALITY_REPAIR_ZERO_AUTHORITY"
    ):
        raise ManifestError("R29_STATUS_INVALID")
    if manifest.get("candidateBase") != R29_BASE:
        raise ManifestError("R29_BASE_INVALID")
    if verify_objects:
        tree, parents = _commit_tuple(R29_BASE["commit"])
        if tree != R29_BASE["tree"] or parents != R29_BASE["orderedParents"]:
            raise ManifestError("R29_BASE_OBJECT_MISMATCH")
        if [_commit_tuple(parent)[0] for parent in parents] != R29_BASE["orderedParentTrees"]:
            raise ManifestError("R29_BASE_PARENT_TREE_MISMATCH")
        if treeish != ":":
            run = subprocess.run(
                ["git", "merge-base", "--is-ancestor", R29_BASE["commit"], treeish],
                cwd=ROOT, check=False, capture_output=True,
            )
            if run.returncode != 0:
                raise ManifestError("R29_BASE_NOT_ANCESTOR")
    authority = manifest.get("authority")
    if authority != {
        "providerExecution": False, "processSpawnResumeKill": False,
        "containmentOrCanaryCredit": False, "automaticGateState": "CLOSED",
        "runtimeImplementation": "NOT_INSTALLED_UNCONDITIONAL_REFUSE",
        "activationRequiresSeparateAdjudication": True, "authorRecused": True,
    }:
        raise ManifestError("R29_AUTHORITY_INVALID")
    policy = manifest.get("reviewAdmissionPolicy")
    if not isinstance(policy, dict) or policy.get("source") != R27_SOURCE:
        raise ManifestError("R29_SOURCE_SUBJECT_MISMATCH")
    if policy.get("identity") != R29_IDENTITY:
        raise ManifestError("R29_EXACT_PROFILE_MISMATCH")
    if policy.get("capacity", {}).get("requiredQuotaWindows") != ["session", "weekly"]:
        raise ManifestError("R29_QUOTA_WINDOWS_MISMATCH")
    if manifest.get("reviewAdmissionPolicyDigest") != canonical_policy_sha256(policy):
        raise ManifestError("R29_POLICY_DIGEST_MISMATCH")
    try:
        import jsonschema

        schema_raw = _git(_blob_spec(FROZEN_R29, REVIEW_SCHEMA))
        assert isinstance(schema_raw, bytes)
        schema = json.loads(schema_raw.decode("utf-8"), object_pairs_hook=_pairs)
        jsonschema.Draft202012Validator.check_schema(schema)
        if next(jsonschema.Draft202012Validator(schema).iter_errors(policy), None) is not None:
            raise ManifestError("R29_POLICY_SCHEMA_INVALID")
    except ManifestError:
        raise
    except Exception as exc:
        raise ManifestError("R29_POLICY_SCHEMA_INVALID") from exc
    if manifest.get("validation") != {
        "universalProviderControl": {"required": True, "claimedGreen": False},
        "providerCapacityGovernor": {"required": True, "claimedGreen": False},
        "canonicalCapacityControl": {"required": True, "claimedGreen": False},
        "hosted": {"requiredFresh": True, "claimedGreen": False},
        "providerInvocation": False,
        "activation": False,
    }:
        raise ManifestError("R29_VALIDATION_AUTHORITY_INVALID")


def verify_r28(
    manifest: dict[str, Any], treeish: str, *, verify_objects: bool = True
) -> None:
    """Verify R28 base, exact external instance, canonical policy digest, and zero authority."""

    if (
        manifest.get("status") != "CANDIDATE_ZERO_AUTHORITY"
        or manifest.get("subjectCoverage")
        != "R28_PROVIDER_NEUTRAL_REVIEW_ADMISSION_REPAIR_ZERO_AUTHORITY"
    ):
        raise ManifestError("R28_STATUS_INVALID")
    if manifest.get("candidateBase") != R28_BASE:
        raise ManifestError("R28_BASE_INVALID")
    if verify_objects:
        tree, parents = _commit_tuple(R28_BASE["commit"])
        if tree != R28_BASE["tree"] or parents != R28_BASE["orderedParents"]:
            raise ManifestError("R28_BASE_OBJECT_MISMATCH")
        if [_commit_tuple(parent)[0] for parent in parents] != R28_BASE["orderedParentTrees"]:
            raise ManifestError("R28_BASE_PARENT_TREE_MISMATCH")
        if treeish != ":":
            run = subprocess.run(
                ["git", "merge-base", "--is-ancestor", R28_BASE["commit"], treeish],
                cwd=ROOT, check=False, capture_output=True,
            )
            if run.returncode != 0:
                raise ManifestError("R28_BASE_NOT_ANCESTOR")
    authority = manifest.get("authority")
    if authority != {
        "providerExecution": False, "processSpawnResumeKill": False,
        "containmentOrCanaryCredit": False, "automaticGateState": "CLOSED",
        "runtimeImplementation": "NOT_INSTALLED_UNCONDITIONAL_REFUSE",
        "activationRequiresSeparateAdjudication": True, "authorRecused": True,
    }:
        raise ManifestError("R28_AUTHORITY_INVALID")
    policy = manifest.get("reviewAdmissionPolicy")
    if not isinstance(policy, dict) or policy.get("source") != R27_SOURCE:
        raise ManifestError("R28_SOURCE_SUBJECT_MISMATCH")
    if policy.get("identity") != R28_IDENTITY:
        raise ManifestError("R28_EXACT_PROFILE_MISMATCH")
    if policy.get("capacity", {}).get("requiredQuotaWindows") != ["session", "weekly"]:
        raise ManifestError("R28_QUOTA_WINDOWS_MISMATCH")
    if manifest.get("reviewAdmissionPolicyDigest") != canonical_policy_sha256(policy):
        raise ManifestError("R28_POLICY_DIGEST_MISMATCH")
    try:
        import jsonschema

        schema_raw = _git(_blob_spec(treeish, REVIEW_SCHEMA))
        assert isinstance(schema_raw, bytes)
        schema = json.loads(schema_raw.decode("utf-8"), object_pairs_hook=_pairs)
        jsonschema.Draft202012Validator.check_schema(schema)
        if next(jsonschema.Draft202012Validator(schema).iter_errors(policy), None) is not None:
            raise ManifestError("R28_POLICY_SCHEMA_INVALID")
    except ManifestError:
        raise
    except Exception as exc:
        raise ManifestError("R28_POLICY_SCHEMA_INVALID") from exc
    if manifest.get("validation") != {
        "universalProviderControl": {"required": True, "claimedGreen": False},
        "providerCapacityGovernor": {"required": True, "claimedGreen": False},
        "canonicalCapacityControl": {"required": True, "claimedGreen": False},
        "hosted": {"requiredFresh": True, "claimedGreen": False},
        "providerInvocation": False,
        "activation": False,
    }:
        raise ManifestError("R28_VALIDATION_AUTHORITY_INVALID")


def verify_r27(manifest: dict[str, Any], treeish: str) -> None:
    """Verify the exact doctrine base, external R5 subject, strict policy, and zero authority."""

    if manifest.get("candidateBase") != R27_BASE:
        raise ManifestError("R27_BASE_INVALID")
    tree, parents = _commit_tuple(R27_BASE["commit"])
    if tree != R27_BASE["tree"] or parents != R27_BASE["orderedParents"]:
        raise ManifestError("R27_BASE_OBJECT_MISMATCH")
    if [_commit_tuple(parent)[0] for parent in parents] != R27_BASE["orderedParentTrees"]:
        raise ManifestError("R27_BASE_PARENT_TREE_MISMATCH")
    if treeish != ":":
        run = subprocess.run(
            ["git", "merge-base", "--is-ancestor", R27_BASE["commit"], treeish],
            cwd=ROOT, check=False, capture_output=True,
        )
        if run.returncode != 0:
            raise ManifestError("R27_BASE_NOT_ANCESTOR")
    authority = manifest.get("authority")
    if authority != {
        "providerExecution": False, "processSpawnResumeKill": False,
        "containmentOrCanaryCredit": False, "automaticGateState": "CLOSED",
        "runtimeImplementation": "NOT_INSTALLED_UNCONDITIONAL_REFUSE",
        "activationRequiresSeparateAdjudication": True, "authorRecused": True,
    }:
        raise ManifestError("R27_AUTHORITY_INVALID")
    policy = manifest.get("reviewAdmissionPolicy")
    if not isinstance(policy, dict) or policy.get("source") != R27_SOURCE:
        raise ManifestError("R27_SOURCE_SUBJECT_MISMATCH")
    try:
        import jsonschema

        schema_raw = _git(_blob_spec(treeish, REVIEW_SCHEMA))
        assert isinstance(schema_raw, bytes)
        schema = json.loads(schema_raw.decode("utf-8"), object_pairs_hook=_pairs)
        jsonschema.Draft202012Validator.check_schema(schema)
        if next(jsonschema.Draft202012Validator(schema).iter_errors(policy), None) is not None:
            raise ManifestError("R27_POLICY_SCHEMA_INVALID")
    except ManifestError:
        raise
    except (ImportError, UnicodeDecodeError, json.JSONDecodeError, Exception) as exc:
        raise ManifestError("R27_POLICY_SCHEMA_INVALID") from exc
    validation = manifest.get("validation")
    if not isinstance(validation, dict) or validation.get("providerInvocation") is not False:
        raise ManifestError("R27_VALIDATION_AUTHORITY_INVALID")
    if validation.get("activation") is not False or validation.get("hosted", {}).get("claimedGreen") is not False:
        raise ManifestError("R27_VALIDATION_AUTHORITY_INVALID")


def _parse_manifest(raw: bytes, expected_schema: str) -> dict[str, Any]:
    try:
        manifest = json.loads(raw.decode("utf-8", errors="strict"), object_pairs_hook=_pairs)
    except (UnicodeDecodeError, json.JSONDecodeError, ManifestError) as exc:
        raise ManifestError("MANIFEST_INVALID") from exc
    if manifest.get("schema") != expected_schema:
        raise ManifestError("MANIFEST_SCHEMA_INVALID")
    return manifest


def _verify_subjects_and_self(
    manifest: dict[str, Any], raw: bytes, *, manifest_path: str, candidate: str
) -> int:
    subjects = manifest.get("subjectFiles")
    if not isinstance(subjects, list) or not subjects:
        raise ManifestError("MANIFEST_SUBJECTS_INVALID")
    seen: set[str] = set()
    for subject in subjects:
        if not isinstance(subject, dict) or set(subject) != {"path", "gitBlobOid", "sha256", "bytes"}:
            raise ManifestError("MANIFEST_SUBJECT_INVALID")
        path = subject["path"]
        if not isinstance(path, str) or path in seen or path == manifest_path:
            raise ManifestError("MANIFEST_SUBJECT_INVALID")
        seen.add(path)
        blob = _git(_blob_spec(candidate, path))
        assert isinstance(blob, bytes)
        expected_sha = "sha256:" + hashlib.sha256(blob).hexdigest()
        if subject["sha256"] != expected_sha or subject["bytes"] != len(blob):
            raise ManifestError("MANIFEST_SUBJECT_MISMATCH")
        if subject["gitBlobOid"] != _oid(candidate, path):
            raise ManifestError("MANIFEST_BLOB_OID_MISMATCH")
    self_binding = manifest.get("manifestSelf")
    if not isinstance(self_binding, dict) or self_binding.get("path") != manifest_path:
        raise ManifestError("MANIFEST_SELF_INVALID")
    if self_binding.get("bytes") != len(raw):
        raise ManifestError("MANIFEST_SELF_SIZE_MISMATCH")
    expected_self = canonical_self_sha256(raw)
    if self_binding.get("canonicalGitBlobSha256") != expected_self:
        raise ManifestError("MANIFEST_SELF_MISMATCH")
    return len(subjects)


def check(treeish: str) -> int:
    r26_raw = _frozen_manifest_bytes(treeish, R26_MANIFEST, FROZEN_CANDIDATE)
    r26 = _parse_manifest(r26_raw, "fleet-universal-provider-control-candidate-manifest/v2")
    verify_reconciliation(r26, FROZEN_CANDIDATE)
    r26_subjects = _verify_subjects_and_self(
        r26, r26_raw, manifest_path=R26_MANIFEST, candidate=FROZEN_CANDIDATE
    )

    r29_raw = _frozen_manifest_bytes(treeish, R29_MANIFEST, FROZEN_R29)
    r29 = _parse_manifest(r29_raw, "fleet-universal-provider-control-candidate-manifest/v3")
    verify_r29(r29, FROZEN_R29)
    r29_subjects = _verify_subjects_and_self(
        r29, r29_raw, manifest_path=R29_MANIFEST, candidate=FROZEN_R29
    )

    r33_raw = _frozen_manifest_bytes(treeish, R33_MANIFEST, FROZEN_R33)
    r33 = _parse_manifest(r33_raw, "fleet-universal-provider-control-candidate-manifest/v3")
    verify_r33(r33, FROZEN_R33)
    r33_subjects = _verify_subjects_and_self(
        r33, r33_raw, manifest_path=R33_MANIFEST, candidate=FROZEN_R33
    )

    r34_raw = _frozen_manifest_bytes(treeish, R34_MANIFEST, FROZEN_R34)
    r34 = _parse_manifest(r34_raw, "fleet-universal-provider-control-candidate-manifest/v3")
    verify_r34(r34, FROZEN_R34)
    r34_subjects = _verify_subjects_and_self(
        r34, r34_raw, manifest_path=R34_MANIFEST, candidate=FROZEN_R34
    )

    r35_raw = _frozen_manifest_bytes(treeish, R35_MANIFEST, FROZEN_R35)
    r35 = _parse_manifest(r35_raw, "fleet-universal-provider-control-candidate-manifest/v3")
    verify_r35(r35, FROZEN_R35)
    r35_subjects = _verify_subjects_and_self(
        r35, r35_raw, manifest_path=R35_MANIFEST, candidate=FROZEN_R35
    )

    r36_raw = _frozen_manifest_bytes(treeish, R36_MANIFEST, FROZEN_R36)
    assert isinstance(r36_raw, bytes)
    r36 = _parse_manifest(r36_raw, "fleet-universal-provider-control-candidate-manifest/v3")
    verify_r36(r36, FROZEN_R36)
    r36_subjects = _verify_subjects_and_self(
        r36, r36_raw, manifest_path=R36_MANIFEST, candidate=FROZEN_R36
    )

    r37_raw = _frozen_manifest_bytes(treeish, R37_MANIFEST, FROZEN_R37)
    assert isinstance(r37_raw, bytes)
    r37 = _parse_manifest(r37_raw, "fleet-universal-provider-control-candidate-manifest/v3")
    verify_r37(r37, FROZEN_R37)
    r37_subjects = _verify_subjects_and_self(
        r37, r37_raw, manifest_path=R37_MANIFEST, candidate=FROZEN_R37
    )

    r38_raw = _git(_blob_spec(treeish, R38_MANIFEST))
    assert isinstance(r38_raw, bytes)
    r38 = _parse_manifest(r38_raw, "fleet-universal-provider-control-candidate-manifest/v3")
    verify_r38(r38, treeish)
    r38_subjects = _verify_subjects_and_self(
        r38, r38_raw, manifest_path=R38_MANIFEST, candidate=treeish
    )
    print(
        f"MANIFEST_PASS r26_subjects={r26_subjects} r29_subjects={r29_subjects} "
        f"r33_subjects={r33_subjects} r34_subjects={r34_subjects} "
        f"r35_subjects={r35_subjects} r36_subjects={r36_subjects} "
        f"r37_subjects={r37_subjects} r38_subjects={r38_subjects} self=PASS "
        f"candidates={FROZEN_CANDIDATE},{FROZEN_R29},{FROZEN_R33},"
        f"{FROZEN_R34},{FROZEN_R35},{FROZEN_R36},{FROZEN_R37},"
        f"{R38_BASE['commit']} checked={treeish}"
    )
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
