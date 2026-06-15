"""
grid_widget.py — Composant graphique de la grille Néonaure (version pro).

Améliorations visuelles et ergonomiques (UX/UI) :
  - Survol réactif et adouci des cases (hover)
  - Mise en évidence douce du motif de la case sélectionnée
  - Sélection avec masque arrondi translucide imbriqué (overlay)
  - Palette dynamique interchangeable (Thème Clair / Thème Sombre)
  - Rendu anti-aliased du texte et des formes géométriques
  - Aide prédictive contextuelle (≤N) intégrée avec finesse en haut à droite
  - Désélection propre lors d'un clic dans le vide ou les marges extérieures
  - Système de verrouillage (Locked) de l'édition après résolution automatique
  - Navigation par flèches clavier entièrement synchronisée
"""

from PyQt5.QtWidgets import QWidget, QSizePolicy
from PyQt5.QtCore import Qt, QRect, QRectF, QSize, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QPainterPath


# ── Constantes visuelles de dimensionnement ───────────────────────────
CELL_SIZE     = 60
BORDER_THIN   = 1
BORDER_THICK  = 3
CORNER_RADIUS = 6


class GridWidget(QWidget):
    """Widget personnalisé gérant le rendu graphique et les interactions de la grille."""

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
        self._locked    = False  # État de verrouillage pour geler la grille

        # Initialisation par défaut du thème clair
        self.appliquer_theme("clair")

        self.setFocusPolicy(Qt.StrongFocus)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setMouseTracking(True)

    def appliquer_theme(self, mode: str):
        """Met à jour dynamiquement la palette de couleurs de la grille selon le mode choisi."""
        if mode == "sombre":
            self.C_BG_VIDE    = QColor(30, 30, 40)       # Fond sombre de case vide
            self.C_BG_FIXE    = QColor(50, 50, 65)       # Case fixe d'origine
            self.C_BG_SELECT  = QColor(74, 127, 191, 70) # Sélection plus marquée
            self.C_BG_HOVER   = QColor(45, 55, 75)       # Survol
            self.C_BG_MOTIF   = QColor(35, 45, 65)       # Même motif
            self.C_BG_ERREUR  = QColor(80, 30, 35)       # Erreur rouge sombre
            
            self.C_TXT_FIXE   = QColor(220, 220, 230)    # Texte blanc/gris
            self.C_TXT_JOUEUR = QColor(100, 160, 230)    # Saisie joueur bleu néon
            self.C_TXT_SELECT = QColor(100, 160, 230)
            self.C_TXT_ERREUR = QColor(240, 100, 100)    # Texte d'erreur rouge vif
            
            self.C_BRD_FINE   = QColor(70, 70, 90)       # Grilles internes
            self.C_BRD_EPAIS  = QColor(200, 200, 220)    # Bord épais externe clair
        else:
            # Mode Clair par défaut
            self.C_BG_VIDE    = QColor(252, 251, 248)   # blanc cassé
            self.C_BG_FIXE    = QColor(224, 220, 213)   # beige gris — case fixe
            self.C_BG_SELECT  = QColor(74, 127, 191, 50) # bleu acier translucide
            self.C_BG_HOVER   = QColor(232, 242, 255)   # bleu très pâle
            self.C_BG_MOTIF   = QColor(236, 245, 255)   # bleu subtil
            self.C_BG_ERREUR  = QColor(253, 234, 232)   # rose pastel

            self.C_TXT_FIXE   = QColor(38,  38,  38)    # quasi-noir
            self.C_TXT_JOUEUR = QColor(26,  80,  140)   # bleu profond
            self.C_TXT_SELECT = QColor(26,  80,  140)
            self.C_TXT_ERREUR = QColor(183,  28,  28)   # rouge sombre

            self.C_BRD_FINE   = QColor(200, 194, 186)   # gris doux
            self.C_BRD_EPAIS  = QColor(38,  38,  38)    # noir d'encre

        self.update()

    # ── Interface Publique ────────────────────────────────────────────

    def update_grid(self, grid_data: dict):
        prev = self._selected
        self._grid_data = grid_data
        self._cols      = grid_data.get("cols", 0)
        self._rows      = grid_data.get("rows", 0)
        self._cell_map  = {
            (c["col"], c["row"]): c
            for c in grid_data.get("cells", [])
        }
        self._selected = prev if (prev and prev in self._cell_map) else None
        self._locked = False
        self.updateGeometry()
        self.update()

    def clear(self):
        self._grid_data = None
        self._cell_map  = {}
        self._selected  = None
        self._hovered   = None
        self._cols = self._rows = 0
        self._locked    = False
        self.update()

    def set_locked(self, locked: bool):
        self._locked = locked
        self.update()

    def sizeHint(self) -> QSize:
        if self._cols == 0:
            return QSize(400, 400)
        return QSize(self._cols * CELL_SIZE + 2, self._rows * CELL_SIZE + 2)

    # ── Moteur de Rendu Graphique (Paint Pipeline) ────────────────────

    def paintEvent(self, _event):
        painter = QPainter(self)

        if self._grid_data is None:
            painter.fillRect(self.rect(), self.C_BG_FIXE)
            painter.setPen(self.C_TXT_FIXE)
            painter.setFont(QFont("Segoe UI", 12))
            painter.drawText(self.rect(), Qt.AlignCenter, "Charger une grille\npour commencer")
            return

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

            if cell["is_error"]:
                painter.fillRect(rect, self.C_BG_ERREUR)
            elif pos == self._hovered and not cell["is_fixed"] and not self._locked:
                painter.fillRect(rect, self.C_BG_HOVER)
            elif selected_motif and cell["motif_id"] == selected_motif:
                painter.fillRect(rect, self.C_BG_MOTIF)
            elif cell["is_fixed"]:
                painter.fillRect(rect, self.C_BG_FIXE)
            else:
                painter.fillRect(rect, self.C_BG_VIDE)

            if pos == self._selected:
                path = QPainterPath()
                path.addRoundedRect(QRectF(rect).adjusted(2, 2, -2, -2), CORNER_RADIUS, CORNER_RADIUS)
                painter.fillPath(path, self.C_BG_SELECT)

        painter.setRenderHint(QPainter.Antialiasing, False)

    def _draw_numbers(self, painter: QPainter):
        painter.setRenderHint(QPainter.TextAntialiasing, True)
        font_bold   = QFont("Segoe UI", CELL_SIZE // 3, QFont.Bold)
        font_normal = QFont("Segoe UI", CELL_SIZE // 3, QFont.Normal)
        font_tiny   = QFont("Segoe UI", CELL_SIZE // 6, QFont.Bold)

        for (col, row), cell in self._cell_map.items():
            rect = self._cell_rect(col, row)
            pos  = (col, row)

            if cell["value"] != 0:
                if pos == self._selected:
                    painter.setPen(self.C_TXT_FIXE if cell["is_fixed"] else self.C_TXT_SELECT)
                    painter.setFont(font_bold if cell["is_fixed"] else font_normal)
                elif cell["is_error"]:
                    painter.setPen(self.C_TXT_ERREUR)
                    painter.setFont(font_normal)
                elif cell["is_fixed"]:
                    painter.setPen(self.C_TXT_FIXE)
                    painter.setFont(font_bold)
                else:
                    painter.setPen(self.C_TXT_JOUEUR)
                    painter.setFont(font_normal)

                painter.drawText(rect, Qt.AlignCenter, str(cell["value"]))
            
            elif pos == self._selected and not cell["is_fixed"] and not self._locked:
                max_val = cell.get("max_value", 9)
                painter.setPen(self.C_TXT_JOUEUR)
                painter.setFont(font_tiny)
                
                margin_rect = rect.adjusted(0, 3, -5, 0)
                painter.drawText(margin_rect, Qt.AlignTop | Qt.AlignRight, f"≤{max_val}")

    def _draw_borders(self, painter: QPainter):
        painter.setRenderHint(QPainter.Antialiasing, False)

        painter.setPen(QPen(self.C_BRD_EPAIS, BORDER_THICK))
        painter.drawRect(1, 1, self._cols * CELL_SIZE, self._rows * CELL_SIZE)

        for col in range(self._cols):
            for row in range(self._rows):
                cell = self._cell_map.get((col, row))
                if cell is None:
                    continue
                x = 1 + col * CELL_SIZE
                y = 1 + row * CELL_SIZE

                if col + 1 < self._cols:
                    v = self._cell_map.get((col + 1, row))
                    if v:
                        diff = cell["motif_id"] != v["motif_id"]
                        painter.setPen(QPen(self.C_BRD_EPAIS if diff else self.C_BRD_FINE,
                                            BORDER_THICK if diff else BORDER_THIN))
                        painter.drawLine(x + CELL_SIZE, y, x + CELL_SIZE, y + CELL_SIZE)
                if row + 1 < self._rows:
                    v = self._cell_map.get((col, row + 1))
                    if v:
                        diff = cell["motif_id"] != v["motif_id"]
                        painter.setPen(QPen(self.C_BRD_EPAIS if diff else self.C_BRD_FINE,
                                            BORDER_THICK if diff else BORDER_THIN))
                        painter.drawLine(x, y + CELL_SIZE, x + CELL_SIZE, y + CELL_SIZE)

    def _cell_rect(self, col: int, row: int) -> QRect:
        return QRect(1 + col * CELL_SIZE, 1 + row * CELL_SIZE, CELL_SIZE, CELL_SIZE)

    def _pos_to_cell(self, x: int, y: int) -> tuple[int, int] | None:
        col = (x - 1) // CELL_SIZE
        row = (y - 1) // CELL_SIZE
        if 0 <= col < self._cols and 0 <= row < self._rows:
            return (col, row)
        return None

    # ── Interceptions des Actions Joueur ──────────────────────────────

    def mousePressEvent(self, event):
        if self._grid_data is None:
            return
        pos = self._pos_to_cell(event.x(), event.y())
        if pos:
            self._selected = pos
            self.cell_selected.emit(pos[0], pos[1])
        else:
            self._selected = None
            self.cell_selected.emit(-1, -1)
        self.update()
        self.setFocus()

    def mouseMoveEvent(self, event):
        if self._grid_data is None or self._locked:
            return
        pos = self._pos_to_cell(event.x(), event.y())
        if pos != self._hovered:
            self._hovered = pos
            self.update()

    def leaveEvent(self, _event):
        self._hovered = None
        self.update()

    def keyPressEvent(self, event):
        if self._selected is None or self._grid_data is None or self._locked:
            return
        col, row = self._selected
        cell = self._cell_map.get((col, row))
        if cell is None:
            return

        key = event.key()

        if Qt.Key_1 <= key <= Qt.Key_9:
            value   = key - Qt.Key_0
            max_val = cell.get("max_value", 9)
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
                    self.update() # Force le rafraîchissement visuel lors d'un déplacement au clavier