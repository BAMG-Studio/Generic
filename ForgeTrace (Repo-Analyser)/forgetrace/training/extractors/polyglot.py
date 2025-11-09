"""Polyglot expansion extractor."""

from __future__ import annotations

import math
import re
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from ..core import RepoSpec, TrainingExample
from .base import BaseExtractor


LANGUAGE_EXTENSIONS: Dict[str, Tuple[str, ...]] = {
    "python": (".py",),
    "javascript": (".js", ".jsx", ".mjs", ".cjs"),
    "typescript": (".ts", ".tsx"),
    "java": (".java",),
    "go": (".go",),
    "rust": (".rs",),
    "php": (".php",),
    "cpp": (".cc", ".cpp", ".cxx", ".hpp", ".hh", ".h"),
    "c": (".c", ".h"),
    "scala": (".scala",),
}


LANGUAGE_IMPORT_RULES: Dict[str, Dict[str, Sequence[str]]] = {
    "python": {
        "stdlib": (
            "os",
            "sys",
            "json",
            "pathlib",
            "collections",
            "typing",
            "math",
            "datetime",
            "subprocess",
            "re",
        ),
        "third_party": (),
    },
    "javascript": {
        "stdlib": ("fs", "path", "http", "https", "crypto"),
        "third_party": ("react", "vue", "angular", "svelte", "lodash"),
    },
    "typescript": {
        "stdlib": ("fs", "path", "http"),
        "third_party": ("@angular", "rxjs", "vue", "react"),
    },
    "java": {
        "stdlib": ("java.", "javax.", "org.w3c", "org.xml"),
        "third_party": ("org.springframework", "com.google", "org.apache"),
    },
    "go": {
        "stdlib": ("fmt", "io", "net", "os", "time", "context"),
        "third_party": (),
    },
    "rust": {
        "stdlib": ("std", "core", "alloc"),
        "third_party": ("tokio", "serde", "regex", "clap"),
    },
    "php": {
        "stdlib": ("App",),
        "third_party": ("Illuminate", "Symfony", "Laravel"),
    },
    "scala": {
        "stdlib": ("scala.", "java."),
        "third_party": ("org.apache.", "com.twitter.", "io.circe."),
        "tests": ("org.scalatest.", "munit."),
    },
    "cpp": {
        "stdlib": ("<iostream>", "<vector>", "<map>", "<string>", "<memory>"),
        "third_party": ("<boost", "<gtest", "<fmt", "Eigen", "Qt"),
    },
    "c": {
        "stdlib": ("<stdio.h>", "<stdlib.h>", "<string.h>", "<math.h>"),
        "third_party": ("<openssl", "<uv.h>", "<zlib.h>"),
    },
}


THIRD_PARTY_DIRS = {"vendor", "third_party", "external", "deps", "node_modules"}


