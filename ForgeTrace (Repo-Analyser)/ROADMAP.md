# ForgeTrace Development Roadmap

## Overview

ForgeTrace is evolving from a basic IP audit tool into a comprehensive code intelligence platform. This roadmap tracks our progress through three development phases.

---

## Phase 1: Production-Ready Core (CURRENT)

**Goal**: Deliver enterprise-ready IP auditing with professional reporting

### ✅ Completed Features

#### 1. **PDF Download & Preview** ✅
- Added `forgetrace preview` command with HTTP server
- Auto-browser launch support
- file:// URL printing for accessibility
- **Commit**: b10208e

#### 2. **Metadata Collection** ✅
- CLI flags: `--client-name`, `--engagement-window`, `--prepared-by`, `--contact-email`
- Structured metadata section in config.yaml
- PDF reporter integration with fallback chain
- **Commit**: a249e4b

#### 3. **Type Annotations** ⏳ IN PROGRESS (20%)
- ✅ similarity.py (100% complete)
- ✅ html_reporter.py (80% complete)
- ⏳ pdf_reporter.py (pending)
- ⏳ Other scanners (pending)
- **Goal**: Improve IDE experience, catch errors early

#### 4. **Multi-Source Vulnerability Scanner** ✅ NEW!
- OSV (Open Source Vulnerabilities) integration
- GitHub Advisory Database support
- OWASP Dependency-Check optional integration
- **Ecosystems**: Python, Node.js, Go, Ruby
- Risk scoring with CVSS-based priority levels
- Full type annotations and documentation
- **Commit**: 06f9274
- **Docs**: `docs/VULNERABILITY_SCANNING.md`

### 🔄 Remaining Phase 1 Tasks

1. **Complete Type Annotations**
   - Priority: HIGH
   - Files: pdf_reporter.py, git.py, sbom.py, license.py, sast.py, secrets.py
   - Estimated: 2-3 days

2. **End-to-End Testing**
   - Test metadata collection workflow
   - Validate vulnerability scanning across ecosystems
   - Performance benchmarks
   - Estimated: 1 day

3. **Documentation Updates**
   - Update README.md with vulnerability scanning
   - Add CLI usage examples
   - Create troubleshooting guide
   - Estimated: 1 day

---

## Phase 2: Advanced Intelligence (NEXT)

**Goal**: Add ML-based classification and advanced analytics

### Priority Features

#### 1. **ML-Based IP Classification** 🎯 HIGH PRIORITY
**Current State**: Rule-based heuristics  
**Target**: Machine learning classifier with confidence scoring

**Components**:
- Feature extraction from code patterns
- Training on labeled datasets
- Confidence scoring (0-1)
- Human-in-the-loop validation workflow
- Model versioning and retraining

**Tech Stack**:
- scikit-learn for initial model
- Optional: PyTorch for advanced features
- Feature engineering: AST analysis, git metrics, similarity scores

**Estimated Effort**: 2-3 weeks

---

#### 2. **Database Persistence Layer** 🎯 HIGH PRIORITY
**Current State**: File-based JSON reports  
**Target**: Database storage for historical analysis

**Features**:
- Store audit results with timestamps
- Historical comparison views
- Trend analysis over time
- Multi-repo aggregation
- Query API for custom reports

**Schema Design**:
```sql
audits: id, repo_path, timestamp, config_hash
findings: id, audit_id, scanner_type, data_json
metrics: id, audit_id, metric_name, value, timestamp
vulnerabilities: id, audit_id, package, cve_id, severity, risk_score
```

**Tech Stack**:
- SQLite for single-user (default)
- PostgreSQL for enterprise (optional)
- SQLAlchemy ORM
- Alembic for migrations

**Estimated Effort**: 1-2 weeks

---

#### 3. **Policy Engine with YAML Rules** 🎯 MEDIUM PRIORITY
**Current State**: Hardcoded thresholds in config.yaml  
**Target**: Flexible policy-as-code system

