"""Tests for Git Scanner functionality."""
from pathlib import Path
from typing import Any, Callable, Type, cast

from forgetrace.scanners.git import GitScanner

ScannerFactory = Callable[[Type[Any], Path | str], Any]


class TestGitScanner:
    """Test suite for GitScanner."""

    def test_scanner_initialization(self, temp_dir: str, scanner_factory: ScannerFactory) -> None:
        """Test that scanner initializes correctly."""

        scanner: Any = scanner_factory(GitScanner, temp_dir)
        assert scanner is not None
        assert hasattr(scanner, "scan")

    def test_scan_basic_repo(self, sample_repo: Path, scanner_factory: ScannerFactory) -> None:
        """Test scanning a basic repository."""

        scanner: Any = scanner_factory(GitScanner, sample_repo)
        results: dict[str, Any] = cast(dict[str, Any], scanner.scan())

        assert isinstance(results, dict)
        assert "authors" in results
        assert "churn" in results
        assert "timeline" in results
        assert results.get("total_commits", 0) >= 1

    def test_scan_commit_metadata(self, sample_repo: Path, scanner_factory: ScannerFactory) -> None:
        """Test that commit metadata is captured correctly."""

        scanner: Any = scanner_factory(GitScanner, sample_repo)
        results: dict[str, Any] = cast(dict[str, Any], scanner.scan())

        timeline = cast(list[dict[str, Any]], results.get("timeline", []))
        if timeline:
            first_entry = timeline[0]
            assert "author" in first_entry
            assert "date" in first_entry

    def test_scan_authorship(
        self,
        sample_repo_with_multiple_authors: Path,
        scanner_factory: ScannerFactory,
    ) -> None:
        """Test authorship analysis."""

        scanner: Any = scanner_factory(GitScanner, sample_repo_with_multiple_authors)
        results: dict[str, Any] = cast(dict[str, Any], scanner.scan())

        authors = cast(dict[str, dict[str, Any]], results.get("authors", {}))
        assert len(authors) >= 2
        for author_data in authors.values():
            assert "commits" in author_data

    def test_scan_file_changes(self, sample_repo: Path, scanner_factory: ScannerFactory) -> None:
        """Test file change tracking."""

        scanner: Any = scanner_factory(GitScanner, sample_repo)
        results: dict[str, Any] = cast(dict[str, Any], scanner.scan())

        churn = cast(dict[str, dict[str, Any]], results.get("churn", {}))
        if churn:
            sample = next(iter(churn.values()))
            assert "added" in sample
            assert "removed" in sample
            assert "files" in sample

    def test_scan_nonexistent_repo(self, temp_dir: str, scanner_factory: ScannerFactory) -> None:
        """Test scanning a non-existent repository."""

        missing_path = Path(temp_dir) / "nonexistent"
        scanner: Any = scanner_factory(GitScanner, missing_path)
        results: dict[str, Any] = cast(dict[str, Any], scanner.scan())

        assert "error" in results

    def test_scan_non_git_directory(self, temp_dir: str, scanner_factory: ScannerFactory) -> None:
        """Test scanning a directory that's not a git repo."""

        test_dir = Path(temp_dir) / "not_a_repo"
        test_dir.mkdir()

        scanner: Any = scanner_factory(GitScanner, test_dir)
        results: dict[str, Any] = cast(dict[str, Any], scanner.scan())

        assert "error" in results

    def test_scan_empty_repo(self, temp_dir: str, scanner_factory: ScannerFactory) -> None:
        """Test scanning an empty git repository."""

        from git import Repo

        repo_path = Path(temp_dir) / "empty_repo"
        repo_path.mkdir()
        Repo.init(repo_path)

        scanner: Any = scanner_factory(GitScanner, repo_path)
        results: dict[str, Any] = cast(dict[str, Any], scanner.scan())

        assert isinstance(results, dict)
        assert results.get("total_commits", 0) == 0
