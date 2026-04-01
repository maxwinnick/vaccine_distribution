# Vaccine Distribution — Project Plan

## Directory Structure

```
project_root/
│
├── county_data/
│   ├── county_adjacency.txt              # Raw Census adjacency file
│   ├── county_demographics.csv           # Raw county demographics (FIPS, name, state, pop, lat, lon)
│   ├── cb_2023_us_county_500k/           # Census cartographic boundary shapefile (for mapping)
│   │   ├── cb_2023_us_county_500k.shp
│   │   ├── cb_2023_us_county_500k.dbf
│   │   └── cb_2023_us_county_500k.shx
│   └── augmented_data/                   # All parsed/created data written here
│       ├── adjacency_26.json
│       └── county_data_26.json
│
├── 410_Source_Code/                       # Course reference code (read-only, style reference)
│
├── py_scripts/                            # All project Python scripts
│   ├── parse_adjacency.py                # Script 1
│   ├── parse_county_data.py              # Script 2
│   ├── min_coverage.py                   # Script 3
│   └── equitable_placement.py            # Script 4
│
└── experiments.ipynb                      # Calls functions, displays map + dataframe
```

---

## Data Sources

| Dataset | Source | Notes |
|---|---|---|
| County Adjacency | `census.gov/programs-surveys/geography` | Pipe-delimited TXT, maps each FIPS to its neighbor FIPS codes |
| County Demographics | U.S. Census Bureau / USDA ERS | CSV with FIPS, name, state, population, lat, lon |
| County Shapefile | Census Cartographic Boundary Files (`cb_2023_us_county_500k.zip`) | Download from `census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.html` |

---

## Mapping Approach

**Library:** `geopandas` + `matplotlib`

The notebook uses the Census cartographic boundary shapefile (`cb_2023_us_county_500k.shp`) loaded via `geopandas.read_file()`. This gives county polygons with a `GEOID` column (5-digit FIPS) that joins directly to our parsed county data.

**Plot structure for each map cell:**
1. Filter the GeoDataFrame to the selected state FIPS.
2. Plot county boundary polygons as the base layer (light gray fill, black edges).
3. Overlay circles at each county centroid, sized proportional to population density (`pop / area`). Use `plt.scatter()` with a scaled `s` parameter.
4. Color centers in red, non-centers in blue.
5. Label each county with its name using `plt.annotate()` at the centroid, small font.
6. `plt.show()` inline — no saving to disk.

```python
import geopandas as gpd
import matplotlib.pyplot as plt

shp = gpd.read_file("county_data/cb_2023_us_county_500k/cb_2023_us_county_500k.shp")
state_shp = shp[shp["STATEFP"] == STATE_FIPS]

fig, ax = plt.subplots(1, 1, figsize=(12, 10))
state_shp.plot(ax=ax, color="lightgray", edgecolor="black", linewidth=0.5)

for i in range(n):
    fips = fips_list[i]
    centroid = state_shp[state_shp["GEOID"] == fips].geometry.centroid.iloc[0]
    color = "red" if fips in centers else "steelblue"
    size = density[i] * scale_factor     #proportional to pop density
    ax.scatter(centroid.x, centroid.y, s=size, c=color, alpha=0.6, edgecolors="black", linewidth=0.5)
    ax.annotate(cdata[fips]["name"], (centroid.x, centroid.y), fontsize=4, ha="center")

ax.set_title("Vaccine Centers — "+state_name)
ax.axis("off")
plt.show()
```

---

## Scripts

### Script 1 — `py_scripts/parse_adjacency.py`

Reads `county_data/county_adjacency.txt`. Writes `county_data/augmented_data/adjacency_{state_fips}.json`.

- Parse pipe-delimited rows, handle continuation rows (blank first column).
- Filter by state FIPS prefix.
- Remove self-loops, enforce symmetry.
- Expose `parse_adjacency(filepath, state_fips)` → returns and saves dict.
- Expose `load_adjacency(state_fips)` → reads saved JSON.

### Script 2 — `py_scripts/parse_county_data.py`

