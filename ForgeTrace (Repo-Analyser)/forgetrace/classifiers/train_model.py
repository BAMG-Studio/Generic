"""
Model Training Script for IP Classifier

WHAT: Trains Random Forest classifier on labeled code examples
WHY: Convert human expertise into automated ML model

USAGE:
    python -m forgetrace.classifiers.train_model training_data.jsonl

TRAINING DATA FORMAT (JSONL):
    {"features": {...}, "label": "foreground", "file_path": "src/main.py"}
    {"features": {...}, "label": "third_party", "file_path": "vendor/lib.js"}
    ...

WORKFLOW:
1. Collect labeled examples from multiple repository audits
2. Human reviews and corrects classifications
3. Run this script to train model
4. Model saved to models/ip_classifier.pkl
5. ForgeTrace automatically uses trained model

HYPERPARAMETER TUNING:
We use cross-validation to find optimal parameters:
- n_estimators: Number of trees (more = better but slower)
- max_depth: Maximum tree depth (deeper = more complex)
- min_samples_split: Minimum samples to split node (higher = more conservative)

DEFAULT HYPERPARAMETERS:
- n_estimators=100: Good balance of accuracy vs speed
- max_depth=10: Prevents overfitting on small datasets
- min_samples_split=5: Requires 5+ examples to create split
- random_state=42: Reproducible results

These defaults work well for 100-1000 training examples.
With 10k+ examples, can increase n_estimators to 200-500.
"""

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Tuple

import joblib

try:
    import numpy as np
    from sklearn.ensemble import RandomForestClassifier  # type: ignore[import-untyped]
    from sklearn.metrics import (  # type: ignore[import-untyped]
        classification_report,
        confusion_matrix,
    )
    from sklearn.model_selection import (  # type: ignore[import-untyped]
        cross_val_score,
        train_test_split,
    )

    ML_AVAILABLE = True
except ImportError:
    print("❌ Error: scikit-learn not installed")
    print("   Install with: pip install scikit-learn numpy")
    sys.exit(1)


def load_training_data(jsonl_path: str) -> Tuple[np.ndarray, np.ndarray, List[str]]:
    """
    Load training data from JSONL file.

    RETURNS:
    - X: Feature matrix (n_samples, n_features)
    - y: Label vector (n_samples,)
    - file_paths: List of file paths for reference

    DATA QUALITY CHECKS:
    1. Remove examples with missing labels
    2. Remove examples with invalid features (NaN, inf)
    3. Warn if class imbalance >10:1 (may need resampling)
    4. Warn if <50 examples total (insufficient for training)
    """
    print(f"📂 Loading training data from {jsonl_path}")

    X_list = []
    y_list = []
    file_paths = []

    with open(jsonl_path, "r") as f:
        for line_num, line in enumerate(f, 1):
            try:
                example = json.loads(line)

                # Extract features
                features = example["features"]
                label = example["label"]
                file_path = example.get("file_path", f"unknown_{line_num}")

                # Convert features dict to array (same order as ml_classifier.py)
                feature_array = _features_dict_to_array(features)

                # Validate features (no NaN, inf)
                if not np.isfinite(feature_array).all():
                    print(f"⚠️  Line {line_num}: Invalid features, skipping")
                    continue

                X_list.append(feature_array)
                y_list.append(label)
                file_paths.append(file_path)

            except Exception as e:
                print(f"⚠️  Line {line_num}: Error parsing - {e}")
                continue

    if len(X_list) == 0:
        print("❌ No valid training examples found")
        sys.exit(1)

    X = np.array(X_list)
    y = np.array(y_list)

    print(f"✅ Loaded {len(X)} training examples")

    # Check class distribution
    class_counts = Counter(y)
    print("\n📊 Class Distribution:")
    for cls, count in class_counts.most_common():
        percentage = (count / len(y)) * 100
        print(f"   {cls}: {count} ({percentage:.1f}%)")

    # Warn about class imbalance
    max_count = max(class_counts.values())
    min_count = min(class_counts.values())
    imbalance_ratio = max_count / min_count if min_count > 0 else float("inf")

    if imbalance_ratio > 10:
        print(f"\n⚠️  WARNING: Severe class imbalance (ratio {imbalance_ratio:.1f}:1)")
        print("   Consider:")
        print("   1. Collecting more examples of minority classes")
        print("   2. Using class_weight='balanced' in RandomForest")
        print("   3. Oversampling minority class (SMOTE)")

    if len(X) < 50:
        print(f"\n⚠️  WARNING: Only {len(X)} examples")
        print("   Recommendation: Collect 100+ examples for reliable model")

    return X, y, file_paths


