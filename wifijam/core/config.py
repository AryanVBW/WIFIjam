"""
Configuration management for WIFIjam.
Handles loading, saving, and validating application configuration.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, asdict, field

from wifijam.core.logger import get_logger
from wifijam.core.exceptions import ConfigurationError

logger = get_logger(__name__)


@dataclass
class AttackConfig:
    """Attack-related configuration."""
    default_packet_count: int = 100
    default_delay_ms: int = 100
    max_packet_count: int = 10000
    min_delay_ms: int = 10
    auto_save_logs: bool = True


@dataclass
class ScanConfig:
    """Scanning-related configuration."""
    default_duration: int = 30
    channel_hopping: bool = True
    save_results: bool = True
    update_interval: int = 5


@dataclass
class InterfaceConfig:
    """Network interface configuration."""
    primary_interface: Optional[str] = None
    auto_detect: bool = True
    monitor_mode_enabled: bool = False


@dataclass
class ServerConfig:
    """API server configuration."""
    host: str = "127.0.0.1"
    port: int = 8080
    cors_enabled: bool = True
    websocket_enabled: bool = True


@dataclass
class UIConfig:
    """User interface configuration."""
    theme: str = "dark"
    real_time_updates: bool = True
    sound_notifications: bool = False
    update_interval_ms: int = 1000


class Config:
    """Main configuration class for WIFIjam."""
    
    DEFAULT_CONFIG_DIR = Path.home() / ".wifijam"
    DEFAULT_CONFIG_FILE = "config.json"
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize configuration.
        
        Args:
            config_path: Optional path to configuration file
        """
        self.config_path = config_path or (self.DEFAULT_CONFIG_DIR / self.DEFAULT_CONFIG_FILE)
        self.config_dir = self.config_path.parent
        
        # Initialize configuration sections
        self.attack = AttackConfig()
        self.scan = ScanConfig()
        self.interface = InterfaceConfig()
        self.server = ServerConfig()
        self.ui = UIConfig()
        
        # Application metadata
        self.version = "2.0.0"
        self.log_level = "INFO"
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Load configuration if exists
        if self.config_path.exists():
            self.load()
        else:
            logger.info(f"No configuration file found. Using defaults.")
            self.save()
    
    def load(self) -> None:
        """Load configuration from file."""
        try:
            with open(self.config_path, 'r') as f:
                data = json.load(f)
            
            # Load each section
            if 'attack' in data:
                self.attack = AttackConfig(**data['attack'])
            if 'scan' in data:
                self.scan = ScanConfig(**data['scan'])
            if 'interface' in data:
                self.interface = InterfaceConfig(**data['interface'])
            if 'server' in data:
                self.server = ServerConfig(**data['server'])
            if 'ui' in data:
                self.ui = UIConfig(**data['ui'])
            
            # Load metadata
            self.log_level = data.get('log_level', 'INFO')
            
            logger.info(f"Configuration loaded from {self.config_path}")
        
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise ConfigurationError(f"Failed to load configuration: {e}")
    
    def save(self) -> None:
        """Save configuration to file."""
        try:
            data = {
                'version': self.version,
                'log_level': self.log_level,
                'attack': asdict(self.attack),
                'scan': asdict(self.scan),
                'interface': asdict(self.interface),
                'server': asdict(self.server),
                'ui': asdict(self.ui),
            }
            
            with open(self.config_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Configuration saved to {self.config_path}")
        
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            raise ConfigurationError(f"Failed to save configuration: {e}")
    
    def reset(self) -> None:
        """Reset configuration to defaults."""
        self.attack = AttackConfig()
        self.scan = ScanConfig()
        self.interface = InterfaceConfig()
        self.server = ServerConfig()
        self.ui = UIConfig()
        self.log_level = "INFO"
        
        self.save()
        logger.info("Configuration reset to defaults")
    
    def update(self, section: str, **kwargs) -> None:
        """
        Update configuration section.
        
        Args:
            section: Configuration section name
            **kwargs: Configuration values to update
        """
        if section == 'attack':
            for key, value in kwargs.items():
                if hasattr(self.attack, key):
                    setattr(self.attack, key, value)
        elif section == 'scan':
            for key, value in kwargs.items():
                if hasattr(self.scan, key):
                    setattr(self.scan, key, value)
        elif section == 'interface':
            for key, value in kwargs.items():
                if hasattr(self.interface, key):
                    setattr(self.interface, key, value)
        elif section == 'server':
            for key, value in kwargs.items():
                if hasattr(self.server, key):
                    setattr(self.server, key, value)
        elif section == 'ui':
            for key, value in kwargs.items():
                if hasattr(self.ui, key):
                    setattr(self.ui, key, value)
        else:
            raise ConfigurationError(f"Unknown configuration section: {section}")
        
        self.save()
        logger.info(f"Configuration section '{section}' updated")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'version': self.version,
            'log_level': self.log_level,
            'attack': asdict(self.attack),
            'scan': asdict(self.scan),
            'interface': asdict(self.interface),
            'server': asdict(self.server),
            'ui': asdict(self.ui),
        }

