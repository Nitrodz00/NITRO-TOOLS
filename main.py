import ctypes
import sys
import os
import tempfile

# PyInstaller onefile: adbutils imports pkg_resources before graph analysis sees it — force bundle
try:
    import pkg_resources
except ImportError:
    pass

# CRITICAL: Fix path issues for both development and packaged environments
def setup_python_path():
    """Setup Python path for proper module imports."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Add current directory to sys.path if not already there
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    # For PyInstaller one-file executable, add the parent directory
    if getattr(sys, 'frozen', False):
        # Running in a PyInstaller bundle
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(sys.executable)
        
        if base_path not in sys.path:
            sys.path.insert(0, base_path)
        
        # CRITICAL: Also add the src directory path for PyInstaller
        src_path = os.path.join(base_path, 'src')
        if os.path.exists(src_path) and src_path not in sys.path:
            sys.path.insert(0, src_path)
    
    # For development, also add src directory
    src_path_dev = os.path.join(current_dir, 'src')
    if os.path.exists(src_path_dev) and src_path_dev not in sys.path:
        sys.path.insert(0, src_path_dev)
    
    # Allow user-data overrides for hot-updates
    try:
        local_appdata = os.getenv('LOCALAPPDATA') or tempfile.gettempdir()
        user_data_dir = os.path.join(local_appdata, 'NitroTools')
        if os.path.isdir(user_data_dir) and user_data_dir not in sys.path:
            sys.path.insert(0, user_data_dir)
    except Exception:
        pass

# Setup paths before importing
setup_python_path()

# Pre-load any patched modules from user data dir so relative imports pick them up
def _load_user_patches():
    import importlib.util
    import glob as _glob
    _patch_dir = os.path.join(os.getenv('LOCALAPPDATA', ''), 'NitroTools')
    _src_dir = os.path.join(_patch_dir, 'src')
    if not os.path.isdir(_src_dir):
        return
    # Load in dependency order: ui_functions MUST be last — it imports from all others.
    # If ui_functions loads before other/gfx/app_functions, it gets the frozen version of those modules.
    _ordered = ['ui', 'app_functions', 'other', 'system', 'gfx',
                'update', 'auto_updater', 'monitor', 'ui_functions']
    _loaded = set()
    for _mod_name in _ordered:
        _path = os.path.join(_src_dir, f'{_mod_name}.py')
        if os.path.isfile(_path):
            try:
                _full = f'src.{_mod_name}'
                _spec = importlib.util.spec_from_file_location(_full, _path)
                _mod = importlib.util.module_from_spec(_spec)
                sys.modules[_full] = _mod
                _spec.loader.exec_module(_mod)
                _loaded.add(_mod_name)
            except Exception:
                pass
    # Auto-discover any additional .py files not in the ordered list
    for _py in _glob.glob(os.path.join(_src_dir, '*.py')):
        _mod_name = os.path.splitext(os.path.basename(_py))[0]
        if _mod_name in _loaded or _mod_name == '__init__':
            continue
        try:
            _full = f'src.{_mod_name}'
            if _full not in sys.modules:
                _spec = importlib.util.spec_from_file_location(_full, _py)
                _mod = importlib.util.module_from_spec(_spec)
                sys.modules[_full] = _mod
                _spec.loader.exec_module(_mod)
        except Exception:
            pass

_load_user_patches()

# Now try imports with error handling - try multiple import methods
import_success = False
import_error = None

try:
    # Method 1: Try importing with src prefix (development)
    from src.ui_functions import Window
    from src.update import UpdateWindow, CheckUpdateThread
    from PyQt5 import QtCore, QtGui, QtWidgets
    import_success = True
except ImportError as e:
    import_error = e
    try:
        # Method 2: Try importing without src prefix (PyInstaller)
        from ui_functions import Window
        from update import UpdateWindow, CheckUpdateThread
        from PyQt5 import QtCore, QtGui, QtWidgets
        import_success = True
    except ImportError as e2:
        import_error = e2

if not import_success:
    print(f"Import Error: {import_error}")
    print("Current Python path:")
    for p in sys.path:
        print(f"  {p}")
    print("Current working directory:", os.getcwd())
    print("Script directory:", os.path.dirname(os.path.abspath(__file__)))
    
    # Show error message in GUI if possible, otherwise exit
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        messagebox.showerror("Import Error", f"Failed to import required modules:\n{import_error}\n\nPlease check the installation.")
        root.destroy()
    except:
        pass  # If even tkinter fails, just exit
    
    sys.exit(1)

from os import environ

APP_NAME = "NITROTOOLS PUBG MOBILE"
APP_VERSION = "v3.1.9"
FULL_APP_NAME = f"{APP_NAME} {APP_VERSION}"
ctypes.windll.kernel32.SetConsoleTitleW(FULL_APP_NAME)

THEMES = {
    "cosmic": {
        "gradient": "qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #0d0020, stop:0.5 #1e003c, stop:1 #001220)",
        "accent": "#ff00ff",
        "secondary": "#00ffca"
    },
    "neon_green": {
        "gradient": "qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #001a00, stop:0.5 #003300, stop:1 #000a00)",
        "accent": "#00ff00",
        "secondary": "#00ffff"
    },
    "red_alert": {
        "gradient": "qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #1a0000, stop:0.5 #330000, stop:1 #0a0000)",
        "accent": "#ff0000",
        "secondary": "#ffaa00"
    }
}

CURRENT_THEME = "cosmic"

def get_stylesheet(theme_name="cosmic"):
    theme = THEMES.get(theme_name, THEMES["cosmic"])
    return """
