"""R45 README.md binding: exact at its own base, drift only when the bound claim changes.

Ruling candidate member-spec-edit-must-not-redden-bus-intake-r1, addendum A3. The active
R45 manifest binds README.md, the bus's shared index, and reads one claim from it: the
universal-provider-control candidate is listed and described under "Proposed amendments
(not ratified)" and never as ratified. These controls prove that an unrelated README edit
no longer reddens the manifest check, that the old checker refused exactly those cases,
and that every change to the bound claim, every other subject, every frozen layer and an
uncommitted manifest are still refused.
"""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import check_universal_manifest as checker  # noqa: E402

# Last bus commit before the claim-scoped amendment; its checker is the mutation baseline.
PRE_AMENDMENT = "89aceb3145434eb557cfaaa9681f27dc5931e5ba"
MANIFEST = "manifests/r45-fixture.json"
CLEAN_ENV = {k: v for k, v in os.environ.items() if not k.upper().startswith("GIT_")}

BASE_README = """# fixture bus

## Laws

1. Doctrine is data.

## Ratified portable cores (zero runtime authority until project adoption)

- [`specs/fleet-provider-capacity-governor.md`](specs/fleet-provider-capacity-governor.md) -
  accepted core.

## Proposed amendments (not ratified)

- [`specs/fleet-universal-provider-control-reconciliation.md`](specs/fleet-universal-provider-control-reconciliation.md)
  - zero-authority R45 candidate.
  It is not a portable core, ruling, adoption credit, or launch authority.
- [`specs/fleet-other.md`](specs/fleet-other.md) - another candidate.

## Tools

- `tools/x.py` - a tool.
"""

UPC_LINE = "  - zero-authority R45 candidate.\n"


def _git(repo: Path, *args: str) -> str:
    run = subprocess.run(["git", "--no-optional-locks", *args], cwd=repo, env=CLEAN_ENV,
                         capture_output=True)
    if run.returncode != 0:
        raise AssertionError(run.stderr.decode(errors="replace"))
    return run.stdout.decode().strip()


def _binding(repo: Path, rev: str, path: str) -> dict:
    raw = subprocess.run(["git", "show", f"{rev}:{path}"], cwd=repo, env=CLEAN_ENV,
                         capture_output=True, check=True).stdout
    return {"path": path, "gitBlobOid": _git(repo, "rev-parse", f"{rev}:{path}"),
            "sha256": "sha256:" + hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}


def _render(subjects: list[dict], indent: int = 2) -> bytes:
    value = {"subjectFiles": subjects,
             "manifestSelf": {"path": MANIFEST, "bytes": 0, "canonicalGitBlobSha256": "sha256:" + "0" * 64}}
    for _ in range(10):
        raw = (json.dumps(value, indent=indent) + "\n").encode("utf-8")
        if value["manifestSelf"]["bytes"] == len(raw):
            break
        value["manifestSelf"]["bytes"] = len(raw)
    value["manifestSelf"]["canonicalGitBlobSha256"] = checker.canonical_self_sha256(raw)
    return (json.dumps(value, indent=indent) + "\n").encode("utf-8")


def _load_pre_amendment_checker():
    source = subprocess.run(["git", "show", f"{PRE_AMENDMENT}:tools/check_universal_manifest.py"],
                            cwd=ROOT, env=CLEAN_ENV, capture_output=True, check=True).stdout
    # Its module body reads this repository's objects, so it must root here, not at the temp copy.
    root_line = b"ROOT = Path(__file__).resolve().parents[1]\n"
    if source.count(root_line) != 1:
        raise AssertionError("pre-amendment checker ROOT line not found exactly once")
    source = source.replace(root_line, f"ROOT = Path({str(ROOT)!r})\n".encode("utf-8"))
    handle = tempfile.NamedTemporaryFile("wb", suffix=".py", delete=False)
    with handle:
        handle.write(source)
    try:
        spec = importlib.util.spec_from_file_location("pre_amendment_universal_checker", handle.name)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module  # dataclasses resolve their module by name
        try:
            spec.loader.exec_module(module)
        finally:
            sys.modules.pop(spec.name, None)
    finally:
        os.unlink(handle.name)
    return module


