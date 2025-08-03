#!/usr/bin/env python3
"""
Content Validation Script for GitHub Class Template Framework

This script validates all content files for proper metadata, file naming,
and framework compliance. Provides rich console output and detailed reporting.

Usage:
    python3 validate_content.py [base_directory]
    
Exit codes:
    0: All validations passed
    1: Validation errors found (in strict mode)
    2: Script execution error
"""

import sys
import argparse
from pathlib import Path
from typing import List, Dict, Tuple
import yaml

from rich.console import Console
from rich.progress import Progress, TaskID
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

# Import our metadata system (handle different execution contexts)
try:
    from content_metadata import (
        MetadataParser, discover_content_files, validate_file_naming,
        REQUIRED_FIELDS, OPTIONAL_FIELDS, CONTENT_TYPES
    )
except ImportError:
    # Try relative import for different execution contexts
    import sys
    from pathlib import Path
    script_dir = Path(__file__).parent
    sys.path.insert(0, str(script_dir))
    from content_metadata import (
        MetadataParser, discover_content_files, validate_file_naming,
        REQUIRED_FIELDS, OPTIONAL_FIELDS, CONTENT_TYPES
    )

# Import additional functions for discussions
try:
    from content_metadata import (
        generate_creation_based_slug, get_all_slugs_from_files, should_have_discussions,
        DISCUSSION_ENABLED_TYPES
    )
except ImportError:
    # Functions not available in this context
    def generate_creation_based_slug(*args, **kwargs):
        return None
    def get_all_slugs_from_files(*args, **kwargs):
        return set()
    def should_have_discussions(*args, **kwargs):
        return False
    DISCUSSION_ENABLED_TYPES = []

console = Console()

class ContentValidator:
    """Main content validation system"""
    
    def __init__(self, base_dir: Path, strict_mode: bool = False):
        self.base_dir = base_dir
        self.strict_mode = strict_mode
        self.parser = MetadataParser()
        
        # Validation statistics
        self.stats = {
            'files_processed': 0,
            'files_valid': 0,
            'files_with_errors': 0,
            'files_with_warnings': 0,
            'total_errors': 0,
            'total_warnings': 0
        }
        
        # Detailed results for reporting
        self.results = []
        
        # Track slugs for discussions
        self.existing_slugs = set()
        self.files_with_generated_slugs = []
    
    def validate_all_content(self) -> bool:
        """
        Validate all content files in the base directory.
        
        Returns:
            bool: True if all validations passed (or warnings only), False if errors found
        """
        console.print(Panel.fit(
            "[bold blue]Content Validation System[/bold blue]\n"
            f"Base directory: [cyan]{self.base_dir}[/cyan]\n"
            f"Strict mode: [{'red' if self.strict_mode else 'green'}]{self.strict_mode}[/]",
            title="Framework Content Validator"
        ))
        
        # Discover content files
        content_files = discover_content_files(self.base_dir)
        
        if not content_files:
            console.print("[yellow]⚠️  No content files found for validation[/yellow]")
            return True
        
        console.print(f"\n[bold]Found {len(content_files)} content files[/bold]")
        
        # Validate each file with progress bar
        with Progress() as progress:
            task = progress.add_task("[cyan]Validating content...", total=len(content_files))
            
            for file_path in content_files:
                self._validate_single_file(file_path)
                progress.update(task, advance=1)
        
        # Display results
        self._display_results()
        
        # Return success/failure based on strict mode and errors
        if self.stats['files_with_errors'] > 0:
            return not self.strict_mode
        return True
    
    def _validate_single_file(self, file_path: Path) -> None:
        """
        Validate a single content file.
        
        Args:
            file_path: Path to the file to validate
        """
        self.stats['files_processed'] += 1
        
        # Relative path for display
        rel_path = file_path.relative_to(self.base_dir)
        
        # Initialize result record
        result = {
            'file': str(rel_path),
            'errors': [],
            'warnings': [],
            'metadata': {}
        }
        
        # File naming validation
        naming_errors = validate_file_naming(file_path)
        result['errors'].extend(naming_errors)
        
        # Metadata validation
        metadata, meta_errors, meta_warnings = self.parser.parse_frontmatter(file_path)
        result['metadata'] = metadata
        result['errors'].extend(meta_errors)
        result['warnings'].extend(meta_warnings)
        
        # Update statistics
        if result['errors']:
            self.stats['files_with_errors'] += 1
            self.stats['total_errors'] += len(result['errors'])
        else:
            self.stats['files_valid'] += 1
        
        if result['warnings']:
            self.stats['files_with_warnings'] += 1
            self.stats['total_warnings'] += len(result['warnings'])
        
        self.results.append(result)
    
    def _display_results(self) -> None:
        """Display validation results with rich formatting"""
        
        # Summary statistics
        self._display_summary()
        
        # Detailed error reports
        if self.stats['files_with_errors'] > 0:
            self._display_errors()
        
        # Warning reports (if any)
        if self.stats['files_with_warnings'] > 0:
            self._display_warnings()
        
        # Success message or failure summary
        if self.stats['files_with_errors'] == 0:
            console.print(f"\n[bold green]✅ All {self.stats['files_processed']} files passed validation![/bold green]")
            if self.stats['total_warnings'] > 0:
                console.print(f"[yellow]⚠️  {self.stats['total_warnings']} warnings found (non-critical)[/yellow]")
        else:
            console.print(f"\n[bold red]❌ Validation failed with {self.stats['total_errors']} errors[/bold red]")
    
    def _display_summary(self) -> None:
        """Display summary statistics table"""
        
        table = Table(title="Validation Summary", box=box.ROUNDED)
        table.add_column("Metric", style="bold")
        table.add_column("Count", justify="right")
        table.add_column("Status", justify="center")
        
        # Add rows with status colors
        table.add_row(
            "Files Processed", 
            str(self.stats['files_processed']), 
            "📄"
        )
        table.add_row(
            "Valid Files", 
            str(self.stats['files_valid']), 
            "[green]✅[/green]" if self.stats['files_valid'] > 0 else "—"
        )
        table.add_row(
            "Files with Errors", 
            str(self.stats['files_with_errors']), 
            "[red]❌[/red]" if self.stats['files_with_errors'] > 0 else "[green]✅[/green]"
        )
        table.add_row(
            "Files with Warnings", 
            str(self.stats['files_with_warnings']), 
            "[yellow]⚠️[/yellow]" if self.stats['files_with_warnings'] > 0 else "—"
        )
        table.add_row(
            "Total Errors", 
            str(self.stats['total_errors']), 
            "[red]❌[/red]" if self.stats['total_errors'] > 0 else "[green]✅[/green]"
        )
        table.add_row(
            "Total Warnings", 
            str(self.stats['total_warnings']), 
            "[yellow]⚠️[/yellow]" if self.stats['total_warnings'] > 0 else "—"
        )
        
        console.print(table)
    
    def _display_errors(self) -> None:
        """Display detailed error reports"""
        
        console.print(Panel.fit(
            "[bold red]Validation Errors[/bold red]",
            title="❌ Issues Requiring Attention"
        ))
        
        for result in self.results:
            if not result['errors']:
                continue
            
            console.print(f"\n[bold red]📄 {result['file']}[/bold red]")
            for error in result['errors']:
                console.print(f"   [red]• {error}[/red]")
    
    def _display_warnings(self) -> None:
        """Display warning reports"""
        
        console.print(Panel.fit(
            "[bold yellow]Validation Warnings[/bold yellow]",
            title="⚠️  Non-Critical Issues"
        ))
        
        for result in self.results:
            if not result['warnings']:
                continue
            
            console.print(f"\n[bold yellow]📄 {result['file']}[/bold yellow]")
            for warning in result['warnings']:
                console.print(f"   [yellow]• {warning}[/yellow]")

