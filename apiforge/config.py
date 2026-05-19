"""
Configuration module for APIForge
Handles configuration loading, validation, and management
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime


@dataclass
class ServerConfig:
    """Mock server configuration"""
    host: str = "127.0.0.1"
    port: int = 8080
    debug: bool = False
    auto_reload: bool = True
    cors_enabled: bool = True
    timeout: int = 30

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MockConfig:
    """Mock behavior configuration"""
    latency_min: int = 0
    latency_max: int = 0
    error_rate: float = 0.0
    error_codes: list = field(default_factory=lambda: [400, 401, 403, 404, 500])
    fallback_enabled: bool = True
    dynamic_responses: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RecorderConfig:
    """API recorder configuration"""
    storage_path: str = "./recordings"
    format: str = "json"  # json, yaml, har
    auto_save: bool = True
    max_size_mb: int = 100
    compression: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class GeneratorConfig:
    """Mock generator configuration"""
    template_dir: str = "./templates"
    validation_enabled: bool = True
    ai_enhanced: bool = False
    preserve_types: bool = True
    null_probability: float = 0.1

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class GlobalConfig:
    """Global APIForge configuration"""
    version: str = "1.0.0"
    log_level: str = "INFO"
    config_file: Optional[str] = None
    server: ServerConfig = field(default_factory=ServerConfig)
    mock: MockConfig = field(default_factory=MockConfig)
    recorder: RecorderConfig = field(default_factory=RecorderConfig)
    generator: GeneratorConfig = field(default_factory=GeneratorConfig)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "log_level": self.log_level,
            "config_file": self.config_file,
            "server": self.server.to_dict(),
            "mock": self.mock.to_dict(),
            "recorder": self.recorder.to_dict(),
            "generator": self.generator.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GlobalConfig":
        """Create config from dictionary"""
        config = cls()
        config.version = data.get("version", config.version)
        config.log_level = data.get("log_level", config.log_level)
        config.config_file = data.get("config_file", config.config_file)
        
        if "server" in data:
            config.server = ServerConfig(**data["server"])
        if "mock" in data:
            config.mock = MockConfig(**data["mock"])
        if "recorder" in data:
            config.recorder = RecorderConfig(**data["recorder"])
        if "generator" in data:
            config.generator = GeneratorConfig(**data["generator"])
        
        return config


class ConfigManager:
    """Manages APIForge configuration"""
    
    DEFAULT_CONFIG_NAME = "apiforge.yaml"
    CONFIG_DIRS = [
        Path.cwd(),
        Path.home() / ".apiforge",
        Path("/etc/apiforge"),
    ]

    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file
        self.config = GlobalConfig()
        self._load_config()

    def _load_config(self):
        """Load configuration from file or use defaults"""
        if self.config_file and Path(self.config_file).exists():
            self._load_from_file(self.config_file)
        else:
            for config_dir in self.CONFIG_DIRS:
                config_path = config_dir / self.DEFAULT_CONFIG_NAME
                if config_path.exists():
                    self._load_from_file(str(config_path))
                    break

    def _load_from_file(self, filepath: str):
        """Load configuration from YAML or JSON file"""
        filepath = Path(filepath)
        
        with open(filepath, "r", encoding="utf-8") as f:
            if filepath.suffix in [".yaml", ".yml"]:
                data = yaml.safe_load(f)
            elif filepath.suffix == ".json":
                data = json.load(f)
            else:
                raise ValueError(f"Unsupported config file format: {filepath.suffix}")
        
        self.config = GlobalConfig.from_dict(data)
        self.config.config_file = filepath

    def save(self, filepath: Optional[str] = None):
        """Save configuration to file"""
        save_path = Path(filepath) if filepath else Path.cwd() / self.DEFAULT_CONFIG_NAME
        
        with open(save_path, "w", encoding="utf-8") as f:
            if save_path.suffix in [".yaml", ".yml"]:
                yaml.dump(self.config.to_dict(), f, default_flow_style=False)
            elif save_path.suffix == ".json":
                json.dump(self.config.to_dict(), f, indent=2)
            else:
                yaml.dump(self.config.to_dict(), f, default_flow_style=False)

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key"""
        keys = key.split(".")
        value = self.config.to_dict()
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value

    def set(self, key: str, value: Any):
        """Set configuration value by key"""
        keys = key.split(".")
        config_dict = self.config.to_dict()
        
        current = config_dict
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value
        self.config = GlobalConfig.from_dict(config_dict)

    def update(self, updates: Dict[str, Any]):
        """Update configuration with dictionary"""
        config_dict = self.config.to_dict()
        self._deep_update(config_dict, updates)
        self.config = GlobalConfig.from_dict(config_dict)

    def _deep_update(self, base: Dict, updates: Dict):
        """Deep update dictionary"""
        for key, value in updates.items():
            if isinstance(value, dict) and key in base and isinstance(base[key], dict):
                self._deep_update(base[key], value)
            else:
                base[key] = value
