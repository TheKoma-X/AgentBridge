#!/bin/bash

# AgentBridge Sync to GitHub
# This script creates a complete backup of the AgentBridge project

echo "🚀 Starting AgentBridge synchronization..."

# Create a timestamped archive
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
ARCHIVE_NAME="AgentBridge_${TIMESTAMP}.tar.gz"

echo "📦 Creating archive: $ARCHIVE_NAME"

# Create compressed archive of all project files
tar -czf "$ARCHIVE_NAME" \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.pytest_cache' \
    --exclude='.venv' \
    --exclude='venv' \
    --exclude='node_modules' \
    --exclude='.DS_Store' \
    --exclude='Thumbs.db' \
    .

echo "✅ Archive created successfully!"

# Show archive contents
echo ""
echo "📄 Archive contents:"
tar -tzf "$ARCHIVE_NAME" | head -20
echo "... (truncated)"

# Show size
ARCHIVE_SIZE=$(du -h "$ARCHIVE_NAME" | cut -f1)
echo ""
echo "💾 Archive size: $ARCHIVE_SIZE"

# If git credentials are configured, attempt to push
if git remote get-url origin >/dev/null 2>&1; then
    echo ""
    echo "📡 Attempting git push..."
    
    # Check if we're in a proper git repository
    if [ -d ".git" ] && git status >/dev/null 2>&1; then
        echo "📋 Git status:"
        git status --porcelain
        
        echo ""
        echo "🏷️  Current branch:"
        git branch --show-current
        
        # Only try to push if we have commits
        if git log --oneline -1 >/dev/null 2>&1; then
            echo ""
            echo "📤 Attempting to push to remote repository..."
            git push origin main || echo "⚠️  Push failed - check your git credentials"
        else
            echo "ℹ️  No commits to push"
        fi
    else
        echo "⚠️  Not in a git repository or git unavailable"
    fi
else
    echo "ℹ️  No git remote configured - skipping push"
fi

echo ""
echo "🎉 AgentBridge synchronization complete!"
echo ""
echo "📋 Summary:"
echo "   • Archive: $ARCHIVE_NAME"
echo "   • Size: $ARCHIVE_SIZE" 
echo "   • Timestamp: $(date)"
echo ""
echo "💡 To restore this backup, simply extract with: tar -xzf $ARCHIVE_NAME"
echo "💡 To set up git push, configure your GitHub credentials first"