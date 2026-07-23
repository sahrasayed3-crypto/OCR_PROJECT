from __future__ import annotations

from dataclasses import dataclass
from statistics import mean


@dataclass(frozen=True)
class PageMetric:
    page_id: str
    profile: str
    severity: str
    cer: float
    wer: float


def aggregate_metrics(metrics: list[PageMetric]) -> dict[str, float]:
    if not metrics:
        return {"pages": 0, "cer_mean": 0.0, "wer_mean": 0.0}
    return {
        "pages": len(metrics),
        "cer_mean": mean(m.cer for m in metrics),
        "wer_mean": mean(m.wer for m in metrics),
    }


def group_by_profile(metrics: list[PageMetric]) -> dict[str, dict[str, float]]:
    grouped: dict[str, list[PageMetric]] = {}
    for metric in metrics:
        grouped.setdefault(metric.profile, []).append(metric)
    return {profile: aggregate_metrics(items) for profile, items in grouped.items()}
