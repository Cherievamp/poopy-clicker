from PyQt6.QtWidgets import QWidget, QSizePolicy


class PlayArea(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(280)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
