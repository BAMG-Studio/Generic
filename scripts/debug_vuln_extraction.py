"""Utility script to inspect vulnerability feature extraction for a repository."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from forgetrace.training.core import ExtractionConfig, Phase, RepoSpec
from forgetrace.training.extractors.security import SecurityExtractor


def build_repo_spec(repo: str, phase: Phase) -> RepoSpec:
    url = f"https://github.com/{repo}.git" if not repo.startswith("http") else repo
    languages: Sequence[str] = ("python",)
    expected_signals: Sequence[str] = (phase.name.lower(),)
    classification_targets: Sequence[str] = ("foreground", "third_party", "background")

    return RepoSpec(
        name=repo,
        url=url,
        phase=phase,
        languages=languages,
        expected_signals=expected_signals,
        classification_targets=classification_targets,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Debug vulnerability feature extraction.")
    parser.add_argument("--repo", required=True, help="Repository in owner/name or full git URL format")
    parser.add_argument(
        "--phase",
        default=Phase.SECURITY.name,
        choices=[phase.name for phase in Phase],
        help="Training phase to emulate",
    )
    parser.add_argument(
        "--output",
        default="training_output/debug",
        help="Directory to store extracted metrics JSON",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print intermediate metrics to stdout",
    )
    args = parser.parse_args()

    phase = Phase[args.phase]
    repo_spec = build_repo_spec(args.repo, phase)

    config = ExtractionConfig(
        phase=phase,
        features=(),
        quality_thresholds={},
        validation_rules=(),
    )
    extractor = SecurityExtractor(config)

    repo_dir = extractor._ensure_repo(repo_spec)  # type: ignore[reportPrivateUsage]
    metrics = extractor._repo_vulnerability_features(repo_dir)  # type: ignore[reportPrivateUsage]

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{repo_spec.short_name()}_vuln_features.json"
    output_file.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    if args.verbose:
        print(json.dumps(metrics, indent=2))

    print(f"✅ Vulnerability metrics written to {output_file}")


if __name__ == "__main__":
    main()
