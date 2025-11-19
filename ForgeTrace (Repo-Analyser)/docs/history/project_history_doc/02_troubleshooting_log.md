# Troubleshooting & Incident Log

This log captures notable debugging sessions so future responders can apply proven fixes quickly.

## 1. Type Checker Regressions (May 2024)

- **Symptom:** `mypy` flagged hundreds of `Any` leaks across scanners.
- **Root Cause:** Dynamic attribute injection plus optional dependencies without explicit stubs.
- **Resolution:**
  1. Introduced dedicated helper types in `forgetrace/utils/typing.py`.
  2. Added `typing.TYPE_CHECKING` imports for heavy dependencies (e.g., GitPython) to keep runtime lean.
  3. Extended `tests/conftest.py` fixtures to return fully typed objects.
- **Verification:** `mypy forgetrace tests` returns success in CI.

## 2. Unsafe Serialization (June 2024)

- **Symptom:** Bandit flagged `pickle.load` usage inside model loader.
- **Root Cause:** Legacy pipeline serialized RandomForest models with pickle.
- **Resolution:** Swapped to `joblib` with explicit trusted model directory and version suffixes.
- **Verification Commands:**

  ```bash
  bandit -q -r forgetrace
  python scripts/train_random_forest.py --persist models/forgetrace_rf.joblib
  ```
- **Follow-up:** Documented BLAKE2 integrity check so CI validates artifacts before inference.

## 3. MLflow Tests Flaking (September 2024)

- **Symptom:** `tests/mlflow` suite failed outside developer machine because it expected a running tracking server.
- **Root Cause:** Tests relied on environment variables that pointed to production-like services.
- **Resolution:** Created `MlflowTestEnv` fixture in `tests/conftest.py` that spins up temporary SQLite URIs plus artifact directories under `tmp_path`.
- **Expected Behavior:** Every test now calls `mlflow.set_tracking_uri(mlflow_local_env.tracking_uri)` so runs never escape the sandbox.
- **Commands:**

  ```bash
  pytest tests/mlflow/test_mlflow_quick.py -q
  pytest tests/mlflow -m "not slow"
  ```

## 4. Safety Scan Blocking Release (October 2024 – present)

- **Symptom:** `safety check` reports eight MLflow CVEs.
- **Root Cause:** Upstream MLflow 3.6.0 vulnerability batch affecting artifact handling and API endpoints.
- **Mitigation:**
  - Locked MLflow to 3.6.0, enforced network isolation, and routed all access through nginx basic auth.
  - Added `config/mlflow_release.yaml` to track status + `docs/MLFLOW_UPGRADE_PLAYBOOK.md` for upgrade choreography.
  - Authenticated CI/CD token to restrict artifact uploads.
- **Verification:**

  ```bash
  safety check --full-report
  docker-compose up -d mlflow && curl -sf http://localhost:5000/health
  ```

## 5. PDF Report Rendering Failures (Historical)

- **Symptom:** WeasyPrint crashes on certain audit reports.
- **Root Cause:** Missing font packages and out-of-date Cairo libraries on developer laptops.
- **Resolution:** Documented optional dependency install path plus containerized render fallback.
- **Command Snippet:**

  ```bash
  pip install weasyprint>=59.0
  python -m weasyprint sample_audit/executive_summary.html sample_audit/executive_summary.pdf
  ```

## 6. Future Troubleshooting Template

When a new incident occurs, record the following in this file:

1. **Symptom & timestamps** (link to CI job IDs if relevant).
2. **Impact radius** (tests, environments, customers).
3. **Instrumentation consulted** (logs, metrics, tracing).
4. **Resolution steps** with copy-pastable commands.
5. **Regression tests** to keep running over time.

Treat this as the single source of truth for "what went wrong" narratives.
