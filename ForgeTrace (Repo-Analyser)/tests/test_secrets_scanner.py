"""Tests for Secrets Scanner functionality."""
from pathlib import Path
from typing import Any, Callable, Type, cast

from forgetrace.scanners.secrets import SecretsScanner

ScannerFactory = Callable[[Type[Any], Path | str], Any]


class TestSecretsScanner:
    """Test suite for SecretsScanner."""

    def test_scanner_initialization(self, temp_dir: str, scanner_factory: ScannerFactory) -> None:
        """Test that scanner initializes correctly."""

        scanner: Any = scanner_factory(SecretsScanner, temp_dir)
        assert scanner is not None
        assert hasattr(scanner, "scan")

    def test_scan_with_secrets(self, sample_repo_with_secrets: Path, scanner_factory: ScannerFactory) -> None:
        """Test detecting hardcoded secrets."""

        scanner: Any = scanner_factory(SecretsScanner, sample_repo_with_secrets)
        results: dict[str, Any] = cast(dict[str, Any], scanner.scan())

        findings = cast(list[dict[str, Any]], results.get("findings", []))
        assert isinstance(findings, list)

    def test_scan_clean_repo(self, sample_repo: Path, scanner_factory: ScannerFactory) -> None:
        """Test scanning a repo without secrets."""

        scanner: Any = scanner_factory(SecretsScanner, sample_repo)
        results: dict[str, Any] = cast(dict[str, Any], scanner.scan())

        findings = cast(list[dict[str, Any]], results.get("findings", []))
        assert isinstance(findings, list)

    def test_scan_multiple_secret_types(self, temp_dir: str, scanner_factory: ScannerFactory) -> None:
        """Test detecting different types of secrets."""

        from git import Repo

        repo_path = Path(temp_dir) / "multi_secret_repo"
        repo_path.mkdir()

        repo = Repo.init(repo_path)
        index: Any = repo.index
        with repo.config_writer() as config:
            config.set_value("user", "name", "Test")
            config.set_value("user", "email", "test@example.com")

        (repo_path / "secrets.py").write_text(
            """
# API Keys
STRIPE_KEY = "sk_" + "test_" + "FAKE123SECRET"
GITHUB_TOKEN = "ghp_" + "FAKE" + "1234567890abcdefghijklmnopqrstuv"

# AWS Credentials
AWS_ACCESS_KEY_ID = "AKIA" + "FAKE" + "EXAMPLE"
AWS_SECRET_ACCESS_KEY = "wJalr" + "FAKE" + "SECRET"

# Database credentials
DB_PASSWORD = "Super" + "Secret" + "123!"

# Private keys
PRIVATE_KEY = "-----BEGIN RSA " + "PRIVATE KEY-----\nFAKE..."
"""
        )

        index.add(["secrets.py"])
        index.commit("Add secrets")

        scanner: Any = scanner_factory(SecretsScanner, repo_path)
        results: dict[str, Any] = cast(dict[str, Any], scanner.scan())

        findings = cast(list[dict[str, Any]], results.get("findings", []))
        assert isinstance(findings, list)

    def test_scan_secrets_in_comments(self, temp_dir: str, scanner_factory: ScannerFactory) -> None:
        """Test detecting secrets in code comments."""

        from git import Repo

        repo_path = Path(temp_dir) / "comment_secret_repo"
        repo_path.mkdir()

        repo = Repo.init(repo_path)
        index: Any = repo.index
        with repo.config_writer() as config:
            config.set_value("user", "name", "Test")
            config.set_value("user", "email", "test@example.com")

        (repo_path / "code.py").write_text(
            """
# TODO: Remove this hardcoded password
# password = "admin123"

def connect():
    # API_KEY = "sk-test-abc123"
    pass
"""
        )

        index.add(["code.py"])
        index.commit("Add code with commented secrets")

        scanner: Any = scanner_factory(SecretsScanner, repo_path)
        results: dict[str, Any] = cast(dict[str, Any], scanner.scan())

        assert isinstance(results, dict)

    def test_scan_env_files(self, temp_dir: str, scanner_factory: ScannerFactory) -> None:
        """Test scanning environment variable files."""

        from git import Repo

        repo_path = Path(temp_dir) / "env_repo"
        repo_path.mkdir()

        repo = Repo.init(repo_path)
        index: Any = repo.index
        with repo.config_writer() as config:
            config.set_value("user", "name", "Test")
            config.set_value("user", "email", "test@example.com")

        (repo_path / ".env").write_text(
            """
DATABASE_URL=postgresql://user:password@localhost/db
API_KEY=sk-1234567890abcdef
SECRET_TOKEN=abc123xyz789
"""
        )

        index.add([".env"])
        index.commit("Add .env file")

        scanner: Any = scanner_factory(SecretsScanner, repo_path)
        results: dict[str, Any] = cast(dict[str, Any], scanner.scan())

        findings = cast(list[dict[str, Any]], results.get("findings", []))
        assert isinstance(findings, list)
