#!/usr/bin/env python3
"""
GitHub Class Template Framework - Unified Management Script
Automates the complete workflow for professors and students

Usage Examples:
  ./manage.py --build          # Full build pipeline
  ./manage.py --dev            # Start development server  
  ./manage.py --sync           # Sync updates (students only)
  ./manage.py --deploy         # Production deployment
  ./manage.py --publish        # Complete build + deploy
  ./manage.py --build --dev    # Build and start dev server
  ./manage.py --build --deploy # Build and deploy (same as --publish)
  ./manage.py --sync --build   # Sync and build (students)
  ./manage.py --status         # Show current state
"""

import argparse
import os
import sys
import subprocess
import json
import time
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Confirm, Prompt
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.table import Table
    from rich.text import Text
    from rich.syntax import Syntax
    from rich.layout import Layout
    from rich import print as rprint
except ImportError:
    print("❌ Missing required 'rich' library. Install with: pip install rich")
    sys.exit(1)

console = Console()

class FrameworkManager:
    def __init__(self):
        self.console = console
        self.env_manager = EnvironmentManager(self.console)
        self.subprocess_runner = SubprocessRunner(self.console)
        self.message_orchestrator = MessageOrchestrator(self.console)
        self.ux = UserExperience(self.console)
        self.operation_sequencer = OperationSequencer(self.console)
        self.command_router = CommandRouter()
        
        # Set up dependencies for operation sequencer
        self.operation_sequencer.set_dependencies(
            self.subprocess_runner,
            self.message_orchestrator,
            self.ux
        )
        
        # Environment properties (populated by detect_environment)
        self.current_dir = Path.cwd()
        self.role = None  # 'professor' or 'student'
        self.base_dir = None
        self.framework_dir = None
        self.is_valid_setup = False
        
        # Backward compatibility properties (delegate to message orchestrator)
        self.verbose = False
    
    @property
    def messages(self):
        """Backward compatibility: access to message orchestrator messages"""
        return self.message_orchestrator.messages
    
    @property
    def operation_stats(self):
        """Backward compatibility: access to operation statistics"""
        return self.message_orchestrator.operation_stats
    
    @property
    def current_operation(self):
        """Backward compatibility: access to current operation"""
        return self.message_orchestrator.current_operation
    
    @property
    def operation_start_time(self):
        """Backward compatibility: access to operation start time"""
        return self.message_orchestrator.operation_start_time
        
    def detect_environment(self) -> bool:
        """Detect if we're in a valid framework directory and determine role"""
        
        success, context = self.env_manager.detect_environment()
        
        if success:
            # Update instance variables to maintain backward compatibility
            self.current_dir = context.current_dir
            self.role = context.role
            self.base_dir = context.base_dir
            self.framework_dir = context.framework_dir
            self.is_valid_setup = context.is_valid_setup
            
            # Set environment context for operation sequencer
            self.operation_sequencer.set_environment_context(
                self.current_dir,
                self.framework_dir,
                self.role
            )
            
        return success
    
    def add_message(self, message_type: str, title: str, details: str = None, context: str = None, duration: float = None):
        """Add a message to be shown in the final summary"""
        return self.message_orchestrator.add_message(message_type, title, details, context, duration)
    
    def start_operation(self, operation_name: str):
        """Start tracking an operation"""
        self.message_orchestrator.set_verbose(self.verbose)
        return self.message_orchestrator.start_operation(operation_name)
    
    def end_operation(self, success: bool, message: str = None):
        """End tracking an operation"""
        return self.message_orchestrator.end_operation(success, message)
    
    def validate_environment(self) -> bool:
        """Validate that all required files and directories exist"""
        
        # Create context from current instance variables
        context = EnvironmentContext()
        context.current_dir = self.current_dir
        context.role = self.role
        context.base_dir = self.base_dir
        context.framework_dir = self.framework_dir
        context.is_valid_setup = self.is_valid_setup
        
        is_valid, missing_files = self.env_manager.validate_environment(context)
        
        if not is_valid:
            file_list = "\n".join([f"   {file}" for file in missing_files])
            self.add_message('errors', 'Missing Framework Files', file_list, 'Environment Validation')
            return False
            
        return True
    
    def show_status(self):
        """Show current framework status"""
        
        # Create status table
        table = Table(title="Framework Status", show_header=True, header_style="bold magenta")
        table.add_column("Property", style="cyan", width=20)
        table.add_column("Value", style="green")
        
        table.add_row("Role", self.role.title())
        table.add_row("Current Directory", str(self.current_dir))
        table.add_row("Framework Directory", str(self.framework_dir))
        table.add_row("Base Repository", str(self.base_dir))
        
        # Check if Hugo config exists - NEW: Hugo config is now in root-level hugo_generated/
        repo_root = self.current_dir.parent if self.current_dir.name in ['professor', 'students'] else self.current_dir
        while repo_root.name != repo_root.parent.name and not (repo_root / "dna.yml").exists():
            repo_root = repo_root.parent
        hugo_config = repo_root / "hugo_generated" / "hugo.toml"
        table.add_row("Hugo Config", "✅ Exists" if hugo_config.exists() else "❌ Missing")
        
        # Check if development server is running
        try:
            result = subprocess.run(["pgrep", "-f", "hugo.*server"], 
                                  capture_output=True, text=True)
            server_running = "✅ Running" if result.returncode == 0 else "❌ Not running"
        except:
            server_running = "❓ Unknown"
        table.add_row("Hugo Server", server_running)
        
        self.console.print(table)
        
        # Show recent content changes
        self.show_recent_changes()
    
    def show_recent_changes(self):
        """Show recently modified content files"""
        
        content_dirs = ["class_notes", "framework_tutorials", "framework_documentation"]
        recent_files = []
        
        for content_dir in content_dirs:
            dir_path = self.current_dir / content_dir
            if dir_path.exists():
                for file_path in dir_path.rglob("*.md"):
                    if file_path.stat().st_mtime > time.time() - 86400:  # Last 24 hours
                        recent_files.append((file_path, file_path.stat().st_mtime))
        
        if recent_files:
            recent_files.sort(key=lambda x: x[1], reverse=True)
            
            table = Table(title="Recent Changes (Last 24h)", show_header=True)
            table.add_column("File", style="cyan")
            table.add_column("Modified", style="yellow")
            
            for file_path, mtime in recent_files[:10]:  # Show last 10
                rel_path = file_path.relative_to(self.current_dir)
                mod_time = time.strftime("%H:%M:%S", time.localtime(mtime))
                table.add_row(str(rel_path), mod_time)
                
            self.console.print(table)
    
    def run_command(self, command: List[str], description: str, 
                   capture_output: bool = False, show_progress: bool = None) -> subprocess.CompletedProcess:
        """Run a command with optional progress indication"""
        
        # Create error callback to maintain backward compatibility with message system
        def error_callback(desc: str, error_text: str):
            self.add_message('errors', desc, error_text)
        
        return self.subprocess_runner.run_command(
            command=command,
            description=description,
            working_directory=self.current_dir,
            capture_output=capture_output,
            show_progress=show_progress,
            verbose=self.verbose,
            error_callback=error_callback
        )
    
    def validate_and_generate(self, force: bool = False) -> bool:
        """Run validation and generation pipeline"""
        return self.operation_sequencer.validate_and_generate(force)
    
    def start_development_server(self, port: int = None):
        """Start Hugo development server"""
        return self.operation_sequencer.start_development_server(port)
    
    def sync_student_updates(self) -> bool:
        """Sync framework updates for students"""
        return self.operation_sequencer.sync_student_updates()
    
    def build_production(self) -> bool:
        """Build production-ready static site"""
        return self.operation_sequencer.build_production()
    
    def full_build_pipeline(self, force: bool = False) -> bool:
        """Run the complete build pipeline"""
        return self.operation_sequencer.full_build_pipeline(force)
    
    def clean_generated_files(self):
        """Clean generated files"""
        return self.operation_sequencer.clean_generated_files()
    
    def show_final_summary(self):
        """Show final summary of all operations with warnings and errors"""
        self.message_orchestrator.set_verbose(self.verbose)
        return self.message_orchestrator.show_final_summary()

