"""Run all training phases and persist outputs."""

from __future__ import annotations

from pathlib import Path

import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from forgetrace.training.catalog import EXTRACTION_CONFIGS, PHASE_REPOS
from forgetrace.training.core import Phase, TrainingDataGenerator


def main() -> None:
    output_dir = Path("training_output/dataset")
    generator = TrainingDataGenerator(
        output_dir=output_dir,
        configs=EXTRACTION_CONFIGS,
    )

    for phase in Phase:
        repos = PHASE_REPOS.get(phase, [])
        if not repos:
            continue
        print(f"\n=== Running {phase.name} phase ({len(repos)} repos) ===")
        generator.run_phase(phase, repos)

    print("\n=== Validating full dataset ===")
    generator.run_all_phases({phase: tuple(repos) for phase, repos in PHASE_REPOS.items()})


if __name__ == "__main__":
    main()