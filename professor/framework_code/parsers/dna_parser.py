"""
DNA Configuration Parser for GitHub Class Template Repository

This module provides functionality to read and validate the dna.yml configuration file.
The parser supports required fields validation, optional fields handling, and extensibility
for unknown keys as specified in the framework design.

Author: Framework Team
License: Follows repository license
"""

import yaml
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class DNAConfig:
    """
    Data class representing the DNA configuration structure.
    
    Attributes:
        professor_profile (str): Required. GitHub username of the professor
        theme (str): Optional. Active visual theme (default: 'default')
        search_mode (str): Optional. Search implementation mode (default: 'simple')
        index_generation (bool): Optional. Enable automatic index regeneration (default: True)
        sync_mode (str): Optional. Synchronization strategy (default: 'additive')
        authoring_tools (List[str]): Optional. Enabled authoring tools (default: ['agent'])
        license (str): Optional. Default license for content (default: 'CC-BY-4.0')
        unknown_fields (Dict[str, Any]): Any additional fields for future extensibility
    """
    
    # Required fields
    professor_profile: str
    
    # Optional fields with defaults
    theme: str = "default"
    search_mode: str = "simple"
    index_generation: bool = True
    sync_mode: str = "additive"
    authoring_tools: List[str] = field(default_factory=lambda: ["agent"])
    license: str = "CC-BY-4.0"
    
    # Extensibility support
    unknown_fields: Dict[str, Any] = field(default_factory=dict)


class DNAParserError(Exception):
    """Custom exception for DNA parser errors."""
    pass


