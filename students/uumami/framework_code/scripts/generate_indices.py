#!/usr/bin/env python3
"""
Automatic Index Generation for GitHub Class Template Framework

This script generates automatic indices (00_index.md, 00_master_index.md) 
based on content structure and metadata. Integrates with the metadata validation
system to create rich, navigable content indices.

Usage:
    python3 generate_indices.py [base_directory]
    
Features:
    - Chapter-level index generation (00_index.md)
    - Master index generation (00_master_index.md)  
    - Homework detection and special formatting
    - Appendix chapter support (A_, B_, etc.)
    - Rich metadata integration
    - Incremental updates based on content changes
"""

import sys
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import yaml

from rich.console import Console
from rich.progress import Progress, TaskID
from rich.panel import Panel
from rich.table import Table
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

console = Console()

@dataclass
class ContentFile:
    """Represents a content file with metadata and path information"""
    path: Path
    relative_path: Path
    filename: str
    metadata: Dict
    is_homework: bool = False
    is_appendix: bool = False
    chapter_order: int = 0
    section_order: int = 0

@dataclass
class Chapter:
    """Represents a chapter directory with its content files"""
    path: Path
    name: str
    title: str
    order: int
    is_appendix: bool
    files: List[ContentFile]
    index_path: Path
    needs_update: bool = True

@dataclass
class ContentCategory:
    """Represents a content category (framework_tutorials, etc.) with chapters"""
    path: Path
    name: str
    title: str
    chapters: List[Chapter]
    master_index_path: Path
    needs_update: bool = True

