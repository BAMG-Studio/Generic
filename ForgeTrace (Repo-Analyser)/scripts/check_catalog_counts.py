#!/usr/bin/env python3
"""Verify repository counts per phase align with the training roadmap."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Mapping, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

from forgetrace.training.catalog import PHASE_REPOS
from forgetrace.training.core import Phase

EXPECTED_COUNTS: Mapping[Phase, int] = {
    Phase.FOUNDATIONAL: 7,
    Phase.POLYGLOT: 20,
    Phase.SECURITY: 9,
    Phase.ENTERPRISE: 10,
    Phase.RESEARCH: 8,
}


def _phase_choices() -> List[str]:
    return [phase.name for phase in Phase]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check that repo counts per phase meet expectations.",
    )
    parser.add_argument(
        "--phase",
        dest="phases",
        action="append",
        choices=_phase_choices(),
        help="Restrict to a subset of phases (repeatable).",
    )
    parser.add_argument(
        "--expect",
        dest="overrides",
        action="append",
        metavar="PHASE=COUNT",
        help="Override expected counts (e.g., POLYGLOT=18).",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        help="Optional path to persist count details as JSON.",
    )
    return parser.parse_args()


def _resolve_phases(raw_phases: Sequence[str] | None) -> List[Phase]:
    if not raw_phases:
        return list(Phase)
    normalized = {value.upper() for value in raw_phases}
    return sorted((Phase[name] for name in normalized), key=lambda phase: phase.value)


def _parse_overrides(raw_overrides: Sequence[str] | None) -> Dict[Phase, int]:
    overrides: Dict[Phase, int] = {}
    if not raw_overrides:
        return overrides
    for raw in raw_overrides:
        if "=" not in raw:
            raise ValueError(f"Invalid override '{raw}'. Use PHASE=COUNT.")
        phase_name, raw_count = raw.split("=", 1)
        phase = Phase[phase_name.upper()]
        overrides[phase] = int(raw_count)
    return overrides


def _phase_counts(phases: Sequence[Phase]) -> Dict[Phase, int]:
    return {phase: len(tuple(PHASE_REPOS.get(phase, ()))) for phase in phases}


def _write_report(path: Path, counts: Dict[Phase, Dict[str, int]]) -> None:
    payload = {
        "phases": {
            phase.name: values
            for phase, values in counts.items()
        }
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Count report written to {path}")


def main() -> None:
    args = _parse_args()
    phases = _resolve_phases(args.phases)
    overrides = _parse_overrides(args.overrides)
    actual = _phase_counts(phases)

    failures = 0
    report: Dict[Phase, Dict[str, int]] = {}
    total_actual = 0
    total_expected = 0

    print("Phase catalog counts:\n")
    for phase in phases:
        expected = overrides.get(phase, EXPECTED_COUNTS.get(phase, actual[phase]))
        count = actual[phase]
        delta = count - expected
        status = "OK" if delta == 0 else "MISMATCH"
        if delta != 0:
            failures = 1
        print(f"{phase.name:<13} actual={count:>2} expected={expected:>2} delta={delta:>+3} [{status}]")
        report[phase] = {
            "actual": count,
            "expected": expected,
            "delta": delta,
        }
        total_actual += count
        total_expected += expected

    print(f"\nTOTAL         actual={total_actual:>2} expected={total_expected:>2} delta={(total_actual - total_expected):>+3}")

    if args.output_json:
        _write_report(args.output_json, report)

    if failures:
        sys.exit(1)
    print("\nCatalog count check passed.")


if __name__ == "__main__":
    main()
