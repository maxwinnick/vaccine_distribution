import math
import time

from gurobipy import GRB, Model, quicksum


def _haversine_miles(lat1, lon1, lat2, lon2):
    """Great-circle distance in miles."""
    rlat1, rlon1 = math.radians(lat1), math.radians(lon1)
    rlat2, rlon2 = math.radians(lat2), math.radians(lon2)
    dlat = rlat2 - rlat1
    dlon = rlon2 - rlon1
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(rlat1) * math.cos(rlat2) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.asin(min(1.0, math.sqrt(a)))
    return 3958.7613 * c


def solve_equitable(adj, county_data, k):
    """
    p-median style: at most k centers, minimize population-weighted distance to assigned center.
    adj is unused but kept for a uniform API with solve_min_coverage.

    Returns (center FIPS list, objective, solve time seconds, assigned dict county_fips -> center_fips).
    """
    _ = adj
    counties = sorted(county_data.keys())
    n = len(counties)
    idx = {fips: i for i, fips in enumerate(counties)}

    dist = [[0.0] * n for _ in range(n)]
    for i, fi in enumerate(counties):
        li, lo = county_data[fi]["lat"], county_data[fi]["lon"]
        for j, fj in enumerate(counties):
            lj, loj = county_data[fj]["lat"], county_data[fj]["lon"]
            dist[i][j] = _haversine_miles(li, lo, lj, loj)

    pop = [county_data[fi]["population"] for fi in counties]

    m = Model("equitable_p_median")
    m.setParam("OutputFlag", 0)
    y = m.addVars(n, vtype=GRB.BINARY, name="y")
    z = m.addVars(n, n, vtype=GRB.BINARY, name="z")

    m.setObjective(
        quicksum(pop[i] * dist[i][j] * z[i, j] for i in range(n) for j in range(n)),
        GRB.MINIMIZE,
    )
    m.addConstr(quicksum(y[j] for j in range(n)) <= k)
    m.addConstr(quicksum(y[j] for j in range(n)) >= 1)
    for i in range(n):
        m.addConstr(quicksum(z[i, j] for j in range(n)) == 1)
    for i in range(n):
        for j in range(n):
            m.addConstr(z[i, j] <= y[j])

    t0 = time.perf_counter()
    m.optimize()
    elapsed = time.perf_counter() - t0

    if m.Status != GRB.OPTIMAL:
        raise RuntimeError(f"Gurobi status {m.Status} (expected OPTIMAL)")

    centers = [counties[j] for j in range(n) if y[j].X > 0.5]
    assigned = {}
    for i in range(n):
        for j in range(n):
            if z[i, j].X > 0.5:
                assigned[counties[i]] = counties[j]
                break

    return centers, float(m.ObjVal), elapsed, assigned
