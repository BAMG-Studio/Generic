# ML-Based IP Classification

## Overview

**WHAT**: Machine learning classifier that automatically detects code origin (third-party, background, foreground IP)

**WHY**: Rule-based classifiers are brittle and miss subtle patterns. ML learns from examples and adapts to your codebase.

## How It Works

### Architecture

```
┌─────────────────┐
│ Repository Scan │  (git, licenses, SBOM, similarity)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Feature Extract │  (20+ numerical features)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Random Forest   │  (100 decision trees)
│   Classifier    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Confidence      │  (High >0.8, Medium 0.5-0.8, Low <0.5)
│   Scoring       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Classification  │  (third_party, background, foreground)
│   + Review Flag │
└─────────────────┘
```

### Feature Engineering

The classifier extracts **19 features** from each file:

#### 1. File Metadata (3 features)
- **lines_of_code**: Large files often indicate third-party libraries
- **file_size_bytes**: Correlates with LOC, redundant but helpful for robustness
- **path_depth**: Third-party code often in deeper directories (vendor/, node_modules/)

#### 2. Git History (7 features)
- **commit_count**: Third-party rarely modified after import, background IP has few commits
- **author_count**: Single author suggests background IP, many authors = foreground
- **days_since_first_commit**: Older files may be imported third-party
- **days_since_last_commit**: Recently modified = active development (foreground)
- **commit_frequency**: commits/day - low frequency suggests static third-party code
- **primary_author_commit_ratio**: Dominant author (>80%) indicates background IP
- **is_primary_author_external**: External email domains (gmail) suggest contractor work

#### 3. Code Complexity (2 features)
- **cyclomatic_complexity**: High complexity = sophisticated library code
- **maintainability_index**: Low score = possibly rushed background code

#### 4. License Indicators (2 features)
- **has_license_header**: SPDX tags, copyright notices → third-party
- **has_third_party_indicators**: Keywords like "Licensed under", "All rights reserved"

#### 5. Import Analysis (3 features)
- **import_count**: Total number of imports
- **stdlib_import_ratio**: High stdlib usage = likely original code
- **third_party_import_ratio**: High third-party imports = uses many dependencies

#### 6. Similarity (2 features)
- **max_similarity_score**: Highest match to known third-party code
- **similar_file_count**: Duplicated files suggest copy-paste

### Algorithm Choice: Random Forest

**Why Random Forest over alternatives?**

| Algorithm | Pros | Cons | Verdict |
|-----------|------|------|---------|
| **Random Forest** | ✅ Non-linear<br>✅ No scaling needed<br>✅ Feature importance<br>✅ Fast inference | ⚠️ Larger model size | ✅ **CHOSEN** |
| Logistic Regression | ✅ Fast<br>✅ Interpretable | ❌ Linear only<br>❌ Requires scaling | ❌ Too simple |
| Neural Network | ✅ Can learn any pattern | ❌ Needs 10k+ examples<br>❌ Slow training<br>❌ Hard to interpret | ❌ Overkill |
| SVM | ✅ Good with small data | ❌ Slow inference<br>❌ Needs scaling<br>❌ Hard to interpret | ❌ Impractical |
| Naive Bayes | ✅ Fast | ❌ Assumes independence<br>❌ Lower accuracy | ❌ Unrealistic assumptions |

**Random Forest wins because:**
- Handles non-linear relationships (e.g., high LOC + low churn = third-party)
- No feature scaling required (saves preprocessing)
- Provides feature importance (explainability for auditors)
- Robust to overfitting (with proper hyperparameters)
- Fast training and inference (<1 second for typical codebases)

## Training Workflow

### Step 1: Bootstrap Training Data

Run audits on 5-10 repositories with **known IP status**:

```bash
forgetrace audit /path/to/repo1 --output-dir output1
forgetrace audit /path/to/repo2 --output-dir output2
# ... repeat for repos 3-10
```

### Step 2: Export Initial Labels

The classifier starts with rule-based heuristics (high confidence only):

```python
from forgetrace.classifiers import MLIPClassifier

classifier = MLIPClassifier(findings, config)
classifier.export_training_data("training_data.jsonl")
```

This creates:
```jsonl
{"features": {...}, "label": "foreground", "file_path": "src/main.py"}
{"features": {...}, "label": "third_party", "file_path": "vendor/lib.js"}
...
```

### Step 3: Human Review

Review and correct labels in `training_data.jsonl`:

```bash
# Open in text editor or use custom review tool
code training_data.jsonl

# Change incorrect labels
# Before: {"features": {...}, "label": "foreground", ...}
# After:  {"features": {...}, "label": "background", ...}
```

**Guidelines:**
- **third_party**: External dependencies (npm, PyPI, vendor/)
- **background**: Developer's prior work, personal projects
- **foreground**: Written specifically for this project
- **unknown**: Insufficient information (exclude from training)

### Step 4: Train Model

```bash
python -m forgetrace.classifiers.train_model training_data.jsonl
```

