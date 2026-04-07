"""
Expert Mode UI for NITROTOOLS
Professional settings interface for advanced users.
"""

import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, 
                           QGroupBox, QLabel, QSlider, QCheckBox, QComboBox, 
                           QPushButton, QSpinBox, QGridLayout, QScrollArea,
                           QFrame, QSplitter, QTextEdit, QProgressBar)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor
from .core.expert_mode import ExpertMode
from .core.compatibility_manager import CompatibilityManager


class ExpertModeUI(QWidget):
    """
    Expert Mode User Interface
    Provides advanced settings and professional controls.
    """
    
    settings_changed = pyqtSignal(dict)
    settings_applied = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.expert_mode = ExpertMode()
        self.compatibility_manager = CompatibilityManager()
        
        self.setup_ui()
        self.connect_signals()
        self.load_current_settings()
        
    def setup_ui(self):
        """Setup the expert mode interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("🎛️ EXPERT MODE")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setStyleSheet("color: #ff00ff; margin-bottom: 10px;")
        
        self.apply_all_btn = QPushButton("Apply All Settings")
        self.apply_all_btn.setStyleSheet("""
            QPushButton {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
            }
        """)
        
        self.reset_all_btn = QPushButton("Reset All")
        self.reset_all_btn.setStyleSheet("""
            QPushButton {
                background: #444;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background: #555;
            }
        """)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.apply_all_btn)
        header_layout.addWidget(self.reset_all_btn)
        
        layout.addLayout(header_layout)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #444;
                background: #2a2a2a;
                border-radius: 8px;
            }
            QTabBar::tab {
                background: #333;
                color: #fff;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: #667eea;
            }
            QTabBar::tab:hover {
                background: #555;
            }
        """)
        
        # Create category tabs
        self.create_cpu_tab()
        self.create_gpu_tab()
        self.create_memory_tab()
        self.create_network_tab()
        self.create_advanced_tab()
        
        layout.addWidget(self.tab_widget)
        
        # Status bar
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(self.status_label)
        
        # Progress bar for operations
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #444;
                border-radius: 3px;
                text-align: center;
                background: #333;
            }
            QProgressBar::chunk {
                background: #667eea;
                border-radius: 2px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
    def create_cpu_tab(self):
        """Create CPU optimization tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # CPU Affinity Group
        affinity_group = QGroupBox("CPU Affinity Control")
        affinity_layout = QVBoxLayout(affinity_group)
        
        self.cpu_affinity_combo = QComboBox()
        self.cpu_affinity_combo.addItems(["Auto", "Manual", "Performance", "Balanced"])
        affinity_layout.addWidget(QLabel("Affinity Mode:"))
        affinity_layout.addWidget(self.cpu_affinity_combo)
        
        self.priority_boost_check = QCheckBox("Priority Boost (High Priority for Game)")
        self.priority_boost_check.setChecked(True)
        affinity_layout.addWidget(self.priority_boost_check)
        
        self.hyperthreading_check = QCheckBox("Disable Hyperthreading (Better Single-Core Performance)")
        affinity_layout.addWidget(self.hyperthreading_check)
        
        self.power_throttling_check = QCheckBox("Disable Power Throttling")
        self.power_throttling_check.setChecked(False)
        affinity_layout.addWidget(self.power_throttling_check)
        
        layout.addWidget(affinity_group)
        
        # CPU Information
        info_group = QGroupBox("CPU Information")
        info_layout = QGridLayout(info_group)
        
        # Get CPU info
        import psutil
        cpu_info = {
            "Cores": psutil.cpu_count(logical=False),
            "Threads": psutil.cpu_count(logical=True),
            "Max Frequency": f"{psutil.cpu_freq().max:.0f} MHz" if psutil.cpu_freq() else "Unknown"
        }
        
        row = 0
        for key, value in cpu_info.items():
            info_layout.addWidget(QLabel(f"{key}:"), row, 0)
            info_layout.addWidget(QLabel(str(value)), row, 1)
            row += 1
        
        layout.addWidget(info_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "🖥️ CPU")
        
    def create_gpu_tab(self):
        """Create GPU optimization tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Shader Cache Group
        shader_group = QGroupBox("Shader Cache")
        shader_layout = QVBoxLayout(shader_group)
        
        self.shader_cache_combo = QComboBox()
        self.shader_cache_combo.addItems(["Default", "Maximum", "Disabled"])
        self.shader_cache_combo.setCurrentText("Maximum")
        shader_layout.addWidget(QLabel("Shader Cache Size:"))
        shader_layout.addWidget(self.shader_cache_combo)
        
        layout.addWidget(shader_group)
        
        # Texture Quality Group
        texture_group = QGroupBox("Texture Settings")
        texture_layout = QVBoxLayout(texture_group)
        
        texture_layout.addWidget(QLabel("Texture Quality:"))
        self.texture_quality_slider = QSlider(Qt.Horizontal)
        self.texture_quality_slider.setRange(1, 5)
        self.texture_quality_slider.setValue(3)
        self.texture_quality_slider.setTickPosition(QSlider.TicksBelow)
        self.texture_quality_slider.setTickInterval(1)
        texture_layout.addWidget(self.texture_quality_slider)
        
        self.texture_quality_label = QLabel("Medium (3)")
        texture_layout.addWidget(self.texture_quality_label)
        
        layout.addWidget(texture_group)
        
        # Anisotropic Filtering
        af_group = QGroupBox("Anisotropic Filtering")
        af_layout = QVBoxLayout(af_group)
        
        self.af_slider = QSlider(Qt.Horizontal)
        self.af_slider.setRange(0, 16)
        self.af_slider.setValue(8)
        self.af_slider.setTickPosition(QSlider.TicksBelow)
        self.af_slider.setTickInterval(4)
        af_layout.addWidget(QLabel("AF Level:"))
        af_layout.addWidget(self.af_slider)
        
        self.af_label = QLabel("8x")
        af_layout.addWidget(self.af_label)
        
        layout.addWidget(af_group)
        
        # VSync
        vsync_group = QGroupBox("Vertical Sync")
        vsync_layout = QVBoxLayout(vsync_group)
        
        self.vsync_combo = QComboBox()
        self.vsync_combo.addItems(["Off", "On", "Adaptive"])
        self.vsync_combo.setCurrentText("Off")
        vsync_layout.addWidget(QLabel("VSync Mode:"))
        vsync_layout.addWidget(self.vsync_combo)
        
        layout.addWidget(vsync_group)
        layout.addStretch()
        
        # Connect slider signals
        self.texture_quality_slider.valueChanged.connect(
            lambda v: self.texture_quality_label.setText(f"{['Low', 'Medium-Low', 'Medium', 'Medium-High', 'Ultra'][v-1]} ({v})")
        )
        self.af_slider.valueChanged.connect(
            lambda v: self.af_label.setText(f"{v}x" if v > 0 else "Off")
        )
        
        self.tab_widget.addTab(tab, "🎮 GPU")
        
    def create_memory_tab(self):
        """Create memory optimization tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # RAM Cleanup Group
        ram_group = QGroupBox("RAM Management")
        ram_layout = QVBoxLayout(ram_group)
        
        ram_layout.addWidget(QLabel("Cleanup Interval (minutes):"))
        self.ram_cleanup_spinbox = QSpinBox()
        self.ram_cleanup_spinbox.setRange(1, 30)
        self.ram_cleanup_spinbox.setValue(5)
        ram_layout.addWidget(self.ram_cleanup_spinbox)
        
        self.standby_cleanup_check = QCheckBox("Periodic Standby List Cleanup")
        self.standby_cleanup_check.setChecked(True)
        ram_layout.addWidget(self.standby_cleanup_check)
        
        layout.addWidget(ram_group)
        
        # Pagefile Group
        pagefile_group = QGroupBox("Pagefile Optimization")
        pagefile_layout = QVBoxLayout(pagefile_group)
        
        self.pagefile_check = QCheckBox("Optimize Windows Page File Settings")
        pagefile_layout.addWidget(self.pagefile_check)
        
        self.memory_compression_check = QCheckBox("Enable Memory Compression")
        self.memory_compression_check.setChecked(True)
        pagefile_layout.addWidget(self.memory_compression_check)
        
        layout.addWidget(pagefile_group)
        
        # Memory Information
        info_group = QGroupBox("Memory Information")
        info_layout = QGridLayout(info_group)
        
        import psutil
        memory = psutil.virtual_memory()
        
        info_layout.addWidget(QLabel("Total RAM:"), 0, 0)
        info_layout.addWidget(QLabel(f"{memory.total // (1024**3)} GB"), 0, 1)
        
        info_layout.addWidget(QLabel("Available:"), 1, 0)
        info_layout.addWidget(QLabel(f"{memory.available // (1024**3)} GB"), 1, 1)
        
        info_layout.addWidget(QLabel("Usage:"), 2, 0)
        info_layout.addWidget(QLabel(f"{memory.percent}%"), 2, 1)
        
        layout.addWidget(info_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "💾 Memory")
        
    def create_network_tab(self):
        """Create network optimization tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # TCP Optimization Group
        tcp_group = QGroupBox("TCP/IP Optimization")
        tcp_layout = QVBoxLayout(tcp_group)
        
        self.tcp_optimization_check = QCheckBox("Optimize TCP Settings for Gaming")
        self.tcp_optimization_check.setChecked(True)
        tcp_layout.addWidget(self.tcp_optimization_check)
        
        self.dns_caching_check = QCheckBox("Enable Aggressive DNS Caching")
        self.dns_caching_check.setChecked(True)
        tcp_layout.addWidget(self.dns_caching_check)
        
        layout.addWidget(tcp_group)
        
        # Network Throttling Group
        throttle_group = QGroupBox("Network Throttling")
        throttle_layout = QVBoxLayout(throttle_group)
        
        self.network_throttling_check = QCheckBox("Disable Network Throttling")
        self.network_throttling_check.setChecked(True)
        throttle_layout.addWidget(self.network_throttling_check)
        
        self.qos_priority_check = QCheckBox("Set QoS Priority for Gaming Traffic")
        self.qos_priority_check.setChecked(True)
        throttle_layout.addWidget(self.qos_priority_check)
        
        layout.addWidget(throttle_group)
        
        # Network Status
        status_group = QGroupBox("Network Status")
        status_layout = QVBoxLayout(status_group)
        
        self.network_status_label = QLabel("Checking network...")
        status_layout.addWidget(self.network_status_label)
        
        # Test network button
        test_btn = QPushButton("Test Network Connection")
        test_btn.clicked.connect(self.test_network)
        status_layout.addWidget(test_btn)
        
        layout.addWidget(status_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "🌐 Network")
        
    def create_advanced_tab(self):
        """Create advanced tweaks tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Registry Tweaks Group
        registry_group = QGroupBox("Registry Optimizations")
        registry_layout = QVBoxLayout(registry_group)
        
        self.registry_tweaks_check = QCheckBox("Apply Advanced Registry Optimizations")
        registry_layout.addWidget(self.registry_tweaks_check)
        
        self.services_optimization_check = QCheckBox("Disable Unnecessary Windows Services")
        registry_layout.addWidget(self.services_optimization_check)
        
        layout.addWidget(registry_group)
        
        # Kernel Mode Group
        kernel_group = QGroupBox("Kernel-Level Optimizations")
        kernel_layout = QVBoxLayout(kernel_group)
        
        self.kernel_mode_check = QCheckBox("Enable Kernel-Level Optimizations (Requires Restart)")
        kernel_layout.addWidget(self.kernel_mode_check)
        
        self.real_time_priority_check = QCheckBox("Set Game Process to Real-Time Priority (Use with Caution)")
        kernel_layout.addWidget(self.real_time_priority_check)
        
        layout.addWidget(kernel_group)
        
        # Warning
        warning_frame = QFrame()
        warning_frame.setStyleSheet("""
            QFrame {
                background: #442222;
                border: 1px solid #ff6666;
                border-radius: 4px;
                padding: 10px;
            }
        """)
        warning_layout = QVBoxLayout(warning_frame)
        
        warning_label = QLabel("⚠️ WARNING: Advanced tweaks can affect system stability. Use with caution and create a system restore point before applying.")
        warning_label.setWordWrap(True)
        warning_label.setStyleSheet("color: #ffaaaa;")
        warning_layout.addWidget(warning_label)
        
        layout.addWidget(warning_frame)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "⚙️ Advanced")
        
    def connect_signals(self):
        """Connect UI signals to expert mode."""
        self.apply_all_btn.clicked.connect(self.apply_all_settings)
        self.reset_all_btn.clicked.connect(self.reset_all_settings)
        
        # Connect individual setting changes
        self.cpu_affinity_combo.currentTextChanged.connect(
            lambda v: self.update_setting("cpu_optimization", "cpu_affinity_mode", v)
        )
        self.priority_boost_check.toggled.connect(
            lambda v: self.update_setting("cpu_optimization", "priority_boost", v)
        )
        self.hyperthreading_check.toggled.connect(
            lambda v: self.update_setting("cpu_optimization", "disable_hyperthreading", v)
        )
        self.power_throttling_check.toggled.connect(
            lambda v: self.update_setting("cpu_optimization", "power_throttling", v)
        )
        
        # GPU settings
        self.shader_cache_combo.currentTextChanged.connect(
            lambda v: self.update_setting("gpu_optimization", "shader_cache", v)
        )
        self.vsync_combo.currentTextChanged.connect(
            lambda v: self.update_setting("gpu_optimization", "vsync_mode", v)
        )
        
        # Memory settings
        self.ram_cleanup_spinbox.valueChanged.connect(
            lambda v: self.update_setting("memory_optimization", "ram_cleanup_interval", v)
        )
        self.standby_cleanup_check.toggled.connect(
            lambda v: self.update_setting("memory_optimization", "standby_list_cleanup", v)
        )
        
        # Network settings
        self.tcp_optimization_check.toggled.connect(
            lambda v: self.update_setting("network_optimization", "tcp_optimization", v)
        )
        self.dns_caching_check.toggled.connect(
            lambda v: self.update_setting("network_optimization", "dns_caching", v)
        )
        
        # Advanced settings
        self.registry_tweaks_check.toggled.connect(
            lambda v: self.update_setting("advanced_tweaks", "registry_tweaks", v)
        )
        self.services_optimization_check.toggled.connect(
            lambda v: self.update_setting("advanced_tweaks", "services_optimization", v)
        )
        
        # Connect expert mode signals
        self.expert_mode.settings_changed.connect(self.on_settings_changed)
        self.expert_mode.settings_applied.connect(self.on_settings_applied)
        
    def update_setting(self, category, setting, value):
        """Update a single setting."""
        self.expert_mode.set_setting_value(category, setting, value)
        
    def load_current_settings(self):
        """Load current settings into UI."""
        # Load CPU settings
        cpu_affinity = self.expert_mode.get_setting_value("cpu_optimization", "cpu_affinity_mode")
        if cpu_affinity:
            self.cpu_affinity_combo.setCurrentText(cpu_affinity)
            
        priority_boost = self.expert_mode.get_setting_value("cpu_optimization", "priority_boost")
        if priority_boost is not None:
            self.priority_boost_check.setChecked(priority_boost)
            
        # Load other settings similarly...
        
    def apply_all_settings(self):
        """Apply all expert mode settings."""
        self.status_label.setText("Applying settings...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        self.expert_mode.apply_settings()
        
    def reset_all_settings(self):
        """Reset all settings to defaults."""
        self.expert_mode.reset_to_defaults()
        self.load_current_settings()
        self.status_label.setText("Settings reset to defaults")
        
    def on_settings_changed(self, settings):
        """Handle settings change."""
        self.settings_changed.emit(settings)
        
    def on_settings_applied(self, message):
        """Handle settings applied."""
        self.progress_bar.setVisible(False)
        self.status_label.setText(message)
        self.settings_applied.emit(message)
        
    def test_network(self):
        """Test network connection."""
        self.network_status_label.setText("Testing connection...")
        
        def test():
            try:
                import ping3
                latency = ping3.ping("8.8.8.8", timeout=3)
                if latency:
                    self.network_status_label.setText(f"✅ Connection OK (Latency: {latency*1000:.0f}ms)")
                else:
                    self.network_status_label.setText("❌ Connection failed")
            except:
                self.network_status_label.setText("❌ Network test failed")
                
        # Run test in background
        QTimer.singleShot(100, test)
