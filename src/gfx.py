from PyQt5.QtCore import QThread, pyqtSignal, QObject
import os
import sys
import json

class SubmitWorkerThread(QThread):
    task_completed = pyqtSignal()

    def __init__(self, window, ui, gfx):
        super(SubmitWorkerThread, self).__init__()
        self.app = window
        self.ui = ui
        self.gfx = gfx

    def run(self):
        self.app.show_status_message("Working on Graphics Settings...")

        checked_graphics_button = next((button for button in self.gfx.graphics_buttons if button.isChecked()), None)
        if checked_graphics_button:
            self.app.set_graphics_quality(checked_graphics_button.text())

        checked_fps_button = next((button for button in self.gfx.fps_buttons if button.isChecked()), None)
        if checked_fps_button:
            self.app.set_fps(checked_fps_button.text())

        checked_style_button = next((button for button in self.gfx.style_buttons if button.isChecked()), None)
        if checked_style_button:
            self.app.set_graphics_style(checked_style_button.property("styleId"))

        self.app.save_graphics_file()
        
        # Handle Shadow Setting - Fixed using objectName for image buttons
        checked_shadow_button = next((button for button in self.gfx.shadow_buttons if button.isChecked()), None)
        if checked_shadow_button:
            shadow_val = "ON" if "enable" in checked_shadow_button.objectName().lower() else "OFF"
            self.app.set_shadow(shadow_val)

        self.app.push_active_shadow_file()

        if self.app.pubg_package == "com.pubg.krmobile" and self.ui.resolution_btn.isChecked():
            self.app.kr_fullhd()
        # Only start app if connected and package exists
        elif self.app.pubg_package:
            self.app.start_app()

        self.task_completed.emit()


class ConnectWorkerThread(QThread):
    task_completed = pyqtSignal()

    def __init__(self, window, ui):
        super(ConnectWorkerThread, self).__init__()
        self.app = window
        self.ui = ui

    def get_active_file(self, pubg_version):
        """ Get the active file for the given PUBG version """
        pubg_package = next(key for key, value in self.app.pubg_versions.items() if value == pubg_version)
        self.app.get_graphics_file(pubg_package)

    def show_connection_error(self, message):
        self.ui.connect_gameloop_btn.setChecked(False)
        self.ui.connect_gameloop_btn.setText("Connect to Gameloop")
        self.app.show_status_message(message)
        self.task_completed.emit()

    def run(self):
        self.ui.connect_gameloop_btn.setText("Connecting...")
        self.ui.connect_gameloop_btn.setEnabled(False)
        self.app.show_status_message("Connecting to Gameloop...", 3)
        self.app.check_adb_status()

        if not self.app.adb_enabled:
            message = "Restart GameLoop and Try Again." if self.app.is_gameloop_running() else "GameLoop not working."
            self.show_connection_error(message)
            return

        if not self.app.is_gameloop_running():
            self.show_connection_error("GameLoop not working.")
            return

        self.app.check_adb_connection()

        if not self.app.is_adb_working:
            message = "Restart GameLoop and Try Again." if self.app.is_gameloop_running() else "Gameloop not working."
            self.show_connection_error(message)
            return

        self.app.pubg_version_found()
        num_found = len(self.app.PUBG_Found)

        if num_found == 0:
            self.app.show_status_message("You don't have any PUBG Mobile version installed")
            self.task_completed.emit()
            return
        elif num_found > 1:
            self.ui.pubgchoose_dropdown.clear()
            self.ui.pubgchoose_dropdown.addItems(self.app.PUBG_Found)
            self.ui.pubgchoose_dropdown.setCurrentText(self.app.PUBG_Found[0])
            self.ui.PubgchooseFrame.setVisible(True)
            self.app.show_status_message("Select version to use")
            self.task_completed.emit()
            return

        self.app.show_status_message(f"Using version {self.app.PUBG_Found[0]}", 3)
        self.get_active_file(self.app.PUBG_Found[0])
        self.ui.connect_gameloop_btn.setText("Connected")
        self.task_completed.emit()


