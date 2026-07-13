from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from pdfword.ranges import select_pages
from pdfword.ui_components import (
    file_summary,
    load_styles,
    processing_panel,
    status_strip,
)
from pdfword.ui_status import UiSystemStatus, fetch_system_status, parse_health_payload


def test_range_10_to_15_has_six_pages():
    ranges, pages = select_pages("Range", 20, start=10, end=15)
    assert ranges == [(10, 15)]
    assert pages == [10, 11, 12, 13, 14, 15]


@pytest.mark.parametrize(
    "kwargs",
    [
        {"start": 5, "end": 2},
        {"start": 0, "end": 2},
        {"start": 1, "end": 21},
    ],
)
def test_invalid_ranges_are_rejected(kwargs):
    with pytest.raises(ValueError):
        select_pages("Range", 20, **kwargs)


def test_page_selection_is_independent_from_parallelism():
    _, pages = select_pages("Separate pages", 20, separate="1, 4, 9")
    parallel_pages = 2
    assert pages == [1, 4, 9]
    assert parallel_pages != len(pages)


def test_worker_and_tools_status_are_visible_without_secrets():
    status = parse_health_payload(
        {
            "status": "ok",
            "redis_available": True,
            "cloud_available": False,
            "workers": [{"worker_name": "windows-worker-1", "state": "ready"}],
        }
    )
    html = status_strip(
        status.as_dict(), direct_text_ready=True, future_ocr_ready=False
    )
    assert "Worker" in html
    assert "Direct PDF text" in html
    assert "Future OCR" in html
    assert "WORKER_API_KEY" not in html
    assert "OPENROUTER_API_KEY" not in html


def test_offline_worker_status():
    status = parse_health_payload(
        {
            "status": "ok",
            "redis_available": True,
            "workers": [],
            "cloud_available": False,
        }
    )
    assert status.worker_state == "offline"
    assert status.cloud is False


def test_legacy_server_uses_redis_and_marks_cloud_unknown():
    status = parse_health_payload(
        {"status": "ok", "role": "server"},
        legacy_status=True,
        redis_available=True,
    )
    assert status.server is True
    assert status.redis is True
    assert status.worker_state == "ready"
    assert status.cloud is None
    assert status.service_status_outdated is True
    html = status_strip(status.as_dict())
    assert "Status Center" in html
    assert "Worker" in html


def test_status_fetch_detects_legacy_404():
    class Response:
        def __init__(self, status_code, payload=None):
            self.status_code = status_code
            self._payload = payload or {}

        def raise_for_status(self):
            if self.status_code >= 400 and self.status_code != 404:
                raise RuntimeError(self.status_code)

        def json(self):
            return self._payload

    class Requester:
        @staticmethod
        def get(url, **_kwargs):
            if url.endswith("/internal/health"):
                return Response(200, {"status": "ok", "role": "server"})
            return Response(404)

    status = fetch_system_status(
        "http://server",
        "test-key",
        Requester,
        redis_available=True,
    )
    assert status.worker_state == "ready"
    assert status.cloud is None
    assert status.service_status_outdated is True


def test_status_fetch_falls_back_to_public_health_for_local_processing():
    class Response:
        def __init__(self, status_code, payload=None):
            self.status_code = status_code
            self._payload = payload or {}

        def raise_for_status(self):
            if self.status_code >= 400:
                raise RuntimeError(self.status_code)

        def json(self):
            return self._payload

    class Requester:
        @staticmethod
        def get(url, **_kwargs):
            if url.endswith("/internal/health"):
                return Response(401)
            return Response(
                200,
                {
                    "status": "ok",
                    "role": "server",
                    "local_processing_enabled": True,
                },
            )

    status = fetch_system_status("http://server", "stale-key", Requester)
    assert status.server is True
    assert status.worker_state == "ready"
    assert status.worker_count == 1


def test_ui_html_escapes_uploaded_filename():
    rendered = file_summary('<script>alert("x")</script>.pdf', 100, 1)
    assert "<script>" not in rendered
    assert "&lt;script&gt;" in rendered


def test_styles_support_rtl_and_mobile():
    css = Path("assets/styles.css").read_text(encoding="utf-8")
    assert "@media (max-width: 800px)" in css
    assert "@media (max-width: 430px)" in css
    assert "--ui-primary: #2563eb" in css
    rendered = load_styles()
    assert rendered.startswith("<style>")
    key_prefix = "sk" + "-or-"
    assert key_prefix not in rendered


def test_navigation_reaches_settings_and_statistics_pages():
    source = Path("app.py").read_text(encoding="utf-8-sig")
    assert '"Settings"' in source
    assert '"Statistics"' in source
    nav_line = next(
        line for line in source.splitlines() if line.startswith("nav_options = [")
    )
    nav_block = source[source.index(nav_line) : source.index("nav_labels = {")]
    assert '"Settings"' in nav_block
    assert '"Statistics"' in nav_block


def test_windows_bat_wrappers_use_script_directory_and_bypass_policy():
    for name, script in {
        "start_clouda_all.bat": "start_clouda_all.ps1",
        "stop_clouda_all.bat": "stop_clouda_all.ps1",
    }.items():
        content = Path(name).read_text(encoding="utf-8")
        assert "%~dp0" in content
        assert "-ExecutionPolicy Bypass" in content
        assert script in content
        assert "D:\\clouda" not in content


def test_processing_panel_is_user_facing_and_accessible():
    rendered = processing_panel(
        stage="Digital text extraction",
        progress=42,
        completed_pages=2,
        total_pages=5,
        elapsed="12 seconds",
        last_update="12:30:04",
    )
    assert "Digital text extraction" in rendered
    assert "42%" in rendered
    assert ".env" not in rendered
    assert "Redis" not in rendered


def test_processing_panel_shows_live_indeterminate_state():
    rendered = processing_panel(
        stage="Digital text extraction",
        progress=None,
        completed_pages=0,
        total_pages=5,
        elapsed="3 seconds",
        last_update="12:30:04",
    )
    assert "indeterminate" in rendered
    assert "12:30:04" in rendered


def test_status_dataclass_defaults_are_safe():
    status = UiSystemStatus()
    assert status.worker_state == "offline"
    assert status.cloud is False


def test_streamlit_conversion_page_smoke(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "ui.sqlite3"))
    monkeypatch.setenv("SERVER_BASE_URL", "http://127.0.0.1:59999")
    monkeypatch.setenv("WORKER_API_KEY", "test-only-worker-key")
    app = AppTest.from_file("app.py", default_timeout=20)
    app.run()
    assert not app.exception
    assert len(app.file_uploader) == 1
    assert not any(widget.key == "login_username" for widget in app.text_input)
    labels = [widget.label for widget in app.radio]
    assert "Navigation" in labels
    assert "Selection mode" in labels
    visible_text = " ".join(
        str(element.value)
        for element in [*app.markdown, *app.caption, *app.info, *app.warning]
    )
    assert "OPENROUTER_API_KEY" not in visible_text
    assert "WORKER_API_KEY" not in visible_text
    navigation = next(widget for widget in app.radio if widget.label == "Navigation")
    navigation.set_value("System status").run()
    assert not app.exception
