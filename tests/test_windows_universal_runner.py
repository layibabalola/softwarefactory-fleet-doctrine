"""Receipt falsification and real Windows descendant-containment controls."""
import copy
import ctypes
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import run_windows_universal_tests as runner


class ReceiptTests(unittest.TestCase):
    def setUp(self):
        ids = [f"suite.C.test_{index:03}" for index in range(250)]
        ids += ["suite.C." + name for name in runner.HEAVY]
        self.plan = runner.plan_for(ids, {"head": "a" * 40, "tree": "b" * 40}, "fresh")
        self.receipts = []
        for index, assigned in enumerate(self.plan["shards"]):
            self.receipts.append({
                "plan_sha256": runner.digest(self.plan), "worker": index,
                "assigned": assigned.copy(), "started": assigned.copy(), "stopped": assigned.copy(),
                "successful": assigned.copy(), "test_seconds": {item: 0.1 for item in assigned},
                "seconds": 1.0, "tests_run": len(assigned), "exit_status": 0,
                "failures": 0, "errors": 0, "skips": 0, "expected_failures": 0,
                "unexpected_successes": 0})

    def test_complete_census_and_deterministic_isolation(self):
        runner.validate_receipts(self.plan, self.receipts)
        self.assertEqual([len(shard) for shard in self.plan["shards"]], [1, 1, 125, 125])
        self.assertEqual(runner.partition(reversed(self.plan["census"])), self.plan["shards"])

    def test_missing_duplicate_extra_and_reordered_executions_refused(self):
        for key in ("assigned", "started", "stopped", "successful"):
            for mutate in (lambda ids: ids[:-1], lambda ids: ids + ids[:1],
                           lambda ids: ids + ["extra"], lambda ids: list(reversed(ids))):
                with self.subTest(key=key, mutation=mutate):
                    receipts = copy.deepcopy(self.receipts)
                    receipts[2][key] = mutate(receipts[2][key])
                    with self.assertRaises(runner.Refused):
                        runner.validate_receipts(self.plan, receipts)

    def test_missing_extra_and_duplicate_receipts_refused(self):
        for receipts in (self.receipts[:-1], self.receipts + self.receipts[:1],
                         [self.receipts[0]] * 4):
            with self.subTest(receipts=len(receipts)), self.assertRaises(runner.Refused):
                runner.validate_receipts(self.plan, receipts)

    def test_stale_source_census_and_nonce_refused(self):
        for key, value in (("source", {"head": "c" * 40}), ("run_id", "stale"),
                           ("census_sha256", "wrong")):
            plan = copy.deepcopy(self.plan)
            plan[key] = value
            with self.subTest(key=key), self.assertRaises(runner.Refused):
                runner.validate_receipts(plan, self.receipts)
        plan = copy.deepcopy(self.plan)
        plan["census"][0] = "extra"
        with self.assertRaises(runner.Refused):
            runner.validate_receipts(plan, self.receipts)

    def test_failures_errors_skips_partial_results_and_malformed_counts_refused(self):
        for key in ("tests_run", "exit_status", "failures", "errors", "skips",
                    "expected_failures", "unexpected_successes", "worker"):
            for value in (None, True, "0", -1, 999):
                receipts = copy.deepcopy(self.receipts)
                receipts[0][key] = value
                with self.subTest(key=key, value=value), self.assertRaises(runner.Refused):
                    runner.validate_receipts(self.plan, receipts)

    def test_corrupt_missing_and_partial_json_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "receipt.json"
            with self.assertRaises(FileNotFoundError):
                runner.read_json(path)
            for raw in ('{"unfinished":', '{"a":1,"a":2}', '{"a":NaN}', '[]'):
                path.write_text(raw, encoding="utf-8")
                with self.subTest(raw=raw), self.assertRaises((ValueError, runner.Refused)):
                    runner.read_json(path)

    def test_nonfinite_and_missing_timings_refused(self):
        for value in (None, True, float("nan"), float("inf"), -1):
            receipts = copy.deepcopy(self.receipts)
            receipts[0]["seconds"] = value
            with self.subTest(value=value), self.assertRaises(runner.Refused):
                runner.validate_receipts(self.plan, receipts)
        receipts = copy.deepcopy(self.receipts)
        receipts[0]["test_seconds"] = {}
        with self.assertRaises(runner.Refused):
            runner.validate_receipts(self.plan, receipts)

    def test_atomic_receipt_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "receipt.json"
            runner.atomic_json(path, {"first": True})
            with self.assertRaises(runner.Refused):
                runner.atomic_json(path, {"second": True})
            self.assertEqual(runner.read_json(path), {"first": True})

    def test_recording_result_detects_fixture_failure_without_execution(self):
        class Broken(unittest.TestCase):
            @classmethod
            def setUpClass(cls):
                raise RuntimeError("fixture failed")

            def test_never_runs(self):
                self.fail("must not run")
        result = unittest.TextTestRunner(stream=io.StringIO(), resultclass=runner.RecordingResult).run(
            unittest.defaultTestLoader.loadTestsFromTestCase(Broken))
        self.assertEqual(result.started, [])
        self.assertEqual(result.stopped, [])
        self.assertEqual(result.testsRun, 0)
        self.assertEqual(len(result.errors), 1)

    def test_child_failure_timeout_and_success_are_distinct(self):
        process = mock.Mock()
        process.poll.return_value = 2
        with self.assertRaisesRegex(runner.Refused, "CHILD_FAILED"):
            runner.wait_workers([process], time.monotonic() + 10)
        process.poll.return_value = None
        with self.assertRaisesRegex(runner.Refused, "DEADLINE"):
            runner.wait_workers([process], time.monotonic() - 1)
        process.poll.return_value = 0
        runner.wait_workers([process], time.monotonic() + 10)

    def test_handshake_eof_refuses_before_project_discovery(self):
        with mock.patch.object(sys, "stdin", io.StringIO("")), mock.patch.object(runner, "discover") as discover:
            with self.assertRaisesRegex(runner.Refused, "HANDSHAKE"):
                runner.worker(Path("unused"), 0)
            discover.assert_not_called()


