"""
controller/game_controller.py
------------------------------
Moteur de jeu Néonaure.

Responsabilités (couche Controller du MVC) :
  - Charger / sauvegarder une grille via grille_io
  - Valider et appliquer les coups du joueur
  - Exposer l'état de la partie à la View (sans que la View touche au Model)
  - Déclencher la résolution automatique via le solveur
  - Réinitialiser la partie
"""

from pathlib import Path

from model.grille import Grille
from controller.grille_io import charger_grille, sauvegarder_grille


class GameController:
    """
    Moteur de jeu Néonaure.

    Attributs :
        grille          (Grille | None) : grille en cours de partie
        chemin_courant  (Path   | None) : chemin du fichier chargé
        partie_en_cours (bool)          : True dès qu'une grille est chargée
    """

    def __init__(self) -> None:
        self.grille:          Grille | None = None
        self.chemin_courant:  Path   | None = None
        self.partie_en_cours: bool          = False

    # ------------------------------------------------------------------ #
    #  Interface avec la Vue (Méthodes attendues par main_window.py)      #
    # ------------------------------------------------------------------ #

    def charger_grille(self, chemin: str | Path) -> dict:
        """Charge une grille et retourne les données formatées pour la View."""
        self.charger(chemin)
        return self._generer_grid_data()

    def sauvegarder_grille(self, chemin: str | Path | None = None) -> None:
        """Sauvegarde la grille courante."""
        self.sauvegarder(chemin)

    def jouer_case(self, col: int, row: int, value: int) -> dict:
        """Joue un coup et retourne le grid_data mis à jour (ou lève une exception)."""
        res = self.jouer_coup(col, row, value)
        if not res["ok"]:
            raise ValueError(res["message"])
        return self._generer_grid_data()

    def resoudre(self) -> dict:
        """Lance le solveur de Novaak et retourne le grid_data résolu."""
        self._verifier_partie()

        # Import de la fonction (et non d'une classe manquante) pour éviter le bug d'intégration
        from solver.solveur import resoudre as solveur_resoudre

        succes = solveur_resoudre(self.grille)
        if not succes:
            raise RuntimeError("Cette grille n'a pas de solution.")
            
        return self._generer_grid_data()

    def reinitialiser(self) -> dict:
        """Remet la grille à zéro (sans les cases fixes) et retourne le grid_data."""
        self._verifier_partie()
        self.grille.reinitialiser()
        return self._generer_grid_data()

    # ------------------------------------------------------------------ #
    #  Logique métier interne (Chargement / Sauvegarde / Coups)          #
    # ------------------------------------------------------------------ #

    def charger(self, chemin: str | Path) -> Grille:
        self.grille = charger_grille(chemin)
        self.chemin_courant = Path(chemin)
        self.partie_en_cours = True
        return self.grille

    def sauvegarder(self, chemin: str | Path | None = None) -> None:
        self._verifier_partie()
        destination = Path(chemin) if chemin else self.chemin_courant
        if destination is None:
            raise ValueError("Aucun chemin fourni et aucun fichier précédemment chargé.")
        sauvegarder_grille(self.grille, destination)
        self.chemin_courant = destination

    def jouer_coup(self, x: int, y: int, valeur: int) -> dict:
        self._verifier_partie()

        case = self.grille.get_case(x, y)
        if case is None:
            return self._reponse(False, f"Case ({x}, {y}) inexistante.")

        if case.fixe:
            return self._reponse(False, f"La case ({x}, {y}) est fixe.")

        if valeur != 0:
            motif = self.grille.get_motif_case(x, y)
            if motif and not (1 <= valeur <= motif.taille()):
                return self._reponse(
                    False,
                    f"Valeur {valeur} hors de la plage autorisée (1–{motif.taille()})."
                )

        case.set_valeur(valeur)

        valide = self.grille.est_valide_case(x, y) if valeur != 0 else True
        gagnee = self.grille.est_gagnee()

        if gagnee:
            return self._reponse(True, "Félicitations, la grille est résolue !", gagnee=True, valide=True)
        if not valide:
            return self._reponse(True, "Coup placé, mais crée un conflit.", valide=False)

        return self._reponse(True, "Coup valide.", valide=True)

    # ------------------------------------------------------------------ #
    #  Consultation et Utilitaires de conversion                         #
    # ------------------------------------------------------------------ #

    def get_conflits(self) -> set:
        self._verifier_partie()
        conflits = set()

        for case in self.grille.cases.values():
            if case.est_vide():
                continue
            if not self.grille.est_valide_case(case.x, case.y):
                conflits.add((case.x, case.y))
                for voisin in self.grille.get_voisins(case.x, case.y):
                    if voisin.valeur == case.valeur:
                        conflits.add((voisin.x, voisin.y))
        for motif in self.grille.motifs.values():
            valeurs_vues = {}
            for case in motif.cases:
                if case.est_vide():
                    continue
                if case.valeur in valeurs_vues:
                    conflits.add((case.x, case.y))
                    conflits.add(valeurs_vues[case.valeur])
                else:
                    valeurs_vues[case.valeur] = (case.x, case.y)
        return conflits

    def _generer_grid_data(self) -> dict:
        """Génère la structure de dictionnaire attendue par GridWidget."""
        if self.grille is None:
            return {"cols": 0, "rows": 0, "cells": []}

        conflits = self.get_conflits()
        cells = []
        for case in self.grille.cases.values():
            motif = self.grille.get_motif_case(case.x, case.y)
            motif_id = motif.nom if motif else ""
            max_val = motif.taille() if motif else 9

            cells.append({
                "col": case.x,
                "row": case.y,
                "value": case.valeur,
                "motif_id": motif_id,
                "is_fixed": case.fixe,
                "is_error": (case.x, case.y) in conflits,
                "max_value": max_val  # Donnée cruciale requise par le GridWidget
            })

        return {
            "cols": self.grille.largeur,
            "rows": self.grille.hauteur,
            "cells": cells
        }

    def _verifier_partie(self) -> None:
        if not self.partie_en_cours or self.grille is None:
            raise RuntimeError("Aucune partie en cours. Chargez d'abord une grille.")

    @staticmethod
    def _reponse(ok: bool, message: str, gagnee: bool = False, valide: bool = True) -> dict:
        return {"ok": ok, "message": message, "gagnee": gagnee, "valide": valide}