class ContentStructureAnalyzer:
    """Analyzes content directory structure and organizes files"""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.parser = MetadataParser()
        self.content_categories = []
        
    def analyze_structure(self) -> List[ContentCategory]:
        """
        Analyze the complete content structure.
        
        Returns:
            List of ContentCategory objects with organized content
        """
        console.print(Panel.fit(
            "[bold blue]Content Structure Analysis[/bold blue]\n"
            f"Base directory: [cyan]{self.base_dir}[/cyan]",
            title="📁 Directory Analysis"
        ))
        
        # Standard content directories
        content_dirs = ['framework_tutorials', 'framework_documentation', 'class_notes']
        
        categories = []
        
        for content_dir in content_dirs:
            content_path = self.base_dir / content_dir
            if not content_path.exists():
                console.print(f"[yellow]⚠️  Directory {content_dir} not found, skipping[/yellow]")
                continue
            
            category = self._analyze_category(content_path)
            if category:
                categories.append(category)
        
        return categories
    
    def _analyze_category(self, category_path: Path) -> Optional[ContentCategory]:
        """Analyze a single content category directory"""
        
        category_name = category_path.name
        category_title = self._generate_category_title(category_name)
        
        console.print(f"\n[bold]Analyzing category: [cyan]{category_name}[/cyan][/bold]")
        
        # Find chapter directories
        chapters = []
        chapter_dirs = [d for d in category_path.iterdir() 
                       if d.is_dir() and not d.name.startswith('.')]
        
        if not chapter_dirs:
            console.print(f"[yellow]No chapter directories found in {category_name}[/yellow]")
            return None
        
        # Sort chapter directories
        chapter_dirs.sort(key=self._chapter_sort_key)
        
        for chapter_dir in chapter_dirs:
            chapter = self._analyze_chapter(chapter_dir, category_path)
            if chapter:
                chapters.append(chapter)
        
        if not chapters:
            console.print(f"[yellow]No valid chapters found in {category_name}[/yellow]")
            return None
        
        master_index_path = category_path / "00_master_index.md"
        
        return ContentCategory(
            path=category_path,
            name=category_name,
            title=category_title,
            chapters=chapters,
            master_index_path=master_index_path
        )
    
    def _analyze_chapter(self, chapter_path: Path, category_path: Path) -> Optional[Chapter]:
        """Analyze a single chapter directory"""
        
        chapter_name = chapter_path.name
        console.print(f"  📂 Chapter: [cyan]{chapter_name}[/cyan]")
        
        # Find content files (exclude existing indices)
        content_files = []
        md_files = [f for f in chapter_path.glob('*.md') 
                   if not f.name.startswith('00_')]
        
        if not md_files:
            console.print(f"    [yellow]No content files found[/yellow]")
            return None
        
        # Sort files by naming convention
        md_files.sort(key=self._file_sort_key)
        
        for md_file in md_files:
            content_file = self._analyze_content_file(md_file, chapter_path, category_path)
            if content_file:
                content_files.append(content_file)
        
        if not content_files:
            console.print(f"    [yellow]No valid content files found[/yellow]")
            return None
        
        # Extract chapter metadata
        chapter_title = self._generate_chapter_title(chapter_name, content_files)
        chapter_order = self._extract_chapter_order(chapter_name)
        is_appendix = chapter_name[0].isupper() and chapter_name[0].isalpha()
        
        index_path = chapter_path / "00_index.md"
        
        console.print(f"    ✅ Found {len(content_files)} content files")
        
        return Chapter(
            path=chapter_path,
            name=chapter_name,
            title=chapter_title,
            order=chapter_order,
            is_appendix=is_appendix,
            files=content_files,
            index_path=index_path
        )
    
    def _analyze_content_file(self, file_path: Path, chapter_path: Path, category_path: Path) -> Optional[ContentFile]:
        """Analyze a single content file"""
        
        # Parse metadata
        metadata, errors, warnings = self.parser.parse_frontmatter(file_path)
        
        if errors:
            console.print(f"    [red]⚠️  {file_path.name}: {len(errors)} metadata errors[/red]")
            # Continue processing even with errors (graceful degradation)
        
        # Calculate relative path
        relative_path = file_path.relative_to(self.base_dir)
        
        # Determine file characteristics
        filename = file_path.name
        is_homework = filename.startswith('hw_')
        is_appendix = chapter_path.name[0].isupper() and chapter_path.name[0].isalpha()
        
        # Extract ordering information
        chapter_order = self._extract_chapter_order(chapter_path.name)
        section_order = self._extract_section_order(filename)
        
        return ContentFile(
            path=file_path,
            relative_path=relative_path,
            filename=filename,
            metadata=metadata,
            is_homework=is_homework,
            is_appendix=is_appendix,
            chapter_order=chapter_order,
            section_order=section_order
        )
    
    def _chapter_sort_key(self, chapter_dir: Path) -> Tuple:
        """Generate sort key for chapter directories"""
        name = chapter_dir.name
        
        # Handle appendix chapters (A_, B_, etc.)
        if name[0].isupper() and name[0].isalpha():
            return (1, name[0], name)  # Appendices come after numbered chapters
        
        # Handle numbered chapters (01_, 02_, etc.)
        if name[:2].isdigit():
            return (0, int(name[:2]), name)
        
        # Fallback for other naming patterns
        return (0, 999, name)
    
    def _file_sort_key(self, file_path: Path) -> Tuple:
        """Generate sort key for content files"""
        name = file_path.stem
        
        # Handle homework files (hw_01, hw_02, etc.)
        if name.startswith('hw_'):
            if name[3:].isdigit():
                return (2, int(name[3:]), name)  # Homework comes after content
            return (2, 999, name)
        
        # Handle numbered content files (01_, 02_, etc.)
        if name[:2].isdigit():
            return (0, int(name[:2]), name)
        
        # Fallback for other patterns
        return (1, 999, name)
    
    def _extract_chapter_order(self, chapter_name: str) -> int:
        """Extract numeric order from chapter directory name"""
        if chapter_name[:2].isdigit():
            return int(chapter_name[:2])
        return 999  # Appendices and special chapters
    
    def _extract_section_order(self, filename: str) -> int:
        """Extract numeric order from content file name"""
        name = Path(filename).stem
        if name[:2].isdigit():
            return int(name[:2])
        if name.startswith('hw_') and name[3:].isdigit():
            return int(name[3:])
        return 999
    
    def _generate_category_title(self, category_name: str) -> str:
        """Generate human-readable title for content category"""
        # Convert snake_case to Title Case
        return category_name.replace('_', ' ').title()
    
    def _generate_chapter_title(self, chapter_name: str, content_files: List[ContentFile]) -> str:
        """Generate human-readable title for chapter"""
        
        # Try to get title from first content file metadata
        if content_files:
            first_file = content_files[0]
            if 'title' in first_file.metadata:
                # Extract chapter from file title (e.g., "Understanding the Framework" from "What is this Framework?")
                title = first_file.metadata['title']
                # For now, use the directory name converted to title case
                pass
        
        # Convert directory name to title (e.g., "01_understanding_framework" -> "Understanding Framework")
        if chapter_name[:2].isdigit() and chapter_name[2] == '_':
            title_part = chapter_name[3:]
        elif chapter_name[0].isupper() and len(chapter_name) > 2 and chapter_name[1] == '_':
            title_part = chapter_name[2:]
        else:
            title_part = chapter_name
        
        return title_part.replace('_', ' ').title()

