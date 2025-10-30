# ForgeTrace (Repo-Analyser)

**Comprehensive IP Audit & Provenance Analysis Tool**

ForgeTrace is a production-grade repository auditor that separates third-party components, developer background IP, and foreground contributions to produce evidence-based IP contribution tables for negotiations and clean-room rewrites.

## Features

- **SBOM Generation**: CycloneDX/SPDX via Syft with intelligent fallbacks
- **License Detection**: ScanCode Toolkit + FOSSology integration + heuristics
- **Git Authorship**: Detailed commit analysis with mailmap support
- **Provenance Analysis**: N-gram shingles + TLSH + ssdeep similarity detection
- **Secrets Scanning**: TruffleHog + Gitleaks integration
- **SAST**: Semgrep security analysis
- **Clone Detection**: Hooks for SourcererCC, NiCad, JPlag, jscpd
- **Rewriteability Scoring**: Complexity, coupling, license risk assessment
- **Multi-Format Output**: JSON, Markdown, HTML, PDF reports

## Quick Start

```bash
# Install
pip install -e .

# Run audit
forgetrace audit /path/to/repo --out ./results --config config.yaml

# With external tools
forgetrace audit /path/to/repo --syft $(which syft) --scancode scancode
```

## Installation

```bash
# Core tool
pip install -e .

# Optional external tools
./scripts/install_tools.sh
```

## Output Files

- `audit.json` - Complete findings
- `ip_contribution_table.md` - Negotiation-ready table
- `report.html` - Interactive report
- `report.pdf` - Comprehensive PDF

## Configuration

Edit `config.yaml` to adjust scoring weights, thresholds, and tool paths.

## Author

Peter Kolawole, BAMG Studio LLC

## License

Proprietary - All Rights Reserved
