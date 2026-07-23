import hmac
import json
import os
import re
import tempfile
import zipfile
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse, Response
from pydantic import BaseModel, Field
from starlette.middleware.trustedhost import TrustedHostMiddleware

from clouda_contracts.archive_security import ArchiveLimits, validate_zip_archive
from .constants import MODEL_ACCURATE_PRIMARY, MODEL_FAST
from .database import Database, utc_now
from .limits import limits_from_env
from .settings import load_settings, runtime_settings
from .correction_learning import rules_checksum
from .operations import (
    OperationsMetrics,
    RedisSecurityConfig,
    SlidingWindowRateLimiter,
    structured_log,
)

JOB_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")
app = FastAPI(title="Clouda Worker API", docs_url=None, redoc_url=None)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        host.strip()
        for host in os.getenv(
            "CLOUDA_ALLOWED_HOSTS", "127.0.0.1,localhost,testserver"
        ).split(",")
        if host.strip()
    ],
)
_rate_limiter = SlidingWindowRateLimiter(
    limit=max(1, int(os.getenv("CLOUDA_INTERNAL_RATE_LIMIT_PER_MINUTE", "120")))
)
_operations_metrics = OperationsMetrics()


@app.middleware("http")
async def security_headers(request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    client = request.client.host if request.client else "unknown"
    if not _rate_limiter.allow(client):
        structured_log("rate_limit_exceeded", request_id=request_id, client=client)
        return JSONResponse(
            {"detail": "Rate limit exceeded", "request_id": request_id},
            status_code=429,
            headers={"X-Request-ID": request_id, "Retry-After": "60"},
        )
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["X-Request-ID"] = request_id
    _operations_metrics.observe_request(request.method, response.status_code)
    structured_log(
        "http_request",
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        status=response.status_code,
    )
    return response


class WorkerMessage(BaseModel):
    worker_name: str = Field(min_length=1, max_length=120)


class FailureMessage(WorkerMessage):
    error: str = Field(min_length=1, max_length=2000)


class WorkerStatusMessage(WorkerMessage):
    cloud_available: bool
    cloud_provider: str = Field(default="", max_length=40)


def _database() -> Database:
    return Database(runtime_settings().database_path)


def _authenticate(x_worker_api_key: str | None = Header(default=None)) -> None:
    expected = runtime_settings().worker_api_key
    previous = os.getenv("CLOUDA_WORKER_API_KEY_PREVIOUS", "")
    accepted = [candidate for candidate in (expected, previous) if candidate]
    if (
        not accepted
        or not x_worker_api_key
        or not any(
            hmac.compare_digest(candidate, x_worker_api_key) for candidate in accepted
        )
    ):
        raise HTTPException(status_code=401, detail="Invalid worker credentials")


def _job_id(value: str) -> str:
    if not JOB_ID_RE.fullmatch(value):
        raise HTTPException(status_code=400, detail="Invalid job ID")
    return value


def _inside_storage(path_value: str) -> Path:
    root = runtime_settings().storage_root.resolve()
    path = Path(path_value)
    if not path.is_absolute():
        path = (Path.cwd() / path).resolve()
    else:
        path = path.resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise HTTPException(
            status_code=403, detail="Stored path is outside storage root"
        ) from exc
    return path


def _get_job(job_id: str) -> tuple[Database, dict]:
    database = _database()
    row = database.get_conversion(_job_id(job_id))
    if row is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return database, row


def _redis_client():
    from redis import Redis

    config = RedisSecurityConfig.from_env()
    return Redis.from_url(config.url, **config.client_kwargs())


def _worker_status_payload(*, message: str = "") -> dict:
    workers = []
    try:
        redis = _redis_client()
        redis.ping()
        for key in redis.scan_iter("clouda:worker-status:*", count=100):
            raw = redis.get(key)
            if raw:
                value = json.loads(raw)
                workers.append(
                    {
                        "worker_name": value.get("worker_name", ""),
                        "cloud_available": bool(value.get("cloud_available")),
                        "cloud_provider": value.get("cloud_provider", ""),
                        "reported_at": value.get("reported_at", ""),
                        "state": value.get("state", "ready"),
                    }
                )
        return {
            "status": "ok",
            "redis_available": True,
            "workers": workers,
            "cloud_available": any(worker["cloud_available"] for worker in workers),
            "message": message or "Distributed workers are available.",
        }
    except Exception:
        return {
            "status": "degraded",
            "redis_available": False,
            "workers": [],
            "cloud_available": False,
            "message": (
                "Distributed workers are unavailable; local conversion remains available."
            ),
        }


@app.get("/health")
def public_health() -> dict:
    config = runtime_settings()
    return {
        "status": "ok",
        "role": config.app_role,
        "local_processing_enabled": config.local_processing_enabled,
    }


@app.get("/ready")
def readiness() -> dict:
    try:
        with _database().connect() as connection:
            connection.execute("SELECT 1").fetchone()
        return {"status": "ready"}
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Service is not ready") from exc


@app.get("/internal/metrics", dependencies=[Depends(_authenticate)])
def metrics() -> Response:
    queue_depth = 0
    failed_jobs = 0
    try:
        redis = _redis_client()
        queue_depth = int(redis.llen(f"rq:queue:{runtime_settings().rq_queue_name}"))
        failed_jobs = int(redis.zcard("rq:failed"))
    except Exception:
        pass
    return Response(
        _operations_metrics.prometheus(
            queue_depth=queue_depth, failed_jobs=failed_jobs
        ),
        media_type="text/plain; version=0.0.4",
    )


@app.get("/internal/health", dependencies=[Depends(_authenticate)])
def health() -> dict:
    database = _database()
    with database.connect() as connection:
        connection.execute("SELECT 1").fetchone()
    worker_status = _worker_status_payload()
    return {
        "status": "ok",
        "role": runtime_settings().app_role,
        "workers": worker_status["workers"],
        "cloud_available": worker_status["cloud_available"],
        "redis_available": worker_status["redis_available"],
        "local_processing_enabled": runtime_settings().local_processing_enabled,
        "worker_status": worker_status["status"],
        "message": worker_status["message"],
    }


@app.get("/internal/workers/status", dependencies=[Depends(_authenticate)])
def get_worker_status() -> dict:
    return _worker_status_payload()


@app.post("/internal/workers/status", dependencies=[Depends(_authenticate)])
def update_worker_status(message: WorkerStatusMessage) -> dict:
    payload = {
        "worker_name": message.worker_name,
        "cloud_available": message.cloud_available,
        "cloud_provider": message.cloud_provider if message.cloud_available else "",
        "reported_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        redis = _redis_client()
        redis.set(
            f"clouda:worker-status:{message.worker_name}",
            json.dumps(payload, ensure_ascii=False),
            ex=90,
        )
        return {"status": "ok", "redis_available": True}
    except Exception:
        return _worker_status_payload(
            message="Worker status was not saved because Redis is unavailable."
        )


@app.get("/internal/corrections/snapshot", dependencies=[Depends(_authenticate)])
def correction_snapshot() -> dict:
    config = runtime_settings()
    if not config.correction_memory_enabled:
        rules = []
    else:
        rules = _database().active_memory_rules(
            config.correction_min_source_files,
            config.correction_auto_apply_threshold,
        )
    safe_fields = {
        "id",
        "wrong_text",
        "correct_text",
        "context_pattern",
        "scope",
        "scope_value",
        "language",
        "document_type",
        "confidence",
        "approved",
        "enabled",
        "is_sensitive",
    }
    payload = [{key: row.get(key) for key in safe_fields} for row in rules]
    for row in payload:
        row["threshold"] = config.correction_auto_apply_threshold
    checksum = rules_checksum(payload)
    return {
        "version": f"3:{checksum[:12]}",
        "checksum": checksum,
        "updated_at": max((row.get("updated_at", "") for row in rules), default=""),
        "rules": payload[: config.correction_max_rules_per_page],
    }


@app.get("/internal/jobs/{job_id}", dependencies=[Depends(_authenticate)])
def get_job(job_id: str) -> dict:
    database, row = _get_job(job_id)
    try:
        pages = json.loads(row.get("page_numbers") or "[]")
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=500, detail="Invalid stored page selection"
        ) from exc
    if not pages:
        pages = list(range(int(row["page_from"]), int(row["page_to"]) + 1))
    settings = load_settings(database)
    return {
        "job_id": row["job_id"],
        "status": row["status"],
        "page_numbers": pages,
        "output_docx_name": row["output_docx_name"],
        "fast_model": os.getenv("FAST_MODEL", MODEL_FAST),
        "accurate_model": os.getenv("ACCURATE_MODEL", MODEL_ACCURATE_PRIMARY),
        "settings": {
            key: settings[key]
            for key in (
                "acceptance_threshold",
                "free_model_attempts",
                "paid_model_attempts",
                "file_cost_limit",
                "daily_cost_limit",
                "scan_dpi",
                "max_dpi",
                "enabled_engines",
                "enabled_models",
                "batch_size",
            )
        }
        | {
            "current_document_cost": float(row.get("total_cost") or 0),
            "daily_cost_spent": database.daily_cost(),
        },
    }


@app.get("/internal/jobs/{job_id}/input", dependencies=[Depends(_authenticate)])
def download_input(job_id: str):
    _, row = _get_job(job_id)
    path = _inside_storage(row["stored_pdf_path"])
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Input PDF not found")
    return FileResponse(path, media_type="application/pdf", filename="input.pdf")


@app.post("/internal/jobs/{job_id}/start", dependencies=[Depends(_authenticate)])
def start_job(job_id: str, message: WorkerMessage) -> dict:
    database, row = _get_job(job_id)
    if row["status"] in {"completed", "manual_review"}:
        raise HTTPException(status_code=409, detail="Job is already final")
    if row["status"] in {"failed", "cancelled"}:
        database.transition_conversion(job_id, "pending")
    elif row["status"] == "processing":
        if row.get("worker_name") == message.worker_name:
            database.heartbeat(job_id, message.worker_name)
            return get_job(job_id)
        raise HTTPException(status_code=409, detail="Job is owned by another worker")
    database.transition_conversion(
        job_id, "processing", worker_name=message.worker_name
    )
    return get_job(job_id)


@app.post("/internal/jobs/{job_id}/heartbeat", dependencies=[Depends(_authenticate)])
def heartbeat(job_id: str, message: WorkerMessage) -> dict:
    database, row = _get_job(job_id)
    if row.get("worker_name") != message.worker_name:
        raise HTTPException(status_code=409, detail="Worker does not own this job")
    try:
        database.heartbeat(job_id, message.worker_name)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return {"status": "ok"}


@app.post("/internal/jobs/{job_id}/result", dependencies=[Depends(_authenticate)])
def upload_result(
    job_id: str,
    worker_name: str = Form(...),
    metadata: str = Form(...),
    result: UploadFile = File(...),
) -> dict:
    database, row = _get_job(job_id)
    if row["status"] in {"completed", "manual_review"}:
        return {"job_id": job_id, "status": row["status"]}
    if row["status"] != "processing" or row.get("worker_name") != worker_name:
        raise HTTPException(
            status_code=409, detail="Worker does not own this processing job"
        )
    if not result.filename or Path(result.filename).suffix.lower() != ".docx":
        raise HTTPException(status_code=400, detail="Only DOCX results are accepted")
    try:
        values = json.loads(metadata)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="Invalid result metadata") from exc
    target_status = values.get("status")
    if target_status not in {"completed", "manual_review"}:
        raise HTTPException(status_code=400, detail="Invalid final status")
    target = _inside_storage(row["stored_docx_path"])
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        dir=target.parent, suffix=".docx.part", delete=False
    ) as temporary:
        temporary_path = Path(temporary.name)
        total = 0
        too_large = False
        limits = limits_from_env()
        while chunk := result.file.read(1024 * 1024):
            total += len(chunk)
            if total > limits.max_result_bytes:
                too_large = True
                break
            temporary.write(chunk)
        if not too_large:
            temporary.flush()
            os.fsync(temporary.fileno())
    if too_large:
        temporary_path.unlink(missing_ok=True)
        raise HTTPException(status_code=413, detail="Result is too large")
    if total < 4 or temporary_path.read_bytes()[:2] != b"PK":
        temporary_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail="Invalid DOCX content")
    try:
        with zipfile.ZipFile(temporary_path) as archive:
            validate_zip_archive(
                archive,
                limits=ArchiveLimits(
                    max_members=limits.max_archive_members,
                    max_total_uncompressed_bytes=limits.max_decompressed_bytes,
                ),
            )
    except (ValueError, zipfile.BadZipFile) as exc:
        temporary_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail="Unsafe DOCX archive") from exc
    os.replace(temporary_path, target)
    updated = database.transition_conversion(
        job_id,
        target_status,
        worker_name=worker_name,
        error_message=(
            "Cloud cost limit reached; best available result requires manual review."
            if values.get("cost_limit_reached")
            else None
        ),
        extra={
            "stored_docx_path": str(target),
            "file_type": values.get("file_type"),
            "text_quality_score": values.get("text_quality_score"),
            "layout_quality_score": values.get("layout_quality_score"),
            "final_quality_score": values.get("final_quality_score"),
            "winning_engine": values.get("winning_engine"),
            "processing_time": values.get("processing_time", 0),
        },
    )
    applications = values.get("correction_applications") or []
    if isinstance(applications, list):
        database.record_correction_applications(job_id, applications[:500])
    attempts = values.get("cloud_attempts") or []
    if isinstance(attempts, list):
        existing_attempts = len(database.list_attempts(row["id"]))
        for offset, attempt in enumerate(attempts[:100], start=1):
            if not isinstance(attempt, dict):
                continue
            database.record_attempt(
                {
                    "conversion_id": row["id"],
                    "engine_name": str(attempt.get("provider") or "openrouter")[:80],
                    "model_name": str(attempt.get("model") or "")[:200],
                    "engine_type": "cloud",
                    "attempt_number": existing_attempts + offset,
                    "quality_score": attempt.get("score"),
                    "cost": float(attempt.get("cost") or 0),
                    "cost_is_estimated": int(bool(attempt.get("cost_is_estimated"))),
                    "prompt_tokens": int(attempt.get("prompt_tokens") or 0),
                    "completion_tokens": int(attempt.get("completion_tokens") or 0),
                    "processing_time": float(attempt.get("latency_ms") or 0) / 1000.0,
                    "success": int(not bool(attempt.get("failure_reason"))),
                    "failure_reason": (
                        str(attempt.get("failure_reason"))[:2000]
                        if attempt.get("failure_reason")
                        else None
                    ),
                    "created_at": utc_now(),
                }
            )
    return {"job_id": job_id, "status": updated["status"]}


@app.post("/internal/jobs/{job_id}/failure", dependencies=[Depends(_authenticate)])
def fail_job(job_id: str, message: FailureMessage) -> dict:
    database, row = _get_job(job_id)
    if row["status"] == "failed":
        return {"job_id": job_id, "status": "failed"}
    if row["status"] in {"completed", "manual_review"}:
        return {"job_id": job_id, "status": row["status"]}
    if row["status"] != "processing" or row.get("worker_name") != message.worker_name:
        raise HTTPException(
            status_code=409, detail="Worker does not own this processing job"
        )
    database.transition_conversion(
        job_id, "failed", worker_name=message.worker_name, error_message=message.error
    )
    return {"job_id": job_id, "status": "failed"}
