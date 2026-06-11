"""
grid_widget.py — Composant graphique de la grille Néonaure (version pro).

Améliorations visuelles :
  - Survol des cases (hover)
  - Mise en évidence du motif de la case sélectionnée
  - Sélection avec fond arrondi
  - Palette chaleureuse et moderne
  - Texte avec anti-aliasing
"""

from PyQt5.QtWidgets import QWidget, QSizePolicy
from PyQt5.QtCore import Qt, QRect, QRectF, QSize, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QPainterPath


# ── Constantes visuelles ──────────────────────────────────────────────
CELL_SIZE     = 60
BORDER_THIN   = 1
BORDER_THICK  = 3
CORNER_RADIUS = 5

# ── Palette ───────────────────────────────────────────────────────────
C_BG_VIDE    = QColor(252, 251, 248)   # blanc cassé
C_BG_FIXE    = QColor(224, 220, 213)   # beige gris — case fixe
C_BG_SELECT  = QColor(74,  127, 191)   # bleu acier — sélection
C_BG_HOVER   = QColor(232, 242, 255)   # bleu très pâle — survol
C_BG_MOTIF   = QColor(236, 245, 255)   # bleu pâle — même motif que sélection
C_BG_ERREUR  = QColor(253, 234, 232)   # rose pâle — erreur

C_TXT_FIXE   = QColor(38,  38,  38)    # quasi-noir — chiffre fixe
C_TXT_JOUEUR = QColor(26,  80,  140)   # bleu foncé — saisie joueur
C_TXT_SELECT = QColor(255, 255, 255)   # blanc — texte sur sélection
C_TXT_ERREUR = QColor(183,  28,  28)   # rouge foncé — erreur

C_BRD_FINE   = QColor(200, 194, 186)   # gris chaud — intra-motif
C_BRD_EPAIS  = QColor(38,  38,  38)    # quasi-noir — inter-motif / externe


