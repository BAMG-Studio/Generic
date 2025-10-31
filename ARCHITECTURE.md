# ForgeTrace Architecture

**Author: Peter Kolawole, BAMG Studio LLC**

## Overview

ForgeTrace is a modular IP audit tool designed to classify repository code into third-party, background, and foreground IP with evidence-based scoring.

## Architecture

```
forgetrace/
├── cli.py              # Command-line interface
├── audit.py            # Main orchestration engine
├── scanners/           # Pluggable scanners
│   ├── sbom.py         # SBOM generation (Syft + fallback)
│   ├── license.py      # License detection (ScanCode + heuristics)
│   ├── git.py          # Git authorship & churn
│   ├── similarity.py   # N-gram shingles + TLSH + ssdeep
│   ├── secrets.py      # TruffleHog + Gitleaks
│   └── sast.py         # Semgrep integration
├── classifiers/        # IP classification & scoring
│   └── ip_classifier.py
└── reporters/          # Multi-format output
    ├── json_reporter.py
    ├── markdown_reporter.py
    ├── html_reporter.py
    └── pdf_reporter.py
```

## Scan Pipeline

1. **SBOM Generation**: Identify third-party packages
2. **License Detection**: Map licenses to files
3. **Git Analysis**: Extract authorship and churn metrics
4. **Similarity**: Detect internal duplication and provenance signals
5. **Secrets**: Flag exposed credentials
6. **SAST**: Security vulnerability scan
7. **Classification**: Categorize as third_party/background/foreground
8. **Scoring**: Rewriteability and cost estimation
9. **Reporting**: JSON, Markdown, HTML, PDF

## Extensibility

- **Scanners**: Add new scanners by implementing `scan()` method
- **Classifiers**: Extend `IPClassifier` for custom logic
- **Reporters**: Add new output formats in `reporters/`

## Configuration

All weights, thresholds, and tool paths are in `config.yaml`.

## Sprint Breakdown

- **Sprint 1**: Foundation (CLI, SBOM, Git, Similarity, basic reporting)
- **Sprint 2**: Compliance (License detection, SPDX alignment)
- **Sprint 3**: Security (Secrets, SAST, provenance)
- **Sprint 4**: Quantification (Scoring, cost estimation, PDF)
