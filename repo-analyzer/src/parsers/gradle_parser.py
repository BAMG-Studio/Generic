"""Gradle build file parser"""
import re
from typing import List, Dict, Any


class GradleParser:
    """Parser for Gradle build files"""
    
    def parse(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse Gradle build file
        
        Args:
            file_path: Path to build.gradle or build.gradle.kts
            
        Returns:
            List of dependency dictionaries
        """
        dependencies = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Match dependency declarations
            # Format: implementation 'group:artifact:version'
            # or compile('group:artifact:version')
            patterns = [
                r'(implementation|compile|api|testImplementation|runtimeOnly)\s+["\']([^:]+):([^:]+):([^"\']+)["\']',
                r'(implementation|compile|api|testImplementation|runtimeOnly)\s*\(["\']([^:]+):([^:]+):([^"\']+)["\']\)',
            ]
            
            for pattern in patterns:
                for match in re.finditer(pattern, content):
                    scope = match.group(1)
                    group_id = match.group(2)
                    artifact_id = match.group(3)
                    version = match.group(4)
                    
                    name = f"{group_id}:{artifact_id}"
                    
                    dependency = {
                        'name': name,
                        'group_id': group_id,
                        'artifact_id': artifact_id,
                        'version': version,
                        'scope': scope,
                        'type': 'gradle-dependency',
                        'source': 'maven',
                        'purl': f'pkg:maven/{group_id}/{artifact_id}@{version}'
                    }
                    dependencies.append(dependency)
        
        except Exception as e:
            print(f"Error parsing Gradle file: {e}")
        
        return dependencies
