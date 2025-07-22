"""
Chapter Structure Validator for GitHub Class Template Repository

This module validates the hierarchical directory structure and organization 
specified in core.md for chapters, sections, and content files.

Expected structure:
class_notes/  # category
    01_introduction/   # chapter
        00_index.md                     # auto-generated chapter index
        01_introduction.md              # section
        01_a_code_for_introduction.py
        01_b_code_for_introduction.py
        02_testing.md
        hw_01.md
        hw_01_a_code_for_hw_01.py
    02_testing/
    A_advanced_topics/  # appendix chapter
        1_advanced_topics.md
        1_a_code_for_1_advanced_topics.py
    00_master_index.md  # auto-generated master index

Author: Framework Team
License: Follows repository license
"""

import os
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict

# Import our naming convention validator
try:
    from .naming_conventions import NamingConventionValidator, FileType, ParsedFileName
except ImportError:
    # Handle standalone execution
    from naming_conventions import NamingConventionValidator, FileType, ParsedFileName


@dataclass
class ChapterInfo:
    """
    Information about a chapter directory and its contents.
    
    Attributes:
        path (Path): Path to the chapter directory
        name (str): Chapter directory name
        number (Optional[int]): Chapter number for regular chapters
        appendix_letter (Optional[str]): Letter for appendix chapters
        title (str): Extracted chapter title
        sections (List[ParsedFileName]): Primary content sections
        associated_files (List[ParsedFileName]): Associated code files
        homework_files (List[ParsedFileName]): Homework files
        other_files (List[ParsedFileName]): Other files
        has_index (bool): Whether 00_index.md exists
        validation_errors (List[str]): Structure validation errors
    """
    path: Path
    name: str
    number: Optional[int] = None
    appendix_letter: Optional[str] = None
    title: str = ""
    sections: List[ParsedFileName] = field(default_factory=list)
    associated_files: List[ParsedFileName] = field(default_factory=list)
    homework_files: List[ParsedFileName] = field(default_factory=list)
    other_files: List[ParsedFileName] = field(default_factory=list)
    has_index: bool = False
    validation_errors: List[str] = field(default_factory=list)


@dataclass
class CategoryInfo:
    """
    Information about a category directory (e.g., class_notes).
    
    Attributes:
        path (Path): Path to the category directory
        name (str): Category directory name
        chapters (List[ChapterInfo]): Regular chapters
        appendices (List[ChapterInfo]): Appendix chapters
        has_master_index (bool): Whether 00_master_index.md exists
        validation_errors (List[str]): Category-level validation errors
    """
    path: Path
    name: str
    chapters: List[ChapterInfo] = field(default_factory=list)
    appendices: List[ChapterInfo] = field(default_factory=list)
    has_master_index: bool = False
    validation_errors: List[str] = field(default_factory=list)


