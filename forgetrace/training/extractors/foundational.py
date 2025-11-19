"""Foundational baseline extractor."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List

from ..core import RepoSpec, TrainingExample
from .base import BaseExtractor

SPDX_PATTERN = re.compile(r"SPDX-License-Identifier:\s*(?P<license>[A-Za-z0-9\-\.]+)")


class FoundationalExtractor(BaseExtractor):
    """Extract clean, high-confidence examples from well-documented repos."""

    def extract(self, repo: RepoSpec) -> List[TrainingExample]:
        repo_dir = self._ensure_repo(repo)
        vuln_features = self._repo_vulnerability_features(repo_dir)
        examples: List[TrainingExample] = []

        for file_path in repo_dir.rglob("*"):
            if not file_path.is_file() or not self._is_source_file(file_path):
                continue

            features = self._collect_basic_features(file_path)
            features.update(self._additional_features(file_path))
            features.update(vuln_features)

            label, confidence = self._infer_label(file_path, features)
            metadata = {
                "confidence": f"{confidence:.2f}",
                "label_source": "foundational_heuristic",
            }
            examples.append(
                self._to_training_example(repo, file_path, label, features, metadata)
            )

        return examples

    def validator(self):
        from ..validators.foundational import FoundationalValidator

        return FoundationalValidator()

    def _additional_features(self, file_path: Path) -> Dict[str, float]:
        text = file_path.read_text(errors="ignore")
        head = "\n".join(text.splitlines()[:30])
        has_spdx = bool(SPDX_PATTERN.search(head))

        lower_parts = [part.lower() for part in file_path.parts]
        is_test = 1.0 if any("test" in part for part in lower_parts) else 0.0

        docs_keywords = {"docs", "doc", "documentation", "guides", "manual"}
        is_docs = (
            1.0
            if any(part in docs_keywords or "docs" in part for part in lower_parts)
            else 0.0
        )
        if file_path.suffix.lower() in {".md", ".rst", ".adoc", ".txt"}:
            is_docs = 1.0
        return {
            "has_spdx_header": 1.0 if has_spdx else 0.0,
            "is_test_path": is_test,
            "is_docs_path": is_docs,
        }

    def _infer_label(
        self, file_path: Path, features: Dict[str, float]
    ) -> tuple[str, float]:
        lower_parts = [part.lower() for part in file_path.parts]
        if any(part in {"vendor", "third_party", "external"} for part in lower_parts):
            return "third_party", 0.95
        if features.get("has_spdx_header", 0.0) >= 0.5:
            return "third_party", 0.9
        if any(part in {"test", "tests"} for part in lower_parts):
            return "foreground", 0.85
        return "foreground", 0.9
