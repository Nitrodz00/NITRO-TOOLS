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

    def run(self):
        """Monitor processes in a loop with low overhead."""
        while self.running:
            try:
                current_running = False
                for proc in psutil.process_iter(['name', 'nice', 'cpu_affinity']):
                    name = proc.info['name']
                    
                    if name in self.target_processes:
                        current_running = True
                        self._apply_boost(proc)
                    
                    # Kill redundant background trackers
                    if name in self.telemetry_killers:
                        try:
                            proc.terminate()
                        except:
                            pass
                
                if current_running != self.game_running:
                    self.game_running = current_running
                    self.game_detected.emit(current_running)
                    
            except Exception:
                pass
            
            # Use adaptive polling - check slower when inactive, faster when game is on
            sleep(2 if not self.game_running else 5)

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

    def stop(self):
        self.running = False
        self.wait()
