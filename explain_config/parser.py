"""YAML parser module for EDOT Collector configurations."""

import sys
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigParser:
    """Parse and validate YAML configuration files."""

    @staticmethod
    def parse_file(file_path: str) -> Dict[str, Any]:
        """
        Parse YAML from a file path.
        
        Args:
            file_path: Path to the YAML file
            
        Returns:
            Parsed YAML as a dictionary
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            yaml.YAMLError: If the YAML is invalid
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {file_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            return ConfigParser.parse_string(f.read())

    @staticmethod
    def parse_stdin() -> Dict[str, Any]:
        """
        Parse YAML from stdin.
        
        Returns:
            Parsed YAML as a dictionary
            
        Raises:
            yaml.YAMLError: If the YAML is invalid
            ValueError: If stdin is empty
        """
        content = sys.stdin.read()
        if not content.strip():
            raise ValueError("No input provided via stdin")
        return ConfigParser.parse_string(content)

    @staticmethod
    def parse_string(content: str) -> Dict[str, Any]:
        """
        Parse YAML from a string.
        
        Args:
            content: YAML content as a string
            
        Returns:
            Parsed YAML as a dictionary
            
        Raises:
            yaml.YAMLError: If the YAML is invalid
            ValueError: If content is empty
        """
        if not content or not content.strip():
            raise ValueError("Empty YAML content provided")
        
        try:
            data = yaml.safe_load(content)
            if data is None:
                raise ValueError("YAML file is empty or contains only comments")
            if not isinstance(data, dict):
                raise ValueError("YAML root must be a dictionary/mapping")
            return data
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Invalid YAML: {str(e)}")

    @staticmethod
    def validate_otel_config(config: Dict[str, Any]) -> bool:
        """
        Basic validation to check if this looks like an OTel/EDOT Collector config.
        
        Args:
            config: Parsed YAML configuration
            
        Returns:
            True if it looks like a valid OTel config
        """
        # OTel Collector configs typically have at least one of these sections
        valid_sections = {'receivers', 'processors', 'exporters', 'extensions', 'service'}
        return bool(set(config.keys()) & valid_sections)

