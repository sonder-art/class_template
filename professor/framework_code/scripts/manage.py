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
            self.console.print("❌ Missing required framework files:")
            for file in missing_files:
                self.console.print(f"   {file}")
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
                   capture_output: bool = False) -> subprocess.CompletedProcess:
        """Run a command with rich progress indication"""
        
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
                    
                return result
                
            except Exception as e:
                progress.update(task, description=f"❌ {description} - {str(e)}")
                raise
    
    def validate_and_generate(self, force: bool = False) -> bool:
        """Run validation and generation pipeline"""
        
        self.console.print("\n🔍 [bold]Validation & Generation Pipeline[/bold]")
        
        if not force:
            if not Confirm.ask("Run validation and regenerate all framework files?"):
                return False
        
        # Run the main generation script
        script_path = self.framework_dir / "scripts" / "generate_hugo_config.py"
        result = self.run_command(
            ["python3", str(script_path)],
            "Running validation and generation"
        )
        
        if result.returncode != 0:
            self.console.print("❌ Validation/generation failed")
            self.console.print(f"Error output: {result.stderr}")
            return False
            
        self.console.print("✅ Validation and generation completed successfully")
        return True
    
    def start_development_server(self, port: int = None):
        """Start Hugo development server"""
        
        # Default ports by role
        if port is None:
            port = 1313 if self.role == "professor" else 1314
            
        hugo_config = self.current_dir / "hugo.toml"
        if not hugo_config.exists():
            self.console.print("❌ Hugo config not found. Running generation first...")
            if not self.validate_and_generate(force=True):
                return
        
        self.console.print(f"\n🚀 [bold]Starting Development Server[/bold]")
        self.console.print(f"Role: {self.role}")
        self.console.print(f"Port: {port}")
        self.console.print(f"URL: [link]http://localhost:{port}[/link]")
        self.console.print("\n💡 Press [bold red]Ctrl+C[/bold red] to stop the server")
        
        try:
            subprocess.run([
                "hugo", "server",
                "--config", "hugo.toml",
                "--port", str(port),
                "--bind", "0.0.0.0"
            ], cwd=self.current_dir)
        except KeyboardInterrupt:
            self.console.print("\n🛑 Server stopped")
    
    def sync_student_updates(self) -> bool:
        """Sync framework updates for students"""
        
        if self.role != "student":
            self.console.print("❌ Sync is only available for students")
            return False
            
        self.console.print("\n🔄 [bold]Syncing Framework Updates[/bold]")
        
        # Show what will be synced
        self.console.print("This will update:")
        self.console.print("• Framework code and scripts")
        self.console.print("• New content from professor")
        self.console.print("• Theme and configuration updates")
        self.console.print("\n⚠️ Your personal content will be preserved")
        
        if not Confirm.ask("Continue with sync?"):
            return False
            
        # Run sync script
        sync_script = self.framework_dir / "scripts" / "sync_student.py"
        result = self.run_command(
            ["python3", str(sync_script)],
            "Syncing framework updates"
        )
        
        if result.returncode != 0:
            self.console.print("❌ Sync failed")
            return False
            
        # Regenerate after sync
        return self.validate_and_generate(force=True)
    
    def build_production(self) -> bool:
        """Build production-ready static site"""
        
        self.console.print("\n🏗️ [bold]Building Production Site[/bold]")
        
        # Ensure everything is up to date
        if not self.validate_and_generate(force=True):
            return False
            
        # Build with Hugo
        output_dir = self.framework_dir / "hugo_generated"
        result = self.run_command([
            "hugo",
            "--destination", str(output_dir),
            "--config", "hugo.toml"
        ], "Building static site")
        
        if result.returncode != 0:
            self.console.print("❌ Production build failed")
            return False
            
        self.console.print(f"✅ Production site built in: {output_dir}")
        self.console.print("📁 Upload the contents of this directory to your hosting service")
        return True
    
    def full_build_pipeline(self, force: bool = False) -> bool:
        """Run the complete build pipeline"""
        
        self.console.print("\n🔧 [bold]Full Build Pipeline[/bold]")
        
        steps = [
            ("Validation & Generation", lambda: self.validate_and_generate(force=True)),
            ("Production Build", self.build_production)
        ]
        
        if not force:
            self.console.print("This will:")
            for step_name, _ in steps:
                self.console.print(f"• {step_name}")
                
            if not Confirm.ask("Continue with full build?"):
                return False
        
        for step_name, step_func in steps:
            if not step_func():
                self.console.print(f"❌ Failed at: {step_name}")
                return False
                
        self.console.print("🎉 Full build pipeline completed successfully!")
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
    console.print(Panel.fit(
        f"🚀 [bold]Framework Manager[/bold]\n"
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
    except Exception as e:
        console.print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 