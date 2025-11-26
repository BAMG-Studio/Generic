# ForgeTrace Production Deployment Checklist

Use this checklist to track your production deployment progress.

## Pre-Deployment Setup

### AWS Infrastructure
- [ ] AWS account created
- [ ] IAM user `forgetrace-ci` created
- [ ] IAM policies attached (S3FullAccess, CloudWatchLogsFullAccess)
- [ ] AWS access key generated and saved securely
- [ ] S3 bucket created: `forgetrace-models-<your-suffix>`
- [ ] S3 folder structure created (models/, training-data/, benchmarks/, audit-reports/, mlflow/)
- [ ] AWS CLI installed and configured locally
- [ ] S3 connection tested successfully
- [ ] (Optional) Lifecycle policies configured for cost optimization
- [ ] (Optional) CloudTrail enabled for audit logging

**AWS Credentials Saved**:
- AWS_ACCESS_KEY_ID: `AKIA________________`
- AWS_SECRET_ACCESS_KEY: `________________________________________`
- AWS_DEFAULT_REGION: `us-east-1`
- DVC_REMOTE_BUCKET: `forgetrace-models-______`

---

### GitHub Configuration
- [ ] Personal access token generated
- [ ] Token scopes verified (repo, workflow, write:packages)
- [ ] Token saved in password manager
- [ ] Token tested with GitHub API
- [ ] Local `.env` file created (and added to .gitignore)
- [ ] `.env.example` reviewed and understood

**GitHub Token Saved**:
- GITHUB_TOKEN: `ghp____________________________________`

---

### MLflow Deployment

#### Self-Hosted Option
- [ ] Docker and Docker Compose installed
- [ ] `.env` file created with AWS credentials
- [ ] MLflow database password set
- [ ] Docker Compose services started (`docker-compose up -d`)
- [ ] MLflow UI accessible at http://localhost:5050
- [ ] PostgreSQL database healthy
- [ ] MLflow can write to S3 (test experiment created)
- [ ] (Optional) Nginx authentication configured
- [ ] (Optional) SSL/TLS certificates configured

**MLflow Configuration**:
- MLFLOW_TRACKING_URI: `http://____________:5050`
- MLFLOW_DB_PASSWORD: `____________________`
- MLFLOW_USERNAME: `____________` (if using auth)
- MLFLOW_PASSWORD: `____________` (if using auth)

#### Managed Option (AWS SageMaker)
- [ ] SageMaker MLflow tracking server created
- [ ] Tracking server ARN copied
- [ ] S3 artifact store configured
- [ ] Test experiment created successfully

**MLflow Configuration**:
- MLFLOW_TRACKING_URI: `arn:aws:sagemaker:____________`

---

## GitHub Repository Setup

### Secrets Configuration
- [ ] All GitHub Secrets added to repository:
  - [ ] AWS_ACCESS_KEY_ID
  - [ ] AWS_SECRET_ACCESS_KEY
  - [ ] AWS_DEFAULT_REGION
  - [ ] DVC_REMOTE_BUCKET
  - [ ] GITHUB_TOKEN
  - [ ] MLFLOW_TRACKING_URI
  - [ ] MLFLOW_USERNAME (if using auth)
  - [ ] MLFLOW_PASSWORD (if using auth)
- [ ] "Test Secrets Configuration" workflow executed successfully
- [ ] All secret validation checks passed

### CI/CD Workflows
- [ ] GitHub Actions enabled in repository settings
- [ ] Workflow permissions set to "Read and write"
- [ ] `.github/workflows/ci.yml` present
- [ ] `.github/workflows/ml-training.yml` present
- [ ] `.github/workflows/test-secrets.yml` present
- [ ] First CI/CD pipeline run successful
- [ ] All lint, test, and security jobs passing

### Branch Protection
- [ ] Branch protection rule created for `main` branch
- [ ] Pull request required before merging
- [ ] Minimum 1 approval required
- [ ] Stale PR approval dismissal enabled
- [ ] Code owners review required
- [ ] Status checks required:
  - [ ] `CI/CD Pipeline / lint`
  - [ ] `CI/CD Pipeline / test`
  - [ ] `CI/CD Pipeline / security`
- [ ] Conversation resolution required
- [ ] Direct pushes to main blocked

### Code Review Setup
- [ ] `.github/CODEOWNERS` file created
- [ ] `.github/PULL_REQUEST_TEMPLATE.md` created
- [ ] CODEOWNERS file assigns correct reviewers
- [ ] Test PR created to verify workflow

---

## Security & Compliance

### Security Documentation
- [ ] `SECURITY.md` reviewed and understood
- [ ] Secret rotation schedule documented
- [ ] Last rotation dates updated
- [ ] Incident response procedures documented
- [ ] Access control policies defined

### Security Features Enabled
- [ ] GitHub Dependabot alerts enabled
- [ ] GitHub Dependabot security updates enabled
- [ ] GitHub Secret scanning enabled
- [ ] GitHub Push protection enabled
- [ ] Repository access permissions reviewed
- [ ] No secrets committed to code

### Compliance
- [ ] Data classification policy reviewed (if applicable)
- [ ] Regulatory requirements documented (GDPR, SOC 2, etc.)
- [ ] Client data handling procedures defined

---

## Training & Model Management

### DVC Configuration
- [ ] DVC installed (`pip install dvc`)
- [ ] DVC remote configured for S3
- [ ] DVC can pull from S3 (`dvc pull`)
- [ ] DVC can push to S3 (`dvc push`)

