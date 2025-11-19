#!/usr/bin/env python3
"""
Feature Importance Analysis Script

Analyzes the trained Random Forest model to identify:
1. Low-importance features that could be removed
2. Feature scaling/transformation opportunities
3. Potential feature engineering improvements
"""

import pickle
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.preprocessing import StandardScaler

# Add project root to path
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))


def load_model(model_path: str = "models/ip_classifier_rf.pkl") -> Dict:
    """Load the trained model and feature names."""
    with open(model_path, "rb") as f:
        model_data = pickle.load(f)
    return model_data


def analyze_feature_distribution(
    model_data: Dict, dataset_path: str = "training_output/dataset/training_dataset.jsonl"
) -> Dict[str, Dict]:
    """Analyze distribution of feature values."""
    import json

    feature_names = model_data["feature_names"]
    feature_values = {name: [] for name in feature_names}

    with open(dataset_path, "r") as f:
        for line in f:
            example = json.loads(line)
            for name in feature_names:
                value = example["features"].get(name, 0.0)
                try:
                    feature_values[name].append(float(value))
                except (ValueError, TypeError):
                    feature_values[name].append(0.0)

    # Calculate statistics
    stats = {}
    for name, values in feature_values.items():
        arr = np.array(values)
        stats[name] = {
            "mean": float(np.mean(arr)),
            "std": float(np.std(arr)),
            "min": float(np.min(arr)),
            "max": float(np.max(arr)),
            "median": float(np.median(arr)),
            "zeros": int(np.sum(arr == 0)),
            "non_zeros": int(np.sum(arr != 0)),
        }

    return stats


def plot_feature_importance(
    feature_names: List[str],
    importances: np.ndarray,
    output_path: str = "docs/feature_importance.png",
) -> None:
    """Generate feature importance visualization."""
    # Sort by importance
    indices = np.argsort(importances)[::-1][:20]  # Top 20
    top_features = [feature_names[i] for i in indices]
    top_importances = importances[indices]

    # Create plot
    plt.figure(figsize=(12, 8))
    sns.barplot(x=top_importances, y=top_features, palette="viridis")
    plt.xlabel("Importance Score", fontsize=12)
    plt.ylabel("Feature", fontsize=12)
    plt.title("Top 20 Most Important Features", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"📊 Saved feature importance plot to {output_path}")


def identify_low_importance_features(
    feature_names: List[str], importances: np.ndarray, threshold: float = 0.001
) -> List[Tuple[str, float]]:
    """Identify features with importance below threshold."""
    low_importance = []
    for name, importance in zip(feature_names, importances):
        if importance < threshold:
            low_importance.append((name, importance))
    return sorted(low_importance, key=lambda x: x[1])


def suggest_feature_engineering(stats: Dict[str, Dict]) -> List[str]:
    """Suggest feature engineering improvements based on distribution."""
    suggestions = []

    for name, stat in stats.items():
        # High percentage of zeros
        zero_pct = stat["zeros"] / (stat["zeros"] + stat["non_zeros"]) * 100
        if zero_pct > 90:
            suggestions.append(
                f"⚠️  {name}: {zero_pct:.1f}% zeros - consider binary indicator or removal"
            )

        # High variance (might need scaling)
        if stat["std"] > 100 and stat["max"] > 1000:
            suggestions.append(
                f"📐 {name}: High variance (std={stat['std']:.1f}) - consider log transformation or scaling"
            )

        # All zeros
        if stat["non_zeros"] == 0:
            suggestions.append(f"🔴 {name}: All zeros - safe to remove")

        # Very low variance
        if stat["std"] < 0.01 and stat["non_zeros"] > 0:
            suggestions.append(
                f"⚪ {name}: Very low variance (std={stat['std']:.4f}) - limited discriminative power"
            )

    return suggestions


def analyze_feature_correlations(
    dataset_path: str, feature_names: List[str], output_path: str = "docs/feature_correlation.png"
) -> None:
    """Generate feature correlation heatmap."""
    import json

    # Load features into matrix
    X = []
    with open(dataset_path, "r") as f:
        for i, line in enumerate(f):
            if i >= 10000:  # Subsample for performance
                break
            example = json.loads(line)
            row = []
            for name in feature_names:
                value = example["features"].get(name, 0.0)
                try:
                    row.append(float(value))
                except (ValueError, TypeError):
                    row.append(0.0)
            X.append(row)

    X = np.array(X)

    # Compute correlation matrix
    corr_matrix = np.corrcoef(X.T)

    # Plot heatmap (top features only)
    plt.figure(figsize=(14, 12))
    top_n = 20
    sns.heatmap(
        corr_matrix[:top_n, :top_n],
        xticklabels=feature_names[:top_n],
        yticklabels=feature_names[:top_n],
        annot=False,
        cmap="coolwarm",
        center=0,
        vmin=-1,
        vmax=1,
    )
    plt.title(f"Feature Correlation Matrix (Top {top_n} Features)", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"📊 Saved correlation heatmap to {output_path}")


