#!/usr/bin/env python3
"""Verify the linear, zero-authority Phase 10 local-review integration."""

from __future__ import annotations

import argparse
import ast
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PHASE9_COMMIT = "18b95fd82f92920117c8f0f432ae8e9bc5e8ffc8"
PHASE9_TREE = "fe0ed384bfd9485f4bbc4004225831c6aabe06a4"
PHASE9_PARENT = "2223647059cb789fd350883597756666357583df"
PHASE10_COMMIT = "940c790eedd118736ff0207c1b7dc407d5643802"
PHASE10_TREE = "9fe8b86a9408917a01e08564454e6c2a47b9952f"
RECEIPT_PATH = "adoption/phase10/r26-local-candidate-review-receipts.json"
RECEIPT_BLOB = "2f5d543754d35eb6e2f8143465e3ea2a1d1abffc"
RECEIPT_BYTES = 18080
RECEIPT_SHA256 = "6c9225317356d2975d97c75d3b4732cfd0f0a8bf14e78485110fd88bacecfcda"
LEDGER_PATH = "adoption/universal-token-control-r26.json"
LEDGER_BLOB = "333cc6d47e99a857b64150a87bd9f834590256e1"
MANIFEST_PATH = "manifests/universal-provider-control-reconciliation-r26.json"
MANIFEST_BLOB = "65901748c5843f05b37e4352c5b469e47804e2f1"
PHASE6_RECEIPT_PATH = "adoption/phase6/r26-local-candidate-review-receipts.json"
PHASE6_RECEIPT_BLOB = "c10b1b7530e0d9695118a02dd21842e4fc1493e0"
PHASE10_PROOF_PATHS = {
    "adoption/phase10/README.md",
    RECEIPT_PATH,
    "tests/test_phase10_integration.py",
    "tools/check_phase10_integration.py",
}
PREDECESSOR_CHECKERS = {
    "tools/check_phase2_disposition_batch.py": "ALLOWED_PHASE2_PATHS",
    "tools/check_phase3_disposition_batch.py": "ALLOWED_PHASE3_PATHS",
    "tools/check_phase5_stale_reconciliation.py": "ALLOWED_PHASE5_PATHS",
    "tools/check_phase6_candidate_reviews.py": "ALLOWED_PATHS",
    "tools/check_phase7_owner_publication_requests.py": "ALLOWED_PHASE7_PATHS",
}
EXPECTED_INTEGRATION_PATHS = PHASE10_PROOF_PATHS | {
    ".github/workflows/disposition-intake.yml",
    *PREDECESSOR_CHECKERS,
    "tools/check_phase8_integration.py",
    "tools/check_phase9_integration.py",
}
PHASE11_PROOF_PATHS = {
    "adoption/phase11/README.md",
    "adoption/phase11/r26-phase10-review-shape-closure.json",
    "tests/test_phase11_integration.py",
    "tools/check_phase11_integration.py",
}
PHASE11_FORWARD_PATHS = PHASE11_PROOF_PATHS | {
    ".github/workflows/disposition-intake.yml",
    "tools/check_phase2_disposition_batch.py",
    "tools/check_phase3_disposition_batch.py",
    "tools/check_phase5_stale_reconciliation.py",
    "tools/check_phase6_candidate_reviews.py",
    "tools/check_phase7_owner_publication_requests.py",
    "tools/check_phase8_integration.py",
    "tools/check_phase9_integration.py",
    "tools/check_phase10_integration.py",
}
EXPECTED_COUNTS = {"ADOPT": 0, "DISTINGUISH": 5, "MISSING": 0, "REJECT": 0, "STALE": 4}
EXPECTED_CAPTURE_FALSE = {
    "networkInspectionPerformed", "providerInvocationPerformed", "authenticationPerformed",
    "projectMutationPerformed", "runtimeMutationPerformed", "scheduledTaskMutationPerformed",
    "gateMutationPerformed", "leaseMutationPerformed", "packetMutationPerformed",
    "pushMergePublishPerformed",
}
EXPECTED_AUTHORITY_KEYS = {
    "projectDisposition", "projectAdoption", "fleetAdoption", "runtime", "activation",
    "provider", "authentication", "scheduler", "gate", "installation", "pushMergePublish",
}
EXPECTED_R8_AUTHORITY_KEYS = EXPECTED_AUTHORITY_KEYS | {"apply", "privilegedPreview"}
SHA40 = re.compile(r"[0-9a-f]{40}")
SHA64 = re.compile(r"[0-9a-f]{64}")


