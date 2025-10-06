"""
Tests for configuration module.
"""

import pytest
import tempfile
from pathlib import Path
from wifijam.core.config import Config, AttackConfig, ScanConfig


def test_config_init():
    """Test Config initialization."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.json"
        config = Config(config_path)
        
        assert config is not None
        assert config.attack is not None
        assert config.scan is not None
        assert config.interface is not None
        assert config.server is not None
        assert config.ui is not None


def test_config_save_load():
    """Test configuration save and load."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.json"
        
        # Create and save config
        config1 = Config(config_path)
        config1.attack.default_packet_count = 200
        config1.save()
        
        # Load config
        config2 = Config(config_path)
        assert config2.attack.default_packet_count == 200


def test_config_update():
    """Test configuration update."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.json"
        config = Config(config_path)
        
        config.update('attack', default_packet_count=300)
        assert config.attack.default_packet_count == 300


def test_config_reset():
    """Test configuration reset."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.json"
        config = Config(config_path)
        
        # Modify config
        config.attack.default_packet_count = 500
        
        # Reset
        config.reset()
        assert config.attack.default_packet_count == 100  # Default value


def test_config_to_dict():
    """Test configuration to dictionary conversion."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.json"
        config = Config(config_path)
        
        config_dict = config.to_dict()
        assert isinstance(config_dict, dict)
        assert 'attack' in config_dict
        assert 'scan' in config_dict
        assert 'version' in config_dict