class ChapterStructureValidator:
    """
    Validator for chapter directory structure and organization.
    
    Enforces the hierarchical structure specified in core.md for 
    categories, chapters, sections, and associated files.
    """
    
    def __init__(self):
        """Initialize the chapter structure validator."""
        self.naming_validator = NamingConventionValidator()
    
    def validate_category(self, category_path: str) -> CategoryInfo:
        """
        Validate a category directory (e.g., class_notes, homework).
        
        Args:
            category_path (str): Path to the category directory
            
        Returns:
            CategoryInfo: Validation results and category information
        """
        path = Path(category_path)
        category = CategoryInfo(path=path, name=path.name)
        
        if not path.exists():
            category.validation_errors.append(f"Category directory '{category_path}' does not exist")
            return category
        
        if not path.is_dir():
            category.validation_errors.append(f"'{category_path}' is not a directory")
            return category
        
        # Check for master index
        master_index = path / "00_master_index.md"
        category.has_master_index = master_index.exists()
        
        # Scan for chapter directories
        for item in path.iterdir():
            if item.is_dir():
                chapter_info = self.validate_chapter(str(item))
                
                if chapter_info.appendix_letter:
                    category.appendices.append(chapter_info)
                else:
                    category.chapters.append(chapter_info)
        
        # Validate chapter numbering sequence
        self._validate_chapter_sequence(category)
        
        # Validate appendix letter sequence
        self._validate_appendix_sequence(category)
        
        return category
    
    def validate_chapter(self, chapter_path: str) -> ChapterInfo:
        """
        Validate a chapter directory structure.
        
        Args:
            chapter_path (str): Path to the chapter directory
            
        Returns:
            ChapterInfo: Validation results and chapter information
        """
        path = Path(chapter_path)
        chapter = ChapterInfo(path=path, name=path.name)
        
        if not path.exists():
            chapter.validation_errors.append(f"Chapter directory '{chapter_path}' does not exist")
            return chapter
        
        if not path.is_dir():
            chapter.validation_errors.append(f"'{chapter_path}' is not a directory")
            return chapter
        
        # Parse chapter directory name
        parsed_dir = self.naming_validator.parse_filename(path.name)
        
        if parsed_dir.file_type == FileType.REGULAR_CHAPTER:
            chapter.number = parsed_dir.number
            chapter.title = parsed_dir.title
        elif parsed_dir.file_type == FileType.APPENDIX_CHAPTER:
            chapter.appendix_letter = parsed_dir.appendix_letter
            chapter.title = parsed_dir.title
        else:
            chapter.validation_errors.append(f"Invalid chapter directory name: '{path.name}'")
        
        # Check for required index file
        index_file = path / "00_index.md"
        chapter.has_index = index_file.exists()
        
        if not chapter.has_index:
            chapter.validation_errors.append("Missing required 00_index.md file")
        
        # Scan and categorize files
        for file_path in path.iterdir():
            if file_path.is_file():
                parsed_file = self.naming_validator.parse_filename(file_path.name)
                
                if parsed_file.file_type == FileType.PRIMARY_CONTENT:
                    chapter.sections.append(parsed_file)
                elif parsed_file.file_type == FileType.ASSOCIATED_CODE:
                    chapter.associated_files.append(parsed_file)
                elif parsed_file.file_type in [FileType.HOMEWORK, FileType.HOMEWORK_CODE, FileType.HOMEWORK_SOLUTION]:
                    chapter.homework_files.append(parsed_file)
                elif parsed_file.file_type == FileType.CHAPTER_INDEX:
                    # Already handled above
                    pass
                else:
                    chapter.other_files.append(parsed_file)
        
        # Validate section numbering
        self._validate_section_sequence(chapter)
        
        # Validate associated files match sections
        self._validate_associated_files(chapter)
        
        # Validate homework numbering
        self._validate_homework_sequence(chapter)
        
        return chapter
    
    def _validate_chapter_sequence(self, category: CategoryInfo):
        """Validate that chapter numbers form a proper sequence."""
        if not category.chapters:
            return
        
        chapter_numbers = {ch.number for ch in category.chapters if ch.number is not None}
        
        if chapter_numbers:
            min_num = min(chapter_numbers)
            max_num = max(chapter_numbers)
            expected = set(range(min_num, max_num + 1))
            missing = expected - chapter_numbers
            
            if missing:
                category.validation_errors.append(f"Missing chapter numbers: {sorted(missing)}")
            
            # Check if numbering starts at 01
            if min_num != 1:
                category.validation_errors.append(f"Chapter numbering should start at 01, found {min_num:02d}")
    
    def _validate_appendix_sequence(self, category: CategoryInfo):
        """Validate that appendix letters form a proper sequence."""
        if not category.appendices:
            return
        
        appendix_letters = {ch.appendix_letter for ch in category.appendices if ch.appendix_letter}
        
        if appendix_letters:
            # Convert to numbers for easier validation (A=1, B=2, etc.)
            letter_numbers = {ord(letter) - ord('A') + 1 for letter in appendix_letters}
            min_num = min(letter_numbers)
            max_num = max(letter_numbers)
            expected = set(range(min_num, max_num + 1))
            missing = expected - letter_numbers
            
            if missing:
                missing_letters = [chr(ord('A') + n - 1) for n in missing]
                category.validation_errors.append(f"Missing appendix letters: {missing_letters}")
    
    def _validate_section_sequence(self, chapter: ChapterInfo):
        """Validate that section numbers form a proper sequence."""
        if not chapter.sections:
            return
        
        section_numbers = {sec.number for sec in chapter.sections if sec.number is not None}
        
        if section_numbers:
            min_num = min(section_numbers)
            max_num = max(section_numbers)
            expected = set(range(min_num, max_num + 1))
            missing = expected - section_numbers
            
            if missing:
                chapter.validation_errors.append(f"Missing section numbers: {sorted(missing)}")
            
            # Check if numbering starts at 01
            if min_num != 1:
                chapter.validation_errors.append(f"Section numbering should start at 01, found {min_num:02d}")
    
    def _validate_associated_files(self, chapter: ChapterInfo):
        """Validate that associated files correspond to existing sections."""
        section_numbers = {sec.number for sec in chapter.sections if sec.number is not None}
        
        for assoc_file in chapter.associated_files:
            if assoc_file.number not in section_numbers:
                chapter.validation_errors.append(
                    f"Associated file '{assoc_file.original_name}' references non-existent section {assoc_file.number:02d}"
                )
    
    def _validate_homework_sequence(self, chapter: ChapterInfo):
        """Validate homework file numbering within chapter."""
        homework_numbers = set()
        
        for hw_file in chapter.homework_files:
            if hw_file.number is not None:
                homework_numbers.add(hw_file.number)
        
        if len(homework_numbers) > 1:
            # If multiple homework files, check sequence
            min_num = min(homework_numbers)
            max_num = max(homework_numbers)
            expected = set(range(min_num, max_num + 1))
            missing = expected - homework_numbers
            
            if missing:
                chapter.validation_errors.append(f"Missing homework numbers: {sorted(missing)}")
    
    def validate_structure(self, base_path: str) -> Dict[str, CategoryInfo]:
        """
        Validate the entire structure starting from a base path.
        
        Args:
            base_path (str): Path to directory containing categories (e.g., professor/)
            
        Returns:
            Dict[str, CategoryInfo]: Validation results for each category
        """
        path = Path(base_path)
        results = {}
        
        if not path.exists():
            return {"error": CategoryInfo(path=path, name="error", 
                                        validation_errors=[f"Base path '{base_path}' does not exist"])}
        
        # Look for category directories
        for item in path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                # Check if this looks like a category (contains chapters)
                has_chapters = any(
                    subitem.is_dir() and self._looks_like_chapter(subitem.name)
                    for subitem in item.iterdir()
                )
                
                if has_chapters:
                    category_info = self.validate_category(str(item))
                    results[item.name] = category_info
        
        return results
    
    def _looks_like_chapter(self, dirname: str) -> bool:
        """Check if a directory name looks like a chapter directory."""
        parsed = self.naming_validator.parse_filename(dirname)
        return parsed.file_type in [FileType.REGULAR_CHAPTER, FileType.APPENDIX_CHAPTER]
    
    def generate_report(self, validation_results: Dict[str, CategoryInfo]) -> str:
        """
        Generate a human-readable validation report.
        
        Args:
            validation_results: Results from validate_structure()
            
        Returns:
            str: Formatted validation report
        """
        report_lines = []
        report_lines.append("📁 Chapter Structure Validation Report")
        report_lines.append("=" * 50)
        
        total_errors = 0
        
        for category_name, category_info in validation_results.items():
            report_lines.append(f"\n📂 Category: {category_name}")
            
            # Category-level errors
            if category_info.validation_errors:
                for error in category_info.validation_errors:
                    report_lines.append(f"  ❌ {error}")
                    total_errors += 1
            
            # Master index status
            index_status = "✅" if category_info.has_master_index else "❌"
            report_lines.append(f"  📄 Master Index: {index_status}")
            if not category_info.has_master_index:
                total_errors += 1
            
            # Regular chapters
            if category_info.chapters:
                report_lines.append(f"  📖 Regular Chapters: {len(category_info.chapters)}")
                for chapter in category_info.chapters:
                    chapter_status = "✅" if not chapter.validation_errors else "❌"
                    report_lines.append(f"    {chapter_status} {chapter.name}")
                    
                    for error in chapter.validation_errors:
                        report_lines.append(f"      ❌ {error}")
                        total_errors += 1
            
            # Appendix chapters
            if category_info.appendices:
                report_lines.append(f"  📚 Appendix Chapters: {len(category_info.appendices)}")
                for appendix in category_info.appendices:
                    appendix_status = "✅" if not appendix.validation_errors else "❌"
                    report_lines.append(f"    {appendix_status} {appendix.name}")
                    
                    for error in appendix.validation_errors:
                        report_lines.append(f"      ❌ {error}")
                        total_errors += 1
        
        # Summary
        report_lines.append(f"\n📊 Summary")
        report_lines.append("-" * 20)
        if total_errors == 0:
            report_lines.append("✅ All structure validations passed!")
        else:
            report_lines.append(f"❌ Found {total_errors} structure validation error(s)")
        
        return "\n".join(report_lines)


