#!/usr/bin/env python3
"""Run the unchanged Windows census in four contained, accountable processes."""
from __future__ import annotations

import argparse
import ast
import ctypes
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time
import unittest
import uuid

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = 252
WORKERS = 4
DEADLINE_SECONDS = 720
JOB_SECONDS = 900
RESERVE_SECONDS = 90
MODULE = "test_universal_provider_control"
CENSUS_SHA256 = "fac79a2f8f40534a3dc7aef5698c5f1c6c6f5bf0cf3fc2eacf060c9be3fb8e4b"
HEAVY = (
    "test_frozen_r43_child_execution_is_bound_to_the_authenticated_graph",
    "test_historical_numbered_tests_are_semantically_quarantined",
)


class Refused(RuntimeError):
    pass


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode()).hexdigest()


def snapshot():
    def git(*args):
        return subprocess.check_output(
            ["git", "--no-replace-objects", "--no-optional-locks", "-C", str(ROOT),
             *args], timeout=30).decode().strip()
    if git("status", "--porcelain", "--untracked-files=all"):
        raise Refused("CLEAN_COMMITTED_SOURCE_REQUIRED")
    return {"head": git("rev-parse", "HEAD"), "tree": git("rev-parse", "HEAD^{tree}")}


def discover():
    def flatten(suite):
        for item in suite:
            if isinstance(item, unittest.TestSuite):
                yield from flatten(item)
            else:
                yield item
    cases = list(flatten(unittest.TestLoader().discover(
        str(ROOT / "tests"), pattern=MODULE + ".py")))
    ids = [case.id() for case in cases]
    verify_census(ids)
    return {case.id(): case for case in cases}


def verify_census(ids):
    if (len(ids) != EXPECTED or len(set(ids)) != EXPECTED
            or digest(sorted(ids)) != CENSUS_SHA256):
        raise Refused("CENSUS_CHANGED_REQUIRES_REVIEW")


def source_census():
    # Parse declarations without executing any project code in the parent.
    # Each contained worker independently verifies real unittest discovery.
    module = ast.parse((ROOT / "tests" / (MODULE + ".py")).read_text(encoding="utf-8"))
    ids = sorted(f"{MODULE}.{case.name}.{method.name}"
                 for case in module.body if isinstance(case, ast.ClassDef)
                 for method in case.body if isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef))
                 and method.name.startswith("test_"))
    verify_census(ids)
    return ids


def worker_budget():
    raw = os.environ.get("UNIVERSAL_JOB_STARTED_UNIX")
    if raw is None:
        if os.environ.get("GITHUB_ACTIONS") == "true":
            raise Refused("CI_JOB_CLOCK_REQUIRED")
        return DEADLINE_SECONDS
    elapsed = time.time() - float(raw)
    if not math.isfinite(elapsed) or elapsed < 0:
        raise Refused("INVALID_JOB_CLOCK")
    remaining = min(DEADLINE_SECONDS, JOB_SECONDS - elapsed - RESERVE_SECONDS)
    if remaining <= 0:
        raise Refused("INSUFFICIENT_JOB_CLEANUP_RESERVE")
    return remaining


def partition(ids):
    ids = sorted(ids)
    if len(ids) != EXPECTED or len(set(ids)) != EXPECTED:
        raise Refused("INVALID_CENSUS")
    shards = [[], [], [], []]
    remaining = ids.copy()
    # Retained cancelled Windows logs show the frozen child execution alone
    # taking 424 s, and quarantine still running after 203 s. Isolate both;
    # split the other 250 tests deterministically. Receipts measure actual balance.
    for index, name in enumerate(HEAVY):
        matches = [item for item in remaining if item.endswith("." + name)]
        if len(matches) != 1:
            raise Refused("TIMING_ANCHOR_CHANGED_REQUIRES_REVIEW")
        shards[index] = matches
        remaining.remove(matches[0])
    for index, item in enumerate(remaining):
        shards[2 + index % 2].append(item)
    return shards


