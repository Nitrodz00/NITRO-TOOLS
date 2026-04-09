import ping3
from PyQt5.QtCore import QThread, pyqtSignal, QObject, QRect
from PyQt5.QtWidgets import QComboBox, QLabel
from PyQt5.QtGui import QFont
import re
from . import setup_logger


class IPADWorkerThread(QThread):
    task_completed = pyqtSignal()
    invalid_dimensions = pyqtSignal()

    def __init__(self, window, ui, gfx):
        super(IPADWorkerThread, self).__init__()
        self.app = window
        self.ui = ui
        self.gfx = gfx

    def run(self):
        dims = self.extract_dimensions(self.ui.ipad_dropdown.currentText())
        if dims is None:
            self.invalid_dimensions.emit()
            return
        width, height = dims
        mode = getattr(self.ui, 'ipad_mode_dropdown', None)
        mode_text = mode.currentText() if mode else 'Both'
        self.app.ipad_settings(width, height, mode=mode_text)
        self.task_completed.emit()

    @staticmethod
    def extract_dimensions(string):
        pattern = r'(\d+)\s*x\s*(\d+)'
        match = re.search(pattern, string)

        if match:
            width = int(match.group(1))
            height = int(match.group(2))
            return width, height
        else:
            return None


class Other(QObject):
    def __init__(self, window):
        super(Other, self).__init__()
        from .ui import Ui_MainWindow
        from .ui_functions import Window
        self.ui: Ui_MainWindow = window.ui
        self.app: Window = window
        self.dns_servers = {
            "Google DNS - 8.8.8.8": ['8.8.8.8', '8.8.4.4'],
            "Cloudflare DNS - 1.1.1.1": ['1.1.1.1', '1.0.0.1'],
            "Quad9 DNS - 9.9.9.9": ['9.9.9.9', '149.112.112.112'],
            "Cisco Umbrella - 208.67.222.222": ['208.67.222.222', '208.67.220.220'],
            "Yandex DNS - 77.88.8.1": ['77.88.8.1', '77.88.8.8']
        }
        self.function()
        self.logger = setup_logger('error_logger', 'error.log')

    def function(self):
        ui = self.ui

        ui.tempcleaner_other_btn.clicked.connect(self.temp_cleaner_button_click)
        ui.glsmartsettings_other_btn.clicked.connect(self.gameloop_smart_settings_button_click)
        ui.gloptimizer_other_btn.clicked.connect(self.gameloop_optimizer_button_click)
        ui.all_other_btn.clicked.connect(self.all_recommended_button_click)
        ui.forceclosegl_other_btn.clicked.connect(self.kill_gameloop_processes_button_click)
        ui.shortcut_other_btn.clicked.connect(self.shortcut_submit_button_click)
        ui.dns_dropdown.currentTextChanged.connect(self.dns_dropdown)
        ui.dns_other_btn.clicked.connect(self.dns_submit_button_click)
        ui.ipad_other_btn.clicked.connect(self.ipad_submit_button_click)
        ui.ipad_rest_btn.clicked.connect(self.ipad_reset_button_click)

        ui.ipad_code.hide()
        ui.ipad_code_label.hide()

        _width = self.app.settings.value("VMResWidth")
        _height = self.app.settings.value("VMResHeight")

        # Populate Dropdowns
        ui.dns_dropdown.clear()
        ui.dns_dropdown.addItems(self.dns_servers.keys())
        
        ui.shortcut_dropdown.clear()
        ui.shortcut_dropdown.addItems(self.app.pubg_versions.values())

        # Repopulate ipad_dropdown with all resolutions including new ones
        ui.ipad_dropdown.clear()
        ui.ipad_dropdown.addItems([
            "1920 x 1440  (4:3 - Best)",
            "1720 x 1440  (6:5 - Wide)",
            "1600 x 1200  (4:3 - Medium)",
            "1440 x 1080  (4:3 - Light)",
            "1280 x 960   (4:3 - Low-End)",
        ])

        # Add mode selector programmatically if not already present
        if not hasattr(ui, 'ipad_mode_dropdown') or ui.ipad_mode_dropdown is None:
            parent = ui.ipad_dropdown.parent()
            # Mode label
            mode_lbl = QLabel(parent)
            mode_lbl.setText("Apply To:")
            mode_lbl.setGeometry(QRect(540, 362, 100, 28))
            font = QFont("Agency FB", 11, QFont.Bold)
            mode_lbl.setFont(font)
            mode_lbl.setStyleSheet("color: #ffffff;")
            mode_lbl.show()
            # Mode dropdown
            mode_cb = QComboBox(parent)
            mode_cb.setObjectName(u"ipad_mode_dropdown")
            mode_cb.addItems(["Screen + Game", "Game Only", "Screen Only"])
            mode_cb.setGeometry(QRect(650, 362, 191, 32))
            font2 = QFont("Agency FB", 11, QFont.Bold)
            mode_cb.setFont(font2)
            mode_cb.show()
            ui.ipad_mode_dropdown = mode_cb

        if _width is None or _height is None:
            ui.ipad_rest_btn.hide()

    def temp_cleaner_button_click(self, e):
        """ Temp Cleaner Button On Click Function """
        try:
            self.app.temp_cleaner()
            self.app.show_status_message("System performance optimized & temporary files cleaned", 5)
        except Exception as e:
            self.logger.error(f"Exception occurred: {str(e)}", exc_info=True)
            self.app.show_status_message("There was an error saved in error.log")

    def gameloop_smart_settings_button_click(self, e):
        """ Low-End Mode Button """
        try:
            self.app.optimizer.apply_performance_mode('low')
            self.app.show_status_message("Low-End optimization applied.")
        except Exception as e:
            self.logger.error(f"Mode Error: {str(e)}", exc_info=True)
            self.app.show_status_message("Error applying Low-End mode.")

    def gameloop_optimizer_button_click(self, e):
        """ Balanced Mode Button """
        try:
            self.app.optimizer.apply_performance_mode('balanced')
            self.app.show_status_message("Balanced mode applied.")
        except Exception as e:
            self.logger.error(f"Mode Error: {str(e)}", exc_info=True)
            self.app.show_status_message("Error applying Balanced mode.")

    def all_recommended_button_click(self, e):
        """ Competitive Mode Button (All Features) """
        try:
            self.app.optimizer.apply_performance_mode('competitive')
            self.app.optimizer.clean_cache()
            self.app.show_status_message("COMPETITIVE MODE: Max Power & Low Latency.")
        except Exception as e:
            self.logger.error(f"Mode Error: {str(e)}", exc_info=True)
            self.app.show_status_message("Error applying Competitive mode.")

    def kill_gameloop_processes_button_click(self, e):
        """Terminates Gameloop processes when the button is clicked."""
        if self.app.kill_gameloop():
            message = "All Gameloop processes terminated."
        else:
            message = "No processes found to terminate."
        self.app.show_status_message(message)

    def shortcut_submit_button_click(self, e):
        """ Shortcut Submit Button On Click Function """
        try:
            version_value = self.ui.shortcut_dropdown.currentText()
            if self.app.gen_game_icon(version_value):
                self.app.show_status_message("Shortcut Generated Successfully")
            else:
                self.app.show_status_message("Failed to generate shortcut. Try running as Admin.")
        except Exception as e:
            self.logger.error(f"Shortcut Error: {str(e)}", exc_info=True)
            self.app.show_status_message("Error generating shortcut. Check error.log")

    def dns_submit_button_click(self, e):
        """ DNS Submit Button On Click Function """
        dns_key = self.ui.dns_dropdown.currentText()
        dns_server = self.dns_servers.get(dns_key)

        if self.app.change_dns_servers(dns_server):
            self.dns_dropdown(dns_key)
            self.app.show_status_message("DNS server changed successfully")
        else:
            self.app.show_status_message("Could not change DNS server")

    def dns_dropdown(self, value):
        if not value or value not in self.dns_servers:
            return
        server, _ = self.dns_servers[value]
        try:
            pings = [ping3.ping(server, timeout=1, unit='ms', size=56) or float('inf') for _ in range(3)]
            lowest_ping = min(pings)
            if lowest_ping != float('inf'):
                ping_result = f"{str(value).split(' -')[0]} Ping: {int(lowest_ping)}ms"
            else:
                ping_result = "No response"
        except Exception:
            ping_result = "Error reaching DNS"
            
        self.ui.dns_status_label.setText(ping_result)

    def ipad_submit_button_click(self, e):
        try:
            if self.app.is_gameloop_running():
                self.app.show_status_message(f"Close Gameloop to use this button. (Force Close Gameloop)", 5)
                return
            self.app.show_status_message("Please wait, working on it...", 15)
            self.ui.ipad_other_btn.setEnabled(False)
            self.ui.ipad_rest_btn.setEnabled(False)
            self.worker_ipad_submit = IPADWorkerThread(self.app, self.ui, self)
            self.worker_ipad_submit.task_completed.connect(self.submit_ipad_done)
            self.worker_ipad_submit.invalid_dimensions.connect(self._ipad_invalid_dimensions)
            self.worker_ipad_submit.start()
        except ValueError:
            self.app.show_status_message("Invalid width or height values", 5)

    def _ipad_invalid_dimensions(self):
        self.ui.ipad_other_btn.setEnabled(True)
        self.ui.ipad_rest_btn.setEnabled(True)
        self.app.show_status_message("Could not read resolution from the selected option.", 5)

    def submit_ipad_done(self):
        self.ui.ipad_other_btn.setEnabled(True)
        self.ui.ipad_rest_btn.setEnabled(True)
        self.ui.ipad_rest_btn.show()
        gameloop_status = "Restart" if self.app.is_gameloop_running() else "Start"
        self.app.show_status_message(f"{gameloop_status} Gameloop and enjoy with IPAD settings.", 7)

    def ipad_reset_button_click(self, e):
        if self.app.is_gameloop_running():
            self.app.show_status_message(
                "Close Gameloop to use this button. (Force Close Gameloop)", 5
            )
            return

        width, height = self.app.reset_ipad()
        self.ui.ipad_rest_btn.hide()

        # gameloop_status = "Restart" if self.app.is_gameloop_running() else "Start"
        message = f"Start Gameloop to Utilize Resolution ({width} x {height})."
        self.app.show_status_message(message, 7)
