"""Rust Cargo.toml parser"""
try:
    import toml
except ImportError:
    toml = None

from typing import List, Dict, Any


class CargoParser:
    """Parser for Cargo.toml files"""
    
    def parse(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse Cargo.toml file
        
        Args:
            file_path: Path to Cargo.toml
            
        Returns:
            List of dependency dictionaries
        """
        dependencies = []
        
        if toml is None:
            print("Warning: toml package not installed, cannot parse Cargo.toml")
            return dependencies
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                cargo_data = toml.load(f)
            
            # Parse regular dependencies
            deps = cargo_data.get('dependencies', {})
            for name, spec in deps.items():
                version = spec if isinstance(spec, str) else spec.get('version', 'latest')
                
                dependency = {
                    'name': name,
                    'version': version,
                    'type': 'cargo-crate',
                    'source': 'crates.io',
                    'purl': f'pkg:cargo/{name}@{version}'
                }
                dependencies.append(dependency)
            
            # Parse dev dependencies
            dev_deps = cargo_data.get('dev-dependencies', {})
            for name, spec in dev_deps.items():
                version = spec if isinstance(spec, str) else spec.get('version', 'latest')
                
                dependency = {
                    'name': name,
                    'version': version,
                    'scope': 'development',
                    'type': 'cargo-crate',
                    'source': 'crates.io',
                    'purl': f'pkg:cargo/{name}@{version}'
                }
                dependencies.append(dependency)
        
        except Exception as e:
            print(f"Error parsing Cargo.toml: {e}")
        
        return dependencies
