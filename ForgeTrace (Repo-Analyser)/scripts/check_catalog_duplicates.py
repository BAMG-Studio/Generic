#!/usr/bin/env python3
"""Detect duplicate repository entries across the training catalog."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

from forgetrace.training.catalog import PHASE_REPOS
from forgetrace.training.core import Phase, RepoSpec


def _phase_choices() -> List[str]:
    return [phase.name for phase in Phase]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Detect duplicate catalog entries by name or URL.",
    )
    parser.add_argument(
        "--phase",
        dest="phases",
        action="append",
        choices=_phase_choices(),
        help="Restrict validation to the provided phase (repeatable).",
    )
    parser.add_argument(
        "--field",
        dest="fields",
        action="append",
        choices=("name", "url"),
        help="Field(s) to inspect for duplicates. Defaults to both.",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        help="Optional path to persist duplicate details as JSON.",
    )
    return parser.parse_args()


def _resolve_phases(raw_phases: Sequence[str] | None) -> List[Phase]:
    if not raw_phases:
        return list(Phase)
    normalized = {value.upper() for value in raw_phases}
    return sorted((Phase[name] for name in normalized), key=lambda phase: phase.value)


def _resolve_fields(raw_fields: Sequence[str] | None) -> Sequence[str]:
    if not raw_fields:
        return ("name", "url")
    return tuple(dict.fromkeys(field for field in raw_fields))


def _selected_repos(phases: Sequence[Phase]) -> Iterable[RepoSpec]:
    for phase in phases:
        for repo in PHASE_REPOS.get(phase, ()):  # type: ignore[arg-type]
            yield repo


def _duplicate_groups(repos: Iterable[RepoSpec], field: str) -> Dict[str, List[RepoSpec]]:
    groups: Dict[str, List[RepoSpec]] = defaultdict(list)
    for repo in repos:
        groups[getattr(repo, field)].append(repo)
    return {value: members for value, members in groups.items() if len(members) > 1}


def _format_group(value: str, repos: Sequence[RepoSpec]) -> str:
    phases = sorted({repo.phase.name for repo in repos})
    repo_names = ", ".join(repo.name for repo in repos)
    return f"{value} -> repos=[{repo_names}] phases={','.join(phases)}"


def _write_report(
    json_path: Path,
    phases: Sequence[Phase],
    duplicates: Mapping[str, Mapping[str, Sequence[RepoSpec]]],
) -> None:
    payload = {
        "phases": [phase.name for phase in phases],
        "duplicates": {
            field: [
                {
                    "value": value,
                    "repos": [repo.name for repo in repos],
                    "phases": sorted({repo.phase.name for repo in repos}),
                    "urls": sorted({repo.url for repo in repos}),
                }
                for value, repos in sorted(field_dups.items())
            ]
            for field, field_dups in duplicates.items()
        },
    }
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Duplicate report written to {json_path}")


def main() -> None:
    args = _parse_args()
    phases = _resolve_phases(args.phases)
    fields = _resolve_fields(args.fields)
    repos = tuple(_selected_repos(phases))

    failures = 0
    duplicate_report: Dict[str, Dict[str, Sequence[RepoSpec]]] = {}
    for field in fields:
        dupes = _duplicate_groups(repos, field)
        duplicate_report[field] = dupes
        if not dupes:
            print(f"No duplicates detected for field '{field}'.")
            continue
        failures = 1
        print(f"\nDuplicates detected for field '{field}':")
        for value, members in sorted(dupes.items()):
            print(f"- {_format_group(value, members)}")

    if args.output_json:
        _write_report(args.output_json, phases, duplicate_report)

    if failures:
        sys.exit(1)
    print("\nCatalog duplicate check passed.")


if __name__ == "__main__":
    main()
