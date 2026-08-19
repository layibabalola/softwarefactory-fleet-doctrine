#!/usr/bin/env python3
"""Normalize structured provider capacity evidence into capacity-snapshot-v1."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib
import sys
from typing import Any, Sequence


SCHEMA = "fleet-capacity-snapshot/v1"
MAX_INPUT_BYTES = 16 * 1024 * 1024
MAX_INPUT_LINES = 200_000


class CapacityError(RuntimeError):
    pass


def parse_time(value: Any) -> dt.datetime | None:
    if not isinstance(value, str): return None
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed.astimezone(dt.timezone.utc) if parsed.tzinfo else None


def iso(value: dt.datetime | None) -> str | None:
    return value.isoformat().replace("+00:00", "Z") if value else None


def read_bounded(path: pathlib.Path) -> bytes:
    if path.is_symlink(): raise CapacityError("SYMLINK_REFUSED")
    if path.stat().st_size > MAX_INPUT_BYTES: raise CapacityError("INPUT_TOO_LARGE")
    with path.open("rb") as source: data=source.read(MAX_INPUT_BYTES+1)
    if len(data)>MAX_INPUT_BYTES: raise CapacityError("INPUT_TOO_LARGE")
    if data.count(b"\n")+(0 if not data or data.endswith(b"\n") else 1)>MAX_INPUT_LINES: raise CapacityError("INPUT_LINE_LIMIT")
    return data


def anthropic(raw: dict[str, Any]) -> list[dict[str, Any]]:
    durations = {"five_hour": dt.timedelta(hours=5), "seven_day": dt.timedelta(days=7)}
    windows=[]
    for native, name in (("five_hour","five-hour"),("seven_day","weekly")):
        bucket=raw.get(native)
        if not isinstance(bucket,dict): continue
        used=bucket.get("utilization")
        reset=parse_time(bucket.get("resets_at"))
        windows.append({"name":name,"used_fraction":float(used)/100 if isinstance(used,(int,float)) else None,"resets_at":iso(reset),"window_started_at":iso(reset-durations[native]) if reset else None})
    if not windows: raise CapacityError("Anthropic evidence contains no five_hour or seven_day bucket")
    return windows


def openai(lines: list[str]) -> list[dict[str, Any]]:
    latest=None
    for line in lines:
        try: event=json.loads(line)
        except json.JSONDecodeError: continue
        payload=event.get("payload") if isinstance(event,dict) else None
        if isinstance(payload,dict) and payload.get("type")=="token_count" and isinstance(payload.get("rate_limits"),dict): latest=payload["rate_limits"]
    if latest is None: raise CapacityError("OpenAI evidence contains no token_count rate_limits event")
    windows=[]
    for native,name in (("primary","primary"),("secondary","secondary")):
        bucket=latest.get(native)
        if not isinstance(bucket,dict): continue
        used=bucket.get("used_percent"); reset_epoch=bucket.get("resets_at"); minutes=bucket.get("window_minutes")
        reset=dt.datetime.fromtimestamp(float(reset_epoch),dt.timezone.utc) if isinstance(reset_epoch,(int,float)) else None
        started=reset-dt.timedelta(minutes=float(minutes)) if reset and isinstance(minutes,(int,float)) else None
        windows.append({"name":name,"used_fraction":float(used)/100 if isinstance(used,(int,float)) else None,"resets_at":iso(reset),"window_started_at":iso(started)})
    if not windows: raise CapacityError("OpenAI rate_limits contains no primary or secondary window")
    return windows


def normalize(provider: str, text: str, quota_domain: str, observed_at: str, artifact_hash: str) -> dict[str, Any]:
    if ":sha256:" not in quota_domain: raise CapacityError("quota_domain must be opaque provider:sha256 form")
    if provider=="anthropic":
        try: raw=json.loads(text)
        except json.JSONDecodeError as exc: raise CapacityError("Anthropic evidence must be one JSON object") from exc
        if not isinstance(raw,dict): raise CapacityError("Anthropic evidence must be one JSON object")
        windows=anthropic(raw)
    elif provider=="openai": windows=openai(text.splitlines())
    else: raise CapacityError(f"no structured capacity adapter for {provider}")
    return {"schema":SCHEMA,"provider":provider,"quota_domain":quota_domain,"observed_at":observed_at,"windows":windows,"source":{"kind":"provider-structured-usage","artifact_sha256":artifact_hash}}


def main(argv: Sequence[str] | None=None) -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider",choices=["anthropic","openai"],required=True)
    parser.add_argument("--input",type=pathlib.Path,required=True)
    parser.add_argument("--quota-domain",required=True)
    parser.add_argument("--observed-at",required=True)
    parser.add_argument("--output",type=pathlib.Path)
    args=parser.parse_args(argv)
    try:
        raw=read_bounded(args.input)
        result=normalize(args.provider,raw.decode("utf-8"),args.quota_domain,args.observed_at,hashlib.sha256(raw).hexdigest())
        encoded=json.dumps(result,indent=2,sort_keys=True)+"\n"
        if args.output: args.output.write_text(encoded,encoding="utf-8")
        else: print(encoded,end="")
        return 0
    except (OSError,UnicodeError,CapacityError):
        print(json.dumps({"error":"INPUT_REFUSED"},sort_keys=True),file=sys.stderr)
        return 22


if __name__=="__main__": raise SystemExit(main())
