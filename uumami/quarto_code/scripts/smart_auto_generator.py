#!/usr/bin/env python3
"""
Smart Automatic Generator for Quarto Educational Infrastructure

This script provides intelligent auto-generation that preserves user content
while automatically updating navigation and indexes based on file changes.

Key Features:
- Uses comment markers to define preservation zones
- Automatically detects file/directory changes
- Preserves user content between markers
- Updates only auto-generated sections
- Creates proper directory indexes

Usage:
    python smart_auto_generator.py [options]
    
Example:
    python smart_auto_generator.py --watch
    python smart_auto_generator.py --force-update
"""

import re
import json
import sys
import hashlib
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Set
import yaml
import click
from rich.console import Console
from rich.panel import Panel
from rich.tree import Tree
from rich.table import Table
from rich.live import Live
from rich.text import Text
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Import our existing utilities
try:
    from scan_structure import scan_content_structure
    from config_utils import resolve_content_paths, get_user_name
    from update_nav_components import NavigationComponentUpdater
except ImportError:
    sys.path.append(str(Path(__file__).parent))
    from scan_structure import scan_content_structure
    from config_utils import resolve_content_paths, get_user_name
    from update_nav_components import NavigationComponentUpdater

console = Console()

# Content preservation markers
MARKERS = {
    'nav_start': '<!-- AUTO-NAVIGATION-START -->',
    'nav_end': '<!-- AUTO-NAVIGATION-END -->',
    'user_start': '<!-- USER-CONTENT-START -->',
    'user_end': '<!-- USER-CONTENT-END -->',
    'index_start': '<!-- AUTO-INDEX-START -->',
    'index_end': '<!-- AUTO-INDEX-END -->',
    'components_start': '<!-- AUTO-COMPONENTS-START -->',
    'components_end': '<!-- AUTO-COMPONENTS-END -->'
}

class ContentChangeHandler(FileSystemEventHandler):
    """Handles file system changes for automatic updates."""
    
    def __init__(self, generator):
        self.generator = generator
        self.last_update = time.time()
        self.update_delay = 2  # Wait 2 seconds before updating
    
    def on_modified(self, event):
        if event.is_directory:
            return
        
        # Only process .qmd files and ignore temporary files
        if event.src_path.endswith('.qmd') and not '/.quarto/' in event.src_path:
            current_time = time.time()
            if current_time - self.last_update > self.update_delay:
                self.generator.trigger_update(event.src_path)
                self.last_update = current_time
    
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.qmd'):
            self.generator.trigger_update(event.src_path)
    
    def on_deleted(self, event):
        if not event.is_directory and event.src_path.endswith('.qmd'):
            self.generator.trigger_update(event.src_path)

