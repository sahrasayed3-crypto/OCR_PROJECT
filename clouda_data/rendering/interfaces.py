from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RenderRequest:
    source_path: str
    page_number: int
    dpi: int
    output_path: str


@dataclass(frozen=True)
class RenderResult:
    image_path: str
    width: int
    height: int
    dpi: int
    checksum: str
