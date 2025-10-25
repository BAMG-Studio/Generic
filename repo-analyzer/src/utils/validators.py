"""Validators for inputs"""
import re
from urllib.parse import urlparse


def validate_repo_url(url: str) -> bool:
    """
    Validate repository URL format
    
    Args:
        url: Repository URL to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not url:
        return False
    
    # Parse URL
    parsed = urlparse(url)
    
    # Check if it's a valid URL
    if not parsed.scheme or not parsed.netloc:
        return False
    
    # Check for GitHub or GitLab
    valid_hosts = [
        'github.com',
        'gitlab.com',
        'gitlab'  # For self-hosted GitLab
    ]
    
    if not any(host in parsed.netloc for host in valid_hosts):
        return False
    
    # Check path has at least owner/repo
    path_parts = [p for p in parsed.path.split('/') if p]
    if len(path_parts) < 2:
        return False
    
    return True


def validate_github_token(token: str) -> bool:
    """
    Validate GitHub token format
    
    Args:
        token: GitHub token to validate
        
    Returns:
        True if format is valid
    """
    if not token:
        return False
    
    # GitHub tokens start with ghp_ (personal), gho_ (OAuth), or ghs_ (server-to-server)
    return token.startswith(('ghp_', 'gho_', 'ghs_', 'github_pat_'))


def validate_gitlab_token(token: str) -> bool:
    """
    Validate GitLab token format
    
    Args:
        token: GitLab token to validate
        
    Returns:
        True if format is valid
    """
    if not token:
        return False
    
    # GitLab tokens are typically 20-26 character alphanumeric strings
    # or start with glpat-
    if token.startswith('glpat-'):
        return True
    
    return bool(re.match(r'^[a-zA-Z0-9_-]{20,26}$', token))
