import time as tm

from gurobipy import GRB, Model, quicksum

from helper_functions import _nearest_adjacent_center, require_optimal


def solve_min_coverage(adj, county_data):
    counties = sorted(set(adj.keys()) | set(county_data.keys()))

    model = Model("min_coverage")
    model.setParam("OutputFlag", 0)
    x = model.addVars(counties, vtype=GRB.BINARY, name="x")

    model.setObjective(quicksum(x[county] for county in counties), GRB.MINIMIZE)

    for county in counties:
        neighbors = adj.get(county, [])
        # Every county is covered by itself or by one adjacent center.
        model.addConstr(x[county] + quicksum(x[neighbor] for neighbor in neighbors) >= 1)

    t0 = tm.time()
    model.optimize()
    elapsed = tm.time() - t0

    require_optimal(model)

    x_solution = model.getAttr("x", x)
    centers = []
    for county in counties:
        if x_solution[county] > 0.5:
            centers.append(county)

    centers_set = set(centers)
    assigned = {}
    for fips in sorted(county_data.keys()):
        assigned[fips] = _nearest_adjacent_center(fips, centers_set, adj, county_data)

    return centers, float(model.ObjVal), elapsed, assigned
