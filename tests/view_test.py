"""
main.py — Point d'entrée de l'application Néonaure.

Lance l'interface avec le stub contrôleur pendant le développement.
Remplacer ControllerStub par GameController (Yanis) pour la version finale.
"""

import sys
from PyQt5.QtWidgets import QApplication

from view.main_window import MainWindow
from tests.controller_test import ControllerStub

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Néonaure")

    # TODO : remplacer par GameController quand Yanis aura terminé
    # from controller.game_controller import GameController
    # controller = GameController()
    controller = ControllerStub()

    window = MainWindow(controller)
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
