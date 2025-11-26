#!/usr/bin/env python3
"""
Random Forest Training Script with Detailed Explanations

WHAT THIS SCRIPT DOES:
====================
Trains a Random Forest classifier to automatically detect code origin:
- third_party: Libraries, frameworks (e.g., React, Django)
- foreground: Your core IP (e.g., business logic, custom features)
- background: Generated code, configs (e.g., migrations, webpack configs)

WHY RANDOM FOREST:
=================
1. Handles Non-Linear Patterns: Real-world code has complex patterns
   Example: "High LOC + Low comments = likely third-party library"
   
2. No Feature Scaling: Works with raw numbers (no normalization needed)
   Example: lines_of_code (10-10,000) and has_spdx_header (0-1) can coexist
   
3. Feature Importance: Shows which signals matter most
   Example: "path_depth is 80% predictive" → focus on that feature
   
4. Resistant to Overfitting: Multiple trees vote → stable predictions
   Example: One tree memorizes training data, 99 others correct it

TRAINING PROCESS:
================
Step 1: Load 131K examples from JSONL file
Step 2: Split into features (X) and labels (y)
Step 3: Create 100 decision trees, each learning different patterns
Step 4: Evaluate accuracy using cross-validation
Step 5: Analyze which features are most important
Step 6: Save trained model to disk

EXPECTED OUTCOME:
================
- Accuracy: 85-95% (varies by dataset quality)
- Training time: 30-60 seconds for 131K examples
- Model size: ~5-10 MB on disk
- Inference speed: <1ms per file classification
"""

import argparse
import json
import os
import pickle
import sys
import time
from collections import Counter
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

try:  # MLflow is optional when running outside CI
    import mlflow
    import mlflow.sklearn
except Exception:  # pragma: no cover - optional dependency guard
    mlflow = None


def _parse_cli_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train the ForgeTrace Random Forest model")
    parser.add_argument(
        "--phase",
        default="ALL",
        help="Phase context for this training run (default: ALL).",
        choices=["ALL", "FOUNDATIONAL", "POLYGLOT", "SECURITY", "ENTERPRISE", "RESEARCH"],
    )
    parser.add_argument(
        "--input",
        dest="input_path",
        help="Path to training dataset JSONL (falls back to positional argument).",
    )
    parser.add_argument(
        "--output",
        dest="output_path",
        help="Where to store the trained model (falls back to positional argument or default).",
    )
    parser.add_argument(
        "--mlflow-experiment",
        dest="mlflow_experiment",
        help="Optional MLflow experiment name (reserved for future logging).",
    )
    parser.add_argument(
        "training_file",
        nargs="?",
        help="Positional dataset path (optional).",
    )
    parser.add_argument(
        "model_file",
        nargs="?",
        help="Positional model output path (optional).",
    )
    return parser.parse_args()


# Feature engineering controls
AUTO_PRUNE_THRESHOLD: Optional[float] = 0.001  # Remove features contributing less than 0.1%
PROTECTED_FEATURES: Set[str] = {
    "repo_vuln_density",
    "repo_vuln_weighted_score",
    "repo_osv_noise_ratio",
    "repo_vulnerability_count",
}

LOG_TRANSFORM_FEATURES: Sequence[str] = (
    "lines_of_code",
    "file_size_bytes",
)

MODEL_CONFIG: Dict[str, Any] = {
    "n_estimators": 100,
    "max_depth": 15,
    "min_samples_split": 10,
    "class_weight": "balanced",
    "random_state": 42,
    "n_jobs": -1,
}


def _mlflow_configured() -> bool:
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI")
    return bool(tracking_uri) and mlflow is not None


