import sys
import threading
from PyQt5 import QtWidgets, QtCore, QtGui
from audioVisual.av_trigger import record
import numpy as np
# from savingIcon import re

class AutoDocsBar(QtWidgets.QWidget):
    def __init__(self):
        self.minimal_label = None
        super().__init__()
        self.drag_position = None
        self.theme_timer = QtCore.QTimer()
        self.theme_timer.timeout.connect(self.update_theme)
        self.current_theme = None  # Track current theme to prevent unnecessary updates
        self.is_minimized = False
        self.init_ui()
        
        # Enable hover tracking and mouse tracking
        self.setAttribute(QtCore.Qt.WA_Hover)  # ✅ fixed
        self.setMouseTracking(True)
        self.bg.setMouseTracking(True)



    def event(self, e):
        if e.type() == QtCore.QEvent.HoverEnter:
            if self.is_minimized:
                self.bg.setStyleSheet('background-color: rgba(255, 255, 255, 140); border-radius: 4px;')
        elif e.type() == QtCore.QEvent.HoverLeave:
            if self.is_minimized:
                self.bg.setStyleSheet('background-color: rgba(255, 255, 255, 50); border-radius: 4px;')
        return super().event(e)

        


    def init_ui(self):
        # Initial size and position
        self.normal_width, self.normal_height = 600, 80  # Increased width to accommodate duration buttons
        self.minimized_height = 30  # 1-2 mm on most screens
        screen = QtWidgets.QDesktopWidget().screenGeometry()
        x = (screen.width() - self.normal_width) // 2
        y = screen.height() - self.normal_height - 20
        self.setGeometry(x, y, self.normal_width, self.normal_height)

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
        self.bg.setGeometry(0, 0, self.normal_width, self.normal_height)

        # Layout inside background
        self.layout = QtWidgets.QHBoxLayout(self.bg)
        self.layout.setContentsMargins(16, 10, 16, 10)  # More margin left/right
        self.layout.setSpacing(12)  # More space between widgets


        self.status_label = QtWidgets.QLabel('🎥 AutoDocs Recorder Ready')
        self.status_label.setStyleSheet('color: #333333; font-size: 14px; font-weight: bold;')
        self.layout.addWidget(self.status_label)

        # Duration selection buttons
        self.duration_frame = QtWidgets.QFrame()
        self.duration_layout = QtWidgets.QHBoxLayout(self.duration_frame)
        self.duration_layout.setSpacing(10)
        self.duration_layout.setContentsMargins(6, 0, 6, 0)
        # btn.setFixedSize(45, 28)  # wider and taller
        # btn.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)




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
            self.duration_layout.addWidget(btn)
        
        self.layout.addWidget(self.duration_frame)

        self.start_btn = QtWidgets.QPushButton('Start')
        self.start_btn.setFixedHeight(30)
        self.start_btn.setStyleSheet(
            '''
            QPushButton {background-color: #0078D4; color: white; padding: 5px 12px;
                        border-radius: 5px; font-weight: bold;}
            QPushButton:hover {background-color: #005a9e;}
            '''
        )
        self.start_btn.clicked.connect(self.start_recording)
        self.layout.addWidget(self.start_btn)

        self.quit_btn = QtWidgets.QPushButton('Quit')
        self.quit_btn.setFixedHeight(30)
        self.quit_btn.setStyleSheet(
            '''
            QPushButton {background-color: #d9534f; color: white; padding: 5px 12px;
                        border-radius: 5px; font-weight: bold;}
            QPushButton:hover {background-color: #c9302c;}
            '''
        )
        self.quit_btn.clicked.connect(QtWidgets.QApplication.quit)
        self.layout.addWidget(self.quit_btn)

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
    @QtCore.pyqtSlot(str)
    def update_status(self, status: str):
        if self.is_minimized and hasattr(self, 'minimal_label'):
            self.minimal_label.setText(status)
        else:
            self.status_label.setText(status)


    def minimize_bar(self):
        """Minimize the bar to a thin strip with a recording/saving indicator"""
        if self.is_minimized:
            return
        self.is_minimized = True

        # Save current geometry and resize
        geo = self.geometry()
        self.setGeometry(geo.x(), geo.y() + self.normal_height - self.minimized_height, self.normal_width, self.minimized_height)
        self.bg.setGeometry(0, 0, self.normal_width, self.minimized_height)

        # Clear layout and add minimal label
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)

        self.minimal_label = QtWidgets.QLabel('🔴 Recording...')
        self.minimal_label.setAlignment(QtCore.Qt.AlignCenter)
        self.minimal_label.setStyleSheet('color: rgba(255, 0, 0, 100); font-size: 12px; font-weight: bold;')

        self.layout.addWidget(self.minimal_label)

        self.bg.setStyleSheet('background-color: rgba(255, 255, 255, 50); border-radius: 4px;')

        self.update()



    def restore_bar(self):
        """Restore the bar to its normal size and contents"""
        if not self.is_minimized:
            return
        self.is_minimized = False

        # Restore geometry
        geo = self.geometry()
        self.setGeometry(geo.x(), geo.y() - self.normal_height + self.minimized_height, self.normal_width, self.normal_height)
        self.bg.setGeometry(0, 0, self.normal_width, self.normal_height)

        # Remove minimal label if it exists
        if self.minimal_label:
            self.layout.removeWidget(self.minimal_label)
            self.minimal_label.deleteLater()
            self.minimal_label = None

        # Re-add full widgets
        self.status_label = QtWidgets.QLabel('🎥 AutoDocs Recorder Ready')
        self.layout.addWidget(self.status_label)
        self.layout.addWidget(self.duration_frame)
        self.layout.addWidget(self.start_btn)
        self.layout.addWidget(self.quit_btn)
        self.bg.setStyleSheet('background-color: rgba(255, 255, 255, 180); border-radius: 12px;')
        self.update_theme()
        self.update()


    def start_recording(self):
        self.status_label.setText(f'🔴 Recording {self.selected_duration}s...')
        self.minimize_bar()

        def run_recording():
            try:
                record(duration=self.selected_duration, status_callback=self.update_status_clean)
            except Exception as e:
                print(f'Error during recording: {e}')
            finally:
                QtCore.QTimer.singleShot(0, self.restore_bar)

        threading.Thread(target=run_recording, daemon=True).start()

    def update_status_clean(self, status):
        """Updates status label without spinner, supports minimized mode."""
        if self.is_minimized and hasattr(self, "minimal_label"):
            self.minimal_label.setText(status)
        elif not self.is_minimized and hasattr(self, "status_label"):
            self.status_label.setText(status)



    def get_screen_brightness(self):
        """Sample the screen area around the bar to determine brightness"""
        try:
            desktop = QtWidgets.QApplication.desktop()
            bar_rect = self.geometry()
            sample_width = 50
            sample_height = 50
            samples = []
            above_rect = QtCore.QRect(
                bar_rect.x() + bar_rect.width() // 2 - sample_width // 2,
                max(0, bar_rect.y() - sample_height - 10),
                sample_width,
                sample_height
            )
            below_rect = QtCore.QRect(
                bar_rect.x() + bar_rect.width() // 2 - sample_width // 2,
                bar_rect.y() + bar_rect.height() + 10,
                sample_width,
                sample_height
            )
            left_rect = QtCore.QRect(
                max(0, bar_rect.x() - sample_width - 10),
                bar_rect.y() + bar_rect.height() // 2 - sample_height // 2,
                sample_width,
                sample_height
            )
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
                screen_rect = desktop.screenGeometry()
                if not screen_rect.contains(rect):
                    continue
                screenshot = QtWidgets.QApplication.primaryScreen().grabWindow(
                    desktop.winId(),
                    rect.x(),
                    rect.y(),
                    rect.width(),
                    rect.height()
                )
                image = screenshot.toImage()
                width, height = image.width(), image.height()
                for x in range(0, width, 5):
                    for y in range(0, height, 5):
                        pixel = image.pixel(x, y)
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
        if self.current_theme == 'dark':
            light_threshold = 140
        else:
            light_threshold = 116
        if brightness > light_threshold:
            new_theme = 'dark'
            bg_color = 'rgba(30, 30, 30, 200)'
            text_color = 'white'
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
        else:
            new_theme = 'light'
            bg_color = 'rgba(255, 255, 255, 180)'
            text_color = '#333333'
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
        if new_theme != self.current_theme:
            self.current_theme = new_theme
            self.bg.setStyleSheet(f'background-color: {bg_color}; border-radius: 10px;')
            if not self.is_minimized:
                self.status_label.setStyleSheet(f'color: {text_color}; font-size: 14px; font-weight: bold;')
                for btn in self.duration_buttons:
                    btn.setStyleSheet(duration_btn_style)

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        if event.buttons() == QtCore.Qt.LeftButton and self.drag_position:
            self.move(event.globalPos() - self.drag_position)
            self.update_theme()
            event.accept()

    def event(self, e):
        if self.is_minimized and self.minimal_label:
            if e.type() == QtCore.QEvent.HoverEnter:
                # Make text and bar more opaque on hover
                self.minimal_label.setStyleSheet("color: rgba(255, 0, 0, 0.9); font-size: 12px; font-weight: bold;")
                self.bg.setStyleSheet("background-color: rgba(255, 255, 255, 220); border-radius: 4px;")
            elif e.type() == QtCore.QEvent.HoverLeave:
                # Make text and bar more transparent when not hovered
                self.minimal_label.setStyleSheet("color: rgba(255, 0, 0, 0.2); font-size: 12px; font-weight: bold;")
                self.bg.setStyleSheet("background-color: rgba(255, 255, 255, 120); border-radius: 4px;")
        return super().event(e)


def run_app():
    app = QtWidgets.QApplication(sys.argv)
    bar = AutoDocsBar()
    bar.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    run_app()
