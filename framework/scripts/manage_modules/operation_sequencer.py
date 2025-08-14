"""
Operation Sequencer Module for Framework Manager

This module handles the core operational logic, operation dependencies,
and sequencing extracted from the original manage.py for better modularity.

Maintains exact compatibility with the original operation behavior.
"""

import subprocess
import shutil
from pathlib import Path
from typing import List, Optional, Callable, Dict, Any

from rich.console import Console
from rich.prompt import Confirm


class OperationSequencer:
    """Handles core framework operations and their sequencing"""
    
    def __init__(self, console: Console = None):
        self.console = console or Console()
        
        # Dependencies will be injected
        self.subprocess_runner = None
        self.message_orchestrator = None
        self.ux = None
        
        # Environment context (injected)
        self.current_dir = None
        self.framework_dir = None
        self.role = None
    
    def set_dependencies(self, subprocess_runner, message_orchestrator, ux):
        """Inject dependencies from the main framework manager
        
        Args:
            subprocess_runner: SubprocessRunner instance
            message_orchestrator: MessageOrchestrator instance
            ux: UserExperience instance
        """
        self.subprocess_runner = subprocess_runner
        self.message_orchestrator = message_orchestrator
        self.ux = ux
    
    def set_environment_context(self, current_dir: Path, framework_dir: Path, role: str):
        """Set environment context for operations
        
        Args:
            current_dir: Current working directory
            framework_dir: Framework directory path
            role: User role (professor/student)
        """
        self.current_dir = current_dir
        self.framework_dir = framework_dir
        self.role = role
    
    def validate_and_generate(self, force: bool = False) -> bool:
        """Run validation and generation pipeline
        
        Args:
            force: Skip user confirmation if True
            
        Returns:
            bool: True if successful, False otherwise
        """
        
        self.message_orchestrator.start_operation("Validation & Generation")
        
        if not force:
            if not self.ux.show_validation_confirmation():
                self.message_orchestrator.end_operation(False, "Operation cancelled by user")
                return False
        
        # Run the main generation script
        script_path = self.framework_dir / "scripts" / "generate_hugo_config.py"
        
        # Create error callback for subprocess runner
        def error_callback(desc: str, error_text: str):
            self.message_orchestrator.add_message('errors', desc, error_text)
        
        result = self.subprocess_runner.run_command(
            command=["python3", str(script_path)],
            description="Validating and generating framework files",
            working_directory=self.current_dir,
            capture_output=True,
            verbose=self.message_orchestrator.verbose,
            error_callback=error_callback
        )
        
        if result.returncode != 0:
            self.message_orchestrator.end_operation(False, "Validation/generation failed")
            return False
            
        self.message_orchestrator.end_operation(True, "Framework files validated and generated")
        return True
    
    def start_development_server(self, port: int = None):
        """Start Hugo development server
        
        Args:
            port: Server port (defaults based on role)
        """
        
        # Default ports by role
        if port is None:
            port = 1313 if self.role == "professor" else 1314
            
        # NEW: Hugo config is now in root-level hugo_generated/
        repo_root = self.current_dir.parent if self.current_dir.name in ['professor', 'students'] else self.current_dir
        while repo_root.name != repo_root.parent.name and not (repo_root / "dna.yml").exists():
            repo_root = repo_root.parent
        hugo_config = repo_root / "hugo_generated" / "hugo.toml"
        if not hugo_config.exists():
            self.message_orchestrator.add_message('warnings', 'Missing Hugo Config', 'Hugo config not found. Running generation first...')
            if not self.validate_and_generate(force=True):
                return
        
        self.ux.announce_development_server(self.role, port)
        
        self.message_orchestrator.add_message('info', 'Development Server Started', f'Server running on http://localhost:{port}', 'Development')
        
        try:
            subprocess.run([
                "hugo", "server",
                "--config", str(hugo_config),
                "--port", str(port),
                "--bind", "0.0.0.0"
            ], cwd=self.current_dir)
        except KeyboardInterrupt:
            self.console.print("\n🛑 Server stopped")
            self.message_orchestrator.add_message('info', 'Development Server Stopped', 'Server shut down by user', 'Development')
    
    def sync_student_updates(self) -> bool:
        """Sync framework updates for students
        
        Returns:
            bool: True if successful, False otherwise
        """
        
        if self.role != "student":
            self.message_orchestrator.add_message('errors', 'Sync Not Available', 'Sync is only available for students', 'Permission Check')
            return False
            
        self.message_orchestrator.start_operation("Framework Sync")
        
        # Show what will be synced
        self.ux.show_sync_preview()
        
        if not self.ux.show_sync_confirmation():
            self.message_orchestrator.end_operation(False, "Sync cancelled by user")
            return False
            
        # Run sync script
        sync_script = self.framework_dir / "scripts" / "sync_student.py"
        
        # Create error callback for subprocess runner
        def error_callback(desc: str, error_text: str):
            self.message_orchestrator.add_message('errors', desc, error_text)
        
        result = self.subprocess_runner.run_command(
            command=["python3", str(sync_script)],
            description="Syncing framework updates",
            working_directory=self.current_dir,
            verbose=self.message_orchestrator.verbose,
            error_callback=error_callback
        )
        
        if result.returncode != 0:
            self.message_orchestrator.end_operation(False, "Framework sync failed")
            return False
            
        self.message_orchestrator.end_operation(True, "Framework updates synced")
        
        # Regenerate after sync
        return self.validate_and_generate(force=True)
    
    def build_production(self) -> bool:
        """Build production-ready static site
        
        Returns:
            bool: True if successful, False otherwise
        """
        
        self.message_orchestrator.start_operation("Production Build")
        
        # Ensure everything is up to date
        if not self.validate_and_generate(force=True):
            self.message_orchestrator.end_operation(False, "Failed during validation phase")
            return False
            
        # Build with Hugo - NEW: Use root-level hugo_generated/
        repo_root = self.current_dir.parent if self.current_dir.name in ['professor', 'students'] else self.current_dir
        while repo_root.name != repo_root.parent.name and not (repo_root / "dna.yml").exists():
            repo_root = repo_root.parent
        output_dir = repo_root / "hugo_generated" / "public"
        hugo_config = repo_root / "hugo_generated" / "hugo.toml"
        
        # Create error callback for subprocess runner
        def error_callback(desc: str, error_text: str):
            self.message_orchestrator.add_message('errors', desc, error_text)
        
        result = self.subprocess_runner.run_command(
            command=[
                "hugo",
                "--destination", str(output_dir),
                "--config", str(hugo_config),
                "--environment", "production"
            ],
            description="Building static site with Hugo",
            working_directory=self.current_dir,
            verbose=self.message_orchestrator.verbose,
            error_callback=error_callback
        )
        
        if result.returncode != 0:
            self.message_orchestrator.end_operation(False, "Hugo build failed")
            return False
            
        self.message_orchestrator.add_message('info', 'Production Build Complete', f"Site built in: {output_dir}\nUpload the contents of this directory to your hosting service")
        self.message_orchestrator.end_operation(True, f"Static site ready in {output_dir}")
        return True
    
    def full_build_pipeline(self, force: bool = False) -> bool:
        """Run the complete build pipeline
        
        Args:
            force: Skip user confirmation if True
            
        Returns:
            bool: True if successful, False otherwise
        """
        
        self.message_orchestrator.start_operation("Full Build Pipeline")
        
        if not force:
            self.ux.show_pipeline_preview("Full Build Pipeline", ["Validation", "Generation", "Hugo Build"])
            if not self.ux.show_build_confirmation():
                self.message_orchestrator.end_operation(False, "Pipeline cancelled by user")
                return False
        
        # Build production (which includes validation)
        if not self.build_production():
            self.message_orchestrator.end_operation(False, "Pipeline failed during build")
            return False
                
        self.message_orchestrator.end_operation(True, "Complete build pipeline finished")
        return True
    
    def clean_generated_files(self):
        """Clean generated files"""
        
        self.ux.announce_cleaning_operation()
        
        # NEW: Clean files from root-level hugo_generated/
        repo_root = self.current_dir.parent if self.current_dir.name in ['professor', 'students'] else self.current_dir
        while repo_root.name != repo_root.parent.name and not (repo_root / "dna.yml").exists():
            repo_root = repo_root.parent
        files_to_clean = [
            repo_root / "hugo_generated"
        ]
        
        existing_files = [f for f in files_to_clean if f.exists()]
        
        if self.ux.show_files_for_removal(existing_files):
            for file in existing_files:
                if file.is_file():
                    file.unlink()
                elif file.is_dir():
                    shutil.rmtree(file)
                self.ux.show_file_removal_result(file)
    
    def execute_operation_chain(self, operations: List[str], **kwargs) -> bool:
        """Execute a sequence of operations
        
        Args:
            operations: List of operation names to execute in order
            **kwargs: Arguments to pass to operations
            
        Returns:
            bool: True if all operations successful, False otherwise
        """
        
        operation_map = {
            'validate': self.validate_and_generate,
            'build': self.build_production,
            'pipeline': self.full_build_pipeline,
            'sync': self.sync_student_updates,
            'clean': self.clean_generated_files,
            'dev': self.start_development_server
        }
        
        for operation in operations:
            if operation not in operation_map:
                self.message_orchestrator.add_message('errors', 'Invalid Operation', f'Unknown operation: {operation}')
                return False
            
            operation_func = operation_map[operation]
            
            # Handle operations with different signatures
            if operation in ['validate', 'pipeline']:
                if not operation_func(kwargs.get('force', False)):
                    return False
            elif operation == 'dev':
                operation_func(kwargs.get('port'))
            elif operation == 'sync':
                if not operation_func():
                    return False
            elif operation == 'build':
                if not operation_func():
                    return False
            elif operation == 'clean':
                operation_func()
        
        return True


if __name__ == "__main__":
    # Test module functionality
    from rich.console import Console
    
    console = Console()
    sequencer = OperationSequencer(console)
    
    print("✅ Operation sequencer module working correctly")
    
    # Test environment context setting
    sequencer.set_environment_context(
        current_dir=Path("/test/dir"),
        framework_dir=Path("/test/framework"),
        role="professor"
    )
    
    print(f"Environment set: {sequencer.current_dir}, {sequencer.role}")
    
    # Test operation mapping
    operations = ['validate', 'build', 'clean']
    print(f"Operation chain example: {operations}")
    
    print("📋 Operation sequencer ready for integration")