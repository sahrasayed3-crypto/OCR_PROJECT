from __future__ import annotations

from typing import TYPE_CHECKING

from .model_observation import ModelObservation
from .ocr_observation import OCRObservation
from .page_identity import PageIdentity
from .statuses import ObservationStatus

if TYPE_CHECKING:
    from clouda_data.ingestion.schema import PageRecord
    from pdfword.engines import OCRResult
    from pdfword.models import PageResult


def page_identity_from_record(record: "PageRecord") -> PageIdentity:
    return PageIdentity(
        document_id=record.document_id,
        page_number=record.page_number,
        page_id=record.page_id,
        source_uri=record.source_path,
    )


def ocr_observation_from_result(
    result: "OCRResult",
    *,
    page: PageIdentity,
) -> OCRObservation:
    status = {
        "succeeded": ObservationStatus.SUCCEEDED,
        "failed": ObservationStatus.FAILED,
        "pending_ocr_model": ObservationStatus.PENDING,
    }.get(result.status, ObservationStatus.FAILED)
    return OCRObservation(
        page=page,
        engine_name=result.engine_name,
        model_name=result.model_name,
        status=status,
        text=result.text,
        confidence=result.confidence,
        processing_seconds=result.processing_time,
        error_code=result.error_message,
    )


def model_observation_from_page_result(
    result: "PageResult",
    *,
    document_id: str,
) -> ModelObservation:
    page = PageIdentity(
        document_id=document_id,
        page_number=result.page_no,
        page_id=f"{document_id}:page:{result.page_no}",
    )
    status = (
        ObservationStatus.MANUAL_REVIEW
        if result.requires_manual_review
        else ObservationStatus.SUCCEEDED
    )
    return ModelObservation(
        page=page,
        model_id=result.model_used,
        status=status,
        output_text=result.markdown,
        quality_score=result.final_score,
        elapsed_seconds=result.elapsed_time,
    )
