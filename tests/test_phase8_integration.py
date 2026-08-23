from __future__ import annotations

import copy
import io
import importlib.util
import os
from pathlib import Path
from unittest import mock
import unittest
from contextlib import redirect_stdout

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "check_phase8_integration.py"
SPEC = importlib.util.spec_from_file_location("check_phase8_integration", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)
SNAPSHOT = MODULE.RETAINED_SNAPSHOT


class Phase8IntegrationTests(unittest.TestCase):
    def test_retained_snapshot_passes_without_unavailable_sources(self):
        MODULE.verify_integration(SNAPSHOT)
        self.assertEqual(set(MODULE.UNAVAILABLE_SOURCE_OBJECTS.values()), {
            "c5b9efd00c47a84488b96734dd9b6a94ecd37999",
            "ed8a2f359de8830c5800d1721faf183015eec01f",
            "1f3c3d8808b3d9bbb1db201039e0c3d18441f7f0",
        })

    def test_optional_source_rederive_fails_closed_while_objects_are_absent(self):
        with self.assertRaisesRegex(MODULE.Phase8Error, "SOURCE_OBJECTS_UNAVAILABLE_NOT_REVERIFIED"):
            MODULE.verify_integration(SNAPSHOT, rederive_source_objects=True)

    def test_present_source_mismatch_is_not_relabeled_unavailable(self):
        with (
            mock.patch.object(MODULE, "missing_source_objects", return_value=set()),
            mock.patch.object(MODULE, "verify_source_objects", side_effect=MODULE.Phase8Error("PHASE7_SUBJECT_MISMATCH")),
        ):
            with self.assertRaisesRegex(MODULE.Phase8Error, "PHASE7_SUBJECT_MISMATCH"):
                MODULE.verify_integration(SNAPSHOT, rederive_source_objects=True)

    def test_success_output_distinguishes_rederived_from_not_reverified(self):
        for enabled, marker in ((False, "SOURCE OBJECTS NOT REVERIFIED"), (True, "SOURCE OBJECTS REDERIVED")):
            output = io.StringIO()
            with mock.patch.object(MODULE, "verify_integration"), redirect_stdout(output):
                argv = ["--treeish", SNAPSHOT] + (["--rederive-source-objects"] if enabled else [])
                self.assertEqual(0, MODULE.main(argv))
            self.assertIn(marker, output.getvalue())

    def test_retained_snapshot_tuple_and_scope_are_exact(self):
        original_tuple = MODULE._commit_tuple
        with mock.patch.object(MODULE, "_commit_tuple", side_effect=lambda commit: (
            ("0" * 40, [MODULE.PHASE10_COMMIT]) if commit == SNAPSHOT else original_tuple(commit)
        )):
            with self.assertRaisesRegex(MODULE.Phase8Error, "RETAINED_SNAPSHOT_TUPLE_MISMATCH"):
                MODULE.verify_integration(SNAPSHOT)
        original_paths = MODULE._changed_paths
        with mock.patch.object(MODULE, "_changed_paths", side_effect=lambda base, tip: (
            original_paths(base, tip) | {"specs/cloudvore.md"}
            if (base, tip) == (MODULE.PHASE10_COMMIT, SNAPSHOT) else original_paths(base, tip)
        )):
            with self.assertRaisesRegex(MODULE.Phase8Error, "PHASE11_SOURCE_SCOPE_MISMATCH"):
                MODULE.verify_integration(SNAPSHOT)

    def test_ledger_packet_manifest_and_spec_drift_refuse(self):
        original = MODULE._oid
        for path, error in (
            (MODULE.LEDGER_PATH, "LEDGER_STATUS_ADVANCE"),
            ("adoption/phase7/requests/airmypc.json", "PRESERVED_ARTIFACT_DRIFT"),
            (MODULE.GLOBAL_MANIFEST_PATH, "GLOBAL_MANIFEST_BASELINE_DRIFT"),
            ("specs/cloudvore.md", "SPEC_BLOB_DRIFT"),
        ):
            with self.subTest(path=path), mock.patch.object(MODULE, "_oid", side_effect=lambda treeish, candidate, target=path: (
                "0" * 40 if treeish == SNAPSHOT and candidate == target else original(treeish, candidate)
            )):
                with self.assertRaisesRegex(MODULE.Phase8Error, error):
                    MODULE.verify_integration(SNAPSHOT)

    def test_packet_semantics_and_authority_are_closed(self):
        original = MODULE._load_json
        for field, error in (("authority", "REQUEST_AUTHORITY_ADVANCE"), ("status", "REQUEST_STATUS_ADVANCE")):
            def drift(treeish, path, target=field):
                value = copy.deepcopy(original(treeish, path))
                if path.endswith("adobe-ingester.json"):
                    if target == "authority":
                        value["authority"]["publication"] = True
                    else:
                        value["status"] = "ADOPT"
                return value
            with self.subTest(field=field), mock.patch.object(MODULE, "_load_json", side_effect=drift):
                with self.assertRaisesRegex(MODULE.Phase8Error, error):
                    MODULE.verify_zero_authority_packets(SNAPSHOT)

    def test_git_environment_indirection_is_refused(self):
        for key in ("GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_REPLACE_REF_BASE", "GIT_CONFIG_COUNT"):
            with self.subTest(key=key), mock.patch.dict(os.environ, {key: "forged"}, clear=False):
                with self.assertRaisesRegex(MODULE.Phase8Error, "GIT_OBJECT_INDIRECTION_REFUSED"):
                    MODULE.verify_git_object_isolation()

    def test_alternate_store_and_replace_refs_are_refused(self):
        with mock.patch.object(Path, "exists", return_value=True):
            with self.assertRaisesRegex(MODULE.Phase8Error, "GIT_ALTERNATE_OBJECT_STORE_REFUSED"):
                MODULE.verify_git_object_isolation()
        original = MODULE._git
        def replacement(args, **kwargs):
            return "0" * 40 + "\n" if args == ["replace", "-l"] else original(args, **kwargs)
        with mock.patch.object(MODULE, "_git", side_effect=replacement):
            with self.assertRaisesRegex(MODULE.Phase8Error, "GIT_REPLACE_OBJECT_REFUSED"):
                MODULE.verify_git_object_isolation()

    def test_snapshot_is_the_only_default_subject(self):
        for treeish in ("HEAD", MODULE.PHASE8_COMMIT, ":"):
            with self.subTest(treeish=treeish), self.assertRaisesRegex(MODULE.Phase8Error, "RETAINED_SNAPSHOT_REQUIRED"):
                MODULE.verify_integration(treeish)


if __name__ == "__main__":
    unittest.main()
