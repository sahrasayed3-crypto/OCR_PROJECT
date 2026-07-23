import io
import json
import time

import streamlit as st
from pypdf import PdfReader

from pdfword.database import Database, utc_now
from pdfword.docx_export import markdown_to_docx
from pdfword.health import system_health
from pdfword.limits import DEFAULT_LIMITS, limits_from_env, validate_pdf_limits
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
    processing_panel,
    progress_steps,
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
    <div class="topbar brand-row">
      <div class="brand"><div class="brand-mark">C</div>
        <div><strong>Clouda PDF</strong><small>منصة تحويل PDF العربية</small></div>
      </div>
      <div class="local-pill">تشغيل محلي آمن</div>
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
nav_labels.update(
    {
        "Convert": "الرئيسية",
        "My files": "ملفاتي",
        "Conversion history": "التحويلات السابقة",
        "Correction memory": "ذاكرة التصحيح",
        "Statistics": "الإحصاءات",
        "Settings": "الإعدادات",
        "System status": "حالة النظام",
    }
)

with st.sidebar:
    st.markdown("## Clouda PDF")
    st.caption("PDF إلى DOCX قابل للتحرير")
    current_page = st.radio(
        "Navigation",
        nav_options,
        format_func=lambda value: nav_labels[value],
        key="main_navigation",
    )


def _read_pdf_pages(uploaded_file) -> tuple[bytes, int]:
    uploaded_file.seek(0)
    limits = limits_from_env()
    output = io.BytesIO()
    total = 0
    while chunk := uploaded_file.read(1024 * 1024):
        total += len(chunk)
        if total > limits.max_upload_bytes:
            raise ValueError("PDF exceeds the configured upload byte limit.")
        output.write(chunk)
    pdf_bytes = output.getvalue()
    page_count = len(PdfReader(io.BytesIO(pdf_bytes)).pages)
    validate_pdf_limits(len(pdf_bytes), page_count, limits=limits)
    uploaded_file.seek(0)
    return pdf_bytes, page_count


if current_page == "Settings":
    st.markdown(
        page_header(
            "الإعدادات",
            "هذه النسخة تستخرج النصوص المضمنة في PDF فقط، وتترك OCR للصفحات المصورة لمحرك معتمد لاحقًا.",
        ),
        unsafe_allow_html=True,
    )
    settings = load_settings(database)
    with st.form("settings-form"):
        acceptance = st.number_input(
            "حد القبول",
            0.0,
            100.0,
            float(settings["acceptance_threshold"]),
        )
        max_pages = st.number_input(
            "الحد الأقصى لصفحات PDF", 1, 5000, int(settings["max_pdf_pages"])
        )
        storage_root = st.text_input(
            "مسار التخزين", value=str(settings["storage_root"])
        )
        enabled_engines = st.multiselect(
            "محركات الاستخراج المفعّلة",
            list(DEFAULT_SETTINGS["enabled_engines"]),
            default=[
                engine
                for engine in settings["enabled_engines"]
                if engine in DEFAULT_SETTINGS["enabled_engines"]
            ],
        )
        if st.form_submit_button("حفظ الإعدادات", type="primary"):
            save_settings(
                database,
                {
                    "acceptance_threshold": acceptance,
                    "max_pdf_pages": max_pages,
                    "storage_root": storage_root,
                    "enabled_engines": enabled_engines,
                },
            )
            st.success("تم حفظ الإعدادات.")
    st.stop()

if current_page == "Statistics":
    st.markdown(
        page_header("الإحصاءات", "ملخص التحويلات المحلية."), unsafe_allow_html=True
    )
    stats = database.statistics(username)
    cols = st.columns(4)
    cols[0].metric("الإجمالي", int(stats.get("total") or 0))
    cols[1].metric("المكتملة", int(stats.get("completed") or 0))
    cols[2].metric("تحتاج مراجعة", int(stats.get("below_text_threshold") or 0))
    cols[3].metric("معدل النجاح", f"{float(stats.get('success_rate') or 0):.1f}%")
    st.stop()

if current_page == "System status":
    st.markdown(
        page_header("حالة النظام", "صحة التشغيل الحالية."), unsafe_allow_html=True
    )
    st.json(system_health(database, runtime.storage_root))
    st.stop()

if current_page in {"My files", "Conversion history"}:
    st.markdown(
        page_header(nav_labels[current_page], "سجلات التحويل المحفوظة."),
        unsafe_allow_html=True,
    )
    rows = database.list_conversions(username, include_hidden=False)
    if not rows:
        st.info("لا توجد تحويلات بعد.")
    else:
        st.dataframe(rows, use_container_width=True)
    st.stop()

