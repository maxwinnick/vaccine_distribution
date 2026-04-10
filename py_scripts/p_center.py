import time as tm

from gurobipy import GRB, Model, quicksum

from helper_functions import _extract_facility_assignment, _pairwise_distance_matrix


def solve_p_center(county_data, k, adj):
    counties = sorted(county_data.keys())
    n = len(counties)
    distance = _pairwise_distance_matrix(counties, county_data)

    if k > n:
        raise ValueError(f"k ({k}) cannot exceed the number of counties ({n})")

    model = Model("equitable_p_center")
    model.setParam("OutputFlag", 0)
    y = model.addVars(n, vtype=GRB.BINARY, name="y")
    z = model.addVars(n, n, vtype=GRB.BINARY, name="z")
    max_assignment_distance = model.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name="D")

    model.setObjective(max_assignment_distance, GRB.MINIMIZE)

    # Open between 1 and k facilities.
    model.addConstr(quicksum(y[j] for j in range(n)) <= k)
    model.addConstr(quicksum(y[j] for j in range(n)) >= 1)

    for i in range(n):
        # Each county is assigned to exactly one open facility.
        model.addConstr(quicksum(z[i, j] for j in range(n)) == 1)

    for i in range(n):
        for j in range(n):
            # County i can only be assigned to county j if j is open.
            model.addConstr(z[i, j] <= y[j])

    for i in range(n):
        # p-center: upper bound on each county's assignment distance (minimize that bound).
        model.addConstr(
            quicksum(distance[i][j] * z[i, j] for j in range(n))
            <= max_assignment_distance
        )

    county_to_index = {fips: i for i, fips in enumerate(counties)}
    for county in counties:
        i = county_to_index[county]
        neighbor_terms = [
            y[county_to_index[neighbor]]
            for neighbor in adj.get(county, [])
            if neighbor in county_to_index
        ]
        # Coverage rule: county is a center or has an adjacent center.
        model.addConstr(y[i] + quicksum(neighbor_terms) >= 1)

    t0 = tm.time()
    model.optimize()
    elapsed = tm.time() - t0

    centers, assigned = _extract_facility_assignment(counties, n, y, z, model)
    return centers, float(model.ObjVal), elapsed, assigned
