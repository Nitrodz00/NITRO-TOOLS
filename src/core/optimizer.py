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
        """Enhanced hardware detection with full AMD GPU support."""
        stats = {
            "cpu_cores": psutil.cpu_count(logical=False) or 4,
            "cpu_threads": psutil.cpu_count(logical=True) or 8,
            "ram_total_gb": round(psutil.virtual_memory().total / (1024**3)),
            "gpu_name": "Generic GPU",
            "vram_mb": 2048,
            "gpu_vendor": "Unknown",
            "gpu_driver_version": "Unknown"
        }
        
        CREATE_NO_WINDOW = 0x08000000
        
        # Try NVIDIA Detection first
        try:
            cmd = ["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader,nounits"]
            res = subprocess.run(cmd, capture_output=True, text=True, creationflags=CREATE_NO_WINDOW)
            out = res.stdout.strip()
            if out and ',' in out:
                parts = out.split(',')
                if len(parts) >= 3:
                    stats["gpu_name"] = parts[0].strip()
                    stats["gpu_vendor"] = "NVIDIA"
                    try: 
                        stats["vram_mb"] = float(parts[1].strip())
                        stats["gpu_driver_version"] = parts[2].strip()
                    except: pass
        except Exception:
            pass
        
        # If NVIDIA not detected, try AMD detection
        if stats["gpu_vendor"] == "Unknown":
            try:
                # AMD GPU detection using AMD-specific tools
                # Try Radeon Software command line interface
                cmd = ["radeon-cmd", "--info"]
                res = subprocess.run(cmd, capture_output=True, text=True, creationflags=CREATE_NO_WINDOW)
                if res.returncode == 0:
                    # Parse AMD GPU info
                    lines = res.stdout.split('\n')
                    for line in lines:
                        if "GPU" in line and "Radeon" in line:
                            stats["gpu_name"] = line.strip()
                            stats["gpu_vendor"] = "AMD"
                            break
            except Exception:
                pass
        
        # Fallback to WMIC for any GPU
        if stats["gpu_vendor"] == "Unknown":
            try:
                cmd = ["wmic", "path", "win32_videocontroller", "get", "name,adapterram", "/format:list"]
                res = subprocess.run(cmd, capture_output=True, text=True, creationflags=CREATE_NO_WINDOW)
                out = res.stdout.strip()
                
                gpu_name = ""
                adapter_ram = ""
                
                for line in out.split('\n'):
                    if line.startswith("Name="):
                        gpu_name = line.split("Name=")[1].strip()
                    elif line.startswith("AdapterRAM="):
                        try:
                            ram_bytes = int(line.split("AdapterRAM=")[1].strip())
                            adapter_ram = ram_bytes // (1024 * 1024)  # Convert to MB
                        except:
                            pass
                
                if gpu_name:
                    stats["gpu_name"] = gpu_name
                    if adapter_ram:
                        stats["vram_mb"] = adapter_ram
                    
                    # Detect vendor from name
                    gpu_name_lower = gpu_name.lower()
                    if "nvidia" in gpu_name_lower or "geforce" in gpu_name_lower or "quadro" in gpu_name_lower or "tesla" in gpu_name_lower:
                        stats["gpu_vendor"] = "NVIDIA"
                    elif "amd" in gpu_name_lower or "radeon" in gpu_name_lower or "ati" in gpu_name_lower:
                        stats["gpu_vendor"] = "AMD"
                    elif "intel" in gpu_name_lower:
                        stats["gpu_vendor"] = "Intel"
                    else:
                        stats["gpu_vendor"] = "Unknown"
                        
            except Exception:
                pass
        
        # Get additional GPU info for AMD using WMI
        if stats["gpu_vendor"] == "AMD":
            try:
                import wmi
                c = wmi.WMI()
                for gpu in c.Win32_VideoController():
                    if "AMD" in gpu.Name or "Radeon" in gpu.Name or "ATI" in gpu.Name:
                        if gpu.DriverVersion:
                            stats["gpu_driver_version"] = gpu.DriverVersion
                        break
            except Exception:
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
