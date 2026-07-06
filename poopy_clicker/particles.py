import random
from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush


class Particle(QLabel):
    def __init__(self, parent, x, y, color, lifetime=600):
        super().__init__(parent)
        self._dx = random.uniform(-3, 3)
        self._dy = random.uniform(-4, -1)
        self._lifetime = lifetime
        self._age = 0
        self._color = QColor(color)
        self._size = random.randint(4, 9)
        self.setFixedSize(self._size * 2, self._size * 2)
        self.move(int(x - self._size), int(y - self._size))
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(30)
        self.show()
        self.raise_()

    def _tick(self):
        self._age += 30
        try:
            alpha = max(0, 255 - int((self._age / self._lifetime) * 255))
        except ZeroDivisionError:
            alpha = 0
        if alpha <= 0:
            self._timer.stop()
            self.deleteLater()
            return
        self._color.setAlpha(alpha)
        self.move(self.x() + int(self._dx), self.y() + int(self._dy))
        self._dy += 0.15
        self._dx *= 0.97
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(self._color))
        painter.drawEllipse(1, 1, self._size, self._size)


PARTICLE_COLORS = [
    "#ff6b6b", "#ffd93d", "#6bcb77", "#4d96ff",
    "#ff9de6", "#ff9f6e", "#8bd3ff", "#c9b1ff",
]


def burst(parent, x, y, count=12, colors=None, enabled=True):
    if not enabled:
        return
    if colors is None:
        colors = PARTICLE_COLORS
    for _ in range(count):
        color = random.choice(colors)
        p = Particle(parent, x, y, color)
        p._dx = random.uniform(-4, 4)
        p._dy = random.uniform(-5, -1)
