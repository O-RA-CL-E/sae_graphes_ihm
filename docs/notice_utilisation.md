# Notice d'utilisation — Néonaure

## Lancement

```bash
python main.py
```

---

## Interface

L'application est composée de deux zones :

- **Zone de jeu** (centre) : affiche la grille Néonaure
- **Panneau latéral** (droite) : timer, compteurs et boutons d'action

---

## Charger une grille

1. Cliquer sur **Charger…** dans le panneau latéral, ou **Fichier → Charger une grille…** (`Ctrl+O`)
2. Sélectionner un fichier `.json` dans le dossier `grilles/`
3. La grille s'affiche et le chronomètre démarre automatiquement

---

## Jouer

- **Sélectionner une case** : clic souris ou touches fléchées
- **Saisir un chiffre** : touches `1` à `9` (limité à la taille N du motif)
- **Effacer une case** : `Suppr` ou `Retour arrière`
- Les cases préremplies (fixes) ne peuvent pas être modifiées
- Une case en **rouge** indique une erreur (conflit de voisinage ou doublon dans un motif)
- Le panneau latéral affiche en temps réel le nombre de cases vides et d'erreurs

---

## Résoudre automatiquement

1. Cliquer sur **Résoudre** (`Ctrl+R`) ou **Jeu → Résoudre**
2. Confirmer dans la boîte de dialogue
3. La solution s'affiche instantanément

> Note : certaines grilles peuvent ne pas avoir de solution valide.

---

## Réinitialiser

Cliquer sur **Réinitialiser** (`Ctrl+N`) ou **Jeu → Réinitialiser** pour effacer toutes les saisies et revenir à l'état initial de la grille. Le chronomètre repart à zéro.

---

## Sauvegarder

Cliquer sur **Sauvegarder…** (`Ctrl+S`) ou **Fichier → Sauvegarder…** pour enregistrer l'état courant de la grille au format JSON.

---

## Affichage

Le menu **Affichage** permet de basculer entre :
- **Mode Clair** : interface fond beige
- **Mode Sombre** : interface fond sombre (par défaut)

---

## Raccourcis clavier

| Action | Raccourci |
|---|---|
| Charger une grille | `Ctrl+O` |
| Sauvegarder | `Ctrl+S` |
| Résoudre | `Ctrl+R` |
| Réinitialiser | `Ctrl+N` |
| Règles du jeu | `F1` |
| Quitter | `Ctrl+Q` |
| Navigation dans la grille | Touches fléchées |
| Saisir un chiffre | `1` à `9` |
| Effacer une case | `Suppr` / `Retour arrière` |