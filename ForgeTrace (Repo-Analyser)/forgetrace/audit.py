"""Main audit engine - Author: Peter"""
import sys
from pathlib import Path
from typing import Any, Dict
from .scanners import (
    SBOMScanner, LicenseScanner, GitScanner, SimilarityScanner, 
    SecretsScanner, SASTScanner, VulnerabilityScanner
)
from .classifiers import IPClassifier
from .reporters import JSONReporter, MarkdownReporter, HTMLReporter, PDFReporter
from .policy import PolicyEngine


class AuditEngine:
    """
    Main orchestrator for ForgeTrace IP audit workflow.
    
    Coordinates all scanners, classifiers, and reporters to produce
    comprehensive IP audit reports with security and compliance analysis.
    """
    
    def __init__(self, repo_path: str | Path, output_dir: str | Path, config: Dict[str, Any]) -> None:
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
            findings["vulnerabilities"] = VulnerabilityScanner(self.repo_path, self.config).scan()
        
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
                "details": v.details
            }
            for v in violations
        ]
        
        # Generate reports
        JSONReporter(findings, self.output_dir).generate()
        MarkdownReporter(findings, self.output_dir, self.config).generate()
        HTMLReporter(findings, self.output_dir, self.config).generate()
        
        if self.config.get("output", {}).get("include_pdf", True):
            PDFReporter(findings, self.output_dir, self.config).generate()
        
        # Fail audit if any BLOCK-level policy violations
        if policy_engine.should_fail_audit():
            print("\n❌ Audit FAILED due to policy violations")
            sys.exit(1)
        
        print("\n✅ Audit completed successfully")
