from PyQt5 import QtCore, QtWidgets, QtGui
from .app_functions import Game
from .gfx import GFX
from .other import Other
from .ui import Ui_MainWindow
from .core import SystemOptimizer, GameWatcher, MonitorStats, AIDynamicOptimizer
from .system import SystemTweaks


class Window(QtWidgets.QMainWindow, Game):
    def __init__(self, app_name, app_version):
        super(Window, self).__init__()
        Game.__init__(self)  # legacy compat
        
        self.app_name = app_name
        self.app_version = app_version
        
        # Core Modules
        self.optimizer = SystemOptimizer()
        self.watcher = GameWatcher()
        self.monitor = MonitorStats()
        self.ai = AIDynamicOptimizer(self.optimizer)
        
        # Thread Connections
        self.watcher.game_detected.connect(self._on_game_detected)
        self.watcher.process_info.connect(lambda msg: self.show_status_message(msg))
        self.monitor.stats_updated.connect(self._on_stats_updated)
        
        # Start Threads
        self.watcher.start()
        self.monitor.start()

        # UI Setup
        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.appname_label.setText(f"{app_name} {app_version}")
        self.timer = None
        
        # Apply programmatic layout fixes to prevent overlaps
        self._fix_ui_layouts()

        # Setup GFX and Other
        self.GFX = GFX(self)
        self.Other = Other(self)
        self.System = SystemTweaks(self)

        # Drag variables
        self.draggable = True
        self.drag_start_position = None

        # Button signals
        self.ui.gfx_button.clicked.connect(lambda: self.buttonClicked(self.ui.gfx_button, self.ui.gfx_page))
        self.ui.other_button.clicked.connect(lambda: self.buttonClicked(self.ui.other_button, self.ui.other_page))
        self.ui.system_button.clicked.connect(lambda: self.buttonClicked(self.ui.system_button, self.ui.system_page))
        self.ui.about_button.clicked.connect(lambda: self.buttonClicked(self.ui.about_button, self.ui.about_page))
        self.ui.close_btn.clicked.connect(self.close)
        self.ui.minimize_btn.clicked.connect(lambda: self.setWindowState(QtCore.Qt.WindowMinimized))
        
        # System Tray Init
        self._init_system_tray()

        # Programmatically Add Performance Monitor Frame
        self._init_perf_monitor()

        # Update Other Page Buttons to Performance Modes
        self.ui.glsmartsettings_other_btn.setText("LOW-END MODE")
        self.ui.gloptimizer_other_btn.setText("BALANCED MODE")
        self.ui.all_other_btn.setText("COMPETITIVE MODE (MAX)")
        
        self.ui.all_other_btn.setToolTip("Maximum FPS and lowest latency.")
        
        # Add Manual Update Button to About Page logic
        if hasattr(self.ui, 'about_label_text'):
            # This is a bit of a hack to add a button to the about page programmatically
            self.update_check_btn = QtWidgets.QPushButton("🔄 CHECK FOR UPDATES NOW", self.ui.about_page)
            self.update_check_btn.setGeometry(QtCore.QRect(400, 600, 300, 50))
            self.update_check_btn.clicked.connect(self._manual_update_check)
            self.update_check_btn.show()

    def _manual_update_check(self):
        self.show_status_message("Checking for updates...")
        # We reuse the logic from main.py by importing it or triggering a signal
        # For simplicity, we can just instantiate the CheckUpdateThread here
        from .update import CheckUpdateThread
        # Note: GITHUB_REPO_API would need to be accessible
        repo = "https://api.github.com/repos/Nitrodz00/NITRO-TOOLS/releases/latest"
        self._manual_checker = CheckUpdateThread(self.app_version, repo)
        self._manual_checker.update_available.connect(self._on_manual_update_avail)
        self._manual_checker.no_update.connect(lambda: self.show_status_message("You are using the latest version!"))
        self._manual_checker.check_failed.connect(lambda: self.show_status_message("Update check failed. Check internet."))
        self._manual_checker.start()

    def _on_manual_update_avail(self, ver, url, name, size, changelog):
        from .update import UpdateWindow
        self._manual_upd_win = UpdateWindow(ver, url, name, size, changelog)
        self._manual_upd_win.show()

    def _init_system_tray(self):
        self.tray_icon = QtWidgets.QSystemTrayIcon(self)
        icon_path = self.resource_path("assets/icons/logo.ico")
        self.tray_icon.setIcon(QtGui.QIcon(icon_path))
        
        tray_menu = QtWidgets.QMenu()
        show_action = tray_menu.addAction("Show Dashboard")
        show_action.triggered.connect(self.showNormal)
        
        tray_menu.addSeparator()
        
        optimize_now = tray_menu.addAction("Optimize System Now")
        optimize_now.triggered.connect(lambda: self.optimizer.clean_cache())
        
        exit_action = tray_menu.addAction("Exit NITROTOOLS")
        exit_action.triggered.connect(self._quit_from_tray)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._on_tray_icon_activated)
        self.tray_icon.show()

    def _quit_from_tray(self):
        self._stop_background_threads()
        QtWidgets.QApplication.quit()

    def _on_tray_icon_activated(self, reason):
        if reason in (QtWidgets.QSystemTrayIcon.Trigger, QtWidgets.QSystemTrayIcon.DoubleClick):
            self.showNormal()
            self.activateWindow()
            self.raise_()

    def _init_perf_monitor(self):
        # Move Monitor to Top-Right Header with elegant transparent style
        self.monitor_frame = QtWidgets.QFrame(self.ui.centralwidget)
        self.monitor_frame.setObjectName("MonitorFrame")
        self.monitor_frame.setGeometry(QtCore.QRect(600, 10, 500, 45))
        self.monitor_frame.setStyleSheet("background: rgba(30, 0, 60, 0.4); border-radius: 8px;")
        
        layout = QtWidgets.QHBoxLayout(self.monitor_frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        self.header_fps_label = QtWidgets.QLabel("FPS: 0")
        self.header_fps_label.setStyleSheet("color: #00ffca; font-size: 22px; font-weight: 900; font-family: 'Agency FB';")
        
        self.header_cpu_label = QtWidgets.QLabel("CPU: 0%")
        self.header_cpu_label.setStyleSheet("color: #ffffff; font-size: 13px; font-weight: bold; font-family: 'Segoe UI';")
        
        self.header_gpu_label = QtWidgets.QLabel("GPU: 0%")
        self.header_gpu_label.setStyleSheet("color: #ffffff; font-size: 13px; font-weight: bold; font-family: 'Segoe UI';")
        
        self.header_ram_label = QtWidgets.QLabel("RAM: 0%")
        self.header_ram_label.setStyleSheet("color: #ffffff; font-size: 13px; font-weight: bold; font-family: 'Segoe UI';")
        
        self.ai_status = QtWidgets.QLabel("[ AI STANDBY ]")
        self.ai_status.setStyleSheet("color: #ff00ff; font-weight: 800; font-size: 10px; letter-spacing: 1px;")
        
        layout.addWidget(self.header_fps_label)
        layout.addStretch()
        layout.addWidget(self.header_cpu_label)
        layout.addWidget(self.header_gpu_label)
        layout.addWidget(self.header_ram_label)
        layout.addWidget(self.ai_status)
        
        self.monitor_frame.show()

    def _fix_ui_layouts(self):
        """Fix hardcoded UI overlaps from the .ui file."""
        try:
            # 1. Increase Frame Heights to prevent clipping
            self.ui.GraphicsFrame.setMinimumHeight(130)
            self.ui.FramerateFrame.setMinimumHeight(130)
            self.ui.ShadowFrame.setMinimumHeight(130)
            self.ui.StyleFrame.setMinimumHeight(240)
            
            # 2. Add Spacing to the main GFX grid
            if hasattr(self.ui, 'gridLayout'):
                self.ui.gridLayout.setVerticalSpacing(40)  # Increased from 25
                self.ui.gridLayout.setHorizontalSpacing(30)
                self.ui.gridLayout.setContentsMargins(20, 20, 20, 20)
            
            # Position elements SAFELY inside their respective frames with safe font sizes
            label_style = "color: #ffffff; font-weight: bold; background: transparent;"
            
            # Graphics — label geometry fixed in ui.py (y=5, w=200)
            if hasattr(self.ui, 'layoutWidget'):
                self.ui.layoutWidget.setGeometry(QtCore.QRect(11, 55, 1060, 50))
            
            # Framerate — label geometry fixed in ui.py (y=5, w=200)
            if hasattr(self.ui, 'layoutWidget1'):
                self.ui.layoutWidget1.setGeometry(QtCore.QRect(10, 55, 1060, 50))
            
            # Shadow — geometry fixed in ui.py (setMinimumHeight=120, label y=5)
            # No override needed here, the frame expands correctly.
            
            # Resolution
            if hasattr(self.ui, 'resolution_label'):
                self.ui.resolution_label.setGeometry(QtCore.QRect(10, 5, 250, 40))
                self.ui.resolution_label.setStyleSheet(label_style + "font-size: 20px;")
            if hasattr(self.ui, 'resolution_btn'):
                self.ui.resolution_btn.setGeometry(QtCore.QRect(10, 55, 220, 50))
            
            # --- PROGRAMMATICALLY ADD SYSTEM PAGE ---
            if not hasattr(self.ui, 'system_page'):
                self.ui.system_page = QtWidgets.QWidget()
                self.ui.system_page.setObjectName("system_page")
                
                system_layout = QtWidgets.QVBoxLayout(self.ui.system_page)
                system_layout.setContentsMargins(50, 40, 50, 40)
                system_layout.setSpacing(20)
                
                title = QtWidgets.QLabel("System Optimization Pro")
                title.setStyleSheet("font-size: 32px; color: #ffffff; font-weight: 800;")
                system_layout.addWidget(title)
                
                desc = QtWidgets.QLabel("Boost your system stability and priority for maximum gaming performance.")
                desc.setStyleSheet("color: #aaaaaa; font-size: 13px;")
                system_layout.addWidget(desc)
                
                # Button Config
                btn_h = 52
                
                # High Priority Button
                self.ui.high_priority_btn = QtWidgets.QPushButton("🚀 ACTIVATE HIGH PRIORITY (GAMELOOP)")
                self.ui.high_priority_btn.setMinimumHeight(btn_h)
                system_layout.addWidget(self.ui.high_priority_btn)

                # CPU Affinity Button
                self.ui.cpu_affinity_btn = QtWidgets.QPushButton("🧠 OPTIMIZE CPU CORES (AFFINITY)")
                self.ui.cpu_affinity_btn.setMinimumHeight(btn_h)
                self.ui.cpu_affinity_btn.setStyleSheet("background: #003366; border: 2px solid #00ffca;")
                system_layout.addWidget(self.ui.cpu_affinity_btn)

                # Power Plan Buttons
                self.ui.high_perf_power_btn = QtWidgets.QPushButton("⚡ ACTIVATE HIGH PERFORMANCE")
                self.ui.high_perf_power_btn.setMinimumHeight(btn_h)
                system_layout.addWidget(self.ui.high_perf_power_btn)

                self.ui.ultimate_perf_power_btn = QtWidgets.QPushButton("💎 ACTIVATE ULTIMATE PERFORMANCE")
                self.ui.ultimate_perf_power_btn.setMinimumHeight(btn_h)
                self.ui.ultimate_perf_power_btn.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ffcc00, stop:1 #ff00ff); color: #000; font-weight: 900;")
                system_layout.addWidget(self.ui.ultimate_perf_power_btn)

                # RAM Cleaner Button
                self.ui.ram_cleaner_btn = QtWidgets.QPushButton("🧹 CLEAN RAM STANDBY LIST")
                self.ui.ram_cleaner_btn.setMinimumHeight(btn_h)
                self.ui.ram_cleaner_btn.setStyleSheet("background: #1a0033; border: 2px solid #ff00ff;")
                system_layout.addWidget(self.ui.ram_cleaner_btn)

                # Ping Stabilizer Button
                self.ui.ping_stab_btn = QtWidgets.QPushButton("📡 STABILIZE PING (NETWORK PRIORITY)")
                self.ui.ping_stab_btn.setMinimumHeight(btn_h)
                self.ui.ping_stab_btn.setStyleSheet("background: #004d00; border: 2px solid #00ff00;")
                system_layout.addWidget(self.ui.ping_stab_btn)
                
                exp_spacer = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
                system_layout.addItem(exp_spacer)
                
                self.ui.stackedWidget.addWidget(self.ui.system_page)
                
            # Add System Button to Sidebar with CORRECT width 168 to match others
            if not hasattr(self.ui, 'system_button'):
                self.ui.system_button = QtWidgets.QPushButton("SYSTEM", self.ui.PagesFrame)
                self.ui.system_button.setObjectName("system_button")
                self.ui.system_button.setGeometry(QtCore.QRect(0, 170, 168, 80)) # PERFECT MATCH
                self.ui.system_button.setCheckable(True)
                self.ui.system_button.show()

            # 4. Status Bar Overlap Fix
            if hasattr(self.ui, 'appstatus_label'): self.ui.appstatus_label.setGeometry(QtCore.QRect(10, 680, 100, 40))
            if hasattr(self.ui, 'appstatus_text_lable'): self.ui.appstatus_text_lable.setGeometry(QtCore.QRect(120, 680, 700, 40))

            # 5. OTHER page spacing refinement
            if hasattr(self.ui, 'optimizer_label'): self.ui.optimizer_label.setGeometry(QtCore.QRect(30, 20, 400, 50))
            if hasattr(self.ui, 'shortcut_label'): self.ui.shortcut_label.setGeometry(QtCore.QRect(520, 20, 400, 50))
            
            # 6. Sidebar & Global Buttons - Width MUST be 168 to match buttons
            if hasattr(self.ui, 'PagesFrame'): self.ui.PagesFrame.setGeometry(QtCore.QRect(1124, 70, 168, 650))
        except Exception as e:
            # Prevent minor UI glitches from crashing the whole app
            print(f"Non-critical UI layout adjustment failed: {e}")

        # ui.py sets PagesFrame QPushButton:checked { border-image: menu_checked.png } — causes green/yellow edge artifact
        self.ui.PagesFrame.setStyleSheet("")
        
        sidebar_style = """
            QPushButton {
                background: rgba(25, 0, 50, 0.5);
                border: 2px solid #b300b3;
                border-radius: 8px;
                color: #d1c4e9;
                font-size: 20px;
                font-weight: 800;
                border-image: none;
                background-origin: border;
                background-clip: padding;
            }
            QPushButton:hover {
                background: rgba(255, 0, 255, 0.1);
                border: 2px solid #00ffca;
                color: #ffffff;
            }
            QPushButton:checked {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff00ff, stop:1 #800080);
                color: #ffffff;
                border: 2px solid #ffffff;
                border-image: none;
            }
        """
        self.ui.gfx_button.setStyleSheet(sidebar_style)
        self.ui.other_button.setStyleSheet(sidebar_style)
        self.ui.system_button.setStyleSheet(sidebar_style)
        self.ui.about_button.setStyleSheet(sidebar_style)
        
        # Consistent global action buttons fix
        action_btn_style = """
            QPushButton {
                background: #1a0033;
                border: 1px solid #ff00ff;
                border-radius: 6px;
                color: #ffffff;
                font-weight: bold;
                padding-bottom: 3px;
            }
            QPushButton:hover {
                background: #ff00ff;
                color: #000000;
            }
            QPushButton:checked {
                background: #00ffca;
                color: #000000;
                border: 1px solid #ffffff;
            }
        """
        self.ui.connect_gameloop_btn.setStyleSheet(action_btn_style)
        self.ui.submit_gfx_btn.setStyleSheet(action_btn_style)

    def _on_stats_updated(self, stats: dict):
        """Update live dashboard stats and run AI Dynamic Optimizer."""
        fps = int(stats['fps'])
        fps_str = f"{fps:02d}" if fps < 100 else str(fps)
        self.header_fps_label.setText(f"{fps_str} FPS")
        
        # Color based on FPS quality
        if fps >= 85: color = "#00ffca"
        elif fps >= 55: color = "#ffff00"
        else: color = "#ff4d4d"
        self.header_fps_label.setStyleSheet(f"color: {color}; font-size: 24px; font-weight: 900; font-family: 'Agency FB';")
        self.header_cpu_label.setText(f"CPU: {int(stats['cpu_percent'])}%")
        self.header_gpu_label.setText(f"GPU: {int(stats['gpu_percent'])}%")
        self.header_ram_label.setText(f"RAM: {int(stats['ram_percent'])}%")
        
        # Evaluate stats with AI (Part 2 - Dynamic Optimization)
        if self.watcher.game_running:
            self.ai.evaluate(stats)
            self.ai_status.setText(f"AI: {self.ai.last_mode.upper()} Mode Active")
            self.ai_status.setStyleSheet("color: #00ffff; font-style: italic; font-size: 11px;")
        else:
            self.ai_status.setText("AI: Waiting for Game...")
            self.ai_status.setStyleSheet("color: #aaaaaa; font-style: italic; font-size: 11px;")

    def _on_game_detected(self, running: bool):
        if running:
            self.show_status_message("GameLoop Detected - Auto-Boost Activated!", duration=10)
            self.optimizer.apply_performance_mode('competitive') # Auto high perf when gaming
        else:
            self.show_status_message("Game Closed - Standing by.")

    def buttonClicked(self, button, page):
        self.ui.gfx_button.setChecked(button == self.ui.gfx_button)
        self.ui.other_button.setChecked(button == self.ui.other_button)
        self.ui.system_button.setChecked(button == self.ui.system_button)
        self.ui.about_button.setChecked(button == self.ui.about_button)
        self.ui.stackedWidget.setCurrentWidget(page)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and self.draggable:
            self.drag_start_position = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.draggable and self.drag_start_position is not None:
            if event.buttons() & QtCore.Qt.LeftButton:
                self.move(self.pos() + event.globalPos() - self.drag_start_position)
                self.drag_start_position = event.globalPos()

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.drag_start_position = None

    def show_status_message(self, message, duration=5):
        if self.timer and self.timer.isActive():
            self.timer.stop()
        self.ui.appstatus_text_lable.setText(message)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(lambda: self.ui.appstatus_text_lable.setText(""))
        self.timer.start(duration * 1000)

    def closeEvent(self, event):
        """Override close to minimize to tray instead of quitting."""
        if self.tray_icon.isVisible():
            self.hide()
            self.tray_icon.showMessage(
                self.app_name,
                "NITROTOOLS is still running in the background.",
                QtWidgets.QSystemTrayIcon.Information,
                2000
            )
            event.ignore()
        else:
            self._stop_background_threads()
            event.accept()

    def _stop_background_threads(self):
        self.watcher.stop()
        self.monitor.stop()
