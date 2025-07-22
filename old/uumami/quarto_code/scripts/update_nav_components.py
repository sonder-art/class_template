#!/usr/bin/env python3
"""
Navigation Component Updater for Quarto Educational Infrastructure

ROLE: Helper script that updates _nav.qmd files and chapter index files to match
actual file organization. Called by master_update.py during navigation updates.

USAGE: Typically called by master_update.py, but can be run standalone for testing.

Key Features:
- Updates JavaScript arrays in _nav.qmd files
- Updates HTML breadcrumb lists
- Updates Markdown link sections
- Updates chapter index navigation links
- Synchronizes all navigation components automatically
- Creates missing files (syllabus.qmd, schedule.qmd) if needed

Usage:
    python update_nav_components.py [options]
    
Example:
    python update_nav_components.py --dry-run
    python update_nav_components.py --verbose
"""

import re
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import yaml
import click
from rich.console import Console
from rich.panel import Panel
from rich.tree import Tree
from rich.table import Table

# Import our existing utilities
try:
    from scan_structure import scan_content_structure
    from config_utils import resolve_content_paths, get_user_name
except ImportError:
    sys.path.append(str(Path(__file__).parent))
    from scan_structure import scan_content_structure
    from config_utils import resolve_content_paths, get_user_name

console = Console()

