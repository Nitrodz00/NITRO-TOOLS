import sys
import os
import re
import zipfile
import tempfile
import subprocess
from PyQt5.QtCore import QThread, pyqtSignal, QSize, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout,
                              QHBoxLayout, QWidget, QPushButton, QProgressBar,
                              QTextEdit)
from . import resource_path
import requests


class DownloadThread(QThread):
    download_progress = pyqtSignal(int)
    download_complete = pyqtSignal(str)   # emits the final path
    download_failed = pyqtSignal(str)

    def __init__(self, url, filename):
        super().__init__()
        self.url = url
        self.filename = filename

    def run(self):
        try:
            # Always download to the system TEMP folder to avoid Permission Denied
            # (the running EXE is locked; writing to Temp side-steps that)
            temp_dir = tempfile.gettempdir()
            base_name, ext = os.path.splitext(os.path.basename(self.filename))
            if not ext:
                ext = '.tmp'
            download_path = os.path.join(temp_dir, f"{base_name}_NEW{ext}")

            response = requests.get(self.url, stream=True, timeout=60)
            if response.status_code == 200:
                total_size = int(response.headers.get("content-length", 0))
                bytes_downloaded = 0
                with open(download_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            bytes_downloaded += len(chunk)
                            if total_size:
                                progress = int((bytes_downloaded / total_size) * 100)
                                self.download_progress.emit(progress)

                self.download_progress.emit(100)
                self.download_complete.emit(download_path)
            else:
                self.download_failed.emit(f"Download failed: HTTP {response.status_code}")
        except requests.exceptions.ConnectionError:
            self.download_failed.emit("No internet connection.")
        except requests.exceptions.Timeout:
            self.download_failed.emit("Download timed out. Try again.")
        except PermissionError as e:
            self.download_failed.emit(f"Permission error: {e}")
        except Exception as e:
            self.download_failed.emit(str(e))


def _clean_changelog(raw: str) -> str:
    """Remove GitHub auto-generated markdown junk and return clean text."""
    if not raw or not raw.strip():
        return "No changelog provided for this version."

    # Remove "**Full Changelog**: https://..." auto-generated line
    cleaned = re.sub(r'\*{0,2}Full Changelog\*{0,2}:?\s*https?://\S+', '', raw)

    # Remove markdown bold (**text**)
    cleaned = re.sub(r'\*{2}(.+?)\*{2}', r'\1', cleaned)

    # Remove markdown italic (*text*)
    cleaned = re.sub(r'\*(.+?)\*', r'\1', cleaned)

    # Remove markdown headers (## Title)
    cleaned = re.sub(r'^#{1,6}\s+', '', cleaned, flags=re.MULTILINE)

    # Strip extra blank lines
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned).strip()

    if not cleaned:
        return "No changelog details provided."
    return cleaned


class CheckUpdateThread(QThread):
    """
    Checks GitHub Releases API in the background.
    - update_available: newer version found → show dialog
    - no_update: already on latest
    - check_failed: no internet / API error → app opens normally
    """
    update_available = pyqtSignal(str, str, str, str, str)  # ver, url, name, size, changelog
    no_update = pyqtSignal()
    check_failed = pyqtSignal()

    def __init__(self, current_version: str, repo_url: str):
        super().__init__()
        self.current_version = current_version
        self.repo_url = repo_url

    @staticmethod
    def _normalize(v: str) -> str:
        return v.strip().lower().lstrip("v") if v else ""

    def run(self):
        try:
            resp = requests.get(self.repo_url, timeout=6)
            if resp.status_code != 200:
                self.check_failed.emit()
                return

            data = resp.json()
            latest_ver = data.get("tag_name", "")
            raw_changelog = data.get("body", "")
            assets = data.get("assets", [])

            cur = self._normalize(self.current_version)
            lat = self._normalize(latest_ver)

            if latest_ver and lat != cur and assets:
                # Prefer in-place patch assets (.zip) if present, otherwise fall back to first asset
                asset = next((a for a in assets if str(a.get('name', '')).lower().endswith('.zip')), None)
                if asset is None:
                    asset = assets[0]

                size_mb = round(asset.get("size", 0) / (1024 * 1024), 2)
                changelog = _clean_changelog(raw_changelog)
                self.update_available.emit(
                    latest_ver,
                    asset.get("browser_download_url", ""),
                    asset.get("name", ""),
                    f"{size_mb} MB",
                    changelog
                )
            else:
                self.no_update.emit()
        except Exception:
            self.check_failed.emit()


