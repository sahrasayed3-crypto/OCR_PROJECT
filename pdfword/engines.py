from __future__ import annotations

import io
import time
from dataclasses import dataclass, field
from typing import Any, Protocol

from pypdf import PdfReader

OCR_STATUS_SUCCEEDED = "succeeded"
OCR_STATUS_FAILED = "failed"
OCR_STATUS_PENDING_MODEL = "pending_ocr_model"


@dataclass(frozen=True)
class OCRBox:
    """Optional layout element returned by engines that expose layout data."""

    text: str = ""
    bbox: tuple[float, float, float, float] | None = None
    confidence: float | None = None
    reading_order: int | None = None
    label: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class OCRResult:
    """Model-agnostic OCR result schema.

    The schema is intentionally broad enough for classic OCR engines,
    vision-language models, and document AI services. Optional fields stay
    optional because not every future model will expose confidence, layout, or
    reading-order data.
    """

    engine_name: str
    status: str
    text: str = ""
    model_name: str | None = None
    processing_time: float | None = None
    confidence: float | None = None
    error_message: str | None = None
    boxes: tuple[OCRBox, ...] = ()
    reading_order: tuple[int, ...] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def success(self) -> bool:
        return self.status == OCR_STATUS_SUCCEEDED

    @property
    def failure_reason(self) -> str | None:
        return self.error_message

    @property
    def requires_future_ocr(self) -> bool:
        return self.status == OCR_STATUS_PENDING_MODEL

    def as_dict(self) -> dict[str, Any]:
        return {
            "engine_name": self.engine_name,
            "model_name": self.model_name,
            "status": self.status,
            "text": self.text,
            "processing_time": self.processing_time,
            "confidence": self.confidence,
            "error_message": self.error_message,
            "boxes": [box.__dict__ for box in self.boxes],
            "reading_order": self.reading_order,
            "metadata": self.metadata,
        }


EngineResult = OCRResult


class ExtractionEngine(Protocol):
    name: str
    engine_type: str
    model_name: str | None

    def available(self) -> bool: ...

    def extract_page(
        self,
        *,
        image_bytes: bytes | None = None,
        image_path: str | None = None,
        pdf_bytes: bytes | None = None,
        page_no: int | None = None,
        **kwargs: Any,
    ) -> OCRResult: ...


class EngineRegistry:
    def __init__(self) -> None:
        self._engines: dict[str, ExtractionEngine] = {}

    def register(self, engine: ExtractionEngine, *, replace: bool = False) -> None:
        if not getattr(engine, "name", None):
            raise ValueError("Engine must expose a non-empty name.")
        if engine.name in self._engines and not replace:
            raise ValueError(f"Engine already registered: {engine.name}")
        self._engines[engine.name] = engine

    def get(self, name: str) -> ExtractionEngine:
        try:
            return self._engines[name]
        except KeyError as exc:
            raise KeyError(f"Unknown extraction engine: {name}") from exc

    def names(self) -> list[str]:
        return sorted(self._engines)

    def available_names(self) -> list[str]:
        return [name for name in self.names() if self._engines[name].available()]

    def all(self) -> list[ExtractionEngine]:
        return [self._engines[name] for name in self.names()]


class DirectPdfTextEngine:
    name = "direct_pdf_text"
    engine_type = "digital_text"
    model_name: str | None = None

    def available(self) -> bool:
        return True

    def extract_page(
        self,
        *,
        image_bytes: bytes | None = None,
        image_path: str | None = None,
        pdf_bytes: bytes | None = None,
        page_no: int | None = None,
        **kwargs: Any,
    ) -> OCRResult:
        del image_bytes, image_path, kwargs
        started = time.perf_counter()
        if pdf_bytes is None or page_no is None:
            return OCRResult(
                engine_name=self.name,
                model_name=self.model_name,
                status=OCR_STATUS_FAILED,
                text="",
                processing_time=time.perf_counter() - started,
                confidence=None,
                error_message="Direct PDF text extraction requires pdf_bytes and page_no.",
            )
        try:
            reader = PdfReader(io.BytesIO(pdf_bytes))
            text = reader.pages[page_no - 1].extract_text() or ""
            has_text = bool(text.strip())
            return OCRResult(
                engine_name=self.name,
                model_name=self.model_name,
                status=OCR_STATUS_SUCCEEDED if has_text else OCR_STATUS_PENDING_MODEL,
                text=text,
                processing_time=time.perf_counter() - started,
                confidence=100.0 if has_text else None,
                error_message=None if has_text else "No embedded text layer was found.",
            )
        except Exception as exc:
            return OCRResult(
                engine_name=self.name,
                model_name=self.model_name,
                status=OCR_STATUS_FAILED,
                text="",
                processing_time=time.perf_counter() - started,
                confidence=None,
                error_message=str(exc),
            )


class FutureOcrEngine:
    """Placeholder for scanned pages until an approved OCR model is selected."""

    name = "future_ocr_engine"
    engine_type = "future_ocr_placeholder"
    model_name: str | None = None

    def available(self) -> bool:
        return False

    def extract_page(
        self,
        *,
        image_bytes: bytes | None = None,
        image_path: str | None = None,
        pdf_bytes: bytes | None = None,
        page_no: int | None = None,
        **kwargs: Any,
    ) -> OCRResult:
        del image_bytes, image_path, pdf_bytes, page_no, kwargs
        started = time.perf_counter()
        return OCRResult(
            engine_name=self.name,
            model_name=self.model_name,
            status=OCR_STATUS_PENDING_MODEL,
            text="",
            processing_time=time.perf_counter() - started,
            confidence=None,
            error_message=(
                "Scanned-page OCR is pending. No final trainable OCR model "
                "has been selected or validated yet."
            ),
        )


DIRECT_TEXT_ENGINE = DirectPdfTextEngine()
FUTURE_OCR_ENGINE = FutureOcrEngine()
DEFAULT_ENGINE_REGISTRY = EngineRegistry()
DEFAULT_ENGINE_REGISTRY.register(DIRECT_TEXT_ENGINE)
DEFAULT_ENGINE_REGISTRY.register(FUTURE_OCR_ENGINE)


def get_engine_registry() -> EngineRegistry:
    return DEFAULT_ENGINE_REGISTRY


def available_engine_status(
    registry: EngineRegistry | None = None,
) -> list[dict[str, Any]]:
    active_registry = registry or DEFAULT_ENGINE_REGISTRY
    statuses: list[dict[str, Any]] = []
    for engine in active_registry.all():
        statuses.append(
            {
                "engine": engine.name,
                "type": engine.engine_type,
                "model": getattr(engine, "model_name", None),
                "available": engine.available(),
                "active": engine.name == DIRECT_TEXT_ENGINE.name,
                "status": "ready" if engine.available() else OCR_STATUS_PENDING_MODEL,
            }
        )
    return statuses
