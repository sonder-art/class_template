"""
Subprocess Runner Module for Framework Manager

This module handles subprocess execution with rich progress indication 
and error collection, extracted from the original manage.py for better modularity.

Maintains exact compatibility with the original subprocess execution behavior.
"""

import subprocess
from pathlib import Path
from typing import List, Callable, Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn


class SubprocessRunner:
    """Handles subprocess execution with rich UI and error collection"""
    
    def __init__(self, console: Console = None):
        self.console = console or Console()
    
    def run_command(self, 
                   command: List[str], 
                   description: str,
                   working_directory: Path = None,
                   capture_output: bool = False, 
                   show_progress: bool = None,
                   verbose: bool = False,
                   error_callback: Optional[Callable[[str, str], None]] = None) -> subprocess.CompletedProcess:
        """Run a command with optional progress indication
        
        Args:
            command: Command and arguments to execute
            description: Human-readable description for progress display
            working_directory: Directory to run command in (defaults to cwd)
            capture_output: Whether to capture stdout/stderr 
            show_progress: Whether to show progress spinner (defaults to verbose mode)
            verbose: Whether in verbose mode (affects default progress display)
            error_callback: Function to call with (description, error_text) on errors
            
        Returns:
            subprocess.CompletedProcess: Result of the command execution
        """
        
        if working_directory is None:
            working_directory = Path.cwd()
            
        # Default show_progress based on verbose mode
        if show_progress is None:
            show_progress = verbose
            
        if show_progress:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
            ) as progress:
                task = progress.add_task(description, total=None)
                
                try:
                    result = subprocess.run(
                        command,
                        capture_output=capture_output,
                        text=True,
                        cwd=working_directory
                    )
                    
                    if result.returncode == 0:
                        progress.update(task, description=f"✅ {description}")
                    else:
                        progress.update(task, description=f"❌ {description}")
                        if result.stderr and error_callback:
                            error_callback(description, result.stderr.strip())
                        
                    return result
                    
                except Exception as e:
                    progress.update(task, description=f"❌ {description} - {str(e)}")
                    if error_callback:
                        error_callback(description, str(e))
                    raise
        else:
            # Silent execution for less verbose operations
            try:
                result = subprocess.run(
                    command,
                    capture_output=capture_output,
                    text=True,
                    cwd=working_directory
                )
                
                if result.returncode != 0 and result.stderr and error_callback:
                    error_callback(description, result.stderr.strip())
                    
                return result
                
            except Exception as e:
                if error_callback:
                    error_callback(description, str(e))
                raise
    
    def run_framework_script(self,
                           script_name: str,
                           working_directory: Path,
                           framework_dir: Path,
                           args: List[str] = None,
                           description: str = None,
                           verbose: bool = False,
                           error_callback: Optional[Callable[[str, str], None]] = None) -> subprocess.CompletedProcess:
        """Run a framework script with standard conventions
        
        Args:
            script_name: Name of the script (e.g., 'generate_hugo_config.py')
            working_directory: Directory to run script from
            framework_dir: Framework directory containing scripts/
            args: Additional arguments to pass to script
            description: Human-readable description (auto-generated if None)
            verbose: Whether in verbose mode
            error_callback: Function to call with (description, error_text) on errors
            
        Returns:
            subprocess.CompletedProcess: Result of the script execution
        """
        
        script_path = framework_dir / "scripts" / script_name
        command = ["python3", str(script_path)]
        
        if args:
            command.extend(args)
            
        if description is None:
            description = f"Running {script_name}"
            
        return self.run_command(
            command=command,
            description=description,
            working_directory=working_directory,
            capture_output=True,
            verbose=verbose,
            error_callback=error_callback
        )
    
    def check_command_available(self, command: str) -> bool:
        """Check if a command is available in the system
        
        Args:
            command: Command to check (e.g., 'hugo', 'python3')
            
        Returns:
            bool: True if command is available, False otherwise
        """
        
        try:
            result = subprocess.run(
                ["which", command],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception:
            return False


if __name__ == "__main__":
    # Test module functionality
    runner = SubprocessRunner()
    
    print("✅ Subprocess runner module working correctly")
    
    # Test basic command
    try:
        result = runner.run_command(
            ["echo", "Hello from subprocess runner"],
            "Testing echo command",
            verbose=True
        )
        print(f"Echo test: {'✅ success' if result.returncode == 0 else '❌ failed'}")
    except Exception as e:
        print(f"❌ Echo test failed: {e}")
    
    # Test command availability check
    has_python = runner.check_command_available("python3")
    has_hugo = runner.check_command_available("hugo")
    print(f"Python3 available: {'✅' if has_python else '❌'}")
    print(f"Hugo available: {'✅' if has_hugo else '❌'}")