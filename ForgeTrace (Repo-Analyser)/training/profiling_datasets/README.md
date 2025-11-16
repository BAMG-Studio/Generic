# Client Profiling Datasets

This directory contains anonymized profiling datasets from real client engagements to ensure ForgeTrace handles diverse repository patterns.

## Purpose

- **Validation**: Test ForgeTrace against real-world edge cases
- **Benchmarking**: Measure performance on client-representative data
- **Training**: Improve ML classifier with diverse examples

## Dataset Structure

```
profiling_datasets/
├── catalog.yaml           # Central registry of all profiles
├── client_profile_1/      # Anonymized client dataset
│   ├── metadata.yaml      # Profile characteristics
│   ├── samples/           # Code samples (100-200 files)
│   └── expected_results.json  # Ground truth for validation
├── client_profile_2/
│   └── ...
└── README.md              # This file
```

## Adding New Client Profiles

### Step 1: Anonymize Client Repository

```bash
# Clone client repo
git clone https://github.com/client/project.git /tmp/client-repo
cd /tmp/client-repo

# Remove sensitive data
rm -rf .env secrets/ credentials/ config/production.yaml

# Anonymize git history
git filter-branch --env-filter '
  export GIT_AUTHOR_NAME="Developer"
  export GIT_AUTHOR_EMAIL="dev@example.com"
  export GIT_COMMITTER_NAME="Developer"
  export GIT_COMMITTER_EMAIL="dev@example.com"
' --all

# Remove remote tracking
git remote remove origin
```

### Step 2: Extract Representative Samples

```bash
# Use profiling extractor
python scripts/extract_profile_samples.py \
  --input /tmp/client-repo \
  --output training/profiling_datasets/client_profile_N/ \
  --sample-size 150 \
  --seed 42

# Output:
# - 150 representative files sampled
# - Metadata extracted
# - Directory structure preserved
```

### Step 3: Document Profile Characteristics

Create `metadata.yaml`:

```yaml
# training/profiling_datasets/client_profile_N/metadata.yaml

profile_id: "client_profile_N"
source: "Client N - Industry Sector"
date_created: "2025-11-16"
anonymized: true

characteristics:
  repo_type: "monorepo"
  primary_languages: ["Python", "TypeScript", "Go"]
  total_files: 3450
  total_loc: 284000
  
  edge_cases:
    - type: "monorepo"
      description: "50 microservices in single repo"
    - type: "graphql_codegen"
      description: "Auto-generated TypeScript types"
      patterns: ["*.generated.ts"]
    - type: "vendored_deps"
      description: "Vendored jQuery and Bootstrap"
      paths: ["vendor/"]
  
  dependencies:
    package_manager: "npm"
    total_packages: 340
    vendored: true
  
  architecture:
    microservices_count: 50
    shared_libraries: 8
    uses_submodules: false
    uses_git_lfs: true

sample_strategy:
  method: "stratified"  # Stratified sampling across languages
  sample_size: 150
  language_distribution:
    python: 60
    typescript: 50
    go: 30
    yaml: 10
  seed: 42

expected_metrics:
  # Ground truth for validation
  third_party_percentage: 55.2
  foreground_percentage: 38.4
  background_percentage: 6.4
  total_dependencies: 340
  high_risk_licenses: 2
```

### Step 4: Generate Expected Results

```bash
# Run manual audit for ground truth
forgetrace audit training/profiling_datasets/client_profile_N/samples/ \
  --out training/profiling_datasets/client_profile_N/ground_truth/ \
  --config config.yaml

# Extract key metrics
python scripts/extract_ground_truth.py \
  --audit training/profiling_datasets/client_profile_N/ground_truth/audit.json \
  --output training/profiling_datasets/client_profile_N/expected_results.json
```

### Step 5: Update Catalog

Add entry to `catalog.yaml`:

```yaml
# training/profiling_datasets/catalog.yaml

datasets:
  client_profile_1:
    source: "Client A - FinTech SaaS"
    characteristics: [monorepo, graphql_codegen, typescript_heavy]
    files: 150
    size_mb: 25
    edge_cases: [multiple_languages_per_file, generated_graphql_types]
    
  client_profile_N:
    source: "Client N - Industry Sector"
    characteristics: [monorepo, microservices, vendored_deps]
    files: 150
    size_mb: 32
    edge_cases: [50_microservices, vendored_jquery, graphql_codegen]
```

## Running Benchmarks

### Individual Profile

```bash
# Test single client profile
pytest tests/performance/test_client_profiles.py::test_client_profile_N -v

# Expected output:
# ✅ Accuracy: 99.6% (target: >99%)
# ✅ Latency: 9ms/file (target: <10ms)
# ✅ Memory: 380 MB (target: <500MB)
```

### All Profiles

```bash
# Benchmark all client profiles
pytest tests/performance/test_client_profiles.py --benchmark-only

# Generate report
pytest tests/performance/test_client_profiles.py \
  --benchmark-json=benchmark_results.json

# View results
python scripts/analyze_benchmark_results.py benchmark_results.json
```

## Validation Criteria

Each profile must meet:

| Metric | Target | Critical |
|--------|--------|----------|
| Classification Accuracy | >99% | Yes |
| Latency per File | <10ms | No |
| Memory Usage | <500MB | No |
| License Detection Rate | >95% | Yes |
| SBOM Completeness | >98% | Yes |

## Privacy & Security

### Data Protection

- ✅ All client code anonymized (git history rewritten)
- ✅ No secrets, credentials, or PII included
- ✅ Company-specific references removed
- ✅ File paths generalized (e.g., `src/` instead of `acme_corp/`)

### Storage

- ✅ Stored in private GitHub repository only
- ✅ Not included in public distribution
- ✅ Excluded from Docker images (`.dockerignore`)
- ✅ DVC-tracked, not committed directly to Git

### Access Control

- 🔒 Access limited to core development team
- 🔒 Client consent obtained before profiling
- 🔒 Retention period: 2 years after engagement

## Current Profiles

<!-- Update this section when adding profiles -->

| Profile ID | Source | Files | Languages | Edge Cases |
|------------|--------|-------|-----------|------------|
| _None yet_ | Add your first profile! | - | - | - |

<!-- Example:
| client_profile_1 | FinTech SaaS | 150 | Python, TS | Monorepo, GraphQL |
| client_profile_2 | E-commerce | 120 | PHP, JS | Legacy, Minified | 
-->

## Scripts

### extract_profile_samples.py

Samples representative files from a repository:

```bash
python scripts/extract_profile_samples.py \
  --input /path/to/repo \
  --output training/profiling_datasets/profile_N/ \
  --sample-size 150 \
  --strategy stratified  # or random, weighted
  --seed 42
```

### extract_ground_truth.py

Extracts validation metrics from audit results:

```bash
python scripts/extract_ground_truth.py \
  --audit ground_truth/audit.json \
  --output expected_results.json
```

## Contributing

When adding client profiles:

1. Ensure client consent and anonymization
2. Follow naming convention: `client_profile_N`
3. Document all edge cases in `metadata.yaml`
4. Validate against benchmark criteria
5. Update this README and `catalog.yaml`

## Contact

Questions about profiling datasets:
- **Maintainer**: Peter Kolawole
- **Email**: peter@beaconagile.net

---

**Last Updated**: 2025-11-16
