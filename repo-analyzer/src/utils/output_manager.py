"""Output directory organization and session management with history tracking"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


def get_session_history(base_dir: str = './output') -> List[Dict[str, Any]]:
    """
    Get complete session history
    
    Args:
        base_dir: Base output directory
        
    Returns:
        List of all session metadata sorted by date (newest first)
    """
    base_path = Path(base_dir)
    history_file = base_path / 'session_history.json'
    
    if history_file.exists():
        with open(history_file, 'r') as f:
            return json.load(f)
    
    return []


def update_session_history(
    session_metadata: Dict[str, Any],
    base_dir: str = './output'
) -> None:
    """
    Update session history with new session
    
    Args:
        session_metadata: Metadata for current session
        base_dir: Base output directory
    """
    base_path = Path(base_dir)
    base_path.mkdir(parents=True, exist_ok=True)
    history_file = base_path / 'session_history.json'
    
    # Load existing history
    history = get_session_history(base_dir)
    
    # Add new session at the beginning
    history.insert(0, session_metadata)
    
    # Keep last 100 sessions
    history = history[:100]
    
    # Save updated history
    with open(history_file, 'w') as f:
        json.dump(history, f, indent=2)


def get_contributor_history(
    repo_url: str,
    base_dir: str = './output'
) -> Dict[str, Any]:
    """
    Get contributor history for a specific repository
    
    Args:
        repo_url: Repository URL
        base_dir: Base output directory
        
    Returns:
        Contributor history aggregated across all sessions
    """
    history = get_session_history(base_dir)
    
    contributors = {}
    total_commits = 0
    sessions_count = 0
    
    for session in history:
        if session.get('repository', {}).get('url') == repo_url:
            sessions_count += 1
            session_contributors = session.get('contributors', {})
            session_commits = session.get('analysis_results', {}).get('total_commits', 0)
            total_commits += session_commits
            
            # Aggregate contributor data
            for contributor, data in session_contributors.items():
                if contributor not in contributors:
                    contributors[contributor] = {
                        'total_commits': 0,
                        'first_seen': session.get('created_at'),
                        'last_seen': session.get('created_at'),
                        'sessions': []
                    }
                
                contributors[contributor]['total_commits'] += data.get('commits', 0)
                contributors[contributor]['last_seen'] = session.get('created_at')
                contributors[contributor]['sessions'].append(session.get('session_id'))
    
    return {
        'repository_url': repo_url,
        'total_sessions': sessions_count,
        'total_commits_tracked': total_commits,
        'contributors': contributors,
        'last_updated': datetime.now().isoformat()
    }


def create_organized_output(
    repo_name: str,
    repo_url: str,
    platform: str,
    base_dir: str = './output',
    contributors: Optional[Dict[str, Any]] = None,
    analysis_metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, str]:
    """
    Create organized output directory structure with session management
    
    Structure:
    output/
      ├── YYYYMMDD_HHMMSS_RepoName/     # Session directory
      │   ├── reports/                   # HTML, JSON, PDF reports
      │   ├── sbom/                      # SBOM files (JSON/XML)
      │   ├── raw_data/                  # Raw API responses
      │   ├── logs/                      # Analysis logs
      │   └── metadata.json              # Session metadata
      └── latest -> YYYYMMDD_HHMMSS_RepoName/  # Symlink to latest session
    
    Args:
        repo_name: Repository name
        repo_url: Repository URL
        platform: Platform (github/gitlab)
        base_dir: Base output directory
        
    Returns:
        Dictionary with paths to all created directories
    """
    base_path = Path(base_dir)
    base_path.mkdir(parents=True, exist_ok=True)
    
    # Create session ID
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    session_id = f"{timestamp}_{repo_name}"
    
    # Create session directory
    session_path = base_path / session_id
    session_path.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories
    reports_dir = session_path / 'reports'
    sbom_dir = session_path / 'sbom'
    raw_data_dir = session_path / 'raw_data'
    logs_dir = session_path / 'logs'
    
    for directory in [reports_dir, sbom_dir, raw_data_dir, logs_dir]:
        directory.mkdir(parents=True, exist_ok=True)
    
    # Create metadata file with enhanced tracking
    metadata = {
        'session_id': session_id,
        'timestamp': timestamp,
        'created_at': datetime.now().isoformat(),
        'repository': {
            'name': repo_name,
            'url': repo_url,
            'platform': platform
        },
        'structure': {
            'base_dir': str(session_path),
            'reports_dir': str(reports_dir),
            'sbom_dir': str(sbom_dir),
            'raw_data_dir': str(raw_data_dir),
            'logs_dir': str(logs_dir)
        },
        'contributors': contributors or {},
        'analysis_results': analysis_metadata or {},
        'version': '3.0.0'
    }
    
    metadata_file = session_path / 'metadata.json'
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    # Update session history
    update_session_history(metadata, base_dir)
    
    # Create/update 'latest' symlink
    latest_link = base_path / 'latest'
    if latest_link.exists() or latest_link.is_symlink():
        latest_link.unlink()
    latest_link.symlink_to(session_id, target_is_directory=True)
    
    # Create README in session directory
    readme_content = f"""# Analysis Session: {repo_name}

