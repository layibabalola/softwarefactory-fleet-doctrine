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
from pathlib import Path


MAX_FILE_BYTES = 2 * 1024 * 1024
MAX_EVIDENCE_LINES_PER_KIND = 64
SOURCE_SUFFIXES = {".bat", ".cmd", ".js", ".ps1", ".psm1", ".py", ".sh", ".ts"}
EXCLUDED_PARTS = {".git", "node_modules", "tmp"}
REVIEW_DISPOSITIONS = {"LAUNCHER", "NON_LAUNCHER", "UNKNOWN"}

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
    return _classify_data(path.relative_to(root).as_posix(), path.read_bytes())


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
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix().casefold()):
        if not path.is_file() or path.suffix.lower() not in SOURCE_SUFFIXES:
            continue
        if any(part.casefold() in EXCLUDED_PARTS for part in path.relative_to(root).parts):
            continue
        try:
            row = _classify(path, root)
        except (OSError, ValueError) as exc:
            refused.append({"path": path.relative_to(root).as_posix(), "reason": str(exc)})
            continue
        if row["providers"]:
            rows.append(row)
    return _report(str(root), rows, refused, sourceMode="WORKING_TREE")


def _git(repo: Path, *arguments: str, text: bool = False) -> subprocess.CompletedProcess:
    environment = os.environ.copy()
    environment["GIT_OPTIONAL_LOCKS"] = "0"
    return subprocess.run(
        ["git", "--no-optional-locks", "-C", str(repo), *arguments],
        check=True,
        capture_output=True,
        text=text,
        env=environment,
    )


def classify_git_tree(repo: Path, treeish: str) -> dict[str, object]:
    repo = repo.resolve(strict=True)
    commit = _git(repo, "rev-parse", f"{treeish}^{{commit}}", text=True).stdout.strip()
    tree = _git(repo, "rev-parse", f"{commit}^{{tree}}", text=True).stdout.strip()
    if not re.fullmatch(r"[0-9a-f]{40}", commit) or not re.fullmatch(r"[0-9a-f]{40}", tree):
        raise ValueError("GIT_SUBJECT_IDENTITY")
    listing = _git(repo, "ls-tree", "-r", "-z", "--full-tree", commit).stdout
    sources: list[tuple[str, str]] = []
    for record in listing.split(b"\0"):
        if not record:
            continue
        metadata, raw_path = record.split(b"\t", 1)
        _mode, kind, raw_oid = metadata.split(b" ", 2)
        path = raw_path.decode("utf-8", errors="surrogateescape")
        parts = Path(path).parts
        if kind == b"blob" and Path(path).suffix.lower() in SOURCE_SUFFIXES and not any(part.casefold() in EXCLUDED_PARTS for part in parts):
            sources.append((path, raw_oid.decode("ascii")))
    environment = os.environ.copy()
    environment["GIT_OPTIONAL_LOCKS"] = "0"
    process = subprocess.Popen(
        ["git", "--no-optional-locks", "-C", str(repo), "cat-file", "--batch"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=environment,
    )
    assert process.stdin is not None and process.stdout is not None
    rows: list[dict[str, object]] = []
    refused: list[dict[str, str]] = []
    try:
        for path, oid in sources:
            process.stdin.write((oid + "\n").encode("ascii"))
            process.stdin.flush()
            header = process.stdout.readline().decode("ascii").strip().split()
            if len(header) != 3 or header[0] != oid or header[1] != "blob":
                raise ValueError("GIT_BLOB_HEADER")
            size = int(header[2])
            data = process.stdout.read(size)
            if len(data) != size or process.stdout.read(1) != b"\n":
                raise ValueError("GIT_BLOB_TRUNCATED")
            try:
                row = _classify_data(path, data)
            except ValueError as exc:
                refused.append({"path": path, "reason": str(exc)})
                continue
            if row["providers"]:
                rows.append(row)
    finally:
        process.stdin.close()
        return_code = process.wait(timeout=30)
        assert process.stderr is not None
        process.stderr.read()
        process.stdout.close()
        process.stderr.close()
    if return_code != 0:
        raise ValueError("GIT_CAT_FILE_FAILURE")
    return _report(str(repo), rows, refused, sourceMode="GIT_COMMIT", subjectCommit=commit, subjectTree=tree)


def reconcile_review(report: dict[str, object], review: dict[str, object]) -> dict[str, object]:
    if set(review) != {"schema", "entries"} or review.get("schema") != "conjugal-launcher-review/v1":
        raise ValueError("REVIEW_SCHEMA")
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
        if disposition not in REVIEW_DISPOSITIONS:
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
    candidates = report.get("candidates")
    if not isinstance(candidates, list):
        raise ValueError("REPORT_SCHEMA")
    return {
        "schema": "conjugal-launcher-review/v1",
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

    value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=pairs, parse_constant=lambda _: (_ for _ in ()).throw(ValueError("NONFINITE_JSON")))
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
    report = classify_git_tree(args.root, args.git_treeish) if args.git_treeish else classify_tree(args.root)
    if args.review_manifest:
        output = reconcile_review(report, _strict_json(args.review_manifest))
    elif args.emit_review_template:
        output = review_template(report)
    else:
        output = report
    print(json.dumps(output, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
