from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest
from PIL import Image, ImageChops, ImageDraw

from clouda_data.distortion.base import DistortionSpec
from clouda_data.distortion.registry import default_registry
from clouda_data.distortion.workflow import (
    generate_preview,
    read_jsonl,
    run_distortion_batch,
    validate_distortion_manifest,
)
from clouda_data.evaluation.execution import evaluate_records
from clouda_data.pipeline.profiles import list_profile_paths, load_profile
from clouda_data.rendering import RenderConfig, render_document, validate_render_manifest
from clouda_training.exporter import export_training_data
from pdfword.local_ocr_adapters import LocalHTTPProvider, LocalOCRConfig, MockOCRProvider
from pdfword.ocr_pipeline import process_pdf


@pytest.fixture()
def state(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "state"
    monkeypatch.setenv("CLOUDA_STATE_HOME", str(root))
    monkeypatch.setenv("CLOUDA_PROJECT_ROOT", str(Path(__file__).resolve().parents[2]))
    for name in ("datasets", "artifacts", "cache", "models", "runtime"):
        (root / name).mkdir(parents=True, exist_ok=True)
    return root


def _synthetic_page(path: Path) -> None:
    image = Image.new("RGB", (640, 800), "white")
    draw = ImageDraw.Draw(image)
    draw.rectangle((40, 40, 600, 760), outline="black", width=3)
    draw.text((80, 100), "Arabic synthetic test 123", fill="black")
    draw.text((80, 700), "footnote 1", fill="black")
    image.save(path)


def test_all_registered_real_operators_execute_and_are_deterministic() -> None:
    image = Image.new("RGB", (96, 96), "white")
    ImageDraw.Draw(image).rectangle((20, 20, 75, 75), fill="black")
    registry = default_registry()
    names = [name for name in registry.names() if name != "metadata_only"]
    assert len(names) >= 20
    changed = 0
    for name in names:
        operator = registry.create(DistortionSpec(name, severity="light"))
        first, first_meta = operator.apply(image, 12345)
        second, second_meta = operator.apply(image, 12345)
        assert first.tobytes() == second.tobytes(), name
        assert first_meta.random_seed == second_meta.random_seed == 12345
        assert first.width > 0 and first.height > 0
        if first.size != image.size or ImageChops.difference(first, image).getbbox():
            changed += 1
    assert changed >= 20


def test_required_yaml_profiles_validate() -> None:
    paths = [path for path in list_profile_paths() if path.suffix == ".yaml"]
    assert len(paths) >= 10
    for path in paths:
        profile = load_profile(path)
        assert profile["schema_version"] == 1
        assert profile["random_seed_policy"] == "required_deterministic"


def test_render_image_is_copy_on_write_and_valid(state: Path) -> None:
    source = state / "datasets" / "source.png"
    _synthetic_page(source)
    before = source.read_bytes()
    manifest = render_document(
        source,
        config=RenderConfig(dpi=144, color_mode="grayscale"),
    )
    assert validate_render_manifest(manifest)["passed"]
    assert source.read_bytes() == before
    record = read_jsonl(manifest)[0]
    assert record["schema_version"] == 1
    assert record["source_checksum"]
    assert record["output_checksum"]


def test_render_pdf_page(state: Path) -> None:
    fixture = Path(__file__).resolve().parents[1] / "fixtures" / "digital_text.pdf"
    source = state / "datasets" / "digital_text.pdf"
    shutil.copy2(fixture, source)
    manifest = render_document(
        source,
        config=RenderConfig(start_page=1, end_page=1, dpi=100),
    )
    assert validate_render_manifest(manifest)["passed"]
    assert len(read_jsonl(manifest)) == 1


def test_distortion_batch_resume_validate_preview_and_export(state: Path) -> None:
    source = state / "datasets" / "clean.png"
    _synthetic_page(source)
    source_checksum = __import__("hashlib").sha256(source.read_bytes()).hexdigest()
    input_manifest = state / "datasets" / "synthetic_manifest.jsonl"
    input_manifest.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "output_uri": "dataset://clean.png",
                "output_checksum": source_checksum,
                "source_document_id": "synthetic-doc-1",
                "source_page_number": 1,
                "page_id": "synthetic-doc-1:1",
                "dataset_id": "synthetic_evaluation",
                "license_status": "evaluation_only",
                "commercial_training_allowed": False,
                "ground_truth_reference": "synthetic://text/1",
                "ground_truth_text": "نص عربي اصطناعي",
                "attribution": "Generated synthetic fixture",
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    profile = Path(__file__).resolve().parents[2] / "configs" / "data_foundation" / "distortions" / "modern_scan_medium.yaml"
    manifest = run_distortion_batch(
        input_manifest,
        profile,
        seed=77,
        variants=3,
        max_pages=1,
    )
    first = read_jsonl(manifest)
    assert len(first) == 3
    assert all(item["ground_truth_text"] == "نص عربي اصطناعي" for item in first)
    assert all(item["output_checksum"] != source_checksum for item in first)
    resumed = run_distortion_batch(
        input_manifest,
        profile,
        seed=77,
        variants=3,
        max_pages=1,
        resume=True,
    )
    assert resumed == manifest
    assert len(read_jsonl(resumed)) == 3
    assert validate_distortion_manifest(manifest)["passed"]
    preview = generate_preview(manifest, limit=2)
    assert preview.is_file()
    export = state / "artifacts" / "training" / "synthetic.jsonl"
    summary = export_training_data(
        manifest,
        export,
        purpose="evaluation",
        export_format="conversation_multimodal",
    )
    assert summary["records"] == 3
    assert not summary["document_leakage"]
    assert summary["training_started"] is False


def test_commercial_export_fails_closed_for_synthetic(state: Path) -> None:
    manifest = state / "datasets" / "records.jsonl"
    manifest.write_text(
        json.dumps(
            {
                "ground_truth_text": "x",
                "license_status": "evaluation_only",
                "commercial_training_allowed": False,
                "dataset_id": "synthetic_evaluation",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    with pytest.raises(PermissionError):
        export_training_data(
            manifest,
            state / "artifacts" / "blocked.jsonl",
        )


def test_evaluation_metrics_are_executed() -> None:
    report = evaluate_records(
        [
            {
                "page_id": "1",
                "reference_text": "مرحبا بالعالم",
                "prediction_text": "مرحبا بالعالم",
                "processing_time": 0.5,
            },
            {
                "page_id": "2",
                "reference_text": "نص",
                "prediction_text": "",
                "processing_time": 0.5,
            },
        ]
    )
    assert report["summary"]["pages"] == 2
    assert report["summary"]["cer"] > 0
    assert report["summary"]["missing_text_rate"] == 0.5


def test_mock_local_ocr_runtime_path(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CLOUDA_LOCAL_OCR_ENABLED", "true")
    monkeypatch.setenv("CLOUDA_LOCAL_OCR_ENGINE", "mock")
    monkeypatch.setenv("CLOUDA_ALLOW_MOCK_OCR", "true")
    monkeypatch.setenv("CLOUDA_MOCK_OCR_TEXT", "نص ممسوح")
    fixture = Path(__file__).resolve().parents[1] / "fixtures" / "scanned.pdf"
    results, _ = process_pdf(
        fixture.read_bytes(),
        1,
        1,
        enabled_engines=["direct_pdf_text", "local_model_ocr"],
    )
    assert results[0].markdown == "نص ممسوح"
    assert results[0].metadata["page_state"] == "local_model_ocr"
    assert results[0].accepted


def test_mock_provider_requires_explicit_test_gate(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CLOUDA_ALLOW_MOCK_OCR", raising=False)
    assert not MockOCRProvider().available()


def test_remote_http_endpoint_requires_opt_in(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CLOUDA_LOCAL_OCR_ALLOW_REMOTE_ENDPOINT", raising=False)
    config = LocalOCRConfig(enabled=True, engine="local_http", endpoint="http://example.com")
    with pytest.raises(ValueError):
        LocalHTTPProvider(config)
