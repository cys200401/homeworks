from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Query

from app.db import get_connection
from app.personalization import (
    build_personalized_report,
    catalog_row_to_paper,
    compile_theme_prompt,
    compute_next_run_at,
    default_delivery_profile,
    default_theme_profile,
    normalize_categories,
)
from app.schemas import (
    ThemeTokens,
    UpdateUserPreferencesRequest,
    UpdateUserThemeRequest,
    UserDeliveryProfilePayload,
    UserListResponse,
    UserPaperBrief,
    UserPaperHighlight,
    UserProfileResponse,
    UserReportPayload,
    UserSummaryItem,
    UserThemeResponse,
    UserWorkspaceResponse,
)

router = APIRouter(prefix="/api/users", tags=["users"])


def _validate_preference_payload(payload: UpdateUserPreferencesRequest) -> None:
    if not 0 <= payload.windowStartHour <= 23:
        raise HTTPException(status_code=422, detail="windowStartHour must be between 0 and 23")
    if not 0 <= payload.windowEndHour <= 24:
        raise HTTPException(status_code=422, detail="windowEndHour must be between 0 and 24")
    if not 1 <= payload.lookbackDays <= 30:
        raise HTTPException(status_code=422, detail="lookbackDays must be between 1 and 30")


def _fetch_user(handle: str) -> dict[str, Any]:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                select
                  id::text as id,
                  handle,
                  display_name,
                  email,
                  timezone,
                  created_at,
                  updated_at
                from users
                where handle = %s
                """,
                (handle,),
            )
            user = cursor.fetchone()

        if not user:
            raise HTTPException(status_code=404, detail=f"user '{handle}' not found")

        delivery, theme = _ensure_profiles(connection, user)
        latest_report = _fetch_latest_report(connection, user["id"])
        return {
            "user": user,
            "delivery": delivery,
            "theme": theme,
            "latest_report": latest_report,
        }


def _ensure_profiles(connection, user: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            select
              user_id::text as user_id,
              delivery_enabled,
              delivery_local_time,
              window_start_hour,
              window_end_hour,
              lookback_days,
              categories_json,
              next_run_at,
              last_run_at
            from user_delivery_profiles
            where user_id = %s::uuid
            """,
            (user["id"],),
        )
        delivery = cursor.fetchone()

        if not delivery:
            defaults = default_delivery_profile(user["id"], user["timezone"])
            cursor.execute(
                """
                insert into user_delivery_profiles (
                  user_id,
                  delivery_enabled,
                  delivery_local_time,
                  window_start_hour,
                  window_end_hour,
                  lookback_days,
                  categories_json,
                  next_run_at
                )
                values (%s::uuid, %s, %s, %s, %s, %s, %s::jsonb, %s)
                returning
                  user_id::text as user_id,
                  delivery_enabled,
                  delivery_local_time,
                  window_start_hour,
                  window_end_hour,
                  lookback_days,
                  categories_json,
                  next_run_at,
                  last_run_at
                """,
                (
                    defaults["user_id"],
                    defaults["delivery_enabled"],
                    defaults["delivery_local_time"],
                    defaults["window_start_hour"],
                    defaults["window_end_hour"],
                    defaults["lookback_days"],
                    json.dumps(defaults["categories_json"], ensure_ascii=True),
                    defaults["next_run_at"],
                ),
            )
            delivery = cursor.fetchone()

        cursor.execute(
            """
            select
              user_id::text as user_id,
              prompt_text,
              theme_name,
              tokens_json
            from user_theme_profiles
            where user_id = %s::uuid
            """,
            (user["id"],),
        )
        theme = cursor.fetchone()

        if not theme:
            defaults = default_theme_profile(user["id"])
            cursor.execute(
                """
                insert into user_theme_profiles (
                  user_id,
                  prompt_text,
                  theme_name,
                  tokens_json
                )
                values (%s::uuid, %s, %s, %s::jsonb)
                returning
                  user_id::text as user_id,
                  prompt_text,
                  theme_name,
                  tokens_json
                """,
                (
                    defaults["user_id"],
                    defaults["prompt_text"],
                    defaults["theme_name"],
                    json.dumps(defaults["tokens_json"], ensure_ascii=True),
                ),
            )
            theme = cursor.fetchone()

        connection.commit()
        return delivery, theme