@contextmanager
def _mlflow_run(run_name: str, phase_context: str):
    if not _mlflow_configured():
        yield None
        return

    tracking_uri = os.environ["MLFLOW_TRACKING_URI"]
    mlflow.set_tracking_uri(tracking_uri)

    # Basic auth variables expected by MLflow's HTTP client
    username = os.getenv("MLFLOW_USERNAME")
    password = os.getenv("MLFLOW_PASSWORD")
    if username and password:
        os.environ["MLFLOW_TRACKING_USERNAME"] = username
        os.environ["MLFLOW_TRACKING_PASSWORD"] = password

    experiment_name = os.getenv("MLFLOW_EXPERIMENT_NAME", "forgetrace-training")
    mlflow.set_experiment(experiment_name)

    default_run_name = run_name or f"rf-{phase_context.lower()}-{datetime.utcnow().isoformat()}"
    with mlflow.start_run(run_name=default_run_name) as active_run:
        mlflow.set_tags({
            "phase": phase_context,
            "training_script": "train_random_forest.py",
            "ci_pipeline": os.getenv("GITHUB_WORKFLOW", "local"),
        })
        yield active_run


def _log_results_to_mlflow(
    model: RandomForestClassifier,
    metrics: Dict[str, float],
    artifacts: List[Path],
    feature_names: Sequence[str],
    metadata: Dict[str, Any],
    phase_context: str,
    dataset_path: str,
    output_path: str,
):
    if not _mlflow_configured():
        return

    with _mlflow_run(run_name=f"RF-{phase_context}", phase_context=phase_context):
        mlflow.log_params({
            "dataset_path": dataset_path,
            "model_output": output_path,
            "feature_count": len(feature_names),
            "phase": phase_context,
            **MODEL_CONFIG,
        })

        mlflow.log_metrics(metrics)
        mlflow.log_dict(
            {
                "feature_names": list(feature_names),
                "metadata": metadata,
                "artifact_paths": [str(path) for path in artifacts],
            },
            artifact_file="training_metadata.json",
        )

        for artifact in artifacts:
            if artifact.exists():
                mlflow.log_artifact(str(artifact))

        # Persist model using MLflow's sklearn utilities for easier serving
        try:
            mlflow.sklearn.log_model(
                sk_model=model,
                artifact_path="model",
                registered_model_name=os.getenv(
                    "MLFLOW_REGISTERED_MODEL_NAME", "forgetrace-ip-classifier"
                ),
            )
        except Exception as exc:  # pragma: no cover - network/registry issues
            print(f"⚠️  Failed to register model with MLflow registry: {exc}")


def apply_log_transforms(
    X: np.ndarray,
    feature_names: List[str],
    features_to_transform: Sequence[str],
) -> Tuple[np.ndarray, List[str]]:
    """Apply log1p scaling to high-variance features."""

    transformed: List[str] = []
    feature_index = {name: idx for idx, name in enumerate(feature_names)}

    for feature in features_to_transform:
        idx = feature_index.get(feature)
        if idx is None:
            continue

        column = X[:, idx]
        min_val = float(np.min(column))
        adjusted = column - min_val if min_val < 0 else column
        X[:, idx] = np.log1p(adjusted)
        transformed.append(feature)

    if transformed:
        print("\n🔧 Applied log1p transform to:")
        for name in transformed:
            print(f"   • {name}")

    return X, transformed


def collect_low_importance_features(
    feature_names: Sequence[str],
    importances: np.ndarray,
    threshold: float,
) -> List[Tuple[str, float]]:
    """Return features with importance below threshold."""

    low_features: List[Tuple[str, float]] = []
    for name, importance in zip(feature_names, importances):
        if importance < threshold:
            low_features.append((name, float(importance)))
    return sorted(low_features, key=lambda item: item[1])


