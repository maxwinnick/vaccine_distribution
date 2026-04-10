import json
import os

import geopandas as gpd
from libpysal import weights

# Directory for augmented JSON outputs (same layout as parse_county_data)
_AUG_DIR = os.path.join(os.path.dirname(__file__), "..", "county_data", "augmented_data")

# Census cartographic county shapefile (500k); static layout under county_data/
_DEFAULT_COUNTY_SHP = os.path.join(
    os.path.dirname(__file__),
    "..",
    "county_data",
    "cb_2023_us_county_500k",
    "cb_2023_us_county_500k.shp",
)


def _state_fips_2(state_fips):
    # Normalize state FIPS to exactly 2 digits
    return str(state_fips).zfill(2)[:2]


def _neighbors_dict_from_queen(gdf, w):
    # Map each county FIPS to sorted neighbor FIPS using Queen contiguity weights
    gdf = gdf.reset_index(drop=True)
    adjacency_map = {}
    for oid in w.id_order:
        fid = str(gdf.at[oid, "_county_fips"]).zfill(5)
        nbrs = w.neighbors[oid]
        adjacency_map[fid] = sorted(
            str(gdf.at[int(j), "_county_fips"]).zfill(5) for j in nbrs
        )
    return dict(sorted(adjacency_map.items()))


def parse_adjacency(state_fips):
    # Build within-state county adjacency from Census county polygons (Queen contiguity, libpysal).
    # Counties are projected to EPSG:5070 before contiguity is computed.
    gdf = gpd.read_file(_DEFAULT_COUNTY_SHP)

    # Restrict to the requested state; GEOID is the 5-digit county FIPS on this layer
    sf = _state_fips_2(state_fips)
    gdf = gdf[gdf["STATEFP"] == sf].copy()
    gdf["_county_fips"] = gdf["GEOID"].astype(str).str.zfill(5)

    gdf = gdf.to_crs(5070)
    gdf = gdf.reset_index(drop=True)

    # Queen neighbors: shared boundary or vertex
    w = weights.contiguity.Queen.from_dataframe(gdf, use_index=False)

    adjacency_map = _neighbors_dict_from_queen(gdf, w)

    # Ensure the output folder exists before writing JSON
    os.makedirs(_AUG_DIR, exist_ok=True)

    # Build the output file path for this state
    out_path = os.path.join(_AUG_DIR, f"adjacency_{sf}.json")

    # Write the adjacency map to a formatted JSON file
    with open(out_path, "w", encoding="utf-8") as out:
        json.dump(adjacency_map, out, indent=2)

    # Return the adjacency map for direct reuse by callers
    return adjacency_map


def load_adjacency(state_fips):
    # Normalize state FIPS to exactly 2 digits
    sf = _state_fips_2(state_fips)

    # Build the JSON path for the requested state
    path = os.path.join(_AUG_DIR, f"adjacency_{sf}.json")

    # Open and return the parsed adjacency JSON content
    with open(path, encoding="utf-8") as f:
        return json.load(f)
