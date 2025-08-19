import os
import sys
import time
import json
import argparse
from datetime import datetime, timedelta
from typing import Dict
from pathlib import Path
import pandas as pd

sys.path.append(r"C:\OPAL-RT\HYPERSIM\hypersim_2025.1.0.o39\Windows\HyApi\python")
import HyWorksApiGRPC as HyWorksApi


def set_parameter(value, block, column, hour_str):
    try:
        value = float(value[column])
        HyWorksApi.setComponentParameter(block, "A", str(value))
        print(f"[{hour_str}] Active: {column} → {block}.A = {value}")
    except Exception as e:
        print(f"[{hour_str}] Error active {column} → {block}: {e}")


def process(df_active, df_reactive, active_mapping, reactive_mapping):

    for df in [df_active, df_reactive]:
        df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%d %H:%M:%S')
        df['hour'] = df['timestamp'].dt.strftime('%H:%M:%S')

    now = datetime.utcnow().replace(second=0, microsecond=0)
    hora_str = now.strftime("%H:%M:%S")

    active_row = df_active[df_active["hour"] == hora_str]
    reactive_row = df_reactive[df_reactive["hour"] == hora_str]

    if not active_row.empty and not reactive_row.empty:
        active_values = active_row.iloc[0]
        reactive_values = reactive_row.iloc[0]

        for bloque, columna in active_mapping.items():
            set_parameter(active_values, bloque, columna, hora_str)

        for bloque, columna in reactive_mapping.items():
            set_parameter(reactive_values, bloque, columna, hora_str)
    else:
        print(f"[{hora_str}] Data not found for this hour.")



class HypersimSimulator:
    def __init__(self, design_path: str, devices: Dict):

        self.design_path = Path(design_path).absolute()
        self.devices: Dict = devices
        self.metrics_ref: Dict[str, pd.DataFrame] = {}

    def add_metric_reference(self, metric: str, df: pd.DataFrame) -> None:
        df["timestamp"] = pd.to_datetime(df["timestamp"], format="%Y-%m-%d %H:%M:%S")
        df["hour"] = df["timestamp"].dt.strftime("%H:%M:%S")
        self.metrics_ref.update({metric: df})


    def start(self) -> None:
        if not self.metrics_ref:
            raise ValueError("No metrics tables added to the simulation.")
        self._start_simulation()

    def stop(self) -> None:
        print("Stopping simulation ...")
        self.stop()
        print("Simulation stopped ...")

    def run_simulation_loop(self, df_active, df_reactive, active_mapping, reactive_mapping):

        last_hour = None

        try:
            while True:
                now_utc = datetime.utcnow().replace(second=0, microsecond=0)
                hour_str = now_utc.strftime('%H:%M:%S')

                if hour_str != last_hour:
                    process(df_active, df_reactive, active_mapping, reactive_mapping)
                    last_hour = hour_str

                now = datetime.utcnow()
                next_minute = (now + timedelta(minutes=1)).replace(second=0, microsecond=0)
                time.sleep(max(0.1, (next_minute - now).total_seconds()))

        except KeyboardInterrupt:
            print("Loop detenido por el usuario.")
            HyWorksApi.stopSim()
        except Exception as e:
            print(f"Error en el loop: {e}")

    def _start_simulation(self) -> None:
        print("Starting simulation ...")
        HyWorksApi.startAndConnectHypersim()
        HyWorksApi.openDesign(self.design_path)
        HyWorksApi.startSim()
        print("Simulation started ...")



def main():
    # argparse loader: single positional JSON config file
    parser = argparse.ArgumentParser(
        description="Run Hypersim simulation with config"
    )
    parser.add_argument(
        "--config-file",
        "-c",
        default="simulation-config.json",
        help="Path to JSON configuration file",
    )
    args = parser.parse_args()

    with open(args.config_file, "r") as config_file:
        config = json.load(config_file)


    active_power_df = pd.read_csv(
        config["input_files"]["active_power"], sep=",", encoding="utf-8"
    )
    reactive_power_df = pd.read_csv(
        config["input_files"]["reactive_power"], sep=",", encoding="utf-8"
    )
    simulator = HypersimSimulator(
        config["design_path"],
        config["devices"]
    )
    simulator.add_metric_reference("active_power", active_power_df)
    simulator.add_metric_reference("reactive_power", reactive_power_df)
    active_mapping = {v["active_power"]: device for device, v in config["devices"].items()}
    reactive_mapping = {v["reactive_power"]: device for device, v in config["devices"].items()}


    print("Active mapping (bloque -> columna):", active_mapping)
    print("Reactive mapping (bloque -> columna):", reactive_mapping)

    simulator.start()

    try:
        simulator.run_simulation_loop(active_power_df, reactive_power_df, active_mapping, reactive_mapping)
    except Exception as exc:
        print(f"Error starting simulation: {exc}")
        simulator.stop()
        sys.exit(1)

if __name__ == "__main__":
    main()
