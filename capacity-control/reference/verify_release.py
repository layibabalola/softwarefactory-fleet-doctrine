#!/usr/bin/env python3
"""Verify an installed capacity-control candidate against a pinned release manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import sys
from typing import Any, Sequence


SCHEMA = "fleet-capacity-release-manifest/v1"


class VerificationError(RuntimeError):
    pass


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def verify(root: pathlib.Path, manifest_path: pathlib.Path, expected_manifest_sha256: str) -> dict[str, Any]:
    root = root.resolve()
    manifest_path = manifest_path.resolve()
    manifest_bytes = manifest_path.read_bytes()
    manifest_digest = sha256_bytes(manifest_bytes)
    if not re.fullmatch(r"[0-9a-f]{64}", expected_manifest_sha256):
        raise VerificationError("expected manifest SHA-256 has invalid syntax")
    if manifest_digest != expected_manifest_sha256:
        raise VerificationError("manifest SHA-256 mismatch")
    try:
        manifest = json.loads(manifest_bytes)
    except json.JSONDecodeError as exc:
        raise VerificationError("manifest is not valid JSON") from exc
    if not isinstance(manifest, dict) or manifest.get("schema") != SCHEMA:
        raise VerificationError("unsupported release manifest schema")
    files = manifest.get("files")
    if not isinstance(files, list) or not files:
        raise VerificationError("manifest files must be a non-empty array")
    seen: set[str] = set()
    for item in files:
        if not isinstance(item, dict) or set(item) != {"path", "sha256", "bytes", "role"}:
            raise VerificationError("manifest file row has invalid shape")
        relative = item["path"]
        if not isinstance(relative, str) or not relative or relative in seen:
            raise VerificationError("manifest file path is missing or duplicated")
        seen.add(relative)
        pure = pathlib.PurePosixPath(relative)
        if pure.is_absolute() or ".." in pure.parts or "\\" in relative:
            raise VerificationError("manifest file path escapes the release root")
        candidate = (root / pathlib.Path(*pure.parts)).resolve()
        try:
            candidate.relative_to(root)
        except ValueError as exc:
            raise VerificationError("manifest file resolves outside the release root") from exc
        if candidate.is_symlink() or not candidate.is_file():
            raise VerificationError(f"manifest file is absent or a symlink: {relative}")
        content = candidate.read_bytes()
        if not isinstance(item["bytes"], int) or item["bytes"] != len(content):
            raise VerificationError(f"byte length mismatch: {relative}")
        if not isinstance(item["sha256"], str) or sha256_bytes(content) != item["sha256"]:
            raise VerificationError(f"SHA-256 mismatch: {relative}")
        if not isinstance(item["role"], str) or not item["role"]:
            raise VerificationError(f"role is invalid: {relative}")
    return {
        "schema": "fleet-capacity-release-verification/v1",
        "status": "VERIFIED_CANDIDATE_BYTES",
        "manifest_sha256": manifest_digest,
        "source_commit": manifest.get("source_commit"),
        "file_count": len(files),
        "activation_authority": False,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=pathlib.Path, required=True)
    parser.add_argument("--manifest", type=pathlib.Path, required=True)
    parser.add_argument("--expected-manifest-sha256", required=True)
    args = parser.parse_args(argv)
    try:
        result = verify(args.root, args.manifest, args.expected_manifest_sha256)
        print(json.dumps(result, sort_keys=True, separators=(",", ":")))
        return 0
    except (OSError, VerificationError) as exc:
        print(json.dumps({"status": "REFUSED", "reason": str(exc)}, sort_keys=True), file=sys.stderr)
        return 22


if __name__ == "__main__":
    raise SystemExit(main())
