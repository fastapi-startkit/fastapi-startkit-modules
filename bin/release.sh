#!/bin/bash

# Exit on error
set -e

echo "🚀 Starting release process..."

PACKAGE_DIR="fastapi_startkit"
BUMP_TYPE=$1

if [ -d "$PACKAGE_DIR" ]; then
    echo "📦 Releasing package: $PACKAGE_DIR"

    # Navigate to package directory
    cd "$PACKAGE_DIR"

    # Bump version if requested
    if [ -n "$BUMP_TYPE" ]; then
        echo "   Bumping version ($BUMP_TYPE)..."
        uv version --bump "$BUMP_TYPE"
    fi

    # Build and Publish
    echo "   Building and publishing..."
    rm -rf dist/
    uv build
    
    # Use twine for publishing (natively handles ~/.pypirc)
    echo "   Uploading to PyPI via twine..."
    twine upload dist/*

    # Return to root
    cd - > /dev/null
    echo "✅ $PACKAGE_DIR processed."
    echo "----------------------------------------"
else
    echo "⚠️  Package directory $PACKAGE_DIR not found."
    exit 1
fi