Output:
```
📂 Loading training data from training_data.jsonl
✅ Loaded 247 training examples

📊 Class Distribution:
   foreground: 142 (57.5%)
   third_party: 89 (36.0%)
   background: 16 (6.5%)

🔨 Training Random Forest classifier...
✅ Model trained successfully

📊 Evaluating model with 5-fold cross-validation...
Cross-validation Accuracy: 0.887 (+/- 0.034)

📈 Classification Report (Test Set):
              precision    recall  f1-score   support
  background       0.75      0.60      0.67         5
  foreground       0.91      0.94      0.93        35
third_party       0.95      0.89      0.92        18

🎯 Feature Importance:
   Top 10 Most Important Features:
   1. commit_count                   0.1872 ████████████████████
   2. author_count                   0.1543 ███████████████
   3. has_license_header             0.1201 ████████████
   4. cyclomatic_complexity          0.0987 ██████████
   ...

💾 Model saved to models/ip_classifier.pkl
✅ Training Complete!
```

### Step 5: Deploy Model

Update `config.yaml`:

```yaml
ml_classifier:
  enabled: true
  model_path: "models/ip_classifier.pkl"
  confidence_threshold: 0.7
```

### Step 6: Continuous Improvement

As you perform more audits:

1. **Export uncertain predictions** for human review
2. **Add corrected labels** to training dataset
3. **Retrain model** monthly/quarterly
4. **Track performance** over time

```bash
# Export uncertain predictions
forgetrace audit /path/to/repo --export-uncertain

# Human reviews uncertain_predictions.jsonl
# Append to training_data.jsonl

# Retrain with expanded dataset
python -m forgetrace.classifiers.train_model training_data.jsonl
```

## Configuration

### config.yaml Settings

```yaml
ml_classifier:
  # Enable/disable ML classification
  enabled: true
  
  # Path to trained model (relative to project root)
  model_path: "models/ip_classifier.pkl"
  
  # Confidence threshold for auto-classification (0.0-1.0)
  # High confidence (>threshold): Auto-classify, no review
  # Low confidence (<threshold): Flag for human review
  confidence_threshold: 0.7
  
  # Fallback to rule-based classification if ML unavailable
  fallback_to_rules: true
  
  # Company email domains (for external author detection)
  company_domains:
    - "company.com"
    - "yourorg.com"
  
  # Export low-confidence predictions for review
  export_uncertain: true
  training_data_path: "training_data.jsonl"
```

### Confidence Thresholds

| Threshold | High Conf (Auto) | Medium Conf (Flag) | Low Conf (Review) |
|-----------|------------------|---------------------|-------------------|
| 0.9 (Strict) | >90% | 70-90% | <70% |
| 0.7 (Balanced) | >70% | 50-70% | <50% |
| 0.5 (Permissive) | >50% | 30-50% | <30% |

**Recommendation**: Start with 0.7 (balanced) and adjust based on review workload.

## Feature Importance Analysis

After training, analyze which features most influence predictions:

```bash
python -m forgetrace.classifiers.train_model training_data.jsonl
```

Output:
```
🎯 Feature Importance:
   1. commit_count                   0.1872  (Most important)
   2. author_count                   0.1543
   3. has_license_header             0.1201
   4. cyclomatic_complexity          0.0987
   5. days_since_last_commit         0.0834
   6. primary_author_commit_ratio    0.0756
   7. path_depth                     0.0654
   8. max_similarity_score           0.0598
   ...
   ℹ️  Top 8 features account for 80% of decisions
```

### Interpretation

- **High importance (>0.10)**: Critical features, ensure data quality
- **Medium importance (0.05-0.10)**: Useful signals, monitor consistency
- **Low importance (<0.05)**: Consider removing (simplify model)

### Red Flags

⚠️ **file_path has high importance**: Model may be memorizing paths instead of learning patterns (overfitting)

⚠️ **All features have similar importance**: Model may be underfitting (too simple hyperparameters)

## Performance Benchmarks

### Training Data Requirements

| Examples | Accuracy | Recommendation |
|----------|----------|----------------|
| 50-100 | 60-70% | Minimum viable |
| 100-500 | 70-85% | Good |
| 500-1000 | 85-92% | Excellent |
| 1000+ | 90-95% | Production-ready |

### Inference Speed

- **Single file**: <1ms
- **1000 files**: ~50ms
- **10,000 files**: ~500ms

Bottleneck is feature extraction (file I/O, git operations), not ML inference.

## Troubleshooting

### Model not loading

**Error**: `⚠️  No trained model found at models/ip_classifier.pkl`

**Solution**: Train a model first:
```bash
python -m forgetrace.classifiers.train_model training_data.jsonl
```

### Low accuracy (<70%)

**Causes**:
1. Insufficient training data (<100 examples)
2. Class imbalance (90% foreground, 5% background, 5% third_party)
3. Poor feature quality (missing git history, no license detection)

