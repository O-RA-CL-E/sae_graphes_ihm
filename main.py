"""
main.py — Point d'entrée de l'application Néonaure.

Usage :
    python main.py

Structure attendue du projet :
    main.py
    model/
        case.py
        motif.py
        grille.py
    view/
        main_window.py
        grid_widget.py
    controller/
        game_controller.py
        grille_io.py
    solver/
        solveur.py
    grilles/
        *.json
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon

from view.main_window import MainWindow
from controller.game_controller import GameController


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("Néonaure")
    app.setApplicationVersion("1.0")

    controller = GameController()
    window = MainWindow(controller)
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
