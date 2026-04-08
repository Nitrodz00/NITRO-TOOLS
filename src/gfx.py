from PyQt5.QtCore import QThread, pyqtSignal, QObject
import os
import sys
import json

class SubmitWorkerThread(QThread):
    task_completed = pyqtSignal()
    status = pyqtSignal(str)

    def __init__(self, window, ui, gfx, *, selected_graphics=None, selected_fps=None,
                 selected_style=None, selected_shadow=None, resolution_checked=False):
        super(SubmitWorkerThread, self).__init__()
        self.app = window
        self.ui = ui
        self.gfx = gfx
        self.selected_graphics = selected_graphics
        self.selected_fps = selected_fps
        self.selected_style = selected_style
        self.selected_shadow = selected_shadow
        self.resolution_checked = resolution_checked

    def run(self):
        self.status.emit("Working on Graphics Settings...")
        try:
            # Apply selected options (collected on main thread)
            if self.selected_graphics:
                self.app.set_graphics_quality(self.selected_graphics)

            if self.selected_fps:
                self.app.set_fps(self.selected_fps)

            if self.selected_style:
                self.app.set_graphics_style(self.selected_style)

            # Shadow handling (MUST be before save_graphics_file to include sav binary changes)
            if self.selected_shadow:
                shadow_val = "ON" if "enable" in str(self.selected_shadow).lower() else "OFF"
                self.app.set_shadow(shadow_val)

            # Persist the modified Active.sav content to new.sav
            self.app.save_graphics_file()

            # Push both sav and ini to device to ensure effect
            self.app.push_active_shadow_file()

            # Apply device-specific resolution tweak if requested
            if self.app.pubg_package == "com.pubg.krmobile" and self.resolution_checked:
                self.app.kr_fullhd()
            elif self.app.pubg_package:
                self.app.start_app()

            self.task_completed.emit()
        except Exception as e:
            try:
                self.app.logger.error(f"SubmitWorkerThread error: {e}")
            except Exception:
                pass
            self.status.emit(f"Error applying graphics: {e}")
            self.task_completed.emit()


class ConnectWorkerThread(QThread):
    task_completed = pyqtSignal()
    status = pyqtSignal(str)
    error = pyqtSignal(str)
    choose_version = pyqtSignal(list)
    connected = pyqtSignal(str)

    def __init__(self, window, ui):
        super(ConnectWorkerThread, self).__init__()
        self.app = window
        self.ui = ui

    def get_active_file(self, pubg_version):
        """ Get the active file for the given PUBG version """
        pubg_package = next(key for key, value in self.app.pubg_versions.items() if value == pubg_version)
        self.app.get_graphics_file(pubg_package)

    def show_connection_error(self, message):
        # Emit an error for the UI to handle
        self.error.emit(message)
        self.task_completed.emit()

    def run(self):
        # Signal UI that connection is starting
        self.connected.emit("Connecting...")
        self.status.emit("Connecting to Gameloop...")
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
            self.status.emit("You don't have any PUBG Mobile version installed")
            self.task_completed.emit()
            return
        elif num_found > 1:
            # Ask UI to show choose dialog
            self.choose_version.emit(self.app.PUBG_Found)
            self.status.emit("Select version to use")
            self.task_completed.emit()
            return

        self.status.emit(f"Using version {self.app.PUBG_Found[0]}")
        self.get_active_file(self.app.PUBG_Found[0])
        self.connected.emit("Connected")
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
        # Collect current selections on the main thread (safe) and pass to worker
        self.ui.submit_gfx_btn.setEnabled(False)
        selected_graphics = next((b.text() for b in self.graphics_buttons if b.isChecked()), None)
        selected_fps = next((b.text() for b in self.fps_buttons if b.isChecked()), None)
        selected_style = next((b.property("styleId") for b in self.style_buttons if b.isChecked()), None)
        selected_shadow = next((b.objectName() for b in self.shadow_buttons if b.isChecked()), None)
        resolution_checked = getattr(self.ui, 'resolution_btn', None) and self.ui.resolution_btn.isChecked()

        self.worker_submit = SubmitWorkerThread(
            self.app, self.ui, self,
            selected_graphics=selected_graphics,
            selected_fps=selected_fps,
            selected_style=selected_style,
            selected_shadow=selected_shadow,
            resolution_checked=resolution_checked
        )
        self.worker_submit.task_completed.connect(self.submit_gfx_done)
        self.worker_submit.status.connect(lambda msg, dur=5: self.app.show_status_message(msg, dur))
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
            # Update UI immediately, then start background worker which will emit signals
            self.ui.connect_gameloop_btn.setEnabled(False)
            self.ui.connect_gameloop_btn.setText("Connecting...")

            self.worker = ConnectWorkerThread(self.app, self.ui)
            self.worker.task_completed.connect(self.connect_gameloop_task_completed)
            self.worker.status.connect(lambda msg, dur=3: self.app.show_status_message(msg, dur))
            self.worker.error.connect(self._on_connect_error)
            self.worker.choose_version.connect(self._on_choose_version)
            self.worker.connected.connect(lambda txt: self.ui.connect_gameloop_btn.setText(txt))
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

    def _on_connect_error(self, message: str):
        # Reset UI to disconnected state and show error
        self.ui.connect_gameloop_btn.setChecked(False)
        self.ui.connect_gameloop_btn.setText("Connect to GameLoop")
        self.gfx_buttons(enabled=False)
        try:
            self.ui.disable_shadow_btn.setChecked(False)
            self.ui.enable_shadow_btn.setChecked(False)
            self.ui.ResolutionkrFrame.hide()
            self.ui.PubgchooseFrame.hide()
        except Exception:
            pass
        try:
            self.app.kill_adb()
        except Exception:
            pass
        self.app.show_status_message(message)

    def _on_choose_version(self, versions: list):
        try:
            self.ui.pubgchoose_dropdown.clear()
            self.ui.pubgchoose_dropdown.addItems(versions)
            if versions:
                self.ui.pubgchoose_dropdown.setCurrentText(versions[0])
            self.ui.PubgchooseFrame.setVisible(True)
            self.app.show_status_message("Select version to use")
        except Exception:
            self.app.show_status_message("Error preparing version chooser")

    def connect_gameloop_task_completed(self, checked: bool = True):
        self.ui.connect_gameloop_btn.setEnabled(True)
        if not self.app.is_adb_working:
            return

        # Enable real FPS reading in the monitor
        try:
            if hasattr(self.app, 'monitor') and self.app.pubg_package:
                self.app.monitor.set_adb(self.app.adb, self.app.pubg_package)
        except Exception:
            pass

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
            if (shadow_val == "Enable" and is_enabled) or (shadow_val == "Disable" and not is_enabled):
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
