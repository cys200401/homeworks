from __future__ import annotations

import unittest
from datetime import UTC, datetime, time

from backend.app.personalization import (
    build_personalized_report,
    compile_theme_prompt,
    compute_next_run_at,
)


class PersonalizationTests(unittest.TestCase):
    def test_compute_next_run_at_respects_timezone(self) -> None:
        now = datetime(2026, 3, 15, 15, 30, tzinfo=UTC)

        next_run = compute_next_run_at(
            "America/Los_Angeles",
            time(hour=8, minute=0),
            now=now,
        )

        self.assertEqual(next_run.isoformat(), "2026-03-16T15:00:00+00:00")

    def test_compile_theme_prompt_applies_keyword_modifiers(self) -> None:
        theme = compile_theme_prompt(
            "Bold brutalist research UI with rounded cards, warm palette and calm motion.",
        )

        self.assertEqual(theme["themeName"], "brutalist")
        self.assertEqual(theme["borderRadius"], "round")
        self.assertEqual(theme["motionLevel"], "calm")
        self.assertEqual(theme["palette"]["accent"], "#c2410c")

    def test_build_personalized_report_uses_categories_and_theme(self) -> None:
        report = build_personalized_report(
            user={
                "handle": "vision-scout",
                "display_name": "Vision Scout",
                "timezone": "Asia/Shanghai",
            },
            delivery_profile={
                "categories_json": ["cs.CV", "cs.AI", "cs.IR"],
                "window_start_hour": 8,
                "window_end_hour": 23,
                "lookback_days": 3,
            },
            theme_profile={
                "prompt_text": "Bold brutalist research UI with cobalt accents.",
                "tokens_json": compile_theme_prompt(
                    "Bold brutalist research UI with cobalt accents.",
                ),
            },
            now=datetime(2026, 3, 15, 0, 30, tzinfo=UTC),
            crawl_meta={
                "triggeredAt": "2026-03-15T00:30:00+00:00",
                "triggerMode": "due_delivery",
                "uniqueRecords": 1,
                "upserted": 1,
            },
            paper_catalog=[
                {
                    "arxivId": "2603.15006v1",
                    "title": "Structured Memory Retrieval for Multimodal Research Assistants",
                    "authors": ["Geoffrey Hinton", "Yoshua Bengio"],
                    "abstract": "This paper introduces a structured memory retrieval scheme for multimodal assistants.",
                    "categories": ["cs.IR", "cs.CV", "cs.CL"],
                    "arxivUrl": "https://arxiv.org/abs/2603.15006",
                    "publishedAt": "2026-03-15T00:25:00Z",
                }
            ],
        )

        self.assertEqual(report["title"], "Vision Scout 的个性化 AI 晨报")
        self.assertGreaterEqual(report["totalPapers"], 1)
        self.assertEqual(report["themeTokens"]["themeName"], "brutalist")
        self.assertIn("视觉推理", report["tags"])
        self.assertGreaterEqual(len(report["highlights"]), 1)
        self.assertEqual(report["sourceMeta"]["paperSource"], "database")
        self.assertEqual(report["sourceMeta"]["crawlMeta"]["triggerMode"], "due_delivery")
        self.assertIn("自动抓取", report["summary"])

    def test_build_personalized_report_expands_lookback_when_primary_window_is_empty(self) -> None:
        report = build_personalized_report(
            user={
                "handle": "research-lead",
                "display_name": "Research Lead",
                "timezone": "Asia/Shanghai",
            },
            delivery_profile={
                "categories_json": ["cs.IR", "cs.CV"],
                "window_start_hour": 8,
                "window_end_hour": 23,
                "lookback_days": 1,
            },
            theme_profile={
                "prompt_text": "",
                "tokens_json": compile_theme_prompt(""),
            },
            now=datetime(2026, 3, 15, 0, 30, tzinfo=UTC),
            paper_catalog=[
                {
                    "arxivId": "2603.15006v1",
                    "title": "Structured Memory Retrieval for Multimodal Research Assistants",
                    "authors": ["Geoffrey Hinton", "Yoshua Bengio"],
                    "abstract": "This paper introduces a structured memory retrieval scheme for multimodal assistants.",
                    "categories": ["cs.IR", "cs.CV", "cs.CL"],
                    "arxivUrl": "https://arxiv.org/abs/2603.15006",
                    "publishedAt": "2026-03-14T00:25:00Z",
                }
            ],
        )

        self.assertEqual(report["totalPapers"], 1)
        self.assertTrue(report["sourceMeta"]["searchExpanded"])
        self.assertEqual(report["sourceMeta"]["effectiveLookbackDays"], 3)
        self.assertIn("自动扩展到 3 天", report["summary"])

    def test_build_personalized_report_keeps_database_source_empty_when_catalog_is_empty(self) -> None:
        report = build_personalized_report(
            user={
                "handle": "robotics",
                "display_name": "Robotics",
                "timezone": "UTC",
            },
            delivery_profile={
                "categories_json": ["cs.RO"],
                "window_start_hour": 0,
                "window_end_hour": 24,
                "lookback_days": 1,
            },
            theme_profile=None,
            now=datetime(2026, 3, 15, 0, 30, tzinfo=UTC),
            paper_catalog=[],
        )

        self.assertEqual(report["totalPapers"], 0)
        self.assertEqual(report["sourceMeta"]["paperSource"], "database")
        self.assertEqual(report["sourceMeta"]["selectedPaperIds"], [])
        self.assertEqual(report["highlights"], [])
        self.assertEqual(report["notables"], [])


if __name__ == "__main__":
    unittest.main()
