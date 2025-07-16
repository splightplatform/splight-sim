import os
import sys
import time
import pandas as pd
from datetime import datetime

# Path to the HYPERSIM API
sys.path.append(r'C:\OPAL-RT\HYPERSIM\hypersim_2024.3.0.o30\Windows\HyApi\python')
import HyWorksApiGRPC as HyWorksApi

# Connect to HYPERSIM and open the design
HyWorksApi.startAndConnectHypersim()
designPath = os.path.join(os.getcwd(), 'CambioDePgen1.ecf')
HyWorksApi.openDesign(designPath)
HyWorksApi.startSim()
print("🔄 Simulation started...")

# Read CSV files
active_path = os.path.join(os.getcwd(), 'active_power.csv')
reactive_path = os.path.join(os.getcwd(), 'reactive_power.csv')

df_active = pd.read_csv(active_path, sep=',', encoding='utf-8')
df_reactive = pd.read_csv(reactive_path, sep=',', encoding='utf-8')

# Convert timestamp to hour only
for df in [df_active, df_reactive]:
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%d %H:%M:%S')
    df['hora'] = df['timestamp'].dt.strftime('%H:%M:%S')

# Mappings
mapeo_activa = {
    'P1': 'PECalama',
    'P2': 'PEValleDeLosVientos',
    'P3': 'PFVAzabache',
    'P4': 'PFVJama',
    'P5': 'PFVSanPedro',
    'P6': 'PFVUsya'
}

mapeo_reactiva = {
    'Q1': 'PECalama',
    'Q2': 'PEValleDeLosVientos',
    'Q3': 'PFVAzabache',
    'Q4': 'PFVJama',
    'Q5': 'PFVSanPedro',
    'Q6': 'PFVUsya'
}

try:
    while True:
        ahora = datetime.utcnow().replace(second=0, microsecond=0)
        hora_str = ahora.strftime('%H:%M:%S')

        fila_activa = df_active[df_active['hora'] == hora_str]
        fila_reactiva = df_reactive[df_reactive['hora'] == hora_str]

        if not fila_activa.empty and not fila_reactiva.empty:
            valores_activa = fila_activa.iloc[0]
            valores_reactiva = fila_reactiva.iloc[0]

            for bloque, columna in mapeo_activa.items():
                try:
                    valor = float(valores_activa[columna])
                    HyWorksApi.setComponentParameter(bloque, 'A', str(valor))
                    print(f"[{hora_str}] ✅ Active: {columna} → {bloque}.A = {valor}")
                except Exception as e:
                    print(f"[{hora_str}] ⚠️ Error active {columna} → {bloque}: {e}")

            for bloque, columna in mapeo_reactiva.items():
                try:
                    valor = float(valores_reactiva[columna])
                    HyWorksApi.setComponentParameter(bloque, 'A', str(valor))
                    print(f"[{hora_str}] ✅ Reactive: {columna} → {bloque}.A = {valor}")
                except Exception as e:
                    print(f"[{hora_str}] ⚠️ Error reactive {columna} → {bloque}: {e}")
        else:
            print(f"[{hora_str}] ⏳ Data not found for this hour.")

        time.sleep(60)

except KeyboardInterrupt:
    print("\n🛑 Ctrl+C detected. Stopping simulation...")
    HyWorksApi.stopSim()
    print("✅ Simulation stopped and HYPERSIM closed successfully.")
