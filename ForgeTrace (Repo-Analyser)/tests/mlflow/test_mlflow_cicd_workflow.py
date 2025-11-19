"""CI/CD style MLflow test that validates quality gates offline."""

from __future__ import annotations

import mlflow
from mlflow.tracking import MlflowClient
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

QUALITY_GATES = {
    "min_test_accuracy": 0.6,
    "max_train_test_gap": 0.2,
}


def test_mlflow_cicd_workflow(mlflow_local_env) -> None:
    """Train, evaluate, and promote a model using a local SQLite-backed store."""

    mlflow.set_tracking_uri(mlflow_local_env.tracking_uri)
    mlflow.set_registry_uri(mlflow_local_env.tracking_uri)
    mlflow.set_experiment("ForgeTrace-CICD-Workflow")

    client = MlflowClient(
        tracking_uri=mlflow_local_env.tracking_uri,
        registry_uri=mlflow_local_env.tracking_uri,
    )

    X, y = make_classification(
        n_samples=1500,
        n_features=24,
        n_informative=16,
        n_redundant=4,
        n_classes=3,
        random_state=42,
    )
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    with mlflow.start_run(run_name="cicd_candidate_v1") as run:
        params = {"n_estimators": 120, "max_depth": 14, "random_state": 42}
        mlflow.log_params(params)

        model = RandomForestClassifier(**params)
        model.fit(X_train, y_train)

        train_acc = accuracy_score(y_train, model.predict(X_train))
        test_acc = accuracy_score(y_test, model.predict(X_test))

        mlflow.log_metric("train_accuracy", float(train_acc))
        mlflow.log_metric("test_accuracy", float(test_acc))

        mlflow.sklearn.log_model(
            model, "model", registered_model_name="ForgeTrace-CICD-Test"
        )

        run_id = run.info.run_id

    run_data = client.get_run(run_id)
    test_acc = run_data.data.metrics["test_accuracy"]
    train_acc = run_data.data.metrics["train_accuracy"]
    gap = abs(train_acc - test_acc)

    assert test_acc >= QUALITY_GATES["min_test_accuracy"]
    assert gap <= QUALITY_GATES["max_train_test_gap"]

    versions = client.search_model_versions("name='ForgeTrace-CICD-Test'")
    assert versions
    latest_version = versions[0]

    client.transition_model_version_stage(
        name=latest_version.name, version=latest_version.version, stage="Staging"
    )
    staged = client.get_model_version(
        name=latest_version.name, version=latest_version.version
    )

    assert staged.current_stage == "Staging"
