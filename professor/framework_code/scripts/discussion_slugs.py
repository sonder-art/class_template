#!/usr/bin/env python3
"""
Discussion Slug Management for GitHub Class Template Framework

This module handles the generation and management of stable slugs for discussion systems.
Slugs are generated once from creation context and never change to maintain discussion continuity.
"""

import sys
import argparse
from pathlib import Path
from typing import List, Tuple, Set

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress

# Import our metadata system
try:
    from content_metadata import (
        MetadataParser, discover_content_files,
        generate_creation_based_slug, get_all_slugs_from_files, should_have_discussions,
        DISCUSSION_ENABLED_TYPES
    )
except ImportError:
    print("❌ Missing content_metadata module. Run from framework_code/scripts/")
    sys.exit(1)

console = Console()

class SlugManager:
    """Manages stable slug generation for discussions"""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.parser = MetadataParser()
        self.existing_slugs: Set[str] = set()
        self.files_with_generated_slugs: List[Tuple[Path, str]] = []
    
    def generate_missing_slugs(self, force: bool = False) -> bool:
        """Generate stable slugs for content missing them"""
        console.print(Panel.fit(
            "🔗 [bold]Discussion Slug Generator[/bold]\n"
            f"Base directory: [cyan]{self.base_dir}[/cyan]\n"
            f"Force regeneration: [{'red' if force else 'green'}]{force}[/]",
            title="Stable Slug Management"
        ))
        
        # Discover content files
        content_files = discover_content_files(self.base_dir)
        
        if not content_files:
            console.print("[yellow]⚠️  No content files found[/yellow]")
            return True
        
        console.print(f"📄 Found {len(content_files)} content files")
        
        # Get existing slugs
        self.existing_slugs = get_all_slugs_from_files(content_files)
        console.print(f"📋 Found {len(self.existing_slugs)} existing slugs")
        
        files_needing_slugs = []
        
        # Check which files need slugs
        for file_path in content_files:
            try:
                metadata, errors, warnings = self.parser.parse_frontmatter(file_path)
                
                # Skip files with errors in required fields
                if errors:
                    continue
                
                # Check if this file should have discussions
                if should_have_discussions(metadata):
                    needs_slug = (
                        not metadata.get('slug') or 
                        not metadata.get('slug_locked') or 
                        force
                    )
                    
                    if needs_slug:
                        files_needing_slugs.append((file_path, metadata))
                        
            except Exception as e:
                console.print(f"[yellow]⚠️  Could not process {file_path}: {e}[/yellow]")
                continue
        
        if not files_needing_slugs:
            console.print("✅ All discussion-enabled content already has stable slugs")
            return True
        
        console.print(f"🔄 Generating slugs for {len(files_needing_slugs)} files...")
        
        if not force:
            console.print("\nFiles that will get new slugs:")
            for file_path, metadata in files_needing_slugs:
                rel_path = file_path.relative_to(self.base_dir)
                current_slug = metadata.get('slug', '[none]')
                console.print(f"  📄 {rel_path} (current: {current_slug})")
            
            from rich.prompt import Confirm
            if not Confirm.ask("\nProceed with slug generation?"):
                console.print("❌ Operation cancelled")
                return False
        
        # Generate slugs with progress bar
        success_count = 0
        with Progress() as progress:
            task = progress.add_task("[cyan]Generating slugs...", total=len(files_needing_slugs))
            
            for file_path, metadata in files_needing_slugs:
                try:
                    if self._generate_slug_for_file(file_path, metadata):
                        success_count += 1
                except Exception as e:
                    console.print(f"[red]❌ Failed to generate slug for {file_path}: {e}[/red]")
                
                progress.update(task, advance=1)
        
        console.print(f"\n✅ Generated stable slugs for {success_count}/{len(files_needing_slugs)} files")
        
        if self.files_with_generated_slugs:
            console.print("\n📝 [bold]Files with new slugs:[/bold]")
            for file_path, slug in self.files_with_generated_slugs:
                rel_path = file_path.relative_to(self.base_dir)
                console.print(f"  📄 {rel_path} → [cyan]{slug}[/cyan]")
        
        return success_count == len(files_needing_slugs)
    
    def audit_slugs(self):
        """Audit existing slugs and show status"""
        console.print(Panel.fit(
            "🔍 [bold]Discussion Slug Audit[/bold]\n"
            f"Base directory: [cyan]{self.base_dir}[/cyan]",
            title="Slug Status Report"
        ))
        
        # Discover content files
        content_files = discover_content_files(self.base_dir)
        
        if not content_files:
            console.print("[yellow]⚠️  No content files found[/yellow]")
            return
        
        stats = {
            'total_files': len(content_files),
            'discussion_enabled': 0,
            'has_slug': 0,
            'locked_slug': 0,
            'missing_slug': 0,
            'unlocked_slug': 0
        }
        
        missing_slugs = []
        unlocked_slugs = []
        
        for file_path in content_files:
            try:
                metadata, errors, warnings = self.parser.parse_frontmatter(file_path)
                
                if should_have_discussions(metadata):
                    stats['discussion_enabled'] += 1
                    
                    if metadata.get('slug'):
                        stats['has_slug'] += 1
                        
                        if metadata.get('slug_locked'):
                            stats['locked_slug'] += 1
                        else:
                            stats['unlocked_slug'] += 1
                            unlocked_slugs.append(file_path)
                    else:
                        stats['missing_slug'] += 1
                        missing_slugs.append(file_path)
                        
            except Exception:
                continue
        
        # Display statistics
        from rich.table import Table
        table = Table(title="Slug Status Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Count", justify="right", style="white")
        table.add_column("Percentage", justify="right", style="dim")
        
        table.add_row("Total Files", str(stats['total_files']), "100%")
        table.add_row("Discussion Enabled", str(stats['discussion_enabled']), 
                     f"{stats['discussion_enabled']/stats['total_files']*100:.1f}%" if stats['total_files'] > 0 else "0%")
        table.add_row("Has Slug", str(stats['has_slug']), 
                     f"{stats['has_slug']/stats['discussion_enabled']*100:.1f}%" if stats['discussion_enabled'] > 0 else "0%")
        table.add_row("Locked Slugs", str(stats['locked_slug']), 
                     f"{stats['locked_slug']/stats['discussion_enabled']*100:.1f}%" if stats['discussion_enabled'] > 0 else "0%")
        
        console.print(table)
        
        # Show issues
        if missing_slugs:
            console.print(f"\n[red]❌ {len(missing_slugs)} files missing slugs:[/red]")
            for file_path in missing_slugs[:5]:  # Show first 5
                rel_path = file_path.relative_to(self.base_dir)
                console.print(f"  📄 {rel_path}")
            if len(missing_slugs) > 5:
                console.print(f"  ... and {len(missing_slugs) - 5} more")
        
        if unlocked_slugs:
            console.print(f"\n[yellow]⚠️  {len(unlocked_slugs)} files with unlocked slugs:[/yellow]")
            for file_path in unlocked_slugs[:5]:  # Show first 5
                rel_path = file_path.relative_to(self.base_dir)
                console.print(f"  📄 {rel_path}")
            if len(unlocked_slugs) > 5:
                console.print(f"  ... and {len(unlocked_slugs) - 5} more")
        
        if not missing_slugs and not unlocked_slugs:
            console.print("\n[green]✅ All discussion-enabled content has locked slugs![/green]")
    
    def _generate_slug_for_file(self, file_path: Path, metadata: dict) -> bool:
        """Generate and save slug for a single file"""
        try:
            # If forcing regeneration, remove old slug from existing set
            if metadata.get('slug'):
                self.existing_slugs.discard(metadata['slug'])
            
            # Generate stable slug
            new_slug = generate_creation_based_slug(metadata, self.existing_slugs)
            
            # Update metadata
            metadata['slug'] = new_slug
            metadata['slug_locked'] = True
            metadata['slug_source'] = 'creation_context'
            
            # Update existing slugs set
            self.existing_slugs.add(new_slug)
            
            # Write back to file
            self._update_frontmatter(file_path, metadata)
            
            # Track for reporting
            self.files_with_generated_slugs.append((file_path, new_slug))
            
            return True
            
        except Exception as e:
            console.print(f"[red]❌ Error generating slug for {file_path}: {e}[/red]")
            return False
    
    def _update_frontmatter(self, file_path: Path, metadata: dict):
        """Update file frontmatter with new metadata"""
        import yaml
        
        # Read current file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split frontmatter and content
        if content.startswith('---\n'):
            parts = content.split('---\n', 2)
            if len(parts) >= 3:
                # parts[0] is empty, parts[1] is frontmatter, parts[2] is content
                body_content = parts[2]
            else:
                # Malformed frontmatter
                body_content = content
        else:
            body_content = content
        
        # Write updated file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('---\n')
            yaml.dump(metadata, f, default_flow_style=False, sort_keys=True, allow_unicode=True)
            f.write('---\n')
            f.write(body_content)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Manage discussion slugs for framework content"
    )
    parser.add_argument(
        'base_dir', 
        nargs='?', 
        default='.',
        help='Base directory to process (default: current directory)'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Generate command
    gen_parser = subparsers.add_parser('generate', help='Generate missing slugs')
    gen_parser.add_argument('--force', action='store_true', 
                           help='Force regeneration of existing slugs')
    
    # Audit command
    subparsers.add_parser('audit', help='Audit existing slug status')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Resolve base directory
    base_dir = Path(args.base_dir).resolve()
    if not base_dir.exists():
        console.print(f"[red]Error: Directory {base_dir} does not exist[/red]")
        sys.exit(1)
    
    try:
        manager = SlugManager(base_dir)
        
        if args.command == 'generate':
            success = manager.generate_missing_slugs(force=getattr(args, 'force', False))
            sys.exit(0 if success else 1)
            
        elif args.command == 'audit':
            manager.audit_slugs()
            sys.exit(0)
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    main()