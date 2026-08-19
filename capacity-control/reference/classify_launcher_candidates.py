#!/usr/bin/env python3
"""Deterministic, provider-free first pass over repository launcher candidates.

The output is deliberately an INCOMPLETE census.  It identifies files that need
human/source-graph classification; it never asserts that a launcher is brokered.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


MAX_FILE_BYTES = 2 * 1024 * 1024
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


def _classify(path: Path, root: Path) -> dict[str, object]:
    if path.is_symlink():
        raise ValueError("SYMLINK_SOURCE_REFUSED")
    data = path.read_bytes()
    if len(data) > MAX_FILE_BYTES:
        raise ValueError("SOURCE_TOO_LARGE")
    text = data.decode("utf-8", errors="replace")
    providers = sorted(name for name, pattern in PROVIDERS.items() if pattern.search(text))
    primitives = sorted(name for name, pattern in PRIMITIVES.items() if pattern.search(text))
    same_line = any(
        any(pattern.search(line) for pattern in PROVIDERS.values())
        and any(pattern.search(line) for pattern in PRIMITIVES.values())
        for line in text.splitlines()
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
    return {
        "path": path.relative_to(root).as_posix(),
        "sha256": _sha256(data),
        "bytes": len(data),
        "providers": providers,
        "launchPrimitives": primitives,
        "classification": classification,
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
    counts: dict[str, int] = {}
    for row in rows:
        key = str(row["classification"])
        counts[key] = counts.get(key, 0) + 1
    unresolved = sum(counts.get(key, 0) for key in ("INDIRECT_VARIABLE", "UNRESOLVED_FLOW", "REFERENCE_ONLY"))
    return {
        "schema": "conjugal-launcher-candidate-classification/v1",
        "status": "INCOMPLETE_ZERO_AUTHORITY",
        "root": str(root),
        "candidateCount": len(rows),
        "classificationCounts": dict(sorted(counts.items())),
        "unresolvedCount": unresolved + len(refused),
        "refused": refused,
        "candidates": rows,
    }


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
    parser.add_argument("--review-manifest", type=Path)
    args = parser.parse_args()
    report = classify_tree(args.root)
    output = reconcile_review(report, _strict_json(args.review_manifest)) if args.review_manifest else report
    print(json.dumps(output, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
