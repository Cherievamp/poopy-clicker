from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout, QProgressBar, QHBoxLayout
from PyQt6.QtCore import Qt

class MissionCard(QFrame):
    def __init__(self, mission, theme):
        super().__init__()
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 {theme['bg']}, stop:1 {theme['panel']});
                border: 1px solid {theme['accent']}66;
                border-radius: 12px;
                padding: 0px;
            }}
        """)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 10, 12, 10)
        lay.setSpacing(6)

        top = QHBoxLayout()
        top.setSpacing(8)
        icon = QLabel(mission.get("icon", "📋"))
        icon.setStyleSheet(f"font-size: 14pt;")
        top.addWidget(icon)

        title = QLabel(mission.get("title", "Missão"))
        title.setStyleSheet(f"font-weight: bold; font-size: 11pt; color: {theme['text']};")
        top.addWidget(title, 1)
        lay.addLayout(top)

        if mission.get("description"):
            desc = QLabel(mission["description"])
            desc.setWordWrap(True)
            desc.setStyleSheet(f"font-size: 9pt; color: {theme['accent2']}; padding-left: 22px;")
            lay.addWidget(desc)

        prog = QProgressBar()
        prog.setRange(0, max(1, int(mission.get("target", 1))))
        prog.setValue(min(int(mission.get("progress", 0)), int(mission.get("target", 1))))
        prog.setTextVisible(True)
        prog.setFormat(f"{int(mission.get('progress', 0))}/{int(mission.get('target', 0))}")
        prog.setFixedHeight(18)
        prog.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {theme['accent']}44; border-radius: 4px;
                background: {theme['bg']}; color: {theme['text']};
                font-weight: bold; font-size: 8pt;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {theme['accent']}, stop:1 {theme['accent2']});
                border-radius: 3px;
            }}
        """)
        lay.addWidget(prog)

        reward = QLabel(f"🎁 {mission.get('reward_text', '')}")
        reward.setStyleSheet(f"font-size: 9pt; color: {theme['accent']}; padding-left: 22px;")
        lay.addWidget(reward)
