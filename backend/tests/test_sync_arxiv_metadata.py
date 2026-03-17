from __future__ import annotations

import unittest
from datetime import date

from backend.scripts.sync_arxiv_metadata import collect_records_with_auto_expand, merge_records


class SyncArxivMetadataTests(unittest.TestCase):
    def test_merge_records_deduplicates_and_unions_categories(self) -> None:
        merged = merge_records(
            [
                {
                    "arxiv_id": "2603.00001v1",
                    "title": "Paper A",
                    "authors": ["Alice"],
                    "abstract": "Abstract A",
                    "categories": ["cs.AI"],
                    "arxiv_url": "https://arxiv.org/abs/2603.00001",
                    "published": "2026-03-15",
                    "published_at": "2026-03-15T08:00:00Z",
                },
                {
                    "arxiv_id": "2603.00001v1",
                    "title": "Paper A",
                    "authors": ["Alice"],
                    "abstract": "Abstract A",
                    "categories": ["cs.LG", "cs.AI"],
                    "arxiv_url": "https://arxiv.org/abs/2603.00001",
                    "published": "2026-03-15",
                    "published_at": "2026-03-15T09:00:00Z",
                },
            ],
        )

        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0]["categories"], ["cs.AI", "cs.LG"])
        self.assertEqual(merged[0]["published_at"], "2026-03-15T09:00:00Z")

    def test_collect_records_with_auto_expand_retries_with_wider_window(self) -> None:
        class FakeCrawler:
            def __init__(self) -> None:
                self.calls: list[tuple[str, str, str]] = []

            def collect_records(self, **kwargs):
                self.calls.append((kwargs["start_date"], kwargs["end_date"], kwargs["category"]))
                if kwargs["start_date"] == "2026-03-14":
                    return []
                return [
                    {
                        "arxiv_id": "2603.00002v1",
                        "title": "Paper B",
                        "authors": ["Bob"],
                        "abstract": "Abstract B",
                        "categories": ["cs.AI"],
                        "arxiv_url": "https://arxiv.org/abs/2603.00002",
                        "published": "2026-03-13",
                        "published_at": "2026-03-13T08:00:00Z",
                    }
                ]

        crawler = FakeCrawler()
        records, attempts = collect_records_with_auto_expand(
            crawler=crawler,
            categories=["cs.AI"],
            end_day=date(2026, 3, 15),
            limit_per_category=50,
            lookback_days=2,
            page_size=100,
            timeout=30,
            retries=2,
            request_interval=0.0,
            expand_step_days=2,
            max_expansions=1,
        )

        self.assertEqual(len(records), 1)
        self.assertEqual(
            attempts,
            [
                {
                    "attempt": 1,
                    "lookbackDays": 2,
                    "startDate": "2026-03-14",
                    "endDate": "2026-03-15",
                    "rawRecords": 0,
                },
                {
                    "attempt": 2,
                    "lookbackDays": 4,
                    "startDate": "2026-03-12",
                    "endDate": "2026-03-15",
                    "rawRecords": 1,
                },
            ],
        )
        self.assertEqual(
            crawler.calls,
            [
                ("2026-03-14", "2026-03-15", "cs.AI"),
                ("2026-03-12", "2026-03-15", "cs.AI"),
            ],
        )


if __name__ == "__main__":
    unittest.main()
