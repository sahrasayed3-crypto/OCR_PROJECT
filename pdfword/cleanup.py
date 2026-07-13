import shutil
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .job_queue import get_job_queue


def cleanup_temporary_directories(
    storage_root: str | Path = "conversions",
    retention_hours: int = 24,
) -> dict:
    root = Path(storage_root).resolve()
    if not root.exists():
        return {"deleted": 0, "bytes_freed": 0, "errors": []}
    cutoff = datetime.now(timezone.utc) - timedelta(hours=max(1, retention_hours))
    active_jobs = get_job_queue().active_job_ids()
    deleted = 0
    bytes_freed = 0
    errors: list[str] = []
    for temporary in root.glob("*/*/temporary"):
        try:
            resolved = temporary.resolve()
            if root not in resolved.parents or temporary.parent.name in active_jobs:
                continue
            modified = datetime.fromtimestamp(
                temporary.stat().st_mtime, tz=timezone.utc
            )
            if modified > cutoff:
                continue
            size = sum(
                path.stat().st_size for path in temporary.rglob("*") if path.is_file()
            )
            shutil.rmtree(resolved)
            deleted += 1
            bytes_freed += size
        except (OSError, ValueError) as exc:
            errors.append(f"{temporary}: {exc}")
    return {"deleted": deleted, "bytes_freed": bytes_freed, "errors": errors}


if __name__ == "__main__":
    print(json.dumps(cleanup_temporary_directories(), ensure_ascii=False))
