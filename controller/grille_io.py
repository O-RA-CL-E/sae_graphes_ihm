"""
controller/grille_io.py
-----------------------
Chargement et sauvegarde d'une grille Néonaure au format JSON.

Format JSON attendu / produit :
{
    "motif1": [[x, y, valeur], ...],
    "motif2": [[x, y, valeur], ...],
    ...
}

Chaque triplet [x, y, valeur] décrit une case.
valeur == 0  →  case vide
valeur != 0  →  case fixe (préremplie)
"""

import json
from pathlib import Path

from model.case import Case
from model.motif import Motif
from model.grille import Grille


# ------------------------------------------------------------------ #
#  Chargement                                                          #
# ------------------------------------------------------------------ #

def charger_grille(chemin: str | Path) -> Grille:
    """
    Lit un fichier JSON et reconstruit un objet Grille complet.

    Args:
        chemin : chemin vers le fichier .json

    Returns:
        Grille : grille initialisée avec ses cases et motifs

    Raises:
        FileNotFoundError : si le fichier n'existe pas
        ValueError        : si le JSON est mal formé
    """
    chemin = Path(chemin)
    if not chemin.exists():
        raise FileNotFoundError(f"Fichier introuvable : {chemin}")

    with chemin.open("r", encoding="utf-8") as f:
        try:
            donnees = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON invalide dans {chemin} : {e}") from e

    grille = Grille()

    for nom_motif, liste_cases in donnees.items():
        cases_motif = []

        for triplet in liste_cases:
            if len(triplet) != 3:
                raise ValueError(
                    f"Triplet mal formé dans {nom_motif} : {triplet} "
                    f"(attendu [x, y, valeur])"
                )
            x, y, valeur = triplet

            # Réutilise la case si elle existe déjà (cases partagées entre motifs)
            if (x, y) not in grille.cases:
                grille.cases[(x, y)] = Case(x, y, valeur)

            cases_motif.append(grille.cases[(x, y)])

        grille.motifs[nom_motif] = Motif(nom_motif, cases_motif)

        for case in cases_motif:
            grille._case_to_motif[(case.x, case.y)] = grille.motifs[nom_motif]

    # Déduit les dimensions réelles depuis les coordonnées chargées
    if grille.cases:
        grille.largeur  = max(x for x, y in grille.cases) + 1
        grille.hauteur  = max(y for x, y in grille.cases) + 1

    return grille


# ------------------------------------------------------------------ #
#  Sauvegarde                                                          #
# ------------------------------------------------------------------ #

def sauvegarder_grille(grille: Grille, chemin: str | Path) -> None:
    """
    Sérialise l'état courant de la grille dans un fichier JSON.

    Seules les valeurs actuelles des cases sont sauvegardées ;
    le caractère 'fixe' est implicitement conservé (valeur != 0).
    Les cases non fixes remises à 0 apparaissent avec valeur 0.

    Args:
        grille : grille à sauvegarder
        chemin : chemin de destination (créé si inexistant)
    """
    chemin = Path(chemin)
    chemin.parent.mkdir(parents=True, exist_ok=True)

    donnees = {}
    for nom_motif, motif in grille.motifs.items():
        donnees[nom_motif] = [
            [case.x, case.y, case.valeur]
            for case in motif.cases
        ]

    with chemin.open("w", encoding="utf-8") as f:
        json.dump(donnees, f, indent=4, ensure_ascii=False)