@unittest.skipUnless(os.name == "nt", "Windows Job Object lifecycle controls")
class WindowsContainmentTests(unittest.TestCase):
    def test_parent_interrupt_and_child_failure_always_clean_every_started_worker(self):
        ids = [f"suite.C.test_{index:03}" for index in range(250)]
        ids += ["suite.C." + name for name in runner.HEAVY]
        for error in (KeyboardInterrupt(), runner.Refused("CHILD_FAILED"),
                      runner.Refused("WORKER_DEADLINE_EXCEEDED")):
            with self.subTest(error=type(error).__name__), tempfile.TemporaryDirectory() as directory:
                job = mock.Mock()
                processes = [mock.Mock() for _ in range(4)]
                with mock.patch.object(runner, "snapshot", return_value={"head": "a" * 40}), \
                     mock.patch.object(runner, "discover", return_value=dict.fromkeys(ids)), \
                     mock.patch.object(runner, "WindowsJob", return_value=job), \
                     mock.patch.object(runner.subprocess, "Popen", side_effect=processes), \
                     mock.patch.object(runner, "wait_workers", side_effect=error), \
                     mock.patch("builtins.print"):
                    with self.assertRaises(type(error)):
                        runner.run(Path(directory) / "new-run")
                job.cleanup.assert_called_once_with(processes)
                self.assertEqual(job.attach.call_count, 4)

    def test_assignment_failure_kills_handshake_child_without_starting_tests(self):
        ids = [f"suite.C.test_{index:03}" for index in range(250)]
        ids += ["suite.C." + name for name in runner.HEAVY]
        with tempfile.TemporaryDirectory() as directory:
            job, process = mock.Mock(), mock.Mock()
            job.attach.side_effect = OSError("assignment refused")
            with mock.patch.object(runner, "snapshot", return_value={"head": "a" * 40}), \
                 mock.patch.object(runner, "discover", return_value=dict.fromkeys(ids)), \
                 mock.patch.object(runner, "WindowsJob", return_value=job), \
                 mock.patch.object(runner.subprocess, "Popen", return_value=process), \
                 mock.patch("builtins.print"):
                with self.assertRaisesRegex(OSError, "assignment refused"):
                    runner.run(Path(directory) / "new-run")
            process.kill.assert_called_once()
            process.wait.assert_called_once_with(timeout=10)
            process.stdin.write.assert_not_called()
            process.stdin.close.assert_called_once()
            job.cleanup.assert_called_once_with([])

    def test_win64_layout_matches_windows_sdk(self):
        if ctypes.sizeof(ctypes.c_void_p) == 8:
            self.assertEqual(ctypes.sizeof(runner.BasicLimit), 64)
            self.assertEqual(ctypes.sizeof(runner.ExtendedLimit), 144)
        self.assertEqual(ctypes.sizeof(runner.Accounting), 48)

    def test_timeout_kills_and_reaps_workers_and_grandchild(self):
        code = ("import subprocess,sys,time; "
                "assert sys.stdin.readline() == 'GO\\n'; "
                "child=subprocess.Popen([sys.executable,'-c','import time;time.sleep(120)']); "
                "time.sleep(120)")
        job = runner.WindowsJob()
        processes = []
        try:
            for _ in range(4):
                process = subprocess.Popen([sys.executable, "-c", code], stdin=subprocess.PIPE,
                                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                processes.append(process)
                job.attach(process)
                process.stdin.write(b"GO\n")
                process.stdin.close()
            deadline = time.monotonic() + 10
            while job.active() != 8 and time.monotonic() < deadline:
                time.sleep(0.05)
            self.assertEqual(job.active(), 8)
            with self.assertRaisesRegex(runner.Refused, "DEADLINE"):
                runner.wait_workers(processes, time.monotonic() - 1)
            job.cleanup(processes)
            self.assertIsNone(job.handle)
            self.assertTrue(all(process.poll() is not None for process in processes))
        finally:
            if job.handle:
                job.cleanup(processes)

    def test_incomplete_cleanup_is_failure_even_if_close_fallback_reaps_child(self):
        job = runner.WindowsJob()
        process = subprocess.Popen([sys.executable, "-c", "import time;time.sleep(120)"],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            job.attach(process)
            with mock.patch.object(job, "active", return_value=1):
                with self.assertRaisesRegex(runner.Refused, "INCOMPLETE_PROCESS_CLEANUP"):
                    job.cleanup([process], timeout=0)
            self.assertIsNotNone(process.poll())
        finally:
            if job.handle:
                job.cleanup([process])


if __name__ == "__main__":
    unittest.main()
