"""
controller_stub.py — Stub du contrôleur pour développement/test de la View.

Ce fichier permet à Maël de tester la View de manière isolée,
sans dépendre du vrai GameController de Yanis.

À REMPLACER par game_controller.py (Yanis) une fois disponible.
L'interface publique est identique : même noms de méthodes, mêmes signatures.
"""

import json
import copy


class ControllerStub:
    """
    Implémente la même interface que GameController.
    Gère une copie locale de l'état pour permettre les interactions.
    """

    def __init__(self):
        self._etat_initial = None   # état original (cases fixes seulement)
        self._etat_courant = None   # état avec saisies joueur

    # ──────────────────────────────────────────────────────────────────
    # Interface publique (identique à GameController)
    # ──────────────────────────────────────────────────────────────────

    def charger_grille(self, filepath: str) -> dict:
        """Charge un fichier JSON et retourne grid_data pour la View."""
        with open(filepath, "r", encoding="utf-8") as f:
            raw = json.load(f)

        cells = []
        for motif_id, cases in raw.items():
            for col, row, valeur in cases:
                cells.append({
                    "col"      : col,
                    "row"      : row,
                    "value"    : valeur,
                    "motif_id" : motif_id,
                    "is_fixed" : valeur != 0,
                    "is_error" : False
                })

        cols = max(c["col"] for c in cells) + 1
        rows = max(c["row"] for c in cells) + 1

        grid_data = {"cols": cols, "rows": rows, "cells": cells}
        self._etat_initial = copy.deepcopy(grid_data)
        self._etat_courant = copy.deepcopy(grid_data)
        return copy.deepcopy(self._etat_courant)

    def sauvegarder_grille(self, filepath: str) -> None:
        """Sauvegarde l'état courant en JSON (format d'origine)."""
        if self._etat_courant is None:
            raise RuntimeError("Aucune grille chargée.")

        # Reconstruction du format d'origine {motifId: [[col, row, val], ...]}
        motifs = {}
        for c in self._etat_courant["cells"]:
            mid = c["motif_id"]
            motifs.setdefault(mid, []).append([c["col"], c["row"], c["value"]])

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(motifs, f, indent=2, ensure_ascii=False)

    def jouer_case(self, col: int, row: int, value: int) -> dict:
        """
        Met à jour la valeur d'une case et recalcule les erreurs.
        Retourne le nouvel état complet pour la View.
        """
        if self._etat_courant is None:
            raise RuntimeError("Aucune grille chargée.")

        cell_map = {(c["col"], c["row"]): c
                    for c in self._etat_courant["cells"]}

        if (col, row) not in cell_map:
            raise ValueError(f"Case ({col},{row}) inexistante.")

        cell = cell_map[(col, row)]
        if cell["is_fixed"]:
            raise ValueError("Cette case est fixe et ne peut pas être modifiée.")

        cell["value"] = value

        # Recalcul des erreurs sur tout l'état courant
        self._recalculer_erreurs(cell_map)

        return copy.deepcopy(self._etat_courant)

    def resoudre(self) -> dict:
        """
        Retourne la grille avec la solution (backtracking simple).
        Lève une exception si aucune solution n'est trouvée.
        """
        if self._etat_courant is None:
            raise RuntimeError("Aucune grille chargée.")

        # Construire une copie de travail
        etat_solution = copy.deepcopy(self._etat_initial)
        cell_map = {(c["col"], c["row"]): c
                    for c in etat_solution["cells"]}

        if not self._backtrack(cell_map, etat_solution["cols"], etat_solution["rows"]):
            raise RuntimeError("Aucune solution trouvée pour cette grille.")

        return etat_solution

    def reinitialiser(self) -> dict:
        """Remet la grille à l'état initial (cases fixes seulement)."""
        if self._etat_initial is None:
            raise RuntimeError("Aucune grille chargée.")
        self._etat_courant = copy.deepcopy(self._etat_initial)
        return copy.deepcopy(self._etat_courant)

    # ──────────────────────────────────────────────────────────────────
    # Logique métier (sera dans Model + Controller de Éthan et Yanis)
    # ──────────────────────────────────────────────────────────────────

    def _recalculer_erreurs(self, cell_map: dict):
        """Marque is_error=True sur toutes les cases violant une contrainte."""
        for (col, row), cell in cell_map.items():
            if cell["value"] == 0:
                cell["is_error"] = False
                continue
            cell["is_error"] = (
                self._viole_voisinage(col, row, cell["value"], cell_map)
                or self._viole_motif(cell["motif_id"], cell_map)
            )

    @staticmethod
    def _viole_voisinage(col: int, row: int, val: int, cell_map: dict) -> bool:
        """True si un voisin (8 directions) a la même valeur."""
        for dc in (-1, 0, 1):
            for dr in (-1, 0, 1):
                if dc == 0 and dr == 0:
                    continue
                voisin = cell_map.get((col + dc, row + dr))
                if voisin and voisin["value"] == val:
                    return True
        return False

    @staticmethod
    def _viole_motif(motif_id: str, cell_map: dict) -> bool:
        """True si le motif contient un doublon (valeurs non nulles)."""
        valeurs = [
            c["value"]
            for c in cell_map.values()
            if c["motif_id"] == motif_id and c["value"] != 0
        ]
        return len(valeurs) != len(set(valeurs))

    def _backtrack(self, cell_map: dict, cols: int, rows: int) -> bool:
        """Résolution par backtracking. Retourne True si solution trouvée."""
        # Chercher la première case vide
        vide = None
        for row in range(rows):
            for col in range(cols):
                c = cell_map.get((col, row))
                if c and c["value"] == 0:
                    vide = (col, row)
                    break
            if vide:
                break

        if vide is None:
            return True  # toutes les cases remplies → solution trouvée

        col, row = vide
        cell = cell_map[(col, row)]
        motif_id = cell["motif_id"]
        taille_motif = sum(
            1 for c in cell_map.values() if c["motif_id"] == motif_id
        )

        for val in range(1, taille_motif + 1):
            if (not self._viole_voisinage(col, row, val, cell_map)
                    and not self._motif_a_valeur(motif_id, val, cell_map)):
                cell["value"] = val
                if self._backtrack(cell_map, cols, rows):
                    return True
                cell["value"] = 0

        return False

    @staticmethod
    def _motif_a_valeur(motif_id: str, val: int, cell_map: dict) -> bool:
        """True si val est déjà présente dans le motif."""
        return any(
            c["value"] == val
            for c in cell_map.values()
            if c["motif_id"] == motif_id
        )