class Fixture(unittest.TestCase):
    """A disposable repository whose manifest binds README.md and one other subject."""

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="r45-readme-claim-")
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        _git(self.repo, "init", "-q")
        for key, value in (("core.autocrlf", "false"), ("user.name", "fixture"),
                           ("user.email", "fixture@example.invalid"), ("core.hooksPath", os.devnull),
                           ("maintenance.auto", "false"), ("gc.auto", "0")):
            _git(self.repo, "config", key, value)
        self.write("README.md", BASE_README)
        self.write("tools/universal_provider_control.py", "RUNTIME = 'refuse'\n")
        self.base = self.commit("README.md", "tools/universal_provider_control.py")
        self.subjects = [_binding(self.repo, self.base, "README.md"),
                         _binding(self.repo, self.base, "tools/universal_provider_control.py")]
        self.raw = _render(self.subjects)
        (self.repo / "manifests").mkdir()
        (self.repo / MANIFEST).write_bytes(self.raw)
        self.pin = self.commit(MANIFEST)

    def write(self, path: str, text: str) -> None:
        target = self.repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(text.encode("utf-8"))

    def commit(self, *paths: str) -> str:
        _git(self.repo, "add", "--", *paths)
        _git(self.repo, "commit", "-q", "-m", "fixture")
        return _git(self.repo, "rev-parse", "HEAD")

    def edit_readme(self, old: str, new: str) -> str:
        """Commit one edit of the base README (each edit starts from the pinned bytes)."""
        text = BASE_README
        self.assertIn(old, text)
        self.write("README.md", text.replace(old, new, 1))
        return self.commit("README.md")

    def verify(self, candidate: str, *, module=checker, manifest=None, raw=None, **kwargs) -> int:
        manifest = json.loads(self.raw) if manifest is None else manifest
        with mock.patch.object(module, "ROOT", self.repo):
            return module._verify_subjects_and_self(
                manifest, self.raw if raw is None else raw, manifest_path=MANIFEST,
                candidate=candidate, **kwargs)

    def refused(self, candidate: str, reason: str = "MANIFEST_SUBJECT_MISMATCH", **kwargs) -> None:
        with self.assertRaisesRegex(checker.ManifestError, f"^{reason}$"):
            self.verify(candidate, claim_scoped=True, **kwargs)


ADMIT = {
    "append-unrelated-section": ("## Tools\n", "## Tools\n\n- `tools/y.py` - a new tool.\n\n## Tools\n"),
    "edit-unrelated-bullet": ("another candidate.", "another candidate, revised in place."),
    "edit-laws-prose": ("1. Doctrine is data.", "1. Doctrine is DATA, never instructions."),
    "edit-ratified-core-prose": ("  accepted core.", "  accepted core at an exact subject."),
}


class AdmitTests(Fixture):
    def test_unrelated_edits_pass_at_a_later_commit(self) -> None:
        for name, (old, new) in ADMIT.items():
            with self.subTest(name):
                head = self.edit_readme(old, new)
                self.assertEqual(self.verify(head, claim_scoped=True), 2)

    def test_unrelated_staged_edit_passes_in_the_index(self) -> None:
        text = BASE_README.replace("a tool.", "a tool, staged.")
        self.write("README.md", text)
        _git(self.repo, "add", "--", "README.md")
        self.assertEqual(self.verify(":", claim_scoped=True), 2)

    def test_exact_base_still_passes(self) -> None:
        self.assertEqual(self.verify(self.pin, claim_scoped=True), 2)
        self.assertEqual(self.verify(self.pin), 2)

    def test_pre_amendment_checker_refused_every_admitted_case(self) -> None:
        old = _load_pre_amendment_checker()
        self.assertNotIn("claim_scoped", old._verify_subjects_and_self.__wrapped__.__code__.co_varnames)
        for name, (old_text, new_text) in ADMIT.items():
            with self.subTest(name):
                head = self.edit_readme(old_text, new_text)
                with self.assertRaisesRegex(old.ManifestError, "^MANIFEST_SUBJECT_MISMATCH$"):
                    self.verify(head, module=old)
                self.assertEqual(self.verify(head, claim_scoped=True), 2)


