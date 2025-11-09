"""Security, licensing, and compliance-focused feature extractor."""

from __future__ import annotations

import math
import re
from pathlib import Path
from typing import Dict, List, Tuple

from ..core import RepoSpec, TrainingExample
from .base import BaseExtractor


MANIFEST_FILENAMES = {
    "requirements.txt",
    "requirements-dev.txt",
    "package.json",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "settings.gradle",
    "go.mod",
    "go.sum",
    "Cargo.toml",
    "Cargo.lock",
    "composer.json",
    "composer.lock",
    "Gemfile",
    "Gemfile.lock",
    "Pipfile",
    "Pipfile.lock",
    "pyproject.toml",
    "environment.yml",
    "conda.yml",
    "sbom.json",
    "bom.json",
}

CONFIG_SUFFIXES = {
    ".env",
    ".yml",
    ".yaml",
    ".ini",
    ".cfg",
    ".conf",
}

LICENSE_KEYWORDS = (
    "permission is hereby granted",
    "apache license",
    "gnu general public license",
    "mozilla public license",
    "bsd license",
    "all rights reserved",
    "copyright",
    "licensed under",
)

SPDX_REGEX = re.compile(r"spdx-license-identifier:\s*[A-Za-z0-9.+-]+", re.IGNORECASE)

PRIVATE_KEY_REGEX = re.compile(r"-----BEGIN (?:RSA |DSA |EC |OPENSSH )?PRIVATE KEY-----", re.IGNORECASE)

SECRET_PATTERNS = (
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"(?i)(api[_-]?key|access[_-]?key)[\"'=:\s]+([A-Za-z0-9\-_/]{16,})"),
    re.compile(r"(?i)secret[_-]?key[\"'=:\s]+([A-Za-z0-9+/=]{12,})"),
    re.compile(r"(?i)(token|password|passphrase)[\"'=:\s]+([^\"'\s]{8,})"),
)

CREDENTIAL_KEYWORDS = (
    "password",
    "secret",
    "apikey",
    "token",
    "access_key",
    "client_secret",
    "private_key",
    "api_key",
)

URL_REGEX = re.compile(r"https?://[^\s\"']+", re.IGNORECASE)

THIRD_PARTY_DIRS = {"vendor", "third_party", "external", "licenses", "deps"}

HIGH_ENTROPY_THRESHOLD = 3.8


