"""
Course Configuration Parser for GitHub Class Template Repository

This module provides functionality to read and validate the course.yml configuration file
that contains class offering metadata. The parser supports required fields validation,
nested data structures, and extensibility for future course-specific features.

Author: Framework Team
License: Follows repository license
"""

import yaml
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ProfessorInfo:
    """
    Data class for professor information.
    
    Attributes:
        name (str): Professor's full name
        email (str): Professor's email address
        office_hours (str): Office hours description
        office_location (str): Office location/address
    """
    name: str
    email: str
    office_hours: str
    office_location: str


@dataclass
class CourseResources:
    """
    Data class for course resources.
    
    Attributes:
        repository (str): Course repository URL
        shared_drive (str): Shared drive URL
        syllabus (str): Syllabus file name
        announcements_feed (str): Announcements file name
    """
    repository: str
    shared_drive: str
    syllabus: str
    announcements_feed: str


@dataclass
class CourseConfig:
    """
    Data class representing the course configuration structure.
    
    Attributes:
        course_name (str): Required. Full name of the course
        course_code (str): Required. Course code/identifier
        semester (str): Required. Semester and year
        professor (ProfessorInfo): Required. Professor information
        resources (CourseResources): Required. Course resources
        contact_policy (str): Required. Communication policy
        unknown_fields (Dict[str, Any]): Any additional fields for future extensibility
    """
    
    # Required fields
    course_name: str
    course_code: str
    semester: str
    professor: ProfessorInfo
    resources: CourseResources
    contact_policy: str
    
    # Extensibility support
    unknown_fields: Dict[str, Any] = field(default_factory=dict)


class CourseParserError(Exception):
    """Custom exception for course parser errors."""
    pass


