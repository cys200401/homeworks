from __future__ import annotations

PIPELINE_STAGES = (
    "metadata_sync",
    "crawler",
    "download_pdf",
    "pdf_to_txt",
    "report_write",
    "personalized_delivery",
    "frontend_build",
)

PIPELINE_STATUSES = ("running", "succeeded", "failed", "partial")