class GFX(QObject):
    def __init__(self, window):
        super(GFX, self).__init__()
        self.ui = window.ui
        self.app = window
        
        # Critical: Populate button lists during initialization to prevent crashes in System Optimizer
        self.graphics_buttons = [
            self.ui.super_smooth_graphics_btn,
            self.ui.smooth_graphics_btn,
            self.ui.balanced_graphics_btn,
            self.ui.hd_graphics_btn,
            self.ui.hdr_graphics_btn,
            self.ui.ultrahd_graphics_btn,
        ]
        self.fps_buttons = [
            self.ui.low_fps_btn,
            self.ui.medium_fps_btn,
            self.ui.high_fps_btn,
            self.ui.ultra_fps_btn,
            self.ui.extreme_fps_btn,
            self.ui.fps90_fps_btn,
            self.ui.fps120_fps_btn
        ]
        self.style_buttons = [
            self.ui.classic_style_btn,
            self.ui.colorful_style_btn,
            self.ui.realistic_style_btn,
            self.ui.soft_style_btn,
            self.ui.movie_style_btn
        ]
        self.shadow_buttons = [
            self.ui.disable_shadow_btn,
            self.ui.enable_shadow_btn
        ]

        self.graphics_buttons_func()
        self.fps_buttons_func()
        self.style_buttons_func()

        # UI Initialization
        self.ui.ResolutionkrFrame.hide()
        self.ui.PubgchooseFrame.hide()
        self.gfx_buttons(enabled=False)

        # Signal Connections
        self.ui.connect_gameloop_btn.clicked.connect(self.connect_gameloop_button_click)
        self.ui.submit_gfx_btn.clicked.connect(self.gfx_submit_button_click)
        
        self.ui.disable_shadow_btn.clicked.connect(lambda: self.check_button_selected(self.shadow_buttons, self.ui.disable_shadow_btn))
        self.ui.enable_shadow_btn.clicked.connect(lambda: self.check_button_selected(self.shadow_buttons, self.ui.enable_shadow_btn))

        if hasattr(self.ui, "save_profile_btn"):
            self.ui.save_profile_btn.clicked.connect(self.save_profile)
        if hasattr(self.ui, "load_profile_btn"):
            self.ui.load_profile_btn.clicked.connect(self.load_profile)

    def gfx_submit_button_click(self):
        self.ui.submit_gfx_btn.setEnabled(False)
        self.worker_submit = SubmitWorkerThread(self.app, self.ui, self)
        self.worker_submit.task_completed.connect(self.submit_gfx_done)
        self.worker_submit.start()

    def save_profile(self):
        # Determine selections using objectName for image-based buttons
        checked_graphics = next((b.objectName() for b in self.graphics_buttons if b.isChecked()), "")
        checked_fps = next((b.objectName() for b in self.fps_buttons if b.isChecked()), "")
        checked_style = next((b.objectName() for b in self.style_buttons if b.isChecked()), "")
        checked_shadow = next((b.objectName() for b in self.shadow_buttons if b.isChecked()), "")
        
        if not any([checked_graphics, checked_fps, checked_style]):
            self.app.show_status_message("Select settings first before saving.")
            return
            
        prof = {
            "graphics_btn": checked_graphics,
            "fps_btn": checked_fps,
            "style_btn": checked_style,
            "shadow_btn": checked_shadow
        }
        
        profile_path = os.path.join(os.path.expanduser("~"), "Documents", "nitro_config_v2.json")
        try:
            with open(profile_path, "w") as f:
                json.dump(prof, f)
            self.app.show_status_message(f"✅ PROFILE SAVED IN DOCUMENTS!", 5)
        except Exception:
            self.app.show_status_message("Error saving profile. check permissions.")

    def load_profile(self):
        profile_path = os.path.join(os.path.expanduser("~"), "Documents", "nitro_config_v2.json")
        if not os.path.exists(profile_path):
            self.app.show_status_message("No custom profile found.")
            return
            
        try:
            with open(profile_path, "r") as f:
                prof = json.load(f)
                
            mapping = {
                "graphics_btn": self.graphics_buttons,
                "fps_btn": self.fps_buttons,
                "style_btn": self.style_buttons,
                "shadow_btn": self.shadow_buttons
            }
            
            for key, btn_list in mapping.items():
                if key in prof and prof[key]:
                    for b in btn_list:
                        b.setChecked(b.objectName() == prof[key])
                    
            self.app.show_status_message("📂 PROFILE LOADED! Press 'Submit' to apply.", 6)
        except Exception:
            self.app.show_status_message("Failed to load profile.")

    def submit_gfx_done(self):
        self.ui.submit_gfx_btn.setEnabled(True)
        self.app.show_status_message("Graphics settings applied successfully!")

    def connect_gameloop_button_click(self, checked: bool):
        if checked:
            self.ui.connect_gameloop_btn.setEnabled(False)
            self.worker = ConnectWorkerThread(self.app, self.ui)
            self.worker.task_completed.connect(self.connect_gameloop_task_completed)
            self.worker.start()
        else:
            self.gfx_buttons(enabled=checked)
            self.ui.disable_shadow_btn.setChecked(False)
            self.ui.enable_shadow_btn.setChecked(False)
            self.ui.ResolutionkrFrame.hide()
            self.ui.PubgchooseFrame.hide()
            self.app.kill_adb()
            self.ui.connect_gameloop_btn.setText("Connect to GameLoop")
            self.app.show_status_message("Disconnected.")

    def connect_gameloop_task_completed(self, checked: bool = True):
        self.ui.connect_gameloop_btn.setEnabled(True)
        if not self.app.is_adb_working:
            return

        # Synchronize UI with current game settings
        graphics_val = self.app.get_graphics_setting()
        for b in self.graphics_buttons:
            if b.text() == graphics_val: b.setChecked(True)

        fps_val = self.app.get_fps()
        for b in self.fps_buttons:
            if b.text() == fps_val: b.setChecked(True)

        style_val = self.app.get_graphics_style()
        for b in self.style_buttons:
            if style_val.lower() in b.objectName().lower(): b.setChecked(True)

        shadow_val = self.app.get_shadow()
        for b in self.shadow_buttons:
            is_enabled = "enable" in b.objectName().lower()
            if (shadow_val == "ON" and is_enabled) or (shadow_val != "ON" and not is_enabled):
                b.setChecked(True)

        self.gfx_buttons(enabled=True)

    def graphics_buttons_func(self):
        for button in self.graphics_buttons:
            button.clicked.connect(lambda checked, btn=button: self.check_button_selected(self.graphics_buttons, btn))

    def fps_buttons_func(self):
        for button in self.fps_buttons:
            button.clicked.connect(lambda checked, btn=button: self.check_button_selected(self.fps_buttons, btn))

    def style_buttons_func(self):
        for button in self.style_buttons:
            button.clicked.connect(lambda checked, btn=button: self.check_button_selected(self.style_buttons, btn))

    @staticmethod
    def check_button_selected(buttons, clicked_button):
        for button in buttons:
            button.setChecked(button is clicked_button)

    def gfx_buttons(self, enabled: bool):
        all_interactive = self.graphics_buttons + self.fps_buttons + self.style_buttons + self.shadow_buttons + [self.ui.submit_gfx_btn]
        for button in all_interactive:
            button.setEnabled(enabled)
            if not enabled:
                button.setChecked(False)
