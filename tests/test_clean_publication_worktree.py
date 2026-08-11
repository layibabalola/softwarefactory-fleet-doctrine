import hashlib
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "new-clean-publication-worktree.ps1"


def run(*args, cwd=None, check=True):
    result = subprocess.run(args, cwd=cwd, text=True, capture_output=True)
    if check and result.returncode != 0:
        raise AssertionError(result.stdout + result.stderr)
    return result


def git(repo, *args, check=True):
    return run("git", "-C", str(repo), *args, check=check)


class CleanPublicationWorktreeTests(unittest.TestCase):
    def setUp(self):
        if not shutil.which("git") or not shutil.which("pwsh.exe"):
            self.skipTest("git and pwsh.exe are required")

    def make_repositories(self, temp):
        root = Path(temp)
        remote = root / "remote.git"
        canonical = root / "canonical"
        run("git", "init", "--bare", str(remote))
        run("git", "init", "-b", "master", str(canonical))
        git(canonical, "config", "user.email", "factory-test@example.invalid")
        git(canonical, "config", "user.name", "Factory Test")
        tracked = canonical / "RULINGS.md"
        tracked.write_text("remote base\n", encoding="utf-8")
        git(canonical, "add", "RULINGS.md")
        git(canonical, "commit", "-m", "remote base")
        git(canonical, "remote", "add", "origin", str(remote))
        git(canonical, "push", "-u", "origin", "master")
        remote_head = git(canonical, "rev-parse", "HEAD").stdout.strip()

        tracked.write_text("remote base\nlocal ahead\n", encoding="utf-8")
        git(canonical, "add", "RULINGS.md")
        git(canonical, "commit", "-m", "local ahead")
        tracked.write_text("remote base\nlocal ahead\nforeign dirty bytes\n", encoding="utf-8")
        return canonical, tracked, remote_head

    def invoke(self, canonical, remote_head, worktree, branch):
        return run(
            "pwsh.exe", "-NoLogo", "-NoProfile", "-NonInteractive",
            "-ExecutionPolicy", "Bypass", "-File", str(SCRIPT),
            "-RepoRoot", str(canonical),
            "-ExpectedRemoteHead", remote_head,
            "-Remote", "origin", "-TargetBranch", "master",
            "-WorktreePath", str(worktree), "-FeatureBranch", branch,
            check=False,
        )

    def test_ahead_dirty_canonical_is_preserved_while_clean_remote_worktree_is_created(self):
        with tempfile.TemporaryDirectory() as temp:
            canonical, tracked, remote_head = self.make_repositories(temp)
            worktree = Path(temp) / "publication"
            before_head = git(canonical, "rev-parse", "HEAD").stdout.strip()
            before_status = git(canonical, "status", "--porcelain=v1").stdout
            before_hash = hashlib.sha256(tracked.read_bytes()).hexdigest()

            result = self.invoke(canonical, remote_head, worktree, "codex/test-publication")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            receipt = json.loads(result.stdout.strip().splitlines()[-1])
            self.assertEqual(receipt["status"], "READY")
            self.assertTrue(receipt["canonicalDirty"])
            self.assertEqual(receipt["canonicalAhead"], 1)
            self.assertEqual(git(worktree, "rev-parse", "HEAD").stdout.strip(), remote_head)
            self.assertEqual(git(worktree, "status", "--porcelain=v1").stdout, "")
            self.assertEqual(git(canonical, "rev-parse", "HEAD").stdout.strip(), before_head)
            self.assertEqual(git(canonical, "status", "--porcelain=v1").stdout, before_status)
            self.assertEqual(hashlib.sha256(tracked.read_bytes()).hexdigest(), before_hash)

    def test_stale_expected_remote_head_refuses_without_creating_state(self):
        with tempfile.TemporaryDirectory() as temp:
            canonical, _, _ = self.make_repositories(temp)
            worktree = Path(temp) / "publication"
            branch = "codex/test-stale-pin"
            result = self.invoke(canonical, "0" * 40, worktree, branch)
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            receipt = json.loads(result.stdout.strip().splitlines()[-1])
            self.assertEqual(receipt["status"], "BLOCKED")
            self.assertIn("Remote target drifted", receipt["error"])
            self.assertFalse(worktree.exists())
            self.assertEqual(
                git(canonical, "show-ref", "--verify", "--quiet", f"refs/heads/{branch}", check=False).returncode,
                1,
            )


if __name__ == "__main__":
    unittest.main()