class DNAParser:
    """
    Parser for dna.yml configuration files.
    
    Handles reading, validation, and provides access to configuration values
    with support for extensibility and clear error reporting.
    """
    
    REQUIRED_FIELDS = ["professor_profile"]
    VALID_SYNC_MODES = ["additive", "force"]
    VALID_SEARCH_MODES = ["simple", "advanced"]
    
    def __init__(self, repo_root: Optional[str] = None):
        """
        Initialize the DNA parser.
        
        Args:
            repo_root (str, optional): Path to repository root. If None, uses current directory.
        """
        self.repo_root = Path(repo_root) if repo_root else Path.cwd()
        self.dna_file_path = self.repo_root / "dna.yml"
        self._config: Optional[DNAConfig] = None
    
    def parse(self) -> DNAConfig:
        """
        Parse the dna.yml file and return a validated DNAConfig object.
        
        Returns:
            DNAConfig: Validated configuration object
            
        Raises:
            DNAParserError: If file doesn't exist, is invalid YAML, or fails validation
        """
        try:
            # Check if file exists
            if not self.dna_file_path.exists():
                raise DNAParserError(f"DNA configuration file not found: {self.dna_file_path}")
            
            # Read and parse YAML
            with open(self.dna_file_path, 'r', encoding='utf-8') as file:
                raw_data = yaml.safe_load(file)
            
            if raw_data is None:
                raise DNAParserError("DNA configuration file is empty")
            
            if not isinstance(raw_data, dict):
                raise DNAParserError("DNA configuration must be a YAML dictionary")
            
            # Validate and create config object
            config = self._validate_and_create_config(raw_data)
            self._config = config
            
            return config
            
        except yaml.YAMLError as e:
            raise DNAParserError(f"Invalid YAML in DNA configuration: {e}")
        except Exception as e:
            raise DNAParserError(f"Error parsing DNA configuration: {e}")
    
    def _validate_and_create_config(self, raw_data: Dict[str, Any]) -> DNAConfig:
        """
        Validate raw data and create DNAConfig object.
        
        Args:
            raw_data: Dictionary from parsed YAML
            
        Returns:
            DNAConfig: Validated configuration object
            
        Raises:
            DNAParserError: If validation fails
        """
        # Check required fields
        missing_required = [field for field in self.REQUIRED_FIELDS if field not in raw_data]
        if missing_required:
            raise DNAParserError(f"Missing required fields: {', '.join(missing_required)}")
        
        # Extract known fields
        known_fields = {}
        unknown_fields = {}
        
        for key, value in raw_data.items():
            if key in DNAConfig.__dataclass_fields__:
                known_fields[key] = value
            else:
                unknown_fields[key] = value
        
        # Validate specific field values
        self._validate_field_values(known_fields)
        
        # Create config object
        try:
            config = DNAConfig(**known_fields, unknown_fields=unknown_fields)
            return config
        except TypeError as e:
            raise DNAParserError(f"Configuration validation error: {e}")
    
    def _validate_field_values(self, fields: Dict[str, Any]):
        """
        Validate specific field values against allowed options.
        
        Args:
            fields: Dictionary of known fields to validate
            
        Raises:
            DNAParserError: If validation fails
        """
        # Validate sync_mode
        if "sync_mode" in fields and fields["sync_mode"] not in self.VALID_SYNC_MODES:
            raise DNAParserError(
                f"Invalid sync_mode '{fields['sync_mode']}'. "
                f"Must be one of: {', '.join(self.VALID_SYNC_MODES)}"
            )
        
        # Validate search_mode
        if "search_mode" in fields and fields["search_mode"] not in self.VALID_SEARCH_MODES:
            raise DNAParserError(
                f"Invalid search_mode '{fields['search_mode']}'. "
                f"Must be one of: {', '.join(self.VALID_SEARCH_MODES)}"
            )
        
        # Validate authoring_tools is a list
        if "authoring_tools" in fields and not isinstance(fields["authoring_tools"], list):
            raise DNAParserError("authoring_tools must be a list")
        
        # Validate index_generation is boolean
        if "index_generation" in fields and not isinstance(fields["index_generation"], bool):
            raise DNAParserError("index_generation must be a boolean value")
    
    def get_config(self) -> DNAConfig:
        """
        Get the current configuration. Parse if not already done.
        
        Returns:
            DNAConfig: Current configuration object
        """
        if self._config is None:
            self._config = self.parse()
        return self._config
    
    def get_professor_profile(self) -> str:
        """Get the professor profile (required field)."""
        return self.get_config().professor_profile
    
    def get_theme(self) -> str:
        """Get the active theme."""
        return self.get_config().theme
    
    def get_unknown_fields(self) -> Dict[str, Any]:
        """Get any unknown fields for extensibility."""
        return self.get_config().unknown_fields
    
    def has_unknown_field(self, field_name: str) -> bool:
        """Check if an unknown field exists."""
        return field_name in self.get_config().unknown_fields
    
    def get_unknown_field(self, field_name: str, default: Any = None) -> Any:
        """Get value of an unknown field, with optional default."""
        return self.get_config().unknown_fields.get(field_name, default)


def load_dna_config(repo_root: Optional[str] = None) -> DNAConfig:
    """
    Convenience function to load DNA configuration.
    
    Args:
        repo_root (str, optional): Path to repository root
        
    Returns:
        DNAConfig: Parsed and validated configuration
        
    Raises:
        DNAParserError: If parsing or validation fails
    """
    parser = DNAParser(repo_root)
    return parser.parse()


# Example usage and testing
if __name__ == "__main__":
    try:
        # Test parsing from current directory
        config = load_dna_config()
        print(f"✅ DNA Configuration loaded successfully!")
        print(f"Professor Profile: {config.professor_profile}")
        print(f"Theme: {config.theme}")
        print(f"Search Mode: {config.search_mode}")
        print(f"Index Generation: {config.index_generation}")
        print(f"Sync Mode: {config.sync_mode}")
        print(f"Authoring Tools: {config.authoring_tools}")
        print(f"License: {config.license}")
        
        if config.unknown_fields:
            print(f"Unknown fields (for future use): {config.unknown_fields}")
        
    except DNAParserError as e:
        print(f"❌ DNA Parser Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}") 