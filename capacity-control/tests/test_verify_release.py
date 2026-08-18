from __future__ import annotations

import hashlib
import importlib.util
import json
import pathlib
import sys
import tempfile
import unittest


MODULE = pathlib.Path(__file__).parents[1] / "reference" / "verify_release.py"
SPEC = importlib.util.spec_from_file_location("verify_release", MODULE)
assert SPEC and SPEC.loader
verifier = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = verifier
SPEC.loader.exec_module(verifier)


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


class ReleaseVerificationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.temporary.name)
        self.payload = self.root / "runtime.py"
        self.payload.write_bytes(b"candidate\n")
        self.manifest = self.root / "manifest.json"
        self.write_manifest()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write_manifest(self, path: str = "runtime.py") -> str:
        content = self.payload.read_bytes()
        value = {
            "schema": verifier.SCHEMA,
            "status": "CANDIDATE",
            "source_commit": "0" * 40,
            "generated_at": "2026-08-18T16:00:00Z",
            "files": [{"path": path, "sha256": digest(content), "bytes": len(content), "role": "runtime"}],
            "activation_requires": ["project-local review"],
        }
        self.manifest.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")
        return digest(self.manifest.read_bytes())

    def test_exact_manifest_and_payload_verify_without_activation_authority(self) -> None:
        result = verifier.verify(self.root, self.manifest, digest(self.manifest.read_bytes()))
        self.assertEqual("VERIFIED_CANDIDATE_BYTES", result["status"])
        self.assertFalse(result["activation_authority"])

    def test_payload_or_manifest_drift_refuses(self) -> None:
        expected = digest(self.manifest.read_bytes())
        self.payload.write_bytes(b"drift\n")
        with self.assertRaisesRegex(verifier.VerificationError, "mismatch"):
            verifier.verify(self.root, self.manifest, expected)
        self.payload.write_bytes(b"candidate\n")
        self.write_manifest()
        with self.assertRaisesRegex(verifier.VerificationError, "manifest SHA-256"):
            verifier.verify(self.root, self.manifest, "f" * 64)

    def test_traversal_and_symlink_costumes_refuse(self) -> None:
        expected = self.write_manifest("../runtime.py")
        with self.assertRaisesRegex(verifier.VerificationError, "escapes"):
            verifier.verify(self.root, self.manifest, expected)


if __name__ == "__main__":
    unittest.main(verbosity=2)
