"""Receipt falsification and real Windows descendant-containment controls."""
import contextlib
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
import types
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import run_windows_universal_tests as runner


class RaisingStream(io.StringIO):
    """A stdout that fails every write once armed."""
    armed = True

    def write(self, text):
        if self.armed:
            raise OSError("stdout unavailable")
        return super().write(text)


class ReceiptTests(unittest.TestCase):
    def test_same_count_census_substitution_is_refused(self):
        ids = runner.source_census()
        runner.verify_census(ids)
        ids[0] += "_substituted"
        with self.assertRaisesRegex(runner.Refused, "CENSUS_CHANGED_REQUIRES_REVIEW"):
            runner.verify_census(ids)

    def test_parent_census_never_imports_project_tests(self):
        with mock.patch.object(unittest.TestLoader, "discover", side_effect=AssertionError("import")):
            self.assertEqual(len(runner.source_census()), 252)

    def test_job_budget_reserves_cleanup_and_downstream_time(self):
        with mock.patch.dict(os.environ, {"UNIVERSAL_JOB_STARTED_UNIX": "1000"}), \
             mock.patch.object(runner.time, "time", return_value=1200):
            self.assertEqual(runner.worker_budget(), 610)
        for start in ("NaN", "Infinity", "3000", "100"):
            with mock.patch.dict(os.environ, {"UNIVERSAL_JOB_STARTED_UNIX": start}), \
                 mock.patch.object(runner.time, "time", return_value=1200), \
                 self.subTest(start=start), self.assertRaises(runner.Refused):
                runner.worker_budget()
        with mock.patch.dict(os.environ, {"GITHUB_ACTIONS": "true"}, clear=True):
            with self.assertRaisesRegex(runner.Refused, "CI_JOB_CLOCK_REQUIRED"):
                runner.worker_budget()

    def setUp(self):
        ids = runner.source_census()
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
            self.assertFalse(path.with_suffix(".partial").exists())

    def test_receipt_created_during_publication_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "receipt.json"
            real_link = os.link
            def racing_link(source, target):
                target.write_bytes(b"concurrent original")
                real_link(source, target)
            with mock.patch.object(runner.os, "link", side_effect=racing_link):
                with self.assertRaisesRegex(runner.Refused, "RECEIPT_ALREADY_EXISTS"):
                    runner.atomic_json(path, {"replacement": True})
            self.assertEqual(path.read_bytes(), b"concurrent original")
            self.assertFalse(path.with_suffix(".partial").exists())

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

    def write_progress(self, directory, index, completed, in_flight=None, torn=False):
        lines = []
        for name, seconds in completed:
            lines += [json.dumps({"start": name, "wall": 1.0}), json.dumps({"stop": name, "seconds": seconds})]
        if in_flight:
            lines.append(json.dumps({"start": in_flight, "wall": 1000.0}))
        text = "\n".join(lines) + "\n" + ('{"start": "torn' if torn else "")
        (Path(directory) / f"worker-{index}.progress.jsonl").write_text(text, encoding="utf-8")

    def progress_lines(self, printed, event):
        lines = [json.loads(call.args[0]) for call in printed.call_args_list
                 if call.args and str(call.args[0]).startswith("{")]
        return [line for line in lines if line.get("event") == event]

    def test_deadline_progress_names_binding_worker_and_in_flight_test(self):
        shards = self.plan["shards"]
        with tempfile.TemporaryDirectory() as directory:
            self.write_progress(directory, 0, [(shards[0][0], 400.0)])
            self.write_progress(directory, 1, [], in_flight=shards[1][0])
            self.write_progress(directory, 2, [(name, 2.0) for name in shards[2][:60]]
                                + [(shards[2][60], 90.0)], in_flight=shards[2][61], torn=True)
            self.write_progress(directory, 3, [(name, 1.0) for name in shards[3]])
            failure = ("WORKER_DEADLINE_EXCEEDED", [0, None, None, 0], 1709.0, 1300.0)
            with mock.patch("builtins.print") as printed:
                runner.report_progress(Path(directory), self.plan, 709.0, 1000.0,
                                       {0: 1500.0, 3: 1600.0}, failure)
        progress = self.progress_lines(printed, "UNIVERSAL_WORKER_PROGRESS")
        self.assertEqual([line["worker"] for line in progress], [0, 1, 2, 3])
        for line in progress:
            self.assertLessEqual({"worker", "elapsed_seconds", "budget_seconds", "last_started_test",
                                  "completed_count", "planned_count"}, set(line))
            self.assertEqual(line["budget_seconds"], 709.0)
        self.assertEqual([line["binding"] for line in progress], [False, True, True, False])
        self.assertEqual([line["elapsed_seconds"] for line in progress], [500.0, 709.0, 709.0, 600.0])
        self.assertEqual([line["completed_count"] for line in progress], [1, 0, 61, 125])
        self.assertEqual([line["planned_count"] for line in progress], [1, 1, 125, 125])
        self.assertEqual(progress[2]["last_started_test"], shards[2][61])
        self.assertEqual(progress[2]["in_flight_seconds"], 300.0)
        self.assertIsNone(progress[3]["in_flight_seconds"])
        slowest = self.progress_lines(printed, "UNIVERSAL_WORKER_SLOWEST")
        self.assertEqual(slowest[2]["slowest"][0], [shards[2][60], 90.0])
        self.assertEqual(len(slowest[3]["slowest"]), 20)

    def test_child_failure_progress_marks_failed_worker_binding(self):
        failure = ("CHILD_FAILED:[None, 0, 1, None]", [None, 0, 1, None], 50.0, 0.0)
        with tempfile.TemporaryDirectory() as directory, mock.patch("builtins.print") as printed:
            runner.report_progress(Path(directory), self.plan, 709.0, 0.0, {1: 20.0, 2: 49.9}, failure)
        progress = self.progress_lines(printed, "UNIVERSAL_WORKER_PROGRESS")
        self.assertEqual([line["binding"] for line in progress], [False, False, True, False])
        self.assertEqual([line["progress_available"] for line in progress], [False] * 4)
        self.assertEqual([line["exit_code"] for line in progress], [None, 0, 1, None])

    def test_progress_report_never_raises_over_the_refusal(self):
        broken_plan = {"shards": []}
        with tempfile.TemporaryDirectory() as directory, mock.patch("builtins.print") as printed:
            runner.report_progress(Path(directory), broken_plan, 1.0, 0.0, {},
                                   ("WORKER_DEADLINE_EXCEEDED", [None] * 4, 1.0, 1.0))
        self.assertEqual(sum("DIAGNOSTIC_PROGRESS_UNAVAILABLE" in str(call)
                             for call in printed.call_args_list), 4)

    def test_progress_report_survives_raising_stdout(self):
        # Cross-family key finding on 754b37b: the fallback print was unguarded.
        for failure in (("WORKER_DEADLINE_EXCEEDED", [0, None, None, 0], 1709.0, 1300.0),
                        ("CHILD_FAILED:[0, 0, 1, None]", [0, 0, 1, None], 50.0, 0.0),
                        ("WORKER_DEADLINE_EXCEEDED", "malformed", None, None)):
            with self.subTest(failure=failure[0]), tempfile.TemporaryDirectory() as directory, \
                 contextlib.redirect_stdout(RaisingStream()):
                runner.report_progress(Path(directory), self.plan, 709.0, 1000.0, {}, failure)

    def test_journal_write_failure_of_any_kind_never_fails_a_test(self):
        class Probe(unittest.TestCase):
            def test_one(self):
                pass
        journal = mock.Mock()
        journal.write.side_effect = RuntimeError("journal broken")
        result = unittest.TextTestRunner(stream=io.StringIO(), resultclass=runner.functools.partial(
            runner.RecordingResult, progress=journal)).run(
            unittest.defaultTestLoader.loadTestsFromTestCase(Probe))
        self.assertTrue(result.wasSuccessful())
        self.assertEqual(len(result.successful), 1)
        self.assertIsNone(result.progress)

    def test_recording_result_journals_start_stop_and_duration(self):
        class Probe(unittest.TestCase):
            def test_one(self):
                pass
        journal = io.StringIO()
        result = unittest.TextTestRunner(
            stream=io.StringIO(), resultclass=runner.functools.partial(
                runner.RecordingResult, progress=journal)).run(
            unittest.defaultTestLoader.loadTestsFromTestCase(Probe))
        events = [json.loads(line) for line in journal.getvalue().splitlines()]
        self.assertEqual([next(iter(set(event) - {"wall", "seconds"})) for event in events],
                         ["start", "stop"])
        self.assertEqual(events[1]["seconds"], result.test_seconds[events[0]["start"]])
        self.assertTrue(result.wasSuccessful())
        journal.close()
        rerun = unittest.TextTestRunner(stream=io.StringIO(), resultclass=runner.functools.partial(
            runner.RecordingResult, progress=journal)).run(
            unittest.defaultTestLoader.loadTestsFromTestCase(Probe))
        self.assertTrue(rerun.wasSuccessful())
        self.assertIsNone(rerun.progress)

    def test_slowest_line_is_top_twenty_descending(self):
        line = runner.slowest_line(2, {f"t{index:02}": float(index) for index in range(30)})
        self.assertEqual(line["worker"], 2)
        self.assertEqual(len(line["slowest"]), 20)
        self.assertEqual(line["slowest"][0], ["t29", 29.0])
        self.assertEqual(line["slowest"][-1], ["t10", 10.0])

    def test_wait_workers_records_first_exit_time_only(self):
        first, second = mock.Mock(), mock.Mock()
        first.poll.return_value, second.poll.return_value = 0, None
        exited = {}
        with mock.patch.object(runner.time, "sleep"), \
             mock.patch.object(runner.time, "monotonic", side_effect=[5.0, 5.0, 7.0, 7.0]):
            with self.assertRaisesRegex(runner.Refused, "WORKER_DEADLINE_EXCEEDED"):
                runner.wait_workers([first, second], 6.0, exited)
        self.assertEqual(exited, {0: 5.0})

    def test_handshake_eof_refuses_before_project_discovery(self):
        with mock.patch.object(sys, "stdin", io.StringIO("")), mock.patch.object(runner, "discover") as discover:
            with self.assertRaisesRegex(runner.Refused, "HANDSHAKE"):
                runner.worker(Path("unused"), 0)
            discover.assert_not_called()


