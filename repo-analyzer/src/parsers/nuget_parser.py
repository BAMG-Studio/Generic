""".NET NuGet package parser"""
import xml.etree.ElementTree as ET
from typing import List, Dict, Any


class NuGetParser:
    """Parser for .csproj and packages.config files"""
    
    def parse(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse .NET project file
        
        Args:
            file_path: Path to .csproj or packages.config
            
        Returns:
            List of dependency dictionaries
        """
        dependencies = []
        
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # For .csproj files (PackageReference style)
            for pkg_ref in root.findall('.//PackageReference'):
                name = pkg_ref.get('Include')
                version = pkg_ref.get('Version', 'latest')
                
                if name:
                    dependency = {
                        'name': name,
                        'version': version,
                        'type': 'nuget-package',
                        'source': 'nuget',
                        'purl': f'pkg:nuget/{name}@{version}'
                    }
                    dependencies.append(dependency)
            
            # For packages.config files
            for package in root.findall('.//package'):
                name = package.get('id')
                version = package.get('version', 'latest')
                
                if name:
                    dependency = {
                        'name': name,
                        'version': version,
                        'type': 'nuget-package',
                        'source': 'nuget',
                        'purl': f'pkg:nuget/{name}@{version}'
                    }
                    dependencies.append(dependency)
        
        except Exception as e:
            print(f"Error parsing .NET project file: {e}")
        
        return dependencies
