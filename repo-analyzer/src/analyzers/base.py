"""
Base Repository Analyzer
Provides universal dependency scanning for ANY project type
"""
import os
import re
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from abc import ABC, abstractmethod
import tempfile
import shutil

from parsers.unity_parser import UnityParser
from parsers.npm_parser import NPMParser
from parsers.pip_parser import PipParser
from parsers.maven_parser import MavenParser
from parsers.gradle_parser import GradleParser
from parsers.go_parser import GoParser
from parsers.cargo_parser import CargoParser
from parsers.composer_parser import ComposerParser
from parsers.bundler_parser import BundlerParser
from parsers.nuget_parser import NuGetParser
from detectors.project_detector import ProjectDetector
from utils.cost_calculator import CostCalculator


# Universal dependency file patterns
DEPENDENCY_FILES = {
    # Python
    'requirements.txt': {'parser': 'pip', 'type': 'python', 'manager': 'pip'},
    'Pipfile': {'parser': 'pip', 'type': 'python', 'manager': 'pipenv'},
    'Pipfile.lock': {'parser': 'pip', 'type': 'python', 'manager': 'pipenv'},
    'pyproject.toml': {'parser': 'pip', 'type': 'python', 'manager': 'poetry'},
    'poetry.lock': {'parser': 'pip', 'type': 'python', 'manager': 'poetry'},
    'setup.py': {'parser': 'pip', 'type': 'python', 'manager': 'setuptools'},
    'setup.cfg': {'parser': 'pip', 'type': 'python', 'manager': 'setuptools'},
    
    # Node.js
    'package.json': {'parser': 'npm', 'type': 'javascript', 'manager': 'npm'},
    'package-lock.json': {'parser': 'npm', 'type': 'javascript', 'manager': 'npm'},
    'yarn.lock': {'parser': 'npm', 'type': 'javascript', 'manager': 'yarn'},
    'pnpm-lock.yaml': {'parser': 'npm', 'type': 'javascript', 'manager': 'pnpm'},
    
    # Java
    'pom.xml': {'parser': 'maven', 'type': 'java', 'manager': 'maven'},
    'build.gradle': {'parser': 'gradle', 'type': 'java', 'manager': 'gradle'},
    'build.gradle.kts': {'parser': 'gradle', 'type': 'java', 'manager': 'gradle'},
    'settings.gradle': {'parser': 'gradle', 'type': 'java', 'manager': 'gradle'},
    
    # Go
    'go.mod': {'parser': 'go', 'type': 'go', 'manager': 'go'},
    'go.sum': {'parser': 'go', 'type': 'go', 'manager': 'go'},
    
    # Rust
    'Cargo.toml': {'parser': 'cargo', 'type': 'rust', 'manager': 'cargo'},
    'Cargo.lock': {'parser': 'cargo', 'type': 'rust', 'manager': 'cargo'},
    
    # Ruby
    'Gemfile': {'parser': 'bundler', 'type': 'ruby', 'manager': 'bundler'},
    'Gemfile.lock': {'parser': 'bundler', 'type': 'ruby', 'manager': 'bundler'},
    
    # PHP
    'composer.json': {'parser': 'composer', 'type': 'php', 'manager': 'composer'},
    'composer.lock': {'parser': 'composer', 'type': 'php', 'manager': 'composer'},
    
    # .NET
    '*.csproj': {'parser': 'nuget', 'type': 'csharp', 'manager': 'nuget'},
    'packages.config': {'parser': 'nuget', 'type': 'csharp', 'manager': 'nuget'},
    '*.sln': {'parser': 'nuget', 'type': 'csharp', 'manager': 'nuget'},
    
    # Unity (can be in subdirectory)
    'Packages/manifest.json': {'parser': 'unity', 'type': 'unity', 'manager': 'upm'},
    
    # Docker
    'Dockerfile': {'parser': 'docker', 'type': 'docker', 'manager': 'docker'},
    'docker-compose.yml': {'parser': 'docker', 'type': 'docker', 'manager': 'docker'},
    'docker-compose.yaml': {'parser': 'docker', 'type': 'docker', 'manager': 'docker'},
}


