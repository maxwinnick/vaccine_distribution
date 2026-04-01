import time

from gurobipy import GRB, Model, quicksum


def solve_min_coverage(adj, county_data):
    """
    Minimum dominating set: choose centers so each county is covered by itself or a neighbor.
    Returns (list of center FIPS, objective value, solve time seconds).
    """
    counties = sorted(set(adj.keys()) | set(county_data.keys()))
    county_set = set(counties)
    adj_clean = {k: [n for n in adj.get(k, []) if n in county_set] for k in counties}

    m = Model("min_coverage_domination")
    m.setParam("OutputFlag", 0)
    x = m.addVars(counties, vtype=GRB.BINARY, name="x")
    m.setObjective(quicksum(x[c] for c in counties), GRB.MINIMIZE)
    for i in counties:
        nbr = adj_clean[i]
        m.addConstr(x[i] + quicksum(x[j] for j in nbr) >= 1)

    t0 = time.perf_counter()
    m.optimize()
    elapsed = time.perf_counter() - t0

    if m.Status != GRB.OPTIMAL:
        raise RuntimeError(f"Gurobi status {m.Status} (expected OPTIMAL)")

    centers = [c for c in counties if x[c].X > 0.5]
    return centers, float(m.ObjVal), elapsed
