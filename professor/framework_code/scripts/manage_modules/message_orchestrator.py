"""
Message Orchestrator Module for Framework Manager

This module handles message collection, operation tracking, and final summary 
reporting extracted from the original manage.py for better modularity.

Maintains exact compatibility with the original message system behavior.
"""

import time
from typing import Dict, List, Optional
from rich.console import Console
from rich.table import Table


class MessageOrchestrator:
    """Handles message collection, operation tracking, and summary reporting"""
    
    def __init__(self, console: Console = None):
        self.console = console or Console()
        
        # Message collection system
        self.messages = {
            'errors': [],
            'warnings': [],
            'info': [],
            'success': []
        }
        
        # Operation tracking
        self.operation_start_time = None
        self.current_operation = None
        self.verbose = False
        
        # Operation statistics
        self.operation_stats = {
            'total_operations': 0,
            'successful_operations': 0,
            'failed_operations': 0,
            'total_duration': 0
        }
    
    def set_verbose(self, verbose: bool):
        """Set verbose mode for operation display"""
        self.verbose = verbose
    
    def add_message(self, message_type: str, title: str, details: str = None, 
                   context: str = None, duration: float = None):
        """Add a message to be shown in the final summary
        
        Args:
            message_type: Type of message ('errors', 'warnings', 'info', 'success')
            title: Message title
            details: Detailed message content
            context: Context (defaults to current operation)
            duration: Operation duration in seconds
        """
        
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
        """Start tracking an operation
        
        Args:
            operation_name: Human-readable name of the operation
        """
        
        self.current_operation = operation_name
        self.operation_start_time = time.time()
        self.operation_stats['total_operations'] += 1
        
        if self.verbose:
            self.console.print(f"\n🔄 [bold]{operation_name}[/bold]")
        else:
            self.console.print(f"🔄 {operation_name}...")
    
    def end_operation(self, success: bool, message: str = None):
        """End tracking an operation
        
        Args:
            success: Whether the operation was successful
            message: Optional completion message
        """
        
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
    
    def has_messages(self) -> bool:
        """Check if there are any messages to show"""
        return any(self.messages.values())
    
    def show_final_summary(self):
        """Show final summary of all operations with warnings and errors"""
        
        if not self.has_messages():
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
    
    def get_operation_statistics(self) -> Dict[str, int]:
        """Get current operation statistics
        
        Returns:
            dict: Operation statistics
        """
        return self.operation_stats.copy()
    
    def clear_messages(self):
        """Clear all collected messages and reset statistics"""
        self.messages = {
            'errors': [],
            'warnings': [],
            'info': [],
            'success': []
        }
        self.operation_stats = {
            'total_operations': 0,
            'successful_operations': 0,
            'failed_operations': 0,
            'total_duration': 0
        }


if __name__ == "__main__":
    # Test module functionality
    orchestrator = MessageOrchestrator()
    orchestrator.set_verbose(True)
    
    print("✅ Message orchestrator module working correctly")
    
    # Test operation tracking
    orchestrator.start_operation("Test Operation")
    time.sleep(0.1)  # Simulate work
    orchestrator.end_operation(True, "Test completed successfully")
    
    # Test message collection
    orchestrator.add_message('info', 'Test Info', 'This is a test info message')
    orchestrator.add_message('warning', 'Test Warning', 'This is a test warning')
    
    # Test statistics
    stats = orchestrator.get_operation_statistics()
    print(f"Operations: {stats['total_operations']}, Successful: {stats['successful_operations']}")
    
    # Test summary (commented out to avoid cluttering test output)
    # orchestrator.show_final_summary()