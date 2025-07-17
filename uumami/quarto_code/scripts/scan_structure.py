#!/usr/bin/env python3
"""
Content Discovery Engine for Quarto Educational Infrastructure

This script scans directory structures to discover chapters, sections, and content
following the educational naming conventions. It outputs structured JSON data
for consumption by other automation scripts.

Usage:
    python scan_structure.py <path> [options]
    
Example:
    python scan_structure.py uumami/
    python scan_structure.py uumami/ --output structure.json --verbose
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
from rich.tree import Tree
from rich.panel import Panel
from rich.table import Table

console = Console()

# Naming convention patterns
NAMING_PATTERNS = {
    'chapter': r'^\d{2}_[\w_]+$',           # 00_intro, 01_python_basics
    'appendix': r'^[a-z]_[\w_]+$',          # a_installation, b_troubleshooting
    'section_file': r'^\d{2}_[\w_]+\.qmd$', # 00_overview.qmd, 01_setup.qmd
    'index_file': r'^\d{2}_index\.qmd$',    # 00_index.qmd, 01_index.qmd
    'section_dir': r'^[a-z]_[\w_]+$',       # a_prompt_engineering, b_intro_system
    'nav_file': r'^_nav\.qmd$'              # _nav.qmd
}

# Patterns to exclude from scanning
EXCLUDE_PATTERNS = {
    'directories': {'scripts', 'examples', 'resources', 'legacy', 'quarto_code', 
                   '_site', '.quarto', '__pycache__', 'quarto_development'},
    'files': {'.py', '.sh', '.json', '.csv', '.txt', '.yml', '.yaml'},
    'hidden': r'^\.',                       # Hidden files/directories
    'temp': r'^__.*__$'                     # Temporary files
}


def extract_title_from_qmd(file_path: Path) -> Optional[str]:
    """Extract title from YAML frontmatter in a .qmd file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for YAML frontmatter between --- markers
        yaml_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if yaml_match:
            yaml_content = yaml_match.group(1)
            try:
                yaml_data = yaml.safe_load(yaml_content)
                return yaml_data.get('title', None)
            except yaml.YAMLError:
                return None
        return None
    except Exception:
        return None


def generate_display_title(prefix: str, title: str, index: int = 0) -> str:
    """Generate display title with proper numbering."""
    if prefix.isdigit():
        # Chapter numbering: 0.0, 0.1, etc.
        return f"{prefix}.{index} {title}" if index > 0 else f"{prefix}. {title}"
    else:
        # Appendix lettering: A.0, A.1, etc.
        return f"{prefix.upper()}.{index} {title}" if index > 0 else f"{prefix.upper()}. {title}"


def is_excluded(path: Path) -> bool:
    """Check if a path should be excluded from scanning."""
    name = path.name
    
    # Check directory exclusions
    if path.is_dir() and name in EXCLUDE_PATTERNS['directories']:
        return True
    
    # Check file extension exclusions
    if path.is_file() and path.suffix in EXCLUDE_PATTERNS['files']:
        return True
    
    # Check hidden files/directories
    if re.match(EXCLUDE_PATTERNS['hidden'], name):
        return True
    
    # Check temporary files
    if re.match(EXCLUDE_PATTERNS['temp'], name):
        return True
    
    return False


def scan_section_directory(section_path: Path, prefix: str) -> Dict[str, Any]:
    """Scan a section directory for subsections and files."""
    section_data = {
        'name': section_path.name,
        'prefix': prefix,
        'title': prefix.replace('_', ' ').title(),  # Default title
        'path': str(section_path),
        'type': 'directory',
        'subsections': []
    }
    
    # Look for index file to extract title
    index_pattern = re.compile(rf'^{re.escape(prefix)}_index\.qmd$')
    for file_path in section_path.iterdir():
        if file_path.is_file() and index_pattern.match(file_path.name):
            title = extract_title_from_qmd(file_path)
            if title:
                section_data['title'] = title
            break
    
    # Scan for subsections (nested directories or files)
    for item in sorted(section_path.iterdir()):
        if is_excluded(item):
            continue
            
        if item.is_file() and item.suffix == '.qmd':
            # Individual .qmd file in section
            title = extract_title_from_qmd(item) or item.stem.replace('_', ' ').title()
            section_data['subsections'].append({
                'file': item.name,
                'title': title,
                'type': 'file'
            })
        elif item.is_dir():
            # Nested directory
            title = extract_title_from_qmd(item / f"{item.name}_index.qmd")
            if not title:
                title = item.name.replace('_', ' ').title()
            
            section_data['subsections'].append({
                'name': item.name,
                'title': title,
                'type': 'directory',
                'path': str(item)
            })
    
    return section_data


