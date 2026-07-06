from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout, QProgressBar
from PyQt6.QtCore import Qt


class EventBubble(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setVisible(False)
        self.setFrameShape(QFrame.Shape.NoFrame)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(5)

        self.title = QLabel("")
        self.title.setObjectName("event_title")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setWordWrap(True)
        layout.addWidget(self.title)

        self.desc = QLabel("")
        self.desc.setObjectName("event_desc")
        self.desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.desc.setWordWrap(True)
        layout.addWidget(self.desc)

        self.bar = QProgressBar()
        self.bar.setTextVisible(False)
        self.bar.setRange(0, 100)
        self.bar.setValue(100)
        self.bar.setFixedHeight(5)
        layout.addWidget(self.bar)

    def apply_theme(self, accent="#8bd3ff", text="#ffffff", bg="#000000"):
        bg_rgb = bg.lstrip("#")
        r, g, b = int(bg_rgb[0:2], 16), int(bg_rgb[2:4], 16), int(bg_rgb[4:6], 16)
        self.setStyleSheet(
            f"""
            EventBubble {{
                background: rgba({r}, {g}, {b}, 170);
                border: 1px solid {accent}66;
                border-radius: 12px;
            }}
            QLabel#event_title {{
                color: {text};
                font-size: 11pt;
                font-weight: bold;
                background: transparent;
            }}
            QLabel#event_desc {{
                color: {text}cc;
                font-size: 9pt;
                background: transparent;
            }}
            QProgressBar {{
                border: none;
                border-radius: 3px;
                background: rgba(255,255,255,16);
            }}
            QProgressBar::chunk {{
                background: {accent};
                border-radius: 3px;
            }}
            """
        )
