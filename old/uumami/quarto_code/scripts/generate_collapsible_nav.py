#!/usr/bin/env python3
"""
Collapsible Navigation Generator for Quarto Educational Infrastructure

ROLE: Helper script that generates enhanced collapsible navigation data for modern UI.
Called by master_update.py to create advanced navigation components.

USAGE: Typically called by master_update.py, but can be run standalone for enhanced nav.

Key Features:
- Generates enhanced navigation data structures
- Creates JavaScript and JSON data files
- Integrates with existing automation system
- Supports collapsible navigation UI components
- Dynamic path resolution and content analysis
- Creates template inclusions for advanced navigation

Usage:
    python generate_collapsible_nav.py <path> [options]
    
Example:
    python generate_collapsible_nav.py uumami/
    python generate_collapsible_nav.py uumami/ --output-format json
    python generate_collapsible_nav.py uumami/ --generate-templates
"""

import re
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
import yaml
import click
from rich.console import Console
from rich.panel import Panel
from rich.tree import Tree
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

# Import our existing content discovery engine and configuration utilities
try:
    from scan_structure import scan_content_structure
    from generate_navigation import NavigationGenerator
    from config_utils import resolve_content_paths, get_user_name
except ImportError:
    sys.path.append(str(Path(__file__).parent))
    from scan_structure import scan_content_structure
    from generate_navigation import NavigationGenerator
    from config_utils import resolve_content_paths, get_user_name

console = Console()

