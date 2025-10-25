"""Configuration management"""
import json
from pathlib import Path
from typing import Any, Dict, Optional


class Config:
    """Configuration manager for the analyzer"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config: Dict[str, Any] = self._load_defaults()
        
        if config_file:
            self._load_from_file(config_file)
    
    def _load_defaults(self) -> Dict[str, Any]:
        """Load default configuration"""
        return {
            'output_dir': './output',
            'hourly_rate': 100,
            'github_token': None,
            'gitlab_token': None,
            'include_vuln': False,
            'verbose': False,
            'output_formats': ['json', 'html', 'pdf', 'cyclonedx'],
            'cocomo_params': {
                'a': 2.94,  # COCOMO II organic mode
                'b': 1.09,
                'c': 3.67,
                'd': 0.28,
                'monthly_hours': 152  # Standard working hours per month
            }
        }
    
    def _load_from_file(self, config_file: str):
        """Load configuration from JSON file"""
        path = Path(config_file)
        if path.exists():
            with open(path, 'r') as f:
                user_config = json.load(f)
                self.config.update(user_config)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        self.config[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Export configuration as dictionary"""
        return self.config.copy()
