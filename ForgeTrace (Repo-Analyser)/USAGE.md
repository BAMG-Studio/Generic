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
forgetrace audit /path/to/target-repo --out ./results

# With custom config
forgetrace audit /path/to/repo --out ./out --config my-config.yaml

# Specify tool paths
forgetrace audit /path/to/repo \
  --syft /usr/local/bin/syft \
  --scancode scancode \
  --semgrep semgrep \
  --trufflehog trufflehog \
  --gitleaks gitleaks
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

## Example Workflow

```bash
# 1. Audit a client repository
forgetrace audit /path/to/client-repo --out ./client-audit

# 2. Review outputs
cat ./client-audit/ip_contribution_table.md
open ./client-audit/report.html

# 3. Share with client
# Send report.pdf and ip_contribution_table.md
```

## Interpreting Results

### IP Classification

- **third_party**: Open-source or commercial packages
- **foreground**: New code created during engagement
- **background**: Pre-existing developer code
- **unknown**: Requires manual review

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
