"""Validator for foundational baseline phase."""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Sequence

from .base import PhaseValidator

if TYPE_CHECKING:
    from ..core import ExtractionConfig, TrainingExample


class FoundationalValidator(PhaseValidator):
    """Ensure foundational dataset keeps only high-confidence examples."""

    def validate(
        self, examples: Sequence["TrainingExample"], config: "ExtractionConfig"
    ) -> List["TrainingExample"]:
        min_conf = config.quality_thresholds.get("min_confidence", 0.85)
        filtered: List["TrainingExample"] = []
        for example in examples:
            confidence = float(example.metadata.get("confidence", "0"))
            if confidence >= min_conf:
                filtered.append(example)
        if not filtered:
            print("⚠️  Foundational phase produced no examples at desired confidence")
        return filtered