def _fetch_latest_report(connection, user_id: str) -> dict[str, Any] | None:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            select
              report_date,
              title,
              summary,
              total_papers,
              tags_json,
              trends,
              highlights_json,
              notables_json,
              theme_tokens_json,
              source_meta_json,
              published_at
            from user_reports
            where user_id = %s::uuid
            order by published_at desc
            limit 1
            """,
            (user_id,),
        )
        return cursor.fetchone()


def _user_profile_response(
    user: dict[str, Any],
    delivery: dict[str, Any],
    theme: dict[str, Any],
    latest_report_date,
) -> UserProfileResponse:
    return UserProfileResponse(
        handle=user["handle"],
        displayName=user["display_name"],
        email=user["email"],
        timezone=user["timezone"],
        delivery=UserDeliveryProfilePayload(
            deliveryEnabled=delivery["delivery_enabled"],
            deliveryLocalTime=delivery["delivery_local_time"],
            windowStartHour=delivery["window_start_hour"],
            windowEndHour=delivery["window_end_hour"],
            lookbackDays=delivery["lookback_days"],
            categories=normalize_categories(delivery["categories_json"]),
            nextRunAt=delivery["next_run_at"],
            lastRunAt=delivery["last_run_at"],
        ),
        themePrompt=theme["prompt_text"],
        theme=ThemeTokens.model_validate(theme["tokens_json"]),
        latestReportDate=latest_report_date,
    )


def _report_payload(report: dict[str, Any]) -> UserReportPayload:
    return UserReportPayload(
        date=report["report_date"],
        title=report["title"],
        summary=report["summary"],
        totalPapers=report["total_papers"],
        tags=list(report["tags_json"]),
        trends=report["trends"],
        highlights=[UserPaperHighlight.model_validate(item) for item in report["highlights_json"]],
        notables=[UserPaperBrief.model_validate(item) for item in report["notables_json"]],
        publishedAt=report["published_at"],
        theme=ThemeTokens.model_validate(report["theme_tokens_json"]),
        source=dict(report["source_meta_json"]),
    )


def _load_catalog_papers(
    connection,
    lookback_days: int,
    reference_time: datetime,
) -> list[dict[str, Any]]:
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
            (reference_time, max(lookback_days + 1, 2)),
        )
        rows = cursor.fetchall()

    return [catalog_row_to_paper(row) for row in rows]


def _upsert_generated_report(
    connection,
    user: dict[str, Any],
    delivery: dict[str, Any],
    theme: dict[str, Any],
    now: datetime | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    generated_at = (now or datetime.now(UTC)).astimezone(UTC)
    paper_catalog = _load_catalog_papers(
        connection,
        lookback_days=int(delivery.get("lookback_days", 1)),
        reference_time=generated_at,
    )
    report = build_personalized_report(
        user=user,
        delivery_profile=delivery,
        theme_profile=theme,
        now=generated_at,
        paper_catalog=paper_catalog or None,
    )
    next_run_at = compute_next_run_at(user["timezone"], delivery["delivery_local_time"], now=generated_at)

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
            returning
              report_date,
              title,
              summary,
              total_papers,
              tags_json,
              trends,
              highlights_json,
              notables_json,
              theme_tokens_json,
              source_meta_json,
              published_at
            """,
            (
                user["id"],
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
                generated_at,
                generated_at,
            ),
        )
        report_row = cursor.fetchone()

        cursor.execute(
            """
            update user_delivery_profiles
            set
              last_run_at = %s,
              next_run_at = %s,
              updated_at = %s
            where user_id = %s::uuid
            returning
              user_id::text as user_id,
              delivery_enabled,
              delivery_local_time,
              window_start_hour,
              window_end_hour,
              lookback_days,
              categories_json,
              next_run_at,
              last_run_at
            """,
            (generated_at, next_run_at, generated_at, user["id"]),
        )
        updated_delivery = cursor.fetchone()
        connection.commit()

    return report_row, updated_delivery


