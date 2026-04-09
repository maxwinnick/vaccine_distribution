import time as tm

from gurobipy import GRB, Model, quicksum

# Solve the minimum coverage problem
def solve_min_coverage(adj, county_data):
    # Sort the counties by FIPS and create a dictionary to map FIPS to index
    counties = sorted(set(adj.keys()) | set(county_data.keys()))
    county_set = set(counties)

    # Sets and variables:
    # x[i] = 1 if county i is opened as a center
    IPmod = Model("min_coverage")
    IPmod.setParam("OutputFlag", 0)
    x = IPmod.addVars(counties, vtype=GRB.BINARY, name="x")

    # Objective: Minimize the number of centers
    IPmod.setObjective(quicksum(x[c] for c in counties), GRB.MINIMIZE)

    # Constraints: Each county must either be a center or be adjacent to a center
    for i in counties:
        nbr = adj[i]
        IPmod.addConstr(x[i] + quicksum(x[j] for j in nbr) >= 1)

    # Run Optimization and record solve time
    t0 = tm.time()
    IPmod.optimize()
    elapsed = tm.time() - t0

    xsol = IPmod.getAttr("x", x)
    centers = []
    for c in counties:
        if xsol[c] > 0.5:
            centers.append(c)

    return centers, float(IPmod.ObjVal), elapsed
