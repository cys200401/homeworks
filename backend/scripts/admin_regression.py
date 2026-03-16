from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass

from playwright.sync_api import Error, Page, sync_playwright


@dataclass
class AdminRegressionSummary:
    admin_url: str
    api_base_url: str
    page_title: str
    health_status: str
    database_status: str
    recent_error_count: str
    latest_stages: list[str]
    recent_pv_rows: list[str]
    console_errors: list[str]
    request_failures: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Use Playwright to verify the local /admin page.",
    )
    parser.add_argument(
        "--admin-url",
        default="http://localhost:3000/admin",
        help="Frontend admin page URL.",
    )
    parser.add_argument(
        "--api-base-url",
        default="http://127.0.0.1:8000",
        help="Expected admin API base URL.",
    )
    parser.add_argument(
        "--screenshot",
        default="",
        help="Optional screenshot output path.",
    )
    return parser.parse_args()


def text_or_empty(page: Page, selector: str) -> str:
    locator = page.locator(selector)
    locator.wait_for(state="visible", timeout=15_000)
    return locator.inner_text().strip()


def collect_list_text(page: Page, selector: str) -> list[str]:
    return [item.strip() for item in page.locator(selector).all_inner_texts() if item.strip()]


def run_regression(admin_url: str, api_base_url: str, screenshot: str) -> AdminRegressionSummary:
    console_errors: list[str] = []
    request_failures: list[str] = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()

        page.on(
            "console",
            lambda message: console_errors.append(message.text)
            if message.type == "error"
            else None,
        )
        page.on(
            "requestfailed",
            lambda request: request_failures.append(
                f"{request.method} {request.url} :: {request.failure}"
            ),
        )

        try:
            page.goto(admin_url, wait_until="domcontentloaded", timeout=30_000)
            page.wait_for_load_state("networkidle")

            page.get_by_role("heading", name="后台概览").wait_for(timeout=15_000)
            page.get_by_role("heading", name="系统健康").wait_for(timeout=15_000)

            if screenshot:
                page.screenshot(path=screenshot, full_page=True)

            health_status = text_or_empty(page, ".admin-kpi:nth-of-type(1) .admin-kpi__value")
            database_status = text_or_empty(page, ".admin-kpi:nth-of-type(2) .admin-kpi__value")
            recent_error_count = text_or_empty(
                page,
                ".admin-kpi:nth-of-type(3) .admin-kpi__value",
            )
            latest_stages = collect_list_text(page, ".admin-grid .admin-panel:nth-of-type(2) .admin-list__item")
            recent_pv_rows = collect_list_text(page, ".admin-grid .admin-panel:nth-of-type(3) .admin-list__item")

            summary = AdminRegressionSummary(
                admin_url=admin_url,
                api_base_url=api_base_url,
                page_title=page.title(),
                health_status=health_status,
                database_status=database_status,
                recent_error_count=recent_error_count,
                latest_stages=latest_stages,
                recent_pv_rows=recent_pv_rows,
                console_errors=console_errors,
                request_failures=request_failures,
            )
        except Error:
            browser.close()
            raise

        browser.close()
        return summary


def main() -> int:
    args = parse_args()
    summary = run_regression(
        admin_url=args.admin_url,
        api_base_url=args.api_base_url,
        screenshot=args.screenshot,
    )
    print(json.dumps(asdict(summary), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
