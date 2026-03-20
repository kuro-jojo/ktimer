import sys
from PySide6.QtCore import Qt, QTimer, QRectF, QRegularExpression
from PySide6.QtGui import (
    QColor,
    QPainter,
    QPen,
    QIcon,
    QPixmap,
    QFont,
    QRegularExpressionValidator,
)
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
)
from playsound3 import playsound


class CircularProgress(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.value = 100
        self.is_playing = False  # New attribute to track play/pause state
        self.setMinimumSize(200, 200)

    def paintEvent(self, event) -> None:
        size = min(self.width(), self.height()) - 40
        rect = QRectF((self.width() - size) / 2, (self.height() - size) / 2, size, size)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        pen = QPen(QColor(60, 60, 60, 150), 10)
        painter.setPen(pen)
        painter.drawEllipse(rect)

        if self.value > 0:
            pen.setColor(QColor("#08BB20"))
            pen.setCapStyle(Qt.RoundCap)
            painter.setPen(pen)
            span_angle = -int((self.value / 100) * 360 * 16)
            painter.drawArc(rect, 90 * 16, span_angle)

        # Draw play/pause emoji in the center
        center_rect = QRectF(self.width() / 2 - 20, self.height() / 2 - 20, 40, 40)
        painter.setFont(QFont("Segoe UI Emoji", 32))
        painter.setPen(QPen(Qt.white))  # Ensure visibility
        emoji = "▶️" if self.is_playing else "⏸️"
        painter.drawText(center_rect, Qt.AlignCenter, emoji)


class ModernTimer(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("KTimer")
        self.setMinimumSize(450, 600)
        self.set_emoji_icon("⏱️")
        self.total_seconds = 0
        self.remaining_seconds = 0

        self.setStyleSheet(
            """
            QMainWindow { background-color: #1c1c1c; }
            QLabel { color: white; font-family: 'Segoe UI Variable Text', sans-serif; }
            
            QLineEdit {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 6px;
                color: white;
                padding: 8px;
                font-size: 16px;
            }

            /* Preset Chips */
            QPushButton#preset {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 15px; /* Rounded pill shape */
                color: #cccccc;
                font-size: 12px;
                padding: 5px 12px;
                min-width: 60px;
            }
            QPushButton#preset:hover {
                background-color: #3d3d3d;
                color: white;
            }

            /* Main Controls */
            QPushButton#primary { 
                background-color: #60CDFF; 
                color: #000; 
                font-weight: 600; 
                border-radius: 6px;
                padding: 12px;
            }
            QPushButton#secondary { 
                background-color: transparent; 
                border: 1px solid #3d3d3d; 
                color: white; 
                border-radius: 6px;
                padding: 12px;
            }
            QPushButton#primary:hover { background-color: #70DFFF; }
            QPushButton#secondary:hover { background-color: #2d2d2d; }
        """
        )

        self.init_ui()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)

    def init_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(40, 30, 40, 40)
        layout.setSpacing(25)

        # 1. Preset Selection Row
        preset_label = QLabel("Quick Start")
        preset_label.setStyleSheet("font-size: 14px; color: #888; font-weight: bold;")
        layout.addWidget(preset_label)

        preset_layout = QHBoxLayout()
        # each tuple is (label, seconds)
        presets = [
            ("30s", 30),
            ("1m", 60),
            ("5m", 5 * 60),
            ("15m", 15 * 60),
            ("30m", 30 * 60),
            ("1h", 60 * 60),
        ]
        for text, secs in presets:
            btn = QPushButton(text, objectName="preset")
            btn.clicked.connect(lambda checked=False, s=secs: self.set_preset(s))
            preset_layout.addWidget(btn)
        layout.addLayout(preset_layout)

        # 2. Custom Input
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Or enter time (m, s or m:s)...")
        # allow 1–3 digits, optional :ss, optional trailing s
        reg = QRegularExpression(r"^\d{1,3}(:\d{1,2})?s?$")
        self.input_field.setValidator(QRegularExpressionValidator(reg))
        input_layout.addWidget(self.input_field)
        layout.addLayout(input_layout)

        # 3. Circular Progress (Main Visual)
        self.progress = CircularProgress()
        layout.addWidget(self.progress, stretch=1)

        # 4. Digital Time Display
        self.time_label = QLabel("01:00")
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet(
            "font-size: 72px; font-weight: 200; margin-top: -20px;"
        )
        layout.addWidget(self.time_label)

        # 5. Controls
        ctrl_layout = QHBoxLayout()
        self.start_btn = QPushButton("Start Timer", objectName="primary")
        self.reset_btn = QPushButton("Reset", objectName="secondary")

        self.start_btn.clicked.connect(self.handle_start)
        self.reset_btn.clicked.connect(self.reset_timer)

        ctrl_layout.addWidget(self.start_btn, stretch=2)
        ctrl_layout.addWidget(self.reset_btn, stretch=1)
        layout.addLayout(ctrl_layout)

    def set_preset(self, seconds: int):
        """apply a preset value expressed in *seconds*"""
        self.reset_timer()
        # show something human-readable in the input field
        if seconds < 60:
            self.input_field.setText(f"{seconds}s")
        elif seconds % 60 == 0:
            self.input_field.setText(str(seconds // 60))
        else:
            m, s = divmod(seconds, 60)
            self.input_field.setText(f"{m}:{s:02d}")
        self.total_seconds = seconds
        self.remaining_seconds = seconds
        self.update_display_only()

    def parse_input(self, text: str) -> int:
        """
        Interpret the text entered by the user and return
        a number of seconds.  Acceptable forms:
            5           -> 5 minutes
            5m          -> 5 minutes (m is optional)
            30s         -> 30 seconds
            2:15        -> 2 minutes 15 seconds
        invalid/empty input falls back to one minute.
        """
        text = text.strip().lower()
        if not text:
            return 60
        # explicit seconds suffix
        if text.endswith("s"):
            text = text[:-1]
            try:
                sec = int(text)
                return max(1, sec)
            except ValueError:
                return 60
        # colon separated minutes:seconds
        if ":" in text:
            parts = text.split(":")
            if len(parts) == 2:
                try:
                    m = int(parts[0])
                    s = int(parts[1])
                    return max(1, m * 60 + s)
                except ValueError:
                    return 60
        # treat plain number as minutes
        try:
            m = int(text)
            return max(1, m * 60)
        except ValueError:
            return 60

    def set_emoji_icon(self, emoji="⏱️"):
        # Create a 64x64 canvas
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        # Use a large font size for the emoji
        painter.setFont(QFont("Segoe UI Emoji", 48))
        painter.drawText(pixmap.rect(), Qt.AlignCenter, emoji)
        painter.end()

        self.setWindowIcon(QIcon(pixmap))

    def handle_start(self) -> None:
        if self.timer.isActive():
            self.timer.stop()
            self.start_btn.setText("Resume")
            self.progress.is_playing = False  # Update to pause state
        else:
            if self.remaining_seconds <= 0:
                val = self.input_field.text()
                self.total_seconds = self.parse_input(val)
                self.remaining_seconds = self.total_seconds

            self.timer.start(1000)
            self.start_btn.setText("Pause")
            self.input_field.setEnabled(False)
            self.progress.is_playing = True  # Update to play state
        self.progress.update()  # Trigger repaint

    def reset_timer(self) -> None:
        self.timer.stop()
        self.remaining_seconds = 0
        self.progress.value = 100
        self.progress.is_playing = False  # Reset to pause state
        self.progress.update()
        self.time_label.setText("00:00")
        self.start_btn.setText("Start Timer")
        self.input_field.setEnabled(True)

    def update_display_only(self) -> None:
        """Updates UI without changing logic state"""
        m, s = divmod(self.remaining_seconds, 60)
        self.time_label.setText(f"{m:02d}:{s:02d}")
        self.progress.value = 100
        self.progress.update()

    def update_timer(self) -> None:
        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            m, s = divmod(self.remaining_seconds, 60)
            self.time_label.setText(f"{m:02d}:{s:02d}")
            self.progress.value = (self.remaining_seconds / self.total_seconds) * 100
            self.progress.update()
        else:
            self.raise_()  # Bring window to front
            self.activateWindow()  # Activate and focus the window
            playsound("alarm.mp3")
            self.reset_timer()


def main() -> None:
    app = QApplication(sys.argv)
    window = ModernTimer()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
