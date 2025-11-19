"""
ML-Based IP Classifier - Author: Peter

WHAT: Machine learning classifier for intelligent code origin detection
WHY: Rule-based classifiers are brittle and miss nuanced patterns. ML learns from examples.

  * Resistant to overfitting with proper parameters (n_estimators=100, max_depth=10)
  * Fast training and inference (<1 second for typical codebases)

- Alternative algorithms considered:
  * Logistic Regression: Too simple, assumes linear separability
  * Neural Networks: Overkill for tabular data, requires more training data
  * SVM: Slower inference, harder to interpret feature importance
  * Naive Bayes: Strong independence assumption doesn't hold for code features

FEATURE ENGINEERING PHILOSOPHY:
We extract 20+ features grouped into 5 categories because each captures different signals:
1. File metadata (size, extension, path depth) - structural clues
2. Git history (author count, commit frequency, age) - ownership signals
3. Code complexity (cyclomatic, maintainability) - sophistication indicators
4. License patterns (file headers, SPDX tags) - legal markers
5. Import/dependency analysis (stdlib vs third-party) - usage patterns

TRAINING DATA STRATEGY:
- Bootstrap approach: Start with heuristic labels (high confidence only)
- Human-in-the-loop: Export uncertain predictions for manual review
- Continuous learning: Retrain as labeled dataset grows
- Cross-validation: 5-fold to prevent overfitting to specific projects

CONFIDENCE SCORING:
Random Forest provides probability distributions. We use these to:
- High confidence (>0.8): Auto-classify, no human review
- Medium confidence (0.5-0.8): Classify with warning flag
- Low confidence (<0.5): Flag for mandatory human review

This three-tier system balances automation with accuracy.
"""

import hashlib
import json
import math
import re
from collections import Counter
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple, cast

import joblib

ENTERPRISE_MODULE_DIRS: Set[str] = {
    "modules",
    "module",
    "addons",
    "apps",
    "services",
    "service",
    "domains",
    "features",
    "packages",
    "bundles",
}

ENTERPRISE_VENDOR_DIRS: Set[str] = {
    "vendor",
    "third_party",
    "external",
    "community",
    "addons-community",
}

ENTERPRISE_CONFIG_FILES: Set[str] = {
    "application.yml",
    "application.yaml",
    "application.properties",
    "settings.py",
    "settings.gradle",
    "config.py",
    "config.json",
    "odoo.conf",
    "docker-compose.yml",
    "docker-compose.yaml",
    "helmfile.yaml",
    "helmfile.yml",
    "values.yaml",
    "values.yml",
}

TEMPLATE_SUFFIXES: Set[str] = {
    ".html",
    ".xml",
    ".jinja",
    ".jinja2",
    ".tpl",
    ".ftl",
    ".twig",
}

FRAMEWORK_KEYWORDS: Tuple[str, ...] = (
    "org.springframework",
    "@RestController",
    "@Service",
    "@Repository",
    "@Controller",
    "odoo.models",
    "from odoo",
    "django.db",
    "fastapi",
    "flask",
    "celery",
    "kafka",
    "rabbitmq",
    "graphql",
    "typeorm",
    "nestjs",
    "ActiveRecord",
    "EntityManager",
    "CommandHandler",
)

BUSINESS_TERMS: Tuple[str, ...] = (
    "invoice",
    "billing",
    "ledger",
    "customer",
    "client",
    "account",
    "payment",
    "subscription",
    "contract",
    "policy",
    "compliance",
    "workflow",
    "fulfillment",
    "inventory",
    "supply",
    "warehouse",
    "logistics",
    "quotation",
    "order",
    "approval",
)

API_ENDPOINT_PATTERNS: Tuple[re.Pattern[str], ...] = (
    re.compile(r"@(?:Get|Post|Put|Delete|Patch)Mapping"),
    re.compile(r"@RequestMapping"),
    re.compile(r"app\.(?:get|post|put|delete|patch)\(", re.IGNORECASE),
    re.compile(r"router\.[a-z]+\(", re.IGNORECASE),
    re.compile(r"^\s*def\s+[a-z0-9_]+\(self,\s*request", re.IGNORECASE | re.MULTILINE),
    re.compile(r"Route::[a-zA-Z]+"),
)

PLUGIN_PATTERNS: Tuple[re.Pattern[str], ...] = (
    re.compile(r"register_(?:module|plugin|addon)", re.IGNORECASE),
    re.compile(r"init_app\(", re.IGNORECASE),
    re.compile(r"Module\.forRoot"),
    re.compile(r"apps\.populate"),
    re.compile(r"registerPlugin", re.IGNORECASE),
    re.compile(r"add_extension", re.IGNORECASE),
    re.compile(r"ExtensionPoint", re.IGNORECASE),
)

ASYNC_KEYWORDS: Tuple[str, ...] = (
    "async def",
    "@Async",
    "Celery",
    "apply_async",
    "Promise",
    "CompletableFuture",
    "TaskRunner",
    "asyncio",
    "asyncio.create_task",
    "RxJava",
    "EventLoop",
)

DATA_ACCESS_KEYWORDS: Tuple[str, ...] = (
    "Repository",
    "EntityManager",
    "Session",
    "cursor.execute",
    "SELECT ",
    "INSERT ",
    "UPDATE ",
    "DELETE ",
    "load_workbook",
)

ORCHESTRATION_KEYWORDS: Tuple[str, ...] = (
    "orchestr",
    "workflow",
    "pipeline",
    "scheduler",
    "cron",
    "airflow",
    "dag",
)

