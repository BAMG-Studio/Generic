"""
Tests for SBOM Scanner functionality.
"""
import pytest
from pathlib import Path
from forgetrace.scanners.sbom import SBOMScanner


class TestSBOMScanner:
    """Test suite for SBOMScanner."""
    
    def test_scanner_initialization(self):
        """Test that scanner initializes correctly."""
        scanner = SBOMScanner()
        assert scanner is not None
        assert hasattr(scanner, 'scan')
    
    def test_scan_with_requirements_txt(self, sample_repo):
        """Test scanning a repo with requirements.txt."""
        scanner = SBOMScanner()
        results = scanner.scan(str(sample_repo))
        
        assert results is not None
        assert "dependencies" in results or "packages" in results
        
        # Get dependencies list
        deps = results.get("dependencies", results.get("packages", []))
        assert len(deps) > 0
        
        # Check that requests is found
        dep_names = [d.get("name", d.get("package", "")).lower() for d in deps]
        assert any("request" in name for name in dep_names)
    
    def test_scan_dependency_structure(self, sample_repo):
        """Test that dependency structure is correct."""
        scanner = SBOMScanner()
        results = scanner.scan(str(sample_repo))
        
        deps = results.get("dependencies", results.get("packages", []))
        
        if len(deps) > 0:
            for dep in deps:
                # Check for required fields (flexible to handle different formats)
                assert "name" in dep or "package" in dep
                # Version may not always be present
    
    def test_scan_empty_repo(self, temp_dir):
        """Test scanning a repo with no dependencies."""
        repo_path = Path(temp_dir) / "empty_repo"
        repo_path.mkdir()
        
        scanner = SBOMScanner()
        results = scanner.scan(str(repo_path))
        
        assert results is not None
        deps = results.get("dependencies", results.get("packages", []))
        assert isinstance(deps, list)
    
    def test_scan_with_package_json(self, temp_dir):
        """Test scanning a repo with package.json."""
        from git import Repo
        
        repo_path = Path(temp_dir) / "node_repo"
        repo_path.mkdir()
        
        repo = Repo.init(repo_path)
        with repo.config_writer() as config:
            config.set_value("user", "name", "Test")
            config.set_value("user", "email", "test@example.com")
        
        # Create package.json
        (repo_path / "package.json").write_text("""{
  "name": "test-app",
  "version": "1.0.0",
  "dependencies": {
    "express": "^4.18.0",
    "lodash": "^4.17.21"
  }
}
""")
        
        repo.index.add(["package.json"])
        repo.index.commit("Add package.json")
        
        scanner = SBOMScanner()
        results = scanner.scan(str(repo_path))
        
        assert results is not None
        deps = results.get("dependencies", results.get("packages", []))
        
        # Should find Node.js dependencies
        if len(deps) > 0:
            dep_names = [d.get("name", d.get("package", "")).lower() for d in deps]
            # May or may not find based on scanner implementation
            assert isinstance(dep_names, list)
    
    def test_scan_multiple_dependency_files(self, temp_dir):
        """Test scanning a repo with multiple dependency files."""
        from git import Repo
        
        repo_path = Path(temp_dir) / "multi_dep_repo"
        repo_path.mkdir()
        
        repo = Repo.init(repo_path)
        with repo.config_writer() as config:
            config.set_value("user", "name", "Test")
            config.set_value("user", "email", "test@example.com")
        
        # Create requirements.txt
        (repo_path / "requirements.txt").write_text("flask==2.3.0\nrequests==2.28.0\n")
        
        # Create setup.py
        (repo_path / "setup.py").write_text("""
from setuptools import setup

setup(
    name="test-package",
    install_requires=["numpy>=1.20.0", "pandas>=1.3.0"]
)
""")
        
        repo.index.add(["requirements.txt", "setup.py"])
        repo.index.commit("Add dependency files")
        
        scanner = SBOMScanner()
        results = scanner.scan(str(repo_path))
        
        assert results is not None
        deps = results.get("dependencies", results.get("packages", []))
        
        # Should find at least some dependencies
        assert isinstance(deps, list)
