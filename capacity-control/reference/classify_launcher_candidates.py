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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    print(json.dumps(classify_tree(args.root), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
