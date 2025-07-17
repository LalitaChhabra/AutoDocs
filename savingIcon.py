from PyQt5 import QtWidgets, QtCore, QtGui


class SavingPopup(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.Tool
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setFixedSize(140, 40)

        # Set position centered over parent if provided
        if parent:
            p_geo = parent.geometry()
            x = p_geo.center().x() - self.width() // 2
            y = p_geo.top() - self.height() - 10
            self.move(x, y)

        self.bg = QtWidgets.QFrame(self)
        self.bg.setGeometry(0, 0, self.width(), self.height())
        self.bg.setStyleSheet('background-color: rgba(255, 255, 255, 220); border-radius: 10px;')

        layout = QtWidgets.QHBoxLayout(self.bg)
        layout.setContentsMargins(10, 5, 10, 5)

        self.icon_label = QtWidgets.QLabel()
        self.icon_label.setPixmap(QtGui.QPixmap(':/qt-project.org/styles/commonstyle/images/standardbutton-ok-32.png'))
        self.icon_label.setFixedSize(24, 24)
        layout.addWidget(self.icon_label)

        self.status_label = QtWidgets.QLabel("Saving...")
        self.status_label.setStyleSheet('color: #0078D4; font-weight: bold; font-size: 14px;')
        layout.addWidget(self.status_label)

        # Optional: Add animation
        self.spinner_timer = QtCore.QTimer()
        self.spinner_timer.timeout.connect(self._spin)
        self.spinner_index = 0
        self.spinner_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        self.spinner_timer.start(100)

    def _spin(self):
        symbol = self.spinner_chars[self.spinner_index % len(self.spinner_chars)]
        self.status_label.setText(f"Saving {symbol}")
        self.spinner_index += 1

    def show_and_auto_close(self, duration_ms=2500):
        self.show()
        QtCore.QTimer.singleShot(duration_ms, self.close)
