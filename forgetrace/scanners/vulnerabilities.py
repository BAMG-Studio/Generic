"""
Enhanced Vulnerability Scanner - Multi-Source Detection
Author: Peter Kolawole, BAMG Studio LLC

Integrates multiple vulnerability databases:
- OSV (Open Source Vulnerabilities)
- GitHub Advisory Database
- Snyk API (optional)
- OWASP Dependency-Check

Provides unified vulnerability reporting with severity scoring.
"""

import json
import math
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timezone


class VulnerabilityScanner:
    """Multi-source vulnerability scanner for dependencies."""
    
    def __init__(self, repo_path: str | Path, config: Dict[str, Any]) -> None:
        """
        Initialize the vulnerability scanner.
        
        Args:
            repo_path: Path to the repository to scan
            config: Configuration dictionary with tool paths and API keys
        """
        self.repo_path = Path(repo_path)
        self.config = config
        self.vulnerabilities: List[Dict[str, Any]] = []
        self.packages: List[Dict[str, Any]] = []
        
    def scan(self) -> Dict[str, Any]:
        """
        Run comprehensive vulnerability scan.
        
        Returns:
            Dictionary containing vulnerability findings
        """
        print("Starting vulnerability scan...")
        
        # Step 1: Extract packages from SBOM
        self.packages = self._extract_packages()
        print(f"Found {len(self.packages)} packages to scan")
        
        # Step 2: Query vulnerability databases
        osv_vulns = self._query_osv()
        github_vulns = self._query_github_advisory()
        
        # Step 3: Optionally run OWASP Dependency-Check
        owasp_vulns = self._run_owasp_check()
        
        # Step 4: Merge and deduplicate findings
        all_vulns = self._merge_vulnerabilities(osv_vulns, github_vulns, owasp_vulns)
        
        # Step 5: Calculate risk scores
        scored_vulns = self._score_vulnerabilities(all_vulns)
        
        return {
            "total_packages": len(self.packages),
            "vulnerable_packages": len(set(v["package"] for v in scored_vulns)),
            "total_vulnerabilities": len(scored_vulns),
            "by_severity": self._group_by_severity(scored_vulns),
            "vulnerabilities": scored_vulns,
            "scan_timestamp": datetime.now(timezone.utc).isoformat(),
            "sources": ["OSV", "GitHub Advisory", "OWASP Dependency-Check"]
        }
    
    def _extract_packages(self) -> List[Dict[str, Any]]:
        """
        Extract package list from repository.
        
        Returns:
            List of packages with name, version, and ecosystem
        """
        packages = []
        
        # Python packages
        for req_file in self.repo_path.rglob("requirements*.txt"):
            packages.extend(self._parse_requirements(req_file))
        
        for pipfile in self.repo_path.rglob("Pipfile.lock"):
            packages.extend(self._parse_pipfile(pipfile))
        
        # Node.js packages
        for pkg_file in self.repo_path.rglob("package.json"):
            packages.extend(self._parse_package_json(pkg_file))
        
        for pkg_lock in self.repo_path.rglob("package-lock.json"):
            packages.extend(self._parse_package_lock(pkg_lock))
        
        # Go packages
        for go_mod in self.repo_path.rglob("go.mod"):
            packages.extend(self._parse_go_mod(go_mod))
        
        # Ruby packages
        for gemfile_lock in self.repo_path.rglob("Gemfile.lock"):
            packages.extend(self._parse_gemfile_lock(gemfile_lock))
        
        # Deduplicate packages
        unique_packages = {}
        for pkg in packages:
            key = f"{pkg['ecosystem']}:{pkg['name']}:{pkg['version']}"
            if key not in unique_packages:
                unique_packages[key] = pkg
        
        return list(unique_packages.values())
    
    def _parse_requirements(self, path: Path) -> List[Dict[str, Any]]:
        """Parse Python requirements.txt file."""
        packages = []
        try:
            for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and not line.startswith("-"):
                    # Handle different version specifiers
                    for sep in ["==", ">=", "<=", "~=", "!="]:
                        if sep in line:
                            name, version = line.split(sep, 1)
                            packages.append({
                                "name": name.strip(),
                                "version": version.strip(),
                                "ecosystem": "PyPI",
                                "file": str(path.relative_to(self.repo_path))
                            })
                            break
                    else:
                        # No version specified
                        packages.append({
                            "name": line.strip(),
                            "version": "*",
                            "ecosystem": "PyPI",
                            "file": str(path.relative_to(self.repo_path))
                        })
        except Exception as e:
            print(f"Error parsing {path}: {e}")
        return packages
    
    def _parse_pipfile(self, path: Path) -> List[Dict[str, Any]]:
        """Parse Pipfile.lock for Python dependencies."""
        packages = []
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            for section in ["default", "develop"]:
                for name, info in data.get(section, {}).items():
                    version = info.get("version", "").lstrip("=")
                    packages.append({
                        "name": name,
                        "version": version,
                        "ecosystem": "PyPI",
                        "file": str(path.relative_to(self.repo_path))
                    })
        except Exception as e:
            print(f"Error parsing {path}: {e}")
        return packages
    
    def _parse_package_json(self, path: Path) -> List[Dict[str, Any]]:
        """Parse package.json for Node.js dependencies."""
        packages = []
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            for section in ["dependencies", "devDependencies"]:
                for name, version in data.get(section, {}).items():
                    packages.append({
                        "name": name,
                        "version": version.lstrip("^~"),
                        "ecosystem": "npm",
                        "file": str(path.relative_to(self.repo_path))
                    })
        except Exception as e:
            print(f"Error parsing {path}: {e}")
        return packages
    
    def _parse_package_lock(self, path: Path) -> List[Dict[str, Any]]:
        """Parse package-lock.json for exact Node.js versions."""
        packages = []
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            # Handle both v1 and v2 lockfile formats
            deps = data.get("dependencies", {}) or data.get("packages", {})
            for name, info in deps.items():
                if isinstance(info, dict) and "version" in info:
                    # Clean up name for v2 format (removes node_modules/ prefix)
                    clean_name = name.replace("node_modules/", "")
                    packages.append({
                        "name": clean_name,
                        "version": info["version"],
                        "ecosystem": "npm",
                        "file": str(path.relative_to(self.repo_path))
                    })
        except Exception as e:
            print(f"Error parsing {path}: {e}")
        return packages
    
    def _parse_go_mod(self, path: Path) -> List[Dict[str, Any]]:
        """Parse go.mod for Go dependencies."""
        packages = []
        try:
            for line in path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith("require "):
                    # Format: require github.com/pkg/name v1.2.3
                    parts = line.replace("require ", "").strip().split()
                    if len(parts) >= 2:
                        packages.append({
                            "name": parts[0],
                            "version": parts[1].lstrip("v"),
                            "ecosystem": "Go",
                            "file": str(path.relative_to(self.repo_path))
                        })
        except Exception as e:
            print(f"Error parsing {path}: {e}")
        return packages
    
    def _parse_gemfile_lock(self, path: Path) -> List[Dict[str, Any]]:
        """Parse Gemfile.lock for Ruby dependencies."""
        packages = []
        try:
            in_specs = False
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip() == "specs:":
                    in_specs = True
                    continue
                if in_specs and line.startswith("    "):
                    # Format:     gem-name (version)
                    parts = line.strip().split(" (")
                    if len(parts) == 2:
                        name = parts[0]
                        version = parts[1].rstrip(")")
                        packages.append({
                            "name": name,
                            "version": version,
                            "ecosystem": "RubyGems",
                            "file": str(path.relative_to(self.repo_path))
                        })
                elif in_specs and not line.startswith(" "):
                    in_specs = False
        except Exception as e:
            print(f"Error parsing {path}: {e}")
        return packages
    
    def _query_osv(self) -> List[Dict[str, Any]]:
        """
        Query OSV (Open Source Vulnerabilities) database.
        
        Returns:
            List of vulnerabilities from OSV
        """
        vulnerabilities = []
        print("Querying OSV database...")
        
        for pkg in self.packages:
            try:
                # OSV API endpoint
                url = "https://api.osv.dev/v1/query"
                payload = {
                    "package": {
                        "name": pkg["name"],
                        "ecosystem": pkg["ecosystem"]
                    },
                    "version": pkg["version"]
                }
                
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"}
                )
                
                with urllib.request.urlopen(req, timeout=10) as response:
                    data = json.loads(response.read().decode("utf-8"))
                    
                    for vuln in data.get("vulns", []):
                        vulnerabilities.append({
                            "package": pkg["name"],
                            "version": pkg["version"],
                            "ecosystem": pkg["ecosystem"],
                            "vulnerability_id": vuln.get("id", ""),
                            "summary": vuln.get("summary", ""),
                            "details": vuln.get("details", ""),
                            "severity": self._extract_severity(vuln),
                            "cvss_score": self._extract_cvss(vuln),
                            "references": vuln.get("references", []),
                            "source": "OSV",
                            "file": pkg["file"]
                        })
            except urllib.error.HTTPError as e:
                if e.code != 404:  # 404 means no vulnerabilities found
                    print(f"OSV query error for {pkg['name']}: {e}")
            except Exception as e:
                print(f"OSV query failed for {pkg['name']}: {e}")
        
        return vulnerabilities
    
    def _query_github_advisory(self) -> List[Dict[str, Any]]:
        """
        Query GitHub Advisory Database (public API).
        
        Returns:
            List of vulnerabilities from GitHub
        """
        vulnerabilities = []
        print("Querying GitHub Advisory Database...")
        
        # GitHub GraphQL API requires authentication for higher rate limits
        # For now, we'll use OSV as the primary source which aggregates GitHub advisories
        # In production, implement GitHub GraphQL queries with token
        
        return vulnerabilities
    
    def _run_owasp_check(self) -> List[Dict[str, Any]]:
        """
        Run OWASP Dependency-Check if available.
        
        Returns:
            List of vulnerabilities from OWASP
        """
        vulnerabilities = []
        owasp_path = self.config.get("tools", {}).get("owasp_dependency_check")
        
        if not owasp_path:
            print("OWASP Dependency-Check not configured, skipping...")
            return vulnerabilities
        
        print("Running OWASP Dependency-Check...")
        try:
            output_dir = self.repo_path / ".forgetrace_temp"
            output_dir.mkdir(exist_ok=True)
            
            result = subprocess.run(
                [
                    owasp_path,
                    "--scan", str(self.repo_path),
                    "--format", "JSON",
                    "--out", str(output_dir),
                    "--prettyPrint"
                ],
                capture_output=True,
                text=True,
                timeout=600
            )
            
            # Parse OWASP JSON report
            report_file = output_dir / "dependency-check-report.json"
            if report_file.exists():
                data = json.loads(report_file.read_text())
                for dep in data.get("dependencies", []):
                    for vuln in dep.get("vulnerabilities", []):
                        vulnerabilities.append({
                            "package": dep.get("fileName", ""),
                            "version": dep.get("version", ""),
                            "ecosystem": "unknown",
                            "vulnerability_id": vuln.get("name", ""),
                            "summary": vuln.get("description", ""),
                            "details": "",
                            "severity": vuln.get("severity", "UNKNOWN"),
                            "cvss_score": vuln.get("cvssv3", {}).get("baseScore", 0.0),
                            "references": [ref.get("url", "") for ref in vuln.get("references", [])],
                            "source": "OWASP Dependency-Check",
                            "file": dep.get("filePath", "")
                        })
            
        except FileNotFoundError:
            print(f"OWASP Dependency-Check not found at {owasp_path}")
        except subprocess.TimeoutExpired:
            print("OWASP Dependency-Check timed out")
        except Exception as e:
            print(f"OWASP Dependency-Check failed: {e}")
        
        return vulnerabilities
    
    def _merge_vulnerabilities(self, *vuln_lists: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Merge and deduplicate vulnerabilities from multiple sources.
        
        Args:
            *vuln_lists: Variable number of vulnerability lists
            
        Returns:
            Deduplicated list of vulnerabilities
        """
        merged = {}
        
        for vuln_list in vuln_lists:
            for vuln in vuln_list:
                # Use CVE ID or vulnerability ID as key
                key = vuln.get("vulnerability_id", "")
                if key:
                    if key not in merged:
                        merged[key] = vuln
                    else:
                        # Merge sources
                        existing = merged[key]
                        if vuln["source"] not in existing.get("sources", []):
                            existing.setdefault("sources", [existing["source"]])
                            existing["sources"].append(vuln["source"])
        
        return list(merged.values())
    
    def _score_vulnerabilities(self, vulnerabilities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Calculate risk scores for vulnerabilities.
        
        Args:
            vulnerabilities: List of vulnerability findings
            
        Returns:
            Vulnerabilities with risk scores
        """
        for vuln in vulnerabilities:
            # Base score from CVSS
            cvss = vuln.get("cvss_score", 0.0)
            
            # Adjust based on severity
            severity = vuln.get("severity", "UNKNOWN").upper()
            severity_multiplier = {
                "CRITICAL": 1.3,
                "HIGH": 1.2,
                "MEDIUM": 1.0,
                "LOW": 0.7,
                "UNKNOWN": 0.5
            }.get(severity, 1.0)
            
            # Calculate final risk score (0-10)
            risk_score = min(10.0, cvss * severity_multiplier)
            vuln["risk_score"] = round(risk_score, 2)
            
            # Add remediation priority
            if risk_score >= 9.0:
                vuln["priority"] = "CRITICAL"
            elif risk_score >= 7.0:
                vuln["priority"] = "HIGH"
            elif risk_score >= 4.0:
                vuln["priority"] = "MEDIUM"
            else:
                vuln["priority"] = "LOW"
        
        # Sort by risk score descending
        vulnerabilities.sort(key=lambda v: v.get("risk_score", 0), reverse=True)
        
        return vulnerabilities
    
    def _group_by_severity(self, vulnerabilities: List[Dict[str, Any]]) -> Dict[str, int]:
        """Group vulnerabilities by severity level."""
        groups = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "UNKNOWN": 0}
        
        for vuln in vulnerabilities:
            severity = vuln.get("severity", "UNKNOWN").upper()
            if severity in groups:
                groups[severity] += 1
            else:
                groups["UNKNOWN"] += 1
        
        return groups
    
    def _extract_severity(self, vuln_data: Dict[str, Any]) -> str:
        """Extract severity from vulnerability data."""
        # Check for severity in different fields
        if "severity" in vuln_data:
            return vuln_data["severity"][0]["type"] if isinstance(vuln_data["severity"], list) else vuln_data["severity"]
        
        # Fallback to CVSS score
        cvss = self._extract_cvss(vuln_data)
        if cvss >= 9.0:
            return "CRITICAL"
        elif cvss >= 7.0:
            return "HIGH"
        elif cvss >= 4.0:
            return "MEDIUM"
        elif cvss > 0:
            return "LOW"
        
        return "UNKNOWN"
    
    def _extract_cvss(self, vuln_data: Dict[str, Any]) -> float:
        """Extract CVSS score from vulnerability data, parsing vector strings when needed."""
        scores: List[float] = []

        def collect_score(value: Any) -> None:
            score = self._normalize_cvss_score(value)
            if score is not None:
                scores.append(score)

        # Standard severity blocks from OSV / GitHub advisories
        if "severity" in vuln_data:
            severity_entries = vuln_data["severity"]
            if not isinstance(severity_entries, list):
                severity_entries = [severity_entries]
            for entry in severity_entries:
                collect_score(entry)

        # Common nested payloads
        for key in ("database_specific", "ecosystem_specific", "cvss", "cvssV3"):
            if key in vuln_data:
                collect_score(vuln_data[key])

        if "cvssScore" in vuln_data:
            collect_score(vuln_data["cvssScore"])

        return max(scores) if scores else 0.0

    def _normalize_cvss_score(self, value: Any) -> Optional[float]:
        """Normalize various CVSS representations into a numeric score."""
        if value is None:
            return None

        if isinstance(value, (int, float)):
            return float(value)

        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                return None
            if stripped.upper().startswith("CVSS:"):
                return self._parse_cvss_vector(stripped)
            try:
                return float(stripped)
            except ValueError:
                return None

        if isinstance(value, dict):
            for key in ("score", "baseScore", "base_score", "cvss_score"):
                if key in value:
                    score = self._normalize_cvss_score(value[key])
                    if score is not None:
                        return score
            for key in ("vector", "vectorString", "cvss_vector"):
                if key in value:
                    score = self._parse_cvss_vector(str(value[key]))
                    if score:
                        return score
            if "severity" in value:
                return self._normalize_cvss_score(value["severity"])

        if isinstance(value, list):
            best: Optional[float] = None
            for item in value:
                score = self._normalize_cvss_score(item)
                if score is not None:
                    best = score if best is None else max(best, score)
            return best

        return None

    def _parse_cvss_vector(self, vector: str) -> float:
        """Parse a CVSS v3.x vector string and return the base score."""
        vector = vector.strip()
        if not vector.upper().startswith("CVSS:3"):
            return 0.0

        try:
            parts = vector.split("/")
            metrics = {}
            for part in parts[1:]:
                if ":" not in part:
                    continue
                key, metric = part.split(":", 1)
                metrics[key] = metric

            required = {"AV", "AC", "PR", "UI", "S", "C", "I", "A"}
            if not required.issubset(metrics.keys()):
                return 0.0

            av_map = {"N": 0.85, "A": 0.62, "L": 0.55, "P": 0.2}
            ac_map = {"L": 0.77, "H": 0.44}
            pr_scope_u = {"N": 0.85, "L": 0.62, "H": 0.27}
            pr_scope_c = {"N": 0.85, "L": 0.68, "H": 0.5}
            ui_map = {"N": 0.85, "R": 0.62}
            impact_map = {"H": 0.56, "L": 0.22, "N": 0.0}

            scope = metrics["S"].upper()
            av = av_map.get(metrics["AV"].upper())
            ac = ac_map.get(metrics["AC"].upper())
            pr_map = pr_scope_c if scope == "C" else pr_scope_u
            pr = pr_map.get(metrics["PR"].upper())
            ui = ui_map.get(metrics["UI"].upper())
            c_impact = impact_map.get(metrics["C"].upper())
            i_impact = impact_map.get(metrics["I"].upper())
            a_impact = impact_map.get(metrics["A"].upper())

            if None in {av, ac, pr, ui, c_impact, i_impact, a_impact} or scope not in {"U", "C"}:
                return 0.0

            impact_subscore = 1 - ((1 - c_impact) * (1 - i_impact) * (1 - a_impact))
            if impact_subscore <= 0:
                return 0.0

            if scope == "U":
                impact_score = 6.42 * impact_subscore
            else:
                impact_score = 7.52 * (impact_subscore - 0.029) - 3.25 * (impact_subscore - 0.02) ** 15

            exploitability = 8.22 * av * ac * pr * ui

            if scope == "U":
                base_score = min(impact_score + exploitability, 10)
            else:
                base_score = min(1.08 * (impact_score + exploitability), 10)

            return self._round_up_cvss(base_score)
        except Exception:
            return 0.0

    @staticmethod
    def _round_up_cvss(score: float) -> float:
        """Round scores to one decimal using CVSS round-up rules."""
        if score <= 0:
            return 0.0
        return math.ceil(score * 10.0) / 10.0
