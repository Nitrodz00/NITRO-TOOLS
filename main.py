import ctypes
import sys
from src.ui_functions import Window, QtWidgets
from src.update import UpdateWindow, CheckUpdateThread
from PyQt5 import QtCore, QtGui
from os import environ

APP_NAME = "NITROTOOLS PUBG MOBILE"
APP_VERSION = "v2.1.0"
FULL_APP_NAME = f"{APP_NAME} {APP_VERSION}"
ctypes.windll.kernel32.SetConsoleTitleW(FULL_APP_NAME)

NITRO_STYLESHEET = """
QMainWindow, QWidget {
    background-color: transparent;
    color: #e0e0e0;
    font-family: 'Agency FB', 'Segoe UI', sans-serif;
}
#PagesFrame {
    background-color: rgba(15, 0, 30, 0.4);
    border-left: 1px solid #3d007a;
}
#PagesFrame QPushButton {
    background-color: transparent;
    border: none;
    border-bottom: 2px solid rgba(138, 43, 226, 0.2);
    color: #9e9e9e;
    font-size: 18px;
    font-weight: 800;
}
#PagesFrame QPushButton:hover {
    color: #ffffff;
    background-color: rgba(255, 0, 255, 0.1);
}
#PagesFrame QPushButton:checked {
    color: #00ffca;
    background-color: rgba(0, 255, 202, 0.1);
    border-bottom: 3px solid #00ffca;
}
QFrame#MonitorFrame {
    background-color: rgba(10, 0, 25, 0.85);
    border: 1px solid #4d0099;
    border-radius: 6px;
    padding: 2px;
}
#appname_label {
    color: #ffffff;
    font-size: 28px;
    font-weight: 900;
    letter-spacing: 2px;
}
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1a0033, stop:1 #2d004d);
    border: 1px solid #5e35b1;
    border-radius: 6px;
    color: #ede7f6;
    font-weight: 800;
    padding: 8px 15px;
}
QPushButton:hover {
    border: 1px solid #00ffca;
    color: #ffffff;
    background: #311b92;
}
QPushButton:checked {
    background: #00ffca;
    color: #000000;
    border: 1px solid #ffffff;
}
QPushButton#forceclosegl_other_btn {
    background: rgba(255, 0, 0, 0.2);
    border: 1px solid #ff0000;
}
QPushButton#forceclosegl_other_btn:hover {
    background: rgba(255, 0, 0, 0.4);
}
QStackedWidget {
    background: transparent;
}
#about_label_text {
    line-height: 1.6;
}
"""


GITHUB_REPO_API = "https://api.github.com/repos/Nitrodz00/NITRO-TOOLS/releases/latest"

# Global references kept alive
_main_window = None
_update_window = None
_update_checker = None
_single_instance_lock = None


def on_update_available(latest_version, download_url, asset_name):
    global _update_window
    _update_window = UpdateWindow(latest_version, download_url, asset_name)
    _update_window.window_closed.connect(run_application)
    _update_window.show()


def run_application():
    global _main_window
    _main_window = Window(APP_NAME, APP_VERSION)
    _main_window.show()
    return _main_window


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
    
    # --- PRO SINGLE INSTANCE CHECK ---
    _single_instance_lock = QtCore.QSharedMemory("NITROTOOLS_UNIQUE_INSTANCE_ID")
    if not _single_instance_lock.create(1):
        sys.exit(0)
    
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

    def _on_about_to_quit():
        global _main_window
        if _main_window is not None:
            try:
                _main_window._stop_background_threads()
            except Exception:
                pass

    app.aboutToQuit.connect(_on_about_to_quit)

    check_updates_silently()
    sys.exit(app.exec_())
