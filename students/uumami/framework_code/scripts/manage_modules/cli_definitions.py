"""
CLI Definitions Module for Framework Manager

This module contains the command-line interface definitions and argument parsing
logic extracted from the original manage.py for better modularity.

Maintains exact compatibility with the original argument parser.
"""

import argparse
from typing import Optional


def create_parser() -> argparse.ArgumentParser:
    """Create command line parser
    
    Returns:
        argparse.ArgumentParser: Configured argument parser with all framework commands
    """
    
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


def validate_arguments(args) -> tuple[bool, Optional[str]]:
    """Validate argument combinations
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        tuple: (is_valid, error_message)
    """
    
    # Check for conflicting combinations
    # Currently all combinations are valid, but this provides extensibility
    
    return True, None


def get_command_examples() -> str:
    """Get formatted command examples for help display
    
    Returns:
        str: Formatted examples text
    """
    
    return """
Common Usage:
  ./manage.py --status          # Check current state
  ./manage.py --build           # Full build pipeline  
  ./manage.py --dev             # Start development server
  ./manage.py --sync            # Sync updates (students)
  
Pipeline Combinations:
  ./manage.py --build --dev     # Build then serve
  ./manage.py --sync --build    # Sync then build (students)
  ./manage.py --publish         # Complete deployment pipeline
"""


if __name__ == "__main__":
    # Test module functionality
    parser = create_parser()
    print("✅ CLI definitions module working correctly")
    print("Available arguments:")
    parser.print_help()