class CourseParser:
    """
    Parser for course.yml configuration files.
    
    Handles reading, validation, and provides access to course metadata
    with support for extensibility and clear error reporting.
    """
    
    REQUIRED_FIELDS = [
        "course_name", "course_code", "semester", 
        "professor", "resources", "contact_policy"
    ]
    
    REQUIRED_PROFESSOR_FIELDS = ["name", "email", "office_hours", "office_location"]
    REQUIRED_RESOURCES_FIELDS = ["repository", "shared_drive", "syllabus", "announcements_feed"]
    
    def __init__(self, repo_root: Optional[str] = None, professor_dir: str = "professor"):
        """
        Initialize the course parser.
        
        Args:
            repo_root (str, optional): Path to repository root. If None, uses current directory.
            professor_dir (str): Name of professor directory (default: "professor")
        """
        self.repo_root = Path(repo_root) if repo_root else Path.cwd()
        self.course_file_path = self.repo_root / professor_dir / "course.yml"
        self._config: Optional[CourseConfig] = None
    
    def parse(self) -> CourseConfig:
        """
        Parse the course.yml file and return a validated CourseConfig object.
        
        Returns:
            CourseConfig: Validated configuration object
            
        Raises:
            CourseParserError: If file doesn't exist, is invalid YAML, or fails validation
        """
        try:
            # Check if file exists
            if not self.course_file_path.exists():
                raise CourseParserError(f"Course configuration file not found: {self.course_file_path}")
            
            # Read and parse YAML
            with open(self.course_file_path, 'r', encoding='utf-8') as file:
                raw_data = yaml.safe_load(file)
            
            if raw_data is None:
                raise CourseParserError("Course configuration file is empty")
            
            if not isinstance(raw_data, dict):
                raise CourseParserError("Course configuration must be a YAML dictionary")
            
            # Validate and create config object
            config = self._validate_and_create_config(raw_data)
            self._config = config
            
            return config
            
        except yaml.YAMLError as e:
            raise CourseParserError(f"Invalid YAML in course configuration: {e}")
        except Exception as e:
            raise CourseParserError(f"Error parsing course configuration: {e}")
    
    def _validate_and_create_config(self, raw_data: Dict[str, Any]) -> CourseConfig:
        """
        Validate raw data and create CourseConfig object.
        
        Args:
            raw_data: Dictionary from parsed YAML
            
        Returns:
            CourseConfig: Validated configuration object
            
        Raises:
            CourseParserError: If validation fails
        """
        # Check required top-level fields
        missing_required = [field for field in self.REQUIRED_FIELDS if field not in raw_data]
        if missing_required:
            raise CourseParserError(f"Missing required fields: {', '.join(missing_required)}")
        
        # Validate nested structures
        professor_info = self._validate_professor_info(raw_data.get("professor", {}))
        resources_info = self._validate_resources_info(raw_data.get("resources", {}))
        
        # Extract known fields
        known_fields = {}
        unknown_fields = {}
        
        for key, value in raw_data.items():
            if key in CourseConfig.__dataclass_fields__ and key not in ["professor", "resources"]:
                known_fields[key] = value
            elif key not in ["professor", "resources"]:
                unknown_fields[key] = value
        
        # Create config object
        try:
            config = CourseConfig(
                professor=professor_info,
                resources=resources_info,
                unknown_fields=unknown_fields,
                **known_fields
            )
            return config
        except TypeError as e:
            raise CourseParserError(f"Configuration validation error: {e}")
    
    def _validate_professor_info(self, professor_data: Dict[str, Any]) -> ProfessorInfo:
        """
        Validate and create ProfessorInfo object.
        
        Args:
            professor_data: Dictionary containing professor information
            
        Returns:
            ProfessorInfo: Validated professor information object
            
        Raises:
            CourseParserError: If validation fails
        """
        if not isinstance(professor_data, dict):
            raise CourseParserError("Professor information must be a dictionary")
        
        missing_fields = [field for field in self.REQUIRED_PROFESSOR_FIELDS 
                         if field not in professor_data]
        if missing_fields:
            raise CourseParserError(
                f"Missing required professor fields: {', '.join(missing_fields)}"
            )
        
        # Basic email validation
        email = professor_data.get("email", "")
        if "@" not in email or "." not in email:
            raise CourseParserError("Professor email must be a valid email address")
        
        try:
            return ProfessorInfo(
                name=professor_data["name"],
                email=professor_data["email"],
                office_hours=professor_data["office_hours"],
                office_location=professor_data["office_location"]
            )
        except Exception as e:
            raise CourseParserError(f"Error creating professor info: {e}")
    
    def _validate_resources_info(self, resources_data: Dict[str, Any]) -> CourseResources:
        """
        Validate and create CourseResources object.
        
        Args:
            resources_data: Dictionary containing resources information
            
        Returns:
            CourseResources: Validated resources information object
            
        Raises:
            CourseParserError: If validation fails
        """
        if not isinstance(resources_data, dict):
            raise CourseParserError("Resources information must be a dictionary")
        
        missing_fields = [field for field in self.REQUIRED_RESOURCES_FIELDS 
                         if field not in resources_data]
        if missing_fields:
            raise CourseParserError(
                f"Missing required resource fields: {', '.join(missing_fields)}"
            )
        
        try:
            return CourseResources(
                repository=resources_data["repository"],
                shared_drive=resources_data["shared_drive"],
                syllabus=resources_data["syllabus"],
                announcements_feed=resources_data["announcements_feed"]
            )
        except Exception as e:
            raise CourseParserError(f"Error creating resources info: {e}")
    
    def get_config(self) -> CourseConfig:
        """
        Get the current configuration. Parse if not already done.
        
        Returns:
            CourseConfig: Current configuration object
        """
        if self._config is None:
            self._config = self.parse()
        return self._config
    
    def get_course_name(self) -> str:
        """Get the course name."""
        return self.get_config().course_name
    
    def get_course_code(self) -> str:
        """Get the course code."""
        return self.get_config().course_code
    
    def get_semester(self) -> str:
        """Get the semester."""
        return self.get_config().semester
    
    def get_professor_info(self) -> ProfessorInfo:
        """Get professor information."""
        return self.get_config().professor
    
    def get_resources(self) -> CourseResources:
        """Get course resources."""
        return self.get_config().resources
    
    def get_contact_policy(self) -> str:
        """Get the contact policy."""
        return self.get_config().contact_policy
    
    def get_unknown_fields(self) -> Dict[str, Any]:
        """Get any unknown fields for extensibility."""
        return self.get_config().unknown_fields
    
    def has_unknown_field(self, field_name: str) -> bool:
        """Check if an unknown field exists."""
        return field_name in self.get_config().unknown_fields
    
    def get_unknown_field(self, field_name: str, default: Any = None) -> Any:
        """Get value of an unknown field, with optional default."""
        return self.get_config().unknown_fields.get(field_name, default)


def load_course_config(repo_root: Optional[str] = None, professor_dir: str = "professor") -> CourseConfig:
    """
    Convenience function to load course configuration.
    
    Args:
        repo_root (str, optional): Path to repository root
        professor_dir (str): Name of professor directory
        
    Returns:
        CourseConfig: Parsed and validated configuration
        
    Raises:
        CourseParserError: If parsing or validation fails
    """
    parser = CourseParser(repo_root, professor_dir)
    return parser.parse()


# Example usage and testing
if __name__ == "__main__":
    try:
        # Test parsing from current directory
        config = load_course_config()
        print(f"✅ Course Configuration loaded successfully!")
        print(f"Course: {config.course_name} ({config.course_code})")
        print(f"Semester: {config.semester}")
        print(f"Professor: {config.professor.name}")
        print(f"Email: {config.professor.email}")
        print(f"Office Hours: {config.professor.office_hours}")
        print(f"Office Location: {config.professor.office_location}")
        print(f"Repository: {config.resources.repository}")
        print(f"Shared Drive: {config.resources.shared_drive}")
        print(f"Syllabus: {config.resources.syllabus}")
        print(f"Announcements: {config.resources.announcements_feed}")
        print(f"Contact Policy: {config.contact_policy}")
        
        if config.unknown_fields:
            print(f"Unknown fields (for future use): {config.unknown_fields}")
        
    except CourseParserError as e:
        print(f"❌ Course Parser Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}") 