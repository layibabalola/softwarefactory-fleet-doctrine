"""Hostile controls for the five post-R26 manifest/spec binding repairs."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import types
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import check_phase2_disposition_batch as phase2  # noqa: E402
import check_phase3_disposition_batch as phase3  # noqa: E402
import check_phase5_stale_reconciliation as phase5  # noqa: E402

HISTORICAL_TREEISH = "e7311e3038bbfeebe15cc10004f40b3795811659"


REPAIRED_SPEC_PATHS = (
    "specs/adversarialllm.md",
    "specs/cloudvore.md",
    "specs/dng-auto-processor.md",
    "specs/mlv-app.md",
    "specs/salesforce-tools.md",
)


def git_bytes(*args: str) -> bytes:
    run = subprocess.run(
        ["git", *args], cwd=ROOT, check=False, capture_output=True
    )
    if run.returncode != 0:
        raise AssertionError(run.stderr.decode("utf-8", errors="replace"))
    return run.stdout


checker = types.ModuleType("phase11_check_universal_manifest")
checker.__file__ = str(ROOT / "tools" / "check_universal_manifest.py")
exec(
    compile(
        git_bytes("show", f"{HISTORICAL_TREEISH}:tools/check_universal_manifest.py"),
        checker.__file__,
        "exec",
    ),
    checker.__dict__,
)


class UniversalManifestSpecBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.raw_manifest = git_bytes("show", f"{HISTORICAL_TREEISH}:{checker.MANIFEST}")
        cls.manifest = json.loads(cls.raw_manifest.decode("utf-8"))
        cls.subjects = {
            subject["path"]: subject for subject in cls.manifest["subjectFiles"]
        }
        cls.blobs = {
            path: git_bytes("show", f"{HISTORICAL_TREEISH}:{path}")
            for path in cls.subjects
        }
        cls.oids = {
            path: git_bytes("rev-parse", f"{HISTORICAL_TREEISH}:{path}").decode("ascii").strip()
            for path in cls.subjects
        }

    def test_repaired_specs_match_all_three_manifest_coordinates(self) -> None:
        self.assertEqual(set(REPAIRED_SPEC_PATHS) - self.subjects.keys(), set())
        for path in REPAIRED_SPEC_PATHS:
            with self.subTest(path=path):
                blob = self.blobs[path]
                subject = self.subjects[path]
                self.assertEqual(subject["bytes"], len(blob))
                self.assertEqual(
                    subject["sha256"], "sha256:" + hashlib.sha256(blob).hexdigest()
                )
                self.assertEqual(subject["gitBlobOid"], self.oids[path])

    def test_each_repaired_spec_tuple_tamper_fails_closed(self) -> None:
        original_git = checker._git
        original_oid = checker._oid

        def run_tampered(path: str, field: str) -> str:
            manifest = copy.deepcopy(self.manifest)
            subject = next(
                entry for entry in manifest["subjectFiles"] if entry["path"] == path
            )
            if field == "bytes":
                subject[field] += 1
            elif field == "sha256":
                subject[field] = "sha256:" + "0" * 64
            else:
                subject[field] = "0" * len(subject[field])
            tampered = json.dumps(manifest, separators=(",", ":")).encode("utf-8") + b"\n"

            def fake_git(spec: str, *, text: bool = False) -> bytes | str:
                if spec == f"{HISTORICAL_TREEISH}:{checker.MANIFEST}":
                    return tampered.decode("utf-8") if text else tampered
                prefix = f"{HISTORICAL_TREEISH}:"
                if spec.startswith(prefix) and spec[len(prefix):] in self.blobs:
                    blob = self.blobs[spec[len(prefix):]]
                    return blob.decode("utf-8") if text else blob
                return original_git(spec, text=text)

            def fake_oid(treeish: str, subject_path: str) -> str:
                if treeish == HISTORICAL_TREEISH and subject_path in self.oids:
                    return self.oids[subject_path]
                return original_oid(treeish, subject_path)

            expected = (
                "MANIFEST_BLOB_OID_MISMATCH"
                if field == "gitBlobOid"
                else "MANIFEST_SUBJECT_MISMATCH"
            )
            with (
                mock.patch.object(checker, "_git", side_effect=fake_git),
                mock.patch.object(checker, "_oid", side_effect=fake_oid),
                mock.patch.object(checker, "verify_reconciliation"),
                self.assertRaisesRegex(checker.ManifestError, expected),
            ):
                checker.check(HISTORICAL_TREEISH)
            return expected

        for path in REPAIRED_SPEC_PATHS:
            for field in ("bytes", "sha256", "gitBlobOid"):
                with self.subTest(path=path, field=field):
                    run_tampered(path, field)

    def test_repair_grants_no_authority_and_changes_no_disposition(self) -> None:
        self.assertEqual(self.manifest["status"], "CANDIDATE_ZERO_AUTHORITY")
        self.assertEqual(self.manifest["authority"]["automaticGateState"], "CLOSED")
        for field in (
            "activationRequiresSeparateAdjudication",
            "containmentOrCanaryCredit",
            "processSpawnResumeKill",
            "providerExecution",
        ):
            expected = field == "activationRequiresSeparateAdjudication"
            self.assertIs(self.manifest["authority"][field], expected)

    def test_prior_phase_scopes_allow_only_the_mechanical_forward_paths(self) -> None:
        repair_paths = {
            checker.MANIFEST,
            "tests/test_universal_manifest_spec_bindings.py",
        }
        allowed_sets = (
            (2, phase2.MANIFEST_BINDING_REPAIR_PATHS, phase2.ALLOWED_PHASE2_PATHS),
            (3, phase3.MANIFEST_BINDING_REPAIR_PATHS, phase3.ALLOWED_PHASE3_PATHS),
            (5, phase5.MANIFEST_BINDING_REPAIR_PATHS, phase5.ALLOWED_PHASE5_PATHS),
        )
        hostile_paths = (
            "specs/adobe-ingester.md",
            "src/runtime.py",
            "tools/check_universal_manifest.py",
        )
        for phase, declared_repair_paths, allowed in allowed_sets:
            with self.subTest(phase=phase):
                self.assertEqual(repair_paths, declared_repair_paths)
                self.assertLessEqual(repair_paths, allowed)
                for hostile in hostile_paths:
                    self.assertFalse((repair_paths | {hostile}).issubset(allowed))


if __name__ == "__main__":
    unittest.main()
