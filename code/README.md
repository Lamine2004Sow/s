# SAE Optimisation 2025-2026 — Anneau-étoile (Ring-Star)

Ce projet charge une instance TSPLIB95 et :
- construit la matrice de distances euclidiennes
- calcule une solution heuristique (p-médian glouton + TSP plus proche voisin)
- améliore la solution par descente stochastique (swap station / non-station)
- peut résoudre la formulation compacte PuLP (CPLEX)
- génère des visuels (stations, cycle métro, affectations)

## Installation

Tout se fait via le Makefile :

```bash
make install
```

Cette commande crée `.venv`, installe pip dedans, puis les dépendances listées dans `requirements.txt`.

## Exécution

Lancer la résolution avec Make :

```bash
make run f=att48.tsp p=10
```

- `f` : chemin du fichier `.tsp` (défaut `ulysses16.tsp` situé dans `data/`).
- `p` : nombre de stations (défaut `5`).

Fichiers générés :
- `solution_gloutonne.png`
- `solution_descente.png`
- `solution_pulp.png` (si l'instance est assez petite pour PuLP)

## Cibles utiles

- `make install` : installe l'environnement virtuel et les dépendances.
- `make run f=... p=...` : exécute `main.py` avec l'instance et `p` donnés.
- `make clean` : supprime `.venv` et les fichiers temporaires Python.

## Notes importantes (sujet)

- Le point n°1 est toujours une station ⇒ dans le code : `station1 = 0` (index Python).
- Le coût total est : \( \alpha \cdot \text{distance métro} + \text{distance marche} \).