class Phase10Error(ValueError):
    pass


def _clean_git_env() -> dict[str, str]:
    environment = os.environ.copy()
    for key in tuple(environment):
        if key in {
            "GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_OBJECT_DIRECTORY",
            "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_REPLACE_REF_BASE", "GIT_INDEX_FILE",
            "GIT_NAMESPACE", "GIT_CEILING_DIRECTORIES", "GIT_EXEC_PATH",
        } or key.startswith("GIT_CONFIG"):
            environment.pop(key, None)
    return environment


def _git(args: list[str], *, root: Path = ROOT, text: bool = False,
         error: str = "GIT_OBJECT_UNAVAILABLE") -> bytes | str:
    run = subprocess.run(
        ["git", *args], cwd=root, env=_clean_git_env(), check=False, capture_output=True,
        text=text, encoding="utf-8" if text else None,
    )
    if run.returncode != 0:
        raise Phase10Error(error)
    return run.stdout


def _blob_spec(treeish: str, path: str) -> str:
    return f":{path}" if treeish == ":" else f"{treeish}:{path}"


def _blob(treeish: str, path: str) -> bytes:
    return _git(["show", _blob_spec(treeish, path)], error="GIT_BLOB_UNAVAILABLE")  # type: ignore[return-value]


def _oid(treeish: str, path: str) -> str:
    value = str(_git(["rev-parse", _blob_spec(treeish, path)], text=True, error="GIT_BLOB_OID_UNAVAILABLE")).strip()
    if SHA40.fullmatch(value) is None:
        raise Phase10Error("GIT_BLOB_OID_INVALID")
    return value


def _commit_tuple(commit: str) -> tuple[str, list[str]]:
    value = str(_git(["show", "-s", "--format=%T%n%P", commit], text=True, error="COMMIT_UNAVAILABLE"))
    lines = value.splitlines()
    if len(lines) != 2 or SHA40.fullmatch(lines[0]) is None:
        raise Phase10Error("COMMIT_INVALID")
    parents = lines[1].split() if lines[1] else []
    if any(SHA40.fullmatch(parent) is None for parent in parents):
        raise Phase10Error("COMMIT_INVALID")
    return lines[0], parents


def _changed_paths(base: str, treeish: str) -> set[str]:
    args = ["diff", "--cached", "--name-only", base] if treeish == ":" else ["diff", "--name-only", f"{base}..{treeish}"]
    return set(str(_git(args, text=True, error="INTEGRATION_DIFF_UNAVAILABLE")).splitlines())


def _tree_paths(treeish: str, prefix: str) -> set[str]:
    args = ["ls-files", prefix] if treeish == ":" else ["ls-tree", "-r", "--name-only", treeish, prefix]
    return set(str(_git(args, text=True, error="TREE_CENSUS_UNAVAILABLE")).splitlines())


def _exact_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise Phase10Error("DUPLICATE_JSON_KEY")
        result[key] = value
    return result


def load_json(raw: bytes) -> dict[str, Any]:
    try:
        value = json.loads(raw.decode("utf-8", errors="strict"), object_pairs_hook=_exact_object)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise Phase10Error("JSON_INVALID") from exc
    if not isinstance(value, dict):
        raise Phase10Error("JSON_ROOT_INVALID")
    return value


def _load_json(treeish: str, path: str) -> dict[str, Any]:
    return load_json(_blob(treeish, path))


def _exact_keys(value: Any, keys: list[str], error: str) -> None:
    if not isinstance(value, dict) or list(value) != keys:
        raise Phase10Error(error)


def _exact_equal(actual: Any, expected: Any, error: str) -> None:
    if type(actual) is not type(expected):
        raise Phase10Error(error)
    if isinstance(expected, dict):
        if list(actual) != list(expected):
            raise Phase10Error(error)
        for key in expected:
            _exact_equal(actual[key], expected[key], error)
    elif isinstance(expected, list):
        if len(actual) != len(expected):
            raise Phase10Error(error)
        for left, right in zip(actual, expected, strict=True):
            _exact_equal(left, right, error)
    elif actual != expected:
        raise Phase10Error(error)


