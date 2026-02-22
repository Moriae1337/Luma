import json
import pytest
from core.config_manager import ConfigManager


class TestConfigManager:
    """Test cases for ConfigManager."""
    
    @pytest.fixture
    def temp_config_file(self, tmp_path):
        """Create a temporary config file path."""
        return str(tmp_path / "test_config.json")
    
    @pytest.fixture
    def config_manager(self, temp_config_file):
        """Create a ConfigManager instance with temp config file."""
        return ConfigManager(config_file=temp_config_file)
    
    def test_initialization(self, config_manager):
        """Test ConfigManager initialization."""
        assert config_manager.config_file is not None
        assert config_manager._config == {}
    
    def test_load_nonexistent_file(self, config_manager):
        """Test loading from non-existent file."""
        config = config_manager.load()
        assert config == {}
    
    def test_save_and_load(self, config_manager):
        """Test saving and loading configuration."""
        test_config = {
            "api_key": "test_key_123",
            "provider": "gemini",
            "setting": "value"
        }
        
        # Save config
        result = config_manager.save(test_config)
        assert result is True
        
        # Load config
        loaded_config = config_manager.load()
        assert loaded_config == test_config
    
    def test_get_existing_value(self, config_manager):
        """Test getting an existing value."""
        config_manager._config = {"test_key": "test_value"}
        value = config_manager.get("test_key")
        assert value == "test_value"
    
    def test_set_value(self, config_manager):
        """Test setting a configuration value."""
        config_manager.set("new_key", "new_value")
        assert config_manager._config["new_key"] == "new_value"
    
    def test_update_config(self, config_manager):
        """Test updating configuration with dictionary."""
        config_manager._config = {"key1": "value1"}
        config_manager.update({"key2": "value2", "key3": "value3"})
        
        assert config_manager._config["key1"] == "value1"
        assert config_manager._config["key2"] == "value2"
        assert config_manager._config["key3"] == "value3"
    
    def test_update_overwrites_existing(self, config_manager):
        """Test that update overwrites existing keys."""
        config_manager._config = {"key1": "old_value"}
        config_manager.update({"key1": "new_value"})
        
        assert config_manager._config["key1"] == "new_value"
    
    def test_load_existing_file(self, temp_config_file):
        """Test loading from existing file."""
        # Create a config file
        test_config = {"api_key": "test_key", "setting": "value"}
        with open(temp_config_file, "w") as f:
            json.dump(test_config, f)
        
        # Load it
        manager = ConfigManager(config_file=temp_config_file)
        loaded = manager.load()
        assert loaded == test_config
