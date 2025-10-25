"""
GitLab Repository Analyzer
"""
import requests
import tempfile
import subprocess
from typing import Dict, Any

from .base import BaseAnalyzer


class GitLabAnalyzer(BaseAnalyzer):
    """Analyzer for GitLab repositories"""
    
    def __init__(self, repo_url: str, config: Any, token: str = None):
        """
        Initialize GitLab analyzer
        
        Args:
            repo_url: GitLab repository URL
            config: Configuration object
            token: GitLab personal access token
        """
        super().__init__(repo_url, config, token)
        
        # Determine GitLab instance (gitlab.com or self-hosted)
        if 'gitlab.com' in repo_url:
            self.api_base = 'https://gitlab.com/api/v4'
        else:
            # Extract base URL for self-hosted GitLab
            import re
            match = re.match(r'https?://([^/]+)', repo_url)
            if match:
                self.api_base = f'https://{match.group(1)}/api/v4'
            else:
                self.api_base = 'https://gitlab.com/api/v4'
        
        self.headers = {}
        if self.token:
            self.headers['PRIVATE-TOKEN'] = self.token
    
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Any:
        """Make GitLab API request"""
        url = f"{self.api_base}{endpoint}"
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def _get_project_id(self) -> str:
        """Get project ID (URL-encoded)"""
        return f"{self.owner}%2F{self.repo_name}"
    
    def get_repo_info(self) -> Dict[str, Any]:
        """Fetch repository information from GitLab API"""
        project_id = self._get_project_id()
        endpoint = f'/projects/{project_id}'
        project_data = self._make_request(endpoint)
        
        self.repo_info = {
            'name': project_data.get('name'),
            'full_name': project_data.get('path_with_namespace'),
            'description': project_data.get('description'),
            'private': project_data.get('visibility') == 'private',
            'size': 0,  # GitLab doesn't provide this easily
            'stargazers_count': project_data.get('star_count', 0),
            'forks_count': project_data.get('forks_count', 0),
            'open_issues_count': project_data.get('open_issues_count', 0),
            'default_branch': project_data.get('default_branch'),
            'created_at': project_data.get('created_at'),
            'updated_at': project_data.get('last_activity_at'),
            'language': None,  # GitLab returns multiple languages
            'topics': project_data.get('topics', []),
            'license': None
        }
        
        return self.repo_info
    
    def clone_repository(self) -> str:
        """Clone repository to temporary directory"""
        if self.temp_dir:
            return self.temp_dir
        
        self.temp_dir = tempfile.mkdtemp(prefix='repo_analyzer_')
        
        clone_url = self.repo_url
        
        if self.token:
            # Use token for authentication
            clone_url = clone_url.replace(
                'https://',
                f'https://oauth2:{self.token}@'
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
        """Get total commit count"""
        try:
            project_id = self._get_project_id()
            endpoint = f'/projects/{project_id}/repository/commits'
            
            # GitLab uses pagination
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
                
                if page > 100:  # Safety limit
                    break
            
            return len(all_commits)
            
        except Exception as e:
            print(f"Warning: Failed to get commit count: {e}")
            return 0
    
    def get_contributors_count(self) -> int:
        """Get total contributors count"""
        try:
            project_id = self._get_project_id()
            endpoint = f'/projects/{project_id}/repository/contributors'
            
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
                
                if page > 10:  # Safety limit
                    break
            
            return len(all_contributors)
            
        except Exception as e:
            print(f"Warning: Failed to get contributors count: {e}")
            return 0
