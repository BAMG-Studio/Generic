"""Main audit engine - Author: Peter"""

import sys
from pathlib import Path
from typing import Any, Dict, List

from .classifiers import IPClassifier
from .policy import PolicyEngine
from .reporters import HTMLReporter, JSONReporter, MarkdownReporter, PDFReporter
from .scanners import (
    GitScanner,
    LicenseScanner,
    SASTScanner,
    SBOMScanner,
    SecretsScanner,
    SimilarityScanner,
    VulnerabilityScanner,
)
from .utils.output_manager import LiveArchiveManager


class AuditEngine:
    """
    Main orchestrator for ForgeTrace IP audit workflow.

    Coordinates all scanners, classifiers, and reporters to produce
    comprehensive IP audit reports with security and compliance analysis.
    """

    def __init__(
        self, repo_path: str | Path, output_dir: str | Path, config: Dict[str, Any]
    ) -> None:
        """
        Initialize the audit engine.

        Args:
            repo_path: Path to the repository to audit (string or Path object)
            output_dir: Directory where reports will be generated
            config: Configuration dictionary from config.yaml
        """
        self.repo_path: Path = Path(repo_path)
        self.output_dir: Path = Path(output_dir)
        self.config: Dict[str, Any] = config
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.archive_manager = LiveArchiveManager(self.config)

    def run(self) -> None:
        """
        Execute the complete audit workflow.

        Runs all configured scanners, performs IP classification,
        and generates all output reports (JSON, Markdown, HTML, PDF).
        """
        findings: Dict[str, Any] = {}

        # Sprint 1: Core scanners
        findings["sbom"] = SBOMScanner(self.repo_path, self.config).scan()
        findings["git"] = GitScanner(self.repo_path, self.config).scan()
        findings["similarity"] = SimilarityScanner(self.repo_path, self.config).scan()

        # Sprint 2: Compliance
        findings["licenses"] = LicenseScanner(self.repo_path, self.config).scan()

        # Sprint 3: Security
        findings["secrets"] = SecretsScanner(self.repo_path, self.config).scan()
        findings["sast"] = SASTScanner(self.repo_path, self.config).scan()

        # Vulnerability scanning (if enabled)
        if self.config.get("vulnerability_scanning", {}).get("enabled", True):
            findings["vulnerabilities"] = VulnerabilityScanner(
                self.repo_path, self.config
            ).scan()

        # Sprint 4: Classification & scoring
        classifier = IPClassifier(findings, self.config)
        findings["classification"] = classifier.classify()
        findings["rewriteability"] = classifier.score_rewriteability()
        findings["cost_estimate"] = classifier.estimate_cost()

        # Policy evaluation
        policy_engine = PolicyEngine(self.config)
        violations = policy_engine.evaluate(findings)
        findings["policy_violations"] = [
            {
                "policy_id": v.policy_id,
                "policy_name": v.policy_name,
                "severity": v.severity.value,
                "action": v.action.value,
                "message": v.message,
                "details": v.details,
            }
            for v in violations
        ]

        # Generate reports
        JSONReporter(findings, self.output_dir).generate()
        MarkdownReporter(findings, self.output_dir, self.config).generate()
        HTMLReporter(findings, self.output_dir, self.config).generate()

        self._persist_sbom_exports(findings.get("sbom"))

        if self.config.get("output", {}).get("include_pdf", True):
            PDFReporter(findings, self.output_dir, self.config).generate()

        archive_path = self.archive_manager.archive(self.repo_path, self.output_dir)
        if archive_path:
            print(f"\n📦 Live archive stored at: {archive_path}")

        # Fail audit if any BLOCK-level policy violations
        if policy_engine.should_fail_audit():
            print("\n❌ Audit FAILED due to policy violations")
            sys.exit(1)

        print("\n✅ Audit completed successfully")

    def _persist_sbom_exports(self, sbom_data: Dict[str, Any] | None) -> None:
        if not sbom_data:
            return
        if not self.config.get("output", {}).get("include_sbom", True):
            return
        exports = sbom_data.get("exports") if isinstance(sbom_data, dict) else None
        if not exports:
            return

        persisted: List[Dict[str, Any]] = []
        for export in exports:
            fmt = export.get("format", "sbom")
            content = export.get("content")
            if content is None:
                continue
            filename = self._derive_sbom_filename(fmt, persisted)
            target = self.output_dir / filename
            target.write_text(content)
            persisted.append(
                {
                    "format": fmt,
                    "path": target.name,
                    "size_bytes": target.stat().st_size,
                }
            )

        sbom_data["exports"] = persisted

    def _derive_sbom_filename(self, fmt: str, existing: List[Dict[str, Any]]) -> str:
        suffix = "json" if "json" in fmt else "txt"
        base = fmt.replace("/", "_").replace(":", "-").replace(" ", "-")
        base = base or "sbom"
        candidate = f"sbom.{base}.{suffix}"
        counter = 1
        existing_names = {entry.get("path") for entry in existing}
        while candidate in existing_names:
            candidate = f"sbom.{base}.{counter}.{suffix}"
            counter += 1
        return candidate
