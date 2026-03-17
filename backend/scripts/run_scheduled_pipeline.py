from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Callable

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from backend.scripts.run_stage import execute_stage


StageRunner = Callable[[str, list[str]], int]


def build_metadata_command(args: argparse.Namespace) -> list[str]:
    command = [sys.executable, str(WORKSPACE_ROOT / "backend" / "scripts" / "sync_arxiv_metadata.py")]

    option_map = [
        ("metadata_categories", "--categories"),
        ("metadata_limit_per_category", "--limit-per-category"),
        ("metadata_lookback_days", "--lookback-days"),
        ("metadata_retention_days", "--retention-days"),
        ("metadata_timeout", "--timeout"),
        ("metadata_retries", "--retries"),
        ("metadata_request_interval", "--request-interval"),
        ("metadata_page_size", "--page-size"),
        ("metadata_end_date", "--end-date"),
        ("metadata_expand_step_days", "--expand-step-days"),
        ("metadata_max_expansions", "--max-expansions"),
    ]

    for attribute, flag in option_map:
        value = getattr(args, attribute)
        if value is None:
            continue
        command.extend([flag, str(value)])

    return command


def build_delivery_command() -> list[str]:
    return [sys.executable, str(WORKSPACE_ROOT / "backend" / "scripts" / "run_due_deliveries.py")]


def run_pipeline(args: argparse.Namespace, stage_runner: StageRunner | None = None) -> int:
    runner = stage_runner or (lambda stage, command: execute_stage(stage=stage, command=command))
    overall_exit_code = 0

    if not args.skip_sync:
        metadata_exit_code = runner("metadata_sync", build_metadata_command(args))
        if metadata_exit_code != 0:
            overall_exit_code = metadata_exit_code
            if not args.continue_on_sync_failure:
                return overall_exit_code

    if not args.skip_deliveries:
        delivery_exit_code = runner("personalized_delivery", build_delivery_command())
        if delivery_exit_code != 0 and overall_exit_code == 0:
            overall_exit_code = delivery_exit_code

    return overall_exit_code


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run metadata sync and personalized delivery in one scheduled pipeline.",
    )
    parser.add_argument("--skip-sync", action="store_true", help="只执行个性化投送，不跑元数据同步")
    parser.add_argument("--skip-deliveries", action="store_true", help="只执行元数据同步，不跑用户投送")
    parser.add_argument(
        "--continue-on-sync-failure",
        action="store_true",
        help="元数据同步失败时仍继续跑个性化投送，但最终仍返回失败退出码",
    )
    parser.add_argument("--metadata-categories", default=None, help="透传给 sync_arxiv_metadata.py 的分类列表")
    parser.add_argument("--metadata-limit-per-category", type=int, default=None)
    parser.add_argument("--metadata-lookback-days", type=int, default=None)
    parser.add_argument("--metadata-retention-days", type=int, default=None)
    parser.add_argument("--metadata-timeout", type=int, default=None)
    parser.add_argument("--metadata-retries", type=int, default=None)
    parser.add_argument("--metadata-request-interval", type=float, default=None)
    parser.add_argument("--metadata-page-size", type=int, default=None)
    parser.add_argument("--metadata-end-date", default=None)
    parser.add_argument("--metadata-expand-step-days", type=int, default=None)
    parser.add_argument("--metadata-max-expansions", type=int, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.skip_sync and args.skip_deliveries:
        raise SystemExit("Nothing to run. Remove --skip-sync or --skip-deliveries.")
    return run_pipeline(args)


if __name__ == "__main__":
    raise SystemExit(main())