QMainWindow, QWidget {{
    background-color: transparent;
    color: #f0f0ff;
    font-family: 'Segoe UI Semibold', 'Agency FB', sans-serif;
}}

/* Base Window - {0} Gradient */
#centralwidget {{
    background: {1};
    border: 1px solid {2};
}}

/* Make background images subtle and atmospheric */
#appbackground, #gfx_page_background, #other_page_background, #label_8 {{
    background-color: rgba(20, 0, 40, 0.4); /* Glass overlay */
    border: none;
}}

/* Sidebar - Elegant and Slim */
#PagesFrame {{
    background-color: rgba(0, 0, 0, 0.3);
    border-left: 1px solid rgba(204, 0, 255, 0.3);
}}

#PagesFrame QPushButton {{
    background-color: transparent;
    border: none;
    border-right: 3px solid transparent;
    color: #b0b0cc;
    font-size: 14pt;
    font-weight: 800;
    padding: 15px;
    text-transform: uppercase;
}}

#PagesFrame QPushButton:hover {{
    color: #ffffff;
    background-color: rgba(204, 0, 255, 0.1);
    border-right: 3px solid {2};
}}

#PagesFrame QPushButton:checked {{
    color: {3};
    background-color: rgba(0, 255, 202, 0.1);
    border-right: 4px solid {3};
}}

/* Header Dashboard Stats */
QFrame#MonitorFrame {{
    background-color: rgba(30, 0, 60, 0.5);
    border: 1px solid {2};
    border-radius: 12px;
}}

#appname_label {{
    color: #ffffff;
    font-size: 18pt;
    font-weight: 900;
    letter-spacing: 2px;
    background: transparent;
}}

/* Header Text Labels Padding */
QLabel#fps_label, QLabel#cpu_label, QLabel#gpu_label, QLabel#ram_label {{
    padding-bottom: 2px;
}}

/* High-Performance Modern Buttons - Harmonious Palette */
QPushButton {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
        stop:0 {2}, stop:1 {3});
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 6px;
    color: #ffffff;
    font-weight: 700;
    font-size: 11pt;
    padding: 8px;
}}

QPushButton:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
        stop:0 #4a1edb, stop:1 #af4dff);
    border: 1px solid {3};
}}

QPushButton:checked {{
    background: {3};
    color: #000000;
    border: 2px solid #ffffff;
}}

QPushButton:disabled {{
    background: #101020;
    color: #3b3b5c;
    border: 1px solid #1c1c3c;
}}

/* Specialized Force Close Button */
QPushButton#forceclosegl_other_btn {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff0000, stop:1 #8b0000);
}}

/* Dropdowns & Inputs */
QComboBox {{
    background-color: #0d0020;
    border: 1px solid {2};
    border-radius: 6px;
    padding: 8px;
    color: {3};
    font-weight: bold;
}}

QComboBox::drop-down {{
    border-left: 1px solid {2};
    width: 25px;
}}