class CollapsibleNavGenerator:
    """Enhanced navigation generator with collapsible functionality."""
    
    def __init__(self, base_path: Optional[Path] = None):
        # Use configuration utilities to resolve paths
        try:
            self.paths = resolve_content_paths()
            self.base_path = self.paths['project_root']
            self.user_name = self.paths['user_name']
            self.user_root = self.paths['user_root']
        except Exception:
            # Fallback to provided base_path
            if base_path is None:
                raise ValueError("Could not resolve paths from configuration and no base_path provided")
            self.base_path = base_path
            self.user_name = 'uumami'
            self.user_root = base_path / self.user_name
            self.paths = {'project_root': base_path, 'user_name': self.user_name, 'user_root': self.user_root}
        
        self.content_structure = {}
        self.navigation_data = {}
        self.output_dir = self.user_root / 'quarto_code' / 'generated'
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def scan_and_analyze(self) -> Dict[str, Any]:
        """Scan content structure and analyze for navigation generation."""
        console.print("🔍 [bold blue]Scanning content structure...[/bold blue]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Analyzing content...", total=None)
            
            # Use existing content discovery
            self.content_structure = scan_content_structure()
            progress.update(task, description="Building navigation data...")
            
            # Build enhanced navigation data
            self.navigation_data = self._build_navigation_data()
            progress.update(task, description="Complete!", total=1, completed=1)
        
        return self.navigation_data
    
    def _build_navigation_data(self) -> Dict[str, Any]:
        """Build comprehensive navigation data structure."""
        nav_data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'base_path': str(self.base_path),
                'total_chapters': len(self.content_structure.get('chapters', [])),
                'total_sections': sum(len(ch.get('sections', [])) for ch in self.content_structure.get('chapters', [])),
                'navigation_version': '3.0'
            },
            'site_structure': {
                'chapters': self._build_chapter_navigation(),
                'appendices': self._build_appendix_navigation(),
                'documentation': self._build_documentation_navigation()
            },
            'breadcrumb_templates': self._build_breadcrumb_templates(),
            'sequential_navigation': self._build_sequential_navigation(),
            'quick_access': self._build_quick_access_data()
        }
        
        return nav_data
    
    def _build_chapter_navigation(self) -> List[Dict[str, Any]]:
        """Build hierarchical chapter navigation data."""
        chapters = []
        
        for chapter in self.content_structure.get('chapters', []):
            chapter_data = {
                'id': f"chapter_{chapter['prefix']}",
                'number': chapter['prefix'],
                'name': chapter['name'],
                'title': chapter['title'],
                'href': f"notas/{chapter['name']}/{chapter.get('index_file', '00_index.qmd')}",
                'icon': self._get_chapter_icon(chapter['name']),
                'sections': [],
                'metadata': {
                    'total_sections': len(chapter.get('sections', [])),
                    'estimated_reading_time': self._estimate_reading_time(chapter),
                    'content_type': 'chapter'
                }
            }
            
            # Add sections
            for section in chapter.get('sections', []):
                if section['type'] == 'file':
                    # Section is a file
                    section_data = {
                        'id': f"section_{chapter['prefix']}_{section.get('file', section.get('name', ''))}",
                        'number': section.get('prefix', ''),
                        'name': section.get('name', section.get('file', '')),
                        'title': section['title'],
                        'href': f"notas/{chapter['name']}/{section.get('file', section.get('name', ''))}",
                        'icon': self._get_section_icon(section.get('name', '')),
                        'subsections': [],
                        'metadata': {
                            'parent_chapter': chapter['prefix'],
                            'content_type': 'section_file',
                            'has_exercises': self._check_for_exercises(section),
                            'difficulty_level': self._assess_difficulty(section)
                        }
                    }
                else:
                    # Section is a directory
                    section_data = {
                        'id': f"section_{chapter['prefix']}_{section['prefix']}",
                        'number': section['prefix'],
                        'name': section['name'],
                        'title': section['title'],
                        'href': f"notas/{chapter['name']}/{section['name']}/00_index.qmd",
                        'icon': self._get_section_icon(section['name']),
                        'subsections': self._build_subsection_data(chapter, section),
                        'metadata': {
                            'parent_chapter': chapter['prefix'],
                            'content_type': 'section_directory',
                            'has_exercises': self._check_for_exercises(section),
                            'difficulty_level': self._assess_difficulty(section)
                        }
                    }
                chapter_data['sections'].append(section_data)
            
            chapters.append(chapter_data)
        
        return chapters
    
    def _build_subsection_data(self, chapter: Dict, section: Dict) -> List[Dict[str, Any]]:
        """Build subsection data for detailed navigation."""
        subsections = []
        
        # Check if this section has subsections (if it's a directory type)
        if section.get('type') == 'directory' and 'subsections' in section:
            for subsection in section['subsections']:
                if subsection['type'] == 'file':
                    file_data = {
                        'id': f"content_{chapter['prefix']}_{section['prefix']}_{subsection.get('file', subsection.get('name', ''))}",
                        'name': subsection.get('file', subsection.get('name', '')),
                        'title': subsection['title'],
                        'href': f"notas/{chapter['name']}/{section['name']}/{subsection.get('file', subsection.get('name', ''))}",
                        'icon': '📄',
                        'metadata': {
                            'file_type': 'content',
                            'estimated_read_time': 3  # Default estimate
                        }
                    }
                    subsections.append(file_data)
                else:
                    # Nested directory
                    dir_data = {
                        'id': f"content_{chapter['prefix']}_{section['prefix']}_{subsection['name']}",
                        'name': subsection['name'],
                        'title': subsection['title'],
                        'href': f"notas/{chapter['name']}/{section['name']}/{subsection['name']}/00_index.qmd",
                        'icon': '📁',
                        'metadata': {
                            'file_type': 'directory'
                        }
                    }
                    subsections.append(dir_data)
        
        return subsections
    
    def _build_appendix_navigation(self) -> List[Dict[str, Any]]:
        """Build appendix navigation data."""
        appendices = []
        
        for appendix in self.content_structure.get('appendices', []):
            appendix_data = {
                'id': f"appendix_{appendix['prefix']}",
                'letter': appendix['prefix'].upper(),
                'name': appendix['name'],
                'title': appendix['title'],
                'href': f"notas/{appendix['name']}/{appendix.get('index_file', '00_index.qmd')}",
                'icon': self._get_appendix_icon(appendix['name']),
                'metadata': {
                    'content_type': 'appendix',
                    'priority': self._get_appendix_priority(appendix['name'])
                }
            }
            appendices.append(appendix_data)
        
        return appendices
    
    def _build_documentation_navigation(self) -> List[Dict[str, Any]]:
        """Build documentation navigation data."""
        doc_sections = []
        
        # Check for documentation structure
        doc_path = self.base_path / 'quarto_development'
        if doc_path.exists():
            doc_sections = [
                {
                    'id': 'doc_automation',
                    'title': 'Automation System',
                    'icon': '🤖',
                    'href': 'quarto_development/01_automation_system/00_index.qmd',
                    'subsections': [
                        {'title': 'Quick Start', 'href': 'quarto_development/01_automation_system/01_quickstart/00_index.qmd', 'icon': '🚀'},
                        {'title': 'Architecture', 'href': 'quarto_development/01_automation_system/02_architecture/00_index.qmd', 'icon': '🏗️'},
                        {'title': 'Scripts Reference', 'href': 'quarto_development/01_automation_system/03_scripts_reference/00_index.qmd', 'icon': '🛠️'},
                        {'title': 'Troubleshooting', 'href': 'quarto_development/01_automation_system/04_troubleshooting/00_index.qmd', 'icon': '🔧'},
                        {'title': 'Development Guide', 'href': 'quarto_development/01_automation_system/05_development/00_index.qmd', 'icon': '🚀'},
                        {'title': 'Auto Generation', 'href': 'quarto_development/01_automation_system/06_auto_generation/00_index.qmd', 'icon': '🤖'}
                    ]
                }
            ]
        
        return doc_sections
    
    def _build_breadcrumb_templates(self) -> Dict[str, Any]:
        """Build breadcrumb navigation templates."""
        return {
            'course': {
                'pattern': 'notas/{chapter}/{section?}/{page?}',
                'template': '📚 Course › {chapter_title} › {section_title?} › {page_title?}',
                'levels': ['course', 'chapter', 'section', 'page']
            },
            'documentation': {
                'pattern': 'quarto_development/{system}/{section?}/{page?}',
                'template': '📖 Documentation › {system_title} › {section_title?} › {page_title?}',
                'levels': ['documentation', 'system', 'section', 'page']
            },
            'appendix': {
                'pattern': 'notas/{appendix_name}/{page?}',
                'template': '📋 Appendices › {appendix_title} › {page_title?}',
                'levels': ['appendices', 'appendix', 'page']
            }
        }
    
    def _build_sequential_navigation(self) -> Dict[str, Any]:
        """Build sequential navigation mapping."""
        sequence_map = {}
        all_pages = []
        
        # Build flat sequence of all content pages
        for chapter in self.content_structure.get('chapters', []):
            # Add chapter index
            all_pages.append({
                'href': f"notas/{chapter['name']}/{chapter.get('index_file', '00_index.qmd')}",
                'title': f"{chapter['prefix']}. {chapter['title']}",
                'type': 'chapter_index',
                'chapter': chapter['prefix']
            })
            
            # Add sections
            for section in chapter.get('sections', []):
                if section['type'] == 'file':
                    # Section is a file, add it directly
                    all_pages.append({
                        'href': f"notas/{chapter['name']}/{section.get('file', section.get('name', ''))}",
                        'title': section['title'],
                        'type': 'section_file',
                        'chapter': chapter['prefix']
                    })
                else:
                    # Section is a directory, add section index
                    all_pages.append({
                        'href': f"notas/{chapter['name']}/{section['name']}/00_index.qmd",
                        'title': f"{chapter['prefix']}.{section['prefix']} {section['title']}",
                        'type': 'section_index',
                        'chapter': chapter['prefix'],
                        'section': section['prefix']
                    })
                    
                    # Add subsection content
                    for subsection in section.get('subsections', []):
                        if subsection['type'] == 'file':
                            all_pages.append({
                                'href': f"notas/{chapter['name']}/{section['name']}/{subsection.get('file', subsection.get('name', ''))}",
                                'title': subsection['title'],
                                'type': 'content',
                                'chapter': chapter['prefix'],
                                'section': section['prefix'],
                                'file': subsection.get('file', subsection.get('name', ''))
                            })
        
        # Build prev/next mapping
        for i, page in enumerate(all_pages):
            sequence_map[page['href']] = {
                'current': page,
                'prev': all_pages[i-1] if i > 0 else None,
                'next': all_pages[i+1] if i < len(all_pages)-1 else None,
                'position': i + 1,
                'total': len(all_pages)
            }
        
        return sequence_map
    
    def _build_quick_access_data(self) -> Dict[str, Any]:
        """Build quick access navigation data."""
        return {
            'recent_pages': [],  # Would be populated by user interaction tracking
            'bookmarks': [],     # User-defined bookmarks
            'search_index': self._build_search_index(),
            'shortcuts': {
                'first_chapter': self._get_first_chapter_href(),
                'last_chapter': self._get_last_chapter_href(),
                'documentation': 'quarto_development/01_automation_system/00_index.qmd',
                'setup_guide': self._get_setup_guide_href()
            }
        }
    
    def _build_search_index(self) -> List[Dict[str, Any]]:
        """Build searchable index for quick navigation."""
        index = []
        
        for chapter in self.content_structure.get('chapters', []):
            index.append({
                'title': f"{chapter['prefix']}. {chapter['title']}",
                'href': f"notas/{chapter['name']}/{chapter.get('index_file', '00_index.qmd')}",
                'type': 'chapter',
                'keywords': [chapter['name'], chapter['title'], 'chapter', chapter['prefix']]
            })
            
            for section in chapter.get('sections', []):
                if section['type'] == 'file':
                    index.append({
                        'title': section['title'],
                        'href': f"notas/{chapter['name']}/{section.get('file', section.get('name', ''))}",
                        'type': 'section_file',
                        'keywords': [section.get('name', ''), section['title'], 'section', chapter['title']]
                    })
                else:
                    index.append({
                        'title': f"{chapter['prefix']}.{section['prefix']} {section['title']}",
                        'href': f"notas/{chapter['name']}/{section['name']}/00_index.qmd",
                        'type': 'section',
                        'keywords': [section['name'], section['title'], 'section', chapter['title']]
                    })
        
        return index
    
    # Helper methods for data enrichment
    def _get_chapter_icon(self, chapter_name: str) -> str:
        """Get appropriate icon for chapter based on name."""
        icon_map = {
            'intro': '🎯',
            'python': '🐍',
            'data': '📊',
            'analysis': '📈',
            'visualization': '📊',
            'machine_learning': '🤖',
            'web': '🌐',
            'database': '🗄️',
            'api': '🔌',
            'deployment': '🚀'
        }
        
        for key, icon in icon_map.items():
            if key in chapter_name.lower():
                return icon
        return '📚'
    
    def _get_section_icon(self, section_name: str) -> str:
        """Get appropriate icon for section based on name."""
        icon_map = {
            'exercise': '✏️',
            'lab': '🧪',
            'project': '🛠️',
            'theory': '📖',
            'practice': '💻',
            'review': '📝',
            'assessment': '📊',
            'homework': '📋'
        }
        
        for key, icon in icon_map.items():
            if key in section_name.lower():
                return icon
        return '📄'
    
    def _get_content_icon(self, content_file: Path) -> str:
        """Get icon based on content file analysis."""
        content = content_file.read_text(encoding='utf-8', errors='ignore')
        
        if 'exercise' in content.lower() or 'homework' in content.lower():
            return '✏️'
        elif 'project' in content.lower():
            return '🛠️'
        elif 'lab' in content.lower():
            return '🧪'
        elif 'quiz' in content.lower() or 'test' in content.lower():
            return '📊'
        else:
            return '📄'
    
    def _get_appendix_icon(self, appendix_name: str) -> str:
        """Get icon for appendix based on name."""
        icon_map = {
            'setup': '⚙️',
            'installation': '💿',
            'troubleshooting': '🔧',
            'reference': '📚',
            'glossary': '📖',
            'resources': '🔗'
        }
        
        for key, icon in icon_map.items():
            if key in appendix_name.lower():
                return icon
        return '📋'
    
    def _extract_title_from_file(self, file_path: Path) -> str:
        """Extract title from Quarto file front matter."""
        try:
            content = file_path.read_text(encoding='utf-8')
            # Look for YAML front matter
            if content.startswith('---'):
                end_index = content.find('---', 3)
                if end_index != -1:
                    yaml_content = content[3:end_index]
                    try:
                        metadata = yaml.safe_load(yaml_content)
                        if isinstance(metadata, dict) and 'title' in metadata:
                            return metadata['title']
                    except yaml.YAMLError:
                        pass
            
            # Fallback: look for first # heading
            lines = content.split('\n')
            for line in lines:
                if line.strip().startswith('# '):
                    return line.strip()[2:].strip()
            
            # Final fallback: use filename
            return file_path.stem.replace('_', ' ').title()
            
        except Exception:
            return file_path.stem.replace('_', ' ').title()
    
    def _estimate_reading_time(self, chapter: Dict) -> int:
        """Estimate reading time for chapter in minutes."""
        # Simple heuristic: 5 minutes per section + 2 minutes for index
        return len(chapter.get('sections', [])) * 5 + 2
    
    def _estimate_file_reading_time(self, file_path: Path) -> int:
        """Estimate reading time for a single file in minutes."""
        try:
            content = file_path.read_text(encoding='utf-8')
            word_count = len(content.split())
            # Average reading speed: 200 words per minute
            return max(1, word_count // 200)
        except Exception:
            return 3  # Default estimate
    
    def _check_for_exercises(self, section: Dict) -> bool:
        """Check if section contains exercises."""
        # This would scan the actual content for exercise markers
        return 'exercise' in section['name'].lower() or 'lab' in section['name'].lower()
    
    def _assess_difficulty(self, section: Dict) -> str:
        """Assess difficulty level of section."""
        name = section['name'].lower()
        if 'intro' in name or 'basic' in name:
            return 'beginner'
        elif 'advanced' in name or 'expert' in name:
            return 'advanced'
        else:
            return 'intermediate'
    
    def _get_appendix_priority(self, appendix_name: str) -> int:
        """Get priority for appendix ordering."""
        priority_map = {
            'setup': 1,
            'installation': 2,
            'troubleshooting': 8,
            'reference': 9,
            'glossary': 10
        }
        
        for key, priority in priority_map.items():
            if key in appendix_name.lower():
                return priority
        return 5
    
    def _get_first_chapter_href(self) -> str:
        """Get href to first chapter."""
        chapters = self.content_structure.get('chapters', [])
        if chapters:
            first_chapter = chapters[0]
            return f"notas/{first_chapter['name']}/{first_chapter.get('index_file', '00_index.qmd')}"
        return ""
    
    def _get_last_chapter_href(self) -> str:
        """Get href to last chapter."""
        chapters = self.content_structure.get('chapters', [])
        if chapters:
            last_chapter = chapters[-1]
            return f"notas/{last_chapter['name']}/{last_chapter.get('index_file', '00_index.qmd')}"
        return ""
    
    def _get_setup_guide_href(self) -> str:
        """Get href to setup guide."""
        appendices = self.content_structure.get('appendices', [])
        for appendix in appendices:
            if 'setup' in appendix['name'].lower() or 'installation' in appendix['name'].lower():
                return f"notas/{appendix['name']}/{appendix.get('index_file', '00_index.qmd')}"
        return ""
    
    def generate_javascript_data(self, output_path: Optional[Path] = None) -> Path:
        """Generate JavaScript data file for navigation."""
        if not output_path:
            output_path = self.output_dir / 'navigation-data.js'
        
        js_content = f"""// Auto-generated navigation data
// Generated at: {datetime.now().isoformat()}
// DO NOT EDIT MANUALLY - This file is auto-generated

window.QuartoNavigation = {json.dumps(self.navigation_data, indent=2)};

// Navigation utility functions
window.QuartoNavUtils = {{
  getCurrentContext: function() {{
    const path = window.location.pathname;
    const parts = path.split('/').filter(p => p);
    
    if (parts.includes('notas')) {{
      const notasIndex = parts.indexOf('notas');
      return {{
        type: 'course',
        chapter: parts[notasIndex + 1] || null,
        section: parts[notasIndex + 2] || null,
        page: parts[notasIndex + 3] || null
      }};
    }} else if (parts.includes('quarto_development')) {{
      return {{ type: 'documentation' }};
    }} else {{
      return {{ type: 'main' }};
    }}
  }},
  
  findInNavigation: function(href) {{
    const sequential = window.QuartoNavigation.sequential_navigation;
    return sequential[href] || null;
  }},
  
  searchContent: function(query) {{
    const index = window.QuartoNavigation.quick_access.search_index;
    const results = index.filter(item => 
      item.title.toLowerCase().includes(query.toLowerCase()) ||
      item.keywords.some(keyword => keyword.toLowerCase().includes(query.toLowerCase()))
    );
    return results.slice(0, 10); // Limit to 10 results
  }}
}};
"""
        
        output_path.write_text(js_content, encoding='utf-8')
        console.print(f"📄 [green]JavaScript data generated:[/green] [cyan]{output_path}[/cyan]")
        return output_path
    
    def generate_json_data(self, output_path: Optional[Path] = None) -> Path:
        """Generate JSON data file for navigation."""
        if not output_path:
            output_path = self.output_dir / 'navigation-data.json'
        
        output_path.write_text(json.dumps(self.navigation_data, indent=2), encoding='utf-8')
        console.print(f"📄 [green]JSON data generated:[/green] [cyan]{output_path}[/cyan]")
        return output_path
    
    def generate_templates(self) -> Dict[str, Path]:
        """Generate navigation template files."""
        templates = {}
        
        # Generate section navigation template
        section_template = self._generate_section_nav_template()
        section_path = self.output_dir / 'section-navigation.qmd'
        section_path.write_text(section_template, encoding='utf-8')
        templates['section'] = section_path
        
        # Generate chapter navigation template
        chapter_template = self._generate_chapter_nav_template()
        chapter_path = self.output_dir / 'chapter-navigation.qmd'
        chapter_path.write_text(chapter_template, encoding='utf-8')
        templates['chapter'] = chapter_path
        
        console.print(f"📄 [green]Navigation templates generated in:[/green] [cyan]{self.output_dir}[/cyan]")
        return templates
    
    def _generate_section_nav_template(self) -> str:
        """Generate section-specific navigation template."""
        return '''<!-- Auto-generated Section Navigation Template -->
```{=html}
<div class="section-navigation-enhanced">
  <script>
    document.addEventListener('DOMContentLoaded', function() {
      // This will be populated by the main navigation system
      if (window.QuartoNavigation && window.CollapsibleNavigation) {
        const nav = new window.CollapsibleNavigation();
        nav.initSectionNavigation();
      }
    });
  </script>
</div>
```
'''
    
    def _generate_chapter_nav_template(self) -> str:
        """Generate chapter-specific navigation template."""
        return '''<!-- Auto-generated Chapter Navigation Template -->
```{=html}
<div class="chapter-navigation-enhanced">
  <script>
    document.addEventListener('DOMContentLoaded', function() {
      // This will be populated by the main navigation system
      if (window.QuartoNavigation && window.CollapsibleNavigation) {
        const nav = new window.CollapsibleNavigation();
        nav.initChapterNavigation();
      }
    });
  </script>
</div>
```
'''
    
    def display_summary(self):
        """Display generation summary."""
        table = Table(title="🧭 Collapsible Navigation Generation Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        metadata = self.navigation_data.get('metadata', {})
        table.add_row("Total Chapters", str(metadata.get('total_chapters', 0)))
        table.add_row("Total Sections", str(metadata.get('total_sections', 0)))
        table.add_row("Navigation Version", metadata.get('navigation_version', 'Unknown'))
        table.add_row("Generated At", metadata.get('generated_at', 'Unknown'))
        
        console.print(table)
        
        # Display structure tree
        tree = Tree("🌳 [bold blue]Navigation Structure[/bold blue]")
        
        chapters_node = tree.add("📚 [bold green]Chapters[/bold green]")
        for chapter in self.navigation_data['site_structure']['chapters']:
            chapter_node = chapters_node.add(f"[cyan]{chapter['number']}. {chapter['title']}[/cyan]")
            for section in chapter['sections']:
                section_node = chapter_node.add(f"[yellow]{section['number']}. {section['title']}[/yellow]")
                if section['subsections']:
                    for subsection in section['subsections'][:3]:  # Show first 3
                        section_node.add(f"[dim]{subsection['title']}[/dim]")
                    if len(section['subsections']) > 3:
                        section_node.add(f"[dim]... and {len(section['subsections']) - 3} more[/dim]")
        
        if self.navigation_data['site_structure']['appendices']:
            appendices_node = tree.add("📋 [bold green]Appendices[/bold green]")
            for appendix in self.navigation_data['site_structure']['appendices']:
                appendices_node.add(f"[cyan]{appendix['letter']}. {appendix['title']}[/cyan]")
        
        if self.navigation_data['site_structure']['documentation']:
            doc_node = tree.add("📖 [bold green]Documentation[/bold green]")
            for doc in self.navigation_data['site_structure']['documentation']:
                doc_section = doc_node.add(f"[cyan]{doc['title']}[/cyan]")
                for subsection in doc['subsections']:
                    doc_section.add(f"[yellow]{subsection['title']}[/yellow]")
        
        console.print(tree)

@click.command()
@click.option('--path', type=click.Path(exists=True, path_type=Path), 
              help='Base directory to scan (auto-detected from config if not provided)')
@click.option('--output-format', '-f', type=click.Choice(['json', 'js', 'both']), 
              default='both', help='Output format for navigation data')
@click.option('--generate-templates', '-t', is_flag=True, 
              help='Generate navigation template files')
@click.option('--output-dir', '-o', type=click.Path(path_type=Path), 
              help='Custom output directory')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def main(path: Optional[Path], output_format: str, generate_templates: bool, 
         output_dir: Optional[Path], verbose: bool):
    """Generate enhanced collapsible navigation for Quarto educational content."""
    
    console.print(Panel.fit(
        "[bold blue]🧭 Collapsible Navigation Generator[/bold blue]\n"
        "[dim]Enhanced hierarchical navigation with collapsible functionality[/dim]",
        title="Navigation Generator",
        border_style="blue"
    ))
    
    try:
        # Initialize generator
        generator = CollapsibleNavGenerator(path)
        
        if output_dir:
            generator.output_dir = output_dir
            generator.output_dir.mkdir(exist_ok=True)
        
        # Scan and analyze content
        navigation_data = generator.scan_and_analyze()
        
        # Generate outputs
        generated_files = []
        
        if output_format in ['json', 'both']:
            json_file = generator.generate_json_data()
            generated_files.append(json_file)
        
        if output_format in ['js', 'both']:
            js_file = generator.generate_javascript_data()
            generated_files.append(js_file)
        
        if generate_templates:
            template_files = generator.generate_templates()
            generated_files.extend(template_files.values())
        
        # Display summary
        generator.display_summary()
        
        # Show generated files
        if generated_files:
            console.print("\n📁 [bold green]Generated Files:[/bold green]")
            for file_path in generated_files:
                console.print(f"  • [cyan]{file_path}[/cyan]")
        
        console.print(f"\n✅ [bold green]Collapsible navigation generation complete![/bold green]")
        
    except Exception as e:
        console.print(f"❌ [bold red]Error generating navigation:[/bold red] {e}")
        if verbose:
            console.print_exception()
        sys.exit(1)

if __name__ == '__main__':
    main() 