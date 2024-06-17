#!/bin/bash
# Check if a repository URL was provided
if [ $# -eq 0 ]; then
    echo "No repository URL provided"
    exit 1
fi

REPO_URL=$1
REPO_NAME=$(basename $REPO_URL .git)

# Check if the repository URL is valid
if [[ ! "$REPO_URL" =~ ^https://github.com/[^/]+/[^/]+\.git$ ]]; then
    echo "Invalid repository URL"
    exit 2
fi

# Clone the repository
if ! git clone "$REPO_URL" "$REPO_NAME"; then
    echo "Failed to clone repository"
    exit 3
fi

echo "Repository cloned successfully"
exit 0