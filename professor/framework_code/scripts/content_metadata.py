"""
Content Metadata System for GitHub Class Template Framework

This module defines the metadata schema for content files and provides
parsing and validation functionality for YAML front matter.

Based on core.md section 10 specifications.
"""

import yaml
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from rich.console import Console
from rich.panel import Panel

console = Console()

# Required metadata fields based on core.md section 10
REQUIRED_FIELDS = {
    'title': str,      # Human nav & <title> tag
    'type': str,       # Styling/icon mapping  
    'date': str,       # YYYY-MM-DD format
    'author': str,     # Attribution & syllabus generation
    'summary': str     # Search snippet & cards
}

# Optional metadata fields for future enhancement
OPTIONAL_FIELDS = {
    'difficulty': ['easy', 'medium', 'hard'],
    'prerequisites': list,
    'estimated_time': int,  # minutes
    'tags': list,
    'agent': bool
}

# Valid content types for type field validation
CONTENT_TYPES = [
    'tutorial', 'documentation', 'overview', 'note', 
    'homework', 'project', 'reference', 'test'
]

# Date format pattern (YYYY-MM-DD)
DATE_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}$')

class MetadataError(Exception):
    """Custom exception for metadata validation errors"""
    pass

class MetadataParser:
    """Parser for YAML front matter in markdown files"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def parse_frontmatter(self, file_path: Path) -> Tuple[Dict[str, Any], List[str], List[str]]:
        """
        Parse YAML front matter from a markdown file.
        
        Args:
            file_path: Path to the markdown file
            
        Returns:
            Tuple of (metadata_dict, errors_list, warnings_list)
        """
        self.errors = []
        self.warnings = []
        
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            self.errors.append(f"Could not read file: {e}")
            return {}, self.errors, self.warnings
        
        # Extract YAML front matter
        if not content.startswith('---\n'):
            self.errors.append("No YAML front matter found (must start with '---')")
            return {}, self.errors, self.warnings
        
        try:
            # Find the end of front matter
            end_match = content.find('\n---\n', 4)
            if end_match == -1:
                self.errors.append("YAML front matter not properly closed (missing '---')")
                return {}, self.errors, self.warnings
            
            # Extract and parse YAML
            yaml_content = content[4:end_match]
            metadata = yaml.safe_load(yaml_content) or {}
            
        except yaml.YAMLError as e:
            self.errors.append(f"Invalid YAML syntax: {e}")
            return {}, self.errors, self.warnings
        
        # Validate the parsed metadata
        validated_metadata = self._validate_metadata(metadata)
        
        return validated_metadata, self.errors, self.warnings
    
    def _validate_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate metadata against schema requirements.
        
        Args:
            metadata: Parsed metadata dictionary
            
        Returns:
            Validated metadata dictionary
        """
        # Check required fields
        for field, expected_type in REQUIRED_FIELDS.items():
            if field not in metadata:
                self.errors.append(f"Missing required field: '{field}'")
                continue
            
            value = metadata[field]
            
            # Type validation
            if not isinstance(value, expected_type):
                self.errors.append(
                    f"Field '{field}' must be {expected_type.__name__}, got {type(value).__name__}"
                )
                continue
            
            # Special validation for specific fields
            if field == 'type':
                if value not in CONTENT_TYPES:
                    self.errors.append(
                        f"Invalid content type '{value}'. Must be one of: {', '.join(CONTENT_TYPES)}"
                    )
            
            elif field == 'date':
                if not DATE_PATTERN.match(value):
                    self.errors.append(
                        f"Date '{value}' must be in YYYY-MM-DD format"
                    )
                else:
                    # Validate it's a real date
                    try:
                        datetime.strptime(value, '%Y-%m-%d')
                    except ValueError:
                        self.errors.append(f"Invalid date '{value}' - not a valid calendar date")
        
        # Validate optional fields
        for field, validation in OPTIONAL_FIELDS.items():
            if field not in metadata:
                continue
            
            value = metadata[field]
            
            if isinstance(validation, list):
                # Enumeration validation
                if value not in validation:
                    self.errors.append(
                        f"Invalid {field} '{value}'. Must be one of: {', '.join(validation)}"
                    )
            elif isinstance(validation, type):
                # Type validation
                if not isinstance(value, validation):
                    self.errors.append(
                        f"Field '{field}' must be {validation.__name__}, got {type(value).__name__}"
                    )
        
        # Check for unknown fields (warnings only)
        all_known_fields = set(REQUIRED_FIELDS.keys()) | set(OPTIONAL_FIELDS.keys())
        for field in metadata:
            if field not in all_known_fields:
                self.warnings.append(f"Unknown field '{field}' - will be ignored")
        
        return metadata

def discover_content_files(base_dir: Path, content_dirs: List[str] = None) -> List[Path]:
    """
    Discover all markdown content files in specified directories.
    
    Args:
        base_dir: Base directory to search from
        content_dirs: List of content directories to scan
        
    Returns:
        List of Path objects for markdown files
    """
    if content_dirs is None:
        content_dirs = ['framework_tutorials', 'framework_documentation', 'class_notes']
    
    markdown_files = []
    
    for content_dir in content_dirs:
        content_path = base_dir / content_dir
        if not content_path.exists():
            continue
        
        # Find all .md files recursively
        for md_file in content_path.rglob('*.md'):
            # Skip auto-generated files
            if md_file.name.startswith('00_'):
                continue
            
            markdown_files.append(md_file)
    
    return sorted(markdown_files)

def validate_file_naming(file_path: Path) -> List[str]:
    """
    Validate file naming conventions based on core.md specifications.
    
    Args:
        file_path: Path to the file to validate
        
    Returns:
        List of error messages
    """
    errors = []
    filename = file_path.name
    
    # Check for .md extension
    if not filename.endswith('.md'):
        errors.append("Content files must have .md extension")
        return errors
    
    # Check naming pattern for content files
    # Should be: NN_descriptive_name.md or hw_NN.md
    name_without_ext = filename[:-3]
    
    if name_without_ext.startswith('hw_'):
        # Homework file - check pattern hw_NN
        if not re.match(r'^hw_\d+$', name_without_ext):
            errors.append("Homework files must follow pattern 'hw_NN.md' (e.g., hw_01.md)")
    elif re.match(r'^[A-Z]_', name_without_ext):
        # Appendix file - check pattern A_descriptive_name (capital letter prefix)
        if not re.match(r'^[A-Z]_[a-z0-9_]+$', name_without_ext):
            errors.append("Appendix files must follow pattern 'A_descriptive_name.md' with capital letter prefix")
    elif re.match(r'^\d+_', name_without_ext):
        # Primary content file - check pattern NN_descriptive_name
        if not re.match(r'^\d{2}_[a-z0-9_]+$', name_without_ext):
            errors.append("Content files must follow pattern 'NN_descriptive_name.md' with lowercase and underscores")
    else:
        # Could be code file or other - less strict
        if not re.match(r'^[a-z0-9_]+$', name_without_ext):
            errors.append("File names should use lowercase letters, numbers, and underscores only")
    
    return errors

if __name__ == "__main__":
    # Simple test when run directly
    console.print(Panel.fit("Content Metadata System", style="bold blue"))
    console.print(f"Required fields: {list(REQUIRED_FIELDS.keys())}")
    console.print(f"Optional fields: {list(OPTIONAL_FIELDS.keys())}")
    console.print(f"Valid content types: {CONTENT_TYPES}") 