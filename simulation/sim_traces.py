import os
import sys
import time
import json
import argparse
from datetime import datetime
from typing import Dict

import pandas as pd

# sys.path.append(r"C:\OPAL-RT\HYPERSIM\hypersim_2024.3.0.o30\Windows\HyApi\python")
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
    now = datetime.utcnow().replace(second=0, microsecond=0)
    hora_str = now.strftime("%H:%M:%S")

    active_row = df_active[df_active["hour"] == hora_str]
    reactive_row = df_reactive[df_reactive["hour"] == hora_str]

    if not active_row.empty and not reactive_row.empty:
        valores_activa = active_row.iloc[0]
        valores_reactiva = reactive_row.iloc[0]

        for bloque, columna in active_mapping.items():
            set_parameter(valores_activa, bloque, columna, hora_str)

        for bloque, columna in reactive_mapping.items():
            set_parameter(valores_reactiva, bloque, columna, hora_str)
    else:
        print(f"[{hora_str}] Data not found for this hour.")



class HypersimSimulator:
    def __init__(self, config_path: str):

        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        self.design_path: str = config["design_path"]
        self.devices: Dict = config["devices"]
        self.metrics_ref: Dict[str, pd.DataFrame] = {}

        for metric_name, csv_path in config["input_files"].items():
            df = pd.read_csv(csv_path)
            self.add_metric_reference(metric_name, df)

    def add_metric_reference(self, metric: str, df: pd.DataFrame) -> None:
        self.metrics_ref.update({metric: df})

    def add_device(
        self, device_name: str, device_metric: Dict[str, str]
    ) -> None:
        if device_name in self.devices:
            raise ValueError(f"Device {device_name} already exists.")
        self.devices.update({device_name: device_metric})

    def start(self) -> None:
        if not self.metrics_ref:
            raise ValueError("No metrics tables added to the simulation.")
        self._start_simulation()

    def stop(self) -> None:
        print("Stopping simulation ...")
        HyWorksApi.stopSim()
        print("Simulation stopped ...")

    def set_parameter(value, block, column, hour_str):
    try:
        value = float(value[column])
        HyWorksApi.setComponentParameter(block, 'A', str(value))
        print(f"[{hour_str}] Active: {column} → {block}.A = {value}")
    except Exception as e:
        print(f"[{hour_str}] Error active {column} → {block}: {e}")

    def run_simulation_loop(config_path):
      
        with open(config_path, "r") as f:
            config = json.load(f)

        devices = config["devices"]

        active_df = pd.read_csv(config["input_files"]["active_power"])
        reactive_df = pd.read_csv(config["input_files"]["reactive_power"])

        for i in range(len(active_df)):
            hour_str = datetime.now().strftime("%H:%M:%S")

            for device_name, mapping in devices.items():
              
                set_parameter(
                    active_df.iloc[i],        
                    mapping["active_power"],   
                    mapping["active_power"],   
                    hour_str
                )

                set_parameter(
                    reactive_df.iloc[i],       
                    mapping["reactive_power"], 
                    mapping["reactive_power"], 
                    hour_str
                )

            time.sleep(1)

        print("Simulación finalizada.")
        

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
        help="Path to JSON configuration file",
    )
    args = parser.parse_args()

    with open(args.config_file, "r", encoding="utf-8") as config_file:
        config = json.load(config_file)

    active_power_df = pd.read_csv(
        config["input_files"]["active_power"], sep=",", encoding="utf-8"
    )
    reactive_power_df = pd.read_csv(
        config["input_files"]["reactive_power"], sep=",", encoding="utf-8"
    )
    simulator = HypersimSimulator(
        config["desing_path"],
    )
    simulator.add_metric_reference("active_power", active_power_df)
    simulator.add_metric_reference("reactive_power", reactive_power_df)
    for device_name, metrics in config["devices"].items():
        simulator.add_device(device_name, metrics)

    simulator.start()

    try:
        simulator.run_simulation_loop()
    except Exception as exc:
        print(f"Error starting simulation: {exc}")
        simulator.stop()
        sys.exit(1)

    # for df in [df_active, df_reactive]:
    #     df["timestamp"] = pd.to_datetime(
    #         df["timestamp"], format="%Y-%m-%d %H:%M:%S"
    #     )
    #     df["hour"] = df["timestamp"].dt.strftime("%H:%M:%S")

    # active_mapping = {
    #     "P1": "PECalama",
    #     "P2": "PEValleDeLosVientos",
    #     "P3": "PFVAzabache",
    #     "P4": "PFVJama",
    #     "P5": "PFVSanPedro",
    #     "P6": "PFVUsya",
    # }
    #
    # reactive_mapping = {
    #     "Q1": "PECalama",
    #     "Q2": "PEValleDeLosVientos",
    #     "Q3": "PFVAzabache",
    #     "Q4": "PFVJama",
    #     "Q5": "PFVSanPedro",
    #     "Q6": "PFVUsya",
    # }

    # try:
    #     while True:
    #         process(df_active, df_reactive, active_mapping, reactive_mapping)
    #         time.sleep(60)
    #
    # except KeyboardInterrupt:
    #     print("\n Ctrl+C detected. Stopping simulation...")
    #     HyWorksApi.stopSim()
    #     print(" Simulation stopped and HYPERSIM closed successfully.")


if __name__ == "__main__":
    main()
