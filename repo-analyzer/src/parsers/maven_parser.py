"""Maven pom.xml parser"""
import xml.etree.ElementTree as ET
from typing import List, Dict, Any


class MavenParser:
    """Parser for Maven pom.xml"""
    
    def parse(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse Maven pom.xml file
        
        Args:
            file_path: Path to pom.xml
            
        Returns:
            List of dependency dictionaries
        """
        dependencies = []
        
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Maven uses namespaces
            ns = {'mvn': 'http://maven.apache.org/POM/4.0.0'}
            
            # Find all dependencies
            for dep in root.findall('.//mvn:dependency', ns):
                group_id = dep.find('mvn:groupId', ns)
                artifact_id = dep.find('mvn:artifactId', ns)
                version = dep.find('mvn:version', ns)
                scope = dep.find('mvn:scope', ns)
                
                if group_id is not None and artifact_id is not None:
                    name = f"{group_id.text}:{artifact_id.text}"
                    ver = version.text if version is not None else 'LATEST'
                    scp = scope.text if scope is not None else 'compile'
                    
                    dependency = {
                        'name': name,
                        'group_id': group_id.text,
                        'artifact_id': artifact_id.text,
                        'version': ver,
                        'scope': scp,
                        'type': 'maven-artifact',
                        'source': 'maven',
                        'purl': f'pkg:maven/{group_id.text}/{artifact_id.text}@{ver}'
                    }
                    dependencies.append(dependency)
        
        except Exception as e:
            print(f"Error parsing pom.xml: {e}")
        
        return dependencies
