"""SAST Scanner - Author: Peter"""

import json
import subprocess
from pathlib import Path


class SASTScanner:
    def __init__(self, repo_path, config):
        self.repo_path = Path(repo_path)
        self.config = config

    def scan(self):
        semgrep = self.config.get("tools", {}).get("semgrep")
        if not semgrep:
            return {"findings": [], "count": 0}

        try:
            result = subprocess.run(
                [semgrep, "scan", "--config=auto", "--json", str(self.repo_path)],
                capture_output=True,
                text=True,
                timeout=600,
            )
            if result.returncode in [0, 1]:  # 1 = findings found
                data = json.loads(result.stdout)
                findings = [
                    {
                        "rule": r.get("check_id", "unknown"),
                        "severity": r.get("extra", {}).get("severity", "INFO"),
                        "file": r.get("path", ""),
                        "line": r.get("start", {}).get("line", 0),
                        "message": r.get("extra", {}).get("message", ""),
                    }
                    for r in data.get("results", [])
                ]
                return {"findings": findings, "count": len(findings)}
        except Exception as e:
            print(f"Semgrep failed: {e}")

        return {"findings": [], "count": 0}
