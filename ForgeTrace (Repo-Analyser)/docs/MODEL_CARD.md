# ForgeTrace ML Model Card

**Model Version:** 2025.11.08  
**Training Date:** November 8, 2025  
**Model Type:** Random Forest Classifier  
**Framework:** scikit-learn 1.5.2

---

## Model Overview

### Purpose
Automated classification of code files into three intellectual property categories:
- **foreground**: Core business logic and custom implementations (target IP)
- **third_party**: External libraries, frameworks, and dependencies
- **background**: Generated code, build artifacts, configurations

### Intended Use Cases
1. M&A due diligence: Quantify proprietary IP in acquisition targets
2. Code audit reporting: Generate executive summaries of codebase composition
3. License compliance: Identify third-party code requiring attribution
4. Rewrite cost estimation: Prioritize replacement of critical IP components

### Out-of-Scope Uses
- Real-time classification during development (not optimized for latency)
- Legal determination of copyright ownership (requires human review)
- Detection of license violations (complementary to, not replacement for, license scanners)

---

## Training Data

### Dataset Composition
- **Total Examples:** 131,906 labeled code files
- **Source:** 54 curated open-source projects across 5 phases
- **Label Distribution:**
  - `third_party`: 117,428 (89.0%)
  - `foreground`: 12,278 (9.3%)
  - `background`: 2,200 (1.7%)

### Data Sources by Phase
| Phase        | Repositories | Examples | Focus                              |
|--------------|--------------|----------|------------------------------------|
| FOUNDATIONAL | 7            | 7,083    | Core Python frameworks (Django, Flask, FastAPI) |
| POLYGLOT     | 20           | 116,407  | Multi-language compilers/runtimes (LLVM, CPython, Rust, Go) |
| SECURITY     | 12           | 5,733    | Security tools (Snyk, Trivy, Syft) |
| ENTERPRISE   | 10           | 1,282    | Enterprise platforms (GitLab, Metabase, Grafana) |
| RESEARCH     | 5            | 1,401    | ML/AI frameworks (PyTorch, DeepSpeed, TensorFlow Lite) |

### Feature Schema (53 Features)
#### Structural Features
- `lines_of_code`, `file_size_bytes`, `path_depth`, `avg_line_length`, `nesting_depth`

#### Code Complexity
- `comment_ratio`, `code_to_text_ratio`, `sample_entropy`, `language_entropy`

#### Import/Dependency Analysis
- `import_count`, `external_import_ratio`, `stdlib_import_ratio`, `module_depth_score`

#### Path & Naming Indicators
- `template_indicator`, `config_indicator`, `sbom_indicator`, `manifest_indicator`
- `vendor_path_indicator`, `is_test_path`, `is_docs_path`

#### License & Legal
- `spdx_header_present`, `has_spdx_header`, `license_keyword_hits`, `permissive_license_indicator`

#### Security Features
- `secret_risk_score`, `credential_keyword_density`, `secret_pattern_hits`
- `sensitive_assignment_hits`, `high_entropy_literal_ratio`, `private_key_indicator`

#### Domain-Specific Indicators
- `data_access_indicator`, `api_endpoint_count`, `async_processing_indicator`
- `orchestration_signal`, `plugin_registration_hits`

#### Research/Academic
- `citation_count`, `paper_reference_hits`, `figure_mentions`, `dataset_mentions`
- `experiment_path_indicator`, `experiment_config_indicator`, `methodology_indicator`, `abstract_indicator`

#### Business Context
- `framework_keyword_hits`, `framework_mentions`, `business_context_density`, `metric_mentions`

#### Repository-Level Vulnerability Metrics
- `repo_vulnerability_count`, `repo_vuln_density`, `repo_vuln_weighted_score`, `repo_osv_noise_ratio`

**Note:** Vulnerability metrics are currently non-functional (all zeros in training data) and contribute 0% to model decisions.

---

## Model Architecture

### Hyperparameters
```python
RandomForestClassifier(
    n_estimators=100,        # Number of decision trees
    max_depth=15,            # Maximum tree depth
    min_samples_split=10,    # Min samples to split internal node
    class_weight='balanced', # Automatic class imbalance correction
    random_state=42,         # Reproducibility seed
    n_jobs=-1                # Parallel tree construction
)
```

### Model Size
- **File Size:** 2.89 MB
- **Decision Nodes:** ~34,026 across 100 trees
- **Average Tree Depth:** ~15 levels

---

## Performance Metrics

### Overall Accuracy
- **Training Accuracy:** 100.0%
- **Test Accuracy:** 99.9%
- **Cross-Validation (5-fold):** 99.9% ± 0.03%

