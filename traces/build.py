import os
from datetime import datetime, timedelta

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
    """Get all assets that have a specific attribute"""
    assets_with_attr = []
    for grid in grids:
        for asset in grid.assets:
            if attr in grid.get_attributes_for_asset(asset):
                assets_with_attr.append(asset)
    return sorted(list(set(assets_with_attr)))


def generate_attribute_csv(attr, grids, output_dir=OUTPUT_DIR):
    ensure_dir(output_dir)
    filename = os.path.join(output_dir, f"{attr}.csv")

    # Get all assets that have this attribute
    assets_with_attr = get_assets_with_attribute(attr, grids)

    if not assets_with_attr:
        print(f"No assets found for attribute {attr}, skipping...")
        return

    with open(filename, "w") as f:
        # Write header
        f.write("timestamp," + ",".join(assets_with_attr) + "\n")

        # Write data rows
        current = START_DATE
        for _ in range(MINUTES):
            row_values = []
            for asset in assets_with_attr:
                # Find which grid this asset belongs to
                value = 0.0
                for grid in grids:
                    if asset in grid.assets and attr in grid.get_attributes_for_asset(
                        asset
                    ):
                        value = grid.get_value(asset, attr, current)
                        break
                row_values.append(normalize(value))

            f.write(
                f"{current.strftime('%Y-%m-%d %H:%M:%S')},"
                + ",".join(row_values)
                + "\n"
            )
            current += STEP

    print(f"Wrote {filename} with {len(assets_with_attr)} assets")


def main():
    # Initialize all grids
    grids = [MarconaGrid(), CalamaGrid(), AtlanticaGrid()]

    # Get all unique attributes
    all_attributes = get_all_attributes(grids)
    print(f"Found {len(all_attributes)} unique attributes: {all_attributes}")

    # Generate one CSV per attribute
    for attr in all_attributes:
        generate_attribute_csv(attr, grids)


if __name__ == "__main__":
    main()
