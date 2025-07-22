"""
Naming Convention Validator for GitHub Class Template Repository

This module implements and validates the file naming convention rules specified in core.md:
- Numbers for primary content files
- Letters (a, b, c, ...) for associated code files  
- Capital letters for appendices (A_, B_, etc.)
- Homework files prefixed with "hw"
- Auto-generated indices: 00_index.md, 00_master_index.md

Author: Framework Team
License: Follows repository license
"""

import re
import os
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum


class FileType(Enum):
    """Enumeration of recognized file types in the naming convention."""
    PRIMARY_CONTENT = "primary_content"        # 01_introduction.md
    ASSOCIATED_CODE = "associated_code"        # 01_a_code_for_introduction.py
    HOMEWORK = "homework"                      # hw_01.md
    HOMEWORK_CODE = "homework_code"            # hw_01_a_code_for_hw_01.py
    HOMEWORK_SOLUTION = "homework_solution"    # solved_hw_01.md
    CHAPTER_INDEX = "chapter_index"            # 00_index.md
    MASTER_INDEX = "master_index"              # 00_master_index.md
    APPENDIX_CHAPTER = "appendix_chapter"      # A_advanced_topics/
    REGULAR_CHAPTER = "regular_chapter"        # 01_introduction/
    UNKNOWN = "unknown"


@dataclass
class ParsedFileName:
    """
    Data class representing a parsed file name according to naming conventions.
    
    Attributes:
        original_name (str): Original file name
        file_type (FileType): Recognized file type
        number (Optional[int]): Primary number (01, 02, etc.)
        letter_suffix (Optional[str]): Letter suffix for associated files (a, b, c)
        appendix_letter (Optional[str]): Capital letter for appendices (A, B, C)
        title (str): Descriptive title extracted from filename
        extension (str): File extension
        is_valid (bool): Whether the name follows conventions
        validation_errors (List[str]): List of validation errors if any
    """
    original_name: str
    file_type: FileType
    number: Optional[int] = None
    letter_suffix: Optional[str] = None
    appendix_letter: Optional[str] = None
    title: str = ""
    extension: str = ""
    is_valid: bool = True
    validation_errors: List[str] = None
    
    def __post_init__(self):
        if self.validation_errors is None:
            self.validation_errors = []


