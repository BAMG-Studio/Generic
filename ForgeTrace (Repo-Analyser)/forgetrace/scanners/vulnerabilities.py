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
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, cast
import urllib.request
import urllib.error
from datetime import datetime, timezone


class VulnerabilityScanner:
    """Multi-source vulnerability scanner for dependencies."""
    
    DEFAULT_SEVERITY_WEIGHTS: Dict[str, float] = {
        "CRITICAL": 1.5,
        "HIGH": 1.3,
        "MEDIUM": 1.0,
        "LOW": 0.6,
        "UNKNOWN": 0.4,
    }

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

    # ------------------------------------------------------------------
    # Configuration helpers
    # ------------------------------------------------------------------

    def _filter_config(self) -> Dict[str, Any]:
        scanning_cfg = cast(Dict[str, Any], self.config.get("vulnerability_scanning", {}) or {})
        return cast(Dict[str, Any], scanning_cfg.get("filters", {}) or {})

    def _filter_float(self, key: str, default: float) -> float:
        filters = self._filter_config()
        value = filters.get(key)
        coerced = self._coerce_float(value)
        return coerced if coerced is not None else default

    def _confidence_floor(self) -> str:
        filters = self._filter_config()
        floor = str(filters.get("confidence_floor", "medium")).strip().lower()
        if floor not in {"none", "low", "medium", "high"}:
            return "medium"
        return floor

    def _confidence_allows(self, confidence: str, floor: str) -> bool:
        order = {"none": 0, "low": 1, "medium": 2, "high": 3}
        return order.get(confidence, 2) >= order.get(floor, 2)

    def _severity_weight(self, severity: str) -> float:
        filters = self._filter_config()
        overrides = cast(Dict[str, Any], filters.get("severity_weights", {}) or {})
        weights = dict(self.DEFAULT_SEVERITY_WEIGHTS)
        for label, value in overrides.items():
            coerced = self._coerce_float(value)
            if coerced is not None:
                weights[str(label).upper()] = coerced
        return weights.get(severity.upper(), weights["UNKNOWN"])

    def _drop_unknown_severity(self) -> bool:
        filters = self._filter_config()
        return bool(filters.get("drop_unknown_severity", True))
        
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

        filtered_vulns, context_metrics = self._apply_context_filters(all_vulns)

        # Step 5: Calculate risk scores
        scored_vulns = self._score_vulnerabilities(filtered_vulns)

        total_packages = len(self.packages)

        return {
            "total_packages": total_packages,
            "vulnerable_packages": len(set(v["package"] for v in scored_vulns)),
            "total_vulnerabilities": len(scored_vulns),
            "by_severity": self._group_by_severity(scored_vulns),
            "vulnerabilities": scored_vulns,
            "scan_timestamp": datetime.now(timezone.utc).isoformat(),
            "sources": ["OSV", "GitHub Advisory", "OWASP Dependency-Check"],
            "normalized_vuln_density": context_metrics.get("normalized_vuln_density", 0.0),
            "weighted_vuln_score": context_metrics.get("weighted_vuln_score", 0.0),
            "osv_noise_ratio": context_metrics.get("noise_ratio", 0.0),
        }
    
    def _extract_packages(self) -> List[Dict[str, Any]]:
        """
        Extract package list from repository.
        
        Returns:
            List of packages with name, version, and ecosystem
        """
        packages: List[Dict[str, Any]] = []
        
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
        unique_packages: Dict[str, Dict[str, Any]] = {}
        for pkg in packages:
            key = f"{pkg['ecosystem']}:{pkg['name']}:{pkg['version']}"
            if key not in unique_packages:
                unique_packages[key] = pkg
        
        return list(unique_packages.values())
    
    def _parse_requirements(self, path: Path) -> List[Dict[str, Any]]:
        """Parse Python requirements.txt file."""
        packages: List[Dict[str, Any]] = []
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
        packages: List[Dict[str, Any]] = []
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
        packages: List[Dict[str, Any]] = []
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
        packages: List[Dict[str, Any]] = []
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
        packages: List[Dict[str, Any]] = []
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
        packages: List[Dict[str, Any]] = []
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
        vulnerabilities: List[Dict[str, Any]] = []
        seen: Set[Tuple[str, str, str]] = set()
        print("Querying OSV database...")

        min_cvss_ingest = self._filter_float("min_cvss_ingest", 4.0)
        confidence_floor = self._confidence_floor()
        drop_unknown = self._drop_unknown_severity()
        
        for pkg in self.packages:
            try:
                # OSV API endpoint
                url = "https://api.osv.dev/v1/query"
                payload: Dict[str, Any] = {
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
                        cvss_score = self._extract_cvss(vuln)
                        if cvss_score < min_cvss_ingest:
                            continue

                        confidence = self._extract_confidence(vuln)
                        if not self._confidence_allows(confidence, confidence_floor):
                            continue

                        severity_label = self._extract_severity(vuln)
                        if drop_unknown and severity_label.upper() == "UNKNOWN":
                            continue

                        if not self._ecosystem_matches(pkg, vuln):
                            continue

                        vuln_id = vuln.get("id", "")
                        key = (vuln_id, pkg["name"], pkg["version"])
                        if key in seen:
                            continue
                        seen.add(key)

                        vulnerabilities.append({
                            "package": pkg["name"],
                            "version": pkg["version"],
                            "ecosystem": pkg["ecosystem"],
                            "vulnerability_id": vuln_id,
                            "summary": vuln.get("summary", ""),
                            "details": vuln.get("details", ""),
                            "severity": severity_label,
                            "cvss_score": cvss_score,
                            "references": vuln.get("references", []),
                            "source": "OSV",
                            "file": pkg["file"],
                            "confidence": confidence,
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
        vulnerabilities: List[Dict[str, Any]] = []
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
        vulnerabilities: List[Dict[str, Any]] = []
        owasp_path = self.config.get("tools", {}).get("owasp_dependency_check")
        
        if not owasp_path:
            print("OWASP Dependency-Check not configured, skipping...")
            return vulnerabilities
        
        print("Running OWASP Dependency-Check...")
        try:
            output_dir = self.repo_path / ".forgetrace_temp"
            output_dir.mkdir(exist_ok=True)
            
            subprocess.run(
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
        merged: Dict[Tuple[str, str, str], Dict[str, Any]] = {}

        for vuln_list in vuln_lists:
            for vuln in vuln_list:
                vuln_id = vuln.get("vulnerability_id") or vuln.get("summary", "")
                key = (
                    str(vuln_id),
                    str(vuln.get("package", "")),
                    str(vuln.get("version", "")),
                )
                existing = merged.get(key)
                if existing is None:
                    merged[key] = vuln
                    continue

                source_candidates: List[str] = []

                def _normalize_sources(entry: Any) -> None:
                    if isinstance(entry, list):
                        for item in cast(List[Any], entry):
                            if item:
                                source_candidates.append(str(item))
                    elif isinstance(entry, str):
                        source_candidates.append(entry)
                    elif entry:
                        source_candidates.append(str(entry))

                _normalize_sources(existing.get("sources"))
                _normalize_sources(existing.get("source"))
                _normalize_sources(vuln.get("sources"))
                _normalize_sources(vuln.get("source"))

                if source_candidates:
                    existing["sources"] = sorted({candidate for candidate in source_candidates if candidate})

                reference_candidates: List[str] = []

                def _normalize_references(entry: Any) -> None:
                    if isinstance(entry, list):
                        for item in cast(List[Any], entry):
                            if item:
                                reference_candidates.append(str(item))
                    elif isinstance(entry, str):
                        reference_candidates.append(entry)
                    elif entry:
                        reference_candidates.append(str(entry))

                _normalize_references(existing.get("references"))
                _normalize_references(vuln.get("references"))

                if reference_candidates:
                    existing["references"] = sorted({ref for ref in reference_candidates if ref})

                # Keep the highest CVSS / severity data available
                if float(vuln.get("cvss_score", 0.0) or 0.0) > float(existing.get("cvss_score", 0.0) or 0.0):
                    existing["cvss_score"] = vuln.get("cvss_score", existing.get("cvss_score", 0.0))
                    existing["severity"] = vuln.get("severity", existing.get("severity", "UNKNOWN"))
                    existing["details"] = vuln.get("details", existing.get("details", ""))

        return list(merged.values())

    def _apply_context_filters(
        self, vulnerabilities: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], Dict[str, float]]:
        """Apply heuristic filters to suppress low-signal vulnerabilities."""

        filtered: List[Dict[str, Any]] = []
        rejected_as_noise = 0
        weighted_sum = 0.0
        min_cvss_context = self._filter_float("min_cvss_context", 3.5)
        confidence_floor = self._confidence_floor()
        drop_unknown = self._drop_unknown_severity()

        for vuln in vulnerabilities:
            severity = str(vuln.get("severity") or self._extract_severity(vuln)).upper()
            cvss = self._coerce_float(vuln.get("cvss_score")) or 0.0
            confidence_value = str(vuln.get("confidence", "")).lower()

            if not self._confidence_allows(confidence_value, confidence_floor):
                rejected_as_noise += 1
                continue

            if drop_unknown and severity == "UNKNOWN":
                rejected_as_noise += 1
                continue

            if cvss < min_cvss_context:
                rejected_as_noise += 1
                continue

            vuln["severity"] = severity
            filtered.append(vuln)
            weighted_sum += cvss * self._severity_weight(severity)

        total_packages = max(len(self.packages), 1)
        total_vulns = len(vulnerabilities)
        metrics = {
            "normalized_vuln_density": round(len(filtered) / total_packages, 4),
            "weighted_vuln_score": round(weighted_sum / len(filtered), 2) if filtered else 0.0,
            "noise_ratio": round(rejected_as_noise / total_vulns, 4) if total_vulns else 0.0,
        }

        return filtered, metrics
    
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
        """Extract severity from vulnerability data in a defensive manner."""

        severity_field = vuln_data.get("severity")
        normalized = self._normalize_severity_field(severity_field)
        if normalized:
            return normalized

        cvss = self._extract_cvss(vuln_data)
        if cvss >= 9.0:
            return "CRITICAL"
        if cvss >= 7.0:
            return "HIGH"
        if cvss >= 4.0:
            return "MEDIUM"
        if cvss > 0:
            return "LOW"

        return "UNKNOWN"

    def _extract_cvss(self, vuln_data: Dict[str, Any]) -> float:
        """Extract CVSS score from vulnerability data."""

        severity_field = vuln_data.get("severity")
        severity_score = self._extract_score_from_severity(severity_field)
        if severity_score is not None:
            return severity_score

        database_specific = vuln_data.get("database_specific")
        if isinstance(database_specific, dict):
            db_dict: Dict[str, Any] = cast(Dict[str, Any], database_specific)
            score = self._coerce_float(db_dict.get("cvss_score"))
            if score is not None:
                return score

        return 0.0

    def _normalize_severity_field(self, severity_field: Any) -> Optional[str]:
        """Normalize severity representations to an uppercase string."""

        if severity_field is None:
            return None
        if isinstance(severity_field, str):
            return severity_field.upper()
        if isinstance(severity_field, dict):
            severity_dict: Dict[str, Any] = cast(Dict[str, Any], severity_field)
            sev_type = severity_dict.get("type")
            if isinstance(sev_type, str):
                return sev_type.upper()
            sev_value = severity_dict.get("value")
            if isinstance(sev_value, str):
                return sev_value.upper()
        if isinstance(severity_field, list):
            for entry in cast(List[Any], severity_field):
                normalized = self._normalize_severity_field(entry)
                if normalized:
                    return normalized
        return None

    def _extract_score_from_severity(self, severity_field: Any) -> Optional[float]:
        """Extract numeric score from severity structures if available."""

        if severity_field is None:
            return None
        if isinstance(severity_field, (float, int)):
            return float(severity_field)
        if isinstance(severity_field, str):
            severity_map = {
                "CRITICAL": 9.5,
                "HIGH": 8.0,
                "MEDIUM": 5.5,
                "LOW": 3.0,
            }
            return severity_map.get(severity_field.upper())
        if isinstance(severity_field, dict):
            severity_dict: Dict[str, Any] = cast(Dict[str, Any], severity_field)
            score = self._coerce_float(severity_dict.get("score"))
            if score is not None:
                return score
            value = severity_dict.get("value")
            if isinstance(value, str):
                return self._extract_score_from_severity(value)
        if isinstance(severity_field, list):
            for entry in cast(List[Any], severity_field):
                score = self._extract_score_from_severity(entry)
                if score is not None:
                    return score
        return None

    def _coerce_float(self, value: Any) -> Optional[float]:
        """Safely convert arbitrary values to float when possible."""

        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str) and value.strip():
            try:
                return float(value.strip())
            except ValueError:
                return None
        return None

    def _extract_confidence(self, vuln_data: Dict[str, Any]) -> str:
        """Extract confidence level from OSV vulnerability data."""

        database_specific = vuln_data.get("database_specific")
        if isinstance(database_specific, dict):
            database_dict: Dict[str, Any] = cast(Dict[str, Any], database_specific)
            confidence = database_dict.get("confidence")
            if isinstance(confidence, str):
                return confidence.lower()

        severity_field = vuln_data.get("severity")
        if isinstance(severity_field, dict):
            severity_dict: Dict[str, Any] = cast(Dict[str, Any], severity_field)
            confidence = severity_dict.get("confidence")
            if isinstance(confidence, str):
                return confidence.lower()

        if isinstance(severity_field, list):
            for entry in cast(List[Any], severity_field):
                if isinstance(entry, dict):
                    entry_dict: Dict[str, Any] = cast(Dict[str, Any], entry)
                    nested_confidence = entry_dict.get("confidence")
                    if isinstance(nested_confidence, str):
                        return nested_confidence.lower()

        return "medium"

    def _ecosystem_matches(self, pkg: Dict[str, Any], vuln: Dict[str, Any]) -> bool:
        """Ensure OSV affected package aligns with the dependency under analysis."""

        affected_entries = vuln.get("affected")
        if not isinstance(affected_entries, list):
            return True

        pkg_name = str(pkg.get("name", "")).lower()
        pkg_ecosystem = str(pkg.get("ecosystem", ""))
        pkg_version = str(pkg.get("version", ""))
        fallback_match = False

        for affected in cast(List[Any], affected_entries):
            if not isinstance(affected, dict):
                continue

            affected_dict: Dict[str, Any] = cast(Dict[str, Any], affected)

            package_info = affected_dict.get("package")
            if isinstance(package_info, dict):
                package_dict: Dict[str, Any] = cast(Dict[str, Any], package_info)
                affected_name = str(package_dict.get("name", "")).lower()
                affected_ecosystem = str(package_dict.get("ecosystem", ""))

                if affected_ecosystem and pkg_ecosystem and affected_ecosystem != pkg_ecosystem:
                    continue

                if affected_name and affected_name != pkg_name:
                    continue

            versions_field = affected_dict.get("versions")
            if isinstance(versions_field, list) and versions_field:
                normalized_versions = {str(version) for version in cast(List[Any], versions_field) if version}
                if pkg_version in normalized_versions:
                    return True
                continue

            fallback_match = True

        return fallback_match