def print_section(title: str):
    """Pretty print section headers"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def infer_feature_schema(jsonl_path: str) -> List[str]:
    """Infer canonical feature ordering across all training examples."""

    feature_names: List[str] = []
    seen: set[str] = set()

    with open(jsonl_path, "r", encoding="utf-8") as fh:
        for line in fh:
            example = json.loads(line)
            for name in example["features"].keys():
                if name not in seen:
                    seen.add(name)
                    feature_names.append(name)

    # Preserve first-seen order (grouped roughly by extractor) for explainability
    return feature_names


def load_training_data(jsonl_path: str, feature_names: List[str]) -> Tuple[np.ndarray, np.ndarray, List[str]]:
    """
    STEP 1: Load Training Data from JSONL File
    ===========================================
    
    INPUT FORMAT (one JSON per line):
    {
        "label": "foreground",
        "features": {
            "lines_of_code": 1179.0,
            "avg_line_length": 1.99,
            "comment_ratio": 0.0008,
            "path_depth": 4.0,
            "file_size_bytes": 39624.0,
            "has_spdx_header": 0.0,
            "is_test_path": 0.0,
            "is_docs_path": 0.0
        },
        ...
    }
    
    OUTPUT:
    - X: Feature matrix (131731 rows × 8 columns)
         Each row = one file, each column = one feature
    - y: Label vector (131731 labels)
         Each element = "foreground", "third_party", or "background"
    - file_paths: Reference for debugging
    
    WHAT HAPPENS HERE:
    1. Read each line of JSONL file
    2. Extract the 8 feature values → becomes one row in X
    3. Extract the label → becomes one element in y
    4. Stack all rows to create full dataset
    
    ANALOGY:
    Like creating a spreadsheet where:
    - Each row = one code file
    - Columns = measurements (LOC, comments, etc.)
    - Last column = the answer we want to predict
    """
    print_section("STEP 1: Loading Training Data")
    print(f"📂 Reading from: {jsonl_path}")
    print("⏳ This may take 30-60 seconds for 131K examples...")
    
    start_time = time.time()
    
    X_list: List[np.ndarray] = []  # Will hold feature arrays
    y_list: List[str] = []  # Will hold labels
    file_paths: List[str] = []  # For reference
    
    feature_index = {name: idx for idx, name in enumerate(feature_names)}

    with open(jsonl_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            if line_num % 10000 == 0:
                print(f"   ... processed {line_num:,} examples", end='\r')
            
            try:
                example = json.loads(line)
                
                # Extract features in consistent order
                features = example['features']
                feature_array = np.zeros(len(feature_names), dtype=float)

                for key, value in features.items():
                    if key not in feature_index:
                        continue
                    try:
                        feature_array[feature_index[key]] = float(value)
                    except (TypeError, ValueError):
                        feature_array[feature_index[key]] = 0.0
                
                # Extract label
                label = example['label']
                
                # Validate: no NaN or infinity values
                if not np.isfinite(feature_array).all():
                    continue
                
                X_list.append(feature_array)
                y_list.append(label)
                file_paths.append(example.get('file_path', f'unknown_{line_num}'))
                
            except Exception:
                # Skip malformed lines
                continue
    
    # Convert lists to numpy arrays (required by scikit-learn)
    X = np.array(X_list)
    y = np.array(y_list)
    
    load_time = time.time() - start_time
    
    print(f"\n✅ Loaded {len(X):,} examples in {load_time:.1f} seconds")
    print(f"   Feature matrix shape: {X.shape} (rows=files, cols=features)")
    
    # Show class distribution
    print("\n📊 Class Distribution (what we're trying to predict):")
    class_counts = Counter(y)
    for cls, count in class_counts.most_common():
        percentage = (count / len(y)) * 100 if len(y) > 0 else 0
        bar = "█" * int(percentage / 2)
        print(f"   {cls:15s}: {count:7,} ({percentage:5.1f}%) {bar}")
        print(f"   Feature matrix shape: {X.shape} (rows=files, cols=features)")
        print(f"   Canonical feature count: {len(feature_names)}")
    # Check for severe imbalance
    max_count = max(class_counts.values())
    min_count = min(class_counts.values())
    imbalance_ratio = max_count / min_count if min_count > 0 else float('inf')
    
    if imbalance_ratio > 10:
        print(f"\n⚠️  Class imbalance detected (ratio {imbalance_ratio:.1f}:1)")
        print("   → Model will use 'balanced' weights to compensate")
    
    return X, y, file_paths


def explain_train_test_split():
    """
    STEP 2: Understanding Train/Test Split
    ======================================
    
    WHY SPLIT THE DATA?
    - Training set (80%): Model learns patterns from these examples
    - Test set (20%): Model NEVER sees these during training
    - Simulates real-world: Can the model classify NEW files it's never seen?
    
    ANALOGY:
    Like studying for an exam:
    - Training set = practice problems you study
    - Test set = actual exam questions (different from practice)
    - If you memorize practice problems, you'll fail the exam!
    
    STRATIFICATION:
    Ensures both sets have same class proportions:
    - If original data = 90% third_party, 5% foreground, 5% background
    - Training set = 90% third_party, 5% foreground, 5% background
    - Test set = 90% third_party, 5% foreground, 5% background
    
    This prevents: "Training only on third_party, testing on foreground"
    """
    print_section("STEP 2: Understanding Train/Test Split")
    print("""
    We split data into 80% training and 20% testing:
    
    ┌─────────────────────────────────────────────────┐
    │         Original Dataset (131,731 files)         │
    └──────────────────┬──────────────────────────────┘
                       │
           ┌───────────┴───────────┐
           ▼                       ▼
    ┌─────────────┐         ┌─────────────┐
    │  Training   │         │   Testing   │
    │  (80% ~105K)│         │  (20% ~26K) │
    │             │         │             │
    │ Model       │         │ Model       │
    │ LEARNS      │         │ EVALUATED   │
    │ patterns    │         │ (never seen │
    │ from this   │         │  during     │
    │             │         │  training)  │
    └─────────────┘         └─────────────┘
    
    WHY THIS MATTERS:
    - High training accuracy + Low test accuracy = OVERFITTING
      (Model memorized training data instead of learning patterns)
    - Both high = GOOD (Model learned generalizable patterns)
    """)


def train_model(X_train: np.ndarray, y_train: np.ndarray) -> RandomForestClassifier:
    """
    STEP 3: Training the Random Forest
    ==================================
    
    WHAT IS A RANDOM FOREST?
    Think of it as a committee of 100 decision trees voting:
    
    Decision Tree Example:
    
                      path_depth > 3?
                      /            \\
                    YES            NO
                    /                \\
          lines_of_code > 500?    is_test_path?
              /         \\              /       \\
            YES         NO           YES       NO
            /            \\            /         \\
      third_party   foreground   foreground  third_party
    
    Random Forest = 100 of these trees, each slightly different
    
    Final prediction = majority vote of all 100 trees
    Example: 78 trees say "third_party", 22 say "foreground"
             → Final prediction: "third_party" (78% confidence)
    
    HYPERPARAMETERS EXPLAINED:
    
    n_estimators=100:
        Number of trees in the forest
        More trees = more stable predictions, but slower
        100 is a good balance for 131K examples
        
    max_depth=15:
        Maximum depth of each tree
        Deeper = more complex patterns, but risk overfitting
        15 levels = can create 2^15 = 32,768 decision rules
        
    min_samples_split=10:
        Minimum examples needed to split a node
        Higher = simpler trees (prevents learning noise)
        10 is conservative for our large dataset
        
    class_weight='balanced':
        Automatically adjusts for imbalanced classes
        If third_party=117K, foreground=12K, background=2K
        → Give higher weight to rare classes
        Formula: total_samples / (n_classes × samples_per_class)
        
    random_state=42:
        Seed for reproducibility
        Same data + same seed = same model every time
        Important for debugging and comparison
        
    n_jobs=-1:
        Use all CPU cores (parallel training)
        -1 = use all available cores
        Speeds up training by 4-8x on modern CPUs
    """
    print_section("STEP 3: Training Random Forest Classifier")
    print("""
    Random Forest Architecture:
    
    Training Data → ┌─────────────┐
                    │   Tree #1   │ → Vote: "third_party"
                    ├─────────────┤
                    │   Tree #2   │ → Vote: "third_party"
                    ├─────────────┤
                    │   Tree #3   │ → Vote: "foreground"
                    ├─────────────┤
                    │     ...     │
                    ├─────────────┤
                    │  Tree #100  │ → Vote: "third_party"
                    └─────────────┘
                           ↓
                    Majority Vote
                           ↓
                  Final: "third_party"
    """)
    
    print("⚙️  Hyperparameters:")
    print("   • n_estimators=100     (100 decision trees)")
    print("   • max_depth=15         (each tree up to 15 levels deep)")
    print("   • min_samples_split=10 (need 10+ examples to create split)")
    print("   • class_weight=balanced (adjust for imbalanced classes)")
    print("   • n_jobs=-1            (use all CPU cores)")
    
    print("\n🔨 Training model...")
    print("   This creates 100 decision trees simultaneously...")
    
    start_time = time.time()
    
    model = RandomForestClassifier(
        **MODEL_CONFIG,
        verbose=0,
    )
    
    # This is where the magic happens!
    # Each tree learns patterns from a random subset of training data
    model.fit(X_train, y_train)
    
    train_time = time.time() - start_time
    
    print(f"✅ Training complete in {train_time:.1f} seconds")
    print(f"   Model created {model.n_estimators} trees")
    print(f"   Total decision nodes: ~{sum(tree.tree_.node_count for tree in model.estimators_):,}")
    
    return model


def evaluate_model(
    model: RandomForestClassifier,
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray,
) -> Tuple[Dict[str, float], Dict[str, Any]]:
    """
    STEP 4: Evaluating Model Performance
    ====================================
    
    METRICS EXPLAINED:
    
    1. ACCURACY: (Correct predictions) / (Total predictions)
       Example: 90% accuracy = 90 out of 100 files classified correctly
       
    2. PRECISION: Of files we classified as X, how many really are X?
       Example: Precision(third_party)=95% means:
       → If we say "third_party", we're right 95% of the time
       → Low precision = too many false alarms
       
    3. RECALL: Of all files that are X, how many did we find?
       Example: Recall(background)=80% means:
       → We found 80% of background IP files
       → Low recall = missed 20% (dangerous for legal compliance!)
       
    4. F1-SCORE: Harmonic mean of precision and recall
       Example: F1=0.87 balances both metrics
       → Good when both precision AND recall matter
    
    CONFUSION MATRIX:
    Shows where model gets confused:
    
                  Predicted
                  fg   tp   bg
    Actual  fg   [90   8   2]  ← Of 100 foreground files
            tp   [ 5  92   3]  ← Of 100 third_party files  
            bg   [ 3   7  90]  ← Of 100 background files
    
    Reading: Row 1, Col 2: "8 foreground files misclassified as third_party"
    
    CROSS-VALIDATION:
    Instead of one train/test split, we do 5 splits:
    
    Split 1: Train on [B,C,D,E], Test on [A] → 88% accuracy
    Split 2: Train on [A,C,D,E], Test on [B] → 91% accuracy
    Split 3: Train on [A,B,D,E], Test on [C] → 89% accuracy
    Split 4: Train on [A,B,C,E], Test on [D] → 90% accuracy
    Split 5: Train on [A,B,C,D], Test on [E] → 92% accuracy
    
    Average: 90% ± 1.4% (more reliable than single split)
    """
    print_section("STEP 4: Evaluating Model Performance")
    
    # Predictions on both sets
    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)
    
    train_accuracy = accuracy_score(y_train, y_train_pred)
    test_accuracy = accuracy_score(y_test, y_test_pred)
    
    print(f"\n📈 Accuracy Scores:")
    print(f"   Training accuracy: {train_accuracy:.3f} ({train_accuracy*100:.1f}%)")
    print(f"   Testing accuracy:  {test_accuracy:.3f} ({test_accuracy*100:.1f}%)")
    
    # Check for overfitting
    if train_accuracy - test_accuracy > 0.05:
        print(f"\n⚠️  WARNING: Possible overfitting detected!")
        print(f"   Gap: {(train_accuracy - test_accuracy)*100:.1f}%")
        print("   → Model memorized training data instead of learning patterns")
        print("   → Consider: reducing max_depth or increasing min_samples_split")
    else:
        print(f"\n✅ Good generalization (train-test gap: {(train_accuracy - test_accuracy)*100:.1f}%)")
    
    # Detailed metrics on test set
    print("\n📊 Detailed Classification Report (Test Set):")
    print("   Shows precision, recall, and F1 for each class\n")
    report = classification_report(y_test, y_test_pred, digits=3)
    print(report)
    
    # Confusion matrix
    print("\n🔢 Confusion Matrix (Test Set):")
    print("   Rows=Actual, Columns=Predicted\n")
    
    cm = confusion_matrix(y_test, y_test_pred)
    labels = sorted(set(y_test))
    
    # Pretty print confusion matrix
    header = "          " + "  ".join(f"{l[:4]:>8}" for l in labels)
    print(header)
    print("          " + "-" * (len(labels) * 10))
    for i, label in enumerate(labels):
        row = f"{label[:10]:>10}" + "  ".join(f"{cm[i][j]:>8,}" for j in range(len(labels)))
        print(row)
    
    print("\n💡 How to read:")
    print("   Diagonal values = correct predictions (higher is better)")
    print("   Off-diagonal = mistakes (lower is better)")
    
    # Cross-validation for robustness
    print("\n🔄 Cross-Validation (5-fold):")
    print("   Testing model stability across different data splits...")
    
    cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy', n_jobs=-1)
    
    print(f"\n   Fold accuracies: {[f'{s:.3f}' for s in cv_scores]}")
    print(f"   Average: {cv_scores.mean():.3f} (±{cv_scores.std():.3f})")
    print(f"\n   Interpretation: Model is {'stable' if cv_scores.std() < 0.02 else 'somewhat variable'} across different data subsets")

    metrics = {
        "train_accuracy": float(train_accuracy),
        "test_accuracy": float(test_accuracy),
        "train_test_gap": float(train_accuracy - test_accuracy),
        "cv_mean_accuracy": float(cv_scores.mean()),
        "cv_std_accuracy": float(cv_scores.std()),
    }

    evaluation = {
        "classification_report": report,
        "confusion_matrix": cm.tolist(),
        "labels": labels,
        "cv_scores": [float(score) for score in cv_scores],
    }

    return metrics, evaluation


def analyze_feature_importance(model: RandomForestClassifier, feature_names: List[str]) -> None:
    """Report feature importance using the canonical feature schema."""

    print_section("STEP 5: Feature Importance Analysis")

    print("""
    Feature Importance shows which signals matter most:

    High importance (>15%):  Critical for predictions
    Medium (5-15%):          Useful supporting signals  
    Low (<5%):               Minor contribution
    """)

    importances = model.feature_importances_

    feature_importance = sorted(
        zip(feature_names, importances),
        key=lambda item: item[1],
        reverse=True,
    )

    print("\n🎯 Feature Ranking:")
    print("   " + "=" * 60)

    cumulative = 0.0
    cumulative_reported = False

    for i, (name, importance) in enumerate(feature_importance, 1):
        cumulative += importance
        bar = "█" * max(1, int(importance * 100)) if importance > 0 else ""
        symbol = "🔥" if importance > 0.15 else "📊" if importance > 0.05 else "📉"
        print(f"   {i}. {symbol} {name:35s} {importance:6.2%}  {bar}")

        if not cumulative_reported and cumulative >= 0.8:
            print(f"\n   💡 Top {i} features account for {cumulative:.1%} of decisions")
            cumulative_reported = True

    print("\n📝 Interpretation Guide:")
    top_feature = feature_importance[0]
    print(f"   • {top_feature[0]} ({top_feature[1]:.1%}) is the strongest predictor")
    print(f"   • This means classification heavily relies on {top_feature[0]}")
    print(f"   • Ensure this feature is accurately extracted in production")

    low_features = [name for name, imp in feature_importance if imp < 0.03]
    if low_features:
        print(f"\n   ⚠️  Low-importance features: {', '.join(low_features)}")
        print("   → Could be removed to simplify model (tradeoff: slightly lower accuracy)")


def persist_evaluation_artifacts(
    evaluation: Dict[str, Any],
    metrics_dir: Path,
) -> List[Path]:
    """Write evaluation artifacts to disk for MLflow/artifact uploads."""

    metrics_dir.mkdir(parents=True, exist_ok=True)

    report_path = metrics_dir / "classification_report.txt"
    report_path.write_text(evaluation["classification_report"] + "\n", encoding="utf-8")

    cm_payload = {
        "labels": evaluation["labels"],
        "matrix": evaluation["confusion_matrix"],
        "cv_scores": evaluation["cv_scores"],
    }
    cm_path = metrics_dir / "confusion_matrix.json"
    cm_path.write_text(json.dumps(cm_payload, indent=2), encoding="utf-8")

    return [report_path, cm_path]


def save_model(
    model: RandomForestClassifier,
    feature_names: List[str],
    output_path: str = "models/ip_classifier_rf.pkl",
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """Persist trained model, feature schema, and metadata to disk."""

    print_section("STEP 6: Saving Trained Model")

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    print(f"💾 Saving model to: {output_file}")

    payload: Dict[str, Any] = {"model": model, "feature_names": feature_names}
    if metadata:
        payload.update(metadata)

    with open(output_file, 'wb') as f:
        pickle.dump(payload, f)

    model_size_kb = output_file.stat().st_size / 1024
    model_size_mb = model_size_kb / 1024

    print("✅ Model saved successfully!")
    print(f"   Size: {model_size_mb:.2f} MB ({model_size_kb:.1f} KB)")
    print(f"   Location: {output_file.absolute()}")

    print("\n📦 Model Contents:")
    print(f"   • {model.n_estimators} decision trees")
    print(f"   • {len(feature_names)} features")
    print(f"   • {len(model.classes_)} classes: {', '.join(model.classes_)}")

    print("\n🚀 Next Steps:")
    print("   1. Update config.yaml:")
    print("      ml_classifier:")
    print(f"        model_path: {output_path}")
    print("        enabled: true")
    print("\n   2. Test the model:")
    print("      forgetrace audit <repo-path> --use-ml")
    print("\n   3. Monitor performance:")
    print("      - Review uncertain classifications (confidence < 0.7)")
    print("      - Collect feedback from human reviewers")
    print("      - Retrain periodically with corrected examples")


def main():
    """
    Main Training Workflow
    ======================
    
    OVERVIEW:
    1. Load 131K training examples
    2. Split into 80% train, 20% test
    3. Train Random Forest (100 trees)
    4. Evaluate accuracy and metrics
    5. Analyze feature importance
    6. Save model to disk
    
    EXPECTED RUNTIME:
    - Loading data: 30-60 seconds
    - Training: 30-60 seconds
    - Evaluation: 10-20 seconds
    - Total: ~2-3 minutes
    
    EXPECTED RESULTS:
    - Accuracy: 85-95%
    - Precision/Recall: >0.80 for all classes
    - Model size: 5-10 MB
    """
    args = _parse_cli_args()
    training_file = (
        args.input_path
        or args.training_file
        or "training_output/dataset/complete_training_dataset.jsonl"
    )
    output_path = args.output_path or args.model_file or "models/ip_classifier_rf.pkl"
    phase_context = args.phase.upper()
    
    if not Path(training_file).exists():
        print(f"❌ Error: File not found: {training_file}")
        sys.exit(1)
    
    print("\n" + "█"*70)
    print("█" + " "*68 + "█")
    print("█" + "  RANDOM FOREST IP CLASSIFIER TRAINING".center(68) + "█")
    print("█" + " "*68 + "█")
    print("█"*70)
    
    print("\n🎯 Goal: Train ML model to classify code as foreground/third_party/background")
    print("📊 Dataset: 131,731 labeled examples from 54 open-source projects")
    print("⏱️  Estimated time: 2-3 minutes\n")
    print(f"🎚️  Phase context: {phase_context}")
    if args.mlflow_experiment:
        print(f"📡 MLflow experiment: {args.mlflow_experiment}")
    
    # Step 1: Load data
    feature_names = infer_feature_schema(training_file)
    print(f"🧬 Discovered {len(feature_names)} unique features across all phases")
    feature_matrix, y, _ = load_training_data(training_file, feature_names)

    # Step 2: Apply feature engineering before splitting
    feature_matrix, transformed_features = apply_log_transforms(
        feature_matrix, feature_names, LOG_TRANSFORM_FEATURES
    )

    # Step 3: Explain and perform train/test split
    explain_train_test_split()
    x_train, x_test, y_train, y_test = train_test_split(
        feature_matrix, y, test_size=0.2, random_state=42, stratify=y
    )
    total_examples = len(feature_matrix)
    print(f"✅ Split complete:")
    print(f"   Training set: {len(x_train):,} examples ({len(x_train)/total_examples*100:.1f}%)")
    print(f"   Test set:     {len(x_test):,} examples ({len(x_test)/total_examples*100:.1f}%)")
    
    # Step 4: Train initial model (used for pruning analysis)
    model = train_model(x_train, y_train)

    removed_features: List[str] = []
    if AUTO_PRUNE_THRESHOLD and AUTO_PRUNE_THRESHOLD > 0:
        threshold = AUTO_PRUNE_THRESHOLD
        low_features = collect_low_importance_features(
            feature_names, model.feature_importances_, threshold
        )

        removable = [(name, importance) for name, importance in low_features if name not in PROTECTED_FEATURES]
        protected = [(name, importance) for name, importance in low_features if name in PROTECTED_FEATURES]

        if removable:
            print("\n🧹 Pruning low-importance features (<0.1% importance):")
            for name, importance in removable:
                print(f"   • {name:35s} {importance:.6f}")

            removed_features = [name for name, _ in removable]
            removed_set = set(removed_features)
            keep_indices = [idx for idx, name in enumerate(feature_names) if name not in removed_set]

            feature_names = [feature_names[idx] for idx in keep_indices]
            feature_matrix = feature_matrix[:, keep_indices]
            x_train = x_train[:, keep_indices]
            x_test = x_test[:, keep_indices]

            print(f"\n🔁 Retraining after removing {len(removed_features)} features...")
            model = train_model(x_train, y_train)

        if protected:
            print("\nℹ️  Retained protected low-importance features (pending upstream fixes):")
            for name, importance in protected:
                print(f"   • {name:35s} {importance:.6f}")

    # Step 5: Evaluate final model
    metrics, evaluation = evaluate_model(model, x_train, y_train, x_test, y_test)

    # Step 6: Feature importance summary
    analyze_feature_importance(model, feature_names)

    # Step 7: Save model with metadata for inference parity
    model_metadata: Dict[str, Any] = {"log_transformed_features": transformed_features}
    if removed_features:
        model_metadata["removed_features"] = removed_features
        model_metadata["auto_prune_threshold"] = AUTO_PRUNE_THRESHOLD

    save_model(model, feature_names, output_path, metadata=model_metadata)

    metrics_dir = Path("training_output/metrics")
    artifact_paths = persist_evaluation_artifacts(evaluation, metrics_dir)
    artifact_paths.append(Path(output_path))

    _log_results_to_mlflow(
        model=model,
        metrics=metrics,
        artifacts=artifact_paths,
        feature_names=feature_names,
        metadata=model_metadata,
        phase_context=phase_context,
        dataset_path=training_file,
        output_path=output_path,
    )
    
    print("\n" + "█"*70)
    print("█" + " "*68 + "█")
    print("█" + "  ✅ TRAINING COMPLETE!".center(68) + "█")
    print("█" + " "*68 + "█")
    print("█"*70 + "\n")
    
    print("🎉 Your Random Forest classifier is ready!")
    print("📚 Review the metrics above to understand model performance")
    print("🔍 Pay special attention to feature importance for insights")


if __name__ == '__main__':
    main()