def _ast_value(node: ast.AST, env: dict[str, Any]) -> Any:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Name) and node.id in env:
        return env[node.id]
    if isinstance(node, ast.Set):
        values = {_ast_value(item, env) for item in node.elts}
        if not all(isinstance(value, str) for value in values):
            raise Phase10Error("ALLOWLIST_AST_INVALID")
        return values
    if isinstance(node, ast.JoinedStr):
        parts: list[str] = []
        for item in node.values:
            if isinstance(item, ast.Constant) and isinstance(item.value, str):
                parts.append(item.value)
            elif isinstance(item, ast.FormattedValue):
                value = _ast_value(item.value, env)
                if not isinstance(value, str):
                    raise Phase10Error("ALLOWLIST_AST_INVALID")
                parts.append(value)
            else:
                raise Phase10Error("ALLOWLIST_AST_UNSUPPORTED")
        return "".join(parts)
    if isinstance(node, ast.SetComp) and len(node.generators) == 1:
        generator = node.generators[0]
        if generator.ifs or generator.is_async or not isinstance(generator.target, ast.Name):
            raise Phase10Error("ALLOWLIST_AST_UNSUPPORTED")
        source = _ast_value(generator.iter, env)
        if not isinstance(source, set) or not all(isinstance(value, str) for value in source):
            raise Phase10Error("ALLOWLIST_AST_INVALID")
        values: set[str] = set()
        for value in source:
            local = dict(env)
            local[generator.target.id] = value
            rendered = _ast_value(node.elt, local)
            if not isinstance(rendered, str):
                raise Phase10Error("ALLOWLIST_AST_INVALID")
            values.add(rendered)
        return values
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        left, right = _ast_value(node.left, env), _ast_value(node.right, env)
        if not isinstance(left, set) or not isinstance(right, set):
            raise Phase10Error("ALLOWLIST_AST_INVALID")
        return left | right
    raise Phase10Error("ALLOWLIST_AST_UNSUPPORTED")


def _assignment_set(treeish: str, path: str, name: str) -> set[str]:
    try:
        parsed = ast.parse(_blob(treeish, path).decode("utf-8", errors="strict"))
    except (SyntaxError, UnicodeDecodeError) as exc:
        raise Phase10Error("ALLOWLIST_SOURCE_INVALID") from exc
    env: dict[str, Any] = {}
    for node in parsed.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
            continue
        try:
            env[node.targets[0].id] = _ast_value(node.value, env)
        except Phase10Error:
            continue
    value = env.get(name)
    if not isinstance(value, set) or not value:
        raise Phase10Error("ALLOWLIST_ASSIGNMENT_INVALID")
    return value


def _review(batch: dict[str, Any], project_id: str) -> dict[str, Any]:
    reviews = batch.get("reviews")
    if not isinstance(reviews, list):
        raise Phase10Error("REVIEWS_INVALID")
    matches = [row for row in reviews if isinstance(row, dict) and row.get("projectId") == project_id]
    if len(matches) != 1:
        raise Phase10Error("REVIEW_IDENTITY_INVALID")
    return matches[0]


def _verify_authority(review: dict[str, Any], *, r8: bool = False) -> None:
    authority = review.get("authority")
    expected = EXPECTED_R8_AUTHORITY_KEYS if r8 else EXPECTED_AUTHORITY_KEYS
    if not isinstance(authority, dict) or set(authority) != expected:
        raise Phase10Error("AUTHORITY_KEYS_INVALID")
    if any(type(value) is not bool or value is not False for value in authority.values()):
        raise Phase10Error("AUTHORITY_OVERCLAIM")
    treatment = review.get("dispositionTreatment")
    if not isinstance(treatment, dict):
        raise Phase10Error("DISPOSITION_TREATMENT_INVALID")
    for key in (
        "ledgerStatusChangeAuthorized", "publicationAuthority", "adoptionCredit", "installationCredit"
    ):
        if treatment.get(key) is not False:
            raise Phase10Error("DISPOSITION_TREATMENT_INVALID")