def plan_for(cases, source, run_id):
    ids = sorted(cases)
    return {"version": 1, "run_id": run_id, "source": source,
            "census": ids, "census_sha256": digest(ids), "shards": partition(ids)}


def validate_receipts(plan, receipts):
    expected_plan = plan_for(plan["census"], plan["source"], plan["run_id"])
    if plan != expected_plan or len(receipts) != WORKERS:
        raise Refused("PLAN_OR_RECEIPT_COUNT_MISMATCH")
    all_executed = []
    for index, receipt in enumerate(receipts):
        assigned = plan["shards"][index]
        if (receipt.get("plan_sha256") != digest(plan)
                or type(receipt.get("worker")) is not int or receipt["worker"] != index
                or receipt.get("assigned") != assigned
                or receipt.get("started") != assigned
                or receipt.get("stopped") != assigned
                or receipt.get("successful") != assigned):
            raise Refused("RECEIPT_IDENTITY_OR_EXECUTION_MISMATCH")
        expected_counts = {"tests_run": len(assigned), "exit_status": 0,
                           "failures": 0, "errors": 0, "skips": 0,
                           "expected_failures": 0, "unexpected_successes": 0}
        for key, value in expected_counts.items():
            if type(receipt.get(key)) is not int or receipt[key] != value:
                raise Refused("RECEIPT_OUTCOME_MISMATCH:" + key)
        timings = receipt.get("test_seconds")
        if not isinstance(timings, dict) or sorted(timings) != assigned:
            raise Refused("RECEIPT_TIMING_MISMATCH")
        for value in [receipt.get("seconds"), *timings.values()]:
            if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
                raise Refused("INVALID_RECEIPT_DURATION")
        all_executed.extend(receipt["stopped"])
    if sorted(all_executed) != plan["census"] or len(set(all_executed)) != EXPECTED:
        raise Refused("AGGREGATE_CENSUS_MISMATCH")


def read_json(path):
    def unique(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise Refused("DUPLICATE_JSON_KEY")
            value[key] = item
        return value
    value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique,
                       parse_constant=lambda _: (_ for _ in ()).throw(Refused("NONFINITE_JSON")))
    if not isinstance(value, dict):
        raise Refused("JSON_OBJECT_REQUIRED")
    return value


def atomic_json(path, value):
    temporary = path.with_suffix(".partial")
    with temporary.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, sort_keys=True, allow_nan=False)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    if path.exists():
        raise Refused("RECEIPT_ALREADY_EXISTS")
    temporary.replace(path)


class RecordingResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.started, self.stopped, self.successful = [], [], []
        self.test_seconds = {}

    def startTest(self, test):
        self.started.append(test.id())
        self.began = time.monotonic()
        super().startTest(test)

    def stopTest(self, test):
        self.stopped.append(test.id())
        self.test_seconds[test.id()] = time.monotonic() - self.began
        super().stopTest(test)

    def addSuccess(self, test):
        self.successful.append(test.id())
        super().addSuccess(test)


def worker(output, index):
    # No project imports, tests or grandchildren before the parent attaches us
    # to the kill-on-close Job Object. EOF also refuses execution.
    if sys.stdin.readline() != "GO\n":
        raise Refused("CONTAINMENT_HANDSHAKE_MISSING")
    plan = read_json(output / "plan.json")
    cases = discover()
    source = snapshot()
    if index not in range(WORKERS) or plan != plan_for(cases, source, plan["run_id"]):
        raise Refused("WORKER_PLAN_OR_SOURCE_MISMATCH")
    assigned = plan["shards"][index]
    start = time.monotonic()
    result = unittest.TextTestRunner(verbosity=2, resultclass=RecordingResult).run(
        unittest.TestSuite(cases[item] for item in assigned))
    if snapshot() != source:
        raise Refused("SOURCE_CHANGED_DURING_EXECUTION")
    status = 0 if result.wasSuccessful() and not result.skipped and not result.expectedFailures else 1
    receipt = {"plan_sha256": digest(plan), "worker": index, "assigned": assigned,
               "started": result.started, "stopped": result.stopped,
               "successful": result.successful, "test_seconds": result.test_seconds,
               "seconds": time.monotonic() - start, "tests_run": result.testsRun,
               "failures": len(result.failures), "errors": len(result.errors),
               "skips": len(result.skipped), "expected_failures": len(result.expectedFailures),
               "unexpected_successes": len(result.unexpectedSuccesses), "exit_status": status}
    atomic_json(output / f"worker-{index}.json", receipt)
    print(json.dumps(receipt, sort_keys=True), flush=True)
    return status


