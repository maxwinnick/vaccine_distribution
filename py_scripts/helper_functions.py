import math
import os

import matplotlib.pyplot as plt
import pandas as pd
from gurobipy import GRB

# JSON outputs from parse_adjacency / parse_county_data
AUG_DIR = os.path.join(os.path.dirname(__file__), "..", "county_data", "augmented_data")


def state_fips_2(state_fips):
    return str(state_fips).zfill(2)[:2]


def normalize_county_fips(county_fips):
    return str(county_fips).zfill(5)[:5]


STATE_FIPS_TO_NAME = {
    "01": "Alabama",
    "02": "Alaska",
    "04": "Arizona",
    "05": "Arkansas",
    "06": "California",
    "08": "Colorado",
    "09": "Connecticut",
    "10": "Delaware",
    "11": "District of Columbia",
    "12": "Florida",
    "13": "Georgia",
    "15": "Hawaii",
    "16": "Idaho",
    "17": "Illinois",
    "18": "Indiana",
    "19": "Iowa",
    "20": "Kansas",
    "21": "Kentucky",
    "22": "Louisiana",
    "23": "Maine",
    "24": "Maryland",
    "25": "Massachusetts",
    "26": "Michigan",
    "27": "Minnesota",
    "28": "Mississippi",
    "29": "Missouri",
    "30": "Montana",
    "31": "Nebraska",
    "32": "Nevada",
    "33": "New Hampshire",
    "34": "New Jersey",
    "35": "New Mexico",
    "36": "New York",
    "37": "North Carolina",
    "38": "North Dakota",
    "39": "Ohio",
    "40": "Oklahoma",
    "41": "Oregon",
    "42": "Pennsylvania",
    "44": "Rhode Island",
    "45": "South Carolina",
    "46": "South Dakota",
    "47": "Tennessee",
    "48": "Texas",
    "49": "Utah",
    "50": "Vermont",
    "51": "Virginia",
    "53": "Washington",
    "54": "West Virginia",
    "55": "Wisconsin",
    "56": "Wyoming",
}


STATE_NAME_TO_FIPS = {name: fips for fips, name in STATE_FIPS_TO_NAME.items()}


def state_name_to_fips(state_name):
    try:
        return STATE_NAME_TO_FIPS[state_name]
    except KeyError as exc:
        choices = ", ".join(sorted(STATE_NAME_TO_FIPS))
        raise ValueError(
            f"Unknown state name '{state_name}'. Expected one of: {choices}"
        ) from exc


def _haversine_miles(lat1, lon1, lat2, lon2):
    # Radius of Earth in miles
    R = 3958.7613

    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))

    return R * c


def require_optimal(model):
    if model.Status != GRB.OPTIMAL:
        raise RuntimeError(
            f"Gurobi finished with status {model.Status} (expected OPTIMAL)"
        )


def _pairwise_distance_matrix(counties, county_data):
    n = len(counties)
    distance = [[0.0] * n for _ in range(n)]
    for i, county_i in enumerate(counties):
        lat_i, lon_i = county_data[county_i]["lat"], county_data[county_i]["lon"]
        for j, county_j in enumerate(counties):
            lat_j, lon_j = county_data[county_j]["lat"], county_data[county_j]["lon"]
            distance[i][j] = _haversine_miles(lat_i, lon_i, lat_j, lon_j)
    return distance


def _extract_facility_assignment(counties, n, y, z, model):
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


def _nearest_adjacent_center(fips, centers_set, adj, cdata):
    if fips in centers_set:
        return fips
    nbr_centers = [j for j in adj.get(fips, []) if j in centers_set]
    if not nbr_centers:
        raise RuntimeError(
            f"Min-coverage post-process: county {fips} has no adjacent open center "
            "(solver output inconsistent with cover constraints)"
        )
    lat, lon = cdata[fips]["lat"], cdata[fips]["lon"]
    return min(
        nbr_centers,
        key=lambda j: _haversine_miles(lat, lon, cdata[j]["lat"], cdata[j]["lon"]),
    )


def _assigned_distance_miles(fips, cdata, assigned):
    af = assigned[fips]
    d = cdata[fips]
    if af == fips:
        return 0.0
    return _haversine_miles(d["lat"], d["lon"], cdata[af]["lat"], cdata[af]["lon"])


def total_state_population(cdata):
    return sum(d["population"] for d in cdata.values())


def total_population_weighted_distance(cdata, assigned):
    return sum(
        cdata[f]["population"] * _assigned_distance_miles(f, cdata, assigned)
        for f in cdata
    )


def max_assigned_distance_miles(cdata, assigned):
    return max(_assigned_distance_miles(f, cdata, assigned) for f in cdata)


def avg_miles_per_person(cdata, assigned):
    tot_pop = total_state_population(cdata)
    if not tot_pop:
        return 0.0
    return total_population_weighted_distance(cdata, assigned) / tot_pop


def assignment_metrics(cdata, assigned):
    """Commensurable stats from an assignment map (same logic as dataframe_assignment distances)."""
    twd = total_population_weighted_distance(cdata, assigned)
    tot_pop = total_state_population(cdata)
    return {
        "total_person_miles": twd,
        "max_miles": max_assigned_distance_miles(cdata, assigned),
        "avg_miles_per_person": twd / tot_pop if tot_pop else 0.0,
    }


def dataframe_assignment(centers, assigned, cdata):
    centers_set = set(centers)
    rows = []
    for fips, data in sorted(cdata.items()):
        af = assigned[fips]
        dist_mi = (
            0.0
            if af == fips
            else _haversine_miles(
                data["lat"], data["lon"], cdata[af]["lat"], cdata[af]["lon"]
            )
        )
        rows.append(
            {
                "FIPS": fips,
                "County": data["name"],
                "Population": data["population"],
                "Is_Center": fips in centers_set,
                "Serving_Center_FIPS": af,
                "Serving_Center": cdata[af]["name"],
                "Distance_Miles": dist_mi,
                "Weighted_Distance": data["population"] * dist_mi,
            }
        )
    return pd.DataFrame(rows)


def plot_centers(state_shp, cdata, centers, title_suffix, pad_frac=0.0):
    # Plot the state map and mark selected center counties.
    center_fips = sorted(set(centers) & set(cdata))
    centroids = state_shp[state_shp["GEOID"].isin(center_fips)].copy()
    centroids["pt"] = centroids.geometry.centroid
    fig, ax = plt.subplots(figsize=(12, 10))
    state_shp.plot(ax=ax, color="lightgray", edgecolor="black", linewidth=0.5)

    # Plot the centroids of the selected center counties
    for _, row in centroids.iterrows():
        fips = normalize_county_fips(row["GEOID"])
        pt = row["pt"]
        ax.scatter(pt.x, pt.y, s=45, c="red", edgecolors="black", linewidths=0.5)

        # Annotate county name above the point, in bold font
        ax.annotate(
            cdata[fips]["name"],
            (pt.x, pt.y),
            fontsize=7,
            ha="center",
            va="bottom",
            fontweight="bold"
        )

    state_name = next(iter(cdata.values()))["state"]
    ax.set_title(f"Vaccine centers - {state_name} ({title_suffix})")
    # Keep full state extent visible; optional tiny padding.
    minx, miny, maxx, maxy = state_shp.total_bounds
    dx = max(maxx - minx, 1e-9)
    dy = max(maxy - miny, 1e-9)
    pad_frac = max(float(pad_frac), 0.0)
    padx = pad_frac * dx
    pady = pad_frac * dy
    ax.set_xlim(minx - padx, maxx + padx)
    ax.set_ylim(miny - pady, maxy + pady)
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")
    plt.show()
