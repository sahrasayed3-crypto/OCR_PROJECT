from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from clouda_contracts.storage import StorageRoots
from clouda_training.sampling.deduplication import deduplicate_records
from clouda_training.sampling.splits import deterministic_document_split

SUPPORTED_FORMATS = {
    "generic_jsonl",
    "conversation_multimodal",
    "ocr_plain_text",
    "markdown_extraction",
    "layout_extraction",
    "word_bounding_boxes",
    "reading_order",
}

PROMPTS = {
    "generic_jsonl": "Extract the text from this document image.",
    "conversation_multimodal": "اقرأ النص العربي في الصورة مع الحفاظ على ترتيب القراءة.",
    "ocr_plain_text": "Return plain text only.",
    "markdown_extraction": "Return document content as Markdown.",
    "layout_extraction": "Return text and layout regions.",
    "word_bounding_boxes": "Return words with bounding boxes.",
    "reading_order": "Return text blocks in reading order.",
}


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def export_training_data(
    manifest: str | Path,
    output: str | Path,
    *,
    export_format: str = "generic_jsonl",
    seed: int = 20260723,
    purpose: str = "commercial_training",
    benchmark_exclusions: set[str] | None = None,
) -> dict[str, Any]:
    if export_format not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported export format: {export_format}")
    roots = StorageRoots.from_env()
    input_path = Path(manifest).expanduser().resolve()
    output_path = Path(output).expanduser().resolve()
    try:
        input_path.relative_to(roots.dataset_root.resolve())
        output_path.relative_to(roots.artifact_root.resolve())
    except ValueError as exc:
        raise PermissionError("Training input/output escaped configured roots") from exc
    source_records = _read_jsonl(input_path)
    exclusions = benchmark_exclusions or set()
    eligible: list[dict[str, Any]] = []
    for record in source_records:
        if record.get("source_document_id") in exclusions:
            continue
        if not record.get("ground_truth_text"):
            continue
        status = str(record.get("license_status", "pending"))
        if purpose == "commercial_training":
            if status not in {"approved", "approved_with_conditions"} or not record.get(
                "commercial_training_allowed", False
            ):
                raise PermissionError(
                    f"Dataset {record.get('dataset_id')} is not approved for commercial training"
                )
        elif purpose == "evaluation":
            if status in {"blocked", "pending", "expired"}:
                raise PermissionError(
                    f"Dataset {record.get('dataset_id')} is blocked for evaluation"
                )
        else:
            raise ValueError("purpose must be commercial_training or evaluation")
        eligible.append(record)
    deduped, duplicates = deduplicate_records(
        eligible, checksum_key="output_checksum"
    )
    assignments = deterministic_document_split(
        [str(item["source_document_id"]) for item in deduped], seed=seed
    )
    records: list[dict[str, Any]] = []
    for item in deduped:
        target: Any = item["ground_truth_text"]
        if export_format in {
            "layout_extraction",
            "word_bounding_boxes",
            "reading_order",
        }:
            target = {
                "text": item["ground_truth_text"],
                "regions": item.get("regions", []),
                "reading_order": item.get("reading_order", []),
            }
        base = {
            "schema_version": 1,
            "image_uri": item["output_uri"],
            "instruction": PROMPTS[export_format],
            "target": target,
            "dataset_id": item["dataset_id"],
            "source_document_id": item["source_document_id"],
            "page_id": item["source_page_id"],
            "generated_page_id": item["generated_page_id"],
            "profile_id": item["profile_id"],
            "license_status": item["license_status"],
            "attribution": item.get("attribution", ""),
            "split": assignments[str(item["source_document_id"])],
            "checksum": item["output_checksum"],
            "export_format": export_format,
        }
        if export_format == "conversation_multimodal":
            base["messages"] = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "image": item["output_uri"]},
                        {"type": "text", "text": PROMPTS[export_format]},
                    ],
                },
                {"role": "assistant", "content": str(item["ground_truth_text"])},
            ]
        records.append(base)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp = output_path.with_suffix(output_path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    temp.replace(output_path)
    split_counts = Counter(record["split"] for record in records)
    documents_by_split = {
        split: {
            record["source_document_id"]
            for record in records
            if record["split"] == split
        }
        for split in ("train", "validation", "test")
    }
    leakage = (
        documents_by_split["train"] & documents_by_split["validation"]
        or documents_by_split["train"] & documents_by_split["test"]
        or documents_by_split["validation"] & documents_by_split["test"]
    )
    summary = {
        "schema_version": 1,
        "records": len(records),
        "duplicates_rejected": len(duplicates),
        "split_counts": dict(split_counts),
        "document_leakage": sorted(leakage),
        "output": str(output_path),
        "sha256": hashlib.sha256(output_path.read_bytes()).hexdigest(),
        "purpose": purpose,
        "training_started": False,
    }
    return summary


def training_statistics(manifest: str | Path) -> dict[str, Any]:
    records = _read_jsonl(Path(manifest))
    return {
        "records": len(records),
        "datasets": dict(Counter(str(item.get("dataset_id")) for item in records)),
        "profiles": dict(Counter(str(item.get("profile_id")) for item in records)),
        "difficulty": dict(
            Counter(str(item.get("estimated_visual_difficulty")) for item in records)
        ),
        "bytes": sum(
            (StorageRoots.from_env().dataset_root / str(item["output_uri"]).removeprefix("dataset://")).stat().st_size
            for item in records
        ),
    }
