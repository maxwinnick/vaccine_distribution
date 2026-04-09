import time as tm

from gurobipy import GRB, Model, quicksum
from helper_functions import _haversine_miles

# Solve the equitable placement problem
def solve_equitable(county_data, k):

    # Sort the counties by FIPS and create a dictionary to map FIPS to index
    counties = sorted(county_data.keys())
    n = len(counties)
    idx = {fips: i for i, fips in enumerate(counties)}

    # Compute pairwise county-to-county distances (miles).
    dist = [[0.0] * n for _ in range(n)]
    for i, fi in enumerate(counties):
        li, lo = county_data[fi]["lat"], county_data[fi]["lon"]
        for j, fj in enumerate(counties):
            lj, loj = county_data[fj]["lat"], county_data[fj]["lon"]
            dist[i][j] = _haversine_miles(li, lo, lj, loj)

    # Population weight for each county in index order.
    pop = [county_data[fi]["population"] for fi in counties]

    # Sets and variables:
    # y[j] = 1 if county j is opened as a center
    # z[i,j] = 1 if county i is assigned to center j
    IPmod = Model("equitable_p_median")
    IPmod.setParam("OutputFlag", 0)
    y = IPmod.addVars(n, vtype=GRB.BINARY, name="y")
    z = IPmod.addVars(n, n, vtype=GRB.BINARY, name="z")

    # Objective: Minimize total population-weighted assignment distance.
    IPmod.setObjective(
        quicksum(pop[i] * dist[i][j] * z[i, j] for i in range(n) for j in range(n)),
        GRB.MINIMIZE,
    )

    # Constraints: Open at most k centers, and at least one center.
    IPmod.addConstr(quicksum(y[j] for j in range(n)) <= k)
    IPmod.addConstr(quicksum(y[j] for j in range(n)) >= 1)

    # Constraints: Every county must be assigned to exactly one center.
    for i in range(n):
        IPmod.addConstr(quicksum(z[i, j] for j in range(n)) == 1)

    # Constraints: Counties can only be assigned to centers that are opened.
    for i in range(n):
        for j in range(n):
            IPmod.addConstr(z[i, j] <= y[j])

    # Run Optimization and record solve time
    t0 = tm.time()
    IPmod.optimize()
    elapsed = tm.time() - t0

    ysol = IPmod.getAttr("x", y)
    zsol = IPmod.getAttr("x", z)

    # Extract selected centers from y.
    centers = []
    for j in range(n):
        if ysol[j] > 0.5:
            centers.append(counties[j])

    # Build county -> center assignment map from z.
    assigned = {}
    for i in range(n):
        for j in range(n):
            if zsol[i, j] > 0.5:
                assigned[counties[i]] = counties[j]
                break

    return centers, float(IPmod.ObjVal), elapsed, assigned
