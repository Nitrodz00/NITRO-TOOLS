import psutil
from PyQt5.QtCore import QThread, pyqtSignal, QTimer

class GameWatcher(QThread):
    """Watcher thread to detect game launch and apply real-time optimizations (Auto-Boost)."""
    game_detected = pyqtSignal(bool)
    process_info = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = True
        self.game_running = False
        self.target_processes = ['AndroidEmulatorEn.exe', 'AndroidEmulatorEx.exe', 'AndroidEmulator.exe', 'aow_exe.exe']
        self.telemetry_killers = ['Syzs_dl_svr.exe', 'QMEmulatorService.exe', 'TBSWebRenderer.exe']
        # Keep reference to main window if provided so watcher can call higher-level tweaks
        self.window = parent
        self.poll_timer = QTimer()
        self.poll_timer.timeout.connect(self._check_processes)
        self.target_procs_lower = [p.lower() for p in self.target_processes]
        self.killer_procs_lower = [p.lower() for p in self.telemetry_killers]

    def run(self):
        """Start the monitoring timer."""
        self.poll_timer.start(4000)  # Start with 4 second interval
        self.exec()  # Start event loop

    def _check_processes(self):
        """Check processes using QTimer for responsive UI."""
        try:
            current_running = False
            for proc in psutil.process_iter(['name', 'nice', 'cpu_affinity']):
                try:
                    name_lower = proc.info['name'].lower()
                    
                    if name_lower in self.target_procs_lower:
                        current_running = True
                        self._apply_boost(proc)
                    
                    # Kill redundant background trackers
                    if name_lower in self.killer_procs_lower:
                        try:
                            proc.terminate()
                        except:
                            pass
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if current_running != self.game_running:
                self.game_running = current_running
                self.game_detected.emit(current_running)
                
            # Adaptive polling - check faster when game is running
            new_interval = 2000 if self.game_running else 4000
            if self.poll_timer.interval() != new_interval:
                self.poll_timer.setInterval(new_interval)
                
        except Exception:
            pass

    def stop(self):
        """Stop the monitoring thread."""
        self.running = False
        if self.poll_timer.isActive():
            self.poll_timer.stop()
        self.quit()
        self.wait()

    def _apply_boost(self, proc):
        """Apply High Priority and CPU Affinity."""
        try:
            # High Priority
            if proc.info['nice'] != psutil.HIGH_PRIORITY_CLASS:
                proc.nice(psutil.HIGH_PRIORITY_CLASS)
            
            # Affinity settings: Leave Core 0 for Windows, use the rest for game
            total_cores = psutil.cpu_count(logical=True)
            if total_cores > 2:
                gaming_cores = list(range(1, total_cores))
                if proc.info['cpu_affinity'] != gaming_cores:
                    proc.cpu_affinity(gaming_cores)
                    self.process_info.emit(f"Applied CPU Affinity: {gaming_cores} to {proc.info['name']}")
                    
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            pass

        # If the main window requested persistent auto-boost, call safer high-level tweaks
        try:
            if getattr(self, 'window', None) and getattr(self.window, 'auto_boost_enabled', False):
                try:
                    # Keep priority/affinity and some light maintenance running while game exists
                    self.window.set_high_performance_power_plan()
                except Exception:
                    pass
                try:
                    # Periodic RAM cleanup (best-effort)
                    self.window.clear_standby_list()
                except Exception:
                    pass
        except Exception:
            pass

