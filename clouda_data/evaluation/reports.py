from __future__ import annotations

import csv
import json
from pathlib import Path

from .aggregations import PageMetric, aggregate_metrics, group_by_profile


def write_json_report(metrics: list[PageMetric], path: str | Path) -> None:
    payload = {
        "summary": aggregate_metrics(metrics),
        "by_profile": group_by_profile(metrics),
        "pages": [metric.__dict__ for metric in metrics],
    }
    Path(path).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def write_csv_report(metrics: list[PageMetric], path: str | Path) -> None:
    with Path(path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=["page_id", "profile", "severity", "cer", "wer"]
        )
        writer.writeheader()
        for metric in metrics:
            writer.writerow(metric.__dict__)


def markdown_summary(metrics: list[PageMetric]) -> str:
    summary = aggregate_metrics(metrics)
    return f"# OCR Evaluation Summary\n\nPages: {summary['pages']}\n\nCER mean: {summary['cer_mean']:.4f}\n\nWER mean: {summary['wer_mean']:.4f}\n"
