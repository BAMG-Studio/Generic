# GitHub Secrets Setup Runbook

Use this checklist when populating repository secrets after Terraform/Terragrunt provisioning. It captures placeholders, example values, and verification commands so no secret lands in Git history.

## 1. Required Secrets

| Secret | Placeholder | Source | Notes |
|--------|-------------|--------|-------|
| `AWS_ACCESS_KEY_ID` | `AKIA********************` | `terraform output -raw aws_access_key_id` | IAM user created by infrastructure code. |
| `AWS_SECRET_ACCESS_KEY` | `wJalrXUtnFEMI/K7MDENG/bPxRfiCY********` | `terraform output -raw aws_secret_access_key` (never log) | Paste directly into GitHub UI; do not store locally. |
| `AWS_DEFAULT_REGION` | `us-east-1` | `var.aws_region` / Terragrunt input | Matches the region used for infra. |
| `DVC_REMOTE_BUCKET` | `forgetrace-models-prod-abc12345` | `terraform output -raw s3_bucket_name` | Used by CI pipelines and DVC remote. |
| `GITHUB_TOKEN` | `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` | Personal access token (repo + workflow scopes) | Prefer fine-grained PAT tied to deployment bot account. |
| `MLFLOW_TRACKING_URI` | `http://mlflow.internal:5050` | DNS/IP of MLflow deployment | Required for pipelines that log experiments. |
| `MLFLOW_USERNAME` | `mlflow_admin` | Nginx/basic auth credential | Optional if MLflow is private network only. |
| `MLFLOW_PASSWORD` | `***************` | Password created during nginx setup | Rotate every 180 days (see `SECURITY.md`). |

## 2. Optional Secrets (enable if/when needed)

- `SLACK_WEBHOOK_URL` — to post CI/CD alerts.
- `SENTRY_DSN` — if crash reporting is enabled.
- `PREFECT_API_KEY` — future workflow orchestration integration.

## 3. Procedure

1. Copy the template and gather values:

   ```bash
   cp config/github_secrets.example config/github_secrets.local
   vim config/github_secrets.local  # replace placeholders, then delete once used
   ```

   ```bash
   cd terraform
   terraform output -raw aws_access_key_id
   terraform output -raw aws_secret_access_key
   terraform output -raw s3_bucket_name
   terraform output -raw deployment_summary
   ```

2. Open the GitHub repo → Settings → Secrets and variables → Actions.
3. Click **New repository secret** for each item listed above.
4. Paste values directly from the terminal (avoid intermediate files).
5. After saving, run the secret validation workflow:

   ```bash
   gh workflow run test-secrets.yml
   gh run watch
   ```

6. Record the date/time in `docs/DEPLOYMENT_CHECKLIST.md` under “Secrets Configuration”.

## 4. Verification Commands

Use the saved secrets (via `gh secret set --app actions`) to run a quick no-op job or validate locally:

```bash
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
export AWS_DEFAULT_REGION=us-east-1
aws s3 ls s3://forgetrace-models-prod-abc12345/
```

For MLflow credentials:

```bash
curl -u "$MLFLOW_USERNAME:$MLFLOW_PASSWORD" "$MLFLOW_TRACKING_URI/health"
```

## 5. Audit Trail

Document every secret addition or rotation inside your change log:

- Date & time
- Operator
- Reason (initial setup, rotation, breach response)
- Evidence link (GitHub Actions run URL, `analysis_outputs/live/terraform-YYYY-MM-DD.txt`, etc.)

Retain this runbook alongside `docs/DEPLOYMENT_CHECKLIST.md` so new operators can on-board quickly.
