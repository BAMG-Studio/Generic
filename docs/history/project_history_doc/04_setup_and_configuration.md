# Setup & Configuration Guide

Use this guide to bootstrap ForgeTrace on a fresh workstation, run validations, and understand configuration surfaces across environments.

## 1. Prerequisites

| Component | Version | Notes |
|-----------|---------|-------|
| Python | 3.12.x | Managed via `.venv`; see commands below. |
| Node (optional) | 18.x | Only needed if extending dashboard visualizations. |
| Docker | 24.x | Required for MLflow + Postgres stack. |
| Terraform | 1.7.x | Used to provision production infrastructure. |

## 2. Local Environment Bring-Up

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-optional.txt  # optional scanners
```

### Verification

- `pytest -m "not slow"` — fast suite guardrail.
- `pytest tests/mlflow/test_mlflow_quick.py -q` — ensures MLflow fixture works.
- `bandit -q -r forgetrace` — lint for security regressions.
- `safety check --full-report` — confirm vulnerability status.

## 3. Configuration Files

| File | Purpose | Key Fields |
|------|---------|------------|
| `config.yaml` | CLI defaults (paths, thresholds). | `scan.targets`, `report.format`. |
| `config/mlflow_release.yaml` | Tracks MLflow version, CVEs, verification checklist. | `current_version`, `verification_checklist`. |
| `config/github_secrets.example` | Placeholder file for GitHub Actions secrets. | Replace with Terraform outputs before populating repo secrets. |
| `terraform/terraform.tfvars` | Production infrastructure variables. | `aws_region`, `mlflow_instance_type`. |
| `deployment/nginx/nginx.conf` | Reverse proxy/auth hardening. | `auth_basic`, TLS termination. |

## 3.5 Automation Runbooks

- `docs/runbooks/IAM_S3_PROVISIONING.md` — step-by-step Terraform/Terragrunt workflow for creating the CI IAM user and S3 bucket with the built-in modules.
- `docs/runbooks/GITHUB_SECRETS_SETUP.md` — placeholder matrix plus validation commands for adding AWS/MLflow secrets to GitHub Actions after provisioning.

## 4. Running MLflow Locally

1. Export minimal env vars:

   ```bash
   export MLFLOW_DB_PASSWORD=dev_password
   export AWS_ACCESS_KEY_ID=fake
   export AWS_SECRET_ACCESS_KEY=fake
   export DVC_REMOTE_BUCKET=forgetrace-models-dev
   ```

2. Start services:

   ```bash
   docker-compose up -d postgres mlflow
   docker-compose logs -f mlflow
   ```

3. Smoke-test endpoints:

   ```bash
   curl -sf http://localhost:5050/health
   curl -sf http://localhost:5050/api/2.0/mlflow/experiments/list | python -m json.tool
   ```

## 5. Production Deployment Snapshot

- **State backend:** Terraform keeps remote state secure (S3 + DynamoDB locks) — run `terraform init -backend-config=...` during first-time setup.
- **MLflow host:** `deployment/mlflow/Dockerfile` builds the image; pass `MLFLOW_S3_ENDPOINT_URL` to target AWS or MinIO.
- **Secrets:** Use AWS SSM or Vault; `.env` files are forbidden in repo. Update nginx `.htpasswd` every 180 days as tracked in `SECURITY.md`.

## 6. Maintenance Cadence

| Task | Frequency | Command |
|------|-----------|---------|
| Rotate MLflow password | 180 days | `htpasswd deployment/nginx/.htpasswd mlflow_admin` |
| Re-run MLflow verification checklist | After every upgrade | `python scripts/update_mlflow_release.py --version <new>` then follow prompts. |
| Refresh classifier | Quarterly or after dataset change | `python scripts/train_random_forest.py --persist models/forgetrace_rf.joblib`. |
| Clean training cache | Monthly | `rm -rf training/cache/*`. |

## 7. Expected Behaviors

- Running `forgetrace audit repo_path` should emit reports under `analysis_outputs/live/` with HTML + JSON artifacts.
- MLflow local runs store artifacts inside the per-test temp directory; production runs point to S3 via `--default-artifact-root`.
- Safety remains in warning state until MLflow ships patched bits; track status through `docs/MLFLOW_UPGRADE_PLAYBOOK.md`.

Keep this guide updated as dependencies or infra layers change.

