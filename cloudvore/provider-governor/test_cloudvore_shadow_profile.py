import copy
import hashlib
import json
import re
import subprocess
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, ValidationError


ROOT = Path(__file__).resolve().parents[2]
PROFILE_PATH = Path(__file__).with_name("cloudvore-shadow-profile-v1.json")
PROFILE_SCHEMA_PATH = Path(__file__).with_name("cloudvore-shadow-profile-v1.schema.json")
UNIVERSAL_PROFILE_PATH = Path(__file__).with_name("cloudvore-project-profile-proposal-v1.json")
UNIVERSAL_PROFILE_SCHEMA_PATH = ROOT / "schemas" / "universal-project-profile-v1.schema.json"
SOURCE_DESIGN_PATH = ROOT / "cloudvore" / "provider-governor" / "provenance" / "HUB-DESIGN-provider-capacity-governor-shadow-adoption-0818.md"
RECEIPT_PATH = Path(__file__).with_name("PROPOSAL-RECEIPT-20260818.md")
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "provider-capacity-governor.yml"
MANIFEST_PATH = Path(__file__).with_name("cloudvore-provider-governor-proposal-manifest-v1.json")
SPEC_PATH = ROOT / "specs" / "cloudvore.md"
ACCEPTED_SUBJECT = "224a6705d81dfbc670313cdcef4d825216f2b380"
ACCEPTED_TREE = "569957a2b62eb0e2e99c1490a9cbec0002894e42"
RULING_COMMIT = "55a5808aa9edffcf9c86f1f9c2837a12a5c3c5d1"
RULING_BLOB = "79b4e8a4708ee5aec5a770a1aa8849d5bc4b1390"
RULING_BLOB_SHA256 = "a51993ef43320c7a6c3038b6e43a2ec72eee68406b948172dd499624bb2bae5b"
DISPOSITION = (
    "DISTINGUISH(224a6705d81dfbc670313cdcef4d825216f2b380, "
    "PENDING_LOCAL_ADAPTER_AND_DRILLS)"
)
R14_DISPOSITION = (
    "DISTINGUISH(874605e43531c9aa230ee16851f8107a8e0d9cec, "
    "PENDING_LOCAL_SUPERVISOR_ADAPTER_COMPLETE_CENSUS_AND_DRILLS, "
    "cloudvore/provider-governor/PROPOSAL-RECEIPT-20260818.md)"
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


def indexed_blob_bytes(path: Path):
    relative = path.relative_to(ROOT).as_posix()
    return subprocess.run(
        ["git", "show", f":{relative}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout


def validate_shadow_profile(profile):
    schema = load_strict_json(PROFILE_SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(profile)
    expected_lanes = {
        "anthropic": ["OPUS", "FABLE", "SONNET"],
        "openai": ["HUB", "SOL", "LUNA"],
        "moonshot": ["KIMI_IMPLEMENTER", "KIMI_REVIEWER"],
        "xai": ["GROK_IMPLEMENTER", "GROK_REVIEWER"],
    }
    actual_lanes = {item["family"]: item["lanes"] for item in profile["provider_adapters"]}
    if actual_lanes != expected_lanes:
        raise ValueError("PROVIDER_LANE_MAP_DRIFT")
    if profile["translation_boundary"]["may_translate"] != [
        "native_identity",
        "cache_fields",
        "usage_fields",
        "reset_fields",
        "terminal_fields",
        "refusal_fields",
    ]:
        raise ValueError("TRANSLATION_ALLOWLIST_DRIFT")
    if profile["translation_boundary"]["must_not_translate"] != [
        "admission_semantics",
        "authority",
        "quality_gate",
        "independence_credit",
        "budget_stop_meaning",
        "role",
        "model",
        "effort",
    ]:
        raise ValueError("TRANSLATION_DENYLIST_DRIFT")
    required_exclusions = ["score", "grade", "doctrine_write", "publication"]
    if profile["source_exclusions"]["excluded_from_admission_authority"] != required_exclusions:
        raise ValueError("SOURCE_EXCLUSION_DRIFT")
    for required in ("doctrine_write", "publication", "git_ref_mutation", "provider_launch"):
        if required not in profile["no_authority"]:
            raise ValueError("NO_AUTHORITY_DRIFT")


class CloudvoreShadowProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile = load_strict_json(PROFILE_PATH)
        cls.profile_schema = load_strict_json(PROFILE_SCHEMA_PATH)
        cls.universal_profile = load_strict_json(UNIVERSAL_PROFILE_PATH)
        cls.spec = SPEC_PATH.read_text(encoding="utf-8")

    def assert_profile_rejected(self, mutation):
        candidate = copy.deepcopy(self.profile)
        mutation(candidate)
        with self.assertRaises((ValidationError, ValueError)):
            validate_shadow_profile(candidate)

    def test_full_shadow_profile_and_tracked_source_preimage_validate(self):
        Draft202012Validator.check_schema(self.profile_schema)
        validate_shadow_profile(self.profile)
        source = indexed_blob_bytes(SOURCE_DESIGN_PATH)
        self.assertEqual(17321, len(source))
        self.assertEqual(
            "424a56c8700813c06bf31ac3b5b8c34b323f1ef6b1f38685e51bb89764957887",
            hashlib.sha256(source).hexdigest(),
        )
        self.assertEqual(self.profile["source_design"]["size_bytes"], len(source))
        self.assertEqual(self.profile["source_design"]["sha256"], hashlib.sha256(source).hexdigest())
        self.assertIn(b"release, score, or doctrine-write authority", source)
        self.assertIn(b"push, publication, release", source)

    def test_unknown_missing_and_semantic_profile_mutations_are_rejected(self):
        self.assert_profile_rejected(lambda value: value.update({"unknown_field": True}))
        self.assert_profile_rejected(lambda value: value.pop("source_exclusions"))
        self.assert_profile_rejected(
            lambda value: value["activation"].update({"automatic_launch_gate": "open"})
        )
        self.assert_profile_rejected(
            lambda value: value["provider_adapters"][0].update({"lanes": ["OPUS", "SONNET"]})
        )
        self.assert_profile_rejected(
            lambda value: value["source_exclusions"].update(
                {"excluded_from_admission_authority": ["score", "grade"]}
            )
        )
        self.assert_profile_rejected(lambda value: value["no_authority"].remove("publication"))

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
            "BLOCKED_TWO_RULING_MISMATCHES_ONE_PRIOR_PROFILE_TRANSCRIPTION_MISMATCH",
            contract["declared_tuple_status"],
        )
        checks = contract["declared_tuple_checks"]
        self.assertEqual(
            {"README.md", "metrics/README.md", "examples/provider-usage-events-v1.jsonl"},
            {item["path"] for item in checks},
        )
        ruling = subprocess.run(
            ["git", "show", f"{RULING_COMMIT}:RULINGS.md"],
            cwd=ROOT,
            check=True,
            capture_output=True,
        ).stdout
        ruling_blob = subprocess.run(
            ["git", "rev-parse", f"{RULING_COMMIT}:RULINGS.md"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        self.assertEqual(RULING_BLOB, ruling_blob)
        self.assertEqual(RULING_BLOB_SHA256, hashlib.sha256(ruling).hexdigest())
        self.assertEqual(RULING_COMMIT, contract["ruling_commit"])
        self.assertEqual(RULING_BLOB, contract["ruling_blob"])
        self.assertEqual(RULING_BLOB_SHA256, contract["ruling_blob_sha256"])
        text = ruling.decode("utf-8")
        start = text.index("## Fleet ratification — provider capacity governor v1, 2026-08-18")
        end = text.find("\n## ", start + 4)
        block = text[start:] if end < 0 else text[start:end]
        patterns = {
            "README.md": r"- root README `([0-9A-F]+)` / ([0-9,]+) B;",
            "metrics/README.md": r"- metrics README `([0-9A-F]+)` / ([0-9,]+) B;",
            "examples/provider-usage-events-v1.jsonl": (
                r"- usage examples `([0-9A-F]+)` / ([0-9,]+) B;"
            ),
        }
        declared = {}
        for path, pattern in patterns.items():
            match = re.search(pattern, block)
            self.assertIsNotNone(match, path)
            declared[path] = (match.group(1).lower(), int(match.group(2).replace(",", "")))
        self.assertEqual(64, len(declared["README.md"][0]))
        self.assertEqual(64, len(declared["metrics/README.md"][0]))
        self.assertEqual(64, len(declared["examples/provider-usage-events-v1.jsonl"][0]))
        source_text = indexed_blob_bytes(SOURCE_DESIGN_PATH).decode("utf-8")
        source_declared = {}
        for path in patterns:
            match = re.search(
                rf"\| `{re.escape(path)}` \| `([0-9A-F]+)` \| ([0-9,]+) \|",
                source_text,
            )
            self.assertIsNotNone(match, path)
            source_declared[path] = (
                match.group(1).lower(),
                int(match.group(2).replace(",", "")),
            )
        self.assertEqual(64, len(source_declared["examples/provider-usage-events-v1.jsonl"][0]))
        check_by_path = {item["path"]: item for item in checks}
        for path, (declared_sha, declared_size) in declared.items():
            item = check_by_path[path]
            self.assertEqual(declared_sha, item["ruling_declared_sha256"])
            self.assertEqual(declared_size, item["ruling_declared_size_bytes"])
            self.assertEqual(source_declared[path][0], item["source_design_sha256"])
            self.assertEqual(source_declared[path][1], item["source_design_size_bytes"])
            payload = subprocess.run(
                ["git", "show", f"{ACCEPTED_SUBJECT}:{path}"],
                cwd=ROOT,
                check=True,
                capture_output=True,
            ).stdout
            self.assertEqual(hashlib.sha256(payload).hexdigest(), item["git_object_sha256"])
            self.assertEqual(len(payload), item["git_object_size_bytes"])
            if item["classification"] == "RULING_TUPLE_MISMATCH":
                self.assertNotEqual(item["ruling_declared_sha256"], item["git_object_sha256"])
            else:
                self.assertEqual(item["ruling_declared_sha256"], item["git_object_sha256"])
                self.assertEqual(item["source_design_sha256"], item["git_object_sha256"])
                self.assertEqual(65, len(item["prior_profile_sha256"]))
                self.assertNotEqual(item["prior_profile_sha256"], item["git_object_sha256"])
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
        flattened = self.spec.replace("\n", " ")
        self.assertIn(DISPOSITION, flattened)
        self.assertIn(R14_DISPOSITION, flattened)
        self.assertIn("cloudvore/provider-governor/cloudvore-shadow-profile-v1.json", self.spec)
        self.assertIn(self.profile["source_design"]["path"], self.spec)
        self.assertIn("PROPOSED_ZERO_AUTHORITY", self.spec)
        for exclusion in ("`score`", "`grade`", "`doctrine_write`", "`publication`"):
            self.assertIn(exclusion, self.spec)

    def test_canonical_workflow_covers_profile_and_runs_validator_in_four_cells(self):
        workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
        self.assertGreaterEqual(workflow.count('"specs/cloudvore.md"'), 2)
        self.assertGreaterEqual(workflow.count('"cloudvore/provider-governor/**"'), 2)
        self.assertIn(
            'python -m unittest discover -s cloudvore/provider-governor -p "test_cloudvore_shadow_profile.py" -v',
            workflow,
        )
        self.assertIn("os: [windows-latest, ubuntu-latest]", workflow)
        self.assertIn('python-version: ["3.13", "3.14"]', workflow)
        self.assertIn(
            "python tools/check_universal_manifest.py --treeish 874605e43531c9aa230ee16851f8107a8e0d9cec",
            workflow,
        )

    def test_receipt_discloses_doctrine_publication_and_scopes_runtime_exclusions(self):
        receipt = RECEIPT_PATH.read_text(encoding="utf-8")
        self.assertIn("codex/cloudvore-provider-governor-shadow-profile-0818", receipt)
        self.assertIn("PR #17", receipt)
        self.assertIn("doctrine branch and PR were intentionally created and updated", receipt)
        self.assertIn("Cloudvore runtime/product Git ref", receipt)
        self.assertNotIn(
            "No provider, hosted workflow, product test, scheduler, credential, launcher, process, Git ref,",
            receipt,
        )

    def test_proposal_manifest_binds_canonical_indexed_blobs_and_self(self):
        manifest = load_strict_json(MANIFEST_PATH)
        self.assertEqual(
            {
                "schema",
                "status",
                "baseMaster",
                "publication",
                "authority",
                "subjectFiles",
                "manifestSelf",
            },
            set(manifest),
        )
        self.assertEqual("cloudvore-provider-governor-proposal-manifest/v1", manifest["schema"])
        self.assertEqual("PROPOSED_ZERO_AUTHORITY", manifest["status"])
        self.assertEqual("58efc8e3f3c1163c443ebe71be3b7a4aede42ce9", manifest["baseMaster"]["commit"])
        self.assertEqual("20c77898460584d27035744fccf4b50cfd17ac36", manifest["baseMaster"]["tree"])
        expected_paths = {
            ".github/workflows/provider-capacity-governor.yml",
            "specs/cloudvore.md",
            "cloudvore/provider-governor/PROPOSAL-RECEIPT-20260818.md",
            "cloudvore/provider-governor/cloudvore-project-profile-proposal-v1.json",
            "cloudvore/provider-governor/cloudvore-shadow-profile-v1.json",
            "cloudvore/provider-governor/cloudvore-shadow-profile-v1.schema.json",
            "cloudvore/provider-governor/test_cloudvore_shadow_profile.py",
            "cloudvore/provider-governor/provenance/HUB-DESIGN-provider-capacity-governor-shadow-adoption-0818.md",
        }
        subjects = manifest["subjectFiles"]
        self.assertEqual(expected_paths, {item["path"] for item in subjects})
        self.assertEqual(len(subjects), len({item["path"] for item in subjects}))
        for item in subjects:
            with self.subTest(path=item["path"]):
                path = ROOT / Path(item["path"])
                payload = indexed_blob_bytes(path)
                oid = subprocess.run(
                    ["git", "rev-parse", f":{item['path']}"],
                    cwd=ROOT,
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout.strip()
                self.assertEqual(item["gitBlobOid"], oid)
                self.assertEqual(item["bytes"], len(payload))
                self.assertEqual(item["sha256"], "sha256:" + hashlib.sha256(payload).hexdigest())
        raw = indexed_blob_bytes(MANIFEST_PATH)
        self.assertEqual(manifest["manifestSelf"]["bytes"], len(raw))
        pattern = re.compile(
            rb'("canonicalGitBlobSha256"\s*:\s*"sha256:)([0-9a-f]{64})(")'
        )
        self.assertEqual(1, len(pattern.findall(raw)))
        zeroed = pattern.sub(lambda match: match.group(1) + b"0" * 64 + match.group(3), raw)
        self.assertEqual(
            manifest["manifestSelf"]["canonicalGitBlobSha256"],
            "sha256:" + hashlib.sha256(zeroed).hexdigest(),
        )


if __name__ == "__main__":
    unittest.main()
