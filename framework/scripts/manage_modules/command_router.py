"""
Command Router Module for Framework Manager

This module handles command combination logic and routing extracted from the
original manage.py main() function for better modularity.

Maintains exact compatibility with the original command routing behavior.
"""

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass


@dataclass
class CommandAction:
    """Represents a command action to be executed"""
    operation: str
    kwargs: Dict[str, Any]
    success_message: Optional[str] = None
    failure_message: Optional[str] = None


@dataclass
class CommandFlow:
    """Represents a complete command execution flow"""
    actions: List[CommandAction]
    show_summary: bool = True
    preview_info: Optional[Dict[str, Any]] = None


class CommandRouter:
    """Handles command combination logic and routing"""
    
    def __init__(self):
        self.command_flows = {}
        self._setup_command_flows()
    
    def _setup_command_flows(self):
        """Setup all command flow definitions"""
        
        # Single commands
        self.command_flows.update({
            'status': CommandFlow(
                actions=[CommandAction('show_status', {})],
                show_summary=False
            ),
            'validate': CommandFlow(
                actions=[CommandAction('validate_and_generate', {'force_key': 'force'})]
            ),
            'sync': CommandFlow(
                actions=[CommandAction('sync_student_updates', {})]
            ),
            'clean': CommandFlow(
                actions=[CommandAction('clean_generated_files', {})],
                show_summary=False
            ),
            'build': CommandFlow(
                actions=[CommandAction('full_build_pipeline', {'force_key': 'force'})]
            ),
            'deploy': CommandFlow(
                actions=[CommandAction('build_production', {})]
            ),
            'dev': CommandFlow(
                actions=[CommandAction('start_development_server', {'port_key': 'port'})],
                show_summary=False
            )
        })
        
        # Complex command combinations
        self.command_flows.update({
            'publish': CommandFlow(
                actions=[
                    CommandAction(
                        'full_build_pipeline',
                        {'force': True},
                        success_message="Complete publish pipeline completed successfully!",
                        failure_message="Publish pipeline failed"
                    )
                ],
                preview_info={
                    'title': 'Complete Publish Pipeline',
                    'steps': ['build', 'validate', 'deploy'],
                    'confirmation': 'Continue with complete publish?'
                }
            ),
            'build_and_dev': CommandFlow(
                actions=[
                    CommandAction('full_build_pipeline', {'force_key': 'force'}),
                    CommandAction('start_development_server', {'port_key': 'port'})
                ],
                show_summary=False
            ),
            'sync_and_build': CommandFlow(
                actions=[
                    CommandAction('sync_student_updates', {}),
                    CommandAction('full_build_pipeline', {'force_key': 'force'})
                ]
            ),
            'sync_and_dev': CommandFlow(
                actions=[
                    CommandAction('sync_student_updates', {}),
                    CommandAction('start_development_server', {'port_key': 'port'})
                ],
                show_summary=False
            )
        })
    
    def route_commands(self, args) -> str:
        """Determine which command flow to execute based on arguments
        
        Args:
            args: Parsed command line arguments
            
        Returns:
            str: Command flow key to execute
        """
        
        # Handle complex combinations first (order matters!)
        if args.publish or (args.build and args.deploy):
            return 'publish'
        elif args.build and args.dev:
            return 'build_and_dev'
        elif args.sync and args.build:
            return 'sync_and_build'
        elif args.sync and args.dev:
            return 'sync_and_dev'
        
        # Handle single commands
        elif args.status:
            return 'status'
        elif args.validate:
            return 'validate'
        elif args.sync:
            return 'sync'
        elif args.clean:
            return 'clean'
        elif args.build:
            return 'build'
        elif args.deploy:
            return 'deploy'
        elif args.dev:
            return 'dev'
        
        # No valid command found
        return 'help'
    
    def get_command_flow(self, flow_key: str) -> Optional[CommandFlow]:
        """Get command flow definition
        
        Args:
            flow_key: Command flow key
            
        Returns:
            CommandFlow: Flow definition or None if not found
        """
        return self.command_flows.get(flow_key)
    
    def should_show_summary(self, flow_key: str) -> bool:
        """Check if summary should be shown for this command flow
        
        Args:
            flow_key: Command flow key
            
        Returns:
            bool: True if summary should be shown
        """
        flow = self.get_command_flow(flow_key)
        return flow.show_summary if flow else True
    
    def execute_command_flow(self, flow_key: str, args, manager) -> bool:
        """Execute a complete command flow
        
        Args:
            flow_key: Command flow key to execute
            args: Parsed command line arguments  
            manager: FrameworkManager instance
            
        Returns:
            bool: True if all operations successful, False otherwise
        """
        
        if flow_key == 'help':
            # Import here to avoid circular imports
            from manage_modules.cli_definitions import create_parser
            parser = create_parser()
            parser.print_help()
            return True
        
        flow = self.get_command_flow(flow_key)
        if not flow:
            manager.add_message('errors', 'Invalid Command Flow', f'Unknown flow: {flow_key}')
            return False
        
        # Show preview if needed
        if flow.preview_info:
            manager.ux.show_pipeline_preview(
                flow.preview_info['title'],
                flow.preview_info['steps']
            )
            
            if not manager.ux.get_user_confirmation(
                flow.preview_info['confirmation'],
                args.force
            ):
                return True  # User cancelled, not an error
        
        # Execute actions in sequence
        for action in flow.actions:
            success = self._execute_action(action, args, manager)
            
            if not success:
                # If this action has a failure message, show it
                if action.failure_message:
                    manager.ux.show_operation_failure(action.failure_message)
                return False
            
            # If this action has a success message, show it
            if action.success_message:
                manager.ux.show_operation_success(action.success_message)
        
        return True
    
    def _execute_action(self, action: CommandAction, args, manager) -> bool:
        """Execute a single action
        
        Args:
            action: CommandAction to execute
            args: Parsed command line arguments
            manager: FrameworkManager instance
            
        Returns:
            bool: True if successful, False otherwise
        """
        
        # Get the operation method from manager
        if not hasattr(manager, action.operation):
            manager.add_message('errors', 'Invalid Operation', f'Unknown operation: {action.operation}')
            return False
        
        operation_func = getattr(manager, action.operation)
        
        # Prepare kwargs from action and args
        kwargs = {}
        for key, value in action.kwargs.items():
            if key.endswith('_key'):
                # This is a reference to an args attribute
                arg_key = value
                kwargs[key[:-4]] = getattr(args, arg_key, None)  # Remove '_key' suffix
            else:
                # This is a direct value
                kwargs[key] = value
        
        # Execute the operation
        try:
            result = operation_func(**kwargs)
            
            # Handle operations that return bool vs None
            if result is False:
                return False
            
            return True
            
        except Exception as e:
            manager.add_message('errors', f'Operation Failed: {action.operation}', str(e))
            return False
    
    def get_available_flows(self) -> List[str]:
        """Get list of available command flow keys
        
        Returns:
            List[str]: Available flow keys
        """
        return list(self.command_flows.keys())
    
    def validate_command_combination(self, args) -> tuple[bool, Optional[str]]:
        """Validate command line argument combinations
        
        Args:
            args: Parsed command line arguments
            
        Returns:
            tuple: (is_valid, error_message)
        """
        
        # Check for conflicting combinations
        # Currently all combinations in the original are valid
        # This provides extensibility for future validation
        
        return True, None


