# Repository Analyzer - Enhanced Features

## Version 3.0.0 - October 25, 2025

### 🎯 New Enhancements

This version includes major enhancements to metadata tracking, cost analysis, and code metrics.

## 1. Enhanced Metadata Tracking

### Session History
The analyzer now maintains a complete history of all analysis sessions:

```json
{
  "session_id": "20251025_HHMMSS_RepoName",
  "timestamp": "20251025_HHMMSS",
  "created_at": "2025-10-25T10:26:54.123456",
  "repository": {
    "name": "RepoName",
    "url": "https://github.com/owner/repo.git",
    "platform": "github"
  },
  "contributors": {
    "user@email.com": {
      "commits": 1234,
      "additions": 50000,
      "deletions": 10000,
      "first_seen": "2025-01-01T00:00:00",
      "last_seen": "2025-10-25T10:26:54"
    }
  },
  "analysis_results": {
    "total_dependencies": 626,
    "total_commits": 13973000,
    "total_contributors": 331,
    "estimated_cost": 14346825597.74,
    "scc_metrics": { ... },
    "git_prime_metrics": { ... }
  }
}
```

### Contributor Tracking
- **Cross-session tracking**: Contributors tracked across all analysis sessions
- **Contribution metrics**: Commits, additions, deletions per contributor
- **Timeline tracking**: First and last seen dates for each contributor
- **Session correlation**: See which sessions each contributor participated in

### Session History File
Located at `output/session_history.json`, contains:
- Last 100 analysis sessions
- Sorted by date (newest first)
- Enables trend analysis over time

## 2. SCC Integration (Sloc Cloc and Code)

### What is SCC?
SCC is a fast, accurate code counter with complexity calculations. It provides:
- Accurate lines of code counting (200+ languages)
- Code complexity analysis
- Comment and blank line detection
- COCOMO II cost estimation
- Language breakdown statistics

### Installation
See [INSTALL_SCC.md](INSTALL_SCC.md) for detailed installation instructions.

Quick install:
```bash
wget https://github.com/boyter/scc/releases/download/v3.1.0/scc_3.1.0_Linux_x86_64.tar.gz
tar -xzf scc_3.1.0_Linux_x86_64.tar.gz
sudo mv scc /usr/local/bin/
```

### SCC Metrics Tracked
```json
{
  "scc": {
    "total_lines": 1500000,
    "total_code": 1200000,
    "total_comments": 200000,
    "total_blanks": 100000,
    "total_complexity": 45000,
    "total_bytes": 50000000,
    "kloc": 1200.0,
    "languages": {
      "TypeScript": {
        "files": 1500,
        "lines": 500000,
        "code": 400000,
        "comments": 80000,
        "blanks": 20000,
        "complexity": 15000,
        "bytes": 20000000
      },
      "...": "..."
    }
  }
}
```

## 3. Git Prime Analysis

### Development Velocity Metrics
The analyzer now includes git-prime-style analysis:

```json
{
  "git_prime": {
    "commits_by_author": {
      "John Doe": 5000,
      "Jane Smith": 3000
    },
    "lines_by_author": {
      "john@example.com": {
        "additions": 150000,
        "deletions": 50000
      },
      "jane@example.com": {
        "additions": 100000,
        "deletions": 30000
      }
    },
    "total_additions": 250000,
    "total_deletions": 80000,
    "total_churn": 330000
  }
}
```

### Code Churn Analysis
- **Total Churn**: Sum of all additions and deletions
- **Per-Author Breakdown**: See individual contributor impact
- **Velocity Tracking**: Understand development pace

## 4. Enhanced Cost Analysis