class BaseAnalyzer(ABC):
    """Base class for repository analyzers"""
    
    def __init__(self, repo_url: str, config: Any, token: Optional[str] = None):
        """
        Initialize base analyzer
        
        Args:
            repo_url: Repository URL
            config: Configuration object
            token: API token for authentication
        """
        self.repo_url = repo_url
        self.config = config
        self.token = token
        self.temp_dir = None
        
        # Parse repository info from URL
        self.owner, self.repo_name = self._parse_repo_url(repo_url)
        
        # Results storage
        self.repo_info: Dict[str, Any] = {}
        self.dependencies: List[Dict[str, Any]] = []
        self.cost_analysis: Dict[str, Any] = {}
        self.project_types: List[str] = []
        self.package_managers: List[str] = []
        
        # Initialize parsers
        self.parsers = {
            'unity': UnityParser(),
            'npm': NPMParser(),
            'pip': PipParser(),
            'maven': MavenParser(),
            'gradle': GradleParser(),
            'go': GoParser(),
            'cargo': CargoParser(),
            'composer': ComposerParser(),
            'bundler': BundlerParser(),
            'nuget': NuGetParser()
        }
        
        # Initialize detector
        self.detector = ProjectDetector()
    
    def _parse_repo_url(self, url: str) -> Tuple[str, str]:
        """
        Parse owner and repo name from URL
        
        Args:
            url: Repository URL
            
        Returns:
            Tuple of (owner, repo_name)
        """
        # Remove .git suffix if present
        if url.endswith('.git'):
            url = url[:-4]
        
        # Extract path components
        parts = url.split('/')
        repo_name = parts[-1]
        owner = parts[-2] if len(parts) >= 2 else 'unknown'
        
        return owner, repo_name
    
    @abstractmethod
    def get_repo_info(self) -> Dict[str, Any]:
        """Fetch repository information from platform API"""
        pass
    
    @abstractmethod
    def clone_repository(self) -> str:
        """Clone repository to temporary directory"""
        pass
    
    @abstractmethod
    def get_commits_count(self) -> int:
        """Get total commit count - FIXED VERSION"""
        pass
    
    @abstractmethod
    def get_contributors_count(self) -> int:
        """Get total contributors count - FIXED VERSION"""
        pass
    
    def scan_dependencies(self) -> List[Dict[str, Any]]:
        """
        Scan repository for dependencies (UNIVERSAL)
        Works with ANY project type
        
        Returns:
            List of dependency dictionaries
        """
        # Clone repository
        repo_path = self.clone_repository()
        
        # Detect all project types
        detected_types = self.detector.detect_all(repo_path)
        self.project_types = list(detected_types.keys())
        
        # Scan for dependency files recursively
        dependencies = []
        package_managers = set()
        
        for root, dirs, files in os.walk(repo_path):
            # Skip common ignore directories
            dirs[:] = [d for d in dirs if d not in {
                '.git', '__pycache__', 'node_modules', 'venv', 'env',
                '.venv', 'build', 'dist', 'target', '.gradle', '.idea'
            }]
            
            for file in files:
                file_path = Path(root) / file
                relative_path = file_path.relative_to(repo_path)
                
                # Check exact filename matches
                if file in DEPENDENCY_FILES:
                    file_info = DEPENDENCY_FILES[file]
                    deps = self._parse_dependency_file(
                        str(file_path),
                        file_info['parser'],
                        file_info['type'],
                        file_info['manager']
                    )
                    dependencies.extend(deps)
                    package_managers.add(file_info['manager'])
                
                # Check pattern matches (like *.csproj)
                for pattern, file_info in DEPENDENCY_FILES.items():
                    if '*' in pattern:
                        import fnmatch
                        if fnmatch.fnmatch(file, pattern):
                            deps = self._parse_dependency_file(
                                str(file_path),
                                file_info['parser'],
                                file_info['type'],
                                file_info['manager']
                            )
                            dependencies.extend(deps)
                            package_managers.add(file_info['manager'])
                
                # Check relative path matches (like Packages/manifest.json for Unity)
                rel_path_str = str(relative_path).replace('\\', '/')
                if rel_path_str in DEPENDENCY_FILES:
                    file_info = DEPENDENCY_FILES[rel_path_str]
                    deps = self._parse_dependency_file(
                        str(file_path),
                        file_info['parser'],
                        file_info['type'],
                        file_info['manager']
                    )
                    dependencies.extend(deps)
                    package_managers.add(file_info['manager'])
        
        self.dependencies = dependencies
        self.package_managers = list(package_managers)
        
        return dependencies
    
    def _parse_dependency_file(
        self,
        file_path: str,
        parser_name: str,
        project_type: str,
        package_manager: str
    ) -> List[Dict[str, Any]]:
        """
        Parse a dependency file using the appropriate parser
        
        Args:
            file_path: Path to dependency file
            parser_name: Parser to use
            project_type: Project type
            package_manager: Package manager
            
        Returns:
            List of parsed dependencies
        """
        try:
            if parser_name in self.parsers:
                parser = self.parsers[parser_name]
                dependencies = parser.parse(file_path)
                
                # Enrich dependencies with metadata
                for dep in dependencies:
                    dep['project_type'] = project_type
                    dep['package_manager'] = package_manager
                    dep['source_file'] = file_path
                
                return dependencies
        except Exception as e:
            print(f"Warning: Failed to parse {file_path}: {e}")
        
        return []
    
    def analyze_costs(self, hourly_rate: float = 100) -> Dict[str, Any]:
        """
        Analyze development costs using COCOMO II, SCC, and Git Prime
        ENHANCED: Now includes comprehensive cost analysis
        
        Args:
            hourly_rate: Hourly developer rate
            
        Returns:
            Comprehensive cost analysis dictionary
        """
        # Get commits and contributors (FIXED API CALLS)
        total_commits = self.get_commits_count()
        total_contributors = self.get_contributors_count()
        
        # Initialize cost calculator
        cost_calc = CostCalculator({
            'hourly_rate': hourly_rate,
            'cocomo_params': self.config.get('cocomo_params', {
                'a': 2.94,
                'b': 1.09,
                'monthly_hours': 152
            })
        })
        
        # Get comprehensive cost analysis
        if self.temp_dir and os.path.exists(self.temp_dir):
            comprehensive = cost_calc.calculate_comprehensive_cost(
                repo_path=self.temp_dir,
                commits=total_commits,
                contributors=total_contributors,
                dependencies=len(self.dependencies)
            )
            
            # Extract key metrics for backward compatibility
            self.cost_analysis = {
                'total_commits': total_commits,
                'total_contributors': total_contributors,
                'estimated_loc': comprehensive['scc']['total_code'],
                'estimated_kloc': comprehensive['scc']['kloc'],
                'effort_months': comprehensive['cocomo']['effort_months'],
                'estimated_hours': comprehensive['cocomo']['effort_hours'],
                'hourly_rate': hourly_rate,
                'estimated_cost': comprehensive['cocomo']['estimated_cost'],
                'cost_per_dependency': comprehensive['metrics']['cost_per_dependency'],
                'commits_per_dependency': comprehensive['metrics']['commits_per_dependency'],
                'dependencies_commits_ratio': f"{len(self.dependencies)}:{total_commits}",
                
                # Enhanced metrics from SCC
                'total_lines': comprehensive['scc']['total_lines'],
                'total_comments': comprehensive['scc']['total_comments'],
                'total_complexity': comprehensive['scc']['total_complexity'],
                'languages': comprehensive['scc']['languages'],
                
                # Git Prime metrics
                'git_prime': comprehensive['git_prime'],
                'code_churn': comprehensive['git_prime']['total_churn'],
                'commits_by_author': comprehensive['git_prime']['commits_by_author'],
                'lines_by_author': comprehensive['git_prime']['lines_by_author'],
                
                # Additional calculated metrics
                'metrics': comprehensive['metrics'],
                'cocomo_parameters': comprehensive['cocomo']['cocomo_parameters']
            }
        else:
            # Fallback to basic COCOMO calculation
            repo_info = self.repo_info
            loc = repo_info.get('size', 0) * 100
            kloc = loc / 1000 if loc > 0 else (total_commits * 50) / 1000
            
            cocomo_results = cost_calc.calculate_cocomo_cost(
                kloc=kloc,
                commits=total_commits,
                contributors=total_contributors
            )
            
            dep_count = len(self.dependencies)
            cost_per_dependency = cocomo_results['estimated_cost'] / dep_count if dep_count > 0 else 0
            commits_per_dep = total_commits / dep_count if dep_count > 0 else 0
            
            self.cost_analysis = {
                'total_commits': total_commits,
                'total_contributors': total_contributors,
                'estimated_loc': int(loc),
                'estimated_kloc': cocomo_results['kloc'],
                'effort_months': cocomo_results['effort_months'],
                'estimated_hours': cocomo_results['effort_hours'],
                'hourly_rate': hourly_rate,
                'estimated_cost': cocomo_results['estimated_cost'],
                'cost_per_dependency': round(cost_per_dependency, 2),
                'commits_per_dependency': round(commits_per_dep, 2),
                'dependencies_commits_ratio': f"{dep_count}:{total_commits}",
                'cocomo_parameters': cocomo_results['cocomo_parameters']
            }
        
        return self.cost_analysis
    
    def get_results(self) -> Dict[str, Any]:
        """
        Get comprehensive analysis results
        
        Returns:
            Complete results dictionary
        """
        return {
            'repository': {
                'url': self.repo_url,
                'owner': self.owner,
                'name': self.repo_name,
                'info': self.repo_info
            },
            'sbom': {
                'total_dependencies': len(self.dependencies),
                'dependencies': self.dependencies,
                'project_types': self.project_types,
                'package_managers': self.package_managers,
                'project_type': '/'.join(self.project_types) if self.project_types else 'unknown'
            },
            'cost_analysis': self.cost_analysis
        }
    
    def cleanup(self):
        """Clean up temporary files"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()
