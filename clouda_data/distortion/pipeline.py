from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .base import DistortionSpec
from .metadata import DistortionMetadata
from .randomness import derive_seed
from .registry import DistortionRegistry, default_registry


@dataclass(frozen=True)
class DistortionPipeline:
    profile_name: str
    operations: list[DistortionSpec]
    base_seed: int
    registry: DistortionRegistry = field(default_factory=default_registry)

    def validate(self) -> None:
        for operation in self.operations:
            operation.validate()

    def replay_plan(self, page_id: str) -> list[tuple[DistortionSpec, int]]:
        return [
            (
                operation,
                derive_seed(self.base_seed, page_id, operation.name, str(index)),
            )
            for index, operation in enumerate(self.operations)
        ]

    def run_metadata_only(
        self, image: Any, page_id: str
    ) -> tuple[Any, list[DistortionMetadata]]:
        self.validate()
        current = image
        metadata: list[DistortionMetadata] = []
        for operation, seed in self.replay_plan(page_id):
            current, op_metadata = self.registry.create(operation).apply(current, seed)
            metadata.append(op_metadata)
        return current, metadata
