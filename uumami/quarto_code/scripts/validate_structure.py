#!/usr/bin/env python3
"""
Structure Validation Engine for Quarto Educational Infrastructure

This script validates directory structures and content organization to ensure
compliance with educational naming conventions and required file patterns.
It integrates with scan_structure.py for data discovery and provides detailed
error reporting with actionable fix suggestions.

Usage:
    python validate_structure.py <path> [options]
    
Example:
    python validate_structure.py uumami/
    python validate_structure.py uumami/ --strict --ci
    python validate_structure.py --input structure.json
"""

import re
import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import yaml
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree
from rich import box

# Import our content discovery engine
try:
    from scan_structure import scan_content_structure, extract_title_from_qmd, NAMING_PATTERNS
except ImportError:
    # Handle import when run from different directory
    sys.path.append(str(Path(__file__).parent))
    from scan_structure import scan_content_structure, extract_title_from_qmd, NAMING_PATTERNS

console = Console()

class ValidationLevel(Enum):
    """Validation issue severity levels."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

@dataclass
class ValidationIssue:
    """Represents a single validation issue."""
    level: ValidationLevel
    category: str
    message: str
    file_path: Optional[str] = None
    suggestion: Optional[str] = None
    rule: Optional[str] = None

class StructureValidator:
    """Main structure validation engine."""
    
    def __init__(self, strict_mode: bool = False, include_warnings: bool = True):
        self.strict_mode = strict_mode
        self.include_warnings = include_warnings
        self.issues: List[ValidationIssue] = []
        
        # Enhanced validation patterns
        self.patterns = {
            'chapter_directory': r'^\d{2}_[a-zA-Z0-9_]+$',        # 00_intro, 01_python_basics
            'appendix_directory': r'^[a-z]_[a-zA-Z0-9_]+$',       # a_installation, b_troubleshooting
            'section_directory': r'^[a-z]_[a-zA-Z0-9_]+$',        # a_prompt_engineering, b_intro_system
            'index_file': r'^\d{2}_index\.qmd$',                  # 00_index.qmd, 01_index.qmd
            'navigation_file': r'^_nav\.qmd$',                    # _nav.qmd
            'section_file': r'^\d{2}_[a-zA-Z0-9_]+\.qmd$',        # 00_overview.qmd, 01_setup.qmd
            'valid_chars': r'^[a-zA-Z0-9_]+$'                     # No special chars except underscore
        }
        
        # Path validation patterns
        self.path_patterns = {
            'css_quarto_code': r'quarto_code/styles/',
            'component_quarto_code': r'quarto_code/components/',
            'extension_quarto_code': r'quarto_code/_extensions/'
        }

    def add_issue(self, level: ValidationLevel, category: str, message: str, 
                  file_path: Optional[str] = None, suggestion: Optional[str] = None, 
                  rule: Optional[str] = None):
        """Add a validation issue to the list."""
        if level == ValidationLevel.WARNING and not self.include_warnings:
            return
        
        issue = ValidationIssue(
            level=level,
            category=category,
            message=message,
            file_path=file_path,
            suggestion=suggestion,
            rule=rule
        )
        self.issues.append(issue)

    def validate_naming_conventions(self, structure_data: Dict[str, Any]) -> None:
        """Validate all naming conventions for chapters, appendices, and sections."""
        
        # Validate chapters
        chapter_prefixes = set()
        for chapter in structure_data.get('chapters', []):
            prefix = chapter['prefix']
            name = chapter['name']
            path = chapter['path']
            
            # Check for duplicate prefixes
            if prefix in chapter_prefixes:
                self.add_issue(
                    ValidationLevel.ERROR,
                    "Naming",
                    f"Duplicate chapter prefix '{prefix}' found",
                    path,
                    f"Each chapter must have a unique numeric prefix (00-99)",
                    "unique_chapter_prefix"
                )
            chapter_prefixes.add(prefix)
            
            # Validate chapter directory naming
            if not re.match(self.patterns['chapter_directory'], name):
                self.add_issue(
                    ValidationLevel.ERROR,
                    "Naming",
                    f"Chapter directory '{name}' doesn't follow naming convention",
                    path,
                    f"Use format: {prefix}_descriptive_name (e.g., {prefix}_introduction)",
                    "chapter_naming"
                )
            
            # Check for reasonable prefix range
            try:
                prefix_num = int(prefix)
                if prefix_num > 50:
                    self.add_issue(
                        ValidationLevel.WARNING,
                        "Organization",
                        f"Chapter prefix {prefix} is quite high - consider reorganizing",
                        path,
                        "Keep chapter numbers reasonable for better organization",
                        "chapter_numbering"
                    )
            except ValueError:
                self.add_issue(
                    ValidationLevel.ERROR,
                    "Naming",
                    f"Chapter prefix '{prefix}' must be numeric",
                    path,
                    "Use two-digit numeric prefixes: 00, 01, 02, etc.",
                    "chapter_prefix_format"
                )
            
            # Validate sections within chapter
            self.validate_chapter_sections(chapter)
        
        # Validate appendices
        appendix_prefixes = set()
        for appendix in structure_data.get('appendices', []):
            prefix = appendix['prefix']
            name = appendix['name']
            path = appendix['path']
            
            # Check for duplicate prefixes
            if prefix in appendix_prefixes:
                self.add_issue(
                    ValidationLevel.ERROR,
                    "Naming",
                    f"Duplicate appendix prefix '{prefix}' found",
                    path,
                    f"Each appendix must have a unique letter prefix (a-z)",
                    "unique_appendix_prefix"
                )
            appendix_prefixes.add(prefix)
            
            # Validate appendix directory naming
            if not re.match(self.patterns['appendix_directory'], name):
                self.add_issue(
                    ValidationLevel.ERROR,
                    "Naming",
                    f"Appendix directory '{name}' doesn't follow naming convention",
                    path,
                    f"Use format: {prefix}_descriptive_name (e.g., {prefix}_installation_guide)",
                    "appendix_naming"
                )

    def validate_chapter_sections(self, chapter: Dict[str, Any]) -> None:
        """Validate sections within a chapter."""
        section_prefixes = set()
        
        for section in chapter.get('sections', []):
            if section.get('type') == 'directory':
                prefix = section.get('prefix', '')
                name = section.get('name', '')
                path = section.get('path', '')
                
                # Check for duplicate section prefixes within chapter
                if prefix in section_prefixes:
                    self.add_issue(
                        ValidationLevel.ERROR,
                        "Naming",
                        f"Duplicate section prefix '{prefix}' in chapter {chapter['prefix']}",
                        path,
                        f"Each section in a chapter must have a unique letter prefix",
                        "unique_section_prefix"
                    )
                section_prefixes.add(prefix)
                
                # Validate section directory naming
                if not re.match(self.patterns['section_directory'], name):
                    self.add_issue(
                        ValidationLevel.ERROR,
                        "Naming",
                        f"Section directory '{name}' doesn't follow naming convention",
                        path,
                        f"Use format: {prefix}_descriptive_name (e.g., {prefix}_getting_started)",
                        "section_naming"
                    )

    def validate_required_files(self, structure_data: Dict[str, Any]) -> None:
        """Validate that required files exist in the correct locations."""
        
        for chapter in structure_data.get('chapters', []) + structure_data.get('appendices', []):
            chapter_path = Path(chapter['path'])
            
            # Check for index file
            if not chapter.get('has_index', False):
                expected_index = f"{chapter['prefix']}_index.qmd"
                self.add_issue(
                    ValidationLevel.ERROR,
                    "Required Files",
                    f"Missing required index file in {chapter['name']}",
                    str(chapter_path),
                    f"Create file: {expected_index}",
                    "missing_index_file"
                )
            else:
                # Validate index file naming
                index_file = chapter.get('index_file', '')
                if not re.match(self.patterns['index_file'], index_file):
                    self.add_issue(
                        ValidationLevel.ERROR,
                        "Naming",
                        f"Index file '{index_file}' doesn't follow naming convention",
                        str(chapter_path / index_file),
                        f"Rename to: {chapter['prefix']}_index.qmd",
                        "index_file_naming"
                    )
            
            # Check for navigation file
            nav_file = chapter_path / '_nav.qmd'
            if not nav_file.exists():
                self.add_issue(
                    ValidationLevel.WARNING,
                    "Navigation",
                    f"Missing navigation file in {chapter['name']}",
                    str(chapter_path),
                    f"Create file: _nav.qmd for chapter navigation",
                    "missing_nav_file"
                )

    def validate_yaml_frontmatter(self, structure_data: Dict[str, Any]) -> None:
        """Validate YAML frontmatter in .qmd files."""
        
        for chapter in structure_data.get('chapters', []) + structure_data.get('appendices', []):
            chapter_path = Path(chapter['path'])
            
            # Validate index file YAML
            if chapter.get('has_index', False):
                index_file = chapter_path / chapter['index_file']
                self.validate_file_yaml(index_file, 'index')
            
            # Validate section files YAML
            for section in chapter.get('sections', []):
                if section.get('type') == 'file':
                    section_file = chapter_path / section['file']
                    self.validate_file_yaml(section_file, 'section')

    def validate_file_yaml(self, file_path: Path, file_type: str) -> None:
        """Validate YAML frontmatter in a single file."""
        if not file_path.exists():
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for YAML frontmatter
            yaml_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
            if not yaml_match:
                self.add_issue(
                    ValidationLevel.WARNING,
                    "Content",
                    f"Missing YAML frontmatter in {file_path.name}",
                    str(file_path),
                    "Add YAML frontmatter with title and format sections",
                    "missing_yaml"
                )
                return
            
            # Parse YAML
            yaml_content = yaml_match.group(1)
            try:
                yaml_data = yaml.safe_load(yaml_content)
                
                # Check for required fields
                if not yaml_data.get('title'):
                    self.add_issue(
                        ValidationLevel.WARNING,
                        "Content",
                        f"Missing title in YAML frontmatter: {file_path.name}",
                        str(file_path),
                        "Add 'title: \"Your Title Here\"' to YAML frontmatter",
                        "missing_title"
                    )
                
                # Validate CSS paths if present
                format_section = yaml_data.get('format', {})
                if isinstance(format_section, dict):
                    html_section = format_section.get('html', {})
                    if isinstance(html_section, dict):
                        css_paths = html_section.get('css', [])
                        if css_paths:
                            self.validate_css_paths(css_paths, file_path)
                
            except yaml.YAMLError as e:
                self.add_issue(
                    ValidationLevel.ERROR,
                    "Content",
                    f"Invalid YAML syntax in {file_path.name}: {str(e)}",
                    str(file_path),
                    "Fix YAML syntax errors in frontmatter",
                    "invalid_yaml"
                )
                
        except Exception as e:
            self.add_issue(
                ValidationLevel.ERROR,
                "File Access",
                f"Cannot read file {file_path.name}: {str(e)}",
                str(file_path),
                "Check file permissions and encoding",
                "file_access_error"
            )

    def validate_css_paths(self, css_paths: List[str], file_path: Path) -> None:
        """Validate CSS path references in YAML frontmatter."""
        for css_path in css_paths:
            # Check if path uses new quarto_code structure
            if 'styles/' in css_path and 'quarto_code/' not in css_path:
                self.add_issue(
                    ValidationLevel.ERROR,
                    "Path References",
                    f"Outdated CSS path in {file_path.name}: {css_path}",
                    str(file_path),
                    f"Update to: {css_path.replace('styles/', 'quarto_code/styles/')}",
                    "outdated_css_path"
                )

    def validate_file_organization(self, structure_data: Dict[str, Any]) -> None:
        """Validate overall file organization and structure."""
        
        # Check for reasonable content distribution
        total_chapters = len(structure_data.get('chapters', []))
        total_sections = sum(len(ch.get('sections', [])) for ch in structure_data.get('chapters', []))
        
        if total_chapters == 0:
            self.add_issue(
                ValidationLevel.WARNING,
                "Organization",
                "No chapters found in content structure",
                structure_data.get('content_path'),
                "Create at least one chapter directory (e.g., 00_introduction)",
                "no_chapters"
            )
        
        if total_sections == 0 and total_chapters > 0:
            self.add_issue(
                ValidationLevel.INFO,
                "Organization",
                "Chapters exist but no sections found",
                structure_data.get('content_path'),
                "Add section directories or files to chapters",
                "no_sections"
            )
        
        # Check for sequential numbering
        chapter_numbers = []
        for chapter in structure_data.get('chapters', []):
            try:
                chapter_numbers.append(int(chapter['prefix']))
            except ValueError:
                continue  # Already caught in naming validation
        
        if chapter_numbers:
            chapter_numbers.sort()
            for i, num in enumerate(chapter_numbers):
                if i > 0 and num != chapter_numbers[i-1] + 1:
                    self.add_issue(
                        ValidationLevel.INFO,
                        "Organization",
                        f"Non-sequential chapter numbering: gap between {chapter_numbers[i-1]:02d} and {num:02d}",
                        structure_data.get('content_path'),
                        "Consider renumbering chapters sequentially",
                        "non_sequential_chapters"
                    )

    def validate_structure(self, structure_data: Dict[str, Any]) -> bool:
        """Run comprehensive structure validation."""
        self.issues.clear()
        
        # Run all validation checks
        self.validate_naming_conventions(structure_data)
        self.validate_required_files(structure_data)
        self.validate_yaml_frontmatter(structure_data)
        self.validate_file_organization(structure_data)
        
        # Return True if no errors (warnings are OK)
        errors = [issue for issue in self.issues if issue.level == ValidationLevel.ERROR]
        return len(errors) == 0

    def get_summary_stats(self) -> Dict[str, int]:
        """Get summary statistics of validation issues."""
        stats = {
            'errors': 0,
            'warnings': 0,
            'info': 0,
            'total': len(self.issues)
        }
        
        for issue in self.issues:
            if issue.level == ValidationLevel.ERROR:
                stats['errors'] += 1
            elif issue.level == ValidationLevel.WARNING:
                stats['warnings'] += 1
            elif issue.level == ValidationLevel.INFO:
                stats['info'] += 1
        
        return stats

def display_validation_results(validator: StructureValidator, verbose: bool = True) -> None:
    """Display validation results in rich console format."""
    
    stats = validator.get_summary_stats()
    
    # Create summary panel
    if stats['errors'] == 0:
        status_color = "green"
        status_icon = "✅"
        status_text = "VALIDATION PASSED"
    else:
        status_color = "red"
        status_icon = "❌"
        status_text = "VALIDATION FAILED"
    
    summary_text = f"[{status_color}]{status_icon} {status_text}[/{status_color}]\n"
    summary_text += f"Errors: [red]{stats['errors']}[/red] | "
    summary_text += f"Warnings: [yellow]{stats['warnings']}[/yellow] | "
    summary_text += f"Info: [blue]{stats['info']}[/blue]"
    
    console.print(Panel(summary_text, title="🔍 Structure Validation Results", border_style=status_color))
    
    if not verbose and stats['total'] == 0:
        console.print("[green]🎉 Perfect! No issues found.[/green]")
        return
    
    # Group issues by category
    issues_by_category = {}
    for issue in validator.issues:
        category = issue.category
        if category not in issues_by_category:
            issues_by_category[category] = []
        issues_by_category[category].append(issue)
    
    # Display issues by category
    for category, issues in issues_by_category.items():
        
        # Create category tree
        tree = Tree(f"📂 [bold]{category}[/bold]")
        
        for issue in issues:
            # Style based on level
            if issue.level == ValidationLevel.ERROR:
                icon = "🔴"
                style = "red"
            elif issue.level == ValidationLevel.WARNING:
                icon = "🟡"
                style = "yellow"
            else:
                icon = "🔵"
                style = "blue"
            
            # Create issue node
            issue_text = f"{icon} [{style}]{issue.message}[/{style}]"
            issue_node = tree.add(issue_text)
            
            # Add file path if available
            if issue.file_path:
                issue_node.add(f"📁 [dim]{issue.file_path}[/dim]")
            
            # Add suggestion if available
            if issue.suggestion:
                issue_node.add(f"💡 [cyan]Suggestion: {issue.suggestion}[/cyan]")
        
        console.print(tree)
        console.print()

def display_validation_table(validator: StructureValidator) -> None:
    """Display validation results in a compact table format."""
    
    if not validator.issues:
        console.print("[green]✅ No validation issues found![/green]")
        return
    
    table = Table(title="🔍 Validation Issues", box=box.ROUNDED)
    table.add_column("Level", style="bold", width=8)
    table.add_column("Category", width=12)
    table.add_column("Issue", min_width=30)
    table.add_column("File", width=25, overflow="ellipsis")
    
    for issue in validator.issues:
        # Style based on level
        if issue.level == ValidationLevel.ERROR:
            level_text = "[red]ERROR[/red]"
        elif issue.level == ValidationLevel.WARNING:
            level_text = "[yellow]WARN[/yellow]"
        else:
            level_text = "[blue]INFO[/blue]"
        
        file_display = Path(issue.file_path).name if issue.file_path else ""
        
        table.add_row(
            level_text,
            issue.category,
            issue.message,
            file_display
        )
    
    console.print(table)


@click.command()
@click.argument('path', type=click.Path(exists=True, path_type=Path), required=False)
@click.option('--input', '-i', 'input_file', type=click.Path(exists=True, path_type=Path),
              help='Use existing scan_structure.py JSON output')
@click.option('--strict', is_flag=True,
              help='Strict mode: only show errors, no warnings')
@click.option('--fix-suggestions', is_flag=True,
              help='Include detailed fix suggestions')
@click.option('--ci', is_flag=True,
              help='CI mode: exit with non-zero code on errors')
@click.option('--table', is_flag=True,
              help='Display results in table format')
@click.option('--verbose', '-v', is_flag=True, default=True,
              help='Verbose output with detailed reporting')
def main(path: Optional[Path], input_file: Optional[Path], strict: bool, 
         fix_suggestions: bool, ci: bool, table: bool, verbose: bool):
    """
    Validate directory structure for educational content organization.
    
    PATH: Base directory to validate (typically 'uumami/')
    
    Can also validate from existing scan_structure.py output using --input.
    """
    
    try:
        # Get structure data
        if input_file:
            with open(input_file, 'r', encoding='utf-8') as f:
                structure_data = json.load(f)
            console.print(f"[dim]📖 Using structure data from: {input_file}[/dim]")
        elif path:
            with console.status("[bold green]Scanning structure for validation..."):
                structure_data = scan_content_structure(path)
        else:
            console.print("[red]❌ Error:[/red] Must provide either PATH or --input file", file=sys.stderr)
            sys.exit(1)
        
        # Create validator
        validator = StructureValidator(
            strict_mode=strict,
            include_warnings=not strict
        )
        
        # Run validation
        with console.status("[bold yellow]Validating structure..."):
            is_valid = validator.validate_structure(structure_data)
        
        # Display results
        if table:
            display_validation_table(validator)
        else:
            display_validation_results(validator, verbose)
        
        # Show fix suggestions if requested
        if fix_suggestions and validator.issues:
            console.print("\n[bold cyan]💡 Fix Suggestions:[/bold cyan]")
            for issue in validator.issues:
                if issue.suggestion:
                    console.print(f"• {issue.category}: [cyan]{issue.suggestion}[/cyan]")
        
        # Exit with appropriate code
        if ci:
            stats = validator.get_summary_stats()
            if stats['errors'] > 0:
                console.print(f"\n[red]❌ CI Mode: Exiting with error code due to {stats['errors']} validation errors[/red]")
                sys.exit(1)
            else:
                console.print(f"\n[green]✅ CI Mode: Validation passed[/green]")
                sys.exit(0)
        
        # Standard exit
        if not is_valid:
            console.print(f"\n[yellow]⚠️  Validation completed with issues. Use --fix-suggestions for help.[/yellow]")
        else:
            console.print(f"\n[green]🎉 Structure validation passed![/green]")
            
    except Exception as e:
        console.print(f"[bold red]❌ Validation Error:[/bold red] {e}", file=sys.stderr)
        if ci:
            sys.exit(1)
        else:
            sys.exit(1)


if __name__ == '__main__':
    main() 