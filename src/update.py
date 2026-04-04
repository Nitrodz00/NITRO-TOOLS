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
                    self.download_failed.emit("Downloaded file is corrupted.")
            else:
                self.download_failed.emit(f"Download failed: HTTP {response.status_code}")
        except Exception as e:
            self.download_failed.emit(str(e))


class CheckUpdateThread(QThread):
    """Checks GitHub for updates silently in background."""
    update_available = pyqtSignal(str, str, str)   # latest_version, download_url, asset_name
    no_update = pyqtSignal()
    check_failed = pyqtSignal()

    def __init__(self, current_version, repo_url):
        super().__init__()
        self.current_version = current_version
        self.repo_url = repo_url

    def run(self):
        try:
            response = requests.get(self.repo_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                latest_version = data.get("tag_name", "")
                assets = data.get("assets", [])
                if latest_version and latest_version != self.current_version and assets:
                    asset = assets[0]
                    self.update_available.emit(
                        latest_version,
                        asset.get("browser_download_url", ""),
                        asset.get("name", "")
                    )
                else:
                    self.no_update.emit()
            else:
                self.no_update.emit()
        except Exception:
            self.no_update.emit()


class UpdateWindow(QMainWindow):
    """Shown only when an update is actually available."""

    window_closed = pyqtSignal()

    def __init__(self, latest_version, download_url, asset_name):
        super().__init__()
        self.latest_version = latest_version
        self.download_url = download_url
        self.asset_name = asset_name
        self.download_thread = None

        icon = QIcon()
        icon.addFile(resource_path(r"assets\icons\logo.ico"), QSize(), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)
        self.setWindowTitle("NITROTOOLS — Update Available")
        self.setFixedSize(400, 220)

        # Center on screen
        screen_geometry = QApplication.desktop().screenGeometry()
        self.move(
            (screen_geometry.width() - self.width()) // 2,
            (screen_geometry.height() - self.height()) // 2
        )

        self.label = QLabel(f"🚀 New version available: <b>{latest_version}</b>")
        self.label.setStyleSheet("font-size: 14px; padding: 10px;")

        self.sublabel = QLabel("Do you want to download and install the update now?")
        self.sublabel.setWordWrap(True)
        self.sublabel.setStyleSheet("color: #aaa; padding: 0 10px;")

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet(
            "QProgressBar { border: 1px solid #cc0000; border-radius: 4px; height: 16px; }"
            "QProgressBar::chunk { background-color: #cc0000; }"
        )

        self.update_btn = QPushButton("⬇ Download Update")
        self.update_btn.setFixedHeight(38)
        self.skip_btn = QPushButton("Skip — Open Tool")
        self.skip_btn.setFixedHeight(38)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.update_btn)
        btn_layout.addWidget(self.skip_btn)

        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.addWidget(self.label)
        layout.addWidget(self.sublabel)
        layout.addWidget(self.progress_bar)
        layout.addLayout(btn_layout)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.update_btn.clicked.connect(self.start_download)
        self.skip_btn.clicked.connect(self.skip_update)

    def start_download(self):
        self.update_btn.setEnabled(False)
        self.skip_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.sublabel.setText("Downloading update...")

        self.download_thread = DownloadThread(self.download_url, self.asset_name)
        self.download_thread.download_progress.connect(self.progress_bar.setValue)
        self.download_thread.download_complete.connect(self.on_complete)
        self.download_thread.download_failed.connect(self.on_failed)
        self.download_thread.start()

    def on_complete(self):
        self.sublabel.setText("✅ Update downloaded! Restarting...")
        QTimer.singleShot(1500, sys.exit)

    def on_failed(self, msg):
        self.sublabel.setText(f"❌ Failed: {msg}")
        self.update_btn.setEnabled(True)
        self.skip_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

    def skip_update(self):
        self.close()
        self.window_closed.emit()

    def closeEvent(self, event):
        self.window_closed.emit()
        event.accept()
