"""
Compatibility Manager for NITROTOOLS
Handles detection and disabling of incompatible features based on system configuration.
"""

import os
import sys
import platform
import subprocess
import psutil
from typing import Dict, List, Any, Tuple
from PyQt5.QtCore import QObject, pyqtSignal


class CompatibilityManager(QObject):
    """
    Manages feature compatibility based on system configuration and hardware.
    Automatically disables features that may cause issues on specific systems.
    """
    
    compatibility_updated = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.system_info = self._get_system_info()
        self.compatibility_matrix = self._build_compatibility_matrix()
        self.disabled_features = set()
        self.warnings = []
        
        # Analyze system compatibility
        self._analyze_compatibility()
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Gather comprehensive system information."""
        info = {
            "os_version": platform.version(),
            "os_build": platform.win32_ver()[1] if platform.system() == "Windows" else "",
            "architecture": platform.architecture()[0],
            "processor": platform.processor(),
            "cpu_cores": psutil.cpu_count(logical=False),
            "cpu_threads": psutil.cpu_count(logical=True),
            "ram_total_gb": round(psutil.virtual_memory().total / (1024**3), 1),
            "gpu_info": self._detect_gpu_info(),
            "admin_privileges": self._check_admin_privileges(),
            "virtualization": self._check_virtualization(),
            "game_loop_installed": self._check_gameloop_installation()
        }
        
        return info
    
    def _detect_gpu_info(self) -> Dict[str, Any]:
        """Detect GPU information."""
        gpu_info = {"vendor": "Unknown", "name": "Unknown", "driver_version": "Unknown"}
        
        try:
            # Try NVIDIA detection
            result = subprocess.run(["nvidia-smi", "--query-gpu=name,driver_version", 
                                   "--format=csv,noheader,nounits"], 
                                  capture_output=True, text=True, creationflags=0x08000000)
            if result.returncode == 0 and result.stdout.strip():
                parts = result.stdout.strip().split(',')
                if len(parts) >= 2:
                    gpu_info["vendor"] = "NVIDIA"
                    gpu_info["name"] = parts[0].strip()
                    gpu_info["driver_version"] = parts[1].strip()
        except:
            pass
        
        if gpu_info["vendor"] == "Unknown":
            try:
                # Try AMD detection
                result = subprocess.run(["radeon-cmd", "--info"], 
                                      capture_output=True, text=True, creationflags=0x08000000)
                if result.returncode == 0:
                    gpu_info["vendor"] = "AMD"
                    # Parse AMD GPU info
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if "GPU" in line and ("Radeon" in line or "AMD" in line):
                            gpu_info["name"] = line.strip()
                            break
            except:
                pass
        
        # Fallback to WMI
        if gpu_info["vendor"] == "Unknown":
            try:
                import wmi
                c = wmi.WMI()
                for gpu in c.Win32_VideoController():
                    name = gpu.Name.lower()
                    if "nvidia" in name or "geforce" in name:
                        gpu_info["vendor"] = "NVIDIA"
                    elif "amd" in name or "radeon" in name or "ati" in name:
                        gpu_info["vendor"] = "AMD"
                    elif "intel" in name:
                        gpu_info["vendor"] = "Intel"
                    
                    gpu_info["name"] = gpu.Name
                    if gpu.DriverVersion:
                        gpu_info["driver_version"] = gpu.DriverVersion
                    break
            except:
                pass
        
        return gpu_info
    
    def _check_admin_privileges(self) -> bool:
        """Check if running with administrator privileges."""
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False
    
    def _check_virtualization(self) -> bool:
        """Check if running in a virtual environment."""
        try:
            # Check for common virtualization indicators
            virtual_indicators = [
                "VirtualBox", "VMware", "QEMU", "Xen", "Hyper-V", 
                "KVM", "Parallels", "Virtual PC"
            ]
            
            # Check system manufacturer
            try:
                import wmi
                c = wmi.WMI()
                for computer in c.Win32_ComputerSystem():
                    manufacturer = computer.Manufacturer.lower()
                    model = computer.Model.lower()
                    
                    for indicator in virtual_indicators:
                        if indicator.lower() in manufacturer or indicator.lower() in model:
                            return True
            except:
                pass
            
            # Check for virtual processes
            for proc in psutil.process_iter(['name']):
                try:
                    proc_name = proc.info['name'].lower()
                    if any(indicator.lower() in proc_name for indicator in virtual_indicators):
                        return True
                except:
                    continue
            
        except:
            pass
        
        return False
    
    def _check_gameloop_installation(self) -> bool:
        """Check if GameLoop is properly installed."""
        try:
            import winreg
            
            # Check registry
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                              r"SOFTWARE\WOW6432Node\Tencent\MobileGamePC\UI") as key:
                install_path, _ = winreg.QueryValueEx(key, "InstallPath")
                if install_path and os.path.exists(install_path):
                    return True
        except:
            pass
        
        return False
    
    def _build_compatibility_matrix(self) -> Dict[str, Dict[str, Any]]:
        """Build the compatibility matrix for features."""
        return {
            "shadow_control": {
                "name": "Shadow Control",
                "description": "Enable/disable game shadows",
                "requirements": {
                    "min_ram_gb": 4,
                    "gpu_blacklist": ["Intel HD Graphics"],  # GPUs that may have issues
                    "os_min_build": "10240",  # Windows 10 version 1507
                    "admin_required": False
                },
                "issues": {
                    "low_ram": "May cause performance issues on systems with <4GB RAM",
                    "intel_gpu": "Intel integrated graphics may have shadow rendering issues",
                    "old_os": "Requires Windows 10 version 1507 or later"
                }
            },
            "ai_optimizer": {
                "name": "AI Dynamic Optimizer",
                "description": "Machine learning based performance optimization",
                "requirements": {
                    "min_ram_gb": 6,
                    "min_cpu_cores": 4,
                    "gpu_whitelist": ["NVIDIA", "AMD"],  # Required GPU vendors
                    "admin_required": True
                },
                "issues": {
                    "low_ram": "Requires at least 6GB RAM for ML models",
                    "weak_cpu": "Requires at least 4 CPU cores for real-time optimization",
                    "unsupported_gpu": "Only NVIDIA and AMD GPUs are supported",
                    "no_admin": "Requires administrator privileges for system optimizations"
                }
            },
            "real_time_monitoring": {
                "name": "Real-time Performance Monitoring",
                "description": "Live system performance monitoring",
                "requirements": {
                    "min_ram_gb": 4,
                    "admin_required": False
                },
                "issues": {
                    "low_ram": "May impact performance on systems with <4GB RAM",
                    "virtual_env": "May not work correctly in virtual environments"
                }
            },
            "advanced_registry_tweaks": {
                "name": "Advanced Registry Tweaks",
                "description": "Deep system optimizations via registry",
                "requirements": {
                    "admin_required": True,
                    "os_blacklist": []  # OS versions where this is problematic
                },
                "issues": {
                    "no_admin": "Requires administrator privileges",
                    "virtual_env": "Not recommended in virtual environments"
                }
            },
            "gpu_overclock": {
                "name": "GPU Overclocking",
                "description": "GPU performance tuning",
                "requirements": {
                    "gpu_whitelist": ["NVIDIA", "AMD"],
                    "admin_required": True
                },
                "issues": {
                    "unsupported_gpu": "Only NVIDIA and AMD GPUs are supported",
                    "no_admin": "Requires administrator privileges",
                    "laptop_warning": "Use caution on laptop systems"
                }
            },
            "network_optimization": {
                "name": "Network Optimization",
                "description": "TCP/IP and network stack optimization",
                "requirements": {
                    "admin_required": True
                },
                "issues": {
                    "no_admin": "Requires administrator privileges",
                    "corporate_network": "May not work on corporate networks with restrictions"
                }
            },
            "hotkeys": {
                "name": "In-game Hotkeys",
                "description": "Keyboard shortcuts for game functions",
                "requirements": {
                    "admin_required": False
                },
                "issues": {
                    "accessibility": "May conflict with accessibility software",
                    "other_games": "May interfere with other games' hotkeys"
                }
            },
            "auto_updates": {
                "name": "Automatic Updates",
                "description": "Check for and install updates automatically",
                "requirements": {
                    "admin_required": False
                },
                "issues": {
                    "metered_connection": "Not recommended on metered internet connections",
                    "firewall": "May be blocked by corporate firewalls"
                }
            }
        }
    
    def _analyze_compatibility(self):
        """Analyze system compatibility and disable problematic features."""
        self.disabled_features.clear()
        self.warnings.clear()
        
        for feature_id, feature_info in self.compatibility_matrix.items():
            issues = self._check_feature_compatibility(feature_id, feature_info)
            
            if issues:
                self.disabled_features.add(feature_id)
                self.warnings.extend(issues)
        
        # Emit compatibility update
        self.compatibility_updated.emit({
            "disabled_features": list(self.disabled_features),
            "warnings": self.warnings,
            "system_info": self.system_info
        })
    
    def _check_feature_compatibility(self, feature_id: str, feature_info: Dict[str, Any]) -> List[str]:
        """Check if a specific feature is compatible with the current system."""
        issues = []
        requirements = feature_info.get("requirements", {})
        
        # Check RAM requirement
        if "min_ram_gb" in requirements:
            if self.system_info["ram_total_gb"] < requirements["min_ram_gb"]:
                issues.append(feature_info["issues"].get("low_ram", f"Requires {requirements['min_ram_gb']}GB RAM"))
        
        # Check CPU requirement
        if "min_cpu_cores" in requirements:
            if self.system_info["cpu_cores"] < requirements["min_cpu_cores"]:
                issues.append(feature_info["issues"].get("weak_cpu", f"Requires {requirements['min_cpu_cores']} CPU cores"))
        
        # Check GPU requirements
        gpu_vendor = self.system_info["gpu_info"]["vendor"]
        
        if "gpu_whitelist" in requirements:
            if gpu_vendor not in requirements["gpu_whitelist"]:
                issues.append(feature_info["issues"].get("unsupported_gpu", f"GPU vendor {gpu_vendor} not supported"))
        
        if "gpu_blacklist" in requirements:
            gpu_name = self.system_info["gpu_info"]["name"].lower()
            for blacklisted_gpu in requirements["gpu_blacklist"]:
                if blacklisted_gpu.lower() in gpu_name:
                    issues.append(feature_info["issues"].get("intel_gpu", f"GPU {blacklisted_gpu} may have issues"))
        
        # Check admin privileges
        if requirements.get("admin_required", False):
            if not self.system_info["admin_privileges"]:
                issues.append(feature_info["issues"].get("no_admin", "Requires administrator privileges"))
        
        # Check OS version
        if "os_min_build" in requirements:
            try:
                current_build = int(self.system_info["os_build"])
                min_build = int(requirements["os_min_build"])
                if current_build < min_build:
                    issues.append(feature_info["issues"].get("old_os", "Requires newer Windows version"))
            except:
                pass
        
        # Check virtual environment
        if self.system_info["virtualization"]:
            if feature_id in ["advanced_registry_tweaks", "real_time_monitoring"]:
                issues.append(feature_info["issues"].get("virtual_env", "Not recommended in virtual environments"))
        
        # Check GameLoop installation
        if not self.system_info["game_loop_installed"]:
            if feature_id in ["shadow_control", "ai_optimizer"]:
                issues.append("GameLoop not properly installed")
        
        return issues
    
    def is_feature_enabled(self, feature_id: str) -> bool:
        """Check if a feature is enabled (not disabled due to compatibility)."""
        return feature_id not in self.disabled_features
    
    def get_disabled_features(self) -> List[str]:
        """Get list of disabled features with reasons."""
        disabled_info = []
        
        for feature_id in self.disabled_features:
            if feature_id in self.compatibility_matrix:
                feature_info = self.compatibility_matrix[feature_id]
                issues = self._check_feature_compatibility(feature_id, feature_info)
                
                disabled_info.append({
                    "id": feature_id,
                    "name": feature_info["name"],
                    "description": feature_info["description"],
                    "reasons": issues
                })
        
        return disabled_info
    
    def get_warnings(self) -> List[str]:
        """Get all compatibility warnings."""
        return self.warnings.copy()
    
    def enable_feature_override(self, feature_id: str) -> bool:
        """
        Manually enable a feature (override compatibility check).
        Returns True if successful, False if feature doesn't exist.
        """
        if feature_id in self.compatibility_matrix:
            if feature_id in self.disabled_features:
                self.disabled_features.remove(feature_id)
                self.compatibility_updated.emit({
                    "disabled_features": list(self.disabled_features),
                    "warnings": self.warnings,
                    "system_info": self.system_info,
                    "override": feature_id
                })
            return True
        return False
    
    def disable_feature_manually(self, feature_id: str) -> bool:
        """
        Manually disable a feature.
        Returns True if successful, False if feature doesn't exist.
        """
        if feature_id in self.compatibility_matrix:
            self.disabled_features.add(feature_id)
            self.compatibility_updated.emit({
                "disabled_features": list(self.disabled_features),
                "warnings": self.warnings,
                "system_info": self.system_info,
                "manual_disable": feature_id
            })
            return True
        return False
    
    def get_system_report(self) -> Dict[str, Any]:
        """Get comprehensive system compatibility report."""
        return {
            "system_info": self.system_info,
            "compatibility_matrix": self.compatibility_matrix,
            "disabled_features": list(self.disabled_features),
            "warnings": self.warnings,
            "enabled_features": [f for f in self.compatibility_matrix.keys() if f not in self.disabled_features]
        }
    
    def export_compatibility_report(self, file_path: str) -> bool:
        """Export compatibility report to file."""
        try:
            import json
            report = self.get_system_report()
            with open(file_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            return True
        except:
            return False
