#!/usr/bin/env python3
"""Provider-free, read-only audit of Claude Desktop scheduler persistence."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Iterable


MAX_JSON_BYTES = 1024 * 1024
MAX_AGGREGATE_JSON_BYTES = 16 * 1024 * 1024
MAX_TASK_PATHS = 256
MAX_TASK_OBJECTS = 4096
MAX_JSON_NODES = 65536
MAX_JSON_DEPTH = 64


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _validate_json_shape(data: bytes) -> None:
    depth = 0
    tokens = 0
    quoted = False
    escaped = False
    for byte in data:
        if quoted:
            if escaped:
                escaped = False
            elif byte == 92:
                escaped = True
            elif byte == 34:
                quoted = False
            continue
        if byte == 34:
            quoted = True
        elif byte in (91, 123):
            depth += 1
            tokens += 1
            if depth > MAX_JSON_DEPTH or tokens > MAX_JSON_NODES:
                raise ValueError("JSON_SHAPE_LIMIT")
        elif byte in (93, 125):
            depth -= 1
            if depth < 0:
                raise ValueError("INVALID_JSON")
        elif byte in (44, 58):
            tokens += 1
            if tokens > MAX_JSON_NODES:
                raise ValueError("JSON_SHAPE_LIMIT")


def _strict_json(path: Path) -> tuple[Any, bytes]:
    if path.is_symlink():
        raise ValueError("SYMLINK_REFUSED")
    if path.stat().st_size > MAX_JSON_BYTES:
        raise ValueError("JSON_TOO_LARGE")
    with path.open("rb") as stream:
        data = stream.read(MAX_JSON_BYTES + 1)
    if len(data) > MAX_JSON_BYTES:
        raise ValueError("JSON_TOO_LARGE")
    _validate_json_shape(data)

    def pairs(values: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in values:
            if key in result:
                raise ValueError("DUPLICATE_JSON_KEY")
            result[key] = value
        return result

    value = json.loads(
        data.decode("utf-8"),
        object_pairs_hook=pairs,
        parse_constant=lambda _: (_ for _ in ()).throw(ValueError("NONFINITE_JSON")),
    )
    return value, data


def _task_objects(value: Any) -> Iterable[dict[str, Any]]:
    stack: list[tuple[Any, int]] = [(value, 0)]
    visited = 0
    emitted = 0
    while stack:
        current, depth = stack.pop()
        visited += 1
        if visited > MAX_JSON_NODES or depth > MAX_JSON_DEPTH:
            raise ValueError("TASK_TREE_LIMIT")
        if isinstance(current, dict):
            if "id" in current and "enabled" in current and ("filePath" in current or "cronExpression" in current):
                emitted += 1
                if emitted > MAX_TASK_OBJECTS:
                    raise ValueError("TASK_COUNT_LIMIT")
                yield current
            stack.extend((child, depth + 1) for child in reversed(list(current.values())))
        elif isinstance(current, list):
            stack.extend((child, depth + 1) for child in reversed(current))


def audit(config_path: Path, task_paths: list[Path], project_prefix: str = "conjugal-") -> dict[str, Any]:
    if len(task_paths) > MAX_TASK_PATHS:
        raise ValueError("TASK_PATH_LIMIT")
    aggregate = config_path.stat().st_size + sum(path.stat().st_size for path in task_paths)
    if aggregate > MAX_AGGREGATE_JSON_BYTES:
        raise ValueError("TASK_AGGREGATE_LIMIT")
    config, config_data = _strict_json(config_path)
    if not isinstance(config, dict) or not isinstance(config.get("preferences"), dict):
        raise ValueError("CONFIG_SCHEMA")
    preferences = config["preferences"]
    cowork = preferences.get("coworkScheduledTasksEnabled")
    ccd = preferences.get("ccdScheduledTasksEnabled")
    reasons: list[str] = []
    if cowork is not False or ccd is not False:
        reasons.append("GLOBAL_PREFERENCES_NOT_FALSE")

    unique: dict[str, dict[str, Any]] = {}
    for path in sorted(task_paths, key=lambda item: item.as_posix().casefold()):
        value, store_data = _strict_json(path)
        for task in _task_objects(value):
            canonical = json.dumps(task, sort_keys=True, separators=(",", ":")).encode("utf-8")
            digest = _sha256(canonical)
            task_id = task.get("id")
            enabled = task.get("enabled")
            if not isinstance(task_id, str) or not isinstance(enabled, bool):
                reasons.append("TASK_SCHEMA")
                continue
            unique.setdefault(
                digest,
                {
                    "id": task_id,
                    "enabled": enabled,
                    "objectSha256": digest,
                    "storeSha256": _sha256(store_data),
                },
            )

    project = sorted(
        (row for row in unique.values() if row["id"].casefold().startswith(project_prefix.casefold())),
        key=lambda row: (row["id"].casefold(), row["objectSha256"]),
    )
    if any(row["enabled"] for row in project):
        reasons.append("PROJECT_TASK_ENABLED")
    globally_enabled = sorted(
        (row for row in unique.values() if row["enabled"]),
        key=lambda row: (row["id"].casefold(), row["objectSha256"]),
    )
    if globally_enabled:
        reasons.append("GLOBAL_TASK_ENABLED")
    return {
        "schema": "claude-scheduler-containment-audit/v1",
        "status": "CLOSED_ON_DISK_HOT_RELOAD_UNPROVEN" if not reasons else "UNCONTAINED_ZERO_AUTHORITY",
        "configSha256": _sha256(config_data),
        "preferences": {"coworkScheduledTasksEnabled": cowork, "ccdScheduledTasksEnabled": ccd},
        "uniqueTaskCount": len(unique),
        "projectTaskCount": len(project),
        "projectTasks": project,
        "globallyEnabledTaskCount": len(globally_enabled),
        "globallyEnabledTasks": globally_enabled,
        "reasons": sorted(set(reasons)),
        "authority": "NONE",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--tasks", required=True, type=Path, nargs="+")
    parser.add_argument("--project-prefix", default="conjugal-")
    args = parser.parse_args()
    try:
        result = audit(args.config, args.tasks, args.project_prefix)
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError):
        print("ERROR audit_claude_scheduler_containment: INPUT_REFUSED", file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
