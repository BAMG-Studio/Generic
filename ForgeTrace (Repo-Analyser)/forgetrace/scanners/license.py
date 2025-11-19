"""License Scanner - Author: Peter"""

import re
import subprocess
from pathlib import Path


class LicenseScanner:
    SPDX_PATTERNS = {
        "MIT": r"MIT License|Permission is hereby granted, free of charge",
        "Apache-2.0": r"Apache License.*Version 2\.0",
        "GPL-3.0": r"GNU GENERAL PUBLIC LICENSE.*Version 3",
        "GPL-2.0": r"GNU GENERAL PUBLIC LICENSE.*Version 2",
        "BSD-3-Clause": r"BSD 3-Clause|Redistribution and use in source and binary",
        "ISC": r"ISC License|Permission to use, copy, modify",
    }

    def __init__(self, repo_path, config):
        self.repo_path = Path(repo_path)
        self.config = config

    def scan(self):
        scancode_path = self.config.get("tools", {}).get("scancode")
        if scancode_path:
            return self._scan_scancode(scancode_path)
        return self._scan_heuristic()

    def _scan_scancode(self, scancode_path):
        try:
            result = subprocess.run(
                [scancode_path, "--license", "--json-pp", "-", str(self.repo_path)],
                capture_output=True,
                text=True,
                timeout=600,
            )
            if result.returncode == 0:
                import json

                data = json.loads(result.stdout)
                return {"tool": "scancode", "findings": data.get("files", [])}
        except Exception as e:
            print(f"ScanCode failed: {e}")
        return self._scan_heuristic()

    def _scan_heuristic(self):
        findings = []
        for lic_file in self.repo_path.rglob("LICENSE*"):
            findings.append(self._detect_license(lic_file))
        for src in self.repo_path.rglob("*.py"):
            if src.stat().st_size < 100000:
                findings.append(self._detect_license(src))
        return {"tool": "heuristic", "findings": [f for f in findings if f["license"]]}

    def _detect_license(self, path):
        try:
            content = path.read_text(errors="ignore")[:5000]
            for spdx, pattern in self.SPDX_PATTERNS.items():
                if re.search(pattern, content, re.IGNORECASE):
                    return {"file": str(path), "license": spdx, "confidence": "high"}
            return {"file": str(path), "license": None, "confidence": "none"}
        except OSError:
            return {"file": str(path), "license": None, "confidence": "error"}
