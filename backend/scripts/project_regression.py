from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass

from playwright.sync_api import sync_playwright


@dataclass
class PageSummary:
    name: str
    url: str
    title: str
    expected_title: str
    title_matches: bool
    key_text: list[str]


@dataclass
class ProjectRegressionSummary:
    pages: list[PageSummary]
    console_errors: list[str]
    request_failures: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Use Playwright to exercise the local Daily Paper project.",
    )
    parser.add_argument("--base-url", default="http://localhost:3000")
    parser.add_argument("--daily-date", default="2026-03-14")
    return parser.parse_args()


def run_regression(base_url: str, daily_date: str) -> ProjectRegressionSummary:
    console_errors: list[str] = []
    request_failures: list[str] = []
    page_summaries: list[PageSummary] = []
    year, month, day = daily_date.split("-")
    daily_title = f"{year}年{int(month)}月{int(day)}日 AI论文日报 | Daily Paper"

    targets = [
        (
            "home",
            f"{base_url}/",
            "Daily Paper — AI 论文日报",
            ["Daily Paper", "AI 论文日报"],
        ),
        (
            "daily",
            f"{base_url}/daily/{daily_date}",
            daily_title,
            ["重点关注", "也值得关注"],
        ),
        (
            "admin",
            f"{base_url}/admin",
            "后台概览 | Daily Paper",
            ["后台概览", "系统健康"],
        ),
    ]

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

        for name, url, expected_title, key_text in targets:
            page.goto(url, wait_until="domcontentloaded", timeout=30_000)
            page.wait_for_load_state("networkidle")

            for expected in key_text:
                page.get_by_text(expected, exact=False).first.wait_for(timeout=15_000)

            current_title = page.title()

            page_summaries.append(
                PageSummary(
                    name=name,
                    url=page.url,
                    title=current_title,
                    expected_title=expected_title,
                    title_matches=current_title == expected_title,
                    key_text=key_text,
                )
            )

        browser.close()

    return ProjectRegressionSummary(
        pages=page_summaries,
        console_errors=console_errors,
        request_failures=request_failures,
    )


def main() -> int:
    args = parse_args()
    summary = run_regression(base_url=args.base_url, daily_date=args.daily_date)
    print(json.dumps(asdict(summary), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
