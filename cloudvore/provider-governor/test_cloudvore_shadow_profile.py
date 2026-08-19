import hashlib
import json
import subprocess
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
PROFILE_PATH = Path(__file__).with_name("cloudvore-shadow-profile-v1.json")
UNIVERSAL_PROFILE_PATH = Path(__file__).with_name("cloudvore-project-profile-proposal-v1.json")
UNIVERSAL_PROFILE_SCHEMA_PATH = ROOT / "schemas" / "universal-project-profile-v1.schema.json"
SPEC_PATH = ROOT / "specs" / "cloudvore.md"
ACCEPTED_SUBJECT = "224a6705d81dfbc670313cdcef4d825216f2b380"
ACCEPTED_TREE = "569957a2b62eb0e2e99c1490a9cbec0002894e42"
DISPOSITION = (
    "DISTINGUISH(224a6705d81dfbc670313cdcef4d825216f2b380, "
    "PENDING_LOCAL_ADAPTER_AND_DRILLS)"
)


def load_strict_json(path: Path):
    def reject_constant(value):
        raise ValueError(f"non-finite JSON value: {value}")

    def reject_duplicates(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    return json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=reject_duplicates,
        parse_constant=reject_constant,
    )


class CloudvoreShadowProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile = load_strict_json(PROFILE_PATH)
        cls.universal_profile = load_strict_json(UNIVERSAL_PROFILE_PATH)
        cls.spec = SPEC_PATH.read_text(encoding="utf-8")

    def test_profile_is_zero_authority_and_hard_closed(self):
        self.assertEqual("PROPOSED_ZERO_AUTHORITY", self.profile["proposal_status"])
        activation = self.profile["activation"]
        self.assertEqual("HARD_CLOSED", activation["current_stage"])
        self.assertEqual("closed", activation["automatic_launch_gate"])
        self.assertFalse(activation["reset_may_advance_stage"])
        self.assertTrue(activation["canary_requires_separate_authority"])
        self.assertIn("provider_launch", self.profile["no_authority"])
        self.assertIn("project_adoption", self.profile["no_authority"])
        self.assertIn("fleet_adoption", self.profile["no_authority"])

    def test_ratified_reconciliation_and_project_profile_are_exact_bound(self):
        reconciliation = self.profile["accepted_reconciliation"]
        self.assertEqual("874605e43531c9aa230ee16851f8107a8e0d9cec", reconciliation["candidate_commit"])
        self.assertEqual("cafc358fd7b60812070cf9a465d7de38b88487c8", reconciliation["candidate_tree"])
        self.assertEqual("488cf0dc0c2c2ddd1ab024c6377e1fd6d61eef1d", reconciliation["canonical_merge"])
        self.assertEqual("PORTABLE_DOCTRINE_ONLY", reconciliation["authority"])
        schema = load_strict_json(UNIVERSAL_PROFILE_SCHEMA_PATH)
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(self.universal_profile)
        self.assertEqual("cloudvore", self.universal_profile["project"])
        self.assertEqual("UNKNOWN", self.universal_profile["independenceClass"])
        self.assertFalse(self.universal_profile["invariants"]["directProviderInvocation"])
        self.assertFalse(self.universal_profile["invariants"]["resetCanOpenGate"])
        self.assertEqual(1, self.universal_profile["policy"]["maxConcurrentPerQuotaDomain"])

    def test_profile_pins_the_accepted_contract_and_every_artifact(self):
        contract = self.profile["accepted_contract"]
        self.assertEqual(ACCEPTED_SUBJECT, contract["commit"])
        self.assertEqual(ACCEPTED_TREE, contract["tree"])
        self.assertEqual(
            "BLOCKED_DECLARED_TUPLE_MISMATCH", contract["ruling_artifact_tuple_status"]
        )
        mismatches = contract["ruling_declared_mismatches"]
        self.assertEqual(
            {"README.md", "metrics/README.md", "examples/provider-usage-events-v1.jsonl"},
            {item["path"] for item in mismatches},
        )
        for item in mismatches:
            self.assertNotEqual(item["declared_sha256"], item["git_object_sha256"])
            self.assertEqual(64, len(item["git_object_sha256"]))
        tree = subprocess.run(
            ["git", "show", "-s", "--format=%T", ACCEPTED_SUBJECT],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        self.assertEqual(ACCEPTED_TREE, tree)
        artifacts = contract["artifact_manifest"]
        self.assertEqual(13, len(artifacts))
        self.assertEqual(13, len({item["path"] for item in artifacts}))
        for item in artifacts:
            with self.subTest(path=item["path"]):
                payload = subprocess.run(
                    ["git", "show", f"{ACCEPTED_SUBJECT}:{item['path']}"],
                    cwd=ROOT,
                    check=True,
                    capture_output=True,
                ).stdout
                self.assertEqual(item["size_bytes"], len(payload))
                self.assertEqual(item["sha256"], hashlib.sha256(payload).hexdigest())

    def test_fleet_activation_states_and_evidence_gates_do_not_fork(self):
        activation = self.profile["activation"]
        self.assertEqual(
            ["HARD_CLOSED", "INSTALLED_UNVERIFIED", "SHADOW", "CONTAINMENT", "CANARY", "ENABLED"],
            activation["fleet_stage_order"],
        )
        self.assertEqual(
            ["SHADOW_PASS", "CONTAINMENT_PASS", "CAPACITY_PASS", "CONTEXT_PASS", "ROUTING_PASS"],
            activation["evidence_gates"],
        )
        for state in activation["fleet_stage_order"] + activation["evidence_gates"]:
            self.assertIn(f"`{state}`", self.spec)

    def test_every_current_provider_family_is_pending_and_translation_only(self):
        adapters = self.profile["provider_adapters"]
        self.assertEqual({"anthropic", "openai", "moonshot", "xai"}, {a["family"] for a in adapters})
        for adapter in adapters:
            self.assertEqual(
                "PENDING_LOCAL_SUPERVISOR_AND_DRILLS", adapter["current_conformance"]
            )
            self.assertGreaterEqual(len(adapter["observed_launcher_sha256"]), 1)
            for digest in adapter["observed_launcher_sha256"]:
                self.assertEqual(64, len(digest))
        self.assertEqual(
            "PLAN_ONLY_NOT_ADMISSION_SUPERVISOR",
            self.profile["deterministic_router"]["authority"],
        )
        boundary = self.profile["translation_boundary"]
        self.assertIn("usage_fields", boundary["may_translate"])
        self.assertIn("admission_semantics", boundary["must_not_translate"])
        self.assertIn("authority", boundary["must_not_translate"])
        self.assertIn("model", boundary["must_not_translate"])
        self.assertTrue(self.profile["portable_contract"]["provider_adapters_translate_only"])
        self.assertFalse(self.profile["portable_contract"]["silent_downgrade_allowed"])

    def test_capsule_and_idle_contract_are_bounded(self):
        capsule = self.profile["evidence_capsule"]
        self.assertEqual(65536, capsule["max_payload_bytes"])
        self.assertEqual(64, capsule["max_references"])
        self.assertFalse(capsule["silent_required_evidence_truncation_allowed"])
        self.assertTrue(self.profile["portable_contract"]["deterministic_zero_inference_idle"])
        self.assertIn("IDLE_SKIPPED", self.profile["usage_event_types"])
        self.assertIn("RESET_OBSERVED", self.profile["usage_event_types"])

    def test_spec_retains_exact_disposition_and_profile_link(self):
        self.assertIn(DISPOSITION, self.spec.replace("\n", " "))
        self.assertIn("cloudvore/provider-governor/cloudvore-shadow-profile-v1.json", self.spec)
        self.assertIn("PROPOSED_ZERO_AUTHORITY", self.spec)


if __name__ == "__main__":
    unittest.main()
