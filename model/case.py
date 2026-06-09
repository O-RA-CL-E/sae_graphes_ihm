class Case:
    """
    Représente une case de la grille Néonaure.
    
    Attributs :
        x (int)      : colonne de la case (0 à 7)
        y (int)      : ligne de la case (0 à 7)
        valeur (int) : chiffre de la case (0 = vide)
        fixe (bool)  : True si la case est préremplie (non modifiable)
    """

    def __init__(self, x: int, y: int, valeur: int = 0) -> None:
        self.x = x
        self.y = y
        self.valeur = valeur
        self.fixe = valeur != 0

    def est_vide(self) -> bool:
        """Retourne True si la case n'a pas encore été remplie."""
        return self.valeur == 0

    def set_valeur(self, valeur: int) -> None:
        """
        Modifie la valeur de la case si elle n'est pas fixe.
        
        Args:
            valeur (int) : nouvelle valeur (0 pour effacer)
        
        Raises:
            ValueError : si la case est fixe
        """
        if self.fixe:
            raise ValueError(f"La case ({self.x}, {self.y}) est fixe et ne peut pas être modifiée.")
        self.valeur = valeur

    def __repr__(self) -> str:
        return f"Case({self.x}, {self.y}, valeur={self.valeur}, fixe={self.fixe})"