import importlib.util
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "reference" / "classify_launcher_candidates.py"
SPEC = importlib.util.spec_from_file_location("classify_launcher_candidates", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class LauncherCandidateClassifierTests(unittest.TestCase):
    def _classify(self, files: dict[str, str]) -> dict[str, object]:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name, text in files.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
            return MODULE.classify_tree(root)

    def test_detects_variable_bound_deadman_launch(self):
        result = self._classify(
            {"deadman.ps1": "$cfg = @{ Runner='claude.exe' }\nStart-Process -FilePath $cfg.Runner\n"}
        )
        self.assertEqual(result["classificationCounts"], {"INDIRECT_VARIABLE": 1})
        self.assertEqual(result["unresolvedCount"], 1)

    def test_separates_direct_registration_and_reference(self):
        result = self._classify(
            {
                "direct.sh": "exec kimi --print\n",
                "register.ps1": "$runner='codex.exe'\nRegister-ScheduledTask -TaskName sample\n",
                "notes.py": "PROVIDER = 'anthropic'\n",
            }
        )
        self.assertEqual(
            result["classificationCounts"],
            {"DIRECT_STATIC": 1, "REFERENCE_ONLY": 1, "REGISTRATION_SURFACE": 1},
        )
        self.assertEqual(result["unresolvedCount"], 1)

    def test_output_is_deterministic_and_excludes_tmp(self):
        files = {"b.py": "# claude\n", "a.py": "# kimi\n", "tmp/ignored.py": "exec grok --run\n"}
        first = self._classify(files)
        second = self._classify(files)
        self.assertEqual(
            [(row["path"], row["sha256"]) for row in first["candidates"]],
            [(row["path"], row["sha256"]) for row in second["candidates"]],
        )
        self.assertEqual([row["path"] for row in first["candidates"]], ["a.py", "b.py"])


if __name__ == "__main__":
    unittest.main()
