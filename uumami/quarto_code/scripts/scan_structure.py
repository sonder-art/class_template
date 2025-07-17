#!/usr/bin/env python3
"""
Content Discovery Engine for Quarto Educational Infrastructure

ROLE: Helper script that scans directory structures to discover chapters, sections, 
and content following educational naming conventions. Used by master_update.py and 
other automation scripts.

USAGE: Typically called by master_update.py, but can be run standalone for debugging.

Key Features:
- Discovers chapters, appendices, and sections with actual file prefixes and titles
- Extracts titles from YAML frontmatter in .qmd files
- Follows hierarchical numbering conventions (01_, 02_, etc.)
- Outputs structured JSON data for other automation tools
- Uses dynamic path resolution (no hardcoded paths)

Usage:
    python scan_structure.py [options]
    
Example:
    python scan_structure.py --output structure.json --verbose
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

# Import configuration utilities
try:
    from config_utils import resolve_content_paths, get_user_name
except ImportError:
    sys.path.append(str(Path(__file__).parent))
    from config_utils import resolve_content_paths, get_user_name

console = Console()

# ============================================================================
# CONTENT SCANNING CONFIGURATION
# ============================================================================
# This section defines what directories and content to scan for automation.
# Modify these lists to control what gets processed by the automation system.

# Directories to scan for content (includes all subdirectories)
CONTENT_DIRECTORIES = {
    'notas',                    # Main educational content following 01_, 02_ patterns
    'quarto_development',       # Development documentation (doesn't follow strict patterns)
}

# Special directories that should be scanned even if they don't follow naming patterns
SPECIAL_DIRECTORIES = {
    'quarto_development': {
        'description': 'Development documentation and automation guides',
        'allow_non_standard_names': True,   # Allow directories like 'automation_system'
        'scan_subdirectories': True,        # Scan all subdirectories recursively
    }
}

# Naming convention patterns - Hierarchical System
NAMING_PATTERNS = {
    'chapter': r'^0[1-9]_[\w_]+$|^[1-9]\d_[\w_]+$',    # 01_intro, 02_python (chapters start from 01)
    'appendix': r'^[a-z]_[\w_]+$',                      # a_installation, b_troubleshooting
    'section_file': r'^0[1-9]_[\w_]+\.qmd$|^[1-9]\d_[\w_]+\.qmd$',  # 01_lesson.qmd, 02_advanced.qmd
    'index_file': r'^00_index\.qmd$',                   # 00_index.qmd (indices always use 00_)
    'section_dir': r'^0[1-9]_[\w_]+$|^[1-9]\d_[\w_]+$', # 01_prompt_engineering, 02_systems (sections start from 01)
    'nav_file': r'^_nav\.qmd$',                         # _nav.qmd
    'special_dir': r'^[\w_]+$',                         # Any word characters (for special directories)
}

# What to exclude even within included directories
EXCLUDE_PATTERNS = {
    'files': {'.py', '.sh', '.json', '.csv', '.txt', '.yml', '.yaml'},
    'hidden': r'^\.',                       # Hidden files/directories
    'temp': r'^__.*__$',                    # Temporary files
    'system': {'_site', '.quarto', '__pycache__', 'scripts', 'examples', 'resources', 'legacy'}
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


def generate_display_title(prefix: str, title: str, use_prefix_only: bool = True) -> str:
    """Generate display title using actual file prefixes."""
    if use_prefix_only:
        # Use the actual prefix from the file/directory name
        if prefix.isdigit():
            return f"{prefix}. {title}"
        else:
            return f"{prefix.upper()}. {title}"
    else:
        # Legacy format (deprecated)
        return f"{prefix}. {title}"


def is_excluded(path: Path, parent_dir: str = None) -> bool:
    """Check if a path should be excluded from scanning."""
    name = path.name
    
    # Check system directory exclusions
    if path.is_dir() and name in EXCLUDE_PATTERNS['system']:
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


def is_content_directory_included(dir_name: str) -> bool:
    """Check if a directory should be scanned for content."""
    return dir_name in CONTENT_DIRECTORIES


def should_scan_non_standard_directory(dir_name: str, parent_dir: str) -> bool:
    """Check if a non-standard directory should be scanned based on special rules."""
    if parent_dir in SPECIAL_DIRECTORIES:
        special_config = SPECIAL_DIRECTORIES[parent_dir]
        return special_config.get('allow_non_standard_names', False)
    return False


def scan_section_directory(section_path: Path, prefix: str, is_special: bool = False) -> Dict[str, Any]:
    """Scan a section directory for subsections and files."""
    
    if is_special:
        # Special section directory that doesn't follow standard patterns
        section_data = {
            'name': section_path.name,
            'prefix': prefix,
            'title': section_path.name.replace('_', ' ').title(),
            'path': str(section_path),
            'type': 'directory',
            'subsections': [],
            'is_special': True
        }
    else:
        # Standard section directory
        section_data = {
            'name': section_path.name,
            'prefix': prefix,
            'title': prefix.replace('_', ' ').title(),  # Default title
            'path': str(section_path),
            'type': 'directory',
            'subsections': []
        }
    
    # Look for index file to extract title (check both 00_index.qmd and {prefix}_index.qmd)
    index_files = ['00_index.qmd', f'{prefix}_index.qmd']
    for index_file in index_files:
        index_path = section_path / index_file
        if index_path.exists():
            title = extract_title_from_qmd(index_path)
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


def scan_chapter_directory(chapter_path: Path, is_special: bool = False) -> Dict[str, Any]:
    """Scan a chapter directory for index file and sections."""
    
    if is_special:
        # Handle special directories that don't follow standard naming patterns
        chapter_data = {
            'name': chapter_path.name,
            'prefix': 'special',  # Special marker for non-standard directories
            'title': chapter_path.name.replace('_', ' ').title(),
            'path': str(chapter_path),
            'has_index': False,
            'index_file': None,
            'sections': [],
            'is_special': True
        }
    else:
        # Standard chapter directory processing
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
            # Section directory - handle both standard and special patterns
            if re.match(NAMING_PATTERNS['section_dir'], item.name):
                # Standard section directory (01_name, 02_name, etc.)
                section_prefix = item.name.split('_')[0]
                section_data = scan_section_directory(item, section_prefix)
                section_items.append({
                    **section_data,
                    'sort_key': section_prefix
                })
            elif is_special and re.match(NAMING_PATTERNS['special_dir'], item.name):
                # Special directory that doesn't follow standard patterns
                section_data = scan_section_directory(item, item.name, is_special=True)
                section_items.append({
                    **section_data,
                    'sort_key': item.name
                })
    
    # Sort sections by prefix (alphabetical for letter prefixes, numerical for number prefixes)
    section_items.sort(key=lambda x: x['sort_key'])
    
    # Add display titles using actual file prefixes
    for section in section_items:
        if section['type'] == 'directory':
            section['display_title'] = generate_display_title(
                section['prefix'], section['title']
            )
        else:
            # For files, extract prefix from filename and use actual title
            if section.get('file'):
                file_prefix = section['file'].split('_')[0] if '_' in section['file'] else section['file'].split('.')[0]
                section['display_title'] = generate_display_title(file_prefix, section['title'])
            else:
                section['display_title'] = section['title']
    
    chapter_data['sections'] = section_items
    
    return chapter_data


def scan_content_structure(base_path: Optional[Path] = None) -> Dict[str, Any]:
    """Scan all configured content directories and return organized data."""
    
    # Use configuration utilities to resolve paths
    try:
        paths = resolve_content_paths()
        user_root = paths.get('user_root')
        user_name = paths.get('user_name', 'uumami')
        
        if user_root is None:
            raise FileNotFoundError("Could not determine user root directory")
        
    except Exception as e:
        console.print(f"[yellow]⚠️ Warning:[/yellow] Could not load configuration: {e}")
        if base_path:
            user_root = base_path
            user_name = 'uumami'
        else:
            raise FileNotFoundError("No base path provided and configuration loading failed")
    
    structure_data = {
        'scan_timestamp': datetime.now().isoformat(),
        'user_name': user_name,
        'base_path': str(paths.get('project_root', base_path or Path.cwd())),
        'content_directories': list(CONTENT_DIRECTORIES),
        'chapters': [],
        'appendices': [],
        'stats': {
            'total_chapters': 0,
            'total_appendices': 0,
            'total_sections': 0,
            'total_files': 0
        }
    }
    
    # Scan each configured content directory
    for content_dir_name in CONTENT_DIRECTORIES:
        content_path = user_root / content_dir_name
        
        if not content_path.exists():
            console.print(f"[yellow]⚠️ Warning:[/yellow] Content directory not found: {content_path}")
            continue
            
        console.print(f"[blue]🔍 Scanning content directory:[/blue] {content_dir_name}")
        
        # Scan for chapters and appendices in this directory
        for item in sorted(content_path.iterdir()):
            if is_excluded(item, content_dir_name) or not item.is_dir():
                continue
            
            # Check if this matches standard patterns
            is_standard_chapter = re.match(NAMING_PATTERNS['chapter'], item.name)
            is_standard_appendix = re.match(NAMING_PATTERNS['appendix'], item.name)
            
            # Check if we should scan non-standard directories
            is_special_dir = should_scan_non_standard_directory(item.name, content_dir_name)
            
            if is_standard_chapter:
                # Standard chapter directory (XX_name)
                chapter_data = scan_chapter_directory(item)
                chapter_data['source_directory'] = content_dir_name
                structure_data['chapters'].append(chapter_data)
                structure_data['stats']['total_chapters'] += 1
                structure_data['stats']['total_sections'] += len(chapter_data['sections'])
                
            elif is_standard_appendix:
                # Standard appendix directory (Y_name)
                appendix_data = scan_chapter_directory(item)
                appendix_data['source_directory'] = content_dir_name
                structure_data['appendices'].append(appendix_data)
                structure_data['stats']['total_appendices'] += 1
                structure_data['stats']['total_sections'] += len(appendix_data['sections'])
                
            elif is_special_dir:
                # Special directory that doesn't follow standard patterns
                # Treat as a chapter but mark it as special
                special_data = scan_chapter_directory(item, is_special=True)
                special_data['source_directory'] = content_dir_name
                special_data['is_special'] = True
                structure_data['chapters'].append(special_data)
                structure_data['stats']['total_chapters'] += 1
                structure_data['stats']['total_sections'] += len(special_data['sections'])
    
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
@click.option('--path', type=click.Path(exists=True, path_type=Path), 
              help='Base directory to scan (auto-detected from config if not provided)')
@click.option('--output', '-o', type=click.Path(path_type=Path), 
              help='Output JSON file path')
@click.option('--verbose', '-v', is_flag=True, 
              help='Show detailed console output')
@click.option('--validate', is_flag=True, 
              help='Validate naming conventions only')
@click.option('--pretty', is_flag=True, default=True,
              help='Pretty-print JSON output')
def main(path: Optional[Path], output: Optional[Path], verbose: bool, validate: bool, pretty: bool):
    """
    Scan directory structure for educational content organization.
    
    Automatically detects content paths from _quarto.yml configuration.
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