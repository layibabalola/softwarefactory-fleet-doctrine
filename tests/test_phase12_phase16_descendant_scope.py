from __future__ import annotations

import importlib.util
import os
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


def _load_checker(name: str):
    path = ROOT / "tools" / f"check_{name}.py"
    spec = importlib.util.spec_from_file_location(f"forward_scope_{name}", path)
    checker = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(checker)
    return checker


P2 = _load_checker("phase2_disposition_batch")
P3 = _load_checker("phase3_disposition_batch")
P5 = _load_checker("phase5_stale_reconciliation")
HISTORICAL_OWNED_EVIDENCE_PATHS = {
    "adoption/phase2/README.md",
    P2.BATCH_PATH,
    "adoption/phase3/README.md",
    P3.INTAKE_PATH,
    "adoption/phase5/README.md",
    P5.INTAKE_PATH,
}


class DescendantScopeTests(unittest.TestCase):
    def _classify(self, event: str, paths: set[str], *, ancestor: bool = True, base: str = BASE) -> str:
        with (
            mock.patch.object(MODULE, "_git", return_value=b""),
            mock.patch.object(MODULE, "_is_ancestor", return_value=ancestor),
            mock.patch.object(MODULE, "_changed_paths", return_value=paths),
        ):
            return MODULE.classify_event(event, base)

    def test_exact_bootstrap_is_applicable_for_pr_and_push(self):
        self.assertEqual(20, len(MODULE.MUTABLE_BOOTSTRAP_ALLOWLIST))
        self.assertTrue(MODULE.MUTABLE_BOOTSTRAP_ALLOWLIST < MODULE.PROTECTED_TRIGGER_PATHS)
        for event in ("pull_request", "push"):
            with self.subTest(event=event):
                self.assertEqual("APPLICABLE", self._classify(event, MODULE.MUTABLE_BOOTSTRAP_ALLOWLIST))

    def test_exact_phase17_repair_is_applicable_only_at_exact_base_and_delta(self):
        self.assertEqual(4, len(MODULE.PHASE17_REPAIR_ALLOWLIST))
        self.assertLessEqual(MODULE.PHASE17_REPAIR_ALLOWLIST, MODULE.PROTECTED_TRIGGER_PATHS)
        for event in ("pull_request", "push"):
            with self.subTest(event=event):
                self.assertEqual(
                    "APPLICABLE_PHASE17_REPAIR",
                    self._classify(
                        event,
                        MODULE.PHASE17_REPAIR_ALLOWLIST,
                        base=MODULE.PHASE17_REPAIR_BASE,
                    ),
                )
        with self.assertRaisesRegex(MODULE.DescendantScopeError, "DESCENDANT_SCOPE_VIOLATION"):
            self._classify(
                "pull_request",
                MODULE.PHASE17_REPAIR_ALLOWLIST | {"README.md"},
                base=MODULE.PHASE17_REPAIR_BASE,
            )

    def test_all_historical_phase2_phase3_phase5_triggers_are_forward_protected(self):
        historical_triggers = P2.PHASE2_TRIGGER_PATHS | P3.PHASE3_TRIGGER_PATHS | P5.PHASE5_TRIGGER_PATHS
        self.assertLessEqual(historical_triggers, MODULE.PROTECTED_TRIGGER_PATHS)
        self.assertIn(P3.LEDGER_PATH, MODULE.PROTECTED_TRIGGER_PATHS)
        for path in sorted(HISTORICAL_OWNED_EVIDENCE_PATHS):
            with self.subTest(path=path, base=BASE), self.assertRaisesRegex(
                MODULE.DescendantScopeError, "DESCENDANT_SCOPE_VIOLATION"
            ):
                self._classify("pull_request", {path})
            with self.subTest(path=path, base="later"), self.assertRaisesRegex(
                MODULE.DescendantScopeError, "BOOTSTRAP_SCOPE_CLOSED"
            ):
                self._classify("push", {path}, base="a" * 40)

        auxiliary = (
            P2.AUXILIARY_EVENT_ALLOWED_PATHS
            | P3.AUXILIARY_EVENT_ALLOWED_PATHS
            | P5.AUXILIARY_EVENT_ALLOWED_PATHS
        )
        self.assertTrue(auxiliary.isdisjoint(MODULE.PROTECTED_TRIGGER_PATHS))
        self.assertEqual("N/A_NO_PHASE12_PHASE16_TRIGGER", self._classify("pull_request", auxiliary))

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
        self.assertEqual("N/A_NO_PHASE12_PHASE16_TRIGGER", self._classify("pull_request", carrier, base="a" * 40))

    def test_bootstrap_is_one_time_exact_base_and_exact_delta(self):
        trigger = {"tools/check_phase12_phase16_descendant_scope.py"}
        with self.assertRaisesRegex(MODULE.DescendantScopeError, "DESCENDANT_SCOPE_VIOLATION"):
            self._classify("pull_request", trigger)
        for base in ("a" * 40, MODULE.PHASE15):
            with self.subTest(base=base), self.assertRaisesRegex(MODULE.DescendantScopeError, "BOOTSTRAP_SCOPE_CLOSED"):
                self._classify("pull_request", set(MODULE.MUTABLE_BOOTSTRAP_ALLOWLIST), base=base)
        with self.assertRaisesRegex(MODULE.DescendantScopeError, "DESCENDANT_SCOPE_VIOLATION"):
            self._classify("push", set(MODULE.MUTABLE_BOOTSTRAP_ALLOWLIST) | {"README.md"})

    def test_protected_immutable_change_and_trigger_mixing_refuse(self):
        trigger = {"tools/check_phase12_phase16_descendant_scope.py"}
        for protected in (
            "adoption/phase12/r26-current-master-review-integration.json",
            "adoption/phase16/phase15-review-packet.json",
            "tests/test_phase13_integration.py", "tools/check_phase15_integration.py",
            "tests/test_phase6_candidate_reviews.py", "tools/check_adoption_ledger.py",
            "adoption/universal-token-control-r26.json",
            "manifests/universal-provider-control-reconciliation-r26.json",
        ):
            with self.subTest(protected=protected), self.assertRaisesRegex(MODULE.DescendantScopeError, "DESCENDANT_SCOPE_VIOLATION"):
                self._classify("pull_request", {protected})
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
            self._classify("push", set(MODULE.MUTABLE_BOOTSTRAP_ALLOWLIST), ancestor=False)

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
            with mock.patch.dict(os.environ, {"R26_SCOPE_EVENT": "workflow_dispatch", "R26_SCOPE_BASE_SHA": ""}, clear=False):
                self.assertEqual(1, MODULE.main([]))
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
        raw = MODULE._blob("HEAD", ".github/workflows/disposition-intake.yml")
        with mock.patch.object(MODULE, "_blob", return_value=raw):
            MODULE.verify_current_workflow()
        final = next(line for line in MODULE.WORKFLOW_ROUTE_LINES if line.endswith(b"python tools/check_phase12_phase16_descendant_scope.py"))
        for hostile, code in (
            (raw.replace(final, b"", 1), "WORKFLOW_"),
            (raw + b"\n" + final, "WORKFLOW_"),
            (raw.replace(b"--treeish 990906b6ea861ca579e1336bcfe8f17dd80c83ae", b"--treeish HEAD", 1), "WORKFLOW_"),
        ):
            with self.subTest(code=code), mock.patch.object(MODULE, "_blob", return_value=hostile):
                with self.assertRaisesRegex(MODULE.DescendantScopeError, code):
                    MODULE.verify_current_workflow()

    def test_complete_workflow_route_env_and_timeout_hostiles_refuse(self):
        raw = MODULE._blob("HEAD", ".github/workflows/disposition-intake.yml")
        first = MODULE.WORKFLOW_ROUTE_LINES[0]
        second = MODULE.WORKFLOW_ROUTE_LINES[1]
        swapped = raw.replace(first, b"__FIRST__", 1).replace(second, first, 1).replace(b"__FIRST__", second, 1)
        hostiles = (
            raw.replace(first, b"", 1),
            raw + b"\n" + first,
            swapped,
            raw.replace(first, b"        # " + first.strip(), 1),
            raw.replace(MODULE.WORKFLOW_ENV_LINES[0], b"      R26_REMOTE_AUTH_CONFIGURED: true", 1),
            raw.replace(b"github.event.before", b"github.sha", 1),
            raw.replace(MODULE.WORKFLOW_TIMEOUT_LINE, b"", 1),
            raw + b"\n" + MODULE.WORKFLOW_TIMEOUT_LINE,
            raw.replace(MODULE.WORKFLOW_TIMEOUT_LINE, b"    timeout-minutes: 10", 1),
        )
        for hostile in hostiles:
            with self.subTest(hostile=hostile[:80]), mock.patch.object(MODULE, "_blob", return_value=hostile):
                with self.assertRaisesRegex(MODULE.DescendantScopeError, "WORKFLOW_"):
                    MODULE.verify_current_workflow()

    def test_workflow_trusted_controls_are_structurally_bound(self):
        raw = MODULE._blob("HEAD", ".github/workflows/disposition-intake.yml")
        blocks = (
            MODULE.WORKFLOW_EVIDENCE_HEADER_BLOCK,
            MODULE.WORKFLOW_PHASE3_REMOTE_BLOCK,
            MODULE.WORKFLOW_PHASE5_REMOTE_BLOCK,
        )
        with mock.patch.object(MODULE, "_blob", return_value=raw):
            MODULE.verify_current_workflow()
        for block in blocks:
            relocated = raw.replace(block, b"", 1) + b"\n  irrelevant:\n" + block
            duplicated = raw + b"\n" + block
            spoofed = raw.replace(block, b"# relocated\n" + block.replace(b"\n", b"\n# "), 1)
            for hostile in (relocated, duplicated, spoofed):
                with self.subTest(block=block[:60], hostile=hostile[-80:]), mock.patch.object(MODULE, "_blob", return_value=hostile):
                    with self.assertRaisesRegex(MODULE.DescendantScopeError, "WORKFLOW_"):
                        MODULE.verify_current_workflow()

    def test_scope_inputs_are_environment_only(self):
        for option in ("--scope-event", "--scope-base"):
            with self.subTest(option=option), self.assertRaises(SystemExit):
                MODULE.main([option, "workflow_dispatch"])

    def test_forward_checker_refuses_git_object_indirection_before_frozen_verifiers(self):
        for key in ("GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_REPLACE_REF_BASE", "GIT_CONFIG_COUNT"):
            with self.subTest(key=key), mock.patch.dict(os.environ, {key: "forged"}, clear=False):
                with self.assertRaisesRegex(MODULE.DescendantScopeError, "GIT_OBJECT_INDIRECTION_REFUSED"):
                    MODULE.verify_git_object_isolation()
        with mock.patch.object(Path, "exists", return_value=True):
            with self.assertRaisesRegex(MODULE.DescendantScopeError, "GIT_ALTERNATE_OBJECT_STORE_REFUSED"):
                MODULE.verify_git_object_isolation()
        original = MODULE._git
        with mock.patch.object(MODULE, "_git", side_effect=lambda args, **kwargs: "0" * 40 + "\n" if args == ["replace", "-l"] else original(args, **kwargs)):
            with self.assertRaisesRegex(MODULE.DescendantScopeError, "GIT_REPLACE_OBJECT_REFUSED"):
                MODULE.verify_git_object_isolation()
        with (
            mock.patch.object(MODULE, "verify_git_object_isolation", side_effect=MODULE.DescendantScopeError("GIT_OBJECT_INDIRECTION_REFUSED")) as isolation,
            mock.patch.object(MODULE, "verify_frozen_publications") as frozen,
        ):
            with mock.patch.dict(os.environ, {"R26_SCOPE_EVENT": "workflow_dispatch", "R26_SCOPE_BASE_SHA": ""}, clear=False):
                self.assertEqual(1, MODULE.main([]))
            isolation.assert_called_once()
            frozen.assert_not_called()

    def test_historical_treeish_cannot_redirect_event_target(self):
        self.assertNotIn("treeish", MODULE.classify_event.__code__.co_varnames)
        with mock.patch.object(MODULE, "_git", return_value=b""), mock.patch.object(MODULE, "_is_ancestor", return_value=True), mock.patch.object(MODULE, "_changed_paths", return_value=set()) as changed:
            MODULE.classify_event("pull_request", BASE)
            changed.assert_called_once_with(BASE)


if __name__ == "__main__":
    unittest.main()
