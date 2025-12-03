<!-- markdownlint-disable MD031 MD032 MD034 MD036 -->

# ForgeTrace Usage Guide

**Author: Peter Kolawole, BAMG Studio LLC**

## Installation

```bash
# Clone repository
git clone git@github.com:BAMG-Studio/Generic.git
cd Generic

# Install core package
pip install -e .

# Install optional tools
./scripts/install_tools.sh
```

## Basic Usage

### CLI Audits

```bash
# Run audit on a repository
forgetrace audit /path/to/target-repo --out repo_audit/example/forgetrace_report

# Preview reports in browser (recommended!)
forgetrace preview repo_audit/example/forgetrace_report --browser

# With custom config
forgetrace audit /path/to/repo --out repo_audit/acme/forgetrace_report --config my-config.yaml

# Specify tool paths
forgetrace audit /path/to/repo \
  --syft /usr/local/bin/syft \
  --scancode scancode \
  --semgrep semgrep \
  --trufflehog trufflehog \
  --gitleaks gitleaks

# Override executive summary depth on the fly
forgetrace audit /path/to/repo --exec-mode board

# Preview on custom port
forgetrace preview repo_audit/acme/forgetrace_report --port 9000 --browser
```

### API Access

ForgeTrace provides a RESTful API for programmatic access. First, create an API token at `https://www.forgetrace.pro/app/developer`.

#### Submit an Audit

```bash
curl -X POST https://api.forgetrace.pro/v1/audits \
  -H "Authorization: Bearer ftk_your_token_here" \
  -H "Content-Type: application/json" \
  -d '{
    "repository": "https://github.com/org/repo",
    "branch": "main",
    "config": {
      "confidence_threshold": 0.75,
      "include_sbom": true,
      "include_vulnerabilities": true
    }
  }'
```

Response:

```json
{
  "id": "aud_abc123xyz",
  "status": "queued",
  "created_at": "2025-11-26T18:00:00Z",
  "estimated_completion": "2025-11-26T18:05:00Z"
}
```

#### Check Audit Status

```bash
curl https://api.forgetrace.pro/v1/audits/aud_abc123xyz \
  -H "Authorization: Bearer ftk_your_token_here"
```

Response:

```json
{
  "id": "aud_abc123xyz",
  "status": "completed",
  "progress": 100,
  "created_at": "2025-11-26T18:00:00Z",
  "completed_at": "2025-11-26T18:03:47Z",
  "summary": {
    "total_files": 1247,
    "foreground_ip": 892,
    "third_party_ip": 338,
    "background_ip": 17,
    "critical_vulnerabilities": 3,
    "high_risk_licenses": 5
  },
  "reports": {
    "html": "https://api.forgetrace.pro/v1/reports/rep_xyz789/html",
    "json": "https://api.forgetrace.pro/v1/reports/rep_xyz789/json",
    "pdf": "https://api.forgetrace.pro/v1/reports/rep_xyz789/pdf"
  }
}
```

#### Download Report

```bash
# JSON report
curl https://api.forgetrace.pro/v1/reports/rep_xyz789/json \
  -H "Authorization: Bearer ftk_your_token_here" \
  -o audit_report.json

# PDF report
curl https://api.forgetrace.pro/v1/reports/rep_xyz789/pdf \
  -H "Authorization: Bearer ftk_your_token_here" \
  -o audit_report.pdf
```

#### Rate Limits

API responses include rate limit headers:

```text
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1732645200
```

If you exceed limits, you'll receive a `429 Too Many Requests` response:

```json
{
  "error": "rate_limit_exceeded",
  "message": "Too many requests. Please slow down.",
  "retry_after": 42
}
```

#### CI/CD Integration

Add to your GitHub Actions workflow:

