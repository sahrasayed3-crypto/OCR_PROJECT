from __future__ import annotations

from .base import Distortion, DistortionSpec, MetadataOnlyDistortion


class DistortionRegistry:
    def __init__(self) -> None:
        self._classes: dict[str, type[Distortion]] = {}

    def register(self, name: str, cls: type[Distortion]) -> None:
        if name in self._classes:
            raise ValueError(f"Distortion already registered: {name}")
        self._classes[name] = cls

    def create(self, spec: DistortionSpec) -> Distortion:
        cls = self._classes.get(spec.name, MetadataOnlyDistortion)
        return cls(spec)

    def names(self) -> list[str]:
        return sorted(self._classes)


DEFAULT_DISTORTIONS = [
    "dpi_reduction",
    "blur",
    "defocus_blur",
    "motion_blur",
    "gaussian_noise",
    "speckle_noise",
    "scanner_noise",
    "jpeg_compression",
    "contrast_loss",
    "brightness_variation",
    "faded_text",
    "uneven_illumination",
    "yellow_paper",
    "gray_paper",
    "paper_texture",
    "stains",
    "dust",
    "ink_bleed",
    "show_through",
    "shadow",
    "binding_shadow",
    "edge_darkening",
    "page_curvature",
    "perspective",
    "rotation",
    "skew",
    "cropping",
    "border_artifacts",
    "torn_edges",
    "fold_marks",
    "wrinkles",
    "small_font_degradation",
    "broken_characters",
    "weak_punctuation",
    "partial_clipping",
    "double_page_scan",
    "scanner_lines",
]


def default_registry() -> DistortionRegistry:
    registry = DistortionRegistry()
    for name in DEFAULT_DISTORTIONS:
        registry.register(name, MetadataOnlyDistortion)
    return registry
