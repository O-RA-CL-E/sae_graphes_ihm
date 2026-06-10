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

La View appelle uniquement les méthodes publiques de ce contrôleur.
Le Model (Grille, Case, Motif) n'est jamais manipulé directement par la View.
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
                                          (pour la sauvegarde rapide)
        partie_en_cours (bool)          : True dès qu'une grille est chargée
    """

    def __init__(self) -> None:
        self.grille:          Grille | None = None
        self.chemin_courant:  Path   | None = None
        self.partie_en_cours: bool          = False

    # ------------------------------------------------------------------ #
    #  Chargement / Sauvegarde                                            #
    # ------------------------------------------------------------------ #

    def charger(self, chemin: str | Path) -> Grille:
        """
        Charge une grille depuis un fichier JSON et démarre la partie.

        Args:
            chemin : chemin vers le fichier .json

        Returns:
            Grille : la grille chargée (la View peut s'en servir pour
                     construire l'affichage, mais ne la modifie pas)

        Raises:
            FileNotFoundError : fichier absent
            ValueError        : JSON mal formé
        """
        self.grille = charger_grille(chemin)
        self.chemin_courant = Path(chemin)
        self.partie_en_cours = True
        return self.grille

    def sauvegarder(self, chemin: str | Path | None = None) -> None:
        """
        Sauvegarde la grille courante dans un fichier JSON.

        Si chemin est None, réutilise le chemin du dernier chargement.

        Args:
            chemin : chemin de destination (optionnel)

        Raises:
            RuntimeError : aucune grille chargée
            ValueError   : aucun chemin fourni ni mémorisé
        """
        self._verifier_partie()
        destination = Path(chemin) if chemin else self.chemin_courant
        if destination is None:
            raise ValueError(
                "Aucun chemin fourni et aucun fichier précédemment chargé."
            )
        sauvegarder_grille(self.grille, destination)
        self.chemin_courant = destination

    # ------------------------------------------------------------------ #
    #  Coup du joueur                                                      #
    # ------------------------------------------------------------------ #

    def jouer_coup(self, x: int, y: int, valeur: int) -> dict:
        """
        Tente de placer une valeur sur la case (x, y).

        Effectue toutes les vérifications métier avant d'appliquer le coup.

        Args:
            x      : colonne (0-indexé)
            y      : ligne (0-indexé)
            valeur : chiffre à placer (0 pour effacer)

        Returns:
            dict avec les clés :
                "ok"      (bool)  : coup accepté ou non
                "message" (str)   : explication lisible
                "gagnee"  (bool)  : True si la partie est remportée après ce coup
                "valide"  (bool)  : True si la case est localement valide après le coup
                                    (uniquement si ok=True et valeur != 0)

        Raises:
            RuntimeError : aucune partie en cours
        """
        self._verifier_partie()

        # --- case existe ?
        case = self.grille.get_case(x, y)
        if case is None:
            return self._reponse(False, f"Case ({x}, {y}) inexistante.")

        # --- case fixe ?
        if case.fixe:
            return self._reponse(False, f"La case ({x}, {y}) est fixe.")

        # --- valeur dans les bornes du motif ?
        if valeur != 0:
            motif = self.grille.get_motif_case(x, y)
            if motif and not (1 <= valeur <= motif.taille()):
                return self._reponse(
                    False,
                    f"Valeur {valeur} hors de la plage autorisée "
                    f"pour ce motif (1–{motif.taille()})."
                )

        # --- application du coup
        case.set_valeur(valeur)

        # --- vérifications post-coup
        valide = self.grille.est_valide_case(x, y) if valeur != 0 else True
        gagnee = self.grille.est_gagnee()

        if gagnee:
            return self._reponse(True, "Félicitations, la grille est résolue !", gagnee=True, valide=True)

        if not valide:
            return self._reponse(True, "Coup placé, mais crée un conflit de voisinage.", valide=False)

        return self._reponse(True, "Coup valide.", valide=True)

    def effacer_case(self, x: int, y: int) -> dict:
        """
        Efface la valeur de la case (x, y) si elle n'est pas fixe.
        Raccourci vers jouer_coup(x, y, 0).
        """
        return self.jouer_coup(x, y, 0)

    # ------------------------------------------------------------------ #
    #  Résolution automatique                                              #
    # ------------------------------------------------------------------ #

    def resoudre(self) -> bool:
        """
        Lance le solveur sur la grille courante et applique la solution.

        Returns:
            True  si une solution a été trouvée et appliquée
            False si la grille n'a pas de solution

        Raises:
            RuntimeError : aucune partie en cours
        """
        self._verifier_partie()

        # Import tardif pour éviter la dépendance circulaire
        # et permettre au solveur d'être développé indépendamment
        from solver.solveur import Solveur

        solveur = Solveur(self.grille)
        return solveur.resoudre()

    # ------------------------------------------------------------------ #
    #  Réinitialisation                                                    #
    # ------------------------------------------------------------------ #

    def reinitialiser(self) -> None:
        """
        Remet la grille à son état initial (efface les cases non fixes).

        Raises:
            RuntimeError : aucune partie en cours
        """
        self._verifier_partie()
        self.grille.reinitialiser()

    # ------------------------------------------------------------------ #
    #  Consultation de l'état (pour la View)                              #
    # ------------------------------------------------------------------ #

    def get_valeur(self, x: int, y: int) -> int | None:
        """
        Retourne la valeur de la case (x, y), ou None si inexistante.
        Utilisé par la View pour afficher la grille sans accéder au Model.
        """
        self._verifier_partie()
        case = self.grille.get_case(x, y)
        return case.valeur if case else None

    def est_fixe(self, x: int, y: int) -> bool:
        """
        Retourne True si la case (x, y) est fixe (non modifiable par le joueur).
        """
        self._verifier_partie()
        case = self.grille.get_case(x, y)
        return case.fixe if case else False

    def get_etat_grille(self) -> dict:
        """
        Retourne un snapshot sérialisable de la grille pour la View.

        Returns:
            dict avec :
                "largeur"  (int)
                "hauteur"  (int)
                "cases"    (dict) : {(x, y): {"valeur": int, "fixe": bool}}
                "motifs"   (dict) : {nom: [(x, y), ...]}
                "gagnee"   (bool)
                "valide"   (bool)
        """
        self._verifier_partie()
        return {
            "largeur": self.grille.largeur,
            "hauteur": self.grille.hauteur,
            "cases": {
                (c.x, c.y): {"valeur": c.valeur, "fixe": c.fixe}
                for c in self.grille.cases.values()
            },
            "motifs": {
                nom: [(c.x, c.y) for c in motif.cases]
                for nom, motif in self.grille.motifs.items()
            },
            "gagnee": self.grille.est_gagnee(),
            "valide": self.grille.est_valide(),
        }

    def get_conflits(self) -> set:
        """
        Retourne l'ensemble des coordonnées (x, y) des cases en conflit
        (voisinage ou motif invalide).

        Utilisé par la View pour colorier les cases incorrectes.
        """
        self._verifier_partie()
        conflits = set()
        for case in self.grille.cases.values():
            if case.est_vide():
                continue
            if not self.grille.est_valide_case(case.x, case.y):
                conflits.add((case.x, case.y))
                # Ajoute aussi les voisins impliqués dans le conflit
                for voisin in self.grille.get_voisins(case.x, case.y):
                    if voisin.valeur == case.valeur:
                        conflits.add((voisin.x, voisin.y))
        return conflits

    def get_infos_motif(self, x: int, y: int) -> dict | None:
        """
        Retourne des informations sur le motif contenant la case (x, y).

        Returns:
            dict avec :
                "nom"      (str)
                "taille"   (int)
                "complet"  (bool)
                "valide"   (bool)
            ou None si aucun motif ne contient cette case.
        """
        self._verifier_partie()
        motif = self.grille.get_motif_case(x, y)
        if motif is None:
            return None
        return {
            "nom":     motif.nom,
            "taille":  motif.taille(),
            "complet": motif.est_complet(),
            "valide":  motif.est_valide(),
        }

    # ------------------------------------------------------------------ #
    #  Utilitaires privés                                                  #
    # ------------------------------------------------------------------ #

    def _verifier_partie(self) -> None:
        """Lève RuntimeError si aucune partie n'est en cours."""
        if not self.partie_en_cours or self.grille is None:
            raise RuntimeError("Aucune partie en cours. Chargez d'abord une grille.")

    @staticmethod
    def _reponse(
        ok: bool,
        message: str,
        gagnee: bool = False,
        valide: bool = True,
    ) -> dict:
        """Construit le dictionnaire de retour standard de jouer_coup."""
        return {"ok": ok, "message": message, "gagnee": gagnee, "valide": valide}
