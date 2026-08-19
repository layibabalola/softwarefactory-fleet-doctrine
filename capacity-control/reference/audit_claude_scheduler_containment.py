#!/usr/bin/env python3
"""Provider-free, read-only audit of Claude Desktop scheduler persistence."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


MAX_JSON_BYTES = 1024 * 1024


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _strict_json(path: Path) -> tuple[Any, bytes]:
    if path.is_symlink():
        raise ValueError("SYMLINK_REFUSED")
    data = path.read_bytes()
    if len(data) > MAX_JSON_BYTES:
        raise ValueError("JSON_TOO_LARGE")

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
    if isinstance(value, dict):
        if "id" in value and "enabled" in value and ("filePath" in value or "cronExpression" in value):
            yield value
        for child in value.values():
            yield from _task_objects(child)
    elif isinstance(value, list):
        for child in value:
            yield from _task_objects(child)


def audit(config_path: Path, task_paths: list[Path], project_prefix: str = "conjugal-") -> dict[str, Any]:
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
    print(json.dumps(audit(args.config, args.tasks, args.project_prefix), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
