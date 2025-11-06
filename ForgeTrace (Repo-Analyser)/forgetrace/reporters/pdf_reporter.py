"""PDF Reporter - Author: Peter"""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple, cast

from jinja2 import Environment


class PDFReporter:
    """Generate an executive-style PDF with business and IP insights."""

    TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>ForgeTrace Executive Summary</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; color: #1a1a1a; }
        .cover { text-align: center; padding: 80px 20px 40px 20px; border-bottom: 4px solid #1b75bc; }
        .cover h1 { font-size: 42px; margin-bottom: 10px; color: #0d3b66; }
        .cover h2 { font-size: 18px; margin-top: 10px; color: #4a4a4a; }
        .meta { margin-top: 30px; font-size: 14px; color: #555555; }
        h2 { border-bottom: 2px solid #1b75bc; padding-bottom: 6px; margin-top: 45px; color: #0d3b66; }
        h3 { color: #1b75bc; margin-top: 25px; }
        .summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 18px; }
        .summary-card { background: #f5f9fc; border: 1px solid #d5e4f3; border-radius: 6px; padding: 16px; }
        .summary-card strong { display: block; font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px; color: #1b75bc; }
        .summary-card span { font-size: 24px; font-weight: 600; display: block; margin-top: 12px; color: #0d3b66; }
        table { width: 100%; border-collapse: collapse; margin-top: 16px; }
        th, td { border: 1px solid #e1e7ef; padding: 10px; text-align: left; font-size: 13px; }
        th { background: #f1f5fb; color: #0d3559; text-transform: uppercase; letter-spacing: 0.4px; }
        .note { font-size: 12px; color: #666666; margin-top: 12px; }
        .callout { background: #fff8e5; border-left: 4px solid #ffb347; padding: 14px; margin-top: 16px; font-size: 13px; }
        .two-column { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 22px; }
        .list-block { background: #f7f9fc; border: 1px solid #dde6f3; border-radius: 6px; padding: 18px; }
        .list-block h4 { margin-top: 0; color: #0d3b66; }
        .list-block ul { padding-left: 18px; margin: 0; }
        .badge-pill { display: inline-block; padding: 4px 10px; border-radius: 999px; font-size: 11px; background: #e8f1ff; color: #0d3b66; margin-right: 6px; }
        .badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; text-transform: uppercase; }
        .badge-critical { background: #f8d7da; color: #721c24; }
        .badge-high { background: #fbe7c6; color: #8c4a03; }
        .badge-medium { background: #fef3bd; color: #856404; }
        .badge-low { background: #d4edda; color: #155724; }
        .heatmap { width: 100%; border-collapse: collapse; margin-top: 16px; }
        .heatmap th, .heatmap td { border: 1px solid #dee4ef; padding: 8px; text-align: center; font-size: 12px; }
        .heatmap td.high { background: #f8d7da; color: #721c24; }
        .heatmap td.medium { background: #fef3bd; color: #856404; }
        .heatmap td.low { background: #d4edda; color: #155724; }
        ol, ul { margin-left: 20px; }
        footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid #dddddd; font-size: 11px; color: #777777; }
    </style>
</head>
<body>
    <div class="cover">
        <h1>ForgeTrace Executive Summary</h1>
        <h2>{{ client.client_name }}</h2>
        <div class="meta">
            <p><strong>Engagement Window:</strong> {{ client.engagement_window }}</p>
            <p><strong>Generated:</strong> {{ client.generated_on }}</p>
            <p><strong>Prepared By:</strong> {{ client.prepared_by }}</p>
        </div>
    </div>

    <h2>1. Executive Overview</h2>
    <div class="summary-grid">
        <div class="summary-card"><strong>Total LOC Inventoried</strong><span>{{ summary.total_loc }}</span></div>
        <div class="summary-card"><strong>Foreground LOC</strong><span>{{ summary.foreground_loc }}</span></div>
        <div class="summary-card"><strong>Estimated Rewrite Cost (USD)</strong><span>{{ summary.estimated_cost }}</span></div>
        <div class="summary-card"><strong>Estimated Schedule (Days)</strong><span>{{ summary.estimated_days }}</span></div>
        <div class="summary-card"><strong>Third-Party Components</strong><span>{{ summary.third_party_components }}</span></div>
        <div class="summary-card"><strong>Open Findings (Security/IP)</strong><span>{{ summary.open_findings }}</span></div>
        <div class="summary-card"><strong>High-Risk Licenses</strong><span>{{ summary.high_risk_licenses }}</span></div>
        <div class="summary-card"><strong>Clean-Room Candidates</strong><span>{{ summary.clean_room_candidates }}</span></div>
    </div>
    <p class="note">Key Risks: {{ summary.key_risks }}</p>
    <div class="callout">Stakeholder Questions Covered: {{ summary.stakeholder_questions }}</div>

    <h2>2. Engagement Context & Scope</h2>
    <div class="two-column">
        <div class="list-block">
            <h4>Assessment Scope</h4>
            <ul>
                {% for item in engagement.scope %}
                <li>{{ item }}</li>
                {% endfor %}
            </ul>
        </div>
        <div class="list-block">
            <h4>Key Deliverables</h4>
            <ul>
                {% for item in engagement.deliverables %}
                <li>{{ item }}</li>
                {% endfor %}
            </ul>
        </div>
    </div>
    <div class="callout">Methodology Summary: {{ engagement.methodology_summary }}</div>

    <h2>3. IP Inventory and Provenance</h2>
    <h3>Origin Breakdown</h3>
    <table>
        <thead><tr><th>Origin</th><th>Files</th><th>Share</th></tr></thead>
        <tbody>
            {% for row in ip.origin_breakdown %}
            <tr><td>{{ row.origin }}</td><td>{{ row.count }}</td><td>{{ row.share }}</td></tr>
            {% endfor %}
        </tbody>
    </table>
    <h3>IP Contribution Highlights</h3>
    <table>
        <thead><tr><th>Module</th><th>Origin</th><th>Primary Author</th><th>License</th><th>Rewriteable</th><th>Score</th><th>LOC</th></tr></thead>
        <tbody>
            {% for row in ip.contribution_table %}
            <tr>
                <td>{{ row.module }}</td>
                <td>{{ row.origin }}</td>
                <td>{{ row.primary_author }}</td>
                <td>{{ row.license }}</td>
                <td>{{ row.rewriteable }}</td>
                <td>{{ row.score }}</td>
                <td>{{ row.loc }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    <div class="callout">Provenance Insights: {{ ip.provenance_notes }}</div>

    <h2>4. Dependency & License Compliance</h2>
    <h3>Dependency Inventory</h3>
    <table>
        <thead><tr><th>Name</th><th>Version</th><th>Type</th><th>Source</th></tr></thead>
        <tbody>
            {% for dep in compliance.dependencies %}
            <tr><td>{{ dep.name }}</td><td>{{ dep.version }}</td><td>{{ dep.type }}</td><td>{{ dep.file }}</td></tr>
            {% endfor %}
        </tbody>
    </table>
    <p class="note">Total dependencies detected: {{ compliance.total_dependencies }} across {{ compliance.unique_files }} manifests.</p>
    <div class="two-column">
        <div class="list-block">
            <h4>Top Packages by Surface Area</h4>
            <ul>
                {% for pkg in compliance.top_packages %}
                <li>{{ pkg }}</li>
                {% endfor %}
            </ul>
        </div>
        <div class="list-block">
            <h4>Dependency Observations</h4>
            <ul>
                {% for obs in compliance.observations %}
                <li>{{ obs }}</li>
                {% endfor %}
            </ul>
        </div>
    </div>

    <h3>License Posture</h3>
    <table>
        <thead><tr><th>License</th><th>Occurrences</th><th>Files</th></tr></thead>
        <tbody>
            {% for lic in compliance.license_summary %}
            <tr><td>{{ lic.license }}</td><td>{{ lic.count }}</td><td>{{ lic.files }}</td></tr>
            {% endfor %}
        </tbody>
    </table>
    <div class="two-column">
        <div class="list-block">
            <h4>License Obligations</h4>
            <ul>
                {% for obligation in compliance.obligations %}
                <li>{{ obligation }}</li>
                {% endfor %}
            </ul>
        </div>
        <div class="list-block">
            <h4>Recommended Counsel Actions</h4>
            <ul>
                {% for action in compliance.counsel_actions %}
                <li>{{ action }}</li>
                {% endfor %}
            </ul>
        </div>
    </div>

    <h2>5. Authorship & Development Activity</h2>
    <h3>Top Contributors</h3>
    <table>
        <thead><tr><th>Author</th><th>Commits</th><th>Lines Added</th><th>Lines Removed</th><th>Files Touched</th></tr></thead>
        <tbody>
            {% for author in provenance.top_authors %}
            <tr>
                <td>{{ author.name }}</td>
                <td>{{ author.commits }}</td>
                <td>{{ author.added }}</td>
                <td>{{ author.removed }}</td>
                <td>{{ author.files }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    <p class="note">Commit window: {{ provenance.commit_window }}</p>
    <div class="two-column">
        <div class="list-block">
            <h4>Authorship Insights</h4>
            <ul>
                {% for insight in provenance.insights %}
                <li>{{ insight }}</li>
                {% endfor %}
            </ul>
        </div>
        <div class="list-block">
            <h4>Historical Milestones</h4>
            <ul>
                {% for milestone in provenance.milestones %}
                <li>{{ milestone }}</li>
                {% endfor %}
            </ul>
        </div>
    </div>

    <h2>6. Rewriteability & Clean Room Planning</h2>
    <div class="summary-grid">
        <div class="summary-card"><strong>Average Rewrite Score</strong><span>{{ rewriteability.avg_score }}</span></div>
        <div class="summary-card"><strong>High-Risk Modules</strong><span>{{ rewriteability.low_rewriteable_count }}</span></div>
        <div class="summary-card"><strong>Candidate Modules (Score ≥ 0.75)</strong><span>{{ rewriteability.high_rewriteable_count }}</span></div>
    </div>
    <h3>Clean Room Recommendations</h3>
    <ul>
        {% for rec in rewriteability.recommendations %}
        <li>{{ rec }}</li>
        {% endfor %}
    </ul>
    <div class="two-column">
        <div class="list-block">
            <h4>Priority Modules to Shield</h4>
            <ul>
                {% for module in rewriteability.priority_modules %}
                <li>{{ module }}</li>
                {% endfor %}
            </ul>
        </div>
        <div class="list-block">
            <h4>Clean-Room Playbook Tasks</h4>
            <ul>
                {% for task in rewriteability.playbook %}
                <li>{{ task }}</li>
                {% endfor %}
            </ul>
        </div>
    </div>

    <h2>7. Security, Similarity & Risk Heat Map</h2>
    <table class="heatmap">
        <thead><tr><th></th><th>High</th><th>Medium</th><th>Low</th></tr></thead>
        <tbody>
            <tr><th>Security</th><td class="{{ risks.heatmap.security_high }}">{{ risks.heatmap_counts.security.high }}</td><td class="{{ risks.heatmap.security_med }}">{{ risks.heatmap_counts.security.med }}</td><td class="{{ risks.heatmap.security_low }}">{{ risks.heatmap_counts.security.low }}</td></tr>
            <tr><th>IP / License</th><td class="{{ risks.heatmap.ip_high }}">{{ risks.heatmap_counts.ip.high }}</td><td class="{{ risks.heatmap.ip_med }}">{{ risks.heatmap_counts.ip.med }}</td><td class="{{ risks.heatmap.ip_low }}">{{ risks.heatmap_counts.ip.low }}</td></tr>
            <tr><th>Operational</th><td class="{{ risks.heatmap.ops_high }}">{{ risks.heatmap_counts.ops.high }}</td><td class="{{ risks.heatmap.ops_med }}">{{ risks.heatmap_counts.ops.med }}</td><td class="{{ risks.heatmap.ops_low }}">{{ risks.heatmap_counts.ops.low }}</td></tr>
        </tbody>
    </table>
    <table>
        <thead><tr><th>Area</th><th>Count</th><th>Severity</th><th>Notes</th></tr></thead>
        <tbody>
            {% for risk in risks.overview %}
            <tr>
                <td>{{ risk.area }}</td>
                <td>{{ risk.count }}</td>
                <td><span class="badge {{ risk.badge }}">{{ risk.severity }}</span></td>
                <td>{{ risk.notes }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    <div class="two-column">
        <div class="list-block">
            <h4>Security Focus</h4>
            <ul>
                {% for item in risks.security_focus %}
                <li>{{ item }}</li>
                {% endfor %}
            </ul>
        </div>
        <div class="list-block">
            <h4>Similarity Focus</h4>
            <ul>
                {% for item in risks.similarity_focus %}
                <li>{{ item }}</li>
                {% endfor %}
            </ul>
        </div>
    </div>
    <h3>Representative Similarity Pairs</h3>
    <table>
        <thead><tr><th>File A</th><th>File B</th><th>Similarity</th></tr></thead>
        <tbody>
            {% for dup in risks.duplicates %}
            <tr><td>{{ dup.file1 }}</td><td>{{ dup.file2 }}</td><td>{{ dup.similarity }}</td></tr>
            {% endfor %}
        </tbody>
    </table>

    <h2>8. Strategic Next Steps</h2>
    <ol>
        {% for action in next_steps %}
        <li>{{ action }}</li>
        {% endfor %}
    </ol>

    <h2>9. Appendix</h2>
    <div class="two-column">
        <div class="list-block">
            <h4>Tooling Footprint</h4>
            <ul>
                {% for tool in appendix.tooling %}
                <li>{{ tool }}</li>
                {% endfor %}
            </ul>
        </div>
        <div class="list-block">
            <h4>Data Coverage</h4>
            <ul>
                {% for item in appendix.coverage %}
                <li>{{ item }}</li>
                {% endfor %}
            </ul>
        </div>
    </div>
    <div class="list-block">
        <h4>Open Questions for Stakeholders</h4>
        <ul>
            {% for question in appendix.questions %}
            <li>{{ question }}</li>
            {% endfor %}
        </ul>
    </div>

    <footer>
        <p>Prepared for {{ client.client_name }} by BAMG Studio LLC &copy; {{ client.year }}. ForgeTrace (Repo-Analyser) v0.1.0.</p>
        <p>Confidential – Not legal advice. Engage qualified counsel for final determinations.</p>
    </footer>
</body>
</html>
"""

    def __init__(self, findings: Dict[str, Any], output_dir: Path | str, config: Dict[str, Any] | None):
        self.findings = findings
        self.output_dir = Path(output_dir)
        self.config = config or {}

    def generate(self) -> None:
        context = self._build_context()
        html_file = self.output_dir / "executive_summary.html"
        pdf_file = self.output_dir / "executive_summary.pdf"

        env = Environment()
        template = env.from_string(self.TEMPLATE)
        rendered = template.render(**context)
        html_file.write_text(rendered, encoding="utf-8")

        try:
            from weasyprint import HTML  # type: ignore[import-not-found]

            HTML(string=rendered, base_url=str(html_file.parent)).write_pdf(str(pdf_file))  # type: ignore[attr-defined]
        except ImportError:
            print("WeasyPrint not available. Skipping PDF generation.")
        except Exception as exc:
            print(f"PDF generation failed: {exc}")

    def _build_context(self) -> Dict[str, Any]:
        output_cfg = cast(Dict[str, Any], self.config.get("output", {}) or {})
        cost = cast(Dict[str, Any], self.findings.get("cost_estimate", {}) or {})
        classifications = cast(Dict[str, Dict[str, Any]], self.findings.get("classification", {}) or {})
        rewriteability = cast(Dict[str, Dict[str, Any]], self.findings.get("rewriteability", {}) or {})
        sbom = cast(Dict[str, Any], self.findings.get("sbom", {}) or {})
        licenses = cast(Dict[str, Any], self.findings.get("licenses", {}) or {})
        git_info = cast(Dict[str, Any], self.findings.get("git", {}) or {})
        secrets = cast(Dict[str, Any], self.findings.get("secrets", {}) or {})
        sast = cast(Dict[str, Any], self.findings.get("sast", {}) or {})
        similarity = cast(Dict[str, Any], self.findings.get("similarity", {}) or {})

        dependency_list = self._extract_dependencies(sbom)
        license_summary = self._summarize_licenses(licenses)
        compliance_obligations = self._build_compliance_obligations(license_summary)
        top_packages = self._identify_top_packages(dependency_list["items"])
        dependency_observations = self._build_dependency_observations(dependency_list, compliance_obligations)
        origin_breakdown = self._summarize_origins(classifications)
        contribution_table = self._build_contribution_table(classifications, rewriteability)
        top_authors, commit_window = self._summarize_authors(git_info)
        provenance_insights = self._build_provenance_insights(git_info, classifications, top_authors)
        rewrite_stats = self._summarize_rewriteability(rewriteability, classifications)

        secrets_count = self._count_findings(secrets)
        sast_count = self._count_findings(sast)
        duplicate_pairs = cast(List[Dict[str, Any]], similarity.get("duplicates", []) or [])
        risk_overview, duplicate_highlights, key_risks = self._build_risk_matrix(secrets_count, sast_count, duplicate_pairs)
        total_license_findings = sum(int(entry.get("count", 0)) for entry in license_summary)
        risk_heatmap, risk_heat_counts = self._build_risk_heatmap(
            secrets_count,
            sast_count,
            compliance_obligations["high_risk_count"],
            total_license_findings,
            duplicate_pairs,
        )
        security_focus = self._build_security_focus(secrets_count, sast_count)
        similarity_focus = self._build_similarity_focus(duplicate_pairs)
        stakeholder_questions = self._build_stakeholder_questions(risk_overview, compliance_obligations, rewrite_stats)
        engagement = self._build_engagement_section(output_cfg, stakeholder_questions)
        appendix = self._build_appendix_section(dependency_list, risk_overview, stakeholder_questions)
        next_steps = self._build_next_steps(risk_overview, rewrite_stats, compliance_obligations)

        total_loc = cost.get("total_loc", 0)
        foreground_loc = cost.get("foreground_loc", 0)
        estimated_cost = cost.get("estimated_cost_usd", 0)
        estimated_days = cost.get("estimated_days", 0)

        now_utc = datetime.now(timezone.utc)

        # Get metadata from config (prefer metadata section, fallback to output section)
        metadata = self.config.get("metadata", {})
        
        context: Dict[str, Any] = {
            "client": {
                "client_name": metadata.get("client_name") or output_cfg.get("client_name") or "ForgeTrace Client",
                "engagement_window": metadata.get("engagement_window") or self._format_engagement_window(output_cfg),
                "generated_on": now_utc.strftime("%Y-%m-%d %H:%M UTC"),
                "prepared_by": metadata.get("prepared_by") or "Peter Kolawole, BAMG Studio LLC",
                "contact_email": metadata.get("contact_email", ""),
                "year": now_utc.year,
            },
            "summary": {
                "total_loc": f"{int(total_loc):,}" if total_loc else "0",
                "foreground_loc": f"{int(foreground_loc):,}" if foreground_loc else "0",
                "estimated_cost": f"${estimated_cost:,.2f}" if estimated_cost else "$0.00",
                "estimated_days": f"{estimated_days}" if estimated_days else "0",
                "third_party_components": f"{dependency_list['third_party_count']:,}",
                "open_findings": f"{risk_overview['total_findings']:,}",
                "key_risks": key_risks,
                "high_risk_licenses": f"{compliance_obligations['high_risk_count']:,}",
                "clean_room_candidates": f"{rewrite_stats.get('high_rewriteable_count', 0)}",
                "stakeholder_questions": "; ".join(stakeholder_questions) or "Risk, provenance, and remediation readiness",
            },
            "engagement": engagement,
            "ip": {
                "origin_breakdown": origin_breakdown,
                "contribution_table": contribution_table,
                "provenance_notes": provenance_insights["notes"],
            },
            "compliance": {
                "dependencies": dependency_list["items"],
                "total_dependencies": dependency_list["total"],
                "unique_files": dependency_list["manifests"],
                "license_summary": license_summary,
                "top_packages": top_packages,
                "observations": dependency_observations,
                "obligations": compliance_obligations["obligations"],
                "counsel_actions": compliance_obligations["counsel_actions"],
            },
            "provenance": {
                "top_authors": top_authors,
                "commit_window": commit_window,
                "insights": provenance_insights["insights"],
                "milestones": provenance_insights["milestones"],
            },
            "rewriteability": rewrite_stats,
            "risks": {
                "overview": risk_overview["items"],
                "duplicates": duplicate_highlights,
                "heatmap": risk_heatmap,
                "heatmap_counts": risk_heat_counts,
                "security_focus": security_focus,
                "similarity_focus": similarity_focus,
            },
            "appendix": appendix,
            "next_steps": next_steps,
        }
        return context

    def _format_engagement_window(self, output_cfg: Dict[str, Any]) -> str:
        start = output_cfg.get("engagement_start")
        end = output_cfg.get("engagement_end")
        if start and end:
            return f"{start} to {end}"
        if start:
            return f"Since {start}"
        if end:
            return f"Through {end}"
        return "Not Specified"

    def _extract_dependencies(self, sbom: Dict[str, Any]) -> Dict[str, Any]:
        packages_raw_list = cast(List[Any], sbom.get("packages") or sbom.get("dependencies") or [])
        packages: List[Dict[str, Any]] = []
        items: List[Dict[str, str]] = []
        manifests: set[str] = set()

        for pkg_candidate in packages_raw_list:
            if isinstance(pkg_candidate, dict):
                pkg = cast(Dict[str, Any], pkg_candidate)
            else:
                continue

            name = pkg.get("name") or pkg.get("package") or "unknown"
            version = pkg.get("version") or pkg.get("qualifier") or ""
            pkg_type = pkg.get("type") or pkg.get("purl", "").split(":")[0] or "unknown"
            source_file = pkg.get("file") or pkg.get("manifestFile") or ""

            packages.append(pkg)

            if source_file:
                manifests.add(str(source_file))
            items.append({
                "name": str(name),
                "version": str(version),
                "type": str(pkg_type),
                "file": str(source_file),
            })

        items = sorted(items, key=lambda x: x.get("name", ""))[:50]
        return {
            "items": items,
            "total": len(packages),
            "manifests": len(manifests),
            "third_party_count": len(packages),
        }

    def _summarize_licenses(self, licenses: Dict[str, Any]) -> List[Dict[str, Any]]:
        findings_raw = cast(List[Any], licenses.get("findings") or [])
        findings: List[Dict[str, Any]] = [cast(Dict[str, Any], entry) for entry in findings_raw if isinstance(entry, dict)]
        counter: Counter[str] = Counter()
        files_by_license: Dict[str, set[str]] = {}
        for entry in findings:
            lic = str(entry.get("license") or "Unknown")
            counter[lic] += 1
            files_by_license.setdefault(lic, set()).add(str(entry.get("file", "")))

        summary: List[Dict[str, Any]] = []
        for license_name, count in counter.most_common(10):
            files = ", ".join(sorted(f for f in files_by_license.get(license_name, set()) if f))
            summary.append({
                "license": license_name,
                "count": int(count),
                "files": files[:200] + ("..." if files and len(files) > 200 else ""),
            })

        if not summary:
            summary.append({"license": "None Detected", "count": 0, "files": ""})
        return summary

    def _summarize_origins(self, classifications: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        total = max(len(classifications), 1)
        counter: Counter[str] = Counter(str(data.get("origin", "unknown")) for data in classifications.values())
        breakdown: List[Dict[str, Any]] = []
        for origin, count in counter.most_common():
            share = f"{(count / total) * 100:.1f}%"
            breakdown.append({"origin": origin, "count": int(count), "share": share})
        if not breakdown:
            breakdown.append({"origin": "unknown", "count": 0, "share": "0.0%"})
        return breakdown

    def _build_contribution_table(
        self,
        classifications: Dict[str, Dict[str, Any]],
        rewriteability: Dict[str, Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        for filepath, data in classifications.items():
            rewrite = rewriteability.get(filepath, {})
            score_value = float(rewrite.get("score", 0) or 0)
            module_name = Path(filepath).name or filepath
            rows.append({
                "module": module_name,
                "origin": data.get("origin", "unknown"),
                "primary_author": data.get("primary_author", "unknown"),
                "license": data.get("license", "none"),
                "rewriteable": "Yes" if rewrite.get("rewriteable") else "No",
                "score": f"{score_value:.2f}",
                "score_value": score_value,
                "loc": int(rewrite.get("loc", 0) or 0),
            })

        rows.sort(key=lambda item: item.get("score_value", 0))
        return rows[:40] or [{
            "module": "No modules analysed",
            "origin": "-",
            "primary_author": "-",
            "license": "-",
            "rewriteable": "-",
            "score": "0.00",
            "score_value": 0.0,
            "loc": 0,
        }]

    def _summarize_authors(self, git_info: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], str]:
        authors = cast(Dict[str, Any], git_info.get("authors", {}) or {})
        churn = cast(Dict[str, Any], git_info.get("churn", {}) or {})
        timeline = cast(List[Dict[str, Any]], git_info.get("timeline", []) or [])

        rows: List[Dict[str, Any]] = []
        for name, metrics in authors.items():
            churn_metrics = cast(Dict[str, Any], churn.get(name, {}) or {})
            rows.append({
                "name": name,
                "commits": int(metrics.get("commits", 0) or 0),
                "added": int(churn_metrics.get("added", 0) or 0),
                "removed": int(churn_metrics.get("removed", 0) or 0),
                "files": int(churn_metrics.get("files", 0) or 0),
            })

        rows.sort(key=lambda item: item.get("commits", 0), reverse=True)
        if not rows:
            rows = [{"name": "Unknown", "commits": 0, "added": 0, "removed": 0, "files": 0}]
        else:
            rows = rows[:10]

        if timeline:
            dates = sorted(str(entry.get("date")) for entry in timeline if entry.get("date"))
            if len(dates) >= 2:
                commit_window = f"{dates[0][:10]} to {dates[-1][:10]}"
            elif dates:
                commit_window = dates[0][:10]
            else:
                commit_window = "No commit history detected"
        else:
            commit_window = "No commit history detected"

        return rows, commit_window

    def _summarize_rewriteability(
        self,
        rewriteability: Dict[str, Dict[str, Any]],
        classifications: Dict[str, Dict[str, Any]],
    ) -> Dict[str, Any]:
        scores = [float(data.get("score", 0) or 0) for data in rewriteability.values()]
        avg_score = sum(scores) / len(scores) if scores else 0.0
        low_rewriteable = [path for path, meta in rewriteability.items() if float(meta.get("score", 0) or 0) < 0.4 and str(classifications.get(path, {}).get("origin", "")).lower() == "foreground"]
        high_rewriteable = [path for path, meta in rewriteability.items() if float(meta.get("score", 0) or 0) >= 0.75 and str(classifications.get(path, {}).get("origin", "")).lower() == "foreground"]

        recommendations: List[str] = []
        if low_rewriteable:
            recommendations.append("Prioritize ring-fencing low-score foreground modules before disclosure to counterparties.")
        if high_rewriteable:
            recommendations.append("Prepare clean-room briefs for high-score modules to accelerate potential rewrites with contractors.")
        if not recommendations:
            recommendations.append("No critical rewrite blockers detected; maintain periodic reassessment alongside refactors.")

        priority_modules = [Path(path).name or path for path in low_rewriteable[:5]]
        if not priority_modules:
            priority_modules = ["No critical modules identified."]

        playbook = [
            "Document clean-room brief per high priority module.",
            "Assign independent implementers for guarded rewrites.",
            "Track escrow-ready deliverables with counsel oversight.",
        ]
        if len(high_rewriteable) >= 5:
            playbook.append("Sequence rewrites in sprints to capture high-score efficiencies.")

        return {
            "avg_score": f"{avg_score:.2f}",
            "low_rewriteable_count": len(low_rewriteable),
            "high_rewriteable_count": len(high_rewriteable),
            "recommendations": recommendations,
            "priority_modules": priority_modules,
            "playbook": playbook,
        }

    def _build_risk_matrix(
        self,
        secrets_count: int,
        sast_count: int,
        duplicate_pairs: List[Dict[str, Any]],
    ) -> Tuple[Dict[str, Any], List[Dict[str, str]], str]:
        overview: List[Dict[str, Any]] = []
        total_findings = 0

        if secrets_count:
            overview.append({
                "area": "Secrets",
                "count": secrets_count,
                "severity": "Critical" if secrets_count > 0 else "None",
                "badge": "badge-critical" if secrets_count else "badge-low",
                "notes": "Escalate immediate redaction and key rotation.",
            })
            total_findings += secrets_count
        else:
            overview.append({
                "area": "Secrets",
                "count": 0,
                "severity": "None",
                "badge": "badge-low",
                "notes": "No hardcoded secrets detected.",
            })

        if sast_count:
            severity = "High" if sast_count > 5 else "Medium"
            badge = "badge-high" if sast_count > 5 else "badge-medium"
            overview.append({
                "area": "SAST",
                "count": sast_count,
                "severity": severity,
                "badge": badge,
                "notes": "Review flagged rules and triage exploitable paths.",
            })
            total_findings += sast_count
        else:
            overview.append({
                "area": "SAST",
                "count": 0,
                "severity": "None",
                "badge": "badge-low",
                "notes": "Static analysis returned no actionable findings.",
            })

        dup_count = len(duplicate_pairs)
        if dup_count:
            severity = "Medium" if dup_count < 10 else "High"
            badge = "badge-medium" if dup_count < 10 else "badge-high"
            overview.append({
                "area": "Similarity",
                "count": dup_count,
                "severity": severity,
                "badge": badge,
                "notes": "Assess overlapping code for prior art or third-party contamination.",
            })
            total_findings += dup_count
        else:
            overview.append({
                "area": "Similarity",
                "count": 0,
                "severity": "Low",
                "badge": "badge-low",
                "notes": "No significant code duplication detected beyond thresholds.",
            })

        duplicates = [{
            "file1": Path(str(pair.get("file1", ""))).name,
            "file2": Path(str(pair.get("file2", ""))).name,
            "similarity": f"{float(pair.get('similarity', 0) or 0):.2f}",
        } for pair in duplicate_pairs[:10]]

        if not duplicates:
            duplicates = [{"file1": "-", "file2": "-", "similarity": "0.00"}]

        key_risks: List[str] = []
        if secrets_count:
            key_risks.append("Secrets exposure")
        if sast_count:
            key_risks.append("Untriaged static analysis findings")
        if dup_count:
            key_risks.append("Potential provenance conflicts")
        key_risks_str = ", ".join(key_risks) if key_risks else "No material risks flagged in this pass"

        return {"items": overview, "total_findings": total_findings}, duplicates, key_risks_str

    def _build_next_steps(
        self,
        risk_overview: Dict[str, Any],
        rewrite_stats: Dict[str, Any],
        compliance_obligations: Dict[str, Any],
    ) -> List[str]:
        actions: List[str] = []
        secrets_exposure = next((int(item.get("count", 0)) for item in risk_overview.get("items", []) if item.get("area") == "Secrets"), 0)
        sast_findings = next((int(item.get("count", 0)) for item in risk_overview.get("items", []) if item.get("area") == "SAST"), 0)

        if secrets_exposure:
            actions.append("Trigger credential rotation playbook and scrub committed secrets from history.")
        if sast_findings:
            actions.append("Schedule engineering triage for SAST findings with accountable owners.")
        if int(compliance_obligations.get("high_risk_count", 0)) > 0:
            actions.append("Engage counsel to validate reciprocal license obligations before external disclosure.")
        if int(rewrite_stats.get("low_rewriteable_count", 0)) > 0:
            actions.append("Draft clean-room specs and isolation plans for low-score foreground modules.")
        actions.append("Maintain continuous SBOM updates as dependencies evolve across sprints.")
        return actions[:6]

    def _count_findings(self, findings: Dict[str, Any]) -> int:
        count = findings.get("count")
        if isinstance(count, int):
            return count
        if isinstance(count, str) and count.isdigit():
            return int(count)
        records = findings.get("findings")
        if isinstance(records, list):
            return len(cast(List[Any], records))
        return 0

    def _build_compliance_obligations(self, license_summary: List[Dict[str, Any]]) -> Dict[str, Any]:
        high_risk_keywords = ("GPL", "AGPL", "LGPL", "AFFERO", "RECIPROCAL", "COPYLEFT")
        high_risk_count = 0
        for entry in license_summary:
            license_name = str(entry.get("license", "")).upper()
            if any(keyword in license_name for keyword in high_risk_keywords):
                high_risk_count += int(entry.get("count", 0) or 0)

        obligations: List[str] = [
            "Ensure SPDX attributions accompany third-party packages in outbound deliverables.",
            "Track dependency provenance in data rooms alongside SBOM exports.",
        ]
        counsel_actions: List[str] = [
            "Review updated SBOM with legal counsel before diligence disclosures.",
        ]

        if high_risk_count:
            obligations.insert(0, f"Review {high_risk_count} GPL-family component obligation{'s' if high_risk_count != 1 else ''} for distribution compatibility.")
            counsel_actions.insert(0, "Engage counsel to confirm reciprocal terms and draft mitigation language.")
        else:
            obligations.append("Confirm permissive-license notices remain within corporate policy thresholds.")

        return {
            "high_risk_count": high_risk_count,
            "obligations": obligations[:6],
            "counsel_actions": counsel_actions[:6],
        }

    def _identify_top_packages(self, dependencies: List[Dict[str, str]]) -> List[str]:
        if not dependencies:
            return ["No package manifests detected."]
        counter: Counter[str] = Counter(dep.get("name", "unknown") for dep in dependencies if dep.get("name"))
        top_entries = [f"{name} ({count} reference{'s' if count != 1 else ''})" for name, count in counter.most_common(5)]
        return top_entries or ["No named dependencies available."]

    def _build_dependency_observations(
        self,
        dependency_list: Dict[str, Any],
        compliance_obligations: Dict[str, Any],
    ) -> List[str]:
        observations: List[str] = []
        total = int(dependency_list.get("total", 0) or 0)
        manifests = int(dependency_list.get("manifests", 0) or 0)
        observations.append(
            f"Detected {total} package entr{'ies' if total != 1 else 'y'} across {manifests} manifest{'s' if manifests != 1 else ''}."
        )
        if int(compliance_obligations.get("high_risk_count", 0)) > 0:
            observations.append("GPL-family packages present; confirm isolation before release.")

        items = cast(List[Dict[str, str]], dependency_list.get("items", []))
        if items:
            ecosystem_counts: Counter[str] = Counter(dep.get("type", "unknown") for dep in items if dep.get("type"))
            if ecosystem_counts:
                ecosystem, count = ecosystem_counts.most_common(1)[0]
                observations.append(
                    f"{ecosystem} ecosystem represents {count} component{'s' if count != 1 else ''} in scope."
                )
        else:
            observations.append("SBOM scanner did not detect dependency manifests in supplied snapshot.")

        return observations[:4]

    def _build_provenance_insights(
        self,
        git_info: Dict[str, Any],
        classifications: Dict[str, Dict[str, Any]],
        top_authors: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        primary_author = top_authors[0] if top_authors else None
        if primary_author and primary_author.get("commits"):
            notes = (
                f"{primary_author['name']} leads with {primary_author['commits']} commits across {primary_author['files']} files."
            )
        else:
            notes = "No dominant contributor identified in git history."

        foreground_count = sum(
            1 for meta in classifications.values() if str(meta.get("origin", "")).lower() == "foreground"
        )
        background_count = sum(
            1 for meta in classifications.values() if str(meta.get("origin", "")).lower() != "foreground"
        )
        total = foreground_count + background_count

        insights: List[str] = []
        if total:
            share = (foreground_count / total) * 100
            insights.append(f"Foreground assets represent {share:.1f}% of inventoried files.")
        if primary_author and primary_author.get("added") is not None:
            churn = int(primary_author.get("added", 0) or 0) - int(primary_author.get("removed", 0) or 0)
            if churn:
                insights.append(f"Net code delta for lead contributor: {churn:+,} lines.")

        timeline = cast(List[Dict[str, Any]], git_info.get("timeline", []) or [])
        milestones: List[str] = []
        if timeline:
            dated_entries = [entry for entry in timeline if entry.get("date")]
            dated_entries.sort(key=lambda entry: str(entry["date"]))
            if dated_entries:
                first = str(dated_entries[0]["date"])
                milestones.append(f"Initial commit observed {first[:10]}.")
                if len(dated_entries) > 1:
                    last = str(dated_entries[-1]["date"])
                    milestones.append(f"Most recent commit {last[:10]}.")

        if not insights:
            insights.append("Contributor distribution appears balanced across the repository.")
        if not milestones:
            milestones.append("No temporal git activity supplied; milestones unavailable.")

        return {
            "notes": notes,
            "insights": insights[:5],
            "milestones": milestones[:5],
        }

    def _build_risk_heatmap(
        self,
        secrets_count: int,
        sast_count: int,
        high_risk_license_count: int,
        total_license_findings: int,
        duplicate_pairs: List[Dict[str, Any]],
    ) -> Tuple[Dict[str, str], Dict[str, Dict[str, int]]]:
        high_similarity = sum(1 for pair in duplicate_pairs if float(pair.get("similarity", 0) or 0) >= 0.9)
        medium_similarity = sum(1 for pair in duplicate_pairs if 0.75 <= float(pair.get("similarity", 0) or 0) < 0.9)
        low_similarity = max(len(duplicate_pairs) - high_similarity - medium_similarity, 0)

        security_counts = {
            "high": secrets_count,
            "med": sast_count,
            "low": 0 if (secrets_count or sast_count) else 1,
        }
        ip_counts = {
            "high": high_risk_license_count,
            "med": max(total_license_findings - high_risk_license_count, 0),
            "low": 0 if total_license_findings else 1,
        }
        ops_counts = {
            "high": high_similarity,
            "med": medium_similarity,
            "low": low_similarity if low_similarity else (0 if duplicate_pairs else 1),
        }

        heatmap_counts = {
            "security": security_counts,
            "ip": ip_counts,
            "ops": ops_counts,
        }

        def css_class(value: int, level: str) -> str:
            return level if value else ""

        heatmap = {
            "security_high": css_class(security_counts["high"], "high"),
            "security_med": css_class(security_counts["med"], "medium"),
            "security_low": css_class(security_counts["low"], "low"),
            "ip_high": css_class(ip_counts["high"], "high"),
            "ip_med": css_class(ip_counts["med"], "medium"),
            "ip_low": css_class(ip_counts["low"], "low"),
            "ops_high": css_class(ops_counts["high"], "high"),
            "ops_med": css_class(ops_counts["med"], "medium"),
            "ops_low": css_class(ops_counts["low"], "low"),
        }

        return heatmap, heatmap_counts

    def _build_security_focus(self, secrets_count: int, sast_count: int) -> List[str]:
        focus: List[str] = []
        if secrets_count:
            focus.append(
                f"Secrets scanner flagged {secrets_count} exposure{'s' if secrets_count != 1 else ''}; rotate credentials and purge history."
            )
        else:
            focus.append("Secrets scanner found no embedded credentials in scope.")

        if sast_count:
            focus.append(
                f"Static analysis produced {sast_count} finding{'s' if sast_count != 1 else ''}; prioritize exploitable rules for triage."
            )
        else:
            focus.append("SAST baseline clean; maintain guardrails in CI pipelines.")

        return focus

    def _build_similarity_focus(self, duplicate_pairs: List[Dict[str, Any]]) -> List[str]:
        if not duplicate_pairs:
            return ["No similarity collisions crossed reporting threshold."]

        sorted_pairs = sorted(
            duplicate_pairs,
            key=lambda pair: float(pair.get("similarity", 0) or 0),
            reverse=True,
        )
        if not sorted_pairs:
            return ["Similarity data unavailable."]

        top_pair = sorted_pairs[0]
        score = float(top_pair.get("similarity", 0) or 0)
        percent = f"{(score * 100):.1f}%" if score <= 1 else f"{score:.1f}%"
        focus = [
            (
                f"Top match {Path(str(top_pair.get('file1', ''))).name} ↔ {Path(str(top_pair.get('file2', ''))).name} "
                f"({percent})."
            )
        ]
        if len(sorted_pairs) > 1:
            focus.append(
                f"{len(sorted_pairs)} code pair{'s' if len(sorted_pairs) != 1 else ''} exceeded similarity thresholds; evaluate provenance."
            )
        return focus[:3]

    def _build_stakeholder_questions(
        self,
        risk_overview: Dict[str, Any],
        compliance_obligations: Dict[str, Any],
        rewrite_stats: Dict[str, Any],
    ) -> List[str]:
        questions: List[str] = []
        secrets_count = next((int(item.get("count", 0)) for item in risk_overview.get("items", []) if item.get("area") == "Secrets"), 0)
        sast_count = next((int(item.get("count", 0)) for item in risk_overview.get("items", []) if item.get("area") == "SAST"), 0)

        if int(compliance_obligations.get("high_risk_count", 0)) > 0:
            questions.append("How do GPL-family components impact the target distribution model?")
        else:
            questions.append("Is attribution coverage sufficient for planned disclosures?")

        if secrets_count or sast_count:
            questions.append("What is the remediation timeline for outstanding security findings?")

        if int(rewrite_stats.get("low_rewriteable_count", 0)) > 0:
            questions.append("Which low-score modules require clean-room isolation before diligence?")

        questions.append("Do we have sign-off on SBOM accuracy for transaction disclosures?")
        return questions[:4]

    def _build_engagement_section(
        self,
        output_cfg: Dict[str, Any],
        stakeholder_questions: List[str],
    ) -> Dict[str, Any]:
        scope_cfg = self._coerce_to_list(output_cfg.get("executive_scope"))
        if not scope_cfg:
            scope_cfg = [
                "Source code, licenses, and dependency manifests supplied in audit bundle.",
                "Historical git metadata (authors, churn, timeline).",
                "ForgeTrace scanners across secrets, SAST, similarity, and licenses.",
            ]

        deliverables_cfg = self._coerce_to_list(output_cfg.get("executive_deliverables"))
        if not deliverables_cfg:
            deliverables_cfg = [
                "Executive summary narrative (PDF/HTML).",
                "Machine-readable SBOM extracts (JSON).",
                "Risk, license, and rewriteability analytics.",
            ]

        methodology_summary = str(
            output_cfg.get("methodology_summary")
            or "ForgeTrace executed automated scanners and manual analytics to surface provenance, license, and security risks."
        )

        return {
            "scope": scope_cfg[:6],
            "deliverables": deliverables_cfg[:6],
            "methodology_summary": methodology_summary,
            "stakeholder_questions": stakeholder_questions,
        }

    def _build_appendix_section(
        self,
        dependency_list: Dict[str, Any],
        risk_overview: Dict[str, Any],
        stakeholder_questions: List[str],
    ) -> Dict[str, Any]:
        tooling = [
            "ForgeTrace scanners: SBOM, license, secrets, SAST, similarity, git provenance.",
            "WeasyPrint-rendered executive PDF via Jinja2 templates.",
        ]

        total_dependencies = int(dependency_list.get("total", 0) or 0)
        manifests = int(dependency_list.get("manifests", 0) or 0)
        coverage: List[str] = []
        coverage.append(
            f"SBOM captured {total_dependencies} package entr{'ies' if total_dependencies != 1 else 'y'} across {manifests} manifest{'s' if manifests != 1 else ''}."
        )
        risk_total = sum(int(item.get("count", 0)) for item in risk_overview.get("items", []))
        coverage.append(
            f"Security scanners surfaced {risk_total} aggregate finding{'s' if risk_total != 1 else ''} across secrets, SAST, and similarity modules."
        )
        coverage.append("Git analytics derived from repository metadata supplied in audit bundle.")

        questions = stakeholder_questions or ["No outstanding stakeholder questions captured."]

        return {
            "tooling": tooling,
            "coverage": coverage[:6],
            "questions": questions[:6],
        }

    def _coerce_to_list(self, value: Any) -> List[str]:
        if isinstance(value, (list, tuple)):
            iterable = cast(Iterable[Any], value)
            result: List[str] = []
            for item in iterable:
                item_str = str(item).strip()
                if item_str:
                    result.append(item_str)
            return result
        if isinstance(value, str) and value.strip():
            return [value.strip()]
        return []
