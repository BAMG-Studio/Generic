"""Base extractor utilities for training data generation."""

from __future__ import annotations

import json
import shutil
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, cast

import yaml

from ..core import ExtractionConfig, RepoSpec, TrainingExample
from ..validators import PhaseValidator
from ...scanners.vulnerabilities import VulnerabilityScanner


class BaseExtractor(ABC):
    """Base class providing clone + scan helpers for phase extractors."""

    def __init__(self, config: ExtractionConfig) -> None:
        self.config = config
        self.cache_dir = Path(".forgetrace-cache") / "repos"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.config_dir = Path("config.yaml")
        self._config_cache: Optional[Dict[str, Any]] = None
        self._vuln_metric_cache: Dict[Path, Dict[str, float]] = {}

    @abstractmethod
    def extract(self, repo: RepoSpec) -> List[TrainingExample]:
        """Collect training examples for a single repository."""

    @abstractmethod
    def validator(self) -> PhaseValidator:
        """Return validator responsible for this phase."""

    def _ensure_repo(self, repo: RepoSpec) -> Path:
        """Clone the repository to a local cache directory if needed."""

        repo_dir = self.cache_dir / repo.short_name()
        if repo_dir.exists():
            self._update_repo(repo_dir)
            return repo_dir

        print(f"📥 Cloning {repo.name} for phase {repo.phase.name}")
        depths: List[Optional[int]] = [500, 200, 50, 10, None]
        last_error: Optional[subprocess.CalledProcessError] = None

        for depth in depths:
            if repo_dir.exists():
                shutil.rmtree(repo_dir, ignore_errors=True)

            clone_cmd = ["git", "clone"]
            if depth is not None:
                clone_cmd.extend(["--depth", str(depth)])
            clone_cmd.extend([repo.url, str(repo_dir)])

            try:
                subprocess.run(clone_cmd, check=True)
                break
            except subprocess.CalledProcessError as error:
                last_error = error
                print(f"⚠️ Clone failed with depth={depth}; retrying...")
        else:
            # Exhausted retries; bubble up the last failure to halt the phase cleanly.
            raise last_error if last_error is not None else RuntimeError(
                f"Unable to clone repository {repo.name}"
            )
        return repo_dir

    def _update_repo(self, repo_dir: Path) -> None:
        """Fetch latest changes for existing clone."""

        for attempt in range(3):
            try:
                subprocess.run(
                    ["git", "fetch", "--all", "--prune"],
                    cwd=repo_dir,
                    check=True,
                    timeout=60,
                )
                subprocess.run(
                    ["git", "reset", "--hard", "origin/HEAD"],
                    cwd=repo_dir,
                    check=True,
                )
                break
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                if attempt < 2:
                    print(f"⚠️ Update failed for {repo_dir.name}, retrying...")
                    continue
                print(f"⚠️ Update failed for {repo_dir.name}, continuing with cached version")
                break

    def _collect_basic_features(self, file_path: Path) -> Dict[str, float]:
        """Extract minimal language-agnostic features for bootstrapping."""

        text = file_path.read_text(errors="ignore")
        lines = text.splitlines()
        loc = len(lines)
        words = sum(len(line.split()) for line in lines)
        comment_ratio = self._estimate_comment_ratio(lines)

        return {
            "lines_of_code": float(loc),
            "avg_line_length": float(words / loc) if loc else 0.0,
            "comment_ratio": comment_ratio,
            "path_depth": float(len(file_path.parts)),
            "file_size_bytes": float(file_path.stat().st_size),
        }

    def _estimate_comment_ratio(self, lines: List[str]) -> float:
        if not lines:
            return 0.0
        comment_lines = sum(1 for line in lines if line.strip().startswith(('#', '//', '/*', '*', '--')))
        return comment_lines / len(lines)

    def _is_source_file(self, file_path: Path) -> bool:
        source_extensions = {
            '.py', '.js', '.ts', '.java', '.go', '.rs', '.c', '.cpp', '.h',
            '.rb', '.php', '.scala', '.kt', '.swift', '.m', '.cs', '.sh'
        }
        excluded_dirs = {'node_modules', 'vendor', '.git', 'build', 'dist', '__pycache__'}

        if file_path.suffix not in source_extensions:
            return False
        if any(part in excluded_dirs for part in file_path.parts):
            return False
        return True

    def _features_to_numeric(self, feature_map: Dict[str, object]) -> Dict[str, float]:
        numeric_features: Dict[str, float] = {}
        for key, value in feature_map.items():
            if isinstance(value, bool):
                numeric_features[key] = 1.0 if value else 0.0
            elif isinstance(value, (int, float)):
                numeric_features[key] = float(value)
        return numeric_features

    def _to_training_example(self, repo: RepoSpec, file_path: Path, label: str, features: Dict[str, float], metadata: Dict[str, str]) -> TrainingExample:
        return TrainingExample(
            repo=repo,
            file_path=str(file_path),
            label=label,
            features=features,
            metadata=metadata,
        )

    def _load_config(self) -> Dict[str, Any]:
        if self._config_cache is not None:
            return self._config_cache

        if not self.config_dir.exists():
            self._config_cache = {}
            return self._config_cache

        try:
            with self.config_dir.open("r", encoding="utf-8") as fh:
                raw = yaml.safe_load(fh)
        except Exception as exc:
            print(f"⚠️  Unable to load config.yaml: {exc}")
            raw = None

        if isinstance(raw, dict):
            loaded_config = cast(Dict[str, Any], raw)
        else:
            loaded_config = {}

        self._config_cache = loaded_config
        return self._config_cache

    def _repo_vulnerability_features(self, repo_dir: Path) -> Dict[str, float]:
        cache_key = repo_dir.resolve()
        cached = self._vuln_metric_cache.get(cache_key)
        if cached is not None:
            return cached

        config = self._load_config()
        vuln_config_raw = config.get("vulnerability_scanning", {})
        vuln_config = cast(Dict[str, Any], vuln_config_raw) if isinstance(vuln_config_raw, dict) else {}
        if vuln_config and not bool(vuln_config.get("enabled", True)):
            metrics = {
                "repo_vuln_density": 0.0,
                "repo_vuln_weighted_score": 0.0,
                "repo_osv_noise_ratio": 0.0,
                "repo_vulnerability_count": 0.0,
            }
            self._vuln_metric_cache[cache_key] = metrics
            return metrics

        metrics = {
            "repo_vuln_density": 0.0,
            "repo_vuln_weighted_score": 0.0,
            "repo_osv_noise_ratio": 0.0,
            "repo_vulnerability_count": 0.0,
        }

        try:
            scanner = VulnerabilityScanner(repo_path=repo_dir, config=config)
            results = scanner.scan()
            metrics = {
                "repo_vuln_density": float(results.get("normalized_vuln_density", 0.0) or 0.0),
                "repo_vuln_weighted_score": float(results.get("weighted_vuln_score", 0.0) or 0.0),
                "repo_osv_noise_ratio": float(results.get("osv_noise_ratio", 0.0) or 0.0),
                "repo_vulnerability_count": float(results.get("total_vulnerabilities", 0.0) or 0.0),
            }
        except Exception as exc:  # pragma: no cover - defensive guard
            print(f"⚠️  Vulnerability scan failed for {repo_dir}: {exc}")

        self._vuln_metric_cache[cache_key] = metrics
        return metrics


def serialize_examples(examples: List[TrainingExample], path: Path) -> None:
    """Utility to persist training examples as JSON lines."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for example in examples:
            fh.write(json.dumps({
                "repo": example.repo.name,
                "phase": example.repo.phase.name,
                "file_path": example.file_path,
                "label": example.label,
                "features": example.features,
                "metadata": example.metadata,
            }) + "\n")