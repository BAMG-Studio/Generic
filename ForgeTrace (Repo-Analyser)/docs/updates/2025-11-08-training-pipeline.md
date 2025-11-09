# 2025-11-08 Training Pipeline Update

## Training Dataset Regeneration

- Ran `python3 scripts/run_training_pipeline.py` to rebuild the full corpus.
- Produced 131,906 labeled examples with phase counts: `FOUNDATIONAL=7,083`, `POLYGLOT=116,407`, `SECURITY=5,733`, `ENTERPRISE=1,282`, `RESEARCH=1,401`.
- Label distribution: `foreground=12,278`, `third_party=117,428`, `background=2,200`.

## Random Forest Retraining

- Trained via `python3 scripts/train_random_forest.py training_output/dataset/training_dataset.jsonl` using the refreshed dataset.
- Feature schema now tracks 53 signals, including repository-level vulnerability metrics.
- Achieved 99.9% test accuracy with per-class precision/recall ≥ 0.99; 5-fold cross-validation mean accuracy 0.999 (±0.000).
- Exported model stored at `models/ip_classifier_rf.pkl` (≈2.9 MB).

## Smoke Validation

- Verified CLI integration with `python3 scripts/run_sample_audit.py`.
- Audit completed successfully, loading the new classifier without errors and emitting artifacts under `sample_audit/`.
- Vulnerability scan within the sample audit scanned two dependencies and respected the current OSV/GitHub advisory filters.
