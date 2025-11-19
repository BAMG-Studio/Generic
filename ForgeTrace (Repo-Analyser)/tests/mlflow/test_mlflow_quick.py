"""Smoke test for the quick MLflow validation workflow without external servers."""

from __future__ import annotations

import pickle

import mlflow
from mlflow.tracking import MlflowClient
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split


def test_mlflow_quick_validation(tmp_path, mlflow_local_env) -> None:
    """Run a lightweight training/eval loop and ensure metrics + artifacts persist."""

    mlflow.set_tracking_uri(mlflow_local_env.tracking_uri)
    mlflow.set_registry_uri(mlflow_local_env.tracking_uri)
    mlflow.set_experiment("ForgeTrace-Quick-Test")

    X, y = make_classification(
        n_samples=600,
        n_features=24,
        n_informative=12,
        n_redundant=6,
        n_classes=3,
        random_state=42,
    )

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    with mlflow.start_run(run_name="quick_validation_test") as run:
        params = {"n_estimators": 80, "max_depth": 12, "min_samples_split": 5}
        mlflow.log_params(params)
        mlflow.log_param("test_type", "quick_validation")

        model = RandomForestClassifier(**params, random_state=42)
        model.fit(X_train, y_train)

        train_acc = accuracy_score(y_train, model.predict(X_train))
        test_acc = accuracy_score(y_test, model.predict(X_test))

        mlflow.log_metric("train_accuracy", float(train_acc))
        mlflow.log_metric("test_accuracy", float(test_acc))

        model_path = tmp_path / "model.pkl"
        with open(model_path, "wb") as f:
            pickle.dump(model, f)
        mlflow.log_artifact(str(model_path))

    client = MlflowClient(
        tracking_uri=mlflow_local_env.tracking_uri,
        registry_uri=mlflow_local_env.tracking_uri,
    )
    run_data = client.get_run(run.info.run_id)

    assert run_data.data.metrics["test_accuracy"] >= 0.6
    artifacts = client.list_artifacts(run.info.run_id)
    assert any(artifact.path.endswith("model.pkl") for artifact in artifacts)