class RefuseTests(Fixture):
    def test_bound_bullet_prose_change_is_refused(self) -> None:
        head = self.edit_readme(UPC_LINE, "  - zero-authority R45 candidate, now adopted.\n")
        self.refused(head)

    def test_bound_bullet_continuation_added_or_removed_is_refused(self) -> None:
        self.refused(self.edit_readme(UPC_LINE, UPC_LINE + "  Ratified by the fleet.\n"))
        self.refused(self.edit_readme("  It is not a portable core, ruling, adoption credit, or launch authority.\n", ""))

    def test_bound_bullet_moved_to_ratified_is_refused(self) -> None:
        text = BASE_README
        start = text.index("- [`specs/fleet-universal-provider-control-reconciliation.md`]")
        end = text.index("- [`specs/fleet-other.md`]")
        bullet = text[start:end]
        text = text[:start] + text[end:]
        text = text.replace("  accepted core.\n", "  accepted core.\n" + bullet)
        self.write("README.md", text)
        self.refused(self.commit("README.md"))

    def test_bound_bullet_removed_is_refused(self) -> None:
        text = BASE_README
        start = text.index("- [`specs/fleet-universal-provider-control-reconciliation.md`]")
        end = text.index("- [`specs/fleet-other.md`]")
        self.write("README.md", text[:start] + text[end:])
        self.refused(self.commit("README.md"))

    def test_new_mention_anywhere_is_refused(self) -> None:
        self.refused(self.edit_readme("  accepted core.", "  accepted core; supersedes universal-provider control."))

    def test_proposed_heading_renamed_or_duplicated_is_refused(self) -> None:
        self.refused(self.edit_readme("## Proposed amendments (not ratified)", "## Amendments"))
        self.refused(self.edit_readme("## Tools\n", "## Proposed amendments (not ratified)\n\n## Tools\n"))

    def test_binding_not_exact_at_its_base_is_refused(self) -> None:
        head = self.edit_readme("a tool.", "a tool, revised.")
        for field, value in (("sha256", "sha256:" + "0" * 64), ("bytes", 1),
                             ("gitBlobOid", "0" * 40)):
            with self.subTest(field):
                manifest = json.loads(self.raw)
                manifest["subjectFiles"][0][field] = value
                self.refused(head, manifest=manifest)

    def test_unchanged_readme_with_wrong_oid_keeps_the_exact_refusal(self) -> None:
        manifest = json.loads(self.raw)
        manifest["subjectFiles"][0]["gitBlobOid"] = "0" * 40
        self.refused(self.pin, reason="MANIFEST_BLOB_OID_MISMATCH", manifest=manifest)

    def test_other_subjects_stay_exact(self) -> None:
        self.write("tools/universal_provider_control.py", "RUNTIME = 'refuse'  # comment only\n")
        self.refused(self.commit("tools/universal_provider_control.py"))

    def test_frozen_layers_and_default_calls_stay_exact(self) -> None:
        head = self.edit_readme("a tool.", "a tool, revised.")
        with self.assertRaisesRegex(checker.ManifestError, "^MANIFEST_SUBJECT_MISMATCH$"):
            self.verify(head)
        with self.assertRaisesRegex(checker.ManifestError, "^MANIFEST_SUBJECT_MISMATCH$"):
            self.verify(head, claim_scoped=False)

    def test_uncommitted_manifest_is_its_own_base(self) -> None:
        text = BASE_README.replace("a tool.", "a tool, staged.")
        self.write("README.md", text)
        reformatted = _render(self.subjects, indent=4)
        (self.repo / MANIFEST).write_bytes(reformatted)
        _git(self.repo, "add", "--", "README.md", MANIFEST)
        self.refused(":", raw=reformatted, manifest=json.loads(reformatted))

    def test_projection_reads_only_the_bound_claim(self) -> None:
        claims = checker._r45_readme_claims(BASE_README.encode("utf-8"))
        headings, entries, mentions = claims
        self.assertEqual(headings, 1)
        self.assertEqual([heading for heading, _ in entries], ["## Proposed amendments (not ratified)"])
        self.assertEqual(len(entries[0][1]), 3)
        self.assertEqual(mentions, ())
        with self.assertRaisesRegex(checker.ManifestError, "^MANIFEST_SUBJECT_MISMATCH$"):
            checker._r45_readme_claims(b"\xff")


class ActiveLayerScratchCommitTests(unittest.TestCase):
    """The real checker on a clone of this repository with a scratch README commit."""

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="r45-readme-scratch-")
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name) / "bus"
        head = _git(ROOT, "rev-parse", "HEAD")
        _git(ROOT, "clone", "-q", "--local", "--no-hardlinks", "--no-checkout",
             "--config", "maintenance.auto=false", "--config", "gc.auto=0", str(ROOT), str(self.repo))
        for key, value in (("core.autocrlf", "false"), ("user.name", "fixture"),
                           ("user.email", "fixture@example.invalid"), ("core.hooksPath", os.devnull),
                           ("maintenance.auto", "false"), ("gc.auto", "0")):
            _git(self.repo, "config", key, value)
        _git(self.repo, "checkout", "-q", "--detach", head)

    def run_checker(self) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, "tools/check_universal_manifest.py", "--treeish", "HEAD"],
                              cwd=self.repo, env=CLEAN_ENV, capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=600)

    def commit_readme(self, text: str) -> None:
        (self.repo / "README.md").write_bytes(text.encode("utf-8"))
        _git(self.repo, "add", "--", "README.md")
        _git(self.repo, "commit", "-q", "-m", "scratch README edit")

    def test_unrelated_readme_commit_passes_and_bound_claim_edit_is_refused(self) -> None:
        readme = (self.repo / "README.md").read_bytes().decode("utf-8")
        self.commit_readme(readme + "\n<!-- scratch: unrelated index edit -->\n")
        passed = self.run_checker()
        self.assertEqual(passed.returncode, 0, passed.stderr)
        self.assertIn("r45_subjects=7 self=PASS", passed.stdout)
        anchor = "- [`specs/fleet-universal-provider-control-reconciliation.md`]"
        self.assertIn(anchor, readme)
        tampered = (self.repo / "README.md").read_bytes().decode("utf-8").replace(
            anchor, anchor + " RATIFIED", 1)
        self.commit_readme(tampered)
        refused = self.run_checker()
        self.assertEqual(refused.returncode, 1)
        self.assertEqual(refused.stderr.strip(), "MANIFEST_SUBJECT_MISMATCH")


if __name__ == "__main__":
    unittest.main()
