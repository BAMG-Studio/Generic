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

## Output Files

After running an audit, you'll find:

- `audit.json` - Complete findings in JSON format
- `ip_contribution_table.md` - Negotiation-ready Markdown table
- `report.html` - Interactive HTML report
- `report.pdf` - Comprehensive PDF report (if WeasyPrint installed)

## Configuration

Edit `config.yaml` to customize:

- **Scoring weights**: Adjust novelty, complexity, ownership, criticality
- **Similarity thresholds**: Control duplicate detection sensitivity
- **Cost parameters**: Set hourly rate, days per KLOC, complexity multiplier
- **Tool paths**: Specify custom locations for external tools
- **Vulnerability filters**: Tune OSV noise suppression via `min_cvss_*`, `confidence_floor`, and severity weights

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

ForgeTrace now supports **machine learning classification** for intelligent code origin detection.

### Quick Start

1. **Install ML dependencies:**
   ```bash
   pip install scikit-learn numpy
   ```

2. **Enable in config.yaml:**
   ```yaml
   ml_classifier:
     enabled: true
     confidence_threshold: 0.7
   ```

3. **Bootstrap training data:**
   ```bash
   # Run audits on 5-10 repositories with known IP status
   forgetrace audit /path/to/repo1 --output-dir output1
   forgetrace audit /path/to/repo2 --output-dir output2
   
   # Export training examples
   python -c "from forgetrace.classifiers import MLIPClassifier; ..."
   ```

4. **Train model:**
   ```bash
   python -m forgetrace.classifiers.train_model training_data.jsonl
   ```

5. **Run with ML:**
   ```bash
   forgetrace audit /path/to/repo --output-dir output
   # Automatically uses trained model
   ```

### See Full Documentation

**Comprehensive ML classifier guide**: [docs/ML_CLASSIFIER.md](docs/ML_CLASSIFIER.md)

Covers:
- Feature engineering details (23 features)
- Training workflow and best practices
- Confidence scoring and thresholds
- Performance tuning and troubleshooting
- Advanced topics (cross-project generalization, model versioning)

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
