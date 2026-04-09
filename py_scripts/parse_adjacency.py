import json
import os
from collections import defaultdict

_AUG_DIR = os.path.join(os.path.dirname(__file__), "..", "county_data", "augmented_data")


def parse_adjacency(filepath, state_fips):
    # Normalize state FIPS to exactly 2 digits.
    state_fips = str(state_fips).zfill(2)[:2]

    # Use a set for each county so duplicate edges are automatically removed
    neighbors = defaultdict(set)

    # Open the adjacency text file and skip the header line
    with open(filepath, encoding="utf-8") as f:
        next(f)

        # Read each line and parse fixed pipe-delimited columns
        for line in f:
            parts = line.rstrip("\n").split("|")
            county_fips = parts[1].strip()
            neighbor_fips = parts[3].strip()

            # Keep only within-state county-to-county relationships
            if county_fips[:2] != state_fips or neighbor_fips[:2] != state_fips:
                continue

            # Store both directions so adjacency is undirected
            neighbors[county_fips].add(neighbor_fips)
            neighbors[neighbor_fips].add(county_fips)

    # Convert each neighbor set to a sorted list for stable JSON output
    adjacency_map = {}
    for county_fips, neighbor_set in sorted(neighbors.items()):
        adjacency_map[county_fips] = sorted(neighbor_set)

    # Ensure the output folder exists before writing JSON
    os.makedirs(_AUG_DIR, exist_ok=True)

    # Build the output file path for this state
    out_path = os.path.join(_AUG_DIR, f"adjacency_{state_fips}.json")

    # Write the parsed adjacency map to a formatted JSON file
    with open(out_path, "w", encoding="utf-8") as out:
        json.dump(adjacency_map, out, indent=2)

    # Return the parsed adjacency map for direct reuse by callers
    return adjacency_map


def load_adjacency(state_fips):
    # Normalize state FIPS to exactly 2 digits
    state_fips = str(state_fips).zfill(2)[:2]

    # Build the JSON path for the requested state
    path = os.path.join(_AUG_DIR, f"adjacency_{state_fips}.json")

    # Open and return the parsed adjacency JSON content
    with open(path, encoding="utf-8") as f:
        return json.load(f)