# Win32 fixed-width fields are deliberate: Python's C long varies by platform.
U32, U64, I64, SIZE = ctypes.c_uint32, ctypes.c_uint64, ctypes.c_int64, ctypes.c_size_t


class BasicLimit(ctypes.Structure):
    _fields_ = [("process_time", I64), ("job_time", I64), ("flags", U32),
                ("minimum_working_set", SIZE), ("maximum_working_set", SIZE),
                ("active_limit", U32), ("affinity", SIZE), ("priority", U32), ("scheduling", U32)]


class IoCounters(ctypes.Structure):
    _fields_ = [(name, U64) for name in ("read_ops", "write_ops", "other_ops",
                                      "read_bytes", "write_bytes", "other_bytes")]


class ExtendedLimit(ctypes.Structure):
    _fields_ = [("basic", BasicLimit), ("io", IoCounters), ("process_memory", SIZE),
                ("job_memory", SIZE), ("peak_process", SIZE), ("peak_job", SIZE)]


class Accounting(ctypes.Structure):
    _fields_ = [("user", I64), ("kernel", I64), ("period_user", I64), ("period_kernel", I64),
                ("page_faults", U32), ("total", U32), ("active", U32), ("terminated", U32)]


class WindowsJob:
    def __init__(self):
        if os.name != "nt":
            raise Refused("WINDOWS_REQUIRED")
        self.api = ctypes.WinDLL("kernel32", use_last_error=True)
        signatures = {
            "CreateJobObjectW": ([ctypes.c_void_p, ctypes.c_wchar_p], ctypes.c_void_p),
            "SetInformationJobObject": ([ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p, U32], ctypes.c_int),
            "AssignProcessToJobObject": ([ctypes.c_void_p, ctypes.c_void_p], ctypes.c_int),
            "TerminateJobObject": ([ctypes.c_void_p, U32], ctypes.c_int),
            "QueryInformationJobObject": ([ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p, U32, ctypes.c_void_p], ctypes.c_int),
            "CloseHandle": ([ctypes.c_void_p], ctypes.c_int),
        }
        for name, (arguments, result) in signatures.items():
            function = getattr(self.api, name)
            function.argtypes, function.restype = arguments, result
        self.handle = self.api.CreateJobObjectW(None, None)
        if not self.handle:
            raise ctypes.WinError(ctypes.get_last_error())
        limits = ExtendedLimit()
        limits.basic.flags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        try:
            self.check(self.api.SetInformationJobObject(
                self.handle, 9, ctypes.byref(limits), ctypes.sizeof(limits)))
        except BaseException:
            self.close()
            raise

    @staticmethod
    def check(result):
        if not result:
            raise ctypes.WinError(ctypes.get_last_error())

    def attach(self, process):
        self.check(self.api.AssignProcessToJobObject(self.handle, int(process._handle)))

    def active(self):
        accounting = Accounting()
        self.check(self.api.QueryInformationJobObject(
            self.handle, 1, ctypes.byref(accounting), ctypes.sizeof(accounting), None))
        return accounting.active

    def close(self):
        if self.handle:
            self.check(self.api.CloseHandle(self.handle))
            self.handle = None

    def cleanup(self, processes, timeout=20):
        errors = []
        deadline = time.monotonic() + timeout
        try:
            self.check(self.api.TerminateJobObject(self.handle, 1))
            for process in processes:
                process.wait(timeout=max(0.01, deadline - time.monotonic()))
            while self.active():
                if time.monotonic() >= deadline:
                    raise Refused("JOB_DESCENDANTS_NOT_REAPED")
                time.sleep(0.05)
        except BaseException as error:
            errors.append(error)
        finally:
            # Kill-on-close also covers an interrupted or failed explicit kill.
            try:
                self.close()
            except BaseException as error:
                errors.append(error)
            for process in processes:
                try:
                    process.wait(timeout=5)
                except BaseException as error:
                    errors.append(error)
        if errors:
            raise Refused("INCOMPLETE_PROCESS_CLEANUP:" + repr(errors))