class SmartAutoGenerator:
    """Smart automatic generator with content preservation."""
    
    def __init__(self):
        # Use configuration utilities to resolve paths
        try:
            self.paths = resolve_content_paths()
            self.user_name = self.paths['user_name']
        except Exception as e:
            console.print(f"[red]❌ Error loading configuration:[/red] {e}")
            sys.exit(1)
        
        self.content_hashes = {}
        self.last_structure = None
        self.updated_files = []
        self.preserved_content = {}
        
        # Load existing hashes if available
        self.hash_file = self.paths['user_root'] / '.content_hashes.json'
        self.load_content_hashes()
    
    def load_content_hashes(self):
        """Load previously stored content hashes."""
        try:
            if self.hash_file.exists():
                with open(self.hash_file, 'r') as f:
                    self.content_hashes = json.load(f)
        except Exception:
            self.content_hashes = {}
    
    def save_content_hashes(self):
        """Save current content hashes."""
        try:
            with open(self.hash_file, 'w') as f:
                json.dump(self.content_hashes, f, indent=2)
        except Exception as e:
            console.print(f"[yellow]⚠️ Could not save content hashes: {e}[/yellow]")
    
    def get_file_hash(self, file_path: Path) -> str:
        """Get hash of file content."""
        try:
            content = file_path.read_text(encoding='utf-8')
            return hashlib.md5(content.encode()).hexdigest()
        except Exception:
            return ""
    
    def has_file_changed(self, file_path: Path) -> bool:
        """Check if file has changed since last processing."""
        current_hash = self.get_file_hash(file_path)
        file_key = str(file_path)
        
        if file_key not in self.content_hashes:
            self.content_hashes[file_key] = current_hash
            return True
        
        if self.content_hashes[file_key] != current_hash:
            self.content_hashes[file_key] = current_hash
            return True
        
        return False
    
    def extract_preserved_content(self, content: str, file_path: Path) -> Dict[str, str]:
        """Extract content that should be preserved between markers."""
        preserved = {}
        
        # Extract user content
        user_pattern = f"{re.escape(MARKERS['user_start'])}(.*?){re.escape(MARKERS['user_end'])}"
        user_match = re.search(user_pattern, content, re.DOTALL)
        if user_match:
            preserved['user_content'] = user_match.group(1).strip()
        
        return preserved
    
    def create_directory_index_content(self, directory: Path, structure_data: Dict[str, Any]) -> str:
        """Create proper directory index content."""
        # Find the chapter/section this directory belongs to
        chapter_info = None
        section_info = None
        
        for chapter in structure_data['chapters']:
            if Path(chapter['path']) == directory:
                chapter_info = chapter
                break
            for section in chapter['sections']:
                if section['type'] == 'directory' and Path(section['path']) == directory:
                    section_info = section
                    chapter_info = chapter
                    break
        
        if chapter_info is None:
            return self.create_generic_index_content(directory)
        
        if section_info is None:
            # This is a chapter index
            return self.create_chapter_index_content(chapter_info)
        else:
            # This is a section index
            return self.create_section_index_content(section_info, chapter_info)
    
    def create_chapter_index_content(self, chapter: Dict[str, Any]) -> str:
        """Create content for a chapter index."""
        title = chapter['title']
        sections = chapter['sections']
        
        # Count content
        total_files = sum(len(s.get('subsections', [])) for s in sections if s['type'] == 'directory')
        total_files += sum(1 for s in sections if s['type'] == 'file')
        
        content = f"""# {title}

> **📚 Chapter Overview**  
> This chapter contains {len(sections)} sections with {total_files} content files covering essential topics for your learning journey.

{MARKERS['index_start']}
## 📋 Chapter Contents

"""
        
        # List sections with proper structure
        for i, section in enumerate(sections, 1):
            if section['type'] == 'directory':
                subsection_count = len(section.get('subsections', []))
                content += f"### {section['prefix']}. {section['title']}\n"
                content += f"**Location**: [`{section['name']}/`](./{section['name']}/00_index.qmd)  \n"
                content += f"**Content**: {subsection_count} files  \n\n"
                
                # List key subsections
                for subsection in section.get('subsections', [])[:3]:  # Show first 3
                    if subsection['type'] == 'file' and subsection['file'] != '00_index.qmd':
                        content += f"- [{subsection['title']}](./{section['name']}/{subsection['file']})  \n"
                
                if len(section.get('subsections', [])) > 3:
                    content += f"- *...and {len(section['subsections']) - 3} more files*  \n"
                content += "\n"
            else:
                # File-based section
                content += f"### {section['prefix']}. {section['title']}\n"
                content += f"**File**: [`{section['file']}`](./{section['file']})  \n\n"
        
        content += f"{MARKERS['index_end']}\n\n"
        
        # Add user content zone
        content += f"{MARKERS['user_start']}\n"
        content += "<!-- Add your custom content here - it will be preserved during auto-updates -->\n\n"
        content += f"{MARKERS['user_end']}\n\n"
        
        return content
    
    def create_section_index_content(self, section: Dict[str, Any], chapter: Dict[str, Any]) -> str:
        """Create content for a section index."""
        title = section['title']
        subsections = section.get('subsections', [])
        
        content = f"""# {title}

> **📖 Section Overview**  
> Part of **{chapter['title']}** chapter. This section contains {len(subsections)} files covering {title.lower()}.

{MARKERS['index_start']}
## 📁 Section Contents

"""
        
        # List files in this section
        for subsection in subsections:
            if subsection['type'] == 'file':
                if subsection['file'] != '00_index.qmd':  # Don't list the index itself
                    content += f"### {subsection['title']}\n"
                    content += f"**File**: [`{subsection['file']}`](./{subsection['file']})  \n"
                    content += f"**Type**: Content file  \n\n"
        
        content += f"{MARKERS['index_end']}\n\n"
        
        # Add user content zone
        content += f"{MARKERS['user_start']}\n"
        content += "<!-- Add your custom section content here - it will be preserved during auto-updates -->\n\n"
        content += f"{MARKERS['user_end']}\n\n"
        
        return content
    
    def create_generic_index_content(self, directory: Path) -> str:
        """Create generic index content for directories not in structure."""
        dir_name = directory.name
        title = dir_name.replace('_', ' ').title()
        
        # List actual files in directory
        qmd_files = [f for f in directory.glob('*.qmd') if f.name != '00_index.qmd']
        subdirs = [d for d in directory.iterdir() if d.is_dir() and not d.name.startswith('.')]
        
        content = f"""# {title}

> **📂 Directory Index**  
> This directory contains {len(qmd_files)} content files and {len(subdirs)} subdirectories.

{MARKERS['index_start']}
## 📋 Directory Contents

"""
        
        if qmd_files:
            content += "### Content Files\n\n"
            for file in sorted(qmd_files):
                file_title = file.stem.replace('_', ' ').title()
                content += f"- [{file_title}](./{file.name})  \n"
            content += "\n"
        
        if subdirs:
            content += "### Subdirectories\n\n"
            for subdir in sorted(subdirs):
                subdir_title = subdir.name.replace('_', ' ').title()
                content += f"- [{subdir_title}](./{subdir.name}/)  \n"
            content += "\n"
        
        content += f"{MARKERS['index_end']}\n\n"
        
        # Add user content zone
        content += f"{MARKERS['user_start']}\n"
        content += "<!-- Add your custom content here - it will be preserved during auto-updates -->\n\n"
        content += f"{MARKERS['user_end']}\n\n"
        
        return content
    
    def update_file_with_preservation(self, file_path: Path, new_content: str) -> bool:
        """Update file while preserving marked user content."""
        try:
            if file_path.exists():
                current_content = file_path.read_text(encoding='utf-8')
                preserved = self.extract_preserved_content(current_content, file_path)
                
                # Replace preserved content in new content
                final_content = new_content
                if 'user_content' in preserved:
                    user_zone = f"{MARKERS['user_start']}\n{preserved['user_content']}\n{MARKERS['user_end']}"
                    pattern = f"{re.escape(MARKERS['user_start'])}.*?{re.escape(MARKERS['user_end'])}"
                    final_content = re.sub(pattern, user_zone, final_content, flags=re.DOTALL)
            else:
                final_content = new_content
            
            file_path.write_text(final_content, encoding='utf-8')
            self.updated_files.append(file_path)
            return True
            
        except Exception as e:
            console.print(f"[red]❌ Failed to update {file_path}: {e}[/red]")
            return False
    
    def process_directory_indexes(self, force_update: bool = False) -> int:
        """Process and update directory indexes."""
        updated_count = 0
        structure_data = scan_content_structure()
        
        # Process chapter indexes
        for chapter in structure_data['chapters']:
            chapter_path = Path(chapter['path'])
            index_file = chapter_path / '00_index.qmd'
            
            if force_update or not index_file.exists() or self.has_file_changed(index_file):
                console.print(f"[cyan]📝 Updating chapter index:[/cyan] {index_file}")
                new_content = self.create_directory_index_content(chapter_path, structure_data)
                if self.update_file_with_preservation(index_file, new_content):
                    updated_count += 1
            
            # Process section indexes
            for section in chapter['sections']:
                if section['type'] == 'directory':
                    section_path = Path(section['path'])
                    section_index = section_path / '00_index.qmd'
                    
                    if force_update or not section_index.exists() or self.has_file_changed(section_index):
                        console.print(f"[cyan]📝 Updating section index:[/cyan] {section_index}")
                        new_content = self.create_directory_index_content(section_path, structure_data)
                        if self.update_file_with_preservation(section_index, new_content):
                            updated_count += 1
        
        return updated_count
    
    def trigger_update(self, changed_file: str):
        """Trigger update when files change."""
        console.print(f"[yellow]🔄 File changed:[/yellow] {changed_file}")
        
        # Update indexes
        index_count = self.process_directory_indexes()
        
        # Update navigation
        nav_updater = NavigationComponentUpdater()
        nav_stats = nav_updater.update_all_navigation()
        
        if index_count > 0 or nav_stats['nav_files'] > 0:
            console.print(f"[green]✅ Auto-updated:[/green] {index_count} indexes, {nav_stats['nav_files']} nav files")
            self.save_content_hashes()
    
    def watch_for_changes(self):
        """Watch for file changes and auto-update."""
        console.print(Panel.fit(
            "[bold green]👁️ Smart Auto-Generator Active[/bold green]\n"
            "[dim]Watching for changes and auto-updating content...\n"
            "Press Ctrl+C to stop[/dim]",
            title="Auto-Generation Mode",
            border_style="green"
        ))
        
        event_handler = ContentChangeHandler(self)
        observer = Observer()
        observer.schedule(event_handler, str(self.paths['user_root']), recursive=True)
        observer.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            console.print("\n[yellow]🛑 Auto-generation stopped[/yellow]")
        observer.join()
    
    def force_update_all(self) -> Dict[str, int]:
        """Force update all content."""
        console.print("[bold blue]🔄 Force updating all content...[/bold blue]")
        
        # Update indexes
        index_count = self.process_directory_indexes(force_update=True)
        
        # Update navigation
        nav_updater = NavigationComponentUpdater()
        nav_stats = nav_updater.update_all_navigation()
        
        self.save_content_hashes()
        
        return {
            'indexes': index_count,
            'nav_files': nav_stats['nav_files'],
            'index_files': nav_stats['index_files']
        }
    
    def display_summary(self, stats: Dict[str, int]):
        """Display update summary."""
        table = Table(title="Smart Auto-Generation Summary")
        table.add_column("Component", style="cyan")
        table.add_column("Updated", style="green")
        
        table.add_row("Directory Indexes", str(stats.get('indexes', 0)))
        table.add_row("Navigation Files", str(stats.get('nav_files', 0)))
        table.add_row("Chapter Index Files", str(stats.get('index_files', 0)))
        
        console.print(table)
        
        if self.updated_files:
            console.print("\n[bold green]📁 Updated Files:[/bold green]")
            for file_path in self.updated_files[-10:]:  # Show last 10
                console.print(f"  • [cyan]{file_path}[/cyan]")
            if len(self.updated_files) > 10:
                console.print(f"  • [dim]...and {len(self.updated_files) - 10} more[/dim]")