def verify_receipt_shape(batch: dict[str, Any]) -> None:
    _exact_keys(batch, ["schema", "status", "frozenBase", "capture", "summary", "reviews"], "ROOT_KEYS_INVALID")
    if batch["schema"] != "fleet-r26-phase10-local-candidate-review-batch/v1" or batch["status"] != "AUTHOR_CONFLICTED_INDEPENDENT_REVIEW_REQUIRED":
        raise Phase10Error("RECEIPT_HEADER_INVALID")
    _exact_equal(batch["frozenBase"], {
        "phase9Commit": PHASE9_COMMIT, "phase9Tree": PHASE9_TREE, "phase9Parent": PHASE9_PARENT,
        "ledgerPath": LEDGER_PATH, "ledgerGitBlobOid": LEDGER_BLOB,
        "manifestPath": MANIFEST_PATH, "manifestGitBlobOid": MANIFEST_BLOB,
        "phase6ReceiptPath": PHASE6_RECEIPT_PATH, "phase6ReceiptGitBlobOid": PHASE6_RECEIPT_BLOB,
    }, "FROZEN_BASE_INVALID")
    capture = batch["capture"]
    _exact_keys(capture, [
        "reviewedAt", "machine", "reviewer", "reviewMode", "networkInspectionPerformed",
        "providerInvocationPerformed", "authenticationPerformed", "projectMutationPerformed",
        "runtimeMutationPerformed", "scheduledTaskMutationPerformed", "gateMutationPerformed",
        "leaseMutationPerformed", "packetMutationPerformed", "pushMergePublishPerformed",
    ], "CAPTURE_KEYS_INVALID")
    if set(capture) - {"reviewedAt", "machine", "reviewer", "reviewMode"} != EXPECTED_CAPTURE_FALSE:
        raise Phase10Error("CAPTURE_KEYS_INVALID")
    if any(capture[key] is not False for key in EXPECTED_CAPTURE_FALSE):
        raise Phase10Error("CAPTURE_AUTHORITY_OVERCLAIM")
    summary = batch["summary"]
    expected_summary = {
        "reviewCount": 3, "acceptedCandidateEvidenceScopes": 3, "candidateOnlyCensusAccepts": 1,
        "nonInstallableClosedStopAccepts": 1, "privilegedPreviewCandidateAccepts": 1,
        "ledgerStatusChangesAuthorized": 0, "adoptionClaims": 0, "installationClaims": 0,
        "runtimeAuthorityClaims": 0, "canonicalLedgerCounts": EXPECTED_COUNTS,
    }
    _exact_equal(summary, expected_summary, "SUMMARY_INVALID")
    reviews = batch["reviews"]
    if not isinstance(reviews, list) or [row.get("projectId") for row in reviews if isinstance(row, dict)] != [
        "mlv-app", "cloudvore", "dng-auto-processor"
    ]:
        raise Phase10Error("REVIEWS_INVALID")

    mlv = _review(batch, "mlv-app")
    if mlv.get("verdict") != "ACCEPT_CANDIDATE_ONLY_CENSUS" or mlv.get("evidenceKind") != "LAUNCHER_ACTION_GRAPH_CENSUS_CANDIDATE_ONLY":
        raise Phase10Error("MLV_VERDICT_INVALID")
    evidence = mlv.get("executionEvidence")
    if not isinstance(evidence, list) or len(evidence) != 1 or evidence[0].get("exitCode") != 0 or evidence[0].get("hostileControlsPassed") != 53 or evidence[0].get("hostileControlsTotal") != 53:
        raise Phase10Error("MLV_EXECUTION_EVIDENCE_INVALID")
    diagnostic = mlv.get("unpersistedIndependentReviewDiagnostic")
    _exact_equal(diagnostic, {
        "reportedResult": "15/15 PASS", "artifactPersisted": False, "artifactCredit": False,
        "evidenceTreatment": "UNPERSISTED_REVIEW_DIAGNOSTIC_NO_ARTIFACT_CREDIT",
        "replacement": "EQUIVALENT_SUBSTITUTION_HOSTILES_ARE_COMMITTED_IN_TEST_PHASE10_INTEGRATION",
    }, "MLV_UNPERSISTED_DIAGNOSTIC_INVALID")
    if mlv.get("semanticFindings", {}).get("networkVerified") is not False:
        raise Phase10Error("MLV_NETWORK_OVERCLAIM")
    _verify_authority(mlv)

    cloud = _review(batch, "cloudvore")
    if cloud.get("verdict") != "ACCEPT_NON_INSTALLABLE_CLOSED_STOP_CANDIDATE" or cloud.get("evidenceKind") != "NON_INSTALLABLE_CLOSED_STOP_SOURCE_CANDIDATE":
        raise Phase10Error("CLOUDVORE_VERDICT_INVALID")
    executions = cloud.get("executionEvidence")
    if not isinstance(executions, list) or [(row.get("testCasesPassed"), row.get("testCasesTotal"), row.get("exitCode")) for row in executions] != [(17, 17, 0), (21, 21, 0)]:
        raise Phase10Error("CLOUDVORE_EXECUTION_EVIDENCE_INVALID")
    bindings = cloud.get("keyBindings")
    if not isinstance(bindings, dict) or bindings.get("gateState") != "CLOSED" or bindings.get("providerProcessCanStart") is not False or bindings.get("candidateInstallable") is not False or bindings.get("trackedArtifactIsInstalledManifest") is not False:
        raise Phase10Error("CLOUDVORE_KEY_BINDING_INVALID")
    findings = cloud.get("semanticFindings")
    if not isinstance(findings, dict) or findings.get("candidateStatus") != "SOURCE_CANDIDATE_CLOSED_STOP_BOUNDARY_NOT_INSTALLABLE" or findings.get("executableInstallerPresent") is not False or findings.get("transactionImplemented") is not False:
        raise Phase10Error("CLOUDVORE_SEMANTIC_INVALID")
    _verify_authority(cloud)

    r8 = _review(batch, "dng-auto-processor")
    if r8.get("verdict") != "ACCEPT_INSTALL_CANDIDATE_FOR_SEPARATE_PRIVILEGED_PREVIEW":
        raise Phase10Error("R8_VERDICT_INVALID")
    subject = r8.get("subject")
    if not isinstance(subject, dict) or subject.get("manifestBytes") != 11616 or subject.get("manifestSha256") != "fd81969894233ede9ef625771f115b9b0581808ad511d5b9b0dbb3563c2b9b8f" or subject.get("treeSha256") != "75a856c2c425a1aa98fc5de61ea977913159d40e1a6bc1fe9eddbeb67ceb6c38" or subject.get("r7TreeSha256") != "fb6f3811d876bd9538695530caeeee275618f90574db3437796f8f9020ed9629":
        raise Phase10Error("R8_SUBJECT_INVALID")
    suites = r8.get("independentExecutionEvidence")
    if not isinstance(suites, list) or [(row.get("assertionsPerRun"), row.get("result")) for row in suites] != [(121, "PASS"), (21, "PASS"), (12, "PASS"), (13, "PASS"), (20, "PASS"), (21, "PASS"), (11, "PASS")]:
        raise Phase10Error("R8_SUITE_EVIDENCE_INVALID")
    preview = r8.get("productionPreview")
    if not isinstance(preview, dict) or preview.get("result") != "BLOCKED_CURRENT_TOKEN_SCHEDULED_TASK_READ_ACCESS_DENIED" or preview.get("exitCode") != 1 or preview.get("beforeFingerprintSha256") != preview.get("afterFingerprintSha256") or preview.get("persistentTargetWrites") != 0 or preview.get("scheduledTaskChanges") != 0 or preview.get("successfulPrivilegedPreviewClaimed") is not False:
        raise Phase10Error("R8_PREVIEW_EVIDENCE_INVALID")
    absence = r8.get("absenceDefectClosure")
    if not isinstance(absence, dict) or absence.get("library") != {"Present": False, "Bytes": 0, "Hash": None, "preimagePresent": False} or absence.get("clear") != {"Present": False, "Bytes": 0, "Hash": None, "preimagePresent": False} or absence.get("receiptFrozenPriorAbsence") != {"library": True, "clear": True} or absence.get("restartValidationCarriesLaw") is not True:
        raise Phase10Error("R8_ABSENCE_CLOSURE_INVALID")
    treatment = r8.get("dispositionTreatment")
    if not isinstance(treatment, dict) or treatment.get("applyAuthorized") is not False or treatment.get("privilegedPreviewAuthorizedByReceipt") is not False:
        raise Phase10Error("R8_SCOPE_OVERCLAIM")
    _verify_authority(r8, r8=True)