class PolyglotExtractor(BaseExtractor):
    """Extract cross-language feature signals for imported vs original code."""

    def extract(self, repo: RepoSpec) -> List[TrainingExample]:
        repo_dir = self._ensure_repo(repo)
        vuln_features = self._repo_vulnerability_features(repo_dir)
        examples: List[TrainingExample] = []

        for file_path in repo_dir.rglob("*"):
            if not file_path.is_file() or not self._is_source_file(file_path):
                continue

            language = self._detect_language(file_path)
            if language is None:
                continue

            text = file_path.read_text(errors="ignore")
            base_features = self._collect_basic_features(file_path)
            lang_features = self._language_features(language, file_path, text)
            features = {**base_features, **lang_features, **vuln_features}

            label, confidence = self._infer_label(features)
            metadata = {
                "language": language,
                "confidence": f"{confidence:.2f}",
                "label_source": "polyglot_heuristic",
            }

            examples.append(
                self._to_training_example(repo, file_path, label, features, metadata)
            )

        return examples

    def validator(self):
        from ..validators.base import QualityValidator

        return QualityValidator()

    def _detect_language(self, file_path: Path) -> Optional[str]:
        suffix = file_path.suffix.lower()
        for language, extensions in LANGUAGE_EXTENSIONS.items():
            if suffix in extensions:
                return language
        return None

    def _language_features(self, language: str, file_path: Path, text: str) -> Dict[str, float]:
        lines = text.splitlines()
        imports = self._import_metrics(language, lines)
        entropy = self._token_entropy(text)
        nesting = self._nesting_depth(language, text)
        vendor_indicator = 1.0 if any(part.lower() in THIRD_PARTY_DIRS for part in file_path.parts) else 0.0

        return {
            "language_entropy": entropy,
            "nesting_depth": nesting,
            "external_import_ratio": imports["external_ratio"],
            "stdlib_import_ratio": imports["stdlib_ratio"],
            "import_count": imports["total"],
            "vendor_path_indicator": vendor_indicator,
        }

    def _infer_label(self, features: Dict[str, float]) -> Tuple[str, float]:
        external_ratio = features.get("external_import_ratio", 0.0)
        vendor_indicator = features.get("vendor_path_indicator", 0.0)
        nesting = features.get("nesting_depth", 0.0)
        entropy = features.get("language_entropy", 0.0)

        if vendor_indicator >= 1.0 or external_ratio >= 0.7:
            return "third_party", 0.9
        if external_ratio >= 0.5 and entropy >= 3.0:
            return "third_party", 0.8
        if nesting <= 2.0 and entropy <= 2.5 and external_ratio <= 0.3:
            return "foreground", 0.8
        return "foreground", 0.6

    def _import_metrics(self, language: str, lines: List[str]) -> Dict[str, float]:
        rules = LANGUAGE_IMPORT_RULES.get(language, {"stdlib": (), "third_party": ()})
        stdlib_hints = rules.get("stdlib", ())
        external_hints = rules.get("third_party", ())

        total = 0
        stdlib = 0
        third_party = 0

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            target = self._extract_import_target(language, stripped)
            if target is None:
                continue

            total += 1

            if self._matches_any(target, stdlib_hints):
                stdlib += 1
                continue
            if self._matches_any(target, external_hints):
                third_party += 1
                continue

            if language in {"python", "go", "rust"}:
                if target.startswith((".", "_")):
                    stdlib += 1
                else:
                    third_party += 1
            elif language in {"javascript", "typescript"}:
                if target.startswith((".", "/")):
                    stdlib += 1
                else:
                    third_party += 1
            elif language == "java":
                if target.startswith("java.") or target.startswith("javax."):
                    stdlib += 1
                else:
                    third_party += 1
            elif language == "scala":
                if target.startswith("scala.") or target.startswith("java."):
                    stdlib += 1
                else:
                    third_party += 1
            elif language in {"cpp", "c"}:
                if target.startswith("<"):
                    stdlib += 1
                else:
                    third_party += 1
            elif language == "php":
                root = target.split("\\")[0]
                if root and root not in stdlib_hints:
                    third_party += 1
                else:
                    stdlib += 1
            else:
                third_party += 1

        if total == 0:
            total = 1

        stdlib_ratio = stdlib / total
        external_ratio = third_party / total

        return {
            "total": float(total),
            "stdlib_ratio": stdlib_ratio,
            "external_ratio": external_ratio,
        }

    def _extract_import_target(self, language: str, line: str) -> Optional[str]:
        if language == "python":
            if line.startswith("from ") or line.startswith("import "):
                parts = line.replace(",", " ").split()
                if len(parts) >= 2:
                    return parts[1].split(".")[0]
        elif language in {"javascript", "typescript"}:
            match = re.search(r"from\s+['\"]([^'\"]+)['\"]", line)
            if not match:
                match = re.search(r"require\(['\"]([^'\"]+)['\"]\)", line)
            if match:
                return match.group(1)
        elif language == "go":
            match = re.search(r'"([^"\s]+)"', line)
            if match:
                return match.group(1)
        elif language == "rust":
            if line.startswith("use "):
                parts = line.split()
                if len(parts) >= 2:
                    return parts[1].split("::")[0]
        elif language == "java":
            if line.startswith("import "):
                return line[len("import "):].rstrip(";")
        elif language == "scala":
            if line.startswith("import "):
                return line[len("import "):].strip()
        elif language in {"cpp", "c"}:
            match = re.search(r"#include\s*[<\"]([^>\"]+)[>\"]", line)
            if match:
                token = match.group(1)
                return f"<{token}>" if line.strip().startswith("#include <") else f'"{token}"'
        elif language == "php":
            if line.startswith("use "):
                return line[len("use "):].rstrip(";")
        return None

    def _matches_any(self, target: str, hints: Iterable[str]) -> bool:
        return any(target.startswith(hint) for hint in hints)

    def _token_entropy(self, text: str) -> float:
        tokens = re.findall(r"[A-Za-z_]+", text)
        if not tokens:
            return 0.0
        counts = Counter(tokens)
        total = sum(counts.values())
        entropy = -sum((count / total) * math.log(count / total, 2) for count in counts.values())
        return float(entropy)

    def _nesting_depth(self, language: str, text: str) -> float:
        if language in {"python"}:
            indent_levels = [len(line) - len(line.lstrip(" ")) for line in text.splitlines() if line.strip()]
            if not indent_levels:
                return 0.0
            normalized = [level // 4 for level in indent_levels]
            return float(max(normalized))

        depth = 0
        max_depth = 0
        for char in text:
            if char in "{[":
                depth += 1
                max_depth = max(max_depth, depth)
            elif char in "}]":
                depth = max(depth - 1, 0)
        return float(max_depth)
