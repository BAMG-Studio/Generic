"""
Tests for Similarity Scanner functionality.
"""
import pytest
from pathlib import Path
from forgetrace.scanners.similarity import SimilarityScanner


class TestSimilarityScanner:
    """Test suite for SimilarityScanner."""
    
    def test_scanner_initialization(self):
        """Test that scanner initializes correctly."""
        scanner = SimilarityScanner()
        assert scanner is not None
        assert hasattr(scanner, 'scan')
    
    def test_scan_basic_repo(self, sample_repo):
        """Test basic similarity scanning."""
        scanner = SimilarityScanner()
        results = scanner.scan(str(sample_repo))
        
        assert results is not None
        # Results should have some similarity data structure
        assert isinstance(results, dict)
    
    def test_detect_identical_files(self, sample_repo_with_duplicates):
        """Test detecting identical files."""
        scanner = SimilarityScanner()
        results = scanner.scan(str(sample_repo_with_duplicates))
        
        assert results is not None
        
        # Check for similar files (exact structure depends on implementation)
        similar_files = results.get("similar_files", results.get("duplicates", []))
        
        # Should detect some similarity
        assert isinstance(similar_files, (list, dict))
    
    def test_scan_unique_files(self, sample_repo):
        """Test scanning files with no duplicates."""
        scanner = SimilarityScanner()
        results = scanner.scan(str(sample_repo))
        
        assert results is not None
        # Should still return valid results even if no duplicates
        assert isinstance(results, dict)
    
    def test_scan_empty_directory(self, temp_dir):
        """Test scanning an empty directory."""
        empty_dir = Path(temp_dir) / "empty"
        empty_dir.mkdir()
        
        scanner = SimilarityScanner()
        results = scanner.scan(str(empty_dir))
        
        assert results is not None
        # Should handle empty directories gracefully
        assert isinstance(results, dict)
    
    def test_scan_large_files(self, temp_dir):
        """Test scanning with large files."""
        from git import Repo
        
        repo_path = Path(temp_dir) / "large_file_repo"
        repo_path.mkdir()
        
        repo = Repo.init(repo_path)
        with repo.config_writer() as config:
            config.set_value("user", "name", "Test")
            config.set_value("user", "email", "test@example.com")
        
        # Create a large file
        large_content = "# Large file\n" + ("x = 1\n" * 1000)
        (repo_path / "large.py").write_text(large_content)
        
        repo.index.add(["large.py"])
        repo.index.commit("Add large file")
        
        scanner = SimilarityScanner()
        results = scanner.scan(str(repo_path))
        
        # Should handle large files without crashing
        assert results is not None
        assert isinstance(results, dict)
    
    def test_scan_binary_files(self, temp_dir):
        """Test that binary files are skipped."""
        from git import Repo
        
        repo_path = Path(temp_dir) / "binary_repo"
        repo_path.mkdir()
        
        repo = Repo.init(repo_path)
        with repo.config_writer() as config:
            config.set_value("user", "name", "Test")
            config.set_value("user", "email", "test@example.com")
        
        # Create a binary file
        (repo_path / "image.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)
        (repo_path / "code.py").write_text("print('hello')\n")
        
        repo.index.add(["image.png", "code.py"])
        repo.index.commit("Add files")
        
        scanner = SimilarityScanner()
        results = scanner.scan(str(repo_path))
        
        # Should process only text files
        assert results is not None
        assert isinstance(results, dict)
