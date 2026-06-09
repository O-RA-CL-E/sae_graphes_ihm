"""
main_window.py — Fenêtre principale de l'application Néonaure.

Responsabilités :
  - Barre de menus (Fichier, Jeu, Aide)
  - Contient et affiche GridWidget
  - Relaie les actions utilisateur vers le contrôleur
  - Met à jour l'affichage avec les données retournées par le contrôleur

Interface attendue du contrôleur (game_controller.py de Yanis) :
    charger_grille(filepath: str) -> dict        # retourne grid_data
    sauvegarder_grille(filepath: str) -> None
    jouer_case(col: int, row: int, val: int) -> dict
    resoudre() -> dict
    reinitialiser() -> dict
"""

from PyQt5.QtWidgets import (
    QMainWindow, QAction, QFileDialog, QMessageBox,
    QWidget, QVBoxLayout, QScrollArea, QLabel
)
from PyQt5.QtCore import Qt

from view.grid_widget import GridWidget


class MainWindow(QMainWindow):
    """Fenêtre principale de l'application Néonaure."""

    def __init__(self, controller):
        super().__init__()
        self._controller   = controller
        self._grille_chargee = False

        self.setWindowTitle("Néonaure")
        self.setMinimumSize(500, 520)

        self._build_ui()
        self._build_menus()
        self._connect_signals()

    # ──────────────────────────────────────────────────────────────────
    # Construction de l'interface
    # ──────────────────────────────────────────────────────────────────

    def _build_ui(self):
        """Construit la zone centrale (scroll + grille)."""
        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(10, 10, 10, 10)

        # QScrollArea pour supporter les grilles larges
        scroll = QScrollArea()
        scroll.setAlignment(Qt.AlignCenter)
        scroll.setWidgetResizable(False)

        self._grid_widget = GridWidget()
        scroll.setWidget(self._grid_widget)

        layout.addWidget(scroll)

        # Label de statut en bas de fenêtre
        self._status_label = QLabel("Aucune grille chargée — Fichier > Charger")
        self.statusBar().addWidget(self._status_label)

    def _build_menus(self):
        """Construit la barre de menus."""
        menubar = self.menuBar()

        # ── Fichier ──────────────────────────────────────────────────
        m_fichier = menubar.addMenu("&Fichier")

        self._act_charger = QAction("&Charger une grille…", self)
        self._act_charger.setShortcut("Ctrl+O")
        self._act_charger.setStatusTip("Ouvrir un fichier JSON de grille")

        self._act_sauvegarder = QAction("&Sauvegarder la grille…", self)
        self._act_sauvegarder.setShortcut("Ctrl+S")
        self._act_sauvegarder.setStatusTip("Sauvegarder la progression en JSON")
        self._act_sauvegarder.setEnabled(False)

        self._act_quitter = QAction("&Quitter", self)
        self._act_quitter.setShortcut("Ctrl+Q")

        m_fichier.addAction(self._act_charger)
        m_fichier.addAction(self._act_sauvegarder)
        m_fichier.addSeparator()
        m_fichier.addAction(self._act_quitter)

        # ── Jeu ──────────────────────────────────────────────────────
        m_jeu = menubar.addMenu("&Jeu")

        self._act_resoudre = QAction("&Résoudre automatiquement", self)
        self._act_resoudre.setShortcut("Ctrl+R")
        self._act_resoudre.setStatusTip("Afficher la solution de la grille")
        self._act_resoudre.setEnabled(False)

        self._act_reinitialiser = QAction("Ré&initialiser", self)
        self._act_reinitialiser.setShortcut("Ctrl+N")
        self._act_reinitialiser.setStatusTip("Effacer toutes les saisies")
        self._act_reinitialiser.setEnabled(False)

        m_jeu.addAction(self._act_resoudre)
        m_jeu.addAction(self._act_reinitialiser)

        # ── Aide ─────────────────────────────────────────────────────
        m_aide = menubar.addMenu("&Aide")

        self._act_regles = QAction("Règles du jeu", self)
        self._act_regles.setShortcut("F1")

        m_aide.addAction(self._act_regles)

    def _connect_signals(self):
        """Connecte les signaux aux slots."""
        self._act_charger.triggered.connect(self._on_charger)
        self._act_sauvegarder.triggered.connect(self._on_sauvegarder)
        self._act_quitter.triggered.connect(self.close)
        self._act_resoudre.triggered.connect(self._on_resoudre)
        self._act_reinitialiser.triggered.connect(self._on_reinitialiser)
        self._act_regles.triggered.connect(self._on_afficher_regles)

        # GridWidget → contrôleur : saisie d'une valeur
        self._grid_widget.cell_value_changed.connect(self._on_cell_value_changed)

    # ──────────────────────────────────────────────────────────────────
    # Slots — actions utilisateur
    # ──────────────────────────────────────────────────────────────────

    def _on_charger(self):
        """Dialogue de chargement d'un fichier JSON."""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Charger une grille",
            "grilles/",
            "Fichiers JSON (*.json);;Tous les fichiers (*)"
        )
        if not filepath:
            return

        try:
            grid_data = self._controller.charger_grille(filepath)
            self._afficher_grille(grid_data)
            nom = filepath.split("/")[-1]
            self._set_status(f"Grille chargée : {nom}")
            self._set_grille_active(True)
        except Exception as e:
            QMessageBox.critical(self, "Erreur de chargement",
                                 f"Impossible de charger la grille :\n{e}")

    def _on_sauvegarder(self):
        """Dialogue de sauvegarde de la grille courante."""
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Sauvegarder la grille",
            "grilles/",
            "Fichiers JSON (*.json);;Tous les fichiers (*)"
        )
        if not filepath:
            return
        if not filepath.endswith(".json"):
            filepath += ".json"

        try:
            self._controller.sauvegarder_grille(filepath)
            nom = filepath.split("/")[-1]
            self._set_status(f"Grille sauvegardée : {nom}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur de sauvegarde",
                                 f"Impossible de sauvegarder :\n{e}")

    def _on_cell_value_changed(self, col: int, row: int, value: int):
        """
        Déclenché par GridWidget quand l'utilisateur saisit ou efface une valeur.
        Délègue au contrôleur et rafraîchit l'affichage.
        """
        try:
            grid_data = self._controller.jouer_case(col, row, value)
            self._afficher_grille(grid_data)

            if self._grille_complete(grid_data):
                self._set_status("Félicitations — grille résolue !")
                QMessageBox.information(self, "Victoire !",
                                        "Bravo, vous avez résolu la grille !")
        except Exception as e:
            QMessageBox.warning(self, "Saisie invalide", str(e))

    def _on_resoudre(self):
        """Demande la résolution automatique après confirmation."""
        rep = QMessageBox.question(
            self, "Résoudre automatiquement",
            "Voulez-vous afficher la solution ?\n"
            "Votre progression sera remplacée.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if rep != QMessageBox.Yes:
            return

        try:
            grid_data = self._controller.resoudre()
            self._afficher_grille(grid_data)
            self._set_status("Solution affichée.")
        except Exception as e:
            QMessageBox.critical(self, "Résolution impossible",
                                 f"Le solveur n'a pas trouvé de solution :\n{e}")

    def _on_reinitialiser(self):
        """Réinitialise la grille à son état initial après confirmation."""
        rep = QMessageBox.question(
            self, "Réinitialiser",
            "Effacer toutes vos saisies et recommencer depuis le début ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if rep != QMessageBox.Yes:
            return

        try:
            grid_data = self._controller.reinitialiser()
            self._afficher_grille(grid_data)
            self._set_status("Grille réinitialisée.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))

    def _on_afficher_regles(self):
        """Affiche les règles du jeu."""
        regles = (
            "<h3>Règles du Néonaure</h3>"
            "<p>Remplissez la grille avec des chiffres selon ces trois contraintes :</p>"
            "<ol>"
            "<li>Un seul chiffre par case.</li>"
            "<li>Chaque chiffre doit être entouré de chiffres <b>tous différents</b> "
            "(8 voisins, diagonales comprises).</li>"
            "<li>Chaque <b>motif de N cases</b> (délimité par des traits gras) "
            "doit contenir tous les chiffres de 1 à N.</li>"
            "</ol>"
            "<p><b>Navigation :</b> clic souris ou touches fléchées.<br>"
            "<b>Saisie :</b> touches 1–9.<br>"
            "<b>Effacement :</b> Suppr ou Retour arrière.</p>"
        )
        QMessageBox.information(self, "Règles du jeu", regles)

    # ──────────────────────────────────────────────────────────────────
    # Méthodes utilitaires privées
    # ──────────────────────────────────────────────────────────────────

    def _afficher_grille(self, grid_data: dict):
        """Passe les données au GridWidget et redimensionne la fenêtre si besoin."""
        self._grid_widget.update_grid(grid_data)
        self._grid_widget.adjustSize()

    def _set_grille_active(self, active: bool):
        """Active ou désactive les actions qui nécessitent une grille chargée."""
        self._grille_chargee = active
        self._act_sauvegarder.setEnabled(active)
        self._act_resoudre.setEnabled(active)
        self._act_reinitialiser.setEnabled(active)

    def _set_status(self, message: str):
        """Met à jour le label de la barre de statut."""
        self._status_label.setText(message)

    @staticmethod
    def _grille_complete(grid_data: dict) -> bool:
        """
        Retourne True si toutes les cases sont remplies sans erreur.
        Vérification superficielle côté vue ; la validation métier
        est assurée par le contrôleur (is_error dans chaque cellule).
        """
        cells = grid_data.get("cells", [])
        return bool(cells) and all(
            c["value"] != 0 and not c["is_error"]
            for c in cells
        )
