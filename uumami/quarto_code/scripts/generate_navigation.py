#!/usr/bin/env python3
"""
Automated Navigation Generation for Quarto Educational Infrastructure

This script auto-generates the navbar section of _quarto.yml from discovered content
structure while preserving all existing configuration elements. It provides
comprehensive backup/restore functionality and supports multiple operation modes.

Usage:
    python generate_navigation.py <path> [options]
    
Example:
    python generate_navigation.py uumami/
    python generate_navigation.py uumami/ --dry-run --backup
    python generate_navigation.py --restore backup_20250716_123456.yml
"""

import re
import json
import sys
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
import yaml
import click
from rich.console import Console
from rich.panel import Panel
from rich.tree import Tree
from rich.table import Table
from rich.prompt import Confirm
from rich.syntax import Syntax
from rich import box

# Import our content discovery engine
try:
    from scan_structure import scan_content_structure
except ImportError:
    sys.path.append(str(Path(__file__).parent))
    from scan_structure import scan_content_structure

console = Console()

class NavigationGenerator:
    """Main navigation generation engine."""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.quarto_config_path = base_path / '_quarto.yml'
        self.backup_dir = base_path / '.navigation_backups'
        self.backup_dir.mkdir(exist_ok=True)
        
        # Elements to preserve from existing configuration
        self.preserve_elements = {
            'metadata',
            'custom-callout', 
            'website.title',
            'website.page-footer',
            'website.navbar.right',
            'format',
            'project'
        }

    def create_backup(self) -> str:
        """Create timestamped backup of current _quarto.yml."""
        if not self.quarto_config_path.exists():
            raise FileNotFoundError(f"Quarto config not found: {self.quarto_config_path}")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"quarto_backup_{timestamp}.yml"
        backup_path = self.backup_dir / backup_filename
        
        shutil.copy2(self.quarto_config_path, backup_path)
        console.print(f"[green]📦 Backup created:[/green] [cyan]{backup_path}[/cyan]")
        return str(backup_path)

    def list_backups(self) -> List[Path]:
        """List available backup files."""
        if not self.backup_dir.exists():
            return []
        
        backups = list(self.backup_dir.glob("quarto_backup_*.yml"))
        return sorted(backups, reverse=True)  # Most recent first

    def restore_backup(self, backup_path: Union[str, Path]) -> bool:
        """Restore from a backup file."""
        backup_path = Path(backup_path)
        
        if not backup_path.exists():
            console.print(f"[red]❌ Backup file not found:[/red] {backup_path}")
            return False
        
        try:
            shutil.copy2(backup_path, self.quarto_config_path)
            console.print(f"[green]✅ Restored from backup:[/green] [cyan]{backup_path}[/cyan]")
            return True
        except Exception as e:
            console.print(f"[red]❌ Restore failed:[/red] {e}")
            return False

    def load_yaml_config(self) -> Dict[str, Any]:
        """Load and parse the current _quarto.yml configuration."""
        try:
            with open(self.quarto_config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            console.print(f"[red]❌ Failed to load Quarto config:[/red] {e}")
            raise

    def save_yaml_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to _quarto.yml with proper formatting."""
        try:
            with open(self.quarto_config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, indent=2, 
                         allow_unicode=True, sort_keys=False)
        except Exception as e:
            console.print(f"[red]❌ Failed to save Quarto config:[/red] {e}")
            raise

    def generate_section_href(self, section: Dict[str, Any], chapter_name: str) -> str:
        """Generate appropriate href for a section based on its type."""
        if section['type'] == 'file':
            return f"notas/{chapter_name}/{section['file']}"
        else:
            # For directories, link to index file if it exists, otherwise the directory
            section_path = Path(section['path'])
            potential_index = section_path / f"{section['prefix']}_index.qmd"
            if potential_index.exists():
                return f"notas/{chapter_name}/{section['name']}/{section['prefix']}_index.qmd"
            else:
                return f"notas/{chapter_name}/{section['name']}/"

    def generate_course_menu(self, structure_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate the course menu with chapters and sections."""
        menu_items = []
        
        # Add chapters with nested sections
        for chapter in structure_data.get('chapters', []):
            chapter_item = {
                'text': f"{chapter['prefix']}. {chapter['title']}",
                'href': f"notas/{chapter['name']}/{chapter['index_file']}"
            }
            
            # Add nested sections if they exist
            if chapter.get('sections'):
                # For Quarto navbar, we don't use nested contents, just show the chapter
                # Sections will be accessible through the chapter index page
                pass
            
            menu_items.append(chapter_item)
        
        # Add appendices section if any exist
        appendices = structure_data.get('appendices', [])
        if appendices:
            menu_items.append({'section': 'Appendices'})
            for appendix in appendices:
                appendix_item = {
                    'text': f"{appendix['prefix'].upper()}. {appendix['title']}",
                    'href': f"notas/{appendix['name']}/{appendix['index_file']}"
                }
                menu_items.append(appendix_item)
        
        return menu_items

    def generate_development_menu(self) -> List[Dict[str, Any]]:
        """Generate the development documentation menu."""
        menu_items = []
        
        # Check for development documentation
        dev_path = self.base_path / 'quarto_development'
        if dev_path.exists():
            # Add Quarto reference if it exists
            quarto_ref = dev_path / 'c_quarto_appendix' / '00_index.qmd'
            if quarto_ref.exists():
                menu_items.append({
                    'text': 'Quarto Reference',
                    'href': 'quarto_development/c_quarto_appendix/00_index.qmd'
                })
        
        # Check for legacy documentation
        legacy_path = self.base_path / 'legacy'
        if legacy_path.exists():
            # Add setup guides if they exist
            setup_guide = legacy_path / 'a_intro_appendix' / '00_index.qmd'
            if setup_guide.exists():
                menu_items.append({
                    'text': 'Setup Guides (Legacy)',
                    'href': 'legacy/a_intro_appendix/00_index.qmd'
                })
        
        return menu_items

    def preserve_navbar_elements(self, original_config: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and preserve non-auto-generated navbar elements."""
        preserved = {}
        
        # Preserve right-side navbar elements
        navbar = original_config.get('website', {}).get('navbar', {})
        if 'right' in navbar:
            preserved['right'] = navbar['right']
        
        return preserved

    def generate_navbar_structure(self, structure_data: Dict[str, Any], 
                                original_config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate complete navbar structure from content discovery data."""
        
        # Preserve existing navbar elements
        preserved_elements = self.preserve_navbar_elements(original_config)
        
        # Build left-side navigation
        left_nav = [
            {'href': 'index.qmd', 'text': 'Class Notes'},
            {'href': 'syllabus.qmd', 'text': 'Syllabus'},
            {'href': 'schedule.qmd', 'text': 'Schedule'}
        ]
        
        # Add course content menu
        course_menu = self.generate_course_menu(structure_data)
        if course_menu:
            left_nav.append({
                'text': '📚 Course',
                'menu': course_menu
            })
        
        # Add development menu
        dev_menu = self.generate_development_menu()
        if dev_menu:
            left_nav.append({
                'text': '🔧 Development',
                'menu': dev_menu
            })
        
        # Construct navbar
        navbar = {'left': left_nav}
        
        # Add preserved elements
        navbar.update(preserved_elements)
        
        return navbar

    def preserve_existing_config(self, original_config: Dict[str, Any], 
                               new_navbar: Dict[str, Any]) -> Dict[str, Any]:
        """Preserve all non-navbar elements from original configuration."""
        
        # Start with original config
        updated_config = original_config.copy()
        
        # Update only the navbar section
        if 'website' not in updated_config:
            updated_config['website'] = {}
        updated_config['website']['navbar'] = new_navbar
        
        return updated_config

    def validate_generated_config(self, config_path: Optional[Path] = None) -> bool:
        """Validate that the generated configuration is valid."""
        test_path = config_path or self.quarto_config_path
        
        try:
            # Test YAML parsing
            with open(test_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # Basic structure validation
            if not isinstance(config, dict):
                console.print(f"[red]❌ Config is not a valid dictionary[/red]")
                return False
            
            # Check that navbar structure is valid
            website = config.get('website', {})
            if not isinstance(website, dict):
                console.print(f"[red]❌ Website section is not a dictionary[/red]")
                return False
            
            navbar = website.get('navbar', {})
            if not isinstance(navbar, dict):
                console.print(f"[red]❌ Navbar section is not a dictionary[/red]")
                return False
            
            # Validate navbar structure
            if 'left' in navbar and not isinstance(navbar['left'], list):
                console.print(f"[red]❌ Navbar left section is not a list[/red]")
                return False
            
            if 'right' in navbar and not isinstance(navbar['right'], list):
                console.print(f"[red]❌ Navbar right section is not a list[/red]")
                return False
            
            # Test Quarto check (just check if the command exists and config is parseable)
            result = subprocess.run(
                ['quarto', 'check'],
                cwd=self.base_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Don't fail on quarto check issues, just warn
            if result.returncode != 0:
                console.print(f"[yellow]⚠️  Quarto check returned warnings, but config structure is valid[/yellow]")
            
            return True
            
        except Exception as e:
            console.print(f"[red]❌ Validation failed:[/red] {e}")
            return False

    def generate_navigation(self, structure_data: Dict[str, Any], 
                          dry_run: bool = False, backup: bool = True) -> bool:
        """Generate navigation structure and update _quarto.yml."""
        
        try:
            # Create backup if requested
            backup_path = None
            if backup and not dry_run:
                backup_path = self.create_backup()
            
            # Load existing configuration
            original_config = self.load_yaml_config()
            
            # Generate new navbar
            new_navbar = self.generate_navbar_structure(structure_data, original_config)
            
            # Preserve existing configuration with new navbar
            updated_config = self.preserve_existing_config(original_config, new_navbar)
            
            if dry_run:
                console.print("[yellow]📋 Dry run mode - showing generated navbar structure:[/yellow]")
                self.display_navbar_preview(new_navbar)
                return True
            
            # Save updated configuration
            self.save_yaml_config(updated_config)
            
            # Validate the result
            if not self.validate_generated_config():
                console.print("[red]❌ Generated configuration failed validation![/red]")
                if backup_path:
                    console.print("[yellow]🔄 Restoring from backup...[/yellow]")
                    self.restore_backup(backup_path)
                return False
            
            console.print("[green]✅ Navigation successfully generated and validated![/green]")
            return True
            
        except Exception as e:
            console.print(f"[red]❌ Navigation generation failed:[/red] {e}")
            return False

    def display_navbar_preview(self, navbar_structure: Dict[str, Any]) -> None:
        """Display a preview of the generated navbar structure."""
        
        tree = Tree("🧭 [bold blue]Generated Navbar Structure[/bold blue]")
        
        # Left side navigation
        left_tree = tree.add("📍 [bold green]Left Navigation[/bold green]")
        for item in navbar_structure.get('left', []):
            if 'menu' in item:
                # Menu item with sub-items
                menu_node = left_tree.add(f"📁 [yellow]{item['text']}[/yellow]")
                for menu_item in item['menu']:
                    if 'section' in menu_item:
                        menu_node.add(f"📂 [cyan]--- {menu_item['section']} ---[/cyan]")
                    else:
                        menu_text = f"📄 [blue]{menu_item['text']}[/blue]"
                        menu_node.add(menu_text)
            else:
                # Simple link
                left_tree.add(f"🔗 [blue]{item['text']}[/blue]")
        
        # Right side navigation (preserved)
        if 'right' in navbar_structure:
            right_tree = tree.add("📍 [bold green]Right Navigation[/bold green] [dim](preserved)[/dim]")
            for item in navbar_structure['right']:
                if 'icon' in item:
                    right_tree.add(f"🔗 [blue]{item.get('icon', 'link')}[/blue]")
                else:
                    right_tree.add(f"🔗 [blue]{item.get('text', 'link')}[/blue]")
        
        console.print(tree)

    def display_navbar_diff(self, original_navbar: Dict[str, Any], 
                          new_navbar: Dict[str, Any]) -> None:
        """Display differences between original and generated navbar."""
        
        console.print("\n[bold yellow]📊 Navbar Changes Preview:[/bold yellow]")
        
        # Show original structure
        console.print("\n[red]❌ Original (Manual):[/red]")
        original_yaml = yaml.dump({'navbar': original_navbar}, default_flow_style=False)
        syntax = Syntax(original_yaml, "yaml", theme="monokai", line_numbers=True)
        console.print(syntax)
        
        # Show new structure
        console.print("\n[green]✅ Generated (Automatic):[/green]")
        new_yaml = yaml.dump({'navbar': new_navbar}, default_flow_style=False)
        syntax = Syntax(new_yaml, "yaml", theme="monokai", line_numbers=True)
        console.print(syntax)


def display_backup_list(generator: NavigationGenerator) -> None:
    """Display available backup files."""
    backups = generator.list_backups()
    
    if not backups:
        console.print("[yellow]📦 No backups found.[/yellow]")
        return
    
    table = Table(title="📦 Available Backups", box=box.ROUNDED)
    table.add_column("File", style="cyan")
    table.add_column("Created", style="green")
    table.add_column("Size", justify="right", style="blue")
    
    for backup in backups:
        created = datetime.fromtimestamp(backup.stat().st_mtime)
        size = backup.stat().st_size
        table.add_row(
            backup.name,
            created.strftime('%Y-%m-%d %H:%M:%S'),
            f"{size:,} bytes"
        )
    
    console.print(table)


@click.command()
@click.argument('path', type=click.Path(exists=True, path_type=Path), required=False)
@click.option('--dry-run', is_flag=True,
              help='Preview generated navbar without applying changes')
@click.option('--backup/--no-backup', default=True,
              help='Create backup before applying changes')
@click.option('--force', is_flag=True,
              help='Skip confirmation prompts')
@click.option('--restore', type=click.Path(exists=True, path_type=Path),
              help='Restore from specific backup file')
@click.option('--list-backups', is_flag=True,
              help='List available backup files')
@click.option('--verbose', '-v', is_flag=True,
              help='Verbose output with detailed information')
def main(path: Optional[Path], dry_run: bool, backup: bool, force: bool,
         restore: Optional[Path], list_backups: bool, verbose: bool):
    """
    Generate automated navigation for Quarto educational sites.
    
    PATH: Base directory containing _quarto.yml (typically 'uumami/')
    
    Automatically generates navbar structure from content discovery while
    preserving all existing configuration elements.
    """
    
    try:
        # Handle backup restoration
        if restore:
            if not path:
                console.print("[red]❌ Error:[/red] Path required for restore operation")
                sys.exit(1)
            
            generator = NavigationGenerator(path)
            success = generator.restore_backup(restore)
            sys.exit(0 if success else 1)
        
        # Handle backup listing
        if list_backups:
            if not path:
                console.print("[red]❌ Error:[/red] Path required to list backups")
                sys.exit(1)
            
            generator = NavigationGenerator(path)
            display_backup_list(generator)
            sys.exit(0)
        
        # Require path for generation
        if not path:
            console.print("[red]❌ Error:[/red] Path required for navigation generation")
            console.print("Use --help for usage information")
            sys.exit(1)
        
        # Initialize generator
        generator = NavigationGenerator(path)
        
        # Scan content structure
        with console.status("[bold green]Scanning content structure..."):
            structure_data = scan_content_structure(path)
        
        if verbose:
            console.print(f"[dim]📖 Discovered {len(structure_data['chapters'])} chapters, "
                         f"{len(structure_data['appendices'])} appendices[/dim]")
        
        # Load current configuration for preview
        original_config = generator.load_yaml_config()
        original_navbar = original_config.get('website', {}).get('navbar', {})
        new_navbar = generator.generate_navbar_structure(structure_data, original_config)
        
        # Show preview
        if verbose or dry_run:
            generator.display_navbar_preview(new_navbar)
        
        # Show differences if not in dry run
        if not dry_run and verbose:
            generator.display_navbar_diff(original_navbar, new_navbar)
        
        # Confirmation for actual changes
        if not dry_run and not force:
            if not Confirm.ask(f"\n[yellow]🔄 Generate navigation for {path}?[/yellow]"):
                console.print("[blue]👍 Operation cancelled by user.[/blue]")
                sys.exit(0)
        
        # Generate navigation
        with console.status("[bold yellow]Generating navigation..."):
            success = generator.generate_navigation(
                structure_data, 
                dry_run=dry_run, 
                backup=backup
            )
        
        if success:
            if dry_run:
                console.print("\n[green]📋 Dry run completed successfully![/green]")
                console.print("[blue]💡 Use without --dry-run to apply changes[/blue]")
            else:
                console.print("\n[green]🎉 Navigation generation completed![/green]")
                console.print("[blue]💡 Test your site with 'quarto render'[/blue]")
        else:
            console.print("\n[red]❌ Navigation generation failed![/red]")
            sys.exit(1)
            
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  Operation cancelled by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]❌ Generation Error:[/bold red] {e}")
        if verbose:
            console.print_exception()
        sys.exit(1)


if __name__ == '__main__':
    main()
