"""Base extractor utilities for training data generation."""

from __future__ import annotations

import json
import shutil
import subprocess
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, cast

import yaml

from ...scanners.vulnerabilities import VulnerabilityScanner
from ..core import ExtractionConfig, RepoSpec, TrainingExample
from ..validators import PhaseValidator

VULN_CACHE_PATH = Path("training/cache/vuln_scan_cache.json")
VULN_CACHE_MAX_AGE_SECONDS = 7 * 24 * 60 * 60  # 7 days


class BaseExtractor(ABC):
    """Base class providing clone + scan helpers for phase extractors."""

    def __init__(self, config: ExtractionConfig) -> None:
        self.config = config
        self.cache_dir = Path(".forgetrace-cache") / "repos"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.config_dir = Path("config.yaml")
        self._config_cache: Optional[Dict[str, Any]] = None
        self._vuln_metric_cache: Dict[Path, Dict[str, float]] = {}
        self._vuln_cache_store: Dict[str, Any] = self._load_vuln_scan_cache()

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
            raise (
                last_error
                if last_error is not None
                else RuntimeError(f"Unable to clone repository {repo.name}")
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
                print(
                    f"⚠️ Update failed for {repo_dir.name}, continuing with cached version"
                )
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
        comment_lines = sum(
            1 for line in lines if line.strip().startswith(("#", "//", "/*", "*", "--"))
        )
        return comment_lines / len(lines)

    def _is_source_file(self, file_path: Path) -> bool:
        source_extensions = {
            ".py",
            ".js",
            ".ts",
            ".java",
            ".go",
            ".rs",
            ".c",
            ".cpp",
            ".h",
            ".rb",
            ".php",
            ".scala",
            ".kt",
            ".swift",
            ".m",
            ".cs",
            ".sh",
        }
        excluded_dirs = {
            "node_modules",
            "vendor",
            ".git",
            "build",
            "dist",
            "__pycache__",
        }

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

    def _to_training_example(
        self,
        repo: RepoSpec,
        file_path: Path,
        label: str,
        features: Dict[str, float],
        metadata: Dict[str, str],
    ) -> TrainingExample:
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

        disk_cache_key = self._build_vuln_cache_key(repo_dir)
        cached_entry = (
            self._vuln_cache_store.get(disk_cache_key) if disk_cache_key else None
        )
        if cached_entry:
            metrics_payload = cached_entry.get("metrics")
            if isinstance(metrics_payload, dict):
                metrics_dict = cast(Dict[str, Any], metrics_payload)
            else:
                metrics_dict = {}
            timestamp = float(cached_entry.get("timestamp", 0.0) or 0.0)
            if time.time() - timestamp <= VULN_CACHE_MAX_AGE_SECONDS:
                numeric_metrics = self._coerce_metric_map(metrics_dict)
                if numeric_metrics:
                    self._vuln_metric_cache[cache_key] = numeric_metrics
                    if numeric_metrics.get("repo_vulnerability_count", 0.0) == 0.0:
                        print(
                            f"ℹ️  Cached vulnerability metrics for {repo_dir.name} are zeroed; "
                            "rerun debug script if this seems incorrect."
                        )
                    else:
                        print(
                            f"✅ Loaded cached vulnerability metrics for {repo_dir.name}"
                        )
                    return numeric_metrics

        config = self._load_config()
        vuln_config_raw = config.get("vulnerability_scanning", {})
        vuln_config = (
            cast(Dict[str, Any], vuln_config_raw)
            if isinstance(vuln_config_raw, dict)
            else {}
        )
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

        scan_summary: Dict[str, Any] = {}
        scan_failed = False

        try:
            scanner = VulnerabilityScanner(repo_path=repo_dir, config=config)
            scan_summary = scanner.scan()
            metrics = {
                "repo_vuln_density": float(
                    scan_summary.get("normalized_vuln_density", 0.0) or 0.0
                ),
                "repo_vuln_weighted_score": float(
                    scan_summary.get("weighted_vuln_score", 0.0) or 0.0
                ),
                "repo_osv_noise_ratio": float(
                    scan_summary.get("osv_noise_ratio", 0.0) or 0.0
                ),
                "repo_vulnerability_count": float(
                    scan_summary.get("total_vulnerabilities", 0.0) or 0.0
                ),
            }

            risk_metrics: Dict[str, Any] = {}
            raw_risk = scan_summary.get("risk_analysis", {})
            if isinstance(raw_risk, dict):
                risk_metrics = cast(Dict[str, Any], raw_risk)

            if risk_metrics:
                risky_count = risk_metrics.get("risky_dependency_count", 0.0)
                risky_ratio = risk_metrics.get("risky_dependency_ratio", 0.0)
                weighted_risk = risk_metrics.get("weighted_risk_score", 0.0)
                unpinned_ratio = risk_metrics.get("unpinned_ratio", 0.0)

                if metrics["repo_vulnerability_count"] == 0.0 and isinstance(
                    risky_count, (int, float)
                ):
                    metrics["repo_vulnerability_count"] = float(risky_count)
                if metrics["repo_vuln_density"] == 0.0 and isinstance(
                    risky_ratio, (int, float)
                ):
                    metrics["repo_vuln_density"] = float(risky_ratio)
                if metrics["repo_vuln_weighted_score"] == 0.0 and isinstance(
                    weighted_risk, (int, float)
                ):
                    metrics["repo_vuln_weighted_score"] = float(weighted_risk)
                if metrics["repo_osv_noise_ratio"] == 0.0 and isinstance(
                    unpinned_ratio, (int, float)
                ):
                    metrics["repo_osv_noise_ratio"] = float(unpinned_ratio)
        except Exception as exc:  # pragma: no cover - defensive guard
            print(f"⚠️  Vulnerability scan failed for {repo_dir}: {exc}")
            scan_failed = True

        self._vuln_metric_cache[cache_key] = metrics
        if disk_cache_key:
            self._persist_vuln_metrics(disk_cache_key, metrics)

        dependency_count = 0.0
        if scan_summary:
            dependency_count = float(scan_summary.get("total_packages", 0.0) or 0.0)

        if metrics.get("repo_vulnerability_count", 0.0) == 0.0:
            if scan_failed:
                print(
                    f"⚠️  Vulnerability metrics for {repo_dir.name} are zero; "
                    "run scripts/debug_vuln_extraction.py to validate inputs."
                )
            elif dependency_count == 0.0:
                print(
                    f"ℹ️  No dependency manifests detected for {repo_dir.name}; "
                    "vulnerability metrics remain zero."
                )
            else:
                print(
                    f"⚠️  Vulnerability metrics for {repo_dir.name} are zero; "
                    "run scripts/debug_vuln_extraction.py to validate inputs."
                )
        else:
            print(
                f"🔍 Vulnerability metrics for {repo_dir.name}: "
                f"count={metrics['repo_vulnerability_count']} density={metrics['repo_vuln_density']} "
                f"weighted_score={metrics['repo_vuln_weighted_score']} noise={metrics['repo_osv_noise_ratio']}"
            )

        return metrics

    def _build_vuln_cache_key(self, repo_dir: Path) -> Optional[str]:
        try:
            git_dir = repo_dir.resolve()
            commit = (
                subprocess.check_output(
                    ["git", "rev-parse", "HEAD"], cwd=git_dir, stderr=subprocess.DEVNULL
                )
                .decode("utf-8")
                .strip()
            )
            return f"{git_dir}:{commit}"
        except Exception:
            return None

    def _load_vuln_scan_cache(self) -> Dict[str, Any]:
        if not VULN_CACHE_PATH.exists():
            return {}
        try:
            raw = VULN_CACHE_PATH.read_text(encoding="utf-8")
            data = json.loads(raw)
            if isinstance(data, dict):
                return cast(Dict[str, Any], data)
        except Exception as exc:  # pragma: no cover - diagnostic info
            print(f"⚠️  Unable to load vulnerability cache: {exc}")
        return {}

    def _persist_vuln_metrics(self, cache_key: str, metrics: Dict[str, float]) -> None:
        self._vuln_cache_store[cache_key] = {
            "timestamp": time.time(),
            "metrics": metrics,
        }
        try:
            VULN_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
            VULN_CACHE_PATH.write_text(
                json.dumps(self._vuln_cache_store, indent=2), encoding="utf-8"
            )
        except Exception as exc:  # pragma: no cover - diagnostic info
            print(f"⚠️  Failed to persist vulnerability cache: {exc}")

    def _coerce_metric_map(self, payload: Dict[str, Any]) -> Dict[str, float]:
        numeric: Dict[str, float] = {}
        for key, value in payload.items():
            if isinstance(value, (int, float)):
                numeric[key] = float(value)
            else:
                try:
                    numeric[key] = float(value)
                except (TypeError, ValueError):
                    continue
        required = {
            "repo_vuln_density",
            "repo_vuln_weighted_score",
            "repo_osv_noise_ratio",
            "repo_vulnerability_count",
        }
        return numeric if required.issubset(numeric.keys()) else {}


def serialize_examples(examples: List[TrainingExample], path: Path) -> None:
    """Utility to persist training examples as JSON lines."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for example in examples:
            fh.write(
                json.dumps(
                    {
                        "repo": example.repo.name,
                        "phase": example.repo.phase.name,
                        "file_path": example.file_path,
                        "label": example.label,
                        "features": example.features,
                        "metadata": example.metadata,
                    }
                )
                + "\n"
            )
