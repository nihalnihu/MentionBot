#!/bin/bash

# Specify the branch name
BRANCH_NAME="main"

# Navigate to the directory containing the Git repository
# Update the path if necessary
cd /path/to/your/repository || { echo "Repository not found!"; exit 1; }

# Checkout the specified branch
git checkout "$BRANCH_NAME" || { echo "Failed to checkout branch $BRANCH_NAME"; exit 1; }

# Pull the latest changes from the specified branch
git pull origin "$BRANCH_NAME" || { echo "Failed to pull latest changes"; exit 1; }

# Restart the bot
# Replace 'your_bot_script.py' with the actual script name and adjust the command if needed
pkill -f 'mention.py'  # Kill the existing bot process
python mention.py &           # Start the bot again in the background

# Notify after the bot has restarted
# Replace the following line with your notification method
# For example, sending a notification to a specific chat via a bot
curl -X POST "https://api.telegram.org/bot7431802835:AAF2Imho1M6AnmBpj9fXZlukVMBt_y_fOes/sendMessage" -d "chat_id=7220858548" -d "text=The bot has been successfully updated and restarted."