def load_validation_config(base_dir: Path) -> Dict:
    """
    Load validation configuration from dna.yml
    
    Args:
        base_dir: Base directory to search for dna.yml
        
    Returns:
        Configuration dictionary
    """
    # Try multiple locations for dna.yml
    dna_paths = [
        base_dir / 'dna.yml',  # Same directory
        base_dir / '../dna.yml',  # Parent directory (for student directories)
        base_dir / '../../dna.yml'  # Repository root (for nested student directories)
    ]
    
    config = {
        'strict_validation': False,
        'content_validation': True
    }
    
    for dna_path in dna_paths:
        if dna_path.exists():
            try:
                with open(dna_path, 'r') as f:
                    dna_config = yaml.safe_load(f) or {}
                
                if 'strict_validation' in dna_config:
                    config['strict_validation'] = bool(dna_config['strict_validation'])
                if 'content_validation' in dna_config:
                    config['content_validation'] = bool(dna_config['content_validation'])
                break  # Use the first found dna.yml
                    
            except Exception as e:
                console.print(f"[yellow]Warning: Could not read {dna_path}: {e}[/yellow]")
                continue
    
    return config

def main():
    """Main entry point for content validation"""
    
    parser = argparse.ArgumentParser(
        description="Validate content files for framework compliance"
    )
    parser.add_argument(
        'base_dir', 
        nargs='?', 
        default='.',
        help='Base directory to validate (default: current directory)'
    )
    parser.add_argument(
        '--strict', 
        action='store_true',
        help='Enable strict mode (fail on any errors)'
    )
    parser.add_argument(
        '--no-config', 
        action='store_true',
        help='Skip loading configuration from dna.yml'
    )
    
    args = parser.parse_args()
    
    # Resolve base directory
    base_dir = Path(args.base_dir).resolve()
    if not base_dir.exists():
        console.print(f"[red]Error: Directory {base_dir} does not exist[/red]")
        sys.exit(2)
    
    # Load configuration
    if args.no_config:
        config = {'strict_validation': args.strict, 'content_validation': True}
    else:
        config = load_validation_config(base_dir)
        # Command line --strict overrides config
        if args.strict:
            config['strict_validation'] = True
    
    # Check if validation is enabled
    if not config['content_validation']:
        console.print("[yellow]Content validation is disabled in configuration[/yellow]")
        sys.exit(0)
    
    try:
        # Run validation
        validator = ContentValidator(base_dir, config['strict_validation'])
        success = validator.validate_all_content()
        
        # Exit with appropriate code
        if success:
            sys.exit(0)
        else:
            console.print(f"\n[red]Validation failed in strict mode[/red]")
            sys.exit(1)
            
    except Exception as e:
        console.print(f"[red]Validation script error: {e}[/red]")
        sys.exit(2)

if __name__ == "__main__":
    main() 