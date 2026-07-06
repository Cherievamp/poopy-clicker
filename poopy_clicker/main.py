import sys
from PyQt6.QtWidgets import QApplication
from .game_window import Game


def main():
    app = QApplication(sys.argv)
    window = Game()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