def _verify_local_git_subject(review: dict[str, Any], error_prefix: str) -> None:
    subject = review.get("subject")
    artifacts = review.get("artifacts")
    if not isinstance(subject, dict) or not isinstance(artifacts, list):
        raise Phase10Error(f"{error_prefix}_SUBJECT_INVALID")
    root = Path(subject["localRoot"])
    if not root.is_dir():
        raise Phase10Error(f"{error_prefix}_ROOT_UNAVAILABLE")
    top = str(_git(["rev-parse", "--show-toplevel"], root=root, text=True, error=f"{error_prefix}_ROOT_UNAVAILABLE")).strip()
    if Path(top).resolve() != root.resolve():
        raise Phase10Error(f"{error_prefix}_ROOT_MISMATCH")
    head = str(_git(["rev-parse", "--verify", "HEAD^{commit}"], root=root, text=True)).strip()
    tree = str(_git(["show", "-s", "--format=%T", head], root=root, text=True)).strip()
    parents = str(_git(["show", "-s", "--format=%P", head], root=root, text=True)).strip().split()
    branch = str(_git(["branch", "--show-current"], root=root, text=True)).strip()
    remote = str(_git(["remote", "get-url", "origin"], root=root, text=True)).strip()
    status = str(_git(["status", "--porcelain=v1", "--untracked-files=all"], root=root, text=True))
    changed = str(_git(["diff-tree", "--no-commit-id", "--name-only", "-r", head], root=root, text=True)).splitlines()
    if head != subject.get("commit") or tree != subject.get("tree") or parents != [subject.get("parent")] or branch != subject.get("localBranch") or remote != subject.get("remote") or status != "" or changed != subject.get("changedPaths"):
        raise Phase10Error(f"{error_prefix}_SUBJECT_MISMATCH")
    remote_refs = str(_git(["for-each-ref", f"--contains={head}", "--format=%(refname)", "refs/remotes"], root=root, text=True)).splitlines()
    if subject.get("networkRemoteVerified") is not False or subject.get("remoteTrackingRefContainsSubject") is not False or remote_refs:
        raise Phase10Error(f"{error_prefix}_NETWORK_BINDING_INVALID")
    for artifact in artifacts:
        if not isinstance(artifact, dict) or list(artifact) != ["path", "gitBlobOid", "bytes", "sha256"]:
            raise Phase10Error(f"{error_prefix}_ARTIFACT_SHAPE_INVALID")
        path = artifact["path"]
        data = _git(["show", f"{head}:{path}"], root=root, error=f"{error_prefix}_ARTIFACT_UNAVAILABLE")
        oid = str(_git(["rev-parse", f"{head}:{path}"], root=root, text=True)).strip()
        if oid != artifact["gitBlobOid"] or len(data) != artifact["bytes"] or hashlib.sha256(data).hexdigest() != artifact["sha256"]:
            raise Phase10Error(f"{error_prefix}_ARTIFACT_MISMATCH")


