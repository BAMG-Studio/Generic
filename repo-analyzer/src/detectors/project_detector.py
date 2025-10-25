"""Project type detector"""
import os
from pathlib import Path
from typing import Dict, Set


class ProjectDetector:
    """Detect project types based on files present"""
    
    # File patterns for each project type
    DETECTION_PATTERNS = {
        'python': [
            'requirements.txt', 'setup.py', 'setup.cfg',
            'Pipfile', 'pyproject.toml', 'poetry.lock',
            '*.py'
        ],
        'javascript': [
            'package.json', 'yarn.lock', 'pnpm-lock.yaml',
            '*.js', '*.jsx', '*.ts', '*.tsx'
        ],
        'java': [
            'pom.xml', 'build.gradle', 'build.gradle.kts',
            '*.java'
        ],
        'go': [
            'go.mod', 'go.sum', '*.go'
        ],
        'rust': [
            'Cargo.toml', 'Cargo.lock', '*.rs'
        ],
        'ruby': [
            'Gemfile', 'Gemfile.lock', '*.rb'
        ],
        'php': [
            'composer.json', 'composer.lock', '*.php'
        ],
        'csharp': [
            '*.csproj', '*.sln', 'packages.config', '*.cs'
        ],
        'unity': [
            'Packages/manifest.json', 'ProjectSettings/ProjectVersion.txt'
        ],
        'docker': [
            'Dockerfile', 'docker-compose.yml', 'docker-compose.yaml', '.dockerignore'
        ]
    }
    
    def detect_all(self, repo_path: str) -> Dict[str, Set[str]]:
        """
        Detect all project types in repository
        
        Args:
            repo_path: Path to repository
            
        Returns:
            Dictionary mapping project type to set of matching files
        """
        detected = {}
        
        for project_type, patterns in self.DETECTION_PATTERNS.items():
            matches = self._find_matches(repo_path, patterns)
            if matches:
                detected[project_type] = matches
        
        return detected
    
    def _find_matches(self, repo_path: str, patterns: list) -> Set[str]:
        """
        Find files matching patterns
        
        Args:
            repo_path: Repository path
            patterns: List of file patterns
            
        Returns:
            Set of matching file paths
        """
        import fnmatch
        matches = set()
        
        for root, dirs, files in os.walk(repo_path):
            # Skip ignore directories
            dirs[:] = [d for d in dirs if d not in {
                '.git', '__pycache__', 'node_modules', 'venv', 'env',
                '.venv', 'build', 'dist', 'target', '.gradle', '.idea'
            }]
            
            # Check relative path patterns (like Packages/manifest.json)
            rel_root = os.path.relpath(root, repo_path)
            
            for pattern in patterns:
                # Check if pattern contains path separator (directory pattern)
                if '/' in pattern or '\\' in pattern:
                    # Path pattern
                    full_pattern_path = os.path.join(repo_path, pattern)
                    if os.path.exists(full_pattern_path):
                        matches.add(pattern)
                else:
                    # File pattern
                    for file in files:
                        if fnmatch.fnmatch(file, pattern):
                            rel_path = os.path.relpath(
                                os.path.join(root, file),
                                repo_path
                            )
                            matches.add(rel_path)
        
        return matches
    
    def is_multi_language(self, detected: Dict[str, Set[str]]) -> bool:
        """Check if repository is multi-language"""
        return len(detected) > 1
    
    def get_primary_language(self, detected: Dict[str, Set[str]]) -> str:
        """Get primary language based on file count"""
        if not detected:
            return 'unknown'
        
        # Count matches for each type
        counts = {lang: len(files) for lang, files in detected.items()}
        primary = max(counts, key=counts.get)
        
        return primary