**Solutions**:
1. Collect more labeled examples (target 500+)
2. Use `class_weight='balanced'` in Random Forest (automatic)
3. Improve scanner configuration (enable all scanners)

### Overfitting (high training accuracy, low test accuracy)

**Symptoms**:
- Training accuracy: 98%
- Test accuracy: 65%

**Causes**:
- Model memorizing training data
- Too complex hyperparameters (max_depth > 15)

**Solutions**:
1. Reduce `max_depth` to 5-10
2. Increase `min_samples_split` to 10-20
3. Collect more diverse training data

### Severe class imbalance

**Warning**: `⚠️  WARNING: Severe class imbalance (ratio 20:1)`

**Impact**: Model ignores minority classes (background IP)

**Solutions**:
1. **Collect more minority examples** (best approach)
2. **Oversample minority class** (SMOTE algorithm)
3. **Adjust class weights** (already automatic with `class_weight='balanced'`)

## Advanced Topics

### Custom Hyperparameters

Edit `train_model.py`:

```python
model = RandomForestClassifier(
    n_estimators=200,      # More trees (default: 100)
    max_depth=15,          # Deeper trees (default: 10)
    min_samples_split=10,  # More conservative splits (default: 5)
    class_weight='balanced',
    random_state=42,
    n_jobs=-1
)
```

**Guidelines**:
- **n_estimators**: 100-500 (diminishing returns after 200)
- **max_depth**: 5-15 (10 is good default)
- **min_samples_split**: 2-20 (higher = simpler model)

### Cross-Project Generalization

Train on **multiple different projects** to improve generalization:

```bash
# Audit diverse projects
forgetrace audit /path/to/python-project --export-training
forgetrace audit /path/to/javascript-project --export-training
forgetrace audit /path/to/java-project --export-training

# Combine training data
cat project1/training.jsonl project2/training.jsonl project3/training.jsonl > combined.jsonl

# Train on combined data
python -m forgetrace.classifiers.train_model combined.jsonl
```

### Model Versioning

Track model versions for A/B testing and rollback:

```bash
# Save with version number
python -m forgetrace.classifiers.train_model training_data.jsonl models/ip_classifier_v2.pkl

# Update config.yaml
ml_classifier:
  model_path: "models/ip_classifier_v2.pkl"

# Compare performance
forgetrace audit /test-repo --model-version v1 > results_v1.json
forgetrace audit /test-repo --model-version v2 > results_v2.json
diff results_v1.json results_v2.json
```

### Alternative Export Format (ONNX)

For production deployment, consider ONNX (safer than pickle):

```python
import onnxmltools
from skl2onnx import convert_sklearn

# Convert sklearn model to ONNX
onnx_model = convert_sklearn(
    model,
    initial_types=[('float_input', FloatTensorType([None, 19]))]
)

# Save ONNX model
with open("models/ip_classifier.onnx", "wb") as f:
    f.write(onnx_model.SerializeToString())
```

**Benefits**:
- Language-agnostic (can use from Node.js, Go, etc.)
- No pickle security concerns
- Smaller file size
- Faster inference (especially with ONNX Runtime)

## FAQ

### Q: How much training data do I need?

**A**: Minimum 100 examples, target 500+. Rule of thumb: 50 examples per class (foreground, background, third_party).

### Q: Can I use the model across different programming languages?

**A**: Yes! Features are language-agnostic (git history, file metadata). Train on mixed Python/JS/Java projects for best generalization.

### Q: What if I don't have labeled data?

**A**: Start with rule-based classification (automatic fallback). Export predictions, human reviews, then train ML model.

### Q: How often should I retrain?

**A**: Monthly for active development, quarterly for maintenance mode. Retrain when:
- Accuracy drops below 80%
- New project types added
- 100+ new labeled examples accumulated

### Q: Can I integrate with CI/CD?

**A**: Yes! Example GitHub Actions workflow:

```yaml
name: IP Audit
on: [push]
jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install ForgeTrace
        run: pip install forgetrace
      - name: Run Audit
        run: forgetrace audit . --fail-on-background
      - name: Upload Report
        uses: actions/upload-artifact@v3
        with:
          name: ip-audit-report
          path: output/
```

### Q: What about false positives?

**A**: ML classifier provides confidence scores. Low confidence predictions are flagged for human review. Adjust `confidence_threshold` to balance automation vs accuracy.

### Q: Can I add custom features?

**A**: Yes! Edit `ml_classifier.py` `FileFeatures` dataclass and `_extract_features()` method. Remember to update `train_model.py` feature order.

## References

- **COCOMO**: Cost estimation model - [Wikipedia](https://en.wikipedia.org/wiki/COCOMO)
- **Random Forest**: Breiman (2001) - [Paper](https://link.springer.com/article/10.1023/A:1010933404324)
- **Feature Engineering**: Zheng & Casari (2018) - *Feature Engineering for Machine Learning*
- **Class Imbalance**: Chawla et al. (2002) - SMOTE algorithm

## License

MIT License - See LICENSE file for details
