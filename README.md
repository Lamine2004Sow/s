# SAE Optimisation 2025-2026 — Anneau-étoile (Ring-Star)

Ce dossier contient un script Python simple qui :
- lit une instance `.tsp` (TSPLIB95) avec `tsplib95`
- construit la matrice de distances euclidiennes (`matriceDist`)
- calcule une solution heuristique (glouton p-médian + TSP plus proche voisin)
- améliore la solution par descente stochastique (swap station / non-station)
- résout (optionnel) la formulation exacte compacte avec PuLP (CPLEX)
- visualise les solutions (stations, cycle métro, affectations)

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Exécution (exemple)

Sur une petite instance :

```bash
python3 main.py data/att48.tsp 10
```

Fichiers générés :
- `solution_gloutonne.png`
- `solution_descente.png`
- `solution_pulp.png` (si l'instance est assez petite pour PuLP)

## Notes importantes (sujet)

- Le point n°1 est toujours une station ⇒ dans le code : `station1 = 0` (index Python).
- Le coût total est : \( \alpha \cdot \text{distance métro} + \text{distance marche} \).
