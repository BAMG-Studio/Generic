"""Ruby Bundler Gemfile parser"""
import re
from typing import List, Dict, Any


class BundlerParser:
    """Parser for Gemfile files"""
    
    def parse(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse Gemfile
        
        Args:
            file_path: Path to Gemfile
            
        Returns:
            List of dependency dictionaries
        """
        dependencies = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Match gem declarations
            # Format: gem 'name', 'version' or gem "name", "version"
            patterns = [
                r'gem\s+["\']([^"\']+)["\']\s*,\s*["\']([^"\']+)["\']',
                r'gem\s+["\']([^"\']+)["\']',
            ]
            
            for pattern in patterns:
                for match in re.finditer(pattern, content):
                    name = match.group(1)
                    version = match.group(2) if len(match.groups()) > 1 else 'latest'
                    
                    dependency = {
                        'name': name,
                        'version': version,
                        'type': 'ruby-gem',
                        'source': 'rubygems',
                        'purl': f'pkg:gem/{name}@{version}' if version != 'latest' else f'pkg:gem/{name}'
                    }
                    dependencies.append(dependency)
        
        except Exception as e:
            print(f"Error parsing Gemfile: {e}")
        
        return dependencies
