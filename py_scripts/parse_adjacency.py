import json
import os
from collections import defaultdict

_AUG_DIR = os.path.join(os.path.dirname(__file__), "..", "county_data", "augmented_data")


def _iter_adjacency_rows(filepath):
    last_county_fips = None
    with open(filepath, encoding="utf-8") as f:
        next(f)  # header
        for line in f:
            line = line.rstrip("\n")
            if not line.strip():
                continue
            parts = line.split("|")
            if len(parts) < 4:
                continue
            if not parts[0].strip() and last_county_fips is not None:
                county_fips = last_county_fips
                neighbor_fips = parts[2].strip()
            else:
                county_fips = parts[1].strip()
                neighbor_fips = parts[3].strip()
                last_county_fips = county_fips
            yield county_fips, neighbor_fips


def parse_adjacency(filepath, state_fips):
    """
    Read pipe-delimited Census county adjacency; keep only edges between counties
    whose GEOIDs start with state_fips (2-digit state code).
    Returns dict FIPS -> sorted neighbor FIPS list; writes JSON under augmented_data/.
    """
    state_fips = str(state_fips).zfill(2)[:2]
    neighbors = defaultdict(set)
    for county_fips, neighbor_fips in _iter_adjacency_rows(filepath):
        if not (county_fips.startswith(state_fips) and neighbor_fips.startswith(state_fips)):
            continue
        if county_fips == neighbor_fips:
            continue
        neighbors[county_fips].add(neighbor_fips)
        neighbors[neighbor_fips].add(county_fips)

    adj = {k: sorted(v) for k, v in sorted(neighbors.items())}
    os.makedirs(_AUG_DIR, exist_ok=True)
    out_path = os.path.join(_AUG_DIR, f"adjacency_{state_fips}.json")
    with open(out_path, "w", encoding="utf-8") as out:
        json.dump(adj, out, indent=2)
    return adj


def load_adjacency(state_fips):
    state_fips = str(state_fips).zfill(2)[:2]
    path = os.path.join(_AUG_DIR, f"adjacency_{state_fips}.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)
