#!/usr/bin/env python3
"""Deterministic, provider-free first pass over repository launcher candidates.

The output is deliberately an INCOMPLETE census.  It identifies files that need
human/source-graph classification; it never asserts that a launcher is brokered.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import threading
from pathlib import Path


MAX_FILE_BYTES = 2 * 1024 * 1024
MAX_LISTING_BYTES = 16 * 1024 * 1024
MAX_AGGREGATE_SOURCE_BYTES = 64 * 1024 * 1024
MAX_SOURCE_FILES = 16384
MAX_CANDIDATES = 4096
MAX_REVIEW_BYTES = 4 * 1024 * 1024
MAX_VISITED_PATHS = 131072
MAX_DIRECTORY_ENTRIES = 32768
MAX_GIT_STDERR_BYTES = 64 * 1024
MAX_REVIEW_NODES = 65536
MAX_REVIEW_DEPTH = 64
MAX_EVIDENCE_LINES_PER_KIND = 64
SOURCE_SUFFIXES = {".bat", ".cjs", ".cmd", ".js", ".mjs", ".ps1", ".psm1", ".py", ".sh", ".ts"}
EXCLUDED_PARTS = {".git", "node_modules", "tmp"}
REVIEW_DISPOSITIONS = {"LAUNCHER", "NON_LAUNCHER", "UNKNOWN"}
REVIEW_SCHEMA = "conjugal-launcher-review/v2"
PUBLIC_REFUSAL_REASONS = {
    "SOURCE_TOO_LARGE",
    "SYMLINK_SOURCE_REFUSED",
}

PROVIDERS = {
    "CLAUDE": re.compile(r"(?i)\b(?:claude(?:\.exe)?|anthropic)\b"),
    "CODEX": re.compile(r"(?i)\b(?:codex(?:\.exe)?|openai)\b"),
    "KIMI": re.compile(r"(?i)\b(?:kimi(?:\.exe)?|moonshot)\b"),
    "GROK": re.compile(r"(?i)\b(?:grok|xai)\b"),
}
PRIMITIVES = {
    "POWERSHELL_START_PROCESS": re.compile(r"(?i)\bStart-Process\b"),
    "PYTHON_SUBPROCESS": re.compile(r"(?i)\bsubprocess\.(?:run|Popen|call|check_call|check_output)\b"),
    "DOTNET_PROCESS": re.compile(r"(?i)\b(?:ProcessStartInfo|System\.Diagnostics\.Process)\b"),
    "NODE_CHILD_PROCESS": re.compile(
        r"(?i)(?:\b(?:node:)?child_process\b|\b(?:spawn|spawnSync|execFile|execFileSync|exec|execSync)\s*\()"
    ),
    "SHELL_EXEC": re.compile(r"(?im)(?:^|[;&|]\s*|\bexec\s+)(?:[\"'][^\"']*[/\\])?(?:claude|codex|kimi|grok)(?:\.exe)?(?:\s|[\"'])"),
}
VARIABLE_LAUNCH = re.compile(
    r"(?i)(?:Start-Process\s+-FilePath\s+\$|subprocess\.(?:run|Popen|call)\s*\(\s*[A-Za-z_]|ProcessStartInfo\s*\(\s*[A-Za-z_$])"
)
SCHEDULER_REGISTRATION = re.compile(r"(?i)\b(?:Register-ScheduledTask|schtasks(?:\.exe)?|New-ScheduledTaskAction)\b")


def _sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _classify_data(relative_path: str, data: bytes) -> dict[str, object]:
    if len(data) > MAX_FILE_BYTES:
        raise ValueError("SOURCE_TOO_LARGE")
    text = data.decode("utf-8", errors="replace")
    lines = text.splitlines()
    provider_lines = {
        name: [number for number, line in enumerate(lines, 1) if pattern.search(line)][:MAX_EVIDENCE_LINES_PER_KIND]
        for name, pattern in PROVIDERS.items()
    }
    primitive_lines = {
        name: [number for number, line in enumerate(lines, 1) if pattern.search(line)][:MAX_EVIDENCE_LINES_PER_KIND]
        for name, pattern in PRIMITIVES.items()
    }
    providers = sorted(name for name, matches in provider_lines.items() if matches)
    primitives = sorted(name for name, matches in primitive_lines.items() if matches)
    same_line = any(
        any(pattern.search(line) for pattern in PROVIDERS.values())
        and any(pattern.search(line) for pattern in PRIMITIVES.values())
        for line in lines
    )
    if same_line:
        classification = "DIRECT_STATIC"
    elif providers and primitives and VARIABLE_LAUNCH.search(text):
        classification = "INDIRECT_VARIABLE"
    elif providers and SCHEDULER_REGISTRATION.search(text):
        classification = "REGISTRATION_SURFACE"
    elif providers and primitives:
        classification = "UNRESOLVED_FLOW"
    else:
        classification = "REFERENCE_ONLY"
    priority = {
        "DIRECT_STATIC": "P0_DIRECT",
        "INDIRECT_VARIABLE": "P0_DIRECT",
        "REGISTRATION_SURFACE": "P1_REGISTRATION",
        "UNRESOLVED_FLOW": "P2_UNRESOLVED",
        "REFERENCE_ONLY": "P3_REFERENCE",
    }[classification]
    return {
        "path": relative_path,
        "sha256": _sha256(data),
        "bytes": len(data),
        "providers": providers,
        "launchPrimitives": primitives,
        "classification": classification,
        "reviewPriority": priority,
        "evidence": {
            "providerLines": {name: provider_lines[name] for name in providers},
            "primitiveLines": {name: primitive_lines[name] for name in primitives},
        },
    }


def _classify(path: Path, root: Path) -> dict[str, object]:
    if path.is_symlink():
        raise ValueError("SYMLINK_SOURCE_REFUSED")
    if path.stat().st_size > MAX_FILE_BYTES:
        raise ValueError("SOURCE_TOO_LARGE")
    with path.open("rb") as stream:
        data = stream.read(MAX_FILE_BYTES + 1)
    return _classify_data(path.relative_to(root).as_posix(), data)


def _public_refusal_reason(error: BaseException) -> str:
    reason = str(error)
    return reason if reason in PUBLIC_REFUSAL_REASONS else "INPUT_REFUSED"


def _report(root: str, rows: list[dict[str, object]], refused: list[dict[str, str]], **identity: str) -> dict[str, object]:
    counts: dict[str, int] = {}
    priorities: dict[str, int] = {}
    for row in rows:
        key = str(row["classification"])
        counts[key] = counts.get(key, 0) + 1
        priority = str(row["reviewPriority"])
        priorities[priority] = priorities.get(priority, 0) + 1
    flow_unresolved = sum(
        counts.get(key, 0) for key in ("INDIRECT_VARIABLE", "UNRESOLVED_FLOW", "REFERENCE_ONLY")
    ) + len(refused)
    # Automated flow classification is triage, never review.  Even a syntactically
    # direct launch or registration surface remains unresolved until its exact
    # hash receives a review disposition.
    review_pending = len(rows) + len(refused)
    return {
        "schema": "conjugal-launcher-candidate-classification/v1",
        "status": "INCOMPLETE_ZERO_AUTHORITY",
        "root": root,
        **identity,
        "candidateCount": len(rows),
        "classificationCounts": dict(sorted(counts.items())),
        "reviewPriorityCounts": dict(sorted(priorities.items())),
        "flowUnresolvedCount": flow_unresolved,
        "reviewPendingCount": review_pending,
        "unresolvedCount": review_pending,
        "refused": refused,
        "candidates": rows,
    }


def classify_tree(root: Path) -> dict[str, object]:
    root = root.resolve(strict=True)
    rows: list[dict[str, object]] = []
    refused: list[dict[str, str]] = []
    sources: list[Path] = []
    pending = [root]
    visited = 0
    while pending:
        directory = pending.pop()
        directory_entries = 0
        with os.scandir(directory) as entries:
            for entry in entries:
                directory_entries += 1
                visited += 1
                if directory_entries > MAX_DIRECTORY_ENTRIES:
                    raise ValueError("DIRECTORY_ENTRY_LIMIT")
                if visited > MAX_VISITED_PATHS:
                    raise ValueError("VISITED_PATH_LIMIT")
                path = Path(entry.path)
                if entry.is_dir(follow_symlinks=False):
                    if entry.name.casefold() not in EXCLUDED_PARTS:
                        pending.append(path)
                elif (entry.is_file(follow_symlinks=False) or entry.is_symlink()) and path.suffix.lower() in SOURCE_SUFFIXES:
                    sources.append(path)
                    if len(sources) > MAX_SOURCE_FILES:
                        raise ValueError("SOURCE_COUNT_LIMIT")

    aggregate = 0
    for path in sorted(sources, key=lambda item: item.relative_to(root).as_posix().casefold()):
        aggregate += path.stat().st_size
        if aggregate > MAX_AGGREGATE_SOURCE_BYTES:
            raise ValueError("SOURCE_AGGREGATE_LIMIT")
        try:
            row = _classify(path, root)
        except (OSError, ValueError) as exc:
            refused.append({"path": path.relative_to(root).as_posix(), "reason": _public_refusal_reason(exc)})
            continue
        if row["providers"]:
            rows.append(row)
            if len(rows) > MAX_CANDIDATES:
                raise ValueError("CANDIDATE_COUNT_LIMIT")
    return _report(".", rows, refused, sourceMode="WORKING_TREE")


def _git_bounded(repo: Path, limit: int, *arguments: str) -> bytes:
    environment = os.environ.copy()
    environment["GIT_OPTIONAL_LOCKS"] = "0"
    process = subprocess.Popen(
        ["git", "--no-optional-locks", "-C", str(repo), *arguments],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=environment,
    )
    assert process.stdout is not None and process.stderr is not None
    stdout = bytearray()
    stderr = bytearray()
    exceeded = threading.Event()

    def drain(stream, target: bytearray, maximum: int) -> None:
        while True:
            chunk = stream.read(65536)
            if not chunk:
                return
            remaining = maximum + 1 - len(target)
            if remaining > 0:
                target.extend(chunk[:remaining])
            if len(target) > maximum:
                exceeded.set()
                try: process.kill()
                except OSError: pass
                return

    readers = [
        threading.Thread(target=drain, args=(process.stdout, stdout, limit), daemon=True),
        threading.Thread(target=drain, args=(process.stderr, stderr, MAX_GIT_STDERR_BYTES), daemon=True),
    ]
    for reader in readers: reader.start()
    try:
        try: return_code = process.wait(timeout=30)
        except subprocess.TimeoutExpired as exc:
            process.kill(); process.wait(timeout=30)
            raise ValueError("GIT_TIMEOUT") from exc
        for reader in readers: reader.join(timeout=5)
        if any(reader.is_alive() for reader in readers): raise ValueError("GIT_PIPE_TIMEOUT")
        if exceeded.is_set(): raise ValueError("GIT_OUTPUT_LIMIT")
        if return_code != 0:
            raise ValueError("GIT_COMMAND_FAILED")
        return bytes(stdout)
    finally:
        process.stdout.close()
        process.stderr.close()


def classify_git_tree(repo: Path, treeish: str) -> dict[str, object]:
    repo = repo.resolve(strict=True)
    commit = _git_bounded(repo, 128, "rev-parse", f"{treeish}^{{commit}}").decode("ascii").strip()
    tree = _git_bounded(repo, 128, "rev-parse", f"{commit}^{{tree}}").decode("ascii").strip()
    if not re.fullmatch(r"[0-9a-f]{40}", commit) or not re.fullmatch(r"[0-9a-f]{40}", tree):
        raise ValueError("GIT_SUBJECT_IDENTITY")
    listing = _git_bounded(repo, MAX_LISTING_BYTES, "ls-tree", "-r", "-z", "--long", "--full-tree", commit)
    sources: list[tuple[str, str, int]] = []
    refused: list[dict[str, str]] = []
    aggregate = 0
    for record in listing.split(b"\0"):
        if not record:
            continue
        metadata, raw_path = record.split(b"\t", 1)
        _mode, kind, raw_oid, raw_size = metadata.split()
        path = raw_path.decode("utf-8", errors="surrogateescape")
        parts = Path(path).parts
        if kind == b"blob" and Path(path).suffix.lower() in SOURCE_SUFFIXES and not any(part.casefold() in EXCLUDED_PARTS for part in parts):
            size = int(raw_size)
            if size > MAX_FILE_BYTES:
                refused.append({"path": path, "reason": "SOURCE_TOO_LARGE"})
                continue
            aggregate += size
            if len(sources) >= MAX_SOURCE_FILES:
                raise ValueError("SOURCE_COUNT_LIMIT")
            if aggregate > MAX_AGGREGATE_SOURCE_BYTES:
                raise ValueError("SOURCE_AGGREGATE_LIMIT")
            sources.append((path, raw_oid.decode("ascii"), size))
    rows: list[dict[str, object]] = []
    for path, oid, expected_size in sources:
        data = _git_bounded(repo, expected_size, "cat-file", "blob", oid)
        if len(data) != expected_size: raise ValueError("GIT_BLOB_SIZE")
        try: row = _classify_data(path, data)
        except ValueError as exc:
            refused.append({"path": path, "reason": _public_refusal_reason(exc)})
            continue
        if row["providers"]:
            rows.append(row)
            if len(rows) > MAX_CANDIDATES: raise ValueError("CANDIDATE_COUNT_LIMIT")
    return _report(".", rows, refused, sourceMode="GIT_COMMIT", subjectCommit=commit, subjectTree=tree)


def _review_subject(report: dict[str, object]) -> tuple[str, str]:
    commit = report.get("subjectCommit")
    tree = report.get("subjectTree")
    if (
        report.get("sourceMode") != "GIT_COMMIT"
        or not isinstance(commit, str)
        or not re.fullmatch(r"[0-9a-f]{40}", commit)
        or not isinstance(tree, str)
        or not re.fullmatch(r"[0-9a-f]{40}", tree)
    ):
        raise ValueError("REVIEW_REQUIRES_GIT_SUBJECT")
    return commit, tree


def reconcile_review(report: dict[str, object], review: dict[str, object]) -> dict[str, object]:
    if set(review) != {"schema", "subjectCommit", "subjectTree", "entries"} or review.get("schema") != REVIEW_SCHEMA:
        raise ValueError("REVIEW_SCHEMA")
    subject_commit, subject_tree = _review_subject(report)
    if review.get("subjectCommit") != subject_commit or review.get("subjectTree") != subject_tree:
        raise ValueError("REVIEW_SUBJECT_MISMATCH")
    entries = review.get("entries")
    if not isinstance(entries, list):
        raise ValueError("REVIEW_SCHEMA")
    candidates = report.get("candidates")
    if not isinstance(candidates, list):
        raise ValueError("REPORT_SCHEMA")
    candidate_by_path = {str(row["path"]): row for row in candidates}
    if len(candidate_by_path) != len(candidates):
        raise ValueError("REPORT_DUPLICATE_PATH")
    reviewed: dict[str, dict[str, str]] = {}
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {"path", "sha256", "disposition"}:
            raise ValueError("REVIEW_SCHEMA")
        path = entry.get("path")
        digest = entry.get("sha256")
        disposition = entry.get("disposition")
        if not isinstance(path, str) or path in reviewed:
            raise ValueError("REVIEW_DUPLICATE_PATH")
        if not isinstance(disposition, str) or disposition not in REVIEW_DISPOSITIONS:
            raise ValueError("REVIEW_DISPOSITION")
        if path not in candidate_by_path:
            raise ValueError("REVIEW_EXTRA_PATH")
        if digest != candidate_by_path[path]["sha256"]:
            raise ValueError("REVIEW_HASH_MISMATCH")
        reviewed[path] = {"sha256": str(digest), "disposition": str(disposition)}
    missing = sorted(set(candidate_by_path) - set(reviewed))
    if missing:
        raise ValueError("REVIEW_MISSING_PATH")
    counts = {name: 0 for name in sorted(REVIEW_DISPOSITIONS)}
    for entry in reviewed.values():
        counts[entry["disposition"]] += 1
    refused = report.get("refused")
    refused_count = len(refused) if isinstance(refused, list) else 0
    pending = counts["UNKNOWN"] + refused_count
    return {
        "schema": "conjugal-launcher-review-result/v1",
        "status": "REVIEWED_CLASSIFICATION_ZERO_AUTHORITY" if pending == 0 else "REVIEW_INCOMPLETE_ZERO_AUTHORITY",
        "candidateCount": len(candidate_by_path),
        "reviewCounts": counts,
        "refusedCount": refused_count,
        "pendingCount": pending,
    }


def review_template(report: dict[str, object]) -> dict[str, object]:
    subject_commit, subject_tree = _review_subject(report)
    candidates = report.get("candidates")
    if not isinstance(candidates, list):
        raise ValueError("REPORT_SCHEMA")
    return {
        "schema": REVIEW_SCHEMA,
        "subjectCommit": subject_commit,
        "subjectTree": subject_tree,
        "entries": [
            {"path": str(row["path"]), "sha256": str(row["sha256"]), "disposition": "UNKNOWN"}
            for row in candidates
        ],
    }


def _strict_json(path: Path) -> dict[str, object]:
    def pairs(values: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in values:
            if key in result:
                raise ValueError("DUPLICATE_JSON_KEY")
            result[key] = value
        return result

    if path.is_symlink() or path.stat().st_size > MAX_REVIEW_BYTES:
        raise ValueError("REVIEW_INPUT_LIMIT")
    with path.open("rb") as stream:
        data = stream.read(MAX_REVIEW_BYTES + 1)
    if len(data) > MAX_REVIEW_BYTES:
        raise ValueError("REVIEW_INPUT_LIMIT")
    depth=0; nodes=0; quoted=False; escaped=False
    for byte in data:
        if quoted:
            if escaped: escaped=False
            elif byte==92: escaped=True
            elif byte==34: quoted=False
            continue
        if byte==34: quoted=True
        elif byte in (91,123):
            depth+=1; nodes+=1
            if depth>MAX_REVIEW_DEPTH or nodes>MAX_REVIEW_NODES: raise ValueError("REVIEW_SHAPE_LIMIT")
        elif byte in (93,125):
            depth-=1
            if depth<0: raise ValueError("REVIEW_SCHEMA")
        elif byte in (44,58):
            nodes+=1
            if nodes>MAX_REVIEW_NODES: raise ValueError("REVIEW_SHAPE_LIMIT")
    value = json.loads(data.decode("utf-8"), object_pairs_hook=pairs, parse_constant=lambda _: (_ for _ in ()).throw(ValueError("NONFINITE_JSON")))
    if not isinstance(value, dict):
        raise ValueError("REVIEW_SCHEMA")
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--git-treeish")
    parser.add_argument("--review-manifest", type=Path)
    parser.add_argument("--emit-review-template", action="store_true")
    args = parser.parse_args()
    if args.review_manifest and args.emit_review_template:
        parser.error("--review-manifest and --emit-review-template are mutually exclusive")
    try:
        report = classify_git_tree(args.root, args.git_treeish) if args.git_treeish else classify_tree(args.root)
        if args.review_manifest:
            output = reconcile_review(report, _strict_json(args.review_manifest))
        elif args.emit_review_template:
            output = review_template(report)
        else:
            output = report
    except (OSError, UnicodeError, ValueError, subprocess.SubprocessError, json.JSONDecodeError):
        print("ERROR classify_launcher_candidates: INPUT_REFUSED", file=sys.stderr)
        return 2
    print(json.dumps(output, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