Reads `county_data/county_demographics.csv`. Writes `county_data/augmented_data/county_data_{state_fips}.json`.

- Read CSV, zero-pad FIPS to 5 digits.
- Filter by state FIPS prefix.
- Expose `parse_county_data(filepath, state_fips)` → returns and saves dict.
- Expose `load_county_data(state_fips)` → reads saved JSON.

### Script 3 — `py_scripts/min_coverage.py`

Minimum vaccine centers so every county is covered by itself or a neighbor.

```
minimize    Σ_i  x_i
subject to  x_i + Σ_{j ∈ N(i)} x_j  ≥  1    ∀ county i
            x_i ∈ {0, 1}
```

- Expose `solve_min_coverage(adj, county_data)` → returns list of center FIPS, objective, solve time.
- Matches `410_Source_Code/` Gurobi style: `Model`, `addVars`, `quicksum`, `addConstr`, `setParam("OutputFlag",0)`, `optimize`, `getAttr`.

### Script 4 — `py_scripts/equitable_placement.py`

Given k centers, minimize population-weighted distance to nearest center.

```
minimize    Σ_i Σ_j  pop_i × d_{ij} × z_{ij}
subject to  Σ_j  y_j  ≤  k
            z_{ij} ≤ y_j              ∀ i,j
            Σ_j  z_{ij} = 1           ∀ i
            y_j, z_{ij} ∈ {0, 1}
```

- Expose `solve_equitable(adj, county_data, k)` → returns list of center FIPS, objective, solve time.
- Haversine for pairwise distances from lat/lon.
- Same Gurobi style as Script 3.

---

## Notebook — `experiments.ipynb`

Minimal. Calls functions, displays inline map, displays `pd.DataFrame`. No saved figures.

**Cell 1 — Config & imports**
```python
import sys
sys.path.insert(0, "py_scripts")
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

from parse_adjacency import parse_adjacency, load_adjacency
from parse_county_data import parse_county_data, load_county_data
from min_coverage import solve_min_coverage
from equitable_placement import solve_equitable

STATE_FIPS = "26"   # Michigan — change to run a different state
K = 30              # Budget for equitable placement
```

**Cell 2 — Parse data** (skip if already cached)
```python
parse_adjacency("county_data/county_adjacency.txt", STATE_FIPS)
parse_county_data("county_data/county_demographics.csv", STATE_FIPS)
adj = load_adjacency(STATE_FIPS)
cdata = load_county_data(STATE_FIPS)
```

**Cell 3 — Load shapefile**
```python
shp = gpd.read_file("county_data/cb_2023_us_county_500k/cb_2023_us_county_500k.shp")
state_shp = shp[shp["STATEFP"] == STATE_FIPS]
```

**Cell 4 — Part A: solve**
```python
centers_a, obj_a, time_a = solve_min_coverage(adj, cdata)
```

**Cell 5 — Part A: map**
- County boundaries from `state_shp`.
- Red circles at centers, blue circles at non-centers.
- Circle size ∝ population density.
- County name labels at centroids.
- `plt.show()`.

**Cell 6 — Part A: dataframe**
```python
rows = []
for fips in cdata:
    rows.append({
        "FIPS": fips,
        "County": cdata[fips]["name"],
        "Population": cdata[fips]["population"],
        "Is_Center": fips in centers_a
    })
df_a = pd.DataFrame(rows)
display(df_a)
```

**Cell 7 — Part B: solve**
```python
centers_b, obj_b, time_b = solve_equitable(adj, cdata, K)
```

**Cell 8 — Part B: map**
- Same pattern as Cell 5, using `centers_b`.

**Cell 9 — Part B: dataframe**
```python
rows = []
for fips in cdata:
    rows.append({
        "FIPS": fips,
        "County": cdata[fips]["name"],
        "Population": cdata[fips]["population"],
        "Is_Center": fips in centers_b,
        "Assigned_To": assigned[fips]   # from solve_equitable return
    })
df_b = pd.DataFrame(rows)
display(df_b)
```
