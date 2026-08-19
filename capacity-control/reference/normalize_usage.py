#!/usr/bin/env python3
"""Normalize native provider session events into usage-event-v1 without prose."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import sys
from typing import Any, Iterable, Sequence


SCHEMA = "fleet-inference-usage-event/v1"
TERMINALS = {"SUCCESS", "PAUSED_BUDGET", "QUOTA_BLOCKED", "REFUSED", "FAILED", "CANCELLED", "UNEVALUABLE"}
MAX_INPUT_BYTES = 16 * 1024 * 1024
MAX_METADATA_BYTES = 1024 * 1024
MAX_INPUT_LINES = 200_000
MAX_JSON_DEPTH = 64
MAX_JSON_NODES = 65536


class NormalizeError(RuntimeError):
    pass


def read_bounded(path: pathlib.Path, maximum: int, line_limit: int | None = None) -> bytes:
    if path.is_symlink(): raise NormalizeError("SYMLINK_REFUSED")
    if path.stat().st_size > maximum: raise NormalizeError("INPUT_TOO_LARGE")
    with path.open("rb") as source: data=source.read(maximum+1)
    if len(data)>maximum: raise NormalizeError("INPUT_TOO_LARGE")
    if line_limit is not None and data.count(b"\n")+(0 if not data or data.endswith(b"\n") else 1)>line_limit:
        raise NormalizeError("INPUT_LINE_LIMIT")
    return data


def validate_json_shape(data: bytes) -> None:
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
            if depth>MAX_JSON_DEPTH or nodes>MAX_JSON_NODES: raise NormalizeError("JSON_SHAPE_LIMIT")
        elif byte in (93,125):
            depth-=1
            if depth<0: raise NormalizeError("INVALID_JSON")
        elif byte in (44,58):
            nodes+=1
            if nodes>MAX_JSON_NODES: raise NormalizeError("JSON_SHAPE_LIMIT")


def json_lines(lines: Iterable[str]) -> Iterable[dict[str, Any]]:
    for line in lines:
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            yield value


def empty_usage() -> dict[str, int | float | None]:
    return {
        "input_tokens": 0,
        "cached_input_tokens": 0,
        "output_tokens": 0,
        "reasoning_tokens": 0,
        "peak_context_tokens": 0,
        "turns": 0,
        "wall_seconds": None,
    }


def wall_seconds(timestamps: list[dt.datetime]) -> float | None:
    return round((max(timestamps) - min(timestamps)).total_seconds(), 3) if len(timestamps) > 1 else None


def parse_iso(value: Any) -> dt.datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else None


def normalize_anthropic(events: Iterable[dict[str, Any]]) -> tuple[dict[str, Any], str | None, str | None]:
    usage = empty_usage()
    seen: set[str] = set()
    models: set[str] = set()
    timestamps: list[dt.datetime] = []
    session_id = None
    for event in events:
        parsed = parse_iso(event.get("timestamp"))
        if parsed: timestamps.append(parsed)
        session_id = session_id or event.get("sessionId")
        message = event.get("message")
        if event.get("type") != "assistant" or not isinstance(message, dict):
            continue
        message_id = message.get("id")
        native = message.get("usage")
        if not isinstance(message_id, str) or message_id in seen or not isinstance(native, dict):
            continue
        seen.add(message_id)
        if isinstance(message.get("model"), str): models.add(message["model"])
        input_other = int(native.get("input_tokens") or 0)
        cache_read = int(native.get("cache_read_input_tokens") or 0)
        cache_create = int(native.get("cache_creation_input_tokens") or 0)
        output = int(native.get("output_tokens") or 0)
        details = native.get("output_tokens_details") or {}
        reasoning = int(details.get("thinking_tokens") or 0) if isinstance(details, dict) else 0
        usage["input_tokens"] += input_other + cache_create
        usage["cached_input_tokens"] += cache_read
        usage["output_tokens"] += output
        usage["reasoning_tokens"] += reasoning
        usage["peak_context_tokens"] = max(int(usage["peak_context_tokens"]), input_other + cache_create + cache_read)
        usage["turns"] += 1
    usage["wall_seconds"] = wall_seconds(timestamps)
    return usage, next(iter(models)) if len(models) == 1 else None, str(session_id) if session_id else None


def normalize_openai(events: Iterable[dict[str, Any]]) -> tuple[dict[str, Any], str | None, str | None]:
    usage = empty_usage()
    timestamps: list[dt.datetime] = []
    model = None
    session_id = None
    last_total: dict[str, Any] | None = None
    turns = 0
    for event in events:
        parsed = parse_iso(event.get("timestamp"))
        if parsed: timestamps.append(parsed)
        payload = event.get("payload")
        if not isinstance(payload, dict): continue
        if event.get("type") == "session_meta":
            model = payload.get("model") or model
            session_id = payload.get("id") or session_id
        if payload.get("type") == "token_count":
            info = payload.get("info")
            if isinstance(info, dict) and isinstance(info.get("total_token_usage"), dict):
                last_total = info["total_token_usage"]
                if isinstance(info.get("last_token_usage"), dict): turns += 1
                context = info.get("model_context_window")
                if isinstance(context, int): usage["peak_context_tokens"] = max(int(usage["peak_context_tokens"]), int(last_total.get("input_tokens") or 0))
    if last_total:
        usage["input_tokens"] = int(last_total.get("input_tokens") or 0)
        usage["cached_input_tokens"] = int(last_total.get("cached_input_tokens") or 0)
        usage["output_tokens"] = int(last_total.get("output_tokens") or 0)
        usage["reasoning_tokens"] = int(last_total.get("reasoning_output_tokens") or 0)
    usage["turns"] = turns
    usage["wall_seconds"] = wall_seconds(timestamps)
    return usage, str(model) if model else None, str(session_id) if session_id else None


def normalize_moonshot(events: Iterable[dict[str, Any]]) -> tuple[dict[str, Any], str | None, str | None]:
    usage = empty_usage()
    models: set[str] = set()
    timestamps: list[dt.datetime] = []
    for event in events:
        millis = event.get("time")
        if isinstance(millis, (int, float)):
            timestamps.append(dt.datetime.fromtimestamp(float(millis) / 1000, dt.timezone.utc))
        if event.get("type") != "usage.record" or event.get("usageScope") != "turn": continue
        native = event.get("usage")
        if not isinstance(native, dict): continue
        if isinstance(event.get("model"), str): models.add(event["model"])
        other = int(native.get("inputOther") or 0)
        cached = int(native.get("inputCacheRead") or 0)
        created = int(native.get("inputCacheCreation") or 0)
        usage["input_tokens"] += other + created
        usage["cached_input_tokens"] += cached
        usage["output_tokens"] += int(native.get("output") or 0)
        usage["peak_context_tokens"] = max(int(usage["peak_context_tokens"]), other + created + cached)
        usage["turns"] += 1
    usage["wall_seconds"] = wall_seconds(timestamps)
    return usage, next(iter(models)) if len(models) == 1 else None, None


def normalize_xai(events: Iterable[dict[str, Any]]) -> tuple[dict[str, Any], str | None, str | None]:
    latest: tuple[float, dict[str, Any], str | None] | None = None
    models: set[str] = set()
    timestamps: list[dt.datetime] = []
    for event in events:
        timestamp = event.get("timestamp")
        if isinstance(timestamp, (int, float)):
            timestamps.append(dt.datetime.fromtimestamp(float(timestamp), dt.timezone.utc))
        params = event.get("params")
        update = params.get("update") if isinstance(params, dict) else None
        if not isinstance(update, dict) or update.get("sessionUpdate") != "turn_completed": continue
        native = update.get("usage")
        if not isinstance(native, dict): continue
        for name in (native.get("modelUsage") or {}): models.add(name)
        marker = float(timestamp or 0)
        if latest is None or marker >= latest[0]: latest = (marker, native, params.get("sessionId"))
    usage = empty_usage()
    session_id = None
    if latest:
        _, native, session_id = latest
        usage.update({
            "input_tokens": int(native.get("inputTokens") or 0),
            "cached_input_tokens": int(native.get("cachedReadTokens") or 0),
            "output_tokens": int(native.get("outputTokens") or 0),
            "reasoning_tokens": int(native.get("reasoningTokens") or 0),
            "peak_context_tokens": int(native.get("inputTokens") or 0),
            "turns": int(native.get("numTurns") or native.get("modelCalls") or 0),
            "wall_seconds": wall_seconds(timestamps),
        })
    return usage, next(iter(models)) if len(models) == 1 else None, str(session_id) if session_id else None


NORMALIZERS = {"anthropic": normalize_anthropic, "openai": normalize_openai, "moonshot": normalize_moonshot, "xai": normalize_xai}


def normalize(provider: str, lines: Iterable[str], metadata: dict[str, Any]) -> dict[str, Any]:
    if provider not in NORMALIZERS: raise NormalizeError(f"unsupported provider: {provider}")
    usage, effective_model, observed_session = NORMALIZERS[provider](json_lines(lines))
    terminal = metadata.get("terminal", "UNEVALUABLE")
    if terminal not in TERMINALS: raise NormalizeError("invalid terminal class")
    requested_model = metadata.get("requested_model")
    requested_effort = metadata.get("requested_effort")
    return {
        "schema": SCHEMA,
        "ts": metadata["ts"],
        "project": metadata["project"],
        "provider": provider,
        "quota_domain": metadata["quota_domain"],
        "session_id": metadata.get("session_id") or observed_session or "unknown",
        "requested_profile": {"model": requested_model, "effort": requested_effort},
        "effective_profile": {"model": effective_model, "effort": metadata.get("effective_effort")},
        "usage": usage,
        "terminal": {"class": terminal, "useful": bool(metadata.get("useful", False)), "evidence_digest": metadata.get("evidence_digest")},
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", choices=sorted(NORMALIZERS), required=True)
    parser.add_argument("--input", type=pathlib.Path, required=True)
    parser.add_argument("--metadata", type=pathlib.Path, required=True)
    parser.add_argument("--output", type=pathlib.Path)
    args = parser.parse_args(argv)
    try:
        metadata_bytes=read_bounded(args.metadata,MAX_METADATA_BYTES)
        validate_json_shape(metadata_bytes)
        metadata = json.loads(metadata_bytes.decode("utf-8"))
        input_bytes=read_bounded(args.input,MAX_INPUT_BYTES,MAX_INPUT_LINES)
        validate_json_shape(input_bytes)
        result = normalize(args.provider, input_bytes.decode("utf-8",errors="replace").splitlines(), metadata)
        encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
        if args.output: args.output.write_text(encoded, encoding="utf-8")
        else: print(encoded, end="")
        return 0
    except (OSError, UnicodeError, KeyError, json.JSONDecodeError, NormalizeError, ValueError, TypeError, OverflowError, AttributeError, RecursionError):
        print(json.dumps({"error": "INPUT_REFUSED"}, sort_keys=True), file=sys.stderr)
        return 22


if __name__ == "__main__":
    raise SystemExit(main())
