import html
from pathlib import Path

STATUS_LABELS = {
    "pending": "قيد الانتظار",
    "processing": "قيد المعالجة",
    "completed": "مكتمل",
    "manual_review": "تحتاج مراجعة",
    "failed": "فشل",
    "cancelled": "ملغى",
}

STATUS_LABEL_TRANSLATIONS = {
    "System": "النظام",
    "Worker": "العامل",
    "Direct PDF text": "استخراج النص المباشر",
    "Future OCR": "OCR القادم",
}

STATUS_STATE_TRANSLATIONS = {
    "ready": "جاهز",
    "busy": "مشغول",
    "offline": "غير متصل",
    "available": "متاح",
    "connected": "متصل",
    "unavailable": "غير متاح",
}


def load_styles(path: str | Path = "assets/styles.css") -> str:
    p = Path(path)
    return f"<style>{p.read_text(encoding='utf-8')}</style>" if p.is_file() else ""


def status_badge(label: str, state: str) -> str:
    safe_label = html.escape(label)
    safe_state = html.escape(state)
    display_label = html.escape(STATUS_LABEL_TRANSLATIONS.get(label, label))
    display_state = html.escape(STATUS_STATE_TRANSLATIONS.get(state, state))
    return (
        f'<span class="status-badge status-{html.escape(state)}">'
        f'<span class="status-dot" aria-hidden="true"></span>'
        f'<span>{display_label}<em class="sr-only">{safe_label}</em></span>'
        f'<strong>{display_state}<em class="sr-only">{safe_state}</em></strong>'
        "</span>"
    )


def status_strip(
    status: dict, *, direct_text_ready: bool = True, future_ocr_ready: bool = False
) -> str:
    worker_ready = status.get("worker_state") in {"ready", "busy"}
    badges = [
        status_badge("System", "ready" if status.get("server") else "offline"),
        status_badge(
            "Worker",
            status.get("worker_state", "offline") if worker_ready else "offline",
        ),
        status_badge("Direct PDF text", "ready" if direct_text_ready else "offline"),
        status_badge("Future OCR", "ready" if future_ocr_ready else "offline"),
    ]
    return (
        '<section class="status-center" aria-label="System status">'
        '<div class="status-center-title">مركز الحالة'
        '<em class="sr-only">Status Center</em></div>'
        '<div class="status-strip">' + "".join(badges) + "</div></section>"
    )


def page_header(title: str, subtitle: str = "") -> str:
    return (
        '<section class="page-header page-heading">'
        f"<h1>{html.escape(title)}</h1>"
        f"<p>{html.escape(subtitle)}</p>"
        "</section>"
    )


def section_title(title: str, description: str = "", step: int | None = None) -> str:
    step_html = f'<span class="section-step">{step}</span>' if step is not None else ""
    return (
        '<div class="section-title section-heading">'
        f"{step_html}<div><h2>{html.escape(title)}</h2>"
        f"<p>{html.escape(description)}</p></div></div>"
    )


def file_summary(filename: str, size_bytes: int, page_count: int | None = None) -> str:
    size_mb = size_bytes / (1024 * 1024)
    pages = "عدد الصفحات غير معروف" if page_count is None else f"{page_count} صفحة"
    return (
        '<div class="file-summary">'
        '<div class="file-icon">PDF</div>'
        '<div class="file-meta">'
        f"<strong>{html.escape(filename)}</strong>"
        '<div class="file-facts">'
        f"<span>{size_mb:.2f} MB</span><span>{html.escape(pages)}</span>"
        "</div></div></div>"
    )


def processing_panel(
    *,
    stage: str,
    progress: int | None,
    completed_pages: int,
    total_pages: int,
    elapsed: str,
    last_update: str = "",
    current_page: int | None = None,
) -> str:
    progress_text = "قيد العمل" if progress is None else f"{progress}%"
    width = "100%" if progress is None else f"{max(0, min(100, progress))}%"
    current = (
        "" if current_page is None else f"<span>الصفحة الحالية: {current_page}</span>"
    )
    progress_track = (
        '<div class="progress-track progress-indeterminate"><span></span></div>'
        if progress is None
        else f'<div class="progress-track"><span style="width:{width}"></span></div>'
    )
    return (
        '<section class="processing-panel">'
        '<div class="processing-head">'
        f"<div><small>المرحلة الحالية</small><strong>{html.escape(stage)}</strong></div>"
        f"<b>{html.escape(progress_text)}</b></div>"
        f"{progress_track}"
        '<div class="processing-grid">'
        f"<span>الصفحات: {completed_pages}/{total_pages}</span>"
        f"{current}"
        f"<span>الزمن المنقضي: {html.escape(elapsed)}</span>"
        f"<span>آخر تحديث: {html.escape(last_update)}</span>"
        "</div></section>"
    )


def progress_steps(active_index: int = 0) -> str:
    labels = [
        "تحليل الملف",
        "تجهيز الصفحات",
        "استخراج النص",
        "فحص OCR القادم",
        "تنسيق Word",
        "إنشاء DOCX",
        "مراجعة نهائية",
    ]
    items = []
    for index, label in enumerate(labels):
        state = (
            "step-done"
            if index < active_index
            else "step-active" if index == active_index else "step-todo"
        )
        items.append(
            f'<li class="progress-step {state}">'
            f"<span>{index + 1}</span>{html.escape(label)}</li>"
        )
    return '<ol class="progress-steps">' + "".join(items) + "</ol>"


def empty_state(title: str, description: str) -> str:
    return (
        '<div class="empty-state">'
        f"<strong>{html.escape(title)}</strong>"
        f"<p>{html.escape(description)}</p>"
        "</div>"
    )