def wait_workers(processes, deadline):
    while True:
        codes = [process.poll() for process in processes]
        if any(code is not None and code != 0 for code in codes):
            raise Refused("CHILD_FAILED:" + repr(codes))
        if all(code == 0 for code in codes):
            return
        if time.monotonic() >= deadline:
            raise Refused("WORKER_DEADLINE_EXCEEDED")
        time.sleep(0.1)


def run(output):
    if os.name != "nt":
        raise Refused("WINDOWS_REQUIRED_USE_UNCHANGED_DISCOVERY_ON_LINUX")
    output = output.resolve()
    if output == ROOT or ROOT in output.parents:
        raise Refused("RECEIPTS_MUST_BE_OUTSIDE_SOURCE_CHECKOUT")
    source = snapshot()
    cases = source_census()
    plan = plan_for(cases, source, uuid.uuid4().hex)
    output.mkdir(parents=True, exist_ok=False)
    atomic_json(output / "plan.json", plan)
    print(json.dumps({"plan": plan}, sort_keys=True), flush=True)
    processes, logs = [], []
    job = WindowsJob()
    started = time.monotonic()
    try:
        budget = worker_budget()
        for index in range(WORKERS):
            log = (output / f"worker-{index}.log").open("xb")
            logs.append(log)
            process = subprocess.Popen(
                [sys.executable, "-u", str(Path(__file__).resolve()), "--output-dir", str(output),
                 "--worker", str(index)], cwd=ROOT, stdin=subprocess.PIPE,
                stdout=log, stderr=subprocess.STDOUT)
            try:
                job.attach(process)
            except BaseException:
                # This child is still at its handshake, so has no descendants.
                try:
                    process.kill()
                    process.wait(timeout=10)
                finally:
                    process.stdin.close()
                raise
            processes.append(process)
            process.stdin.write(b"GO\n")
            process.stdin.close()
        wait_workers(processes, started + budget)
        if job.active() != 0:
            raise Refused("WORKER_LEFT_LIVE_DESCENDANTS")
    finally:
        try:
            job.cleanup(processes)
        finally:
            for log in logs:
                log.close()
            for index in range(len(logs)):
                print(f"--- worker {index} log ---", flush=True)
                print((output / f"worker-{index}.log").read_text(encoding="utf-8", errors="replace"), flush=True)
            print(f"Preserved receipts and logs: {output}", flush=True)
    if snapshot() != source:
        raise Refused("PARENT_SOURCE_CHANGED")
    receipts = [read_json(output / f"worker-{index}.json") for index in range(WORKERS)]
    validate_receipts(plan, receipts)
    # Full completion receipts remain in normal CI logs even when artifacts expire.
    for receipt in receipts:
        print(json.dumps(receipt, sort_keys=True), flush=True)
    summary = {"status": "PASS", "plan": plan, "tests_run": EXPECTED,
               "workers": WORKERS, "seconds": time.monotonic() - started}
    atomic_json(output / "complete.json", summary)
    print(json.dumps(summary, sort_keys=True), flush=True)
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--worker", type=int)
    args = parser.parse_args()
    try:
        return worker(args.output_dir, args.worker) if args.worker is not None else run(args.output_dir)
    except Exception as error:
        print(f"UNIVERSAL_RUN_REFUSED: {error}", file=sys.stderr, flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
