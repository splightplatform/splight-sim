import os
import sys
import time
import pandas as pd
from datetime import datetime

sys.path.append(r'C:\OPAL-RT\HYPERSIM\hypersim_2024.3.0.o30\Windows\HyApi\python')
import HyWorksApiGRPC as HyWorksApi

def set_parameter(value, block, column, hour_str):
    try:
        value = float(value[column])
        HyWorksApi.setComponentParameter(block, 'A', str(value))
        print(f"[{hour_str}] Active: {column} → {block}.A = {value}")
    except Exception as e:
        print(f"[{hour_str}] Error active {column} → {block}: {e}")



def process(df_active, df_reactive, active_mapping, reactive_mapping):
    now = datetime.utcnow().replace(second=0, microsecond=0)
    hora_str = now.strftime('%H:%M:%S')

    active_row = df_active[df_active['hour'] == hora_str]
    reactive_row = df_reactive[df_reactive['hour'] == hora_str]

    if not active_row.empty and not reactive_row.empty:
        valores_activa = active_row.iloc[0]
        valores_reactiva = reactive_row.iloc[0]

        for bloque, columna in active_mapping.items():
            set_parameter(valores_activa, bloque, columna, hora_str)

        for bloque, columna in reactive_mapping.items():
            set_parameter(valores_reactiva, bloque, columna, hora_str)
    else:
        print(f"[{hora_str}] Data not found for this hour.")



def main():

    HyWorksApi.startAndConnectHypersim()
    design_path = "C:\\Users\\lucas\\OneDrive\\Documentos\\HYPERSIM\\Black Box\\Python\\CambioDePgen1.ecf"
    HyWorksApi.openDesign(design_path)
    HyWorksApi.startSim()
    print("Simulation started...")

    active_path = "C:\\Users\\lucas\\OneDrive\\Documentos\\HYPERSIM\\Black Box\\Python\\active_power.csv"
    reactive_path = "C:\\Users\\lucas\\OneDrive\\Documentos\\HYPERSIM\\Black Box\\Python\\reactive_power.csv"

    df_active = pd.read_csv(active_path, sep=',', encoding='utf-8')
    df_reactive = pd.read_csv(reactive_path, sep=',', encoding='utf-8')

    for df in [df_active, df_reactive]:
        df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%d %H:%M:%S')
        df['hour'] = df['timestamp'].dt.strftime('%H:%M:%S')

    active_mapping = {
        "P1": "PECalama",
        "P2": "PEValleDeLosVientos",
        "P3": "PFVAzabache",
        "P4": "PFVJama",
        "P5": "PFVSanPedro",
        "P6": "PFVUsya"
    }

    reactive_mapping = {
        "Q1": "PECalama",
        "Q2": "PEValleDeLosVientos",
        "Q3": "PFVAzabache",
        "Q4": "PFVJama",
        "Q5": "PFVSanPedro",
        "Q6": "PFVUsya"
    }

    try:
        while True:
            process(df_active, df_reactive, active_mapping, reactive_mapping)
            time.sleep(60)

    except KeyboardInterrupt:
        print("\n Ctrl+C detected. Stopping simulation...")
        HyWorksApi.stopSim()
        print(" Simulation stopped and HYPERSIM closed successfully.")


if __name__ == "__main__":
    main()