```yaml
name: ForgeTrace Audit
on: [pull_request]

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run ForgeTrace Audit
        run: |
          AUDIT_ID=$(curl -X POST https://api.forgetrace.pro/v1/audits \
            -H "Authorization: Bearer ${{ secrets.FORGETRACE_TOKEN }}" \
            -H "Content-Type: application/json" \
            -d '{"repository": "'"$GITHUB_REPOSITORY"'", "branch": "'"$GITHUB_REF"'"}' \
            | jq -r '.id')
          
          # Poll for completion
          while true; do
            STATUS=$(curl https://api.forgetrace.pro/v1/audits/$AUDIT_ID \
              -H "Authorization: Bearer ${{ secrets.FORGETRACE_TOKEN }}" \
              | jq -r '.status')
            
            if [ "$STATUS" = "completed" ]; then
              break
            fi
            sleep 10
          done
          
          # Check for critical issues
          CRITICAL=$(curl https://api.forgetrace.pro/v1/audits/$AUDIT_ID \
            -H "Authorization: Bearer ${{ secrets.FORGETRACE_TOKEN }}" \
            | jq -r '.summary.critical_vulnerabilities')
          
          if [ "$CRITICAL" -gt 0 ]; then
            echo "::error::Found $CRITICAL critical vulnerabilities"
            exit 1
          fi
```

## Output Files

After running an audit, you'll find:

- `audit.json` - Complete findings in JSON format
- `ip_contribution_table.md` - Negotiation-ready Markdown table
- `report.html` - Interactive HTML report
- `report.pdf` - Comprehensive PDF report (if WeasyPrint installed)
- `sbom.*.json` - CycloneDX/SPDX exports when Syft is configured

## Live Client Archives

ForgeTrace automatically mirrors every successful audit into a permanent, human-friendly archive so live client data never mixes with throwaway test runs. By default, archives are written to `analysis_outputs/live/<owner>/<repo>/<YYYY/MM/DD>/<HHMMSS>/` with a `metadata.json` manifest plus a `latest` symlink for fast access.

- Remote repository URLs are parsed to determine the `<owner>/<repo>` folders (falls back to the local directory name when no Git metadata is available).
- Archives keep up to 50 runs per repository (configurable via `output.archive.max_runs_per_repo`). Older runs are pruned automatically, preventing clutter.
- Temporary locations such as `/tmp/...` are still written when you pass `--out`, ensuring automated workflows remain unchanged while the curated archive receives a clean copy.

You can customize the archive root or disable mirroring entirely:

```yaml
output:
  archive:
    enabled: true
    root_dir: "/secure/path/for/clients"
    max_runs_per_repo: 25
```

Every archive includes:

- A copy of all generated reports
- `metadata.json` with source path, Git commit/branch (when available), timestamp, and report list
- A rolling `latest` symlink for integrations that only need the freshest audit

## SBOM & Dependency Exports

ForgeTrace can now emit standard SBOMs for downstream tooling. Install Syft once (via `./scripts/install_tools.sh` or manually) and either set the path in `config.yaml` or pass `--syft /path/to/syft` at runtime.

```yaml
output:
  include_sbom: true
  sbom_formats:
    - cyclonedx-json
    - spdx-json
tools:
  syft: "/usr/local/bin/syft"
```

Override formats per run:

```bash
forgetrace audit /repo/path --sbom-format cyclonedx-json --sbom-format spdx-json
```

The HTML/PDF reports now include a **Software Bill of Materials** section with download links, and the raw files (e.g., `sbom.cyclonedx-json.json`) live alongside `report.html` and in the `analysis_outputs/live/...` archive tree.

## Configuration

Edit `config.yaml` to customize:

- **Scoring weights**: Adjust novelty, complexity, ownership, criticality
- **Similarity thresholds**: Control duplicate detection sensitivity
- **Cost parameters**: Set hourly rate, days per KLOC, complexity multiplier
- **Tool paths**: Specify custom locations for external tools
- **Vulnerability filters**: Tune OSV noise suppression via `min_cvss_ingest`, `min_cvss_context`, `confidence_floor`, and severity weights

### Vulnerability Filtering (OSV)

ForgeTrace applies intelligent filtering to reduce false positives in vulnerability reports:

```yaml
vulnerability_filters:
  # Minimum CVSS score to ingest vulnerability (0.0-10.0)
  min_cvss_ingest: 4.0
  
  # Minimum CVSS score for contextual display (show only if relevant)
  min_cvss_context: 6.0
  
  # Confidence floor: filter vulnerabilities below this certainty (0.0-1.0)
  confidence_floor: 0.3
  
  # Severity score weights (used in vulnerability_weighted_score calculation)
  severity_weights:
    CRITICAL: 1.0
    HIGH: 0.75
    MEDIUM: 0.5
    LOW: 0.25
    UNKNOWN: 0.1
```

