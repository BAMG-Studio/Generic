"""
Classifiers module - Author: Peter

WHAT: IP classification algorithms for code origin detection
WHY: Distinguish third-party, background, and foreground IP

MODULES:
- ip_classifier: Legacy rule-based classifier (backward compatible)
- ml_classifier: ML-based classifier with Random Forest
- train_model: Training script for ML model

USAGE:
    from forgetrace.classifiers import IPClassifier

    classifier = IPClassifier(findings, config)
    classifications = classifier.classify()

The IPClassifier automatically uses ML if:
1. ML libraries (sklearn, numpy) are installed
2. Trained model exists at config.ml_classifier.model_path
3. config.ml_classifier.enabled = True

Otherwise, falls back to rule-based classification.
"""

from .ml_classifier import IPClassifier, MLIPClassifier

__all__ = ["IPClassifier", "MLIPClassifier"]
