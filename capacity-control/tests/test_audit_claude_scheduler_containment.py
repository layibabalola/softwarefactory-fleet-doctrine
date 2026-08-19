import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


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

    def test_other_project_enabled_task_fails_runtime_containment(self):
        result = self._audit(
            {"coworkScheduledTasksEnabled": False, "ccdScheduledTasksEnabled": False},
            [{"id": "cloudvore-warden", "enabled": True, "filePath": "prompt.md"}],
        )
        self.assertEqual(result["status"], "UNCONTAINED_ZERO_AUTHORITY")
        self.assertIn("GLOBAL_TASK_ENABLED", result["reasons"])
        self.assertEqual(result["globallyEnabledTasks"][0]["id"], "cloudvore-warden")

    def test_unpublishable_preference_and_task_values_are_refused_without_echo(self):
        private = "C:/private/token"
        with self.assertRaisesRegex(ValueError, "PREFERENCE_SCHEMA"):
            self._audit(
                {"coworkScheduledTasksEnabled": {"secret": private}, "ccdScheduledTasksEnabled": False},
                [],
            )
        with self.assertRaisesRegex(ValueError, "TASK_SCHEMA"):
            self._audit(
                {"coworkScheduledTasksEnabled": False, "ccdScheduledTasksEnabled": False},
                [{"id": private, "enabled": True, "filePath": "prompt.md"}],
            )

    def test_duplicate_json_keys_are_refused(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = root / "config.json"
            store = root / "scheduled-tasks.json"
            config.write_text('{"preferences":{"coworkScheduledTasksEnabled":false,"coworkScheduledTasksEnabled":false}}', encoding="utf-8")
            store.write_text('{"tasks":[]}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "DUPLICATE_JSON_KEY"):
                MODULE.audit(config, [store])

    def test_oversize_json_is_refused_before_read(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "large.json"
            with path.open("wb") as stream:
                stream.truncate(MODULE.MAX_JSON_BYTES + 1)
            with self.assertRaisesRegex(ValueError, "JSON_TOO_LARGE"):
                MODULE._strict_json(path)

    def test_deep_json_is_refused_before_parser_allocation(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "deep.json"
            path.write_bytes(b"[" * (MODULE.MAX_JSON_DEPTH + 1) + b"0" + b"]" * (MODULE.MAX_JSON_DEPTH + 1))
            with mock.patch.object(MODULE.json, "loads", side_effect=AssertionError("parser must not run")):
                with self.assertRaisesRegex(ValueError, "JSON_SHAPE_LIMIT"):
                    MODULE._strict_json(path)

    def test_task_tree_and_path_bounds_fail_closed(self):
        nested: object = {"leaf": True}
        for _ in range(MODULE.MAX_JSON_DEPTH + 1):
            nested = {"child": nested}
        with self.assertRaisesRegex(ValueError, "TASK_TREE_LIMIT"):
            list(MODULE._task_objects(nested))
        with self.assertRaisesRegex(ValueError, "TASK_PATH_LIMIT"):
            MODULE.audit(Path("config"), [Path("task")] * (MODULE.MAX_TASK_PATHS + 1))

    def test_task_count_limit_is_global_across_stores(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary); config=root/"config.json"
            config.write_text(json.dumps({"preferences":{"coworkScheduledTasksEnabled":False,"ccdScheduledTasksEnabled":False}}),encoding="utf-8")
            stores=[]
            for index in range(2):
                store=root/f"tasks-{index}.json"
                store.write_text(json.dumps({"tasks":[{"id":f"task-{index}","enabled":False,"filePath":"prompt.md"}]}),encoding="utf-8")
                stores.append(store)
            with mock.patch.object(MODULE,"MAX_TASK_OBJECTS",1), self.assertRaisesRegex(ValueError,"TASK_COUNT_LIMIT"):
                MODULE.audit(config,stores)

    def test_cli_error_is_stable_and_does_not_echo_private_details(self):
        stderr = io.StringIO()
        with mock.patch.object(sys, "argv", ["audit", "--config", "private", "--tasks", "private"]), \
             mock.patch.object(MODULE, "audit", side_effect=OSError("C:/secret/token")), \
             contextlib.redirect_stderr(stderr):
            self.assertEqual(MODULE.main(), 2)
        self.assertEqual(stderr.getvalue(), "ERROR audit_claude_scheduler_containment: INPUT_REFUSED\n")


if __name__ == "__main__":
    unittest.main()