**Key Parameters:**
- `min_cvss_ingest`: Filters out low-severity vulnerabilities at ingestion time
- `min_cvss_context`: Additional filter for display; vulnerabilities between `min_cvss_ingest` and `min_cvss_context` are tracked but not prominently shown
- `confidence_floor`: Removes speculative/low-confidence vulnerability matches (useful for polyglot repos with high false-positive rates)
- `severity_weights`: Adjust importance of different severity levels in aggregate metrics

**Example Scenarios:**
- **Enterprise security audit**: Set `min_cvss_ingest: 6.0` and `confidence_floor: 0.6` for high-confidence critical/high vulnerabilities only
- **Comprehensive assessment**: Set `min_cvss_ingest: 0.0` and `confidence_floor: 0.0` to see all potential issues
- **M&A due diligence**: Set `min_cvss_context: 7.0` to focus executive summary on high-impact risks

## Example Workflow

```bash
# 1. Audit a client repository (stored in repo_audit/<client>)
forgetrace audit /path/to/client-repo --out repo_audit/client-name/forgetrace_report

# 2. Review outputs
cat repo_audit/client-name/forgetrace_report/ip_contribution_table.md
open repo_audit/client-name/forgetrace_report/report.html

# 3. Share with client
# Send report.pdf and ip_contribution_table.md
```

## ML-Based IP Classification

ForgeTrace now supports **machine learning classification** for intelligent code origin detection using a Random Forest classifier with 53 feature dimensions.

### Quick Start

1. **Install ML dependencies:**
   ```bash
   pip install scikit-learn numpy matplotlib seaborn
   ```

2. **Enable in config.yaml:**
   ```yaml
   ml_classifier:
     enabled: true
     confidence_threshold: 0.7
   ```

3. **Use pre-trained model (recommended):**
   ```bash
   # Model already trained on 131,906 examples from 54 repositories
   forgetrace audit /path/to/repo --out repo_audit/example/forgetrace_report
   # Automatically uses models/ip_classifier_rf.pkl
   ```

4. **Or train custom model:**
   ```bash
   # Generate training data from curated repositories
   python scripts/run_training_pipeline.py --output training_output/
   
   # Train Random Forest classifier
   python scripts/train_random_forest.py --data training_output/dataset/training_dataset.jsonl
   ```

### Feature Schema (53 Features)

The ML classifier analyzes code files across multiple dimensions:

**Structural Features (5)**
- `lines_of_code`, `file_size_bytes`, `path_depth`, `avg_line_length`, `nesting_depth`

**Code Complexity (4)**
- `comment_ratio`, `code_to_text_ratio`, `sample_entropy`, `language_entropy`

**Import/Dependency Analysis (4)**
- `import_count`, `external_import_ratio`, `stdlib_import_ratio`, `module_depth_score`

**Path & Naming Indicators (7)**
- `template_indicator`, `config_indicator`, `sbom_indicator`, `manifest_indicator`
- `vendor_path_indicator`, `is_test_path`, `is_docs_path`

**License & Legal (4)**
- `spdx_header_present`, `has_spdx_header`, `license_keyword_hits`, `permissive_license_indicator`

**Security Features (7)**
- `secret_risk_score`, `credential_keyword_density`, `secret_pattern_hits`
- `sensitive_assignment_hits`, `high_entropy_literal_ratio`, `private_key_indicator`, `crypto_import_indicator`

**Domain-Specific Indicators (5)**
- `data_access_indicator`, `api_endpoint_count`, `async_processing_indicator`
- `orchestration_signal`, `plugin_registration_hits`

**Research/Academic (8)**
- `citation_count`, `paper_reference_hits`, `figure_mentions`, `dataset_mentions`
- `experiment_path_indicator`, `experiment_config_indicator`, `methodology_indicator`, `abstract_indicator`

**Business Context (5)**
- `framework_keyword_hits`, `framework_mentions`, `business_context_density`
- `metric_mentions`, `dashboard_indicator`

**Repository-Level Vulnerability Metrics (4)** *(currently non-functional)*
- `repo_vulnerability_count`, `repo_vuln_density`, `repo_vuln_weighted_score`, `repo_osv_noise_ratio`

