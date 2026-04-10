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
    # Map each county FIPS to sorted neighbor FIPS (Queen contiguity).
    adjacency_map = {}
    for origin_id in w.id_order:
        county_fips = normalize_county_fips(gdf.at[origin_id, "_county_fips"])
        neighbor_ids = w.neighbors[origin_id]
        adjacency_map[county_fips] = sorted(
            normalize_county_fips(gdf.at[int(neighbor_id), "_county_fips"])
            for neighbor_id in neighbor_ids
        )
    return dict(sorted(adjacency_map.items()))


def parse_adjacency(state_fips):
    # Within-state Queen adjacency from Census polygons; projected to EPSG:5070 for weights.
    gdf = gpd.read_file(_DEFAULT_COUNTY_SHP)

    state_code = state_fips_2(state_fips)
    gdf = gdf[gdf["STATEFP"] == state_code].copy()
    gdf["_county_fips"] = gdf["GEOID"].astype(str).map(normalize_county_fips)

    gdf = gdf.to_crs(5070)
    gdf = gdf.reset_index(drop=True)

    w = weights.contiguity.Queen.from_dataframe(gdf, use_index=False)

    adjacency_map = _neighbors_dict_from_queen(gdf, w)

    os.makedirs(AUG_DIR, exist_ok=True)

    out_path = os.path.join(AUG_DIR, f"adjacency_{state_code}.json")

    with open(out_path, "w", encoding="utf-8") as out:
        json.dump(adjacency_map, out, indent=2)

    county_path = os.path.join(AUG_DIR, f"county_data_{state_code}.json")
    with open(county_path, encoding="utf-8") as f:
        county_data = json.load(f)
    adj_keys = set(adjacency_map.keys())
    cd_keys = set(county_data.keys())
    if adj_keys != cd_keys:
        only_adj = sorted(adj_keys - cd_keys)
        only_cd = sorted(cd_keys - adj_keys)
        raise ValueError(
            "Adjacency county FIPS keys do not match county_data JSON: "
            f"only_in_adjacency={only_adj}, only_in_county_data={only_cd}"
        )

    return adjacency_map


def load_adjacency(state_fips):
    sf = state_fips_2(state_fips)

    path = os.path.join(AUG_DIR, f"adjacency_{sf}.json")

    with open(path, encoding="utf-8") as f:
        return json.load(f)
