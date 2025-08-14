#!/usr/bin/env python3
"""
Student Directory Sync Tool - Framework Level Synchronization
Copies files from professor/ directory to students/<username>/ directory
Follows non-destructive sync principles with KEEP block preservation

NO GIT OPERATIONS - Pure file-to-file directory synchronization
SMART EXCLUSIONS - Avoids syncing auto-generated content and build artifacts
"""

import os
import sys
import shutil
import re
import fnmatch
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table
from rich.prompt import Confirm
from rich.tree import Tree
import yaml

console = Console()

# Content sync includes only these directories
CONTENT_DIRECTORIES = [
    'class_notes'
]

# Exclusion patterns for content sync
SYNC_EXCLUSIONS = {
    'generated_content': [
        '**/00_index.md',
        '**/00_master_index.md',
        '*.backup'
    ],
    'build_artifacts': [
        '__pycache__/',
        '__pycache__/**',
        '*.pyc', '*.pyo', '*.pyd',
        '.hugo_build.lock',
        '*.log', '*.tmp', '*.temp'
    ],
    'personal_files': [
        '.vscode/', '.idea/',
        '.vscode/**', '.idea/**',
        '*.swp', '*.swo', '*~',
        '.DS_Store', 'Thumbs.db', 'desktop.ini',
        '.env', '.env.local', '.env.*'
    ]
}

def get_all_exclusion_patterns():
    """Get flattened list of all exclusion patterns."""
    patterns = []
    for category, pattern_list in SYNC_EXCLUSIONS.items():
        patterns.extend(pattern_list)
    return patterns

def should_sync_file(rel_path, exclusion_patterns):
    """Check if file should be synced based on exclusion patterns."""
    path_str = str(rel_path).replace('\\', '/')  # Normalize path separators
    
    for pattern in exclusion_patterns:
        # Direct match
        if fnmatch.fnmatch(path_str, pattern):
            return False, f"pattern: {pattern}"
        
        # Directory prefix match
        if pattern.endswith('/') and path_str.startswith(pattern):
            return False, f"directory: {pattern}"
        
        # Parent directory match for ** patterns
        if '/**' in pattern:
            base_pattern = pattern.replace('/**', '/')
            if path_str.startswith(base_pattern):
                return False, f"recursive: {pattern}"
    
    return True, "include"

def is_framework_file(rel_path):
    """Check if file is part of framework and should always be overwritten."""
    path_str = str(rel_path).replace('\\', '/')  # Normalize path separators
    
    # Framework files that should always be synced/overwritten
    framework_paths = [
        'framework_code/scripts/',
        'framework_code/themes/',
        'framework_code/components/',
        'framework_code/css/',
        'framework_code/assets/',
        'framework_code/hugo_config/'
    ]
    
    for framework_path in framework_paths:
        if path_str.startswith(framework_path):
            return True
    
    return False

def load_dna_config():
    """Load dna.yml configuration to get professor profile."""
    try:
        with open("dna.yml", 'r') as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        console.print("[red]❌ dna.yml not found in repository root[/red]")
        return {}
    except yaml.YAMLError as e:
        console.print(f"[red]❌ Error parsing dna.yml: {e}[/red]")
        return {}

def detect_student_directory():
    """Detect which student directory we're syncing to."""
    current_dir = Path.cwd()
    
    # Check if we're in a student directory
    if current_dir.parent.name == "students":
        return current_dir.name
    
    # If not, ask user to specify
    console.print("[yellow]⚠️  Not in a student directory[/yellow]")
    
    # List available student directories
    students_dir = Path("students")
    if students_dir.exists():
        student_dirs = [d.name for d in students_dir.iterdir() if d.is_dir()]
        if student_dirs:
            console.print(f"[blue]📁 Available student directories:[/blue] {', '.join(student_dirs)}")
    
    student_name = console.input("[blue]🎓 Enter student username to sync: [/blue]")
    return student_name.strip()

