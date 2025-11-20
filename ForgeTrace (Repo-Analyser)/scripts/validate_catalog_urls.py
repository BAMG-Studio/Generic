#!/usr/bin/env python3
"""Validate that every catalog URL is reachable via git ls-remote."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

from forgetrace.training.catalog import PHASE_REPOS
from forgetrace.training.core import Phase, RepoSpec


def _phase_choices() -> List[str]:
    return [phase.name for phase in Phase]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run git ls-remote against every repository in the catalog.",
    )
    parser.add_argument(
        "--phase",
        dest="phases",
        action="append",
        choices=_phase_choices(),
        help="Restrict validation to the provided phase (repeatable).",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=25,
        help="Per-repository timeout in seconds (default: 25).",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=1,
        help="Number of retries per repository when ls-remote fails (default: 1).",
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=2.0,
        help="Seconds to sleep between retries (default: 2).",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        help="Optional path to persist pass/fail results as JSON.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the repos to be checked without running git.",
    )
    return parser.parse_args()


def _resolve_phases(raw_phases: Sequence[str] | None) -> List[Phase]:
    if not raw_phases:
        return list(Phase)
    normalized = {value.upper() for value in raw_phases}
    return sorted((Phase[name] for name in normalized), key=lambda phase: phase.value)


def _selected_repos(phases: Sequence[Phase]) -> Iterable[RepoSpec]:
    for phase in phases:
        for repo in PHASE_REPOS.get(phase, ()):  # type: ignore[arg-type]
            yield repo


def _git_executable() -> str:
    git_path = shutil.which("git")
    if not git_path:
        raise RuntimeError("git executable not found in PATH")
    return git_path


def _validate_single(
    git_cmd: str,
    repo: RepoSpec,
    timeout: int,
    retries: int,
    sleep_seconds: float,
) -> Tuple[bool, str]:
    attempt = 0
    while attempt <= retries:
        try:
            subprocess.run(
                [git_cmd, "ls-remote", "--heads", repo.url],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                timeout=timeout,
            )
            return True, ""
        except subprocess.TimeoutExpired:
            error = f"timed out after {timeout}s"
        except subprocess.CalledProcessError as exc:
            stderr = exc.stderr.decode("utf-8", errors="ignore") if exc.stderr else ""
            error = stderr.strip() or f"exit code {exc.returncode}"
        except OSError as exc:
            error = str(exc)
        attempt += 1
        if attempt > retries:
            break
        time.sleep(max(0.0, sleep_seconds))
    return False, error


def _summarize(results: Dict[str, Dict[str, str]]) -> None:
    failures = results["failures"]
    if not failures:
        print("All catalog URLs validated successfully.")
        return
    print("\nFailures detected:")
    for repo_name, message in failures.items():
        print(f"- {repo_name}: {message}")


def _write_report(path: Path, results: Dict[str, Dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(results, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Validation report written to {path}")


def main() -> None:
    args = _parse_args()
    phases = _resolve_phases(args.phases)
    repos = tuple(_selected_repos(phases))

    if args.dry_run:
        print("Planned catalog URL validation targets:")
        for repo in repos:
            print(f"- {repo.phase.name}: {repo.name} -> {repo.url}")
        return

    git_cmd = _git_executable()
    results: Dict[str, Dict[str, str]] = {"passed": {}, "failures": {}}

    for repo in repos:
        ok, message = _validate_single(
            git_cmd=git_cmd,
            repo=repo,
            timeout=args.timeout,
            retries=max(0, args.retries),
            sleep_seconds=max(0.0, args.sleep),
        )
        if ok:
            results["passed"][repo.name] = repo.url
            print(f"[OK] {repo.name} ({repo.phase.name})")
        else:
            results["failures"][repo.name] = message
            print(f"[FAIL] {repo.name} ({repo.phase.name}) -> {message}")

    _summarize(results)

    if args.output_json:
        _write_report(args.output_json, results)

    if results["failures"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
