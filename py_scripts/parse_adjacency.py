import json
import os

import geopandas as gpd
from libpysal import weights

from helper_functions import AUG_DIR, normalize_county_fips, state_fips_2

# Census cartographic county shapefile (500k)
_DEFAULT_COUNTY_SHP = os.path.join(
    os.path.dirname(__file__),
    "..",
    "county_data",
    "cb_2023_us_county_500k",
    "cb_2023_us_county_500k.shp",
)


def _neighbors_dict_from_queen(gdf, w):
    # Map each county FIPS to sorted neighbor FIPS (Queen contiguity; gdf index 0..n-1).
    adjacency_map = {}
    for oid in w.id_order:
        fid = normalize_county_fips(gdf.at[oid, "_county_fips"])
        nbrs = w.neighbors[oid]
        adjacency_map[fid] = sorted(
            normalize_county_fips(gdf.at[int(j), "_county_fips"]) for j in nbrs
        )
    return dict(sorted(adjacency_map.items()))


def parse_adjacency(state_fips):
    # Within-state Queen adjacency from Census polygons; projected to EPSG:5070 for weights.
    gdf = gpd.read_file(_DEFAULT_COUNTY_SHP)

    sf = state_fips_2(state_fips)
    gdf = gdf[gdf["STATEFP"] == sf].copy()
    gdf["_county_fips"] = gdf["GEOID"].astype(str).map(normalize_county_fips)

    gdf = gdf.to_crs(5070)
    gdf = gdf.reset_index(drop=True)

    w = weights.contiguity.Queen.from_dataframe(gdf, use_index=False)

    adjacency_map = _neighbors_dict_from_queen(gdf, w)

    os.makedirs(AUG_DIR, exist_ok=True)

    out_path = os.path.join(AUG_DIR, f"adjacency_{sf}.json")

    with open(out_path, "w", encoding="utf-8") as out:
        json.dump(adjacency_map, out, indent=2)

    return adjacency_map


def load_adjacency(state_fips):
    sf = state_fips_2(state_fips)

    path = os.path.join(AUG_DIR, f"adjacency_{sf}.json")

    with open(path, encoding="utf-8") as f:
        return json.load(f)
