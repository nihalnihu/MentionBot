import os
import subprocess
import sys

def update_and_restart():
    try:
      subprocess.check_call(["git", "pull"])
      os.execv(sys.executable, ['python'] + sys.argv)
    except subprocess.CalledProcessError as e:
      print(f"An error occurred while updating: {e}")

if __name__ == "__main__":
    update_and_restart()
