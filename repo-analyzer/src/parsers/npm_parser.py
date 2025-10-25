"""NPM/Node.js package parser"""
import json
from typing import List, Dict, Any


class NPMParser:
    """Parser for package.json and lock files"""
    
    def parse(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse package.json file
        
        Args:
            file_path: Path to package.json
            
        Returns:
            List of dependency dictionaries
        """
        dependencies = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
            
            # Parse all dependency types
            dep_types = [
                ('dependencies', 'runtime'),
                ('devDependencies', 'development'),
                ('peerDependencies', 'peer'),
                ('optionalDependencies', 'optional')
            ]
            
            for dep_type, scope in dep_types:
                deps = package_data.get(dep_type, {})
                for name, version in deps.items():
                    dependency = {
                        'name': name,
                        'version': version.lstrip('^~>=<'),
                        'type': 'npm-package',
                        'scope': scope,
                        'source': 'npm',
                        'purl': f'pkg:npm/{name}@{version.lstrip("^~>=<")}'
                    }
                    dependencies.append(dependency)
        
        except Exception as e:
            print(f"Error parsing package.json: {e}")
        
        return dependencies
