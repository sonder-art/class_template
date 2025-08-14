"""
Manage Modules - Orchestration Components for Framework Manager

This package contains the refactored orchestration modules that were extracted
from the monolithic manage.py to improve maintainability and testability.

All modules maintain backward compatibility with the original FrameworkManager API.
"""

__version__ = "1.0.0"
__author__ = "GitHub Class Template Framework"

# Version check to ensure we're working with the expected manage.py structure
EXPECTED_MANAGE_VERSION = "1.0.0"

def get_module_info():
    """Get information about all available orchestration modules"""
    return {
        "version": __version__,
        "modules": [
            "cli_definitions",
            "environment_manager", 
            "subprocess_runner",
            "message_orchestrator",
            "user_experience",
            "operation_sequencer",
            "command_router"
        ],
        "status": "refactored_from_monolithic_manage_py"
    }