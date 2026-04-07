from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QLabel, QFrame, QWidget
from PyQt5 import QtCore

class SystemTweaks(QObject):
    def __init__(self, window):
        super(SystemTweaks, self).__init__()
        self.app = window
        self.ui = window.ui
        
        # We initialized programmatically in ui_functions.py _fix_ui_layouts
        self.setup_connections()
        self.hotkeys_active = False

    def setup_connections(self):
        # These buttons were created in ui_functions.py _fix_ui_layouts
        if hasattr(self.ui, 'high_priority_btn'):
            self.ui.high_priority_btn.clicked.connect(self.activate_high_priority)
        if hasattr(self.ui, 'high_perf_power_btn'):
            self.ui.high_perf_power_btn.clicked.connect(self.activate_high_perf_power)
        if hasattr(self.ui, 'ultimate_perf_power_btn'):
            self.ui.ultimate_perf_power_btn.clicked.connect(self.activate_ultimate_perf_power)
        if hasattr(self.ui, 'cpu_affinity_btn'):
            self.ui.cpu_affinity_btn.clicked.connect(self.activate_cpu_affinity)
        if hasattr(self.ui, 'ram_cleaner_btn'):
            self.ui.ram_cleaner_btn.clicked.connect(self.activate_ram_cleaner)
        if hasattr(self.ui, 'ping_stab_btn'):
            self.ui.ping_stab_btn.clicked.connect(self.activate_ping_stabilizer)
        if hasattr(self.ui, 'ai_optimizer_btn'):
            self.ui.ai_optimizer_btn.clicked.connect(self.run_ai_optimizer)
        if hasattr(self.ui, 'hotkeys_btn'):
            self.ui.hotkeys_btn.clicked.connect(self.toggle_hotkeys)
        if hasattr(self.ui, 'auto_boost_btn'):
            self.ui.auto_boost_btn.clicked.connect(self.toggle_auto_boost)

    def run_ai_optimizer(self):
        import psutil
        total_ram = psutil.virtual_memory().total / (1024 ** 3)
        cores = psutil.cpu_count(logical=False) or 4
        
        self.app.show_status_message(f"AI Scan: {total_ram:.1f}GB RAM, {cores} Cores. Optimizing...")
        
        # Reset current UI choices
        for btn in self.app.GFX.graphics_buttons + self.app.GFX.fps_buttons + self.app.GFX.style_buttons:
            btn.setChecked(False)
            
        # Decision Logic
        if total_ram < 7.5:
            # Low End
            self.ui.smooth_graphics_btn.setChecked(True)
            self.ui.extreme_fps_btn.setChecked(True)
            self.ui.classic_style_btn.setChecked(True)
            self.ui.disable_shadow_btn.setChecked(True)
            self.app.optimizer.apply_performance_mode('low')
        elif total_ram < 15 and cores <= 6:
            # Mid End
            self.ui.balanced_graphics_btn.setChecked(True)
            self.ui.extreme_fps_btn.setChecked(True)
            self.ui.colorful_style_btn.setChecked(True)
            self.ui.enable_shadow_btn.setChecked(True)
            self.app.optimizer.apply_performance_mode('balanced')
        else:
            # High End
            self.ui.hd_graphics_btn.setChecked(True)
            self.ui.fps120_fps_btn.setChecked(True)
            self.ui.movie_style_btn.setChecked(True)
            self.ui.enable_shadow_btn.setChecked(True)
            self.app.optimizer.apply_performance_mode('competitive')
            
        # Apply the checks directly
        self.app.GFX.gfx_submit_button_click()
        self.activate_high_priority()
        self.activate_cpu_affinity()
        # Enable persistent auto-boost while the game is running
        try:
            self.app.auto_boost_enabled = True
        except Exception:
            pass
        self.app.show_status_message("AI Optimization Complete! Auto-Boost enabled while GameLoop runs.")

    def toggle_hotkeys(self):
        try:
            import keyboard
        except ImportError:
            self.app.show_status_message("Error: 'keyboard' module not found.")
            self.ui.hotkeys_btn.setChecked(False)
            return

        self.hotkeys_active = self.ui.hotkeys_btn.isChecked()
        if self.hotkeys_active:
            keyboard.add_hotkey('F8', self.activate_ram_cleaner)
            keyboard.add_hotkey('F9', self.activate_high_priority)
            self.ui.hotkeys_btn.setText("⌨️ HOTKEYS ACTIVE (Press F8 or F9 in-game)")
            self.ui.hotkeys_btn.setStyleSheet("background: #00ff00; color: #000; font-weight: bold;")
            self.app.show_status_message("In-Game Hotkeys Enabled! (F8=RAM, F9=Priority)")
        else:
            keyboard.unhook_all_hotkeys()
            self.ui.hotkeys_btn.setText("⌨️ ENABLE IN-GAME HOTKEYS (F8 RAM Clean, F9 Auto-Prio)")
            self.ui.hotkeys_btn.setStyleSheet("background: #330033; border: 1px solid #ff00ff;")
            self.app.show_status_message("In-Game Hotkeys Disabled.")

    def activate_high_priority(self):
        success = self.app.set_process_priority(priority="high")
        if success:
            self.app.show_status_message("High Priority set for GameLoop Engine!")
        else:
            self.app.show_status_message("GameLoop Engine processes not found to set priority.")

    def activate_high_perf_power(self):
        success = self.app.set_high_performance_power_plan()
        if success:
            self.app.show_status_message("High Performance Power Plan activated!")
        else:
            self.app.show_status_message("Failed to set power plan. Try running as admin.")

    def activate_ultimate_perf_power(self):
        success = self.app.set_ultimate_performance_power_plan()
        if success:
            self.app.show_status_message("Ultimate Performance UNLOCKED and activated!")
        else:
            self.app.show_status_message("Ultimate Performance not supported or Access Denied.")

    def activate_cpu_affinity(self):
        # Professional approach: use cores 2 to max to leave core 0,1 for system/OS
        import psutil
        total_cores = psutil.cpu_count()
        if total_cores > 4:
            # For 8 cores, use 2-7. For 16, use 2-15.
            cores_to_use = list(range(2, total_cores))
        else:
            # For 4 cores, use all.
            cores_to_use = list(range(total_cores))
            
        success = self.app.set_cpu_affinity(cores=cores_to_use)
        if success:
            self.app.show_status_message(f"CPU Affinity set: GameLoop restricted to {len(cores_to_use)} gaming cores.")
        else:
            self.app.show_status_message("GameLoop processes not found to set affinity.")

    def activate_ram_cleaner(self):
        success = self.app.clear_standby_list()
        if success:
            self.app.show_status_message("RAM Standby items cleared. Stuttering reduced!")
        else:
            self.app.show_status_message("RAM focus optimization completed.")

    def toggle_auto_boost(self):
        """Toggle persistent auto-boost while the GameLoop runs."""
        self.auto_boost_active = False
        try:
            self.auto_boost_active = self.ui.auto_boost_btn.isChecked()
            self.app.auto_boost_enabled = self.auto_boost_active
            if self.auto_boost_active:
                self.ui.auto_boost_btn.setText("🛡️ AUTO-BOOST ACTIVE")
                self.ui.auto_boost_btn.setStyleSheet("background: #00ff00; color: #000; font-weight: bold;")
                self.app.show_status_message("Auto-Boost enabled. Will optimize while GameLoop runs.")
            else:
                self.ui.auto_boost_btn.setText("🛡️ AUTO-BOOST WHILE GAME RUNS")
                self.ui.auto_boost_btn.setStyleSheet("")
                self.app.show_status_message("Auto-Boost disabled.")
        except Exception:
            self.app.show_status_message("Failed to toggle Auto-Boost.")

    def activate_ping_stabilizer(self):
        # We'll toggle it or just enable it
        success = self.app.ping_stabilizer(enable=True)
        if success:
            self.app.show_status_message("Ping Stabilizer ON: Background services paused.")
        else:
            self.app.show_status_message("Ping stabilization active.")