def scan_chapter_directory(chapter_path: Path) -> Dict[str, Any]:
    """Scan a chapter directory for index file and sections."""
    name_parts = chapter_path.name.split('_', 1)
    prefix = name_parts[0]
    
    chapter_data = {
        'name': chapter_path.name,
        'prefix': prefix,
        'title': name_parts[1].replace('_', ' ').title() if len(name_parts) > 1 else 'Untitled',
        'path': str(chapter_path),
        'has_index': False,
        'index_file': None,
        'sections': []
    }
    
    # Look for index file
    index_pattern = re.compile(NAMING_PATTERNS['index_file'])
    for file_path in chapter_path.iterdir():
        if file_path.is_file() and index_pattern.match(file_path.name):
            chapter_data['has_index'] = True
            chapter_data['index_file'] = file_path.name
            
            # Extract title from index file
            title = extract_title_from_qmd(file_path)
            if title:
                chapter_data['title'] = title
            break
    
    # Scan for sections
    section_items = []
    for item in chapter_path.iterdir():
        if is_excluded(item):
            continue
        
        if item.is_file() and item.suffix == '.qmd' and not index_pattern.match(item.name):
            # Individual section file
            if not re.match(NAMING_PATTERNS['nav_file'], item.name):
                title = extract_title_from_qmd(item) or item.stem.replace('_', ' ').title()
                section_items.append({
                    'file': item.name,
                    'title': title,
                    'type': 'file',
                    'sort_key': item.stem
                })
        elif item.is_dir():
            # Section directory
            if re.match(NAMING_PATTERNS['section_dir'], item.name):
                section_prefix = item.name.split('_')[0]
                section_data = scan_section_directory(item, section_prefix)
                section_items.append({
                    **section_data,
                    'sort_key': section_prefix
                })
    
    # Sort sections by prefix (alphabetical for letter prefixes, numerical for number prefixes)
    section_items.sort(key=lambda x: x['sort_key'])
    
    # Add display titles with proper numbering
    for i, section in enumerate(section_items):
        if section['type'] == 'directory':
            section['display_title'] = generate_display_title(
                section['prefix'], section['title'], i
            )
        else:
            # For files, use the extracted title as-is
            section['display_title'] = section['title']
    
    chapter_data['sections'] = section_items
    
    return chapter_data


def scan_content_structure(base_path: Path) -> Dict[str, Any]:
    """Scan the content directory structure and return organized data."""
    
    # Look for notas directory
    notas_path = base_path / 'notas' if (base_path / 'notas').exists() else base_path
    
    if not notas_path.exists():
        raise FileNotFoundError(f"Content directory not found: {notas_path}")
    
    structure_data = {
        'scan_timestamp': datetime.now().isoformat(),
        'base_path': str(base_path),
        'content_path': str(notas_path),
        'chapters': [],
        'appendices': [],
        'stats': {
            'total_chapters': 0,
            'total_appendices': 0,
            'total_sections': 0,
            'total_files': 0
        }
    }
    
    # Scan for chapters and appendices
    for item in sorted(notas_path.iterdir()):
        if is_excluded(item) or not item.is_dir():
            continue
        
        if re.match(NAMING_PATTERNS['chapter'], item.name):
            # Chapter directory (XX_name)
            chapter_data = scan_chapter_directory(item)
            structure_data['chapters'].append(chapter_data)
            structure_data['stats']['total_chapters'] += 1
            structure_data['stats']['total_sections'] += len(chapter_data['sections'])
            
        elif re.match(NAMING_PATTERNS['appendix'], item.name):
            # Appendix directory (Y_name)
            appendix_data = scan_chapter_directory(item)  # Same structure as chapter
            structure_data['appendices'].append(appendix_data)
            structure_data['stats']['total_appendices'] += 1
            structure_data['stats']['total_sections'] += len(appendix_data['sections'])
    
    # Sort chapters numerically, appendices alphabetically
    structure_data['chapters'].sort(key=lambda x: int(x['prefix']))
    structure_data['appendices'].sort(key=lambda x: x['prefix'])
    
    # Calculate total files
    for chapter in structure_data['chapters'] + structure_data['appendices']:
        structure_data['stats']['total_files'] += len([
            s for s in chapter['sections'] 
            if s['type'] == 'file'
        ]) + (1 if chapter['has_index'] else 0)
        
        # Count subsection files
        for section in chapter['sections']:
            if section['type'] == 'directory':
                structure_data['stats']['total_files'] += len(section.get('subsections', []))
    
    return structure_data