class NamingConventionValidator:
    """
    Validator for file and directory naming conventions.
    
    Enforces the naming rules specified in core.md for consistent structure
    that enables automation and parsing.
    """
    
    # Regular expression patterns for different file types
    PATTERNS = {
        # Primary content: 01_introduction.md, 02_testing.md
        'primary_content': re.compile(r'^(\d{2})_([a-z_]+)\.(md|qmd)$'),
        
        # Associated code: 01_a_code_for_introduction.py, 01_b_another_file.ipynb
        'associated_code': re.compile(r'^(\d{2})_([a-z])_([a-z_]+)\.(py|ipynb|js|css|html)$'),
        
        # Homework: hw_01.md, hw_02_advanced.md
        'homework': re.compile(r'^hw_(\d{2})(?:_([a-z_]+))?\.(md|qmd)$'),
        
        # Homework code: hw_01_a_code_for_hw_01.py
        'homework_code': re.compile(r'^hw_(\d{2})_([a-z])_([a-z_]+)\.(py|ipynb|js)$'),
        
        # Homework solutions: solved_hw_01.md
        'homework_solution': re.compile(r'^solved_hw_(\d{2})(?:_([a-z_]+))?\.(md|qmd)$'),
        
        # Chapter index: 00_index.md
        'chapter_index': re.compile(r'^00_index\.(md|qmd)$'),
        
        # Master index: 00_master_index.md
        'master_index': re.compile(r'^00_master_index\.(md|qmd)$'),
        
        # Regular chapter directories: 01_introduction/, 02_testing/
        'regular_chapter': re.compile(r'^(\d{2})_([a-z_]+)$'),
        
        # Appendix chapter directories: A_advanced_topics/, B_references/
        'appendix_chapter': re.compile(r'^([A-Z])_([a-z_]+)$'),
    }
    
    VALID_EXTENSIONS = {
        'content': {'.md', '.qmd'},
        'code': {'.py', '.ipynb', '.js', '.css', '.html', '.ts'},
        'data': {'.csv', '.json', '.yml', '.yaml', '.txt'},
        'media': {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.mp4', '.pdf'}
    }
    
    def __init__(self):
        """Initialize the naming convention validator."""
        pass
    
    def parse_filename(self, filename: str) -> ParsedFileName:
        """
        Parse a filename according to naming conventions.
        
        Args:
            filename (str): The filename to parse
            
        Returns:
            ParsedFileName: Parsed filename information
        """
        parsed = ParsedFileName(original_name=filename, file_type=FileType.UNKNOWN)
        
        # Extract extension
        path = Path(filename)
        parsed.extension = path.suffix
        name_without_ext = path.stem
        
        # Try to match against each pattern
        for pattern_name, pattern in self.PATTERNS.items():
            match = pattern.match(filename)
            if match:
                parsed = self._parse_matched_pattern(pattern_name, match, parsed)
                break
        
        # If no pattern matched, mark as unknown and add validation error
        if parsed.file_type == FileType.UNKNOWN:
            parsed.is_valid = False
            parsed.validation_errors.append(f"Filename '{filename}' does not match any naming convention")
        
        return parsed
    
    def _parse_matched_pattern(self, pattern_name: str, match: re.Match, parsed: ParsedFileName) -> ParsedFileName:
        """Parse a matched pattern and populate the ParsedFileName object."""
        
        if pattern_name == 'primary_content':
            parsed.file_type = FileType.PRIMARY_CONTENT
            parsed.number = int(match.group(1))
            parsed.title = match.group(2).replace('_', ' ')
            
        elif pattern_name == 'associated_code':
            parsed.file_type = FileType.ASSOCIATED_CODE
            parsed.number = int(match.group(1))
            parsed.letter_suffix = match.group(2)
            parsed.title = match.group(3).replace('_', ' ')
            
        elif pattern_name == 'homework':
            parsed.file_type = FileType.HOMEWORK
            parsed.number = int(match.group(1))
            parsed.title = match.group(2).replace('_', ' ') if match.group(2) else f"homework {parsed.number}"
            
        elif pattern_name == 'homework_code':
            parsed.file_type = FileType.HOMEWORK_CODE
            parsed.number = int(match.group(1))
            parsed.letter_suffix = match.group(2)
            parsed.title = match.group(3).replace('_', ' ')
            
        elif pattern_name == 'homework_solution':
            parsed.file_type = FileType.HOMEWORK_SOLUTION
            parsed.number = int(match.group(1))
            parsed.title = match.group(2).replace('_', ' ') if match.group(2) else f"homework {parsed.number} solution"
            
        elif pattern_name == 'chapter_index':
            parsed.file_type = FileType.CHAPTER_INDEX
            parsed.title = "chapter index"
            
        elif pattern_name == 'master_index':
            parsed.file_type = FileType.MASTER_INDEX
            parsed.title = "master index"
            
        elif pattern_name == 'regular_chapter':
            parsed.file_type = FileType.REGULAR_CHAPTER
            parsed.number = int(match.group(1))
            parsed.title = match.group(2).replace('_', ' ')
            
        elif pattern_name == 'appendix_chapter':
            parsed.file_type = FileType.APPENDIX_CHAPTER
            parsed.appendix_letter = match.group(1)
            parsed.title = match.group(2).replace('_', ' ')
        
        return parsed
    
    def validate_filename(self, filename: str) -> Tuple[bool, List[str]]:
        """
        Validate a single filename against naming conventions.
        
        Args:
            filename (str): The filename to validate
            
        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_errors)
        """
        parsed = self.parse_filename(filename)
        errors = []
        
        if not parsed.is_valid:
            errors.extend(parsed.validation_errors)
            return False, errors
        
        # Additional validation rules
        if parsed.extension:
            if not self._is_valid_extension(parsed.extension, parsed.file_type):
                errors.append(f"Invalid extension '{parsed.extension}' for file type {parsed.file_type.value}")
        
        # Check number sequencing (requires context of other files)
        # This would be implemented in validate_directory_structure
        
        return len(errors) == 0, errors
    
    def _is_valid_extension(self, extension: str, file_type: FileType) -> bool:
        """Check if the extension is valid for the given file type."""
        
        if file_type in [FileType.PRIMARY_CONTENT, FileType.HOMEWORK, FileType.HOMEWORK_SOLUTION, 
                        FileType.CHAPTER_INDEX, FileType.MASTER_INDEX]:
            return extension in self.VALID_EXTENSIONS['content']
        
        elif file_type in [FileType.ASSOCIATED_CODE, FileType.HOMEWORK_CODE]:
            return extension in self.VALID_EXTENSIONS['code']
        
        return True  # Allow any extension for other types
    
    def validate_directory_structure(self, directory_path: str) -> Dict[str, List[str]]:
        """
        Validate the naming conventions for an entire directory structure.
        
        Args:
            directory_path (str): Path to the directory to validate
            
        Returns:
            Dict[str, List[str]]: Dictionary mapping file paths to validation errors
        """
        path = Path(directory_path)
        validation_results = {}
        
        if not path.exists():
            return {"directory": [f"Directory '{directory_path}' does not exist"]}
        
        # Validate all files in the directory
        for file_path in path.rglob('*'):
            if file_path.is_file():
                relative_path = str(file_path.relative_to(path))
                is_valid, errors = self.validate_filename(file_path.name)
                
                if errors:
                    validation_results[relative_path] = errors
        
        # Additional structural validations
        self._validate_numbering_sequence(path, validation_results)
        self._validate_required_indices(path, validation_results)
        
        return validation_results
    
    def _validate_numbering_sequence(self, path: Path, results: Dict[str, List[str]]):
        """Validate that numbered files follow proper sequence (01, 02, 03, ...)."""
        
        # Group files by directory and check numbering
        for dir_path in path.rglob('*'):
            if dir_path.is_dir():
                files = [f for f in dir_path.iterdir() if f.is_file()]
                numbers_used = set()
                
                for file in files:
                    parsed = self.parse_filename(file.name)
                    if parsed.number is not None:
                        numbers_used.add(parsed.number)
                
                # Check for gaps in numbering
                if numbers_used:
                    max_num = max(numbers_used)
                    expected = set(range(1, max_num + 1))
                    missing = expected - numbers_used
                    
                    if missing:
                        rel_dir = str(dir_path.relative_to(path))
                        key = f"{rel_dir}/numbering"
                        if key not in results:
                            results[key] = []
                        results[key].append(f"Missing numbered files: {sorted(missing)}")
    
    def _validate_required_indices(self, path: Path, results: Dict[str, List[str]]):
        """Validate that required index files exist where expected."""
        
        # Check for chapter indices in chapter directories
        for dir_path in path.rglob('*'):
            if dir_path.is_dir():
                dir_name = dir_path.name
                parsed = self.parse_filename(dir_name)
                
                if parsed.file_type in [FileType.REGULAR_CHAPTER, FileType.APPENDIX_CHAPTER]:
                    index_file = dir_path / "00_index.md"
                    if not index_file.exists():
                        rel_dir = str(dir_path.relative_to(path))
                        key = f"{rel_dir}/missing_index"
                        if key not in results:
                            results[key] = []
                        results[key].append("Missing required 00_index.md file")
    
    def suggest_filename(self, intended_type: FileType, number: Optional[int] = None, 
                        letter: Optional[str] = None, title: str = "", 
                        extension: str = ".md") -> str:
        """
        Suggest a properly formatted filename based on the intended type.
        
        Args:
            intended_type (FileType): The intended file type
            number (Optional[int]): Number for the file (if applicable)
            letter (Optional[str]): Letter suffix for associated files
            title (str): Descriptive title for the file
            extension (str): File extension
            
        Returns:
            str: Suggested filename following conventions
        """
        
        clean_title = title.lower().replace(' ', '_').replace('-', '_')
        clean_title = re.sub(r'[^a-z0-9_]', '', clean_title)
        
        if intended_type == FileType.PRIMARY_CONTENT:
            return f"{number:02d}_{clean_title}{extension}"
        
        elif intended_type == FileType.ASSOCIATED_CODE:
            return f"{number:02d}_{letter}_{clean_title}{extension}"
        
        elif intended_type == FileType.HOMEWORK:
            return f"hw_{number:02d}_{clean_title}{extension}" if clean_title else f"hw_{number:02d}{extension}"
        
        elif intended_type == FileType.HOMEWORK_CODE:
            return f"hw_{number:02d}_{letter}_{clean_title}{extension}"
        
        elif intended_type == FileType.HOMEWORK_SOLUTION:
            return f"solved_hw_{number:02d}_{clean_title}{extension}" if clean_title else f"solved_hw_{number:02d}{extension}"
        
        elif intended_type == FileType.CHAPTER_INDEX:
            return f"00_index{extension}"
        
        elif intended_type == FileType.MASTER_INDEX:
            return f"00_master_index{extension}"
        
        elif intended_type == FileType.REGULAR_CHAPTER:
            return f"{number:02d}_{clean_title}"
        
        elif intended_type == FileType.APPENDIX_CHAPTER:
            return f"{letter}_{clean_title}"
        
        return f"unknown_{clean_title}{extension}"


# Convenience functions for common validation tasks
def validate_file(filename: str) -> Tuple[bool, List[str]]:
    """Validate a single filename. Convenience function."""
    validator = NamingConventionValidator()
    return validator.validate_filename(filename)


def validate_directory(directory_path: str) -> Dict[str, List[str]]:
    """Validate an entire directory structure. Convenience function."""
    validator = NamingConventionValidator()
    return validator.validate_directory_structure(directory_path)


def parse_file(filename: str) -> ParsedFileName:
    """Parse a filename according to conventions. Convenience function."""
    validator = NamingConventionValidator()
    return validator.parse_filename(filename)


# Example usage and testing
if __name__ == "__main__":
    validator = NamingConventionValidator()
    
    # Test various filename patterns
    test_files = [
        "01_introduction.md",           # Valid primary content
        "01_a_code_for_introduction.py", # Valid associated code
        "hw_01.md",                     # Valid homework
        "hw_01_a_solution.py",          # Valid homework code
        "solved_hw_01.md",              # Valid homework solution
        "00_index.md",                  # Valid chapter index
        "00_master_index.md",           # Valid master index
        "A_advanced_topics",            # Valid appendix chapter
        "invalid_file.txt",             # Invalid
        "1_bad_numbering.md",           # Invalid (should be 01)
    ]
    
    print("🔍 Testing Naming Convention Validator")
    print("=" * 50)
    
    for filename in test_files:
        parsed = validator.parse_filename(filename)
        is_valid, errors = validator.validate_filename(filename)
        
        status = "✅" if is_valid else "❌"
        print(f"{status} {filename}")
        print(f"   Type: {parsed.file_type.value}")
        if parsed.number:
            print(f"   Number: {parsed.number}")
        if parsed.letter_suffix:
            print(f"   Letter: {parsed.letter_suffix}")
        if parsed.title:
            print(f"   Title: {parsed.title}")
        if errors:
            print(f"   Errors: {errors}")
        print()
    
    # Test filename suggestions
    print("💡 Filename Suggestions")
    print("=" * 30)
    suggestions = [
        (FileType.PRIMARY_CONTENT, 1, None, "Introduction to Python", ".md"),
        (FileType.ASSOCIATED_CODE, 1, "a", "example code", ".py"),
        (FileType.HOMEWORK, 3, None, "data analysis", ".md"),
        (FileType.APPENDIX_CHAPTER, None, "A", "advanced topics", ""),
    ]
    
    for file_type, number, letter, title, ext in suggestions:
        suggested = validator.suggest_filename(file_type, number, letter, title, ext)
        print(f"{file_type.value}: '{suggested}'") 