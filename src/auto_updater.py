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
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from PyQt5.QtWidgets import QMessageBox, QApplication


class UpdateCheckThread(QThread):
    """Background thread that checks GitHub for a newer release."""

    # version, download_url, changelog
    update_available = pyqtSignal(str, str, str)
    no_update = pyqtSignal()
    check_failed = pyqtSignal(str)

    def __init__(self, current_version, repo_api_url):
        super().__init__()
        self.current_version = current_version.lstrip('v')
        self.repo_api_url = repo_api_url

    def run(self):
        try:
            response = requests.get(self.repo_api_url, timeout=10)
            if response.status_code != 200:
                self.check_failed.emit(f"GitHub API returned {response.status_code}")
                return

            releases = response.json()
            if not releases:
                self.no_update.emit()
                return

            # API may return a list (multi-release endpoint) or a single object (/latest)
            if isinstance(releases, list):
                latest_release = releases[0]
            else:
                latest_release = releases

            latest_version = latest_release.get('tag_name', '').lstrip('v')

            if not latest_version or not self._is_newer(latest_version, self.current_version):
                self.no_update.emit()
                return

            # Prefer .exe asset, then .zip, skip .sha256
            asset = None
            for ext in ('.exe', '.zip'):
                asset = next((a for a in latest_release.get('assets', [])
                              if str(a.get('name', '')).lower().endswith(ext)), None)
                if asset:
                    break
            if asset is None:
                # pick first non-sha256 asset
                asset = next((a for a in latest_release.get('assets', [])
                              if not str(a.get('name', '')).lower().endswith('.sha256')), None)
            if asset is None:
                self.no_update.emit()
                return

            download_url = asset.get('browser_download_url', '')
            changelog = latest_release.get('body', '') or ''
            self.update_available.emit(latest_version, download_url, changelog)

        except requests.exceptions.ConnectionError:
            self.check_failed.emit("No internet connection.")
        except requests.exceptions.Timeout:
            self.check_failed.emit("Connection timed out.")
        except Exception as e:
            self.check_failed.emit(str(e))

    @staticmethod
    def _is_newer(latest: str, current: str) -> bool:
        try:
            return tuple(map(int, latest.split('.'))) > tuple(map(int, current.split('.')))
        except Exception:
            return latest != current


class UpdateDownloadThread(QThread):
    """Background thread that downloads an update file."""

    progress = pyqtSignal(int)
    completed = pyqtSignal(str)  # downloaded file path
    failed = pyqtSignal(str)

    def __init__(self, download_url):
        super().__init__()
        self.download_url = download_url
        self.running = True

    def run(self):
        try:
            temp_dir = tempfile.gettempdir()
            download_path = os.path.join(temp_dir, "NITROTOOLS_UPDATE.exe")

            response = requests.get(self.download_url, stream=True, timeout=300)
            if response.status_code != 200:
                self.failed.emit(f"Download failed: HTTP {response.status_code}")
                return

            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0

            with open(download_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if not self.running:
                        self.failed.emit("Download cancelled.")
                        return
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        self.progress.emit(int((downloaded / total_size) * 100))

            self.progress.emit(100)
            self.completed.emit(download_path)

        except Exception as e:
            self.failed.emit(f"Download error: {e}")

    def stop(self):
        self.running = False


class AutoUpdateManager:
    """
    Manager class for handling automatic updates with user interaction.
    Orchestrates check → prompt → download → install flow.
    """

    def __init__(self, parent_window, current_version, repo_api_url):
        self.parent_window = parent_window
        self.current_version = current_version
        self.repo_api_url = repo_api_url
        self._checker = None
        self._downloader = None
        self._pending_url = None

    def check_for_updates(self):
        """Check for updates in background."""
        self._checker = UpdateCheckThread(self.current_version, self.repo_api_url)
        self._checker.update_available.connect(self._on_update_available)
        self._checker.no_update.connect(self._on_no_update)
        self._checker.check_failed.connect(self._on_check_failed)
        self._checker.start()

    # -- Signals from check thread --

    def _on_update_available(self, version, url, changelog):
        """Prompt the user to download the new version."""
        clean_log = changelog[:500].strip()
        if len(changelog) > 500:
            clean_log += "\n..."

        reply = QMessageBox.question(
            self.parent_window,
            "NITROTOOLS — Update Available",
            f"A new version is available!\n\n"
            f"Current: v{self.current_version.lstrip('v')}\n"
            f"Latest:  v{version}\n\n"
            f"{clean_log}\n\n"
            f"Download and install now?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self._start_download(url)
        else:
            self.parent_window.show_status_message("Update skipped.")

    def _on_no_update(self):
        self.parent_window.show_status_message("You are on the latest version.")

    def _on_check_failed(self, error):
        self.parent_window.show_status_message(f"Update check failed: {error}")

    # -- Download --

    def _start_download(self, url):
        self.parent_window.show_status_message("Downloading update...")
        self._downloader = UpdateDownloadThread(url)
        self._downloader.progress.connect(self._on_download_progress)
        self._downloader.completed.connect(self._on_download_complete)
        self._downloader.failed.connect(self._on_download_failed)
        self._downloader.start()

    def _on_download_progress(self, pct):
        self.parent_window.show_status_message(f"Downloading update... {pct}%")

    def _on_download_complete(self, path):
        self.parent_window.show_status_message("Download complete. Installing...")
        self._install_update(path)

    def _on_download_failed(self, error):
        QMessageBox.critical(
            self.parent_window,
            "Update Failed",
            f"Failed to download update:\n{error}\n\n"
            "Please download manually from GitHub."
        )
        self.parent_window.show_status_message("Update download failed.")

    # -- Install --

    def _install_update(self, update_path):
        """Replace current EXE via a batch script, then restart."""
        try:
            current_exe = sys.executable

            bat_path = os.path.join(tempfile.gettempdir(), "nitro_update.bat")
            with open(bat_path, "w") as bat:
                bat.write('@echo off\n')
                bat.write('echo Updating NITROTOOLS, please wait...\n')
                bat.write('set count=0\n')
                bat.write(':wait_loop\n')
                bat.write('timeout /t 1 /nobreak >nul\n')
                bat.write(f'del /Q "{current_exe}" >nul 2>&1\n')
                bat.write(f'if exist "{current_exe}" (\n')
                bat.write('  set /a count+=1\n')
                bat.write('  if %count% LSS 15 goto wait_loop\n')
                bat.write(')\n')
                bat.write(f'move /Y "{update_path}" "{current_exe}" >nul\n')
                bat.write(f'start "" "{current_exe}"\n')
                bat.write('del "%~f0"\n')

            subprocess.Popen(
                ['cmd', '/c', bat_path],
                creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS,
                close_fds=True
            )

            self.parent_window.show_status_message("Restarting with new version...")
            QTimer.singleShot(1500, QApplication.quit)

        except Exception as e:
            QMessageBox.critical(
                self.parent_window,
                "Install Failed",
                f"Could not install update:\n{e}\n\n"
                f"The downloaded file is at:\n{update_path}\n"
                "You can replace the EXE manually."
            )
            self.parent_window.show_status_message("Update install failed.")
