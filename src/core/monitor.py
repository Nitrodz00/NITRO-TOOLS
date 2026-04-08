import random
import subprocess
import time
import psutil
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from typing import Dict, Any, List

from .cache_manager import get_cache_manager, PerformanceCache

class MonitorStats(QThread):
    """
    Enhanced real-time monitoring thread with AMD GPU support and detailed performance tracking.
    """
    stats_updated = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = True
        self._prev_cpu_times = {}
        self._gpu_vendor = "Unknown"
        self._performance_history = []
        self._max_history_size = 100
        
        # Initialize caching system
        self.cache_manager = get_cache_manager()
        self.performance_cache = PerformanceCache(self.cache_manager)
        
        # Use QTimer instead of sleep for better responsiveness
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_stats)
        self.update_timer.setInterval(500)  # 500ms update interval
        
        # Detect GPU vendor on initialization
        self._detect_gpu_vendor()

        # ADB real FPS state
        self._adb = None
        self._pubg_package = None

    def _detect_gpu_vendor(self):
        """Detect GPU vendor for appropriate monitoring methods."""
        try:
            # Try NVIDIA detection
            result = subprocess.run(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader,nounits"], 
                                  capture_output=True, text=True, creationflags=0x08000000)
            if result.returncode == 0 and result.stdout.strip():
                self._gpu_vendor = "NVIDIA"
                return
        except:
            pass
        
        # Try AMD detection
        try:
            result = subprocess.run(["radeon-cmd", "--info"], 
                                  capture_output=True, text=True, creationflags=0x08000000)
            if result.returncode == 0:
                self._gpu_vendor = "AMD"
                return
        except:
            pass
        
        # Fallback to WMI
        try:
            import wmi
            c = wmi.WMI()
            for gpu in c.Win32_VideoController():
                name = gpu.Name.lower()
                if "nvidia" in name or "geforce" in name:
                    self._gpu_vendor = "NVIDIA"
                    return
                elif "amd" in name or "radeon" in name or "ati" in name:
                    self._gpu_vendor = "AMD"
                    return
                elif "intel" in name:
                    self._gpu_vendor = "Intel"
                    return
        except:
            pass

    def _get_gpu_stats(self) -> dict:
        """Get GPU statistics based on detected vendor."""
        stats = {"gpu_percent": 0.0, "gpu_temp": 0, "gpu_memory_used": 0, "gpu_memory_total": 0}
        
        if self._gpu_vendor == "NVIDIA":
            try:
                cmd = ["nvidia-smi", "--query-gpu=utilization.gpu,temperature.gpu,memory.used,memory.total", 
                       "--format=csv,noheader,nounits"]
                result = subprocess.run(cmd, capture_output=True, text=True, creationflags=0x08000000)
                if result.stdout.strip():
                    parts = result.stdout.strip().split(',')
                    if len(parts) >= 4:
                        stats["gpu_percent"] = float(parts[0].strip())
                        stats["gpu_temp"] = int(parts[1].strip())
                        stats["gpu_memory_used"] = int(parts[2].strip())
                        stats["gpu_memory_total"] = int(parts[3].strip())
            except:
                pass
                
        elif self._gpu_vendor == "AMD":
            try:
                # AMD GPU monitoring using Radeon Software
                cmd = ["radeon-cmd", "--showgpuclock", "--showgpuload", "--showgputemp"]
                result = subprocess.run(cmd, capture_output=True, text=True, creationflags=0x08000000)
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if "GPU Load" in line:
                            try:
                                stats["gpu_percent"] = float(line.split('%')[0].split()[-1])
                            except:
                                pass
                        elif "GPU Temperature" in line:
                            try:
                                stats["gpu_temp"] = int(line.split('C')[0].split()[-1])
                            except:
                                pass
            except:
                pass
                
        # Fallback to generic monitoring
        if stats["gpu_percent"] == 0.0:
            try:
                import GPUtil
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]
                    stats["gpu_percent"] = gpu.load * 100
                    stats["gpu_temp"] = gpu.temperature
                    stats["gpu_memory_used"] = gpu.memoryUsed
                    stats["gpu_memory_total"] = gpu.memoryTotal
            except:
                pass
        
        return stats

    def set_adb(self, adb_device, package: str):
        """Enable real FPS reading via ADB when GameLoop connects."""
        self._adb = adb_device
        self._pubg_package = package

    def clear_adb(self):
        """Disable real FPS reading when ADB disconnects."""
        self._adb = None
        self._pubg_package = None

    def _get_real_fps(self) -> int:
        """
        Read real FPS from Android via dumpsys gfxinfo framestats.
        Returns 0 if ADB not connected or data unavailable.
        """
        try:
            output = self._adb.shell(
                f"dumpsys gfxinfo {self._pubg_package} framestats", timeout=1
            )
            timestamps = []
            for line in output.splitlines():
                line = line.strip()
                if not line or not (line[0].isdigit()):
                    continue
                parts = line.split(',')
                if len(parts) < 14:
                    continue
                try:
                    # Column 13 = FRAME_COMPLETED timestamp (nanoseconds)
                    ts = int(parts[13])
                    if ts > 0:
                        timestamps.append(ts)
                except (ValueError, IndexError):
                    continue
            if len(timestamps) < 5:
                return 0
            # FPS = (frames - 1) / elapsed_seconds
            elapsed_ns = timestamps[-1] - timestamps[0]
            if elapsed_ns <= 0:
                return 0
            fps = (len(timestamps) - 1) * 1_000_000_000 / elapsed_ns
            return max(0, min(int(fps), 999))
        except Exception:
            return 0

    def _estimate_fps(self, gpu_load, cpu_process_load, gpu_memory_usage_percent=0):
        """
        Fallback FPS estimation based on GPU/CPU load when ADB is unavailable.
        """
        if gpu_load == 0: return 0
        
        # Base logic: Correlation with hardware potential
        # Adjust target based on GPU vendor and capabilities
        if self._gpu_vendor == "NVIDIA":
            target_max = 120.0  # NVIDIA cards often achieve higher FPS
        elif self._gpu_vendor == "AMD":
            target_max = 110.0  # AMD cards performance
        else:
            target_max = 90.0   # Generic/Intel fallback
        
        # CPU/GPU correlation factor with memory consideration
        correlation = (gpu_load / 100.0)
        
        # Adjust for memory pressure
        if gpu_memory_usage_percent > 80:
            correlation *= 0.8  # Reduce FPS estimate if VRAM is nearly full
        
        estimated = target_max * correlation
        
        # Add 'Jitter' check based on CPU load variability
        if cpu_process_load > 60:
            estimated *= (1.0 - (cpu_process_load / 400.0))  # Reduce if CPU bottleneck
        
        # Add slight realistic fluctuation (+/- 2 FPS) if active
        if estimated > 10:
            estimated += random.uniform(-2, 2)
            
        return int(max(min(estimated, target_max), 0))

    def run(self):
        """Start the monitoring with QTimer-based approach."""
        self.update_timer.start()
    
    def _update_stats(self):
        """Update system statistics using QTimer."""
        if not self.running:
            return
            
        try:
            # Get enhanced GPU stats with caching
            gpu_stats = self.performance_cache.cache.get_or_compute(
                "gpu_stats", 
                self._get_gpu_stats, 
                1  # Cache GPU stats for 1 second
            )
            
            stats = {
                "cpu_percent": psutil.cpu_percent(interval=None),
                "ram_percent": psutil.virtual_memory().percent,
                "ram_used_gb": round(psutil.virtual_memory().used / (1024**3), 2),
                "ram_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
                "gpu_percent": gpu_stats["gpu_percent"],
                "gpu_temp": gpu_stats["gpu_temp"],
                "gpu_memory_used": gpu_stats["gpu_memory_used"],
                "gpu_memory_total": gpu_stats["gpu_memory_total"],
                "cpu_temp": 0,
                "fps": 0,
                "gpu_vendor": self._gpu_vendor,
                "network_latency": 0,
                "disk_usage": 0
            }
            
            # Calculate GPU memory usage percentage
            if gpu_stats["gpu_memory_total"] > 0:
                stats["gpu_memory_percent"] = (gpu_stats["gpu_memory_used"] / gpu_stats["gpu_memory_total"]) * 100
            else:
                stats["gpu_memory_percent"] = 0

            # CPU Temperature monitoring with caching
            stats["cpu_temp"] = self.performance_cache.cache.get_or_compute(
                "cpu_temp",
                self._get_cpu_temperature,
                5  # Cache CPU temp for 5 seconds
            )

            # Get GameLoop process CPU usage for FPS estimation
            game_cpu_load = self._get_game_cpu_load()

            # Real FPS via ADB when connected, estimated otherwise
            if self._adb and self._pubg_package:
                real = self.performance_cache.cache.get_or_compute(
                    "real_fps",
                    self._get_real_fps,
                    1  # Refresh every 1 second
                )
                stats["fps"] = real if real > 0 else self.performance_cache.cache.get_or_compute(
                    "fps_estimate",
                    lambda: self._estimate_fps(stats["gpu_percent"], game_cpu_load, stats.get("gpu_memory_percent", 0)),
                    0.5
                )
                stats["fps_source"] = "real" if real > 0 else "estimate"
            else:
                stats["fps"] = self.performance_cache.cache.get_or_compute(
                    "fps_estimate",
                    lambda: self._estimate_fps(stats["gpu_percent"], game_cpu_load, stats.get("gpu_memory_percent", 0)),
                    0.5
                )
                stats["fps_source"] = "estimate"

            # Network latency check with caching
            stats["network_latency"] = self.performance_cache.get_network_latency(
                lambda: self._get_network_latency()
            )

            # Disk usage check with caching
            stats["disk_usage"] = self.performance_cache.cache.get_or_compute(
                "disk_usage",
                self._get_disk_usage,
                30  # Cache disk usage for 30 seconds
            )

            # Performance history tracking
            self._performance_history.append({
                "timestamp": psutil.boot_time(),
                "fps": stats["fps"],
                "gpu_percent": stats["gpu_percent"],
                "cpu_percent": stats["cpu_percent"]
            })
            
            # Keep history size manageable
            if len(self._performance_history) > self._max_history_size:
                self._performance_history.pop(0)

            # Add performance alerts
            stats["alerts"] = self._generate_alerts(stats)
            
            # Cache performance snapshot
            self.performance_cache.cache_performance_snapshot(stats)
            
            self.stats_updated.emit(stats)
            
        except Exception as e:
            # Log error but continue monitoring
            pass
    
    def _get_cpu_temperature(self) -> int:
        """Get CPU temperature with error handling."""
        try:
            import wmi
            w = wmi.WMI()
            temp_info = w.query("SELECT * FROM Win32_TemperatureProbe")
            if temp_info:
                return temp_info[0].CurrentReading / 10  # Convert to Celsius
        except:
            pass
        return 0
    
    def _get_game_cpu_load(self) -> float:
        """Get GameLoop process CPU usage."""
        game_cpu_load = 0.0
        target_names = {'aow_exe.exe', 'androidemulatorex.exe', 'androidemulatoren.exe', 'androidemulator.exe'}
        
        for proc in psutil.process_iter(['name', 'cpu_percent', 'memory_info']):
            try:
                if proc.info['name'].lower() in target_names:
                    game_cpu_load += proc.cpu_percent()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        return game_cpu_load
    
    def _get_network_latency(self) -> float:
        """Get network latency to Google DNS."""
        try:
            import ping3
            latency = ping3.ping("8.8.8.8", timeout=1)
            if latency:
                return round(latency * 1000, 1)  # Convert to ms
        except:
            pass
        return 0
    
    def _get_disk_usage(self) -> float:
        """Get disk usage percentage."""
        try:
            disk_usage = psutil.disk_usage('C:\\')
            return round((disk_usage.used / disk_usage.total) * 100, 1)
        except:
            pass
        return 0
    
    def _generate_alerts(self, stats: dict) -> list:
        """Generate performance alerts based on stats."""
        alerts = []
        if stats["gpu_temp"] > 85:
            alerts.append("⚠️ High GPU Temperature")
        if stats["cpu_temp"] > 80:
            alerts.append("⚠️ High CPU Temperature")
        if stats.get("gpu_memory_percent", 0) > 90:
            alerts.append("⚠️ High GPU Memory Usage")
        if stats["fps"] < 30 and stats["gpu_percent"] > 50:
            alerts.append("⚠️ Performance Bottleneck Detected")
        if stats["network_latency"] > 150:
            alerts.append("⚠️ High Network Latency")
        if stats["disk_usage"] > 95:
            alerts.append("⚠️ Low Disk Space")
        
        return alerts

    def stop(self):
        self.running = False
        self.update_timer.stop()
        self.wait()
