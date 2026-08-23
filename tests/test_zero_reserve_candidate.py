from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "tools/check_zero_reserve_candidate.py"
MANIFEST = ROOT / "manifests/zero-discretionary-capacity-reserve-r2.json"
SELF_FIELD = re.compile(rb'("canonicalGitBlobSha256"\s*:\s*"sha256:)([0-9a-f]{64})(")')


def reseal(value: dict) -> bytes:
    value = copy.deepcopy(value)
    value["manifestSelf"]["canonicalGitBlobSha256"] = "sha256:" + "0" * 64
    zeroed = (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    digest = hashlib.sha256(zeroed).hexdigest()
    value["manifestSelf"]["canonicalGitBlobSha256"] = "sha256:" + digest
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


class ZeroReserveCandidateTests(unittest.TestCase):
    def run_checker(self, manifest_bytes: bytes) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory(prefix="zero-reserve-candidate-") as temp:
            path = Path(temp) / "manifest.json"
            path.write_bytes(manifest_bytes)
            return subprocess.run(
                ["python", str(CHECKER), "--root", str(ROOT), "--manifest", str(path)],
                cwd=ROOT, check=False, capture_output=True, text=True, encoding="utf-8",
            )

    def manifest(self) -> dict:
        return json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_exact_candidate_passes(self) -> None:
        run = subprocess.run(
            ["python", str(CHECKER)], cwd=ROOT, check=False,
            capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(0, run.returncode, run.stderr)
        self.assertIn("9/9 projects", run.stdout)

    def test_default_verification_ignores_checkout_line_endings(self) -> None:
        original = MANIFEST.read_bytes()
        try:
            MANIFEST.write_bytes(original.replace(b"\n", b"\r\n"))
            run = subprocess.run(
                ["python", str(CHECKER)], cwd=ROOT, check=False,
                capture_output=True, text=True, encoding="utf-8",
            )
            self.assertEqual(0, run.returncode, run.stderr)
        finally:
            MANIFEST.write_bytes(original)

    def test_unsealed_manifest_change_is_refused(self) -> None:
        data = MANIFEST.read_bytes().replace(b'"count": 9', b'"count": 8', 1)
        run = self.run_checker(data)
        self.assertNotEqual(0, run.returncode)
        self.assertIn("MANIFEST_SELF_MISMATCH", run.stderr)

    def test_duplicate_key_is_refused(self) -> None:
        data = MANIFEST.read_bytes().replace(
            b'"status": "CANDIDATE_ZERO_AUTHORITY",',
            b'"status": "CANDIDATE_ZERO_AUTHORITY",\n  "status": "CANDIDATE_ZERO_AUTHORITY",',
            1,
        )
        run = self.run_checker(data)
        self.assertNotEqual(0, run.returncode)
        self.assertIn("MANIFEST_JSON_INVALID", run.stderr)

    def test_missing_project_is_refused_even_when_resealed(self) -> None:
        value = self.manifest()
        value["closedProjectSet"]["projectIds"].pop()
        run = self.run_checker(reseal(value))
        self.assertNotEqual(0, run.returncode)
        self.assertIn("PROJECT_SET_INVALID", run.stderr)

    def test_authority_true_is_refused_even_when_resealed(self) -> None:
        value = self.manifest()
        value["authority"]["portableDoctrine"] = True
        run = self.run_checker(reseal(value))
        self.assertNotEqual(0, run.returncode)
        self.assertIn("AUTHORITY_INVALID", run.stderr)

    def test_subject_hash_drift_is_refused_even_when_resealed(self) -> None:
        value = self.manifest()
        value["subjectFiles"][0]["sha256"] = "sha256:" + "0" * 64
        run = self.run_checker(reseal(value))
        self.assertNotEqual(0, run.returncode)
        self.assertIn("SUBJECT_SHA256_MISMATCH", run.stderr)

    def test_unknown_source_commit_is_refused_even_when_resealed(self) -> None:
        value = self.manifest()
        value["source"]["commit"] = "0" * 40
        run = self.run_checker(reseal(value))
        self.assertNotEqual(0, run.returncode)
        self.assertIn("GIT_OBJECT_UNAVAILABLE", run.stderr)

    def test_changed_path_drift_is_refused_even_when_resealed(self) -> None:
        value = self.manifest()
        value["source"]["changedPaths"].append("RULINGS.md")
        run = self.run_checker(reseal(value))
        self.assertNotEqual(0, run.returncode)
        self.assertIn("CHANGED_PATH_MANIFEST_INVALID", run.stderr)

    def test_reserve_boundary_drift_is_refused_even_when_resealed(self) -> None:
        value = self.manifest()
        value["migrationSurface"]["hardEstimatedCeilingPct"] = 101
        run = self.run_checker(reseal(value))
        self.assertNotEqual(0, run.returncode)
        self.assertIn("MIGRATION_BOUNDARY_INVALID", run.stderr)


if __name__ == "__main__":
    unittest.main()