class IndexGenerator:
    """Generates index files based on content structure analysis"""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.analyzer = ContentStructureAnalyzer(base_dir)
    
    def generate_all_indices(self) -> bool:
        """
        Generate all indices for the content structure.
        
        Returns:
            bool: True if successful, False if errors occurred
        """
        console.print(Panel.fit(
            "[bold blue]Automatic Index Generation[/bold blue]\n"
            f"Base directory: [cyan]{self.base_dir}[/cyan]",
            title="📚 Index Generation System"
        ))
        
        # Analyze content structure
        categories = self.analyzer.analyze_structure()
        
        if not categories:
            console.print("[yellow]⚠️  No content categories found for index generation[/yellow]")
            return True
        
        success = True
        
        # Generate indices for each category
        with Progress() as progress:
            task = progress.add_task("[cyan]Generating indices...", total=len(categories))
            
            for category in categories:
                category_success = self._generate_category_indices(category)
                success = success and category_success
                progress.update(task, advance=1)
        
        # Report results
        if success:
            console.print(f"\n[bold green]✅ Successfully generated indices for {len(categories)} categories[/bold green]")
        else:
            console.print(f"\n[bold red]❌ Index generation completed with errors[/bold red]")
        
        return success
    
    def _generate_category_indices(self, category: ContentCategory) -> bool:
        """Generate indices for a single content category"""
        
        console.print(f"\n[bold]Generating indices for: [cyan]{category.name}[/cyan][/bold]")
        
        success = True
        
        # Generate chapter indices
        for chapter in category.chapters:
            chapter_success = self._generate_chapter_index(chapter, category)
            success = success and chapter_success
        
        # Generate master index
        master_success = self._generate_master_index(category)
        success = success and master_success
        
        return success
    
    def _generate_chapter_index(self, chapter: Chapter, category: ContentCategory) -> bool:
        """Generate 00_index.md for a chapter"""
        
        console.print(f"  📝 Generating chapter index: {chapter.name}")
        
        try:
            # Generate chapter index content
            index_content = self._create_chapter_index_content(chapter, category)
            
            # Write to file
            with open(chapter.index_path, 'w', encoding='utf-8') as f:
                f.write(index_content)
            
            console.print(f"    ✅ Generated {chapter.index_path.name}")
            return True
        except Exception as e:
            console.print(f"    [red]Error generating chapter index: {e}[/red]")
            return False
    
    def _create_chapter_index_content(self, chapter: Chapter, category: ContentCategory) -> str:
        """Create the content for a chapter index file"""
        
        # Header with metadata
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        content = []
        content.append("---")
        content.append(f'title: "{chapter.title}"')
        content.append('type: "index"')
        content.append(f'date: "{current_date}"')
        content.append('author: "Framework (Auto-generated)"')
        content.append(f'summary: "Index for {chapter.title} chapter"')
        content.append("---")
        content.append("")
        content.append(f"# {chapter.title}")
        content.append("")
        content.append("*This index is automatically generated from the chapter content.*")
        content.append("")
        
        # Separate content files by type
        regular_files = [f for f in chapter.files if not f.is_homework]
        homework_files = [f for f in chapter.files if f.is_homework]
        
        # Main content section
        if regular_files:
            content.append("## 📚 Chapter Content")
            content.append("")
            
            for file in regular_files:
                content.extend(self._format_file_entry(file))
                content.append("")
        
        # Homework section
        if homework_files:
            content.append("## 📝 Homework & Assignments")
            content.append("")
            
            for file in homework_files:
                content.extend(self._format_homework_entry(file))
                content.append("")
        
        # Navigation section
        content.extend(self._create_chapter_navigation(chapter, category))
        
        # Footer
        content.append("---")
        content.append("")
        content.append("*This index was automatically generated. Do not edit manually.*")
        
        return "\n".join(content)
    
    def _format_file_entry(self, file: ContentFile) -> List[str]:
        """Format a regular content file entry for the index"""
        
        entry = []
        
        # Title with link
        title = file.metadata.get('title', file.filename)
        entry.append(f"### [{title}]({file.filename})")
        
        # Summary
        summary = file.metadata.get('summary', '')
        if summary:
            entry.append(f"*{summary}*")
            entry.append("")
        
        # Metadata badges
        badges = []
        
        # Difficulty badge
        difficulty = file.metadata.get('difficulty', '')
        if difficulty:
            difficulty_emoji = {
                'easy': '🟢',
                'medium': '🟡', 
                'hard': '🔴'
            }
            emoji = difficulty_emoji.get(difficulty, '⚪')
            badges.append(f"{emoji} **{difficulty.title()}**")
        
        # Estimated time
        estimated_time = file.metadata.get('estimated_time', '')
        if estimated_time:
            badges.append(f"⏱️ **{estimated_time} min**")
        
        # Content type
        content_type = file.metadata.get('type', '')
        if content_type:
            badges.append(f"📋 **{content_type.title()}**")
        
        if badges:
            entry.append(" | ".join(badges))
        
        return entry
    
    def _format_homework_entry(self, file: ContentFile) -> List[str]:
        """Format a homework file entry for the index"""
        
        entry = []
        
        # Title with homework icon
        title = file.metadata.get('title', file.filename)
        entry.append(f"### 📝 [{title}]({file.filename})")
        
        # Summary
        summary = file.metadata.get('summary', '')
        if summary:
            entry.append(f"*{summary}*")
            entry.append("")
        
        # Homework-specific metadata
        badges = []
        
        # Difficulty
        difficulty = file.metadata.get('difficulty', '')
        if difficulty:
            difficulty_emoji = {
                'easy': '🟢',
                'medium': '🟡',
                'hard': '🔴'
            }
            emoji = difficulty_emoji.get(difficulty, '⚪')
            badges.append(f"{emoji} **{difficulty.title()}**")
        
        # Estimated time (important for homework)
        estimated_time = file.metadata.get('estimated_time', '')
        if estimated_time:
            badges.append(f"⏱️ **~{estimated_time} min**")
        
        # Due date (if available in metadata)
        due_date = file.metadata.get('due_date', '')
        if due_date:
            badges.append(f"📅 **Due: {due_date}**")
        
        if badges:
            entry.append(" | ".join(badges))
        
        return entry
    
    def _create_chapter_navigation(self, chapter: Chapter, category: ContentCategory) -> List[str]:
        """Create navigation section for chapter index"""
        
        nav = []
        nav.append("## 🧭 Navigation")
        nav.append("")
        
        # Find previous and next chapters
        chapter_index = next((i for i, c in enumerate(category.chapters) if c.name == chapter.name), -1)
        
        nav_links = []
        
        # Previous chapter
        if chapter_index > 0:
            prev_chapter = category.chapters[chapter_index - 1]
            nav_links.append(f"← [Previous: {prev_chapter.title}](../{prev_chapter.name}/00_index.md)")
        
        # Up to category
        nav_links.append(f"↑ [Back to {category.title}](../00_master_index.md)")
        
        # Next chapter  
        if chapter_index < len(category.chapters) - 1:
            next_chapter = category.chapters[chapter_index + 1]
            nav_links.append(f"[Next: {next_chapter.title}](../{next_chapter.name}/00_index.md) →")
        
        nav.extend(nav_links)
        nav.append("")
        
        return nav
    
    def _generate_master_index(self, category: ContentCategory) -> bool:
        """Generate 00_master_index.md for a category"""
        
        console.print(f"  📋 Generating master index: {category.name}")
        
        try:
            # Generate master index content
            index_content = self._create_master_index_content(category)
            
            # Write to file
            with open(category.master_index_path, 'w', encoding='utf-8') as f:
                f.write(index_content)
            
            console.print(f"    ✅ Generated {category.master_index_path.name}")
            return True
        except Exception as e:
            console.print(f"    [red]Error generating master index: {e}[/red]")
            return False
    
    def _create_master_index_content(self, category: ContentCategory) -> str:
        """Create the content for a master index file"""
        
        # Header with metadata
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        content = []
        content.append("---")
        content.append(f'title: "{category.title}"')
        content.append('type: "master-index"')
        content.append(f'date: "{current_date}"')
        content.append('author: "Framework (Auto-generated)"')
        content.append(f'summary: "Master index for {category.title} content"')
        content.append("---")
        content.append("")
        content.append(f"# {category.title}")
        content.append("")
        content.append("*This master index is automatically generated from all chapter content.*")
        content.append("")
        
        # Category overview
        content.append("## 📖 Overview")
        content.append("")
        overview_text = self._generate_category_overview(category)
        content.append(overview_text)
        content.append("")
        
        # Statistics
        total_files = sum(len(chapter.files) for chapter in category.chapters)
        homework_count = sum(len([f for f in chapter.files if f.is_homework]) for chapter in category.chapters)
        regular_count = total_files - homework_count
        
        content.append("## 📊 Content Statistics")
        content.append("")
        content.append(f"- **{len(category.chapters)}** chapters")
        content.append(f"- **{regular_count}** content files")
        if homework_count > 0:
            content.append(f"- **{homework_count}** homework assignments")
        content.append("")
        
        # Chapters section
        regular_chapters = [c for c in category.chapters if not c.is_appendix]
        appendix_chapters = [c for c in category.chapters if c.is_appendix]
        
        if regular_chapters:
            content.append("## 📚 Chapters")
            content.append("")
            
            for chapter in regular_chapters:
                content.extend(self._format_chapter_entry(chapter))
                content.append("")
        
        # Appendices section
        if appendix_chapters:
            content.append("## 📎 Appendices")
            content.append("")
            
            for chapter in appendix_chapters:
                content.extend(self._format_chapter_entry(chapter))
                content.append("")
        
        # Homework overview
        if homework_count > 0:
            content.append("## 📝 All Homework & Assignments")
            content.append("")
            
            for chapter in category.chapters:
                homework_files = [f for f in chapter.files if f.is_homework]
                if homework_files:
                    content.append(f"### {chapter.title}")
                    for file in homework_files:
                        title = file.metadata.get('title', file.filename)
                        content.append(f"- [{title}]({chapter.name}/{file.filename})")
                    content.append("")
        
        # Footer
        content.append("---")
        content.append("")
        content.append("*This master index was automatically generated. Do not edit manually.*")
        
        return "\n".join(content)
    
    def _generate_category_overview(self, category: ContentCategory) -> str:
        """Generate overview text for a content category"""
        
        overviews = {
            'framework_tutorials': 
                "Step-by-step guides for using the framework. Start here if you're new to the system.",
            'framework_documentation': 
                "Technical documentation for framework internals. Useful for contributors and advanced users.",
            'class_notes': 
                "Course content and instructional materials organized by topic.",
        }
        
        return overviews.get(category.name, f"Content for {category.title}.")
    
    def _format_chapter_entry(self, chapter: Chapter) -> List[str]:
        """Format a chapter entry for the master index"""
        
        entry = []
        
        # Chapter title with link to index
        entry.append(f"### [{chapter.title}]({chapter.name}/00_index.md)")
        
        # Chapter summary (from first file or derived)
        chapter_summary = self._get_chapter_summary(chapter)
        if chapter_summary:
            entry.append(f"*{chapter_summary}*")
            entry.append("")
        
        # Chapter statistics
        regular_files = [f for f in chapter.files if not f.is_homework]
        homework_files = [f for f in chapter.files if f.is_homework]
        
        stats = []
        if regular_files:
            stats.append(f"{len(regular_files)} content files")
        if homework_files:
            stats.append(f"{len(homework_files)} assignments")
        
        if stats:
            entry.append(f"📊 {' | '.join(stats)}")
        
        # Quick links to content
        if len(regular_files) <= 3:  # Show direct links for small chapters
            entry.append("")
            entry.append("**Content:**")
            for file in regular_files:
                title = file.metadata.get('title', file.filename)
                difficulty = file.metadata.get('difficulty', '')
                difficulty_emoji = {
                    'easy': '🟢',
                    'medium': '🟡',
                    'hard': '🔴'
                }.get(difficulty, '')
                
                difficulty_badge = f" {difficulty_emoji}" if difficulty_emoji else ""
                entry.append(f"- [{title}]({chapter.name}/{file.filename}){difficulty_badge}")
        
        return entry
    
    def _get_chapter_summary(self, chapter: Chapter) -> str:
        """Get or generate a summary for a chapter"""
        
        # Try to get summary from first file
        if chapter.files:
            first_file = chapter.files[0]
            summary = first_file.metadata.get('summary', '')
            if summary:
                # Adapt file summary to chapter context
                return f"Chapter covering {summary.lower()}"
        
        # Fallback to generic summary
        return f"Chapter {chapter.order}: {chapter.title}"

