from __future__ import annotations

import unittest

from backend.scripts.sync_arxiv_metadata import merge_records


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


if __name__ == "__main__":
    unittest.main()
