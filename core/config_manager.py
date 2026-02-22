import json
import os
from typing import Any
from constants import CONFIG_FILE


class ConfigManager:
    """Manages application configuration."""
    
    def __init__(self, config_file: str = CONFIG_FILE):
        self.config_file = config_file
        self._config: dict[str, Any] = {}
    
    def load(self) -> dict[str, Any]:
        """Load configuration from file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r") as f:
                    self._config = json.load(f)
            else:
                self._config = {}
        except Exception as e:
            print(f"Could not load config: {str(e)}")
            self._config = {}
        
        return self._config
    
    def save(self, config: dict[str, Any]) -> bool:
        """Save configuration to file."""
        try:
            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            print(f"Failed to save config: {str(e)}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        self._config[key] = value
    
    def update(self, config: dict[str, Any]) -> None:
        """Update configuration with new values."""
        self._config.update(config)