QComboBox QAbstractItemView {{
    background-color: #0d0020;
    border: 1px solid {2};
    selection-background-color: {2};
}}

/* Labels and Content */
QLabel {{
    background: transparent;
    color: #ffffff;
}}

#appstatus_text_lable {{
    color: {3};
    font-weight: bold;
}}
""".format(theme_name.title(), theme['gradient'], theme['accent'], theme['secondary'])

NITRO_STYLESHEET = get_stylesheet(CURRENT_THEME)


# Update check: GET GitHub Releases API (needs internet). If offline, blocked, or no Releases
# published, the app still opens (see CheckUpdateThread). To skip the request entirely:
#   set env NITROTOOLS_SKIP_UPDATE_CHECK=1
GITHUB_REPO_API = "https://api.github.com/repos/Nitrodz00/NITRO-TOOLS/releases/latest"

# Global references kept alive
_main_window = None
_update_window = None
_update_checker = None
_single_instance_lock = None


def on_update_available(latest_version, download_url, asset_name, expected_bytes, size, expected_sha, changelog):
    global _update_window
    _update_window = UpdateWindow(latest_version, download_url, asset_name, expected_bytes, size, expected_sha, changelog)
    _update_window.window_closed.connect(run_application)
    _update_window.show()


def run_application():
    global _main_window
    try:
        _main_window = Window(APP_NAME, APP_VERSION)
        _main_window.show()
        return _main_window
    except ImportError as e:
        # Handle missing dependencies gracefully
        msg = f"MISSING DEPENDENCY:\n\n{str(e)}\n\nPlease install required packages:\n1. Run as Administrator\n2. Install dependencies with: pip install -r requirements.txt\n3. Restart the application"
        ctypes.windll.user32.MessageBoxW(0, msg, "NITROTOOLS - Missing Dependencies", 0x30)
        sys.exit(1)
    except Exception as e:
        import traceback
        error_info = traceback.format_exc()
        
        # Check for common errors and provide helpful messages
        error_str = str(e).lower()
        if "access" in error_str or "permission" in error_str:
            msg = f"PERMISSION ERROR:\n\n{str(e)}\n\nSolution:\n1. Right-click NITROTOOLS and 'Run as Administrator'\n2. Check if antivirus is blocking the application\n3. Ensure Windows has proper permissions"
        elif "dll" in error_str or "module" in error_str:
            msg = f"SYSTEM ERROR:\n\n{str(e)}\n\nSolution:\n1. Install Visual C++ Redistributable\n2. Update Windows to latest version\n3. Reinstall the application"
        elif "memory" in error_str or "ram" in error_str:
            msg = f"MEMORY ERROR:\n\n{str(e)}\n\nSolution:\n1. Close other applications\n2. Ensure at least 4GB RAM available\n3. Restart your computer"
        else:
            msg = f"APPLICATION ERROR:\n\n{str(e)}\n\nTechnical details saved to error.log\n\nPlease:\n1. Run as Administrator\n2. Check system requirements\n3. Contact support if issue persists"
        
        # Log the error for debugging
        try:
            import logging
            logging.basicConfig(filename='error.log', level=logging.ERROR)
            logging.error(f"Startup Error: {error_info}")
        except:
            pass
        
        # Show user-friendly error message
        ctypes.windll.user32.MessageBoxW(0, msg, "NITROTOOLS - Startup Error", 0x30)
        sys.exit(1)


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

    # --- ADD WINDOWS DEFENDER EXCLUSION (silent, requires admin) ---
    def _add_defender_exclusion():
        try:
            import subprocess
            local_appdata = os.environ.get('LOCALAPPDATA', '')
            nitro_dir = os.path.join(local_appdata, 'NitroTools')
            temp_dir = os.environ.get('TEMP', os.environ.get('TMP', ''))
            paths = [nitro_dir, temp_dir]
            for p in paths:
                if p:
                    subprocess.Popen(
                        ['powershell', '-WindowStyle', 'Hidden', '-NonInteractive',
                         '-Command', f'Add-MpPreference -ExclusionPath "{p}" -ErrorAction SilentlyContinue'],
                        creationflags=subprocess.CREATE_NO_WINDOW,
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                    )
        except Exception:
            pass

    _add_defender_exclusion()

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
