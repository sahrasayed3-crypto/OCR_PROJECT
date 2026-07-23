from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from clouda_data.distortion.base import DistortionSpec
from clouda_data.locations import default_profile_dir

REQUIRED_PROFILE_FIELDS = {
    "name",
    "recommended_use",
    "distortions",
    "ordering_constraints",
    "mutually_exclusive",
    "maximum_allowed_crop",
    "minimum_readable_text_threshold",
    "metadata_fields",
}


def load_profile(path: str | Path) -> dict[str, Any]:
    profile = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_profile(profile)
    return profile


def validate_profile(profile: dict[str, Any]) -> None:
    missing = sorted(REQUIRED_PROFILE_FIELDS - set(profile))
    if missing:
        raise ValueError(f"Profile is missing fields: {', '.join(missing)}")
    if not 0 <= profile["maximum_allowed_crop"] <= 0.2:
        raise ValueError("maximum_allowed_crop must be between 0 and 0.2.")
    if not 0 <= profile["minimum_readable_text_threshold"] <= 1:
        raise ValueError("minimum_readable_text_threshold must be between 0 and 1.")
    if not isinstance(profile["distortions"], list):
        raise ValueError("distortions must be a list.")
    for item in profile["distortions"]:
        spec = DistortionSpec(
            name=item["name"],
            probability=float(item.get("probability", 1.0)),
            severity=item.get("severity", "medium"),
            parameters=item.get("parameters", {}),
        )
        spec.validate()


def profile_to_specs(profile: dict[str, Any]) -> list[DistortionSpec]:
    return [
        DistortionSpec(
            name=item["name"],
            probability=float(item.get("probability", 1.0)),
            severity=item.get("severity", "medium"),
            parameters=item.get("parameters", {}),
        )
        for item in profile["distortions"]
    ]


def list_profile_paths(config_dir: str | Path | None = None) -> list[Path]:
    root = Path(config_dir) if config_dir is not None else default_profile_dir()
    return sorted(root.glob("*.json"))