# Modular components
from manage_modules.cli_definitions import create_parser
from manage_modules.environment_manager import EnvironmentManager, EnvironmentContext
from manage_modules.subprocess_runner import SubprocessRunner
from manage_modules.message_orchestrator import MessageOrchestrator
from manage_modules.user_experience import UserExperience
from manage_modules.operation_sequencer import OperationSequencer
from manage_modules.command_router import CommandRouter

def main():
    """Main entry point"""
    
    parser = create_parser()
    args = parser.parse_args()
    
    # Show help if no arguments
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    manager = FrameworkManager()
    manager.verbose = args.verbose
    manager.message_orchestrator.set_verbose(args.verbose)
    
    # Environment detection and validation
    if not manager.detect_environment():
        manager.ux.show_environment_guidance()
        sys.exit(1)
    
    if not manager.validate_environment():
        console.print("❌ Framework environment validation failed")
        sys.exit(1)
    
    # Show welcome message
    framework_info = {
        'role': manager.role,
        'current_dir': manager.current_dir,
        'verbose': manager.verbose
    }
    manager.ux.show_welcome_panel(framework_info)
    
    # Execute commands
    try:
        # Route and execute commands
        flow_key = manager.command_router.route_commands(args)
        success = manager.command_router.execute_command_flow(flow_key, args, manager)
        
        if not success and flow_key != 'help':
            console.print(f"❌ Command execution failed")
            
    except KeyboardInterrupt:
        console.print("\n🛑 Operation cancelled by user")
        manager.add_message('warnings', 'Operation Cancelled', 'User interrupted the operation', 'User Action')
    except Exception as e:
        console.print(f"❌ Unexpected error: {e}")
        manager.add_message('errors', 'Unexpected Error', str(e), 'System')
        
    finally:
        # Always show summary at the end (except for dev server and status)
        flow_key = manager.command_router.route_commands(args)
        if manager.command_router.should_show_summary(flow_key):
            manager.show_final_summary()

if __name__ == "__main__":
    main() 