# Convenience functions
def validate_category_structure(category_path: str) -> CategoryInfo:
    """Validate a single category directory structure."""
    validator = ChapterStructureValidator()
    return validator.validate_category(category_path)


def validate_chapter_structure(chapter_path: str) -> ChapterInfo:
    """Validate a single chapter directory structure."""
    validator = ChapterStructureValidator()
    return validator.validate_chapter(chapter_path)


def validate_full_structure(base_path: str) -> Dict[str, CategoryInfo]:
    """Validate the entire directory structure."""
    validator = ChapterStructureValidator()
    return validator.validate_structure(base_path)


# Example usage and testing
if __name__ == "__main__":
    validator = ChapterStructureValidator()
    
    print("🔍 Testing Chapter Structure Validator")
    print("=" * 50)
    
    # Test with the professor directory
    base_path = "../.."  # Assuming we're in professor/framework_code/validation
    
    try:
        results = validator.validate_structure(base_path)
        report = validator.generate_report(results)
        print(report)
        
    except Exception as e:
        print(f"❌ Error during validation: {e}")
        
        # Test with a simple example structure
        print("\n🧪 Testing with example chapter...")
        
        # Create example chapter info manually for testing
        example_chapter = ChapterInfo(
            path=Path("example/01_introduction"),
            name="01_introduction",
            number=1,
            title="introduction"
        )
        
        print(f"Example chapter: {example_chapter.name}")
        print(f"Number: {example_chapter.number}")
        print(f"Title: {example_chapter.title}")
        print(f"Has index: {example_chapter.has_index}")
        print(f"Errors: {example_chapter.validation_errors}") 