def display_structure_tree(structure_data: Dict[str, Any]) -> None:
    """Display the discovered structure as a rich tree."""
    tree = Tree("📚 [bold blue]Content Structure[/bold blue]")
    
    # Add chapters
    for chapter in structure_data['chapters']:
        chapter_node = tree.add(
            f"📖 [bold green]{chapter['prefix']}. {chapter['title']}[/bold green] "
            f"({'✅' if chapter['has_index'] else '❌'} index)"
        )
        
        for section in chapter['sections']:
            if section['type'] == 'file':
                chapter_node.add(f"📄 [blue]{section['display_title']}[/blue]")
            else:
                section_node = chapter_node.add(f"📁 [yellow]{section['display_title']}[/yellow]")
                for subsection in section.get('subsections', []):
                    if subsection['type'] == 'file':
                        section_node.add(f"📄 {subsection['title']}")
                    else:
                        section_node.add(f"📁 {subsection['title']}")
    
    # Add appendices
    if structure_data['appendices']:
        appendix_tree = tree.add("📋 [bold cyan]Appendices[/bold cyan]")
        for appendix in structure_data['appendices']:
            appendix_node = appendix_tree.add(
                f"📖 [cyan]{appendix['prefix'].upper()}. {appendix['title']}[/cyan] "
                f"({'✅' if appendix['has_index'] else '❌'} index)"
            )
            
            for section in appendix['sections']:
                if section['type'] == 'file':
                    appendix_node.add(f"📄 [blue]{section['display_title']}[/blue]")
                else:
                    section_node = appendix_node.add(f"📁 [yellow]{section['display_title']}[/yellow]")
                    for subsection in section.get('subsections', []):
                        section_node.add(f"📄 {subsection['title']}")
    
    console.print(tree)


def display_stats_table(stats: Dict[str, int]) -> None:
    """Display structure statistics in a table."""
    table = Table(title="📊 Structure Statistics")
    table.add_column("Metric", style="cyan")
    table.add_column("Count", justify="right", style="green")
    
    table.add_row("Chapters", str(stats['total_chapters']))
    table.add_row("Appendices", str(stats['total_appendices']))
    table.add_row("Sections", str(stats['total_sections']))
    table.add_row("Total Files", str(stats['total_files']))
    
    console.print(table)


@click.command()
@click.argument('path', type=click.Path(exists=True, path_type=Path))
@click.option('--output', '-o', type=click.Path(path_type=Path), 
              help='Output JSON file path')
@click.option('--verbose', '-v', is_flag=True, 
              help='Show detailed console output')
@click.option('--validate', is_flag=True, 
              help='Validate naming conventions only')
@click.option('--pretty', is_flag=True, default=True,
              help='Pretty-print JSON output')
def main(path: Path, output: Optional[Path], verbose: bool, validate: bool, pretty: bool):
    """
    Scan directory structure for educational content organization.
    
    PATH: Base directory to scan (typically 'uumami/')
    """
    try:
        with console.status("[bold green]Scanning content structure..."):
            structure_data = scan_content_structure(path)
        
        if verbose or not output:
            console.print(Panel.fit(
                f"[bold green]✅ Scan Complete![/bold green]\n"
                f"Scanned: [cyan]{structure_data['content_path']}[/cyan]\n"
                f"Timestamp: [dim]{structure_data['scan_timestamp']}[/dim]",
                title="Content Discovery"
            ))
            
            display_structure_tree(structure_data)
            display_stats_table(structure_data['stats'])
        
        if validate:
            console.print("\n[bold yellow]🔍 Validation Mode:[/bold yellow] Structure follows naming conventions ✅")
            return
        
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                if pretty:
                    json.dump(structure_data, f, indent=2, ensure_ascii=False)
                else:
                    json.dump(structure_data, f, ensure_ascii=False)
            
            console.print(f"\n[bold green]💾 Data saved to:[/bold green] [cyan]{output}[/cyan]")
        else:
            # Print JSON to stdout if no output file specified
            if pretty:
                console.print_json(data=structure_data)
            else:
                print(json.dumps(structure_data, ensure_ascii=False))
                
    except Exception as e:
        console.print(f"[bold red]❌ Error:[/bold red] {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main() 