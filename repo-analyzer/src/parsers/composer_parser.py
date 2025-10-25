"""PHP Composer parser"""
import json
from typing import List, Dict, Any


class ComposerParser:
    """Parser for composer.json files"""
    
    def parse(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse composer.json file
        
        Args:
            file_path: Path to composer.json
            
        Returns:
            List of dependency dictionaries
        """
        dependencies = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                composer_data = json.load(f)
            
            # Parse dependencies
            deps = composer_data.get('require', {})
            for name, version in deps.items():
                # Skip PHP itself
                if name == 'php':
                    continue
                
                dependency = {
                    'name': name,
                    'version': version,
                    'type': 'composer-package',
                    'source': 'packagist',
                    'purl': f'pkg:composer/{name}@{version}'
                }
                dependencies.append(dependency)
            
            # Parse dev dependencies
            dev_deps = composer_data.get('require-dev', {})
            for name, version in dev_deps.items():
                dependency = {
                    'name': name,
                    'version': version,
                    'scope': 'development',
                    'type': 'composer-package',
                    'source': 'packagist',
                    'purl': f'pkg:composer/{name}@{version}'
                }
                dependencies.append(dependency)
        
        except Exception as e:
            print(f"Error parsing composer.json: {e}")
        
        return dependencies
