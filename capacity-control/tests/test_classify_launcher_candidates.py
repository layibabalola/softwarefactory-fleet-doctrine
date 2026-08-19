import contextlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


MODULE_PATH = Path(__file__).parents[1] / "reference" / "classify_launcher_candidates.py"
SPEC = importlib.util.spec_from_file_location("classify_launcher_candidates", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class LauncherCandidateClassifierTests(unittest.TestCase):
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

    def test_output_is_deterministic_and_excludes_tmp(self):
        files = {"b.py": "# claude\n", "a.py": "# kimi\n", "tmp/ignored.py": "exec grok --run\n"}
        first = self._classify(files)
        second = self._classify(files)
        self.assertEqual(
            [(row["path"], row["sha256"]) for row in first["candidates"]],
            [(row["path"], row["sha256"]) for row in second["candidates"]],
        )
        self.assertEqual([row["path"] for row in first["candidates"]], ["a.py", "b.py"])

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

    def test_review_manifest_is_bounded_before_decode(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "review.json"
            with path.open("wb") as stream:
                stream.truncate(MODULE.MAX_REVIEW_BYTES + 1)
            with self.assertRaisesRegex(ValueError, "REVIEW_INPUT_LIMIT"):
                MODULE._strict_json(path)

    def test_cli_error_is_stable_and_does_not_echo_git_or_path_details(self):
        stderr = io.StringIO()
        with mock.patch.object(sys, "argv", ["classifier", "C:/private"]), \
             mock.patch.object(MODULE, "classify_tree", side_effect=ValueError("stderr C:/secret token")), \
             contextlib.redirect_stderr(stderr):
            self.assertEqual(MODULE.main(), 2)
        self.assertEqual(stderr.getvalue(), "ERROR classify_launcher_candidates: INPUT_REFUSED\n")


if __name__ == "__main__":
    unittest.main()
