#!/bin/bash

# Exit on error
set -e

echo "🚀 Starting release process..."

PACKAGE_DIR="fastapi_startkit"

if [ -d "$PACKAGE_DIR" ]; then
    echo "📦 Releasing package: $PACKAGE_DIR"

    # Navigate to package directory
    cd "$PACKAGE_DIR"

    # Build and Publish
    echo "   Building and publishing..."
    uv build
    uv publish

    # Return to root
    cd - > /dev/null
    echo "✅ $PACKAGE_DIR processed."
    echo "----------------------------------------"
else
    echo "⚠️  Package directory $PACKAGE_DIR not found."
    exit 1
fi
