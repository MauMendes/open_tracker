#!/bin/bash

# OpenTracker Database Cleanup Script
# Shell wrapper for the Python cleanup script

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🚀 OpenTracker Database Cleanup"
echo "=============================="
echo

# Check if virtual environment exists
if [ -d "$PROJECT_DIR/venv" ]; then
    echo "🐍 Activating virtual environment..."
    source "$PROJECT_DIR/venv/bin/activate"
else
    echo "⚠️  Virtual environment not found. Using system Python."
fi

# Change to project directory
cd "$PROJECT_DIR"

# Run the Python cleanup script
python scripts/clean_database.py

# Exit with the same code as the Python script
exit $?