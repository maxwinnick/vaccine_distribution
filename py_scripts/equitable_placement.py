import time as tm

from gurobipy import GRB, Model, quicksum

from helper_functions import _haversine_miles, require_optimal


def _build_distance_matrix(county_data):
    counties = sorted(county_data.keys())
    n = len(counties)
    dist = [[0.0] * n for _ in range(n)]
    for i, fi in enumerate(counties):
        li, lo = county_data[fi]["lat"], county_data[fi]["lon"]
        for j, fj in enumerate(counties):
            lj, loj = county_data[fj]["lat"], county_data[fj]["lon"]
            dist[i][j] = _haversine_miles(li, lo, lj, loj)
    return counties, n, dist


def _add_coverage_constraints(IPmod, counties, n, y, adj):
    idx = {fips: i for i, fips in enumerate(counties)}
    for c in counties:
        i = idx[c]
        nbr_terms = [y[idx[j]] for j in adj.get(c, []) if j in idx]
        IPmod.addConstr(y[i] + quicksum(nbr_terms) >= 1)


def _extract_solution(counties, n, y, z, model):
    require_optimal(model)
    ysol = model.getAttr("x", y)
    zsol = model.getAttr("x", z)
    centers = []
    for j in range(n):
        if ysol[j] > 0.5:
            centers.append(counties[j])
    assigned = {}
    for i in range(n):
        for j in range(n):
            if zsol[i, j] > 0.5:
                assigned[counties[i]] = counties[j]
                break
    return centers, assigned


def solve_equitable(county_data, k, adj):
    counties, n, dist = _build_distance_matrix(county_data)
    if n == 0:
        raise ValueError("county_data is empty")
    if k < 1:
        raise ValueError("k must be at least 1 (model requires at least one center)")
    if k > n:
        raise ValueError(f"k ({k}) cannot exceed the number of counties ({n})")

    pop = [county_data[fi]["population"] for fi in counties]

    IPmod = Model("equitable_p_median")
    IPmod.setParam("OutputFlag", 0)
    y = IPmod.addVars(n, vtype=GRB.BINARY, name="y")
    z = IPmod.addVars(n, n, vtype=GRB.BINARY, name="z")

    IPmod.setObjective(
        quicksum(pop[i] * dist[i][j] * z[i, j] for i in range(n) for j in range(n)),
        GRB.MINIMIZE,
    )

    IPmod.addConstr(quicksum(y[j] for j in range(n)) <= k)
    IPmod.addConstr(quicksum(y[j] for j in range(n)) >= 1)

    for i in range(n):
        IPmod.addConstr(quicksum(z[i, j] for j in range(n)) == 1)

    for i in range(n):
        for j in range(n):
            IPmod.addConstr(z[i, j] <= y[j])

    _add_coverage_constraints(IPmod, counties, n, y, adj)

    t0 = tm.time()
    IPmod.optimize()
    elapsed = tm.time() - t0

    centers, assigned = _extract_solution(counties, n, y, z, IPmod)
    return centers, float(IPmod.ObjVal), elapsed, assigned


def solve_equitable_p_center(county_data, k, adj):
    counties, n, dist = _build_distance_matrix(county_data)
    if n == 0:
        raise ValueError("county_data is empty")
    if k < 1:
        raise ValueError("k must be at least 1 (model requires at least one center)")
    if k > n:
        raise ValueError(f"k ({k}) cannot exceed the number of counties ({n})")

    IPmod = Model("equitable_p_center")
    IPmod.setParam("OutputFlag", 0)
    y = IPmod.addVars(n, vtype=GRB.BINARY, name="y")
    z = IPmod.addVars(n, n, vtype=GRB.BINARY, name="z")
    D = IPmod.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name="D")

    IPmod.setObjective(D, GRB.MINIMIZE)

    IPmod.addConstr(quicksum(y[j] for j in range(n)) <= k)
    IPmod.addConstr(quicksum(y[j] for j in range(n)) >= 1)

    for i in range(n):
        IPmod.addConstr(quicksum(z[i, j] for j in range(n)) == 1)

    for i in range(n):
        for j in range(n):
            IPmod.addConstr(z[i, j] <= y[j])

    for i in range(n):
        IPmod.addConstr(
            quicksum(dist[i][j] * z[i, j] for j in range(n)) <= D
        )

    _add_coverage_constraints(IPmod, counties, n, y, adj)

    t0 = tm.time()
    IPmod.optimize()
    elapsed = tm.time() - t0

    centers, assigned = _extract_solution(counties, n, y, z, IPmod)
    return centers, float(IPmod.ObjVal), elapsed, assigned
