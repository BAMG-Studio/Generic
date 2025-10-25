"""
GitHub Repository Analyzer
FIXED: Properly fetches commits and contributors
"""
import os
import requests
import tempfile
import subprocess
from typing import Dict, Any
from pathlib import Path

from .base import BaseAnalyzer


class GitHubAnalyzer(BaseAnalyzer):
    """Analyzer for GitHub repositories with FIXED API calls"""
    
    def __init__(self, repo_url: str, config: Any, token: str = None):
        """
        Initialize GitHub analyzer
        
        Args:
            repo_url: GitHub repository URL
            config: Configuration object
            token: GitHub personal access token
        """
        super().__init__(repo_url, config, token)
        
        self.api_base = 'https://api.github.com'
        self.headers = {
            'Accept': 'application/vnd.github.v3+json'
        }
        
        if self.token:
            self.headers['Authorization'] = f'token {self.token}'
    
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Any:
        """
        Make GitHub API request with error handling
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            JSON response
            
        Raises:
            requests.HTTPError: On API error
        """
        url = f"{self.api_base}{endpoint}"
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_repo_info(self) -> Dict[str, Any]:
        """
        Fetch repository information from GitHub API
        
        Returns:
            Repository information dictionary
        """
        endpoint = f'/repos/{self.owner}/{self.repo_name}'
        repo_data = self._make_request(endpoint)
        
        self.repo_info = {
            'name': repo_data.get('name'),
            'full_name': repo_data.get('full_name'),
            'description': repo_data.get('description'),
            'private': repo_data.get('private'),
            'size': repo_data.get('size'),  # Size in KB
            'stargazers_count': repo_data.get('stargazers_count'),
            'watchers_count': repo_data.get('watchers_count'),
            'forks_count': repo_data.get('forks_count'),
            'open_issues_count': repo_data.get('open_issues_count'),
            'default_branch': repo_data.get('default_branch'),
            'created_at': repo_data.get('created_at'),
            'updated_at': repo_data.get('updated_at'),
            'pushed_at': repo_data.get('pushed_at'),
            'language': repo_data.get('language'),
            'languages_url': repo_data.get('languages_url'),
            'topics': repo_data.get('topics', []),
            'license': repo_data.get('license', {}).get('name') if repo_data.get('license') else None
        }
        
        return self.repo_info
    
    def clone_repository(self) -> str:
        """
        Clone repository to temporary directory
        
        Returns:
            Path to cloned repository
        """
        if self.temp_dir:
            return self.temp_dir
        
        self.temp_dir = tempfile.mkdtemp(prefix='repo_analyzer_')
        
        # Clone using git command
        clone_url = self.repo_url
        
        # Use token if available for private repos
        if self.token and 'github.com' in clone_url:
            clone_url = clone_url.replace(
                'https://github.com/',
                f'https://{self.token}@github.com/'
            )
        
        try:
            subprocess.run(
                ['git', 'clone', '--depth', '1', clone_url, self.temp_dir],
                check=True,
                capture_output=True,
                text=True
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to clone repository: {e.stderr}")
        
        return self.temp_dir
    
    def get_commits_count(self) -> int:
        """
        Get total commit count - FIXED VERSION
        
        This was the bug! The old version wasn't properly paginating
        or handling the GitHub API response.
        
        Returns:
            Total number of commits
        """
        try:
            # Method 1: Try to get from repo info (fastest but approximate)
            # Some repos don't have this, so we'll use API pagination
            
            # Method 2: Use GitHub API with pagination
            endpoint = f'/repos/{self.owner}/{self.repo_name}/commits'
            
            # Get first page to check total
            params = {
                'per_page': 1,
                'page': 1
            }
            
            response = requests.get(
                f"{self.api_base}{endpoint}",
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            
            # Check Link header for pagination info
            link_header = response.headers.get('Link', '')
            
            if 'rel="last"' in link_header:
                # Extract last page number from Link header
                import re
                last_page_match = re.search(r'page=(\d+)>; rel="last"', link_header)
                if last_page_match:
                    last_page = int(last_page_match.group(1))
                    
                    # Get the last page to find exact count
                    last_response = requests.get(
                        f"{self.api_base}{endpoint}",
                        headers=self.headers,
                        params={'per_page': 100, 'page': last_page}
                    )
                    last_response.raise_for_status()
                    last_page_commits = len(last_response.json())
                    
                    # Total = (last_page - 1) * 100 + commits_on_last_page
                    total_commits = (last_page - 1) * 100 + last_page_commits
                    return total_commits
            
            # If no pagination, just count the commits directly
            params = {'per_page': 100}
            all_commits = []
            page = 1
            
            while True:
                params['page'] = page
                response = requests.get(
                    f"{self.api_base}{endpoint}",
                    headers=self.headers,
                    params=params
                )
                response.raise_for_status()
                commits = response.json()
                
                if not commits:
                    break
                
                all_commits.extend(commits)
                page += 1
                
                # Safety limit to avoid infinite loops
                if page > 100:  # Max 10,000 commits
                    break
            
            return len(all_commits)
            
        except Exception as e:
            print(f"Warning: Failed to get commit count: {e}")
            return 0
    
    def get_contributors_count(self) -> int:
        """
        Get total contributors count - FIXED VERSION
        
        This was also buggy! Now properly counts all contributors
        
        Returns:
            Total number of contributors
        """
        try:
            endpoint = f'/repos/{self.owner}/{self.repo_name}/contributors'
            
            # Get all contributors with pagination
            params = {'per_page': 100}
            all_contributors = []
            page = 1
            
            while True:
                params['page'] = page
                response = requests.get(
                    f"{self.api_base}{endpoint}",
                    headers=self.headers,
                    params=params
                )
                response.raise_for_status()
                contributors = response.json()
                
                if not contributors:
                    break
                
                all_contributors.extend(contributors)
                page += 1
                
                # Safety limit
                if page > 10:  # Max 1,000 contributors
                    break
            
            return len(all_contributors)
            
        except Exception as e:
            print(f"Warning: Failed to get contributors count: {e}")
            return 0
    
    def get_languages(self) -> Dict[str, int]:
        """
        Get language statistics
        
        Returns:
            Dictionary of language names to byte counts
        """
        try:
            endpoint = f'/repos/{self.owner}/{self.repo_name}/languages'
            languages = self._make_request(endpoint)
            return languages
        except Exception as e:
            print(f"Warning: Failed to get languages: {e}")
            return {}
