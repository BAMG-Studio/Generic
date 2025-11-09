"""Unit tests for training data extractors' heuristic helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Dict
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

import pytest

from forgetrace.training.core import ExtractionConfig, Phase, RepoSpec
from forgetrace.classifiers.ml_classifier import FileFeatures
from forgetrace.training.extractors.enterprise import EnterpriseExtractor
from forgetrace.training.extractors.research import ResearchExtractor
from forgetrace.training.extractors.security import SecurityExtractor


@pytest.fixture
def security_extractor(tmp_path: Path) -> SecurityExtractor:
    config = ExtractionConfig(
        phase=Phase.SECURITY,
        features=["dummy"],
        quality_thresholds={"min_confidence": 0.0},
        validation_rules=[],
    )
    extractor = SecurityExtractor(config)
    extractor.cache_dir = tmp_path  # avoid touching real cache
    return extractor


@pytest.fixture
def enterprise_extractor(tmp_path: Path) -> EnterpriseExtractor:
    config = ExtractionConfig(
        phase=Phase.ENTERPRISE,
        features=["dummy"],
        quality_thresholds={"min_confidence": 0.0},
        validation_rules=[],
    )
    extractor = EnterpriseExtractor(config)
    extractor.cache_dir = tmp_path
    return extractor


@pytest.fixture
def research_extractor(tmp_path: Path) -> ResearchExtractor:
    config = ExtractionConfig(
        phase=Phase.RESEARCH,
        features=["dummy"],
        quality_thresholds={"min_confidence": 0.0},
        validation_rules=[],
    )
    extractor = ResearchExtractor(config)
    extractor.cache_dir = tmp_path
    return extractor


def test_security_features_detect_secrets(tmp_path: Path, security_extractor: SecurityExtractor) -> None:
    file_path = tmp_path / ".env"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    secret_text = (
        "API_KEY = \"AKIAABCDEFGHIJKLMNOP\"\n"
        "SECRET_TOKEN = \"sk-1234567890abcdef1234567890abcdef\"\n"
        "DATABASE_PASSWORD = 'StrongPass123'\n"
    )
    file_path.write_text(secret_text)

    security_helper = getattr(security_extractor, "_security_features")
    features = security_helper(file_path, secret_text)

    assert features["secret_pattern_hits"] >= 1
    assert features["credential_keyword_density"] > 0.0
    assert features["secret_risk_score"] > 0.0
    assert features["config_indicator"] == 1.0


def test_enterprise_features_capture_business_context(
    tmp_path: Path, enterprise_extractor: EnterpriseExtractor
) -> None:
    file_path = tmp_path / "modules" / "billing" / "invoice_controller.py"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    text = (
        "from fastapi import APIRouter\n"
        "router = APIRouter()\n\n"
        "@router.post('/invoices')\n"
        "async def create_invoice(request):\n"
        "    payment = await process_payment(request)\n"
        "    return {'status': 'created', 'payment': payment}\n"
    )
    file_path.write_text(text)

    enterprise_helper = getattr(enterprise_extractor, "_enterprise_features")
    features = enterprise_helper(file_path, text)

    assert features["module_depth_score"] > 0.0
    assert features["business_context_density"] > 0.0
    assert features["api_endpoint_count"] >= 1.0
    assert features["async_processing_indicator"] == 1.0


def test_research_features_detect_citations(
    tmp_path: Path, research_extractor: ResearchExtractor
) -> None:
    file_path = tmp_path / "research" / "paper.md"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    text = (
        "# Novel Transformer Architecture\n\n"
        "We build on prior work [1] and [2] with a dataset derived from ImageNet.\n"
        "Refer to https://arxiv.org/abs/2106.04554 for baseline comparisons.\n"
        "Experimental results achieve an accuracy of 94% and F1 score of 0.93.\n"
    )
    file_path.write_text(text)

    research_helper = getattr(research_extractor, "_research_features")
    features = research_helper(file_path, text)

    assert features["citation_count"] >= 2.0
    assert features["paper_reference_hits"] >= 1.0
    assert features["dataset_mentions"] >= 1.0
    assert features["metric_mentions"] >= 1.0


def test_training_examples_include_vulnerability_metrics(
    tmp_path: Path, security_extractor: SecurityExtractor, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo_dir = tmp_path / "sample-repo"
    repo_dir.mkdir(parents=True, exist_ok=True)
    config_file = repo_dir / "config.yaml"
    config_file.write_text("API_KEY='secret'\n")

    def _mock_ensure_repo(self: SecurityExtractor, _repo: RepoSpec) -> Path:
        return repo_dir

    monkeypatch.setattr(SecurityExtractor, "_ensure_repo", _mock_ensure_repo)

    mocked_metrics = {
        "repo_vuln_density": 0.2,
        "repo_vuln_weighted_score": 5.1,
        "repo_osv_noise_ratio": 0.05,
        "repo_vulnerability_count": 4.0,
    }
    def _mock_vuln_features(self: SecurityExtractor, _repo_dir: Path) -> Dict[str, float]:
        return mocked_metrics

    monkeypatch.setattr(
        SecurityExtractor,
        "_repo_vulnerability_features",
        _mock_vuln_features,
    )

    repo_spec = RepoSpec(
        name="example/repo",
        url="https://example.invalid/repo.git",
        phase=Phase.SECURITY,
        languages=("python",),
        expected_signals=("security",),
        classification_targets=("foreground",),
    )

    examples = security_extractor.extract(repo_spec)
    assert examples, "Expected extractor to produce at least one training example"

    for key, value in mocked_metrics.items():
        assert examples[0].features.get(key) == value


def test_file_features_to_array_includes_repo_metrics() -> None:
    features = FileFeatures(
        file_path="src/example.py",
        lines_of_code=100,
        file_size_bytes=2048,
        extension=".py",
        path_depth=3,
        commit_count=10,
        author_count=2,
        days_since_first_commit=30,
        days_since_last_commit=5,
        commit_frequency=0.33,
        cyclomatic_complexity=5.0,
        maintainability_index=75.0,
        has_license_header=True,
        has_third_party_indicators=False,
        import_count=8,
        stdlib_import_ratio=0.6,
        third_party_import_ratio=0.4,
        max_similarity_score=0.1,
        similar_file_count=2,
        primary_author_commit_ratio=0.7,
        is_primary_author_external=False,
        repo_vuln_density=0.12,
        repo_vuln_weighted_score=6.5,
        repo_osv_noise_ratio=0.25,
        repo_vulnerability_count=4.0,
    )

    vector = features.to_array()
    assert len(vector) == 23
    assert vector[-4:] == [0.12, 6.5, 0.25, 4.0]