### Per-Class Performance (Test Set)
| Class        | Precision | Recall | F1-Score | Support |
|--------------|-----------|--------|----------|---------|
| background   | 0.991     | 1.000  | 0.995    | 440     |
| foreground   | 0.995     | 1.000  | 0.997    | 2,456   |
| third_party  | 1.000     | 0.999  | 1.000    | 23,486  |

**Weighted Avg:** Precision=0.999, Recall=0.999, F1=0.999

### Confusion Matrix (Test Set)
```
                Predicted
                bg      fg      tp
Actual  bg      440      0       0
        fg        1   2455       0
        tp        3     12   23471
```

### Feature Importance (Top 10)
1. `template_indicator` (16.43%)
2. `language_entropy` (13.92%)
3. `external_import_ratio` (11.02%)
4. `import_count` (10.24%)
5. `nesting_depth` (8.82%)
6. `sample_entropy` (5.45%)
7. `citation_count` (4.74%)
8. `module_depth_score` (4.52%)
9. `code_to_text_ratio` (3.46%)
10. `comment_ratio` (2.84%)

**Top 10 features account for 81.4% of classification decisions.**

---

## Known Limitations

### 1. Class Imbalance
- Training data is heavily skewed toward `third_party` (89%)
- Model may underperform on rare `background` examples in production
- Mitigation: `class_weight='balanced'` applied during training

### 2. Non-Functional Features
- Repository-level vulnerability metrics contribute 0% importance
- 22 features show <0.1% importance and are candidates for removal
- 43 features have >90% zero values, limiting their utility

### 3. Domain Specificity
- Trained primarily on Python, C++, JavaScript, Go, Rust codebases
- May not generalize well to niche languages (e.g., COBOL, Fortran, Erlang)
- Performance on proprietary codebases may differ from open-source training data

### 4. Feature Scaling
- Features like `lines_of_code` and `file_size_bytes` exhibit high variance (std >1000)
- No normalization applied; Random Forest is robust but transformations may improve performance

### 5. Temporal Validity
- Model reflects code patterns as of November 2025
- New frameworks, coding styles, or security practices may reduce accuracy over time
- Recommend retraining quarterly with updated examples

---

## Ethical Considerations

### Bias & Fairness
- Training data sourced exclusively from public GitHub/GitLab repositories
- May exhibit bias toward Western open-source development practices
- Underrepresents proprietary enterprise code patterns

### Privacy & Security
- Model does not store or memorize specific code snippets
- Feature extraction is statistical; no verbatim code copying occurs
- Ensure audit targets consent to automated classification

### Transparency
- Feature importances and decision tree visualizations available for inspection
- Prediction confidence scores provided to flag uncertain classifications
- Human review recommended for high-stakes decisions (e.g., IP valuations >$1M)

---

## Monitoring & Maintenance

### Production Metrics to Track
1. **Confidence Distribution:** Monitor % of predictions below 70% confidence threshold
2. **Class Drift:** Track ratio of foreground/third_party/background over time
3. **Feature Drift:** Alert on significant shifts in feature value distributions
4. **Disagreement Rate:** Measure human override frequency for low-confidence predictions

### Retraining Triggers
- Quarterly schedule (every 3 months)
- Confidence drops below 80% on validation set
- >10% human override rate on production predictions
- Introduction of new programming languages or frameworks

### Feedback Loop
- Export uncertain predictions (`confidence < 0.7`) to `training_data.jsonl`
- Solicit human labels for exported examples
- Append corrected examples to training dataset
- Retrain model when >1,000 new labeled examples accumulated

---

## Deployment Recommendations

### Infrastructure
- **Model Storage:** Version-controlled artifact repository (e.g., MLflow, AWS S3)
- **Inference Environment:** Python 3.12+, scikit-learn 1.5.2, 512MB RAM minimum
- **Throughput:** ~1ms per file classification (single-threaded)

### Integration Points
1. **CLI Tool:** `forgetrace audit <repo> --use-ml`
2. **Python API:** `from forgetrace.classifiers import MLClassifier`
3. **Batch Processing:** Process entire repositories in parallel

### Versioning Strategy
- Semantic versioning: `YYYY.MM.DD.PATCH`
- Tag models with training dataset hash for reproducibility
- Maintain backward compatibility for feature schema changes

---

## References

### Model Training Script
- `scripts/train_random_forest.py`
- `scripts/run_training_pipeline.py`

### Analysis Tools
- `scripts/analyze_feature_importance.py`
- `scripts/model_interpretability.py`

### Documentation
- `docs/ML_CLASSIFIER.md` - Feature descriptions
- `docs/VULNERABILITY_SCANNING.md` - Vulnerability metric details
- `docs/updates/2025-11-08-training-pipeline.md` - Training run log

---

**Contact:** Peter Kolawole, BAMG Studio LLC  
**Last Updated:** November 8, 2025
