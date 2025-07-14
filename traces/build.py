import json
import os

from grids.atlantica import AtlanticaGrid
from grids.calama import CalamaGrid
from grids.marcona import MarconaGrid

OUTPUT_DIR = "data/mqtt/traces"


def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def generate_traces_json(traces, output_path="data/mqtt/traces/traces.json"):
    ensure_dir(os.path.dirname(output_path))
    with open(output_path, "w") as f:
        json.dump({"traces": traces}, f, indent=2)


def main():
    # Initialize
    grids = [MarconaGrid(), CalamaGrid(), AtlanticaGrid()]

    # Build each grid and collect traces
    all_traces = []
    for grid in grids:
        traces = grid.build(output_base_dir=OUTPUT_DIR)
        all_traces.extend(traces)
        print(f"Built grid {grid.name} with {len(traces)} traces.")

    generate_traces_json(all_traces)
    print(f"Wrote traces.json with {len(all_traces)} traces.")


if __name__ == "__main__":
    main()
