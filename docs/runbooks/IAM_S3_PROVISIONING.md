# IAM & S3 Provisioning Runbook

This runbook shows how to spin up the ForgeTrace IAM CI/CD user and the model-storage S3 bucket using the infrastructure code under `terraform/`. Use Terraform for single-run setups or Terragrunt when you want environment-specific state isolation.

## 1. Prerequisites

- AWS CLI v2 configured with credentials that can create IAM/S3 resources.
- Terraform ≥ 1.6.0 and/or Terragrunt ≥ 0.55.0 installed.
- `terraform/terraform.tfvars` populated (see example file) when running plain Terraform.
- Remote state bucket/DynamoDB table created if you enable the backend block.

Quick install check:

```bash
terraform -version
terragrunt --version
aws sts get-caller-identity
```

## 2. Option A – Terraform (Single Environment)

1. Copy the example variables file:
   ```bash
   cd terraform
   cp terraform.tfvars.example terraform.tfvars
   vim terraform.tfvars  # update owner_email, ci_user_name, etc.
   ```
2. Validate credentials and initialize:
   ```bash
   ./deploy.sh init
   ```
3. Review the plan and apply:
   ```bash
   ./deploy.sh plan
   ./deploy.sh apply
   ```
4. Capture outputs for GitHub secrets and documentation:
   ```bash
   ./deploy.sh outputs > ../analysis_outputs/live/terraform-$(date +%F).txt
   ```
5. Optional smoke test of generated credentials:
   ```bash
   ./deploy.sh test
   ```

## 3. Option B – Terragrunt (Multiple Environments)

The `terraform/environments/production/terragrunt.hcl` file already wires remote state, provider config, and default inputs.

1. Bootstrap the shared state store once:
   ```bash
   aws s3 mb s3://forgetrace-terraform-state-production
   aws dynamodb create-table \
     --table-name forgetrace-terraform-locks \
     --attribute-definitions AttributeName=LockID,AttributeType=S \
     --key-schema AttributeName=LockID,KeyType=HASH \
     --billing-mode PAY_PER_REQUEST
   ```
2. Run the Terragrunt workflow:
   ```bash
   cd terraform/environments/production
   terragrunt init
   terragrunt plan
   terragrunt apply
   ```
3. Retrieve outputs (Terragrunt proxies Terraform outputs):
   ```bash
   terragrunt output deployment_summary
   terragrunt output -raw aws_access_key_id
   terragrunt output -raw aws_secret_access_key  # paste directly into GitHub Secret
   terragrunt output -raw s3_bucket_name
   ```
4. Store a sanitized copy of the output inside `analysis_outputs/live/` for auditing.

## 4. Populating GitHub Secrets

After either workflow, record the following (see `docs/runbooks/GITHUB_SECRETS_SETUP.md` for details):

| Secret Name | Source |
|-------------|--------|
| `AWS_ACCESS_KEY_ID` | `terraform output -raw aws_access_key_id` |
| `AWS_SECRET_ACCESS_KEY` | `terraform output -raw aws_secret_access_key` |
| `AWS_DEFAULT_REGION` | Value of `var.aws_region` / Terragrunt input |
| `DVC_REMOTE_BUCKET` | `terraform output -raw s3_bucket_name` |

## 5. Cleanup / Destruction

When tearing down non-production environments:

```bash
cd terraform
./deploy.sh destroy
```

or, for Terragrunt:

```bash
cd terraform/environments/production
terragrunt destroy
```

Remember that destroying resources deletes **all** artifacts stored in the S3 bucket and revokes the IAM credentials. Export MLflow experiments and model artifacts before running destroy.

## 6. Runbook Ownership

- **Primary:** DevOps Lead
- **Backup:** ML Lead

Log every execution (date, environment, outputs filename) in your change management tracker so we can trace when credentials or buckets were created.