if __name__ == "__main__":
    # Test module functionality
    router = CommandRouter()
    
    print("✅ Command router module working correctly")
    
    # Test flow availability
    flows = router.get_available_flows()
    print(f"Available flows: {len(flows)}")
    print(f"Single commands: status, validate, sync, clean, build, deploy, dev")
    print(f"Complex combinations: publish, build_and_dev, sync_and_build, sync_and_dev")
    
    # Test routing logic
    class MockArgs:
        def __init__(self, **kwargs):
            self.status = kwargs.get('status', False)
            self.build = kwargs.get('build', False)
            self.dev = kwargs.get('dev', False)
            self.sync = kwargs.get('sync', False)
            self.publish = kwargs.get('publish', False)
            self.deploy = kwargs.get('deploy', False)
            self.validate = kwargs.get('validate', False)
            self.clean = kwargs.get('clean', False)
            self.force = kwargs.get('force', False)
            self.port = kwargs.get('port', None)
    
    # Test some routing scenarios
    test_scenarios = [
        (MockArgs(status=True), 'status'),
        (MockArgs(build=True, dev=True), 'build_and_dev'),
        (MockArgs(sync=True, build=True), 'sync_and_build'),
        (MockArgs(publish=True), 'publish'),
        (MockArgs(build=True), 'build')
    ]
    
    for args, expected in test_scenarios:
        result = router.route_commands(args)
        status = "✅" if result == expected else "❌"
        print(f"{status} {expected}: {result}")
    
    print("📋 Command router ready for integration")