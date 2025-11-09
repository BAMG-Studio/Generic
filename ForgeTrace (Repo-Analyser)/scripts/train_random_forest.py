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

import json
import pickle
import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple
from collections import Counter
import time

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score


def print_section(title: str):
    """Pretty print section headers"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def infer_feature_schema(jsonl_path: str) -> List[str]:
    """Infer canonical feature ordering across all training examples."""

    feature_names: List[str] = []
    seen = set()

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
    
    X_list = []  # Will hold feature arrays
    y_list = []  # Will hold labels
    file_paths = []  # For reference
    
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
                
            except Exception as e:
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
        n_estimators=100,
        max_depth=15,
        min_samples_split=10,
        class_weight='balanced',
        random_state=42,
        n_jobs=-1,
        verbose=0
    )
    
    # This is where the magic happens!
    # Each tree learns patterns from a random subset of training data
    model.fit(X_train, y_train)
    
    train_time = time.time() - start_time
    
    print(f"✅ Training complete in {train_time:.1f} seconds")
    print(f"   Model created {model.n_estimators} trees")
    print(f"   Total decision nodes: ~{sum(tree.tree_.node_count for tree in model.estimators_):,}")
    
    return model


def evaluate_model(model: RandomForestClassifier, X_train: np.ndarray, y_train: np.ndarray, 
                   X_test: np.ndarray, y_test: np.ndarray) -> None:
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
    print(classification_report(y_test, y_test_pred, digits=3))
    
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


def save_model(model: RandomForestClassifier, feature_names: List[str], output_path: str = "models/ip_classifier_rf.pkl") -> None:
    """Persist trained model and feature schema to disk."""

    print_section("STEP 6: Saving Trained Model")

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    print(f"💾 Saving model to: {output_file}")

    with open(output_file, 'wb') as f:
        pickle.dump({"model": model, "feature_names": feature_names}, f)

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
    if len(sys.argv) < 2:
        print("Usage: python train_random_forest.py <training_data.jsonl>")
        print("\nExample:")
        print("  python train_random_forest.py training_output/dataset/training_dataset.jsonl")
        sys.exit(1)
    
    training_file = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "models/ip_classifier_rf.pkl"
    
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
    
    # Step 1: Load data
    feature_names = infer_feature_schema(training_file)
    print(f"🧬 Discovered {len(feature_names)} unique features across all phases")
    X, y, _ = load_training_data(training_file, feature_names)
    
    # Step 2: Explain and perform train/test split
    explain_train_test_split()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"✅ Split complete:")
    print(f"   Training set: {len(X_train):,} examples ({len(X_train)/len(X)*100:.1f}%)")
    print(f"   Test set:     {len(X_test):,} examples ({len(X_test)/len(X)*100:.1f}%)")
    
    # Step 3: Train model
    model = train_model(X_train, y_train)
    
    # Step 4: Evaluate
    evaluate_model(model, X_train, y_train, X_test, y_test)
    
    # Step 5: Feature importance
    analyze_feature_importance(model, feature_names)
    
    # Step 6: Save model
    save_model(model, feature_names, output_path)
    
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