def main():
    """Main analysis workflow."""
    print("=" * 70)
    print("  FEATURE ENGINEERING ANALYSIS")
    print("=" * 70)

    # Load model
    print("\n📦 Loading trained model...")
    model_data = load_model()
    model = model_data["model"]
    feature_names = model_data["feature_names"]
    importances = model.feature_importances_

    print(f"✅ Loaded model with {len(feature_names)} features\n")

    # 1. Feature Importance Analysis
    print("=" * 70)
    print("  1. FEATURE IMPORTANCE RANKING")
    print("=" * 70 + "\n")

    sorted_idx = np.argsort(importances)[::-1]
    print("Top 15 Most Important Features:")
    print("-" * 70)
    for i, idx in enumerate(sorted_idx[:15], 1):
        print(f"{i:2d}. {feature_names[idx]:35s} {importances[idx]:.4f}")

    # 2. Low-Importance Features
    print("\n" + "=" * 70)
    print("  2. LOW-IMPORTANCE FEATURES (< 0.1%)")
    print("=" * 70 + "\n")

    low_features = identify_low_importance_features(feature_names, importances, threshold=0.001)
    if low_features:
        print(f"Found {len(low_features)} features with importance < 0.1%:\n")
        for name, importance in low_features[:10]:
            print(f"  • {name:35s} {importance:.6f}")
        print(f"\n💡 Consider removing these features to simplify the model")
    else:
        print("✅ All features have importance >= 0.1%")

    # 3. Feature Distribution Analysis
    print("\n" + "=" * 70)
    print("  3. FEATURE DISTRIBUTION ANALYSIS")
    print("=" * 70 + "\n")

    print("Analyzing feature distributions from training dataset...")
    stats = analyze_feature_distribution(model_data)

    print("\nFeatures with High Zero Percentage (>90%):")
    print("-" * 70)
    zero_heavy = [(name, stat) for name, stat in stats.items() if stat["zeros"] / (stat["zeros"] + stat["non_zeros"]) > 0.9]
    for name, stat in sorted(zero_heavy, key=lambda x: x[1]["zeros"] / (x[1]["zeros"] + x[1]["non_zeros"]), reverse=True)[
        :10
    ]:
        zero_pct = stat["zeros"] / (stat["zeros"] + stat["non_zeros"]) * 100
        print(f"  • {name:35s} {zero_pct:.1f}% zeros")

    # 4. Feature Engineering Suggestions
    print("\n" + "=" * 70)
    print("  4. FEATURE ENGINEERING SUGGESTIONS")
    print("=" * 70 + "\n")

    suggestions = suggest_feature_engineering(stats)
    if suggestions:
        for suggestion in suggestions[:15]:
            print(f"  {suggestion}")
    else:
        print("✅ No immediate feature engineering suggestions")

    # 5. Generate Visualizations
    print("\n" + "=" * 70)
    print("  5. GENERATING VISUALIZATIONS")
    print("=" * 70 + "\n")

    Path("docs").mkdir(exist_ok=True)

    plot_feature_importance(feature_names, importances)
    analyze_feature_correlations("training_output/dataset/training_dataset.jsonl", feature_names)

    # 6. Summary & Recommendations
    print("\n" + "=" * 70)
    print("  6. SUMMARY & RECOMMENDATIONS")
    print("=" * 70 + "\n")

    print("Key Findings:")
    print(f"  • Total Features: {len(feature_names)}")
    print(f"  • Low-Importance Features (<0.1%): {len(low_features)}")
    print(f"  • Features with >90% zeros: {len(zero_heavy)}")

    print("\n📌 Next Steps:")
    print("  1. Review low-importance features for potential removal")
    print("  2. Consider log transformation for high-variance features")
    print("  3. Experiment with feature interactions (e.g., ratio features)")
    print("  4. Investigate why repo_vuln_* features have 0% importance")
    print("  5. Try StandardScaler or MinMaxScaler on numeric features")

    print("\n✅ Analysis complete! Check docs/ for visualizations.\n")


if __name__ == "__main__":
    main()