class NavigationComponentUpdater:
    """Updates navigation components to match actual file structure."""
    
    def __init__(self):
        # Use configuration utilities to resolve paths
        try:
            self.paths = resolve_content_paths()
            self.user_name = self.paths['user_name']
        except Exception as e:
            console.print(f"[red]❌ Error loading configuration:[/red] {e}")
            sys.exit(1)
        
        # Get current content structure
        self.structure_data = scan_content_structure()
        self.updated_files = []
        self.errors = []
    
    def generate_chapter_nav_pages(self, chapter: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate the pages array for a chapter's _nav.qmd file."""
        pages = []
        
        # Add chapter index
        pages.append({
            'file': '00_index.qmd',
            'title': chapter['title']
        })
        
        # Add sections
        for section in chapter['sections']:
            if section['type'] == 'directory':
                # Directory-based section - link to its index
                section_file = f"{section['name']}/00_index.qmd"
                pages.append({
                    'file': section_file,
                    'title': f"{section['prefix']}. {section['title']}"
                })
                
                # Add subsection files if they exist
                for subsection in section.get('subsections', []):
                    if subsection['type'] == 'file' and subsection['file'] != '00_index.qmd':
                        subsection_file = f"{section['name']}/{subsection['file']}"
                        pages.append({
                            'file': subsection_file,
                            'title': f"{section['prefix']}.{len(pages)} {subsection['title']}"
                        })
            else:
                # File-based section
                pages.append({
                    'file': section['file'],
                    'title': f"{section['prefix']}. {section['title']}"
                })
        
        return pages
    
    def generate_chapter_overview_links(self, chapter: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate overview links for chapter index files."""
        links = []
        
        for section in chapter['sections']:
            if section['type'] == 'directory':
                # Directory-based section
                link = {
                    'href': f"./{section['name']}/00_index.qmd",
                    'title': f"{section['prefix']}. {section['title']}"
                }
                links.append(link)
                
                # Add important subsection files
                for subsection in section.get('subsections', []):
                    if subsection['type'] == 'file' and subsection['file'] != '00_index.qmd':
                        link = {
                            'href': f"./{section['name']}/{subsection['file']}",
                            'title': f"{section['prefix']}.{len(links)} {subsection['title']}"
                        }
                        links.append(link)
            else:
                # File-based section
                link = {
                    'href': f"./{section['file']}",
                    'title': f"{section['prefix']}. {section['title']}"
                }
                links.append(link)
        
        return links
    
    def update_nav_file(self, chapter: Dict[str, Any], dry_run: bool = False) -> bool:
        """Update a chapter's _nav.qmd file."""
        chapter_path = Path(chapter['path'])
        nav_file = chapter_path / '_nav.qmd'
        
        if not nav_file.exists():
            console.print(f"[yellow]⚠️ No _nav.qmd found in {chapter_path}[/yellow]")
            return False
        
        try:
            # Read current content
            current_content = nav_file.read_text(encoding='utf-8')
            updated_content = current_content
            
            # Generate new pages array
            pages = self.generate_chapter_nav_pages(chapter)
            pages_js = json.dumps(pages, indent=4)
            
            # 1. Update JavaScript pages array
            pattern = r'const pages = \[\s*{[^}]*}(?:\s*,\s*{[^}]*})*\s*\];'
            replacement = f'const pages = {pages_js};'
            updated_content = re.sub(pattern, replacement, updated_content, flags=re.DOTALL)
            
            # 2. Update markdown links section
            # Find the callout-note section with Setup Guides
            markdown_links = []
            for page in pages[1:]:  # Skip the index page
                title = page['title']
                file = page['file']
                markdown_links.append(f"- [**{title}**](./{file})")
            
            new_markdown = '\n'.join(markdown_links)
            
            # Replace the markdown links inside the callout-note
            pattern = r'(::: \{\.callout-note \.fw-light\}\s*#### Setup Guides\s*)(.*?)(\s*:::)'
            def replace_markdown(match):
                return f"{match.group(1)}\n\n{new_markdown}\n\n{match.group(3)}"
            
            updated_content = re.sub(pattern, replace_markdown, updated_content, flags=re.DOTALL)
            
            # 3. Update HTML breadcrumb list
            html_links = []
            for page in pages:
                title = page['title']
                file = page['file']
                # Clean up title for HTML (remove number prefix for cleaner display)
                clean_title = title.replace(chapter['title'], 'Welcome') if file == '00_index.qmd' else title
                html_links.append(f'        <li><a href="./{file}">{clean_title}</a></li>')
            
            new_html = '\n'.join(html_links)
            
            # Replace the HTML breadcrumb list
            pattern = r'(<ul class="breadcrumb-list">\s*)(.*?)(\s*</ul>)'
            def replace_html(match):
                return f"{match.group(1)}\n{new_html}\n{match.group(3)}"
            
            updated_content = re.sub(pattern, replace_html, updated_content, flags=re.DOTALL)
            
            if updated_content == current_content:
                console.print(f"[yellow]⚠️ No changes needed for {nav_file}[/yellow]")
                return False
            
            if dry_run:
                console.print(f"[cyan]📋 Would update:[/cyan] {nav_file}")
                console.print(f"[dim]   New pages: {len(pages)} items (JS, MD, HTML)[/dim]")
                return True
            else:
                nav_file.write_text(updated_content, encoding='utf-8')
                self.updated_files.append(nav_file)
                console.print(f"[green]✅ Updated:[/green] {nav_file}")
                return True
                
        except Exception as e:
            error_msg = f"Failed to update {nav_file}: {e}"
            self.errors.append(error_msg)
            console.print(f"[red]❌ {error_msg}[/red]")
            return False
    
    def update_chapter_index(self, chapter: Dict[str, Any], dry_run: bool = False) -> bool:
        """Update a chapter's 00_index.qmd file with correct navigation links."""
        chapter_path = Path(chapter['path'])
        index_file = chapter_path / '00_index.qmd'
        
        if not index_file.exists():
            console.print(f"[yellow]⚠️ No 00_index.qmd found in {chapter_path}[/yellow]")
            return False
        
        try:
            # Read current content
            current_content = index_file.read_text(encoding='utf-8')
            
            # Generate new overview links
            links = self.generate_chapter_overview_links(chapter)
            
            # Create new checklist content
            checklist_items = []
            for i, link in enumerate(links, 1):
                checklist_items.append(f'{i}.  [**{link["title"]}**]({link["href"]})')
            
            new_checklist = '\n'.join(checklist_items)
            
            # Find and replace the setup checklist
            # Look for the callout-note with Setup Checklist
            pattern = r'(::: \{\.callout-note\}\s*### Setup Checklist\s*)(.*?)(\s*:::)'
            
            def replace_checklist(match):
                return f"{match.group(1)}\n\n{new_checklist}\n{match.group(3)}"
            
            updated_content = re.sub(pattern, replace_checklist, current_content, flags=re.DOTALL)
            
            if updated_content == current_content:
                console.print(f"[yellow]⚠️ No Setup Checklist found in {index_file}[/yellow]")
                return False
            
            if dry_run:
                console.print(f"[cyan]📋 Would update:[/cyan] {index_file}")
                console.print(f"[dim]   New links: {len(links)} items[/dim]")
                return True
            else:
                index_file.write_text(updated_content, encoding='utf-8')
                self.updated_files.append(index_file)
                console.print(f"[green]✅ Updated:[/green] {index_file}")
                return True
                
        except Exception as e:
            error_msg = f"Failed to update {index_file}: {e}"
            self.errors.append(error_msg)
            console.print(f"[red]❌ {error_msg}[/red]")
            return False
    
    def update_all_navigation(self, dry_run: bool = False) -> Dict[str, int]:
        """Update all navigation components."""
        stats = {'nav_files': 0, 'index_files': 0, 'errors': 0}
        
        for chapter in self.structure_data['chapters']:
            console.print(f"\n[bold blue]📁 Processing Chapter:[/bold blue] {chapter['name']}")
            
            # Update _nav.qmd
            if self.update_nav_file(chapter, dry_run):
                stats['nav_files'] += 1
            
            # Update 00_index.qmd
            if self.update_chapter_index(chapter, dry_run):
                stats['index_files'] += 1
        
        stats['errors'] = len(self.errors)
        return stats
    
    def create_missing_files(self, dry_run: bool = False) -> int:
        """Create missing files that are referenced in navigation."""
        created_count = 0
        
        # Create syllabus.qmd if missing
        syllabus_file = self.paths['user_root'] / 'syllabus.qmd'
        if not syllabus_file.exists():
            syllabus_content = '''---
title: "Course Syllabus"
---

# Course Syllabus

## Course Information

- **Course Title**: {{< meta class_name >}}
- **Course Code**: {{< meta course_code >}}
- **Period**: {{< meta period >}}
- **Instructor**: {{< meta instructor_name >}}
- **Email**: {{< meta instructor_email >}}
- **Office Hours**: {{< meta office_hours >}}

## Course Description

This course provides a comprehensive introduction to modern software development practices...

## Learning Objectives

By the end of this course, students will be able to:

1. Write clean, efficient, and well-documented code
2. Use version control systems effectively
3. Collaborate on software projects using modern tools
4. Apply best practices for software development

## Schedule

Please see the [course schedule](schedule.qmd) for detailed week-by-week topics.

## Assessment

- Assignments: 40%
- Midterm Project: 30% 
- Final Project: 30%

## Resources

- [Course Repository]({{< meta repository_url >}})
- [Class Files]({{< meta class_drive_url >}})
'''
            
            if not dry_run:
                syllabus_file.write_text(syllabus_content, encoding='utf-8')
                self.updated_files.append(syllabus_file)
                console.print(f"[green]✅ Created:[/green] {syllabus_file}")
                created_count += 1
            else:
                console.print(f"[cyan]📋 Would create:[/cyan] {syllabus_file}")
        
        # Create schedule.qmd if missing
        schedule_file = self.paths['user_root'] / 'schedule.qmd'
        if not schedule_file.exists():
            schedule_content = '''---
title: "Course Schedule"
---

# Course Schedule

## Week 1: Getting Started
- Introduction to the course
- Setting up development environment
- First steps with version control

## Week 2: Python Fundamentals
- Python syntax and basics
- Data types and structures
- Control flow and functions

## Week 3: Development Tools
- Code editors and IDEs
- Debugging techniques
- Testing fundamentals

## Week 4: Version Control
- Git fundamentals
- GitHub workflow
- Collaboration strategies

*Schedule subject to change based on class progress*
'''
            
            if not dry_run:
                schedule_file.write_text(schedule_content, encoding='utf-8')
                self.updated_files.append(schedule_file)
                console.print(f"[green]✅ Created:[/green] {schedule_file}")
                created_count += 1
            else:
                console.print(f"[cyan]📋 Would create:[/cyan] {schedule_file}")
        
        return created_count
    
    def display_summary(self, stats: Dict[str, int]):
        """Display update summary."""
        table = Table(title="Navigation Update Summary")
        table.add_column("Component", style="cyan")
        table.add_column("Updated", style="green")
        
        table.add_row("_nav.qmd files", str(stats['nav_files']))
        table.add_row("Chapter index files", str(stats['index_files']))
        table.add_row("Missing files created", str(stats.get('created_files', 0)))
        table.add_row("Errors", str(stats['errors']), style="red" if stats['errors'] > 0 else "green")
        
        console.print(table)
        
        if self.updated_files:
            console.print("\n[bold green]📁 Updated Files:[/bold green]")
            for file_path in self.updated_files:
                console.print(f"  • [cyan]{file_path}[/cyan]")
        
        if self.errors:
            console.print("\n[bold red]❌ Errors:[/bold red]")
            for error in self.errors:
                console.print(f"  • [red]{error}[/red]")

@click.command()
@click.option('--dry-run', is_flag=True, help='Preview changes without applying them')
@click.option('--create-missing', is_flag=True, help='Create missing files (syllabus.qmd, schedule.qmd)')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def main(dry_run: bool, create_missing: bool, verbose: bool):
    """Update navigation components to match actual file structure."""
    
    console.print(Panel.fit(
        "[bold blue]🧭 Navigation Component Updater[/bold blue]\n"
        "[dim]Updates _nav.qmd and index files to match actual file structure[/dim]",
        title="Navigation Updater",
        border_style="blue"
    ))
    
    try:
        # Initialize updater
        updater = NavigationComponentUpdater()
        
        # Show current structure if verbose
        if verbose:
            console.print(f"\n[bold green]📊 Discovered Structure:[/bold green]")
            console.print(f"  • Chapters: {len(updater.structure_data['chapters'])}")
            for chapter in updater.structure_data['chapters']:
                console.print(f"    - {chapter['name']}: {len(chapter['sections'])} sections")
        
        # Update navigation components
        with console.status("[bold green]Updating navigation components..."):
            stats = updater.update_all_navigation(dry_run)
        
        # Create missing files if requested
        if create_missing:
            with console.status("[bold green]Creating missing files..."):
                created_count = updater.create_missing_files(dry_run)
                stats['created_files'] = created_count
        
        # Display summary
        updater.display_summary(stats)
        
        if dry_run:
            console.print(f"\n[yellow]💡 Use without --dry-run to apply the changes[/yellow]")
        elif stats['nav_files'] > 0 or stats['index_files'] > 0:
            console.print(f"\n[green]🎉 Navigation components updated successfully![/green]")
            console.print(f"[dim]💡 Test your site with 'quarto render' to verify the changes[/dim]")
        else:
            console.print(f"\n[yellow]ℹ️ No navigation components needed updating[/yellow]")
        
    except Exception as e:
        console.print(f"❌ [bold red]Error updating navigation:[/bold red] {e}")
        if verbose:
            console.print_exception()
        sys.exit(1)

if __name__ == '__main__':
    main() 