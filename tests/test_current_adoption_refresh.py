import copy
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from contextlib import redirect_stdout
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("refresh", ROOT / "tools/refresh_current_adoption_census.py")
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)


class RefreshTests(unittest.TestCase):
    def test_changed_control_refuses_before_loading_checker_or_emitting_json(self):
        with tempfile.TemporaryDirectory(prefix='r26-refresh-control-') as tmp:
            repo = Path(tmp) / 'repo'
            def git(*args):
                return subprocess.run(['git', '--no-optional-locks', *args], cwd=repo if repo.exists() else ROOT,
                                      check=True, capture_output=True)
            git('clone', '--local', '--no-checkout', str(ROOT), str(repo))
            git('config', 'core.autocrlf', 'false')
            git('checkout', '--detach', R.E.git('rev-parse', 'HEAD').decode().strip())
            checker = repo / 'tools/check_adoption_ledger.py'
            checker.write_bytes(checker.read_bytes() + b'\n# unreviewed control mutation\n')
            result = subprocess.run([sys.executable, 'tools/refresh_current_adoption_census.py'],
                                    cwd=repo, capture_output=True, text=True, timeout=120)
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn('CONTROL_WORKTREE_DRIFT', result.stderr)
            self.assertEqual(result.stdout, '', 'refused controls must never emit candidate JSON')

            git('checkout', '--', 'tools/check_adoption_ledger.py')
            frozen = repo / 'adoption/universal-token-control-r26.json'
            frozen.write_bytes(frozen.read_bytes() + b'\n')
            git('add', '--', 'adoption/universal-token-control-r26.json')
            git('-c', 'user.name=Refresh fixture', '-c', 'user.email=fixture@example.invalid',
                '-c', 'core.hooksPath=/dev/null', 'commit', '-m', 'Fixture historical artifact mutation')
            result = subprocess.run([sys.executable, 'tools/refresh_current_adoption_census.py'],
                                    cwd=repo, capture_output=True, text=True, timeout=120)
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn('HISTORICAL_ARTIFACT_CHANGED', result.stderr)
            self.assertEqual(result.stdout, '', 'refused frozen artifacts must never emit candidate JSON')

    def test_actual_refresh_verifies_current_evidence_without_writing(self):
        path = ROOT / R.E.CURRENT_LEDGER
        before = path.read_bytes()
        refreshed = R.refreshed_census()
        prior = json.loads(R.E.blob("HEAD", R.E.CURRENT_LEDGER))
        self.assertEqual(before, path.read_bytes())
        expected = copy.deepcopy(refreshed)
        expected['census']['baseCommit'] = prior['census']['baseCommit']
        for new, old in zip(expected['projects'], prior['projects'], strict=True):
            for key in ('commit', 'gitBlobOid'):
                new['evidence'][key] = old['evidence'][key]
        self.assertEqual(expected, prior, 'refresh must preserve every disposition/proof/population field')

    def test_claim_failure_emits_no_candidate_json(self):
        module = R.E.load('adoption_ledger')
        with mock.patch.object(module, 'verify_ledger', side_effect=ValueError('DISPOSITION_CHANGED')), mock.patch.object(R.E, 'load', return_value=module), mock.patch.object(R.E, 'verify_history'), redirect_stdout(io.StringIO()) as output:
            with self.assertRaisesRegex(ValueError, 'DISPOSITION_CHANGED'):
                R.refreshed_census()
        self.assertEqual(output.getvalue(), '')

    def test_head_move_refuses_before_output(self):
        original = R.E.git
        heads = 0
        def moved(*args, **kwargs):
            nonlocal heads
            if args == ('rev-parse', 'HEAD'):
                heads += 1
                if heads == 2:
                    return b'0' * 40
            return original(*args, **kwargs)
        with mock.patch.object(R.E, 'git', side_effect=moved), redirect_stdout(io.StringIO()) as output:
            with self.assertRaisesRegex(R.E.IntakeError, 'REFRESH_HEAD_MOVED'):
                R.refreshed_census()
        self.assertEqual(output.getvalue(), '')


if __name__ == '__main__':
    unittest.main()