def scan_directory_changes(professor_dir, student_dir):
    """Scan for content files that need to be synced."""
    changes = {
        'new_files': [],
        'updated_files': [],
        'unchanged_files': [],
        'student_only_files': [],
        'excluded_files': []
    }
    
    professor_path = Path(professor_dir)
    student_path = Path(student_dir)
    exclusion_patterns = get_all_exclusion_patterns()
    
    # Ensure student directory exists
    student_path.mkdir(parents=True, exist_ok=True)
    
    # Only scan content directories in professor
    for content_dir in CONTENT_DIRECTORIES:
        content_path = professor_path / content_dir
        if not content_path.exists():
            continue
            
        for prof_file in content_path.rglob('*'):
            if prof_file.is_file():
                # Calculate relative path from professor root
                rel_path = prof_file.relative_to(professor_path)
                
                # Check exclusions
                should_sync, reason = should_sync_file(rel_path, exclusion_patterns)
                if not should_sync:
                    changes['excluded_files'].append((rel_path, reason))
                    continue
                
                student_file = student_path / rel_path
                
                if not student_file.exists():
                    changes['new_files'].append(rel_path)
                elif student_file.stat().st_mtime < prof_file.stat().st_mtime:
                    changes['updated_files'].append(rel_path)
                else:
                    changes['unchanged_files'].append(rel_path)
    
    # Find student-only content files
    for content_dir in CONTENT_DIRECTORIES:
        student_content_path = student_path / content_dir
        if not student_content_path.exists():
            continue
            
        for student_file in student_content_path.rglob('*'):
            if student_file.is_file():
                rel_path = student_file.relative_to(student_path)
                prof_file = professor_path / rel_path
                
                # Skip if excluded or professor has this file
                should_sync, _ = should_sync_file(rel_path, exclusion_patterns)
                if should_sync and not prof_file.exists():
                    changes['student_only_files'].append(rel_path)
    
    return changes

def preserve_keep_blocks(content):
    """Extract KEEP blocks from content."""
    keep_pattern = r'<!-- KEEP:START -->(.*?)<!-- KEEP:END -->'
    keep_blocks = re.findall(keep_pattern, content, re.DOTALL)
    return keep_blocks

def apply_keep_blocks(new_content, keep_blocks):
    """Append preserved KEEP blocks to new content."""
    if not keep_blocks:
        return new_content
    
    preserved_section = "\n\n<!-- PRESERVED CONTENT FROM PREVIOUS VERSION -->\n"
    for i, block in enumerate(keep_blocks, 1):
        preserved_section += f"\n<!-- PRESERVED BLOCK {i} -->\n"
        preserved_section += block.strip()
        preserved_section += f"\n<!-- END PRESERVED BLOCK {i} -->\n"
    
    return new_content + preserved_section

def sync_file(source_path, target_path, force_update=False):
    """Sync a single file with KEEP block preservation."""
    target_path.parent.mkdir(parents=True, exist_ok=True)
    
    # If target exists and not forcing update, skip
    if target_path.exists() and not force_update:
        return "skipped"
    
    # Handle KEEP blocks for text files
    keep_blocks = []
    if target_path.exists() and target_path.suffix in ['.md', '.txt', '.html', '.qmd']:
        try:
            with open(target_path, 'r', encoding='utf-8') as f:
                old_content = f.read()
                keep_blocks = preserve_keep_blocks(old_content)
        except UnicodeDecodeError:
            pass  # Binary file, no KEEP blocks
    
    # Copy the file
    try:
        if keep_blocks:
            # Read new content and apply KEEP blocks
            with open(source_path, 'r', encoding='utf-8') as f:
                new_content = f.read()
            
            final_content = apply_keep_blocks(new_content, keep_blocks)
            
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(final_content)
        else:
            # Direct copy for binary files or files without KEEP blocks
            shutil.copy2(source_path, target_path)
        
        return "updated" if target_path.exists() else "created"
    
    except Exception as e:
        console.print(f"[red]❌ Error copying {source_path}: {e}[/red]")
        return "error"