**Example Policy**:
```yaml
policies:
  - id: no-gpl-dependencies
    severity: high
    action: block
    condition: license in ['GPL-2.0', 'GPL-3.0']
    message: "GPL dependencies violate company policy"
    
  - id: max-third-party-ratio
    severity: medium
    action: warn
    condition: third_party_percentage > 60
    message: "Third-party code exceeds 60% threshold"
    
  - id: critical-vulnerabilities
    severity: critical
    action: block
    condition: vulnerabilities.CRITICAL > 0
    message: "Critical vulnerabilities must be resolved"
    
  - id: test-coverage
    severity: medium
    action: warn
    condition: test_coverage < 0.70
    message: "Test coverage below 70%"
```

**Features**:
- Policy validation on scan
- Custom actions: block, warn, info
- Policy inheritance (org → team → repo)
- Exemption workflow
- Policy violation reports

**Estimated Effort**: 1 week

---

#### 4. **Background IP Detection** 🎯 MEDIUM PRIORITY
**Current State**: Basic ownership classification  
**Target**: Distinguish developer background IP from foreground contributions

**Algorithm**:
1. Analyze git history for developer patterns
2. Identify "template" code vs custom logic
3. Use similarity analysis to find copied code
4. Score contributions by originality

**Use Case**: Identify when developers bring IP from previous employers

**Estimated Effort**: 1-2 weeks

---

#### 5. **Rewriteability Scoring Logic** 🎯 LOW PRIORITY
**Current State**: Basic LOC-based estimates  
**Target**: Sophisticated rewrite cost prediction

**Factors**:
- Cyclomatic complexity (radon integration)
- Coupling metrics (dependency analysis)
- Test coverage assessment
- Code change frequency (git history)
- External dependency count

**Output**: Risk score (0-10) for rewrite difficulty

**Estimated Effort**: 1 week

---

## Phase 3: Platform Features (FUTURE)

**Goal**: Transform into collaborative security platform

### 1. **Real-Time Monitoring** 🔮
- Git hooks integration
- CI/CD pipeline plugins (GitHub Actions, GitLab CI, Jenkins)
- Webhook triggers for policy violations
- Automated alerts (Slack, email, PagerDuty)

**Estimated Effort**: 2-3 weeks

### 2. **Interactive Web Dashboard** 🔮
- Modern web UI (React/Vue)
- Real-time visualization (Chart.js, D3.js)
- Drill-down into findings
- Comparison views (repo vs repo, time vs time)
- Export capabilities (PDF, CSV, JSON)
- User authentication and RBAC

**Tech Stack**:
- Backend: FastAPI or Flask
- Frontend: React with Material-UI
- Real-time: WebSocket for live updates
- Database: PostgreSQL

**Estimated Effort**: 4-6 weeks

### 3. **Demo Mode** 🔮
- `--demo` flag for showcasing capabilities
- Sample repos with known issues
- Mock data for privacy-sensitive demos
- Interactive tutorial mode

**Estimated Effort**: 1 week

---

## Development Metrics

### Current Stats (as of Nov 3, 2025)
- **Total Commits**: 3 major features
- **Lines of Code**: ~3,500 (estimated)
- **Test Coverage**: TBD (tests needed)
- **Type Coverage**: ~20% (improving)
- **Documentation**: 4 guides + inline docs

### Velocity
- **Phase 1 Progress**: 70% complete
- **Average Feature Time**: 1-2 days
- **Target Phase 1 Completion**: Nov 15, 2025
- **Target Phase 2 Completion**: Dec 15, 2025

---

## Contributing

To contribute to this roadmap:

1. Review the priority levels 🎯
2. Pick a feature that matches your expertise
3. Create an issue on GitHub with proposal
4. Fork, develop, and submit PR
5. Update this roadmap with progress

---

## Questions & Feedback

**Email**: peter@beaconagile.net  
**Organization**: BAMG Studio LLC  
**Project**: ForgeTrace - Intelligent IP Auditing Platform
