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
        self.current_dir = Path.cwd()
        self.role = None  # 'professor' or 'student'
        self.base_dir = None
        self.framework_dir = None
        self.is_valid_setup = False
        
        # Message collection system
        self.messages = {
            'errors': [],
            'warnings': [],
            'info': [],
            'success': []
        }
        self.operation_start_time = None
        self.current_operation = None
        self.verbose = False
        self.operation_stats = {
            'total_operations': 0,
            'successful_operations': 0,
            'failed_operations': 0,
            'total_duration': 0
        }
        
    def detect_environment(self) -> bool:
        """Detect if we're in a valid framework directory and determine role"""
        
        # Check if we're in professor directory
        if self.current_dir.name == "professor" and (self.current_dir.parent / "dna.yml").exists():
            self.role = "professor"
            self.base_dir = self.current_dir.parent
            self.framework_dir = self.current_dir / "framework_code"
            self.is_valid_setup = True
            return True
            
        # Check if we're in a student directory
        elif (self.current_dir.parent.name == "students" and 
              (self.current_dir.parent.parent / "dna.yml").exists()):
            self.role = "student"
            self.base_dir = self.current_dir.parent.parent
            self.framework_dir = self.current_dir / "framework_code"
            self.is_valid_setup = True
            return True
            
        # Check if we're in repository root
        elif (self.current_dir / "dna.yml").exists():
            self.console.print("📁 You're in the repository root. Please navigate to:")
            self.console.print("   Professor: [cyan]cd professor[/cyan]")
            self.console.print("   Student: [cyan]cd students/[your-username][/cyan]")
            return False
            
        return False
    
    def add_message(self, message_type: str, title: str, details: str = None, context: str = None, duration: float = None):
        """Add a message to be shown in the final summary"""
        if message_type not in self.messages:
            return
            
        message = {
            'title': title,
            'details': details,
            'context': context or self.current_operation,
            'timestamp': time.time(),
            'duration': duration
        }
        self.messages[message_type].append(message)
    
    def start_operation(self, operation_name: str):
        """Start tracking an operation"""
        self.current_operation = operation_name
        self.operation_start_time = time.time()
        self.operation_stats['total_operations'] += 1
        
        if self.verbose:
            self.console.print(f"\n🔄 [bold]{operation_name}[/bold]")
        else:
            self.console.print(f"🔄 {operation_name}...")
    
    def end_operation(self, success: bool, message: str = None):
        """End tracking an operation"""
        if self.operation_start_time:
            duration = time.time() - self.operation_start_time
            duration_str = f"({duration:.1f}s)"
            self.operation_stats['total_duration'] += duration
        else:
            duration = None
            duration_str = ""
            
        if success:
            icon = "✅"
            self.operation_stats['successful_operations'] += 1
            if message:
                self.add_message('success', self.current_operation, message, None, duration)
        else:
            icon = "❌"
            self.operation_stats['failed_operations'] += 1
            if message:
                self.add_message('errors', self.current_operation, message, None, duration)
                
        if self.verbose:
            if message:
                self.console.print(f"{icon} {self.current_operation}: {message} {duration_str}")
            else:
                self.console.print(f"{icon} {self.current_operation} {duration_str}")
        else:
            # Compact output for non-verbose mode
            status_msg = message if message else ("completed" if success else "failed")
            self.console.print(f"  {icon} {status_msg} {duration_str}")
            
        self.current_operation = None
        self.operation_start_time = None
    
    def validate_environment(self) -> bool:
        """Validate that all required files and directories exist"""
        
        if not self.is_valid_setup:
            return False
            
        required_files = [
            self.framework_dir / "scripts" / "generate_hugo_config.py",
            self.framework_dir / "scripts" / "validate_content.py"
        ]
        
        if self.role == "student":
            required_files.append(self.framework_dir / "scripts" / "sync_student.py")
            
        missing_files = [f for f in required_files if not f.exists()]
        
        if missing_files:
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
        
        # Check if Hugo config exists
        hugo_config = self.current_dir / "hugo.toml"
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
        
        # Default show_progress based on verbose mode
        if show_progress is None:
            show_progress = self.verbose
            
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
                        cwd=self.current_dir
                    )
                    
                    if result.returncode == 0:
                        progress.update(task, description=f"✅ {description}")
                    else:
                        progress.update(task, description=f"❌ {description}")
                        if result.stderr:
                            self.add_message('errors', description, result.stderr.strip())
                        
                    return result
                    
                except Exception as e:
                    progress.update(task, description=f"❌ {description} - {str(e)}")
                    self.add_message('errors', description, str(e))
                    raise
        else:
            # Silent execution for less verbose operations
            try:
                result = subprocess.run(
                    command,
                    capture_output=capture_output,
                    text=True,
                    cwd=self.current_dir
                )
                
                if result.returncode != 0 and result.stderr:
                    self.add_message('errors', description, result.stderr.strip())
                    
                return result
                
            except Exception as e:
                self.add_message('errors', description, str(e))
                raise
    
    def validate_and_generate(self, force: bool = False) -> bool:
        """Run validation and generation pipeline"""
        
        self.start_operation("Validation & Generation")
        
        if not force:
            if not Confirm.ask("Run validation and regenerate all framework files?"):
                self.end_operation(False, "Operation cancelled by user")
                return False
        
        # Run the main generation script
        script_path = self.framework_dir / "scripts" / "generate_hugo_config.py"
        result = self.run_command(
            ["python3", str(script_path)],
            "Validating and generating framework files",
            capture_output=True
        )
        
        if result.returncode != 0:
            self.end_operation(False, "Validation/generation failed")
            return False
            
        self.end_operation(True, "Framework files validated and generated")
        return True
    
    def start_development_server(self, port: int = None):
        """Start Hugo development server"""
        
        # Default ports by role
        if port is None:
            port = 1313 if self.role == "professor" else 1314
            
        hugo_config = self.current_dir / "hugo.toml"
        if not hugo_config.exists():
            self.add_message('warnings', 'Missing Hugo Config', 'Hugo config not found. Running generation first...')
            if not self.validate_and_generate(force=True):
                return
        
        self.console.print(f"\n🚀 [bold]Starting Development Server[/bold]")
        self.console.print(f"Role: {self.role} | Port: {port} | URL: [link]http://localhost:{port}[/link]")
        self.console.print("\n💡 Press [bold red]Ctrl+C[/bold red] to stop the server")
        
        self.add_message('info', 'Development Server Started', f'Server running on http://localhost:{port}', 'Development')
        
        try:
            subprocess.run([
                "hugo", "server",
                "--config", "hugo.toml",
                "--port", str(port),
                "--bind", "0.0.0.0"
            ], cwd=self.current_dir)
        except KeyboardInterrupt:
            self.console.print("\n🛑 Server stopped")
            self.add_message('info', 'Development Server Stopped', 'Server shut down by user', 'Development')
    
    def sync_student_updates(self) -> bool:
        """Sync framework updates for students"""
        
        if self.role != "student":
            self.add_message('errors', 'Sync Not Available', 'Sync is only available for students', 'Permission Check')
            return False
            
        self.start_operation("Framework Sync")
        
        # Show what will be synced
        self.console.print("This will update:")
        self.console.print("• Framework code and scripts")
        self.console.print("• New content from professor")
        self.console.print("• Theme and configuration updates")
        self.console.print("\n⚠️ Your personal content will be preserved")
        
        if not Confirm.ask("Continue with sync?"):
            self.end_operation(False, "Sync cancelled by user")
            return False
            
        # Run sync script
        sync_script = self.framework_dir / "scripts" / "sync_student.py"
        result = self.run_command(
            ["python3", str(sync_script)],
            "Syncing framework updates"
        )
        
        if result.returncode != 0:
            self.end_operation(False, "Framework sync failed")
            return False
            
        self.end_operation(True, "Framework updates synced")
        
        # Regenerate after sync
        return self.validate_and_generate(force=True)
    
    def build_production(self) -> bool:
        """Build production-ready static site"""
        
        self.start_operation("Production Build")
        
        # Ensure everything is up to date
        if not self.validate_and_generate(force=True):
            self.end_operation(False, "Failed during validation phase")
            return False
            
        # Build with Hugo
        output_dir = self.framework_dir / "hugo_generated"
        result = self.run_command([
            "hugo",
            "--destination", str(output_dir),
            "--config", "hugo.toml"
        ], "Building static site with Hugo")
        
        if result.returncode != 0:
            self.end_operation(False, "Hugo build failed")
            return False
            
        self.add_message('info', 'Production Build Complete', f"Site built in: {output_dir}\nUpload the contents of this directory to your hosting service")
        self.end_operation(True, f"Static site ready in {output_dir}")
        return True
    
    def full_build_pipeline(self, force: bool = False) -> bool:
        """Run the complete build pipeline"""
        
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
        table.add_column("Status", style="white", width=12)
        table.add_column("Duration", style="dim", width=10)
        table.add_column("Details", style="dim")
        
        # Add successful operations
        for success in self.messages['success']:
            duration_str = f"{success['duration']:.1f}s" if success.get('duration') else "-"
            details = success['details'][:50] + "..." if success['details'] and len(success['details']) > 50 else success['details'] or ""
            table.add_row(
                success['title'],
                "[green]✅ Success[/green]",
                duration_str,
                details
            )
        
        # Add errors
        for error in self.messages['errors']:
            duration_str = f"{error['duration']:.1f}s" if error.get('duration') else "-"
            details = error['details'][:50] + "..." if error['details'] and len(error['details']) > 50 else error['details'] or ""
            table.add_row(
                error['title'],
                "[red]❌ Failed[/red]",
                duration_str,
                details
            )
        
        # Add warnings
        for warning in self.messages['warnings']:
            details = warning['details'][:50] + "..." if warning['details'] and len(warning['details']) > 50 else warning['details'] or ""
            table.add_row(
                warning['title'],
                "[yellow]⚠️ Warning[/yellow]",
                "-",
                details
            )
        
        self.console.print(table)
        
        # Show detailed errors if any exist
        if self.messages['errors'] and not self.verbose:
            self.console.print("\n❌ [bold red]Error Details:[/bold red]")
            for i, error in enumerate(self.messages['errors'], 1):
                self.console.print(f"  {i}. [red]{error['title']}[/red]")
                if error['details']:
                    # Show first few lines of error details
                    details_lines = error['details'].split('\n')[:2]
                    for line in details_lines:
                        if line.strip():
                            self.console.print(f"     [dim]{line.strip()}[/dim]")
                    if len(error['details'].split('\n')) > 2:
                        self.console.print("     [dim]... (use --verbose for full details)[/dim]")
        
        # Show verbose details if enabled
        if self.verbose and (self.messages['errors'] or self.messages['warnings']):
            if self.messages['errors']:
                self.console.print("\n❌ [bold red]Full Error Details:[/bold red]")
                for i, error in enumerate(self.messages['errors'], 1):
                    self.console.print(f"  {i}. [red]{error['title']}[/red]")
                    if error['context']:
                        self.console.print(f"     Context: [dim]{error['context']}[/dim]")
                    if error['details']:
                        for line in error['details'].split('\n'):
                            if line.strip():
                                self.console.print(f"     {line.strip()}")
                    self.console.print()
            
            if self.messages['warnings']:
                self.console.print("⚠️ [bold yellow]Full Warning Details:[/bold yellow]")
                for i, warning in enumerate(self.messages['warnings'], 1):
                    self.console.print(f"  {i}. [yellow]{warning['title']}[/yellow]")
                    if warning['context']:
                        self.console.print(f"     Context: [dim]{warning['context']}[/dim]")
                    if warning['details']:
                        self.console.print(f"     {warning['details']}")
                    self.console.print()
        
        # Show important info
        if self.messages['info']:
            important_info = [info for info in self.messages['info'] if 'server' in info['title'].lower() or 'build' in info['title'].lower()]
            if important_info:
                self.console.print("\n📝 [bold blue]Important Information:[/bold blue]")
                for info in important_info:
                    self.console.print(f"  • [blue]{info['title']}[/blue]")
                    if info['details']:
                        # Handle multi-line details
                        for line in info['details'].split('\n'):
                            if line.strip():
                                self.console.print(f"    {line.strip()}")
        
        # Show statistics and final status
        stats_table = Table(show_header=False, box=None)
        stats_table.add_column("Metric", style="cyan", width=20)
        stats_table.add_column("Value", style="white")
        
        stats_table.add_row("Total Operations:", str(self.operation_stats['total_operations']))
        stats_table.add_row("Successful:", f"[green]{self.operation_stats['successful_operations']}[/green]")
        if self.operation_stats['failed_operations'] > 0:
            stats_table.add_row("Failed:", f"[red]{self.operation_stats['failed_operations']}[/red]")
        if self.operation_stats['total_duration'] > 0:
            stats_table.add_row("Total Duration:", f"{self.operation_stats['total_duration']:.1f}s")
        
        self.console.print("\n")
        self.console.print(stats_table)
        
        # Final status message
        self.console.print("\n" + "─"*60)
        if self.messages['errors']:
            self.console.print("🛑 [bold red]Operations completed with errors[/bold red]")
            if not self.verbose:
                self.console.print("   💡 Use [cyan]--verbose[/cyan] flag for detailed error information")
        elif self.messages['warnings']:
            self.console.print("⚠️ [bold yellow]Operations completed with warnings[/bold yellow]")
            if not self.verbose:
                self.console.print("   💡 Use [cyan]--verbose[/cyan] flag for detailed warning information")
        else:
            self.console.print("✅ [bold green]All operations completed successfully![/bold green]")
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
    
    # Show help if no arguments
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    manager = FrameworkManager()
    manager.verbose = args.verbose
    
    # Environment detection and validation
    if not manager.detect_environment():
        console.print("❌ Not in a valid framework directory")
        console.print("Please run this script from:")
        console.print("• Professor: [cyan]professor/[/cyan] directory")
        console.print("• Student: [cyan]students/[your-username]/[/cyan] directory")
        sys.exit(1)
    
    if not manager.validate_environment():
        console.print("❌ Framework environment validation failed")
        sys.exit(1)
    
    # Show welcome message
    verbose_indicator = " [dim](verbose mode)[/dim]" if manager.verbose else ""
    console.print(Panel.fit(
        f"🚀 [bold]Framework Manager[/bold]{verbose_indicator}\n"
        f"Role: [cyan]{manager.role.title()}[/cyan]\n"
        f"Directory: [yellow]{manager.current_dir}[/yellow]",
        border_style="green"
    ))
    
    # Execute commands
    try:
        # Handle single commands first
        if args.status:
            manager.show_status()
            
        elif args.validate:
            manager.validate_and_generate(force=args.force)
            
        elif args.sync:
            manager.sync_student_updates()
            
        elif args.clean:
            manager.clean_generated_files()
            
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
                
        elif args.build and args.dev:
            # Build and start dev server
            if manager.full_build_pipeline(force=args.force):
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