def load_index_config(base_dir: Path) -> Dict:
    """
    Load index generation configuration from dna.yml
    
    Args:
        base_dir: Base directory containing dna.yml
        
    Returns:
        Configuration dictionary
    """
    dna_path = base_dir / 'dna.yml'
    config = {
        'index_generation': True,
        'force_regeneration': False
    }
    
    if dna_path.exists():
        try:
            with open(dna_path, 'r') as f:
                dna_config = yaml.safe_load(f) or {}
            
            if 'index_generation' in dna_config:
                config['index_generation'] = bool(dna_config['index_generation'])
                
        except Exception as e:
            console.print(f"[yellow]Warning: Could not read dna.yml: {e}[/yellow]")
    
    return config

def main():
    """Main entry point for index generation"""
    
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate automatic indices for framework content"
    )
    parser.add_argument(
        'base_dir', 
        nargs='?', 
        default='.',
        help='Base directory to analyze (default: current directory)'
    )
    parser.add_argument(
        '--force', 
        action='store_true',
        help='Force regeneration of all indices'
    )
    
    args = parser.parse_args()
    
    # Resolve base directory
    base_dir = Path(args.base_dir).resolve()
    if not base_dir.exists():
        console.print(f"[red]Error: Directory {base_dir} does not exist[/red]")
        sys.exit(2)
    
    # Load configuration
    config = load_index_config(base_dir)
    if args.force:
        config['force_regeneration'] = True
    
    # Check if index generation is enabled
    if not config['index_generation']:
        console.print("[yellow]Index generation is disabled in configuration[/yellow]")
        sys.exit(0)
    
    try:
        # Run index generation
        generator = IndexGenerator(base_dir)
        success = generator.generate_all_indices()
        
        # Exit with appropriate code
        if success:
            sys.exit(0)
        else:
            console.print(f"\n[red]Index generation failed[/red]")
            sys.exit(1)
            
    except Exception as e:
        console.print(f"[red]Index generation script error: {e}[/red]")
        sys.exit(2)

if __name__ == "__main__":
    main() 