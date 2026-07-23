import ast
import io
import json
import sys
import zipfile
from pathlib import Path

import fakeredis
import pytest
import requests
from fastapi.testclient import TestClient
from rq import Queue

from pdfword.database import Database, utc_now
from pdfword.job_queue import DistributedJobQueue
from pdfword.worker_client import WorkerApiClient
from pdfword.worker_api import app
from pdfword import worker_tasks

API_KEY = "test-worker-secret"


def valid_docx_bytes() -> bytes:
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "[Content_Types].xml",
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>',
        )
        archive.writestr(
            "word/document.xml",
            '<document xmlns="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>',
        )
    return output.getvalue()


def create_job(database: Database, storage: Path, job_id: str = "job-a") -> dict:
    job_root = storage / "alice" / job_id
    job_root.mkdir(parents=True)
    pdf = job_root / "input.pdf"
    pdf.write_bytes(b"%PDF-1.4 test")
    docx = job_root / "output.docx"
    database.create_conversion(
        {
            "job_id": job_id,
            "username": "alice",
            "original_pdf_name": "input.pdf",
            "stored_pdf_path": str(pdf),
            "output_docx_name": "output.docx",
            "stored_docx_path": str(docx),
            "page_from": 1,
            "page_to": 1,
            "page_numbers": "[1]",
            "status": "pending",
            "created_at": utc_now(),
            "updated_at": utc_now(),
        }
    )
    result = database.get_conversion(job_id)
    assert result is not None
    return result


@pytest.fixture
def api_environment(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    storage = tmp_path / "storage"
    database_path = tmp_path / "clouda.sqlite3"
    monkeypatch.setenv("APP_ROLE", "server")
    monkeypatch.setenv("WORKER_API_KEY", API_KEY)
    monkeypatch.setenv("STORAGE_ROOT", str(storage))
    monkeypatch.setenv("DATABASE_PATH", str(database_path))
    database = Database(database_path)
    return TestClient(app), database, storage


def test_rq_payload_contains_only_job_id(monkeypatch: pytest.MonkeyPatch):
    redis = fakeredis.FakeRedis()
    queue = Queue("pdf_conversion", connection=redis)
    backend = DistributedJobQueue()
    monkeypatch.setattr(backend, "_queue", lambda: queue)

    job = backend.enqueue("job-only-id")

    assert job.args == ("job-only-id",)
    assert "clouda" not in json.dumps(job.kwargs).lower()


def test_redis_failure_does_not_remove_pending_database_job(tmp_path: Path):
    database = Database(tmp_path / "db.sqlite3")
    storage = tmp_path / "storage"
    create_job(database, storage)

    conversion = database.get_conversion("job-a")
    assert conversion is not None
    assert conversion["status"] == "pending"
    assert (storage / "alice" / "job-a" / "input.pdf").is_file()


def test_api_requires_worker_key(api_environment):
    client, database, storage = api_environment
    create_job(database, storage)

    assert client.get("/internal/jobs/job-a").status_code == 401
    assert (
        client.get(
            "/internal/jobs/job-a", headers={"X-Worker-API-Key": "wrong"}
        ).status_code
        == 401
    )
    assert (
        client.get(
            "/internal/jobs/job-a", headers={"X-Worker-API-Key": API_KEY}
        ).status_code
        == 200
    )


def test_public_health_reports_local_processing_without_worker_key(
    api_environment, monkeypatch: pytest.MonkeyPatch
):
    client, _database, _storage = api_environment
    monkeypatch.setenv("LOCAL_PROCESSING_ENABLED", "true")

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "role": "server",
        "local_processing_enabled": True,
    }
    assert API_KEY not in response.text


def test_worker_cloud_status_is_reported_without_exposing_key(
    api_environment, monkeypatch: pytest.MonkeyPatch
):
    client, _database, _storage = api_environment
    redis = fakeredis.FakeRedis()
    monkeypatch.setattr("redis.Redis.from_url", lambda *_args, **_kwargs: redis)
    headers = {"X-Worker-API-Key": API_KEY}

    reported = client.post(
        "/internal/workers/status",
        headers=headers,
        json={
            "worker_name": "windows-worker-1",
            "cloud_available": True,
            "cloud_provider": "openrouter",
        },
    )
    assert reported.status_code == 200

    health = client.get("/internal/health", headers=headers)
    assert health.status_code == 200
    payload = health.json()
    assert payload["cloud_available"] is True
    assert payload["workers"][0]["cloud_provider"] == "openrouter"
    assert API_KEY not in health.text


