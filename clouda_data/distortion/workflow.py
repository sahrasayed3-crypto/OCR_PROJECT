from __future__ import annotations

import csv
import hashlib
import html
import json
import math
import os
import platform
import shutil
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from PIL import Image, ImageChops, ImageStat

from clouda_contracts.storage import StorageRoots
from clouda_data.datasets.license_gate import decide_dataset_use
from clouda_data.pipeline.profiles import load_profile, profile_to_specs

from .pipeline import DistortionPipeline

PAGE_STATES = {
    "queued", "processing", "complete", "failed", "skipped", "quarantined",
    "cancelled", "manual_review",
}
CONFLICT_POLICIES = {
    "reject", "skip_identical", "version_new", "overwrite_only_with_explicit_flag"
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def _atomic_save(image: Image.Image, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=f".{target.stem}-", suffix=".png", dir=target.parent)
    os.close(fd)
    temp = Path(name)
    try:
        image.save(temp, "PNG", optimize=True)
        if target.exists():
            raise FileExistsError(target)
        temp.replace(target)
    finally:
        temp.unlink(missing_ok=True)


def _write_jsonl_atomic(path: Path, records: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    temp.replace(path)


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in Path(path).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def classify_visual_difficulty(image: Image.Image, severity: str) -> dict[str, Any]:
    gray = image.convert("L")
    stat = ImageStat.Stat(gray)
    mean = float(stat.mean[0])
    stddev = float(stat.stddev[0])
    histogram = gray.histogram()
    pixels = max(1, image.width * image.height)
    entropy = -sum(
        (count / pixels) * math.log2(count / pixels)
        for count in histogram
        if count
    )
    white_ratio = sum(histogram[250:]) / pixels
    black_ratio = sum(histogram[:6]) / pixels
    score = {"minimal": 0, "light": 1, "medium": 2, "heavy": 3, "extreme": 4}.get(severity, 2)
    if stddev < 18 or white_ratio > 0.998 or black_ratio > 0.98 or entropy < 0.4:
        label = "invalid"
    elif score >= 4 or stddev < 30:
        label = "extreme"
    elif score >= 3:
        label = "difficult"
    elif score >= 2:
        label = "medium"
    else:
        label = "easy"
    return {
        "estimated_visual_difficulty": label,
        "brightness": mean,
        "contrast": stddev,
        "page_entropy": entropy,
        "blankness": white_ratio,
        "blackness": black_ratio,
    }


def _validate_asset(
    record: dict[str, Any],
    *,
    roots: StorageRoots,
    source_path: Path,
    output_path: Path,
    image: Image.Image,
) -> list[str]:
    errors: list[str] = []
    if not _inside(output_path, roots.dataset_root):
        errors.append("output_root_escape")
    if not output_path.is_file():
        errors.append("missing_output")
        return errors
    if _sha256(output_path) != record.get("output_checksum"):
        errors.append("checksum_mismatch")
    try:
        with Image.open(output_path) as decoded:
            decoded.verify()
    except Exception:
        errors.append("decode_failed")
    if image.width < 1 or image.height < 1:
        errors.append("invalid_dimensions")
    if record.get("transformation_chain") and _sha256(source_path) == _sha256(output_path):
        errors.append("identical_to_source")
    difficulty = classify_visual_difficulty(image, str(record.get("overall_severity", "medium")))
    if difficulty["estimated_visual_difficulty"] == "invalid":
        errors.append("invalid_visual_quality")
    if not record.get("seeds"):
        errors.append("missing_seed")
    if not record.get("profile_hash"):
        errors.append("missing_profile_hash")
    if not record.get("ground_truth_reference"):
        errors.append("missing_ground_truth_reference")
    return errors


def run_distortion_batch(
    input_manifest: str | Path,
    profile_path: str | Path,
    *,
    output_root: str | Path | None = None,
    seed: int = 1,
    variants: int = 1,
    max_pages: int = 100,
    allow_large_run: bool = False,
    dry_run: bool = False,
    resume: bool = False,
    fail_fast: bool = False,
    conflict_policy: str = "reject",
) -> Path:
    if max_pages < 1 or variants < 1:
        raise ValueError("max_pages and variants must be positive")
    if max_pages > 100 and not allow_large_run:
        raise PermissionError("--allow-large-run is required above 100 pages")
    if conflict_policy not in CONFLICT_POLICIES:
        raise ValueError("invalid conflict policy")
    roots = StorageRoots.from_env()
    manifest_path = Path(input_manifest).expanduser().resolve()
    if not _inside(manifest_path, roots.dataset_root):
        raise PermissionError("input manifest must be inside dataset root")
    profile = load_profile(profile_path)
    profile_hash = hashlib.sha256(
        json.dumps(profile, sort_keys=True).encode()
    ).hexdigest()
    input_records = read_jsonl(manifest_path)[:max_pages]
    material = f"{_sha256(manifest_path)}:{profile['name']}:{profile_hash}:{seed}:{variants}"
    run_id = hashlib.sha256(material.encode()).hexdigest()[:24]
    root = (
        Path(output_root).expanduser().resolve()
        if output_root
        else roots.dataset_root / "distorted"
    )
    if not _inside(root, roots.dataset_root):
        raise PermissionError("output root must be inside dataset root")
    run_root = root / run_id
    output_manifest = run_root / "distortion_manifest.v1.jsonl"
    existing = read_jsonl(output_manifest) if resume and output_manifest.is_file() else []
    by_id = {str(item["generated_page_id"]): item for item in existing}
    records = list(existing)
    pipeline = DistortionPipeline(
        profile_name=str(profile["name"]),
        operations=profile_to_specs(profile),
        base_seed=seed,
    )
    run_root.mkdir(parents=True, exist_ok=True)
    run_manifest = run_root / "run_manifest.v1.json"
    run_manifest.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "run_id": run_id,
                "profile_id": profile["name"],
                "profile_hash": profile_hash,
                "state": "processing",
                "heartbeat_at": datetime.now(timezone.utc).isoformat(),
                "max_pages": max_pages,
                "variants": variants,
                "dry_run": dry_run,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    for source in input_records:
        source_uri = str(source.get("output_uri") or source.get("image_uri") or "")
        if not source_uri.startswith("dataset://"):
            if fail_fast:
                raise ValueError("unsafe source URI")
            continue
        source_path = roots.dataset_root / source_uri.removeprefix("dataset://")
        if not _inside(source_path, roots.dataset_root) or not source_path.is_file():
            if fail_fast:
                raise FileNotFoundError(source_path)
            continue
        dataset_id = str(source.get("dataset_id", "synthetic_evaluation"))
        license_status = str(source.get("license_status", "evaluation_only"))
        commercial_allowed = False
        if dataset_id != "synthetic_evaluation":
            decision = decide_dataset_use(dataset_id, purpose="evaluation")
            if not decision.allowed:
                if fail_fast:
                    raise PermissionError(f"Dataset {dataset_id} is not approved")
                continue
            license_status = decision.status
            commercial_allowed = decide_dataset_use(
                dataset_id, purpose="commercial_training"
            ).allowed
        source_page_id = str(
            source.get("page_id")
            or f"{source.get('source_document_id')}:{source.get('source_page_number')}"
        )
        for variant in range(variants):
            generated_id = hashlib.sha256(
                f"{run_id}:{source_page_id}:{variant}".encode()
            ).hexdigest()[:32]
            if generated_id in by_id and by_id[generated_id].get("status") == "complete":
                continue
            output_path = run_root / "pages" / f"{generated_id}.png"
            if output_path.exists() and not resume:
                raise FileExistsError(output_path)
            started = time.perf_counter()
            with Image.open(source_path) as opened:
                opened.load()
                result, transformations = pipeline.run(
                    opened,
                    f"{source_page_id}:{variant}",
                    context={"regions": source.get("regions", [])},
                )
            record: dict[str, Any] = {
                "schema_version": 1,
                "generated_page_id": generated_id,
                "source_page_id": source_page_id,
                "source_document_id": source.get("source_document_id"),
                "dataset_id": dataset_id,
                "source_uri": source_uri,
                "source_checksum": _sha256(source_path),
                "output_uri": f"dataset://{output_path.relative_to(roots.dataset_root).as_posix()}",
                "output_checksum": None,
                "ground_truth_reference": source.get("ground_truth_reference", "synthetic://unchanged"),
                "profile_id": profile["name"],
                "profile_version": profile.get("schema_version", 1),
                "profile_hash": profile_hash,
                "transformation_chain": [item.name for item in transformations],
                "transformation_parameters": [item.parameters for item in transformations],
                "seeds": [item.random_seed for item in transformations],
                "severity_per_transformation": [item.severity for item in transformations],
                "overall_severity": profile.get("severity", "medium"),
                "layout_mode": "regions" if source.get("regions") else "whole_page_fallback",
                "affected_regions": [
                    region
                    for item in transformations
                    for region in item.output_metadata.get("affected_regions", [])
                ],
                "source_dimensions": list(opened.size),
                "output_dimensions": list(result.size),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "software_version": "clouda-pdf/0.2.0",
                "python_version": platform.python_version(),
                "pillow_version": Image.__version__,
                "host": {"system": platform.system(), "machine": platform.machine()},
                "license_status": license_status,
                "commercial_training_allowed": commercial_allowed,
                "status": "planned" if dry_run else "processing",
                "retry_count": 0,
                "processing_seconds": time.perf_counter() - started,
                "warning_list": [],
                "error": None,
            }
            if not dry_run:
                _atomic_save(result, output_path)
                record["output_checksum"] = _sha256(output_path)
                quality = classify_visual_difficulty(result, str(record["overall_severity"]))
                record.update(quality)
                errors = _validate_asset(
                    record,
                    roots=roots,
                    source_path=source_path,
                    output_path=output_path,
                    image=result,
                )
                record["status"] = "manual_review" if errors else "complete"
                record["warning_list"] = errors
            records.append(record)
            by_id[generated_id] = record
            _write_jsonl_atomic(output_manifest, records)
    status = "complete" if all(item.get("status") in {"complete", "manual_review", "planned"} for item in records) else "failed"
    payload = json.loads(run_manifest.read_text(encoding="utf-8"))
    payload.update({"state": status, "completed_at": datetime.now(timezone.utc).isoformat(), "records": len(records)})
    run_manifest.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    if not dry_run:
        (run_root / "COMPLETE.v1.json").write_text(
            json.dumps({"schema_version": 1, "run_id": run_id, "records": len(records)}, indent=2),
            encoding="utf-8",
        )
    return output_manifest


def validate_distortion_manifest(
    manifest: str | Path,
    *,
    quarantine: bool = False,
) -> dict[str, Any]:
    roots = StorageRoots.from_env()
    path = Path(manifest).expanduser().resolve()
    records = read_jsonl(path)
    failures: list[dict[str, Any]] = []
    for record in records:
        source = roots.dataset_root / str(record["source_uri"]).removeprefix("dataset://")
        output = roots.dataset_root / str(record["output_uri"]).removeprefix("dataset://")
        try:
            with Image.open(output) as image:
                image.load()
                errors = _validate_asset(record, roots=roots, source_path=source, output_path=output, image=image)
        except Exception as exc:
            errors = [f"decode_failed:{type(exc).__name__}"]
        if errors:
            failures.append({"generated_page_id": record["generated_page_id"], "errors": errors})
            if quarantine and output.is_file():
                destination = roots.dataset_root / "quarantine" / path.parent.name / output.name
                destination.parent.mkdir(parents=True, exist_ok=True)
                if not destination.exists():
                    shutil.copy2(output, destination)
    report = {"schema_version": 1, "records": len(records), "failures": failures, "passed": not failures}
    report_root = roots.artifact_root / "reports" / "validation"
    report_root.mkdir(parents=True, exist_ok=True)
    stem = path.parent.name
    (report_root / f"{stem}.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    with (report_root / f"{stem}.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["generated_page_id", "errors"])
        for item in failures:
            writer.writerow([item["generated_page_id"], ";".join(item["errors"])])
    (report_root / f"{stem}.md").write_text(
        f"# Validation\n\n- Records: {len(records)}\n- Failures: {len(failures)}\n- Passed: {not failures}\n",
        encoding="utf-8",
    )
    return report


def generate_preview(manifest: str | Path, *, limit: int = 10, difference: bool = True) -> Path:
    roots = StorageRoots.from_env()
    records = read_jsonl(manifest)[: max(1, min(limit, 100))]
    preview_root = roots.artifact_root / "previews" / Path(manifest).parent.name
    preview_root.mkdir(parents=True, exist_ok=True)
    rows: list[str] = []
    for record in records:
        source = roots.dataset_root / str(record["source_uri"]).removeprefix("dataset://")
        output = roots.dataset_root / str(record["output_uri"]).removeprefix("dataset://")
        with Image.open(source) as src, Image.open(output) as dst:
            src = src.convert("RGB")
            dst = dst.convert("RGB")
            thumb_size = (640, 640)
            src.thumbnail(thumb_size)
            dst.thumbnail(thumb_size)
            canvas = Image.new("RGB", (src.width + dst.width, max(src.height, dst.height)), "white")
            canvas.paste(src, (0, 0))
            canvas.paste(dst, (src.width, 0))
            if difference and src.size == dst.size:
                diff = ImageChops.difference(src, dst)
                diff.save(preview_root / f"{record['generated_page_id']}-diff.png")
            preview = preview_root / f"{record['generated_page_id']}.jpg"
            canvas.save(preview, "JPEG", quality=85)
        rows.append(
            f"<tr><td>{html.escape(str(record['source_page_id']))}</td>"
            f"<td>{html.escape(str(record['generated_page_id']))}</td>"
            f"<td>{html.escape(str(record['profile_id']))}</td>"
            f"<td>{html.escape(str(record.get('overall_severity')))}</td>"
            f"<td><img loading='lazy' width='640' src='{preview.name}'></td></tr>"
        )
    document = (
        "<!doctype html><meta charset='utf-8'><title>Clouda distortion preview</title>"
        "<h1>Distortion preview</h1><table><thead><tr><th>Source</th><th>Generated</th>"
        "<th>Profile</th><th>Severity</th><th>Preview</th></tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table>"
    )
    index = preview_root / "index.html"
    index.write_text(document, encoding="utf-8")
    (preview_root / "README.md").write_text(
        "# Preview index\n\n" + "\n".join(f"- `{record['generated_page_id']}` — {record['profile_id']}" for record in records),
        encoding="utf-8",
    )
    return index
