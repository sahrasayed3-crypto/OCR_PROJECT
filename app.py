import io
import json
import time

import streamlit as st
from pypdf import PdfReader

from pdfword.database import Database, utc_now
from pdfword.docx_export import markdown_to_docx
from pdfword.health import system_health
from pdfword.limits import DEFAULT_LIMITS, validate_pdf_limits
from pdfword.ranges import build_output_filename, select_pages
from pdfword.settings import (
    DEFAULT_SETTINGS,
    load_settings,
    runtime_settings,
    save_settings,
)
from pdfword.storage import create_job_storage, ensure_disk_space, save_job_files
from pdfword.ui_components import (
    empty_state,
    file_summary,
    load_styles,
    page_header,
    section_title,
    status_strip,
)
from pdfword.ui_status import fetch_system_status
import requests

DEFAULT_PARALLEL_PAGES = 1
LOCAL_USER_ID = "local"


@st.cache_resource
def get_database() -> Database:
    return Database()


database = get_database()
runtime = runtime_settings()
username = LOCAL_USER_ID

st.set_page_config(page_title="Clouda PDF", page_icon="PDF", layout="wide")
styles = load_styles()
if styles:
    st.markdown(styles, unsafe_allow_html=True)

system_state = fetch_system_status(
    runtime.server_base_url,
    runtime.worker_api_key,
    requests,
    redis_available=False,
).as_dict()

