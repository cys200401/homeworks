from __future__ import annotations

PIPELINE_STAGES = (
    "crawler",
    "download_pdf",
    "pdf_to_txt",
    "report_write",
    "frontend_build",
)

PIPELINE_STATUSES = ("running", "succeeded", "failed", "partial")
