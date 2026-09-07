import copy
import importlib.util
import io
import json
from pathlib import Path
from contextlib import redirect_stdout
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("refresh", ROOT / "tools/refresh_current_adoption_census.py")
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)


class RefreshTests(unittest.TestCase):
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
        with mock.patch.object(module, 'verify_ledger', side_effect=ValueError('DISPOSITION_CHANGED')), mock.patch.object(R.E, 'load', return_value=module), redirect_stdout(io.StringIO()) as output:
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
