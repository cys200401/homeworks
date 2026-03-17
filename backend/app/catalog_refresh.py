from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.personalization import normalize_categories, resolve_search_expansion
from scripts.sync_arxiv_metadata import (
    DEFAULT_LIMIT_PER_CATEGORY,
    DEFAULT_RETENTION_DAYS,
    collect_records_with_auto_expand,
    load_crawler_module,
    merge_records,
    persist_records,
)

DEFAULT_TIMEOUT_SECONDS = 30
DEFAULT_RETRIES = 4
DEFAULT_REQUEST_INTERVAL = 3.0
DEFAULT_PAGE_SIZE = 200


def compute_due_crawl_lookback_days(lookback_days: int) -> int:
    return max(int(lookback_days) + 1, 2)


def refresh_catalog_for_delivery(
    *,
    categories: list[str],
    lookback_days: int,
    reference_time: datetime,
    delivery_profile: dict[str, Any] | None = None,
    crawler=None,
    limit_per_category: int = DEFAULT_LIMIT_PER_CATEGORY,
    retention_days: int = DEFAULT_RETENTION_DAYS,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
    retries: int = DEFAULT_RETRIES,
    request_interval: float = DEFAULT_REQUEST_INTERVAL,
    page_size: int = DEFAULT_PAGE_SIZE,
) -> dict[str, Any]:
    normalized_categories = normalize_categories(categories)
    expansion_step_days, max_search_expansions = resolve_search_expansion(delivery_profile)
    active_crawler = crawler or load_crawler_module()
    crawl_lookback_days = compute_due_crawl_lookback_days(lookback_days)
    end_day = reference_time.astimezone(UTC).date()

    all_records, search_attempts = collect_records_with_auto_expand(
        crawler=active_crawler,
        categories=normalized_categories,
        end_day=end_day,
        limit_per_category=limit_per_category,
        lookback_days=crawl_lookback_days,
        page_size=page_size,
        timeout=timeout,
        retries=retries,
        request_interval=request_interval,
        expand_step_days=expansion_step_days,
        max_expansions=max_search_expansions,
    )
    merged_records = merge_records(all_records)
    inserted_or_updated, deleted = persist_records(
        records=merged_records,
        retention_days=retention_days,
    )

    return {
        "triggeredAt": reference_time.isoformat(),
        "categories": normalized_categories,
        "requestedLookbackDays": int(lookback_days),
        "crawlLookbackDays": crawl_lookback_days,
        "searchExpansionStepDays": expansion_step_days,
        "maxSearchExpansions": max_search_expansions,
        "rawRecords": len(all_records),
        "uniqueRecords": len(merged_records),
        "upserted": inserted_or_updated,
        "deleted": deleted,
        "searchAttempts": search_attempts,
        "finalWindow": (
            {
                "startDate": search_attempts[-1]["startDate"],
                "endDate": search_attempts[-1]["endDate"],
            }
            if search_attempts
            else None
        ),
        "triggerMode": "due_delivery",
    }
