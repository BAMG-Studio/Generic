"""
ML-Based IP Classifier - Author: Peter

WHAT: Machine learning classifier for intelligent code origin detection
WHY: Rule-based classifiers are brittle and miss nuanced patterns. ML learns from examples.

DESIGN RATIONALE:
- Random Forest chosen over other algorithms because:
  * Handles non-linear relationships (e.g., high LOC + low churn = likely third-party)
  * Robust to feature scaling issues (no normalization needed)
  * Provides feature importance rankings (explainability for auditors)
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

from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional
import json
import pickle
from collections import defaultdict, Counter
from dataclasses import dataclass, asdict
from enum import Enum

# Conditional imports - gracefully degrade if ML libraries unavailable
try:
    import numpy as np
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import cross_val_score
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    np = None
    RandomForestClassifier = None


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
    maintainability_index: float  # Low maintainability = possibly rushed background code
    
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
    
    def to_array(self) -> List[float]:
        """
        Convert features to numpy-compatible array.
        
        WHY THIS ORDER:
        - Numerical features first (most informative)
        - Boolean features converted to 0/1
        - String features excluded (need encoding separately)
        
        CAVEAT: Feature order must match training data exactly.
        Mismatch causes silent accuracy degradation!
        """
        return [
            float(self.lines_of_code),
            float(self.file_size_bytes),
            float(self.path_depth),
            float(self.commit_count),
            float(self.author_count),
            float(self.days_since_first_commit),
            float(self.days_since_last_commit),
            float(self.commit_frequency),
            float(self.cyclomatic_complexity),
            float(self.maintainability_index),
            float(self.has_license_header),
            float(self.has_third_party_indicators),
            float(self.import_count),
            float(self.stdlib_import_ratio),
            float(self.third_party_import_ratio),
            float(self.max_similarity_score),
            float(self.similar_file_count),
            float(self.primary_author_commit_ratio),
            float(self.is_primary_author_external),
        ]


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
        
        # Configuration extraction
        ml_config = config.get("ml_classifier", {})
        self.confidence_threshold = ml_config.get("confidence_threshold", 0.7)
        self.model_path = ml_config.get("model_path", "models/ip_classifier.pkl")
        self.enable_ml = ml_config.get("enabled", True) and ML_AVAILABLE
        self.fallback_to_rules = ml_config.get("fallback_to_rules", True)
        
        if self.enable_ml:
            self._load_model()
    
    def _load_model(self) -> None:
        """
        Load pre-trained model from disk.
        
        WHY PICKLE:
        - Standard Python serialization for sklearn models
        - Preserves exact model state (hyperparameters, trained weights)
        - Fast to load (<100ms for typical models)
        
        SECURITY CAVEAT:
        Pickle can execute arbitrary code. Only load models from trusted sources!
        In production, consider:
        - Model signing/verification
        - ONNX format (language-agnostic, safer)
        - Model version tracking (MLflow, DVC)
        """
        try:
            model_file = Path(self.model_path)
            if model_file.exists():
                with open(model_file, 'rb') as f:
                    self.model = pickle.load(f)
                self.model_loaded = True
                print(f"✅ ML model loaded from {model_file}")
            else:
                print(f"⚠️  No trained model found at {model_file}")
                print("   Run audit on labeled data to bootstrap training.")
                self.enable_ml = False
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            self.enable_ml = False
    
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
        
        # Convert to numpy array for sklearn
        # SHAPE: (n_files, n_features) - 2D array required by sklearn
        X = np.array([f.to_array() for f in features_list])
        
        # Predict class labels and probability distributions
        # predict() returns most likely class
        # predict_proba() returns probability for each class
        predictions = self.model.predict(X)
        probabilities = self.model.predict_proba(X)
        
        classifications = {}
        
        for i, features in enumerate(features_list):
            predicted_class = predictions[i]
            proba_dist = probabilities[i]
            
            # Get confidence (probability of predicted class)
            # WHY MAX: Confidence is how sure we are about the prediction
            confidence = float(max(proba_dist))
            
            # Build probability distribution dictionary
            # Maps each class name to its probability
            class_names = [c.value for c in CodeOrigin if c != CodeOrigin.UNKNOWN]
            proba_dict = dict(zip(class_names, proba_dist.tolist()))
            
            # Determine if human review required
            requires_review = confidence < self.confidence_threshold
            
            # Map numeric prediction back to CodeOrigin enum
            origin = CodeOrigin(class_names[predicted_class])
            
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
        print(f"📊 ML Classification: {len(classifications)} files, {review_count} require review")
        
        return classifications
    
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
        git_data = self.findings.get("git", {})
        churn = git_data.get("churn", {})
        
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
                    "rule": "sbom_match"
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
                        "rule": "permissive_license"
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
                    "rule": "single_author_low_churn"
                }
            # Multiple authors + active development = foreground
            elif author_count >= 2 and commit_count >= 5:
                classifications[fstr] = {
                    "origin": CodeOrigin.FOREGROUND.value,
                    "confidence": 0.70,
                    "requires_review": True,
                    "license": licensed.get(fstr, "none"),
                    "primary_author": primary_author,
                    "rule": "multi_author_active"
                }
            # Insufficient data
            else:
                classifications[fstr] = {
                    "origin": CodeOrigin.UNKNOWN.value,
                    "confidence": 0.30,
                    "requires_review": True,
                    "license": licensed.get(fstr, "none"),
                    "primary_author": primary_author,
                    "rule": "insufficient_data"
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
        
        # File metadata extraction
        try:
            file_size = file_path.stat().st_size
            lines_of_code = len(file_path.read_text(errors='ignore').splitlines())
        except:
            file_size = 0
            lines_of_code = 0
        
        extension = file_path.suffix
        path_depth = len(file_path.parts)
        
        # Git history extraction
        git_data = self.findings.get("git", {})
        file_commits = self._get_file_commits(fstr)
        file_authors = self._get_file_authors(fstr)
        
        commit_count = len(file_commits)
        author_count = len(file_authors)
        
        # Calculate days since first/last commit
        if file_commits:
            # Assumes commits have 'date' field (unix timestamp)
            first_commit_date = min(c.get('date', 0) for c in file_commits)
            last_commit_date = max(c.get('date', 0) for c in file_commits)
            days_since_first = (self._get_current_timestamp() - first_commit_date) // 86400
            days_since_last = (self._get_current_timestamp() - last_commit_date) // 86400
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
        
        # Import analysis
        import_stats = self._analyze_imports(file_path)
        
        # Similarity features
        similarity_data = self._get_similarity_data(fstr)
        
        # Authorship patterns
        primary_author = self._get_primary_author(fstr)
        if file_authors:
            author_commits = Counter(c.get('author') for c in file_commits)
            primary_author_commits = author_commits.most_common(1)[0][1] if author_commits else 0
            primary_author_commit_ratio = primary_author_commits / max(commit_count, 1)
        else:
            primary_author_commit_ratio = 0.0
        
        is_primary_author_external = self._is_external_author(primary_author)
        
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
            cyclomatic_complexity=complexity_data['cyclomatic'],
            maintainability_index=complexity_data['maintainability'],
            has_license_header=has_license_header,
            has_third_party_indicators=has_third_party_indicators,
            import_count=import_stats['total'],
            stdlib_import_ratio=import_stats['stdlib_ratio'],
            third_party_import_ratio=import_stats['third_party_ratio'],
            max_similarity_score=similarity_data['max_score'],
            similar_file_count=similarity_data['similar_count'],
            primary_author_commit_ratio=primary_author_commit_ratio,
            is_primary_author_external=is_primary_author_external,
        )
    
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
            '.py', '.js', '.ts', '.java', '.go', '.rs', '.c', '.cpp', '.h',
            '.rb', '.php', '.scala', '.kt', '.swift', '.m', '.cs', '.sh'
        }
        
        p = Path(file_path)
        
        # Check extension
        if p.suffix not in source_extensions:
            return False
        
        # Exclude common third-party directories
        exclude_dirs = {'node_modules', 'vendor', '.git', 'build', 'dist', '__pycache__'}
        if any(part in exclude_dirs for part in p.parts):
            return False
        
        return True
    
    def _get_file_commits(self, file_path: str) -> List[Dict]:
        """Get all commits that modified this file."""
        # Placeholder - would use git log --follow
        git_data = self.findings.get("git", {})
        churn = git_data.get("churn", {})
        return churn.get(file_path, {}).get("commits", [])
    
    def _get_file_authors(self, file_path: str) -> List[str]:
        """Get all authors who modified this file."""
        commits = self._get_file_commits(file_path)
        return list(set(c.get('author', 'unknown') for c in commits))
    
    def _get_primary_author(self, file_path: str) -> str:
        """Get primary author (most commits) for this file."""
        authors = self._get_file_authors(file_path)
        if not authors:
            return "unknown"
        
        commits = self._get_file_commits(file_path)
        author_counts = Counter(c.get('author', 'unknown') for c in commits)
        
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
        try:
            from radon.complexity import cc_visit
            from radon.metrics import mi_visit
            
            code = file_path.read_text(errors='ignore')
            
            # Cyclomatic complexity (average across all functions)
            cc_results = cc_visit(code)
            if cc_results:
                avg_complexity = sum(r.complexity for r in cc_results) / len(cc_results)
            else:
                avg_complexity = 1.0
            
            # Maintainability index
            mi_score = mi_visit(code, multi=True)
            avg_mi = sum(mi_score.values()) / len(mi_score) if mi_score else 50.0
            
            return {
                'cyclomatic': avg_complexity,
                'maintainability': avg_mi
            }
        except:
            # Radon not available or file not parseable
            return {
                'cyclomatic': 1.0,
                'maintainability': 50.0
            }
    
    def _has_license_header(self, file_path: Path) -> bool:
        """Check if file has license/copyright header in first 20 lines."""
        try:
            lines = file_path.read_text(errors='ignore').splitlines()[:20]
            header_text = '\n'.join(lines).lower()
            
            keywords = ['copyright', 'license', 'spdx-license-identifier', 'licensed under']
            return any(kw in header_text for kw in keywords)
        except:
            return False
    
    def _has_third_party_keywords(self, file_path: Path) -> bool:
        """Check for common third-party indicators in file."""
        try:
            lines = file_path.read_text(errors='ignore').splitlines()[:30]
            header_text = '\n'.join(lines).lower()
            
            # Common patterns in third-party code
            patterns = [
                'all rights reserved',
                'redistribution and use',
                'this library is free software',
                'apache license',
                'mit license',
                'permission is hereby granted'
            ]
            return any(p in header_text for p in patterns)
        except:
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
            code = file_path.read_text(errors='ignore')
            
            # Simple regex-based extraction (MVP approach)
            # Production would use AST parsing (ast.parse in Python)
            import re
            import_lines = [l for l in code.splitlines() if l.strip().startswith(('import ', 'from '))]
            
            total_imports = len(import_lines)
            if total_imports == 0:
                return {'total': 0, 'stdlib_ratio': 0.5, 'third_party_ratio': 0.5}
            
            # Python stdlib modules (partial list)
            stdlib_modules = {
                'os', 'sys', 're', 'json', 'time', 'datetime', 'pathlib',
                'collections', 'itertools', 'functools', 'typing', 'enum',
                'logging', 'argparse', 'subprocess', 'urllib', 'http'
            }
            
            stdlib_count = 0
            for line in import_lines:
                # Extract module name (first part before '.')
                match = re.search(r'(?:from|import)\s+(\w+)', line)
                if match:
                    module = match.group(1)
                    if module in stdlib_modules:
                        stdlib_count += 1
            
            stdlib_ratio = stdlib_count / total_imports
            third_party_ratio = 1.0 - stdlib_ratio
            
            return {
                'total': total_imports,
                'stdlib_ratio': stdlib_ratio,
                'third_party_ratio': third_party_ratio
            }
        except:
            return {'total': 0, 'stdlib_ratio': 0.5, 'third_party_ratio': 0.5}
    
    def _get_similarity_data(self, file_path: str) -> Dict[str, Any]:
        """Extract similarity metrics from similarity scanner."""
        similarity_findings = self.findings.get("similarity", {}).get("findings", [])
        
        # Find this file in similarity results
        for finding in similarity_findings:
            if finding.get("file") == file_path:
                return {
                    'max_score': finding.get("max_similarity", 0.0),
                    'similar_count': len(finding.get("similar_files", []))
                }
        
        return {'max_score': 0.0, 'similar_count': 0}
    
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
        if not author_email or '@' not in author_email:
            return True  # Unknown = treat as external (conservative)
        
        company_domains = self.config.get("ml_classifier", {}).get("company_domains", [])
        
        domain = author_email.split('@')[1].lower()
        
        # Check if company domain
        if any(domain.endswith(cd) for cd in company_domains):
            return False
        
        # Common personal email providers
        personal_providers = {
            'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
            'icloud.com', 'protonmail.com', 'mail.com'
        }
        
        return domain in personal_providers or len(company_domains) == 0
    
    def _get_current_timestamp(self) -> int:
        """Get current Unix timestamp."""
        import time
        return int(time.time())
    
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
        
        with open(output_path, 'w') as f:
            for features in features_list:
                if features.file_path in classifications:
                    classification = classifications[features.file_path]
                    
                    training_example = {
                        'features': asdict(features),
                        'label': classification['origin'],
                        'file_path': features.file_path,
                        'confidence': classification.get('confidence', 0.0),
                    }
                    
                    f.write(json.dumps(training_example) + '\n')
        
        print(f"✅ Exported {len(features_list)} training examples to {output_path}")
        print("   Next steps:")
        print("   1. Review and correct labels in training_data.jsonl")
        print("   2. Train model: python -m forgetrace.classifiers.train_model training_data.jsonl")
    
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
            'lines_of_code', 'file_size_bytes', 'path_depth',
            'commit_count', 'author_count', 'days_since_first_commit',
            'days_since_last_commit', 'commit_frequency',
            'cyclomatic_complexity', 'maintainability_index',
            'has_license_header', 'has_third_party_indicators',
            'import_count', 'stdlib_import_ratio', 'third_party_import_ratio',
            'max_similarity_score', 'similar_file_count',
            'primary_author_commit_ratio', 'is_primary_author_external'
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
            except:
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
                "rewriteable": score > 0.6
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
            "estimated_cost_usd": round(cost, 2)
        }
    
    def _estimate_coupling(self, filepath: str) -> float:
        """Estimate coupling (simplified for MVP)."""
        return 0.3
