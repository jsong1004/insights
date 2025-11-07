#!/bin/bash

# Flask Runner Script with WeasyPrint Support
# Sets up library paths for macOS

# Set library paths for WeasyPrint
export DYLD_LIBRARY_PATH="/opt/homebrew/lib:$DYLD_LIBRARY_PATH"
export DYLD_FALLBACK_LIBRARY_PATH="/opt/homebrew/lib"

# Run Flask
echo "Starting Flask with WeasyPrint support..."
python app.py
