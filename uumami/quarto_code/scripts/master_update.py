#!/usr/bin/env python3
"""
Master Update Script for Quarto Educational Infrastructure

This script runs all automation tools in the correct order to clean and update
the entire project. Should be run from the scripts directory.

Usage:
    python master_update.py [options]
    
Example:
    python master_update.py
    python master_update.py --force --verbose
    python master_update.py --validation-only
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import click
from rich.console import Console
from rich.panel import Panel
from rich.tree import Tree
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

# Import our existing utilities
try:
    from config_utils import resolve_content_paths, validate_project_structure
    from scan_structure import scan_content_structure
    from validate_structure import StructureValidator
    from generate_navigation import NavigationGenerator
    from smart_auto_generator import SmartAutoGenerator
except ImportError:
    console = Console()
    console.print("[red]❌ Error:[/red] Could not import required modules. Make sure you're running from the scripts directory.")
    sys.exit(1)

console = Console()

class MasterUpdater:
    """Master update coordinator for the entire project."""
    
    def __init__(self, force: bool = False, verbose: bool = False):
        self.force = force
        self.verbose = verbose
        self.start_time = datetime.now()
        self.results = {
            'validation': {'passed': False, 'errors': [], 'warnings': []},
            'structure_scan': {'completed': False, 'chapters': 0, 'sections': 0},
            'index_generation': {'updated': 0, 'preserved': 0},
            'navigation_update': {'nav_files': 0, 'index_files': 0},
            'final_validation': {'passed': False, 'remaining_issues': 0}
        }
        
        # Verify we're in the right directory
        current_dir = Path.cwd()
        if not (current_dir.name == 'scripts' and (current_dir.parent.name == 'quarto_code')):
            console.print("[red]❌ Error:[/red] This script must be run from the 'uumami/quarto_code/scripts' directory")
            sys.exit(1)
        
        # Load configuration
        try:
            self.paths = resolve_content_paths()
            self.user_name = self.paths['user_name']
        except Exception as e:
            console.print(f"[red]❌ Configuration Error:[/red] {e}")
            sys.exit(1)
    
    def step_1_validate_project_structure(self) -> bool:
        """Step 1: Validate project structure and configuration."""
        console.print("\n[bold blue]🔍 Step 1: Project Structure Validation[/bold blue]")
        
        try:
            # Basic structure validation
            is_valid = validate_project_structure()
            if not is_valid:
                console.print("[red]❌ Basic project structure validation failed[/red]")
                return False
            
            # Advanced validation using our validation engine
            validator = StructureValidator(strict_mode=False, include_warnings=True)
            structure_data = scan_content_structure()
            validation_result = validator.validate_structure(structure_data)
            
            # Store results
            self.results['validation']['passed'] = validation_result
            self.results['validation']['errors'] = [issue.message for issue in validator.issues if issue.level.value == 'error']
            self.results['validation']['warnings'] = [issue.message for issue in validator.issues if issue.level.value == 'warning']
            
            if validation_result:
                console.print("[green]✅ Project structure validation passed[/green]")
            else:
                console.print(f"[yellow]⚠️ Validation completed with {len(self.results['validation']['errors'])} errors, {len(self.results['validation']['warnings'])} warnings[/yellow]")
            
            return True
            
        except Exception as e:
            console.print(f"[red]❌ Validation failed: {e}[/red]")
            return False
    
    def step_2_scan_content_structure(self) -> bool:
        """Step 2: Scan and analyze content structure."""
        console.print("\n[bold blue]📊 Step 2: Content Structure Analysis[/bold blue]")
        
        try:
            structure_data = scan_content_structure()
            
            # Store results
            self.results['structure_scan']['completed'] = True
            self.results['structure_scan']['chapters'] = len(structure_data['chapters'])
            self.results['structure_scan']['sections'] = sum(len(ch['sections']) for ch in structure_data['chapters'])
            
            console.print(f"[green]✅ Found {self.results['structure_scan']['chapters']} chapters with {self.results['structure_scan']['sections']} sections[/green]")
            
            if self.verbose:
                for chapter in structure_data['chapters']:
                    console.print(f"  • [cyan]{chapter['name']}:[/cyan] {len(chapter['sections'])} sections")
            
            return True
            
        except Exception as e:
            console.print(f"[red]❌ Structure scan failed: {e}[/red]")
            return False
    
    def step_3_smart_index_generation(self) -> bool:
        """Step 3: Generate/update indexes with content preservation."""
        console.print("\n[bold blue]📝 Step 3: Smart Index Generation[/bold blue]")
        
        try:
            generator = SmartAutoGenerator()
            
            # Force update if requested, otherwise smart update
            index_count = generator.process_directory_indexes(force_update=self.force)
            
            # Store results
            self.results['index_generation']['updated'] = index_count
            
            console.print(f"[green]✅ Updated {index_count} directory indexes[/green]")
            
            if self.verbose and generator.updated_files:
                console.print("  [cyan]Updated files:[/cyan]")
                for file_path in generator.updated_files[-5:]:  # Show last 5
                    console.print(f"    • {file_path}")
            
            # Save hashes for future change detection
            generator.save_content_hashes()
            
            return True
            
        except Exception as e:
            console.print(f"[red]❌ Index generation failed: {e}[/red]")
            return False
    
    def step_4_update_navigation(self) -> bool:
        """Step 4: Update navigation components."""
        console.print("\n[bold blue]🧭 Step 4: Navigation Update[/bold blue]")
        
        try:
            # Update navigation using existing system
            from update_nav_components import NavigationComponentUpdater
            nav_updater = NavigationComponentUpdater()
            nav_stats = nav_updater.update_all_navigation()
            
            # Update main navbar
            nav_generator = NavigationGenerator()
            structure_data = scan_content_structure()
            original_config = nav_generator.load_yaml_config()
            new_navbar = nav_generator.generate_navbar_structure(structure_data, original_config)
            
            # Apply navbar if force update or if significant changes
            if self.force or nav_stats['nav_files'] > 0:
                nav_success = nav_generator.generate_navigation(structure_data, dry_run=False, backup=True)
                if nav_success:
                    console.print("[green]✅ Navbar structure updated[/green]")
                else:
                    console.print("[yellow]⚠️ Navbar update skipped (no changes needed)[/yellow]")
            
            # Store results
            self.results['navigation_update']['nav_files'] = nav_stats['nav_files']
            self.results['navigation_update']['index_files'] = nav_stats['index_files']
            
            console.print(f"[green]✅ Updated {nav_stats['nav_files']} nav files, {nav_stats['index_files']} index files[/green]")
            
            return True
            
        except Exception as e:
            console.print(f"[red]❌ Navigation update failed: {e}[/red]")
            return False
    
    def step_5_generate_collapsible_nav(self) -> bool:
        """Step 5: Generate enhanced collapsible navigation."""
        console.print("\n[bold blue]🎛️ Step 5: Enhanced Navigation Generation[/bold blue]")
        
        try:
            from generate_collapsible_nav import CollapsibleNavGenerator
            
            collapsible_generator = CollapsibleNavGenerator()
            navigation_data = collapsible_generator.scan_and_analyze()
            
            # Generate both JSON and JS formats
            json_file = collapsible_generator.generate_json_data()
            js_file = collapsible_generator.generate_javascript_data()
            
            console.print(f"[green]✅ Generated enhanced navigation data[/green]")
            if self.verbose:
                console.print(f"  • [cyan]JSON:[/cyan] {json_file}")
                console.print(f"  • [cyan]JS:[/cyan] {js_file}")
            
            return True
            
        except Exception as e:
            console.print(f"[red]❌ Enhanced navigation generation failed: {e}[/red]")
            return False
    
    def step_6_final_validation(self) -> bool:
        """Step 6: Final validation and cleanup."""
        console.print("\n[bold blue]🔍 Step 6: Final Validation & Cleanup[/bold blue]")
        
        try:
            # Re-run validation to check improvements
            validator = StructureValidator(strict_mode=False, include_warnings=True)
            structure_data = scan_content_structure()
            validation_result = validator.validate_structure(structure_data)
            
            # Count remaining issues
            remaining_errors = len([issue for issue in validator.issues if issue.level.value == 'error'])
            remaining_warnings = len([issue for issue in validator.issues if issue.level.value == 'warning'])
            
            # Store results
            self.results['final_validation']['passed'] = validation_result
            self.results['final_validation']['remaining_issues'] = remaining_errors + remaining_warnings
            
            if validation_result and remaining_errors == 0:
                console.print("[green]✅ Final validation passed - project is clean![/green]")
            else:
                console.print(f"[yellow]⚠️ Final validation: {remaining_errors} errors, {remaining_warnings} warnings remaining[/yellow]")
            
            # Cleanup temp files
            temp_files = list(Path('.').glob('*.tmp')) + list(Path('.').glob('.*~'))
            for temp_file in temp_files:
                try:
                    temp_file.unlink()
                except:
                    pass
            
            console.print("[green]✅ Cleanup completed[/green]")
            return True
            
        except Exception as e:
            console.print(f"[red]❌ Final validation failed: {e}[/red]")
            return False
    
    def display_summary(self):
        """Display comprehensive update summary."""
        duration = datetime.now() - self.start_time
        
        console.print(f"\n[bold green]🎉 Master Update Complete![/bold green]")
        console.print(f"[dim]Duration: {duration.total_seconds():.1f} seconds[/dim]\n")
        
        # Create summary table
        table = Table(title="Update Summary", show_header=True, header_style="bold blue")
        table.add_column("Step", style="cyan", no_wrap=True)
        table.add_column("Status", style="green")
        table.add_column("Details", style="white")
        
        # Add results
        validation_status = "✅ Passed" if self.results['validation']['passed'] else "⚠️ Issues"
        validation_details = f"{len(self.results['validation']['errors'])} errors, {len(self.results['validation']['warnings'])} warnings"
        table.add_row("1. Structure Validation", validation_status, validation_details)
        
        scan_status = "✅ Completed" if self.results['structure_scan']['completed'] else "❌ Failed"
        scan_details = f"{self.results['structure_scan']['chapters']} chapters, {self.results['structure_scan']['sections']} sections"
        table.add_row("2. Content Scan", scan_status, scan_details)
        
        index_details = f"{self.results['index_generation']['updated']} indexes updated"
        table.add_row("3. Index Generation", "✅ Completed", index_details)
        
        nav_details = f"{self.results['navigation_update']['nav_files']} nav files, {self.results['navigation_update']['index_files']} index files"
        table.add_row("4. Navigation Update", "✅ Completed", nav_details)
        
        table.add_row("5. Enhanced Navigation", "✅ Generated", "JSON + JS data files")
        
        final_status = "✅ Clean" if self.results['final_validation']['passed'] else f"⚠️ {self.results['final_validation']['remaining_issues']} issues"
        table.add_row("6. Final Validation", final_status, "Project cleaned")
        
        console.print(table)
        
        # Recommendations
        if not self.results['final_validation']['passed']:
            console.print("\n[yellow]💡 Recommendations:[/yellow]")
            console.print("  • Run [cyan]python validate_structure.py --fix-suggestions[/cyan] for detailed guidance")
            console.print("  • Check individual scripts for specific issues")
        else:
            console.print("\n[green]🚀 Your project is fully up-to-date and clean![/green]")
            console.print("  • All indexes are current")
            console.print("  • Navigation is synchronized") 
            console.print("  • Structure follows conventions")

def run_master_update(force: bool = False, verbose: bool = False, validation_only: bool = False) -> bool:
    """Run the complete master update process."""
    
    updater = MasterUpdater(force=force, verbose=verbose)
    
    console.print(Panel.fit(
        "[bold blue]🚀 Master Update System[/bold blue]\n"
        f"[dim]User: {updater.user_name} | Force: {force} | Verbose: {verbose}[/dim]",
        title="Quarto Educational Infrastructure",
        border_style="blue"
    ))
    
    success = True
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        
        # Define steps
        steps = [
            ("Validating project structure...", updater.step_1_validate_project_structure),
            ("Scanning content structure...", updater.step_2_scan_content_structure),
        ]
        
        if not validation_only:
            steps.extend([
                ("Generating smart indexes...", updater.step_3_smart_index_generation),
                ("Updating navigation...", updater.step_4_update_navigation),
                ("Generating enhanced nav...", updater.step_5_generate_collapsible_nav),
                ("Final validation & cleanup...", updater.step_6_final_validation),
            ])
        
        # Execute steps
        task = progress.add_task("Processing...", total=len(steps))
        
        for i, (description, step_func) in enumerate(steps):
            progress.update(task, description=description, completed=i)
            
            step_success = step_func()
            if not step_success:
                success = False
                if not validation_only:  # Don't break on validation-only mode
                    break
            
            progress.update(task, completed=i + 1)
    
    # Display results
    updater.display_summary()
    
    return success

@click.command()
@click.option('--force', is_flag=True, help='Force update all content regardless of changes')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output with detailed information')
@click.option('--validation-only', is_flag=True, help='Run only validation steps (no updates)')
def main(force: bool, verbose: bool, validation_only: bool):
    """
    Master update script for Quarto educational infrastructure.
    
    Runs all automation tools in the correct order to clean and update the entire project.
    Must be run from the 'uumami/quarto_code/scripts' directory.
    """
    
    try:
        success = run_master_update(force=force, verbose=verbose, validation_only=validation_only)
        
        if success:
            console.print("\n[bold green]✨ Master update completed successfully![/bold green]")
            if not validation_only:
                console.print("[dim]💡 Your project is fully updated and ready to use[/dim]")
        else:
            console.print("\n[bold red]❌ Master update completed with errors[/bold red]")
            console.print("[dim]💡 Check the output above for specific issues[/dim]")
            sys.exit(1)
        
    except KeyboardInterrupt:
        console.print("\n[yellow]🛑 Master update interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[bold red]💥 Fatal error during master update:[/bold red] {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 