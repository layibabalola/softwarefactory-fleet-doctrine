import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "reference" / "audit_claude_scheduler_containment.py"
SPEC = importlib.util.spec_from_file_location("audit_claude_scheduler_containment", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class ClaudeSchedulerContainmentAuditTests(unittest.TestCase):
    def _audit(self, preferences: dict[str, bool], tasks: list[dict[str, object]]) -> dict[str, object]:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = root / "config.json"
            store = root / "scheduled-tasks.json"
            config.write_text(json.dumps({"preferences": preferences}), encoding="utf-8")
            store.write_text(json.dumps({"tasks": tasks}), encoding="utf-8")
            return MODULE.audit(config, [store])

    def test_closed_preferences_and_disabled_project_task_are_zero_authority(self):
        result = self._audit(
            {"coworkScheduledTasksEnabled": False, "ccdScheduledTasksEnabled": False},
            [{"id": "conjugal-fable", "enabled": False, "filePath": "prompt.md"}],
        )
        self.assertEqual(result["status"], "CLOSED_ON_DISK_HOT_RELOAD_UNPROVEN")
        self.assertEqual(result["authority"], "NONE")

    def test_true_preference_fails_closed(self):
        result = self._audit(
            {"coworkScheduledTasksEnabled": True, "ccdScheduledTasksEnabled": False},
            [{"id": "conjugal-fable", "enabled": False, "filePath": "prompt.md"}],
        )
        self.assertEqual(result["status"], "UNCONTAINED_ZERO_AUTHORITY")
        self.assertIn("GLOBAL_PREFERENCES_NOT_FALSE", result["reasons"])

    def test_enabled_project_task_fails_even_with_global_preferences_false(self):
        result = self._audit(
            {"coworkScheduledTasksEnabled": False, "ccdScheduledTasksEnabled": False},
            [{"id": "conjugal-opus", "enabled": True, "cronExpression": "*/5 * * * *"}],
        )
        self.assertIn("PROJECT_TASK_ENABLED", result["reasons"])
        self.assertEqual(result["globallyEnabledTaskCount"], 1)

    def test_other_project_enabled_task_is_reported_without_opening_local_status(self):
        result = self._audit(
            {"coworkScheduledTasksEnabled": False, "ccdScheduledTasksEnabled": False},
            [{"id": "cloudvore-warden", "enabled": True, "filePath": "prompt.md"}],
        )
        self.assertEqual(result["status"], "CLOSED_ON_DISK_HOT_RELOAD_UNPROVEN")
        self.assertEqual(result["globallyEnabledTasks"][0]["id"], "cloudvore-warden")

    def test_duplicate_json_keys_are_refused(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = root / "config.json"
            store = root / "scheduled-tasks.json"
            config.write_text('{"preferences":{"coworkScheduledTasksEnabled":false,"coworkScheduledTasksEnabled":false}}', encoding="utf-8")
            store.write_text('{"tasks":[]}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "DUPLICATE_JSON_KEY"):
                MODULE.audit(config, [store])


if __name__ == "__main__":
    unittest.main()
