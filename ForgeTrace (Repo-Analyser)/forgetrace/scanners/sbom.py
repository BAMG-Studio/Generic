"""SBOM Scanner - Author: Peter"""
import subprocess
import json
from pathlib import Path

class SBOMScanner:
    def __init__(self, repo_path, config):
        self.repo_path = Path(repo_path)
        self.config = config
        
    def scan(self):
        syft_path = self.config.get("tools", {}).get("syft")
        if syft_path:
            return self._scan_syft(syft_path)
        return self._scan_fallback()
    
    def _scan_syft(self, syft_path):
        try:
            result = subprocess.run(
                [syft_path, "dir:" + str(self.repo_path), "-o", "json"],
                capture_output=True, text=True, timeout=300
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return {"tool": "syft", "format": "cyclonedx", "packages": data.get("artifacts", [])}
        except Exception as e:
            print(f"Syft failed: {e}")
        return self._scan_fallback()
    
    def _scan_fallback(self):
        packages = []
        # Python
        for req in self.repo_path.rglob("requirements.txt"):
            packages.extend(self._parse_requirements(req))
        for lock in self.repo_path.rglob("Pipfile.lock"):
            packages.extend(self._parse_pipfile(lock))
        # Node
        for pkg in self.repo_path.rglob("package.json"):
            packages.extend(self._parse_package_json(pkg))
        return {"tool": "fallback", "format": "custom", "packages": packages}
    
    def _parse_requirements(self, path):
        pkgs = []
        try:
            for line in path.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    pkgs.append({"name": line.split("==")[0].split(">=")[0], "type": "python", "file": str(path)})
        except:
            pass
        return pkgs
    
    def _parse_pipfile(self, path):
        try:
            data = json.loads(path.read_text())
            return [{"name": k, "version": v.get("version", ""), "type": "python", "file": str(path)} 
                    for k, v in data.get("default", {}).items()]
        except:
            return []
    
    def _parse_package_json(self, path):
        try:
            data = json.loads(path.read_text())
            pkgs = []
            for k, v in data.get("dependencies", {}).items():
                pkgs.append({"name": k, "version": v, "type": "node", "file": str(path)})
            return pkgs
        except:
            return []
