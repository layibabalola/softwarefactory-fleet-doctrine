"""Exercise current event and seal boundaries with real, small Git histories."""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("epoch", ROOT / "tools/check_current_intake_epoch.py")
E = importlib.util.module_from_spec(spec)
spec.loader.exec_module(E)

def manifest():
    return {
        "schema": E.SCHEMA, "status": "CANDIDATE_ZERO_AUTHORITY",
        "bootstrapBase": E.BOOTSTRAP_BASE, "historicalWorkflow": E.SEALED_WORKFLOW,
        "newPhase17": E.NEW_PHASE17, "originalFailedPhase17": E.FAILED_PHASE17,
        "authority": {"runtime": False, "projectAdoption": False, "fleetAdoption": False},
        "controlFiles": {p: {"gitBlobOid": "a" * 40, "bytes": 1, "sha256": "b" * 64} for p in E.CONTROL_PATHS},
    }

class ManifestTests(unittest.TestCase):
    def test_successor_workflow_retains_all_suites_and_authorized_remote_call(self):
        workflow = (ROOT / '.github/workflows/disposition-intake.yml').read_text(encoding='utf-8')
        for name in E.UNIT_MODULES:
            self.assertEqual(workflow.count(f'run: python -m unittest discover -s tests -p "test_{name}.py" -v'), 1, name)
        step = next(part for part in workflow.split('      - name: ') if part.startswith('Verify immutable history and separately sealed current intake'))
        self.assertIn('R26_REMOTE_GITHUB_TOKEN: ${{ secrets.R26_CROSS_REPO_READ_TOKEN }}', step)
        self.assertIn("run: python tools/check_current_intake_epoch.py ${{ env.R26_REMOTE_AUTH_CONFIGURED == 'true' && '--verify-remotes' || '' }}", step)
        for token in ('fetch-depth: 0', 'persist-credentials: false', 'R26_SCOPE_EVENT: ${{ github.event_name }}', 'github.event.pull_request.base.sha', 'github.event.before'):
            self.assertIn(token, workflow)

    def test_remote_flag_reaches_both_retained_verifiers_and_failures_propagate(self):
        modules = {}
        for name in ('phase2_disposition_batch', 'phase3_disposition_batch', 'phase5_stale_reconciliation'):
            modules[name] = SimpleNamespace(FROZEN_PUBLICATION='frozen', BATCH_PATH='batch', INTAKE_PATH='intake', _blob=mock.Mock(return_value=b'{}'), load_json=mock.Mock(return_value={}), verify_batch=mock.Mock(), verify_remotes=mock.Mock())
        modules['phase12_phase16_descendant_scope'] = SimpleNamespace(verify_frozen_publications=mock.Mock(), verify_current_workflow=mock.Mock())
        class OriginalFailure(ValueError):
            pass
        modules['phase17_dng_r60_publication'] = SimpleNamespace(ALLOWED={'proof'}, CheckFailure=OriginalFailure, verify=mock.Mock(side_effect=[None, OriginalFailure('unexpected Phase 17 paths')]))
        modules['adoption_ledger'] = SimpleNamespace(LEDGER_PATH='ledger', _blob=mock.Mock(return_value=b'{}'), load_ledger=mock.Mock(return_value={}), verify_ledger=mock.Mock())
        with mock.patch.object(E, 'load', side_effect=lambda name: modules[name]), mock.patch.object(E, 'blob', return_value=b'identical original proof'):
            E.verify_history(verify_remotes=True)
            for name in ('phase3_disposition_batch', 'phase5_stale_reconciliation'):
                modules[name].verify_remotes.assert_called_once_with({})
            modules['phase2_disposition_batch'].verify_remotes.assert_not_called()
            modules['phase3_disposition_batch'].verify_remotes.side_effect = E.IntakeError('REMOTE_RED')
            with self.assertRaisesRegex(E.IntakeError, 'REMOTE_RED'):
                E.verify_history(verify_remotes=True)

    def test_valid_and_adverse_manifest(self):
        good = manifest()
        self.assertEqual(E.parse_manifest(json.dumps(good).encode()), good)
        cases = (
            (lambda m: m.update(extra=True), "EPOCH_FIELDS_INVALID"),
            (lambda m: m["controlFiles"].pop(next(iter(m["controlFiles"]))), "CONTROL_CLOSED_SET_INVALID"),
            (lambda m: m["controlFiles"].update({"hidden.py": {}}), "CONTROL_CLOSED_SET_INVALID"),
            (lambda m: m["authority"].update(runtime=True), "EPOCH_AUTHORITY_OVERCLAIM"),
            (lambda m: m["authority"].update(runtime=0), "EPOCH_AUTHORITY_OVERCLAIM"),
            (lambda m: m["controlFiles"][next(iter(m["controlFiles"]))].update(bytes=True), "CONTROL_RECORD_INVALID"),
            (lambda m: m.update(newPhase17="0" * 40), "EPOCH_SUBJECT_INVALID"),
        )
        for mutate, code in cases:
            value = copy.deepcopy(good)
            mutate(value)
            with self.subTest(code=code), self.assertRaisesRegex(E.IntakeError, code):
                E.parse_manifest(json.dumps(value).encode())
        raw = json.dumps(good).encode().replace(b'"schema":', b'"schema":"x","schema":', 1)
        with self.assertRaisesRegex(E.IntakeError, "DUPLICATE_JSON_KEY"):
            E.parse_manifest(raw)

    def test_manual_validates_before_classification_or_checker_import(self):
        names = ("verify_git_object_isolation", "verify_control_seal", "verify_retained_current_artifacts", "verify_history")
        for failing in names:
            with self.subTest(failing=failing), mock.patch.dict(os.environ, {"R26_SCOPE_EVENT": "workflow_dispatch"}):
                with (
                    mock.patch.object(E, names[0]) as isolation,
                    mock.patch.object(E, "blob", return_value=json.dumps(manifest()).encode()),
                    mock.patch.object(E, names[1]) as seal,
                    mock.patch.object(E, names[2]) as retained,
                    mock.patch.object(E, names[3]) as history,
                    mock.patch.object(E, "load") as loader,
                    mock.patch.object(E, "classify_event") as event,
                ):
                    dict(zip(names, (isolation, seal, retained, history)))[failing].side_effect = E.IntakeError("BOUNDARY_RED")
                    with self.assertRaisesRegex(E.IntakeError, "BOUNDARY_RED"):
                        E.verify()
                    event.assert_not_called()
                    loader.assert_not_called()

class GitEventTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="r26-epoch-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        clean = {k: v for k, v in os.environ.items() if k not in E.UNSAFE_GIT_ENV and not k.startswith("GIT_CONFIG")}
        self.enterContext(mock.patch.dict(os.environ, clean, clear=True))
        self.enterContext(mock.patch.object(E, "ROOT", self.root))
        self.git("init", "-q")
        self.git("config", "core.autocrlf", "false")
        self.git("config", "core.hooksPath", str(self.root / "no-hooks"))
        self.write("control.py", "print('sealed')\n")
        self.write("adoption/old.json", "old\n")
        self.base = self.commit("base")
        self.enterContext(mock.patch.object(E, "BOOTSTRAP_BASE", self.base))
        self.enterContext(mock.patch.object(E, "CONTROL_PATHS", {"control.py"}))
        self.enterContext(mock.patch.object(E, "BOOTSTRAP_CHANGED", {E.EPOCH_PATH, E.CURRENT_LEDGER}))

    def git(self, *args):
        run = subprocess.run(["git", "--no-optional-locks", "-c", "user.name=Epoch Test", "-c", "user.email=epoch@example.invalid", *args], cwd=self.root, capture_output=True, check=True)
        return run.stdout.decode().strip()

    def write(self, path, value):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(value.encode())

    def commit(self, message):
        # Only this disposable fixture repository is staged.
        self.git("add", ".")
        self.git("commit", "-qm", message)
        return self.git("rev-parse", "HEAD")

    def publish_epoch(self):
        self.write(E.EPOCH_PATH, "sealed epoch\n")
        self.write(E.CURRENT_LEDGER, "census\n")
        return self.commit("epoch")

    def test_bootstrap_exact_change_set_and_missing_or_extra(self):
        self.write(E.EPOCH_PATH, "sealed epoch\n")
        self.commit("incomplete")
        with self.assertRaisesRegex(E.IntakeError, "BOOTSTRAP_CHANGE_SET_INVALID"):
            E.classify_event("pull_request", self.base)
        self.publish_epoch()
        self.assertEqual(E.classify_event("pull_request", self.base), "BOOTSTRAP_CANDIDATE_REQUIRES_INDEPENDENT_REVIEW")
        self.write("unexpected.md", "extra\n")
        self.commit("extra")
        with self.assertRaisesRegex(E.IntakeError, "BOOTSTRAP_CHANGE_SET_INVALID"):
            E.classify_event("push", self.base)

    def test_census_accepted_but_manifest_change_needs_amendment(self):
        base = self.publish_epoch()
        self.write(E.CURRENT_LEDGER, "new census\n")
        self.commit("census")
        self.assertEqual(E.classify_event("push", base), "CURRENT_INTAKE_VALIDATED_ZERO_AUTHORITY")
        self.write(E.EPOCH_PATH, "new control epoch\n")
        self.commit("amendment")
        with self.assertRaisesRegex(E.IntakeError, "CONTROL_EPOCH_AMENDMENT_REQUIRED"):
            E.classify_event("push", base)

    def test_control_change_without_manifest_edit_needs_amendment(self):
        base = self.publish_epoch()
        self.write("control.py", "print('changed')\n")
        self.commit("changed controller")
        with self.assertRaisesRegex(E.IntakeError, "CONTROL_EPOCH_AMENDMENT_REQUIRED"):
            E.classify_event("pull_request", base)

    def test_event_rejects_zero_missing_and_real_nonancestor(self):
        self.publish_epoch()
        sibling = self.git("commit-tree", self.git("rev-parse", f"{self.base}^{{tree}}"), "-p", self.base, "-m", "sibling")
        for base in ("bad", "0" * 40, "f" * 40, sibling):
            with self.subTest(base=base), self.assertRaisesRegex(E.IntakeError, "EVENT_BASE_INVALID"):
                E.classify_event("push", base)
        with self.assertRaisesRegex(E.IntakeError, "EVENT_INVALID"):
            E.classify_event("pull_request_target", self.base)

    def test_seal_accepts_crlf_only_and_refuses_working_or_committed_drift(self):
        raw = E.blob("HEAD", "control.py")
        seal = {"controlFiles": {"control.py": {"bytes": len(raw), "gitBlobOid": self.git("rev-parse", "HEAD:control.py"), "sha256": hashlib.sha256(raw).hexdigest()}}}
        E.verify_control_seal(seal)
        (self.root / "control.py").write_bytes(raw.replace(b"\n", b"\r\n"))
        E.verify_control_seal(seal)
        self.write("control.py", "print('bad')\n")
        with self.assertRaisesRegex(E.IntakeError, "CONTROL_WORKTREE_DRIFT"):
            E.verify_control_seal(seal)
        self.commit("changed bytes")
        with self.assertRaisesRegex(E.IntakeError, "CONTROL_BYTES_CHANGED"):
            E.verify_control_seal(seal)

    def test_historical_artifact_mutation_refused_with_real_diff(self):
        self.publish_epoch()
        E.verify_retained_current_artifacts()
        self.write("adoption/old.json", "rewritten history\n")
        self.commit("rewrite old evidence")
        with self.assertRaisesRegex(E.IntakeError, "HISTORICAL_ARTIFACT_CHANGED"):
            E.verify_retained_current_artifacts()

    def test_git_indirection_and_replace_refs_are_refused(self):
        E.verify_git_object_isolation()
        with mock.patch.dict(os.environ, {"GIT_CONFIG_COUNT": "0"}):
            with self.assertRaisesRegex(E.IntakeError, "GIT_OBJECT_INDIRECTION_REFUSED"):
                E.verify_git_object_isolation()
        self.publish_epoch()
        self.git("replace", self.base, "HEAD")
        with self.assertRaisesRegex(E.IntakeError, "GIT_REPLACE_OBJECT_REFUSED"):
            E.verify_git_object_isolation()

if __name__ == "__main__":
    unittest.main()