if current_page == "Correction memory":
    st.markdown(
        page_header(
            "ذاكرة التصحيح",
            "تعلم التصحيحات متاح، لكن لم يتم تفعيل محرك OCR نهائي بعد.",
        ),
        unsafe_allow_html=True,
    )
    st.json(database.correction_readiness())
    st.stop()

st.markdown(
    page_header(
        "حوّل PDF إلى Word قابل للتحرير",
        "ارفع ملف PDF يحتوي على نص مدمج. الصفحات المصورة تُحفظ للمراجعة ومحرك OCR مستقبلي.",
    ),
    unsafe_allow_html=True,
)

upload_col, info_col = st.columns([1.05, 1], gap="large")
with upload_col:
    with st.container(border=True):
        st.markdown(
            section_title("رفع الملفات", "اختر ملف PDF واحدًا.", step=1),
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
        empty_state("لا يوجد ملف محدد", "ارفع ملف PDF واحدًا للبدء."),
        unsafe_allow_html=True,
    )

with info_col:
    with st.container(border=True):
        st.markdown(
            section_title("المستند", "سمّ ملف DOCX الناتج.", step=2),
            unsafe_allow_html=True,
        )
        book_name = st.text_input(
            "اسم ملف Word الناتج", placeholder="مثال: annual-report"
        )

ranges: list[tuple[int, int]] = []
selected_pages: list[int] = []
selection_error = ""
settings_col, range_col = st.columns(2, gap="large")
with range_col:
    with st.container(border=True):
        st.markdown(
            section_title("الصفحات", "اختر الصفحات التي تريد تضمينها.", step=3),
            unsafe_allow_html=True,
        )
        range_mode = st.radio(
            "Selection mode",
            ["All pages", "Range", "Separate pages"],
            format_func=lambda value: {
                "All pages": "كل الصفحات",
                "Range": "نطاق",
                "Separate pages": "صفحات محددة",
            }[value],
            horizontal=True,
        )
        max_page = max(1, total_pdf_pages or 1)
        page_start = page_end = 1
        separate_pages = ""
        if range_mode == "Range":
            start_col, end_col = st.columns(2)
            page_start = start_col.number_input(
                "من صفحة", min_value=1, max_value=max_page, value=1
            )
            page_end = end_col.number_input(
                "إلى صفحة", min_value=1, max_value=max_page, value=max_page
            )
        elif range_mode == "Separate pages":
            separate_pages = st.text_input("أرقام الصفحات", placeholder="مثال: 1, 3, 7")
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
                    f"تم اختيار {len(selected_pages)} صفحة من أصل {total_pdf_pages}."
                )
            except ValueError as exc:
                selection_error = str(exc)
                st.error(selection_error)

with settings_col:
    with st.container(border=True):
        st.markdown(
            section_title(
                "إعدادات التحويل",
                "استخراج النص المباشر فقط. OCR ينتظر نموذجًا معتمدًا لاحقًا.",
                step=4,
            ),
            unsafe_allow_html=True,
        )
        st.info("لا تدّعي هذه النسخة وجود محرك OCR أو دعم AMD ROCm في التشغيل الحالي.")

run_disabled = (
    not uploaded_file
    or bool(upload_error)
    or not selected_pages
    or bool(selection_error)
)
st.markdown(
    section_title("التشغيل", "ابدأ التحويل وراقب الحالة.", step=5),
    unsafe_allow_html=True,
)
run = st.button(
    "ابدأ التحويل الذكي",
    type="primary",
    use_container_width=True,
    disabled=run_disabled,
)
st.markdown(
    progress_steps(active_index=0 if not uploaded_file else 1), unsafe_allow_html=True
)
progress_placeholder = st.empty()

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
    progress_placeholder.markdown(
        processing_panel(
            stage="استخراج النص المباشر",
            progress=None,
            completed_pages=0,
            total_pages=len(selected_pages),
            elapsed="0 ثانية",
            last_update=time.strftime("%H:%M:%S"),
        ),
        unsafe_allow_html=True,
    )
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
    elapsed_seconds = time.perf_counter() - started_at
    progress_placeholder.markdown(
        processing_panel(
            stage="اكتمل إنشاء ملف Word",
            progress=100,
            completed_pages=len(selected_pages),
            total_pages=len(selected_pages),
            elapsed=f"{elapsed_seconds:.1f} ثانية",
            last_update=time.strftime("%H:%M:%S"),
        ),
        unsafe_allow_html=True,
    )
    st.success(
        "تم إنشاء ملف DOCX."
        if not manual_review
        else "تم إنشاء ملف DOCX مع صفحات تحتاج OCR مستقبليًا."
    )
    st.download_button(
        "تنزيل ملف Word",
        docx_bytes,
        file_name=output_filename,
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
