"""HTML/PDF executive summary reporter built on modular Jinja templates."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple, cast

from jinja2 import Environment, FileSystemLoader, TemplateNotFound, select_autoescape

from .narrative import build_narrative


class PDFReporter:
    """Render the ForgeTrace executive summary into HTML and optionally PDF."""

    TEMPLATE_NAME = "executive_summary.html.jinja2"

    SECTION_ORDER: Dict[str, List[str]] = {
        "board": [
            "cover",
            "narrative",
            "kpis",
            "risk",
            "compliance",
            "rewrite",
            "next_steps",
        ],
        "executive": [
            "cover",
            "narrative",
            "kpis",
            "risk",
            "rewrite",
            "ip",
            "compliance",
            "provenance",
            "similarity",
            "policy",
            "next_steps",
        ],
        "detailed": [
            "cover",
            "narrative",
            "kpis",
            "risk",
            "rewrite",
            "ip",
            "compliance",
            "similarity",
            "policy",
            "provenance",
            "appendix",
            "next_steps",
        ],
    }

    def __init__(
        self,
        findings: Dict[str, Any],
        output_dir: Path | str,
        config: Dict[str, Any] | None,
    ) -> None:
        self.findings = findings
        self.output_dir = Path(output_dir)
        self.config = config or {}
        self.templates_dir = Path(__file__).resolve().parent / "templates"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(self) -> None:
        """Render HTML (and optionally PDF) to the output directory."""

        context = self._build_context()
        env = self._build_environment()

        try:
            template = env.get_template(self.TEMPLATE_NAME)
        except (
            TemplateNotFound
        ) as exc:  # pragma: no cover - hard failure during runtime usage
            raise RuntimeError(
                f"Template '{self.TEMPLATE_NAME}' not found under {self.templates_dir}"
            ) from exc

        rendered_html = template.render(**context)

        html_path = self.output_dir / "executive_summary.html"
        pdf_path = self.output_dir / "executive_summary.pdf"

        html_path.write_text(rendered_html, encoding="utf-8")

        if not self._should_render_pdf():
            return

        try:
            from weasyprint import HTML  # type: ignore[import-untyped]

            html = HTML(string=rendered_html, base_url=str(html_path.parent))
            html.write_pdf(str(pdf_path))  # type: ignore[attr-defined]
        except ImportError:  # pragma: no cover - optional dependency
            print("WeasyPrint not available. Skipping PDF generation.")
        except Exception as exc:  # pragma: no cover - runtime safeguard
            print(f"PDF generation failed: {exc}")

    # ------------------------------------------------------------------
    # Context + environment helpers
    # ------------------------------------------------------------------

    def _build_environment(self) -> Environment:
        loader = FileSystemLoader(str(self.templates_dir))
        env = Environment(
            loader=loader,
            autoescape=select_autoescape(("html", "jinja2")),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        def _format_int_filter(value: Any) -> str:
            return self._format_int(value)

        def _format_percent_filter(value: Any) -> str:
            return self._format_percent(value)

        def _coalesce_filter(value: Any, fallback: str = "N/A") -> str:
            if value in {None, ""}:
                return fallback
            return str(value)

        filters = env.filters  # type: ignore[assignment]
        filters["format_int"] = _format_int_filter  # type: ignore[assignment]
        filters["format_percent"] = _format_percent_filter  # type: ignore[assignment]
        filters["coalesce"] = _coalesce_filter  # type: ignore[assignment]

        return env

    def _should_render_pdf(self) -> bool:
        output_cfg = cast(Dict[str, Any], self.config.get("output", {}) or {})
        include_pdf = output_cfg.get("include_pdf")
        if include_pdf is None:
            return True
        return bool(include_pdf)

    def _build_context(self) -> Dict[str, Any]:
        output_cfg = cast(Dict[str, Any], self.config.get("output", {}) or {})
        layout_cfg = cast(Dict[str, Any], output_cfg.get("report_layout", {}) or {})
        mode = str(output_cfg.get("executive_mode", "executive")).lower()
        if mode not in self.SECTION_ORDER:
            mode = "executive"

        cost = cast(Dict[str, Any], self.findings.get("cost_estimate", {}) or {})
        classifications = cast(
            Dict[str, Dict[str, Any]], self.findings.get("classification", {}) or {}
        )
        rewriteability = cast(
            Dict[str, Dict[str, Any]], self.findings.get("rewriteability", {}) or {}
        )
        sbom = cast(Dict[str, Any], self.findings.get("sbom", {}) or {})
        licenses = cast(Dict[str, Any], self.findings.get("licenses", {}) or {})
        git_info = cast(Dict[str, Any], self.findings.get("git", {}) or {})
        secrets = cast(Dict[str, Any], self.findings.get("secrets", {}) or {})
        sast = cast(Dict[str, Any], self.findings.get("sast", {}) or {})
        similarity = cast(Dict[str, Any], self.findings.get("similarity", {}) or {})
        vulnerabilities = cast(
            Dict[str, Any], self.findings.get("vulnerabilities", {}) or {}
        )
        policy_findings = cast(
            List[Dict[str, Any]], self.findings.get("policy_violations", []) or []
        )

        dependencies = self._extract_dependencies(sbom)
        license_summary = self._summarize_licenses(licenses)
        compliance = self._build_compliance_obligations(license_summary)
        origin_breakdown = self._summarize_origins(classifications)
        contribution_table = self._build_contribution_table(
            classifications, rewriteability
        )
        top_authors, commit_window = self._summarize_authors(git_info)
        provenance = self._build_provenance_insights(
            git_info, classifications, top_authors
        )
        rewrite_stats = self._summarize_rewriteability(rewriteability, classifications)
        rewrite_stats["quadrants"] = self._build_rewrite_quadrants(
            classifications, rewriteability
        )

        secrets_count = self._count_findings(secrets)
        sast_count = self._count_findings(sast)
        duplicate_pairs = cast(
            List[Dict[str, Any]], similarity.get("duplicates", []) or []
        )
        risk, duplicate_highlights, key_risks = self._build_risk_matrix(
            secrets_count,
            sast_count,
            duplicate_pairs,
            vulnerabilities,
        )

        stakeholder_questions = self._build_stakeholder_questions(
            risk, compliance, rewrite_stats
        )
        engagement = self._build_engagement_section(output_cfg, stakeholder_questions)
        appendix = self._build_appendix_section(
            dependencies, risk, stakeholder_questions
        )
        next_steps = self._build_next_steps(risk, rewrite_stats, compliance)

        kpis = self._build_kpis(
            cost,
            dependencies,
            compliance,
            rewrite_stats,
            classifications,
            vulnerabilities,
        )
        kpi_cards = self._build_kpi_cards(mode, kpis)
        policy_summary = self._summarize_policy_violations(policy_findings)
        negotiation_points = self._build_negotiation_points(
            classifications,
            compliance,
            rewrite_stats,
            risk,
            key_risks,
            kpis,
        )
        recommendation = self._decide_recommendation(
            kpis, compliance, rewrite_stats, policy_summary
        )
        license_heatmap = self._build_license_heatmap(classifications, licenses)
        high_risk_identifiers = self._extract_high_risk_identifiers(license_summary)
        ip_share_list = self._build_ip_share_list(classifications)
        ip_top_modules = self._select_top_modules(contribution_table)
        similarity_section = self._summarize_similarity_section(
            similarity, duplicate_highlights
        )
        dependency_observations = self._build_dependency_observations(
            dependencies, compliance
        )
        top_packages = self._identify_top_packages(
            cast(List[Dict[str, str]], dependencies.get("items", []))
        )

        narrative_blocks = build_narrative(
            kpis, risk, rewrite_stats, compliance, recommendation, vulnerabilities
        )
        commit_sparkline = self._build_commit_sparkline(
            cast(List[Dict[str, Any]], git_info.get("timeline", []) or [])
        )

        now_utc = datetime.now(timezone.utc)
        metadata = cast(Dict[str, Any], self.config.get("metadata", {}) or {})
        branding = {
            "logo_path": metadata.get("logo_path") or output_cfg.get("logo_path") or "",
            "watermark": metadata.get("watermark_text")
            or output_cfg.get("watermark_text")
            or "",
            "classification_label": metadata.get("classification_label")
            or output_cfg.get("classification_label")
            or "",
        }
        engagement_id = (
            metadata.get("engagement_id") or output_cfg.get("engagement_id") or ""
        )
        classification_label = (
            branding["classification_label"] or "Confidential - Technical Due Diligence"
        )

        context: Dict[str, Any] = {
            "mode": mode,
            "sections": self._resolve_sections(mode, layout_cfg),
            "client": {
                "client_name": metadata.get("client_name")
                or output_cfg.get("client_name")
                or "ForgeTrace Client",
                "engagement_window": metadata.get("engagement_window")
                or self._format_engagement_window(output_cfg),
                "generated_on": now_utc.strftime("%Y-%m-%d %H:%M UTC"),
                "prepared_by": metadata.get("prepared_by")
                or "Peter Kolawole, BAMG Studio LLC",
                "contact_email": metadata.get("contact_email", ""),
                "year": now_utc.year,
                "engagement_id": engagement_id,
                "classification_label": classification_label,
            },
            "branding": branding,
            "recommendation": recommendation,
            "negotiation": {"points": negotiation_points},
            "narrative": narrative_blocks,
            "kpis": kpis,
            "kpi_cards": kpi_cards,
            "risk": risk,
            "vulnerabilities": vulnerabilities,
            "duplicate_highlights": duplicate_highlights,
            "key_risks": key_risks,
            "rewrite": rewrite_stats,
            "licenses": {
                "summary": license_summary,
                "heatmap": license_heatmap,
                "high_risk": high_risk_identifiers,
            },
            "compliance": compliance,
            "origin_breakdown": origin_breakdown,
            "ip": {
                "share_list": ip_share_list,
                "top_modules": ip_top_modules,
                "contribution_table": contribution_table,
            },
            "similarity": similarity_section,
            "policy": policy_summary,
            "provenance": {
                "notes": provenance["notes"],
                "insights": provenance["insights"],
                "milestones": provenance["milestones"],
                "commit_window": commit_window,
                "sparkline": commit_sparkline,
            },
            "engagement": engagement,
            "appendix": appendix,
            "next_steps": next_steps,
            "dependency": {
                "observations": dependency_observations,
                "top_packages": top_packages,
            },
        }

        return context

    def _resolve_sections(self, mode: str, layout_cfg: Dict[str, Any]) -> List[str]:
        default_order = self.SECTION_ORDER.get(mode, self.SECTION_ORDER["executive"])
        toggles: Dict[str, bool] = {name: True for name in self._all_section_names()}
        for key, value in layout_cfg.items():
            key_norm = str(key).lower().strip()
            if key_norm.startswith("include_"):
                key_norm = key_norm.split("include_", 1)[1]
            if key_norm in toggles:
                toggles[key_norm] = bool(value)
        return [section for section in default_order if toggles.get(section, True)]

    def _all_section_names(self) -> List[str]:
        names: List[str] = []
        for section_list in self.SECTION_ORDER.values():
            for section in section_list:
                if section not in names:
                    names.append(section)
        return names

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

    # ------------------------------------------------------------------
    # Metrics + summarisation helpers (portions adapted from the legacy reporter)
    # ------------------------------------------------------------------

    def _build_kpis(
        self,
        cost: Dict[str, Any],
        dependencies: Dict[str, Any],
        compliance: Dict[str, Any],
        rewrite: Dict[str, Any],
        classifications: Dict[str, Dict[str, Any]],
        vulnerabilities: Dict[str, Any],
    ) -> Dict[str, Any]:
        loc_total = int(cost.get("total_loc", 0) or 0)
        loc_foreground = int(cost.get("foreground_loc", 0) or 0)
        loc_background = int(cost.get("background_loc", 0) or 0)

        counts, total = self._count_origins(classifications)
        foreground_files = counts.get("foreground", 0)
        background_files = counts.get("background", 0)
        third_party_files = counts.get("third_party", 0)

        components_third_party = int(dependencies.get("third_party_count", 0) or 0)
        high_risk_licenses = int(compliance.get("high_risk_count", 0) or 0)
        clean_room_candidates = int(rewrite.get("high_rewriteable_count", 0) or 0)
        vuln_total = int(vulnerabilities.get("total_vulnerabilities", 0) or 0)
        vuln_density = float(vulnerabilities.get("normalized_vuln_density", 0.0) or 0.0)
        vuln_weighted = float(vulnerabilities.get("weighted_vuln_score", 0.0) or 0.0)
        vuln_noise_ratio = float(vulnerabilities.get("osv_noise_ratio", 0.0) or 0.0)

        def share(value: int) -> float:
            if total <= 0:
                return 0.0
            return (value / total) * 100.0

        return {
            "loc_total": loc_total,
            "loc_foreground": loc_foreground,
            "loc_background": loc_background,
            "components_third_party": components_third_party,
            "licenses_high_risk": high_risk_licenses,
            "clean_room_candidates": clean_room_candidates,
            "foreground_share": share(foreground_files),
            "background_share": share(background_files),
            "third_party_share": share(third_party_files),
            "vuln_open_count": vuln_total,
            "vuln_density": vuln_density,
            "vuln_weighted_score": vuln_weighted,
            "vuln_noise_ratio": vuln_noise_ratio,
        }

    def _build_kpi_cards(self, mode: str, kpis: Dict[str, Any]) -> List[Dict[str, str]]:
        cards = [
            {
                "label": "Open Vulnerabilities",
                "value": self._format_int(kpis.get("vuln_open_count", 0)),
            },
            {
                "label": "Vuln Density",
                "value": f"{kpis.get('vuln_density', 0.0) * 100:.1f}%",
            },
            {
                "label": "Weighted Vuln Score",
                "value": f"{float(kpis.get('vuln_weighted_score', 0.0)):.2f}",
            },
            {
                "label": "Foreground LOC",
                "value": self._format_int(kpis.get("loc_foreground", 0)),
            },
            {
                "label": "Background LOC",
                "value": self._format_int(kpis.get("loc_background", 0)),
            },
            {
                "label": "Third-Party Components",
                "value": self._format_int(kpis.get("components_third_party", 0)),
            },
            {
                "label": "High-Risk Licenses",
                "value": self._format_int(kpis.get("licenses_high_risk", 0)),
            },
            {
                "label": "Clean-Room Candidates",
                "value": self._format_int(kpis.get("clean_room_candidates", 0)),
            },
            {
                "label": "Foreground Share",
                "value": self._format_percent(kpis.get("foreground_share", 0.0)),
            },
            {
                "label": "Third-Party Share",
                "value": self._format_percent(kpis.get("third_party_share", 0.0)),
            },
            {
                "label": "Total LOC Inventoried",
                "value": self._format_int(kpis.get("loc_total", 0)),
            },
        ]

        if mode == "board":
            return cards[:5]
        if mode == "executive":
            return cards[:7]
        return cards

    def _build_negotiation_points(
        self,
        classifications: Dict[str, Dict[str, Any]],
        compliance: Dict[str, Any],
        rewrite: Dict[str, Any],
        risk: Dict[str, Any],
        key_risks: str,
        kpis: Dict[str, Any],
    ) -> List[str]:
        points: List[str] = []
        if kpis.get("background_share", 0.0) >= 20.0:
            points.append(
                (
                    f"Background IP share sits at {self._format_percent(kpis['background_share'])}; "
                    "confirm contract scope covers these modules."
                )
            )

        if int(compliance.get("high_risk_count", 0) or 0) > 0:
            points.append(
                "Reciprocal licenses present; negotiate carve-outs or plan clean-room isolation."
            )

        if int(rewrite.get("low_rewriteable_count", 0) or 0) > 0:
            points.append(
                (
                    "Low rewriteability foreground modules require clean-room planning "
                    "before partner disclosures."
                )
            )

        if kpis.get("third_party_share", 0.0) >= 60.0 and len(points) < 3:
            points.append(
                (
                    "Third-party code exceeds 60% of inventoried files; expect diligence "
                    "questions on integration rights."
                )
            )

        if (
            not points
            and key_risks
            and key_risks.lower() != "no material risks flagged in this pass"
        ):
            points.append(key_risks)

        if not points:
            points.append(
                "No material blockers detected; maintain watchlist as new code lands."
            )

        return points[:3]

    def _decide_recommendation(
        self,
        kpis: Dict[str, Any],
        compliance: Dict[str, Any],
        rewrite: Dict[str, Any],
        policy_summary: Dict[str, Any],
    ) -> Dict[str, str]:
        high_risk = int(compliance.get("high_risk_count", 0) or 0)
        clean_room = int(rewrite.get("high_rewriteable_count", 0) or 0)
        low_rewrite = int(rewrite.get("low_rewriteable_count", 0) or 0)
        block_count = int(policy_summary.get("block", 0) or 0)

        if block_count > 0 or high_risk > 0:
            return {
                "text": "Clean-Room",
                "badge_class": "badge-critical",
                "reason": "Block-level policies or high-risk licenses require isolation and remediation before close.",
            }

        if clean_room > 0 or low_rewrite > 0:
            return {
                "text": "Refactor",
                "badge_class": "badge-medium",
                "reason": "Foreground modules need refactor or clean-room execution prior to transfer.",
            }

        if kpis.get("third_party_share", 0.0) > 50.0:
            return {
                "text": "Monitor",
                "badge_class": "badge-high",
                "reason": "Majority third-party footprint; tighten provenance attestations in negotiations.",
            }

        return {
            "text": "Keep",
            "badge_class": "badge-low",
            "reason": "No material blockers identified; continue routine IP hygiene checks.",
        }

    def _build_license_heatmap(
        self,
        classifications: Dict[str, Dict[str, Any]],
        licenses: Dict[str, Any],
    ) -> List[List[Any]]:
        buckets = {
            "Permissive": {"foreground": 0, "background": 0, "third_party": 0},
            "Weak Copyleft": {"foreground": 0, "background": 0, "third_party": 0},
            "Strong Copyleft": {"foreground": 0, "background": 0, "third_party": 0},
        }

        for data in classifications.values():
            origin_raw = str(data.get("origin", "unknown")).lower()
            origin = "foreground"
            if "third" in origin_raw:
                origin = "third_party"
            elif origin_raw not in {"foreground"}:
                origin = "background"

            license_name = str(data.get("license") or "unknown").lower()
            category = self._categorize_license(license_name)
            if category in buckets:
                buckets[category][origin] += 1

        if not any(sum(values.values()) for values in buckets.values()):
            findings = cast(List[Dict[str, Any]], licenses.get("findings", []) or [])
            for entry in findings:
                license_name = str(entry.get("license") or "unknown").lower()
                category = self._categorize_license(license_name)
                if category in buckets:
                    buckets[category]["third_party"] += 1

        heatmap: List[List[Any]] = [["", "Foreground", "Background", "Third-party"]]
        for category in ("Permissive", "Weak Copyleft", "Strong Copyleft"):
            row = buckets.get(
                category, {"foreground": 0, "background": 0, "third_party": 0}
            )
            heatmap.append(
                [
                    category,
                    self._format_int(row.get("foreground", 0)),
                    self._format_int(row.get("background", 0)),
                    self._format_int(row.get("third_party", 0)),
                ]
            )
        return heatmap

    def _extract_high_risk_identifiers(
        self, license_summary: List[Dict[str, Any]]
    ) -> List[str]:
        high_risk: List[str] = []
        for entry in license_summary:
            name = str(entry.get("license", "")).strip()
            if not name:
                continue
            upper_name = name.upper()
            if any(
                keyword in upper_name for keyword in ("GPL", "AGPL", "SSPL", "COPYLEFT")
            ):
                high_risk.append(name)
        return high_risk[:6]

    def _build_ip_share_list(
        self, classifications: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        counts, total = self._count_origins(classifications)
        if total == 0:
            return [
                {"label": "Foreground", "value": "0%"},
                {"label": "Background", "value": "0%"},
                {"label": "Third-party", "value": "0%"},
            ]

        return [
            {
                "label": "Foreground",
                "value": self._format_percent(
                    (counts.get("foreground", 0) / total) * 100
                ),
            },
            {
                "label": "Background",
                "value": self._format_percent(
                    (counts.get("background", 0) / total) * 100
                ),
            },
            {
                "label": "Third-party",
                "value": self._format_percent(
                    (counts.get("third_party", 0) / total) * 100
                ),
            },
        ]

    def _select_top_modules(
        self, contribution_table: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        top_rows = contribution_table[:5]
        formatted: List[Dict[str, Any]] = []
        for row in top_rows:
            formatted.append(
                {
                    "name": row.get("module", "unknown"),
                    "origin": row.get("origin", "unknown"),
                    "rewriteability": row.get("rewriteable", "-"),
                    "score": row.get("score", "0.00"),
                    "loc": self._format_int(row.get("loc", 0)),
                }
            )
        if not formatted:
            formatted.append(
                {
                    "name": "No modules analysed",
                    "origin": "-",
                    "rewriteability": "-",
                    "score": "0.00",
                    "loc": "0",
                }
            )
        return formatted

    def _summarize_policy_violations(
        self, policy_findings: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        summary = {"block": 0, "warn": 0, "info": 0}
        violations: List[Dict[str, Any]] = []
        for entry in policy_findings:
            action = str(entry.get("action", "INFO")).upper()
            if action == "BLOCK":
                summary["block"] += 1
            elif action == "WARN":
                summary["warn"] += 1
            else:
                summary["info"] += 1
            if len(violations) < 40:
                violations.append(
                    {
                        "policy_id": entry.get("policy_id", "-"),
                        "policy_name": entry.get("policy_name", "-"),
                        "severity": entry.get("severity", "-"),
                        "action": action,
                        "message": entry.get("message", ""),
                    }
                )
        return {
            "block": summary["block"],
            "warn": summary["warn"],
            "info": summary["info"],
            "violations": violations or [],
        }

    def _summarize_similarity_section(
        self,
        similarity: Dict[str, Any],
        duplicate_highlights: List[Dict[str, str]],
    ) -> Dict[str, Any]:
        public_matches_raw = cast(
            List[Dict[str, Any]], similarity.get("public_matches", []) or []
        )
        public_matches: List[Dict[str, str]] = []
        for match in public_matches_raw[:5]:
            public_matches.append(
                {
                    "file": str(match.get("file", "-")),
                    "source": str(match.get("source", "unknown")),
                    "confidence": f"{float(match.get('confidence', 0) or 0):.2f}",
                }
            )

        duplicates = duplicate_highlights[:5] or [
            {"file1": "-", "file2": "-", "similarity": "0.00"}
        ]

        total_duplicates = len(cast(List[Any], similarity.get("duplicates", []) or []))
        summary: List[str] = [
            f"{total_duplicates} similarity pair{'s' if total_duplicates != 1 else ''} exceeded diligence threshold.",
        ]
        if public_matches:
            summary.append(
                "Public code matches detected; confirm provenance and licensing for overlapping files."
            )
        else:
            summary.append("No public code matches surfaced in this pass.")
        return {
            "duplicates": duplicates,
            "public_matches": public_matches,
            "summary": summary[:3],
        }

    def _build_rewrite_quadrants(
        self,
        classifications: Dict[str, Dict[str, Any]],
        rewriteability: Dict[str, Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        quadrants: Dict[str, List[str]] = {
            "Easy/Low-risk": [],
            "Easy/High-risk": [],
            "Hard/Low-risk": [],
            "Hard/High-risk": [],
        }

        for path, metrics in rewriteability.items():
            score = float(metrics.get("score", 0) or 0)
            difficulty = (
                "Easy" if score >= 0.75 else "Hard" if score <= 0.4 else "Medium"
            )
            origin_raw = str(
                classifications.get(path, {}).get("origin", "foreground")
            ).lower()
            risk = "Low-risk"
            if "third" in origin_raw or origin_raw == "background":
                risk = "High-risk"

            quadrant_key = f"{difficulty}/{risk}"
            if quadrant_key not in quadrants:
                quadrant_key = f"Hard/{risk}"
            quadrants[quadrant_key].append(Path(path).name or path)

        quadrant_list: List[Dict[str, Any]] = []
        for key in (
            "Easy/Low-risk",
            "Easy/High-risk",
            "Hard/Low-risk",
            "Hard/High-risk",
        ):
            modules = quadrants.get(key, [])[:6]
            quadrant_list.append(
                {
                    "quadrant": key,
                    "modules": modules or ["No modules identified"],
                }
            )
        return quadrant_list

    def _format_int(self, value: Any) -> str:
        try:
            return f"{int(value):,}"
        except (TypeError, ValueError):
            return "0"

    def _format_percent(self, value: Any) -> str:
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            numeric = 0.0
        return f"{numeric:.1f}%"

    def _count_origins(
        self, classifications: Dict[str, Dict[str, Any]]
    ) -> Tuple[Counter[str], int]:
        counter: Counter[str] = Counter()
        for data in classifications.values():
            origin = str(data.get("origin", "unknown")).lower()
            if "third" in origin:
                origin = "third_party"
            counter[origin] += 1
        total = sum(counter.values())
        return counter, total

    def _categorize_license(self, license_name: str) -> str:
        name = license_name.upper()
        if any(keyword in name for keyword in ("GPL", "AGPL", "SSPL", "COPYLEFT")):
            return "Strong Copyleft"
        if any(keyword in name for keyword in ("LGPL", "MPL", "CDDL", "EUPL")):
            return "Weak Copyleft"
        if name and name != "UNKNOWN":
            return "Permissive"
        return "Permissive"

    def _extract_dependencies(self, sbom: Dict[str, Any]) -> Dict[str, Any]:
        packages_raw_list = cast(
            List[Any], sbom.get("packages") or sbom.get("dependencies") or []
        )
        packages: List[Dict[str, Any]] = []
        items: List[Dict[str, str]] = []
        manifests: set[str] = set()

        for entry in packages_raw_list:
            if not isinstance(entry, dict):
                continue
            pkg = cast(Dict[str, Any], entry)
            name = pkg.get("name") or pkg.get("package") or "unknown"
            version = pkg.get("version") or pkg.get("qualifier") or ""
            pkg_type = pkg.get("type") or pkg.get("purl", "").split(":")[0] or "unknown"
            source_file = pkg.get("file") or pkg.get("manifestFile") or ""

            packages.append(pkg)
            if source_file:
                manifests.add(str(source_file))
            items.append(
                {
                    "name": str(name),
                    "version": str(version),
                    "type": str(pkg_type),
                    "file": str(source_file),
                }
            )

        items = sorted(items, key=lambda row: row.get("name", ""))[:50]
        return {
            "items": items,
            "total": len(packages),
            "manifests": len(manifests),
            "third_party_count": len(packages),
        }

    def _summarize_licenses(self, licenses: Dict[str, Any]) -> List[Dict[str, Any]]:
        findings_raw = cast(List[Any], licenses.get("findings") or [])
        findings: List[Dict[str, Any]] = [
            cast(Dict[str, Any], entry)
            for entry in findings_raw
            if isinstance(entry, dict)
        ]
        counter: Counter[str] = Counter()
        files_by_license: Dict[str, set[str]] = {}
        for entry in findings:
            lic = str(entry.get("license") or "Unknown")
            counter[lic] += 1
            files_by_license.setdefault(lic, set()).add(str(entry.get("file", "")))

        summary: List[Dict[str, Any]] = []
        for license_name, count in counter.most_common(10):
            files = ", ".join(
                sorted(f for f in files_by_license.get(license_name, set()) if f)
            )
            summary.append(
                {
                    "license": license_name,
                    "count": int(count),
                    "files": files[:200]
                    + ("..." if files and len(files) > 200 else ""),
                }
            )

        if not summary:
            summary.append({"license": "None Detected", "count": 0, "files": ""})
        return summary

    def _summarize_origins(
        self, classifications: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        total = max(len(classifications), 1)
        counter: Counter[str] = Counter(
            str(data.get("origin", "unknown")) for data in classifications.values()
        )
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
            rows.append(
                {
                    "module": module_name,
                    "origin": data.get("origin", "unknown"),
                    "primary_author": data.get("primary_author", "unknown"),
                    "license": data.get("license", "none"),
                    "rewriteable": "Yes" if rewrite.get("rewriteable") else "No",
                    "score": f"{score_value:.2f}",
                    "score_value": score_value,
                    "loc": int(rewrite.get("loc", 0) or 0),
                }
            )

        rows.sort(key=lambda item: item.get("score_value", 0))
        return rows[:40] or [
            {
                "module": "No modules analysed",
                "origin": "-",
                "primary_author": "-",
                "license": "-",
                "rewriteable": "-",
                "score": "0.00",
                "score_value": 0.0,
                "loc": 0,
            }
        ]

    def _summarize_authors(
        self, git_info: Dict[str, Any]
    ) -> Tuple[List[Dict[str, Any]], str]:
        authors = cast(Dict[str, Any], git_info.get("authors", {}) or {})
        churn = cast(Dict[str, Any], git_info.get("churn", {}) or {})
        timeline = cast(List[Dict[str, Any]], git_info.get("timeline", []) or [])

        rows: List[Dict[str, Any]] = []
        for name, metrics in authors.items():
            churn_metrics = cast(Dict[str, Any], churn.get(name, {}) or {})
            rows.append(
                {
                    "name": name,
                    "commits": int(metrics.get("commits", 0) or 0),
                    "added": int(churn_metrics.get("added", 0) or 0),
                    "removed": int(churn_metrics.get("removed", 0) or 0),
                    "files": int(churn_metrics.get("files", 0) or 0),
                }
            )

        rows.sort(key=lambda item: item.get("commits", 0), reverse=True)
        top_rows: List[Dict[str, Any]]
        if rows:
            top_rows = rows[:10]
        else:
            top_rows = [
                {"name": "Unknown", "commits": 0, "added": 0, "removed": 0, "files": 0}
            ]

        if timeline:
            dates = sorted(
                str(entry.get("date")) for entry in timeline if entry.get("date")
            )
            if len(dates) >= 2:
                commit_window = f"{dates[0][:10]} to {dates[-1][:10]}"
            elif dates:
                commit_window = dates[0][:10]
            else:
                commit_window = "No commit history detected"
        else:
            commit_window = "No commit history detected"

        return top_rows, commit_window

    def _summarize_rewriteability(
        self,
        rewriteability: Dict[str, Dict[str, Any]],
        classifications: Dict[str, Dict[str, Any]],
    ) -> Dict[str, Any]:
        scores = [float(data.get("score", 0) or 0) for data in rewriteability.values()]
        avg_score = sum(scores) / len(scores) if scores else 0.0
        low_rewriteable = [
            path
            for path, meta in rewriteability.items()
            if float(meta.get("score", 0) or 0) < 0.4
            and str(classifications.get(path, {}).get("origin", "")).lower()
            == "foreground"
        ]
        high_rewriteable = [
            path
            for path, meta in rewriteability.items()
            if float(meta.get("score", 0) or 0) >= 0.75
            and str(classifications.get(path, {}).get("origin", "")).lower()
            == "foreground"
        ]

        recommendations: List[str] = []
        if low_rewriteable:
            recommendations.append(
                "Prioritize ring-fencing low-score foreground modules before disclosure to counterparties."
            )
        if high_rewriteable:
            recommendations.append(
                "Prepare clean-room briefs for high-score modules to accelerate potential rewrites with contractors."
            )
        if not recommendations:
            recommendations.append(
                "No critical rewrite blockers detected; maintain periodic reassessment alongside refactors."
            )

        priority_modules = [
            Path(path).name or path for path in low_rewriteable[:5]
        ] or ["No critical modules identified."]

        playbook = [
            "Document clean-room brief per high priority module.",
            "Assign independent implementers for guarded rewrites.",
            "Track escrow-ready deliverables with counsel oversight.",
        ]
        if len(high_rewriteable) >= 5:
            playbook.append(
                "Sequence rewrites in sprints to capture high-score efficiencies."
            )

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
        vulnerabilities: Dict[str, Any],
    ) -> Tuple[Dict[str, Any], List[Dict[str, str]], str]:
        overview: List[Dict[str, Any]] = []
        total_findings = 0
        vuln_total = int(vulnerabilities.get("total_vulnerabilities", 0) or 0)
        by_severity = cast(Dict[str, int], vulnerabilities.get("by_severity", {}) or {})
        density = float(vulnerabilities.get("normalized_vuln_density", 0.0) or 0.0)
        weighted_score = float(vulnerabilities.get("weighted_vuln_score", 0.0) or 0.0)
        noise_ratio = float(vulnerabilities.get("osv_noise_ratio", 0.0) or 0.0)
        severity_order = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN"]
        highest_severity = "UNKNOWN"
        for severity_name in severity_order:
            if int(by_severity.get(severity_name, 0) or 0) > 0:
                highest_severity = severity_name
                break

        if vuln_total:
            overview.append(
                {
                    "area": "Dependencies",
                    "count": vuln_total,
                    "severity": highest_severity.title(),
                    "badge": self._badge_for_severity(highest_severity),
                    "notes": f"Density {density * 100:.1f}% • Weighted score {weighted_score:.2f}",
                }
            )
            total_findings += vuln_total
        else:
            overview.append(
                {
                    "area": "Dependencies",
                    "count": 0,
                    "severity": "None",
                    "badge": "badge-low",
                    "notes": "Noise filters cleared the OSV backlog.",
                }
            )

        if secrets_count:
            overview.append(
                {
                    "area": "Secrets",
                    "count": secrets_count,
                    "severity": "Critical" if secrets_count > 0 else "None",
                    "badge": "badge-critical" if secrets_count else "badge-low",
                    "notes": "Escalate immediate redaction and key rotation.",
                }
            )
            total_findings += secrets_count
        else:
            overview.append(
                {
                    "area": "Secrets",
                    "count": 0,
                    "severity": "None",
                    "badge": "badge-low",
                    "notes": "No hardcoded secrets detected.",
                }
            )

        if sast_count:
            severity = "High" if sast_count > 5 else "Medium"
            badge = "badge-high" if sast_count > 5 else "badge-medium"
            overview.append(
                {
                    "area": "SAST",
                    "count": sast_count,
                    "severity": severity,
                    "badge": badge,
                    "notes": "Review flagged rules and triage exploitable paths.",
                }
            )
            total_findings += sast_count
        else:
            overview.append(
                {
                    "area": "SAST",
                    "count": 0,
                    "severity": "None",
                    "badge": "badge-low",
                    "notes": "Static analysis returned no actionable findings.",
                }
            )

        dup_count = len(duplicate_pairs)
        if dup_count:
            severity = "Medium" if dup_count < 10 else "High"
            badge = "badge-medium" if dup_count < 10 else "badge-high"
            overview.append(
                {
                    "area": "Similarity",
                    "count": dup_count,
                    "severity": severity,
                    "badge": badge,
                    "notes": "Assess overlapping code for prior art or third-party contamination.",
                }
            )
            total_findings += dup_count
        else:
            overview.append(
                {
                    "area": "Similarity",
                    "count": 0,
                    "severity": "Low",
                    "badge": "badge-low",
                    "notes": "No significant code duplication detected beyond thresholds.",
                }
            )

        duplicates = [
            {
                "file1": Path(str(pair.get("file1", ""))).name,
                "file2": Path(str(pair.get("file2", ""))).name,
                "similarity": f"{float(pair.get('similarity', 0) or 0):.2f}",
            }
            for pair in duplicate_pairs[:10]
        ]
        if not duplicates:
            duplicates = [{"file1": "-", "file2": "-", "similarity": "0.00"}]

        key_risks: List[str] = []
        if vuln_total:
            key_risks.append("Dependency exposure")
        if secrets_count:
            key_risks.append("Secrets exposure")
        if sast_count:
            key_risks.append("Untriaged static analysis findings")
        if dup_count:
            key_risks.append("Potential provenance conflicts")
        key_risks_str = (
            ", ".join(key_risks)
            if key_risks
            else "No material risks flagged in this pass"
        )

        return (
            {
                "items": overview,
                "total_findings": total_findings,
                "vulnerability_density_percent": density * 100,
                "vulnerability_weighted_score": weighted_score,
                "vulnerability_noise_ratio_percent": noise_ratio * 100,
                "has_vulnerability_findings": bool(vuln_total),
            },
            duplicates,
            key_risks_str,
        )

    def _badge_for_severity(self, severity: str) -> str:
        mapping = {
            "CRITICAL": "badge-critical",
            "HIGH": "badge-high",
            "MEDIUM": "badge-medium",
            "LOW": "badge-low",
            "UNKNOWN": "badge-low",
        }
        return mapping.get(severity.upper(), "badge-low")

    def _build_next_steps(
        self,
        risk: Dict[str, Any],
        rewrite: Dict[str, Any],
        compliance: Dict[str, Any],
    ) -> List[str]:
        actions: List[str] = []
        secrets_exposure = next(
            (
                int(item.get("count", 0))
                for item in risk.get("items", [])
                if item.get("area") == "Secrets"
            ),
            0,
        )
        sast_findings = next(
            (
                int(item.get("count", 0))
                for item in risk.get("items", [])
                if item.get("area") == "SAST"
            ),
            0,
        )

        if secrets_exposure:
            actions.append(
                "Trigger credential rotation playbook and scrub committed secrets from history."
            )
        if sast_findings:
            actions.append(
                "Schedule engineering triage for SAST findings with accountable owners."
            )
        if int(compliance.get("high_risk_count", 0)) > 0:
            actions.append(
                "Engage counsel to validate reciprocal license obligations before external disclosure."
            )
        if int(rewrite.get("low_rewriteable_count", 0)) > 0:
            actions.append(
                "Draft clean-room specs and isolation plans for low-score foreground modules."
            )
        actions.append(
            "Maintain continuous SBOM updates as dependencies evolve across sprints."
        )
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

    def _build_compliance_obligations(
        self, license_summary: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        high_risk_keywords = ("GPL", "AGPL", "LGPL", "AFFERO", "RECIPROCAL", "COPYLEFT")
        high_risk_count = 0
        for entry in license_summary:
            license_name = str(entry.get("license", "")).upper()
            if any(keyword in license_name for keyword in high_risk_keywords):
                high_risk_count += int(entry.get("count", 0) or 0)

        obligations: List[str] = [
            (
                "Ensure SPDX attributions accompany third-party packages "
                "in outbound deliverables."
            ),
            "Track dependency provenance in data rooms alongside SBOM exports.",
        ]
        counsel_actions: List[str] = [
            "Review updated SBOM with legal counsel before diligence disclosures.",
        ]

        if high_risk_count:
            obligations.insert(
                0,
                (
                    f"Review {high_risk_count} GPL-family component obligation"
                    f"{'s' if high_risk_count != 1 else ''} for distribution compatibility."
                ),
            )
            counsel_actions.insert(
                0,
                "Engage counsel to confirm reciprocal terms and draft mitigation language.",
            )
        else:
            obligations.append(
                "Confirm permissive-license notices remain within corporate policy thresholds."
            )

        return {
            "high_risk_count": high_risk_count,
            "obligations": obligations[:6],
            "counsel_actions": counsel_actions[:6],
        }

    def _identify_top_packages(self, dependencies: List[Dict[str, str]]) -> List[str]:
        if not dependencies:
            return ["No package manifests detected."]
        counter: Counter[str] = Counter(
            dep.get("name", "unknown") for dep in dependencies if dep.get("name")
        )
        top_entries = [
            f"{name} ({count} reference{'s' if count != 1 else ''})"
            for name, count in counter.most_common(5)
        ]
        return top_entries or ["No named dependencies available."]

    def _build_dependency_observations(
        self,
        dependencies: Dict[str, Any],
        compliance: Dict[str, Any],
    ) -> List[str]:
        observations: List[str] = []
        total = int(dependencies.get("total", 0) or 0)
        manifests = int(dependencies.get("manifests", 0) or 0)
        observations.append(
            (
                f"Detected {total} package entr{'ies' if total != 1 else 'y'} across "
                f"{manifests} manifest{'s' if manifests != 1 else ''}."
            )
        )
        if int(compliance.get("high_risk_count", 0)) > 0:
            observations.append(
                "GPL-family packages present; confirm isolation before release."
            )

        items = cast(List[Dict[str, str]], dependencies.get("items", []))
        if items:
            ecosystem_counts: Counter[str] = Counter(
                dep.get("type", "unknown") for dep in items if dep.get("type")
            )
            if ecosystem_counts:
                ecosystem, count = ecosystem_counts.most_common(1)[0]
                observations.append(
                    (
                        f"{ecosystem} ecosystem represents {count} component"
                        f"{'s' if count != 1 else ''} in scope."
                    )
                )
        else:
            observations.append(
                "SBOM scanner did not detect dependency manifests in supplied snapshot."
            )

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
                f"{primary_author['name']} leads with {primary_author['commits']} commits "
                f"across {primary_author['files']} files."
            )
        else:
            notes = "No dominant contributor identified in git history."

        foreground_count = sum(
            1
            for meta in classifications.values()
            if str(meta.get("origin", "")).lower() == "foreground"
        )
        background_count = sum(
            1
            for meta in classifications.values()
            if str(meta.get("origin", "")).lower() != "foreground"
        )
        total = foreground_count + background_count

        insights: List[str] = []
        if total:
            share = (foreground_count / total) * 100
            insights.append(
                f"Foreground assets represent {share:.1f}% of inventoried files."
            )
        if primary_author and primary_author.get("added") is not None:
            churn = int(primary_author.get("added", 0) or 0) - int(
                primary_author.get("removed", 0) or 0
            )
            if churn:
                insights.append(
                    f"Net code delta for lead contributor: {churn:+,} lines."
                )

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
            insights.append(
                "Contributor distribution appears balanced across the repository."
            )
        if not milestones:
            milestones.append(
                "No temporal git activity supplied; milestones unavailable."
            )

        return {
            "notes": notes,
            "insights": insights[:5],
            "milestones": milestones[:5],
        }

    def _build_stakeholder_questions(
        self,
        risk: Dict[str, Any],
        compliance: Dict[str, Any],
        rewrite: Dict[str, Any],
    ) -> List[str]:
        questions: List[str] = []
        secrets_count = next(
            (
                int(item.get("count", 0))
                for item in risk.get("items", [])
                if item.get("area") == "Secrets"
            ),
            0,
        )
        sast_count = next(
            (
                int(item.get("count", 0))
                for item in risk.get("items", [])
                if item.get("area") == "SAST"
            ),
            0,
        )

        if int(compliance.get("high_risk_count", 0)) > 0:
            questions.append(
                "How do GPL-family components impact the target distribution model?"
            )
        else:
            questions.append(
                "Is attribution coverage sufficient for planned disclosures?"
            )

        if secrets_count or sast_count:
            questions.append(
                "What is the remediation timeline for outstanding security findings?"
            )

        if int(rewrite.get("low_rewriteable_count", 0)) > 0:
            questions.append(
                "Which low-score modules require clean-room isolation before diligence?"
            )

        questions.append(
            "Do we have sign-off on SBOM accuracy for transaction disclosures?"
        )
        return questions[:4]

    def _build_engagement_section(
        self,
        output_cfg: Dict[str, Any],
        stakeholder_questions: List[str],
    ) -> Dict[str, Any]:
        scope_cfg = self._coerce_to_list(output_cfg.get("executive_scope"))
        if not scope_cfg:
            scope_cfg = [
                (
                    "Source code, licenses, and dependency manifests supplied "
                    "in audit bundle."
                ),
                "Historical git metadata (authors, churn, timeline).",
                "ForgeTrace scanners across secrets, SAST, similarity, and licenses.",
            ]

        deliverables_cfg = self._coerce_to_list(
            output_cfg.get("executive_deliverables")
        )
        if not deliverables_cfg:
            deliverables_cfg = [
                "Executive summary narrative (PDF/HTML).",
                "Machine-readable SBOM extracts (JSON).",
                "Risk, license, and rewriteability analytics.",
            ]

        methodology_summary = str(
            output_cfg.get("methodology_summary")
            or (
                "ForgeTrace executed automated scanners and manual analytics to "
                "surface provenance, license, and security risks."
            )
        )

        return {
            "scope": scope_cfg[:6],
            "deliverables": deliverables_cfg[:6],
            "methodology_summary": methodology_summary,
            "stakeholder_questions": stakeholder_questions,
        }

    def _build_appendix_section(
        self,
        dependencies: Dict[str, Any],
        risk: Dict[str, Any],
        stakeholder_questions: List[str],
    ) -> Dict[str, Any]:
        tooling = [
            (
                "ForgeTrace scanners: SBOM, license, secrets, SAST, similarity, "
                "git provenance."
            ),
            "WeasyPrint-rendered executive PDF via Jinja2 templates.",
        ]

        total_dependencies = int(dependencies.get("total", 0) or 0)
        manifests = int(dependencies.get("manifests", 0) or 0)
        coverage: List[str] = []
        coverage.append(
            (
                f"SBOM captured {total_dependencies} package entr"
                f"{'ies' if total_dependencies != 1 else 'y'} across {manifests} "
                f"manifest{'s' if manifests != 1 else ''}."
            )
        )
        risk_total = sum(int(item.get("count", 0)) for item in risk.get("items", []))
        coverage.append(
            (
                f"Security scanners surfaced {risk_total} aggregate finding"
                f"{'s' if risk_total != 1 else ''} across secrets, SAST, and "
                "similarity modules."
            )
        )
        coverage.append(
            "Git analytics derived from repository metadata supplied in audit bundle."
        )

        questions = stakeholder_questions or [
            "No outstanding stakeholder questions captured."
        ]

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

    def _build_commit_sparkline(
        self, timeline: List[Dict[str, Any]]
    ) -> Dict[str, Any] | None:
        if not timeline:
            return None

        weekly_counts: Dict[datetime, int] = {}
        seen_date = False
        for entry in timeline:
            date_str = str(entry.get("date", "")).strip()
            parsed = self._safe_parse_date(date_str)
            if not parsed:
                continue
            seen_date = True
            week_start = self._compute_week_key(parsed)
            count_raw = (
                entry.get("commits") or entry.get("count") or entry.get("value") or 1
            )
            try:
                count = int(count_raw)
            except (TypeError, ValueError):
                count = 1
            weekly_counts[week_start] = weekly_counts.get(week_start, 0) + max(count, 0)

        if not weekly_counts or not seen_date:
            return None

        sorted_weeks = sorted(weekly_counts.items(), key=lambda item: item[0])
        data = [count for _, count in sorted_weeks]
        if len(data) == 1:
            data.append(data[0])

        max_value = max(data) or 1
        width = 240
        height = 48
        padding = 6
        usable_width = width - (2 * padding)
        usable_height = height - (2 * padding)

        step = usable_width / (len(data) - 1 or 1)
        path_commands: List[str] = []
        x = float(padding)
        for idx, value in enumerate(data):
            normalized = value / max_value if max_value else 0.0
            y = height - padding - (normalized * usable_height)
            command = "M" if idx == 0 else "L"
            path_commands.append(f"{command}{x:.2f},{y:.2f}")
            x += step

        return {
            "path": " ".join(path_commands),
            "width": width,
            "height": height,
            "max": max_value,
            "points": data,
        }

    def _compute_week_key(self, moment: datetime) -> datetime:
        start = moment - timedelta(days=moment.weekday())
        return datetime(start.year, start.month, start.day, tzinfo=moment.tzinfo)

    def _safe_parse_date(self, value: str) -> datetime | None:
        if not value:
            return None
        try:
            if value.endswith("Z"):
                value = value[:-1]
                return datetime.fromisoformat(value).replace(tzinfo=timezone.utc)
            return datetime.fromisoformat(value)
        except ValueError:
            return None
