import ctypes
import sys
from src.ui_functions import Window, QtWidgets
from src.update import UpdateWindow, CheckUpdateThread
from PyQt5 import QtCore, QtGui
from os import environ

APP_NAME = "NITROTOOLS PUBG MOBILE"
APP_VERSION = "v2.0.0"
FULL_APP_NAME = f"{APP_NAME} {APP_VERSION}"
ctypes.windll.kernel32.SetConsoleTitleW(FULL_APP_NAME)

NITRO_STYLESHEET = """
QMainWindow, QWidget {
    background-color: #0d0d0d;
    color: #e0e0e0;
    font-family: 'Agency FB', 'Segoe UI', Arial;
}
QLabel {
    color: #e0e0e0;
    background: transparent;
}
QPushButton {
    background-color: rgba(25, 25, 25, 0.85);
    border: 2px solid #555;
    border-radius: 6px;
    color: #cc0000;
    font-weight: bold;
    font-size: 12px;
    padding: 4px 8px;
    min-height: 28px;
}
QPushButton:hover {
    background-color: rgba(180, 0, 0, 0.25);
    border: 2px solid #ff1744;
    color: #ff5252;
}
QPushButton:checked, QPushButton:pressed {
    background-color: rgba(180, 0, 0, 0.75);
    border: 2px solid #ff1744;
    color: #ffffff;
}
QPushButton:disabled {
    background-color: rgba(20, 20, 20, 0.5);
    border: 2px solid #333;
    color: #555;
}
QComboBox {
    background-color: #1a1a1a;
    border: 1px solid #cc0000;
    border-radius: 4px;
    color: #e0e0e0;
    padding: 4px 8px;
    min-height: 28px;
}
QComboBox::drop-down {
    border: none;
    background: #cc0000;
    width: 20px;
}
QComboBox QAbstractItemView {
    background-color: #1a1a1a;
    border: 1px solid #cc0000;
    color: #e0e0e0;
    selection-background-color: #cc0000;
}
QScrollBar:vertical {
    background: #1a1a1a;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #cc0000;
    border-radius: 4px;
}
QTextBrowser {
    background-color: #1a1a1a;
    border: 1px solid #333;
    color: #e0e0e0;
}
QMenu {
    background-color: #1a1a1a;
    border: 1px solid #cc0000;
    color: #e0e0e0;
}
QMenu::item:selected {
    background-color: #cc0000;
}
"""


def run_application():
    ui = Window(APP_NAME, APP_VERSION)
    ui.show()
    return ui


GITHUB_REPO_API = "https://api.github.com/repos/Nitrodz00/NITRO-TOOLS/releases/latest"

# Global references kept alive
_main_window = None
_update_window = None
_update_checker = None


def run_application():
    global _main_window
    _main_window = Window(APP_NAME, APP_VERSION)
    _main_window.show()
    return _main_window


def on_update_available(latest_version, download_url, asset_name):
    global _update_window
    _update_window = UpdateWindow(latest_version, download_url, asset_name)
    _update_window.window_closed.connect(run_application)
    _update_window.show()


def check_updates_silently():
    global _update_checker
    _update_checker = CheckUpdateThread(APP_VERSION, GITHUB_REPO_API)
    _update_checker.update_available.connect(on_update_available)
    _update_checker.no_update.connect(run_application)
    _update_checker.check_failed.connect(run_application)
    _update_checker.start()


if __name__ == "__main__":
    environ["QT_DEVICE_PIXEL_RATIO"] = "0"
    environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    environ["QT_SCREEN_SCALE_FACTORS"] = "1"
    environ["QT_SCALE_FACTOR"] = "1"

    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(NITRO_STYLESHEET)

    icon_path = "assets/icons/logo.ico"
    if hasattr(sys, '_MEIPASS'):
        import os
        icon_path = os.path.join(sys._MEIPASS, 'assets', 'icons', 'logo.ico')
    
    app_icon = QtGui.QIcon(icon_path)
    app.setWindowIcon(app_icon)
    
    # Force taskbar icon refresh for Windows
    try:
        myappid = 'nitrodz.nitrotools.gaming.1.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception:
        pass

    check_updates_silently()
    sys.exit(app.exec_())
