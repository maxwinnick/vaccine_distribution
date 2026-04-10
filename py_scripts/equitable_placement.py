import time as tm

from gurobipy import GRB, Model, quicksum

from helper_functions import _haversine_miles, require_optimal


def solve_equitable(county_data, k):
    counties = sorted(county_data.keys())
    n = len(counties)
    if n == 0:
        raise ValueError("county_data is empty")
    if k < 1:
        raise ValueError("k must be at least 1 (model requires at least one center)")
    if k > n:
        raise ValueError(f"k ({k}) cannot exceed the number of counties ({n})")

    dist = [[0.0] * n for _ in range(n)]
    for i, fi in enumerate(counties):
        li, lo = county_data[fi]["lat"], county_data[fi]["lon"]
        for j, fj in enumerate(counties):
            lj, loj = county_data[fj]["lat"], county_data[fj]["lon"]
            dist[i][j] = _haversine_miles(li, lo, lj, loj)

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

    t0 = tm.time()
    IPmod.optimize()
    elapsed = tm.time() - t0

    require_optimal(IPmod)

    ysol = IPmod.getAttr("x", y)
    zsol = IPmod.getAttr("x", z)

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

    return centers, float(IPmod.ObjVal), elapsed, assigned
