"""JSON report exporter"""
import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime


class JSONExporter:
    """Export analysis results to JSON format"""
    
    def __init__(self, output_dir: str, repo_name: str):
        """
        Initialize JSON exporter
        
        Args:
            output_dir: Output directory path
            repo_name: Repository name
        """
        self.output_dir = Path(output_dir)
        self.repo_name = repo_name
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export(self, results: Dict[str, Any]) -> str:
        """
        Export results to JSON file
        
        Args:
            results: Analysis results dictionary
            
        Returns:
            Path to exported file
        """
        output_file = self.output_dir / f"{self.repo_name}_report.json"
        
        # Add comprehensive summary
        summary = self._create_summary(results)
        
        export_data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'repository': results['repository']['name'],
                'version': '2.0.0'
            },
            'summary': summary,
            'repository': results['repository'],
            'sbom': results['sbom'],
            'cost_analysis': results['cost_analysis']
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        return str(output_file)
    
    def _create_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create comprehensive summary section
        
        Args:
            results: Full analysis results
            
        Returns:
            Summary dictionary
        """
        sbom = results.get('sbom', {})
        cost = results.get('cost_analysis', {})
        
        return {
            'total_dependencies': sbom.get('total_dependencies', 0),
            'total_commits': cost.get('total_commits', 0),
            'total_contributors': cost.get('total_contributors', 0),
            'project_types': sbom.get('project_types', []),
            'package_managers': sbom.get('package_managers', []),
            'estimated_cost': cost.get('estimated_cost', 0),
            'estimated_hours': cost.get('estimated_hours', 0),
            'cost_per_dependency': cost.get('cost_per_dependency', 0),
            'commits_per_dependency': cost.get('commits_per_dependency', 0),
            'dependencies_commits_ratio': f"{sbom.get('total_dependencies', 0)}:{cost.get('total_commits', 0)}"
        }