@router.get("", response_model=UserListResponse)
def list_users(limit: int = Query(default=20, ge=1, le=100)) -> UserListResponse:
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    select
                      u.handle,
                      u.display_name,
                      u.timezone,
                      coalesce(d.delivery_enabled, true) as delivery_enabled,
                      coalesce(d.delivery_local_time, time '08:00') as delivery_local_time,
                      coalesce(d.categories_json, '["cs.AI"]'::jsonb) as categories_json,
                      coalesce(t.theme_name, 'editorial') as theme_name,
                      d.next_run_at,
                      max(r.report_date) as latest_report_date
                    from users u
                    left join user_delivery_profiles d on d.user_id = u.id
                    left join user_theme_profiles t on t.user_id = u.id
                    left join user_reports r on r.user_id = u.id
                    group by
                      u.id,
                      u.handle,
                      u.display_name,
                      u.timezone,
                      d.delivery_enabled,
                      d.delivery_local_time,
                      d.categories_json,
                      t.theme_name,
                      d.next_run_at
                    order by u.created_at asc
                    limit %s
                    """,
                    (limit,),
                )
                items = [
                    UserSummaryItem(
                        handle=row["handle"],
                        displayName=row["display_name"],
                        timezone=row["timezone"],
                        deliveryEnabled=row["delivery_enabled"],
                        deliveryLocalTime=row["delivery_local_time"],
                        categories=normalize_categories(row["categories_json"]),
                        themeName=row["theme_name"],
                        nextRunAt=row["next_run_at"],
                        latestReportDate=row["latest_report_date"],
                    )
                    for row in cursor.fetchall()
                ]

        return UserListResponse(items=items)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/{handle}", response_model=UserProfileResponse)
def get_user_profile(handle: str) -> UserProfileResponse:
    try:
        bundle = _fetch_user(handle)
        latest_report_date = (
            bundle["latest_report"]["report_date"] if bundle["latest_report"] else None
        )
        return _user_profile_response(
            bundle["user"],
            bundle["delivery"],
            bundle["theme"],
            latest_report_date,
        )
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/{handle}/workspace", response_model=UserWorkspaceResponse)
def get_user_workspace(handle: str) -> UserWorkspaceResponse:
    try:
        bundle = _fetch_user(handle)
        latest_report_date = (
            bundle["latest_report"]["report_date"] if bundle["latest_report"] else None
        )
        return UserWorkspaceResponse(
            user=_user_profile_response(
                bundle["user"],
                bundle["delivery"],
                bundle["theme"],
                latest_report_date,
            ),
            report=_report_payload(bundle["latest_report"]) if bundle["latest_report"] else None,
        )
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.put("/{handle}/preferences", response_model=UserProfileResponse)
def update_user_preferences(
    handle: str,
    payload: UpdateUserPreferencesRequest,
) -> UserProfileResponse:
    _validate_preference_payload(payload)
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    select
                      id::text as id,
                      handle,
                      display_name,
                      email,
                      timezone
                    from users
                    where handle = %s
                    """,
                    (handle,),
                )
                user = cursor.fetchone()

                if not user:
                    raise HTTPException(status_code=404, detail=f"user '{handle}' not found")

                categories = normalize_categories(payload.categories)
                current_time = datetime.now(UTC)
                next_run_at = compute_next_run_at(payload.timezone, payload.deliveryLocalTime, now=current_time)

                cursor.execute(
                    """
                    update users
                    set
                      display_name = %s,
                      timezone = %s,
                      updated_at = %s
                    where id = %s::uuid
                    returning
                      id::text as id,
                      handle,
                      display_name,
                      email,
                      timezone
                    """,
                    (payload.displayName, payload.timezone, current_time, user["id"]),
                )
                user = cursor.fetchone()

                cursor.execute(
                    """
                    insert into user_delivery_profiles (
                      user_id,
                      delivery_enabled,
                      delivery_local_time,
                      window_start_hour,
                      window_end_hour,
                      lookback_days,
                      categories_json,
                      next_run_at,
                      updated_at
                    )
                    values (%s::uuid, %s, %s, %s, %s, %s, %s::jsonb, %s, %s)
                    on conflict (user_id)
                    do update set
                      delivery_enabled = excluded.delivery_enabled,
                      delivery_local_time = excluded.delivery_local_time,
                      window_start_hour = excluded.window_start_hour,
                      window_end_hour = excluded.window_end_hour,
                      lookback_days = excluded.lookback_days,
                      categories_json = excluded.categories_json,
                      next_run_at = excluded.next_run_at,
                      updated_at = excluded.updated_at
                    returning
                      user_id::text as user_id,
                      delivery_enabled,
                      delivery_local_time,
                      window_start_hour,
                      window_end_hour,
                      lookback_days,
                      categories_json,
                      next_run_at,
                      last_run_at
                    """,
                    (
                        user["id"],
                        payload.deliveryEnabled,
                        payload.deliveryLocalTime,
                        payload.windowStartHour,
                        payload.windowEndHour,
                        payload.lookbackDays,
                        json.dumps(categories, ensure_ascii=True),
                        next_run_at,
                        current_time,
                    ),
                )
                delivery = cursor.fetchone()

                _, theme = _ensure_profiles(connection, user)
                latest_report = _fetch_latest_report(connection, user["id"])
                connection.commit()

        latest_report_date = latest_report["report_date"] if latest_report else None
        return _user_profile_response(user, delivery, theme, latest_report_date)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.put("/{handle}/theme", response_model=UserThemeResponse)
