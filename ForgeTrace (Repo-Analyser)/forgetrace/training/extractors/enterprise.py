"""Enterprise systems feature extractor."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

from ..core import RepoSpec, TrainingExample
from .base import BaseExtractor

ENTERPRISE_MODULE_DIRS = {
    "modules",
    "module",
    "addons",
    "apps",
    "services",
    "service",
    "domains",
    "features",
    "packages",
    "bundles",
}

ENTERPRISE_VENDOR_DIRS = {
    "vendor",
    "third_party",
    "external",
    "community",
    "addons-community",
}

ENTERPRISE_CONFIG_FILES = {
    "application.yml",
    "application.yaml",
    "application.properties",
    "settings.py",
    "settings.gradle",
    "config.py",
    "config.json",
    "odoo.conf",
    "docker-compose.yml",
    "docker-compose.yaml",
    "helmfile.yaml",
    "helmfile.yml",
    "values.yaml",
    "values.yml",
}

TEMPLATE_SUFFIXES = {
    ".html",
    ".xml",
    ".jinja",
    ".jinja2",
    ".tpl",
    ".ftl",
    ".twig",
}

FRAMEWORK_KEYWORDS: Sequence[str] = (
    "org.springframework",
    "@restcontroller",
    "@service",
    "@repository",
    "@controller",
    "odoo.models",
    "from odoo",
    "django.db",
    "fastapi",
    "flask",
    "celery",
    "kafka",
    "rabbitmq",
    "graphql",
    "typeorm",
    "nestjs",
    "ActiveRecord",
    "EntityManager",
    "CommandHandler",
)

BUSINESS_TERMS: Sequence[str] = (
    "invoice",
    "billing",
    "ledger",
    "customer",
    "client",
    "account",
    "payment",
    "subscription",
    "contract",
    "policy",
    "compliance",
    "workflow",
    "fulfillment",
    "inventory",
    "supply",
    "warehouse",
    "logistics",
    "quotation",
    "order",
    "approval",
)

API_ENDPOINT_PATTERNS: Sequence[re.Pattern[str]] = (
    re.compile(r"@(?:Get|Post|Put|Delete|Patch)Mapping"),
    re.compile(r"@RequestMapping"),
    re.compile(r"app\.(?:get|post|put|delete|patch)\(", re.IGNORECASE),
    re.compile(r"router\.[a-z]+\(", re.IGNORECASE),
    re.compile(r"^\s*def\s+[a-z0-9_]+\(self,\s*request", re.IGNORECASE | re.MULTILINE),
    re.compile(r"Route::[a-zA-Z]+"),
)

PLUGIN_PATTERNS: Sequence[re.Pattern[str]] = (
    re.compile(r"register_(?:module|plugin|addon)", re.IGNORECASE),
    re.compile(r"init_app\(", re.IGNORECASE),
    re.compile(r"Module\.forRoot"),
    re.compile(r"apps\.populate"),
    re.compile(r"registerPlugin", re.IGNORECASE),
    re.compile(r"add_extension", re.IGNORECASE),
    re.compile(r"ExtensionPoint", re.IGNORECASE),
)

ASYNC_KEYWORDS: Sequence[str] = (
    "async def",
    "@Async",
    "Celery",
    "apply_async",
    "Promise",
    "CompletableFuture",
    "TaskRunner",
    "asyncio",
    "asyncio.create_task",
    "RxJava",
    "EventLoop",
)

DATA_ACCESS_KEYWORDS: Sequence[str] = (
    "Repository",
    "EntityManager",
    "Session",
    "cursor.execute",
    "SELECT ",
    "INSERT ",
    "UPDATE ",
    "DELETE ",
    "load_workbook",
)

ORCHESTRATION_KEYWORDS: Sequence[str] = (
    "orchestr",
    "workflow",
    "pipeline",
    "scheduler",
    "cron",
    "airflow",
    "dag",
)


class EnterpriseExtractor(BaseExtractor):
    """Extract enterprise architecture signals from large codebases."""

    def extract(self, repo: RepoSpec) -> List[TrainingExample]:
        repo_dir = self._ensure_repo(repo)
        vuln_features = self._repo_vulnerability_features(repo_dir)
        examples: List[TrainingExample] = []

        for file_path in repo_dir.rglob("*"):
            if not file_path.is_file() or not self._is_source_file(file_path):
                continue

            text = file_path.read_text(errors="ignore")
            base_features = self._collect_basic_features(file_path)
            ent_features = self._enterprise_features(file_path, text)
            features = {**base_features, **ent_features, **vuln_features}

            label, confidence = self._infer_label(file_path, features)
            metadata = {
                "confidence": f"{confidence:.2f}",
                "label_source": "enterprise_heuristic",
            }

            examples.append(
                self._to_training_example(repo, file_path, label, features, metadata)
            )

        return examples

    def validator(self):
        from ..validators.base import QualityValidator

        return QualityValidator()

    def _enterprise_features(self, file_path: Path, text: str) -> Dict[str, float]:
        lower_path = [part.lower() for part in file_path.parts]
        lower_text = text.lower()
        lines = text.splitlines()

        module_hits = sum(1 for part in lower_path if part in ENTERPRISE_MODULE_DIRS)
        module_depth_score = module_hits / max(len(file_path.parts), 1)

        vendor_indicator = (
            1.0 if any(part in ENTERPRISE_VENDOR_DIRS for part in lower_path) else 0.0
        )

        config_indicator = (
            1.0 if file_path.name.lower() in ENTERPRISE_CONFIG_FILES else 0.0
        )
        if file_path.suffix.lower() in {
            ".yml",
            ".yaml",
            ".properties",
            ".conf",
        } and any(segment in {"config", "settings", "env"} for segment in lower_path):
            config_indicator = 1.0

        template_indicator = (
            1.0
            if (
                file_path.suffix.lower() in TEMPLATE_SUFFIXES
                or any(segment in {"templates", "views"} for segment in lower_path)
            )
            else 0.0
        )

        framework_keyword_hits = sum(
            lower_text.count(keyword.lower()) for keyword in FRAMEWORK_KEYWORDS
        )
        framework_keyword_variety = sum(
            1 for keyword in FRAMEWORK_KEYWORDS if keyword.lower() in lower_text
        )

        business_term_hits = sum(lower_text.count(term) for term in BUSINESS_TERMS)
        business_context_density = business_term_hits / max(len(lines), 1)

        api_endpoint_count = float(
            sum(len(pattern.findall(text)) for pattern in API_ENDPOINT_PATTERNS)
        )

        plugin_registration_hits = float(
            sum(len(pattern.findall(text)) for pattern in PLUGIN_PATTERNS)
        )

        async_processing_indicator = (
            1.0
            if any(keyword.lower() in lower_text for keyword in ASYNC_KEYWORDS)
            else 0.0
        )

        data_access_indicator = (
            1.0
            if any(keyword.lower() in lower_text for keyword in DATA_ACCESS_KEYWORDS)
            else 0.0
        )

        orchestration_matches = sum(
            lower_text.count(keyword) for keyword in ORCHESTRATION_KEYWORDS
        )
        orchestration_signal = 1.0 if orchestration_matches > 0 else 0.0
        orchestration_path_indicator = (
            1.0
            if any(
                segment
                in {
                    "pipeline",
                    "pipelines",
                    "workflow",
                    "workflows",
                    "airflow",
                    "dags",
                    "dag",
                }
                for segment in lower_path
            )
            else 0.0
        )

        return {
            "module_depth_score": module_depth_score,
            "vendor_path_indicator": vendor_indicator,
            "config_indicator": config_indicator,
            "template_indicator": template_indicator,
            "framework_keyword_hits": float(framework_keyword_hits),
            "framework_keyword_variety": float(framework_keyword_variety),
            "business_context_density": float(business_context_density),
            "api_endpoint_count": api_endpoint_count,
            "plugin_registration_hits": plugin_registration_hits,
            "async_processing_indicator": async_processing_indicator,
            "data_access_indicator": data_access_indicator,
            "orchestration_signal": orchestration_signal,
            "orchestration_keyword_hits": float(orchestration_matches),
            "orchestration_path_indicator": orchestration_path_indicator,
        }

    def _infer_label(
        self, file_path: Path, features: Dict[str, float]
    ) -> Tuple[str, float]:
        if features.get("vendor_path_indicator", 0.0) >= 1.0:
            return "third_party", 0.92
        if (
            features.get("config_indicator", 0.0) >= 1.0
            and features.get("module_depth_score", 0.0) >= 0.4
        ):
            return "third_party", 0.85
        if (
            features.get("business_context_density", 0.0) >= 0.03
            and features.get("api_endpoint_count", 0.0) >= 2.0
        ):
            return "foreground", 0.85
        if (
            features.get("framework_keyword_hits", 0.0) >= 3.0
            and features.get("module_depth_score", 0.0) >= 0.25
        ):
            return "foreground", 0.8
        if (
            features.get("template_indicator", 0.0) >= 1.0
            and features.get("business_context_density", 0.0) < 0.02
        ):
            return "background", 0.75
        if features.get("plugin_registration_hits", 0.0) >= 1.0:
            return "foreground", 0.75
        if (
            features.get("orchestration_signal", 0.0) >= 1.0
            and features.get("data_access_indicator", 0.0) >= 1.0
        ):
            return "foreground", 0.72
        if (
            features.get("orchestration_path_indicator", 0.0) >= 1.0
            and features.get("framework_keyword_variety", 0.0) >= 2.0
        ):
            return "foreground", 0.7
        return "foreground", 0.6
