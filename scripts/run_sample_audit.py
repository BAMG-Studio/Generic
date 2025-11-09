"""Generate a ForgeTrace sample audit for quick smoke testing."""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path
import sys
from textwrap import dedent

import yaml
from git import Repo

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from forgetrace.audit import AuditEngine

APP_PY = (
    dedent(
        """
        import requests


        def fetch(url: str) -> str:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return response.text[:80]


        if __name__ == "__main__":
            print(fetch("https://example.com"))
        """
    ).strip()
    + "\n"
)

README_MD = (
    dedent(
        """
        # Sample Repo

        Generated for ForgeTrace executive summary smoke tests.
        """
    ).strip()
    + "\n"
)

REQUIREMENTS_TXT = "requests==2.31.0\npyyaml>=6.0\n"


def _prepare_sample_repo(base_dir: Path) -> Path:
    repo_dir = base_dir / "sample_repo"
    repo_dir.mkdir(parents=True, exist_ok=True)

    repo = Repo.init(repo_dir)
    with repo.config_writer() as writer:
        writer.set_value("user", "name", "Sample User")
        writer.set_value("user", "email", "sample@example.com")

    (repo_dir / "README.md").write_text(README_MD, encoding="utf-8")
    (repo_dir / "app.py").write_text(APP_PY, encoding="utf-8")
    (repo_dir / "requirements.txt").write_text(REQUIREMENTS_TXT, encoding="utf-8")

    repo.index.add(["README.md", "app.py", "requirements.txt"])
    repo.index.commit("Initial commit")
    return repo_dir


def _load_config() -> dict:
    config_path = Path("config.yaml")
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    output_cfg = config.setdefault("output", {})
    output_cfg.setdefault("include_pdf", True)
    return config


def main() -> None:
    base_dir = Path(tempfile.mkdtemp(prefix="forgetrace_sample_"))
    out_dir = Path("sample_audit")
    if out_dir.exists():
        shutil.rmtree(out_dir)

    try:
        repo_dir = _prepare_sample_repo(base_dir)
        config = _load_config()
        AuditEngine(str(repo_dir), str(out_dir), config).run()
        print(f"✓ Sample audit generated at {out_dir}/")
    finally:
        shutil.rmtree(base_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
