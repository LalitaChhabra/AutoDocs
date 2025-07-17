import sys
import threading
from PyQt5 import QtWidgets, QtCore, QtGui
from audiovisual.av_trigger import record
import numpy as np

class AutoDocsBar(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.drag_position = None
        self.theme_timer = QtCore.QTimer()
        self.theme_timer.timeout.connect(self.update_theme)
        self.current_theme = None  # Track current theme to prevent unnecessary updates
        self.init_ui()

    def init_ui(self):
        # Initial size and position
        width, height = 600, 80  # Increased width to accommodate duration buttons
        screen = QtWidgets.QDesktopWidget().screenGeometry()
        x = (screen.width() - width) // 2
        y = screen.height() - height - 20
        self.setGeometry(x, y, width, height)

        # Window flags for frameless, always on top, and tool window
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.Tool
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # Background frame
        self.bg = QtWidgets.QFrame(self)
        self.bg.setStyleSheet(
            'background-color: rgba(255, 255, 255, 180); border-radius: 12px;'
        )
        self.bg.setGeometry(0, 0, width, height)

        # Layout inside background
        layout = QtWidgets.QHBoxLayout(self.bg)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        self.status_label = QtWidgets.QLabel('🎥 AutoDocs Recorder Ready')
        self.status_label.setStyleSheet('color: #333333; font-size: 14px; font-weight: bold;')
        layout.addWidget(self.status_label)

        # Duration selection buttons
        duration_frame = QtWidgets.QFrame()
        duration_layout = QtWidgets.QHBoxLayout(duration_frame)
        duration_layout.setContentsMargins(0, 0, 0, 0)
        duration_layout.setSpacing(4)

        # Duration buttons
        self.duration_buttons = []
        self.selected_duration = 15  # Default duration
        
        for duration in [10, 15, 20]:
            btn = QtWidgets.QPushButton(f'{duration}s')
            btn.setFixedSize(35, 25)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, d=duration: self.set_duration(d))
            
            # Default styling
            btn.setStyleSheet(
                '''
                QPushButton {
                    background-color: rgba(255, 255, 255, 100);
                    color: #666666;
                    border: 1px solid #cccccc;
                    border-radius: 3px;
                    font-size: 11px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 150);
                }
                QPushButton:checked {
                    background-color: #0078D4;
                    color: white;
                    border: 1px solid #005a9e;
                }
                '''
            )
            
            # Set default selection
            if duration == self.selected_duration:
                btn.setChecked(True)
            
            self.duration_buttons.append(btn)
            duration_layout.addWidget(btn)
        
        layout.addWidget(duration_frame)

        start_btn = QtWidgets.QPushButton('Start')
        start_btn.setFixedHeight(30)
        start_btn.setStyleSheet(
            '''
            QPushButton {background-color: #0078D4; color: white; padding: 5px 12px;
                        border-radius: 5px; font-weight: bold;}
            QPushButton:hover {background-color: #005a9e;}
            '''
        )
        start_btn.clicked.connect(self.start_recording)
        layout.addWidget(start_btn)

        quit_btn = QtWidgets.QPushButton('Quit')
        quit_btn.setFixedHeight(30)
        quit_btn.setStyleSheet(
            '''
            QPushButton {background-color: #d9534f; color: white; padding: 5px 12px;
                        border-radius: 5px; font-weight: bold;}
            QPushButton:hover {background-color: #c9302c;}
            '''
        )
        quit_btn.clicked.connect(QtWidgets.QApplication.quit)
        layout.addWidget(quit_btn)

        # Start adaptive theme updates
        self.update_theme()  # Initial theme update
        self.theme_timer.start(1000)  # Update every second

    def set_duration(self, duration):
        """Set the recording duration and update button states"""
        self.selected_duration = duration
        
        # Update button states
        for btn in self.duration_buttons:
            btn.setChecked(False)
        
        # Find and check the selected button
        for btn in self.duration_buttons:
            if btn.text() == f'{duration}s':
                btn.setChecked(True)
                break

    @QtCore.pyqtSlot(str)
    def update_status(self, status: str):
        self.status_label.setText(status)

    def start_recording(self):
        self.status_label.setText(f'🔴 Recording {self.selected_duration}s...')
        self.hide()

        def run_recording():
            try:
                record(duration=self.selected_duration, status_callback=self.update_status)
            except Exception as e:
                print(f'Error during recording: {e}')
            finally:
                # Restore UI
                QtCore.QTimer.singleShot(0, self.show)
                QtCore.QTimer.singleShot(0, lambda: self.status_label.setText('🎥 AutoDocs Recorder Ready'))

        threading.Thread(target=run_recording, daemon=True).start()

    def get_screen_brightness(self):
        """Sample the screen area around the bar to determine brightness"""
        try:
            # Get the screen where the bar is positioned
            desktop = QtWidgets.QApplication.desktop()
            
            # Get bar position and size
            bar_rect = self.geometry()
            
            # Sample areas around the bar instead of directly behind it
            # Create sampling rectangles above, below, left, and right of the bar
            sample_width = 50
            sample_height = 50
            
            samples = []
            
            # Sample above the bar
            above_rect = QtCore.QRect(
                bar_rect.x() + bar_rect.width() // 2 - sample_width // 2,
                max(0, bar_rect.y() - sample_height - 10),
                sample_width,
                sample_height
            )
            
            # Sample below the bar
            below_rect = QtCore.QRect(
                bar_rect.x() + bar_rect.width() // 2 - sample_width // 2,
                bar_rect.y() + bar_rect.height() + 10,
                sample_width,
                sample_height
            )
            
            # Sample left of the bar
            left_rect = QtCore.QRect(
                max(0, bar_rect.x() - sample_width - 10),
                bar_rect.y() + bar_rect.height() // 2 - sample_height // 2,
                sample_width,
                sample_height
            )
            
            # Sample right of the bar
            right_rect = QtCore.QRect(
                bar_rect.x() + bar_rect.width() + 10,
                bar_rect.y() + bar_rect.height() // 2 - sample_height // 2,
                sample_width,
                sample_height
            )
            
            sample_rects = [above_rect, below_rect, left_rect, right_rect]
            
            total_brightness = 0
            total_pixels = 0
            
            for rect in sample_rects:
                # Skip if sample area is outside screen bounds
                screen_rect = desktop.screenGeometry()
                if not screen_rect.contains(rect):
                    continue
                    
                # Capture screenshot of sample area
                screenshot = QtWidgets.QApplication.primaryScreen().grabWindow(
                    desktop.winId(),
                    rect.x(),
                    rect.y(),
                    rect.width(),
                    rect.height()
                )
                
                # Convert to QImage for pixel analysis
                image = screenshot.toImage()
                
                # Sample pixels and calculate brightness
                width, height = image.width(), image.height()
                
                # Sample every 5th pixel for better coverage
                for x in range(0, width, 5):
                    for y in range(0, height, 5):
                        pixel = image.pixel(x, y)
                        # Calculate luminance using standard formula
                        r = (pixel >> 16) & 0xFF
                        g = (pixel >> 8) & 0xFF
                        b = pixel & 0xFF
                        brightness = 0.299 * r + 0.587 * g + 0.114 * b
                        total_brightness += brightness
                        total_pixels += 1
            
            return total_brightness / total_pixels if total_pixels > 0 else 128
        except Exception:
            return 128  # Default to medium brightness if sampling fails

    def update_theme(self):
        """Update the bar's theme based on screen brightness"""
        brightness = self.get_screen_brightness()
        
        # Use hysteresis to prevent rapid switching
        # If currently dark theme, need brighter threshold to switch to light
        # If currently light theme, need darker threshold to switch to dark
        if self.current_theme == 'dark':
            light_threshold = 140  # Higher threshold to switch to light
        else:
            light_threshold = 116  # Lower threshold to switch to light
        
        # Determine theme based on brightness with hysteresis
        if brightness > light_threshold:  # Light background detected
            new_theme = 'dark'
            bg_color = 'rgba(30, 30, 30, 200)'
            text_color = 'white'
            # Duration button styling for dark theme
            duration_btn_style = '''
                QPushButton {
                    background-color: rgba(255, 255, 255, 50);
                    color: #cccccc;
                    border: 1px solid #555555;
                    border-radius: 3px;
                    font-size: 11px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 80);
                }
                QPushButton:checked {
                    background-color: #0078D4;
                    color: white;
                    border: 1px solid #005a9e;
                }
            '''
        else:  # Dark background detected
            new_theme = 'light'
            bg_color = 'rgba(255, 255, 255, 180)'
            text_color = '#333333'
            # Duration button styling for light theme
            duration_btn_style = '''
                QPushButton {
                    background-color: rgba(255, 255, 255, 100);
                    color: #666666;
                    border: 1px solid #cccccc;
                    border-radius: 3px;
                    font-size: 11px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 150);
                }
                QPushButton:checked {
                    background-color: #0078D4;
                    color: white;
                    border: 1px solid #005a9e;
                }
            '''
        
        # Only update if theme actually changed
        if new_theme != self.current_theme:
            self.current_theme = new_theme
            
            # Update background
            self.bg.setStyleSheet(f'background-color: {bg_color}; border-radius: 10px;')
            
            # Update text color
            self.status_label.setStyleSheet(f'color: {text_color}; font-size: 14px; font-weight: bold;')
            
            # Update duration button styling
            for btn in self.duration_buttons:
                btn.setStyleSheet(duration_btn_style)

    # Enable dragging
    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        if event.buttons() == QtCore.Qt.LeftButton and self.drag_position:
            self.move(event.globalPos() - self.drag_position)
            # Update theme immediately when dragging
            self.update_theme()
            event.accept()


def run_app():
    app = QtWidgets.QApplication(sys.argv)
    bar = AutoDocsBar()
    bar.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    run_app()