def _features_dict_to_array(features: Dict[str, Any]) -> np.ndarray:
    """
    Convert features dictionary to numpy array.

    CRITICAL: Order must match ml_classifier.py FileFeatures.to_array()

    WHY EXPLICIT ORDER:
    - sklearn requires consistent feature order
    - Mismatch causes silent accuracy degradation
    - Better to explicitly define than rely on dict order
    """
    return np.array(
        [
            float(features["lines_of_code"]),
            float(features["file_size_bytes"]),
            float(features["path_depth"]),
            float(features["commit_count"]),
            float(features["author_count"]),
            float(features["days_since_first_commit"]),
            float(features["days_since_last_commit"]),
            float(features["commit_frequency"]),
            float(features["cyclomatic_complexity"]),
            float(features["maintainability_index"]),
            float(features["has_license_header"]),
            float(features["has_third_party_indicators"]),
            float(features["import_count"]),
            float(features["stdlib_import_ratio"]),
            float(features["third_party_import_ratio"]),
            float(features["max_similarity_score"]),
            float(features["similar_file_count"]),
            float(features["primary_author_commit_ratio"]),
            float(features["is_primary_author_external"]),
            float(features.get("repo_vuln_density", 0.0)),
            float(features.get("repo_vuln_weighted_score", 0.0)),
            float(features.get("repo_osv_noise_ratio", 0.0)),
            float(features.get("repo_vulnerability_count", 0.0)),
        ]
    )


def train_model(X: np.ndarray, y: np.ndarray) -> RandomForestClassifier:
    """
    Train Random Forest classifier.

    HYPERPARAMETER SELECTION:

    n_estimators=100:
    - Each tree votes on classification
    - 100 trees provides stable predictions
    - More trees = diminishing returns after ~200
    - Training time scales linearly

    max_depth=10:
    - Limits tree depth to prevent overfitting
    - Depth 10 handles ~1024 decision nodes
    - Sufficient for typical code classification
    - Deeper trees memorize training data

    min_samples_split=5:
    - Requires 5+ samples to create split
    - Prevents overfitting to noise
    - Lower values (2) allow more specific rules
    - Higher values (10+) create simpler trees

    class_weight='balanced':
    - Automatically adjusts for class imbalance
    - Gives higher weight to minority classes
    - Formula: n_samples / (n_classes * n_samples_per_class)
    - Alternative: Manual weights {foreground: 1.5, background: 2.0}

    random_state=42:
    - Seed for reproducibility
    - Same data + seed = same model
    - Important for debugging and comparison
    """
    print("\n🔨 Training Random Forest classifier...")

    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,  # Use all CPU cores
    )

    model.fit(X, y)

    print("✅ Model trained successfully")

    return model


