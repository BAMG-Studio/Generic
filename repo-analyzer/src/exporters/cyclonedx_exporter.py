"""CycloneDX SBOM exporter"""
import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom


class CycloneDXExporter:
    """Export SBOM in CycloneDX format (JSON and XML)"""
    
    CYCLONEDX_VERSION = "1.4"
    SPEC_VERSION = "1.4"
    
    def __init__(self, output_dir: str, repo_name: str):
        """
        Initialize CycloneDX exporter
        
        Args:
            output_dir: Output directory path
            repo_name: Repository name
        """
        self.output_dir = Path(output_dir)
        self.repo_name = repo_name
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export(self, results: Dict[str, Any]) -> str:
        """
        Export SBOM in both JSON and XML formats
        
        Args:
            results: Analysis results dictionary
            
        Returns:
            Path to JSON SBOM file
        """
        # Generate CycloneDX data
        cyclonedx_data = self._generate_cyclonedx(results)
        
        # Export JSON
        json_file = self.output_dir / f"{self.repo_name}_sbom.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(cyclonedx_data, f, indent=2, ensure_ascii=False)
        
        # Export XML
        xml_file = self.output_dir / f"{self.repo_name}_sbom.xml"
        xml_content = self._generate_xml(cyclonedx_data)
        with open(xml_file, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        return str(json_file)
    
    def _generate_cyclonedx(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate CycloneDX SBOM structure"""
        repo = results.get('repository', {})
        sbom = results.get('sbom', {})
        dependencies = sbom.get('dependencies', [])
        
        # Create components list
        components = []
        for dep in dependencies:
            component = {
                "type": "library",
                "name": dep.get('name', 'unknown'),
                "version": dep.get('version', ''),
                "purl": dep.get('purl', '')
            }
            
            # Add group for Java dependencies
            if dep.get('group_id'):
                component['group'] = dep.get('group_id')
            
            # Add scope if available
            if dep.get('scope'):
                component['scope'] = dep.get('scope')
            
            components.append(component)
        
        # Build CycloneDX structure
        cyclonedx = {
            "bomFormat": "CycloneDX",
            "specVersion": self.SPEC_VERSION,
            "serialNumber": f"urn:uuid:{self._generate_uuid()}",
            "version": 1,
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "tools": [
                    {
                        "vendor": "Universal Repository Analyzer",
                        "name": "repo-analyzer",
                        "version": "2.0.0"
                    }
                ],
                "component": {
                    "type": "application",
                    "name": repo.get('name', 'unknown'),
                    "version": "1.0.0",
                    "description": repo.get('info', {}).get('description', ''),
                }
            },
            "components": components
        }
        
        return cyclonedx
    
    def _generate_xml(self, cyclonedx_data: Dict[str, Any]) -> str:
        """Generate XML representation of CycloneDX SBOM"""
        # Create root element
        root = ET.Element('bom', {
            'xmlns': 'http://cyclonedx.org/schema/bom/1.4',
            'serialNumber': cyclonedx_data.get('serialNumber', ''),
            'version': str(cyclonedx_data.get('version', 1))
        })
        
        # Metadata
        metadata = ET.SubElement(root, 'metadata')
        timestamp = ET.SubElement(metadata, 'timestamp')
        timestamp.text = cyclonedx_data.get('metadata', {}).get('timestamp', '')
        
        # Tools
        tools = ET.SubElement(metadata, 'tools')
        for tool_data in cyclonedx_data.get('metadata', {}).get('tools', []):
            tool = ET.SubElement(tools, 'tool')
            vendor = ET.SubElement(tool, 'vendor')
            vendor.text = tool_data.get('vendor', '')
            name = ET.SubElement(tool, 'name')
            name.text = tool_data.get('name', '')
            version = ET.SubElement(tool, 'version')
            version.text = tool_data.get('version', '')
        
        # Component
        component_data = cyclonedx_data.get('metadata', {}).get('component', {})
        component = ET.SubElement(metadata, 'component', {'type': component_data.get('type', 'application')})
        comp_name = ET.SubElement(component, 'name')
        comp_name.text = component_data.get('name', '')
        comp_version = ET.SubElement(component, 'version')
        comp_version.text = component_data.get('version', '')
        if component_data.get('description'):
            comp_desc = ET.SubElement(component, 'description')
            comp_desc.text = component_data.get('description', '')
        
        # Components
        components = ET.SubElement(root, 'components')
        for comp_data in cyclonedx_data.get('components', []):
            comp = ET.SubElement(components, 'component', {'type': comp_data.get('type', 'library')})
            
            if comp_data.get('group'):
                group = ET.SubElement(comp, 'group')
                group.text = comp_data.get('group', '')
            
            name = ET.SubElement(comp, 'name')
            name.text = comp_data.get('name', '')
            
            version = ET.SubElement(comp, 'version')
            version.text = comp_data.get('version', '')
            
            if comp_data.get('purl'):
                purl = ET.SubElement(comp, 'purl')
                purl.text = comp_data.get('purl', '')
        
        # Pretty print XML
        xml_str = ET.tostring(root, encoding='unicode')
        dom = minidom.parseString(xml_str)
        return dom.toprettyxml(indent="  ")
    
    def _generate_uuid(self) -> str:
        """Generate a UUID for the BOM"""
        import uuid
        return str(uuid.uuid4())
