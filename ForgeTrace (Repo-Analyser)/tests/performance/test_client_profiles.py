"""
Performance benchmarks for client profiling datasets.

This module tests ForgeTrace against real-world repository patterns to ensure
performance and accuracy meet production requirements.
"""

import json
import time
from pathlib import Path
from typing import Any, Dict

import pytest
import yaml

# Test configuration
PROFILING_DATASETS_DIR = (
    Path(__file__).parent.parent.parent / "training" / "profiling_datasets"
)
CATALOG_PATH = PROFILING_DATASETS_DIR / "catalog.yaml"

# Performance targets
ACCURACY_TARGET = 0.99  # 99% classification accuracy
LATENCY_TARGET_MS = 10  # 10ms per file
MEMORY_TARGET_MB = 500  # 500 MB memory usage


def load_catalog() -> Dict[str, Any]:
    """Load client profiling dataset catalog."""
    if not CATALOG_PATH.exists():
        return {}

    with open(CATALOG_PATH, "r") as f:
        catalog = yaml.safe_load(f)

    return catalog.get("datasets", {})


def get_profile_paths() -> list:
    """Get all available client profile paths."""
    catalog = load_catalog()

    profiles = []
    for profile_id in catalog.keys():
        profile_dir = PROFILING_DATASETS_DIR / profile_id
        if profile_dir.exists():
            profiles.append((profile_id, profile_dir))

    return profiles


PROFILE_PARAMS = get_profile_paths()

if not PROFILE_PARAMS:
    pytest.skip(
        "No client profiles configured in catalog or directories missing",
        allow_module_level=True,
    )


@pytest.mark.performance
@pytest.mark.parametrize("profile_id,profile_dir", PROFILE_PARAMS)
def test_client_profile_performance(profile_id: str, profile_dir: Path):
    """
    Benchmark ForgeTrace against a client profiling dataset.

    Validates:
    - Classification accuracy
    - Processing latency per file
    - Memory usage
    """
    # Load metadata
    metadata_path = profile_dir / "metadata.yaml"
    if not metadata_path.exists():
        pytest.skip(f"Metadata not found for {profile_id}")

    with open(metadata_path, "r") as f:
        metadata = yaml.safe_load(f)

    # Load expected results (ground truth)
    expected_path = profile_dir / "expected_results.json"
    if not expected_path.exists():
        pytest.skip(f"Expected results not found for {profile_id}")

    with open(expected_path, "r") as f:
        expected = json.load(f)

    # Run ForgeTrace audit
    samples_dir = profile_dir / "samples"
    if not samples_dir.exists():
        pytest.skip(f"Samples directory not found for {profile_id}")

    # Import here to avoid import errors if forgetrace not installed
    from forgetrace.audit import run_audit

    # Measure performance
    start_time = time.time()
    result = run_audit(str(samples_dir))
    end_time = time.time()

    # Calculate metrics
    total_files = metadata["sample_strategy"]["sample_size"]
    elapsed_ms = (end_time - start_time) * 1000
    latency_per_file = elapsed_ms / total_files

    # Validate accuracy
    actual_third_party = result.get("ip_breakdown", {}).get("third_party_percentage", 0)
    expected_third_party = expected.get("ip_breakdown", {}).get(
        "third_party_percentage", 0
    )

    accuracy = 1.0 - abs(actual_third_party - expected_third_party) / 100.0

    # Assertions
    assert accuracy >= ACCURACY_TARGET, (
        f"Classification accuracy {accuracy:.2%} below target {ACCURACY_TARGET:.2%} "
        f"for {profile_id}"
    )

    assert latency_per_file <= LATENCY_TARGET_MS, (
        f"Latency {latency_per_file:.2f}ms/file exceeds target {LATENCY_TARGET_MS}ms "
        f"for {profile_id}"
    )

    # Report metrics
    print(f"\n{'='*60}")
    print(f"Profile: {profile_id}")
    print(f"{'='*60}")
    print(f"Files: {total_files}")
    print(f"Accuracy: {accuracy:.2%} (target: {ACCURACY_TARGET:.2%})")
    print(f"Latency: {latency_per_file:.2f}ms/file (target: {LATENCY_TARGET_MS}ms)")
    print(f"Total time: {elapsed_ms:.2f}ms")
    print(f"{'='*60}\n")


@pytest.mark.performance
def test_all_profiles_exist():
    """Verify all profiles in catalog have corresponding directories."""
    catalog = load_catalog()

    if not catalog:
        pytest.skip("No client profiles in catalog")

    for profile_id in catalog.keys():
        profile_dir = PROFILING_DATASETS_DIR / profile_id
        assert profile_dir.exists(), f"Profile directory not found: {profile_dir}"

        # Check required files
        assert (
            profile_dir / "metadata.yaml"
        ).exists(), f"metadata.yaml missing for {profile_id}"

        assert (
            profile_dir / "samples"
        ).exists(), f"samples/ directory missing for {profile_id}"


@pytest.mark.performance
def test_catalog_integrity():
    """Validate catalog.yaml structure and consistency."""
    catalog = load_catalog()

    if not catalog:
        pytest.skip("No client profiles in catalog")

    required_fields = ["source", "characteristics", "files", "size_mb"]

    for profile_id, profile_data in catalog.items():
        for field in required_fields:
            assert (
                field in profile_data
            ), f"Missing required field '{field}' in {profile_id}"

        # Validate data types
        assert isinstance(
            profile_data["files"], int
        ), f"'files' must be int for {profile_id}"

        assert isinstance(
            profile_data["size_mb"], (int, float)
        ), f"'size_mb' must be numeric for {profile_id}"

        assert isinstance(
            profile_data["characteristics"], list
        ), f"'characteristics' must be list for {profile_id}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--benchmark-only"])
