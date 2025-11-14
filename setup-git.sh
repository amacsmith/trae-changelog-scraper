#!/bin/bash

# Setup script for initializing the output directory as a git repository
# This script helps set up the automated git push feature

set -e

echo "====================================="
echo "Trae Changelog Scraper - Git Setup"
echo "====================================="
echo ""

# Check if output directory exists
if [ ! -d "output" ]; then
    echo "Creating output directory..."
    mkdir -p output/images
fi

cd output

# Initialize git if not already done
if [ ! -d ".git" ]; then
    echo "Initializing git repository..."
    git init
    echo ""
fi

# Check if remote is set
if ! git remote get-url origin &>/dev/null; then
    echo "Please enter your GitHub repository URL (SSH format):"
    echo "Example: git@github.com:amacsmith/trae-changed.git"
    read -p "URL: " REPO_URL

    git remote add origin "$REPO_URL"
    echo "Remote 'origin' added: $REPO_URL"
    echo ""
fi

# Create initial README if it doesn't exist
if [ ! -f "README.md" ]; then
    cat > README.md << 'EOF'
# Trae.ai Changelog Archive

This repository contains the scraped changelog from Trae.ai.

- **View Online**: [GitHub Pages](https://amacsmith.github.io/trae-changed/)
- **Markdown**: [changelog.md](changelog.md)
- **Images**: [images/](images/)

## Auto-updated

This repository is automatically updated every 15 minutes by a Docker service.

Last manual update: $(date -u)
EOF
    echo "Created initial README.md"
fi

# Copy index.html template if it doesn't exist
if [ ! -f "index.html" ] && [ -f "../index.html.template" ]; then
    cp ../index.html.template index.html
    echo "Copied index.html template"
fi

# Set up gitignore
if [ ! -f ".gitignore" ]; then
    cat > .gitignore << 'EOF'
# Ignore temp files
*.tmp
*.temp
.DS_Store
Thumbs.db
EOF
    echo "Created .gitignore"
fi

echo ""
echo "Git setup complete!"
echo ""
echo "Next steps:"
echo "1. Make sure you have SSH keys set up for GitHub"
echo "2. Test the scraper: python ../scraper.py"
echo "3. Check git status: git status"
echo "4. Start Docker: docker-compose up -d"
echo ""
echo "Your SSH keys location: ~/.ssh/"
echo "Make sure your SSH key is added to your GitHub account!"
echo ""