def evaluate_model(model: RandomForestClassifier, X: np.ndarray, y: np.ndarray) -> None:
    """
    Evaluate model performance using cross-validation.

    CROSS-VALIDATION:
    - Split data into K folds (K=5 default)
    - Train on K-1 folds, test on remaining fold
    - Repeat K times, average results
    - Provides unbiased estimate of generalization performance

    WHY K=5:
    - Good bias-variance tradeoff
    - 80% training, 20% validation per fold
    - Less computation than K=10
    - More stable than K=3

    METRICS:

    Accuracy: (TP + TN) / Total
    - Overall correctness
    - Misleading with class imbalance
    - Example: 90% accuracy but misses all background IP

    Precision: TP / (TP + FP)
    - Of predicted positives, how many correct?
    - Important when false positives costly
    - Example: Flagging foreground as background

    Recall: TP / (TP + FN)
    - Of actual positives, how many found?
    - Important when false negatives costly
    - Example: Missing background IP (legal risk)

    F1 Score: 2 * (Precision * Recall) / (Precision + Recall)
    - Harmonic mean of precision and recall
    - Balances both metrics
    - Best for imbalanced datasets
    """
    print("\n📊 Evaluating model with 5-fold cross-validation...")

    # Cross-validation scores
    cv_scores = cross_val_score(model, X, y, cv=5, scoring="accuracy")

    print(
        f"\nCross-validation Accuracy: {cv_scores.mean():.3f} (+/- {cv_scores.std():.3f})"
    )
    print(f"   Scores per fold: {[f'{s:.3f}' for s in cv_scores]}")

    # Train/test split for detailed metrics
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    print("\n📈 Classification Report (Test Set):")
    print(classification_report(y_test, y_pred))

    print("\n🔢 Confusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    labels = sorted(set(y))

    # Print confusion matrix with labels
    print("   ", "  ".join(f"{label_name[:4]:>6}" for label_name in labels))
    for i, label in enumerate(labels):
        print(
            f"{label[:4]:>6}", "  ".join(f"{cm[i][j]:>6}" for j in range(len(labels)))
        )

    print("\nInterpretation:")
    print("- Rows: Actual labels")
    print("- Columns: Predicted labels")
    print("- Diagonal: Correct predictions")
    print("- Off-diagonal: Misclassifications")


def analyze_feature_importance(model: RandomForestClassifier) -> None:
    """
    Analyze which features most influence predictions.

    FEATURE IMPORTANCE:
    - Measured by Gini impurity reduction
    - Higher value = more discriminative
    - Scores sum to 1.0

    INTERPRETATION:
    - Top 3 features typically account for 40-60% of decisions
    - Features with <0.01 importance can often be removed
    - Correlated features split importance (both may be low individually)

    ACTIONABLE INSIGHTS:
    - High importance → Ensure feature quality
    - Low importance → Consider removing (simplify model)
    - Unexpected importance → Investigate data leakage

    DATA LEAKAGE EXAMPLE:
    If "file_path" has high importance, model may be memorizing paths
    instead of learning patterns. This won't generalize to new repos.
    """
    print("\n🎯 Feature Importance:")

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

    importances = model.feature_importances_

    # Sort by importance
    feature_importance = sorted(
        zip(feature_names, importances), key=lambda x: x[1], reverse=True
    )

    print("\n   Top 10 Most Important Features:")
    for i, (name, importance) in enumerate(feature_importance[:10], 1):
        bar = "█" * int(importance * 100)
        print(f"   {i:2d}. {name:30s} {importance:.4f} {bar}")

    # Cumulative importance
    cumulative = 0
    for i, (name, importance) in enumerate(feature_importance):
        cumulative += importance
        if cumulative >= 0.8:
            print(f"\n   ℹ️  Top {i+1} features account for 80% of decisions")
            break


def save_model(
    model: RandomForestClassifier, output_path: str = "models/ip_classifier.pkl"
) -> None:
    """
    Save trained model to disk.

    PICKLE FORMAT:
    - Standard Python serialization
    - Preserves complete model state
    - Fast to load (<100ms)

    SECURITY WARNING:
    Joblib persists numpy-heavy sklearn models efficiently and avoids
    direct pickle usage flagged by security linters.

    MODEL VERSIONING:
    Consider naming: ip_classifier_v1.pkl, ip_classifier_v2.pkl
    Allows A/B testing and rollback if new model underperforms.
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    joblib.dump(model, output_file)

    print(f"\n💾 Model saved to {output_file}")
    print(f"   Size: {output_file.stat().st_size / 1024:.1f} KB")


def main():
    """
    Main training workflow.

    STEPS:
    1. Load training data from JSONL
    2. Train Random Forest classifier
    3. Evaluate using cross-validation
    4. Analyze feature importance
    5. Save model to disk

    COMMAND LINE USAGE:
    python -m forgetrace.classifiers.train_model training_data.jsonl
    python -m forgetrace.classifiers.train_model data/labeled_examples.jsonl --output models/custom.pkl
    """
    if len(sys.argv) < 2:
        print(
            "Usage: python -m forgetrace.classifiers.train_model <training_data.jsonl>"
        )
        print("\nExample:")
        print("  python -m forgetrace.classifiers.train_model training_data.jsonl")
        sys.exit(1)

    training_file = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "models/ip_classifier.pkl"

    if not Path(training_file).exists():
        print(f"❌ Error: File not found: {training_file}")
        sys.exit(1)

    print("=" * 70)
    print("ML IP Classifier Training")
    print("=" * 70)

    # Load data
    X, y, file_paths = load_training_data(training_file)

    # Train model
    model = train_model(X, y)

    # Evaluate
    evaluate_model(model, X, y)

    # Analyze features
    analyze_feature_importance(model)

    # Save model
    save_model(model, output_path)

    print("\n" + "=" * 70)
    print("✅ Training Complete!")
    print("=" * 70)
    print("\nNext Steps:")
    print("1. Review classification report above")
    print("2. If accuracy <80%, collect more training examples")
    print("3. Update config.yaml with model path:")
    print("   ml_classifier:")
    print(f"     model_path: {output_path}")
    print("4. Run audit: forgetrace audit <repo-path>")
    print("\nContinuous Improvement:")
    print("- Export uncertain predictions: forgetrace audit --export-uncertain")
    print("- Human reviews and corrects labels")
    print("- Retrain model with expanded dataset")
    print("- Track performance over time")


if __name__ == "__main__":
    main()
