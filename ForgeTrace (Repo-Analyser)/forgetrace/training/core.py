"""Core infrastructure for ForgeTrace ML training data generation."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence


class Phase(Enum):
    """Training program phases aligned with roadmap."""

    FOUNDATIONAL = auto()
    POLYGLOT = auto()
    SECURITY = auto()
    ENTERPRISE = auto()
    RESEARCH = auto()

    def describe(self) -> str:
        descriptions = {
            Phase.FOUNDATIONAL: (
                "Calibrate baseline signals using clean, well-documented repos"
            ),
            Phase.POLYGLOT: (
                "Expand language coverage and learn cross-language IP patterns"
            ),
            Phase.SECURITY: (
                "Deepen license, SBOM, and security provenance understanding"
            ),
            Phase.ENTERPRISE: ("Model complex multi-author enterprise codebases"),
            Phase.RESEARCH: (
                "Expose classifier to niche, research-grade, and anomalous code"
            ),
        }
        return descriptions[self]


@dataclass(frozen=True)
class RepoSpec:
    """Repository specification for training data collection."""

    name: str
    url: str
    phase: Phase
    languages: Sequence[str]
    expected_signals: Sequence[str]
    classification_targets: Sequence[str]
    priority: int = 3

    def short_name(self) -> str:
        return self.name.replace("/", "-")


@dataclass
class ExtractionConfig:
    """Configuration controlling per-phase feature extraction."""

    phase: Phase
    features: Sequence[str]
    quality_thresholds: Dict[str, float]
    validation_rules: Sequence[str]
    parallelism: int = 4


def _empty_metadata() -> Dict[str, str]:
    return {}


@dataclass
class TrainingExample:
    """Structured representation of a single labeled example."""

    repo: RepoSpec
    file_path: str
    label: str
    features: Dict[str, float]
    metadata: Dict[str, str] = field(default_factory=_empty_metadata)


class TrainingDataGenerator:
    """Top-level orchestrator coordinating the full training pipeline."""

    def __init__(self, output_dir: Path, configs: Dict[Phase, ExtractionConfig]):
        self.output_dir = Path(output_dir)
        self.configs = configs
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run_phase(
        self, phase: Phase, repos: Iterable[RepoSpec]
    ) -> List[TrainingExample]:
        """Run a single phase extractor and return validated examples."""

        config = self.configs[phase]
        extractor = self._build_extractor(config)

        raw_examples: List[TrainingExample] = []
        for repo in sorted(repos, key=lambda r: r.priority):
            repo_examples = extractor.extract(repo)
            raw_examples.extend(repo_examples)

        validator = extractor.validator()
        validated_examples = validator.validate(raw_examples, config)
        self._persist_phase_data(phase, validated_examples)

        return validated_examples

    def run_all_phases(self, repo_catalog: Mapping[Phase, Sequence[RepoSpec]]) -> None:
        """Run every phase in order."""

        all_examples: List[TrainingExample] = []
        for phase in Phase:
            repos = repo_catalog.get(phase, [])
            if not repos:
                continue
            examples = self.run_phase(phase, repos)
            all_examples.extend(examples)

        dataset_validator = self._build_dataset_validator()
        dataset_validator.validate(all_examples)
        self._persist_full_dataset(all_examples)

    def _build_extractor(self, config: ExtractionConfig):
        from .extractors import extractor_factory

        return extractor_factory(config)

    def _build_dataset_validator(self):
        from .validators import DatasetValidator

        return DatasetValidator()

    def _persist_phase_data(
        self, phase: Phase, examples: Sequence[TrainingExample]
    ) -> None:
        phase_dir = self.output_dir / phase.name.lower()
        phase_dir.mkdir(parents=True, exist_ok=True)
        output_file = phase_dir / "examples.jsonl"

        with output_file.open("w", encoding="utf-8") as fh:
            for example in examples:
                line: Dict[str, Any] = {
                    "repo": example.repo.name,
                    "phase": example.repo.phase.name,
                    "file_path": example.file_path,
                    "label": example.label,
                    "features": example.features,
                    "metadata": example.metadata,
                }
                fh.write(json.dumps(line, ensure_ascii=False) + "\n")

    def _persist_full_dataset(self, examples: Sequence[TrainingExample]) -> None:
        dataset_paths = [
            self.output_dir / "training_dataset.jsonl",
            self.output_dir / "complete_training_dataset.jsonl",
        ]

        handles = [path.open("w", encoding="utf-8") for path in dataset_paths]
        try:
            for example in examples:
                line: Dict[str, Any] = {
                    "repo": example.repo.name,
                    "phase": example.repo.phase.name,
                    "file_path": example.file_path,
                    "label": example.label,
                    "features": example.features,
                    "metadata": example.metadata,
                }
                json_line = json.dumps(line, ensure_ascii=False) + "\n"
                for handle in handles:
                    handle.write(json_line)
        finally:
            for handle in handles:
                handle.close()
