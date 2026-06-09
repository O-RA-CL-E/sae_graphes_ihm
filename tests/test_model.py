import json
from model.case import Case
from model.motif import Motif
from model.grille import Grille


def charger_grille(chemin: str) -> Grille:
    """Charge une grille depuis un fichier JSON et retourne un objet Grille."""
    with open(chemin, "r") as f:
        data = json.load(f)

    grille = Grille()

    for nom_motif, liste_cases in data.items():
        cases = []
        for x, y, valeur in liste_cases:
            case = Case(x, y, valeur)
            grille.cases[(x, y)] = case
            cases.append(case)
        grille.motifs[nom_motif] = Motif(nom_motif, cases)

    return grille


if __name__ == "__main__":
    grille = charger_grille("grilles/grille1.json")

    print(grille)
    print(f"Nombre de cases : {len(grille.cases)}")
    print(f"Nombre de motifs : {len(grille.motifs)}")
    print(f"Grille complète : {grille.est_complete()}")
    print(f"Grille valide : {grille.est_valide()}")

    # Test get_voisins
    case = grille.get_case(1, 1)
    print(f"\nVoisins de (1,1) : {grille.get_voisins(1, 1)}")

    # Test get_motif_case
    motif = grille.get_motif_case(1, 1)
    print(f"Motif de (1,1) : {motif}")

    # Test reinitialiser
    grille.reinitialiser()
    print(f"\nAprès réinitialisation, grille complète : {grille.est_complete()}")