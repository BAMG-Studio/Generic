"""Main audit engine - Author: Peter"""
from pathlib import Path
import json
from .scanners import SBOMScanner, LicenseScanner, GitScanner, SimilarityScanner, SecretsScanner, SASTScanner
from .classifiers import IPClassifier
from .reporters import JSONReporter, MarkdownReporter, HTMLReporter, PDFReporter

class AuditEngine:
    def __init__(self, repo_path, output_dir, config):
        self.repo_path = Path(repo_path)
        self.output_dir = Path(output_dir)
        self.config = config
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def run(self):
        findings = {}
        
        # Sprint 1: Core scanners
        findings["sbom"] = SBOMScanner(self.repo_path, self.config).scan()
        findings["git"] = GitScanner(self.repo_path, self.config).scan()
        findings["similarity"] = SimilarityScanner(self.repo_path, self.config).scan()
        
        # Sprint 2: Compliance
        findings["licenses"] = LicenseScanner(self.repo_path, self.config).scan()
        
        # Sprint 3: Security
        findings["secrets"] = SecretsScanner(self.repo_path, self.config).scan()
        findings["sast"] = SASTScanner(self.repo_path, self.config).scan()
        
        # Sprint 4: Classification & scoring
        classifier = IPClassifier(findings, self.config)
        findings["classification"] = classifier.classify()
        findings["rewriteability"] = classifier.score_rewriteability()
        findings["cost_estimate"] = classifier.estimate_cost()
        
        # Generate reports
        JSONReporter(findings, self.output_dir).generate()
        MarkdownReporter(findings, self.output_dir, self.config).generate()
        HTMLReporter(findings, self.output_dir, self.config).generate()
        
        if self.config.get("output", {}).get("include_pdf", True):
            PDFReporter(findings, self.output_dir, self.config).generate()