**Top 10 Most Important Features:**
1. `template_indicator` (16.43%)
2. `language_entropy` (13.92%)
3. `external_import_ratio` (11.02%)
4. `import_count` (10.24%)
5. `nesting_depth` (8.82%)
6. `sample_entropy` (5.45%)
7. `citation_count` (4.74%)
8. `module_depth_score` (4.52%)
9. `code_to_text_ratio` (3.46%)
10. `comment_ratio` (2.84%)

### Production Deployment

#### 1. Model Versioning

Add metadata to models for audit trails:

```bash
python scripts/model_versioning.py \
  --model models/ip_classifier_rf.pkl \
  --output models/ip_classifier_v2025.11.08.pkl \
  --version 2025.11.08.1 \
  --notes "Initial production release with 131K training examples"

# Inspect versioned model
python scripts/model_versioning.py --inspect models/ip_classifier_v2025.11.08.pkl
```

**Metadata Included:**
- Training dataset hash (reproducibility)
- Feature schema version
- Hyperparameters
- Performance metrics (99.9% test accuracy)
- Label distribution (89% third_party, 9.3% foreground, 1.7% background)

#### 2. Production Monitoring

Track model performance and data drift:

```bash
# Run audit and save predictions
forgetrace audit /path/to/repo --out output/ --save-predictions predictions.jsonl

# Monitor confidence, class distribution, feature drift
python scripts/production_monitor.py \
  --predictions predictions.jsonl \
  --output metrics/ \
  --confidence-threshold 0.70

# Export low-confidence predictions for human review
python scripts/production_monitor.py \
  --predictions predictions.jsonl \
  --export-retraining retraining_candidates.jsonl
```

**Monitoring Outputs:**
- `metrics/monitoring_results.json` - Full analysis results
- `metrics/confidence_distribution.png` - Confidence score histogram
- `metrics/class_distribution.png` - Training vs production class ratios
- `metrics/feature_drift.png` - Top 10 drifted features
- `retraining_candidates.jsonl` - Low-confidence cases for retraining

#### 3. Feedback Loop for Continuous Improvement

```bash
# 1. Export uncertain predictions
python scripts/production_monitor.py \
  --predictions predictions.jsonl \
  --export-retraining review_queue.jsonl \
  --confidence-threshold 0.70

# 2. Human reviewers label exported cases
# Edit review_queue.jsonl: Set "human_label": "foreground|third_party|background"

# 3. Append corrected examples to training dataset
cat review_queue.jsonl >> training_output/dataset/training_dataset.jsonl

# 4. Retrain when >1,000 new examples accumulated
python scripts/train_random_forest.py \
  --data training_output/dataset/training_dataset.jsonl \
  --output models/ip_classifier_v2025.12.01.pkl
```

### See Full Documentation

**Comprehensive ML classifier guide**: [docs/ML_CLASSIFIER.md](docs/ML_CLASSIFIER.md)

**Model card with full specifications**: [docs/MODEL_CARD.md](docs/MODEL_CARD.md)

Covers:
- Feature engineering details (53 features with importance rankings)
- Training workflow and dataset composition (54 repos, 5 phases)
- Confidence scoring and thresholds
- Performance metrics (99.9% accuracy, per-class precision/recall)
- Production deployment best practices
- Known limitations and ethical considerations

## Interpreting Results

### IP Classification

- **third_party**: Open-source or commercial packages
- **foreground**: New code created during engagement
- **background**: Pre-existing developer code (highest legal risk)
- **unknown**: Requires manual review

**With ML enabled**, each classification includes:
- **Confidence score** (0.0-1.0): How certain the model is
- **Review flag**: Low confidence predictions flagged for human review
- **Probability distribution**: Likelihood of each class

### Rewriteability Score

- **> 0.7**: Easy to rewrite (low complexity, well-tested)
- **0.4 - 0.7**: Moderate effort required
- **< 0.4**: High complexity or coupling

### Cost Estimate

Conservative estimate for clean-room rewrite of foreground code based on:
- Lines of code
- Complexity multiplier
- Configured hourly rate

## Troubleshooting

**No SBOM generated**: Install Syft or ensure package manifests exist

**License detection incomplete**: Install ScanCode Toolkit

**PDF generation fails**: Install WeasyPrint: `pip install weasyprint`

**Secrets scan skipped**: Install TruffleHog and/or Gitleaks

## Support

Contact: peter@beaconagile.net