@click.command()
@click.option('--watch', is_flag=True, help='Watch for changes and auto-update')
@click.option('--force-update', is_flag=True, help='Force update all content')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def main(watch: bool, force_update: bool, verbose: bool):
    """Smart automatic generator with content preservation."""
    
    try:
        generator = SmartAutoGenerator()
        
        if watch:
            generator.watch_for_changes()
        elif force_update:
            stats = generator.force_update_all()
            generator.display_summary(stats)
            console.print("\n[green]🎉 Force update completed![/green]")
        else:
            # Regular update - only changed files
            index_count = generator.process_directory_indexes()
            nav_updater = NavigationComponentUpdater()
            nav_stats = nav_updater.update_all_navigation()
            
            stats = {
                'indexes': index_count,
                'nav_files': nav_stats['nav_files'],
                'index_files': nav_stats['index_files']
            }
            
            generator.display_summary(stats)
            generator.save_content_hashes()
            
            if any(stats.values()):
                console.print("\n[green]🎉 Smart auto-generation completed![/green]")
            else:
                console.print("\n[yellow]ℹ️ No updates needed - all content is current[/yellow]")
        
    except Exception as e:
        console.print(f"❌ [bold red]Error in smart auto-generation:[/bold red] {e}")
        if verbose:
            console.print_exception()
        sys.exit(1)

if __name__ == '__main__':
    main() 