st.markdown(
    """
    <div class="topbar">
      <div class="brand"><div class="brand-mark">C</div>
        <div><strong>Clouda PDF</strong><small>Direct PDF text extraction</small></div>
      </div>
      <div class="local-pill">Local development build</div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown(
    status_strip(system_state, direct_text_ready=True, future_ocr_ready=False),
    unsafe_allow_html=True,
)

nav_options = [
    "Convert",
    "My files",
    "Conversion history",
    "Correction memory",
    "Statistics",
    "Settings",
    "System status",
]
nav_labels = {item: item for item in nav_options}

with st.sidebar:
    st.markdown("## Clouda PDF")
    st.caption("PDF to editable DOCX")
    current_page = st.radio(
        "Navigation",
        nav_options,
        format_func=lambda value: nav_labels[value],
        key="main_navigation",
    )


def _read_pdf_pages(uploaded_file) -> tuple[bytes, int]:
    uploaded_file.seek(0)
    pdf_bytes = uploaded_file.read()
    page_count = len(PdfReader(io.BytesIO(pdf_bytes)).pages)
    uploaded_file.seek(0)
    return pdf_bytes, page_count


if current_page == "Settings":
    st.markdown(
        page_header(
            "Settings",
            "This build extracts embedded PDF text only. Scanned-page OCR waits for a future approved engine.",
        ),
        unsafe_allow_html=True,
    )
    settings = load_settings(database)
    with st.form("settings-form"):
        acceptance = st.number_input(
            "Acceptance threshold",
            0.0,
            100.0,
            float(settings["acceptance_threshold"]),
        )
        max_pages = st.number_input(
            "Maximum PDF pages", 1, 5000, int(settings["max_pdf_pages"])
        )
        storage_root = st.text_input(
            "Storage root", value=str(settings["storage_root"])
        )
        enabled_engines = st.multiselect(
            "Enabled extraction engines",
            list(DEFAULT_SETTINGS["enabled_engines"]),
            default=[
                engine
                for engine in settings["enabled_engines"]
                if engine in DEFAULT_SETTINGS["enabled_engines"]
            ],
        )
        if st.form_submit_button("Save settings", type="primary"):
            save_settings(
                database,
                {
                    "acceptance_threshold": acceptance,
                    "max_pdf_pages": max_pages,
                    "storage_root": storage_root,
                    "enabled_engines": enabled_engines,
                },
            )
            st.success("Settings saved.")
    st.stop()

if current_page == "Statistics":
    st.markdown(
        page_header("Statistics", "Local conversion summary."), unsafe_allow_html=True
    )
    stats = database.statistics(username)
    cols = st.columns(4)
    cols[0].metric("Total", int(stats.get("total") or 0))
    cols[1].metric("Completed", int(stats.get("completed") or 0))
    cols[2].metric("Manual review", int(stats.get("below_text_threshold") or 0))
    cols[3].metric("Success rate", f"{float(stats.get('success_rate') or 0):.1f}%")
    st.stop()

if current_page == "System status":
    st.markdown(page_header("System status", "Runtime health."), unsafe_allow_html=True)
    st.json(system_health(database, runtime.storage_root))
    st.stop()

if current_page in {"My files", "Conversion history"}:
    st.markdown(
        page_header(current_page, "Stored conversion records."), unsafe_allow_html=True
    )
    rows = database.list_conversions(username, include_hidden=False)
    if not rows:
        st.info("No conversions yet.")
    else:
        st.dataframe(rows, use_container_width=True)
    st.stop()

if current_page == "Correction memory":
    st.markdown(
        page_header(
            "Correction memory",
            "Correction learning remains available, but no OCR model is selected yet.",
        ),
        unsafe_allow_html=True,
    )
    st.json(database.correction_readiness())
    st.stop()

st.markdown(
    page_header(
        "Convert PDF to Word",
        "Upload a born-digital PDF with embedded text. Scanned pages are marked for a future OCR engine.",
    ),
    unsafe_allow_html=True,
)

upload_col, info_col = st.columns([1.05, 1], gap="large")
with upload_col:
    with st.container(border=True):
        st.markdown(
            section_title("Upload", "Choose one PDF file.", step=1),
            unsafe_allow_html=True,
        )
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type=["pdf"],
            accept_multiple_files=False,
            label_visibility="collapsed",
        )

pdf_bytes = b""
total_pdf_pages = 0
upload_error = ""
if uploaded_file:
    try:
        pdf_bytes, total_pdf_pages = _read_pdf_pages(uploaded_file)
        validate_pdf_limits(len(pdf_bytes), total_pdf_pages, limits=DEFAULT_LIMITS)
    except ValueError as exc:
        upload_error = str(exc)
    except Exception:
        upload_error = "Invalid or unreadable PDF file."
    st.markdown(
        file_summary(uploaded_file.name, uploaded_file.size, total_pdf_pages),
        unsafe_allow_html=True,
    )
    if upload_error:
        st.error(upload_error)
else:
    st.markdown(
        empty_state("No PDF selected", "Upload one PDF to begin."),
        unsafe_allow_html=True,
    )

with info_col:
    with st.container(border=True):
        st.markdown(
            section_title("Document", "Name the DOCX output.", step=2),
            unsafe_allow_html=True,
        )
        book_name = st.text_input("Output name", placeholder="Example: annual-report")

ranges: list[tuple[int, int]] = []
selected_pages: list[int] = []
selection_error = ""
settings_col, range_col = st.columns(2, gap="large")
with range_col:
    with st.container(border=True):
        st.markdown(
            section_title("Pages", "Select pages to include.", step=3),
            unsafe_allow_html=True,
        )
        range_mode = st.radio(
            "Selection mode",
            ["All pages", "Range", "Separate pages"],
            horizontal=True,
        )
        max_page = max(1, total_pdf_pages or 1)
        page_start = page_end = 1
        separate_pages = ""
        if range_mode == "Range":
            start_col, end_col = st.columns(2)
            page_start = start_col.number_input(
                "From page", min_value=1, max_value=max_page, value=1
            )
            page_end = end_col.number_input(
                "To page", min_value=1, max_value=max_page, value=max_page
            )
        elif range_mode == "Separate pages":
            separate_pages = st.text_input(
                "Page numbers", placeholder="Example: 1, 3, 7"
            )
        if total_pdf_pages:
            try:
                ranges, selected_pages = select_pages(
                    range_mode,
                    total_pdf_pages,
                    start=int(page_start),
                    end=int(page_end),
                    separate=separate_pages,
                )
                st.caption(
                    f"{len(selected_pages)} page(s) selected from {total_pdf_pages}."
                )
            except ValueError as exc:
                selection_error = str(exc)
                st.error(selection_error)

with settings_col:
    with st.container(border=True):
        st.markdown(
            section_title(
                "Pipeline",
                "Direct PDF text extraction only. OCR waits for a future approved model.",
                step=4,
            ),
            unsafe_allow_html=True,
        )
        st.info("No OCR model or AMD ROCm support is claimed in this build.")

run_disabled = (
    not uploaded_file
    or bool(upload_error)
    or not selected_pages
    or bool(selection_error)
)
st.markdown(section_title("Run", "Start conversion.", step=5), unsafe_allow_html=True)
run = st.button(
    "Start conversion", type="primary", use_container_width=True, disabled=run_disabled
)

if run:
    from pdfword.ocr_pipeline import process_pdf

    assert uploaded_file is not None

    class SilentProgress:
        def progress(self, *_args, **_kwargs) -> None:
            return None

    class SilentStatus:
        def info(self, *_args, **_kwargs) -> None:
            return None

        def warning(self, *_args, **_kwargs) -> None:
            return None

        def success(self, *_args, **_kwargs) -> None:
            return None

    started_at = time.perf_counter()
    output_filename = build_output_filename(
        book_name or uploaded_file.name.rsplit(".", 1)[0], ranges
    )
    ensure_disk_space(runtime.storage_root, len(pdf_bytes) * 3)
    job_storage = create_job_storage(
        username, uploaded_file.name, output_filename, root=runtime.storage_root
    )
    save_job_files(job_storage, pdf_bytes, b"")
    conversion_id = database.create_conversion(
        {
            "job_id": job_storage.job_id,
            "username": username,
            "original_pdf_name": uploaded_file.name,
            "stored_pdf_path": str(job_storage.pdf_path),
            "output_docx_name": output_filename,
            "stored_docx_path": str(job_storage.docx_path),
            "page_from": min(selected_pages),
            "page_to": max(selected_pages),
            "page_numbers": json.dumps(selected_pages),
            "status": "processing",
            "created_at": utc_now(),
            "updated_at": utc_now(),
        }
    )
    page_results, _ = process_pdf(
        pdf_bytes=pdf_bytes,
        from_page=None,
        to_page=None,
        page_numbers=selected_pages,
        progress_bar=SilentProgress(),
        status_placeholder=SilentStatus(),
    )
    docx_bytes = markdown_to_docx(page_results)
    job_storage.docx_path.write_bytes(docx_bytes)
    manual_review = any(page.requires_manual_review for page in page_results)
    scores = [
        page.text_quality_score
        for page in page_results
        if page.text_quality_score is not None
    ]
    database.update_conversion(
        conversion_id,
        {
            "file_type": "mixed" if manual_review else "digital",
            "text_quality_score": sum(scores) / len(scores) if scores else None,
            "layout_quality_score": None,
            "final_quality_score": None,
            "winning_engine": "direct_pdf_text",
            "processing_time": time.perf_counter() - started_at,
            "status": "manual_review" if manual_review else "completed",
            "updated_at": utc_now(),
        },
    )
    st.success(
        "DOCX created."
        if not manual_review
        else "DOCX created with pages requiring future OCR."
    )
    st.download_button(
        "Download DOCX",
        docx_bytes,
        file_name=output_filename,
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
