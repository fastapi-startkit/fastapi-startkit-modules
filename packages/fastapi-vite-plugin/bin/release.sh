#!/usr/bin/env bash

set -e

# Ensure we are in the package directory
cd "$(dirname "$0")/.."

# Check if we're on a clean branch
if [[ -n $(git status --porcelain) ]]; then
    echo "⚠️  You have uncommitted changes. Please commit or stash them before releasing."
    exit 1
fi

# Build the project
echo "📦 Building project..."
npm run build

# Default to patch if no argument is provided
VERSION_TYPE=${1:-patch}
echo "🚀 Bumping version ($VERSION_TYPE)..."
npm version "$VERSION_TYPE" -m "chore: release v%s"

# Get the current branch name
BRANCH=$(git branch --show-current)

# Push to git
echo "📤 Pushing to git ($BRANCH)..."
git push origin "$BRANCH" --tags

# Publish to NPM
echo "✨ Publishing to NPM..."
npm publish --access public

echo "✅ Release complete!"
