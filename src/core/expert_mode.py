"""
Expert Mode Module for NITROTOOLS
Provides advanced settings and fine-tuning options for power users.
"""

import os
import json
import winreg
import subprocess
from typing import Dict, Any, List
from PyQt5.QtCore import QObject, pyqtSignal
from .optimizer import SystemOptimizer


class ExpertMode(QObject):
    """
    Expert Mode with advanced settings for power users.
    Provides fine-grained control over system and game optimizations.
    """
    
    settings_changed = pyqtSignal(dict)
    settings_applied = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.optimizer = SystemOptimizer()
        self.settings_file = os.path.join(os.path.expanduser("~"), "Documents", "nitro_expert_settings.json")
        self.current_settings = self._load_settings()
        
        # Advanced setting categories
        self.categories = {
            "cpu_optimization": {
                "name": "CPU Optimization",
                "settings": {
                    "cpu_affinity_mode": {
                        "type": "combo",
                        "options": ["Auto", "Manual", "Performance", "Balanced"],
                        "default": "Auto",
                        "description": "CPU core assignment strategy"
                    },
                    "priority_boost": {
                        "type": "checkbox",
                        "default": True,
                        "description": "Boost game process priority to High"
                    },
                    "disable_hyperthreading": {
                        "type": "checkbox",
                        "default": False,
                        "description": "Disable hyperthreading for better single-core performance"
                    },
                    "power_throttling": {
                        "type": "checkbox",
                        "default": False,
                        "description": "Disable CPU power throttling"
                    }
                }
            },
            "gpu_optimization": {
                "name": "GPU Optimization",
                "settings": {
                    "shader_cache": {
                        "type": "combo",
                        "options": ["Default", "Maximum", "Disabled"],
                        "default": "Maximum",
                        "description": "Shader cache size optimization"
                    },
                    "texture_quality": {
                        "type": "slider",
                        "min": 1,
                        "max": 5,
                        "default": 3,
                        "description": "Texture quality override (1=Low, 5=Ultra)"
                    },
                    "anisotropic_filtering": {
                        "type": "slider",
                        "min": 0,
                        "max": 16,
                        "default": 8,
                        "description": "Anisotropic filtering level"
                    },
                    "vsync_mode": {
                        "type": "combo",
                        "options": ["Off", "On", "Adaptive"],
                        "default": "Off",
                        "description": "Vertical sync mode"
                    }
                }
            },
            "memory_optimization": {
                "name": "Memory Optimization",
                "settings": {
                    "ram_cleanup_interval": {
                        "type": "slider",
                        "min": 1,
                        "max": 30,
                        "default": 5,
                        "description": "RAM cleanup interval (minutes)"
                    },
                    "standby_list_cleanup": {
                        "type": "checkbox",
                        "default": True,
                        "description": "Periodic standby list cleanup"
                    },
                    "pagefile_optimization": {
                        "type": "checkbox",
                        "default": False,
                        "description": "Optimize Windows page file settings"
                    },
                    "memory_compression": {
                        "type": "checkbox",
                        "default": True,
                        "description": "Enable memory compression"
                    }
                }
            },
            "network_optimization": {
                "name": "Network Optimization",
                "settings": {
                    "tcp_optimization": {
                        "type": "checkbox",
                        "default": True,
                        "description": "Optimize TCP settings for gaming"
                    },
                    "dns_caching": {
                        "type": "checkbox",
                        "default": True,
                        "description": "Enable aggressive DNS caching"
                    },
                    "network_throttling": {
                        "type": "checkbox",
                        "default": True,
                        "description": "Disable network throttling"
                    },
                    "qos_priority": {
                        "type": "checkbox",
                        "default": True,
                        "description": "Set QoS priority for gaming traffic"
                    }
                }
            },
            "advanced_tweaks": {
                "name": "Advanced Tweaks",
                "settings": {
                    "registry_tweaks": {
                        "type": "checkbox",
                        "default": False,
                        "description": "Apply advanced registry optimizations"
                    },
                    "services_optimization": {
                        "type": "checkbox",
                        "default": False,
                        "description": "Disable unnecessary Windows services"
                    },
                    "kernel_mode": {
                        "type": "checkbox",
                        "default": False,
                        "description": "Enable kernel-level optimizations (requires restart)"
                    },
                    "real_time_priority": {
                        "type": "checkbox",
                        "default": False,
                        "description": "Set game process to real-time priority (use with caution)"
                    }
                }
            }
        }
    
    def _load_settings(self) -> Dict[str, Any]:
        """Load expert settings from file."""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        
        # Return default settings
        return {}
    
    def _save_settings(self):
        """Save expert settings to file."""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.current_settings, f, indent=2)
        except Exception as e:
            print(f"Failed to save expert settings: {e}")
    
    def get_categories(self) -> Dict[str, Dict]:
        """Get all available setting categories."""
        return self.categories
    
    def get_setting_value(self, category: str, setting: str) -> Any:
        """Get the current value of a specific setting."""
        if category in self.current_settings and setting in self.current_settings[category]:
            return self.current_settings[category][setting]
        
        # Return default value
        if category in self.categories and setting in self.categories[category]["settings"]:
            return self.categories[category]["settings"][setting]["default"]
        
        return None
    
    def set_setting_value(self, category: str, setting: str, value: Any):
        """Set the value of a specific setting."""
        if category not in self.current_settings:
            self.current_settings[category] = {}
        
        self.current_settings[category][setting] = value
        self.settings_changed.emit({category: {setting: value}})
    
    def apply_settings(self, category: str = None):
        """Apply expert settings to the system."""
        try:
            if category:
                self._apply_category_settings(category)
                self.settings_applied.emit(f"Applied {category} settings")
            else:
                # Apply all categories
                for cat in self.categories.keys():
                    self._apply_category_settings(cat)
                self.settings_applied.emit("Applied all expert settings")
            
            self._save_settings()
            
        except Exception as e:
            self.settings_applied.emit(f"Error applying settings: {str(e)}")
    
    def _apply_category_settings(self, category: str):
        """Apply settings for a specific category."""
        if category == "cpu_optimization":
            self._apply_cpu_settings()
        elif category == "gpu_optimization":
            self._apply_gpu_settings()
        elif category == "memory_optimization":
            self._apply_memory_settings()
        elif category == "network_optimization":
            self._apply_network_settings()
        elif category == "advanced_tweaks":
            self._apply_advanced_tweaks()
    
    def _apply_cpu_settings(self):
        """Apply CPU optimization settings."""
        # CPU Affinity
        affinity_mode = self.get_setting_value("cpu_optimization", "cpu_affinity_mode")
        if affinity_mode != "Auto":
            # Apply specific CPU affinity logic
            pass
        
        # Priority Boost
        if self.get_setting_value("cpu_optimization", "priority_boost"):
            # Set high priority for game processes
            pass
        
        # Power Throttling
        if self.get_setting_value("cpu_optimization", "power_throttling"):
            # Disable CPU power throttling
            self.optimizer.set_registry_dword(
                r"SYSTEM\CurrentControlSet\Control\Power\PowerThrottling",
                "PowerThrottlingOff", 1, winreg.HKEY_LOCAL_MACHINE
            )
    
    def _apply_gpu_settings(self):
        """Apply GPU optimization settings."""
        # Shader Cache
        shader_cache = self.get_setting_value("gpu_optimization", "shader_cache")
        if shader_cache != "Default":
            # Apply shader cache settings
            pass
        
        # VSync Mode
        vsync_mode = self.get_setting_value("gpu_optimization", "vsync_mode")
        # Apply VSync settings through registry or driver settings
        pass
    
    def _apply_memory_settings(self):
        """Apply memory optimization settings."""
        # Pagefile Optimization
        if self.get_setting_value("memory_optimization", "pagefile_optimization"):
            # Optimize Windows page file
            pass
        
        # Memory Compression
        if self.get_setting_value("memory_optimization", "memory_compression"):
            # Enable memory compression
            subprocess.run(["powershell", "-Command", "Enable-MMAgent -MemoryCompression"], 
                         creationflags=0x08000000)
    
    def _apply_network_settings(self):
        """Apply network optimization settings."""
        # TCP Optimization
        if self.get_setting_value("network_optimization", "tcp_optimization"):
            # Apply TCP registry tweaks
            tcp_settings = {
                r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Tcpip\Parameters": {
                    "TcpAckFrequency": 1,
                    "TCPNoDelay": 1,
                    "TcpWindowSize": 65535
                }
            }
            
            for path, settings in tcp_settings.items():
                for key, value in settings.items():
                    self.optimizer.set_registry_dword(path, key, value, winreg.HKEY_LOCAL_MACHINE)
        
        # Network Throttling
        if self.get_setting_value("network_optimization", "network_throttling"):
            self.optimizer.optimize_network()
    
    def _apply_advanced_tweaks(self):
        """Apply advanced system tweaks."""
        # Registry Tweaks
        if self.get_setting_value("advanced_tweaks", "registry_tweaks"):
            # Apply advanced registry optimizations
            advanced_settings = {
                r"SYSTEM\CurrentControlSet\Control\PriorityControl": {
                    "Win32PrioritySeparation": 38
                },
                r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile": {
                    "SystemResponsiveness": 0,
                    "NetworkThrottlingIndex": 0xFFFFFFFF
                }
            }
            
            for path, settings in advanced_settings.items():
                for key, value in settings.items():
                    self.optimizer.set_registry_dword(path, key, value, winreg.HKEY_LOCAL_MACHINE)
        
        # Services Optimization
        if self.get_setting_value("advanced_tweaks", "services_optimization"):
            # Disable unnecessary services
            services_to_disable = [
                "SysMain",  # Superfetch/Prefetch
                "WSearch",  # Windows Search
                "Themes",   # Themes (if not needed)
            ]
            
            for service in services_to_disable:
                try:
                    subprocess.run(["sc", "config", service, "start=disabled"], 
                                 creationflags=0x08000000)
                    subprocess.run(["sc", "stop", service], 
                                 creationflags=0x08000000)
                except:
                    pass
    
    def reset_to_defaults(self, category: str = None):
        """Reset settings to default values."""
        if category:
            if category in self.current_settings:
                del self.current_settings[category]
        else:
            self.current_settings = {}
        
        self._save_settings()
        self.settings_changed.emit({})
    
    def export_settings(self, file_path: str):
        """Export current settings to a file."""
        try:
            with open(file_path, 'w') as f:
                json.dump(self.current_settings, f, indent=2)
            return True
        except:
            return False
    
    def import_settings(self, file_path: str):
        """Import settings from a file."""
        try:
            with open(file_path, 'r') as f:
                self.current_settings = json.load(f)
            self._save_settings()
            self.settings_changed.emit(self.current_settings)
            return True
        except:
            return False
    
    def get_performance_profile(self) -> Dict[str, Any]:
        """Get current performance profile based on settings."""
        profile = {
            "name": "Custom",
            "description": "Custom expert configuration",
            "settings_applied": []
        }
        
        # Analyze settings to determine profile type
        cpu_settings = self.current_settings.get("cpu_optimization", {})
        gpu_settings = self.current_settings.get("gpu_optimization", {})
        
        if (cpu_settings.get("priority_boost") and 
            gpu_settings.get("shader_cache") == "Maximum" and
            self.current_settings.get("network_optimization", {}).get("tcp_optimization")):
            profile["name"] = "Maximum Performance"
            profile["description"] = "Optimized for maximum gaming performance"
        
        return profile
