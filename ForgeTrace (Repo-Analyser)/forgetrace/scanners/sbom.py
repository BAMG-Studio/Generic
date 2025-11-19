"""SBOM Scanner - Author: Peter"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List


class SBOMScanner:
    DEFAULT_EXPORTS = ["cyclonedx-json"]

    def __init__(self, repo_path, config):
        self.repo_path = Path(repo_path)
        self.config = config
        output_cfg = (
            self.config.get("output", {}) if isinstance(self.config, dict) else {}
        )
        self.export_formats: List[str] = self._resolve_formats(output_cfg)

    def scan(self):
        syft_path = self._resolve_syft_path()
        if syft_path:
            return self._scan_syft(syft_path)
        return self._scan_fallback()

    def _resolve_syft_path(self) -> str | None:
        tools_cfg = (
            self.config.get("tools", {}) if isinstance(self.config, dict) else {}
        )
        syft_path = tools_cfg.get("syft")
        if syft_path:
            return syft_path
        return shutil.which("syft")

    def _resolve_formats(self, output_cfg: Dict[str, Any]) -> List[str]:
        formats = (
            output_cfg.get("sbom_formats") if isinstance(output_cfg, dict) else None
        )
        if not formats:
            return list(self.DEFAULT_EXPORTS)
        if isinstance(formats, str):
            return [formats]
        return [str(fmt) for fmt in formats if str(fmt).strip()]

    def _scan_syft(self, syft_path):
        try:
            primary = self._run_syft_json(syft_path)
            exports = self._collect_exports(syft_path)
            if primary is not None:
                return {
                    "tool": "syft",
                    "format": "syft-json",
                    "packages": primary.get("artifacts", []),
                    "exports": exports,
                }
            if exports:
                return {
                    "tool": "syft",
                    "format": "syft-json",
                    "packages": [],
                    "exports": exports,
                }
        except Exception as e:
            print(f"Syft failed: {e}")
        return self._scan_fallback()

    def _run_syft_json(self, syft_path: str) -> Dict[str, Any] | None:
        cmd = [syft_path, f"dir:{self.repo_path}", "-o", "json"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            return None
        return json.loads(result.stdout)

    def _collect_exports(self, syft_path: str) -> List[Dict[str, Any]]:
        exports: List[Dict[str, Any]] = []
        for fmt in self.export_formats:
            cmd = [syft_path, f"dir:{self.repo_path}", "-o", fmt]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                exports.append(
                    {
                        "format": fmt,
                        "content": result.stdout,
                    }
                )
            else:
                print(f"Syft export failed for format {fmt}: {result.stderr.strip()}")
        return exports

    def _scan_fallback(self):
        packages = []
        # Python
        for req in self.repo_path.rglob("requirements.txt"):
            packages.extend(self._parse_requirements(req))
        for lock in self.repo_path.rglob("Pipfile.lock"):
            packages.extend(self._parse_pipfile(lock))
        # Node
        for pkg in self.repo_path.rglob("package.json"):
            packages.extend(self._parse_package_json(pkg))
        return {"tool": "fallback", "format": "custom", "packages": packages}

    def _parse_requirements(self, path):
        pkgs = []
        try:
            for line in path.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    pkgs.append(
                        {
                            "name": line.split("==")[0].split(">=")[0],
                            "type": "python",
                            "file": str(path),
                        }
                    )
        except OSError:
            pass
        return pkgs

    def _parse_pipfile(self, path):
        try:
            data = json.loads(path.read_text())
            return [
                {
                    "name": k,
                    "version": v.get("version", ""),
                    "type": "python",
                    "file": str(path),
                }
                for k, v in data.get("default", {}).items()
            ]
        except (OSError, json.JSONDecodeError):
            return []

    def _parse_package_json(self, path):
        try:
            data = json.loads(path.read_text())
            pkgs = []
            for k, v in data.get("dependencies", {}).items():
                pkgs.append(
                    {"name": k, "version": v, "type": "node", "file": str(path)}
                )
            return pkgs
        except (OSError, json.JSONDecodeError):
            return []
