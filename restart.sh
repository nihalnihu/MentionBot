#!/bin/bash

# Specify the branch name
BRANCH_NAME="main"

# Specify the directory to clone into
REPO_DIR="MentionBot"

# Check if the repository directory exists and delete it
if [ -d "$REPO_DIR" ]; then
    echo "Repository directory found. Deleting..."
    rm -rf "$REPO_DIR" || { echo "Failed to delete existing repository directory"; exit 1; }
fi

# Clone the repository
echo "Cloning repository..."
git clone https://github.com/nihalnihu/MentionBot.git "$REPO_DIR" || { echo "Failed to clone repository"; exit 1; }

# Navigate to the directory containing the Git repository
cd "$REPO_DIR" || { echo "Failed to navigate to repository directory"; exit 1; }

# Checkout the specified branch
git checkout "$BRANCH_NAME" || { echo "Failed to checkout branch $BRANCH_NAME"; exit 1; }

# Pull the latest changes from the specified branch
git pull origin "$BRANCH_NAME" || { echo "Failed to pull latest changes"; exit 1; }

# Restart the bot
pkill -f 'mention.py'  # Kill the existing bot process
python mention.py &    # Start the bot again in the background

# Notify after the bot has restarted
curl -X POST "https://api.telegram.org/bot7431802835:AAF2Imho1M6AnmBpj9fXZlukVMBt_y_fOes/sendMessage" \
     -d "chat_id=7431802835" \
     -d "text=The bot has been successfully updated and restarted."
