"""Unit tests for training data extractors' heuristic helpers."""

from __future__ import annotations

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

import pytest

from forgetrace.training.core import ExtractionConfig, Phase
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