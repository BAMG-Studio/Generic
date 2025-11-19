#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/preflight_check.sh [--phase PHASE]

Options:
  --phase PHASE   Phase name (FOUNDATIONAL, POLYGLOT, SECURITY, ENTERPRISE, RESEARCH, ALL).
                  Repeatable; defaults to ALL when omitted.
EOF
}

PHASES=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --phase)
      [[ $# -lt 2 ]] && { echo "Missing value for --phase" >&2; usage; exit 1; }
      PHASES+=("$2")
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if [[ ${#PHASES[@]} -eq 0 ]]; then
  PHASES=("ALL")
fi

mapfile -t VALID_PHASES < <(cat <<'EOF'
ALL
FOUNDATIONAL
POLYGLOT
SECURITY
ENTERPRISE
RESEARCH
EOF
)

validate_phase() {
  local phase="$1"
  for valid in "${VALID_PHASES[@]}"; do
    [[ "$phase" == "$valid" ]] && return 0
  done
  return 1
}

upper_phases=()
for phase in "${PHASES[@]}"; do
  upper=$(echo "$phase" | tr '[:lower:]' '[:upper:]')
  if ! validate_phase "$upper"; then
    echo "Invalid phase: $phase" >&2
    echo "Valid phases: ${VALID_PHASES[*]}" >&2
    exit 1
  fi
  upper_phases+=("$upper")
  if [[ "$upper" == "ALL" ]]; then
    # ALL means every phase; no need to keep other entries
    upper_phases=("ALL")
    break
  fi
done

requires_polyglot_threshold() {
  for phase in "$@"; do
    [[ "$phase" == "ALL" || "$phase" == "POLYGLOT" ]] && return 0
  done
  return 1
}

if requires_polyglot_threshold "${upper_phases[@]}"; then
  MIN_GB=80
else
  MIN_GB=40
fi

if [[ -n "${FORGETRACE_MIN_DISK_GB:-}" ]]; then
  MIN_GB=${FORGETRACE_MIN_DISK_GB}
fi

available_gb=$(df --output=avail -BG / | tail -n 1 | tr -dc '0-9')
if [[ -z "$available_gb" ]]; then
  echo "Unable to determine available disk space" >&2
  exit 1
fi

if (( available_gb < MIN_GB )); then
  echo "Insufficient disk space: need >= ${MIN_GB}GB, have ${available_gb}GB" >&2
  exit 1
fi

echo "Disk check passed: ${available_gb}GB available (threshold ${MIN_GB}GB)."

if ! command -v dvc >/dev/null 2>&1; then
  echo "DVC not installed; install before running training." >&2
  exit 1
fi

if ! dvc root >/dev/null 2>&1; then
  echo "Not inside a DVC repository." >&2
  exit 1
fi

if ! dvc remote list >/dev/null 2>&1; then
  echo "No DVC remote configured; configure remote before running training." >&2
  exit 1
fi

echo "Preflight checks completed for phases: ${upper_phases[*]}"
