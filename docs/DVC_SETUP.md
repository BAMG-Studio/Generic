# DVC Configuration

DVC is configured to track ML models and training datasets using your production S3 bucket.

## Remote Storage

- **Remote Name**: production (default)
- **Location**: s3://forgetrace-models-production-dbjohpzx/dvc-storage
- **Region**: us-east-1

## Tracked Assets

- `models/ip_classifier_rf.pkl` - Random Forest IP classifier model

## Common Commands

```bash
# Activate environment
source .venv/bin/activate

# Pull models from S3
dvc pull

# Push models to S3
dvc push

# Check status
dvc status

# Add new model/data
dvc add models/new_model.pkl
git add models/new_model.pkl.dvc models/.gitignore
git commit -m "Track new model with DVC"
dvc push
```

## CI/CD Integration

DVC credentials are configured via AWS credentials in `.env`:
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
- AWS_DEFAULT_REGION

## Next Steps

1. Commit DVC configuration:
```bash
git add .dvc .gitignore models/.gitignore models/ip_classifier_rf.pkl.dvc
git commit -m "Configure DVC with S3 remote storage"
```

2. Push model to S3:
```bash
dvc push
```

3. Add training datasets:
```bash
dvc add training_output/dataset/
git add training_output/dataset.dvc training_output/.gitignore
git commit -m "Track training datasets with DVC"
dvc push
```