def update_user_theme(handle: str, payload: UpdateUserThemeRequest) -> UserThemeResponse:
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    select
                      id::text as id,
                      handle,
                      display_name,
                      email,
                      timezone
                    from users
                    where handle = %s
                    """,
                    (handle,),
                )
                user = cursor.fetchone()

                if not user:
                    raise HTTPException(status_code=404, detail=f"user '{handle}' not found")

                current_time = datetime.now(UTC)
                tokens = compile_theme_prompt(payload.promptText)

                cursor.execute(
                    """
                    insert into user_theme_profiles (
                      user_id,
                      prompt_text,
                      theme_name,
                      tokens_json,
                      updated_at
                    )
                    values (%s::uuid, %s, %s, %s::jsonb, %s)
                    on conflict (user_id)
                    do update set
                      prompt_text = excluded.prompt_text,
                      theme_name = excluded.theme_name,
                      tokens_json = excluded.tokens_json,
                      updated_at = excluded.updated_at
                    returning
                      user_id::text as user_id,
                      prompt_text,
                      theme_name,
                      tokens_json
                    """,
                    (
                        user["id"],
                        payload.promptText,
                        tokens["themeName"],
                        json.dumps(tokens, ensure_ascii=True),
                        current_time,
                    ),
                )
                theme = cursor.fetchone()
                connection.commit()

        return UserThemeResponse(
            promptText=theme["prompt_text"],
            theme=ThemeTokens.model_validate(theme["tokens_json"]),
        )
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/{handle}/report/generate", response_model=UserWorkspaceResponse)
def generate_user_report(handle: str) -> UserWorkspaceResponse:
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    select
                      id::text as id,
                      handle,
                      display_name,
                      email,
                      timezone
                    from users
                    where handle = %s
                    """,
                    (handle,),
                )
                user = cursor.fetchone()

                if not user:
                    raise HTTPException(status_code=404, detail=f"user '{handle}' not found")

            delivery, theme = _ensure_profiles(connection, user)
            report_row, updated_delivery = _upsert_generated_report(connection, user, delivery, theme)

        profile = _user_profile_response(
            user,
            updated_delivery,
            theme,
            report_row["report_date"],
        )
        return UserWorkspaceResponse(
            user=profile,
            report=_report_payload(report_row),
        )
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc
