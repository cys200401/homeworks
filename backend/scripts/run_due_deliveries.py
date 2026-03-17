from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.catalog_refresh import refresh_catalog_for_delivery
from app.db import get_connection
from app.personalization import (
    build_personalized_report,
    catalog_row_to_paper,
    compile_theme_prompt,
    compute_catalog_lookback_days,
    compute_next_run_at,
    resolve_search_expansion,
)


def load_catalog_papers(
    connection,
    lookback_days: int,
    reference_time: datetime,
) -> list[dict[str, object]]:
    expansion_step_days, max_search_expansions = resolve_search_expansion()
    catalog_lookback_days = compute_catalog_lookback_days(
        lookback_days,
        expansion_step_days=expansion_step_days,
        max_search_expansions=max_search_expansions,
    )

    with connection.cursor() as cursor:
        cursor.execute(
            """
            select
              arxiv_id,
              title,
              authors_json,
              abstract,
              categories_json,
              arxiv_url,
              published_at
            from arxiv_papers
            where published_at >= %s - (%s * interval '1 day')
            order by published_at desc
            limit 500
            """,
            (reference_time, catalog_lookback_days),
        )
        rows = cursor.fetchall()

    return [catalog_row_to_paper(row) for row in rows]


def main() -> int:
    now = datetime.now(UTC)
    generated_count = 0
    catalog_cache: dict[tuple[tuple[str, ...], int], dict[str, object]] = {}

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                select
                  u.id::text as user_id,
                  u.handle,
                  u.display_name,
                  u.email,
                  u.timezone,
                  d.delivery_enabled,
                  d.delivery_local_time,
                  d.window_start_hour,
                  d.window_end_hour,
                  d.lookback_days,
                  d.categories_json,
                  d.next_run_at,
                  t.prompt_text,
                  t.theme_name,
                  t.tokens_json
                from users u
                join user_delivery_profiles d on d.user_id = u.id
                left join user_theme_profiles t on t.user_id = u.id
                where d.delivery_enabled = true
                  and (d.next_run_at is null or d.next_run_at <= %s)
                order by d.next_run_at nulls first, u.created_at asc
                """,
                (now,),
            )
            due_rows = cursor.fetchall()

        for row in due_rows:
            theme_tokens = row["tokens_json"] or compile_theme_prompt(row["prompt_text"] or "")
            categories = tuple(sorted(str(item) for item in (row["categories_json"] or [])))
            cache_key = (categories, int(row["lookback_days"]))

            cached = catalog_cache.get(cache_key)
            if cached is None:
                crawl_meta = refresh_catalog_for_delivery(
                    categories=list(categories),
                    lookback_days=int(row["lookback_days"]),
                    reference_time=now,
                    delivery_profile={
                        "lookback_days": row["lookback_days"],
                        "categories_json": row["categories_json"],
                    },
                )
                paper_catalog = load_catalog_papers(
                    connection,
                    lookback_days=int(row["lookback_days"]),
                    reference_time=now,
                )
                cached = {
                    "crawl_meta": crawl_meta,
                    "paper_catalog": paper_catalog,
                }
                catalog_cache[cache_key] = cached

            crawl_meta = dict(cached["crawl_meta"])
            paper_catalog = list(cached["paper_catalog"])
            report = build_personalized_report(
                user={
                    "id": row["user_id"],
                    "handle": row["handle"],
                    "display_name": row["display_name"],
                    "email": row["email"],
                    "timezone": row["timezone"],
                },
                delivery_profile={
                    "categories_json": row["categories_json"],
                    "window_start_hour": row["window_start_hour"],
                    "window_end_hour": row["window_end_hour"],
                    "lookback_days": row["lookback_days"],
                    "delivery_local_time": row["delivery_local_time"],
                },
                theme_profile={
                    "prompt_text": row["prompt_text"] or "",
                    "tokens_json": theme_tokens,
                },
                now=now,
                paper_catalog=paper_catalog,
                crawl_meta=crawl_meta,
            )
            next_run_at = compute_next_run_at(row["timezone"], row["delivery_local_time"], now=now)

            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    insert into user_reports (
                      user_id,
                      report_date,
                      status,
                      title,
                      summary,
                      total_papers,
                      tags_json,
                      trends,
                      highlights_json,
                      notables_json,
                      theme_tokens_json,
                      source_meta_json,
                      published_at,
                      updated_at
                    )
                    values (
                      %s::uuid,
                      %s,
                      'published',
                      %s,
                      %s,
                      %s,
                      %s::jsonb,
                      %s,
                      %s::jsonb,
                      %s::jsonb,
                      %s::jsonb,
                      %s::jsonb,
                      %s,
                      %s
                    )
                    on conflict (user_id, report_date)
                    do update set
                      status = excluded.status,
                      title = excluded.title,
                      summary = excluded.summary,
                      total_papers = excluded.total_papers,
                      tags_json = excluded.tags_json,
                      trends = excluded.trends,
                      highlights_json = excluded.highlights_json,
                      notables_json = excluded.notables_json,
                      theme_tokens_json = excluded.theme_tokens_json,
                      source_meta_json = excluded.source_meta_json,
                      published_at = excluded.published_at,
                      updated_at = excluded.updated_at
                    """,
                    (
                        row["user_id"],
                        report["date"],
                        report["title"],
                        report["summary"],
                        report["totalPapers"],
                        json.dumps(report["tags"], ensure_ascii=True),
                        report["trends"],
                        json.dumps(report["highlights"], ensure_ascii=False),
                        json.dumps(report["notables"], ensure_ascii=False),
                        json.dumps(report["themeTokens"], ensure_ascii=True),
                        json.dumps(report["sourceMeta"], ensure_ascii=True),
                        now,
                        now,
                    ),
                )
                cursor.execute(
                    """
                    update user_delivery_profiles
                    set
                      last_run_at = %s,
                      next_run_at = %s,
                      updated_at = %s
                    where user_id = %s::uuid
                    """,
                    (now, next_run_at, now, row["user_id"]),
                )
            connection.commit()
            generated_count += 1
            print(
                f"generated personalized report for {row['handle']} "
                f"({report['date']}) next_run_at={next_run_at.isoformat()}",
                flush=True,
            )

    print(f"completed personalized delivery run: generated={generated_count}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
