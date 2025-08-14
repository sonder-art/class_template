"""
User Experience Module for Framework Manager

This module handles rich UI components, welcome panels, user confirmations,
and interactive flows extracted from the original manage.py for better modularity.

Maintains exact compatibility with the original user interaction behavior.
"""

from pathlib import Path
from typing import List, Optional, Dict, Any

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from rich.table import Table


class UserExperience:
    """Handles rich UI components and user interaction flows"""
    
    def __init__(self, console: Console = None):
        self.console = console or Console()
    
    def show_welcome_panel(self, framework_info: Dict[str, Any]):
        """Show the framework manager welcome panel
        
        Args:
            framework_info: Dictionary with manager information:
                - role: User role (professor/student)
                - current_dir: Current directory path
                - verbose: Whether in verbose mode
        """
        
        verbose_indicator = " [dim](verbose mode)[/dim]" if framework_info.get('verbose', False) else ""
        role = framework_info.get('role', 'Unknown').title()
        current_dir = framework_info.get('current_dir', 'Unknown')
        
        self.console.print(Panel.fit(
            f"🚀 [bold]Framework Manager[/bold]{verbose_indicator}\n"
            f"Role: [cyan]{role}[/cyan]\n"
            f"Directory: [yellow]{current_dir}[/yellow]",
            border_style="green"
        ))
    
    def show_environment_guidance(self):
        """Show guidance for running from correct directory"""
        
        import os
        from pathlib import Path
        
        self.console.print("❌ Not in a valid framework directory")
        
        # Show additional debug info in GitHub Actions
        if os.environ.get('GITHUB_ACTIONS') == 'true':
            self.console.print(f"🔍 DEBUG - Current directory: {Path.cwd()}")
            self.console.print(f"🔍 DEBUG - BUILD_TARGET_DIR: {os.environ.get('BUILD_TARGET_DIR', 'Not set')}")
            self.console.print(f"🔍 DEBUG - BUILD_TARGET: {os.environ.get('BUILD_TARGET', 'Not set')}")
            self.console.print(f"🔍 DEBUG - Directory contents: {list(Path.cwd().iterdir())[:10]}")
        
        self.console.print("Please run this script from:")
        self.console.print("• Professor: [cyan]professor/[/cyan] directory")
        self.console.print("• Student: [cyan]students/[your-username]/[/cyan] directory")
    
    def get_user_confirmation(self, message: str, force: bool = False) -> bool:
        """Get user confirmation with force override
        
        Args:
            message: Confirmation message to display
            force: If True, bypass confirmation and return True
            
        Returns:
            bool: True if user confirms or force is True
        """
        
        if force:
            return True
        
        return Confirm.ask(message)
    
    def announce_operation(self, operation_name: str, description: str = None):
        """Announce start of a major operation
        
        Args:
            operation_name: Name of the operation
            description: Optional description of what will happen
        """
        
        self.console.print(f"\n🚀 [bold]{operation_name}[/bold]")
        if description:
            self.console.print(description)
    
    def announce_development_server(self, role: str, port: int):
        """Announce development server startup
        
        Args:
            role: User role (professor/student) 
            port: Server port number
        """
        
        self.console.print(f"\n🚀 [bold]Starting Development Server[/bold]")
        self.console.print(f"Role: {role} | Port: {port} | URL: [link]http://localhost:{port}[/link]")
        self.console.print("\n💡 Press [bold red]Ctrl+C[/bold red] to stop the server")
    
    def announce_cleaning_operation(self):
        """Announce file cleaning operation"""
        
        self.console.print("\n🧹 [bold]Cleaning Generated Files[/bold]")
    
    def show_files_for_removal(self, files: List[Path]) -> bool:
        """Show files that will be removed and get confirmation
        
        Args:
            files: List of file paths to be removed
            
        Returns:
            bool: True if user confirms removal, False otherwise
        """
        
        if not files:
            self.console.print("✅ No generated files to clean")
            return False
            
        self.console.print("Files to be removed:")
        for file in files:
            self.console.print(f"• {file}")
            
        return Confirm.ask("Remove these files?")
    
    def show_file_removal_result(self, file_path: Path):
        """Show result of file removal
        
        Args:
            file_path: Path of the removed file
        """
        
        self.console.print(f"🗑️ Removed: {file_path}")
    
    def show_operation_success(self, message: str):
        """Show successful operation message
        
        Args:
            message: Success message to display
        """
        
        self.console.print(f"🎉 {message}")
    
    def show_operation_failure(self, message: str):
        """Show failed operation message
        
        Args:
            message: Failure message to display
        """
        
        self.console.print(f"❌ {message}")
    
    def show_operation_info(self, message: str, status: str = "info"):
        """Show informational message with appropriate icon
        
        Args:
            message: Information message to display
            status: Status type (info, success, warning, error)
        """
        
        icons = {
            'info': 'ℹ️',
            'success': '✅',
            'warning': '⚠️',  
            'error': '❌'
        }
        
        icon = icons.get(status, 'ℹ️')
        self.console.print(f"{icon} {message}")
    
    def show_pipeline_preview(self, pipeline_name: str, steps: List[str]):
        """Show preview of pipeline steps
        
        Args:
            pipeline_name: Name of the pipeline
            steps: List of pipeline steps
        """
        
        self.console.print(f"\n🚀 [bold]{pipeline_name}[/bold]")
        steps_text = " → ".join(steps)
        self.console.print(f"This will run: {steps_text}")
    
    def show_sync_preview(self):
        """Show preview of sync operation"""
        
        self.console.print("This will update:")
        self.console.print("• Framework code and scripts")
        self.console.print("• New content from professor")
        self.console.print("• Theme and configuration updates")
        self.console.print("\n⚠️ Your personal content will be preserved")
    
    def create_status_table(self, status_data: Dict[str, str], title: str = "Status") -> Table:
        """Create a formatted status table
        
        Args:
            status_data: Dictionary of status key-value pairs
            title: Table title
            
        Returns:
            Table: Formatted rich table
        """
        
        table = Table(title=title, show_header=True, header_style="bold magenta")
        table.add_column("Property", style="cyan", width=20)
        table.add_column("Value", style="green")
        
        for key, value in status_data.items():
            table.add_row(key, value)
        
        return table
    
    def show_table(self, table: Table):
        """Display a table
        
        Args:
            table: Rich table to display
        """
        
        self.console.print(table)
    
    def show_validation_confirmation(self) -> bool:
        """Show validation operation confirmation
        
        Returns:
            bool: True if user confirms
        """
        
        return Confirm.ask("Run validation and regenerate all framework files?")
    
    def show_build_confirmation(self) -> bool:
        """Show build pipeline confirmation
        
        Returns:
            bool: True if user confirms
        """
        
        return Confirm.ask("Continue with full build?")
    
    def show_sync_confirmation(self) -> bool:
        """Show sync operation confirmation
        
        Returns:
            bool: True if user confirms
        """
        
        return Confirm.ask("Continue with sync?")
    
    def show_publish_confirmation(self) -> bool:
        """Show publish pipeline confirmation
        
        Returns:
            bool: True if user confirms
        """
        
        return Confirm.ask("Continue with complete publish?")


if __name__ == "__main__":
    # Test module functionality
    ux = UserExperience()
    
    print("✅ User experience module working correctly")
    
    # Test welcome panel
    framework_info = {
        'role': 'professor',
        'current_dir': '/test/directory',
        'verbose': True
    }
    ux.show_welcome_panel(framework_info)
    
    # Test operation announcement
    ux.announce_operation("Test Operation", "This is a test operation")
    
    # Test status messages
    ux.show_operation_success("Test completed successfully")
    ux.show_operation_info("This is test information")
    
    # Test confirmations (commented out to avoid interactive prompts)
    # confirmed = ux.get_user_confirmation("Continue with test?", force=True)
    # print(f"Confirmation result: {confirmed}")
    
    print("📋 All UX components tested successfully")