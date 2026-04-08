"""
Automatic In-Place Updater for NITROTOOLS
Professional update system that updates the current executable in-place.
"""

import os
import sys
import json
import zipfile
import subprocess
import tempfile
import requests
import hashlib
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from PyQt5.QtWidgets import QMessageBox, QApplication

PATCH_DIR = os.path.join(os.environ.get('LOCALAPPDATA', tempfile.gettempdir()), 'NitroTools')
PATCH_LOG = os.path.join(PATCH_DIR, 'patches.json')


def _applied_patches():
    try:
        with open(PATCH_LOG, 'r') as f:
            return set(json.load(f).get('applied', []))
    except Exception:
        return set()


def _mark_patch_applied(name):
    applied = _applied_patches()
    applied.add(name)
    os.makedirs(PATCH_DIR, exist_ok=True)
    with open(PATCH_LOG, 'w') as f:
        json.dump({'applied': list(applied)}, f)


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

    # patch_name, download_url
    patch_available = pyqtSignal(str, str)

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

            if isinstance(releases, list):
                latest_release = releases[0]
            else:
                latest_release = releases

            latest_version = latest_release.get('tag_name', '').lstrip('v')

            if latest_version and self._is_newer(latest_version, self.current_version):
                # Full version upgrade available
                asset = None
                for ext in ('.exe', '.zip'):
                    asset = next((a for a in latest_release.get('assets', [])
                                  if str(a.get('name', '')).lower().endswith(ext)
                                  and not str(a.get('name', '')).lower().startswith('patch_')), None)
                    if asset:
                        break
                if asset is None:
                    asset = next((a for a in latest_release.get('assets', [])
                                  if not str(a.get('name', '')).lower().endswith('.sha256')
                                  and not str(a.get('name', '')).lower().startswith('patch_')), None)
                if asset:
                    download_url = asset.get('browser_download_url', '')
                    changelog = latest_release.get('body', '') or ''
                    self.update_available.emit(latest_version, download_url, changelog)
                    return

            # Same version — check for patch ZIPs in current release
            applied = _applied_patches()
            for asset in latest_release.get('assets', []):
                name = str(asset.get('name', ''))
                if name.startswith('patch_') and name.endswith('.zip') and name not in applied:
                    self.patch_available.emit(name, asset.get('browser_download_url', ''))
                    return

            self.no_update.emit()

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

    def __init__(self, download_url, is_patch=False):
        super().__init__()
        self.download_url = download_url
        self.is_patch = is_patch
        self.running = True

    def run(self):
        try:
            temp_dir = tempfile.gettempdir()
            filename = "NITROTOOLS_PATCH.zip" if self.is_patch else "NITROTOOLS_UPDATE.exe"
            download_path = os.path.join(temp_dir, filename)

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
        self._pending_patch_name = None

    def check_for_updates(self):
        """Check for updates and patches in background."""
        self._checker = UpdateCheckThread(self.current_version, self.repo_api_url)
        self._checker.update_available.connect(self._on_update_available)
        self._checker.patch_available.connect(self._on_patch_available)
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

    def _on_patch_available(self, patch_name, url):
        """A patch ZIP is available — apply silently without asking."""
        self._pending_patch_name = patch_name
        self.parent_window.show_status_message(f"Patch available: {patch_name} — downloading...")
        self._downloader = UpdateDownloadThread(url, is_patch=True)
        self._downloader.progress.connect(self._on_download_progress)
        self._downloader.completed.connect(self._on_patch_complete)
        self._downloader.failed.connect(self._on_download_failed)
        self._downloader.start()

    def _on_patch_complete(self, zip_path):
        """Extract patch ZIP to NitroTools user dir and restart."""
        try:
            os.makedirs(PATCH_DIR, exist_ok=True)
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(PATCH_DIR)
            if self._pending_patch_name:
                _mark_patch_applied(self._pending_patch_name)
            self.parent_window.show_status_message("Patch applied! Restarting...")
            QTimer.singleShot(1000, self._restart_app)
        except Exception as e:
            self.parent_window.show_status_message(f"Patch failed: {e}")

    def _restart_app(self):
        subprocess.Popen([sys.executable] + sys.argv,
                         creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW)
        QApplication.quit()

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
        """Run the downloaded installer silently, then quit so it can replace files."""
        try:
            name = os.path.basename(update_path).lower()
            if name.endswith('_setup.exe') or 'setup' in name:
                # Inno Setup installer: run silently
                subprocess.Popen(
                    [update_path, '/SILENT', '/NORESTART', '/CLOSEAPPLICATIONS'],
                    creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW,
                    close_fds=True
                )
            else:
                # Legacy: replace EXE via batch
                current_exe = sys.executable
                bat_path = os.path.join(tempfile.gettempdir(), "nitro_update.bat")
                with open(bat_path, "w") as bat:
                    bat.write('@echo off\n')
                    bat.write('timeout /t 2 /nobreak >nul\n')
                    bat.write(f'move /Y "{update_path}" "{current_exe}" >nul\n')
                    bat.write(f'start "" "{current_exe}"\n')
                    bat.write('del "%~f0"\n')
                subprocess.Popen(
                    ['cmd', '/c', bat_path],
                    creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS,
                    close_fds=True
                )

            self.parent_window.show_status_message("Installing update...")
            QTimer.singleShot(1500, QApplication.quit)

        except Exception as e:
            QMessageBox.critical(
                self.parent_window,
                "Install Failed",
                f"Could not install update:\n{e}\n\n"
                f"Downloaded file: {update_path}\n"
                "Please run it manually."
            )
            self.parent_window.show_status_message("Update install failed.")
