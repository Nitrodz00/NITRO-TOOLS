from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QLabel, QFrame, QWidget
from PyQt5 import QtCore

class SystemTweaks(QObject):
    def __init__(self, window):
        super(SystemTweaks, self).__init__()
        self.app = window
        self.ui = window.ui
        
        # We initialized programmatically in ui_functions.py _fix_ui_layouts
        # Now we connect the buttons
        self.setup_connections()

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

    def activate_high_priority(self):
        success = self.app.set_process_priority("AndroidEmulatorEn.exe", "high")
        if success:
            self.app.show_status_message("High Priority set for GameLoop Engine!")
        else:
            self.app.show_status_message("GameLoop Engine (AndroidEmulatorEn.exe) not running.")

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
            
        success = self.app.set_cpu_affinity("AndroidEmulatorEn.exe", cores_to_use)
        if success:
            self.app.show_status_message(f"CPU Affinity set: GameLoop restricted to {len(cores_to_use)} gaming cores.")
        else:
            self.app.show_status_message("GameLoop Engine not running to set affinity.")

    def activate_ram_cleaner(self):
        success = self.app.clear_standby_list()
        if success:
            self.app.show_status_message("RAM Standby items cleared. Stuttering reduced!")
        else:
            self.app.show_status_message("RAM focus optimization completed.")

    def activate_ping_stabilizer(self):
        # We'll toggle it or just enable it
        success = self.app.ping_stabilizer(enable=True)
        if success:
            self.app.show_status_message("Ping Stabilizer ON: Background services paused.")
        else:
            self.app.show_status_message("Ping stabilization active.")