def _r8_tree_hash(root: Path) -> tuple[int, str]:
    rows: list[str] = []
    files = sorted((path for path in root.iterdir() if path.is_file()), key=lambda path: path.name.casefold())
    for path in files:
        data = path.read_bytes()
        rows.append(f"{path.name}|{len(data)}|{hashlib.sha256(data).hexdigest().upper()}")
    return len(files), hashlib.sha256("\n".join(rows).encode("utf-8")).hexdigest()


def _verify_r8_local(review: dict[str, Any]) -> None:
    subject = review["subject"]
    root = Path(subject["localRoot"])
    if not root.is_dir() or root.is_symlink():
        raise Phase10Error("R8_ROOT_UNAVAILABLE")
    manifest_path = root / subject["manifestPath"]
    raw = manifest_path.read_bytes()
    if len(raw) != subject["manifestBytes"] or hashlib.sha256(raw).hexdigest() != subject["manifestSha256"]:
        raise Phase10Error("R8_MANIFEST_MISMATCH")
    manifest = load_json(raw)
    if manifest.get("schema") != "dng-candidate-manifest.v7" or manifest.get("candidate") != "durable-campaign-hold-latch-r8" or manifest.get("status") != "FROZEN_AUTHOR_CONFLICTED":
        raise Phase10Error("R8_MANIFEST_HEADER_INVALID")
    authority = manifest.get("authority")
    if not isinstance(authority, dict) or not authority or any(value is not False for value in authority.values()):
        raise Phase10Error("R8_MANIFEST_AUTHORITY_OVERCLAIM")
    subjects, metadata, bundles = manifest.get("subjects"), manifest.get("metadata"), manifest.get("static_review_bundles")
    if not isinstance(subjects, list) or not isinstance(metadata, list) or not isinstance(bundles, list):
        raise Phase10Error("R8_MANIFEST_ROWS_INVALID")
    if len(subjects) != subject["subjectCount"] or len(metadata) != subject["metadataCount"] or len(bundles) != subject["staticReviewBundleCount"]:
        raise Phase10Error("R8_MANIFEST_COUNT_MISMATCH")
    declared = {subject["manifestPath"]}
    for row in [*subjects, *metadata]:
        if not isinstance(row, dict) or set(row) != {"path", "bytes", "sha256"}:
            raise Phase10Error("R8_MANIFEST_ROW_INVALID")
        path = root / row["path"]
        if path.parent != root or not path.is_file() or path.is_symlink():
            raise Phase10Error("R8_MANIFEST_PATH_INVALID")
        data = path.read_bytes()
        try:
            data.decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            raise Phase10Error("R8_SUBJECT_UTF8_INVALID") from exc
        if len(data) != row["bytes"] or hashlib.sha256(data).hexdigest().upper() != row["sha256"]:
            raise Phase10Error("R8_SUBJECT_TUPLE_MISMATCH")
        declared.add(row["path"])
    actual = {path.name for path in root.iterdir() if path.is_file()}
    if actual != declared:
        raise Phase10Error("R8_CLOSED_SET_MISMATCH")
    limits = manifest.get("static_limits")
    if limits != {"subject_max_bytes": 24576, "bundle_max_bytes": 32768, "exact_sum_verifier": "test-static-bundle-sums.ps1"}:
        raise Phase10Error("R8_STATIC_LIMITS_INVALID")
    if max(row["bytes"] for row in subjects) != subject["largestSubjectBytes"] or any(row["bytes"] > limits["subject_max_bytes"] for row in subjects):
        raise Phase10Error("R8_SUBJECT_LIMIT_INVALID")
    sizes = {row["path"]: row["bytes"] for row in subjects}
    sums = [sum(sizes[path] for path in bundle["paths"]) for bundle in bundles]
    if any(total != bundle["bytes"] for total, bundle in zip(sums, bundles, strict=True)) or max(sums) != subject["largestBundleBytes"] or any(total > limits["bundle_max_bytes"] for total in sums):
        raise Phase10Error("R8_BUNDLE_LIMIT_INVALID")
    count, tree_hash = _r8_tree_hash(root)
    if count != subject["treeFileCount"] or tree_hash != subject["treeSha256"]:
        raise Phase10Error("R8_TREE_MISMATCH")
    manifest_rows = {row["path"]: row for row in subjects}
    for row in review["criticalArtifacts"]:
        expected = manifest_rows.get(row["path"])
        if expected is None or expected["bytes"] != row["bytes"] or expected["sha256"].lower() != row["sha256"]:
            raise Phase10Error("R8_CRITICAL_ARTIFACT_MISMATCH")