def perform_sync(professor_dir, student_dir, changes, force_update_list=None):
    """Perform the actual directory synchronization."""
    professor_path = Path(professor_dir)
    student_path = Path(student_dir)
    
    force_update_list = force_update_list or []
    results = {'created': 0, 'updated': 0, 'skipped': 0, 'errors': 0, 'framework_forced': 0}
    
    all_files = changes['new_files'] + changes['updated_files']
    
    if not all_files:
        return results
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console
    ) as progress:
        
        task = progress.add_task("🔄 Synchronizing files...", total=len(all_files))
        
        for rel_path in all_files:
            source_file = professor_path / rel_path
            target_file = student_path / rel_path
            
            # Check if this is a framework file that needs force updating
            is_framework = is_framework_file(rel_path)
            force_update = str(rel_path) in force_update_list or is_framework
            
            result = sync_file(source_file, target_file, force_update)
            
            # Track framework force updates separately
            if is_framework and result in ['updated', 'created']:
                results['framework_forced'] = results.get('framework_forced', 0) + 1
            
            results[result] = results.get(result, 0) + 1
            progress.advance(task)
    
    return results

def show_sync_summary(student_name, changes, results):
    """Display comprehensive sync summary with exclusions."""
    
    # Create summary table
    table = Table(title=f"📋 Sync Summary for {student_name}")
    table.add_column("Category", style="cyan")
    table.add_column("Count", style="white")
    table.add_column("Description", style="dim")
    
    table.add_row("📄 New Files", str(len(changes['new_files'])), "Added to your directory")
    table.add_row("🔄 Updated Files", str(len(changes['updated_files'])), "Professor made changes")
    table.add_row("✅ Files Created", str(results['created']), "Successfully added")
    table.add_row("🔄 Files Updated", str(results['updated']), "Successfully updated")
    table.add_row("🔧 Framework Updated", str(results.get('framework_forced', 0)), "Framework files force-synced")
    table.add_row("⏭️ Files Skipped", str(results['skipped']), "Unchanged, protected your work")
    table.add_row("🚫 Files Excluded", str(len(changes['excluded_files'])), "Auto-generated/cache/dev files")
    table.add_row("🛡️ Your Files", str(len(changes['student_only_files'])), "Untouched, student-only")
    
    console.print(table)
    
    # Show file changes tree
    if changes['new_files'] or changes['updated_files'] or changes['excluded_files']:
        console.print("\n[bold blue]📁 Sync Details:[/bold blue]")
        tree = Tree("📂 Changes")
        
        if changes['new_files']:
            new_branch = tree.add("📄 New Files")
            for file in changes['new_files'][:8]:  # Limit display
                new_branch.add(f"[green]+ {file}[/green]")
            if len(changes['new_files']) > 8:
                new_branch.add(f"[dim]... and {len(changes['new_files']) - 8} more[/dim]")
        
        if changes['updated_files']:
            updated_branch = tree.add("🔄 Updated Files")
            for file in changes['updated_files'][:8]:  # Limit display
                updated_branch.add(f"[yellow]~ {file}[/yellow]")
            if len(changes['updated_files']) > 8:
                updated_branch.add(f"[dim]... and {len(changes['updated_files']) - 8} more[/dim]")
        
        if changes['excluded_files']:
            excluded_branch = tree.add("🚫 Smart Exclusions")
            for file, reason in changes['excluded_files'][:5]:  # Show fewer exclusions
                excluded_branch.add(f"[dim]- {file} ({reason})[/dim]")
            if len(changes['excluded_files']) > 5:
                excluded_branch.add(f"[dim]... and {len(changes['excluded_files']) - 5} more[/dim]")
        
        console.print(tree)