class GridWidget(QWidget):
    """
    Widget de rendu de la grille Néonaure.

    Signal émis lors d'une saisie utilisateur :
        cell_value_changed(col: int, row: int, value: int)
        value = 0 → effacement

    Données attendues via update_grid(grid_data) :
    {
        "cols": int, "rows": int,
        "cells": [
            {"col", "row", "value", "motif_id", "is_fixed", "is_error"}
        ]
    }
    """

    cell_value_changed = pyqtSignal(int, int, int)
    cell_selected = pyqtSignal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._grid_data = None
        self._cell_map  = {}
        self._selected  = None
        self._hovered   = None
        self._cols      = 0
        self._rows      = 0

        self.setFocusPolicy(Qt.StrongFocus)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setMouseTracking(True)

    # ── Interface publique ────────────────────────────────────────────

    def update_grid(self, grid_data: dict):
        """Rafraîchit l'affichage. Préserve la sélection si la case existe encore."""
        prev = self._selected
        self._grid_data = grid_data
        self._cols      = grid_data.get("cols", 0)
        self._rows      = grid_data.get("rows", 0)
        self._cell_map  = {
            (c["col"], c["row"]): c
            for c in grid_data.get("cells", [])
        }
        self._selected = prev if (prev and prev in self._cell_map) else None
        self.updateGeometry()
        self.update()

    def clear(self):
        self._grid_data = None
        self._cell_map  = {}
        self._selected  = None
        self._hovered   = None
        self._cols = self._rows = 0
        self.update()

    def sizeHint(self) -> QSize:
        if self._cols == 0:
            return QSize(400, 400)
        return QSize(self._cols * CELL_SIZE + 2,
                     self._rows * CELL_SIZE + 2)

    # ── Rendu ─────────────────────────────────────────────────────────

    def paintEvent(self, _event):
        painter = QPainter(self)

        if self._grid_data is None:
            painter.fillRect(self.rect(), QColor(245, 243, 240))
            painter.setPen(QColor(160, 155, 148))
            painter.setFont(QFont("Segoe UI", 12))
            painter.drawText(self.rect(), Qt.AlignCenter,
                             "Charger une grille\npour commencer")
            return

        # Motif de la case sélectionnée (pour la surbrillance motif)
        selected_motif = None
        if self._selected:
            sc = self._cell_map.get(self._selected)
            if sc:
                selected_motif = sc["motif_id"]

        self._draw_backgrounds(painter, selected_motif)
        self._draw_numbers(painter)
        self._draw_borders(painter)

    def _draw_backgrounds(self, painter: QPainter, selected_motif):
        painter.setRenderHint(QPainter.Antialiasing, True)

        for (col, row), cell in self._cell_map.items():
            rect = self._cell_rect(col, row)
            pos  = (col, row)

            if pos == self._selected:
                # Fond neutre, puis overlay arrondi bleu
                base = C_BG_FIXE if cell["is_fixed"] else C_BG_VIDE
                painter.fillRect(rect, base)
                path = QPainterPath()
                path.addRoundedRect(QRectF(rect).adjusted(3, 3, -3, -3),
                                    CORNER_RADIUS, CORNER_RADIUS)
                painter.fillPath(path, C_BG_SELECT)
            elif cell["is_error"]:
                painter.fillRect(rect, C_BG_ERREUR)
            elif pos == self._hovered and not cell["is_fixed"]:
                painter.fillRect(rect, C_BG_HOVER)
            elif selected_motif and cell["motif_id"] == selected_motif:
                painter.fillRect(rect, C_BG_MOTIF)
            elif cell["is_fixed"]:
                painter.fillRect(rect, C_BG_FIXE)
            else:
                painter.fillRect(rect, C_BG_VIDE)

        painter.setRenderHint(QPainter.Antialiasing, False)

    def _draw_numbers(self, painter: QPainter):
        painter.setRenderHint(QPainter.TextAntialiasing, True)
        font_bold   = QFont("Segoe UI", CELL_SIZE // 3, QFont.Bold)
        font_normal = QFont("Segoe UI", CELL_SIZE // 3, QFont.Normal)

        for (col, row), cell in self._cell_map.items():
            if cell["value"] == 0:
                continue
            rect = self._cell_rect(col, row)
            pos  = (col, row)

            if pos == self._selected:
                painter.setPen(C_TXT_SELECT)
                painter.setFont(font_bold if cell["is_fixed"] else font_normal)
            elif cell["is_error"]:
                painter.setPen(C_TXT_ERREUR)
                painter.setFont(font_normal)
            elif cell["is_fixed"]:
                painter.setPen(C_TXT_FIXE)
                painter.setFont(font_bold)
            else:
                painter.setPen(C_TXT_JOUEUR)
                painter.setFont(font_normal)

            painter.drawText(rect, Qt.AlignCenter, str(cell["value"]))

    def _draw_borders(self, painter: QPainter):
        painter.setRenderHint(QPainter.Antialiasing, False)

        # Bordure externe épaisse
        painter.setPen(QPen(C_BRD_EPAIS, BORDER_THICK))
        painter.drawRect(1, 1,
                         self._cols * CELL_SIZE,
                         self._rows * CELL_SIZE)

        for col in range(self._cols):
            for row in range(self._rows):
                cell = self._cell_map.get((col, row))
                if cell is None:
                    continue
                x = 1 + col * CELL_SIZE
                y = 1 + row * CELL_SIZE

                # Bord droit
                if col + 1 < self._cols:
                    v = self._cell_map.get((col + 1, row))
                    if v:
                        diff = cell["motif_id"] != v["motif_id"]
                        painter.setPen(QPen(C_BRD_EPAIS if diff else C_BRD_FINE,
                                            BORDER_THICK if diff else BORDER_THIN))
                        painter.drawLine(x + CELL_SIZE, y,
                                         x + CELL_SIZE, y + CELL_SIZE)
                # Bord bas
                if row + 1 < self._rows:
                    v = self._cell_map.get((col, row + 1))
                    if v:
                        diff = cell["motif_id"] != v["motif_id"]
                        painter.setPen(QPen(C_BRD_EPAIS if diff else C_BRD_FINE,
                                            BORDER_THICK if diff else BORDER_THIN))
                        painter.drawLine(x,             y + CELL_SIZE,
                                         x + CELL_SIZE, y + CELL_SIZE)

    # ── Helpers géométriques ──────────────────────────────────────────

    def _cell_rect(self, col: int, row: int) -> QRect:
        return QRect(1 + col * CELL_SIZE,
                     1 + row * CELL_SIZE,
                     CELL_SIZE, CELL_SIZE)

    def _pos_to_cell(self, x: int, y: int) -> tuple[int, int] | None:
        col = (x - 1) // CELL_SIZE
        row = (y - 1) // CELL_SIZE
        if 0 <= col < self._cols and 0 <= row < self._rows:
            return (col, row)
        return None

    # ── Événements utilisateur ────────────────────────────────────────

    def mousePressEvent(self, event):
        if self._grid_data is None:
            return
        pos = self._pos_to_cell(event.x(), event.y())
        if pos:
            self._selected = pos
            self.cell_selected.emit(pos[0], pos[1])
            self.update()
        self.setFocus()

    def mouseMoveEvent(self, event):
        if self._grid_data is None:
            return
        pos = self._pos_to_cell(event.x(), event.y())
        if pos != self._hovered:
            self._hovered = pos
            self.update()

    def leaveEvent(self, _event):
        self._hovered = None
        self.update()

    def keyPressEvent(self, event):
        if self._selected is None or self._grid_data is None:
            return
        col, row = self._selected
        cell = self._cell_map.get((col, row))
        if cell is None:
            return

        key = event.key()

        if Qt.Key_1 <= key <= Qt.Key_9:
            value   = key - Qt.Key_0
            max_val = cell.get("max_value", 9)  # fourni par le contrôleur
            if not cell["is_fixed"] and value <= max_val:
                self.cell_value_changed.emit(col, row, value)
        elif key in (Qt.Key_Delete, Qt.Key_Backspace):
            if not cell["is_fixed"]:
                self.cell_value_changed.emit(col, row, 0)
        else:
            moves = {
                Qt.Key_Left:  (-1,  0), Qt.Key_Right: (1, 0),
                Qt.Key_Up:    ( 0, -1), Qt.Key_Down:  (0, 1),
            }
            if key in moves:
                dc, dr = moves[key]
                nc, nr = col + dc, row + dr
                if 0 <= nc < self._cols and 0 <= nr < self._rows:
                    self._selected = (nc, nr)
                    self.cell_selected.emit(nc, nr)
                    self.update()