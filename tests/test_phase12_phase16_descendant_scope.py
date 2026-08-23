from __future__ import annotations

import importlib.util
from pathlib import Path
from unittest import mock
import unittest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "check_phase12_phase16_descendant_scope.py"
SPEC = importlib.util.spec_from_file_location("check_phase12_phase16_descendant_scope", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)
BASE = MODULE.PHASE16


class DescendantScopeTests(unittest.TestCase):
    def _classify(self, event: str, paths: set[str], *, ancestor: bool = True) -> str:
        with (
            mock.patch.object(MODULE, "_git", return_value=b""),
            mock.patch.object(MODULE, "_is_ancestor", return_value=ancestor),
            mock.patch.object(MODULE, "_changed_paths", return_value=paths),
        ):
            return MODULE.classify_event(event, BASE)

    def test_exact_bootstrap_is_applicable_for_pr_and_push(self):
        self.assertEqual(20, len(MODULE.BOOTSTRAP_CONTROL_PATHS))
        for event in ("pull_request", "push"):
            with self.subTest(event=event):
                self.assertEqual("APPLICABLE", self._classify(event, MODULE.BOOTSTRAP_CONTROL_PATHS))

    def test_carrier_and_unrelated_events_are_na(self):
        carrier = {
            "README.md", "RECONCILIATION.md",
            "manifests/universal-provider-control-reconciliation-r34.json",
            "schemas/universal-provider-review-admission-v1.schema.json",
            "specs/fleet-universal-provider-control-reconciliation.md",
            "tests/test_universal_provider_control.py",
            "tools/check_universal_manifest.py",
            "tools/universal_provider_control.py",
        }
        self.assertEqual("N/A_NO_PHASE12_PHASE16_TRIGGER", self._classify("pull_request", carrier))
        self.assertEqual("N/A_NO_PHASE12_PHASE16_TRIGGER", self._classify("push", {"README.md"}))

    def test_trigger_mixed_with_forbidden_or_foreign_refuses(self):
        trigger = {"tools/check_phase12_phase16_descendant_scope.py"}
        for path in (
            "specs/cloudvore.md", "manifests/forged.json",
            "adoption/universal-token-control-r26.json", "snapshots/forged.json",
            "tools/universal_provider_control.py", "src/runtime.py", "RULINGS.md",
        ):
            with self.subTest(path=path), self.assertRaisesRegex(MODULE.DescendantScopeError, "DESCENDANT_SCOPE_VIOLATION"):
                self._classify("pull_request", trigger | {path})

    def test_invalid_zero_missing_and_nonancestor_base_refuse(self):
        for base in ("", "0" * 40, "not-a-sha"):
            with self.subTest(base=base):
                if base == "0" * 40:
                    with mock.patch.object(MODULE, "_git", side_effect=MODULE.DescendantScopeError("SCOPE_BASE_INVALID")):
                        with self.assertRaisesRegex(MODULE.DescendantScopeError, "SCOPE_BASE_INVALID"):
                            MODULE.classify_event("pull_request", base)
                else:
                    with self.assertRaisesRegex(MODULE.DescendantScopeError, "SCOPE_BASE_INVALID"):
                        MODULE.classify_event("pull_request", base)
        with self.assertRaisesRegex(MODULE.DescendantScopeError, "SCOPE_BASE_INVALID"):
            self._classify("push", set(MODULE.BOOTSTRAP_CONTROL_PATHS), ancestor=False)

    def test_manual_is_explicit_na_and_unknown_event_refuses(self):
        self.assertEqual("N/A_WORKFLOW_DISPATCH", MODULE.classify_event("workflow_dispatch", ""))
        with self.assertRaisesRegex(MODULE.DescendantScopeError, "SCOPE_EVENT_INVALID"):
            MODULE.classify_event("schedule", BASE)

    def test_frozen_publications_are_verified_in_order(self):
        calls: list[str] = []
        patches = []
        for label, module, function in (
            ("12", MODULE.P12, "verify_integration"), ("13", MODULE.P13, "verify"),
            ("14", MODULE.P14, "verify"), ("15", MODULE.P15, "verify"),
            ("16", MODULE.P16, "verify"),
        ):
            patches.append(mock.patch.object(module, function, side_effect=lambda _treeish, value=label: calls.append(value)))
        with patches[0], patches[1], patches[2], patches[3], patches[4]:
            MODULE.verify_frozen_publications()
        self.assertEqual(["12", "13", "14", "15", "16"], calls)

    def test_frozen_failure_precedes_scope_and_manual_na(self):
        with (
            mock.patch.object(MODULE, "verify_frozen_publications", side_effect=MODULE.DescendantScopeError("PHASE12_FROZEN_PUBLICATION_INVALID")) as frozen,
            mock.patch.object(MODULE, "verify_current_workflow") as workflow,
            mock.patch.object(MODULE, "classify_event") as scope,
        ):
            self.assertEqual(1, MODULE.main(["--scope-event", "workflow_dispatch"]))
            frozen.assert_called_once()
            workflow.assert_not_called()
            scope.assert_not_called()

    def test_frozen_artifact_snapshot_ledger_manifest_and_spec_drift_refuse(self):
        cases = (
            (MODULE.P12, "verify_integration", "PHASE12_FROZEN_PUBLICATION_INVALID"),
            (MODULE.P13, "verify", "PHASE13_FROZEN_PUBLICATION_INVALID"),
            (MODULE.P14, "verify", "PHASE14_FROZEN_PUBLICATION_INVALID"),
            (MODULE.P15, "verify", "PHASE15_FROZEN_PUBLICATION_INVALID"),
            (MODULE.P16, "verify", "PHASE16_FROZEN_PUBLICATION_INVALID"),
        )
        for target, function, code in cases:
            with self.subTest(code=code), mock.patch.object(target, function, side_effect=ValueError("snapshot/spec/ledger/manifest drift")):
                with self.assertRaisesRegex(MODULE.DescendantScopeError, code):
                    MODULE.verify_frozen_publications()

    def test_workflow_routes_once_in_order_and_restores_literal_subjects(self):
        raw = (ROOT / ".github" / "workflows" / "disposition-intake.yml").read_bytes()
        with mock.patch.object(MODULE, "_blob", return_value=raw):
            MODULE.verify_current_workflow()
        final = b"python tools/check_phase12_phase16_descendant_scope.py"
        for hostile, code in (
            (raw.replace(final, b"", 1), "WORKFLOW_ROUTE_COUNT_INVALID"),
            (raw + b"\n" + final, "WORKFLOW_ROUTE_COUNT_INVALID"),
            (raw.replace(b"--treeish 990906b6ea861ca579e1336bcfe8f17dd80c83ae", b"--treeish HEAD", 1), "WORKFLOW_FROZEN_DISPOSITION_ROUTE_INVALID"),
        ):
            with self.subTest(code=code), mock.patch.object(MODULE, "_blob", return_value=hostile):
                with self.assertRaisesRegex(MODULE.DescendantScopeError, code):
                    MODULE.verify_current_workflow()

    def test_historical_treeish_cannot_redirect_event_target(self):
        self.assertNotIn("treeish", MODULE.classify_event.__code__.co_varnames)
        with mock.patch.object(MODULE, "_git", return_value=b""), mock.patch.object(MODULE, "_is_ancestor", return_value=True), mock.patch.object(MODULE, "_changed_paths", return_value=set()) as changed:
            MODULE.classify_event("pull_request", BASE)
            changed.assert_called_once_with(BASE)


if __name__ == "__main__":
    unittest.main()