def main(professor_dir=None, student_dir=None):
    """Main sync process."""
    console.print(Panel(
        "[bold blue]📚 Student Content Sync Tool[/bold blue]\n\n"
        "Class content synchronization: <professor_dir>/ → students/<username>/\n"
        "• Copies new class content from instructor\n"
        "• Updates class content you haven't modified\n"
        "• [bold]Only syncs class_notes content[/bold] (framework shared at root)\n"
        "• Protects your personal work (non-destructive)\n"
        "• Preserves KEEP blocks during updates\n"
        "• Smart exclusions for generated content",
        title="🎓 Content Sync",
        border_style="blue"
    ))
    
    # Use provided parameters or detect/load from config
    if professor_dir is None:
        # Try to get professor directory from class_template/course.yml
        try:
            with open("class_template/course.yml", 'r') as f:
                course_config = yaml.safe_load(f)
                professor_dir = course_config.get('structure', {}).get('professor_directory', 'professor')
        except (FileNotFoundError, yaml.YAMLError):
            professor_dir = 'professor'  # Default fallback
    
    if student_dir is None:
        # Detect student directory
        student_name = detect_student_directory()
        student_dir = f"students/{student_name}"
    else:
        # Extract student name from directory path
        student_name = Path(student_dir).name
    if not student_name:
        console.print("[red]❌ No student directory specified[/red]")
        sys.exit(1)
    
    console.print(f"[blue]📍 Syncing:[/blue] {professor_dir}/ → {student_dir}/")
    
    # Check if professor directory exists
    if not Path(professor_dir).exists():
        console.print(f"[red]❌ Professor directory '{professor_dir}' not found[/red]")
        sys.exit(1)
    
    # Scan for changes
    console.print("\n[yellow]🔍 Scanning for changes (with smart exclusions)...[/yellow]")
    changes = scan_directory_changes(professor_dir, student_dir)
    
    total_changes = len(changes['new_files']) + len(changes['updated_files'])
    
    # Count framework files that will be force-updated
    all_files = changes['new_files'] + changes['updated_files']
    framework_files = [f for f in all_files if is_framework_file(f)]
    
    if framework_files:
        console.print(f"[blue]🔧 Framework files to force-update: {len(framework_files)}[/blue] (scripts, themes, components)")
    
    if total_changes == 0:
        console.print(Panel(
            "[green]✅ Already synchronized![/green]\n\n"
            f"Your directory is up to date with the professor's content.\n"
            f"🚫 Excluded {len(changes['excluded_files'])} auto-generated files",
            title="🎉 All Current",
            border_style="green"
        ))
        return
    
    # Show what will be synced
    console.print(f"\n[yellow]📊 Found {total_changes} files to sync, excluded {len(changes['excluded_files'])} auto-generated files[/yellow]")
    
    # Confirm with user
    if not Confirm.ask("🤔 Proceed with synchronization?"):
        console.print("[yellow]⏸️ Sync cancelled by user[/yellow]")
        return
    
    # Perform sync
    results = perform_sync(professor_dir, student_dir, changes)
    
    # Show results
    console.print()
    show_sync_summary(student_name, changes, results)
    
    console.print(Panel(
        "[green]✅ Synchronization completed![/green]\n\n"
        "[white]What happened:[/white]\n"
        "• 📂 Copied new/updated files from professor\n"
        "• 🛡️ Protected your existing work\n"
        "• 🔄 Preserved KEEP blocks where applicable\n"
        "• 🚫 Smartly excluded auto-generated content\n\n"
        "[yellow]Next steps:[/yellow]\n"
        "• 👀 Review the synchronized files\n"
        "• 📚 Check for new assignments or materials\n"
        "• 🚀 Continue with your learning!",
        title=f"🎉 {student_name} - Sync Complete",
        border_style="green"
    ))

if __name__ == "__main__":
    console.print("\n[bold blue]🎓 GitHub Class Template - Student Content Sync[/bold blue]")
    console.print("[dim]Syncs class content from professor to student directories (framework shared at root)[/dim]")
    
    try:
        # Check for command line arguments
        professor_dir = sys.argv[1] if len(sys.argv) > 1 else None
        student_dir = sys.argv[2] if len(sys.argv) > 2 else None
        
        main(professor_dir, student_dir)
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  Sync cancelled by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]❌ Sync failed: {e}[/red]")
        sys.exit(1) 