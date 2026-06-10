import json
from model.case import Case
from model.motif import Motif
from model.grille import Grille
from solver.solveur import resoudre


def charger_grille(chemin: str) -> Grille:
    """Charge une grille depuis un fichier JSON et retourne un objet Grille."""
    with open(chemin, "r") as f:
        data = json.load(f)

    toutes_cases = [case for motif in data.values() for case in motif]
    largeur = max(x for x, y, v in toutes_cases) + 1
    hauteur = max(y for x, y, v in toutes_cases) + 1
    grille = Grille(largeur, hauteur)

    for nom_motif, liste_cases in data.items():
        cases = []
        for x, y, valeur in liste_cases:
            case = Case(x, y, valeur)
            grille.cases[(x, y)] = case
            cases.append(case)
        grille.motifs[nom_motif] = Motif(nom_motif, cases)

    return grille


if __name__ == "__main__":
    for i in range(1, 10):
        print(f"\n--- Grille {i} ---")
        grille = charger_grille(f"grilles/grille{i}.json")
        print(f"Dimensions : {grille.largeur}x{grille.hauteur}")

        resolu = resoudre(grille)
        print(f"Résolu : {resolu}")
        print(f"Grille gagnée : {grille.est_gagnee()}")