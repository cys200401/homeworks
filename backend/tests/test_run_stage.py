from __future__ import annotations

import io
import sys
import types
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

fake_app = types.ModuleType("app")
fake_app.__path__ = []  # type: ignore[attr-defined]
fake_app_db = types.ModuleType("app.db")
fake_app_models = types.ModuleType("app.models")


def _unused_get_connection():
    raise AssertionError("database access should be stubbed in unit tests")


fake_app_db.get_connection = _unused_get_connection  # type: ignore[attr-defined]
fake_app_models.PIPELINE_STAGES = (
    "crawler",
    "download_pdf",
    "pdf_to_txt",
    "report_write",
    "frontend_build",
)  # type: ignore[attr-defined]

sys.modules.setdefault("app", fake_app)
sys.modules["app.db"] = fake_app_db
sys.modules["app.models"] = fake_app_models

from backend.scripts.run_stage import execute_stage, stream_command  # type: ignore[attr-defined]


class RunStageTests(unittest.TestCase):
    def test_stream_command_passthroughs_stdout_stderr_and_exit_code(self) -> None:
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()

        command = [
            sys.executable,
            "-c",
            (
                "import sys; "
                "print('stdout-line'); "
                "print('stderr-line', file=sys.stderr); "
                "raise SystemExit(7)"
            ),
        ]

        with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
            exit_code, captured_stdout, captured_stderr = stream_command(command)

        self.assertEqual(exit_code, 7)
        self.assertIn("stdout-line", stdout_buffer.getvalue())
        self.assertIn("stderr-line", stderr_buffer.getvalue())
        self.assertIn("stdout-line", captured_stdout)
        self.assertIn("stderr-line", captured_stderr)

    def test_execute_stage_is_fail_open_when_monitoring_write_fails(self) -> None:
        warnings = io.StringIO()

        def fake_runner(_command: list[str]) -> tuple[int, str, str]:
            return 3, "ok-output", "bad-output"

        class BrokenRecorder:
            def start_run(self, *_args, **_kwargs) -> str | None:
                raise RuntimeError("db down")

            def finish_run(self, *_args, **_kwargs) -> None:
                raise RuntimeError("db down")

            def record_error(self, *_args, **_kwargs) -> None:
                raise RuntimeError("db down")

        with redirect_stderr(warnings):
            exit_code = execute_stage(
                stage="crawler",
                command=["python", "crawler.py"],
                recorder=BrokenRecorder(),
                runner=fake_runner,
            )

        self.assertEqual(exit_code, 3)
        self.assertIn("warning", warnings.getvalue().lower())


if __name__ == "__main__":
    unittest.main()
