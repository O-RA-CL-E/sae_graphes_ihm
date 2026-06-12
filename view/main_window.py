"""
main_window.py — Fenêtre principale de l'application Néonaure (version pro).

Améliorations :
  - Panneau latéral sombre : timer, compteurs cases vides / erreurs, boutons
  - Menubar et status bar avec thème sombre assorti
  - Chronomètre de jeu intégré (100% côté View, pas de logique métier)
"""

from PyQt5.QtWidgets import (
    QMainWindow, QAction, QFileDialog, QMessageBox,
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QLabel, QFrame, QPushButton, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer

from view.grid_widget import GridWidget


# ── Feuilles de style ─────────────────────────────────────────────────
STYLE_WINDOW = """
QMenuBar {
    background-color: #2A2A3A;
    color: #D8D4CC;
    padding: 4px 8px;
    font-size: 13px;
    font-family: "Segoe UI";
}
QMenuBar::item { padding: 4px 10px; border-radius: 4px; }
QMenuBar::item:selected { background-color: #4A7FBF; }
QMenu {
    background-color: #3A3A4A;
    color: #D8D4CC;
    border: 1px solid #555568;
    font-family: "Segoe UI";
    font-size: 13px;
}
QMenu::item { padding: 6px 24px; }
QMenu::item:selected { background-color: #4A7FBF; }
QMenu::separator { height: 1px; background: #555568; margin: 4px 0; }
QStatusBar {
    background-color: #2A2A3A;
    color: #7A7A9A;
    font-size: 11px;
    font-family: "Segoe UI";
    padding: 0 8px;
}
"""

STYLE_PANEL = """
QFrame#panel {
    background-color: #23233A;
    border-radius: 12px;
}
"""

BTN_PRIMARY = """
QPushButton {
    background-color: #4A7FBF;
    color: #FFFFFF;
    border: none;
    border-radius: 7px;
    padding: 11px 0;
    font-size: 13px;
    font-weight: bold;
    font-family: "Segoe UI";
}
QPushButton:hover    { background-color: #5B90D4; }
QPushButton:pressed  { background-color: #3A6FAF; }
QPushButton:disabled { background-color: #404058; color: #666680; }
"""

BTN_GHOST = """
QPushButton {
    background-color: transparent;
    color: #9898B8;
    border: 1px solid #404058;
    border-radius: 7px;
    padding: 9px 0;
    font-size: 12px;
    font-family: "Segoe UI";
}
QPushButton:hover    { background-color: #2E2E48; color: #D8D4CC; border-color: #5A5A78; }
QPushButton:pressed  { background-color: #1E1E30; }
QPushButton:disabled { color: #404058; border-color: #303048; }
"""
# ─────────────────────────────────────────────────────────────────────


class MainWindow(QMainWindow):
    """Fenêtre principale de l'application Néonaure."""

    def __init__(self, controller):
        super().__init__()
        self._controller      = controller
        self._grille_chargee  = False
        self._secondes        = 0

        self.setWindowTitle("Néonaure")
        self.setMinimumSize(740, 580)
        self.setStyleSheet(STYLE_WINDOW)

        self._build_ui()
        self._build_menus()
        self._connect_signals()
        self._init_timer()

    # ── Construction de l'interface ───────────────────────────────────

    def _build_ui(self):
        central = QWidget()
        central.setStyleSheet("background-color: #F0EDE8;")
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(16)

        # ── Zone grille (gauche, extensible) ─────────────────────────
        scroll = QScrollArea()
        scroll.setAlignment(Qt.AlignCenter)
        scroll.setWidgetResizable(False)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._grid_widget = GridWidget()
        scroll.setWidget(self._grid_widget)
        root.addWidget(scroll, stretch=1)

        # ── Panneau latéral (droite, largeur fixe) ───────────────────
        panel = QFrame()
        panel.setObjectName("panel")
        panel.setStyleSheet(STYLE_PANEL)
        panel.setFixedWidth(210)

        pv = QVBoxLayout(panel)
        pv.setContentsMargins(20, 28, 20, 28)
        pv.setSpacing(0)

        # Titre
        lbl_logo = QLabel("NÉONAURE")
        lbl_logo.setAlignment(Qt.AlignCenter)
        lbl_logo.setStyleSheet(
            "font-size:19px; font-weight:bold; color:#F0EDE8;"
            "letter-spacing:4px; font-family:'Segoe UI'; background:transparent;"
        )
        pv.addWidget(lbl_logo)

        lbl_sub = QLabel("variante du Sudoku")
        lbl_sub.setAlignment(Qt.AlignCenter)
        lbl_sub.setStyleSheet(
            "font-size:10px; color:#5A5A7A; font-family:'Segoe UI';"
            "background:transparent; padding-bottom:16px;"
        )
        pv.addWidget(lbl_sub)

        pv.addWidget(self._separator())
        pv.addSpacing(18)

        # Stat : timer
        pv.addWidget(self._stat_label("TEMPS"))
        self._lbl_timer = self._stat_value("00:00")
        pv.addWidget(self._lbl_timer)
        pv.addSpacing(14)

        # Stat : cases vides
        pv.addWidget(self._stat_label("CASES VIDES"))
        self._lbl_vides = self._stat_value("—")
        pv.addWidget(self._lbl_vides)
        pv.addSpacing(14)

        # Stat : erreurs
        pv.addWidget(self._stat_label("ERREURS"))
        self._lbl_erreurs = self._stat_value("—")
        pv.addWidget(self._lbl_erreurs)

        pv.addSpacing(22)
        pv.addWidget(self._separator())
        pv.addSpacing(22)

        # Boutons
        self._btn_resoudre = QPushButton("Résoudre")
        self._btn_resoudre.setStyleSheet(BTN_PRIMARY)
        self._btn_resoudre.setEnabled(False)
        self._btn_reinit   = QPushButton("Réinitialiser")
        self._btn_charger  = QPushButton("Charger une grille…")
        self._btn_sauvegarder = QPushButton("Sauvegarder…")
        pv.addWidget(self._btn_resoudre)

        pv.addSpacing(8)

        self._btn_reinit = QPushButton("Réinitialiser")
        self._btn_reinit.setStyleSheet(BTN_GHOST)
        self._btn_reinit.setEnabled(False)
        pv.addWidget(self._btn_reinit)

        pv.addSpacing(14)

        self._btn_charger = QPushButton("Charger…")
        self._btn_charger.setStyleSheet(BTN_GHOST)
        pv.addWidget(self._btn_charger)

        pv.addSpacing(8)

        self._btn_sauvegarder = QPushButton("Sauvegarder…")
        self._btn_sauvegarder.setStyleSheet(BTN_GHOST)
        self._btn_sauvegarder.setEnabled(False)
        pv.addWidget(self._btn_sauvegarder)

        pv.addStretch()
        root.addWidget(panel)

        # Barre de statut
        self._lbl_status = QLabel("Aucune grille chargée")
        self.statusBar().addWidget(self._lbl_status)

    @staticmethod
    def _separator() -> QFrame:
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFixedHeight(1)
        sep.setStyleSheet("background-color: #353550; border: none;")
        return sep

    @staticmethod
    def _stat_label(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet(
            "font-size:9px; color:#5A5A7A; letter-spacing:2px;"
            "font-family:'Segoe UI'; background:transparent;"
        )
        return lbl

    @staticmethod
    def _stat_value(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet(
            "font-size:26px; font-weight:bold; color:#F0EDE8;"
            "font-family:'Segoe UI'; background:transparent;"
        )
        return lbl

    def _build_menus(self):
        mb = self.menuBar()

        # Fichier
        m = mb.addMenu("&Fichier")
        self._act_charger     = QAction("&Charger une grille…",  self, shortcut="Ctrl+O")
        self._act_sauvegarder = QAction("&Sauvegarder…",         self, shortcut="Ctrl+S")
        self._act_sauvegarder.setEnabled(False)
        self._act_quitter     = QAction("&Quitter",              self, shortcut="Ctrl+Q")
        m.addAction(self._act_charger)
        m.addAction(self._act_sauvegarder)
        m.addSeparator()
        m.addAction(self._act_quitter)

        # Jeu
        m = mb.addMenu("&Jeu")
        self._act_resoudre      = QAction("&Résoudre",      self, shortcut="Ctrl+R")
        self._act_reinitialiser = QAction("Ré&initialiser", self, shortcut="Ctrl+N")
        self._act_resoudre.setEnabled(False)
        self._act_reinitialiser.setEnabled(False)
        m.addAction(self._act_resoudre)
        m.addAction(self._act_reinitialiser)

        # Aide
        m = mb.addMenu("&Aide")
        self._act_regles = QAction("Règles du jeu", self, shortcut="F1")
        m.addAction(self._act_regles)

    def _connect_signals(self):
        # Menus
        self._act_charger.triggered.connect(self._on_charger)
        self._act_sauvegarder.triggered.connect(self._on_sauvegarder)
        self._act_quitter.triggered.connect(self.close)
        self._act_resoudre.triggered.connect(self._on_resoudre)
        self._act_reinitialiser.triggered.connect(self._on_reinitialiser)
        self._act_regles.triggered.connect(self._on_regles)

        # Boutons panneau (mêmes slots)
        self._btn_charger.clicked.connect(self._on_charger)
        self._btn_sauvegarder.clicked.connect(self._on_sauvegarder)
        self._btn_resoudre.clicked.connect(self._on_resoudre)
        self._btn_reinit.clicked.connect(self._on_reinitialiser)

        # Grille → contrôleur
        self._grid_widget.cell_value_changed.connect(self._on_cell_changed)
        self._grid_widget.cell_selected.connect(self._on_cell_selected)

    def _init_timer(self):
        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._on_tick)

    # ── Slots ─────────────────────────────────────────────────────────

    def _on_charger(self):
        fp, _ = QFileDialog.getOpenFileName(
            self, "Charger une grille", "grilles/",
            "Fichiers JSON (*.json);;Tous les fichiers (*)"
        )
        if not fp:
            return
        try:
            grid_data = self._controller.charger_grille(fp)
            self._afficher(grid_data)
            self._set_active(True)
            self._reset_timer()
            nom = fp.replace("\\", "/").split("/")[-1]
            self._status(f"Grille chargée : {nom}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur de chargement", str(e))

    def _on_sauvegarder(self):
        fp, _ = QFileDialog.getSaveFileName(
            self, "Sauvegarder", "grilles/",
            "Fichiers JSON (*.json);;Tous les fichiers (*)"
        )
        if not fp:
            return
        if not fp.endswith(".json"):
            fp += ".json"
        try:
            self._controller.sauvegarder_grille(fp)
            self._status("Grille sauvegardée.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))

    def _on_cell_changed(self, col: int, row: int, value: int):
        try:
            grid_data = self._controller.jouer_case(col, row, value)
            self._afficher(grid_data)
            if self._est_complete(grid_data):
                self._timer.stop()
                self._status("Grille résolue !")
                QMessageBox.information(self, "Victoire !",
                                        "Félicitations, vous avez résolu la grille !")
        except Exception as e:
            QMessageBox.warning(self, "Saisie invalide", str(e))

    def _on_cell_selected(self, col: int, row: int):
        """Met à jour les stats quand la sélection change."""
        if self._grille_chargee:
            self._maj_stats(self._controller._generer_grid_data())

    def _on_resoudre(self):
        if QMessageBox.question(
            self, "Résoudre automatiquement",
            "Afficher la solution ?\nVotre progression sera perdue.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        ) != QMessageBox.Yes:
            return
        try:
            grid_data = self._controller.resoudre()
            self._afficher(grid_data)
            self._timer.stop()
            self._status("Solution affichée.")
            if self._est_complete(grid_data):
                QMessageBox.information(self, "Résolu !",
                                        "La solution a été résolue automatiquement !")
        except Exception as e:
            QMessageBox.critical(self, "Résolution impossible", str(e))

    def _on_reinitialiser(self):
        if QMessageBox.question(
            self, "Réinitialiser",
            "Effacer toutes vos saisies ?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        ) != QMessageBox.Yes:
            return
        try:
            grid_data = self._controller.reinitialiser()
            self._afficher(grid_data)
            self._reset_timer()
            self._status("Grille réinitialisée.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))

    def _on_regles(self):
        QMessageBox.information(self, "Règles du Néonaure",
            "<h3>Règles du Néonaure</h3>"
            "<ol>"
            "<li>Un seul chiffre par case.</li>"
            "<li>Chaque chiffre doit être entouré de chiffres <b>tous différents</b>"
            " (8 voisins, diagonales incluses).</li>"
            "<li>Chaque <b>motif de N cases</b> (délimité en traits gras)"
            " doit contenir les chiffres de 1 à N.</li>"
            "</ol>"
            "<p><b>Navigation :</b> clic souris ou flèches.<br>"
            "<b>Saisie :</b> touches 1–9.<br>"
            "<b>Effacement :</b> Suppr ou Retour arrière.</p>"
        )

    def _on_tick(self):
        self._secondes += 1
        m, s = divmod(self._secondes, 60)
        self._lbl_timer.setText(f"{m:02d}:{s:02d}")

    # ── Utilitaires ───────────────────────────────────────────────────

    def _afficher(self, grid_data: dict):
        """Passe les données à la grille et met à jour le panneau."""
        self._grid_widget.update_grid(grid_data)
        self._grid_widget.adjustSize()
        self._maj_stats(grid_data)
        self._grid_widget.setMinimumSize(self._grid_widget.sizeHint())

    def _maj_stats(self, grid_data: dict):
        cells   = grid_data.get("cells", [])
        vides   = sum(1 for c in cells if c["value"] == 0)
        erreurs = sum(1 for c in cells if c["is_error"])

        self._lbl_vides.setText("✓" if vides == 0 else str(vides))
        self._lbl_vides.setStyleSheet(
            "font-size:26px; font-weight:bold; background:transparent;"
            "font-family:'Segoe UI'; color:"
            + ("#5EBF8A;" if vides == 0 else "#F0EDE8;")
        )

        self._lbl_erreurs.setText(str(erreurs))
        self._lbl_erreurs.setStyleSheet(
            "font-size:26px; font-weight:bold; background:transparent;"
            "font-family:'Segoe UI'; color:"
            + ("#E05C5C;" if erreurs > 0 else "#F0EDE8;")
        )

    def _set_active(self, active: bool):
        self._grille_chargee = active
        for w in (self._act_sauvegarder, self._act_resoudre,
                  self._act_reinitialiser, self._btn_resoudre,
                  self._btn_reinit, self._btn_sauvegarder):
            w.setEnabled(active)

    def _reset_timer(self):
        self._secondes = 0
        self._lbl_timer.setText("00:00")
        self._timer.start()

    def _status(self, msg: str):
        self._lbl_status.setText(msg)

    @staticmethod
    def _est_complete(grid_data: dict) -> bool:
        cells = grid_data.get("cells", [])
        return bool(cells) and all(
            c["value"] != 0 and not c["is_error"] for c in cells
        )