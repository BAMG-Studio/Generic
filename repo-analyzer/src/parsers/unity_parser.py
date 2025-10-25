"""Unity Package Manager (UPM) parser"""
import json
from typing import List, Dict, Any
from pathlib import Path


class UnityParser:
    """Parser for Unity Packages/manifest.json"""
    
    def parse(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse Unity manifest.json file
        
        Args:
            file_path: Path to Packages/manifest.json
            
        Returns:
            List of dependency dictionaries
        """
        dependencies = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            # Parse dependencies section
            deps = manifest.get('dependencies', {})
            
            for package_name, version in deps.items():
                dependency = {
                    'name': package_name,
                    'version': version,
                    'type': 'unity-package',
                    'source': 'upm',
                    'purl': f'pkg:unity/{package_name}@{version}'
                }
                dependencies.append(dependency)
        
        except Exception as e:
            print(f"Error parsing Unity manifest: {e}")
        
        return dependencies
