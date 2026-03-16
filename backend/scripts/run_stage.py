from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.db import get_connection
from app.models import PIPELINE_STAGES


@dataclass
class StageCounts:
    success_count: int
    failed_count: int
    skipped_count: int
    notes: str | None = None


class Recorder(Protocol):
    def start_run(self, stage: str, command: list[str], started_at: datetime) -> str | None: ...

    def finish_run(
        self,
        run_id: str | None,
        stage: str,
        command: list[str],
        exit_code: int,
        started_at: datetime,
        finished_at: datetime,
        stdout_text: str,
        stderr_text: str,
    ) -> None: ...

    def record_error(
        self,
        run_id: str | None,
        stage: str,
        command: list[str],
        exit_code: int,
        stdout_text: str,
        stderr_text: str,
    ) -> None: ...


def warn_monitoring(message: str) -> None:
    sys.stderr.write(f"[run_stage warning] {message}\n")
    sys.stderr.flush()


def _forward_output(
    stream: subprocess.Popen[str] | None,
    writer,
    chunks: list[str],
) -> None:
    if stream is None:
        return

    pipe = stream
    while True:
        line = pipe.readline()
        if not line:
            break
        writer.write(line)
        writer.flush()
        chunks.append(line)

    pipe.close()


def stream_command(command: list[str]) -> tuple[int, str, str]:
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )

    stdout_chunks: list[str] = []
    stderr_chunks: list[str] = []

    stdout_thread = threading.Thread(
        target=_forward_output,
        args=(process.stdout, sys.stdout, stdout_chunks),
        daemon=True,
    )
    stderr_thread = threading.Thread(
        target=_forward_output,
        args=(process.stderr, sys.stderr, stderr_chunks),
        daemon=True,
    )

    stdout_thread.start()
    stderr_thread.start()
    stdout_thread.join()
    stderr_thread.join()

    exit_code = process.wait()
    return exit_code, "".join(stdout_chunks), "".join(stderr_chunks)


def infer_stage_counts(
    stage: str,
    exit_code: int,
    stdout_text: str,
    stderr_text: str,
) -> StageCounts:
    combined_output = f"{stdout_text}\n{stderr_text}"

    if stage == "crawler":
        match = re.search(
            r"抓取完成：原始记录\s*(\d+)\s*篇，去重后\s*(\d+)\s*篇，输出\s*(\d+)\s*篇",
            combined_output,
        )
        if match:
            deduplicated = int(match.group(2))
            emitted = int(match.group(3))
            return StageCounts(
                success_count=emitted,
                failed_count=0 if exit_code == 0 else 1,
                skipped_count=max(deduplicated - emitted, 0),
                notes=match.group(0),
            )

    if stage == "download_pdf":
        match = re.search(
            r"PDF 下载完成：成功\s*(\d+)，跳过\s*(\d+)，失败\s*(\d+)",
            combined_output,
        )
        if match:
            return StageCounts(
                success_count=int(match.group(1)),
                skipped_count=int(match.group(2)),
                failed_count=int(match.group(3)),
                notes=match.group(0),
            )

    if stage == "pdf_to_txt":
        match = re.search(
            r"文本提取完成：成功\s*(\d+)，跳过\s*(\d+)，失败\s*(\d+)",
            combined_output,
        )
        if match:
            return StageCounts(
                success_count=int(match.group(1)),
                skipped_count=int(match.group(2)),
                failed_count=int(match.group(3)),
                notes=match.group(0),
            )

    if stage == "frontend_build":
        return StageCounts(
            success_count=1 if exit_code == 0 else 0,
            failed_count=0 if exit_code == 0 else 1,
            skipped_count=0,
        )

    return StageCounts(
        success_count=1 if exit_code == 0 else 0,
        failed_count=0 if exit_code == 0 else 1,
        skipped_count=0,
    )


