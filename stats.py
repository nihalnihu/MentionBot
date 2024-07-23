#!/bin/bash

# Specify the branch name
BRANCH_NAME="main"

# Navigate to the directory containing the Git repository
# Update the path if necessary
cd https://github.com/nihalnihu/MentionBot || { echo "Repository not found!"; exit 1; }

# Checkout the specified branch
git checkout "$BRANCH_NAME" || { echo "Failed to checkout branch $BRANCH_NAME"; exit 1; }

# Pull the latest changes from the specified branch
git pull origin "$BRANCH_NAME" || { echo "Failed to pull latest changes"; exit 1; }

# Restart the bot
# Replace 'your_bot_script.py' with the actual script name and adjust the command if needed
pkill -f 'python mention.py'  # Kill the existing bot process
python mention.py &           # Start the bot again in the background