def test_worker_status_get_reports_registered_workers(
    api_environment, monkeypatch: pytest.MonkeyPatch
):
    client, _database, _storage = api_environment
    redis = fakeredis.FakeRedis()
    monkeypatch.setattr("redis.Redis.from_url", lambda *_args, **_kwargs: redis)
    headers = {"X-Worker-API-Key": API_KEY}

    client.post(
        "/internal/workers/status",
        headers=headers,
        json={
            "worker_name": "windows-worker-1",
            "cloud_available": False,
            "cloud_provider": "",
        },
    )
    response = client.get("/internal/workers/status", headers=headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["redis_available"] is True
    assert payload["workers"][0]["worker_name"] == "windows-worker-1"


@pytest.mark.parametrize("error_type", [ConnectionError, TimeoutError])
def test_worker_status_degrades_when_redis_is_unavailable(
    api_environment, monkeypatch: pytest.MonkeyPatch, error_type
):
    client, _database, _storage = api_environment

    class BrokenRedis:
        def ping(self):
            raise error_type("redis unavailable")

        def set(self, *_args, **_kwargs):
            raise error_type("redis unavailable")

    monkeypatch.setattr("redis.Redis.from_url", lambda *_args, **_kwargs: BrokenRedis())
    headers = {"X-Worker-API-Key": API_KEY}

    get_response = client.get("/internal/workers/status", headers=headers)
    post_response = client.post(
        "/internal/workers/status",
        headers=headers,
        json={
            "worker_name": "windows-worker-1",
            "cloud_available": True,
            "cloud_provider": "openrouter",
        },
    )

    for response in (get_response, post_response):
        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "degraded"
        assert payload["redis_available"] is False
        assert payload["workers"] == []
        assert "local conversion remains available" in payload["message"]


def test_worker_api_full_status_flow(api_environment):
    client, database, storage = api_environment
    create_job(database, storage)
    headers = {"X-Worker-API-Key": API_KEY}

    started = client.post(
        "/internal/jobs/job-a/start", headers=headers, json={"worker_name": "worker-1"}
    )
    assert started.status_code == 200
    assert database.get_conversion("job-a")["status"] == "processing"
    assert database.get_conversion("job-a")["attempt_count"] == 1

    heartbeat = client.post(
        "/internal/jobs/job-a/heartbeat",
        headers=headers,
        json={"worker_name": "worker-1"},
    )
    assert heartbeat.status_code == 200

    metadata = {
        "status": "manual_review",
        "file_type": "scan",
        "text_quality_score": 70,
        "layout_quality_score": 80,
        "final_quality_score": 75,
        "winning_engine": "pending:future_ocr_engine",
        "processing_time": 2.5,
        "cloud_attempts": [
            {
                "provider": "openrouter",
                "model": "openai/gpt-5-mini",
                "latency_ms": 1250,
                "prompt_tokens": 120,
                "completion_tokens": 40,
                "cost": 0.002,
                "cost_is_estimated": 0,
                "score": 70,
                "failure_reason": "quality below threshold",
            }
        ],
        "cost_limit_reached": True,
    }
    uploaded = client.post(
        "/internal/jobs/job-a/result",
        headers=headers,
        data={"worker_name": "worker-1", "metadata": json.dumps(metadata)},
        files={
            "result": (
                "result.docx",
                io.BytesIO(valid_docx_bytes()),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )
    assert uploaded.status_code == 200
    row = database.get_conversion("job-a")
    assert row["status"] == "manual_review"
    assert "cost limit" in row["error_message"].lower()
    attempts = database.list_attempts(row["id"])
    assert attempts[-1]["model_name"] == "openai/gpt-5-mini"
    assert attempts[-1]["prompt_tokens"] == 120
    assert attempts[-1]["completion_tokens"] == 40
    assert attempts[-1]["cost"] == pytest.approx(0.002)
    assert attempts[-1]["quality_score"] == 70
    assert attempts[-1]["failure_reason"] == "quality below threshold"
    assert Path(row["stored_docx_path"]).read_bytes().startswith(b"PK")


def test_api_rejects_path_outside_storage(api_environment, tmp_path: Path):
    client, database, storage = api_environment
    outside = tmp_path / "outside.pdf"
    outside.write_bytes(b"%PDF")
    row = create_job(database, storage)
    database.update_conversion(row["id"], {"status": "pending"})
    with database.transaction() as connection:
        connection.execute(
            "UPDATE conversions SET stored_pdf_path = ? WHERE job_id = ?",
            (str(outside), "job-a"),
        )

    response = client.get(
        "/internal/jobs/job-a/input", headers={"X-Worker-API-Key": API_KEY}
    )
    assert response.status_code == 403


def test_database_rejects_invalid_final_transition(tmp_path: Path):
    database = Database(tmp_path / "db.sqlite3")
    create_job(database, tmp_path / "storage")
    database.transition_conversion("job-a", "processing", worker_name="worker")
    database.transition_conversion("job-a", "completed")

    with pytest.raises(ValueError, match="Invalid status transition"):
        database.transition_conversion("job-a", "processing", worker_name="worker")


def test_server_entry_has_no_heavy_worker_imports():
    tree = ast.parse(Path("app.py").read_text(encoding="utf-8-sig"))
    top_imports = []
    for node in tree.body:
        if isinstance(node, ast.Import):
            top_imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            top_imports.append(node.module or "")
    assert "pdfword.ocr_pipeline" not in top_imports
    assert "pdfword.conversion_service" not in top_imports


def test_server_modules_do_not_load_ocr():
    before = set(sys.modules)
    __import__("pdfword.worker_api")
    __import__("pdfword.health")
    loaded = set(sys.modules) - before
    assert "pdfword.ocr_pipeline" not in loaded
    assert "pdfword.ocr_pipeline" not in loaded


def test_worker_downloads_converts_uploads_and_cleans_temp(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    events = []

    class FakeClient:
        def start(self, job_id, worker_name):
            events.append(("start", job_id))
            return {
                "page_numbers": [1],
                "fast_model": "fast",
                "accurate_model": "accurate",
                "settings": {},
            }

        def download_input(self, job_id, target):
            events.append(("download", job_id))
            target.write_bytes(b"%PDF")

        def upload_result(self, job_id, worker_name, docx, metadata):
            events.append(("upload", docx.read(), metadata["status"]))
            return {"job_id": job_id, "status": metadata["status"]}

        def heartbeat(self, job_id, worker_name):
            events.append(("heartbeat", job_id))

        def fail(self, job_id, worker_name, error):
            events.append(("fail", error))

    def fake_conversion(request):
        assert request.pdf_path.read_bytes() == b"%PDF"
        request.docx_path.write_bytes(b"PK\x03\x04worker-result")
        return {"status": "completed", "processing_time": 1}

    monkeypatch.setenv("APP_ROLE", "worker")
    monkeypatch.setenv("WORKER_API_KEY", API_KEY)
    monkeypatch.setenv("TEMP_ROOT", str(tmp_path / "temporary"))
    monkeypatch.setattr(worker_tasks, "WorkerApiClient", FakeClient)
    import pdfword.conversion_service as conversion_service

    monkeypatch.setattr(
        conversion_service, "execute_worker_conversion", fake_conversion
    )
    result = worker_tasks.run_remote_job("job-a")

    assert result["status"] == "completed"
    assert [event[0] for event in events] == ["start", "download", "upload"]
    assert list((tmp_path / "temporary").iterdir()) == []


def test_worker_reports_failure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    failures = []

    class FakeClient:
        def start(self, job_id, worker_name):
            return {
                "page_numbers": [1],
                "fast_model": "fast",
                "accurate_model": "accurate",
                "settings": {},
            }

        def download_input(self, job_id, target):
            target.write_bytes(b"%PDF")

        def heartbeat(self, job_id, worker_name):
            return None

        def fail(self, job_id, worker_name, error):
            failures.append((job_id, error))

    monkeypatch.setenv("APP_ROLE", "worker")
    monkeypatch.setenv("WORKER_API_KEY", API_KEY)
    monkeypatch.setenv("TEMP_ROOT", str(tmp_path / "temporary"))
    monkeypatch.setattr(worker_tasks, "WorkerApiClient", FakeClient)
    import pdfword.conversion_service as conversion_service

    monkeypatch.setattr(
        conversion_service,
        "execute_worker_conversion",
        lambda _request: (_ for _ in ()).throw(RuntimeError("OCR failed")),
    )
    with pytest.raises(RuntimeError, match="OCR failed"):
        worker_tasks.run_remote_job("job-a")
    assert failures == [("job-a", "OCR failed")]
    assert list((tmp_path / "temporary").iterdir()) == []


def test_worker_status_404_is_treated_as_legacy_server(
    monkeypatch: pytest.MonkeyPatch,
):
    response = requests.Response()
    response.status_code = 404
    response.url = "http://server/internal/workers/status"

    def fake_request(*_args, **_kwargs):
        return response

    monkeypatch.setenv("SERVER_BASE_URL", "http://server")
    monkeypatch.setenv("WORKER_API_KEY", API_KEY)
    monkeypatch.setattr(requests, "request", fake_request)

    result = WorkerApiClient().report_status("windows-worker-1", True, "openrouter")

    assert result == {"status": "unsupported", "legacy_server": True}
