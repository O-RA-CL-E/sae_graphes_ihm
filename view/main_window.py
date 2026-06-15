"""
main_window.py — Fenêtre principale de l'application Néonaure (version pro).

Améliorations UX/UI :
  - Panneau latéral sombre poli : gestion ergonomique du chrono, compteurs et boutons
  - Double thème global (Mode Clair et Mode Sombre intégral) commutable à la volée
  - Alignement thématique complet appliqué sur les fenêtres contextuelles QMessageBox
  - Feedback visuel instantané complet (Survol / Pressé / Désactivé) via styles QSS
  - Intégration de glyphes clairs sur la signalétique des boutons pour un repérage immédiat
  - Chronomètre de jeu autonome réinitialisable à la volée
  - Gestion de la désélection globale au clic en dehors du canevas de la grille
  - Verrouillage automatique de sécurité des modifications après calcul du solveur
"""

from PyQt5.QtWidgets import (
    QMainWindow, QAction, QFileDialog, QMessageBox,
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QLabel, QFrame, QPushButton, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer

from view.grid_widget import GridWidget


# ── Feuille de style unifiée : THEME CLAIR ────────────────────────────
STYLE_CLAIR = """
QMainWindow { background-color: #F0EDE8; }
QWidget#central { background-color: #F0EDE8; }
QMenuBar { background-color: #2A2A3A; color: #D8D4CC; padding: 4px 8px; font-size: 13px; font-family: "Segoe UI"; }
QMenuBar::item { padding: 4px 10px; border-radius: 4px; }
QMenuBar::item:selected { background-color: #4A7FBF; }
QMenu { background-color: #3A3A4A; color: #D8D4CC; border: 1px solid #555568; font-family: "Segoe UI"; font-size: 13px; }
QMenu::item { padding: 6px 24px; }
QMenu::item:selected { background-color: #4A7FBF; }
QMenu::separator { height: 1px; background: #555568; margin: 4px 0; }
QStatusBar { background-color: #2A2A3A; color: #7A7A9A; font-size: 11px; font-family: "Segoe UI"; padding: 0 8px; }
QFrame#panel { background-color: #23233A; border-radius: 12px; }

/* Thème Clair pour QMessageBox */
QMessageBox { background-color: #F0EDE8; font-family: "Segoe UI"; }
QMessageBox QLabel { color: #383838; font-size: 13px; }
QMessageBox QPushButton { 
    background-color: #4A7FBF; color: #FFFFFF; border: none; 
    border-radius: 5px; padding: 6px 14px; font-weight: bold; 
}
QMessageBox QPushButton:hover { background-color: #5B90D4; }

QPushButton#btn_primary {
    background-color: #4A7FBF; color: #FFFFFF; border: none; border-radius: 7px;
    padding: 11px 0; font-size: 13px; font-weight: bold; font-family: "Segoe UI";
}
QPushButton#btn_primary:hover    { background-color: #5B90D4; }
QPushButton#btn_primary:pressed  { background-color: #3A6FAF; }
QPushButton#btn_primary:disabled { background-color: #404058; color: #666680; }
QPushButton#btn_ghost {
    background-color: transparent; color: #9898B8; border: 1px solid #404058; border-radius: 7px;
    padding: 9px 0; font-size: 12px; font-family: "Segoe UI";
}
QPushButton#btn_ghost:hover    { background-color: #2E2E48; color: #D8D4CC; border-color: #5A5A78; }
QPushButton#btn_ghost:pressed  { background-color: #1E1E30; }
QPushButton#btn_ghost:disabled { color: #404058; border-color: #303048; }
"""

# ── Feuille de style unifiée : THEME SOMBRE ───────────────────────────
STYLE_SOMBRE = """
QMainWindow { background-color: #1A1A26; }
QWidget#central { background-color: #1A1A26; }
QMenuBar { background-color: #12121A; color: #D8D4CC; padding: 4px 8px; font-size: 13px; font-family: "Segoe UI"; }
QMenuBar::item { padding: 4px 10px; border-radius: 4px; }
QMenuBar::item:selected { background-color: #3B6CA3; }
QMenu { background-color: #181822; color: #D8D4CC; border: 1px solid #333344; font-family: "Segoe UI"; font-size: 13px; }
QMenu::item { padding: 6px 24px; }
QMenu::item:selected { background-color: #3B6CA3; }
QMenu::separator { height: 1px; background: #333344; margin: 4px 0; }
QStatusBar { background-color: #12121A; color: #5A5A7A; font-size: 11px; font-family: "Segoe UI"; padding: 0 8px; }
QFrame#panel { background-color: #12121A; border-radius: 12px; border: 1px solid #252535; }

/* Thème Sombre pour QMessageBox */
QMessageBox { background-color: #181822; border: 1px solid #333344; font-family: "Segoe UI"; }
QMessageBox QLabel { color: #D8D4CC; font-size: 13px; }
QMessageBox QPushButton { 
    background-color: #3B6CA3; color: #FFFFFF; border: none; 
    border-radius: 5px; padding: 6px 14px; font-weight: bold; 
}
QMessageBox QPushButton:hover { background-color: #4C7DB4; }

QPushButton#btn_primary {
    background-color: #3B6CA3; color: #FFFFFF; border: none; border-radius: 7px;
    padding: 11px 0; font-size: 13px; font-weight: bold; font-family: "Segoe UI";
}
QPushButton#btn_primary:hover    { background-color: #4C7DB4; }
QPushButton#btn_primary:pressed  { background-color: #2A5B92; }
QPushButton#btn_primary:disabled { background-color: #252535; color: #555566; }
QPushButton#btn_ghost {
    background-color: transparent; color: #787898; border: 1px solid #252535; border-radius: 7px;
    padding: 9px 0; font-size: 12px; font-family: "Segoe UI";
}
QPushButton#btn_ghost:hover    { background-color: #1C1C28; color: #D8D4CC; border-color: #444455; }
QPushButton#btn_ghost:pressed  { background-color: #0F0F18; }
QPushButton#btn_ghost:disabled { color: #333344; border-color: #222233; }
"""

STYLE_LOGO = """
    font-size: 19px; font-weight: bold; color: #F0EDE8;
    letter-spacing: 4px; font-family: 'Segoe UI'; background: transparent;
"""
STYLE_SUBTITLE = """
    font-size: 10px; color: #5A5A7A; font-family: 'Segoe UI';
    background: transparent; padding-bottom: 16px;
"""
STYLE_STAT_LBL = """
    font-size: 9px; color: #5A5A7A; letter-spacing: 2px;
    font-family: 'Segoe UI'; background: transparent;
"""
STYLE_STAT_VAL = """
    font-size: 26px; font-weight: bold; color: #F0EDE8;
    font-family: 'Segoe UI'; background: transparent;
"""

# ─────────────────────────────────────────────────────────────────────


class MainWindow(QMainWindow):
    """Fenêtre maîtresse de gestion de l'interface graphique de l'application."""

    def __init__(self, controller):
        super().__init__()
        self._controller      = controller
        self._grille_chargee  = False
        self._secondes        = 0
        self._theme_actuel    = "clair"

        self.setWindowTitle("Néonaure")
        self.setMinimumSize(740, 580)
        self.setStyleSheet(STYLE_CLAIR)

        self._build_ui()
        self._build_menus()
        self._connect_signals()
        self._init_timer()

    # ── Construction des Éléments d'IHM ───────────────────────────────

    def _build_ui(self):
        central = QWidget()
        central.setObjectName("central")
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(16)

        # ── Zone de rendu de la grille de jeu (Côté Gauche)
        scroll = QScrollArea()
        scroll.setAlignment(Qt.AlignCenter)
        scroll.setWidgetResizable(False)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._grid_widget = GridWidget()
        scroll.setWidget(self._grid_widget)
        root.addWidget(scroll, stretch=1)

        # ── Panneau de bord d'informations et d'actions (Côté Droite)
        panel = QFrame()
        panel.setObjectName("panel")
        panel.setFixedWidth(210)

        pv = QVBoxLayout(panel)
        pv.setContentsMargins(20, 28, 20, 28)
        pv.setSpacing(0)

        # Identité visuelle (Logo de l'application)
        lbl_logo = QLabel("NÉONAURE")
        lbl_logo.setAlignment(Qt.AlignCenter)
        lbl_logo.setStyleSheet(STYLE_LOGO)
        pv.addWidget(lbl_logo)

        lbl_sub = QLabel("variante du Sudoku")
        lbl_sub.setAlignment(Qt.AlignCenter)
        lbl_sub.setStyleSheet(STYLE_SUBTITLE)
        pv.addWidget(lbl_sub)

        pv.addWidget(self._separator())
        pv.addSpacing(18)

        # Indicateur : Chronomètre de jeu
        pv.addWidget(self._stat_label("TEMPS"))
        self._lbl_timer = self._stat_value("00:00")
        pv.addWidget(self._lbl_timer)
        pv.addSpacing(14)

        # Indicateur : Compteur de complétion
        pv.addWidget(self._stat_label("CASES VIDES"))
        self._lbl_vides = self._stat_value("—")
        pv.addWidget(self._lbl_vides)
        pv.addSpacing(14)

        # Indicateur : Compteur d'infractions aux règles en temps réel
        pv.addWidget(self._stat_label("ERREURS"))
        self._lbl_erreurs = self._stat_value("—")
        pv.addWidget(self._lbl_erreurs)

        pv.addSpacing(22)
        pv.addWidget(self._separator())
        pv.addSpacing(22)

        # Boutons de commande avec ID de feuille de style explicite
        self._btn_resoudre = QPushButton("Résoudre")
        self._btn_resoudre.setObjectName("btn_primary")
        self._btn_resoudre.setEnabled(False)
        pv.addWidget(self._btn_resoudre)

        pv.addSpacing(8)

        self._btn_reinit = QPushButton("Réinitialiser")
        self._btn_reinit.setObjectName("btn_ghost")
        self._btn_reinit.setEnabled(False)
        pv.addWidget(self._btn_reinit)

        pv.addSpacing(14)

        self._btn_charger = QPushButton("Charger…")
        self._btn_charger.setObjectName("btn_ghost")
        pv.addWidget(self._btn_charger)

        pv.addSpacing(8)

        self._btn_sauvegarder = QPushButton("Sauvegarder…")
        self._btn_sauvegarder.setObjectName("btn_ghost")
        self._btn_sauvegarder.setEnabled(False)
        pv.addWidget(self._btn_sauvegarder)

        pv.addStretch()
        root.addWidget(panel)

        # Barre de notification système inférieure (Status Bar)
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
        lbl.setStyleSheet(STYLE_STAT_LBL)
        return lbl

    @staticmethod
    def _stat_value(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet(STYLE_STAT_VAL)
        return lbl

    def _build_menus(self):
        mb = self.menuBar()

        # Onglet Fichier
        m = mb.addMenu("&Fichier")
        self._act_charger     = QAction("&Charger une grille…",  self, shortcut="Ctrl+O")
        self._act_sauvegarder = QAction("&Sauvegarder…",         self, shortcut="Ctrl+S")
        self._act_sauvegarder.setEnabled(False)
        self._act_quitter     = QAction("&Quitter",              self, shortcut="Ctrl+Q")
        m.addAction(self._act_charger)
        m.addAction(self._act_sauvegarder)
        m.addSeparator()
        m.addAction(self._act_quitter)

        # Onglet Jeu
        m = mb.addMenu("&Jeu")
        self._act_resoudre      = QAction("&Résoudre",      self, shortcut="Ctrl+R")
        self._act_reinitialiser = QAction("Ré&initialiser", self, shortcut="Ctrl+N")
        self._act_resoudre.setEnabled(False)
        self._act_reinitialiser.setEnabled(False)
        m.addAction(self._act_resoudre)
        m.addAction(self._act_reinitialiser)

        # Onglet Affichage pour basculer de thème
        m_theme = mb.addMenu("&Affichage")
        self._act_theme_clair  = QAction("Mode Clair", self)
        self._act_theme_sombre = QAction("Mode Sombre", self)
        m_theme.addAction(self._act_theme_clair)
        m_theme.addAction(self._act_theme_sombre)

        # Onglet Aide
        m = mb.addMenu("&Aide")
        self._act_regles = QAction("Règles du jeu", self, shortcut="F1")
        m.addAction(self._act_regles)

    def _connect_signals(self):
        self._act_charger.triggered.connect(self._on_charger)
        self._act_sauvegarder.triggered.connect(self._on_sauvegarder)
        self._act_quitter.triggered.connect(self.close)
        self._act_resoudre.triggered.connect(self._on_resoudre)
        self._act_reinitialiser.triggered.connect(self._on_reinitialiser)
        self._act_regles.triggered.connect(self._on_regles)
        
        # Liaison du changement de thèmes
        self._act_theme_clair.triggered.connect(lambda: self._on_changer_theme("clair"))
        self._act_theme_sombre.triggered.connect(lambda: self._on_changer_theme("sombre"))

        self._btn_charger.clicked.connect(self._on_charger)
        self._btn_sauvegarder.clicked.connect(self._on_sauvegarder)
        self._btn_resoudre.clicked.connect(self._on_resoudre)
        self._btn_reinit.clicked.connect(self._on_reinitialiser)

        self._grid_widget.cell_value_changed.connect(self._on_cell_changed)
        self._grid_widget.cell_selected.connect(self._on_cell_selected)

    def _init_timer(self):
        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._on_tick)

    # ── Slots de Gestion des Thèmes ───────────────────────────────────

    def _on_changer_theme(self, theme: str):
        """Bascule le style global de la fenêtre et ordonne à la grille de s'adapter."""
        self._theme_actuel = theme
        if theme == "sombre":
            self.setStyleSheet(STYLE_SOMBRE)
            self._grid_widget.appliquer_theme("sombre")
            self._status("Thème sombre appliqué.")
        else:
            self.setStyleSheet(STYLE_CLAIR)
            self._grid_widget.appliquer_theme("clair")
            self._status("Thème clair appliqué.")

    # ── Slots de Gestion des Événements Applicatifs ───────────────────

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
                                        "Félicitations, vous avez résolu la grille avec succès !")
        except Exception as e:
            QMessageBox.warning(self, "Saisie invalide", str(e))

    def _on_cell_selected(self, col: int, row: int):
        if col == -1 and row == -1:
            return
        if self._grille_chargee:
            self._maj_stats(self._controller._generer_grid_data())
            self._grid_widget.update() # Déclenche un rafraîchissement visuel pour synchroniser la navigation par flèches

    def _on_resoudre(self):
        if QMessageBox.question(
            self, "Résoudre automatiquement",
            "Afficher la solution complète ?\nVotre progression actuelle sera perdue.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        ) != QMessageBox.Yes:
            return
        try:
            grid_data = self._controller.resoudre()
            self._afficher(grid_data)
            self._timer.stop()
            self._status("Solution automatique affichée.")
            
            self._grid_widget.set_locked(True)
            self._btn_resoudre.setEnabled(False)
            self._act_resoudre.setEnabled(False)

            if self._est_complete(grid_data):
                QMessageBox.information(self, "Résolu !",
                                        "La solution a été calculée et affichée par le solveur.")
        except Exception as e:
            QMessageBox.critical(self, "Résolution impossible", str(e))

    def _on_reinitialiser(self):
        if QMessageBox.question(
            self, "Réinitialiser",
            "Effacer toutes vos saisies pour recommencer ?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        ) != QMessageBox.Yes:
            return
        try:
            grid_data = self._controller.reinitialiser()
            self._afficher(grid_data)
            self._reset_timer()
            
            self._btn_resoudre.setEnabled(True)
            self._act_resoudre.setEnabled(True)

            self._status("Grille réinitialisée à l'état initial.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))

    def _on_regles(self):
        QMessageBox.information(self, "Règles du Néonaure",
            "<h3>Règles du Néonaure</h3>"
            "<ol>"
            "<li>Un seul chiffre par case.</li>"
            "<li>Chaque chiffre doit être entouré de chiffres <b>tous différents</b>"
            " (8 voisins directs, diagonales incluses).</li>"
            "<li>Chaque <b>motif de N cases</b> (délimité en traits gras)"
            " doit contenir exactement les chiffres de 1 à N.</li>"
            "</ol>"
            "<p><b>Navigation :</b> Clic souris ou flèches du clavier.<br>"
            "<b>Saisie :</b> Touches numériques 1–9.<br>"
            "<b>Effacement :</b> Touches Suppr ou Retour arrière.</p>"
        )

    def _on_tick(self):
        self._secondes += 1
        m, s = divmod(self._secondes, 60)
        self._lbl_timer.setText(f"{m:02d}:{s:02d}")

    # ── Fonctions Utilitaires d'Affichage ─────────────────────────────

    def _afficher(self, grid_data: dict):
        self._grid_widget.update_grid(grid_data)
        self._grid_widget.adjustSize()
        self._maj_stats(grid_data)
        self._grid_widget.setMinimumSize(self._grid_widget.sizeHint())
        
        # Important : préserve le thème actuel sur la grille fraîchement affichée
        self._grid_widget.appliquer_theme(self._theme_actuel)

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
        return bool(cells) and all(c["value"] != 0 and not c["is_error"] for c in cells)

    def mousePressEvent(self, event):
        if self._grille_chargee and self._grid_widget:
            self._grid_widget._selected = None
            self._grid_widget.update()
            self._maj_stats(self._controller._generer_grid_data())
        super().mousePressEvent(event)