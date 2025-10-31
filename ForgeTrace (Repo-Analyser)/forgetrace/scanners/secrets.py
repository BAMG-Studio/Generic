"""Secrets Scanner - Author: Peter"""
import subprocess
import json
from pathlib import Path

class SecretsScanner:
    def __init__(self, repo_path, config):
        self.repo_path = Path(repo_path)
        self.config = config
        
    def scan(self):
        findings = []
        
        trufflehog = self.config.get("tools", {}).get("trufflehog")
        if trufflehog:
            findings.extend(self._scan_trufflehog(trufflehog))
        
        gitleaks = self.config.get("tools", {}).get("gitleaks")
        if gitleaks:
            findings.extend(self._scan_gitleaks(gitleaks))
        
        return {"findings": findings, "count": len(findings)}
    
    def _scan_trufflehog(self, tool_path):
        try:
            result = subprocess.run(
                [tool_path, "filesystem", str(self.repo_path), "--json"],
                capture_output=True, text=True, timeout=300
            )
            findings = []
            for line in result.stdout.splitlines():
                if line.strip():
                    try:
                        data = json.loads(line)
                        findings.append({
                            "tool": "trufflehog",
                            "type": data.get("DetectorName", "unknown"),
                            "file": data.get("SourceMetadata", {}).get("Data", {}).get("Filesystem", {}).get("file", ""),
                            "line": data.get("SourceMetadata", {}).get("Data", {}).get("Filesystem", {}).get("line", 0)
                        })
                    except:
                        pass
            return findings
        except Exception as e:
            print(f"TruffleHog failed: {e}")
            return []
    
    def _scan_gitleaks(self, tool_path):
        try:
            result = subprocess.run(
                [tool_path, "detect", "--source", str(self.repo_path), "--report-format", "json", "--report-path", "/dev/stdout"],
                capture_output=True, text=True, timeout=300
            )
            if result.stdout:
                data = json.loads(result.stdout)
                return [{
                    "tool": "gitleaks",
                    "type": f.get("RuleID", "unknown"),
                    "file": f.get("File", ""),
                    "line": f.get("StartLine", 0)
                } for f in data]
            return []
        except Exception as e:
            print(f"Gitleaks failed: {e}")
            return []
