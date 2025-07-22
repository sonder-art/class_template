#!/usr/bin/env python3
"""
Configuration Utilities for Quarto Educational Infrastructure

This module provides utilities for reading configuration from _quarto.yml
and resolving dynamic paths based on user settings, eliminating hardcoded paths.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import sys
from rich.console import Console

console = Console()

def find_quarto_config(start_path: Path) -> Optional[Path]:
    """Find the _quarto.yml configuration file by searching up the directory tree."""
    current_path = start_path.resolve()
    
    while current_path != current_path.parent:
        quarto_file = current_path / '_quarto.yml'
        if quarto_file.exists():
            return quarto_file
        current_path = current_path.parent
    
    return None

def load_quarto_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """Load the _quarto.yml configuration file."""
    if config_path is None:
        # Search for config file starting from current directory
        config_path = find_quarto_config(Path.cwd())
        
        if config_path is None:
            # Try common locations
            for common_path in [Path('.'), Path('..'), Path('../..'), Path('uumami')]:
                potential_config = common_path / '_quarto.yml'
                if potential_config.exists():
                    config_path = potential_config
                    break
    
    if config_path is None or not config_path.exists():
        raise FileNotFoundError(
            "Could not find _quarto.yml configuration file. "
            "Make sure you're running from the project root or provide the path explicitly."
        )
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in {config_path}: {e}")

def get_user_name(config_path: Optional[Path] = None) -> str:
    """Get the user_name from _quarto.yml configuration."""
    config = load_quarto_config(config_path)
    
    user_name = config.get('metadata', {}).get('user_name')
    
    if not user_name:
        console.print("[yellow]⚠️ Warning:[/yellow] No 'user_name' found in _quarto.yml metadata.")
        console.print("Please add 'user_name: your_github_username' to the metadata section.")
        return 'uumami'  # Fallback
    
    return user_name

def get_project_root(config_path: Optional[Path] = None) -> Path:
    """Get the project root directory."""
    if config_path is None:
        config_path = find_quarto_config(Path.cwd())
    
    if config_path is None:
        raise FileNotFoundError("Could not find _quarto.yml to determine project root")
    
    # The user directory contains _quarto.yml, project root is its parent
    return config_path.parent.parent

def resolve_user_path(relative_path: str, config_path: Optional[Path] = None) -> Path:
    """Resolve a path relative to the user directory (e.g., 'notas' -> 'uumami/notas')."""
    user_name = get_user_name(config_path)
    project_root = get_project_root(config_path)
    
    return project_root / user_name / relative_path

def resolve_content_paths(config_path: Optional[Path] = None) -> Dict[str, Path]:
    """Resolve all content paths based on configuration."""
    if config_path is None:
        config_path = find_quarto_config(Path.cwd())
    
    if config_path is None:
        raise FileNotFoundError("Could not find _quarto.yml to determine project structure")
    
    user_name = get_user_name(config_path)
    
    # The user directory is the one containing _quarto.yml
    user_root = config_path.parent
    # The project root is the parent of the user directory
    project_root = user_root.parent
    
    paths = {
        'project_root': project_root,
        'user_root': user_root,
        'user_name': user_name,
        'config_file': config_path
    }
    
    # Content directories
    content_dirs = ['notas', 'quarto_development', 'quarto_code', 'styles']
    for dir_name in content_dirs:
        potential_path = user_root / dir_name
        if potential_path.exists():
            paths[dir_name] = potential_path
    
    return paths

def validate_project_structure(config_path: Optional[Path] = None) -> bool:
    """Validate that the project has the expected structure."""
    try:
        paths = resolve_content_paths(config_path)
        
        required_paths = ['user_root', 'config_file']
        for path_name in required_paths:
            if path_name not in paths or not paths[path_name].exists():
                console.print(f"[red]❌ Missing required path:[/red] {path_name}")
                return False
        
        return True
    except Exception as e:
        console.print(f"[red]❌ Project structure validation failed:[/red] {e}")
        return False

def get_relative_css_path(from_path: Path, config_path: Optional[Path] = None) -> str:
    """Calculate relative path to main CSS file from any location."""
    try:
        paths = resolve_content_paths(config_path)
        css_file = paths.get('quarto_code', paths['user_root'] / 'quarto_code') / 'styles' / 'main.css'
        
        # Calculate relative path
        relative_path = Path(css_file).relative_to(from_path.parent)
        return str(relative_path)
    except Exception:
        # Fallback to a reasonable default
        return "../quarto_code/styles/main.css"

if __name__ == '__main__':
    """Test the configuration utilities."""
    try:
        console.print("[bold blue]🔧 Testing Configuration Utilities[/bold blue]\n")
        
        # Test loading config
        config = load_quarto_config()
        user_name = get_user_name()
        paths = resolve_content_paths()
        
        console.print(f"[green]✅ User Name:[/green] {user_name}")
        console.print(f"[green]✅ Project Root:[/green] {paths['project_root']}")
        console.print(f"[green]✅ User Root:[/green] {paths['user_root']}")
        
        if 'notas' in paths:
            console.print(f"[green]✅ Content Path:[/green] {paths['notas']}")
        
        # Test validation
        is_valid = validate_project_structure()
        console.print(f"[green]✅ Structure Valid:[/green] {is_valid}")
        
    except Exception as e:
        console.print(f"[red]❌ Error:[/red] {e}")
        sys.exit(1) 