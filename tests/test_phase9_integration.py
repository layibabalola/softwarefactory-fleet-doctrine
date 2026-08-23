from __future__ import annotations

import copy
import importlib.util
import os
from pathlib import Path
from unittest import mock
import unittest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "check_phase9_integration.py"
SPEC = importlib.util.spec_from_file_location("check_phase9_integration", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)
SNAPSHOT = MODULE.PHASE11_COMMIT


class Phase9IntegrationTests(unittest.TestCase):
    def test_retained_snapshot_passes_without_unavailable_sources(self):
        MODULE.verify_integration(SNAPSHOT)
        self.assertEqual(set(MODULE.UNAVAILABLE_SOURCE_OBJECTS.values()), {
            "c5b9efd00c47a84488b96734dd9b6a94ecd37999",
            "ed8a2f359de8830c5800d1721faf183015eec01f",
            "1f3c3d8808b3d9bbb1db201039e0c3d18441f7f0",
        })

    def test_optional_source_rederive_fails_closed_while_objects_are_absent(self):
        with self.assertRaisesRegex(MODULE.Phase9Error, "SOURCE_OBJECTS_UNAVAILABLE_NOT_REVERIFIED"):
            MODULE.verify_integration(SNAPSHOT, rederive_source_objects=True)

    def test_retained_tuple_and_reachable_diffs_are_exact(self):
        original_tuple = MODULE._commit_tuple
        with mock.patch.object(MODULE, "_commit_tuple", side_effect=lambda commit: (
            ("0" * 40, [MODULE.PHASE10_COMMIT]) if commit == SNAPSHOT else original_tuple(commit)
        )):
            with self.assertRaisesRegex(MODULE.Phase9Error, "RETAINED_SNAPSHOT_TUPLE_MISMATCH"):
                MODULE.verify_integration(SNAPSHOT)
        original_paths = MODULE._changed_paths
        with mock.patch.object(MODULE, "_changed_paths", side_effect=lambda base, tip: (
            original_paths(base, tip) | {"src/runtime.py"}
            if (base, tip) == (MODULE.PHASE10_COMMIT, SNAPSHOT) else original_paths(base, tip)
        )):
            with self.assertRaisesRegex(MODULE.Phase9Error, "PHASE11_SOURCE_SCOPE_MISMATCH"):
                MODULE.verify_integration(SNAPSHOT)

    def test_manifest_receipt_request_ledger_spec_and_authority_drift_refuse(self):
        original_oid = MODULE._oid
        for path, error in (
            (MODULE.MANIFEST_PATH, "MECHANICAL_REPAIR_DRIFT"),
            (MODULE.MANIFEST_TEST_PATH, "MECHANICAL_REPAIR_DRIFT"),
            (MODULE.RECEIPT_PATH, "RECEIPT_DRIFT"),
            (next(iter(MODULE.REQUEST_BLOBS)), "REQUEST_DRIFT"),
            (MODULE.LEDGER_PATH, "LEDGER_DRIFT"),
            ("specs/cloudvore.md", "SPEC_STATUS_DRIFT"),
        ):
            with self.subTest(path=path), mock.patch.object(MODULE, "_oid", side_effect=lambda treeish, candidate, target=path: (
                "0" * 40 if treeish == SNAPSHOT and candidate == target else original_oid(treeish, candidate)
            )):
                with self.assertRaisesRegex(MODULE.Phase9Error, error):
                    MODULE.verify_integration(SNAPSHOT)

        original_json = MODULE._load_json
        def authority_drift(treeish, path):
            value = copy.deepcopy(original_json(treeish, path))
            if path == MODULE.MANIFEST_PATH:
                value["authority"]["providerExecution"] = True
            return value
        with mock.patch.object(MODULE, "_load_json", side_effect=authority_drift):
            with self.assertRaisesRegex(MODULE.Phase9Error, "MANIFEST_AUTHORITY_ADVANCE"):
                MODULE.verify_integration(SNAPSHOT)

    def test_git_environment_indirection_is_refused(self):
        for key in ("GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_REPLACE_REF_BASE", "GIT_CONFIG_COUNT"):
            with self.subTest(key=key), mock.patch.dict(os.environ, {key: "forged"}, clear=False):
                with self.assertRaisesRegex(MODULE.Phase9Error, "GIT_OBJECT_INDIRECTION_REFUSED"):
                    MODULE.verify_git_object_isolation()

    def test_alternate_store_and_replace_refs_are_refused(self):
        with mock.patch.object(Path, "exists", return_value=True):
            with self.assertRaisesRegex(MODULE.Phase9Error, "GIT_ALTERNATE_OBJECT_STORE_REFUSED"):
                MODULE.verify_git_object_isolation()
        original = MODULE._git
        def replacement(args, **kwargs):
            return "0" * 40 + "\n" if args == ["replace", "-l"] else original(args, **kwargs)
        with mock.patch.object(MODULE, "_git", side_effect=replacement):
            with self.assertRaisesRegex(MODULE.Phase9Error, "GIT_REPLACE_OBJECT_REFUSED"):
                MODULE.verify_git_object_isolation()

    def test_snapshot_is_the_only_default_subject(self):
        for treeish in ("HEAD", MODULE.PHASE9_COMMIT, ":"):
            with self.subTest(treeish=treeish), self.assertRaisesRegex(MODULE.Phase9Error, "RETAINED_SNAPSHOT_REQUIRED"):
                MODULE.verify_integration(treeish)


if __name__ == "__main__":
    unittest.main()