@unittest.skipUnless(os.name == "nt", "Windows Job Object lifecycle controls")
class WindowsContainmentTests(unittest.TestCase):
    def test_parent_interrupt_and_child_failure_always_clean_every_started_worker(self):
        ids = runner.source_census()
        for error in (KeyboardInterrupt(), runner.Refused("CHILD_FAILED"),
                      runner.Refused("WORKER_DEADLINE_EXCEEDED")):
            with self.subTest(error=type(error).__name__), tempfile.TemporaryDirectory() as directory:
                job = mock.Mock()
                processes = [mock.Mock() for _ in range(4)]
                with mock.patch.object(runner, "snapshot", return_value={"head": "a" * 40}), \
                     mock.patch.object(runner, "source_census", return_value=ids), \
                     mock.patch.object(runner, "WindowsJob", return_value=job), \
                     mock.patch.object(runner.subprocess, "Popen", side_effect=processes), \
                     mock.patch.object(runner, "wait_workers", side_effect=error), \
                     mock.patch("builtins.print"):
                    with self.assertRaises(type(error)):
                        runner.run(Path(directory) / "new-run")
                job.cleanup.assert_called_once_with(processes)
                self.assertEqual(job.attach.call_count, 4)

    def test_assignment_failure_kills_handshake_child_without_starting_tests(self):
        ids = runner.source_census()
        with tempfile.TemporaryDirectory() as directory:
            job, process = mock.Mock(), mock.Mock()
            job.attach.side_effect = OSError("assignment refused")
            with mock.patch.object(runner, "snapshot", return_value={"head": "a" * 40}), \
                 mock.patch.object(runner, "source_census", return_value=ids), \
                 mock.patch.object(runner, "WindowsJob", return_value=job), \
                 mock.patch.object(runner.subprocess, "Popen", return_value=process), \
                 mock.patch("builtins.print"):
                with self.assertRaisesRegex(OSError, "assignment refused"):
                    runner.run(Path(directory) / "new-run")
            process.kill.assert_called_once()
            process.wait.assert_called_once_with(timeout=10)
            process.stdin.write.assert_not_called()
            process.stdin.close.assert_called_once()
            job.cleanup.assert_called_once_with([process])

    def test_failed_assignment_and_failed_initial_kill_retain_child_ownership(self):
        with tempfile.TemporaryDirectory() as directory:
            job, process = mock.Mock(), mock.Mock()
            job.attach.side_effect = OSError("assignment refused")
            process.kill.side_effect = OSError("first kill failed")
            with mock.patch.object(runner, "snapshot", return_value={"head": "a" * 40}), \
                 mock.patch.object(runner, "WindowsJob", return_value=job), \
                 mock.patch.object(runner.subprocess, "Popen", return_value=process), \
                 mock.patch("builtins.print"):
                with self.assertRaisesRegex(OSError, "first kill failed"):
                    runner.run(Path(directory) / "new-run")
            job.cleanup.assert_called_once_with([process])
            process.stdin.write.assert_not_called()

    def test_unreadable_log_does_not_mask_primary_child_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            original_read = Path.read_text
            def read(path, *args, **kwargs):
                if path.suffix == ".log":
                    raise OSError("diagnostic unavailable")
                return original_read(path, *args, **kwargs)
            with mock.patch.object(runner, "snapshot", return_value={"head": "a" * 40}), \
                 mock.patch.object(runner, "WindowsJob"), \
                 mock.patch.object(runner.subprocess, "Popen"), \
                 mock.patch.object(runner, "wait_workers", side_effect=runner.Refused("CHILD_FAILED")), \
                 mock.patch.object(Path, "read_text", read), mock.patch("builtins.print") as output:
                with self.assertRaisesRegex(runner.Refused, "CHILD_FAILED"):
                    runner.run(Path(directory) / "new-run")
                self.assertEqual(sum("DIAGNOSTIC_LOG_UNAVAILABLE" in str(call) for call in output.call_args_list), 4)

    def test_simulated_deadline_emits_worker_progress_before_refusal_and_fails_closed(self):
        ids = runner.source_census()
        shards = runner.partition(ids)
        for reason, codes, binding in (("WORKER_DEADLINE_EXCEEDED", [0, None, None, 0], [1, 2]),
                                       ("CHILD_FAILED:[0, 0, 1, None]", [0, 0, 1, None], [2])):
            with self.subTest(reason=reason), tempfile.TemporaryDirectory() as directory:
                output = Path(directory) / "new-run"
                processes = [mock.Mock() for _ in range(4)]
                for process, code in zip(processes, codes):
                    process.poll.return_value = code
                def deadline(processes, deadline, exited):
                    (output / "worker-2.progress.jsonl").write_text(
                        json.dumps({"start": shards[2][0], "wall": time.time()}) + "\n", encoding="utf-8")
                    raise runner.Refused(reason)
                stream = io.StringIO()
                with mock.patch.object(runner, "snapshot", return_value={"head": "a" * 40}), \
                     mock.patch.object(runner, "source_census", return_value=ids), \
                     mock.patch.object(runner, "WindowsJob"), \
                     mock.patch.object(runner.subprocess, "Popen", side_effect=processes), \
                     mock.patch.object(runner, "wait_workers", side_effect=deadline), \
                     mock.patch.object(sys, "argv", ["runner", "--output-dir", str(output)]), \
                     contextlib.redirect_stdout(stream), contextlib.redirect_stderr(stream):
                    self.assertEqual(runner.main(), 1)
                lines = stream.getvalue().splitlines()
                refusal = [index for index, line in enumerate(lines)
                           if line == "UNIVERSAL_RUN_REFUSED: " + reason]
                self.assertEqual(len(refusal), 1)
                progress = [(index, json.loads(line)) for index, line in enumerate(lines)
                            if line.startswith('{"') and '"UNIVERSAL_WORKER_PROGRESS"' in line]
                self.assertEqual([line["worker"] for _, line in progress], [0, 1, 2, 3])
                self.assertTrue(all(index < refusal[0] for index, _ in progress))
                self.assertEqual([line["worker"] for _, line in progress if line["binding"]], binding)
                self.assertEqual(progress[2][1]["last_started_test"], shards[2][0])
                self.assertFalse((output / "complete.json").exists())

    def run_refused(self, reason, codes, poll_error=None):
        """Drive main() to a simulated refusal with stdout failing from that moment on."""
        ids = runner.source_census()
        stdout, stderr = RaisingStream(), io.StringIO()
        stdout.armed = False
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "new-run"
            processes = [mock.Mock() for _ in range(4)]
            for process, code in zip(processes, codes):
                process.poll.return_value = code
                if poll_error is not None:
                    process.poll.side_effect = poll_error
            def refuse(processes, deadline, exited):
                (output / "worker-2.progress.jsonl").write_text(
                    json.dumps({"start": "in.flight", "wall": time.time()}) + "\n", encoding="utf-8")
                stdout.armed = poll_error is None
                raise runner.Refused(reason)
            with mock.patch.object(runner, "snapshot", return_value={"head": "a" * 40}), \
                 mock.patch.object(runner, "source_census", return_value=ids), \
                 mock.patch.object(runner, "WindowsJob"), \
                 mock.patch.object(runner.subprocess, "Popen", side_effect=processes), \
                 mock.patch.object(runner, "wait_workers", side_effect=refuse), \
                 mock.patch.object(sys, "argv", ["runner", "--output-dir", str(output)]), \
                 contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                code = runner.main()
        return code, stderr.getvalue().splitlines(), stdout.getvalue()

    def test_raising_stdout_during_refusal_keeps_refusal_line_and_exit_code(self):
        for reason, codes in (("WORKER_DEADLINE_EXCEEDED", [0, None, None, 0]),
                              ("CHILD_FAILED:[0, 0, 1, None]", [0, 0, 1, None])):
            with self.subTest(reason=reason):
                code, stderr, _ = self.run_refused(reason, codes)
                self.assertEqual(code, 1)
                self.assertEqual(stderr, ["UNIVERSAL_RUN_REFUSED: " + reason])

    def test_poll_failure_while_capturing_progress_keeps_refusal(self):
        for reason in ("WORKER_DEADLINE_EXCEEDED", "CHILD_FAILED:[0, 0, 1, None]"):
            with self.subTest(reason=reason):
                code, stderr, stdout = self.run_refused(reason, [None] * 4, OSError("poll failed"))
                self.assertEqual(code, 1)
                self.assertEqual(stderr, ["UNIVERSAL_RUN_REFUSED: " + reason])
                progress = [json.loads(line) for line in stdout.splitlines()
                            if '"UNIVERSAL_WORKER_PROGRESS"' in line]
                self.assertEqual([line["exit_code"] for line in progress], [None] * 4)
                self.assertEqual(progress[2]["last_started_test"], "in.flight")

    def drive_main(self, ctx, on_wait):
        """Run main() with mocked workers; `on_wait` plays wait_workers. Returns
        (exit code, every refusal sink: stderr + sys.__stderr__ + raw fd writes)."""
        ids = runner.source_census()
        stdout, stderr, dunder, raw = RaisingStream(), RaisingStream(), RaisingStream(), []
        stdout.armed = stderr.armed = dunder.armed = False
        real_write = os.write
        def write(descriptor, data):
            if descriptor in (1, 2):
                raw.append(bytes(data))
                return len(data)
            return real_write(descriptor, data)
        def wait(processes, deadline, exited):
            try:
                return on_wait(ctx.output)
            finally:
                ctx.armed = True
                stdout.armed = ctx.stdout_fails
                stderr.armed = ctx.stderr_fails >= 1
                dunder.armed = ctx.stderr_fails >= 2
        processes = [mock.Mock() for _ in range(4)]
        for process, code in zip(processes, ctx.codes):
            process.poll.return_value = code
            process.poll.side_effect = ctx.poll_error
        job = mock.Mock()
        job.active.return_value = 0
        job.cleanup.side_effect = ctx.job_error
        with tempfile.TemporaryDirectory() as directory, contextlib.ExitStack() as stack:
            ctx.output = Path(directory) / "new-run"
            for patcher in [mock.patch.object(runner, "snapshot", return_value={"head": "a" * 40}),
                            mock.patch.object(runner, "source_census", return_value=ids),
                            mock.patch.object(runner, "WindowsJob", return_value=job),
                            mock.patch.object(runner.subprocess, "Popen", side_effect=processes),
                            mock.patch.object(runner, "wait_workers", side_effect=wait),
                            mock.patch.object(runner.os, "write", write),
                            mock.patch.object(sys, "__stderr__", dunder),
                            mock.patch.object(sys, "argv", ["runner", "--output-dir", str(ctx.output)]),
                            *ctx.patchers]:
                stack.enter_context(patcher)
            stack.enter_context(contextlib.redirect_stdout(stdout))
            stack.enter_context(contextlib.redirect_stderr(stderr))
            try:
                code = runner.main()
            except SystemExit as error:
                code = ("SystemExit", error.code)
            except BaseException as error:
                code = error
        sink = stderr.getvalue() + dunder.getvalue() + b"".join(raw).decode("utf-8", "replace")
        return code, sink.splitlines()

    def test_refusal_choke_point_holds_when_any_refusal_path_site_raises(self):
        # Sites enumerated from run()/main(): every call that executes after
        # wait_workers decides a refusal, in execution order.
        real_read, real_open = Path.read_text, Path.open
        def armed(ctx, real, error):
            def call(*args, **kwargs):
                if ctx.armed:
                    raise error
                return real(*args, **kwargs)
            return call
        def module(name, error):
            return lambda ctx: [mock.patch.object(runner, name, armed(ctx, getattr(runner, name), error))]
        def read(suffix, error):
            def build(ctx):
                def read_text(path, *args, **kwargs):
                    if ctx.armed and path.suffix == suffix:
                        raise error
                    return real_read(path, *args, **kwargs)
                return [mock.patch.object(Path, "read_text", read_text)]
            return build
        def log_close(error):
            def build(ctx):
                def open_(path, mode="r", *args, **kwargs):
                    if mode == "xb":  # worker log handles; Popen is mocked
                        log = mock.Mock()
                        log.close.side_effect = error
                        return log
                    return real_open(path, mode, *args, **kwargs)
                return [mock.patch.object(Path, "open", open_)]
            return build
        def field(name, value):
            return lambda ctx: setattr(ctx, name, value) or []
        rows = [
            ("capture_failure", module("capture_failure", RuntimeError("capture failed"))),
            ("process.poll", field("poll_error", OSError("poll failed"))),
            ("job.cleanup", field("job_error", runner.Refused("INCOMPLETE_PROCESS_CLEANUP:[]"))),
            ("log.close", log_close(OSError("log close failed"))),
            ("log.close SystemExit(0)", log_close(SystemExit(0))),
            ("emit", module("emit", RuntimeError("emit failed"))),
            ("worker log read_text", read(".log", RuntimeError("log read failed"))),
            ("report_progress", module("report_progress", RuntimeError("report failed"))),
            ("timing-file read_text", read(".jsonl", RuntimeError("timing read failed"))),
            ("read_progress", module("read_progress", RuntimeError("progress failed"))),
            ("json.dumps", lambda ctx: [mock.patch.object(
                runner.json, "dumps", armed(ctx, json.dumps, RuntimeError("dumps failed")))]),
            ("slowest_line", module("slowest_line", RuntimeError("slowest failed"))),
            ("stdout print", field("stdout_fails", True)),
            ("stderr refusal print", field("stderr_fails", 1)),
            ("stderr and sys.__stderr__", field("stderr_fails", 2)),
        ]
        for reason, codes in (("WORKER_DEADLINE_EXCEEDED", [0, None, None, 0]),
                              ("CHILD_FAILED:[0, 0, 1, None]", [0, 0, 1, None])):
            for site, build in rows:
                with self.subTest(reason=reason, site=site):
                    ctx = types.SimpleNamespace(armed=False, codes=codes, poll_error=None, job_error=None,
                                                stdout_fails=False, stderr_fails=0, patchers=[])
                    ctx.patchers = build(ctx)
                    def on_wait(output):
                        (output / "worker-2.progress.jsonl").write_text(
                            json.dumps({"start": "in.flight", "wall": time.time()}) + "\n", encoding="utf-8")
                        raise runner.Refused(reason)
                    code, sink = self.drive_main(ctx, on_wait)
                    self.assertEqual(code, 1)
                    self.assertIn("UNIVERSAL_RUN_REFUSED: " + reason, sink)

    def test_diagnostic_failure_cannot_flip_success_or_genuine_failure(self):
        for broken, want in ((False, 0), (True, 1)):
            with self.subTest(genuine_failure=broken):
                ctx = types.SimpleNamespace(armed=False, codes=[0] * 4, poll_error=None, job_error=None,
                                            stdout_fails=True, stderr_fails=0, patchers=[])
                def on_wait(output):
                    plan = runner.read_json(output / "plan.json")
                    for index, assigned in enumerate(plan["shards"]):
                        runner.atomic_json(output / f"worker-{index}.json", {
                            "plan_sha256": runner.digest(plan), "worker": index, "assigned": assigned,
                            "started": assigned, "stopped": assigned, "successful": assigned,
                            "test_seconds": {item: 0.1 for item in assigned}, "seconds": 1.0,
                            "tests_run": len(assigned), "exit_status": int(broken and index == 2),
                            "failures": int(broken and index == 2), "errors": 0, "skips": 0,
                            "expected_failures": 0, "unexpected_successes": 0})
                code, sink = self.drive_main(ctx, on_wait)
                self.assertEqual(code, want)
                if broken:
                    self.assertIn("UNIVERSAL_RUN_REFUSED: RECEIPT_OUTCOME_MISMATCH:exit_status", sink)
                else:
                    self.assertEqual(sink, [])

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
