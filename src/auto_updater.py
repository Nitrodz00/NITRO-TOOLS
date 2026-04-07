"""
Automatic In-Place Updater for NITROTOOLS
Professional update system that updates the current executable in-place.
"""

import os
import sys
import subprocess
import tempfile
import requests
import hashlib
import shutil
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from PyQt5.QtWidgets import QMessageBox, QApplication


class AutoUpdater(QThread):
    """
    Automatic in-place updater that replaces the current executable
    with the new version automatically.
    """
    
    update_available = pyqtSignal(str, str, str)  # version, url, changelog
    update_downloaded = pyqtSignal(str)  # download path
    update_installed = pyqtSignal()  # update completed
    update_failed = pyqtSignal(str)  # error message
    progress_updated = pyqtSignal(int)  # progress percentage
    
    def __init__(self, current_version, repo_api_url):
        super().__init__()
        self.current_version = current_version
        self.repo_api_url = repo_api_url
        self.running = True
        
    def run(self):
        """Main update process."""
        try:
            # Check for updates
            if not self._check_for_updates():
                return
                
            # Download update
            download_path = self._download_update()
            if not download_path:
                return
                
            # Install update
            self._install_update(download_path)
            
        except Exception as e:
            self.update_failed.emit(f"Update failed: {str(e)}")
    
    def _check_for_updates(self):
        """Check if a new version is available."""
        try:
            response = requests.get(self.repo_api_url, timeout=10)
            if response.status_code == 200:
                releases = response.json()
                if releases:
                    latest_release = releases[0]
                    latest_version = latest_release['tag_name']
                    
                    # Remove 'v' prefix if present
                    if latest_version.startswith('v'):
                        latest_version = latest_version[1:]
                    
                    if self._is_newer_version(latest_version, self.current_version):
                        # Find the executable asset
                        download_url = None
                        for asset in latest_release.get('assets', []):
                            if asset['name'].endswith('.exe') or asset['name'].endswith('.zip'):
                                download_url = asset['browser_download_url']
                                break
                        
                        if download_url:
                            changelog = latest_release.get('body', '')
                            self.update_available.emit(latest_version, download_url, changelog)
                            return True
                            
        except Exception as e:
            self.update_failed.emit(f"Failed to check for updates: {str(e)}")
            
        return False
    
    def _is_newer_version(self, latest, current):
        """Compare version strings."""
        def version_tuple(v):
            # Remove 'v' prefix and split
            v = v.lstrip('v')
            return tuple(map(int, (v.split("."))))
        
        return version_tuple(latest) > version_tuple(current)
    
    def _download_update(self):
        """Download the update file."""
        try:
            # Get download info from signal (this should be stored)
            if not hasattr(self, '_download_url'):
                return None
                
            # Download to temp directory
            temp_dir = tempfile.gettempdir()
            filename = f"NITROTOOLS_UPDATE_{self.current_version}_to_latest.exe"
            download_path = os.path.join(temp_dir, filename)
            
            response = requests.get(self._download_url, stream=True, timeout=60)
            if response.status_code == 200:
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                with open(download_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if not self.running:
                            return None
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = int((downloaded / total_size) * 100)
                            self.progress_updated.emit(progress)
                
                self.update_downloaded.emit(download_path)
                return download_path
                
        except Exception as e:
            self.update_failed.emit(f"Download failed: {str(e)}")
            
        return None
    
    def _install_update(self, update_path):
        """Install the update by replacing the current executable."""
        try:
            # Get current executable path
            current_exe = sys.executable
            current_dir = os.path.dirname(current_exe)
            
            # Get the update script path
            script_path = os.path.join(current_dir, "src", "update_script.py")
            
            # Launch update script and exit current application
            subprocess.Popen([
                sys.executable, script_path, current_exe, update_path
            ], creationflags=subprocess.CREATE_NEW_CONSOLE)
            
            # Signal that update is being installed
            self.update_installed.emit()
            
            # Exit current application to allow update
            QApplication.quit()
            
        except Exception as e:
            self.update_failed.emit(f"Installation failed: {str(e)}")
    
    def set_download_info(self, download_url):
        """Set download URL for the update."""
        self._download_url = download_url
    
    def stop(self):
        """Stop the update process."""
        self.running = False


class AutoUpdateManager:
    """
    Manager class for handling automatic updates with user interaction.
    """
    
    def __init__(self, parent_window, current_version, repo_api_url):
        self.parent_window = parent_window
        self.current_version = current_version
        self.repo_api_url = repo_api_url
        self.updater = None
        
    def check_for_updates(self):
        """Check for updates in background."""
        self.updater = AutoUpdater(self.current_version, self.repo_api_url)
        self.updater.update_available.connect(self._on_update_available)
        self.updater.update_downloaded.connect(self._on_update_downloaded)
        self.updater.update_installed.connect(self._on_update_installed)
        self.updater.update_failed.connect(self._on_update_failed)
        self.updater.progress_updated.connect(self._on_progress_updated)
        self.updater.start()
    
    def _on_update_available(self, version, url, changelog):
        """Handle update available notification."""
        reply = QMessageBox.question(
            self.parent_window,
            "NITROTOOLS Update Available",
            f"New version {version} is available!\n\n"
            f"Current version: {self.current_version}\n"
            f"New version: {version}\n\n"
            f"Changelog:\n{changelog[:300]}...\n\n"
            f"Do you want to update automatically?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.updater.set_download_info(url)
            # Show progress dialog or update status
            self.parent_window.show_status_message("Downloading update...")
        else:
            self.updater.stop()
    
    def _on_update_downloaded(self, path):
        """Handle download completion."""
        self.parent_window.show_status_message("Installing update...")
        # Installation will happen automatically
    
    def _on_update_installed(self):
        """Handle successful installation."""
        self.parent_window.show_status_message("Update installed! Restarting...")
        # Application will restart automatically
    
    def _on_update_failed(self, error):
        """Handle update failure."""
        QMessageBox.critical(
            self.parent_window,
            "Update Failed",
            f"Failed to update NITROTOOLS:\n{error}\n\n"
            "Please download the update manually from GitHub."
        )
    
    def _on_progress_updated(self, progress):
        """Handle progress updates."""
        self.parent_window.show_status_message(f"Downloading update... {progress}%")
