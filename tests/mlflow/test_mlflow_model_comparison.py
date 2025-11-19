"""Regression test that logs multiple model candidates to a local MLflow store."""

from __future__ import annotations

import mlflow
import numpy as np
from mlflow.tracking import MlflowClient
from sklearn.datasets import make_classification
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import cross_val_score, train_test_split


def test_mlflow_model_comparison(mlflow_local_env) -> None:
    """Ensure each candidate model logs metrics and that one exceeds the threshold."""

    mlflow.set_tracking_uri(mlflow_local_env.tracking_uri)
    mlflow.set_registry_uri(mlflow_local_env.tracking_uri)
    mlflow.set_experiment("ForgeTrace-Model-Comparison")

    X, y = make_classification(
        n_samples=1200,
        n_features=24,
        n_informative=14,
        n_redundant=4,
        n_classes=3,
        random_state=7,
    )
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=7
    )

    models_to_test = [
        (
            "RandomForest_100trees",
            RandomForestClassifier(n_estimators=100, max_depth=12, random_state=7),
        ),
        (
            "RandomForest_200trees",
            RandomForestClassifier(n_estimators=200, max_depth=12, random_state=7),
        ),
        (
            "GradientBoosting",
            GradientBoostingClassifier(n_estimators=120, max_depth=3, random_state=7),
        ),
        (
            "LogisticRegression",
            LogisticRegression(max_iter=500, multi_class="multinomial", random_state=7),
        ),
    ]

    client = MlflowClient(tracking_uri=mlflow_local_env.tracking_uri)
    run_ids = []

    for name, model in models_to_test:
        with mlflow.start_run(run_name=name) as run:
            mlflow.log_param("model_type", name)
            for param, value in model.get_params().items():
                if isinstance(value, (int, float, str)):
                    mlflow.log_param(param, value)

            model.fit(X_train, y_train)
            train_acc = accuracy_score(y_train, model.predict(X_train))
            test_acc = accuracy_score(y_test, model.predict(X_test))
            cv_scores = cross_val_score(model, X_train, y_train, cv=3)

            mlflow.log_metric("train_accuracy", float(train_acc))
            mlflow.log_metric("test_accuracy", float(test_acc))
            mlflow.log_metric("cv_mean_accuracy", float(np.mean(cv_scores)))
            mlflow.log_metric("cv_std_accuracy", float(np.std(cv_scores)))

            mlflow.sklearn.log_model(model, "model")
            run_ids.append(run.info.run_id)

    test_accuracies = [
        client.get_run(run_id).data.metrics["test_accuracy"] for run_id in run_ids
    ]

    assert len(test_accuracies) == len(models_to_test)
    assert max(test_accuracies) >= 0.55
