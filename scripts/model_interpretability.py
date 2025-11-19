#!/usr/bin/env python3
"""
Model Interpretability Tool

Generates SHAP-style explanations and decision tree visualizations
to understand model predictions.
"""

import json
import pickle
import sys
from pathlib import Path
from typing import Dict, List

import matplotlib.pyplot as plt
import numpy as np

# Add project root to path
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))


def load_model(model_path: str = "models/ip_classifier_rf.pkl") -> Dict:
    """Load the trained model."""
    with open(model_path, "rb") as f:
        return pickle.load(f)


def visualize_sample_tree(model_data: Dict, tree_index: int = 0, max_depth: int = 3):
    """Visualize a sample decision tree from the forest."""
    from sklearn.tree import plot_tree

    model = model_data["model"]
    feature_names = model_data["feature_names"]

    plt.figure(figsize=(20, 10))
    plot_tree(
        model.estimators_[tree_index],
        feature_names=feature_names,
        class_names=model.classes_,
        filled=True,
        max_depth=max_depth,
        fontsize=10,
    )
    plt.title(f"Decision Tree #{tree_index} (depth limited to {max_depth})", fontsize=14, fontweight="bold")
    plt.tight_layout()

    output_path = f"docs/decision_tree_{tree_index}.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"🌳 Saved decision tree visualization to {output_path}")


def explain_prediction(model_data: Dict, example: Dict) -> Dict:
    """Explain a single prediction using feature contributions."""
    model = model_data["model"]
    feature_names = model_data["feature_names"]

    # Build feature vector
    X = np.zeros((1, len(feature_names)))
    for idx, name in enumerate(feature_names):
        value = example["features"].get(name, 0.0)
        try:
            X[0, idx] = float(value)
        except (ValueError, TypeError):
            X[0, idx] = 0.0

    # Get prediction
    prediction = model.predict(X)[0]
    probabilities = model.predict_proba(X)[0]

    # Get feature importances for this prediction
    # (approximation: use global feature importance scaled by feature value)
    importances = model.feature_importances_
    contributions = []
    for idx, name in enumerate(feature_names):
        contrib = float(importances[idx] * X[0, idx])
        contributions.append({"feature": name, "value": float(X[0, idx]), "contribution": contrib})

    contributions.sort(key=lambda x: abs(x["contribution"]), reverse=True)

    return {
        "prediction": prediction,
        "confidence": {model.classes_[i]: float(prob) for i, prob in enumerate(probabilities)},
        "top_contributors": contributions[:10],
    }


def plot_prediction_explanation(explanation: Dict, file_path: str):
    """Visualize feature contributions for a prediction."""
    top_features = explanation["top_contributors"][:10]
    features = [item["feature"] for item in top_features]
    contributions = [item["contribution"] for item in top_features]

    plt.figure(figsize=(10, 6))
    colors = ["green" if c > 0 else "red" for c in contributions]
    plt.barh(features, contributions, color=colors)
    plt.xlabel("Contribution to Prediction", fontsize=12)
    plt.ylabel("Feature", fontsize=12)
    plt.title(
        f"Top Feature Contributions\nPrediction: {explanation['prediction']} (confidence: {explanation['confidence'][explanation['prediction']]:.2%})",
        fontsize=14,
        fontweight="bold",
    )
    plt.tight_layout()
    plt.savefig(file_path, dpi=300, bbox_inches="tight")
    print(f"📊 Saved prediction explanation to {file_path}")


def analyze_sample_predictions(model_data: Dict, dataset_path: str, n_samples: int = 5):
    """Analyze and explain sample predictions."""
    print("\n" + "=" * 70)
    print("  SAMPLE PREDICTION EXPLANATIONS")
    print("=" * 70 + "\n")

    with open(dataset_path, "r") as f:
        examples = [json.loads(line) for line in f]

    # Sample from each class
    classes = {}
    for example in examples:
        label = example["label"]
        if label not in classes:
            classes[label] = []
        classes[label].append(example)

    for label, label_examples in classes.items():
        if label_examples:
            example = label_examples[0]
            print(f"\n📄 Example: {example.get('file_path', 'unknown')}")
            print(f"   Actual Label: {example['label']}")

            explanation = explain_prediction(model_data, example)
            print(f"   Predicted: {explanation['prediction']}")
            print(f"   Confidence: {explanation['confidence'][explanation['prediction']]:.2%}")

            print("\n   Top Contributing Features:")
            for item in explanation["top_contributors"][:5]:
                print(f"      {item['feature']:30s} = {item['value']:10.2f} (contrib: {item['contribution']:.4f})")

            # Save visualization
            output_path = f"docs/explanation_{label}.png"
            plot_prediction_explanation(explanation, output_path)


def main():
    """Main interpretability workflow."""
    print("=" * 70)
    print("  MODEL INTERPRETABILITY ANALYSIS")
    print("=" * 70)

    # Load model
    print("\n📦 Loading trained model...")
    model_data = load_model()
    print(f"✅ Loaded Random Forest with {len(model_data['model'].estimators_)} trees\n")

    # Create docs directory
    Path("docs").mkdir(exist_ok=True)

    # 1. Visualize sample decision trees
    print("=" * 70)
    print("  1. VISUALIZING SAMPLE DECISION TREES")
    print("=" * 70 + "\n")

    for i in [0, 1, 2]:
        visualize_sample_tree(model_data, tree_index=i, max_depth=3)

    # 2. Explain sample predictions
    analyze_sample_predictions(model_data, "training_output/dataset/training_dataset.jsonl")

    print("\n" + "=" * 70)
    print("  ✅ INTERPRETABILITY ANALYSIS COMPLETE")
    print("=" * 70 + "\n")

    print("📌 Generated Artifacts:")
    print("  • docs/decision_tree_*.png - Sample decision tree visualizations")
    print("  • docs/explanation_*.png - Feature contribution explanations by class")
    print("\n💡 Next Steps:")
    print("  1. Review decision trees to understand model logic")
    print("  2. Validate that top features align with domain knowledge")
    print("  3. Use explanations to build trust with stakeholders")


if __name__ == "__main__":
    main()
