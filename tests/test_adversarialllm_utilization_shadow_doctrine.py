import hashlib
from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "specs" / "adversarialllm.md"
RULINGS_PATH = ROOT / "RULINGS.md"
HEADING = "## DISTINGUISH_UTILIZATION_SHADOW_BOUNDED_FOREGROUND_EXCEPTION"
EXPECTED_PRIOR_SPEC_BLOB = "33fe9c7fb7cc31b1f172b9216475fef5fe97aaad"
EXPECTED_BASE_COMMIT = "5ac7036705338cfe3370f5fddda224e07d5d1bdd"
EXPECTED_BASE_TREE = "9e53ff055bbf1a4fe796104d06f009f503082ad5"
EXPECTED_AMENDMENT_BASE_SPEC_BLOB = "f169a661956830aced574e6c3fa6f4989098e892"
EXPECTED_CANDIDATE_SPEC_BLOB = "e964d2b77426ece703f8fb1fd82a9cb068e98632"
EXPECTED_CANDIDATE_SPEC_BYTES = 23316
EXPECTED_CANDIDATE_SPEC_SHA256 = "8e90c07a1962d552dd5269354548beaabc79d5174b9d0717931709ba33df769f"
EXPECTED_RULINGS_BLOB = "34520b7f75386ab2dba6948bb27d256d3b06c2c9"
EXPECTED_R26_MERGE = "909f769d02e8412e51e28e242cfa8d00dadc9a3d"
EXPECTED_R26_SUBJECT = "e70a044f31dd2f43ab7c716d63a4eb89318c61b6"
EXPECTED_R26_TREE = "e9283a1c297103dd53f0bc7a1310fb1dc86b591e"
EXPECTED_R26_FIRST_PARENT = "c1529bc3030c6663e0be63c4789b07530b9b2ecc"
EXPECTED_R26_SUBJECT_PARENT = "387b4e13c4a8eeccf414d527b2d6a04dcd4e3ed8"


def extract_section(text: str) -> str:
    start = text.index(HEADING)
    remainder = text[start + len(HEADING) :]
    next_heading = remainder.find("\n## ")
    return text[start:] if next_heading < 0 else text[start : start + len(HEADING) + next_heading]


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def git_bytes(*args: str) -> bytes:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout


class AdversarialLlmUtilizationShadowDoctrineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = SPEC_PATH.read_text(encoding="utf-8")
        cls.section = extract_section(cls.spec)

    def test_exact_ruling_is_unique_and_currently_no_go(self):
        self.assertEqual(1, self.spec.count(HEADING))
        for required in (
            "Status: `PROJECT_DOCTRINE_EXCEPTION_NO_CURRENT_AUTHORITY`. Decision: `NO_GO`.",
            "remains `DISTINGUISH`, not `ADOPT`",
            "`hostHardCloseClaimed=false`",
            "`observedHostContainmentState=UNPROVED`",
            "`implementationState=NOT_INSTALLED`",
            "necessary but never\nsufficient for a provider call",
        ):
            self.assertIn(required, self.section)

    def test_exact_object_identity_is_pinned_without_self_pinning_result_blob(self):
        for oid in (
            EXPECTED_BASE_COMMIT,
            EXPECTED_BASE_TREE,
            EXPECTED_AMENDMENT_BASE_SPEC_BLOB,
            EXPECTED_PRIOR_SPEC_BLOB,
            EXPECTED_RULINGS_BLOB,
            EXPECTED_R26_MERGE,
            EXPECTED_R26_TREE,
            EXPECTED_R26_SUBJECT,
        ):
            self.assertIn(oid, self.section)
        self.assertNotIn("resultingSpecBlob=", self.section)
        expected_types = {
            EXPECTED_BASE_COMMIT: "commit",
            EXPECTED_BASE_TREE: "tree",
            EXPECTED_AMENDMENT_BASE_SPEC_BLOB: "blob",
            EXPECTED_PRIOR_SPEC_BLOB: "blob",
            EXPECTED_RULINGS_BLOB: "blob",
            EXPECTED_R26_MERGE: "commit",
            EXPECTED_R26_TREE: "tree",
            EXPECTED_R26_SUBJECT: "commit",
        }
        for oid, expected_type in expected_types.items():
            self.assertEqual(expected_type, git("cat-file", "-t", oid), oid)

        self.assertEqual(
            [EXPECTED_BASE_TREE],
            git("show", "-s", "--format=%T", EXPECTED_BASE_COMMIT).splitlines(),
        )
        self.assertEqual(
            EXPECTED_AMENDMENT_BASE_SPEC_BLOB,
            git("rev-parse", f"{EXPECTED_BASE_COMMIT}:specs/adversarialllm.md"),
        )
        self.assertEqual(
            EXPECTED_RULINGS_BLOB,
            git("rev-parse", f"{EXPECTED_BASE_COMMIT}:RULINGS.md"),
        )

        merge_lines = git("show", "-s", "--format=%T%n%P", EXPECTED_R26_MERGE).splitlines()
        self.assertEqual(EXPECTED_R26_TREE, merge_lines[0])
        self.assertEqual(
            f"{EXPECTED_R26_FIRST_PARENT} {EXPECTED_R26_SUBJECT}", merge_lines[1]
        )
        subject_lines = git("show", "-s", "--format=%T%n%P", EXPECTED_R26_SUBJECT).splitlines()
        self.assertEqual([EXPECTED_R26_TREE, EXPECTED_R26_SUBJECT_PARENT], subject_lines)
        self.assertEqual(
            EXPECTED_PRIOR_SPEC_BLOB,
            git("rev-parse", f"{EXPECTED_R26_MERGE}:specs/adversarialllm.md"),
        )
        self.assertEqual(
            EXPECTED_RULINGS_BLOB,
            git("rev-parse", f"{EXPECTED_R26_MERGE}:RULINGS.md"),
        )

    def test_complete_candidate_bytes_are_exact_base_plus_sole_amendment(self):
        working = SPEC_PATH.read_bytes()
        self.assertNotIn(b"\r", working.replace(b"\r\n", b""))
        canonical = working.replace(b"\r\n", b"\n")
        self.assertEqual(EXPECTED_CANDIDATE_SPEC_BYTES, len(canonical))
        self.assertEqual(
            EXPECTED_CANDIDATE_SPEC_SHA256,
            hashlib.sha256(canonical).hexdigest(),
        )
        self.assertEqual(
            EXPECTED_CANDIDATE_SPEC_BLOB,
            git("hash-object", "--path=specs/adversarialllm.md", "specs/adversarialllm.md"),
        )

        base = git_bytes("cat-file", "blob", EXPECTED_AMENDMENT_BASE_SPEC_BLOB)
        self.assertEqual(base, canonical[: len(base)])
        suffix = canonical[len(base) :]
        self.assertTrue(suffix.startswith(f"{HEADING}\n".encode("utf-8")))
        self.assertEqual(1, suffix.count(f"{HEADING}\n".encode("utf-8")))

        prior = git_bytes("cat-file", "blob", EXPECTED_PRIOR_SPEC_BLOB)
        self.assertEqual(12264, len(prior))
        self.assertEqual(
            "0d5758fc43094a9029491852faee190c8b34ec28d3fb14c561f82b87137ed99f",
            hashlib.sha256(prior).hexdigest(),
        )

    def test_rulings_are_unchanged_and_not_adjudicated_here(self):
        oid = subprocess.run(
            ["git", "hash-object", "--path=RULINGS.md", "RULINGS.md"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        self.assertEqual(EXPECTED_RULINGS_BLOB, oid)
        unchanged = subprocess.run(
            ["git", "diff", "--quiet", "HEAD", "--", "RULINGS.md"],
            cwd=ROOT,
            check=False,
        )
        self.assertEqual(0, unchanged.returncode)
        self.assertNotIn("APPROVED_BY_OWNER", self.section)
        self.assertNotIn("ADJUDICATED_PASS", self.section)

    def test_exact_six_entry_precedence_map_is_complete(self):
        expected = {
            "DISTINGUISH_SUCCESSOR_AND_HARD_CLOSED_BOUNDARY": (
                f"specs/adversarialllm.md@blob:{EXPECTED_PRIOR_SPEC_BLOB}#L65-L82",
                "PRESERVE_AND_SATISFY_SUCCESSOR_CONDITION_ONLY_AFTER_CANONICAL_MERGE",
            ),
            "UNIVERSAL_PROVIDER_SEMANTICS": (
                f"specs/adversarialllm.md@blob:{EXPECTED_PRIOR_SPEC_BLOB}#L85-L112",
                "PRESERVE",
            ),
            "ROLLOUT_OVERLAY_STATE_MACHINE": (
                f"specs/adversarialllm.md@blob:{EXPECTED_PRIOR_SPEC_BLOB}#L119-L127",
                "PRESERVE",
            ),
            "CANARY_AND_ROLLOUT_PREREQUISITES": (
                f"specs/adversarialllm.md@blob:{EXPECTED_PRIOR_SPEC_BLOB}#L129-L168",
                "PRESERVE_WITH_EXPLICIT_CLASSIFICATION",
            ),
            "NARROW_PROVIDER_LAUNCH_EXCEPTION": (
                f"specs/adversarialllm.md@blob:{EXPECTED_PRIOR_SPEC_BLOB}#L170-L176",
                "SUPERSEDE_ONLY_PROVIDER_LAUNCH_PROHIBITION_FOR_EXACT_CHILD_AFTER_ALL_GATES",
            ),
            "FLEET_RULINGS_NON_ADOPTION_BOUNDARY": (
                f"RULINGS.md@blob:{EXPECTED_RULINGS_BLOB}#L982-L987,L1027-L1034",
                "PRESERVE",
            ),
        }
        rows = [line for line in self.section.splitlines() if line.startswith("| `")]
        self.assertEqual(6, len(rows))
        for name, (source, relation) in expected.items():
            matches = [row for row in rows if row.startswith(f"| `{name}` |")]
            self.assertEqual(1, len(matches), name)
            self.assertIn(source, matches[0])
            self.assertIn(relation, matches[0])

    def test_scope_caps_and_credit_denials_are_exact(self):
        required = (
            "exactly one attended,\nforeground, one-shot Claude `DOCTRINE_EXACT_OBJECT_REVIEW` evidence job",
            "one job, one attempt, one provider turn",
            "observed concurrency exactly zero",
            "at most 900 seconds",
            "32,000 estimated tokens and 131,072 bytes",
            "4,000 estimated tokens and 32,768\nbytes",
            "capped at 1 percent",
            "no retry, continuation, second job",
            "no patch, repository mutation, review, correctness, adjudication, merge, release,\nactivation, or completion credit",
        )
        for value in required:
            self.assertIn(value, self.section)

    def test_provider_call_prerequisites_and_acyclic_order_are_exact(self):
        normalized = " ".join(self.section.split())
        required = (
            "`adversarialllm-utilization-shadow-adjudication/v1` record with decision\n`APPROVE_ONE_SHOT_UTILIZATION_SHADOW`",
            "two independent exact-proposal-byte `PASS` reviews",
            "authorized project-owner approval and a distinct authorized adjudicator",
            "digest-pinned installed controls and exact negative-control receipts",
            "adjudication record must not embed a future permit or receipt digest",
            "issue a later canonical one-use permit blob",
            "preflight and durably reserve the create-new terminal-receipt destination",
            "atomically consuming the permit before spawn",
            "already-reserved create-new destination without overwrite",
            "The permit remains consumed on failure",
        )
        for value in required:
            self.assertIn(" ".join(value.split()), normalized)
        numbered = [line for line in self.section.splitlines() if line[:3] in {f"{i}. " for i in range(1, 7)}]
        self.assertEqual([f"{i}. " for i in range(1, 7)], [line[:3] for line in numbered])
        reserve = normalized.index("preflight and durably reserve")
        consume = normalized.index("atomically consuming the permit before spawn")
        terminal_write = normalized.index("after the child terminates, write")
        self.assertLess(reserve, consume)
        self.assertLess(consume, terminal_write)

    def test_non_grants_remain_fail_closed(self):
        non_grants = self.section.split("This section grants no ", 1)[1]
        for value in (
            "`ADOPT`",
            "provider lane",
            "runtime activation",
            "rollout stage",
            "canary",
            "task",
            "schedule",
            "authentication",
            "Desktop",
            "automatic-gate",
            "repository-write",
            "merge",
            "review",
            "second-job",
            "host-hard-close authority",
        ):
            self.assertIn(value, non_grants)


if __name__ == "__main__":
    unittest.main()
