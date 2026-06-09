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

    # ----------------------------------------