MANIFEST_FILENAMES: Set[str] = {
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

CONFIG_SUFFIXES: Set[str] = {
    ".env",
    ".yml",
    ".yaml",
    ".ini",
    ".cfg",
    ".conf",
}

LICENSE_KEYWORDS: Tuple[str, ...] = (
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

PRIVATE_KEY_REGEX = re.compile(
    r"-----BEGIN (?:RSA |DSA |EC |OPENSSH )?PRIVATE KEY-----", re.IGNORECASE
)

SECRET_PATTERNS: Tuple[re.Pattern[str], ...] = (
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"(?i)(api[_-]?key|access[_-]?key)[\"'=:\s]+([A-Za-z0-9\-_/]{16,})"),
    re.compile(r"(?i)secret[_-]?key[\"'=:\s]+([A-Za-z0-9+/=]{12,})"),
    re.compile(r"(?i)(token|password|passphrase)[\"'=:\s]+([^\"'\s]{8,})"),
)

CREDENTIAL_KEYWORDS: Tuple[str, ...] = (
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

HIGH_ENTROPY_THRESHOLD = 3.8

NOTEBOOK_SUFFIXES: Set[str] = {".ipynb", ".rmd", ".qmd"}

EXPERIMENT_CONFIG_NAMES: Set[str] = {
    "config.yaml",
    "config.yml",
    "experiment.yaml",
    "experiment.yml",
    "config.json",
    "hparams.yaml",
    "hyperparams.yaml",
    "params.json",
}

EXPERIMENT_DIR_KEYWORDS: Set[str] = {
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

LICENSE_PERMISSIVE: Set[str] = {"mit", "bsd", "apache", "isc", "cc-by"}

DATASET_KEYWORDS: Tuple[str, ...] = (
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

ML_FRAMEWORK_KEYWORDS: Tuple[str, ...] = (
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

METRIC_KEYWORDS: Tuple[str, ...] = (
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

FIGURE_KEYWORDS: Tuple[str, ...] = (
    "figure",
    "plot",
    "chart",
    "graph",
    "visualization",
)

CITATION_REGEX = re.compile(r"\[[0-9]{1,3}\]")

PAPER_REFERENCE_REGEX = re.compile(
    r"\b(?:arxiv|doi|icml|neurips|cvpr|acl|sigir|iclr|kdd)[\w/:.-]*", re.IGNORECASE
)

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

THIRD_PARTY_DIRS: Set[str] = {
    "vendor",
    "third_party",
    "external",
    "deps",
    "node_modules",
    "licenses",
}


def _safe_entropy(text: str) -> float:
    if not text:
        return 0.0
    frequencies: Dict[str, int] = {}
    for char in text:
        frequencies[char] = frequencies.get(char, 0) + 1
    total = len(text)
    entropy = 0.0
    for count in frequencies.values():
        probability = count / total
        entropy -= probability * math.log(probability, 2)
    return entropy


# Conditional imports - gracefully degrade if ML libraries unavailable
# isort: off
try:
    import joblib
    import numpy as np
    from sklearn.ensemble import (  # type: ignore[import-untyped]
        RandomForestClassifier,
    )

    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    joblib = cast(Any, None)
    np = cast(Any, None)
    RandomForestClassifier = cast(Any, None)
# isort: on


class CodeOrigin(Enum):
    """
    Code origin categories.

    WHY THESE CATEGORIES:
    - THIRD_PARTY: External dependencies (npm, PyPI, etc.) - not your IP liability
    - BACKGROUND: Developer's prior work reused - potential IP issues if not properly licensed
    - FOREGROUND: Written specifically for this project - your owned IP
    - UNKNOWN: Insufficient data to classify - requires human review

    LEGAL SIGNIFICANCE:
    Background IP is the highest risk category because it may contain:
    - Code from previous employers (work-for-hire agreements)
    - Personal projects with incompatible licenses
    - Copy-pasted snippets from restricted sources
    """

    THIRD_PARTY = "third_party"
    BACKGROUND = "background"
    FOREGROUND = "foreground"
    UNKNOWN = "unknown"


@dataclass
class FileFeatures:
    """
    Feature vector for a single file.

    DESIGN: Dataclass chosen for:
    - Type safety (IDE autocomplete, static analysis)
    - Automatic __init__ generation
    - Easy conversion to dict via asdict()
    - Immutability support with frozen=True (not used here for flexibility)
    """

    # File metadata features
    file_path: str
    lines_of_code: int
    file_size_bytes: int
    extension: str
    path_depth: int  # How deep in directory tree (vendor/third_party often deeper)

    # Git history features
    commit_count: int  # Files with few commits likely imported wholesale
    author_count: int  # Single author suggests background IP, many authors = foreground
    days_since_first_commit: int
    days_since_last_commit: int
    commit_frequency: float  # commits per day - third-party rarely modified

    # Code complexity features (using radon if available)
    cyclomatic_complexity: float  # High complexity = likely sophisticated third-party
    maintainability_index: (
        float  # Low maintainability = possibly rushed background code
    )

    # License indicators
    has_license_header: bool  # SPDX tags, copyright notices
    has_third_party_indicators: bool  # Keywords: "Copyright", "Licensed under"

    # Import/dependency features
    import_count: int
    stdlib_import_ratio: float  # High stdlib ratio = likely original code
    third_party_import_ratio: float

    # Similarity features (from similarity scanner)
    max_similarity_score: float  # Highest match to known third-party code
    similar_file_count: int  # How many files share high similarity

    # Authorship patterns
    primary_author_commit_ratio: float  # Dominant author suggests background IP
    is_primary_author_external: bool  # Based on email domain analysis

    # Repository-level vulnerability posture
    repo_vuln_density: float  # Vulnerable packages / total packages
    repo_vuln_weighted_score: float  # Weighted CVSS score across actionable vulns
    repo_osv_noise_ratio: float  # Share of OSV entries filtered out
    repo_vulnerability_count: float  # Actionable vulnerability count
    extra_features: Dict[str, float] = field(default_factory=dict)

    def to_feature_map(self) -> Dict[str, float]:
        """Convert feature dataclass into a flat numeric mapping."""

        base_values: Dict[str, float] = {
            "lines_of_code": float(self.lines_of_code),
            "file_size_bytes": float(self.file_size_bytes),
            "path_depth": float(self.path_depth),
            "commit_count": float(self.commit_count),
            "author_count": float(self.author_count),
            "days_since_first_commit": float(self.days_since_first_commit),
            "days_since_last_commit": float(self.days_since_last_commit),
            "commit_frequency": float(self.commit_frequency),
            "cyclomatic_complexity": float(self.cyclomatic_complexity),
            "maintainability_index": float(self.maintainability_index),
            "has_license_header": 1.0 if self.has_license_header else 0.0,
            "has_third_party_indicators": (
                1.0 if self.has_third_party_indicators else 0.0
            ),
            "import_count": float(self.import_count),
            "stdlib_import_ratio": float(self.stdlib_import_ratio),
            "third_party_import_ratio": float(self.third_party_import_ratio),
            "max_similarity_score": float(self.max_similarity_score),
            "similar_file_count": float(self.similar_file_count),
            "primary_author_commit_ratio": float(self.primary_author_commit_ratio),
            "is_primary_author_external": (
                1.0 if self.is_primary_author_external else 0.0
            ),
            "repo_vuln_density": float(self.repo_vuln_density),
            "repo_vuln_weighted_score": float(self.repo_vuln_weighted_score),
            "repo_osv_noise_ratio": float(self.repo_osv_noise_ratio),
            "repo_vulnerability_count": float(self.repo_vulnerability_count),
        }
        base_values.update({k: float(v) for k, v in self.extra_features.items()})
        return base_values

    def to_array(self, order: Optional[Sequence[str]] = None) -> List[float]:
        """
        Convert features to numpy-compatible array.

        WHY THIS ORDER:
        - Numerical features first (most informative)
        - Boolean features converted to 0/1
        - String features excluded (need encoding separately)

        CAVEAT: Feature order must match training data exactly.
        Mismatch causes silent accuracy degradation!
        """
        feature_map = self.to_feature_map()
        if order is None:
            default_order: Sequence[str] = (
                "lines_of_code",
                "file_size_bytes",
                "path_depth",
                "commit_count",
                "author_count",
                "days_since_first_commit",
                "days_since_last_commit",
                "commit_frequency",
                "cyclomatic_complexity",
                "maintainability_index",
                "has_license_header",
                "has_third_party_indicators",
                "import_count",
                "stdlib_import_ratio",
                "third_party_import_ratio",
                "max_similarity_score",
                "similar_file_count",
                "primary_author_commit_ratio",
                "is_primary_author_external",
                "repo_vuln_density",
                "repo_vuln_weighted_score",
                "repo_osv_noise_ratio",
                "repo_vulnerability_count",
            )
            order = default_order
        return [float(feature_map.get(name, 0.0)) for name in order]


@dataclass
class ClassificationResult:
    """
    Result of ML classification for a single file.

    WHY INCLUDE CONFIDENCE:
    - Allows downstream systems to make risk-based decisions
    - Enables human-in-the-loop workflows (review low confidence)
    - Supports policy enforcement (e.g., "BLOCK if background + low confidence")
    """

    file_path: str
    predicted_origin: CodeOrigin
    confidence: float  # 0.0 to 1.0
    probability_distribution: Dict[str, float]  # All class probabilities
    features: FileFeatures
    requires_review: bool  # True if confidence < threshold


class MLIPClassifier:
    """
    Machine Learning IP Classifier.

    ARCHITECTURE:
    1. Feature Extraction: Convert raw scan data → numerical features
    2. ML Prediction: RandomForest → probability distributions
    3. Confidence Filtering: High confidence auto-accept, low confidence flag
    4. Fallback Logic: If ML unavailable, use rule-based heuristics

    TRAINING WORKFLOW:
    1. Run on 5-10 repositories with known IP status
    2. Export features + labels to training dataset
    3. Train model: python -m forgetrace.classifiers.train_model
    4. Save model: model.pkl placed in config directory
    5. Deploy: ForgeTrace automatically uses trained model


    # Repository-level vulnerability posture
    repo_vuln_density: float  # Vulnerable packages / total packages
    repo_vuln_weighted_score: float  # Weighted CVSS score across actionable vulns
    repo_osv_noise_ratio: float  # Share of OSV entries filtered out
    repo_vulnerability_count: float  # Actionable vulnerability count
    CONTINUOUS IMPROVEMENT:
    - Each audit with human review adds to training data
    - Periodic retraining (monthly/quarterly) improves accuracy
    - Track model performance metrics (precision, recall, F1)
    """

    def __init__(self, findings: Dict[str, Any], config: Dict[str, Any]):
        """
        Initialize classifier.

        PARAMETERS:
        - findings: Output from all scanners (git, sbom, licenses, similarity)
        - config: User configuration with model paths, thresholds
        """
        self.findings = findings
        self.config = config
        self.model: Optional[RandomForestClassifier] = None
        self.model_loaded = False
        self._vuln_metrics_cache: Optional[Dict[str, float]] = None
        self.feature_names: List[str] = []
        self.log_transformed_features: Sequence[str] = []
        self.removed_features: Set[str] = set()
        self._feature_index: Dict[str, int] = {}

        # Configuration extraction
        ml_config = config.get("ml_classifier", {})
        self.confidence_threshold = ml_config.get("confidence_threshold", 0.7)
        self.model_path = ml_config.get("model_path", "models/ip_classifier.pkl")
        self.model_root = Path(ml_config.get("model_root", "models")).expanduser()
        self.expected_model_hash = (
            ml_config.get("model_sha256", "").strip().lower() or None
        )
        self.enable_ml = ml_config.get("enabled", True) and ML_AVAILABLE
        self.fallback_to_rules = ml_config.get("fallback_to_rules", True)

        if self.enable_ml:
            self._load_model()

    def _load_model(self) -> None:
        """
        Load pre-trained model from disk.

        WHY JOBLIB:
        - Native support in scikit-learn ecosystem
        - Efficient for numpy-heavy payloads
        - Avoids direct pickle usage flagged by Bandit

        SECURITY HARDENING:
        - Restrict model path to configured directory
        - Optional SHA256 verification before loading
        - Consider ONNX/MLflow registry for additional guarantees
        """
        try:
            model_file = self._resolve_model_path(self.model_path)
            if model_file.exists():
                self._verify_model_integrity(model_file)
                bundle = joblib.load(model_file)

                if isinstance(bundle, dict) and "model" in bundle:
                    self.model = bundle["model"]
                    self.feature_names = list(bundle.get("feature_names", []))
                    self.log_transformed_features = tuple(
                        bundle.get("log_transformed_features", [])
                    )
                    self.removed_features = set(bundle.get("removed_features", []))
                else:
                    self.model = bundle
                    self.feature_names = []
                    self.log_transformed_features = ()
                    self.removed_features = set()

                self._feature_index = {
                    name: idx for idx, name in enumerate(self.feature_names)
                }

                self.model_loaded = True
                print(f"✅ ML model loaded from {model_file}")
            else:
                print(f"⚠️  No trained model found at {model_file}")
                print("   Run audit on labeled data to bootstrap training.")
                self.enable_ml = False
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            self.enable_ml = False

    def _resolve_model_path(self, configured_path: str | Path) -> Path:
        """Ensure model file resides within the approved directory tree."""
        candidate = Path(configured_path).expanduser().resolve()
        root = self.model_root.expanduser().resolve()

        if not candidate.is_relative_to(root):
            raise ValueError(
                f"Model path {candidate} is outside of allowed directory {root}"
            )
        return candidate

    def _verify_model_integrity(self, model_file: Path) -> None:
        """Optionally validate the model checksum before loading."""
        if not self.expected_model_hash:
            return

        digest = hashlib.sha256(model_file.read_bytes()).hexdigest()
        if digest != self.expected_model_hash:
            raise ValueError(
                "Model checksum mismatch. Refusing to load untrusted artifact."
            )

    def classify(self) -> Dict[str, Dict[str, Any]]:
        """
        Classify all files in repository.

        WORKFLOW:
        1. Extract features for each file from scanner findings
        2. If ML enabled and model loaded: predict using Random Forest
        3. Else: fallback to rule-based classification
        4. Apply confidence thresholds and flag uncertain results
        5. Return classification dictionary

        RETURN FORMAT:
        {
            "src/main.py": {
                "origin": "foreground",
                "confidence": 0.92,
                "requires_review": False,
                "license": "MIT",
                "primary_author": "john@company.com"
            },
            ...
        }
        """
        if self.enable_ml and self.model_loaded:
            return self._classify_ml()
        elif self.fallback_to_rules:
            print("⚠️  ML unavailable, using rule-based fallback")
            return self._classify_rules()
        else:
            print("❌ ML disabled and fallback disabled")
            return {}

    def _classify_ml(self) -> Dict[str, Dict[str, Any]]:
        """
        ML-based classification using trained Random Forest.

        PROCESS:
        1. Extract features for all files
        2. Batch predict (faster than one-by-one)
        3. Get probability distributions (predict_proba)
        4. Apply confidence thresholding
        5. Flag low-confidence predictions for review
        """
        features_list = self._extract_all_features()

        if not features_list:
            print("⚠️  No files to classify")
            return {}

        if self.model is None:
            print("⚠️  ML model not loaded")
            return {}

        feature_matrix = self._build_feature_matrix(features_list)
        if feature_matrix.size == 0:
            print("⚠️  Feature matrix is empty; skipping ML classification")
            return {}

        predictions = self.model.predict(feature_matrix)
        probabilities = self.model.predict_proba(feature_matrix)
        class_labels = list(getattr(self.model, "classes_", []))
        if not class_labels:
            class_labels = [c.value for c in CodeOrigin if c != CodeOrigin.UNKNOWN]

        classifications = {}

        for i, features in enumerate(features_list):
            predicted_class = predictions[i]
            proba_dist = probabilities[i]

            proba_dict = dict(zip(class_labels, proba_dist.tolist()))

            predicted_label = str(predicted_class)
            confidence = float(proba_dict.get(predicted_label, max(proba_dist)))

            # Determine if human review required
            requires_review = confidence < self.confidence_threshold

            # Map numeric prediction back to CodeOrigin enum
            try:
                origin = CodeOrigin(predicted_label)
            except ValueError:
                origin = CodeOrigin.FOREGROUND

            classifications[features.file_path] = {
                "origin": origin.value,
                "confidence": confidence,
                "requires_review": requires_review,
                "probability_distribution": proba_dict,
                "license": self._get_file_license(features.file_path),
                "primary_author": self._get_primary_author(features.file_path),
                "features": asdict(features),  # Include for debugging/analysis
            }

        # Summary statistics for reporting
        review_count = sum(1 for c in classifications.values() if c["requires_review"])
        print(
            f"📊 ML Classification: {len(classifications)} files, {review_count} require review"
        )

        return classifications

    def _build_feature_matrix(self, features_list: List[FileFeatures]) -> np.ndarray:
        """Construct a feature matrix aligned to the trained model schema."""

        if not features_list:
            columns = len(self.feature_names)
            return np.empty((0, columns), dtype=float)

        if self.feature_names:
            matrix = np.array(
                [feature.to_array(self.feature_names) for feature in features_list],
                dtype=float,
            )
        else:
            matrix = np.array(
                [feature.to_array() for feature in features_list], dtype=float
            )

        return self._apply_inference_transforms(matrix)

    def _apply_inference_transforms(self, matrix: np.ndarray) -> np.ndarray:
        """Mirror training-time feature engineering steps during inference."""

        if not self.feature_names or not self.log_transformed_features:
            return matrix

        transformed = matrix.copy()
        for feature_name in self.log_transformed_features:
            idx = self._feature_index.get(feature_name)
            if idx is None or idx >= transformed.shape[1]:
                continue

            column = transformed[:, idx]
            safe_column = np.clip(column, a_min=0.0, a_max=None)
            transformed[:, idx] = np.log1p(safe_column)

        return transformed

    def _classify_rules(self) -> Dict[str, Dict[str, Any]]:
        """
        Rule-based classification fallback.

        WHY KEEP RULES:
        - Zero-shot capability (works without training data)
        - Transparency (auditors can inspect exact logic)
        - Fallback when ML libraries unavailable
        - Baseline for measuring ML improvement

        RULE LOGIC:
        1. SBOM packages → THIRD_PARTY (high confidence)
        2. Permissive license headers → THIRD_PARTY (medium confidence)
        3. Single author + low churn → BACKGROUND (medium confidence)
        4. Multiple authors + high churn → FOREGROUND (medium confidence)
        5. Otherwise → UNKNOWN (low confidence)

        CAVEAT: Rules miss subtle patterns that ML catches:
        - Background code disguised with many small commits
        - Foreground code with irregular commit patterns
        - Third-party code with modified headers
        """
        classifications = {}

        # Get scanner outputs
        third_party = self._get_third_party_files()
        licensed = self._get_licensed_files()
        # Get all repository files
        repo_files = self._get_all_repo_files()

        for file_path in repo_files:
            fstr = str(file_path)

            # Rule 1: Known third-party from SBOM
            if fstr in third_party:
                classifications[fstr] = {
                    "origin": CodeOrigin.THIRD_PARTY.value,
                    "confidence": 0.95,  # High confidence
                    "requires_review": False,
                    "license": licensed.get(fstr, "unknown"),
                    "primary_author": None,
                    "rule": "sbom_match",
                }
                continue

            # Rule 2: Permissive license headers indicate third-party
            if fstr in licensed:
                lic = licensed[fstr]
                if lic in ["MIT", "Apache-2.0", "BSD-3-Clause", "ISC"]:
                    classifications[fstr] = {
                        "origin": CodeOrigin.THIRD_PARTY.value,
                        "confidence": 0.75,  # Medium confidence
                        "requires_review": True,
                        "license": lic,
                        "primary_author": None,
                        "rule": "permissive_license",
                    }
                    continue

            # Rule 3-4: Use git history to distinguish background/foreground
            primary_author = self._get_primary_author(fstr)
            author_count = len(self._get_file_authors(fstr))
            commit_count = len(self._get_file_commits(fstr))

            # Single author + few commits = likely background IP
            if author_count == 1 and commit_count < 5:
                classifications[fstr] = {
                    "origin": CodeOrigin.BACKGROUND.value,
                    "confidence": 0.60,
                    "requires_review": True,
                    "license": licensed.get(fstr, "none"),
                    "primary_author": primary_author,
                    "rule": "single_author_low_churn",
                }
            # Multiple authors + active development = foreground
            elif author_count >= 2 and commit_count >= 5:
                classifications[fstr] = {
                    "origin": CodeOrigin.FOREGROUND.value,
                    "confidence": 0.70,
                    "requires_review": True,
                    "license": licensed.get(fstr, "none"),
                    "primary_author": primary_author,
                    "rule": "multi_author_active",
                }
            # Insufficient data
            else:
                classifications[fstr] = {
                    "origin": CodeOrigin.UNKNOWN.value,
                    "confidence": 0.30,
                    "requires_review": True,
                    "license": licensed.get(fstr, "none"),
                    "primary_author": primary_author,
                    "rule": "insufficient_data",
                }

        return classifications

    def _extract_all_features(self) -> List[FileFeatures]:
        """
        Extract features for all files in repository.

        FEATURE EXTRACTION CHALLENGES:
        - Missing data: Not all files have git history (newly added)
        - Performance: Avoid re-parsing files multiple times
        - Scalability: Large repos (100k+ files) need batching

        SOLUTION:
        - Cache scanner outputs in memory
        - Use default values for missing features (0, False, etc.)
        - Extract features in parallel for large repos (future optimization)
        """
        features_list = []
        repo_files = self._get_all_repo_files()

        for file_path in repo_files:
            try:
                features = self._extract_features(file_path)
                features_list.append(features)
            except Exception as e:
                # Don't fail entire classification if one file errors
                print(f"⚠️  Error extracting features for {file_path}: {e}")
                continue

        return features_list

    def _extract_features(self, file_path: Path) -> FileFeatures:
        """
        Extract features for a single file.

        FEATURE ENGINEERING DETAILS:

        1. FILE METADATA:
        - lines_of_code: Larger files often third-party libraries
        - path_depth: vendor/node_modules/third_party usually deep
        - extension: .min.js, .bundle.js indicate third-party

        2. GIT HISTORY:
        - commit_count: Third-party rarely modified after import
        - author_count: Background IP typically single author
        - commit_frequency: Low frequency suggests imported code

        3. CODE COMPLEXITY:
        - cyclomatic_complexity: High = sophisticated library code
        - maintainability_index: Low = possibly rushed background code

        4. LICENSE INDICATORS:
        - has_license_header: Third-party usually includes copyright
        - Keywords: "Copyright", "Licensed under", "SPDX-License-Identifier"

        5. IMPORT ANALYSIS:
        - stdlib_import_ratio: High = likely original code
        - third_party_import_ratio: High = uses many dependencies

        6. SIMILARITY:
        - max_similarity_score: Match to known third-party code
        - similar_file_count: Duplicated files suggest copy-paste
        """
        fstr = str(file_path)

        try:
            file_size = file_path.stat().st_size
        except OSError:
            file_size = 0

        try:
            text = file_path.read_text(errors="ignore")
        except Exception:
            text = ""

        lines = text.splitlines()
        lines_of_code = len(lines)

        extension = file_path.suffix
        path_depth = len(file_path.parts)

        # Git history extraction
        file_commits = self._get_file_commits(fstr)
        file_authors = self._get_file_authors(fstr)
        commit_count = len(file_commits)
        author_count = len(file_authors)

        # Calculate days since first/last commit
        if file_commits:
            # Assumes commits have 'date' field (unix timestamp)
            first_commit_date = min(c.get("date", 0) for c in file_commits)
            last_commit_date = max(c.get("date", 0) for c in file_commits)
            days_since_first = (
                self._get_current_timestamp() - first_commit_date
            ) // 86400
            days_since_last = (
                self._get_current_timestamp() - last_commit_date
            ) // 86400
            commit_frequency = commit_count / max(days_since_first, 1)
        else:
            days_since_first = 0
            days_since_last = 0
            commit_frequency = 0.0

        # Code complexity extraction (using radon if available)
        complexity_data = self._get_complexity_metrics(file_path)

        # License indicators
        has_license_header = self._has_license_header(file_path)
        has_third_party_indicators = self._has_third_party_keywords(file_path)

        extra_features, import_stats = self._collect_runtime_extra_features(
            file_path, text, lines
        )

        # Similarity features
        similarity_data = self._get_similarity_data(fstr)

        # Authorship patterns
        primary_author = self._get_primary_author(fstr)
        if file_authors:
            author_commits = Counter(c.get("author") for c in file_commits)
            primary_author_commits = (
                author_commits.most_common(1)[0][1] if author_commits else 0
            )
            primary_author_commit_ratio = primary_author_commits / max(commit_count, 1)
        else:
            primary_author_commit_ratio = 0.0

        is_primary_author_external = self._is_external_author(primary_author)

        vuln_metrics = self._repo_vulnerability_metrics()

        return FileFeatures(
            file_path=fstr,
            lines_of_code=lines_of_code,
            file_size_bytes=file_size,
            extension=extension,
            path_depth=path_depth,
            commit_count=commit_count,
            author_count=author_count,
            days_since_first_commit=days_since_first,
            days_since_last_commit=days_since_last,
            commit_frequency=commit_frequency,
            cyclomatic_complexity=complexity_data["cyclomatic"],
            maintainability_index=complexity_data["maintainability"],
            has_license_header=has_license_header,
            has_third_party_indicators=has_third_party_indicators,
            import_count=int(import_stats["total"]),
            stdlib_import_ratio=import_stats["stdlib_ratio"],
            third_party_import_ratio=import_stats["third_party_ratio"],
            max_similarity_score=similarity_data["max_score"],
            similar_file_count=similarity_data["similar_count"],
            primary_author_commit_ratio=primary_author_commit_ratio,
            is_primary_author_external=is_primary_author_external,
            repo_vuln_density=vuln_metrics["repo_vuln_density"],
            repo_vuln_weighted_score=vuln_metrics["repo_vuln_weighted_score"],
            repo_osv_noise_ratio=vuln_metrics["repo_osv_noise_ratio"],
            repo_vulnerability_count=vuln_metrics["repo_vulnerability_count"],
            extra_features=extra_features,
        )

    def _collect_runtime_extra_features(
        self,
        file_path: Path,
        text: str,
        lines: Sequence[str],
    ) -> Tuple[Dict[str, float], Dict[str, float]]:
        lower_path = [segment.lower() for segment in file_path.parts]
        name_lower = file_path.name.lower()
        suffix_lower = file_path.suffix.lower()
        lower_text = text.lower()
        loc = len(lines)
        word_count = sum(len(line.split()) for line in lines)

        avg_line_length = float(word_count / loc) if loc else 0.0
        comment_ratio = self._estimate_comment_ratio(lines)

        features: Dict[str, float] = {
            "avg_line_length": avg_line_length,
            "comment_ratio": comment_ratio,
        }

        # Foundational heuristics
        features["is_test_path"] = (
            1.0 if self._is_test_path(lower_path, name_lower) else 0.0
        )
        features["is_docs_path"] = (
            1.0 if self._is_docs_path(lower_path, suffix_lower) else 0.0
        )

        header_text = "\n".join(lines[:40])
        has_spdx = 1.0 if SPDX_REGEX.search(header_text) else 0.0
        features["has_spdx_header"] = has_spdx
        features["spdx_header_present"] = has_spdx

        manifest_indicator = 1.0 if name_lower in MANIFEST_FILENAMES else 0.0
        features["manifest_indicator"] = manifest_indicator

        sbom_indicator = (
            1.0 if ("sbom" in name_lower or name_lower.endswith("bom.json")) else 0.0
        )
        features["sbom_indicator"] = sbom_indicator

        config_indicator = 0.0
        if suffix_lower in CONFIG_SUFFIXES or name_lower in {".env", ".env.example"}:
            config_indicator = 1.0
        elif name_lower in ENTERPRISE_CONFIG_FILES:
            config_indicator = 1.0
        elif any(
            segment in {"config", "configs", "settings", "env"}
            for segment in lower_path
        ):
            config_indicator = 1.0
        features["config_indicator"] = config_indicator

        vendor_indicator = (
            1.0
            if any(
                segment in ENTERPRISE_VENDOR_DIRS or segment in THIRD_PARTY_DIRS
                for segment in lower_path
            )
            else 0.0
        )
        features["vendor_path_indicator"] = vendor_indicator

        module_hits = sum(
            1 for segment in lower_path if segment in ENTERPRISE_MODULE_DIRS
        )
        features["module_depth_score"] = module_hits / max(len(lower_path), 1)

        template_indicator = (
            1.0
            if (
                suffix_lower in TEMPLATE_SUFFIXES
                or any(segment in {"templates", "views"} for segment in lower_path)
            )
            else 0.0
        )
        features["template_indicator"] = template_indicator

        # Enterprise language signals
        framework_hits = sum(
            lower_text.count(keyword.lower()) for keyword in FRAMEWORK_KEYWORDS
        )
        features["framework_keyword_hits"] = float(framework_hits)
        framework_variety = sum(
            1 for keyword in FRAMEWORK_KEYWORDS if keyword.lower() in lower_text
        )
        features["framework_keyword_variety"] = float(framework_variety)

        business_hits = sum(lower_text.count(term) for term in BUSINESS_TERMS)
        features["business_context_density"] = business_hits / max(loc, 1)

        api_endpoint_count = sum(
            len(pattern.findall(text)) for pattern in API_ENDPOINT_PATTERNS
        )
        features["api_endpoint_count"] = float(api_endpoint_count)

        plugin_hits = sum(len(pattern.findall(text)) for pattern in PLUGIN_PATTERNS)
        features["plugin_registration_hits"] = float(plugin_hits)

        async_indicator = (
            1.0
            if any(keyword.lower() in lower_text for keyword in ASYNC_KEYWORDS)
            else 0.0
        )
        features["async_processing_indicator"] = async_indicator

        data_access_indicator = (
            1.0
            if any(keyword.lower() in lower_text for keyword in DATA_ACCESS_KEYWORDS)
            else 0.0
        )
        features["data_access_indicator"] = data_access_indicator

        orchestration_hits = sum(
            lower_text.count(keyword) for keyword in ORCHESTRATION_KEYWORDS
        )
        features["orchestration_signal"] = 1.0 if orchestration_hits > 0 else 0.0
        features["orchestration_keyword_hits"] = float(orchestration_hits)
        features["orchestration_path_indicator"] = (
            1.0
            if any(
                segment
                in {
                    "pipeline",
                    "pipelines",
                    "workflow",
                    "workflows",
                    "airflow",
                    "dags",
                    "dag",
                }
                for segment in lower_path
            )
            else 0.0
        )

        # Security + licensing signals
        license_hits = sum(1 for keyword in LICENSE_KEYWORDS if keyword in lower_text)
        features["license_keyword_hits"] = float(license_hits)

        secret_hits, sensitive_assignments = self._secret_signals(text)
        features["secret_pattern_hits"] = float(secret_hits)
        features["sensitive_assignment_hits"] = float(sensitive_assignments)

        private_key_indicator = 1.0 if PRIVATE_KEY_REGEX.search(text) else 0.0
        features["private_key_indicator"] = private_key_indicator

        credential_density = self._credential_keyword_density(text)
        features["credential_keyword_density"] = credential_density

        entropy_ratio = self._high_entropy_literal_ratio(text)
        features["high_entropy_literal_ratio"] = entropy_ratio

        features["url_reference_count"] = float(len(URL_REGEX.findall(text)))

        secret_risk = self._secret_risk_score(
            secret_hits, private_key_indicator, entropy_ratio, sensitive_assignments
        )
        features["secret_risk_score"] = secret_risk

        # Research signals
        permissive_indicator = (
            1.0 if any(token in lower_text for token in LICENSE_PERMISSIVE) else 0.0
        )
        features["permissive_license_indicator"] = permissive_indicator

        abstract_window = lower_text[:800]
        features["abstract_indicator"] = (
            1.0
            if ("abstract" in abstract_window or "summary" in abstract_window)
            else 0.0
        )

        methodology_indicator = (
            1.0
            if any(
                phrase in lower_text
                for phrase in (
                    "methodology",
                    "proposed method",
                    "our method",
                    "methods",
                    "approach",
                    "experimental setup",
                )
            )
            else 0.0
        )
        features["methodology_indicator"] = methodology_indicator

        citation_count = len(CITATION_REGEX.findall(text))
        features["citation_count"] = float(citation_count)

        paper_hits = len(PAPER_REFERENCE_REGEX.findall(text))
        features["paper_reference_hits"] = float(paper_hits)

        dataset_mentions = sum(
            lower_text.count(keyword) for keyword in DATASET_KEYWORDS
        )
        features["dataset_mentions"] = float(dataset_mentions)

        framework_mentions = sum(
            lower_text.count(keyword) for keyword in ML_FRAMEWORK_KEYWORDS
        )
        features["framework_mentions"] = float(framework_mentions)

        metric_mentions = sum(lower_text.count(keyword) for keyword in METRIC_KEYWORDS)
        features["metric_mentions"] = float(metric_mentions)

        figure_mentions = sum(lower_text.count(keyword) for keyword in FIGURE_KEYWORDS)
        figure_mentions += len(re.findall(r"figure\s+[0-9]+", lower_text))
        features["figure_mentions"] = float(figure_mentions)

        features["notebook_indicator"] = (
            1.0 if suffix_lower in NOTEBOOK_SUFFIXES else 0.0
        )

        experiment_config_indicator = (
            1.0
            if (
                name_lower in EXPERIMENT_CONFIG_NAMES
                or "config" in name_lower
                or "hparam" in name_lower
            )
            else 0.0
        )
        features["experiment_config_indicator"] = experiment_config_indicator

        experiment_path_indicator = (
            1.0
            if any(
                segment in EXPERIMENT_DIR_KEYWORDS
                or "experiment" in segment
                or "trial" in segment
                for segment in lower_path
            )
            else 0.0
        )
        features["experiment_path_indicator"] = experiment_path_indicator

        features["sample_entropy"] = _safe_entropy(text[:5000])
        features["code_to_text_ratio"] = self._code_to_text_ratio(text)

        # Polyglot signals (language-aware imports + complexity proxies)
        polyglot_features, import_metrics = self._polyglot_runtime_features(
            file_path, text, lines
        )
        features.update(polyglot_features)

        return features, import_metrics

    def _estimate_comment_ratio(self, lines: Sequence[str]) -> float:
        if not lines:
            return 0.0
        comment_markers = ("#", "//", "/*", "*", "--")
        comment_lines = sum(
            1 for line in lines if line.strip().startswith(comment_markers)
        )
        return comment_lines / len(lines)

    def _is_test_path(self, path_segments: Sequence[str], filename: str) -> bool:
        if any("test" in segment for segment in path_segments):
            return True
        if filename.startswith("test"):
            return True
        stem = filename.split(".", 1)[0]
        return stem.endswith("_test") or stem.endswith("_spec")

    def _is_docs_path(self, path_segments: Sequence[str], suffix: str) -> bool:
        doc_suffixes = {".md", ".rst", ".adoc", ".txt", ".pdf"}
        if suffix in doc_suffixes:
            return True
        doc_segments = {"docs", "doc", "documentation", "guides", "manual"}
        return any(
            segment in doc_segments or "docs" in segment for segment in path_segments
        )

    def _secret_signals(self, text: str) -> Tuple[int, int]:
        secret_hits = sum(len(pattern.findall(text)) for pattern in SECRET_PATTERNS)
        assignment_pattern = re.compile(
            r"(?i)(password|secret|token|apikey|api_key)\s*[:=]\s*[\"']?[^\s\"']{6,}"
        )
        sensitive_assignments = len(assignment_pattern.findall(text))
        return secret_hits, sensitive_assignments

    def _credential_keyword_density(self, text: str) -> float:
        if not text:
            return 0.0
        words = text.lower().split()
        if not words:
            return 0.0
        matches = sum(
            1
            for word in words
            if any(keyword in word for keyword in CREDENTIAL_KEYWORDS)
        )
        return matches / max(len(text.splitlines()), 1)

    def _high_entropy_literal_ratio(self, text: str) -> float:
        literals = re.findall(r"[\"']([A-Za-z0-9/_\-+=]{8,})[\"']", text)
        if not literals:
            return 0.0
        high_entropy = sum(
            1
            for literal in literals
            if self._shannon_entropy(literal) >= HIGH_ENTROPY_THRESHOLD
        )
        return high_entropy / len(literals)

    def _secret_risk_score(
        self,
        secret_hits: int,
        private_key_indicator: float,
        entropy_ratio: float,
        sensitive_assignments: int,
    ) -> float:
        score = (
            secret_hits * 0.25
            + sensitive_assignments * 0.2
            + entropy_ratio * 0.8
            + private_key_indicator * 1.0
        )
        return float(min(1.0, score))

    def _code_to_text_ratio(self, text: str) -> float:
        if not text:
            return 0.0
        code_lines = 0
        prose_lines = 0
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith(("#", "//", "/*", "*")):
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

    def _polyglot_runtime_features(
        self,
        file_path: Path,
        text: str,
        lines: Sequence[str],
    ) -> Tuple[Dict[str, float], Dict[str, float]]:
        language = self._detect_language(file_path)
        entropy = self._token_entropy(text)
        nesting = self._nesting_depth(language, text)

        if language is not None:
            import_metrics = self._import_metrics_for_language(language, lines)
        else:
            fallback = self._analyze_imports(file_path)
            import_metrics = {
                "total": float(fallback.get("total", 0.0)),
                "stdlib_ratio": float(fallback.get("stdlib_ratio", 0.0)),
                "third_party_ratio": float(fallback.get("third_party_ratio", 0.0)),
                "external_ratio": float(fallback.get("third_party_ratio", 0.0)),
            }

        if "third_party_ratio" not in import_metrics:
            import_metrics["third_party_ratio"] = float(
                import_metrics.get("external_ratio", 0.0)
            )
        if "external_ratio" not in import_metrics:
            import_metrics["external_ratio"] = float(
                import_metrics.get("third_party_ratio", 0.0)
            )
        if "stdlib_ratio" not in import_metrics:
            import_metrics["stdlib_ratio"] = 0.0
        if "total" not in import_metrics:
            import_metrics["total"] = 0.0

        features = {
            "language_entropy": entropy,
            "nesting_depth": nesting,
            "external_import_ratio": import_metrics.get("external_ratio", 0.0),
        }
        return features, import_metrics

    def _detect_language(self, file_path: Path) -> Optional[str]:
        suffix = file_path.suffix.lower()
        for language, extensions in LANGUAGE_EXTENSIONS.items():
            if suffix in extensions:
                return language
        return None

    def _import_metrics_for_language(
        self, language: str, lines: Sequence[str]
    ) -> Dict[str, float]:
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
                if root and not self._matches_any(root, external_hints):
                    stdlib += 1
                else:
                    third_party += 1

        if total == 0:
            return {
                "total": 0.0,
                "stdlib_ratio": 0.0,
                "external_ratio": 0.0,
                "third_party_ratio": 0.0,
            }

        stdlib_ratio = stdlib / total
        external_ratio = third_party / total
        return {
            "total": float(total),
            "stdlib_ratio": float(stdlib_ratio),
            "external_ratio": float(external_ratio),
            "third_party_ratio": float(external_ratio),
        }

    def _extract_import_target(self, language: str, line: str) -> Optional[str]:
        if language == "python":
            if line.startswith("import "):
                return line[len("import ") :].split(" as ")[0].strip()
            if line.startswith("from "):
                remainder = line[len("from ") :]
                return remainder.split(" import ")[0].strip()
        elif language in {"javascript", "typescript"}:
            match = re.search(r"from\s+['\"]([^'\"]+)", line)
            if match:
                return match.group(1)
            if line.startswith("require("):
                inner = line.split("require(", 1)[1]
                return inner.strip("')\"")
        elif language == "java":
            if line.startswith("import "):
                return line[len("import ") :].rstrip(";")
        elif language == "go":
            if line.startswith("import "):
                token = line[len("import ") :].strip()
                return token.strip('"')
        elif language == "rust":
            if line.startswith("use "):
                return line[len("use ") :].rstrip(";")
        elif language == "cpp" or language == "c":
            match = re.search(r"#include\s*[<\"]([^>\"]+)[>\"]", line)
            if match:
                token = match.group(1)
                return f"<{token}>" if line.strip().startswith("#include <") else token
        elif language == "php":
            if line.startswith("use "):
                return line[len("use ") :].rstrip(";")
        elif language == "scala":
            if line.startswith("import "):
                return line[len("import ") :].strip()
        return None

    def _matches_any(self, target: str, hints: Iterable[str]) -> bool:
        return any(target.startswith(hint) for hint in hints)

    def _token_entropy(self, text: str) -> float:
        tokens = re.findall(r"[A-Za-z_]+", text)
        if not tokens:
            return 0.0
        counts = Counter(tokens)
        total = sum(counts.values())
        return float(
            -sum(
                (count / total) * math.log(count / total, 2)
                for count in counts.values()
            )
        )

    def _nesting_depth(self, language: Optional[str], text: str) -> float:
        if language == "python":
            indent_levels = [
                len(line) - len(line.lstrip(" "))
                for line in text.splitlines()
                if line.strip()
            ]
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
            elif char in "]}":
                depth = max(depth - 1, 0)
        return float(max_depth)

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

    # ============================================================================
    # HELPER METHODS - Data extraction from scanner findings
    # ============================================================================

    def _get_third_party_files(self) -> set:
        """Extract third-party files from SBOM scanner."""
        third_party = set()
        for pkg in self.findings.get("sbom", {}).get("packages", []):
            if "file" in pkg:
                third_party.add(pkg["file"])
        return third_party

    def _get_licensed_files(self) -> Dict[str, str]:
        """Extract licensed files from license scanner."""
        licensed = {}
        for lic in self.findings.get("licenses", {}).get("findings", []):
            if lic.get("license"):
                licensed[lic["file"]] = lic["license"]
        return licensed

    def _get_all_repo_files(self) -> List[Path]:
        """
        Get all relevant files in repository.

        FILTERING LOGIC:
        - Include: source code files (.py, .js, .java, .go, etc.)
        - Exclude: binary files, images, generated code
        - Exclude: Common third-party directories (node_modules, vendor, .git)

        WHY: Focus classification on human-written code, not assets/dependencies
        """
        # In production, walk repository directory
        # For now, extract from scanner outputs
        files = set()

        # From git scanner
        git_data = self.findings.get("git", {})
        files.update(git_data.get("files", []))

        # From license scanner
        for lic in self.findings.get("licenses", {}).get("findings", []):
            files.add(lic.get("file", ""))

        # From SBOM
        for pkg in self.findings.get("sbom", {}).get("packages", []):
            if "file" in pkg:
                files.add(pkg["file"])

        # Convert to Path objects and filter
        return [Path(f) for f in files if f and self._is_source_file(f)]

    def _is_source_file(self, file_path: str) -> bool:
        """Check if file is source code (not binary, image, etc.)."""
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

        p = Path(file_path)

        # Check extension
        if p.suffix not in source_extensions:
            return False

        # Exclude common third-party directories
        exclude_dirs = {
            "node_modules",
            "vendor",
            ".git",
            "build",
            "dist",
            "__pycache__",
        }
        if any(part in exclude_dirs for part in p.parts):
            return False

        return True

    def _get_file_commits(self, file_path: str) -> List[Dict]:
        """Get all commits that modified this file."""
        # Placeholder - would use git log --follow
        churn = self.findings.get("git", {}).get("churn", {})
        return churn.get(file_path, {}).get("commits", [])

    def _get_file_authors(self, file_path: str) -> List[str]:
        """Get all authors who modified this file."""
        commits = self._get_file_commits(file_path)
        return list(set(c.get("author", "unknown") for c in commits))

    def _get_primary_author(self, file_path: str) -> str:
        """Get primary author (most commits) for this file."""
        authors = self._get_file_authors(file_path)
        if not authors:
            return "unknown"

        commits = self._get_file_commits(file_path)
        author_counts = Counter(c.get("author", "unknown") for c in commits)

        if author_counts:
            return author_counts.most_common(1)[0][0]
        return authors[0]

    def _get_file_license(self, file_path: str) -> str:
        """Get license for this file."""
        licensed = self._get_licensed_files()
        return licensed.get(file_path, "none")

    def _get_complexity_metrics(self, file_path: Path) -> Dict[str, float]:
        """
        Calculate code complexity metrics.

        METRICS:
        - Cyclomatic Complexity: Number of independent paths through code
          * 1-10: Simple, easy to understand
          * 11-20: Moderate complexity
          * 21+: High complexity, hard to maintain

        - Maintainability Index: 0-100 score based on LOC, complexity, volume
          * 20+: Highly maintainable
          * 10-19: Needs improvement
          * <10: Difficult to maintain

        WHY THESE METRICS:
        - High complexity often indicates sophisticated library code
        - Low maintainability suggests rushed/copy-pasted background code

        LIBRARY: radon (optional dependency)
        If unavailable, return default values (no impact on rule-based classification)
        """
        # isort: off
        try:
            from radon.complexity import (  # type: ignore[import-not-found]
                cc_visit,
            )
            from radon.metrics import (  # type: ignore[import-not-found]
                mi_visit,
            )

            # isort: on

            code = file_path.read_text(errors="ignore")

            # Cyclomatic complexity (average across all functions)
            cc_results = cc_visit(code)
            if cc_results:
                avg_complexity = sum(r.complexity for r in cc_results) / len(cc_results)
            else:
                avg_complexity = 1.0

            # Maintainability index
            mi_score = mi_visit(code, multi=True)
            avg_mi = sum(mi_score.values()) / len(mi_score) if mi_score else 50.0

            return {"cyclomatic": avg_complexity, "maintainability": avg_mi}
        except (ImportError, OSError):
            # Radon not available or file not parseable
            return {"cyclomatic": 1.0, "maintainability": 50.0}

    def _has_license_header(self, file_path: Path) -> bool:
        """Check if file has license/copyright header in first 20 lines."""
        try:
            lines = file_path.read_text(errors="ignore").splitlines()[:20]
            header_text = "\n".join(lines).lower()

            keywords = [
                "copyright",
                "license",
                "spdx-license-identifier",
                "licensed under",
            ]
            return any(kw in header_text for kw in keywords)
        except OSError:
            return False

    def _has_third_party_keywords(self, file_path: Path) -> bool:
        """Check for common third-party indicators in file."""
        try:
            lines = file_path.read_text(errors="ignore").splitlines()[:30]
            header_text = "\n".join(lines).lower()

            # Common patterns in third-party code
            patterns = [
                "all rights reserved",
                "redistribution and use",
                "this library is free software",
                "apache license",
                "mit license",
                "permission is hereby granted",
            ]
            return any(p in header_text for p in patterns)
        except OSError:
            return False

    def _analyze_imports(self, file_path: Path) -> Dict[str, Any]:
        """
        Analyze import statements to detect stdlib vs third-party usage.

        RATIONALE:
        - Original code tends to use more stdlib (os, sys, re, json)
        - Third-party code imports other third-party packages
        - Background code may have unusual import patterns

        LIMITATIONS:
        - Language-specific parsing required
        - Only supports Python in this MVP
        - Future: Add JS (require/import), Java (import), Go (import)
        """
        try:
            code = file_path.read_text(errors="ignore")

            # Simple regex-based extraction (MVP approach)
            # Production would use AST parsing (ast.parse in Python)
            import re

            import_lines = [
                line_text
                for line_text in code.splitlines()
                if line_text.strip().startswith(("import ", "from "))
            ]

            total_imports = len(import_lines)
            if total_imports == 0:
                return {"total": 0, "stdlib_ratio": 0.5, "third_party_ratio": 0.5}

            # Python stdlib modules (partial list)
            stdlib_modules = {
                "os",
                "sys",
                "re",
                "json",
                "time",
                "datetime",
                "pathlib",
                "collections",
                "itertools",
                "functools",
                "typing",
                "enum",
                "logging",
                "argparse",
                "subprocess",
                "urllib",
                "http",
            }

            stdlib_count = 0
            for line in import_lines:
                # Extract module name (first part before '.')
                match = re.search(r"(?:from|import)\s+(\w+)", line)
                if match:
                    module = match.group(1)
                    if module in stdlib_modules:
                        stdlib_count += 1

            stdlib_ratio = stdlib_count / total_imports
            third_party_ratio = 1.0 - stdlib_ratio

            return {
                "total": total_imports,
                "stdlib_ratio": stdlib_ratio,
                "third_party_ratio": third_party_ratio,
            }
        except OSError:
            return {"total": 0, "stdlib_ratio": 0.5, "third_party_ratio": 0.5}

    def _get_similarity_data(self, file_path: str) -> Dict[str, Any]:
        """Extract similarity metrics from similarity scanner."""
        similarity_findings = self.findings.get("similarity", {}).get("findings", [])

        # Find this file in similarity results
        for finding in similarity_findings:
            if finding.get("file") == file_path:
                return {
                    "max_score": finding.get("max_similarity", 0.0),
                    "similar_count": len(finding.get("similar_files", [])),
                }

        return {"max_score": 0.0, "similar_count": 0}

    def _is_external_author(self, author_email: str) -> bool:
        """
        Check if author is external (not company email).

        WHY:
        External emails (gmail, yahoo, personal domains) suggest:
        - Contractor work (background IP risk)
        - Open source contributors (foreground if contributing to your repo)
        - Personal side projects (background IP if brought into company project)

        Company emails (jdoe@company.com) suggest:
        - Employee work (foreground IP, owned by company)
        - Proper work-for-hire agreements

        CAVEAT: Email alone insufficient - contractor may use company email
        """
        if not author_email or "@" not in author_email:
            return True  # Unknown = treat as external (conservative)

        company_domains = self.config.get("ml_classifier", {}).get(
            "company_domains", []
        )

        domain = author_email.split("@")[1].lower()

        # Check if company domain
        if any(domain.endswith(cd) for cd in company_domains):
            return False

        # Common personal email providers
        personal_providers = {
            "gmail.com",
            "yahoo.com",
            "hotmail.com",
            "outlook.com",
            "icloud.com",
            "protonmail.com",
            "mail.com",
        }

        return domain in personal_providers or len(company_domains) == 0

    def _get_current_timestamp(self) -> int:
        """Get current Unix timestamp."""
        import time

        return int(time.time())

    def _repo_vulnerability_metrics(self) -> Dict[str, float]:
        if self._vuln_metrics_cache is not None:
            return self._vuln_metrics_cache

        data = self.findings.get("vulnerabilities", {})
        metrics = {
            "repo_vuln_density": 0.0,
            "repo_vuln_weighted_score": 0.0,
            "repo_osv_noise_ratio": 0.0,
            "repo_vulnerability_count": 0.0,
        }

        if isinstance(data, dict):
            metrics = {
                "repo_vuln_density": float(
                    data.get("normalized_vuln_density", 0.0) or 0.0
                ),
                "repo_vuln_weighted_score": float(
                    data.get("weighted_vuln_score", 0.0) or 0.0
                ),
                "repo_osv_noise_ratio": float(data.get("osv_noise_ratio", 0.0) or 0.0),
                "repo_vulnerability_count": float(
                    data.get("total_vulnerabilities", 0.0) or 0.0
                ),
            }

        self._vuln_metrics_cache = metrics
        return metrics

    # ============================================================================
    # TRAINING AND MODEL MANAGEMENT
    # ============================================================================

    def export_training_data(self, output_path: str = "training_data.jsonl") -> None:
        """
        Export features and classifications for model training.

        WHY JSONL (JSON Lines):
        - Each line is a complete JSON object (one training example)
        - Easy to append new examples without reparsing entire file
        - Standard format for ML training data
        - Can process in streaming fashion (memory efficient)

        WORKFLOW:
        1. Run audit on multiple repositories
        2. Human reviews and corrects classifications
        3. Export corrected labels as training data
        4. Train model: python -m forgetrace.classifiers.train_model training_data.jsonl

        FORMAT:
        {"features": {...}, "label": "foreground", "file_path": "src/main.py"}
        {"features": {...}, "label": "third_party", "file_path": "vendor/lib.js"}
        ...
        """
        features_list = self._extract_all_features()
        classifications = self._classify_rules()  # Use rules as initial labels

        with open(output_path, "w") as f:
            for features in features_list:
                if features.file_path in classifications:
                    classification = classifications[features.file_path]

                    training_example = {
                        "features": asdict(features),
                        "label": classification["origin"],
                        "file_path": features.file_path,
                        "confidence": classification.get("confidence", 0.0),
                    }

                    f.write(json.dumps(training_example) + "\n")

        print(f"✅ Exported {len(features_list)} training examples to {output_path}")
        print("   Next steps:")
        print("   1. Review and correct labels in training_data.jsonl")
        print(
            "   2. Train model: python -m forgetrace.classifiers.train_model training_data.jsonl"
        )

    def get_feature_importance(self) -> Dict[str, float]:
        """
        Get feature importance scores from trained model.

        WHY IMPORTANT:
        - Shows which features most influence predictions
        - Helps debug misclassifications
        - Guides feature engineering (add similar high-value features)
        - Provides explainability for auditors

        INTERPRETATION:
        - Score 0.0-1.0, higher = more important
        - Scores sum to 1.0 across all features
        - Typical distribution: 2-3 dominant features, rest contribute marginally

        EXAMPLE OUTPUT:
        {
            "commit_count": 0.18,
            "author_count": 0.15,
            "cyclomatic_complexity": 0.12,
            "has_license_header": 0.10,
            ...
        }
        """
        if not self.model_loaded or self.model is None:
            return {}

        # Random Forest provides feature_importances_ attribute
        importances = self.model.feature_importances_

        # Map to feature names
        feature_names = [
            "lines_of_code",
            "file_size_bytes",
            "path_depth",
            "commit_count",
            "author_count",
            "days_since_first_commit",
            "days_since_last_commit",
            "commit_frequency",
            "cyclomatic_complexity",
            "maintainability_index",
            "has_license_header",
            "has_third_party_indicators",
            "import_count",
            "stdlib_import_ratio",
            "third_party_import_ratio",
            "max_similarity_score",
            "similar_file_count",
            "primary_author_commit_ratio",
            "is_primary_author_external",
            "repo_vuln_density",
            "repo_vuln_weighted_score",
            "repo_osv_noise_ratio",
            "repo_vulnerability_count",
        ]

        return dict(zip(feature_names, importances.tolist()))


# ============================================================================
# CONVENIENCE FUNCTIONS FOR BACKWARD COMPATIBILITY
# ============================================================================


class IPClassifier:
    """
    Wrapper for backward compatibility with existing audit.py code.

    WHY KEEP THIS:
    - Minimizes changes to audit.py
    - Same interface as old rule-based classifier
    - Gradual migration path

    DEPRECATION PLAN:
    - Phase 1: Dual operation (ML + rules fallback)
    - Phase 2: ML primary, rules only for comparison
    - Phase 3: Remove rules entirely (6-12 months after Phase 1)
    """

    def __init__(self, findings: Dict[str, Any], config: Dict[str, Any]):
        self.ml_classifier = MLIPClassifier(findings, config)
        self.findings = findings
        self.config = config

    def classify(self) -> Dict[str, Dict[str, Any]]:
        """Run classification (ML or rule-based fallback)."""
        return self.ml_classifier.classify()

    def score_rewriteability(self) -> Dict[str, Dict[str, Any]]:
        """
        Score rewriteability of each file.

        KEPT FROM ORIGINAL: This method uses different logic than ML classification.
        Could be enhanced with ML in future, but rules-based approach works well.
        """
        classifications = self.findings.get("classification", {})
        scores = {}

        for filepath, data in classifications.items():
            if data["origin"] == "third_party":
                scores[filepath] = {"score": 0, "reason": "Third-party package"}
                continue

            p = Path(filepath)
            if not p.exists():
                continue

            try:
                loc = len(p.read_text(errors="ignore").splitlines())
            except OSError:
                loc = 0

            complexity = min(loc / 500, 1.0)
            coupling = self._estimate_coupling(filepath)
            test_coverage = 0.5  # Placeholder for future enhancement

            score = (1 - complexity) * 0.4 + (1 - coupling) * 0.4 + test_coverage * 0.2

            scores[filepath] = {
                "score": round(score, 2),
                "complexity": round(complexity, 2),
                "coupling": round(coupling, 2),
                "loc": loc,
                "rewriteable": score > 0.6,
            }

        return scores

    def estimate_cost(self) -> Dict[str, Any]:
        """
        Estimate replacement cost for foreground code.

        KEPT FROM ORIGINAL: Industry-standard cost estimation formula.
        Based on COCOMO model (COnstructive COst MOdel).
        """
        classifications = self.findings.get("classification", {})
        rewriteability = self.findings.get("rewriteability", {})

        total_loc = 0
        foreground_loc = 0

        for filepath, data in classifications.items():
            if data["origin"] == "foreground":
                loc = rewriteability.get(filepath, {}).get("loc", 0)
                foreground_loc += loc
            total_loc += rewriteability.get(filepath, {}).get("loc", 0)

        cost_cfg = self.config.get("cost", {})
        days_per_kloc = cost_cfg.get("days_per_kloc", 15)
        hours_per_day = cost_cfg.get("hours_per_day", 8)
        rate = cost_cfg.get("hourly_rate", 150)
        multiplier = cost_cfg.get("complexity_multiplier", 1.5)

        kloc = foreground_loc / 1000
        days = kloc * days_per_kloc * multiplier
        hours = days * hours_per_day
        cost = hours * rate

        return {
            "total_loc": total_loc,
            "foreground_loc": foreground_loc,
            "estimated_days": round(days, 1),
            "estimated_hours": round(hours, 1),
            "estimated_cost_usd": round(cost, 2),
        }

    def _estimate_coupling(self, filepath: str) -> float:
        """Estimate coupling (simplified for MVP)."""
        return 0.3
