import networkx as nx
import pulp

from heuristique import coutTotal


def resoudrePlneCompacte(
    matriceDist,
    p,
    alpha,
    station1,
):
    # Indices 0..n-1 dans le code, mais la formulation du PDF est en 1..n
    n = matriceDist.shape[0]
    sommets = list(range(n))
    aretes = [(i, j) for i in range(n) for j in range(i + 1, n)]  # arêtes non orientées

    modele = pulp.LpProblem("Anneau_Etoile", pulp.LpMinimize)

    # Variables y[i][j] : i affecté à j, et y[j][j]=1 si j station
    y = pulp.LpVariable.dicts("y", (sommets, sommets), lowBound=0, upBound=1, cat=pulp.LpBinary)

    # Variables x[i][j] pour i<j : arête du cycle métro
    x = pulp.LpVariable.dicts("x", aretes, lowBound=0, upBound=1, cat=pulp.LpBinary)

    # Variables de flot z[i][j] dirigées
    z = pulp.LpVariable.dicts("z", (sommets, sommets), lowBound=0, upBound=p - 1, cat=pulp.LpContinuous)

    # Objectif: alpha * sum(dij xij) + sum(dij yij)
    coutMetroLineaire = pulp.lpSum(float(matriceDist[i, j]) * x[(i, j)] for (i, j) in aretes)
    coutMarcheLineaire = pulp.lpSum(float(matriceDist[i, j]) * y[i][j] for i in sommets for j in sommets)
    modele += alpha * coutMetroLineaire + coutMarcheLineaire

    # (1) nombre de stations
    modele += pulp.lpSum(y[i][i] for i in sommets) == p

    # (2) chaque point affecté à exactement une station (ou lui-même s'il est station)
    for i in sommets:
        modele += pulp.lpSum(y[i][j] for j in sommets) == 1

    # (3) affectation seulement vers une station
    for i in sommets:
        for j in sommets:
            if i == j:
                continue
            modele += y[i][j] <= y[j][j]

    # Contraintes station1 (PDF: y11=1 et y1j=0)
    modele += y[station1][station1] == 1
    for j in sommets:
        if j == station1:
            continue
        modele += y[station1][j] == 0

    # (4) degré: sum_{arêtes incidentes à i} x = 2*yii
    for i in sommets:
        aretesIncidentes = []
        for j in sommets:
            if i == j:
                continue
            a, b = (i, j) if i < j else (j, i)
            aretesIncidentes.append(x[(a, b)])
        modele += pulp.lpSum(aretesIncidentes) == 2 * y[i][i]

    # (5) flot sortant de station1: sum_{j != 1} z1j = p-1
    modele += pulp.lpSum(z[station1][j] for j in sommets if j != station1) == p - 1

    # (6) conservation: flotEntrant(i) = flotSortant(i) + yii pour i != 1
    for i in sommets:
        if i == station1:
            continue
        flotEntrant = pulp.lpSum(z[j][i] for j in sommets if j != i)
        flotSortant = pulp.lpSum(z[i][j] for j in sommets if (j != i and j != station1))
        modele += flotEntrant == flotSortant + y[i][i]

    # (7) flot uniquement sur arêtes sélectionnées: z_ij + z_ji <= (p-1)*x_ij
    for i, j in aretes:
        modele += z[i][j] + z[j][i] <= (p - 1) * x[(i, j)]

    # (9) Renforcement : Si une arête existe, les extrémités sont des stations
    # for (i, j) in aretes:
    #     modele += y[j][j] >= x[(i, j)]
    #     modele += y[i][i] >= x[(i, j)]

    solveur = pulp.PULP_CBC_CMD(msg=False)
    statut = modele.solve(solveur)
    chaineStatut = pulp.LpStatus.get(statut, str(statut))

    stations = [i for i in sommets if (pulp.value(y[i][i]) or 0.0) > 0.5]
    stations = sorted(set(stations))

    affectation = []
    for i in sommets:
        stationAssociee = max(sommets, key=lambda j: pulp.value(y[i][j]) or 0.0)
        affectation.append(int(stationAssociee))

    aretesCycle = []
    for i, j in aretes:
        if (pulp.value(x[(i, j)]) or 0.0) > 0.5:
            aretesCycle.append((i, j))

    # Reconstruire un cycle ordonné sur les stations à partir des arêtes (cycle unique)
    graphe = nx.Graph()
    graphe.add_nodes_from(stations)
    graphe.add_edges_from(aretesCycle)

    cycleStations = [station1]
    if len(stations) > 1 and graphe.has_node(station1):
        stationPrecedente = None
        stationCourante = station1
        for _ in range(len(stations) - 1):
            voisins = list(graphe.neighbors(stationCourante))
            if len(voisins) < 2 and stationPrecedente is None:
                break
            stationSuivante = voisins[0] if stationPrecedente is None or voisins[0] != stationPrecedente else voisins[1]
            cycleStations.append(int(stationSuivante))
            stationPrecedente, stationCourante = stationCourante, stationSuivante

    cout, coutMetro, coutMarche = coutTotal(stations, cycleStations, affectation, matriceDist, alpha)
    return chaineStatut, {
        "stations": stations,
        "affectation": affectation,
        "cycleStations": cycleStations,
        "coutTotal": cout,
        "coutMetro": coutMetro,
        "coutMarche": coutMarche,
    }

