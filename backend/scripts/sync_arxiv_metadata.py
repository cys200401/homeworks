from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.db import get_connection

DEFAULT_CATEGORIES = ("cs.AI", "cs.CL", "cs.CV", "cs.IR", "cs.LG", "cs.RO")
DEFAULT_LIMIT_PER_CATEGORY = 200
DEFAULT_LOOKBACK_DAYS = 2
DEFAULT_RETENTION_DAYS = 180
DEFAULT_EXPAND_STEP_DAYS = 2
DEFAULT_MAX_EXPANSIONS = 1


def load_crawler_module():
    crawler_path = ROOT / ".qwen" / "skills" / "daily-paper" / "crawler.py"
    spec = importlib.util.spec_from_file_location("daily_paper_crawler", crawler_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load crawler module from {crawler_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def merge_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}

    for record in records:
        arxiv_id = record["arxiv_id"]
        if arxiv_id not in merged:
            merged[arxiv_id] = {
                **record,
                "categories": list(record.get("categories", [])),
            }
            continue

        existing = merged[arxiv_id]
        combined_categories = list(
            dict.fromkeys([*existing.get("categories", []), *record.get("categories", [])]),
        )
        existing["categories"] = combined_categories
        if record.get("published_at") and record["published_at"] > existing.get("published_at", ""):
            existing["published_at"] = record["published_at"]
            existing["published"] = record.get("published", existing.get("published"))

    return sorted(
        merged.values(),
        key=lambda item: item.get("published_at") or item.get("published", ""),
        reverse=True,
    )


def collect_records_with_auto_expand(
    crawler,
    categories: list[str],
    end_day: date,
    limit_per_category: int,
    lookback_days: int,
    page_size: int,
    timeout: int,
    retries: int,
    request_interval: float,
    expand_step_days: int = DEFAULT_EXPAND_STEP_DAYS,
    max_expansions: int = DEFAULT_MAX_EXPANSIONS,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    normalized_lookback_days = max(int(lookback_days), 1)
    normalized_expand_step_days = max(int(expand_step_days), 1)
    normalized_max_expansions = max(int(max_expansions), 0)
    search_attempts: list[dict[str, Any]] = []

    for attempt in range(normalized_max_expansions + 1):
        current_lookback_days = normalized_lookback_days + (attempt * normalized_expand_step_days)
        start_day = end_day - timedelta(days=max(current_lookback_days - 1, 0))
        all_records: list[dict[str, Any]] = []

        for category in categories:
            print(
                f"syncing category={category} window={start_day.isoformat()}..{end_day.isoformat()} "
                f"limit={limit_per_category} attempt={attempt + 1}",
                flush=True,
            )
            category_records = crawler.collect_records(
                start_date=start_day.isoformat(),
                end_date=end_day.isoformat(),
                limit=limit_per_category,
                category=category,
                workers=1,
                page_size=page_size,
                timeout=timeout,
                retries=retries,
                request_interval=request_interval,
            )
            all_records.extend(category_records)

        search_attempts.append(
            {
                "attempt": attempt + 1,
                "lookbackDays": current_lookback_days,
                "startDate": start_day.isoformat(),
                "endDate": end_day.isoformat(),
                "rawRecords": len(all_records),
            }
        )

        if all_records or attempt == normalized_max_expansions:
            return all_records, search_attempts

        print(
            "no arxiv records found for requested window; "
            f"expanding search by {normalized_expand_step_days} days and retrying",
            flush=True,
        )

    return [], search_attempts


def persist_records(
    records: list[dict[str, Any]],
    retention_days: int,
) -> tuple[int, int]:
    inserted_or_updated = 0
    deleted = 0

    with get_connection() as connection:
        with connection.cursor() as cursor:
            for record in records:
                published_at = record.get("published_at") or f"{record['published']}T00:00:00Z"
                cursor.execute(
                    """
                    insert into arxiv_papers (
                      arxiv_id,
                      title,
                      authors_json,
                      abstract,
                      categories_json,
                      arxiv_url,
                      published_at,
                      first_seen_at,
                      last_seen_at,
                      source
                    )
                    values (
                      %s,
                      %s,
                      %s::jsonb,
                      %s,
                      %s::jsonb,
                      %s,
                      %s,
                      now(),
                      now(),
                      'arxiv'
                    )
                    on conflict (arxiv_id)
                    do update set
                      title = excluded.title,
                      authors_json = excluded.authors_json,
                      abstract = excluded.abstract,
                      categories_json = excluded.categories_json,
                      arxiv_url = excluded.arxiv_url,
                      published_at = excluded.published_at,
                      last_seen_at = now(),
                      source = excluded.source
                    """,
                    (
                        record["arxiv_id"],
                        record["title"],
                        json.dumps(record.get("authors", []), ensure_ascii=True),
                        record["abstract"],
                        json.dumps(record.get("categories", []), ensure_ascii=True),
                        record["arxiv_url"],
                        published_at,
                    ),
                )
                inserted_or_updated += 1

            cursor.execute(
                """
                delete from arxiv_papers
                where published_at < %s - (%s * interval '1 day')
                """,
                (datetime.now(UTC), retention_days),
            )
            deleted = cursor.rowcount
        connection.commit()

    return inserted_or_updated, deleted


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="抓取最近的 arXiv AI 元数据并同步到 PostgreSQL。")
    parser.add_argument(
        "--categories",
        default=",".join(DEFAULT_CATEGORIES),
        help="逗号分隔的 arXiv 分类列表",
    )
    parser.add_argument(
        "--limit-per-category",
        type=int,
        default=DEFAULT_LIMIT_PER_CATEGORY,
        help="每个分类的抓取上限",
    )
    parser.add_argument(
        "--lookback-days",
        type=int,
        default=DEFAULT_LOOKBACK_DAYS,
        help="抓取近几天的元数据，默认 2 天",
    )
    parser.add_argument(
        "--retention-days",
        type=int,
        default=DEFAULT_RETENTION_DAYS,
        help="保留元数据的天数，默认 180 天",
    )
    parser.add_argument("--timeout", type=int, default=30, help="请求超时秒数")
    parser.add_argument("--retries", type=int, default=4, help="重试次数")
    parser.add_argument(
        "--request-interval",
        type=float,
        default=3.0,
        help="arXiv API 请求间隔",
    )
    parser.add_argument(
        "--page-size",
        type=int,
        default=200,
        help="单次 API 请求拉取上限",
    )
    parser.add_argument(
        "--end-date",
        default=date.today().isoformat(),
        help="结束日期，格式 YYYY-MM-DD",
    )
    parser.add_argument(
        "--expand-step-days",
        type=int,
        default=DEFAULT_EXPAND_STEP_DAYS,
        help="首轮无结果时，第二轮向前额外扩大的天数，默认 2 天",
    )
    parser.add_argument(
        "--max-expansions",
        type=int,
        default=DEFAULT_MAX_EXPANSIONS,
        help="首轮无结果后最多自动扩窗重试几次，默认 1 次",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    crawler = load_crawler_module()
    categories = [item.strip() for item in args.categories.split(",") if item.strip()]
    if not categories:
        raise SystemExit("No categories configured. Pass --categories with at least one arXiv category.")
    end_day = date.fromisoformat(args.end_date)
    all_records, search_attempts = collect_records_with_auto_expand(
        crawler=crawler,
        categories=categories,
        end_day=end_day,
        limit_per_category=args.limit_per_category,
        lookback_days=args.lookback_days,
        page_size=args.page_size,
        timeout=args.timeout,
        retries=args.retries,
        request_interval=args.request_interval,
        expand_step_days=args.expand_step_days,
        max_expansions=args.max_expansions,
    )

    merged_records = merge_records(all_records)
    inserted_or_updated, deleted = persist_records(
        records=merged_records,
        retention_days=args.retention_days,
    )

    final_window = (
        f"{search_attempts[-1]['startDate']}..{search_attempts[-1]['endDate']}"
        if search_attempts
        else f"{end_day.isoformat()}..{end_day.isoformat()}"
    )
    print(
        "arxiv metadata sync completed: "
        f"raw={len(all_records)} unique={len(merged_records)} upserted={inserted_or_updated} "
        f"deleted={deleted} attempts={len(search_attempts)} final_window={final_window}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
