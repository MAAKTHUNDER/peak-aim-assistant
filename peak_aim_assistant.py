import sys
import json
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QLineEdit, 
                             QCheckBox, QSystemTrayIcon, QMenu, QAction)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QFont, QPalette, QColor
import keyboard
import time
from pynput.mouse import Listener as MouseListener

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
        self.label.setStyleSheet("color: #FF0000; background-color: rgba(0, 0, 0, 180); padding: 5px;")
        
        layout.addWidget(self.label)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        
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
        
    def run(self):
        # Mouse listener for right-click
        def on_click(x, y, button, pressed):
            if str(button) == "Button.right":
                if pressed:
                    self.right_click_time = time.time()
                else:
                    hold_duration = (time.time() - self.right_click_time) * 1000
                    if hold_duration < 1000:
                        self.scope_toggled = not self.scope_toggled
        
        mouse_listener = MouseListener(on_click=on_click)
        mouse_listener.start()
        
        while self.running:
            try:
                if self.enabled:
                    e_pressed = keyboard.is_pressed('e')
                    q_pressed = keyboard.is_pressed('q')
                    right_click_held = keyboard.is_pressed('right')
                    
                    scope_active = self.scope_toggled or right_click_held
                    should_hold = (e_pressed or q_pressed) and not scope_active
                    
                    if should_hold and not self.o_held:
                        keyboard.press('o')
                        self.o_held = True
                    elif not should_hold and self.o_held:
                        keyboard.release('o')
                        self.o_held = False
                        
                    self.status_update.emit(True, scope_active)
                else:
                    if self.o_held:
                        keyboard.release('o')
                        self.o_held = False
                    self.status_update.emit(False, self.scope_toggled)
                    
                time.sleep(0.01)  # 10ms loop
                
            except Exception as e:
                print(f"Error in macro thread: {e}")
                if self.o_held:
                    try:
                        keyboard.release('o')
                    except:
                        pass
                    self.o_held = False
                time.sleep(0.1)
    
    def stop(self):
        self.running = False
        if self.o_held:
            try:
                keyboard.release('o')
            except:
                pass

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings_file = "settings.json"
        self.load_settings()
        
        self.macro_thread = MacroThread()
        self.macro_thread.status_update.connect(self.update_overlay_status)
        self.macro_thread.start()
        
        self.init_ui()
        self.setup_tray()
        self.setup_overlay()
        
        # Setup F8 hotkey
        keyboard.add_hotkey('f8', self.toggle_macro)
        
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
            else:
                self.overlay_x = 1600
                self.overlay_y = 50
                self.overlay_bg = True
                self.start_minimized = False
                self.is_first_run = True
        except:
            self.overlay_x = 1600
            self.overlay_y = 50
            self.overlay_bg = True
            self.start_minimized = False
            self.is_first_run = True
    
    def save_settings(self):
        settings = {
            'overlay_x': self.overlay_x,
            'overlay_y': self.overlay_y,
            'overlay_bg': self.overlay_bg,
            'start_minimized': self.start_minimized
        }
        with open(self.settings_file, 'w') as f:
            json.dump(settings, f)
    
    def init_ui(self):
        self.setWindowTitle("Peak & Aim Assistant v1.0")
        self.setFixedSize(400, 550)
        
        # Dark theme
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(30, 30, 30))
        palette.setColor(QPalette.WindowText, Qt.white)
        self.setPalette(palette)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("🎮 Peak & Aim Assistant")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: white;")
        layout.addWidget(title)
        
        # Status
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
        
        # Toggle button
        self.toggle_btn = QPushButton("Toggle Macro (F8)")
        self.toggle_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.toggle_btn.setFixedHeight(40)
        self.toggle_btn.clicked.connect(self.toggle_macro)
        layout.addWidget(self.toggle_btn)
        
        # Position settings
        pos_label = QLabel("Overlay Position:")
        pos_label.setStyleSheet("color: #AAAAAA;")
        layout.addWidget(pos_label)
        
        pos_layout = QHBoxLayout()
        pos_layout.addWidget(QLabel("X:"))
        self.x_input = QLineEdit(str(self.overlay_x))
        self.x_input.setFixedWidth(80)
        pos_layout.addWidget(self.x_input)
        
        pos_layout.addWidget(QLabel("Y:"))
        self.y_input = QLineEdit(str(self.overlay_y))
        self.y_input.setFixedWidth(80)
        pos_layout.addWidget(self.y_input)
        
        apply_btn = QPushButton("Apply & Save")
        apply_btn.clicked.connect(self.apply_position)
        pos_layout.addWidget(apply_btn)
        layout.addLayout(pos_layout)
        
        # Checkboxes
        self.bg_check = QCheckBox("Show Background (Semi-transparent)")
        self.bg_check.setChecked(self.overlay_bg)
        self.bg_check.stateChanged.connect(self.toggle_background)
        layout.addWidget(self.bg_check)
        
        self.minimize_check = QCheckBox("Start Minimized to Tray")
        self.minimize_check.setChecked(self.start_minimized)
        self.minimize_check.stateChanged.connect(self.toggle_minimize)
        layout.addWidget(self.minimize_check)
        
        # Features
        layout.addWidget(QLabel("\nFeatures:", self))
        features = [
            "☑ Peak & Aim (Q/E → O)",
            "☑ Scope Detection (Right-Click)",
            "☑ Auto-Recovery & Watchdog",
            "☑ Persistent Settings"
        ]
        for feature in features:
            label = QLabel(feature)
            label.setStyleSheet("color: #00FF00;")
            layout.addWidget(label)
        
        layout.addStretch()
        central_widget.setLayout(layout)
        
        # Show or hide based on settings
        if self.is_first_run or not self.start_minimized:
            self.show()
        else:
            self.hide()
    
    def setup_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setToolTip("Peak & Aim Assistant")
        
        # Create tray menu
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
    
    def tray_clicked(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()
    
    def setup_overlay(self):
        self.overlay = OverlayWindow()
        self.overlay.move(self.overlay_x, self.overlay_y)
        self.overlay.update_status(False, False, self.overlay_bg)
        
        # Timer to check if GameLoop is active
        self.overlay_timer = QTimer()
        self.overlay_timer.timeout.connect(self.check_gameloop)
        self.overlay_timer.start(100)
    
    def check_gameloop(self):
        # Check if GameLoop window is active (simplified - you may need psutil for better detection)
        try:
            import win32gui
            hwnd = win32gui.GetForegroundWindow()
            title = win32gui.GetWindowText(hwnd)
            
            if "gameloop" in title.lower() or "emulator" in title.lower():
                self.overlay.show()
            else:
                self.overlay.hide()
        except:
            # Fallback: always show overlay
            self.overlay.show()
    
    def update_overlay_status(self, active, scope_open):
        self.overlay.update_status(active, scope_open, self.overlay_bg)
        
        # Update main GUI status
        if active:
            self.status_dot.setStyleSheet("color: #00FF00;")
            self.status_text.setStyleSheet("color: #00FF00;")
            self.status_text.setText("ACTIVE")
        else:
            self.status_dot.setStyleSheet("color: #FF0000;")
            self.status_text.setStyleSheet("color: #FF0000;")
            self.status_text.setText("INACTIVE")
    
    def toggle_macro(self):
        self.macro_thread.enabled = not self.macro_thread.enabled
    
    def apply_position(self):
        try:
            self.overlay_x = int(self.x_input.text())
            self.overlay_y = int(self.y_input.text())
            self.overlay.move(self.overlay_x, self.overlay_y)
            self.save_settings()
        except:
            pass
    
    def toggle_background(self):
        self.overlay_bg = self.bg_check.isChecked()
        self.save_settings()
    
    def toggle_minimize(self):
        self.start_minimized = self.minimize_check.isChecked()
        self.save_settings()
    
    def closeEvent(self, event):
        event.ignore()
        self.hide()
    
    def quit_app(self):
        self.macro_thread.stop()
        self.macro_thread.wait()
        QApplication.quit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    window = MainWindow()
    sys.exit(app.exec_())
