#!/bin/bash

# Exit on error
set -e

BUMP_TYPE=${1:-patch}

echo "🚀 Starting release process with $BUMP_TYPE bump..."

PACKAGE_DIR="fastapi_startkit"

if [ -d "$PACKAGE_DIR" ]; then
    echo "📦 Releasing package: $PACKAGE_DIR"

    # Navigate to package directory
    cd "$PACKAGE_DIR"

    # Bump version
    echo "   Bumping version..."
    uv version --bump "$BUMP_TYPE"

    # Build
    echo "   Building..."
    uv build

    # Publish via twine
    echo "   Publishing..."
    uv run twine upload dist/* --verbose

    # Return to root
    cd - > /dev/null
    echo "✅ $PACKAGE_DIR processed."
    echo "----------------------------------------"
else
    echo "⚠️  Package directory $PACKAGE_DIR not found."
    exit 1
fi
