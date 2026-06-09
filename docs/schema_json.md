# Schéma JSON des grilles

## Structure générale

Un fichier JSON de grille est un objet dont chaque clé est un nom de motif
("motif1", "motif2", ...) associé à une liste de cases.

## Format d'une case

Chaque case est un tableau de 3 entiers : [x, y, valeur]

- x : colonne (0 à 7)
- y : ligne (0 à 7)
- valeur : chiffre prérempli (1..N), ou 0 si la case est vide

## Règles

- La grille est 8×8 (x et y de 0 à 7)
- Chaque case appartient à exactement un motif
- Un motif de N cases doit contenir les chiffres 1 à N
- Les motifs ont des tailles variables (minimum 1 case)
- Une case avec valeur != 0 est fixe : le joueur ne peut pas la modifier

## Exemple

```json
{
  "motif1": [[0,0,0], [1,0,0], [0,1,0], [1,1,3], [2,1,0]],
  "motif11": [[7,1,0], [7,2,0]],
  "motif14": [[6,3,0]]
}
```