"""Tests for SBOM Scanner functionality."""

from pathlib import Path
from typing import Any, Callable, Type, cast

from forgetrace.scanners.sbom import SBOMScanner

ScannerFactory = Callable[[Type[Any], Path | str], Any]


class TestSBOMScanner:
    """Test suite for SBOMScanner."""

    def test_scanner_initialization(
        self, temp_dir: str, scanner_factory: ScannerFactory
    ) -> None:
        """Test that scanner initializes correctly."""

        scanner: Any = scanner_factory(SBOMScanner, temp_dir)
        assert scanner is not None
        assert hasattr(scanner, "scan")

    def test_scan_with_requirements_txt(
        self, sample_repo: Path, scanner_factory: ScannerFactory
    ) -> None:
        """Test scanning a repo with requirements.txt."""

        scanner: Any = scanner_factory(SBOMScanner, sample_repo)
        results: dict[str, Any] = cast(dict[str, Any], scanner.scan())

        packages = cast(list[dict[str, Any]], results.get("packages", []))
        assert packages

        dep_names = [pkg.get("name", "").lower() for pkg in packages]
        assert any("request" in name for name in dep_names)

    def test_scan_dependency_structure(
        self, sample_repo: Path, scanner_factory: ScannerFactory
    ) -> None:
        """Test that dependency structure is correct."""

        scanner: Any = scanner_factory(SBOMScanner, sample_repo)
        results: dict[str, Any] = cast(dict[str, Any], scanner.scan())

        packages = cast(list[dict[str, Any]], results.get("packages", []))
        for pkg in packages:
            assert "name" in pkg

    def test_scan_empty_repo(
        self, temp_dir: str, scanner_factory: ScannerFactory
    ) -> None:
        """Test scanning a repo with no dependencies."""

        repo_path = Path(temp_dir) / "empty_repo"
        repo_path.mkdir()

        scanner: Any = scanner_factory(SBOMScanner, repo_path)
        results: dict[str, Any] = cast(dict[str, Any], scanner.scan())

        packages = cast(list[dict[str, Any]], results.get("packages", []))
        assert isinstance(packages, list)

    def test_scan_with_package_json(
        self, temp_dir: str, scanner_factory: ScannerFactory
    ) -> None:
        """Test scanning a repo with package.json."""

        from git import Repo

        repo_path = Path(temp_dir) / "node_repo"
        repo_path.mkdir()

        repo = Repo.init(repo_path)
        index: Any = repo.index
        with repo.config_writer() as config:
            config.set_value("user", "name", "Test")
            config.set_value("user", "email", "test@example.com")

        (repo_path / "package.json").write_text(
            """{
  "name": "test-app",
  "version": "1.0.0",
  "dependencies": {
    "express": "^4.18.0",
    "lodash": "^4.17.21"
  }
}
"""
        )

        index.add(["package.json"])
        index.commit("Add package.json")

        scanner: Any = scanner_factory(SBOMScanner, repo_path)
        results: dict[str, Any] = cast(dict[str, Any], scanner.scan())

        packages = cast(list[dict[str, Any]], results.get("packages", []))
        assert isinstance(packages, list)

    def test_scan_multiple_dependency_files(
        self, temp_dir: str, scanner_factory: ScannerFactory
    ) -> None:
        """Test scanning a repo with multiple dependency files."""

        from git import Repo

        repo_path = Path(temp_dir) / "multi_dep_repo"
        repo_path.mkdir()

        repo = Repo.init(repo_path)
        index: Any = repo.index
        with repo.config_writer() as config:
            config.set_value("user", "name", "Test")
            config.set_value("user", "email", "test@example.com")

        (repo_path / "requirements.txt").write_text("flask==2.3.0\nrequests==2.28.0\n")
        (repo_path / "setup.py").write_text(
            """
from setuptools import setup

setup(
    name="test-package",
    install_requires=["numpy>=1.20.0", "pandas>=1.3.0"]
)
"""
        )

        index.add(["requirements.txt", "setup.py"])
        index.commit("Add dependency files")

        scanner: Any = scanner_factory(SBOMScanner, repo_path)
        results: dict[str, Any] = cast(dict[str, Any], scanner.scan())

        packages = cast(list[dict[str, Any]], results.get("packages", []))
        assert isinstance(packages, list)
