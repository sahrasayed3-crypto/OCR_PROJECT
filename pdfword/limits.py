from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ProcessingLimits:
    max_upload_bytes: int = 100 * 1024 * 1024
    max_result_bytes: int = 100 * 1024 * 1024
    max_pdf_bytes: int = 100 * 1024 * 1024
    max_pdf_pages: int = 500
    max_image_pixels: int = 40_000_000
    max_archive_members: int = 10_000
    max_decompressed_bytes: int = 1024 * 1024 * 1024
    max_dpi: int = 400
    max_parallel_pages: int = 2
    max_ocr_attempts: int = 6
    page_timeout_seconds: int = 300
    file_timeout_seconds: int = 7200


DEFAULT_LIMITS = ProcessingLimits()


def limits_from_settings(settings: dict[str, Any]) -> ProcessingLimits:
    return ProcessingLimits(
        max_upload_bytes=max(
            1024, int(settings.get("max_upload_bytes", 100 * 1024 * 1024))
        ),
        max_result_bytes=max(
            1024, int(settings.get("max_result_bytes", 100 * 1024 * 1024))
        ),
        max_pdf_bytes=max(1024, int(settings.get("max_pdf_bytes", 100 * 1024 * 1024))),
        max_pdf_pages=max(1, int(settings.get("max_pdf_pages", 500))),
        max_image_pixels=max(
            1_000_000, int(settings.get("max_image_pixels", 40_000_000))
        ),
        max_archive_members=max(10, int(settings.get("max_archive_members", 10_000))),
        max_decompressed_bytes=max(
            1024 * 1024,
            int(settings.get("max_decompressed_bytes", 1024 * 1024 * 1024)),
        ),
        max_dpi=max(100, int(settings.get("max_dpi", 400))),
        max_parallel_pages=max(1, min(2, int(settings.get("max_parallel_pages", 2)))),
        max_ocr_attempts=max(1, int(settings.get("max_ocr_attempts", 6))),
        page_timeout_seconds=max(30, int(settings.get("page_timeout_seconds", 300))),
        file_timeout_seconds=max(60, int(settings.get("file_timeout_seconds", 7200))),
    )


def limits_from_env() -> ProcessingLimits:
    return limits_from_settings(
        {
            "max_upload_bytes": os.getenv("CLOUDA_MAX_UPLOAD_BYTES", 100 * 1024 * 1024),
            "max_result_bytes": os.getenv("CLOUDA_MAX_RESULT_BYTES", 100 * 1024 * 1024),
            "max_pdf_bytes": os.getenv("CLOUDA_MAX_PDF_BYTES", 100 * 1024 * 1024),
            "max_pdf_pages": os.getenv("CLOUDA_MAX_PDF_PAGES", 500),
            "max_image_pixels": os.getenv("CLOUDA_MAX_IMAGE_PIXELS", 40_000_000),
            "max_archive_members": os.getenv("CLOUDA_MAX_ARCHIVE_MEMBERS", 10_000),
            "max_decompressed_bytes": os.getenv(
                "CLOUDA_MAX_DECOMPRESSED_BYTES", 1024 * 1024 * 1024
            ),
        }
    )


def validate_pdf_limits(
    pdf_size_bytes: int,
    total_pages: int,
    *,
    limits: ProcessingLimits = DEFAULT_LIMITS,
) -> None:
    if pdf_size_bytes <= 0:
        raise ValueError("PDF is empty.")
    if total_pages <= 0:
        raise ValueError("PDF has no processable pages.")
    if pdf_size_bytes > min(limits.max_upload_bytes, limits.max_pdf_bytes):
        raise ValueError("PDF exceeds the configured byte limit.")
    if total_pages > limits.max_pdf_pages:
        raise ValueError(
            f"PDF page count exceeds the configured limit ({limits.max_pdf_pages})."
        )
