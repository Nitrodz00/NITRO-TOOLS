import sys
import os
import zipfile
from PyQt5.QtCore import QThread, pyqtSignal, QSize, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QProgressBar
from . import resource_path
import requests


class DownloadThread(QThread):
    download_progress = pyqtSignal(int)
    download_complete = pyqtSignal()
    download_failed = pyqtSignal(str)

    def __init__(self, url, filename):
        super().__init__()
        self.url = url
        self.filename = filename

    def run(self):
        try:
            response = requests.get(self.url, stream=True)
            if response.status_code == 200:
                total_size = int(response.headers.get("content-length", 0))
                bytes_downloaded = 0
                with open(self.filename, "wb") as file:
                    for chunk in response.iter_content(chunk_size=4096):
                        if chunk:
                            file.write(chunk)
                            bytes_downloaded += len(chunk)
                            if total_size:
                                progress = int((bytes_downloaded / total_size) * 100)
                                self.download_progress.emit(progress)
                if self.filename.endswith(".exe"):
                    os.startfile(self.filename, 'runas')
                    self.download_complete.emit()
                    return

                try:
                    with zipfile.ZipFile(self.filename, 'r') as zip_ref:
                        exe_file = next((name for name in zip_ref.namelist() if name.endswith(".exe")), None)
                        if exe_file:
                            zip_ref.extractall()
                            os.startfile(exe_file, 'runas')
                            self.download_complete.emit()
                        else:
                            self.download_failed.emit("No EXE found in the update file.")
                except zipfile.BadZipFile:
                    self.download_failed.emit("Downloaded file is corrupted or not a valid zip.")
            else:
                self.download_failed.emit(f"Download failed: HTTP {response.status_code}")
        except Exception as e:
            self.download_failed.emit(str(e))


class CheckUpdateThread(QThread):
    """
    Checks GitHub Releases API in the background (requires internet).
    - On success: either shows update dialog or opens the main app.
    - On failure (timeout, DNS, 404, no assets): emits check_failed or no_update; app still opens.
    """
    update_available = pyqtSignal(str, str, str, str, str)   # latest_version, download_url, asset_name, size, changelog
    no_update = pyqtSignal()
    check_failed = pyqtSignal()

    def __init__(self, current_version, repo_url):
        super().__init__()
        self.current_version = current_version
        self.repo_url = repo_url

    @staticmethod
    def _normalize_version(v):
        if not v:
            return ""
        return v.strip().lower().lstrip("v")

    def run(self):
        try:
            response = requests.get(self.repo_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                latest_version = data.get("tag_name", "")
                changelog = data.get("body", "No changelog provided.")
                assets = data.get("assets", [])
                cur = self._normalize_version(self.current_version)
                lat = self._normalize_version(latest_version)
                if latest_version and lat != cur and assets:
                    asset = assets[0]
                    size_mb = round(asset.get("size", 0) / (1024 * 1024), 2)
                    self.update_available.emit(
                        latest_version,
                        asset.get("browser_download_url", ""),
                        asset.get("name", ""),
                        f"{size_mb} MB",
                        changelog
                    )
                else:
                    self.no_update.emit()
            else:
                self.check_failed.emit()
        except Exception:
            self.check_failed.emit()


class UpdateWindow(QMainWindow):
    """Shown only when an update is actually available."""

    window_closed = pyqtSignal()

    def __init__(self, latest_version, download_url, asset_name, size, changelog):
        super().__init__()
        self.latest_version = latest_version
        self.download_url = download_url
        self.asset_name = asset_name
        self.size = size
        self.changelog = changelog
        self.download_thread = None

        icon = QIcon()
        icon.addFile(resource_path(r"assets\icons\logo.ico"), QSize(), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)
        self.setWindowTitle("NITROTOOLS — Update Available")
        self.setFixedSize(500, 480) # Increased for changelog

        # Center on screen
        screen_geometry = QApplication.desktop().screenGeometry()
        self.move(
            (screen_geometry.width() - self.width()) // 2,
            (screen_geometry.height() - self.height()) // 2
        )

        self.label = QLabel(f"🚀 New version available: <b>{latest_version}</b>")
        self.label.setStyleSheet("font-size: 16px; color: #ff00ff; padding-top: 10px;")

        self.sublabel = QLabel("What's New in this version:")
        self.sublabel.setStyleSheet("color: #ffffff; font-weight: bold; margin-top: 5px;")

        from PyQt5.QtWidgets import QTextEdit
        self.changelog_box = QTextEdit()
        self.changelog_box.setReadOnly(True)
        self.changelog_box.setPlainText(self.changelog)
        self.changelog_box.setStyleSheet("background: #111; color: #00ffca; border: 1px solid #333; border-radius: 4px; padding: 5px;")

        self.size_label = QLabel(f"📦 Size: {self.size}")
        self.size_label.setStyleSheet("color: #aaaaaa; font-weight: bold;")

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet(
            "QProgressBar { border: 1px solid #ff00ff; border-radius: 4px; height: 16px; }"
            "QProgressBar::chunk { background-color: #ff00ff; }"
        )

        self.update_btn = QPushButton("⬇ Download and Apply Update")
        self.update_btn.setFixedHeight(45)
        self.update_btn.setStyleSheet("background: #ff00ff; color: white; font-weight: 800; border-radius: 5px;")
        
        self.skip_btn = QPushButton("Skip — Open Tool")
        self.skip_btn.setFixedHeight(45)
        self.skip_btn.setStyleSheet("background: transparent; border: 1px solid #aaa; color: #aaa;")

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.addWidget(self.update_btn)
        btn_layout.addWidget(self.skip_btn)

        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.addWidget(self.label)
        layout.addWidget(self.sublabel)
        layout.addWidget(self.changelog_box)
        layout.addWidget(self.size_label)
        layout.addWidget(self.progress_bar)
        layout.addLayout(btn_layout)

        widget = QWidget()
        widget.setStyleSheet("background-color: #0b001a;")
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.update_btn.clicked.connect(self.start_download)
        self.skip_btn.clicked.connect(self.skip_update)

    def start_download(self):
        self.update_btn.setEnabled(False)
        self.skip_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.label.setText("⬇ Downloading update...")

        self.download_thread = DownloadThread(self.download_url, self.asset_name)
        self.download_thread.download_progress.connect(self.progress_bar.setValue)
        self.download_thread.download_complete.connect(self.on_complete)
        self.download_thread.download_failed.connect(self.on_failed)
        self.download_thread.start()

    def on_complete(self):
        self.label.setText("✅ Update downloaded! Restarting...")
        # Start the updater/installer if necessary, but here we just restart
        QTimer.singleShot(1500, sys.exit)

    def on_failed(self, msg):
        self.label.setText(f"❌ Failed: {msg}")
        self.update_btn.setEnabled(True)
        self.skip_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

    def skip_update(self):
        self.close()
        self.window_closed.emit()

    def closeEvent(self, event):
        self.window_closed.emit()
        event.accept()
