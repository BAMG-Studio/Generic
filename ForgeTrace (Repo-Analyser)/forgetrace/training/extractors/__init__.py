"""Phase-specific training data extractors."""

from __future__ import annotations

from typing import Dict, Type

from ..core import ExtractionConfig, Phase
from .base import BaseExtractor
from .enterprise import EnterpriseExtractor
from .foundational import FoundationalExtractor
from .polyglot import PolyglotExtractor
from .research import ResearchExtractor
from .security import SecurityExtractor

EXTRACTOR_MAP: Dict[Phase, Type[BaseExtractor]] = {
    Phase.FOUNDATIONAL: FoundationalExtractor,
    Phase.POLYGLOT: PolyglotExtractor,
    Phase.SECURITY: SecurityExtractor,
    Phase.ENTERPRISE: EnterpriseExtractor,
    Phase.RESEARCH: ResearchExtractor,
}


def extractor_factory(config: ExtractionConfig) -> BaseExtractor:
    extractor_cls = EXTRACTOR_MAP.get(config.phase)
    if extractor_cls is None:
        raise ValueError(f"No extractor registered for phase {config.phase}")
    return extractor_cls(config)
