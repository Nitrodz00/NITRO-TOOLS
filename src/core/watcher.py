import psutil
from PyQt5.QtCore import QThread, pyqtSignal
from time import sleep

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

    def run(self):
        """Monitor processes in a loop with low overhead."""
        target_procs_lower = [p.lower() for p in self.target_processes]
        killer_procs_lower = [p.lower() for p in self.telemetry_killers]
        
        while self.running:
            try:
                current_running = False
                for proc in psutil.process_iter(['name', 'nice', 'cpu_affinity']):
                    try:
                        name_lower = proc.info['name'].lower()
                        
                        if name_lower in target_procs_lower:
                            current_running = True
                            self._apply_boost(proc)
                        
                        # Kill redundant background trackers
                        if name_lower in killer_procs_lower:
                            try:
                                proc.terminate()
                            except:
                                pass
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                if current_running != self.game_running:
                    self.game_running = current_running
                    self.game_detected.emit(current_running)
                    
            except Exception:
                pass
            
            # Use adaptive polling - check slower when inactive, faster when game is on
            sleep(4 if self.game_running else 8) # Faster check when game_running, slower when idle

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

    def stop(self):
        self.running = False
        self.wait()
