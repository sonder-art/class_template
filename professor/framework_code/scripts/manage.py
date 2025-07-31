#!/usr/bin/env python3
"""
Framework Management Script for GitHub Class Template Framework

Central management tool for the entire framework lifecycle including
validation, generation, building, and deployment.

This script provides a unified interface for all framework operations
and is the primary entry point for automation tasks.
"""

import os
import sys
import shutil
import time
import argparse
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List
import yaml

from rich.console import Console
from rich.progress import Progress, TaskID
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Confirm
from rich import box

# Initialize rich console
console = Console()

# Get script directory for relative imports
SCRIPT_DIR = Path(__file__).parent
ROOT_DIR = SCRIPT_DIR.parent.parent  # Two levels up from scripts/

# Add the scripts directory to Python path for imports
sys.path.insert(0, str(SCRIPT_DIR))

# Framework role detection
if "student" in str(Path.cwd()):
    ROLE = "Student" 
    DEFAULT_PORT = 1314
else:
    ROLE = "Professor"
    DEFAULT_PORT = 1313

class FrameworkManager:
    """Main framework management class"""
    
    def __init__(self):
        self.current_dir = Path.cwd()
        self.framework_dir = self.current_dir / "framework_code"
        self.scripts_dir = self.framework_dir / "scripts"
        self.console = console
        
        # Output management system
        self.messages = {'success': [], 'warnings': [], 'errors': [], 'info': []}
        self.operation_stats = {'total_operations': 0, 'successful_operations': 0, 'failed_operations': 0, 'total_duration': 0.0}
        self.current_operation = None
        self.operation_start_time = None
        self.verbose = False  # Will be set by argument parser
        
        # Track slugs for discussions
        self.existing_slugs = set()
        self.files_with_generated_slugs = []
    
    def add_message(self, message_type: str, title: str, details: str = None, error_output: str = None, duration: Optional[float] = None):
        """Add a message to the collection for final summary"""
        self.messages[message_type].append({
            'title': title,
            'details': details,
            'error_output': error_output,
            'duration': duration
        })
    
    def start_operation(self, operation_name: str):
        """Start timing an operation"""
        self.current_operation = operation_name
        self.operation_start_time = time.time()
        self.operation_stats['total_operations'] += 1
        
        if self.verbose:
            self.console.print(f"\n🔄 [bold]{operation_name}[/bold]")
        else:
            self.console.print(f"🔄 {operation_name}...")
    
    def end_operation(self, success: bool, message: str = None):
        """End timing an operation and log the result"""
        if self.operation_start_time:
            duration = time.time() - self.operation_start_time
            duration_str = f"({duration:.1f}s)"
            self.operation_stats['total_duration'] += duration
        else:
            duration = None
            duration_str = ""
        
        if success:
            self.operation_stats['successful_operations'] += 1
            if self.verbose:
                self.console.print(f"  ✅ [green]{message or self.current_operation + ' completed'}[/green] {duration_str}")
            self.add_message('success', self.current_operation, message, duration=duration)
        else:
            self.operation_stats['failed_operations'] += 1
            if self.verbose:
                self.console.print(f"  ❌ [red]{message or self.current_operation + ' failed'}[/red] {duration_str}")
            self.add_message('errors', self.current_operation, message, duration=duration)
        
        # Reset operation tracking
        self.current_operation = None
        self.operation_start_time = None
    
    def show_status(self):
        """Show current framework status"""
        
        self.console.print(Panel.fit(
            f"🚀 [bold]Framework Manager[/bold]\n"
            f"Role: [cyan]{ROLE}[/cyan]\n"
            f"Directory: [cyan]{self.current_dir}[/cyan]",
            title="Framework Status"
        ))
        
        # Check key directories and files
        status_items = [
            ("Framework Code", self.framework_dir.exists()),
            ("Scripts Directory", self.scripts_dir.exists()),
            ("Config File", (self.current_dir / "config.yml").exists()),
            ("Course File", (self.current_dir / "course.yml").exists()),
            ("Generated Hugo", (self.current_dir / "hugo.toml").exists()),
        ]
        
        table = Table(title="Framework Components", show_header=True, header_style="bold cyan")
        table.add_column("Component", style="white")
        table.add_column("Status", justify="center")
        
        for item, exists in status_items:
            status = "✅" if exists else "❌"
            table.add_row(item, status)
        
        self.console.print(table)
        
        # Additional status information
        if (self.framework_dir / "hugo_generated").exists():
            self.console.print("\n📁 Generated site available")
        
        if ROLE == "Student":
            self.console.print(f"\n🎓 Running in [bold cyan]Student[/bold cyan] mode")
            self.console.print("Available commands: --sync, --dev, --build")
        else:
            self.console.print(f"\n👨‍🏫 Running in [bold cyan]Professor[/bold cyan] mode") 
            self.console.print("Available commands: --build, --dev, --deploy, --sync")

    def run_command(self, cmd: List[str], cwd: Path = None, capture_output: bool = False) -> tuple:
        """Run a shell command with error handling"""
        
        if self.verbose:
            self.console.print(f"Running: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd or self.current_dir,
                capture_output=capture_output,
                text=True,
                check=True
            )
            return True, result.stdout if capture_output else ""
        except subprocess.CalledProcessError as e:
            error_msg = f"Command failed: {' '.join(cmd)}"
            if capture_output and e.stderr:
                error_msg += f"\nError: {e.stderr}"
            
            if self.verbose:
                self.console.print(f"[red]❌ {error_msg}[/red]")
            
            return False, error_msg
        except FileNotFoundError:
            error_msg = f"Command not found: {cmd[0]}"
            if self.verbose:
                self.console.print(f"[red]❌ {error_msg}[/red]")
            return False, error_msg

    def validate_and_generate(self, force: bool = False):
        """Run validation and generation scripts"""
        
        self.start_operation("Validation & Generation")
        
        scripts = [
            ("content_metadata.py", "Content validation"),
            ("generate_hugo_config.py", "Hugo configuration generation")
        ]
        
        overall_success = True
        
        for script, description in scripts:
            script_path = self.scripts_dir / script
            
            if not script_path.exists():
                self.console.print(f"⚠️ Script not found: {script}")
                continue
            
            if self.verbose:
                self.console.print(f"  Running {description}...")
            
            success, output = self.run_command(
                ["python3", str(script_path)], 
                capture_output=not self.verbose
            )
            
            if not success:
                overall_success = False
                self.add_message('errors', f'{description} Failed', output)
            
        if overall_success:
            self.end_operation(True, "Framework files validated and generated")
        else:
            self.end_operation(False, "One or more validation steps failed")
        
        return overall_success

    def start_development_server(self, port: int = None):
        """Start Hugo development server"""
        
        if port is None:
            port = DEFAULT_PORT
        
        self.start_operation("Development Server")
        
        # Check if Hugo is installed
        hugo_check, _ = self.run_command(["hugo", "version"], capture_output=True)
        if not hugo_check:
            self.end_operation(False, "Hugo not found - please install Hugo")
            return False
        
        # Ensure hugo.toml exists
        hugo_config = self.current_dir / "hugo.toml"
        if not hugo_config.exists():
            self.console.print("🔧 Generating Hugo configuration...")
            if not self.validate_and_generate():
                self.end_operation(False, "Failed to generate Hugo configuration")
                return False
        
        self.console.print(f"\n🌐 [bold]Starting development server on http://localhost:{port}[/bold]")
        self.console.print("Press [bold red]Ctrl+C[/bold red] to stop the server")
        
        # Start Hugo server
        try:
            subprocess.run([
                "hugo", "server",
                "--port", str(port),
                "--bind", "0.0.0.0",
                "--buildDrafts",
                "--buildFuture",
                "--disableFastRender"
            ], cwd=self.current_dir)
            
        except KeyboardInterrupt:
            self.console.print("\n🛑 Development server stopped")
            
        # Don't call end_operation for dev server as it's a continuous process
        return True

    def sync_student_updates(self):
        """Sync framework updates (students only)"""
        
        if ROLE != "Student":
            self.console.print("❌ Sync is only available for students")
            return False
        
        self.start_operation("Framework Sync")
        
        sync_script = self.scripts_dir / "sync_student.py"
        if not sync_script.exists():
            self.end_operation(False, "Sync script not found")
            return False
        
        # Run sync script
        success, output = self.run_command(
            ["python3", str(sync_script)],
            capture_output=not self.verbose
        )
        
        if success:
            self.end_operation(True, "Framework updates synced")
        else:
            self.end_operation(False, "Sync failed")
            self.add_message('errors', 'Sync Failed', output)
            
        return success

    def build_production(self):
        """Build for production deployment"""
        
        self.start_operation("Production Build")
        
        # First validate and generate
        if not self.validate_and_generate():
            self.end_operation(False, "Pre-build validation failed")
            return False
        
        # Check if Hugo is installed
        hugo_check, _ = self.run_command(["hugo", "version"], capture_output=True)
        if not hugo_check:
            self.end_operation(False, "Hugo not found - please install Hugo")
            return False
        
        # Build static site
        success, output = self.run_command(
            ["hugo", "--minify"],
            capture_output=not self.verbose
        )
        
        if success:
            output_dir = self.framework_dir / "hugo_generated"
            self.end_operation(True, f"Static site ready in {output_dir}")
            self.add_message('info', 'Production Build Complete', 
                           f'Site built in: {output_dir}\nUpload the contents of this directory to your hosting service')
        else:
            self.end_operation(False, "Hugo build failed")
            self.add_message('errors', 'Hugo Build Failed', output)
            
        return success

    def full_build_pipeline(self, force: bool = False):
        """Run complete build pipeline"""
        
        self.start_operation("Full Build Pipeline")
        
        if not force:
            self.console.print("This will run: Validation → Generation → Hugo Build")
            if not Confirm.ask("Continue with full build?"):
                self.end_operation(False, "Pipeline cancelled by user")
                return False
        
        # Build production (which includes validation)
        if not self.build_production():
            self.end_operation(False, "Pipeline failed during build")
            return False
                
        self.end_operation(True, "Complete build pipeline finished")
        return True
    
    def clean_generated_files(self):
        """Clean generated files"""
        
        self.console.print("\n🧹 [bold]Cleaning Generated Files[/bold]")
        
        files_to_clean = [
            self.current_dir / "hugo.toml",
            self.framework_dir / "hugo_generated"
        ]
        
        existing_files = [f for f in files_to_clean if f.exists()]
        
        if not existing_files:
            self.console.print("✅ No generated files to clean")
            return
            
        self.console.print("Files to be removed:")
        for file in existing_files:
            self.console.print(f"• {file}")
            
        if Confirm.ask("Remove these files?"):
            for file in existing_files:
                if file.is_file():
                    file.unlink()
                elif file.is_dir():
                    shutil.rmtree(file)
                self.console.print(f"🗑️ Removed: {file}")
    
    def discussions_status(self):
        """Show discussions configuration and content status"""
        self.start_operation("Discussions Status")
        
        # Check if discussions are configured
        config_file = self.current_dir / "config.yml"
        if not config_file.exists():
            self.console.print("❌ No config.yml found")
            self.end_operation(False, "Configuration file missing")
            return
        
        # Load and display configuration
        import yaml
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            discussions_config = config.get('discussions', {})
            
            # Create status table
            from rich.table import Table
            table = Table(title="Discussions Configuration", show_header=True)
            table.add_column("Setting", style="cyan")
            table.add_column("Value", style="white")
            table.add_column("Status", style="white")
            
            enabled = discussions_config.get('enabled', False)
            table.add_row("Enabled", str(enabled), "✅" if enabled else "❌")
            table.add_row("Provider", discussions_config.get('provider', 'none'), "ℹ️")
            table.add_row("Repository", discussions_config.get('repository', 'none'), "ℹ️")
            table.add_row("Category", discussions_config.get('category', 'none'), "ℹ️")
            
            auto_types = discussions_config.get('auto_enable_for_types', [])
            table.add_row("Auto-enabled Types", str(len(auto_types)), "ℹ️")
            
            self.console.print(table)
            
            if enabled:
                # Run slug audit
                try:
                    from discussion_slugs import SlugManager
                    slug_manager = SlugManager(self.current_dir)
                    self.console.print("\n")
                    slug_manager.audit_slugs()
                except ImportError:
                    self.console.print("\n⚠️ Discussion slug manager not available")
            
            self.end_operation(True, "Configuration displayed")
            
        except Exception as e:
            self.console.print(f"❌ Error reading configuration: {e}")
            self.end_operation(False, "Failed to read configuration")
    
    def generate_missing_slugs(self, force: bool = False) -> bool:
        """Generate stable slugs for content missing them"""
        self.start_operation("Slug Generation")
        
        try:
            from discussion_slugs import SlugManager
            
            slug_manager = SlugManager(self.current_dir)
            success = slug_manager.generate_missing_slugs(force=force)
            
            if success:
                self.end_operation(True, "Slugs generated successfully")
            else:
                self.end_operation(False, "Slug generation failed")
            
            return success
            
        except ImportError:
            self.console.print("❌ Discussion slug manager not available")
            self.end_operation(False, "Missing dependency")
            return False
        except Exception as e:
            self.console.print(f"❌ Error: {e}")
            self.end_operation(False, str(e))
            return False
    
    def discussions_audit(self):
        """Audit existing content for discussion system readiness"""
        self.start_operation("Discussions Audit")
        
        try:
            from discussion_slugs import SlugManager
            
            slug_manager = SlugManager(self.current_dir)
            slug_manager.audit_slugs()
            
            self.end_operation(True, "Audit completed")
            
        except ImportError:
            self.console.print("❌ Discussion slug manager not available")
            self.end_operation(False, "Missing dependency")
        except Exception as e:
            self.console.print(f"❌ Error: {e}")
            self.end_operation(False, str(e))
    
    def show_final_summary(self):
        """Show final summary of all operations with warnings and errors"""
        
        if not any(self.messages.values()):
            return
            
        self.console.print("\n" + "="*60)
        self.console.print("📊 [bold]Operation Summary[/bold]")
        self.console.print("="*60)
        
        # Create summary table
        table = Table(title="Operation Summary", show_header=True, header_style="bold cyan")
        table.add_column("Operation", style="white", width=25)
        table.add_column("Status", justify="center", width=12)
        table.add_column("Duration", justify="center", width=10)
        table.add_column("Details", style="dim", width=35)
        
        # Add successful operations
        for success in self.messages['success']:
            duration_str = f"{success.get('duration', 0):.1f}s" if success.get('duration') else "-"
            table.add_row(
                success['title'], 
                "✅ Success", 
                duration_str,
                success.get('details', '')[:35] + ('...' if len(success.get('details', '')) > 35 else '')
            )
        
        # Add failed operations  
        for error in self.messages['errors']:
            duration_str = f"{error.get('duration', 0):.1f}s" if error.get('duration') else "-"
            table.add_row(
                error['title'], 
                "❌ Failed", 
                duration_str,
                error.get('details', '')[:35] + ('...' if len(error.get('details', '')) > 35 else '')
            )
        
        self.console.print(table)
        
        # Show detailed errors if any
        if self.messages['errors']:
            self.console.print("\n🔴 [bold red]Detailed Error Information:[/bold red]")
            for i, error in enumerate(self.messages['errors'], 1):
                self.console.print(f"\n{i}. [bold]{error['title']}[/bold]")
                if error.get('details'):
                    self.console.print(f"   Details: {error['details']}")
                if error.get('error_output'):
                    self.console.print(f"   Output: [dim]{error['error_output']}[/dim]")
        
        # Show warnings if any
        if self.messages['warnings']:
            self.console.print("\n🟡 [bold yellow]Warnings:[/bold yellow]")
            for i, warning in enumerate(self.messages['warnings'], 1):
                self.console.print(f"{i}. {warning['title']}")
                if warning.get('details'):
                    self.console.print(f"   {warning['details']}")
        
        # Show important information if any
        if self.messages['info']:
            self.console.print("\n📝 [bold]Important Information:[/bold]")
            for info in self.messages['info']:
                self.console.print(f"  • [bold]{info['title']}[/bold]")
                if info.get('details'):
                    # Split details into lines for better formatting
                    for line in info['details'].split('\n'):
                        if line.strip():
                            self.console.print(f"    {line}")
        
        # Summary statistics
        self.console.print(f"\n [bold]Total Operations:[/bold]     {self.operation_stats['total_operations']}    ")
        self.console.print(f" [bold]Successful:[/bold]           {self.operation_stats['successful_operations']}    ")
        
        if self.operation_stats['failed_operations'] > 0:
            self.console.print(f" [bold red]Failed:[/bold red]               {self.operation_stats['failed_operations']}    ")
        
        self.console.print(f" [bold]Total Duration:[/bold]       {self.operation_stats['total_duration']:.1f}s ")
        
        self.console.print("\n" + "─"*60)
        
        # Final status message
        if self.operation_stats['failed_operations'] == 0:
            self.console.print("✅ [bold green]All operations completed successfully![/bold green]")
        else:
            self.console.print("❌ [bold red]Some operations failed. Check details above.[/bold red]")
        
        self.console.print("─"*60)

