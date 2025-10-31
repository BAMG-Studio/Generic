"""Pytest configuration and shared fixtures for ForgeTrace tests."""
import shutil
import tempfile
from pathlib import Path
from typing import Any, Callable, Dict, Iterator, Type

import pytest
from git import Repo


@pytest.fixture
def temp_dir() -> Iterator[str]:
    """Create a temporary directory for tests."""

    temp = tempfile.mkdtemp()
    try:
        yield temp
    finally:
        shutil.rmtree(temp, ignore_errors=True)


@pytest.fixture
def sample_repo(temp_dir: str) -> Iterator[Path]:
    """Create a sample git repository for testing."""
    repo_path = Path(temp_dir) / "test_repo"
    repo_path.mkdir()
    
    # Initialize git repo
    repo = Repo.init(repo_path)
    index: Any = repo.index
    index: Any = repo.index
    
    # Configure git user
    with repo.config_writer() as config:
        config.set_value("user", "name", "Test User")
        config.set_value("user", "email", "test@example.com")
    
    # Create sample files
    (repo_path / "README.md").write_text("# Test Repository\n\nThis is a test repo.\n")
    
    (repo_path / "main.py").write_text("""#!/usr/bin/env python3
\"\"\"Main application module.\"\"\"

def hello():
    \"\"\"Return greeting message.\"\"\"
    return "Hello, World!"

def main():
    \"\"\"Entry point.\"\"\"
    print(hello())

if __name__ == "__main__":
    main()
""")
    
    (repo_path / "requirements.txt").write_text("requests==2.28.0\npyyaml>=6.0\n")
    
    # Create LICENSE file
    (repo_path / "LICENSE").write_text("""MIT License

Copyright (c) 2024 Test User

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
""")
    
    # Initial commit
    index.add(["README.md", "main.py", "requirements.txt", "LICENSE"])
    index.commit("Initial commit")
    
    # Add another commit
    (repo_path / "utils.py").write_text("""\"\"\"Utility functions.\"\"\"

def add(a, b):
    \"\"\"Add two numbers.\"\"\"
    return a + b

def multiply(a, b):
    \"\"\"Multiply two numbers.\"\"\"
    return a * b
""")
    index.add(["utils.py"])
    index.commit("Add utils module")
    
    yield repo_path


@pytest.fixture
def sample_repo_with_secrets(temp_dir: str) -> Iterator[Path]:
    """Create a repo with hardcoded secrets for testing."""
    repo_path = Path(temp_dir) / "secrets_repo"
    repo_path.mkdir()
    
    repo = Repo.init(repo_path)
    index: Any = repo.index

    with repo.config_writer() as config:
        config.set_value("user", "name", "Test User")
        config.set_value("user", "email", "test@example.com")
    
    # Create file with fake secrets
    (repo_path / "config.py").write_text("""# Configuration file
API_KEY = "sk-1234567890abcdef1234567890abcdef"
AWS_SECRET = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
PASSWORD = "admin123"
DATABASE_URL = "postgresql://user:password@localhost:5432/db"
""")
    
    index.add(["config.py"])
    index.commit("Add config with secrets")
    
    yield repo_path


@pytest.fixture
def sample_repo_with_multiple_authors(temp_dir: str) -> Iterator[Path]:
    """Create a repo with multiple authors."""
    repo_path = Path(temp_dir) / "multi_author_repo"
    repo_path.mkdir()
    
    repo = Repo.init(repo_path)
    index: Any = repo.index

    # First author
    with repo.config_writer() as config:
        config.set_value("user", "name", "Alice")
        config.set_value("user", "email", "alice@example.com")
    
    (repo_path / "alice.py").write_text("# Alice's code\ndef alice_func():\n    return 'Alice'\n")
    index.add(["alice.py"])
    index.commit("Alice's commit")
    
    # Second author
    with repo.config_writer() as config:
        config.set_value("user", "name", "Bob")
        config.set_value("user", "email", "bob@example.com")
    
    (repo_path / "bob.py").write_text("# Bob's code\ndef bob_func():\n    return 'Bob'\n")
    index.add(["bob.py"])
    index.commit("Bob's commit")
    
    # Third author
    with repo.config_writer() as config:
        config.set_value("user", "name", "Charlie")
        config.set_value("user", "email", "charlie@example.com")
    
    (repo_path / "charlie.py").write_text("# Charlie's code\ndef charlie_func():\n    return 'Charlie'\n")
    index.add(["charlie.py"])
    index.commit("Charlie's commit")
    
    yield repo_path


@pytest.fixture
def sample_repo_with_duplicates(temp_dir: str) -> Iterator[Path]:
    """Create a repo with duplicate/similar code."""
    repo_path = Path(temp_dir) / "dup_repo"
    repo_path.mkdir()
    
    repo = Repo.init(repo_path)
    index: Any = repo.index

    with repo.config_writer() as config:
        config.set_value("user", "name", "Test User")
        config.set_value("user", "email", "test@example.com")
    
    # Create identical files
    code = """def hello():
    return 'Hello, World!'

def greet(name):
    return f'Hello, {name}!'

def farewell():
    return 'Goodbye!'
"""
    (repo_path / "file1.py").write_text(code)
    (repo_path / "file2.py").write_text(code)
    
    # Create similar but not identical file
    similar_code = """def hello():
    return 'Hello, World!'

def greet(name):
    return f'Hi, {name}!'

def farewell():
    return 'Bye!'
"""
    (repo_path / "file3.py").write_text(similar_code)
    
    index.add(["file1.py", "file2.py", "file3.py"])
    index.commit("Add files with duplicates")
    
    yield repo_path


@pytest.fixture
def mock_config() -> Dict[str, Any]:
    """Provide a mock configuration."""

    return {
        "scanners": {
            "sbom": {"enabled": True},
            "git": {"enabled": True},
            "similarity": {"enabled": True},
            "license": {"enabled": True},
            "secrets": {"enabled": True},
            "sast": {"enabled": False},  # Disabled by default for tests
        },
        "output": {
            "format": "json",
            "verbose": False,
        },
        "classification": {
            "cost_per_hour": 100,
            "third_party_patterns": ["node_modules", "vendor", "third_party"],
        },
        "tools": {},
    }


@pytest.fixture
def scanner_factory(mock_config: Dict[str, Any]) -> Callable[[Type[Any], Path | str], Any]:
    """Factory to construct scanners with required parameters."""

    def _factory(scanner_cls: Type[Any], repo_path: Path | str) -> Any:
        return scanner_cls(repo_path, mock_config)

    return _factory
