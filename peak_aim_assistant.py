import sys
import json
import os
import time
import webbrowser
import logging
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QLineEdit, 
                             QCheckBox, QSystemTrayIcon, QMenu, QAction, QMessageBox)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QSharedMemory
from PyQt5.QtGui import QIcon, QFont, QPalette, QColor, QPixmap, QCursor
import keyboard
from pynput.mouse import Button, Listener as MouseListener
from logging.handlers import RotatingFileHandler

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def setup_logging():
    """Setup rotating file logger with millisecond precision"""
    log_file = "peak_aim_log.txt"
    
    # Create logger
    logger = logging.getLogger("PeakAimAssistant")
    logger.setLevel(logging.DEBUG)
    
    # Remove existing handlers
    logger.handlers = []
    
    # Create rotating file handler (2MB per file, keep 2 backups)
    handler = RotatingFileHandler(
        log_file,
        maxBytes=2*1024*1024,  # 2MB
        backupCount=2,
        encoding='utf-8'
    )
    
    # Custom formatter with milliseconds
    class MillisecondFormatter(logging.Formatter):
        def formatTime(self, record, datefmt=None):
            ct = self.converter(record.created)
            t = time.strftime("%Y-%m-%d %H:%M:%S", ct)
            s = "%s.%03d" % (t, record.msecs)
            return s
    
    formatter = MillisecondFormatter('[%(asctime)s] [%(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger

# Initialize logger
logger = setup_logging()

class OverlayWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint | 
            Qt.FramelessWindowHint | 
            Qt.Tool |
            Qt.WindowTransparentForInput
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        layout = QHBoxLayout()
        self.label = QLabel("● INACTIVE | Scope: CLOSED")
        self.label.setFont(QFont("Consolas", 10, QFont.Bold))
        self.update_status(False, False, True)
        
        layout.addWidget(self.label)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        
        logger.info("Overlay window created")
        
    def update_status(self, active, scope_open, show_bg):
        color = "#00FF00" if active else "#FF0000"
        status = "ACTIVE" if active else "INACTIVE"
        scope = "OPEN" if scope_open else "CLOSED"
        
        text = f"● {status} | Scope: {scope}"
        
        if show_bg:
            bg_color = "rgba(0, 0, 0, 180)"
        else:
            bg_color = "transparent"
            
        self.label.setStyleSheet(f"color: {color}; background-color: {bg_color}; padding: 5px;")
        self.label.setText(text)
        self.adjustSize()

class MacroThread(QThread):
    status_update = pyqtSignal(bool, bool)
    
    def __init__(self):
        super().__init__()
        self.enabled = False
        self.scope_toggled = False
        self.o_held = False
        self.right_click_time = 0
        self.running = True
        self.right_click_pressed = False
        logger.info("Macro thread initialized")
    
    def run(self):
        logger.info("Macro thread started")
        
        def on_click(x, y, button, pressed):
            if button == Button.right:
                if pressed:
                    self.right_click_time = time.time()
                    self.right_click_pressed = True
                    logger.debug("MOUSE: Right-click DOWN")
                else:
                    self.right_click_pressed = False
                    hold_duration = (time.time() - self.right_click_time) * 1000
                    logger.debug(f"MOUSE: Right-click UP (held: {hold_duration:.0f}ms)")
                    
                    if hold_duration < 300:
                        old_state = self.scope_toggled
                        self.scope_toggled = not self.scope_toggled
                        logger.info(f"SCOPE: Toggled {old_state} → {self.scope_toggled}")
        
        mouse_listener = MouseListener(on_click=on_click)
        mouse_listener.start()
        logger.info("Mouse listener started")
        
        last_e_state = False
        last_q_state = False
        last_enabled = False
        
        while self.running:
            try:
                # Log macro state changes
                if self.enabled != last_enabled:
                    logger.info(f"STATUS: Macro enabled flag = {self.enabled}")
                    last_enabled = self.enabled
                
                if self.enabled:
                    e_pressed = keyboard.is_pressed('e')
                    q_pressed = keyboard.is_pressed('q')
                    
                    # Log key state changes
                    if e_pressed != last_e_state:
                        logger.debug(f"KEY: E detected: {'DOWN' if e_pressed else 'UP'}")
                        last_e_state = e_pressed
                    
                    if q_pressed != last_q_state:
                        logger.debug(f"KEY: Q detected: {'DOWN' if q_pressed else 'UP'}")
                        last_q_state = q_pressed
                    
                    scope_active = self.scope_toggled or self.right_click_pressed
                    should_hold = (e_pressed or q_pressed) and not scope_active
                    
                    # Log decision logic
                    if (e_pressed or q_pressed):
                        logger.debug(f"SCOPE: Status check - toggle:{self.scope_toggled} rclick:{self.right_click_pressed} active:{scope_active}")
                        logger.debug(f"ACTION: Should hold O = {should_hold} (Q:{q_pressed} E:{e_pressed} Scope:{scope_active})")
                    
                    if should_hold and not self.o_held:
                        try:
                            logger.debug("KEY: Sending keyboard.press('o')")
                            keyboard.press('o')
                            logger.info(f"STATE: o_held changed False → True")
                            self.o_held = True
                        except Exception as e:
                            logger.error(f"ERROR: keyboard.press('o') failed - {str(e)}")
                            logger.error(f"RECOVERY: Attempting to reset o_held state")
                            self.o_held = False
                            
                    elif not should_hold and self.o_held:
                        try:
                            logger.debug("KEY: Sending keyboard.release('o')")
                            keyboard.release('o')
                            logger.info(f"STATE: o_held changed True → False")
                            self.o_held = False
                        except Exception as e:
                            logger.error(f"ERROR: keyboard.release('o') failed - {str(e)}")
                            logger.error(f"RECOVERY: Force setting o_held to False")
                            self.o_held = False
                        
                    self.status_update.emit(True, scope_active)
                else:
                    # Reset key states when disabled
                    if last_e_state or last_q_state:
                        last_e_state = False
                        last_q_state = False
                        logger.debug("KEY: Reset E and Q states (macro disabled)")
                    
                    if self.o_held:
                        try:
                            logger.debug("KEY: Macro disabled - releasing O")
                            keyboard.release('o')
                            logger.info(f"STATE: o_held changed True → False (macro disabled)")
                            self.o_held = False
                        except Exception as e:
                            logger.error(f"ERROR: Failed to release O on disable - {str(e)}")
                            self.o_held = False
                            
                    self.status_update.emit(False, self.scope_toggled)
                
                # Optimized sleep times for CPU usage
                if self.enabled:
                    time.sleep(0.05)  # 50ms when active (20 checks/second)
                else:
                    time.sleep(0.2)   # 200ms when inactive (5 checks/second)
                
            except Exception as e:
                logger.error(f"CRITICAL ERROR in macro thread: {str(e)}")
                logger.error(f"RECOVERY: Attempting to release O key")
                if self.o_held:
                    try:
                        keyboard.release('o')
                        logger.info("RECOVERY: Successfully released O")
                    except:
                        logger.error("RECOVERY: Failed to release O")
                    self.o_held = False
                time.sleep(0.1)
        
        logger.info("Macro thread stopping")
    
    def stop(self):
        logger.info("Macro thread stop requested")
        self.running = False
        if self.o_held:
            try:
                keyboard.release('o')
                logger.info("SHUTDOWN: Released O key")
            except Exception as e:
                logger.error(f"SHUTDOWN: Failed to release O - {str(e)}")

class ClickableLabel(QLabel):
    """Custom clickable label for links"""
    def __init__(self, text, url, parent=None):
        super().__init__(text, parent)
        self.url = url
        self.setCursor(QCursor(Qt.PointingHandCursor))
        
    def mousePressEvent(self, event):
        logger.info(f"UI: Opening URL - {self.url}")
        webbrowser.open(self.url)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        logger.info("═══════════════════════════════════════")
        logger.info("STARTUP: Peak & Aim Assistant v1.0")
        logger.info("═══════════════════════════════════════")
        
        self.settings_file = "settings.json"
        self.load_settings()
        
        self.macro_thread = MacroThread()
        self.macro_thread.status_update.connect(self.update_overlay_status)
        self.macro_thread.start()
        
        self.init_ui()
        self.setup_tray()
        self.setup_overlay()
        
        keyboard.add_hotkey('f8', self.toggle_macro)
        logger.info("STARTUP: F8 hotkey registered")
        
        self.watchdog_timer = QTimer()
        self.watchdog_timer.timeout.connect(self.watchdog_check)
        self.watchdog_timer.start(2000)
        logger.info("STARTUP: Watchdog timer started (2000ms interval)")
        
        self.set_window_icon()
        logger.info("STARTUP: Initialization complete")
        
    def set_window_icon(self):
        """Set window icon"""
        icon_path = resource_path("icon.ico")
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
            self.setWindowIcon(icon)
            logger.debug(f"UI: Window icon loaded from {icon_path}")
        else:
            pixmap = QPixmap(32, 32)
            pixmap.fill(QColor(0, 255, 0))
            self.setWindowIcon(QIcon(pixmap))
            logger.warning("UI: icon.ico not found, using placeholder")
    
    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    self.overlay_x = settings.get('overlay_x', 1600)
                    self.overlay_y = settings.get('overlay_y', 50)
                    self.overlay_bg = settings.get('overlay_bg', True)
                    self.start_minimized = settings.get('start_minimized', False)
                    self.is_first_run = False
                    logger.info(f"SETTINGS: Loaded from {self.settings_file}")
                    logger.debug(f"SETTINGS: overlay_x={self.overlay_x}, overlay_y={self.overlay_y}, bg={self.overlay_bg}, minimized={self.start_minimized}")
            else:
                self.overlay_x = 1600
                self.overlay_y = 50
                self.overlay_bg = True
                self.start_minimized = False
                self.is_first_run = True
                logger.info("SETTINGS: Using defaults (first run)")
        except Exception as e:
            logger.error(f"SETTINGS: Failed to load - {str(e)}")
            self.overlay_x = 1600
            self.overlay_y = 50
            self.overlay_bg = True
            self.start_minimized = False
            self.is_first_run = True
    
    def save_settings(self):
        try:
            settings = {
                'overlay_x': self.overlay_x,
                'overlay_y': self.overlay_y,
                'overlay_bg': self.overlay_bg,
                'start_minimized': self.start_minimized
            }
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f)
            logger.info("SETTINGS: Saved successfully")
            logger.debug(f"SETTINGS: {settings}")
        except Exception as e:
            logger.error(f"SETTINGS: Failed to save - {str(e)}")
    
    def init_ui(self):
        self.setWindowTitle("Peak & Aim Assistant v1.0")
        self.setFixedSize(400, 680)
        
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(30, 30, 30))
        palette.setColor(QPalette.WindowText, Qt.white)
        self.setPalette(palette)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        layout.setSpacing(8)
        
        # Title section with logo beside
        title_container = QHBoxLayout()
        title_container.addStretch()
        
        logo_path = resource_path("logo.png")
        if os.path.exists(logo_path):
            logo_label = QLabel()
            logo_pixmap = QPixmap(logo_path)
            logo_label.setPixmap(logo_pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            title_container.addWidget(logo_label)
            logger.debug(f"UI: Logo loaded from {logo_path}")
        else:
            logger.warning("UI: logo.png not found")
        
        title_text_layout = QVBoxLayout()
        title_text_layout.setSpacing(0)
        
        title = QLabel("Peak & Aim Assistant")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("color: white;")
        title_text_layout.addWidget(title)
        
        title_container.addLayout(title_text_layout)
        title_container.addStretch()
        
        layout.addLayout(title_container)
        
        # Creator centered
        creator = QLabel("Created by MAAKTHUNDER")
        creator.setFont(QFont("Segoe UI", 9))
        creator.setStyleSheet("color: #AAAAAA;")
        creator.setAlignment(Qt.AlignCenter)
        layout.addWidget(creator)
        
        layout.addWidget(QLabel("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", self))
        
        # Status (reduced spacing)
        status_layout = QHBoxLayout()
        self.status_dot = QLabel("●")
        self.status_dot.setFont(QFont("Segoe UI", 14))
        self.status_dot.setStyleSheet("color: #FF0000;")
        self.status_text = QLabel("INACTIVE")
        self.status_text.setFont(QFont("Segoe UI", 10))
        self.status_text.setStyleSheet("color: #FF0000;")
        status_layout.addStretch()
        status_layout.addWidget(self.status_dot)
        status_layout.addWidget(self.status_text)
        status_layout.addStretch()
        layout.addLayout(status_layout)
        
        layout.addWidget(QLabel("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", self))
        
        # Toggle button
        self.toggle_btn = QPushButton("Toggle Macro (F8)")
        self.toggle_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.toggle_btn.setFixedHeight(40)
        self.toggle_btn.clicked.connect(self.toggle_macro)
        layout.addWidget(self.toggle_btn)
        
        # View Logs button
        view_logs_btn = QPushButton("📄 View Logs")
        view_logs_btn.setFont(QFont("Segoe UI", 9))
        view_logs_btn.setFixedHeight(30)
        view_logs_btn.clicked.connect(self.view_logs)
        layout.addWidget(view_logs_btn)
        
        # Overlay position
        pos_label = QLabel("Overlay Position:")
        pos_label.setStyleSheet("color: #AAAAAA;")
        layout.addWidget(pos_label)
        
        pos_layout = QHBoxLayout()
        x_label = QLabel("X:")
        x_label.setStyleSheet("color: white;")
        pos_layout.addWidget(x_label)
        self.x_input = QLineEdit(str(self.overlay_x))
        self.x_input.setFixedWidth(80)
        pos_layout.addWidget(self.x_input)
        
        y_label = QLabel("Y:")
        y_label.setStyleSheet("color: white;")
        pos_layout.addWidget(y_label)
        self.y_input = QLineEdit(str(self.overlay_y))
        self.y_input.setFixedWidth(80)
        pos_layout.addWidget(self.y_input)
        
        apply_btn = QPushButton("Apply & Save")
        apply_btn.clicked.connect(self.apply_position)
        pos_layout.addWidget(apply_btn)
        layout.addLayout(pos_layout)
        
        # Checkboxes
        self.bg_check = QCheckBox("Show Background (Semi-transparent)")
        self.bg_check.setStyleSheet("color: white;")
        self.bg_check.setChecked(self.overlay_bg)
        self.bg_check.stateChanged.connect(self.toggle_background)
        layout.addWidget(self.bg_check)
        
        self.minimize_check = QCheckBox("Start Minimized to Tray")
        self.minimize_check.setStyleSheet("color: white;")
        self.minimize_check.setChecked(self.start_minimized)
        self.minimize_check.stateChanged.connect(self.toggle_minimize)
        layout.addWidget(self.minimize_check)
        
        tip_label = QLabel("Tip: Works everywhere, optimized for GameLoop")
        tip_label.setStyleSheet("color: #00FF00; font-size: 8pt;")
        layout.addWidget(tip_label)
        
        layout.addWidget(QLabel("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", self))
        
        # Hotkeys section
        hotkeys_label = QLabel("Hotkeys:")
        hotkeys_label.setStyleSheet("color: white; font-weight: bold;")
        layout.addWidget(hotkeys_label)
        
        hotkey1 = QLabel("F8 - Toggle Macro ON/OFF")
        hotkey1.setStyleSheet("color: #CCCCCC;")
        layout.addWidget(hotkey1)
        
        hotkey2 = QLabel("Q/E - Peak with Auto-Aim")
        hotkey2.setStyleSheet("color: #CCCCCC;")
        layout.addWidget(hotkey2)
        
        layout.addWidget(QLabel("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", self))
        
        # Social links with larger icons
        youtube_layout = QHBoxLayout()
        youtube_layout.setSpacing(10)
        
        yt_icon_path = resource_path("youtube.png")
        if os.path.exists(yt_icon_path):
            yt_icon = QLabel()
            yt_pixmap = QPixmap(yt_icon_path)
            yt_icon.setPixmap(yt_pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            youtube_layout.addWidget(yt_icon)
        
        yt_link = ClickableLabel("WWW.YOUTUBE.COM/@MAAKTHUNDER", "https://www.youtube.com/@MAAKTHUNDER")
        yt_link.setFont(QFont("Segoe UI", 10))
        yt_link.setStyleSheet("color: #00BFFF; text-decoration: underline;")
        youtube_layout.addWidget(yt_link)
        youtube_layout.addStretch()
        layout.addLayout(youtube_layout)
        
        tiktok_layout = QHBoxLayout()
        tiktok_layout.setSpacing(10)
        
        tt_icon_path = resource_path("tiktok.png")
        if os.path.exists(tt_icon_path):
            tt_icon = QLabel()
            tt_pixmap = QPixmap(tt_icon_path)
            tt_icon.setPixmap(tt_pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            tiktok_layout.addWidget(tt_icon)
        
        tt_link = ClickableLabel("WWW.TIKTOK.COM/@MAAKTHUNDER", "https://www.tiktok.com/@maakthunder")
        tt_link.setFont(QFont("Segoe UI", 10))
        tt_link.setStyleSheet("color: #00BFFF; text-decoration: underline;")
        tiktok_layout.addWidget(tt_link)
        tiktok_layout.addStretch()
        layout.addLayout(tiktok_layout)
        
        layout.addWidget(QLabel("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", self))
        
        # Footer
        footer = QLabel("Made for GameLoop | v1.0")
        footer.setStyleSheet("color: #888888;")
        footer.setAlignment(Qt.AlignCenter)
        layout.addWidget(footer)
        
        central_widget.setLayout(layout)
        
        if self.is_first_run or not self.start_minimized:
            self.show()
            logger.info("UI: Main window shown")
        else:
            self.hide()
            logger.info("UI: Started minimized to tray")
    
    def view_logs(self):
        """Open log file in default text editor"""
        log_file = "peak_aim_log.txt"
        try:
            if os.path.exists(log_file):
                logger.info("UI: Opening log file")
                os.startfile(log_file)
            else:
                logger.warning("UI: Log file not found")
                QMessageBox.information(self, "Logs", "Log file not found yet.\nLogs will be created as the app runs.")
        except Exception as e:
            logger.error(f"UI: Failed to open log file - {str(e)}")
            QMessageBox.warning(self, "Error", f"Could not open log file:\n{str(e)}")
    
    def setup_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setToolTip("Peak & Aim Assistant - MAAKTHUNDER")
        
        icon_path = resource_path("icon.ico")
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
            self.tray_icon.setIcon(icon)
        else:
            pixmap = QPixmap(16, 16)
            pixmap.fill(QColor(0, 255, 0))
            self.tray_icon.setIcon(QIcon(pixmap))
        
        tray_menu = QMenu()
        
        show_action = QAction("Show GUI", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        toggle_action = QAction("Toggle Macro (F8)", self)
        toggle_action.triggered.connect(self.toggle_macro)
        tray_menu.addAction(toggle_action)
        
        tray_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.quit_app)
        tray_menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_clicked)
        self.tray_icon.show()
        logger.info("UI: System tray icon created")
    
    def tray_clicked(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()
            logger.info("UI: Window shown from tray")
    
    def setup_overlay(self):
        self.overlay = OverlayWindow()
        self.overlay.move(self.overlay_x, self.overlay_y)
        self.overlay.update_status(False, False, self.overlay_bg)
        self.overlay.show()
        logger.info(f"OVERLAY: Created at X:{self.overlay_x} Y:{self.overlay_y}")
        
        # Optimized overlay update timer
        self.overlay_timer = QTimer()
        self.overlay_timer.timeout.connect(self.update_overlay_display)
        self.overlay_timer.start(300)  # 300ms for lower CPU usage
        logger.info("OVERLAY: Update timer started (300ms interval)")
    
    def update_overlay_display(self):
        """Separate function for overlay timer updates"""
        pass  # Actual updates happen via signals
    
    def update_overlay_status(self, active, scope_open):
        self.overlay.update_status(active, scope_open, self.overlay_bg)
        
        if active:
            self.status_dot.setStyleSheet("color: #00FF00;")
            self.status_text.setStyleSheet("color: #00FF00;")
            self.status_text.setText("ACTIVE")
        else:
            self.status_dot.setStyleSheet("color: #FF0000;")
            self.status_text.setStyleSheet("color: #FF0000;")
            self.status_text.setText("INACTIVE")
    
    def toggle_macro(self):
        old_state = self.macro_thread.enabled
        self.macro_thread.enabled = not self.macro_thread.enabled
        logger.info(f"ACTION: F8 pressed - Macro: {old_state} → {self.macro_thread.enabled}")
    
    def apply_position(self):
        try:
            self.overlay_x = int(self.x_input.text())
            self.overlay_y = int(self.y_input.text())
            self.overlay.move(self.overlay_x, self.overlay_y)
            self.save_settings()
            logger.info(f"UI: Overlay position changed to X:{self.overlay_x} Y:{self.overlay_y}")
            QMessageBox.information(self, "Success", f"Position saved: X={self.overlay_x}, Y={self.overlay_y}")
        except Exception as e:
            logger.error(f"UI: Invalid position values - {str(e)}")
            QMessageBox.warning(self, "Error", "Invalid position values!")
    
    def toggle_background(self):
        self.overlay_bg = self.bg_check.isChecked()
        self.save_settings()
        logger.info(f"UI: Overlay background changed to {self.overlay_bg}")
    
    def toggle_minimize(self):
        self.start_minimized = self.minimize_check.isChecked()
        self.save_settings()
        logger.info(f"UI: Start minimized changed to {self.start_minimized}")
    
    def watchdog_check(self):
        """Watchdog timer to detect stuck O key"""
        if self.macro_thread.o_held:
            e_state = keyboard.is_pressed('e')
            q_state = keyboard.is_pressed('q')
            
            if not e_state and not q_state:
                logger.warning(f"WATCHDOG: Stuck key detected - o_held=True but Q:{q_state} E:{e_state}")
                logger.warning("WATCHDOG: Force releasing O key")
                try:
                    keyboard.release('o')
                    self.macro_thread.o_held = False
                    logger.info("WATCHDOG: Successfully released stuck O key")
                except Exception as e:
                    logger.error(f"WATCHDOG: Failed to release O - {str(e)}")
    
    def closeEvent(self, event):
        event.ignore()
        self.hide()
        logger.info("UI: Window hidden (minimized to tray)")
    
    def quit_app(self):
        logger.info("SHUTDOWN: Exit requested")
        self.macro_thread.stop()
        self.macro_thread.wait()
        logger.info("SHUTDOWN: Macro thread stopped")
        logger.info("═══════════════════════════════════════")
        logger.info("SHUTDOWN: Application closed")
        logger.info("═══════════════════════════════════════")
        QApplication.quit()

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    # Single instance check
    shared_mem = QSharedMemory("PeakAimAssistantUniqueName")
    
    if not shared_mem.create(1):
        logger.warning("STARTUP: Another instance already running")
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Already Running")
        msg.setText("Peak & Aim Assistant is already running!")
        msg.setInformativeText("Check your system tray.")
        msg.exec_()
        sys.exit(0)
    
    window = MainWindow()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
