"""Research-focused feature extractor."""

from __future__ import annotations

import math
import re
from pathlib import Path
from typing import Dict, List, Tuple

from ..core import RepoSpec, TrainingExample
from .base import BaseExtractor


PAPER_REFERENCE_REGEX = re.compile(r"\b(?:arxiv|doi|icml|neurips|cvpr|acl|sigir|iclr|kdd)[\w/:.-]*", re.IGNORECASE)

CITATION_REGEX = re.compile(r"\[[0-9]{1,3}\]")

EXPERIMENT_CONFIG_NAMES = {
    "config.yaml",
    "config.yml",
    "experiment.yaml",
    "experiment.yml",
    "config.json",
    "hparams.yaml",
    "hyperparams.yaml",
    "params.json",
}

EXPERIMENT_DIR_KEYWORDS = {
    "experiments",
    "runs",
    "artifacts",
    "checkpoints",
    "models",
    "logs",
    "notebooks",
    "research",
    "papers",
}

NOTEBOOK_SUFFIXES = {".ipynb", ".rmd", ".qmd"}

DATASET_KEYWORDS = (
    "dataset",
    "benchmark",
    "corpus",
    "mnist",
    "imagenet",
    "coco",
    "squad",
    "wikidata",
    "kaggle",
    "uci",
)

ML_FRAMEWORK_KEYWORDS = (
    "pytorch",
    "tensorflow",
    "jax",
    "keras",
    "sklearn",
    "lightgbm",
    "xgboost",
    "huggingface",
    "transformers",
    "onnx",
)

METRIC_KEYWORDS = (
    "accuracy",
    "precision",
    "recall",
    "f1",
    "auc",
    "bleu",
    "rouge",
    "perplexity",
    "loss",
    "psnr",
    "fid",
)

FIGURE_KEYWORDS = (
    "figure",
    "plot",
    "chart",
    "graph",
    "visualization",
)

LICENSE_PERMISSIVE = {"mit", "bsd", "apache", "isc", "cc-by"}

def _safe_entropy(text: str) -> float:
    if not text:
        return 0.0
    freq: Dict[str, int] = {}
    for char in text:
        freq[char] = freq.get(char, 0) + 1
    total = len(text)
    entropy = 0.0
    for count in freq.values():
        probability = count / total
        entropy -= probability * math.log(probability, 2)
    return entropy


class ResearchExtractor(BaseExtractor):
    """Extract signals common in academic or research-grade repositories."""

    def extract(self, repo: RepoSpec) -> List[TrainingExample]:
        repo_dir = self._ensure_repo(repo)
        examples: List[TrainingExample] = []

        for file_path in repo_dir.rglob("*"):
            if not file_path.is_file() or not self._should_process(file_path):
                continue

            text = file_path.read_text(errors="ignore")
            base_features = self._collect_basic_features(file_path)
            research_features = self._research_features(file_path, text)
            features = {**base_features, **research_features}

            label, confidence = self._infer_label(features)
            metadata = {
                "confidence": f"{confidence:.2f}",
                "label_source": "research_heuristic",
            }

            examples.append(
                self._to_training_example(repo, file_path, label, features, metadata)
            )

        return examples

    def validator(self):
        from ..validators.base import QualityValidator

        return QualityValidator()

    def _should_process(self, file_path: Path) -> bool:
        if self._is_source_file(file_path):
            return True
        name = file_path.name.lower()
        suffix = file_path.suffix.lower()
        if suffix in NOTEBOOK_SUFFIXES:
            return True
        if name in EXPERIMENT_CONFIG_NAMES:
            return True
        if any(segment.lower() in EXPERIMENT_DIR_KEYWORDS for segment in file_path.parts):
            return True
        if suffix in {".md", ".pdf", ".tex"} and "paper" in name:
            return True
        return False

    def _research_features(self, file_path: Path, text: str) -> Dict[str, float]:
        lower_text = text.lower()

        citation_matches = len(CITATION_REGEX.findall(text))
        paper_reference_hits = len(PAPER_REFERENCE_REGEX.findall(text))

        dataset_mentions = sum(lower_text.count(keyword) for keyword in DATASET_KEYWORDS)
        framework_mentions = sum(lower_text.count(keyword) for keyword in ML_FRAMEWORK_KEYWORDS)
        metric_mentions = sum(lower_text.count(keyword) for keyword in METRIC_KEYWORDS)
        figure_mentions = sum(lower_text.count(keyword) for keyword in FIGURE_KEYWORDS)

        notebook_indicator = 1.0 if file_path.suffix.lower() in NOTEBOOK_SUFFIXES else 0.0
        experiment_config_indicator = 1.0 if file_path.name.lower() in EXPERIMENT_CONFIG_NAMES else 0.0
        experiment_path_indicator = 1.0 if any(
            segment.lower() in EXPERIMENT_DIR_KEYWORDS for segment in file_path.parts
        ) else 0.0

        permissive_license_indicator = 1.0 if any(license_name in lower_text for license_name in LICENSE_PERMISSIVE) else 0.0

        abstract_indicator = 1.0 if "abstract" in lower_text[:200] else 0.0
        methodology_indicator = 1.0 if "methodology" in lower_text or "proposed method" in lower_text else 0.0

        entropy = _safe_entropy(text[:5000])
        code_ratio = self._code_to_text_ratio(text)

        return {
            "citation_count": float(citation_matches),
            "paper_reference_hits": float(paper_reference_hits),
            "dataset_mentions": float(dataset_mentions),
            "framework_mentions": float(framework_mentions),
            "metric_mentions": float(metric_mentions),
            "figure_mentions": float(figure_mentions),
            "notebook_indicator": notebook_indicator,
            "experiment_config_indicator": experiment_config_indicator,
            "experiment_path_indicator": experiment_path_indicator,
            "permissive_license_indicator": permissive_license_indicator,
            "abstract_indicator": abstract_indicator,
            "methodology_indicator": methodology_indicator,
            "sample_entropy": entropy,
            "code_to_text_ratio": code_ratio,
        }

    def _code_to_text_ratio(self, text: str) -> float:
        if not text:
            return 0.0
        code_lines = 0
        prose_lines = 0
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith(("#", "//", "/*", "*") ):
                prose_lines += 1
            elif re.search(r"[=+\-*/<>]", stripped) and len(stripped) < 160:
                code_lines += 1
            elif len(stripped.split()) >= 7:
                prose_lines += 1
            else:
                code_lines += 1
        total = code_lines + prose_lines
        if total == 0:
            return 0.0
        return code_lines / total

    def _infer_label(self, features: Dict[str, float]) -> Tuple[str, float]:
        if features.get("permissive_license_indicator", 0.0) >= 1.0 and features.get("paper_reference_hits", 0.0) >= 2.0:
            return "third_party", 0.9
        if (
            features.get("notebook_indicator", 0.0) >= 1.0
            or features.get("experiment_config_indicator", 0.0) >= 1.0
            or features.get("experiment_path_indicator", 0.0) >= 1.0
        ) and features.get("dataset_mentions", 0.0) >= 1.0:
            return "foreground", 0.85
        if features.get("citation_count", 0.0) >= 3.0 or features.get("paper_reference_hits", 0.0) >= 3.0:
            return "background", 0.8
        if (
            features.get("framework_mentions", 0.0) >= 2.0
            and features.get("metric_mentions", 0.0) >= 2.0
            and features.get("code_to_text_ratio", 0.0) >= 0.4
        ):
            return "foreground", 0.75
        return "foreground", 0.6
