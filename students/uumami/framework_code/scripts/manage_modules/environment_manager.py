"""
Environment Manager Module for Framework Manager

This module handles environment detection and validation logic extracted
from the original manage.py for better modularity.

Maintains exact compatibility with the original environment detection behavior.
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple
from rich.console import Console


class EnvironmentContext:
    """Container for environment detection results"""
    
    def __init__(self):
        self.current_dir: Path = Path.cwd()
        self.role: Optional[str] = None  # 'professor' or 'student'
        self.base_dir: Optional[Path] = None
        self.framework_dir: Optional[Path] = None
        self.is_valid_setup: bool = False


class EnvironmentManager:
    """Manages environment detection and validation for the framework"""
    
    def __init__(self, console: Console = None):
        self.console = console or Console()
        self.context = EnvironmentContext()
    
    def detect_environment(self) -> Tuple[bool, EnvironmentContext]:
        """Detect if we're in a valid framework directory and determine role
        
        Returns:
            tuple: (success, environment_context)
        """
        
        current_dir = Path.cwd()
        
        # Check if we're in professor directory
        if current_dir.name == "professor" and (current_dir.parent / "dna.yml").exists():
            self.context.role = "professor"
            self.context.base_dir = current_dir.parent
            self.context.framework_dir = current_dir / "framework_code"
            self.context.is_valid_setup = True
            self.context.current_dir = current_dir
            return True, self.context
            
        # Check if we're in a student directory
        elif (current_dir.parent.name == "students" and 
              (current_dir.parent.parent / "dna.yml").exists()):
            self.context.role = "student"
            self.context.base_dir = current_dir.parent.parent
            self.context.framework_dir = current_dir / "framework_code"
            self.context.is_valid_setup = True
            self.context.current_dir = current_dir
            return True, self.context
            
        # Check if we're in repository root
        elif (current_dir / "dna.yml").exists():
            self.console.print("📁 You're in the repository root. Please navigate to:")
            self.console.print("   Professor: [cyan]cd professor[/cyan]")
            self.console.print("   Student: [cyan]cd students/[your-username][/cyan]")
            return False, self.context
            
        return False, self.context
    
    def validate_environment(self, context: EnvironmentContext = None) -> Tuple[bool, List[str]]:
        """Validate that all required files and directories exist
        
        Args:
            context: Environment context (uses self.context if None)
            
        Returns:
            tuple: (is_valid, list_of_missing_files)
        """
        
        if context is None:
            context = self.context
            
        if not context.is_valid_setup:
            return False, ["Environment not properly detected"]
            
        required_files = [
            context.framework_dir / "scripts" / "generate_hugo_config.py",
            context.framework_dir / "scripts" / "validate_content.py"
        ]
        
        if context.role == "student":
            required_files.append(context.framework_dir / "scripts" / "sync_student.py")
            
        missing_files = []
        for file_path in required_files:
            if not file_path.exists():
                missing_files.append(str(file_path))
        
        return len(missing_files) == 0, missing_files
    
    def get_environment_info(self, context: EnvironmentContext = None) -> Dict[str, str]:
        """Get formatted environment information for display
        
        Args:
            context: Environment context (uses self.context if None)
            
        Returns:
            dict: Environment information for display
        """
        
        if context is None:
            context = self.context
            
        if not context.is_valid_setup:
            return {
                "status": "invalid",
                "message": "Environment not properly detected"
            }
            
        return {
            "status": "valid",
            "role": context.role.title() if context.role else "Unknown",
            "current_directory": str(context.current_dir),
            "framework_directory": str(context.framework_dir),
            "base_repository": str(context.base_dir),
        }
    
    def show_environment_guidance(self):
        """Show guidance for environment setup"""
        
        self.console.print("❌ Not in a valid framework directory")
        self.console.print("Please run this script from:")
        self.console.print("• Professor: [cyan]professor/[/cyan] directory")
        self.console.print("• Student: [cyan]students/[your-username]/[/cyan] directory")


if __name__ == "__main__":
    # Test module functionality
    env_manager = EnvironmentManager()
    success, context = env_manager.detect_environment()
    
    print(f"✅ Environment detection: {'success' if success else 'failed'}")
    if success:
        print(f"Role: {context.role}")
        print(f"Framework dir: {context.framework_dir}")
        
        is_valid, missing = env_manager.validate_environment(context)
        print(f"Validation: {'passed' if is_valid else 'failed'}")
        if missing:
            print(f"Missing files: {missing}")
    else:
        print("Environment detection failed - not in framework directory")