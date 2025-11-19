"""End-to-end MLflow test that mimics ForgeTrace feature engineering."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import mlflow
import numpy as np
import pandas as pd
import seaborn as sns
from mlflow.tracking import MlflowClient
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    precision_recall_fscore_support,
)
from sklearn.model_selection import train_test_split

matplotlib.use("Agg")


def _generate_forgetrace_features(
    n_samples: int = 1500, seed: int = 42
) -> tuple[pd.DataFrame, np.ndarray]:
    """Generate synthetic ForgeTrace-like feature matrix and imbalanced labels."""

    rng = np.random.default_rng(seed)
    feature_map: dict[str, np.ndarray] = {
        "template_indicator": rng.beta(2, 5, n_samples),
        "language_entropy": rng.gamma(3, 1, n_samples),
        "external_import_ratio": rng.beta(3, 2, n_samples),
        "import_count": rng.poisson(12, n_samples),
        "nesting_depth": rng.poisson(4, n_samples),
        "comment_ratio": rng.beta(2, 8, n_samples),
        "code_to_text_ratio": rng.gamma(5, 0.2, n_samples),
        "function_count": rng.poisson(6, n_samples),
        "class_count": rng.poisson(2, n_samples),
        "log_lines_of_code": rng.normal(5, 1.2, n_samples),
        "spdx_header_present": rng.binomial(1, 0.3, n_samples),
        "permissive_license": rng.binomial(1, 0.4, n_samples),
        "secret_risk_score": rng.beta(1, 10, n_samples),
    }

    for idx in range(13, 30):
        feature_map[f"feature_{idx}"] = rng.normal(0, 1, n_samples)

    labels = rng.choice(
        [0, 1, 2], size=n_samples, p=[0.02, 0.1, 0.88]
    )  # background, foreground, third_party

    return pd.DataFrame(feature_map), labels


def test_mlflow_forgetrace_feature_pipeline(tmp_path, mlflow_local_env) -> None:
    """Ensure the simulated feature workflow logs metrics, charts, and artifacts."""

    mlflow.set_tracking_uri(mlflow_local_env.tracking_uri)
    mlflow.set_registry_uri(mlflow_local_env.tracking_uri)
    mlflow.set_experiment("ForgeTrace-Feature-Simulation")

    X, y = _generate_forgetrace_features()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    class_counts = {
        "background": int(np.sum(y == 0)),
        "foreground": int(np.sum(y == 1)),
        "third_party": int(np.sum(y == 2)),
    }

    confusion_path = tmp_path / "confusion_matrix.png"
    importance_csv = tmp_path / "feature_importance.csv"
    importance_plot = tmp_path / "feature_importance_plot.png"

    with mlflow.start_run(run_name="forgetrace_feature_test_v1") as run:
        mlflow.log_param("train_size", len(X_train))
        mlflow.log_param("test_size", len(X_test))
        mlflow.log_param("feature_count", X.shape[1])
        mlflow.log_param("class_distribution", json.dumps(class_counts))

        params = {
            "n_estimators": 120,
            "max_depth": 14,
            "min_samples_split": 8,
            "class_weight": "balanced_subsample",
        }
        mlflow.log_params(params)

        model = RandomForestClassifier(**params, random_state=42)
        model.fit(X_train, y_train)

        y_train_pred = model.predict(X_train)
        y_test_pred = model.predict(X_test)

        train_acc = accuracy_score(y_train, y_train_pred)
        test_acc = accuracy_score(y_test, y_test_pred)
        mlflow.log_metric("train_accuracy", float(train_acc))
        mlflow.log_metric("test_accuracy", float(test_acc))

        class_names = ["background", "foreground", "third_party"]
        precision, recall, f1, support = precision_recall_fscore_support(
            y_test, y_test_pred, labels=[0, 1, 2]
        )
        for idx, label in enumerate(class_names):
            mlflow.log_metric(f"{label}_precision", float(precision[idx]))
            mlflow.log_metric(f"{label}_recall", float(recall[idx]))
            mlflow.log_metric(f"{label}_f1", float(f1[idx]))
            mlflow.log_metric(f"{label}_support", float(support[idx]))

        cm = confusion_matrix(y_test, y_test_pred)
        plt.figure(figsize=(8, 6))
        sns.heatmap(
            cm,
            annot=True,
            fmt="d",
            cmap="Blues",
            xticklabels=class_names,
            yticklabels=class_names,
        )
        plt.title("ForgeTrace Classification Confusion Matrix")
        plt.ylabel("Actual")
        plt.xlabel("Predicted")
        plt.tight_layout()
        plt.savefig(confusion_path, dpi=150)
        mlflow.log_artifact(str(confusion_path))

        feature_importance = (
            pd.DataFrame(
                {"feature": X.columns, "importance": model.feature_importances_}
            )
            .sort_values("importance", ascending=False)
            .reset_index(drop=True)
        )
        feature_importance.to_csv(importance_csv, index=False)
        mlflow.log_artifact(str(importance_csv))

        plt.figure(figsize=(10, 5))
        top_10 = feature_importance.head(10)
        plt.barh(top_10["feature"], top_10["importance"])
        plt.xlabel("Importance")
        plt.title("Top 10 Feature Importance")
        plt.tight_layout()
        plt.savefig(importance_plot, dpi=150)
        mlflow.log_artifact(str(importance_plot))

        mlflow.sklearn.log_model(model, "model")

    client = MlflowClient(tracking_uri=mlflow_local_env.tracking_uri)
    run_data = client.get_run(run.info.run_id)

    assert run_data.data.metrics["test_accuracy"] >= 0.5
    assert confusion_path.exists()
    assert importance_csv.exists()
