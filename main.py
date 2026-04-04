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
    background-color: #090310;
    color: #f2e6ff;
    font-family: 'Segoe UI', Arial;
}
QLabel {
    color: #f2e6ff;
    background: transparent;
    font-weight: bold;
}
QPushButton {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(80, 0, 120, 0.8), stop:1 rgba(180, 0, 160, 0.8));
    border: 2px solid #a600ff;
    border-radius: 8px;
    color: #ffffff;
    font-weight: bold;
    font-size: 13px;
    padding: 6px 10px;
    min-height: 28px;
}
QPushButton:hover {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(120, 0, 180, 0.9), stop:1 rgba(220, 0, 190, 0.9));
    border: 2px solid #ff00ff;
    color: #ffffff;
}
QPushButton:checked, QPushButton:pressed {
    background-color: #ff00cc;
    border: 2px solid #ffffff;
    color: #ffffff;
}
QPushButton:disabled {
    background-color: rgba(30, 10, 40, 0.5);
    border: 2px solid #4a1060;
    color: #9955b3;
}
QComboBox {
    background-color: #12051f;
    border: 1px solid #ff00cc;
    border-radius: 5px;
    color: #ffffff;
    padding: 4px 8px;
    min-height: 28px;
}
QComboBox::drop-down {
    border: none;
    background: #a600ff;
    width: 20px;
}
QComboBox QAbstractItemView {
    background-color: #12051f;
    border: 1px solid #ff00cc;
    color: #f2e6ff;
    selection-background-color: #ff00cc;
}
QScrollBar:vertical {
    background: #090310;
    width: 10px;
    border-radius: 5px;
}
QScrollBar::handle:vertical {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #a600ff, stop:1 #ff00cc);
    border-radius: 5px;
}
QTextBrowser {
    background-color: #12051f;
    border: 1px solid #a600ff;
    color: #f2e6ff;
    border-radius: 5px;
}
QMenu {
    background-color: #12051f;
    border: 1px solid #ff00cc;
    color: #f2e6ff;
}
QMenu::item:selected {
    background-color: #ff00cc;
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