def verify_local_subjects(batch: dict[str, Any]) -> None:
    _verify_local_git_subject(_review(batch, "mlv-app"), "MLV")
    _verify_local_git_subject(_review(batch, "cloudvore"), "CLOUDVORE")
    _verify_r8_local(_review(batch, "dng-auto-processor"))


def verify_frozen_doctrine(treeish: str) -> None:
    for path, expected in ((LEDGER_PATH, LEDGER_BLOB), (MANIFEST_PATH, MANIFEST_BLOB), (PHASE6_RECEIPT_PATH, PHASE6_RECEIPT_BLOB)):
        if _oid(PHASE9_COMMIT, path) != expected or _oid(treeish, path) != expected:
            raise Phase10Error("FROZEN_DOCTRINE_ARTIFACT_DRIFT")
    ledger = _load_json(treeish, LEDGER_PATH)
    summary = ledger.get("summary")
    projects = ledger.get("projects")
    if not isinstance(summary, dict) or summary.get("counts") != EXPECTED_COUNTS or summary.get("fleetAdoptionClaim") is not False:
        raise Phase10Error("LEDGER_STATUS_ADVANCE")
    if not isinstance(projects, list) or Counter(row.get("status") for row in projects if isinstance(row, dict)) != Counter({"DISTINGUISH": 5, "STALE": 4}):
        raise Phase10Error("LEDGER_STATUS_ADVANCE")
    source_specs = _tree_paths(PHASE9_COMMIT, "specs")
    if _tree_paths(treeish, "specs") != source_specs:
        raise Phase10Error("SPEC_SET_DRIFT")
    for path in source_specs:
        if _oid(treeish, path) != _oid(PHASE9_COMMIT, path):
            raise Phase10Error("SPEC_BLOB_DRIFT")


def verify_forward_allowlists(treeish: str, *, phase11_forward: bool = False) -> None:
    for path, attribute in PREDECESSOR_CHECKERS.items():
        if phase11_forward:
            source = _assignment_set(PHASE10_COMMIT, path, attribute)
            if _assignment_set(treeish, path, "PHASE11_INTEGRATION_PATHS") != PHASE11_PROOF_PATHS:
                raise Phase10Error("PHASE11_ALLOWLIST_SCOPE_DRIFT")
            if _assignment_set(treeish, path, attribute) != source | PHASE11_PROOF_PATHS:
                raise Phase10Error("PREDECESSOR_ALLOWLIST_UNION_MISMATCH")
            continue
        source = _assignment_set(PHASE9_COMMIT, path, attribute)
        if _assignment_set(treeish, path, "PHASE10_INTEGRATION_PATHS") != PHASE10_PROOF_PATHS:
            raise Phase10Error("PHASE10_ALLOWLIST_SCOPE_DRIFT")
        if _assignment_set(treeish, path, attribute) != source | PHASE10_PROOF_PATHS:
            raise Phase10Error("PREDECESSOR_ALLOWLIST_UNION_MISMATCH")
    paths = ("tools/check_phase8_integration.py", "tools/check_phase9_integration.py")
    if phase11_forward:
        paths = (*paths, "tools/check_phase10_integration.py")
        for path in paths:
            if _assignment_set(treeish, path, "PHASE11_FORWARD_PATHS") != PHASE11_FORWARD_PATHS:
                raise Phase10Error("FORWARD_SCOPE_DRIFT")
    else:
        for path in paths:
            if _assignment_set(treeish, path, "PHASE10_FORWARD_PATHS") != EXPECTED_INTEGRATION_PATHS:
                raise Phase10Error("FORWARD_SCOPE_DRIFT")


