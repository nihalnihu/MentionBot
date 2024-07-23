import os
import subprocess
import sys

def update_and_restart():
    branch_name = 'main'  # Specify the branch name here
    try:
        # Check out the specified branch
        subprocess.check_call(["git", "checkout", branch_name])
        # Pull the latest code from the specified branch
        subprocess.check_call(["git", "pull", "origin", branch_name])
        # Restart the bot
        os.execv(sys.executable, ['python'] + sys.argv)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while updating: {e}")

if __name__ == "__main__":
    update_and_restart()
