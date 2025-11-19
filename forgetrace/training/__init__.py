"""
Training Data Generation for ML-Based IP Classification

WHAT: Infrastructure for generating high-quality labeled training data
WHY: ML models are only as good as their training data. This module systematically
     collects diverse, labeled code examples from 100 public repositories.

ARCHITECTURE:
    1. Repository Specification: Define which repos to analyze and why
    2. Feature Extraction: Convert raw code → numerical features
    3. Quality Validation: Ensure data quality and consistency
    4. Dataset Generation: Create train/val/test splits

USAGE:
    from forgetrace.training import TrainingDataGenerator

    generator = TrainingDataGenerator(output_dir="training_data")
    generator.run_all_phases()
"""

from .core import (
    ExtractionConfig,
    Phase,
    RepoSpec,
    TrainingDataGenerator,
    TrainingExample,
)
from .extractors import (
    EnterpriseExtractor,
    FoundationalExtractor,
    PolyglotExtractor,
    ResearchExtractor,
    SecurityExtractor,
)
from .validators import DatasetValidator, PhaseValidator, QualityValidator

__all__ = [
    "Phase",
    "RepoSpec",
    "ExtractionConfig",
    "TrainingDataGenerator",
    "TrainingExample",
    "FoundationalExtractor",
    "PolyglotExtractor",
    "SecurityExtractor",
    "EnterpriseExtractor",
    "ResearchExtractor",
    "QualityValidator",
    "PhaseValidator",
    "DatasetValidator",
]
