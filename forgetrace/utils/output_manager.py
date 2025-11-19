"""Output management helpers for ForgeTrace."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, Optional, Sequence, Tuple


class LiveArchiveManager:
    """Create structured archives for live client audits."""

    def __init__(self, config: Dict) -> None:
        output_cfg = config.get("output", {}) if isinstance(config, dict) else {}
        archive_cfg = (
            output_cfg.get("archive", {}) if isinstance(output_cfg, dict) else {}
        )

        default_root = Path("analysis_outputs") / "live"
        root_value = archive_cfg.get("root_dir", default_root)

        self.enabled: bool = archive_cfg.get("enabled", True)
        self.root_dir: Optional[Path] = (
            Path(root_value).expanduser() if root_value else None
        )
        self.max_runs_per_repo: Optional[int] = archive_cfg.get("max_runs_per_repo", 50)
        self.metadata: Dict = (
            config.get("metadata", {}) if isinstance(config, dict) else {}
        )

        if self.enabled and self.root_dir:
            self.root_dir.mkdir(parents=True, exist_ok=True)
            self.root_dir = self.root_dir.resolve()

    # ------------------------------------------------------------------
    def archive(self, repo_path: Path, source_dir: Path) -> Optional[Path]:
        """Archive run outputs into structured live folders."""

        if not self.enabled or not self.root_dir:
            return None

        owner_slug, repo_slug = self._derive_identity(repo_path)
        timestamp = datetime.now(timezone.utc).strftime("%Y/%m/%d/%H%M%S")
        destination = self.root_dir / owner_slug / repo_slug / timestamp
        destination.parent.mkdir(parents=True, exist_ok=True)

        # Copy tree (ensuring unique target)
        suffix = 1
        final_destination = destination
        while final_destination.exists():
            final_destination = destination.parent / f"{timestamp}-{suffix:02d}"
            suffix += 1

        shutil.copytree(source_dir, final_destination)
        self._write_metadata(final_destination, repo_path, source_dir)
        self._prune_history(final_destination.parent)
        self._update_latest_pointer(final_destination)
        return final_destination

    # ------------------------------------------------------------------
    def _derive_identity(self, repo_path: Path) -> Tuple[str, str]:
        owner = "local"
        repo_name = repo_path.name or "repository"

        git_dir = repo_path / ".git"
        if git_dir.exists():
            remote = self._capture_cmd(
                ["git", "-C", str(repo_path), "config", "--get", "remote.origin.url"]
            )
            if remote:
                owner_candidate, repo_candidate = self._parse_remote(remote)
                owner = owner_candidate or owner
                repo_name = repo_candidate or repo_name
            else:
                repo_candidate = self._capture_cmd(
                    ["git", "-C", str(repo_path), "rev-parse", "--show-toplevel"]
                )
                if repo_candidate:
                    repo_name = Path(repo_candidate).name

        return self._slugify(owner), self._slugify(repo_name)

    # ------------------------------------------------------------------
    @staticmethod
    def _parse_remote(remote: str) -> Tuple[Optional[str], Optional[str]]:
        remote = remote.strip().removesuffix(".git")

        if "@" in remote and ":" in remote:
            # git@host:owner/name
            _, remainder = remote.split(":", 1)
        else:
            remainder = remote.split("//", 1)[-1]
            if "/" in remainder:
                remainder = remainder.split("/", 1)[1]

        parts = [part for part in remainder.split("/") if part]
        if len(parts) >= 2:
            return parts[-2], parts[-1]
        if parts:
            return None, parts[-1]
        return None, None

    # ------------------------------------------------------------------
    def _write_metadata(
        self, archive_dir: Path, repo_path: Path, source_dir: Path
    ) -> None:
        repo_dir = archive_dir.parent
        owner_dir = repo_dir.parent if repo_dir else None

        meta = {
            "archived_at_utc": datetime.now(timezone.utc).isoformat(),
            "source_repo": str(repo_path.resolve()),
            "source_output": str(source_dir.resolve()),
            "archived_output": str(archive_dir.resolve()),
            "owner": owner_dir.name if owner_dir else "local",
            "repo": repo_dir.name if repo_dir else "repo",
            "output_files": sorted(self._relative_file_names(archive_dir)),
            "client_metadata": self.metadata,
        }

        commit = self._capture_cmd(["git", "-C", str(repo_path), "rev-parse", "HEAD"])
        if commit:
            meta["git_commit"] = commit

        branch = self._capture_cmd(
            ["git", "-C", str(repo_path), "rev-parse", "--abbrev-ref", "HEAD"]
        )
        if branch:
            meta["git_branch"] = branch

        with (archive_dir / "metadata.json").open("w", encoding="utf-8") as handle:
            json.dump(meta, handle, indent=2)

    # ------------------------------------------------------------------
    def _relative_file_names(self, source_dir: Path) -> Iterable[str]:
        for path in sorted(source_dir.rglob("*")):
            if path.is_file():
                yield str(path.relative_to(source_dir))

    # ------------------------------------------------------------------
    def _prune_history(self, per_repo_root: Path) -> None:
        if not self.max_runs_per_repo or self.max_runs_per_repo <= 0:
            return

        runs = sorted(
            [p for p in per_repo_root.iterdir() if p.is_dir()],
            key=lambda p: p.stat().st_mtime,
        )
        while len(runs) > self.max_runs_per_repo:
            oldest = runs.pop(0)
            shutil.rmtree(oldest, ignore_errors=True)

    # ------------------------------------------------------------------
    def _update_latest_pointer(self, destination: Path) -> None:
        latest_path = destination.parent / "latest"
        if latest_path.exists() or latest_path.is_symlink():
            if latest_path.is_dir() and not latest_path.is_symlink():
                shutil.rmtree(latest_path)
            else:
                latest_path.unlink()

        try:
            latest_path.symlink_to(destination)
        except OSError:
            shutil.copytree(destination, latest_path)

    # ------------------------------------------------------------------
    @staticmethod
    def _slugify(value: str) -> str:
        clean = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip().lower())
        clean = re.sub(r"-+", "-", clean)
        return clean.strip("-_") or "repo"

    # ------------------------------------------------------------------
    @staticmethod
    def _capture_cmd(cmd: Sequence[str]) -> Optional[str]:
        try:
            result = subprocess.run(cmd, check=False, capture_output=True, text=True)
            data = result.stdout.strip()
            return data or None
        except FileNotFoundError:
            return None
