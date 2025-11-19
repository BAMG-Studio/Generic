# Toolchain & Decision Log

## Overview

ForgeTrace blends security scanning, ML experimentation, and deployment automation. This document records why we chose specific tools, which alternatives were considered, and how to operate each component.

## Scanners

| Capability | Current Tool | Replaced Tool | Why it Stuck |
|------------|--------------|---------------|--------------|
| Git history diffing | `gitpython` | Shell-only wrappers | Native object model + cross-platform support. |
| License detection | SPDX handcrafted rules | `licensecheck` | Greater control over custom allowlists. |
| SBOM parsing | `cyclonedx-python-lib` | Raw JSON parsing | Handles spec updates faster. |
| Secrets scanning | Custom regex bundle | TruffleHog CLI | Fewer false positives + inline suppression comments. |
| Similarity metrics | `py-tlsh`, `ppdeep` | pure-python ssdeep | Native libs improved performance 6x. |

## Linting & Quality

- **mypy:** Strict optional checking, `warn-unused-ignores`, and custom `typing` helpers drive predictable APIs.
- **bandit:** Run with `-q -r forgetrace`; high findings must be resolved or explicitly justified.
- **safety:** Weekly `safety check --full-report`; results logged under `analysis_outputs/live/`.
- **black/isort:** Standard formatting to keep diffs readable (enforced before landing PRs).

## ML & Data Stack

| Layer | Tool | Notes |
|-------|------|-------|
| Feature engineering | `scikit-learn`, pandas-lite utilities | Keep dependencies minimal; avoid heavy pandas on audit agents. |
| Model serialization | `joblib` | Selected for deterministic hashing + avoidance of `pickle` RCE vectors. |
| Experiment tracking | `mlflow` | Currently pinned to 3.6.0 pending CVE fixes; local tests use SQLite fixture. |
| Interpretation | `sklearn.inspection`, custom plots | Plots exported to HTML for audit inclusion. |

## Infrastructure & Deployment

- **Docker Compose:** Spins up PostgreSQL + MLflow (+ optional nginx). Compose health checks guard dependent service ordering.
- **Terraform:** Resides under `terraform/` with layered modules for AWS networking, EC2 hosts, and S3 buckets.
- **MLflow Docker image:** Built from `deployment/mlflow/Dockerfile`; script `scripts/update_mlflow_release.py` keeps version drift in check.

## Tooling Decisions & Revisions

1. **Serialization:** `joblib` replaced `pickle` once Bandit highlighted RCE risks. BLAKE2 digests verify file integrity before loading models.
2. **Template rendering:** Enabled Jinja2 autoescape; reasoning documented in `SECURITY.md` to stop XSS vectors inside generated HTML.
3. **URL handling:** Introduced `_safe_urlopen` wrapper with configurable timeouts to avoid SSRF and indefinite hangs.
4. **MLflow testing:** Local fixture replaced ad-hoc environment variables to ensure deterministic CI runs.
5. **Release automation:** Instead of ad-hoc edits, `scripts/update_mlflow_release.py` edits every touched file and prints the validation checklist.

## Operational Scripts

| Script | Purpose | Expected Inputs | Example |
|--------|---------|-----------------|---------|
| `scripts/run_sample_audit.py` | Produce demo audit artifacts plus MLflow logs. | `--repo-path`, optional `--log-mlflow`. | `python scripts/run_sample_audit.py --repo-path sample_audit`. |
| `scripts/train_random_forest.py` | Retrain IP classifier. | `--dataset training/dataset/latest.csv`. | `python scripts/train_random_forest.py --persist models/forgetrace_rf.joblib`. |
| `scripts/update_mlflow_release.py` | Sync MLflow version metadata. | `--version`, optional release info. | `python scripts/update_mlflow_release.py --version 3.7.1`. |
| `scripts/analyze_feature_importance.py` | Export CSV/plots for explainability. | `--model-path models/forgetrace_rf.joblib`. | `python scripts/analyze_feature_importance.py --output analysis_outputs/local/features`. |

## Tools to Revisit Later

- **Trivy / Grype:** consider layering in container scanning for the MLflow image once we publish to a registry.
- **Prefect:** orchestration alternative if Bash-driven training becomes unwieldy.
- **Delta Lake:** candidate for versioning training datasets beyond Git LFS.

Document every future tool swap (even if we revert) to keep the rationale transparent.

