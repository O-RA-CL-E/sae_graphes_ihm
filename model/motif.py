class Motif:
    """
    Représente un motif de la grille Néonaure.
    
    Un motif de N cases doit contenir exactement les chiffres de 1 à N.
    
    Attributs :
        nom (str)        : identifiant du motif ("motif1", "motif2", ...)
        cases (list)     : liste des Case appartenant à ce motif
    """

    def __init__(self, nom: str, cases: list) -> None:
        self.nom = nom
        self.cases = cases

    def taille(self) -> int:
        """Retourne le nombre de cases du motif (= valeur maximale attendue)."""
        return len(self.cases)

    def valeurs_remplies(self) -> list:
        """Retourne la liste des valeurs non nulles du motif."""
        return [c.valeur for c in self.cases if c.valeur != 0]

    def est_valide(self) -> bool:
        """
        Vérifie qu'il n'y a pas de doublon parmi les cases remplies.
        Ne vérifie pas la complétude — utilisable en cours de partie.
        """
        valeurs = self.valeurs_remplies()
        return len(valeurs) == len(set(valeurs))

    def est_complet(self) -> bool:
        """
        Vérifie que le motif est entièrement et correctement rempli.
        Les valeurs doivent former exactement l'ensemble {1, ..., N}.
        """
        valeurs = sorted([c.valeur for c in self.cases])
        return valeurs == list(range(1, self.taille() + 1))

    def __repr__(self) -> str:
        return f"Motif({self.nom}, taille={self.taille()}, cases={self.cases})"