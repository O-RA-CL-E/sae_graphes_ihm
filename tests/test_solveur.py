import json
from model.case import Case
from model.motif import Motif
from model.grille import Grille
from solver.solveur import resoudre
from controller.grille_io import charger_grille 


if __name__ == "__main__":
    for i in range(1, 10):
        print(f"\n--- Grille {i} ---")
        grille = charger_grille(f"grilles/grille{i}.json")
        print(f"Dimensions : {grille.largeur}x{grille.hauteur}")

        resolu = resoudre(grille)
        print(f"Résolu : {resolu}")
        print(f"Grille gagnée : {grille.est_gagnee()}")