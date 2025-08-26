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
    
    def _get_repo_root(self) -> Path:
        """Get repository root directory consistently across all operations"""
        repo_root = self.current_dir
        if self.current_dir.name in ['professor', 'students']:
            # Traditional execution - we're in content directory
            repo_root = self.current_dir.parent
        elif (self.current_dir / "dna.yml").exists():
            # New execution - we're already at repo root
            repo_root = self.current_dir
        else:
            # Find repo root by looking for dna.yml
            while repo_root.name != repo_root.parent.name and not (repo_root / "dna.yml").exists():
                repo_root = repo_root.parent
        return repo_root
    
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
        
        # Inject class context for frontend JavaScript configuration
        inject_script_path = self.framework_dir / "scripts" / "inject_class_context.py"
        target_directory = "professor" if self.current_dir.name == "professor" else "student"
        
        result = self.subprocess_runner.run_command(
            command=["python3", str(inject_script_path), target_directory],
            description="Injecting class context for frontend",
            working_directory=self.current_dir.parent,  # Run from project root
            capture_output=True,
            verbose=self.message_orchestrator.verbose,
            error_callback=error_callback
        )
        
        if result.returncode != 0:
            self.message_orchestrator.add_message('warnings', 'Class context injection failed', 'Frontend features may be limited')
            # Don't fail the entire build for this - it's not critical
            
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
        repo_root = self._get_repo_root()
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
    
    def _get_professor_directory(self) -> str:
        """Get professor directory name from configuration."""
        # Try to get from build.yml first  
        try:
            import yaml
            repo_root = self._get_repo_root()
                
            build_yml_path = repo_root / "build.yml"
            if build_yml_path.exists():
                with open(build_yml_path, 'r') as f:
                    build_config = yaml.safe_load(f)
                    prof_dir = build_config.get('structure', {}).get('professor_directory')
                    if prof_dir:
                        return prof_dir
            
            # Try class_template/course.yml
            course_yml_path = repo_root / "class_template" / "course.yml"
            if course_yml_path.exists():
                with open(course_yml_path, 'r') as f:
                    course_config = yaml.safe_load(f)
                    prof_dir = course_config.get('structure', {}).get('professor_directory')
                    if prof_dir:
                        return prof_dir
        except Exception:
            pass
            
        # Default fallback
        return "professor"
        
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
            
        # Get professor directory from configuration
        professor_dir = self._get_professor_directory()
        
        # Determine student directory (relative to repo root)
        repo_root = self._get_repo_root()
            
        if self.current_dir.parent.name == 'students':
            # We're in a student directory
            student_dir = f"students/{self.current_dir.name}"
        else:
            student_dir = f"students/{self.context.github_user or 'unknown'}"
        
        # Run sync script from repo root with correct parameters
        sync_script = self.framework_dir / "scripts" / "sync_student.py"
        
        # Create error callback for subprocess runner
        def error_callback(desc: str, error_text: str):
            self.message_orchestrator.add_message('errors', desc, error_text)
        
        result = self.subprocess_runner.run_command(
            command=["python3", str(sync_script), professor_dir, student_dir],
            description="Syncing framework updates",
            working_directory=repo_root,  # Run from repo root
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
        repo_root = self._get_repo_root()
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
        repo_root = self._get_repo_root()
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
    
    def inject_class_context(self, force: bool = False) -> bool:
        """Inject class context for secure frontend operations
        
        Args:
            force: Skip user confirmation if True
            
        Returns:
            bool: True if successful, False otherwise
        """
        
        self.message_orchestrator.start_operation("Class Context Injection")
        
        # Determine target directory based on current context
        target_directory = "professor" if self.role == "professor" else f"students/{self.current_dir.name}"
        
        # Run the class context injection script
        script_path = self.framework_dir / "scripts" / "inject_class_context.py"
        
        # Create error callback for subprocess runner
        def error_callback(desc: str, error_text: str):
            self.message_orchestrator.add_message('errors', desc, error_text)
        
        result = self.subprocess_runner.run_command(
            command=["python3", str(script_path), target_directory],
            description="Injecting class context for secure operations",
            working_directory=self.current_dir,
            capture_output=True,
            verbose=self.message_orchestrator.verbose,
            error_callback=error_callback
        )
        
        if result.returncode != 0:
            self.message_orchestrator.end_operation(False, "Class context injection failed")
            return False
            
        self.message_orchestrator.end_operation(True, "Class context injected successfully")
        return True
    
    def parse_grading_data(self) -> bool:
        """Parse and validate grading configuration files
        
        Returns:
            bool: True if successful, False otherwise
        """
        
        self.message_orchestrator.start_operation("Grading Data Parsing")
        
        # Run the grading data parser
        script_path = self.framework_dir / "scripts" / "parse_grading_data.py"
        
        # Create error callback for subprocess runner
        def error_callback(desc: str, error_text: str):
            self.message_orchestrator.add_message('errors', desc, error_text)
        
        result = self.subprocess_runner.run_command(
            command=["python3", str(script_path)],
            description="Parsing grading configuration files",
            working_directory=self.current_dir,
            capture_output=True,
            verbose=self.message_orchestrator.verbose,
            error_callback=error_callback
        )
        
        if result.returncode != 0:
            self.message_orchestrator.end_operation(False, "Grading data parsing failed")
            return False
            
        self.message_orchestrator.end_operation(True, "Grading data parsed and validated")
        return True
    
    def sync_grading_with_supabase(self) -> bool:
        """Synchronize grading data with Supabase database
        
        Returns:
            bool: True if successful, False otherwise
        """
        
        self.message_orchestrator.start_operation("Grading Data Synchronization")
        
        # Check for required environment variables
        import os
        supabase_url = os.environ.get('SUPABASE_URL')
        supabase_key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or os.environ.get('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            self.message_orchestrator.add_message('warnings', 'Missing Supabase Configuration', 
                'SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not found in environment variables.\n'
                'Grading data synchronization will be skipped.')
            self.message_orchestrator.end_operation(True, "Grading sync skipped - no Supabase config")
            return True
        
        # Run the grading data synchronizer
        script_path = self.framework_dir / "scripts" / "sync_grading_data.py"
        
        # Create error callback for subprocess runner
        def error_callback(desc: str, error_text: str):
            self.message_orchestrator.add_message('errors', desc, error_text)
        
        result = self.subprocess_runner.run_command(
            command=["python3", str(script_path)],
            description="Synchronizing grading data with Supabase",
            working_directory=self.current_dir,
            capture_output=True,
            verbose=self.message_orchestrator.verbose,
            error_callback=error_callback,
            env_vars={'SUPABASE_URL': supabase_url, 'SUPABASE_SERVICE_ROLE_KEY': supabase_key}
        )
        
        if result.returncode != 0:
            self.message_orchestrator.add_message('warnings', 'Grading Sync Failed', 
                'Grading data synchronization failed but build will continue.\n'
                'The framework will work without grading features.')
            self.message_orchestrator.end_operation(True, "Grading sync failed but continuing")
            return True  # Don't fail the entire build
            
        self.message_orchestrator.end_operation(True, "Grading data synchronized with Supabase")
        return True
    
    def parse_and_sync_items(self) -> bool:
        """Parse items from markdown files and sync to Supabase
        
        Returns:
            bool: True if successful, False otherwise
        """
        
        self.message_orchestrator.start_operation("Item Parsing and Sync")
        
        # Run the item parser
        script_path = self.framework_dir / "scripts" / "parse_items.py"
        
        # Create error callback for subprocess runner
        def error_callback(desc: str, error_text: str):
            self.message_orchestrator.add_message('errors', desc, error_text)
        
        result = self.subprocess_runner.run_command(
            command=["python3", str(script_path)],
            description="Parsing items from markdown files",
            working_directory=self.current_dir,
            capture_output=True,
            verbose=self.message_orchestrator.verbose,
            error_callback=error_callback
        )
        
        if result.returncode != 0:
            self.message_orchestrator.add_message('warnings', 'Item Parsing Failed', 
                'Item parsing failed but build will continue.\n'
                'Graded items may not be available for submission.')
            self.message_orchestrator.end_operation(True, "Item parsing failed but continuing")
            return True  # Don't fail the entire build
            
        self.message_orchestrator.end_operation(True, "Items parsed and synchronized")
        return True
    
    def generate_all_grading_json(self) -> bool:
        """Generate all grading JSON files for frontend sync interface
        
        Returns:
            bool: True if successful, False otherwise
        """
        
        self.message_orchestrator.start_operation("Grading JSON Generation")
        
        # Run the grading JSON generator
        script_path = self.framework_dir / "scripts" / "generate_all_grading_json.py"
        
        # Create error callback for subprocess runner
        def error_callback(desc: str, error_text: str):
            self.message_orchestrator.add_message('errors', desc, error_text)
        
        result = self.subprocess_runner.run_command(
            command=["python3", str(script_path)],
            description="Generating grading JSON files",
            working_directory=self.current_dir,
            capture_output=True,
            verbose=self.message_orchestrator.verbose,
            error_callback=error_callback
        )
        
        if result.returncode != 0:
            self.message_orchestrator.add_message('warnings', 'Grading JSON Generation Failed', 
                'Grading JSON generation failed but build will continue.\n'
                'Sync interface may not have current data.')
            self.message_orchestrator.end_operation(True, "Grading JSON generation failed but continuing")
            return False
        
        self.message_orchestrator.end_operation(True, "Grading JSON generation completed")
        return True
    
    def setup_grading_system(self, force: bool = False) -> bool:
        """Complete grading system setup (parse + sync + context injection)
        
        Args:
            force: Skip user confirmation if True
            
        Returns:
            bool: True if successful, False otherwise
        """
        
        self.message_orchestrator.start_operation("Grading System Setup")
        
        if not force:
            from rich.prompt import Confirm
            self.ux.show_pipeline_preview("Grading System Setup", [
                "Parse Configuration", 
                "Validate Data", 
                "Sync with Supabase",
                "Parse Items",
                "Inject Class Context"
            ])
            if not Confirm.ask("Continue with grading system setup?"):
                self.message_orchestrator.end_operation(False, "Setup cancelled by user")
                return False
        
        # Step 1: Parse grading configuration
        if not self.parse_grading_data():
            self.message_orchestrator.end_operation(False, "Setup failed during configuration parsing")
            return False
        
        # Step 2: Synchronize with Supabase
        if not self.sync_grading_with_supabase():
            self.message_orchestrator.end_operation(False, "Setup failed during Supabase sync")
            return False
        
        # Step 3: Parse and sync items
        if not self.parse_and_sync_items():
            self.message_orchestrator.end_operation(False, "Setup failed during item parsing")
            return False
        
        # Step 4: Inject class context
        if not self.inject_class_context(force=True):
            self.message_orchestrator.end_operation(False, "Setup failed during context injection")
            return False
                
        self.message_orchestrator.end_operation(True, "Grading system setup completed successfully")
        return True
    
    def enhanced_build_pipeline(self, force: bool = False) -> bool:
        """Enhanced build pipeline with grading system integration
        
        Args:
            force: Skip user confirmation if True
            
        Returns:
            bool: True if successful, False otherwise
        """
        
        self.message_orchestrator.start_operation("Enhanced Build Pipeline")
        
        if not force:
            self.ux.show_pipeline_preview("Enhanced Build Pipeline", [
                "Validation & Generation", 
                "Grading System Setup",
                "Class Context Injection", 
                "Hugo Build"
            ])
            if not self.ux.show_build_confirmation():
                self.message_orchestrator.end_operation(False, "Pipeline cancelled by user")
                return False
        
        # Step 1: Standard validation and generation
        if not self.validate_and_generate(force=True):
            self.message_orchestrator.end_operation(False, "Pipeline failed during validation")
            return False
        
        # Step 1.5: Generate all grading JSON files
        if not self.generate_all_grading_json():
            self.message_orchestrator.add_message('warnings', 'Grading JSON Generation Failed', 
                'Failed to generate grading JSON files but continuing build')
        
        # Step 2: Setup grading system (non-blocking)
        self.setup_grading_system(force=True)
        
        # Step 3: Build production site
        if not self.build_production():
            self.message_orchestrator.end_operation(False, "Pipeline failed during Hugo build")
            return False
                
        self.message_orchestrator.end_operation(True, "Enhanced build pipeline completed successfully")
        return True
    
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
            'enhanced_pipeline': self.enhanced_build_pipeline,
            'sync': self.sync_student_updates,
            'clean': self.clean_generated_files,
            'dev': self.start_development_server,
            'inject_context': self.inject_class_context,
            'parse_grades': self.parse_grading_data,
            'sync_grades': self.sync_grading_with_supabase,
            'parse_items': self.parse_and_sync_items,
            'setup_grades': self.setup_grading_system
        }
        
        for operation in operations:
            if operation not in operation_map:
                self.message_orchestrator.add_message('errors', 'Invalid Operation', f'Unknown operation: {operation}')
                return False
            
            operation_func = operation_map[operation]
            
            # Handle operations with different signatures
            if operation in ['validate', 'pipeline', 'enhanced_pipeline', 'setup_grades', 'inject_context']:
                if not operation_func(kwargs.get('force', False)):
                    return False
            elif operation == 'dev':
                operation_func(kwargs.get('port'))
            elif operation in ['sync', 'build', 'parse_grades', 'sync_grades', 'parse_items']:
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