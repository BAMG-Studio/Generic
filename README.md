# ForgeTrace: ML-Powered IP Audit & Provenance Analysis Platform

**Production-grade IP forensics for M&A, clean-room rewrites, and continuous compliance.**

ForgeTrace blends static analysis, Git forensics, and ML-powered IP classification (99.9% accuracy on 131,731 training examples) to answer the hardest diligence question: _"What code did your team write vs. what came from open source or prior employers?"_

---

## Table of Contents

1. [What ForgeTrace Does](#what-forgetrace-does)
2. [Quick Start (5 Minutes)](#quick-start-5-minutes)
3. [ForgeTrace App & Developer Portal](#forgetrace-app--developer-portal)
4. [Scenarios & Workflows](#scenarios--workflows)
5. [Outputs & Reports](#outputs--reports)
6. [Platform Capabilities](#platform-capabilities)
7. [Advanced Configuration](#advanced-configuration)
8. [Learning Resources & Support](#learning-resources--support)

---

## What ForgeTrace Does

### The Problem

- Manual code provenance audits take weeks, cost $50K–$500K, and still miss hidden risks (license conflicts, CVEs, leaked secrets, background IP).
- Legal, finance, and compliance teams need evidence-backed answers _before_ closing an acquisition or shipping regulated software.

### The ForgeTrace Solution

- End-to-end automation of the IP audit workflow in minutes.
- ML classifier, SBOM generation, vulnerability scanning, license detection, and rewriteability scoring in one toolchain.
- Outputs a defensible evidence pack that legal teams, investors, and regulators trust.

#### Typical engagement outcomes

- Price adjustments based on real IP composition
- Clean-room rewrite prioritization with rewriteability scores
- Continuous PR compliance with GitHub/GitLab/Gerrit hooks

---

## Quick Start (5 Minutes)

### Installation

```bash
# Clone repository
git clone https://github.com/BAMG-Studio/Generic.git
cd Generic

# Install core dependencies
pip install -e .

# Verify installation
forgetrace --version
# Output: ForgeTrace v0.4.0 (ML Classifier: 99.9% accuracy)
```

### Your First Audit

```bash
# Audit any Git repository
forgetrace audit /path/to/your-repo --out ./audit_results

# Real-world example
git clone https://github.com/django/django.git
forgetrace audit ./django --out ./django_audit
```

Console snapshot:

```text
🔍 Scanning repository...
├─ Git history: 45,123 commits analyzed
├─ License detection: 1,247 files scanned
├─ SBOM generation: 89 dependencies identified
├─ Vulnerability scan: 3 medium CVEs found
├─ Secret detection: 0 credentials leaked ✅
└─ ML classification: 1,247 files classified

📊 IP Contribution Summary:
├─ Foreground IP:   892 files (71.5%)
├─ Third-Party IP:  338 files (27.1%)
└─ Background IP:    17 files (1.4%)

✅ Audit complete in 47 seconds!
📁 Results saved to: ./django_audit/
```

### Preview the Dashboard

```bash
forgetrace preview ./django_audit --browser
```

What you get:

- File explorer with per-file rationale
- Interactive charts (licenses, vulnerabilities, contributor heatmaps)
- Export options for JSON, CSV, PDF, and slide decks

---

## ForgeTrace App & Developer Portal

### Web Application

Access the ForgeTrace platform at `https://www.forgetrace.pro/app` for:

- **Mission Control** – Real-time dashboard with audit summaries and risk metrics
- **Code DNA** – Interactive file explorer with per-file IP classification
- **Review Queue** – Human-in-the-loop verification for low-confidence predictions
- **Developer Portal** – Manage API tokens, view usage, and integrate with your CI/CD
- **Settings** – Configure analysis thresholds, policies, and integrations

### API Access & Tokens

ForgeTrace provides a RESTful API for programmatic access and automation.

#### Creating an API Token

1. Log in to `https://www.forgetrace.pro/app`
2. Navigate to **Developer** → **API Tokens**
3. Click **Create Token**
4. Assign a name and select scopes (`read:reports`, `write:audits`, etc.)
5. Copy the token immediately (it won't be shown again)

#### Using the API

```bash
# Submit an audit
curl -X POST https://api.forgetrace.pro/v1/audits \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "repository": "https://github.com/org/repo",
    "branch": "main"
  }'

# Get audit status
curl https://api.forgetrace.pro/v1/audits/{audit_id} \
  -H "Authorization: Bearer YOUR_TOKEN"

# Download report
curl https://api.forgetrace.pro/v1/reports/{report_id} \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o report.json
```

#### Rate Limits

- **Free Tier**: 1,000 files/month, 60 requests/minute
- **Pro Tier**: 50,000 files/month, priority queue
- **Enterprise**: Custom quotas, SLA, and dedicated support

See the [Developer Portal](https://www.forgetrace.pro/app/developer) for current usage and limits.

---

## Scenarios & Workflows

### 1. M&A Due Diligence (30-minute workflow)

1. **Run comprehensive audit**

```bash
forgetrace audit target-startup/ \
    --out ma_audit \
    --client "Acquirer Corp" \
    --engagement "Startup XYZ Acquisition" \
    --config config/policies/ma_strict.yaml
```

1. **Review executive summary** with `forgetrace preview ma_audit --browser`
1. **Drill into red flags** (critical CVEs, GPL-3.0 contamination, leaked secrets)
1. **Generate PDF report**

```bash
forgetrace generate-report ma_audit \
    --format pdf \
    --template ma_template \
    --include-remediation-plan
```

1. **Export briefings** for legal, finance, and the seller.

_Outcome:_ evidence-backed negotiation adjustments, remediation plan, escrow recommendations.

### 2. Clean-Room Rewrite (Developer workflow)

- Focus config: `config/policies/rewrite_focus.yaml` (complexity, coupling, rewriteability scoring).
- Dashboards surface high-risk files with rewrite priority, CVE counts, coupling analysis, and estimated effort.
- Automate roadmap export:

```bash
forgetrace export-rewrite-plan rewrite_analysis \
    --format csv \
    --output rewrite_roadmap.csv
```

### 3. Continuous Compliance (DevOps automation)

- GitHub Actions workflow (`.github/workflows/forgetrace-audit.yml`) blocks PRs introducing critical CVEs, GPL-3.0 code, or leaked secrets.
- Policy file `.forgetrace/ci_policy.yaml` drives enforcement rules.
- Violation gate script `.forgetrace/check_violations.py` fails builds and comments on PRs.

### 4. Employee OSS Contribution Audit (Compliance)

- Detect potential company IP drifting into public OSS.
- Run the activity audit:

```bash
forgetrace audit-employee-activity \
    --org-domain "acme-corp.com" \
    --email-pattern "*@acme-corp.com" \
    --output employee_oss_audit.json
```

- Outputs risk-ranked incidents with recommended next steps.

---

## Outputs & Reports

| File | Purpose |
|------|---------|
| `audit.json` | Machine-readable summary for CI/CD pipelines |
| `ip_contribution_table.md` | Negotiation-ready IP table |
| `report.html` | Interactive dashboard with charts/tables |
| `report.pdf` | Compliance-grade PDF (42 pages) |
| `reports/rewrite_roadmap.csv` | Clean-room prioritization |

Artifacts live under `repo_audit/<client>/forgetrace_report/` so each engagement stays isolated. Pair with `repo_audit/<client>/source/` if you need working copies alongside reports.

---

## Platform Capabilities

- **ML IP Classification** – Random Forest trained on 131K examples (Django, Kubernetes, React, etc.).
- **SBOM Generation** – CycloneDX/SPDX via Syft with fallbacks.
- **License Detection** – ScanCode Toolkit, FOSSology, heuristics, SPDX normalization.
- **Git Authorship Analysis** – Mailmap-aware commit attribution, churn metrics.
- **Provenance & Similarity** – N-gram shingles, TLSH, ssdeep, clone detection (SourcererCC, NiCad, JPlag, jscpd).
- **Security Tooling** – TruffleHog, Gitleaks, Semgrep, CVE enrichment, rewriteability scoring.
- **Secrets & Vulnerabilities** – Alerting, remediation guidance, policy enforcement.
- **Outputs & Integrations** – JSON/Markdown/HTML/PDF, GitHub issues export, CI gates, MLflow tracking.

---

## Advanced Configuration

- `config.yaml` – Global scoring weights, thresholds, tool paths.
- Policy packs under `config/policies/*.yaml` tailor audits for M&A, clean-room rewrite, CI, or OSS compliance.
- Custom scoring example (`config/custom_weights.yaml`):
    ```yaml
    scoring:
        ip_classification:
            license_signal: 0.3
            authorship_signal: 0.25
            path_pattern: 0.2
            sbom_match: 0.15
            similarity: 0.1
        rewriteability:
            complexity: 0.3
            coupling: 0.25
            license_risk: 0.2
            vulnerability_density: 0.15
            test_coverage: 0.1
    ```

Refer to `PRODUCTION_READY.md` for the phase-scoped ML training matrix, optimization modes, and DVC/MLflow workflows that keep the classifier at 99.9% accuracy.

---

## Learning Resources & Support

- **Docs**: Architecture guide, ML classifier guide, API reference, troubleshooting (see `docs/`).
- **Videos (planned)**: Getting started, M&A workflow, CI/CD integration, custom policies.
- **Community & Support**

    - FAQ, discussion channels, issue tracker
    - Business inquiries: `hello@bamgstudio.com`
    - Website: `https://bamgstudio.com`

## Credits & License

- Built by Peter Kolawole, BAMG Studio LLC
- Proprietary – All Rights Reserved
