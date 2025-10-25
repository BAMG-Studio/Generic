"""HTML report exporter"""
from pathlib import Path
from typing import Dict, Any
from datetime import datetime


class HTMLExporter:
    """Export analysis results to HTML format"""
    
    def __init__(self, output_dir: str, repo_name: str):
        """
        Initialize HTML exporter
        
        Args:
            output_dir: Output directory path
            repo_name: Repository name
        """
        self.output_dir = Path(output_dir)
        self.repo_name = repo_name
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export(self, results: Dict[str, Any]) -> str:
        """
        Export results to HTML file
        
        Args:
            results: Analysis results dictionary
            
        Returns:
            Path to exported file
        """
        output_file = self.output_dir / f"{self.repo_name}_report.html"
        
        html_content = self._generate_html(results)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(output_file)
    
    def _generate_html(self, results: Dict[str, Any]) -> str:
        """Generate HTML content"""
        repo = results.get('repository', {})
        sbom = results.get('sbom', {})
        cost = results.get('cost_analysis', {})
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Repository Analysis: {self.repo_name}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .card h3 {{
            margin-top: 0;
            color: #667eea;
        }}
        .metric {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
            margin: 10px 0;
        }}
        .section {{
            background: white;
            padding: 25px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #667eea;
            color: white;
            font-weight: 600;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: 500;
            background-color: #e7e7e7;
            color: #333;
            margin: 2px;
        }}
        .highlight {{
            background-color: #fef3cd;
            padding: 15px;
            border-left: 4px solid #f0ad4e;
            border-radius: 4px;
            margin: 15px 0;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Repository Analysis Report</h1>
        <h2>{repo.get('name', 'Unknown')}</h2>
        <p>{repo.get('info', {}).get('description', 'No description')}</p>
        <p><strong>URL:</strong> {repo.get('url', 'N/A')}</p>
        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>

    <div class="highlight">
        <h3>📝 Summary: Dependencies → Commits → Cost Correlation</h3>
        <p><strong>Ratio:</strong> {sbom.get('total_dependencies', 0)} dependencies across {cost.get('total_commits', 0)} commits by {cost.get('total_contributors', 0)} contributors</p>
        <p><strong>Analysis:</strong> ${cost.get('estimated_cost', 0):,.2f} estimated development cost ({cost.get('estimated_hours', 0):,.1f} hours)</p>
    </div>

    <div class="summary">
        <div class="card">
            <h3>📦 Dependencies</h3>
            <div class="metric">{sbom.get('total_dependencies', 0)}</div>
            <p>{len(sbom.get('package_managers', []))} package managers</p>
        </div>
        
        <div class="card">
            <h3>💾 Commits</h3>
            <div class="metric">{cost.get('total_commits', 0):,}</div>
            <p>{cost.get('commits_per_dependency', 0):.1f} per dependency</p>
        </div>
        
        <div class="card">
            <h3>👥 Contributors</h3>
            <div class="metric">{cost.get('total_contributors', 0)}</div>
            <p>Active developers</p>
        </div>
        
        <div class="card">
            <h3>💰 Estimated Cost</h3>
            <div class="metric">${cost.get('estimated_cost', 0):,.0f}</div>
            <p>${cost.get('cost_per_dependency', 0):.2f} per dependency</p>
        </div>
    </div>

    <div class="section">
        <h2>🏗️ Project Information</h2>
        <p><strong>Project Types:</strong> {', '.join(sbom.get('project_types', ['unknown']))}</p>
        <p><strong>Package Managers:</strong> 
            {' '.join([f'<span class="badge">{pm}</span>' for pm in sbom.get('package_managers', ['none'])])}
        </p>
        <p><strong>Total Lines of Code (est):</strong> {cost.get('estimated_loc', 0):,}</p>
        <p><strong>Estimated Development Time:</strong> {cost.get('estimated_hours', 0):,.1f} hours ({cost.get('effort_months', 0):.1f} months)</p>
    </div>

    <div class="section">
        <h2>📦 Dependencies ({sbom.get('total_dependencies', 0)})</h2>
        <table>
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Version</th>
                    <th>Type</th>
                    <th>Package Manager</th>
                </tr>
            </thead>
            <tbody>
                {self._generate_dependency_rows(sbom.get('dependencies', []))}
            </tbody>
        </table>
    </div>

    <div class="section">
        <h2>📊 Cost Analysis (COCOMO II)</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>Value</th>
            </tr>
            <tr>
                <td>Total Commits</td>
                <td>{cost.get('total_commits', 0):,}</td>
            </tr>
            <tr>
                <td>Total Contributors</td>
                <td>{cost.get('total_contributors', 0)}</td>
            </tr>
            <tr>
                <td>Estimated LOC</td>
                <td>{cost.get('estimated_loc', 0):,}</td>
            </tr>
            <tr>
                <td>Estimated KLOC</td>
                <td>{cost.get('estimated_kloc', 0):.2f}</td>
            </tr>
            <tr>
                <td>Effort (months)</td>
                <td>{cost.get('effort_months', 0):.2f}</td>
            </tr>
            <tr>
                <td>Estimated Hours</td>
                <td>{cost.get('estimated_hours', 0):,.2f}</td>
            </tr>
            <tr>
                <td>Hourly Rate</td>
                <td>${cost.get('hourly_rate', 0):.2f}</td>
            </tr>
            <tr>
                <td><strong>Total Estimated Cost</strong></td>
                <td><strong>${cost.get('estimated_cost', 0):,.2f}</strong></td>
            </tr>
        </table>
    </div>

    <div class="section">
        <p style="text-align: center; color: #999; font-size: 0.9em;">
            Generated by Universal Repository Analyzer v2.0.0
        </p>
    </div>
</body>
</html>"""
    
    def _generate_dependency_rows(self, dependencies: list) -> str:
        """Generate HTML table rows for dependencies"""
        if not dependencies:
            return '<tr><td colspan="4">No dependencies found</td></tr>'
        
        rows = []
        for dep in dependencies[:100]:  # Limit to first 100 for HTML
            rows.append(f"""
                <tr>
                    <td>{dep.get('name', 'Unknown')}</td>
                    <td>{dep.get('version', 'N/A')}</td>
                    <td>{dep.get('type', 'unknown')}</td>
                    <td><span class="badge">{dep.get('package_manager', 'unknown')}</span></td>
                </tr>
            """)
        
        if len(dependencies) > 100:
            rows.append(f'<tr><td colspan="4"><em>... and {len(dependencies) - 100} more</em></td></tr>')
        
        return '\n'.join(rows)
