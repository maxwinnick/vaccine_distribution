import time as tm

from gurobipy import GRB, Model, quicksum

from helper_functions import require_optimal


def solve_min_coverage(adj, county_data):
    counties = sorted(set(adj.keys()) | set(county_data.keys()))

    IPmod = Model("min_coverage")
    IPmod.setParam("OutputFlag", 0)
    x = IPmod.addVars(counties, vtype=GRB.BINARY, name="x")

    IPmod.setObjective(quicksum(x[c] for c in counties), GRB.MINIMIZE)

    for i in counties:
        nbr = adj.get(i, [])
        IPmod.addConstr(x[i] + quicksum(x[j] for j in nbr) >= 1)

    t0 = tm.time()
    IPmod.optimize()
    elapsed = tm.time() - t0

    require_optimal(IPmod)

    xsol = IPmod.getAttr("x", x)
    centers = []
    for c in counties:
        if xsol[c] > 0.5:
            centers.append(c)

    return centers, float(IPmod.ObjVal), elapsed
