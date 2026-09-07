import copy
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "check_phase17_dng_r60_publication.py"
SPEC = importlib.util.spec_from_file_location("check_phase17_dng_r60_publication", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class Phase17PublicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = json.loads((ROOT / MODULE.ARTIFACT).read_text(encoding="utf-8"))

    def assert_refused(self, mutate):
        candidate = copy.deepcopy(self.baseline)
        mutate(candidate)
        with self.assertRaises(MODULE.CheckFailure):
            MODULE.validate_document(candidate)

    def test_baseline_document_passes(self):
        MODULE.validate_document(copy.deepcopy(self.baseline))

    def test_worktree_integration_passes(self):
        MODULE.verify("WORKTREE")

    def test_status_overclaim_refused(self):
        self.assert_refused(lambda value: value.__setitem__("status", "ADOPTED"))

    def test_source_commit_substitution_refused(self):
        self.assert_refused(lambda value: value["sourceProject"].__setitem__("commit", "0" * 40))

    def test_project_artifact_substitution_refused(self):
        self.assert_refused(lambda value: value["projectArtifacts"][0].__setitem__("sha256", "0" * 64))

    def test_provider_verdict_substitution_refused(self):
        self.assert_refused(lambda value: value["r102Acceptance"]["verdicts"].__setitem__("opus", "REVISE"))

    def test_actionable_findings_overclaim_refused(self):
        self.assert_refused(lambda value: value["r102Acceptance"].__setitem__("actionableFindings", 1))

    def test_rollback_checkpoint_substitution_refused(self):
        self.assert_refused(lambda value: value["runtimeProof"]["rollbackCheckpoint"].__setitem__("sha256", "0" * 64))

    def test_full_rollback_overclaim_refused(self):
        self.assert_refused(lambda value: value["currentDisposition"].__setitem__("fullAdoptionRollbackProven", True))

    def test_idle_tick_overclaim_refused(self):
        self.assert_refused(lambda value: value["currentDisposition"].__setitem__("idleTicks", 1))

    def test_adoption_credit_overclaim_refused(self):
        self.assert_refused(lambda value: value["currentDisposition"].__setitem__("adoptionCredit", True))

    def test_ledger_mutation_claim_refused(self):
        self.assert_refused(lambda value: value["ledgerTreatment"].__setitem__("modified", True))

    def test_ledger_counts_substitution_refused(self):
        self.assert_refused(lambda value: value["ledgerTreatment"]["counts"].__setitem__("ADOPT", 1))

    def test_authority_overclaim_refused(self):
        self.assert_refused(lambda value: value["authority"].__setitem__("fleetAdoption", True))

    def test_extra_key_refused(self):
        self.assert_refused(lambda value: value.__setitem__("adopted", True))


if __name__ == "__main__":
    unittest.main()