### ML Training Pipeline
- [ ] Training dataset exists in `training_output/dataset/`
- [ ] "ML Training Pipeline" workflow executed
- [ ] Model trained successfully
- [ ] Model uploaded to S3
- [ ] Model artifacts tracked with DVC
- [ ] MLflow experiment logged
- [ ] Model metrics meet baseline (accuracy >99%)

### Model Validation
- [ ] Feature importance analysis completed
- [ ] Model interpretability report generated
- [ ] Cross-validation performed
- [ ] Model card updated (`docs/MODEL_CARD.md`)
- [ ] Performance benchmarks passing

---

## Client Profiling Setup

### Profiling Infrastructure
- [ ] `training/profiling_datasets/` directory created
- [ ] `catalog.yaml` initialized
- [ ] README.md reviewed
- [ ] `scripts/extract_profile_samples.py` tested
- [ ] `scripts/extract_ground_truth.py` tested

### First Client Profile (Optional)
- [ ] Client repository anonymized
- [ ] Representative samples extracted
- [ ] `metadata.yaml` created and reviewed
- [ ] Ground truth audit completed
- [ ] `expected_results.json` generated
- [ ] Catalog updated
- [ ] Benchmarks passing for profile

---

## Documentation

### Core Documentation
- [ ] `README.md` reviewed and updated
- [ ] `USAGE.md` reviewed
- [ ] `ARCHITECTURE.md` reviewed
- [ ] `SECURITY.md` created
- [ ] `docs/EDGE_CASES.md` created
- [ ] `docs/PRODUCTION_DEPLOYMENT.md` created

### Configuration Files
- [ ] `.env.example` created
- [ ] `config.yaml` reviewed
- [ ] `docker-compose.yml` created
- [ ] `deployment/nginx/nginx.conf` created (if using auth)

---

## Deployment Validation

### Smoke Tests
- [ ] Run local audit on test repository:
  ```bash
  forgetrace audit test_output/ml_demo_repo/ --out validation/smoke_test/
  ```
- [ ] Verify audit completes successfully
- [ ] Check output files generated (audit.json, report.html, etc.)
- [ ] Review metrics for sanity

### Integration Tests
- [ ] Unit tests passing locally (`pytest tests/`)
- [ ] Integration tests passing in CI/CD
- [ ] Security scans passing (Bandit, Safety)
- [ ] Dependency audit clean (`pip-audit`)

### End-to-End Test
- [ ] Create test PR with code changes
- [ ] Verify CI/CD pipeline runs
- [ ] Verify branch protection enforces reviews
- [ ] Merge PR after approval
- [ ] Trigger ML training pipeline manually
- [ ] Verify model trains and deploys to S3
- [ ] Pull trained model with DVC
- [ ] Run audit with new model

---

## Production Readiness

### Monitoring Setup
- [ ] AWS CloudWatch logs configured
- [ ] MLflow UI accessible and monitored
- [ ] GitHub Actions usage tracked
- [ ] Dependabot alerts reviewed weekly
- [ ] Secret rotation reminders set (90-day calendar)

### Backup & Recovery
- [ ] Critical data backed up:
  - [ ] Trained models (DVC + S3)
  - [ ] Training datasets (DVC + S3)
  - [ ] Configuration files (Git)
  - [ ] MLflow database (PostgreSQL backups)
- [ ] Recovery procedures documented
- [ ] Recovery tested (optional but recommended)

### Team Readiness
- [ ] Deployment guide reviewed by team
- [ ] Security policy acknowledged
- [ ] Access permissions assigned
- [ ] On-call rotation defined (if applicable)
- [ ] Incident response plan communicated

---

## Go-Live

### Final Checks
- [ ] All above sections completed
- [ ] No critical issues in CI/CD
- [ ] No critical security vulnerabilities
- [ ] All secrets rotated within 90 days
- [ ] Documentation complete and accurate

### Post-Deployment
- [ ] Monitor first 24 hours of production use
- [ ] Review CloudWatch logs for errors
- [ ] Check MLflow for experiment logging
- [ ] Verify S3 storage usage
- [ ] Schedule first maintenance window (1 week)

### First Client Audit
- [ ] Client repository ready
- [ ] Engagement scope defined
- [ ] Run production audit:
  ```bash
  forgetrace audit /path/to/client/repo \
    --out repo_audit/<client>/forgetrace_report/ \
    --config config.yaml
  ```
- [ ] Review results with client
- [ ] Generate deliverables (PDF, HTML, etc.)
- [ ] Archive engagement materials

---

## Ongoing Maintenance

### Daily
- [ ] Check GitHub Actions status
- [ ] Review Dependabot alerts

### Weekly
- [ ] Review audit logs (CloudTrail)
- [ ] Check S3 storage usage
- [ ] Review security scan results

### Monthly
- [ ] Update dependencies
- [ ] Run pip-audit
- [ ] Backup critical data

### Quarterly
- [ ] Rotate secrets (see SECURITY.md)
- [ ] Review access permissions
- [ ] Update documentation
- [ ] Retrain ML model (if needed)

---

## Notes

Use this space to document deployment-specific details:

**AWS Account ID**: _______________

**MLflow Server IP**: _______________

**S3 Bucket ARN**: _______________

**Production URL** (if web-hosted): _______________

**Team Contacts**:
- Primary: Peter Kolawole (peter@beaconagile.net)
- Backup: _______________

**Last Deployment**: _______________

**Next Security Review**: _______________

---

**Deployment Status**: 🚧 In Progress / ✅ Complete

**Completed By**: _______________

**Date**: _______________

**Sign-Off**: _______________
