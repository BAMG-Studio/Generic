"""Python pip requirements parser"""
import re
from typing import List, Dict, Any


class PipParser:
    """Parser for requirements.txt and other Python dependency files"""
    
    def parse(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse Python requirements file
        
        Args:
            file_path: Path to requirements file
            
        Returns:
            List of dependency dictionaries
        """
        dependencies = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    
                    # Skip comments and empty lines
                    if not line or line.startswith('#'):
                        continue
                    
                    # Skip -r includes (could enhance to follow these)
                    if line.startswith('-r ') or line.startswith('--requirement'):
                        continue
                    
                    # Parse package specification
                    # Format: package==version, package>=version, etc.
                    match = re.match(r'^([a-zA-Z0-9_\-\[\]\.]+)([><=!~]+)?(.*?)$', line)
                    
                    if match:
                        name = match.group(1)
                        operator = match.group(2) or '=='
                        version = match.group(3).strip() if match.group(3) else 'latest'
                        
                        dependency = {
                            'name': name,
                            'version': version,
                            'operator': operator,
                            'type': 'python-package',
                            'source': 'pypi',
                            'purl': f'pkg:pypi/{name}@{version}' if version != 'latest' else f'pkg:pypi/{name}'
                        }
                        dependencies.append(dependency)
        
        except Exception as e:
            print(f"Error parsing requirements file: {e}")
        
        return dependencies
