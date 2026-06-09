"""
grid_widget.py — Composant graphique de la grille Néonaure.

Responsabilités :
  - Afficher la grille (cases, chiffres, bordures de motifs)
  - Gérer la sélection de case (clic souris)
  - Gérer la saisie utilisateur (clavier)
  - Émettre le signal cell_value_changed vers le contrôleur

Ce widget ne touche JAMAIS aux données métier.
Toute saisie transite par le signal cell_value_changed.
"""

from PyQt5.QtWidgets import QWidget, QSizePolicy
from PyQt5.QtCore import Qt, QRect, QSize, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QFont, QPen


# ── Constantes visuelles ─────────────────────────────────────────────
CELL_SIZE     = 60          # taille d'une case en pixels
BORDER_THIN   = 1           # épaisseur bordure intra-motif
BORDER_THICK  = 3           # épaisseur bordure inter-motif

# Couleurs
C_BG_VIDE     = QColor(255, 255, 255)   # case vide, saisissable
C_BG_FIXE     = QColor(210, 210, 210)   # case pré-remplie (non modifiable)
C_BG_SELECT   = QColor(173, 216, 230)   # case sélectionnée (bleu clair)
C_BG_ERREUR   = QColor(255, 200, 200)   # case en erreur (rouge clair)
C_TEXTE_FIXE  = QColor(50,  50,  50)    # chiffre pré-rempli (gris foncé)
C_TEXTE_JOUEUR= QColor(0,   80,  180)   # chiffre saisi par le joueur (bleu)
C_TEXTE_ERREUR= QColor(180,  0,    0)   # chiffre en erreur (rouge)
C_BORDURE     = QColor(0,    0,    0)   # noir pour les bordures
# ─────────────────────────────────────────────────────────────────────


