"""Validation helpers for phase training datasets."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import Counter
from statistics import mean
from typing import TYPE_CHECKING, Dict, List, Sequence

if TYPE_CHECKING:
    from ..core import ExtractionConfig, TrainingExample
else:  # pragma: no cover
    ExtractionConfig = object  # type: ignore
    TrainingExample = object  # type: ignore


class PhaseValidator(ABC):
    """Base validator enforcing per-phase quality requirements."""

    @abstractmethod
    def validate(
        self, examples: Sequence["TrainingExample"], config: "ExtractionConfig"
    ) -> List["TrainingExample"]:
        """Validate and possibly filter training examples."""


class QualityValidator(PhaseValidator):
    """Generic validator applying confidence and coverage checks."""

    def validate(
        self, examples: Sequence["TrainingExample"], config: "ExtractionConfig"
    ) -> List["TrainingExample"]:
        if not examples:
            return []

        thresholds = config.quality_thresholds
        min_conf = thresholds.get("min_confidence", 0.7)
        min_files = int(thresholds.get("min_files", 50))

        filtered: List["TrainingExample"] = []
        for example in examples:
            confidence = float(example.metadata.get("confidence", "0"))
            if confidence >= min_conf:
                filtered.append(example)

        if len(filtered) < min_files:
            print(
                f"⚠️  Phase {config.phase.name}: only {len(filtered)} examples >= confidence {min_conf}"
            )
        return filtered


class DatasetValidator:
    """Cross-phase dataset health checks."""

    def validate(self, examples: Sequence["TrainingExample"]) -> None:
        if not examples:
            raise ValueError("No training examples generated")

        by_phase: Dict[str, int] = Counter(
            example.repo.phase.name for example in examples
        )
        print("📊 Dataset distribution by phase:")
        for phase, count in by_phase.items():
            print(f"   {phase}: {count}")

        labels = Counter(example.label for example in examples)
        print("📊 Label distribution:")
        for label, count in labels.items():
            print(f"   {label}: {count}")

        if len(labels) < 2:
            print("⚠️  Warning: dataset lacks class diversity")

        feature_counts = [len(example.features) for example in examples]
        print(f"📈 Average feature count per example: {mean(feature_counts):.2f}")
