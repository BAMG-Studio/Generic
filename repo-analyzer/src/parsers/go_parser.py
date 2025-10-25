"""Go modules parser"""
import re
from typing import List, Dict, Any


class GoParser:
    """Parser for go.mod files"""
    
    def parse(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse go.mod file
        
        Args:
            file_path: Path to go.mod
            
        Returns:
            List of dependency dictionaries
        """
        dependencies = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse require statements
            # Format: require module/path v1.2.3
            in_require_block = False
            
            for line in content.split('\n'):
                line = line.strip()
                
                # Check for require block
                if line.startswith('require ('):
                    in_require_block = True
                    continue
                
                if in_require_block and line == ')':
                    in_require_block = False
                    continue
                
                # Parse single require or require block entry
                if line.startswith('require ') or in_require_block:
                    match = re.match(r'require\s+([^\s]+)\s+([^\s]+)', line)
                    if not match and in_require_block:
                        match = re.match(r'([^\s]+)\s+([^\s]+)', line)
                    
                    if match:
                        module_path = match.group(1)
                        version = match.group(2)
                        
                        dependency = {
                            'name': module_path,
                            'version': version,
                            'type': 'go-module',
                            'source': 'go',
                            'purl': f'pkg:golang/{module_path}@{version}'
                        }
                        dependencies.append(dependency)
        
        except Exception as e:
            print(f"Error parsing go.mod: {e}")
        
        return dependencies
