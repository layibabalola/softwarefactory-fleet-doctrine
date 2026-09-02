import contextlib
import hashlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest import mock


MODULE_PATH = Path(__file__).parents[1] / "reference" / "classify_launcher_candidates.py"
SPEC = importlib.util.spec_from_file_location("classify_launcher_candidates", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class LauncherCandidateClassifierTests(unittest.TestCase):
    def test_production_scale_bounds_are_finite_and_explicit(self):
        self.assertEqual(MODULE.MAX_LISTING_BYTES, 32 * 1024 * 1024)
        self.assertEqual(MODULE.MAX_CANDIDATES, 8192)
        self.assertLess(MODULE.MAX_LISTING_BYTES, MODULE.MAX_AGGREGATE_SOURCE_BYTES)
        self.assertLess(MODULE.MAX_CANDIDATES, MODULE.MAX_VISITED_PATHS)

    def _classify(self, files: dict[str, str]) -> dict[str, object]:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name, text in files.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
            return MODULE.classify_tree(root)

    def _frozen(self, report: dict[str, object]) -> dict[str, object]:
        report = dict(report)
        report.update(
            sourceMode="GIT_COMMIT",
            subjectCommit="1" * 40,
            subjectTree="2" * 40,
        )
        return report

    def test_detects_variable_bound_deadman_launch(self):
        result = self._classify(
            {"deadman.ps1": "$cfg = @{ Runner='claude.exe' }\nStart-Process -FilePath $cfg.Runner\n"}
        )
        self.assertEqual(result["classificationCounts"], {"INDIRECT_VARIABLE": 1})
        self.assertEqual(result["reviewPriorityCounts"], {"P0_DIRECT": 1})
        self.assertEqual(result["flowUnresolvedCount"], 1)
        self.assertEqual(result["reviewPendingCount"], 1)
        self.assertEqual(result["unresolvedCount"], 1)
        candidate = result["candidates"][0]
        self.assertEqual(candidate["evidence"]["providerLines"], {"CLAUDE": [1]})
        self.assertEqual(candidate["evidence"]["primitiveLines"], {"POWERSHELL_START_PROCESS": [2]})

    def test_separates_direct_registration_and_reference(self):
        result = self._classify(
            {
                "direct.sh": "exec kimi --print\n",
                "register.ps1": "$runner='codex.exe'\nRegister-ScheduledTask -TaskName sample\n",
                "notes.py": "PROVIDER = 'anthropic'\n",
            }
        )
        self.assertEqual(
            result["classificationCounts"],
            {"DIRECT_STATIC": 1, "REFERENCE_ONLY": 1, "REGISTRATION_SURFACE": 1},
        )
        self.assertEqual(result["flowUnresolvedCount"], 1)
        self.assertEqual(result["reviewPendingCount"], 3)
        self.assertEqual(result["unresolvedCount"], 3)

    def test_detects_node_launchers_in_mjs_and_cjs(self):
        result = self._classify(
            {
                "launch.mjs": 'import { spawn } from "node:child_process";\nconst provider = "claude";\nspawn(provider, ["-p"]);\n',
                "bridge.cjs": 'const { execFile } = require("child_process");\nexecFile("codex", ["exec", "-"]);\n',
            }
        )
        self.assertEqual(result["candidateCount"], 2)
        self.assertEqual(result["classificationCounts"], {"DIRECT_STATIC": 1, "UNRESOLVED_FLOW": 1})
        for candidate in result["candidates"]:
            self.assertIn("NODE_CHILD_PROCESS", candidate["launchPrimitives"])
        self.assertEqual(result["reviewPendingCount"], 2)

    def test_output_is_deterministic_and_excludes_tmp(self):
        files = {"b.py": "# claude\n", "a.py": "# kimi\n", "tmp/ignored.py": "exec grok --run\n"}
        first = self._classify(files)
        second = self._classify(files)
        self.assertEqual(
            [(row["path"], row["sha256"]) for row in first["candidates"]],
            [(row["path"], row["sha256"]) for row in second["candidates"]],
        )
        self.assertEqual([row["path"] for row in first["candidates"]], ["a.py", "b.py"])
        self.assertEqual(first["root"], ".")

    def test_irrelevant_tree_is_bounded_before_source_filter(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            (root/"a.txt").write_text("irrelevant",encoding="utf-8")
            (root/"b.txt").write_text("irrelevant",encoding="utf-8")
            with mock.patch.object(MODULE,"MAX_VISITED_PATHS",1), self.assertRaisesRegex(ValueError,"VISITED_PATH_LIMIT"):
                MODULE.classify_tree(root)

    def test_working_tree_refusal_does_not_echo_private_details(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "private.ps1"
            source.write_text("# claude\n", encoding="utf-8")
            with mock.patch.object(MODULE, "_classify", side_effect=OSError("C:/secret/token")):
                result = MODULE.classify_tree(root)
        self.assertEqual(result["root"], ".")
        self.assertEqual(result["refused"], [{"path": "private.ps1", "reason": "INPUT_REFUSED"}])
        self.assertNotIn("secret", json.dumps(result))

    def test_oversize_source_is_refused_and_counted_unresolved(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "large.ps1").write_bytes(b"# claude\n" + b"x" * MODULE.MAX_FILE_BYTES)
            result = MODULE.classify_tree(root)
        self.assertEqual(result["candidateCount"], 0)
        self.assertEqual(result["flowUnresolvedCount"], 1)
        self.assertEqual(result["reviewPendingCount"], 1)
        self.assertEqual(result["unresolvedCount"], 1)
        self.assertEqual(result["refused"], [{"path": "large.ps1", "reason": "SOURCE_TOO_LARGE"}])

    def test_even_all_direct_candidates_remain_zero_authority(self):
        result = self._classify({"launch.sh": "exec claude --print\n"})
        self.assertEqual(result["classificationCounts"], {"DIRECT_STATIC": 1})
        self.assertEqual(result["flowUnresolvedCount"], 0)
        self.assertEqual(result["reviewPendingCount"], 1)
        self.assertEqual(result["unresolvedCount"], 1)
        self.assertEqual(result["status"], "INCOMPLETE_ZERO_AUTHORITY")

    def test_review_requires_exact_population_and_hashes(self):
        report = self._frozen(self._classify({"launch.sh": "exec claude --print\n"}))
        candidate = report["candidates"][0]
        with self.assertRaisesRegex(ValueError, "REVIEW_MISSING_PATH"):
            MODULE.reconcile_review(
                report,
                {
                    "schema": MODULE.REVIEW_SCHEMA,
                    "subjectCommit": report["subjectCommit"],
                    "subjectTree": report["subjectTree"],
                    "entries": [],
                },
            )
        with self.assertRaisesRegex(ValueError, "REVIEW_HASH_MISMATCH"):
            MODULE.reconcile_review(
                report,
                {
                    "schema": MODULE.REVIEW_SCHEMA,
                    "subjectCommit": report["subjectCommit"],
                    "subjectTree": report["subjectTree"],
                    "entries": [{"path": candidate["path"], "sha256": "sha256:" + "0" * 64, "disposition": "LAUNCHER"}],
                },
            )

    def test_review_requires_exact_frozen_subject(self):
        working_report = self._classify({"launch.sh": "exec claude --print\n"})
        with self.assertRaisesRegex(ValueError, "REVIEW_REQUIRES_GIT_SUBJECT"):
            MODULE.review_template(working_report)
        report = self._frozen(working_report)
        review = MODULE.review_template(report)
        review["subjectTree"] = "3" * 40
        with self.assertRaisesRegex(ValueError, "REVIEW_SUBJECT_MISMATCH"):
            MODULE.reconcile_review(report, review)

    def test_review_never_grants_runtime_authority(self):
        report = self._frozen(self._classify({"launch.sh": "exec claude --print\n", "note.py": "# anthropic\n"}))
        entries = [
            {"path": row["path"], "sha256": row["sha256"], "disposition": "LAUNCHER" if row["path"] == "launch.sh" else "NON_LAUNCHER"}
            for row in report["candidates"]
        ]
        result = MODULE.reconcile_review(
            report,
            {
                "schema": MODULE.REVIEW_SCHEMA,
                "subjectCommit": report["subjectCommit"],
                "subjectTree": report["subjectTree"],
                "entries": entries,
            },
        )
        self.assertEqual(result["pendingCount"], 0)
        self.assertEqual(result["status"], "REVIEWED_CLASSIFICATION_ZERO_AUTHORITY")

    def test_unknown_review_remains_incomplete(self):
        report = self._frozen(self._classify({"launch.sh": "exec claude --print\n"}))
        row = report["candidates"][0]
        result = MODULE.reconcile_review(
            report,
            {
                "schema": MODULE.REVIEW_SCHEMA,
                "subjectCommit": report["subjectCommit"],
                "subjectTree": report["subjectTree"],
                "entries": [{"path": row["path"], "sha256": row["sha256"], "disposition": "UNKNOWN"}],
            },
        )
        self.assertEqual(result["pendingCount"], 1)
        self.assertEqual(result["status"], "REVIEW_INCOMPLETE_ZERO_AUTHORITY")

    def test_review_refuses_array_or_object_disposition_without_traceback(self):
        report = self._frozen(self._classify({"launch.sh": "exec claude --print\n"}))
        row = report["candidates"][0]
        for disposition in (["LAUNCHER"], {"value": "LAUNCHER"}):
            review = {
                "schema": MODULE.REVIEW_SCHEMA,
                "subjectCommit": report["subjectCommit"],
                "subjectTree": report["subjectTree"],
                "entries": [{"path": row["path"], "sha256": row["sha256"], "disposition": disposition}],
            }
            with self.subTest(disposition=disposition):
                with self.assertRaisesRegex(ValueError, "^REVIEW_DISPOSITION$"):
                    MODULE.reconcile_review(report, review)
                with tempfile.TemporaryDirectory() as temporary:
                    manifest = Path(temporary) / "review.json"
                    manifest.write_text(json.dumps(review), encoding="utf-8")
                    stderr = io.StringIO()
                    with mock.patch.object(
                        sys,
                        "argv",
                        ["classifier", ".", "--review-manifest", str(manifest)],
                    ), mock.patch.object(MODULE, "classify_tree", return_value=report), contextlib.redirect_stderr(stderr):
                        self.assertEqual(MODULE.main(), 2)
                    self.assertEqual(stderr.getvalue(), "ERROR classify_launcher_candidates: INPUT_REFUSED\n")

    def test_review_template_binds_every_candidate_as_unknown(self):
        report = self._frozen(self._classify({"b.py": "# claude\n", "a.sh": "exec kimi --print\n"}))
        template = MODULE.review_template(report)
        self.assertEqual(template["schema"], MODULE.REVIEW_SCHEMA)
        self.assertEqual(template["subjectCommit"], report["subjectCommit"])
        self.assertEqual(template["subjectTree"], report["subjectTree"])
        self.assertEqual([entry["path"] for entry in template["entries"]], ["a.sh", "b.py"])
        self.assertTrue(all(entry["disposition"] == "UNKNOWN" for entry in template["entries"]))
        result = MODULE.reconcile_review(report, template)
        self.assertEqual(result["pendingCount"], 2)

    def test_git_subject_scan_ignores_working_tree_drift(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            environment = os.environ.copy()
            environment["GIT_OPTIONAL_LOCKS"] = "0"
            subprocess.run(["git", "init", "-q", str(root)], check=True, env=environment)
            subprocess.run(["git", "-C", str(root), "config", "user.email", "test@example.invalid"], check=True, env=environment)
            subprocess.run(["git", "-C", str(root), "config", "user.name", "test"], check=True, env=environment)
            source = root / "launch.ps1"
            source.write_text("$runner='claude.exe'\nStart-Process -FilePath $runner\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "launch.ps1"], check=True, env=environment)
            subprocess.run(["git", "-C", str(root), "commit", "-q", "-m", "subject"], check=True, env=environment)
            source.write_text("# working tree no longer mentions a provider\n", encoding="utf-8")
            report = MODULE.classify_git_tree(root, "HEAD")
        self.assertEqual(report["sourceMode"], "GIT_COMMIT")
        self.assertRegex(report["subjectCommit"], r"^[0-9a-f]{40}$")
        self.assertRegex(report["subjectTree"], r"^[0-9a-f]{40}$")
        self.assertEqual(report["classificationCounts"], {"INDIRECT_VARIABLE": 1})
        self.assertEqual(report["root"], ".")

    def test_review_manifest_is_bounded_before_decode(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "review.json"
            with path.open("wb") as stream:
                stream.truncate(MODULE.MAX_REVIEW_BYTES + 1)
            with self.assertRaisesRegex(ValueError, "REVIEW_INPUT_LIMIT"):
                MODULE._strict_json(path)

    def test_review_manifest_shape_is_bounded_before_parser(self):
        with tempfile.TemporaryDirectory() as temporary:
            path=Path(temporary)/"review.json"
            path.write_bytes(b"["*(MODULE.MAX_REVIEW_DEPTH+1)+b"0"+b"]"*(MODULE.MAX_REVIEW_DEPTH+1))
            with mock.patch.object(MODULE.json,"loads",side_effect=AssertionError("parser must not run")):
                with self.assertRaisesRegex(ValueError,"REVIEW_SHAPE_LIMIT"):
                    MODULE._strict_json(path)

    def test_git_pipe_timeout_terminates_without_echo(self):
        process=mock.Mock()
        process.stdout=io.BytesIO(b"")
        process.stderr=io.BytesIO(b"")
        process.wait.side_effect=[subprocess.TimeoutExpired("git",30),-9]
        with mock.patch.object(MODULE.subprocess,"Popen",return_value=process):
            with self.assertRaisesRegex(ValueError,"GIT_TIMEOUT"):
                MODULE._git_bounded(Path("."),128,"rev-parse","HEAD")
        process.kill.assert_called_once()

    def test_git_stderr_is_bounded_and_refused(self):
        process=mock.Mock()
        process.stdout=io.BytesIO(b"ok")
        process.stderr=io.BytesIO(b"x"*(MODULE.MAX_GIT_STDERR_BYTES+1))
        process.wait.return_value=0
        with mock.patch.object(MODULE.subprocess,"Popen",return_value=process):
            with self.assertRaisesRegex(ValueError,"GIT_OUTPUT_LIMIT"):
                MODULE._git_bounded(Path("."),128,"rev-parse","HEAD")

    def test_git_pipe_uses_nonfilling_read1(self):
        class Read1Only(io.BytesIO):
            def read(self, *_args, **_kwargs):
                raise AssertionError("bounded pipe reader must use read1")

        process=mock.Mock()
        process.stdout=Read1Only(b"ok")
        process.stderr=Read1Only(b"")
        process.wait.return_value=0
        with mock.patch.object(MODULE.subprocess,"Popen",return_value=process):
            self.assertEqual(MODULE._git_bounded(Path("."),128,"rev-parse","HEAD"),b"ok")

    def test_git_blob_batch_parses_exact_records(self):
        sources = [("a.ps1", "a" * 40, 3), ("b.mjs", "b" * 40, 2)]
        output = (b"a" * 40 + b" blob 3\none\n" + b"b" * 40 + b" blob 2\nxy\n")
        with mock.patch.object(MODULE, "_git_bounded", return_value=output) as bounded:
            self.assertEqual(MODULE._git_blob_batch(Path("."), sources), [b"one", b"xy"])
        self.assertEqual(bounded.call_args.kwargs["stdin_bytes"], (b"a" * 40 + b"\n" + b"b" * 40 + b"\n"))

    def test_git_blob_batch_refuses_identity_and_trailing_output(self):
        sources = [("a.ps1", "a" * 40, 3)]
        wrong = b"b" * 40 + b" blob 3\none\n"
        with mock.patch.object(MODULE, "_git_bounded", return_value=wrong):
            with self.assertRaisesRegex(ValueError, "GIT_BATCH_IDENTITY"):
                MODULE._git_blob_batch(Path("."), sources)
        trailing = b"a" * 40 + b" blob 3\none\nextra"
        with mock.patch.object(MODULE, "_git_bounded", return_value=trailing):
            with self.assertRaisesRegex(ValueError, "GIT_BATCH_TRAILING"):
                MODULE._git_blob_batch(Path("."), sources)

    def test_git_pipe_timeout_closes_reader_without_thread_exception(self):
        class BlockingReader:
            def __init__(self):
                self.closed=False
                self.released=threading.Event()
            def read1(self, _size):
                self.released.wait(1)
                if self.closed: raise ValueError("I/O operation on closed file")
                return b""
            def read(self, _size):
                raise AssertionError("bounded pipe reader must use read1")
            def close(self):
                self.closed=True
                self.released.set()

        process=mock.Mock()
        process.stdout=BlockingReader()
        process.stderr=io.BytesIO(b"")
        process.wait.return_value=0
        with mock.patch.object(MODULE.subprocess,"Popen",return_value=process), \
             mock.patch.object(MODULE,"GIT_READER_DRAIN_TIMEOUT_SECONDS",0.01):
            with self.assertRaisesRegex(ValueError,"GIT_PIPE_TIMEOUT"):
                MODULE._git_bounded(Path("."),128,"rev-parse","HEAD")
        process.stdout.released.wait(1)

    def test_cli_error_is_stable_and_does_not_echo_git_or_path_details(self):
        stderr = io.StringIO()
        with mock.patch.object(sys, "argv", ["classifier", "C:/private"]), \
             mock.patch.object(MODULE, "classify_tree", side_effect=ValueError("stderr C:/secret token")), \
             contextlib.redirect_stderr(stderr):
            self.assertEqual(MODULE.main(), 2)
        self.assertEqual(stderr.getvalue(), "ERROR classify_launcher_candidates: INPUT_REFUSED\n")

    def test_published_conjugal_manifest_is_complete_and_exact(self):
        path = MODULE_PATH.parents[1] / "findings" / "conjugal-launcher-review-5bff7d44.json"
        data = path.read_bytes()
        canonical = data.rstrip(b"\r\n")
        self.assertEqual(len(canonical), 19069)
        self.assertEqual(
            hashlib.sha256(canonical).hexdigest(),
            "ea01fb26c539691e4ad6e1b432a0b9542c4e6552cb1cda92f9c25489e82ece35",
        )
        manifest = json.loads(canonical)
        self.assertEqual(manifest["subjectCommit"], "5bff7d4498b1b14c1b3488fef849d5b28a06bb89")
        self.assertEqual(manifest["subjectTree"], "d27dbe84af4076ea6e38a5152435f41d68a73cba")
        counts = {name: 0 for name in MODULE.REVIEW_DISPOSITIONS}
        for entry in manifest["entries"]:
            counts[entry["disposition"]] += 1
        self.assertEqual(counts, {"LAUNCHER": 23, "NON_LAUNCHER": 95, "UNKNOWN": 0})


if __name__ == "__main__":
    unittest.main()
