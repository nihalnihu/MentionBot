#!/bin/bash

# Specify the branch name
BRANCH_NAME="main"

# Navigate to the directory containing the Git repository
cd https://github.com/nihalnihu/MentionBot || { echo "Repository not found!"; exit 1; }

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
