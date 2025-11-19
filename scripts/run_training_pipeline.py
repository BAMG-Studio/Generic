"""Run training phases and persist outputs."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, List

import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from forgetrace.training.catalog import EXTRACTION_CONFIGS, PHASE_REPOS
from forgetrace.training.core import Phase, TrainingDataGenerator


def _phase_choices() -> List[str]:
    return ["ALL", *[phase.name for phase in Phase]]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ForgeTrace training pipeline")
    parser.add_argument(
        "--phase",
        dest="phases",
        action="append",
        help="Phase to run (repeatable). Defaults to ALL when omitted.",
        choices=_phase_choices(),
    )
    parser.add_argument(
        "--tiers",
        type=str,
        default="",
        help="Optional tier list (e.g., 1,2,3) for phased batching.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the execution plan without running extractors.",
    )
    return parser.parse_args()


def _resolve_phases(raw_phases: Iterable[str] | None) -> List[Phase]:
    if not raw_phases:
        return list(Phase)

    normalized = {value.upper() for value in raw_phases}
    if "ALL" in normalized:
        return list(Phase)

    resolved: List[Phase] = []
    for name in normalized:
        resolved.append(Phase[name])
    return sorted(resolved, key=lambda phase: phase.value)


def main() -> None:
    args = _parse_args()
    selected_phases = _resolve_phases(args.phases)

    tier_display = args.tiers if args.tiers else "(not specified)"
    print(
        "Selected phases: "
        + ", ".join(phase.name for phase in selected_phases)
        + f" | tiers: {tier_display}"
    )

    if args.dry_run:
        print("Dry run enabled; skipping extraction.")
        return

    output_dir = Path("training_output/dataset")
    generator = TrainingDataGenerator(
        output_dir=output_dir,
        configs=EXTRACTION_CONFIGS,
    )

    for phase in Phase:
        if phase not in selected_phases:
            continue
        repos = PHASE_REPOS.get(phase, [])
        if not repos:
            continue
        print(f"\n=== Running {phase.name} phase ({len(repos)} repos) ===")
        generator.run_phase(phase, repos)

    print("\n=== Validating selected dataset ===")
    selected_repo_map = {
        phase: tuple(PHASE_REPOS.get(phase, ())) for phase in selected_phases
    }
    generator.run_all_phases(selected_repo_map)


if __name__ == "__main__":
    main()