#!/usr/bin/env python3
"""Utility for bumping MLflow versions across the repo once a patched release ships."""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path
from typing import List

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = REPO_ROOT / "config" / "mlflow_release.yaml"
REQUIREMENTS_PATH = REPO_ROOT / "requirements.txt"
DOCKERFILE_PATH = REPO_ROOT / "deployment" / "mlflow" / "Dockerfile"
SECURITY_PATH = REPO_ROOT / "SECURITY.md"


def _load_config() -> dict:
    if not CONFIG_PATH.exists():
        raise SystemExit(f"Config file not found: {CONFIG_PATH}")
    with CONFIG_PATH.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _dump_config(config: dict) -> None:
    with CONFIG_PATH.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(config, handle, sort_keys=False)


def _update_requirements(version: str) -> None:
    lines = REQUIREMENTS_PATH.read_text(encoding="utf-8").splitlines()
    updated = False
    pattern = re.compile(r"^(mlflow==)([^#\s]+)(.*)$")
    for idx, line in enumerate(lines):
        match = pattern.match(line)
        if match:
            prefix, _, suffix = match.groups()
            lines[idx] = f"{prefix}{version}{suffix}"
            updated = True
            break
    if not updated:
        raise SystemExit("Could not find pinned mlflow entry in requirements.txt")
    REQUIREMENTS_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _update_dockerfile(image_tag: str) -> None:
    lines = DOCKERFILE_PATH.read_text(encoding="utf-8").splitlines()
    for idx, line in enumerate(lines):
        if line.startswith("FROM ghcr.io/mlflow/mlflow:"):
            lines[idx] = f"FROM {image_tag}"
            break
    else:
        raise SystemExit("Could not update MLflow base image in Dockerfile")
    DOCKERFILE_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _format_cve_list(cves: List[str]) -> str:
    return "/".join(cves) if cves else "None"


def _update_security_md(version: str, cves: List[str], status: str) -> None:
    lines = SECURITY_PATH.read_text(encoding="utf-8").splitlines()
    table_line_prefix = "| mlflow |"
    replacement = f"| mlflow | {version} | {_format_cve_list(cves)} | {status} |"
    for idx, line in enumerate(lines):
        if line.startswith(table_line_prefix):
            lines[idx] = replacement
            break
    else:
        raise SystemExit("Could not locate MLflow row inside SECURITY.md")
    SECURITY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Update MLflow release metadata across the repo")
    parser.add_argument("--version", required=True, help="Target mlflow package version (e.g. 3.6.1)")
    parser.add_argument(
        "--image-tag",
        help="Full container image reference (defaults to ghcr.io/mlflow/mlflow:v<version>)",
    )
    parser.add_argument("--release-notes", help="URL for the upstream release notes", default="")
    parser.add_argument(
        "--status",
        default="✅ No known CVEs",
        help="Status string written to SECURITY.md",
    )
    parser.add_argument(
        "--cve",
        action="append",
        dest="cves",
        default=None,
        help="CVE identifier to track (repeatable). Leave empty once release is clean.",
    )
    parser.add_argument(
        "--upgrade-status",
        choices=["blocked", "monitoring", "queued", "shipped"],
        default="queued",
        help="High-level upgrade state stored in config",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    version = args.version
    image_tag = args.image_tag or f"ghcr.io/mlflow/mlflow:v{version}"
    cves = args.cves or []

    config = _load_config()
    config.update(
        {
            "current_version": version,
            "container_image": image_tag,
            "last_verified": dt.date.today().isoformat(),
            "release_notes_url": args.release_notes or config.get("release_notes_url", ""),
            "upgrade_status": args.upgrade_status,
            "safety_cves": cves,
        }
    )
    _dump_config(config)

    _update_requirements(version)
    _update_dockerfile(image_tag)
    _update_security_md(version, cves, args.status)

    print("MLflow upgrade metadata updated. Remember to:")
    for item in config.get("verification_checklist", []):
        print(f" - {item}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pragma: no cover
        print(f"[ERROR] {exc}", file=sys.stderr)
        sys.exit(1)
