from model.case import Case
from model.motif import Motif


class Grille:
    """
    Représente la grille de jeu Néonaure.

    Attributs :
        largeur (int)  : nombre de colonnes (défaut 8)
        hauteur (int)  : nombre de lignes (défaut 8)
        cases (dict)   : dictionnaire (x, y) -> Case
        motifs (dict)  : dictionnaire nom -> Motif
    """

    def __init__(self, largeur: int = 8, hauteur: int = 8) -> None:
        self.largeur = largeur
        self.hauteur = hauteur
        self.cases: dict = {}
        self.motifs: dict = {}

    # ------------------------------------------------------------------ #
    #  Accès                                                               #
    # ------------------------------------------------------------------ #

    def get_case(self, x: int, y: int) -> Case | None:
        """Retourne la case aux coordonnées (x, y), ou None si inexistante."""
        return self.cases.get((x, y))

    def get_voisins(self, x: int, y: int) -> list:
        """
        Retourne les cases voisines de (x, y) dans les 8 directions.
        Les cases hors grille sont ignorées.
        """
        voisins = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                voisin = self.cases.get((x + dx, y + dy))
                if voisin:
                    voisins.append(voisin)
        return voisins

    def get_motif_case(self, x: int, y: int) -> Motif | None:
        """Retourne le motif auquel appartient la case (x, y), ou None."""
        for motif in self.motifs.values():
            if any(c.x == x and c.y == y for c in motif.cases):
                return motif
        return None

    # ------------------------------------------------------------------ #
    #  Validation                                                          #
    # ------------------------------------------------------------------ #

    def est_valide_case(self, x: int, y: int) -> bool:
        """
        Vérifie la contrainte de voisinage pour une case donnée.
        Une case ne doit pas avoir la même valeur qu'un de ses 8 voisins.
        """
        case = self.get_case(x, y)
        if not case or case.est_vide():
            return True
        return all(v.valeur != case.valeur for v in self.get_voisins(x, y))

    def est_valide(self) -> bool:
        """Vérifie la contrainte de voisinage sur toutes les cases remplies."""
        return all(
            self.est_valide_case(c.x, c.y)
            for c in self.cases.values()
            if not c.est_vide()
        )

    def est_complete(self) -> bool:
        """Retourne True si toutes les cases sont remplies."""
        return all(not c.est_vide() for c in self.cases.values())

    def est_gagnee(self) -> bool:
        """
        Vérifie les trois conditions de victoire :
        - toutes les cases sont remplies
        - contrainte de voisinage respectée partout
        - tous les motifs sont complets (contiennent 1..N)
        """
        return (
            self.est_complete()
            and self.est_valide()
            and all(m.est_complet() for m in self.motifs.values())
        )

    # ------------------------------------------------------------------ #
    #  Réinitialisation                                                    #
    # ------------------------------------------------------------------ #

    def reinitialiser(self) -> None:
        """Efface les valeurs non fixes (remet le joueur à l'état initial)."""
        for case in self.cases.values():
            if not case.fixe:
                case.valeur = 0

    def __repr__(self) -> str:
        return f"Grille({self.largeur}x{self.hauteur}, {len(self.motifs)} motifs)"