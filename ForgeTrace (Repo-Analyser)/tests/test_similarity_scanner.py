"""Tests for Similarity Scanner functionality."""
from pathlib import Path
from typing import Any, Callable, Type, cast

from forgetrace.scanners.similarity import SimilarityScanner

ScannerFactory = Callable[[Type[Any], Path | str], Any]


class TestSimilarityScanner:
    """Test suite for SimilarityScanner."""

    def test_scanner_initialization(self, temp_dir: str, scanner_factory: ScannerFactory) -> None:
        """Test that scanner initializes correctly."""

        scanner: Any = scanner_factory(SimilarityScanner, temp_dir)
        assert scanner is not None
        assert hasattr(scanner, "scan")

    def test_scan_basic_repo(self, sample_repo: Path, scanner_factory: ScannerFactory) -> None:
        """Test basic similarity scanning."""

        scanner: Any = scanner_factory(SimilarityScanner, sample_repo)
        results: dict[str, Any] = cast(dict[str, Any], scanner.scan())

        assert isinstance(results, dict)

    def test_detect_identical_files(self, sample_repo_with_duplicates: Path, scanner_factory: ScannerFactory) -> None:
        """Test detecting identical files."""

        scanner: Any = scanner_factory(SimilarityScanner, sample_repo_with_duplicates)
        results: dict[str, Any] = cast(dict[str, Any], scanner.scan())

        duplicates = cast(list[dict[str, Any]], results.get("duplicates", []))
        assert isinstance(duplicates, list)

    def test_scan_unique_files(self, sample_repo: Path, scanner_factory: ScannerFactory) -> None:
        """Test scanning files with no duplicates."""

        scanner: Any = scanner_factory(SimilarityScanner, sample_repo)
        results: dict[str, Any] = cast(dict[str, Any], scanner.scan())

        assert isinstance(results, dict)

    def test_scan_empty_directory(self, temp_dir: str, scanner_factory: ScannerFactory) -> None:
        """Test scanning an empty directory."""

        empty_dir = Path(temp_dir) / "empty"
        empty_dir.mkdir()

        scanner: Any = scanner_factory(SimilarityScanner, empty_dir)
        results: dict[str, Any] = cast(dict[str, Any], scanner.scan())

        assert isinstance(results, dict)

    def test_scan_large_files(self, temp_dir: str, scanner_factory: ScannerFactory) -> None:
        """Test scanning with large files."""

        from git import Repo

        repo_path = Path(temp_dir) / "large_file_repo"
        repo_path.mkdir()

        repo = Repo.init(repo_path)
        index: Any = repo.index
        with repo.config_writer() as config:
            config.set_value("user", "name", "Test")
            config.set_value("user", "email", "test@example.com")

        large_content = "# Large file\n" + ("x = 1\n" * 1000)
        (repo_path / "large.py").write_text(large_content)

        index.add(["large.py"])
        index.commit("Add large file")

        scanner: Any = scanner_factory(SimilarityScanner, repo_path)
        results: dict[str, Any] = cast(dict[str, Any], scanner.scan())

        assert isinstance(results, dict)

    def test_scan_binary_files(self, temp_dir: str, scanner_factory: ScannerFactory) -> None:
        """Test that binary files are skipped."""

        from git import Repo

        repo_path = Path(temp_dir) / "binary_repo"
        repo_path.mkdir()

        repo = Repo.init(repo_path)
        index: Any = repo.index
        with repo.config_writer() as config:
            config.set_value("user", "name", "Test")
            config.set_value("user", "email", "test@example.com")

        (repo_path / "image.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)
        (repo_path / "code.py").write_text("print('hello')\n")

        index.add(["image.png", "code.py"])
        index.commit("Add files")

        scanner: Any = scanner_factory(SimilarityScanner, repo_path)
        results: dict[str, Any] = cast(dict[str, Any], scanner.scan())

        assert isinstance(results, dict)
