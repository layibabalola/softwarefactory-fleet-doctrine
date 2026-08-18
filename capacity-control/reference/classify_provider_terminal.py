#!/usr/bin/env python3
"""Classify bounded provider refusal output without invoking a model.

The classifier emits no raw provider prose. Structured status/code fields win; narrowly bounded
text patterns are a compatibility fallback for CLIs that expose quota refusal only as text.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import sys
from typing import Any, Iterable, Sequence


SCHEMA = "fleet-provider-terminal-classification/v1"
LIMIT_PATTERNS = (
    ("SESSION_LIMIT", re.compile(r"\breached\s+(?:your\s+)?(?:[a-z0-9.-]+\s+){0,3}session\s+limit\b", re.I)),
    ("WEEKLY_LIMIT", re.compile(r"\breached\s+(?:your\s+)?(?:[a-z0-9.-]+\s+){0,3}weekly\s+limit\b", re.I)),
    ("USAGE_LIMIT", re.compile(r"\b(?:usage|credit|spend)\s+limit\s+(?:has\s+been\s+)?(?:reached|exceeded)\b", re.I)),
    ("RATE_LIMIT", re.compile(r"\brate\s+limit(?:ed|\s+(?:reached|exceeded))?\b", re.I)),
)
AUTH_PATTERN = re.compile(r"\b(?:authentication|authorization|sign[ -]?in|log[ -]?in)\s+(?:required|failed|expired)\b", re.I)
RFC3339_PATTERN = re.compile(r"\b(20\d\d-[01]\d-[0-3]\dT[0-2]\d:[0-5]\d:[0-5]\d(?:\.\d+)?(?:Z|[+-][0-2]\d:[0-5]\d))\b")


class ClassificationError(RuntimeError):
    pass


def _walk(value: Any) -> Iterable[tuple[str, Any]]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield str(key), child
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def _structured_signal(text: str) -> tuple[str, str] | None:
    candidates: list[Any] = []
    stripped = text.strip()
    if stripped:
        try:
            candidates.append(json.loads(stripped))
        except json.JSONDecodeError:
            for line in stripped.splitlines():
                try:
                    candidates.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    for candidate in candidates:
        for key, value in _walk(candidate):
            lowered = key.lower()
            if lowered in {"status", "status_code", "http_status"} and value in {429, "429"}:
                return "QUOTA_BLOCKED", "HTTP_429"
            if lowered in {"code", "error_code", "type"} and isinstance(value, str):
                normalized = value.lower()
                if any(token in normalized for token in ("rate_limit", "quota", "usage_limit", "credit_limit")):
                    return "QUOTA_BLOCKED", "STRUCTURED_LIMIT"
                if any(token in normalized for token in ("auth", "unauthorized", "forbidden")):
                    return "REFUSED", "AUTH_REQUIRED"
    return None


def classify(provider: str, text: str) -> dict[str, Any]:
    if not isinstance(provider, str) or not re.fullmatch(r"[a-z0-9][a-z0-9._-]{1,31}", provider):
        raise ClassificationError("provider has invalid syntax")
    if not isinstance(text, str):
        raise ClassificationError("provider output must be text")
    if len(text.encode("utf-8", errors="replace")) > 262_144:
        raise ClassificationError("provider output exceeds the bounded classifier input")

    signal = _structured_signal(text)
    if signal is None:
        for reason, pattern in LIMIT_PATTERNS:
            if pattern.search(text):
                signal = ("QUOTA_BLOCKED", reason)
                break
    if signal is None and AUTH_PATTERN.search(text):
        signal = ("REFUSED", "AUTH_REQUIRED")
    terminal, reason = signal or ("UNEVALUABLE", "NO_RECOGNIZED_TERMINAL")
    reset_match = RFC3339_PATTERN.search(text) if terminal == "QUOTA_BLOCKED" else None
    return {
        "schema": SCHEMA,
        "provider": provider,
        "terminal": terminal,
        "reason": reason,
        "reset_at": reset_match.group(1) if reset_match else None,
        "raw_sha256": hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest(),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", required=True)
    parser.add_argument("--input", type=pathlib.Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = classify(args.provider, args.input.read_text(encoding="utf-8", errors="replace"))
        print(json.dumps(result, sort_keys=True, separators=(",", ":")))
        return 0 if result["terminal"] != "UNEVALUABLE" else 23
    except (OSError, ClassificationError) as exc:
        print(json.dumps({"error": "UNEVALUABLE", "detail": str(exc)}, sort_keys=True), file=sys.stderr)
        return 22


if __name__ == "__main__":
    raise SystemExit(main())
