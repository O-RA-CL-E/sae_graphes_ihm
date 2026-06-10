from model.grille import Grille


def valeurs_possibles(grille: Grille, x: int, y: int) -> list:
    """
    Retourne la liste des valeurs jouables pour la case (x, y).

    Une valeur est possible si :
    - elle est dans la plage 1..N du motif de la case
    - elle n'est pas déjà présente dans ce motif
    - elle ne correspond à aucun des 8 voisins de la case
    """
    motif = grille.get_motif_case(x, y)
    if not motif:
        return []

    valeurs_motif = set(motif.valeurs_remplies())
    valeurs_voisins = {v.valeur for v in grille.get_voisins(x, y) if not v.est_vide()}
    interdites = valeurs_motif | valeurs_voisins

    return [v for v in range(1, motif.taille() + 1) if v not in interdites]


def case_mrv(grille: Grille):
    """
    Retourne la case vide ayant le moins de valeurs possibles (MRV).
    Retourne None si aucune case vide n'existe.
    """
    case_choisie = None
    min_valeurs = float("inf")

    for case in grille.cases.values():
        if case.est_vide():
            nb = len(valeurs_possibles(grille, case.x, case.y))
            if nb < min_valeurs:
                min_valeurs = nb
                case_choisie = case

    return case_choisie


def resoudre(grille: Grille) -> bool:
    """
    Résout la grille par backtracking avec heuristique MRV.

    Retourne True si une solution a été trouvée, False sinon.
    La grille est modifiée en place.
    """
    if grille.est_complete():
        return grille.est_gagnee()

    case = case_mrv(grille)

    if not case:
        return False

    for valeur in valeurs_possibles(grille, case.x, case.y):
        case.valeur = valeur

        if resoudre(grille):
            return True

        case.valeur = 0

    return False