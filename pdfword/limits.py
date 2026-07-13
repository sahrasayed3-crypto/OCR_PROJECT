from dataclasses import dataclass


@dataclass(frozen=True)
class ProcessingLimits:
    max_pdf_pages: int = 500
    max_dpi: int = 400
    max_parallel_pages: int = 2
    max_ocr_attempts: int = 6
    page_timeout_seconds: int = 300
    file_timeout_seconds: int = 7200


DEFAULT_LIMITS = ProcessingLimits()


def limits_from_settings(settings: dict) -> ProcessingLimits:
    return ProcessingLimits(
        max_pdf_pages=max(1, int(settings.get("max_pdf_pages", 500))),
        max_dpi=max(100, int(settings.get("max_dpi", 400))),
        max_parallel_pages=max(1, min(2, int(settings.get("max_parallel_pages", 2)))),
        max_ocr_attempts=max(1, int(settings.get("max_ocr_attempts", 6))),
        page_timeout_seconds=max(30, int(settings.get("page_timeout_seconds", 300))),
        file_timeout_seconds=max(60, int(settings.get("file_timeout_seconds", 7200))),
    )


def validate_pdf_limits(
    pdf_size_bytes: int,
    total_pages: int,
    *,
    limits: ProcessingLimits = DEFAULT_LIMITS,
) -> None:
    if pdf_size_bytes <= 0:
        raise ValueError("ملف PDF فارغ.")
    if total_pages <= 0:
        raise ValueError("ملف PDF لا يحتوي على صفحات قابلة للمعالجة.")
    if total_pages > limits.max_pdf_pages:
        raise ValueError(f"عدد صفحات PDF يتجاوز الحد المسموح ({limits.max_pdf_pages}).")
