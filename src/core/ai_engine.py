import json
import os
from .optimizer import SystemOptimizer

class AIDynamicOptimizer:
    """
    True AI Dynamic Optimization System (Part 2).
    Evaluates real-time performance and adjusts system parameters dynamically.
    """
    def __init__(self, optimizer: SystemOptimizer):
        self.optimizer = optimizer
        self.history_file = os.path.join(os.path.expanduser("~"), ".nitro_ai_history.json")
        self.performance_history = self._load_history()
        self.last_mode = "balanced"
        self.consecutive_stutter = 0

    def _load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except: return {}
        return {}

    def _save_history(self):
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.performance_history, f)
        except: pass

    def evaluate(self, stats: dict):
        """
        Real-Time Decision Engine.
        Analyzes FPS, CPU, and GPU load to predict the best optimization mode.
        """
        fps = stats.get("fps", 0)
        cpu = stats.get("cpu_percent", 0)
        gpu = stats.get("gpu_percent", 0)
        
        # 1. Detection of 'Performance Health'
        is_stuttering = fps < 45 and cpu > 85
        is_healthy = fps > 55 and cpu < 60
        
        target_mode = self.last_mode
        
        # 2. Decision Logic
        if is_stuttering:
            self.consecutive_stutter += 1
            if self.consecutive_stutter >= 3: # Persistent bottleneck
                target_mode = "competitive"
        elif is_healthy:
            self.consecutive_stutter = 0
            if cpu < 30: # Excess headroom, save resources
                target_mode = "balanced"
        
        # 3. Dynamic adjustment trigger
        if target_mode != self.last_mode:
            self.optimizer.apply_performance_mode(target_mode)
            self.last_mode = target_mode
            
        # 4. Learning logic - Store the 'Best' configuration detected
        hw_info = self.optimizer.get_hardware_info()
        hw_key = f"{hw_info['gpu_name']}_{hw_info['cpu_cores']}"
        
        if fps > self.performance_history.get(hw_key, {}).get("best_fps", 0):
            self.performance_history[hw_key] = {
                "best_fps": fps,
                "mode": target_mode,
                "cpu_load": cpu,
                "gpu_load": gpu
            }
            self._save_history()

    def get_smart_suggestion(self):
        """Adaptive Learning output."""
        hw_info = self.optimizer.get_hardware_info()
        hw_key = f"{hw_info['gpu_name']}_{hw_info['cpu_cores']}"
        best = self.performance_history.get(hw_key)
        if best:
            return f"Calculated best mode for your hardware: {best['mode'].upper()} (Expected FPS: {best['best_fps']})"
        return "Learning hardware patterns... Play for 5 minutes."