### Comprehensive Metrics
```json
{
  "cost_analysis": {
    "cocomo": {
      "kloc": 1200.0,
      "effort_months": 4523.45,
      "effort_hours": 687404.40,
      "estimated_cost": 68740440.00,
      "hourly_rate": 100.0,
      "development_time_months": 13.66
    },
    "metrics": {
      "total_commits": 13973000,
      "total_contributors": 331,
      "total_dependencies": 626,
      "commits_per_contributor": 42214.50,
      "commits_per_dependency": 22321.09,
      "cost_per_dependency": 109808.03,
      "cost_per_commit": 4.92,
      "lines_per_dependency": 1916.93,
      "complexity_per_kloc": 37.50
    },
    "summary": {
      "estimated_cost": 68740440.00,
      "estimated_hours": 687404.40,
      "total_lines": 1500000,
      "total_code": 1200000,
      "total_complexity": 45000,
      "code_churn": 330000,
      "dependencies_commits_ratio": "626:13973000"
    }
  }
}
```

### New Calculated Metrics
- **Cost per Commit**: How much each commit costs
- **Lines per Dependency**: Code volume per dependency
- **Complexity per KLOC**: Complexity density
- **Code Churn**: Total code changes (additions + deletions)

## 5. API Usage

### Creating Session with Metadata
```python
from utils.output_manager import create_organized_output

# Create session with contributor tracking
session = create_organized_output(
    repo_name="MyProject",
    repo_url="https://github.com/owner/myproject.git",
    platform="github",
    contributors={
        "user@email.com": {
            "commits": 100,
            "additions": 5000,
            "deletions": 1000
        }
    },
    analysis_metadata={
        "total_dependencies": 50,
        "total_commits": 1000,
        "total_contributors": 5,
        "estimated_cost": 500000.00
    }
}
```

### Getting Session History
```python
from utils.output_manager import get_session_history, get_contributor_history

# Get all sessions
history = get_session_history()

# Get contributor history for specific repo
contributor_data = get_contributor_history(
    "https://github.com/owner/myproject.git"
)
```

### Running Cost Analysis
```python
from utils.cost_calculator import CostCalculator

calc = CostCalculator({
    'hourly_rate': 150.0,
    'cocomo_params': {
        'a': 2.94,
        'b': 1.14,
        'monthly_hours': 152
    }
})

# Comprehensive analysis
results = calc.calculate_comprehensive_cost(
    repo_path="/path/to/repo",
    commits=5000,
    contributors=10,
    dependencies=100
)
```

## 6. Report Enhancements

All report formats (JSON, HTML, PDF, SBOM) now include:

### Enhanced Summary Section
- SCC code metrics
- Git prime development velocity
- Contributor breakdown
- Language distribution
- Complexity analysis

### New Metrics in Reports
- Total lines (not just code)
- Code complexity scores
- Code churn statistics
- Per-language breakdowns
- Author contribution stats

## 7. Backward Compatibility

All existing functionality remains:
- ✅ Universal project detection
- ✅ COCOMO II cost estimation
- ✅ Dependency tracking
- ✅ Multiple export formats
- ✅ Session-based organization

New features are additive and don't break existing workflows.

## 8. Usage Examples

### Basic Analysis
```bash
cd /home/papaert/projects/lab/repo-analyzer
source venv/bin/activate
python src/analyze.py https://github.com/owner/repo.git --verbose
```

### View Latest Session
```bash
ls -la output/latest/
cat output/latest/metadata.json
```

### Check Session History
```bash
cat output/session_history.json | jq '.[] | {session_id, created_at, repo: .repository.name}'
```

### View SCC Metrics
```bash
cat output/latest/reports/*_report.json | jq '.cost_analysis.scc'
```

### View Git Prime Metrics
```bash
cat output/latest/reports/*_report.json | jq '.cost_analysis.git_prime'
```

## 9. Performance Notes

- **SCC**: Analyzes large repos in seconds (written in Go)
- **Git Prime**: Uses native git commands for speed
- **Caching**: Session history cached for quick lookups
- **Pagination**: GitHub API properly paginated for large repos

## 10. Future Enhancements

Planned for future versions:
- [ ] Trend analysis dashboard
- [ ] Cost prediction based on historical data
- [ ] Team productivity metrics
- [ ] Integration with CI/CD pipelines
- [ ] Real-time cost tracking
- [ ] Dependency security scoring
- [ ] License compliance checking

## Questions?

See the main [README.md](README.md) for general usage or create an issue on GitHub.
