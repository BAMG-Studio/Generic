"""Helpers for producing audience-tailored report narrative blocks."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, cast


def build_narrative(
    kpis: Dict[str, Any],
    risk: Dict[str, Any],
    rewrite: Dict[str, Any],
    compliance: Dict[str, Any],
    recommendation: Dict[str, str],
    vulnerabilities: Dict[str, Any],
) -> Dict[str, List[str]]:
    """Generate concise narrative bullets for different stakeholder audiences.

    The copy is intentionally deterministic so the PDF exporter remains reproducible,
    while still highlighting the most material datapoints surfaced in the findings.
    """

    total_components = int(kpis.get("components_third_party", 0) or 0)
    high_risk_licenses = int(kpis.get("licenses_high_risk", 0) or 0)
    foreground_share = float(kpis.get("foreground_share", 0.0) or 0.0)
    third_party_share = float(kpis.get("third_party_share", 0.0) or 0.0)
    clean_room_candidates = int(kpis.get("clean_room_candidates", 0) or 0)

    total_findings = int(risk.get("total_findings", 0) or 0)
    open_vulns = int(kpis.get("vuln_open_count", 0) or 0)
    vuln_density_pct = float(kpis.get("vuln_density", 0.0) or 0.0) * 100.0
    vuln_noise_pct = float(kpis.get("vuln_noise_ratio", 0.0) or 0.0) * 100.0
    weighted_vuln_score = float(kpis.get("vuln_weighted_score", 0.0) or 0.0)
    highest_risk = _primary_risk_caption(risk.get("items", []))

    rewrite_avg = rewrite.get("avg_score", "0.00")
    rewrite_low = int(rewrite.get("low_rewriteable_count", 0) or 0)

    vuln_sources = cast(List[str], vulnerabilities.get("sources", []) or [])

    exec_lines: List[str] = []
    exec_lines.append(
        f"Recommendation: {recommendation.get('text', 'Monitor')} — {recommendation.get('reason', 'No blockers detected.')}."
    )
    exec_lines.append(
        f"IP composition is {foreground_share:.1f}% foreground and {third_party_share:.1f}% third-party across {total_components:,} audited components."
    )
    if high_risk_licenses:
        exec_lines.append(f"High-risk licenses present: {high_risk_licenses}. Engage counsel before disclosures.")
    else:
        exec_lines.append("No high-risk licenses surfaced across sampled manifests.")
    if open_vulns:
        exec_lines.append(
            f"Dependency backlog: {open_vulns} items ({vuln_density_pct:.1f}% density, weighted score {weighted_vuln_score:.2f})."
        )
    else:
        exec_lines.append(
            "Dependency scan cleared noise-floor filters; no actionable vulnerabilities in scope."
        )
    if total_findings:
        exec_lines.append(f"{total_findings} aggregate risk signals remain; top watch item: {highest_risk}.")
    else:
        exec_lines.append("Security, similarity, and dependency scanners reported a clean baseline.")

    board_lines: List[str] = []
    board_lines.append(
        f"Foreground ownership at {foreground_share:.1f}% signals clear provenance; {third_party_share:.1f}% external footprint requires contract alignment."
    )
    if clean_room_candidates:
        board_lines.append(
            f"{clean_room_candidates} clean-room candidates identified. Expect diligence dialogue on escrow readiness."
        )
    else:
        board_lines.append("No clean-room blockers identified in this pass; keep hygiene checks active.")
    if open_vulns:
        board_lines.append(
            f"Dependency risk: {open_vulns} vulnerabilities retained after filters, {vuln_noise_pct:.1f}% of OSV noise suppressed."
        )
    else:
        board_lines.append("Dependency risk nominal; OSV noise filters suppressed all non-actionable hits.")
    board_lines.append(f"Risk snapshot: {total_findings} open findings, primary theme is {highest_risk}.")

    engineering_lines: List[str] = []
    engineering_lines.append(f"Average rewriteability score: {rewrite_avg}. Focus on {rewrite_low} low-score modules for isolation.")
    engineering_lines.append(
        f"Vulnerability queue: {open_vulns} items (noise rejection {vuln_noise_pct:.1f}%). Patch highest-weight findings ({weighted_vuln_score:.2f} avg score)."
    )
    engineering_lines.append(
        f"Secrets + SAST backlog totals {total_findings} items. Prioritise rotation and triage workflows next sprint."
    )
    engineering_lines.append(
        f"License scan flagged {high_risk_licenses} reciprocal obligations; confirm NOTICE files before pushing release builds."
    )
    if vuln_sources:
        engineering_lines.append(f"Vulnerability coverage: {', '.join(vuln_sources)}.")

    return {
        "executive": exec_lines,
        "board": board_lines,
        "engineering": engineering_lines,
    }


def _primary_risk_caption(items: Any) -> str:
    if not isinstance(items, list) or not items:
        return "baseline monitoring"
    dict_items: List[Dict[str, Any]] = []
    for entry in cast(Iterable[Any], items):
        if isinstance(entry, dict):
            dict_items.append(cast(Dict[str, Any], entry))
    sorted_items = sorted(
        dict_items,
        key=lambda entry: int(entry.get("count", 0) or 0),
        reverse=True,
    )
    if not sorted_items:
        return "baseline monitoring"
    top = sorted_items[0]
    area = str(top.get("area", "risk")).strip() or "risk"
    severity = str(top.get("severity", "Medium")).strip()
    return f"{severity.lower()} {area.lower()} exposure"