class GridWidget(QWidget):
    """
    Widget de rendu de la grille Néonaure.

    Interface attendue de grid_data (fourni par le contrôleur) :
    {
        "cols"  : int,
        "rows"  : int,
        "cells" : [
            {
                "col"      : int,
                "row"      : int,
                "value"    : int,    # 0 = vide
                "motif_id" : str,    # ex. "motif1"
                "is_fixed" : bool,   # True → case de départ, non modifiable
                "is_error" : bool    # True → contrainte violée
            },
            ...
        ]
    }

    Signal émis :
        cell_value_changed(col: int, row: int, value: int)
            value = 0 signifie effacement de la case
    """

    cell_value_changed = pyqtSignal(int, int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._grid_data  = None   # dict complet reçu du contrôleur
        self._cell_map   = {}     # (col, row) → dict cellule
        self._selected   = None   # (col, row) sélectionnée ou None
        self._cols       = 0
        self._rows       = 0

        self.setFocusPolicy(Qt.StrongFocus)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

    # ──────────────────────────────────────────────────────────────────
    # Interface publique (appelée par MainWindow)
    # ──────────────────────────────────────────────────────────────────

    def update_grid(self, grid_data: dict):
        """
        Rafraîchit l'affichage à partir des nouvelles données du contrôleur.
        Préserve la sélection courante si la case existe encore.
        """
        previous_selected = self._selected

        self._grid_data = grid_data
        self._cols      = grid_data.get("cols", 0)
        self._rows      = grid_data.get("rows", 0)
        self._cell_map  = {
            (c["col"], c["row"]): c
            for c in grid_data.get("cells", [])
        }

        # Conserver la sélection si la case existe toujours
        if previous_selected and previous_selected in self._cell_map:
            self._selected = previous_selected
        else:
            self._selected = None

        self.updateGeometry()
        self.update()   # déclenche paintEvent

    def clear(self):
        """Réinitialise le widget (aucune grille chargée)."""
        self._grid_data = None
        self._cell_map  = {}
        self._selected  = None
        self._cols      = 0
        self._rows      = 0
        self.update()

    # ──────────────────────────────────────────────────────────────────
    # Taille préférée (utilisée par QScrollArea / layout)
    # ──────────────────────────────────────────────────────────────────

    def sizeHint(self) -> QSize:
        if self._cols == 0 or self._rows == 0:
            return QSize(300, 300)
        # +2 pour inclure la bordure externe (1px de chaque côté)
        return QSize(self._cols * CELL_SIZE + 2,
                     self._rows * CELL_SIZE + 2)

    # ──────────────────────────────────────────────────────────────────
    # Rendu (QPainter)
    # ──────────────────────────────────────────────────────────────────

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, False)

        if self._grid_data is None:
            painter.fillRect(self.rect(), QColor(240, 240, 240))
            painter.setPen(QColor(120, 120, 120))
            painter.drawText(self.rect(), Qt.AlignCenter, "Aucune grille chargée")
            return

        self._draw_backgrounds(painter)
        self._draw_numbers(painter)
        self._draw_borders(painter)

    def _draw_backgrounds(self, painter: QPainter):
        """Dessine le fond coloré de chaque case."""
        for (col, row), cell in self._cell_map.items():
            rect = self._cell_rect(col, row)

            if (col, row) == self._selected:
                color = C_BG_SELECT
            elif cell["is_error"]:
                color = C_BG_ERREUR
            elif cell["is_fixed"]:
                color = C_BG_FIXE
            else:
                color = C_BG_VIDE

            painter.fillRect(rect, color)

    def _draw_numbers(self, painter: QPainter):
        """Affiche les chiffres dans les cases."""
        font = QFont("Arial", CELL_SIZE // 3, QFont.Bold)
        painter.setFont(font)

        for (col, row), cell in self._cell_map.items():
            if cell["value"] == 0:
                continue

            rect = self._cell_rect(col, row)

            if cell["is_error"]:
                painter.setPen(C_TEXTE_ERREUR)
            elif cell["is_fixed"]:
                painter.setPen(C_TEXTE_FIXE)
            else:
                painter.setPen(C_TEXTE_JOUEUR)

            painter.drawText(rect, Qt.AlignCenter, str(cell["value"]))

    def _draw_borders(self, painter: QPainter):
        """
        Trace les bordures :
          - Épaisse  : séparation entre deux motifs différents
          - Fine     : séparation entre deux cases du même motif
          - Épaisse  : bordure externe de la grille
        """
        # Bordure externe
        pen = QPen(C_BORDURE, BORDER_THICK)
        painter.setPen(pen)
        painter.drawRect(1, 1,
                         self._cols * CELL_SIZE,
                         self._rows * CELL_SIZE)

        # Bordures internes
        for col in range(self._cols):
            for row in range(self._rows):
                cell = self._cell_map.get((col, row))
                if cell is None:
                    continue

                x = 1 + col * CELL_SIZE
                y = 1 + row * CELL_SIZE

                # Bord droit : entre (col, row) et (col+1, row)
                if col + 1 < self._cols:
                    voisin = self._cell_map.get((col + 1, row))
                    if voisin:
                        inter_motif = cell["motif_id"] != voisin["motif_id"]
                        epaisseur   = BORDER_THICK if inter_motif else BORDER_THIN
                        painter.setPen(QPen(C_BORDURE, epaisseur))
                        painter.drawLine(x + CELL_SIZE, y,
                                         x + CELL_SIZE, y + CELL_SIZE)

                # Bord bas : entre (col, row) et (col, row+1)
                if row + 1 < self._rows:
                    voisin = self._cell_map.get((col, row + 1))
                    if voisin:
                        inter_motif = cell["motif_id"] != voisin["motif_id"]
                        epaisseur   = BORDER_THICK if inter_motif else BORDER_THIN
                        painter.setPen(QPen(C_BORDURE, epaisseur))
                        painter.drawLine(x,                y + CELL_SIZE,
                                         x + CELL_SIZE,   y + CELL_SIZE)

    # ──────────────────────────────────────────────────────────────────
    # Helpers géométriques
    # ──────────────────────────────────────────────────────────────────

    def _cell_rect(self, col: int, row: int) -> QRect:
        """Retourne le QRect de la case (col, row)."""
        return QRect(1 + col * CELL_SIZE,
                     1 + row * CELL_SIZE,
                     CELL_SIZE,
                     CELL_SIZE)

    def _pos_to_cell(self, x: int, y: int):
        """Convertit des coordonnées pixel en (col, row), ou None si hors grille."""
        col = (x - 1) // CELL_SIZE
        row = (y - 1) // CELL_SIZE
        if 0 <= col < self._cols and 0 <= row < self._rows:
            return (col, row)
        return None

    # ──────────────────────────────────────────────────────────────────
    # Événements utilisateur
    # ──────────────────────────────────────────────────────────────────

    def mousePressEvent(self, event):
        """Sélectionne la case cliquée."""
        if self._grid_data is None:
            return
        pos = self._pos_to_cell(event.x(), event.y())
        if pos:
            self._selected = pos
            self.update()
        self.setFocus()

    def keyPressEvent(self, event):
        """
        Gère la saisie clavier :
          - Touches 1–9  : saisir un chiffre
          - Delete / Backspace : effacer la case
          - Flèches       : déplacer la sélection
        """
        if self._selected is None or self._grid_data is None:
            return

        col, row = self._selected
        cell = self._cell_map.get((col, row))
        if cell is None:
            return

        key = event.key()

        # ── Saisie d'un chiffre ──
        if Qt.Key_1 <= key <= Qt.Key_9:
            if not cell["is_fixed"]:
                self.cell_value_changed.emit(col, row, key - Qt.Key_0)
            return

        # ── Effacement ──
        if key in (Qt.Key_Delete, Qt.Key_Backspace):
            if not cell["is_fixed"]:
                self.cell_value_changed.emit(col, row, 0)
            return

        # ── Navigation ──
        moves = {
            Qt.Key_Left:  (-1,  0),
            Qt.Key_Right: ( 1,  0),
            Qt.Key_Up:    ( 0, -1),
            Qt.Key_Down:  ( 0,  1),
        }
        if key in moves:
            dc, dr = moves[key]
            new_col = col + dc
            new_row = row + dr
            if 0 <= new_col < self._cols and 0 <= new_row < self._rows:
                self._selected = (new_col, new_row)
                self.update()
