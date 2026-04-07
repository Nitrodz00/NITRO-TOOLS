"""
In-place update script for NITROTOOLS
This script handles the actual file replacement process.
"""

import os
import sys
import time
import shutil
import subprocess


def main():
    """Main update process."""
    try:
        # Get command line arguments
        if len(sys.argv) < 3:
            print("Usage: update_script.py <current_exe> <new_exe>")
            return 1
        
        current_exe = sys.argv[1]
        new_exe = sys.argv[2]
        
        print(f"Starting update process...")
        print(f"Current: {current_exe}")
        print(f"New: {new_exe}")
        
        # Wait for main application to close
        print("Waiting for application to close...")
        for i in range(30):  # Wait up to 30 seconds
            if not is_process_running("NITROTOOLS_PUBG_MOBILE"):
                break
            time.sleep(1)
            print(f"Waiting... ({i+1}/30)")
        
        # Create backup
        backup_path = current_exe + ".backup"
        print(f"Creating backup: {backup_path}")
        if os.path.exists(current_exe):
            shutil.copy2(current_exe, backup_path)
        
        # Replace the executable
        print("Installing new version...")
        shutil.copy2(new_exe, current_exe)
        
        # Verify the update
        if os.path.exists(current_exe) and os.path.getsize(current_exe) > 0:
            print("Update completed successfully!")
            
            # Start the updated application
            print("Starting updated application...")
            subprocess.Popen([current_exe], shell=True)
            
            # Clean up
            try:
                os.remove(new_exe)
                os.remove(sys.argv[0])  # Remove this script
            except:
                pass
            
            return 0
        else:
            print("Update failed! Restoring backup...")
            if os.path.exists(backup_path):
                shutil.copy2(backup_path, current_exe)
            return 1
            
    except Exception as e:
        print(f"Update failed: {e}")
        return 1


def is_process_running(process_name):
    """Check if a process is running."""
    try:
        result = subprocess.run(['tasklist', '/FI', f'IMAGENAME eq {process_name}.exe'], 
                              capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        return process_name in result.stdout
    except:
        return False


if __name__ == "__main__":
    sys.exit(main())
