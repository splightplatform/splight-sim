import os
from datetime import datetime, timedelta
import json

from grids.atlantica import AtlanticaGrid
from grids.calama import CalamaGrid
from grids.marcona import MarconaGrid
from utils import normalize

START_DATE = datetime(2024, 1, 1)
MINUTES = 24 * 60
STEP = timedelta(minutes=1)
OUTPUT_DIR = "data/mqtt/traces"


def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def get_all_attributes(grids):
    """Get all unique attributes from all grids"""
    all_attrs = set()
    for grid in grids:
        all_attrs.update(grid.get_all_attributes())
    return sorted(list(all_attrs))


def get_assets_with_attribute(attr, grids):
    """Get all (grid, asset) pairs that have a specific attribute"""
    asset_grid_pairs = []
    for grid in grids:
        for asset in grid.assets:
            if attr in grid.get_attributes_for_asset(asset):
                asset_grid_pairs.append((grid, asset))
    return asset_grid_pairs


def generate_attribute_csv(attr, grids, output_dir=OUTPUT_DIR):
    ensure_dir(output_dir)
    filename = os.path.join(output_dir, f"{attr}.csv")

    asset_grid_pairs = get_assets_with_attribute(attr, grids)
    asset_grid_pairs = sorted(asset_grid_pairs, key=lambda pair: pair[1])
    if not asset_grid_pairs:
        print(f"No assets found for attribute {attr}, skipping...")
        return

    method_name = f"get_{attr}"

    with open(filename, "w") as f:
        # header
        f.write("timestamp," + ",".join(asset for _, asset in asset_grid_pairs) + "\n")

        current = START_DATE
        for _ in range(MINUTES):
            merged_values = {}
            for grid, _ in asset_grid_pairs:
                if hasattr(grid, method_name):
                    method = getattr(grid, method_name)
                    values = method(current)  # returns {asset: normalized_value}
                    merged_values.update(values)
            row_values = [
                merged_values.get(asset, normalize(grid.default_value(attr)))
                for grid, asset in asset_grid_pairs
            ]
            f.write(
                f"{current.strftime('%Y-%m-%d %H:%M:%S')},"
                + ",".join(row_values)
                + "\n"
            )
            current += STEP

    print(f"Wrote {filename} with {len(asset_grid_pairs)} assets")


def generate_traces_json(grids, all_attributes, output_path="data/mqtt/traces/traces.json"):
    traces = []
    for attr in all_attributes:
        asset_grid_pairs = get_assets_with_attribute(attr, grids)
        asset_grid_pairs = sorted(asset_grid_pairs, key=lambda pair: pair[1])
        for grid, asset in asset_grid_pairs:
            noise = 0.02 if ("switch_status" not in attr and attr != "contingency") else None
            trace = {
                "name": f"{grid.name}/{asset}/{attr}",
                "topic": f"{grid.name}/{asset}/{attr}",
                "filename": f"{attr}.csv",
                "noise_factor": noise,
                "match_timestamp_by": "hour",
                "target_value": asset
            }
            traces.append(trace)
    ensure_dir(os.path.dirname(output_path))
    with open(output_path, "w") as f:
        json.dump({"traces": traces}, f, indent=2)


def main():
    # Initialize
    grids = [MarconaGrid(), CalamaGrid(), AtlanticaGrid()]

    # Get all unique attributes
    all_attributes = get_all_attributes(grids)
    print(f"Found {len(all_attributes)} unique attributes: {all_attributes}")

    # Generate one CSV per attribute
    for attr in all_attributes:
        generate_attribute_csv(attr, grids)

    # Generate traces.json
    generate_traces_json(grids, all_attributes)


if __name__ == "__main__":
    main()
