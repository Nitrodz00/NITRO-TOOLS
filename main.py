import ctypes
import sys

# PyInstaller onefile: adbutils imports pkg_resources before graph analysis sees it — force bundle
import pkg_resources  # noqa: F401
import setuptools  # noqa: F401

from src.ui_functions import Window, QtWidgets
from src.update import UpdateWindow, CheckUpdateThread
from PyQt5 import QtCore, QtGui
from os import environ

APP_NAME = "NITROTOOLS PUBG MOBILE"
APP_VERSION = "v2.2.5"
FULL_APP_NAME = f"{APP_NAME} {APP_VERSION}"
ctypes.windll.kernel32.SetConsoleTitleW(FULL_APP_NAME)

NITRO_STYLESHEET = """
QMainWindow, QWidget {
    background-color: transparent;
    color: #f0f0ff;
    font-family: 'Segoe UI Semibold', 'Agency FB', sans-serif;
}

/* Base Window - Deep Cosmic Gradient */
#centralwidget {
    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, 
        stop:0 #0d0020, stop:0.5 #1e003c, stop:1 #001220);
    border: 1px solid #4d0099;
}

/* Make background images subtle and atmospheric */
#appbackground, #gfx_page_background, #other_page_background, #label_8 {
    background-color: rgba(20, 0, 40, 0.4); /* Glass overlay */
    border: none;
}

/* Sidebar - Elegant and Slim */
#PagesFrame {
    background-color: rgba(0, 0, 0, 0.3);
    border-left: 1px solid rgba(204, 0, 255, 0.3);
}

#PagesFrame QPushButton {
    background-color: transparent;
    border: none;
    border-right: 3px solid transparent;
    color: #b0b0cc;
    font-size: 14pt;
    font-weight: 800;
    padding: 15px;
    text-transform: uppercase;
}

#PagesFrame QPushButton:hover {
    color: #ffffff;
    background-color: rgba(204, 0, 255, 0.1);
    border-right: 3px solid #ff00ff;
}

#PagesFrame QPushButton:checked {
    color: #00ffca;
    background-color: rgba(0, 255, 202, 0.1);
    border-right: 4px solid #00ffca;
}

/* Header Dashboard Stats */
QFrame#MonitorFrame {
    background-color: rgba(30, 0, 60, 0.5);
    border: 1px solid #7c00f0;
    border-radius: 12px;
}

#appname_label {
    color: #ffffff;
    font-size: 18pt;
    font-weight: 900;
    letter-spacing: 2px;
    background: transparent;
}

/* Header Text Labels Padding */
QLabel#fps_label, QLabel#cpu_label, QLabel#gpu_label, QLabel#ram_label {
    padding-bottom: 2px;
}

/* High-Performance Modern Buttons - Harmonious Palette */
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
        stop:0 #5c27fe, stop:1 #c165ff);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 6px;
    color: #ffffff;
    font-weight: 700;
    font-size: 11pt;
    padding: 8px;
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
        stop:0 #4a1edb, stop:1 #af4dff);
    border: 1px solid #00f0ff;
}

QPushButton:checked {
    background: #00ffca;
    color: #000000;
    border: 2px solid #ffffff;
}

QPushButton:disabled {
    background: #101020;
    color: #3b3b5c;
    border: 1px solid #1c1c3c;
}

/* Specialized Force Close Button */
QPushButton#forceclosegl_other_btn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff0000, stop:1 #8b0000);
}

/* Dropdowns & Inputs */
QComboBox {
    background-color: #0d0020;
    border: 1px solid #7c00f0;
    border-radius: 6px;
    padding: 8px;
    color: #00ffca;
    font-weight: bold;
}

QComboBox::drop-down {
    border-left: 1px solid #7c00f0;
    width: 25px;
}

QComboBox QAbstractItemView {
    background-color: #0d0020;
    border: 1px solid #7c00f0;
    selection-background-color: #7c00f0;
}

/* Labels and Content */
QLabel {
    background: transparent;
    color: #ffffff;
}

#appstatus_text_lable {
    color: #00ffca;
    font-weight: bold;
}
"""


# Update check: GET GitHub Releases API (needs internet). If offline, blocked, or no Releases
# published, the app still opens (see CheckUpdateThread). To skip the request entirely:
#   set env NITROTOOLS_SKIP_UPDATE_CHECK=1
GITHUB_REPO_API = "https://api.github.com/repos/Nitrodz00/NITRO-TOOLS/releases/latest"

# Global references kept alive
_main_window = None
_update_window = None
_update_checker = None
_single_instance_lock = None


def on_update_available(latest_version, download_url, asset_name, size, changelog):
    global _update_window
    _update_window = UpdateWindow(latest_version, download_url, asset_name, size, changelog)
    _update_window.window_closed.connect(run_application)
    _update_window.show()


def run_application():
    global _main_window
    _main_window = Window(APP_NAME, APP_VERSION)
    _main_window.show()
    return _main_window


def check_updates_silently():
    global _update_checker
    skip = environ.get("NITROTOOLS_SKIP_UPDATE_CHECK", "").strip().lower()
    if skip in ("1", "true", "yes", "on"):
        run_application()
        return
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

    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    if not is_admin():
        # Re-run the program with admin rights
        try:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        except Exception:
            pass
        sys.exit(0)

    # --- PRO SINGLE INSTANCE LOCK (NATIVE WINDOWS MUTEX) ---
    def check_single_instance():
        try:
            # We create a unique system-wide Mutex
            # If it already exists, Another instance is running
            mutex_name = "Global\\NITROTOOLS_UNIQUE_MUTEX_ID_v2"
            handle = ctypes.windll.kernel32.CreateMutexW(None, False, mutex_name)
            last_error = ctypes.windll.kernel32.GetLastError()
            
            # ERROR_ALREADY_EXISTS = 183
            if last_error == 183:
                # Release the handle if duplicate
                if handle:
                    ctypes.windll.kernel32.CloseHandle(handle)
                return False
            # Hold the reference kept alive by the script
            return handle
        except Exception:
            return True # If something fails, let it run anyway

    _lock_handle = check_single_instance()
    if not _lock_handle:
        sys.exit(0)

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