class DatabaseRecorder:
    def start_run(self, stage: str, command: list[str], started_at: datetime) -> str | None:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    insert into pipeline_runs (
                      run_date,
                      stage,
                      status,
                      params_json,
                      started_at
                    )
                    values (%s, %s, %s, %s::jsonb, %s)
                    returning id::text as id
                    """,
                    (
                        started_at.date(),
                        stage,
                        "running",
                        json.dumps({"command": command}, ensure_ascii=True),
                        started_at,
                    ),
                )
                row = cursor.fetchone()
                connection.commit()
                return row["id"] if row else None

    def finish_run(
        self,
        run_id: str | None,
        stage: str,
        command: list[str],
        exit_code: int,
        started_at: datetime,
        finished_at: datetime,
        stdout_text: str,
        stderr_text: str,
    ) -> None:
        counts = infer_stage_counts(stage, exit_code, stdout_text, stderr_text)
        status = "succeeded" if exit_code == 0 else "failed"
        duration_ms = int((finished_at - started_at).total_seconds() * 1000)
        params_json = json.dumps({"command": command}, ensure_ascii=True)

        with get_connection() as connection:
            with connection.cursor() as cursor:
                if run_id:
                    cursor.execute(
                        """
                        update pipeline_runs
                        set
                          status = %s,
                          success_count = %s,
                          failed_count = %s,
                          skipped_count = %s,
                          finished_at = %s,
                          duration_ms = %s,
                          notes = %s,
                          params_json = %s::jsonb
                        where id = %s::uuid
                        """,
                        (
                            status,
                            counts.success_count,
                            counts.failed_count,
                            counts.skipped_count,
                            finished_at,
                            duration_ms,
                            counts.notes,
                            params_json,
                            run_id,
                        ),
                    )
                else:
                    cursor.execute(
                        """
                        insert into pipeline_runs (
                          run_date,
                          stage,
                          status,
                          params_json,
                          success_count,
                          failed_count,
                          skipped_count,
                          started_at,
                          finished_at,
                          duration_ms,
                          notes
                        )
                        values (%s, %s, %s, %s::jsonb, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            started_at.date(),
                            stage,
                            status,
                            params_json,
                            counts.success_count,
                            counts.failed_count,
                            counts.skipped_count,
                            started_at,
                            finished_at,
                            duration_ms,
                            counts.notes,
                        ),
                    )
                connection.commit()

    def record_error(
        self,
        run_id: str | None,
        stage: str,
        command: list[str],
        exit_code: int,
        stdout_text: str,
        stderr_text: str,
    ) -> None:
        error_message = stderr_text.strip() or f"Command exited with code {exit_code}"
        raw_context = json.dumps(
            {
                "command": command,
                "stdout": stdout_text[-4000:],
                "stderr": stderr_text[-4000:],
            },
            ensure_ascii=True,
        )

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    insert into run_errors (
                      pipeline_run_id,
                      stage,
                      error_code,
                      error_message,
                      raw_context
                    )
                    values (%s::uuid, %s, %s, %s, %s::jsonb)
                    """,
                    (
                        run_id,
                        stage,
                        f"exit_{exit_code}",
                        error_message,
                        raw_context,
                    ),
                )
                connection.commit()


def execute_stage(
    stage: str,
    command: list[str],
    recorder: Recorder | None = None,
    runner=stream_command,
) -> int:
    active_recorder = recorder or DatabaseRecorder()
    started_at = datetime.now(timezone.utc)
    run_id: str | None = None

    try:
        run_id = active_recorder.start_run(stage=stage, command=command, started_at=started_at)
    except Exception as exc:  # noqa: BLE001
        warn_monitoring(f"failed to start monitoring for {stage}: {exc}")

    exit_code, stdout_text, stderr_text = runner(command)
    finished_at = datetime.now(timezone.utc)

    try:
        active_recorder.finish_run(
            run_id=run_id,
            stage=stage,
            command=command,
            exit_code=exit_code,
            started_at=started_at,
            finished_at=finished_at,
            stdout_text=stdout_text,
            stderr_text=stderr_text,
        )
    except Exception as exc:  # noqa: BLE001
        warn_monitoring(f"failed to finish monitoring for {stage}: {exc}")

    if exit_code != 0:
        try:
            active_recorder.record_error(
                run_id=run_id,
                stage=stage,
                command=command,
                exit_code=exit_code,
                stdout_text=stdout_text,
                stderr_text=stderr_text,
            )
        except Exception as exc:  # noqa: BLE001
            warn_monitoring(f"failed to record error for {stage}: {exc}")

    return exit_code


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a pipeline stage while writing fail-open monitoring rows.",
    )
    parser.add_argument("--stage", required=True, choices=PIPELINE_STAGES)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    command = args.command
    if command and command[0] == "--":
        command = command[1:]

    if not command:
        raise SystemExit("Missing command. Pass it after --.")

    return execute_stage(stage=args.stage, command=command)


if __name__ == "__main__":
    raise SystemExit(main())
