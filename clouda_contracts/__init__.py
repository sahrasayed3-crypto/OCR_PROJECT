"""Dependency-light contracts shared by Clouda subsystems."""

from .dataset_identity import DatasetIdentity
from .model_observation import ModelObservation
from .ocr_observation import OCRObservation
from .page_identity import PageIdentity
from .storage import StorageRoots, StorageSecurityError

__all__ = [
    "DatasetIdentity",
    "ModelObservation",
    "OCRObservation",
    "PageIdentity",
    "StorageRoots",
    "StorageSecurityError",
]
