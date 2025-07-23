#!/bin/bash
# GitHub Class Template Framework - Management Script Wrapper
# Simple shell wrapper for the Python management script

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MANAGE_SCRIPT="$SCRIPT_DIR/manage.py"

# Check if Python script exists
if [[ ! -f "$MANAGE_SCRIPT" ]]; then
    echo "❌ Management script not found: $MANAGE_SCRIPT"
    exit 1
fi

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Run the Python script with all arguments
exec python3 "$MANAGE_SCRIPT" "$@" 