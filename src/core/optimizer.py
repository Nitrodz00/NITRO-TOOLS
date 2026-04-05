import os
import subprocess
import winreg
import psutil
import GPUtil
import tempfile
import shutil
from typing import Dict, Any

class SystemOptimizer:
    """Core logic for system and GameLoop optimizations."""
    
    def __init__(self):
        self.REG_GAMELOOP = r'SOFTWARE\Tencent\MobileGamePC'
        self.REG_UI = r'SOFTWARE\WOW6432Node\Tencent\MobileGamePC\UI'
        
    def get_hardware_info(self) -> Dict[str, Any]:
        """Detect system hardware to recommend settings."""
        stats = {
            "cpu_cores": psutil.cpu_count(logical=False),
            "cpu_threads": psutil.cpu_count(logical=True),
            "ram_total_gb": round(psutil.virtual_memory().total / (1024**3)),
            "gpu_name": "Unknown",
            "vram_mb": 0
        }
        
        try:
            CREATE_NO_WINDOW = 0x08000000
            cmd = ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"]
            out = subprocess.run(cmd, capture_output=True, text=True, creationflags=CREATE_NO_WINDOW).stdout
            if out.strip():
                name, vram = out.strip().split(',')
                stats["gpu_name"] = name.strip()
                stats["vram_mb"] = float(vram.strip())
        except:
            pass
            
        return stats

    def set_registry_dword(self, path: str, name: str, value: int, root=winreg.HKEY_CURRENT_USER):
        """Helper to set registry DWORD values safely."""
        try:
            key = winreg.CreateKeyEx(root, path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, value)
            winreg.CloseKey(key)
            return True
        except Exception:
            return False

    def optimize_network(self):
        """Applies TCP and Network Throttling tweaks."""
        # Throttling Index - 0xFFFFFFFF disables it
        self.set_registry_dword(
            r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile",
            "NetworkThrottlingIndex", 0xFFFFFFFF, winreg.HKEY_LOCAL_MACHINE
        )
        # System Responsiveness - 0 for gaming
        self.set_registry_dword(
            r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile",
            "SystemResponsiveness", 0, winreg.HKEY_LOCAL_MACHINE
        )

    def clean_cache(self):
        """Safely cleans GameLoop and System temp files."""
        temp_dirs = [
            tempfile.gettempdir(),
            r"C:\Windows\Temp",
            os.path.expandvars(r'%windir%\Prefetch')
        ]
        
        # Get GameLoop shader cache path
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, self.REG_UI) as key:
                gl_path, _ = winreg.QueryValueEx(key, "InstallPath")
                shader_path = os.path.join(gl_path, 'ShaderCache')
                if os.path.exists(shader_path):
                    temp_dirs.append(shader_path)
        except:
            pass

        cleaned_count = 0
        for directory in temp_dirs:
            if not os.path.exists(directory): continue
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                try:
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path, ignore_errors=True)
                    cleaned_count += 1
                except:
                    continue
        return cleaned_count

    def optimize_power_plan(self):
        """Sets Windows Power Plan to High Performance."""
        try:
            # High Performance GUID: 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c
            # Ultimate Performance GUID: e9a42b02-d5df-448d-aa00-03f14749eb61
            CREATE_NO_WINDOW = 0x08000000
            subprocess.run(["powercfg", "/setactive", "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"], 
                            capture_output=True, check=False, creationflags=CREATE_NO_WINDOW)
        except Exception:
            pass

    def apply_performance_mode(self, mode: str):
        """
        Applies a specific optimization profile.
        Modes: 'low', 'balanced', 'competitive'
        """
        self.optimize_power_plan() # Trigger for all high-perf modes
        hw = self.get_hardware_info()
        
        # Base GameLoop Registries
        path = self.REG_GAMELOOP
        
        if mode == 'low':
            self.set_registry_dword(path, "VMMemorySizeInMB", min(hw["ram_total_gb"] * 1024 // 2, 2048))
            self.set_registry_dword(path, "VMCpuCount", min(hw["cpu_cores"], 2))
            self.set_registry_dword(path, "FxaaQuality", 0)
            self.set_registry_dword(path, "RenderOptimizeEnabled", 1)
        
        elif mode == 'competitive':
            self.set_registry_dword(path, "VMMemorySizeInMB", min(hw["ram_total_gb"] * 1024, 8192))
            self.set_registry_dword(path, "VMCpuCount", min(hw["cpu_cores"], 8))
            self.set_registry_dword(path, "FxaaQuality", 2)
            self.set_registry_dword(path, "RenderOptimizeEnabled", 1)
            self.set_registry_dword(path, "GraphicsCardEnabled", 1)
            self.optimize_network()
            
        else: # Balanced
            self.set_registry_dword(path, "VMMemorySizeInMB", min(hw["ram_total_gb"] * 1024 // 1.5, 4096))
            self.set_registry_dword(path, "VMCpuCount", min(hw["cpu_cores"], 4))
            self.set_registry_dword(path, "FxaaQuality", 1)
            self.set_registry_dword(path, "RenderOptimizeEnabled", 1)
