"""
Tests for Git Scanner functionality.
"""
import pytest
from pathlib import Path
from forgetrace.scanners.git import GitScanner


class TestGitScanner:
    """Test suite for GitScanner."""
    
    def test_scanner_initialization(self):
        """Test that scanner initializes correctly."""
        scanner = GitScanner()
        assert scanner is not None
        assert hasattr(scanner, 'scan')
    
    def test_scan_basic_repo(self, sample_repo):
        """Test scanning a basic repository."""
        scanner = GitScanner()
        results = scanner.scan(str(sample_repo))
        
        assert results is not None
        assert "commits" in results
        assert len(results["commits"]) == 2  # Initial + utils commit
        assert "authors" in results
        assert len(results["authors"]) >= 1
    
    def test_scan_commit_metadata(self, sample_repo):
        """Test that commit metadata is captured correctly."""
        scanner = GitScanner()
        results = scanner.scan(str(sample_repo))
        
        commits = results["commits"]
        assert len(commits) > 0
        
        # Check first commit structure
        first_commit = commits[0]
        assert "sha" in first_commit or "hash" in first_commit
        assert "author" in first_commit
        assert "date" in first_commit
        assert "message" in first_commit
    
    def test_scan_authorship(self, sample_repo_with_multiple_authors):
        """Test authorship analysis."""
        scanner = GitScanner()
        results = scanner.scan(str(sample_repo_with_multiple_authors))
        
        authors = results["authors"]
        assert len(authors) >= 2
        
        # Check author structure
        for author in authors:
            assert "name" in author or "email" in author
            assert "commits" in author
            assert author["commits"] > 0
    
    def test_scan_file_changes(self, sample_repo):
        """Test file change tracking."""
        scanner = GitScanner()
        results = scanner.scan(str(sample_repo))
        
        commits = results["commits"]
        
        # At least one commit should have file changes
        has_files = any("files" in commit for commit in commits)
        assert has_files or any("stats" in commit for commit in commits)
    
    def test_scan_nonexistent_repo(self, temp_dir):
        """Test scanning a non-existent repository."""
        scanner = GitScanner()
        
        with pytest.raises(Exception):
            scanner.scan(str(Path(temp_dir) / "nonexistent"))
    
    def test_scan_non_git_directory(self, temp_dir):
        """Test scanning a directory that's not a git repo."""
        scanner = GitScanner()
        
        # Create a regular directory
        test_dir = Path(temp_dir) / "not_a_repo"
        test_dir.mkdir()
        
        with pytest.raises(Exception):
            scanner.scan(str(test_dir))
    
    def test_scan_empty_repo(self, temp_dir):
        """Test scanning an empty git repository."""
        from git import Repo
        
        repo_path = Path(temp_dir) / "empty_repo"
        repo_path.mkdir()
        Repo.init(repo_path)
        
        scanner = GitScanner()
        results = scanner.scan(str(repo_path))
        
        # Empty repo should have no commits
        assert results is not None
        assert "commits" in results
        assert len(results["commits"]) == 0