def verify_workflow(treeish: str) -> None:
    workflow = _blob(treeish, ".github/workflows/disposition-intake.yml").decode("utf-8", errors="strict")
    required = (
        'test_phase10_integration.py" -v',
        "check_phase10_integration.py --treeish HEAD",
    )
    if any(item not in workflow for item in required):
        raise Phase10Error("WORKFLOW_PHASE10_MISSING")


def verify_receipt_blob(treeish: str) -> dict[str, Any]:
    raw = _blob(treeish, RECEIPT_PATH)
    if _oid(treeish, RECEIPT_PATH) != RECEIPT_BLOB:
        raise Phase10Error("RECEIPT_BLOB_OID_MISMATCH")
    if len(raw) != RECEIPT_BYTES:
        raise Phase10Error("RECEIPT_BYTES_MISMATCH")
    if hashlib.sha256(raw).hexdigest() != RECEIPT_SHA256:
        raise Phase10Error("RECEIPT_SHA256_MISMATCH")
    return load_json(raw)


def verify_integration(treeish: str) -> None:
    if _commit_tuple(PHASE9_COMMIT) != (PHASE9_TREE, [PHASE9_PARENT]):
        raise Phase10Error("PHASE9_BASE_MISMATCH")
    if _commit_tuple(PHASE10_COMMIT) != (PHASE10_TREE, [PHASE9_COMMIT]):
        raise Phase10Error("PHASE10_SOURCE_MISMATCH")
    if _changed_paths(PHASE9_COMMIT, PHASE10_COMMIT) != EXPECTED_INTEGRATION_PATHS:
        raise Phase10Error("INTEGRATION_SCOPE_MISMATCH")
    resolved = None if treeish == ":" else str(
        _git(["rev-parse", f"{treeish}^{{commit}}"], text=True, error="COMMIT_UNAVAILABLE")
    ).strip()
    if resolved == PHASE10_COMMIT:
        if _commit_tuple(treeish) != (PHASE10_TREE, [PHASE9_COMMIT]):
            raise Phase10Error("INTEGRATION_PARENT_MISMATCH")
        if _changed_paths(PHASE9_COMMIT, treeish) != EXPECTED_INTEGRATION_PATHS:
            raise Phase10Error("INTEGRATION_SCOPE_MISMATCH")
        batch = verify_receipt_blob(treeish)
        verify_receipt_shape(batch)
        verify_local_subjects(batch)
        verify_frozen_doctrine(treeish)
        verify_forward_allowlists(treeish)
        verify_workflow(treeish)
        return
    if treeish == ":":
        head = str(_git(["rev-parse", "HEAD"], text=True, error="HEAD_UNAVAILABLE")).strip()
        if head != PHASE10_COMMIT:
            raise Phase10Error("STAGED_BASE_MISMATCH")
    elif _commit_tuple(treeish)[1] != [PHASE10_COMMIT]:
        raise Phase10Error("INTEGRATION_PARENT_MISMATCH")
    if _changed_paths(PHASE10_COMMIT, treeish) != PHASE11_FORWARD_PATHS:
        raise Phase10Error("INTEGRATION_SCOPE_MISMATCH")
    batch = verify_receipt_blob(treeish)
    verify_receipt_shape(batch)
    verify_local_subjects(batch)
    verify_frozen_doctrine(treeish)
    verify_forward_allowlists(treeish, phase11_forward=True)
    verify_workflow(treeish)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--treeish", default="HEAD")
    args = parser.parse_args()
    try:
        verify_integration(args.treeish)
    except Phase10Error as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(
        "PASS: Phase 10 exact-binds three local candidate reviews; ledger/spec dispositions and "
        "all installation, runtime, preview, adoption, and publication authority remain frozen"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