class UpdateWindow(QMainWindow):
    """Shown only when an update is available."""

    window_closed = pyqtSignal()

    def __init__(self, latest_version, download_url, asset_name, size, changelog):
        super().__init__()
        self.latest_version = latest_version
        self.download_url = download_url
        self.asset_name = asset_name
        self.size = size
        self.changelog = changelog
        self.download_thread = None
        self._downloaded_path = None

        icon = QIcon()
        icon.addFile(resource_path(r"assets\icons\logo.ico"), QSize(), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)
        self.setWindowTitle("NITROTOOLS — Update Available")
        self.setFixedSize(520, 500)

        # Center on screen
        screen_geo = QApplication.desktop().screenGeometry()
        self.move(
            (screen_geo.width() - self.width()) // 2,
            (screen_geo.height() - self.height()) // 2
        )

        # --- Widgets ---
        self.title_label = QLabel(f"🚀  New Version Available: <b>{latest_version}</b>")
        self.title_label.setStyleSheet("font-size: 16px; color: #ff00ff; padding-top: 8px;")

        self.sub_label = QLabel("📋  What's new in this version:")
        self.sub_label.setStyleSheet("color: #cccccc; font-weight: bold; margin-top: 6px;")

        self.changelog_box = QTextEdit()
        self.changelog_box.setReadOnly(True)
        self.changelog_box.setPlainText(self.changelog)
        self.changelog_box.setStyleSheet(
            "background: #0d001a; color: #00ffca; border: 1px solid #4d0099;"
            "border-radius: 6px; padding: 8px; font-size: 12px;"
        )

        self.size_label = QLabel(f"📦  Size: {self.size}")
        self.size_label.setStyleSheet("color: #aaaaaa; font-weight: bold;")

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #ffff00; font-size: 11px;")
        self.status_label.setVisible(False)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")
        self.progress_bar.setStyleSheet(
            "QProgressBar { border: 1px solid #7c00f0; border-radius: 5px; height: 18px; }"
            "QProgressBar::chunk { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            "stop:0 #ff00ff, stop:1 #00ffca); }"
        )

        self.update_btn = QPushButton("⬇  Download & Apply Update")
        self.update_btn.setFixedHeight(48)
        self.update_btn.setStyleSheet(
            "background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #cc00cc,stop:1 #ff00ff);"
            "color: white; font-weight: 900; border-radius: 6px; font-size: 13px;"
        )

        self.skip_btn = QPushButton("Skip — Open Tool")
        self.skip_btn.setFixedHeight(48)
        self.skip_btn.setStyleSheet(
            "background: transparent; border: 1px solid #555; color: #999;"
            "border-radius: 6px; font-size: 12px;"
        )

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        btn_layout.addWidget(self.update_btn)
        btn_layout.addWidget(self.skip_btn)

        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.addWidget(self.title_label)
        layout.addWidget(self.sub_label)
        layout.addWidget(self.changelog_box)
        layout.addWidget(self.size_label)
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)
        layout.addLayout(btn_layout)

        container = QWidget()
        container.setStyleSheet("background-color: #0b001a;")
        container.setLayout(layout)
        self.setCentralWidget(container)

        # If the asset is a zip patch, change label to indicate in-place patch
        try:
            if str(self.asset_name).lower().endswith('.zip'):
                self.update_btn.setText("⬇  Apply Patch (In-Place)")
        except Exception:
            pass

        self.update_btn.clicked.connect(self.start_download)
        self.skip_btn.clicked.connect(self.skip_update)

    def start_download(self):
        self.update_btn.setEnabled(False)
        self.skip_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.status_label.setVisible(True)
        self.status_label.setText("⬇  Connecting to server...")
        self.title_label.setText("⬇  Downloading update...")

        self.download_thread = DownloadThread(self.download_url, self.asset_name)
        self.download_thread.download_progress.connect(self._on_progress)
        self.download_thread.download_complete.connect(self._on_complete)
        self.download_thread.download_failed.connect(self._on_failed)
        self.download_thread.start()

    def _on_progress(self, pct: int):
        self.progress_bar.setValue(pct)
        self.status_label.setText(f"Downloading... {pct}%")

    def _on_complete(self, path: str):
        """Download succeeded. Launch the new EXE using a batch script so the
        current process can exit fully before the installer/new EXE starts."""
        # File integrity check
        try:
            downloaded_size = os.path.getsize(path)
            expected_size_mb = float(self.size.split()[0])
            expected_size = expected_size_mb * 1024 * 1024
            if abs(downloaded_size - expected_size) > 1024:  # Allow 1KB tolerance
                self._on_failed(f"File integrity check failed. Expected {expected_size_mb}MB, got {downloaded_size / (1024*1024):.2f}MB.")
                return
        except Exception as e:
            self._on_failed(f"Integrity check error: {e}")
            return

        self._downloaded_path = path
        self.progress_bar.setValue(100)

        # If this is a zip patch, apply it in-place into user data directory
        if str(path).lower().endswith('.zip'):
            self._apply_patch_zip(path)
            return

        # Otherwise, assume an executable update (legacy behavior): replace current EXE
        self.title_label.setText("✅  Download complete! Launching new version...")
        self.status_label.setText("Starting new version. This window will close.")

        bat_path = os.path.join(tempfile.gettempdir(), "nitro_update_launcher.bat")
        current_exe = sys.executable
        try:
            with open(bat_path, "w") as bat:
                bat.write('@echo off\n')
                bat.write('set count=0\n')
                bat.write(':wait_loop\n')
                bat.write('timeout /t 1 /nobreak >nul\n') # wait 1 sec
                bat.write(f'del /Q "{current_exe}" >nul 2>&1\n')
                bat.write(f'if exist "{current_exe}" (\n')
                bat.write('  set /a count+=1\n')
                bat.write('  if %count% LSS 10 goto wait_loop\n') # try 10 times
                bat.write(')\n')
                bat.write(f'move /Y "{path}" "{current_exe}" >nul\n')
                bat.write(f'start "" "{current_exe}"\n')
                bat.write('del "%~f0"\n')   # self-delete the bat after launch

            subprocess.Popen(['cmd', '/c', bat_path],
                             creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS,
                             close_fds=True)
        except Exception:
            # Fallback: try os.startfile
            try:
                os.startfile(path)
            except Exception:
                pass

        QTimer.singleShot(1800, sys.exit)

    def _apply_patch_zip(self, zip_path: str):
        """Extract patch zip into user data dir (safe extraction) and restart app."""
        try:
            local_appdata = os.getenv('LOCALAPPDATA') or tempfile.gettempdir()
            user_data_dir = os.path.join(local_appdata, 'NitroTools')
            os.makedirs(user_data_dir, exist_ok=True)

            with zipfile.ZipFile(zip_path, 'r') as z:
                for member in z.infolist():
                    member_name = member.filename
                    # Skip absolute paths and attempts to traverse directories
                    dest_path = os.path.join(user_data_dir, member_name)
                    abs_dest = os.path.abspath(dest_path)
                    abs_user = os.path.abspath(user_data_dir)
                    if not abs_dest.startswith(abs_user + os.sep) and abs_dest != abs_user:
                        continue

                    if member.is_dir():
                        os.makedirs(abs_dest, exist_ok=True)
                        continue

                    parent = os.path.dirname(abs_dest)
                    if parent and not os.path.isdir(parent):
                        os.makedirs(parent, exist_ok=True)

                    with z.open(member) as source, open(abs_dest, 'wb') as target:
                        data = source.read()
                        target.write(data)

            self.title_label.setText("✅  Patch applied successfully")
            self.status_label.setText("Restarting application to apply changes...")

            try:
                subprocess.Popen([sys.executable] + sys.argv,
                                 creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS,
                                 close_fds=True)
            except Exception:
                try:
                    os.startfile(sys.executable)
                except Exception:
                    pass

            QTimer.singleShot(1200, sys.exit)
        except Exception as e:
            self._on_failed(f"Patch apply failed: {e}")

    def _on_failed(self, msg: str):
        self.title_label.setText(f"❌  Failed: {msg}")
        self.title_label.setStyleSheet("font-size: 13px; color: #ff4d4d; padding-top: 8px;")
        self.status_label.setVisible(False)
        self.update_btn.setEnabled(True)
        self.skip_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

    def skip_update(self):
        self.close()

    def closeEvent(self, event):
        self.window_closed.emit()
        event.accept()
