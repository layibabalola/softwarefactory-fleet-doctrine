#!/usr/bin/env python3
"""Build a bounded, deterministic, hash-bound exact-byte evidence capsule."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import sys
from typing import Any, Sequence


REQUEST_SCHEMA = "fleet-evidence-capsule-request/v1"
CAPSULE_SCHEMA = "fleet-evidence-capsule/v1"
MAX_MANIFEST_BYTES = 1024 * 1024
MAX_ITEMS = 4096
MAX_SOURCE_BYTES = 16 * 1024 * 1024
MAX_AGGREGATE_SOURCE_BYTES = 64 * 1024 * 1024
MAX_SOURCE_LINES = 200_000


class CapsuleError(RuntimeError):
    pass


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest_json(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def read_bounded(path: pathlib.Path, maximum: int) -> bytes:
    if path.is_symlink():
        raise CapsuleError("SYMLINK_REFUSED")
    if path.stat().st_size > maximum:
        raise CapsuleError("INPUT_TOO_LARGE")
    with path.open("rb") as stream:
        data = stream.read(maximum + 1)
    if len(data) > maximum:
        raise CapsuleError("INPUT_TOO_LARGE")
    return data


def build(manifest: dict[str, Any]) -> dict[str, Any]:
    if manifest.get("schema") != REQUEST_SCHEMA:
        raise CapsuleError("unsupported capsule request schema")
    root_value = manifest.get("workspace_root")
    if not isinstance(root_value, str) or not root_value:
        raise CapsuleError("workspace_root is required")
    root = pathlib.Path(root_value).resolve(strict=True)
    if not root.is_dir():
        raise CapsuleError("workspace_root is not a directory")
    maximum = manifest.get("max_payload_bytes")
    if not isinstance(maximum, int) or maximum <= 0:
        raise CapsuleError("max_payload_bytes must be positive")
    items = manifest.get("items")
    if not isinstance(items, list) or not items:
        raise CapsuleError("items must be a non-empty array")
    if len(items) > MAX_ITEMS:
        raise CapsuleError("ITEM_COUNT_LIMIT")
    seen: set[tuple[str, int, int]] = set()
    output_items=[]
    payload_bytes=0
    aggregate_source_bytes=0
    for item in items:
        if not isinstance(item, dict): raise CapsuleError("capsule item must be an object")
        relative=item.get("relative_path")
        if not isinstance(relative,str) or not relative: raise CapsuleError("relative_path is required")
        candidate=(root/relative).resolve(strict=True)
        try: candidate.relative_to(root)
        except ValueError as exc: raise CapsuleError(f"path escapes workspace: {relative}") from exc
        if not candidate.is_file(): raise CapsuleError(f"item is not a regular file: {relative}")
        raw=read_bounded(candidate,MAX_SOURCE_BYTES)
        aggregate_source_bytes+=len(raw)
        if aggregate_source_bytes>MAX_AGGREGATE_SOURCE_BYTES: raise CapsuleError("SOURCE_AGGREGATE_LIMIT")
        if raw.count(b"\n")+(0 if not raw or raw.endswith(b"\n") else 1)>MAX_SOURCE_LINES: raise CapsuleError("SOURCE_LINE_LIMIT")
        actual=hashlib.sha256(raw).hexdigest()
        if item.get("sha256") != actual: raise CapsuleError(f"file hash mismatch: {relative}")
        try: text=raw.decode("utf-8")
        except UnicodeDecodeError as exc: raise CapsuleError(f"item is not UTF-8: {relative}") from exc
        start=item.get("start_line"); end=item.get("end_line")
        if not isinstance(start,int) or not isinstance(end,int) or start<1 or end<start:
            raise CapsuleError(f"invalid line range: {relative}")
        lines=text.splitlines(keepends=True)
        if end>len(lines): raise CapsuleError(f"line range exceeds file: {relative}")
        key=(relative.replace('\\','/'),start,end)
        if key in seen: raise CapsuleError(f"duplicate capsule slice: {relative}:{start}-{end}")
        seen.add(key)
        content=''.join(lines[start-1:end]); size=len(content.encode('utf-8')); payload_bytes+=size
        if payload_bytes>maximum: raise CapsuleError("capsule payload exceeds max_payload_bytes")
        purpose=item.get("purpose")
        if not isinstance(purpose,str) or not purpose: raise CapsuleError(f"purpose is required: {relative}")
        output_items.append({"relative_path":key[0],"file_sha256":actual,"start_line":start,"end_line":end,"purpose":purpose,"content":content})
    identity_manifest={key:value for key,value in manifest.items() if key!="workspace_root"}
    return {"schema":CAPSULE_SCHEMA,"subject_digest":manifest.get("subject_digest"),"manifest_digest":digest_json(identity_manifest),"payload_bytes":payload_bytes,"items":output_items}


def write_atomic(path: pathlib.Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    os.replace(temporary,path)


def main(argv: Sequence[str] | None=None) -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest",type=pathlib.Path,required=True)
    parser.add_argument("--output",type=pathlib.Path)
    args=parser.parse_args(argv)
    try:
        manifest=json.loads(read_bounded(args.manifest,MAX_MANIFEST_BYTES).decode("utf-8")); result=build(manifest)
        if args.output: write_atomic(args.output,result)
        else: print(json.dumps(result,indent=2,sort_keys=True))
        return 0
    except (OSError,UnicodeError,json.JSONDecodeError,CapsuleError):
        print(json.dumps({"error":"INPUT_REFUSED"},sort_keys=True),file=sys.stderr)
        return 22


if __name__=="__main__": raise SystemExit(main())
