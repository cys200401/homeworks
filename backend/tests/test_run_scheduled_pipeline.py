from __future__ import annotations

import argparse
import sys
import types
import unittest

fake_scripts = types.ModuleType("scripts")
fake_scripts.__path__ = []  # type: ignore[attr-defined]
fake_run_stage = types.ModuleType("scripts.run_stage")


def _unused_execute_stage(*_args, **_kwargs) -> int:
    raise AssertionError("execute_stage should be stubbed in unit tests")


fake_run_stage.execute_stage = _unused_execute_stage  # type: ignore[attr-defined]
sys.modules.setdefault("scripts", fake_scripts)
sys.modules.setdefault("scripts.run_stage", fake_run_stage)

from backend.scripts.run_scheduled_pipeline import run_pipeline

sys.modules.pop("scripts.run_stage", None)
sys.modules.pop("scripts", None)


def make_args(**overrides) -> argparse.Namespace:
    defaults = {
        "skip_sync": False,
        "skip_deliveries": False,
        "continue_on_sync_failure": False,
        "metadata_categories": None,
        "metadata_limit_per_category": None,
        "metadata_lookback_days": None,
        "metadata_retention_days": None,
        "metadata_timeout": None,
        "metadata_retries": None,
        "metadata_request_interval": None,
        "metadata_page_size": None,
        "metadata_end_date": None,
        "metadata_expand_step_days": None,
        "metadata_max_expansions": None,
    }
    defaults.update(overrides)
    return argparse.Namespace(**defaults)


class RunScheduledPipelineTests(unittest.TestCase):
    def test_run_pipeline_executes_sync_then_delivery(self) -> None:
        calls: list[tuple[str, list[str]]] = []

        def fake_runner(stage: str, command: list[str]) -> int:
            calls.append((stage, command))
            return 0

        exit_code = run_pipeline(make_args(), stage_runner=fake_runner)

        self.assertEqual(exit_code, 0)
        self.assertEqual([stage for stage, _command in calls], ["metadata_sync", "personalized_delivery"])
        self.assertTrue(calls[0][1][-1].endswith("sync_arxiv_metadata.py"))
        self.assertTrue(calls[1][1][-1].endswith("run_due_deliveries.py"))

    def test_run_pipeline_stops_when_sync_fails_by_default(self) -> None:
        calls: list[str] = []

        def fake_runner(stage: str, _command: list[str]) -> int:
            calls.append(stage)
            return 7 if stage == "metadata_sync" else 0

        exit_code = run_pipeline(make_args(), stage_runner=fake_runner)

        self.assertEqual(exit_code, 7)
        self.assertEqual(calls, ["metadata_sync"])

    def test_run_pipeline_can_continue_after_sync_failure(self) -> None:
        calls: list[str] = []

        def fake_runner(stage: str, _command: list[str]) -> int:
            calls.append(stage)
            return 5 if stage == "metadata_sync" else 0

        exit_code = run_pipeline(
            make_args(continue_on_sync_failure=True),
            stage_runner=fake_runner,
        )

        self.assertEqual(exit_code, 5)
        self.assertEqual(calls, ["metadata_sync", "personalized_delivery"])


if __name__ == "__main__":
    unittest.main()