def create_parser() -> argparse.ArgumentParser:
    """Create command line parser"""
    
    parser = argparse.ArgumentParser(
        description="GitHub Class Template Framework - Unified Management Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ./manage.py --status          Show current framework status
  ./manage.py --build           Full build pipeline (validate + generate + hugo build)
  ./manage.py --dev             Start development server
  ./manage.py --sync            Sync framework updates (students only)
  ./manage.py --deploy          Build for production deployment
  ./manage.py --publish         Complete build + deploy pipeline
  
Command Combinations:
  ./manage.py --build --dev     Build and start development server
  ./manage.py --build --deploy  Build and deploy (same as --publish)
  ./manage.py --sync --build    Sync updates and build (students)
  ./manage.py --sync --dev      Sync updates and start dev server (students)
  
Advanced:
  ./manage.py --validate        Run validation only
  ./manage.py --dev --port 8080 Custom development server port
  ./manage.py --build --force   Skip confirmation prompts
  ./manage.py --clean           Remove generated files
        """
    )
    
    # Common operations
    parser.add_argument("--status", "-s", action="store_true",
                       help="Show current framework status")
    parser.add_argument("--build", "-b", action="store_true",
                       help="Full build pipeline (validate + generate + build)")
    parser.add_argument("--dev", "-d", action="store_true",
                       help="Start development server")
    parser.add_argument("--sync", action="store_true",
                       help="Sync framework updates (students only)")
    parser.add_argument("--deploy", action="store_true",
                       help="Build for production deployment")
    parser.add_argument("--publish", action="store_true",
                       help="Complete build and deploy pipeline (alias for --deploy)")
    
    # Advanced operations
    parser.add_argument("--validate", action="store_true",
                       help="Run validation and generation only")
    parser.add_argument("--clean", action="store_true",
                       help="Clean generated files")
    
    # Discussion management
    parser.add_argument("--discussions-status", action="store_true",
                       help="Show discussions configuration and content status")
    parser.add_argument("--generate-slugs", action="store_true", 
                       help="Generate stable slugs for content missing them")
    parser.add_argument("--discussions-audit", action="store_true",
                       help="Audit content for discussion system readiness")
    
    # Options
    parser.add_argument("--port", type=int, metavar="PORT",
                       help="Development server port (default: 1313 for professor, 1314 for student)")
    parser.add_argument("--force", "-f", action="store_true",
                       help="Skip confirmation prompts")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Show detailed output and full error messages")
    
    return parser

def main():
    """Main entry point"""
    
    parser = create_parser()
    args = parser.parse_args()
    
    # Create manager and set verbosity
    manager = FrameworkManager()
    manager.verbose = args.verbose
    
    try:
        # Single command operations
        if args.status:
            manager.show_status()
            
        elif args.validate:
            manager.validate_and_generate(force=args.force)
            
        elif args.sync:
            manager.sync_student_updates()
            
        elif args.clean:
            manager.clean_generated_files()
            
        elif args.discussions_status:
            manager.discussions_status()
            
        elif args.generate_slugs:
            manager.generate_missing_slugs(force=args.force)
            
        elif args.discussions_audit:
            manager.discussions_audit()
            
        # Handle build/deploy combinations
        elif args.publish or (args.build and args.deploy):
            # Complete publish pipeline: build + deploy
            console.print("\n🚀 [bold]Complete Publish Pipeline[/bold]")
            console.print("This will: build + validate + deploy")
            
            if not args.force and not Confirm.ask("Continue with complete publish?"):
                return
                
            success = manager.full_build_pipeline(force=True)
            if success:
                console.print("🎉 Complete publish pipeline completed successfully!")
            else:
                console.print("❌ Publish pipeline failed")
                
        # Handle sync combinations
        elif args.sync and args.build and args.dev:
            # Sync, build, and start dev server (for students)
            if manager.sync_student_updates():
                manager.full_build_pipeline(force=args.force)
                manager.start_development_server(port=args.port)
                
        elif args.sync and args.build:
            # Sync and build (for students)  
            if manager.sync_student_updates():
                manager.full_build_pipeline(force=args.force)
                
        elif args.sync and args.dev:
            # Sync and start dev server (for students)
            if manager.sync_student_updates():
                manager.start_development_server(port=args.port)
                
        elif args.build:
            manager.full_build_pipeline(force=args.force)
            
        elif args.deploy:
            manager.build_production()
            
        elif args.dev:
            manager.start_development_server(port=args.port)
            
        else:
            parser.print_help()
            
    except KeyboardInterrupt:
        console.print("\n🛑 Operation cancelled by user")
        manager.add_message('warnings', 'Operation Cancelled', 'User interrupted the operation', 'User Action')
    except Exception as e:
        console.print(f"❌ Unexpected error: {e}")
        manager.add_message('errors', 'Unexpected Error', str(e), 'System')
        
    finally:
        # Always show summary at the end (except for dev server and status)
        if not (args.dev or args.status):
            manager.show_final_summary()

if __name__ == "__main__":
    main()