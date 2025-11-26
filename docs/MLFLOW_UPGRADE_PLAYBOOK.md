# MLflow Upgrade Playbook

ForgeTrace currently pins `mlflow==3.6.0`, which ships with eight upstream CVEs (CVE-2024-37052/53/54/55/56/57/59/60). Until maintainers publish a fixed train, the repository tracks risk in `config/mlflow_release.yaml` and keeps the Docker image aligned via `scripts/update_mlflow_release.py`. Follow this playbook the moment a patched build is available.

## 1. Release Triage

1. Monitor upstream sources:
   - MLflow GitHub releases RSS feed.
   - `safety check --full-report` output during CI runs.
   - Dependabot alerts scoped to the `mlflow` package.
2. Validate the release changelog for explicit CVE remediations.
3. Update `config/mlflow_release.yaml` with tentative metadata so the risk tracker reflects what you are watching.

## 2. Pre-Upgrade Checklist

| Step | Command | Rationale |
|------|---------|-----------|
| Snapshot experiments | `mlflow experiments export --output-dir mlruns/backup-$(date +%F)` | Enables fast rollback. |
| Lock environment | `pip freeze > tmp_mlflow_lock.txt` | Captures current dependency graph. |
| Smoke-check docker image | `docker run --rm ghcr.io/mlflow/mlflow:vX.Y.Z mlflow --version` | Verifies tag exists before composing services. |
| Verify database backup | `pg_dump --dbname=$MLFLOW_DB_URI --file=mlflow_backup.sql` | Protects metadata store. |
| Collect safety baseline | `safety check --json > .reports/safety-before.json` | Provides before/after evidence. |

## 3. Automated Version Bump

Use the helper script to fan out version updates across the repo. Example for `3.7.1`:

```bash
"$(pwd)/.venv/bin/python" scripts/update_mlflow_release.py \
  --version 3.7.1 \
  --status "✅ No known CVEs" \
  --upgrade-status queued
```

Options:

- `--image-tag` overrides the default `ghcr.io/mlflow/mlflow:v<version>` naming if the registry shifts.
- `--cve` can be specified multiple times when residual issues remain.
- `--release-notes` persists the upstream URL inside the config file for future audits.

The script synchronizes:

- `config/mlflow_release.yaml`
- `requirements.txt`
- `deployment/mlflow/Dockerfile`
- the MLflow row in `SECURITY.md`

## 4. Validation Matrix

After bumping, complete the verification checklist captured inside `config/mlflow_release.yaml` (edit it if new steps are needed).

| Area | Command | Expected Outcome |
|------|---------|------------------|
| Fast unit tests | `pytest tests/mlflow/test_mlflow_quick.py -q` | Pass, ensures fixture works with new client. |
| End-to-end MLflow suite | `pytest tests/mlflow -m "not slow"` | All green, metrics logged locally. |
| Regression safety scan | `safety check --full-report` | No MLflow CVEs. |
| Container smoke test | `docker-compose up -d mlflow && curl -sf http://localhost:5050/health` | HTTP 200. |
| Artifact push | `python scripts/run_sample_audit.py --log-mlflow` | Completes with run recorded in staging bucket. |

## 5. Deployment Rollout

1. Build and push the refreshed MLflow image (if you maintain a fork):

   ```bash
   docker build -t forgetrace-mlflow:3.7.1 deployment/mlflow
   docker tag forgetrace-mlflow:3.7.1 <registry>/forgetrace-mlflow:3.7.1
   docker push <registry>/forgetrace-mlflow:3.7.1
   ```

2. Reference the new tag inside your infrastructure layer (Terraform variables, Kubernetes manifests, or Docker Compose overrides).
3. Execute blue/green or rolling restart depending on environment:

   ```bash
   docker-compose pull mlflow
   docker-compose up -d mlflow
   docker-compose logs -f mlflow
   ```

4. Confirm downstream consumers (CI/CD jobs, notebook users) read from the upgraded endpoint.

## 6. Rollback Plan

If regressions appear:

- Re-run `scripts/update_mlflow_release.py --version <old>` to reset metadata.
- Restore the database snapshot and artifact backups.
- Redeploy the prior container tag and announce temporary freeze in `#mlops`.

## 7. Audit Evidence

Archive the following artifacts after every upgrade:

- `tmp_mlflow_lock.txt` and `pip list --outdated` output.
- Safety scan reports (before/after) inside `analysis_outputs/live/`.
- Docker image digest produced by `docker inspect forgetrace-mlflow:<tag> --format '{{.Id}}'`.
- Screenshots or curl outputs showing `/health` and `/api/2.0/mlflow/experiments/list` success.

## 8. Ownership & Notifications

- **DRI:** ML Lead
- **Backup:** Platform Lead
- Notify Security and Compliance once Safety reports turn green; attach logs to `SECURITY.md` PR for review.

Keeping this playbook updated ensures the outstanding Safety advisories are cleared the instant an upstream fix ships while maintaining auditable change control.