**Repository:** {repo_url}
**Platform:** {platform}
**Session ID:** {session_id}
**Created:** {metadata['created_at']}

## Directory Structure

- `reports/` - Analysis reports (JSON, HTML, PDF)
- `sbom/` - Software Bill of Materials (CycloneDX format)
- `raw_data/` - Raw API responses and intermediate data
- `logs/` - Analysis execution logs
- `metadata.json` - Session metadata

## Quick Access

View the latest reports in the `reports/` directory:
- JSON: Full machine-readable analysis
- HTML: Interactive web report
- PDF: Printable summary report

SBOM files in `sbom/`:
- JSON: CycloneDX JSON format
- XML: CycloneDX XML format
"""
    
    readme_file = session_path / 'README.md'
    with open(readme_file, 'w') as f:
        f.write(readme_content)
    
    return {
        'session_id': session_id,
        'base_dir': str(session_path),
        'reports_dir': str(reports_dir),
        'sbom_dir': str(sbom_dir),
        'raw_data_dir': str(raw_data_dir),
        'logs_dir': str(logs_dir),
        'metadata_file': str(metadata_file),
        'readme_file': str(readme_file),
        'latest_link': str(latest_link)
    }


def get_latest_session(base_dir: str = './output') -> Dict[str, str]:
    """
    Get the latest analysis session
    
    Args:
        base_dir: Base output directory
        
    Returns:
        Dictionary with paths to latest session directories
        
    Raises:
        FileNotFoundError: If no sessions exist
    """
    base_path = Path(base_dir)
    latest_link = base_path / 'latest'
    
    if not latest_link.exists():
        raise FileNotFoundError("No analysis sessions found")
    
    session_path = latest_link.resolve()
    
    return {
        'base_dir': str(session_path),
        'reports_dir': str(session_path / 'reports'),
        'sbom_dir': str(session_path / 'sbom'),
        'raw_data_dir': str(session_path / 'raw_data'),
        'logs_dir': str(session_path / 'logs'),
        'metadata_file': str(session_path / 'metadata.json')
    }


def list_sessions(base_dir: str = './output') -> List[Dict[str, Any]]:
    """
    List all analysis sessions
    
    Args:
        base_dir: Base output directory
        
    Returns:
        List of session metadata dictionaries
    """
    base_path = Path(base_dir)
    
    if not base_path.exists():
        return []
    
    sessions = []
    for item in base_path.iterdir():
        if item.is_dir() and item.name != 'latest':
            metadata_file = item / 'metadata.json'
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                    sessions.append(metadata)
    
    # Sort by created_at descending
    sessions.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    return sessions