class SecurityExtractor(BaseExtractor):
    """Collect security, licensing, and compliance-oriented signals."""

    def extract(self, repo: RepoSpec) -> List[TrainingExample]:
        repo_dir = self._ensure_repo(repo)
        vuln_features = self._repo_vulnerability_features(repo_dir)
        examples: List[TrainingExample] = []

        for file_path in repo_dir.rglob("*"):
            if not file_path.is_file() or not self._should_inspect(file_path):
                continue

            text = file_path.read_text(errors="ignore")
            base_features = self._collect_basic_features(file_path)
            sec_features = self._security_features(file_path, text)
            features = {**base_features, **sec_features, **vuln_features}

            label, confidence = self._infer_label(file_path, features)
            metadata = {
                "confidence": f"{confidence:.2f}",
                "label_source": "security_heuristic",
                "risk_score": f"{features['secret_risk_score']:.2f}",
            }

            examples.append(
                self._to_training_example(repo, file_path, label, features, metadata)
            )

        return examples

    def validator(self):
        from ..validators.base import QualityValidator

        return QualityValidator()

    def _should_inspect(self, file_path: Path) -> bool:
        if self._is_source_file(file_path):
            return True
        name = file_path.name.lower()
        suffix = file_path.suffix.lower()
        if name in MANIFEST_FILENAMES:
            return True
        if suffix in CONFIG_SUFFIXES:
            return True
        if name in {".env", ".env.example"}:
            return True
        if name.endswith(".lock"):
            return True
        if name.endswith("sbom.json") or name.endswith("bom.json"):
            return True
        return False

    def _security_features(self, file_path: Path, text: str) -> Dict[str, float]:
        license_hits, spdx_present = self._license_signals(text)
        secret_hits, sensitive_assignments = self._secret_signals(text)
        private_key_indicator = 1.0 if PRIVATE_KEY_REGEX.search(text) else 0.0
        credential_density = self._credential_keyword_density(text)
        entropy_ratio = self._high_entropy_literal_ratio(text)
        url_count = float(len(URL_REGEX.findall(text)))

        manifest_indicator = 1.0 if file_path.name.lower() in MANIFEST_FILENAMES else 0.0
        sbom_indicator = 1.0 if self._is_sbom_file(file_path, text) else 0.0
        config_indicator = 1.0 if file_path.suffix.lower() in CONFIG_SUFFIXES or file_path.name.lower() in {".env", ".env.example"} else 0.0
        vendor_path_indicator = 1.0 if any(part.lower() in THIRD_PARTY_DIRS for part in file_path.parts) else 0.0

        secret_risk_score = self._secret_risk(secret_hits, private_key_indicator, entropy_ratio, sensitive_assignments)

        return {
            "license_keyword_hits": float(license_hits),
            "spdx_header_present": float(spdx_present),
            "secret_pattern_hits": float(secret_hits),
            "sensitive_assignment_hits": float(sensitive_assignments),
            "private_key_indicator": private_key_indicator,
            "credential_keyword_density": credential_density,
            "high_entropy_literal_ratio": entropy_ratio,
            "url_reference_count": url_count,
            "manifest_indicator": manifest_indicator,
            "sbom_indicator": sbom_indicator,
            "config_indicator": config_indicator,
            "vendor_path_indicator": vendor_path_indicator,
            "secret_risk_score": secret_risk_score,
        }

    def _infer_label(self, file_path: Path, features: Dict[str, float]) -> Tuple[str, float]:
        if features.get("vendor_path_indicator", 0.0) >= 1.0:
            return "third_party", 0.92
        if features.get("manifest_indicator", 0.0) >= 1.0 or features.get("sbom_indicator", 0.0) >= 1.0:
            return "third_party", 0.9
        if features.get("license_keyword_hits", 0.0) >= 2.0 or features.get("spdx_header_present", 0.0) >= 0.5:
            return "third_party", 0.85
        if features.get("private_key_indicator", 0.0) >= 1.0:
            return "foreground", 0.92
        if features.get("secret_pattern_hits", 0.0) >= 1.0:
            confidence = min(0.9, 0.75 + 0.05 * features["secret_pattern_hits"])
            return "foreground", float(confidence)
        if features.get("config_indicator", 0.0) >= 1.0 and features.get("credential_keyword_density", 0.0) >= 0.01:
            return "foreground", 0.78
        if features.get("high_entropy_literal_ratio", 0.0) >= 0.6:
            return "foreground", 0.72
        return "foreground", 0.6

    def _license_signals(self, text: str) -> Tuple[int, float]:
        lower = text.lower()
        hits = sum(1 for keyword in LICENSE_KEYWORDS if keyword in lower)
        spdx_present = 1.0 if SPDX_REGEX.search(text) else 0.0
        return hits, spdx_present

    def _secret_signals(self, text: str) -> Tuple[int, int]:
        secret_hits = 0
        sensitive_assignments = 0
        for pattern in SECRET_PATTERNS:
            matches = list(pattern.finditer(text))
            secret_hits += len(matches)
        assignment_pattern = re.compile(r"(?i)(password|secret|token|apikey|api_key)\s*[:=]\s*[\"']?[^\s\"']{6,}")
        sensitive_assignments = len(assignment_pattern.findall(text))
        return secret_hits, sensitive_assignments

    def _credential_keyword_density(self, text: str) -> float:
        if not text:
            return 0.0
        words = text.lower().split()
        if not words:
            return 0.0
        matches = sum(1 for word in words if any(keyword in word for keyword in CREDENTIAL_KEYWORDS))
        return matches / max(len(text.splitlines()), 1)

    def _high_entropy_literal_ratio(self, text: str) -> float:
        literals = re.findall(r"[\"']([A-Za-z0-9/_\-+=]{8,})[\"']", text)
        if not literals:
            return 0.0
        high_entropy = sum(1 for literal in literals if self._shannon_entropy(literal) >= HIGH_ENTROPY_THRESHOLD)
        return high_entropy / len(literals)

    def _shannon_entropy(self, value: str) -> float:
        counts: Dict[str, int] = {}
        for char in value:
            counts[char] = counts.get(char, 0) + 1
        length = len(value)
        entropy = 0.0
        for count in counts.values():
            probability = count / length
            entropy -= probability * math.log(probability, 2)
        return entropy

    def _is_sbom_file(self, file_path: Path, text: str) -> bool:
        lowered = file_path.name.lower()
        if "sbom" in lowered or "bom" in lowered:
            return True
        if "cyclonedx" in text or ("component" in text and "bomFormat" in text):
            return True
        return False

    def _secret_risk(self, secret_hits: int, private_key: float, entropy_ratio: float, sensitive_assignments: int) -> float:
        score = secret_hits * 0.25 + sensitive_assignments * 0.2 + entropy_ratio * 0.8 + private_key * 1.0
        return min(1.0, score)
