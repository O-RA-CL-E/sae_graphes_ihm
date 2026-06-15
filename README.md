# Néonaure — SAÉ Graphes & IHM

> Implémentation du jeu **Néonaure** (variante du Sudoku) en Python avec architecture MVC.  
> SAÉ R2-07 Graphes · R2-02 IHM — IUT du Littoral Côte d'Opale · 2025-2026

---

## Présentation

Le Néonaure est une variante du Sudoku jouée sur une grille (carrée ou rectangulaire) avec trois contraintes :

- Un chiffre par case
- Chaque chiffre doit être entouré de chiffres **différents**, diagonales comprises
- Chaque **motif** de N cases (délimité en traits gras) doit contenir les chiffres de 1 à N

---

## Fonctionnalités

- Chargement et sauvegarde d'une grille au format JSON
- Jeu interactif (saisie clavier et souris, détection des erreurs en temps réel)
- Résolution automatique par backtracking avec heuristique MRV
- Chronomètre, compteur de cases vides et d'erreurs
- Réinitialisation de la grille

---

## Stack technique

- Python 3.10+
- PyQt5
- Architecture MVC stricte

---

## Installation

```bash
git clone https://github.com/O-RA-CL-E/sae_graphes_ihm.git
cd sae_graphes_ihm
python -m venv venv
# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate
pip install -r requirements.txt
```

---

## Lancement

```bash
python main.py
```

---

## Structure du projet

    sae_graphes_ihm/
    ├── model/
    │   ├── case.py             # Classe Case
    │   ├── motif.py            # Classe Motif
    │   └── grille.py           # Classe Grille
    ├── view/
    │   ├── main_window.py      # Fenêtre principale
    │   └── grid_widget.py      # Composant graphique de la grille
    ├── controller/
    │   ├── game_controller.py  # Moteur de jeu
    │   └── grille_io.py        # Chargement / sauvegarde JSON
    ├── solver/
    │   └── solveur.py          # Algorithme de résolution (backtracking MRV)
    ├── grilles/                # Grilles de jeu fournies (.json + .png)
    ├── tests/                  # Tests unitaires
    ├── docs/                   # Notice d'utilisation
    ├── comptes_rendus/         # Comptes-rendus de séances
    ├── requirements.txt
    └── README.md

---

## Groupe

| Membre | Rôle |
|---|---|
| Ethan | Model + Solveur |
| Maël | View PyQt |
| Yanis | Controller + I/O |

---

## Modules évalués

R2-07 Graphes · R2-02 IHM  
Responsable : L. Conoir · Intervenants : R. Cozot, J. Hermilier
