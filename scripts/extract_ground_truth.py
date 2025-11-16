#!/usr/bin/env python3
"""
Extract ground truth metrics from ForgeTrace audit results.

This creates expected_results.json for validation of client profiles.
"""

import argparse
import json
from pathlib import Path
from typing import Dict, Any


def extract_metrics(audit_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract key metrics from audit.json."""
    
    metrics = {
        'timestamp': audit_data.get('timestamp', 'unknown'),
        'repository_name': audit_data.get('repository_name', 'unknown'),
        
        # IP classification breakdown
        'ip_breakdown': audit_data.get('ip_breakdown', {}),
        
        # SBOM metrics
        'sbom': {
            'total_packages': len(audit_data.get('sbom', {}).get('components', [])),
            'package_types': {},
        },
        
        # License summary
        'licenses': {
            'total_licenses': len(audit_data.get('licenses', [])),
            'license_types': [lic.get('name', 'Unknown') for lic in audit_data.get('licenses', [])],
            'high_risk_count': sum(
                1 for lic in audit_data.get('licenses', [])
                if lic.get('risk', 'LOW') in ['HIGH', 'CRITICAL']
            ),
        },
        
        # Vulnerability summary
        'vulnerabilities': {
            'total_vulnerabilities': audit_data.get('vulnerability_summary', {}).get('total', 0),
            'by_severity': audit_data.get('vulnerability_summary', {}).get('by_severity', {}),
            'critical_count': audit_data.get('vulnerability_summary', {}).get('by_severity', {}).get('CRITICAL', 0),
        },
        
        # Code metrics
        'code_metrics': {
            'total_files': audit_data.get('stats', {}).get('total_files', 0),
            'total_loc': audit_data.get('stats', {}).get('total_loc', 0),
            'languages': audit_data.get('stats', {}).get('languages', {}),
        },
        
        # Secrets found
        'secrets': {
            'total_secrets': len(audit_data.get('secrets', [])),
            'secret_types': {},
        },
        
        # Similarity/provenance
        'similarity': {
            'total_matches': len(audit_data.get('similarity_matches', [])),
            'high_similarity_count': sum(
                1 for match in audit_data.get('similarity_matches', [])
                if match.get('similarity', 0) > 0.85
            ),
        },
    }
    
    # Count SBOM package types
    for component in audit_data.get('sbom', {}).get('components', []):
        pkg_type = component.get('type', 'unknown')
        metrics['sbom']['package_types'][pkg_type] = \
            metrics['sbom']['package_types'].get(pkg_type, 0) + 1
    
    # Count secret types
    for secret in audit_data.get('secrets', []):
        secret_type = secret.get('type', 'unknown')
        metrics['secrets']['secret_types'][secret_type] = \
            metrics['secrets']['secret_types'].get(secret_type, 0) + 1
    
    return metrics


def main():
    parser = argparse.ArgumentParser(
        description='Extract ground truth from audit results'
    )
    parser.add_argument(
        '--audit',
        required=True,
        help='Path to audit.json file'
    )
    parser.add_argument(
        '--output',
        required=True,
        help='Output path for expected_results.json'
    )
    
    args = parser.parse_args()
    
    audit_path = Path(args.audit)
    output_path = Path(args.output)
    
    if not audit_path.exists():
        print(f"❌ Audit file not found: {audit_path}")
        return 1
    
    print(f"📊 Extracting metrics from {audit_path}")
    
    # Load audit data
    with open(audit_path, 'r') as f:
        audit_data = json.load(f)
    
    # Extract metrics
    metrics = extract_metrics(audit_data)
    
    # Save to output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print(f"✅ Ground truth saved to {output_path}")
    print(f"\n📋 Summary:")
    print(f"   Total files: {metrics['code_metrics']['total_files']}")
    print(f"   Total LOC: {metrics['code_metrics']['total_loc']}")
    print(f"   Third-party: {metrics['ip_breakdown'].get('third_party_percentage', 'N/A')}%")
    print(f"   Foreground: {metrics['ip_breakdown'].get('foreground_percentage', 'N/A')}%")
    print(f"   Packages: {metrics['sbom']['total_packages']}")
    print(f"   Licenses: {metrics['licenses']['total_licenses']}")
    print(f"   Vulnerabilities: {metrics['vulnerabilities']['total_vulnerabilities']}")
    
    return 0


if __name__ == '__main__':
    exit(main())
