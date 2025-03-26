import json
import random
from datetime import datetime, timedelta
import os
import numpy as np
import pandas as pd


def _get_solar_gaussian_value(
    time: datetime, max_value: int = 5, sigma: int = 2, mu: int = 14
):
    x = time.hour + (time.minute / 60)
    # mu = Mean ("center" of the curve)
    # sigma = Standard deviation (spread or "width" of the curve)
    # Amplitude (height of the curve)
    amplitude = max_value * np.sqrt(2 * np.pi * sigma**2)
    return round(
        amplitude
        * (1 / np.sqrt(2 * np.pi * sigma**2))
        * np.exp(-((x - mu) ** 2) / (2 * sigma**2)),
        3,
    )


def _get_noise(max_value: int = 1):
    return max_value * random.random()


def _get_order():
    return [
        "timestamp",
        "jama0",
        "jama1",
        "jama",
        "sanpedro",
        "vlv",
        "usy",
        "cal",
        "aza",
        "jamLas",
        "lasCal",
        "vlvCal",
        "calChu",
        "calSal",
        "salChu",
        "calNch",
        "nchChu",
    ]


def _get_power(
    time: datetime, peak_power_per_generator: int = 10, power_end: bool = False
):
    # power_end modifier that inverts the value adding a loss
    power_factor = -0.93 if power_end else 1

    delta_vlv = -1.4
    delta_aza = 1.3
    delta_cal = 1.7
    delta_usy = -1.6
    delta_sanpedro = 0
    sanpedro = _get_solar_gaussian_value(
        time, peak_power_per_generator + delta_sanpedro
    )
    aza = _get_solar_gaussian_value(time, peak_power_per_generator + delta_aza, sigma=3)
    usy = _get_solar_gaussian_value(
        time, peak_power_per_generator + delta_usy, sigma=2.5
    )
    jama1 = _get_solar_gaussian_value(time, peak_power_per_generator * 2 / 3)
    jama0 = _get_solar_gaussian_value(time, peak_power_per_generator / 3)
    jama = jama1 + jama0

    jamLas = jama1 + jama0 - _get_noise(peak_power_per_generator * 0.1)
    lasCal = jamLas + sanpedro - _get_noise(peak_power_per_generator * 0.1)

    vlv = (
        peak_power_per_generator
        + delta_vlv
        - _get_noise((peak_power_per_generator + delta_vlv) * 0.1)
    )
    vlvCal = vlv - _get_noise((peak_power_per_generator + delta_vlv) * 0.1)

    cal = (
        peak_power_per_generator
        + delta_cal
        - _get_noise((peak_power_per_generator + delta_cal) * 0.1)
    )

    calChu = lasCal + vlvCal + usy + aza + cal
    calSal = (calChu / 2) - _get_noise(peak_power_per_generator * 0.1)
    salChu = calSal - _get_noise(peak_power_per_generator * 0.1)
    calNch = (calChu / 2) - _get_noise(peak_power_per_generator * 0.1)
    nchChu = calNch - _get_noise(peak_power_per_generator * 0.1)

    values = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "jama0": str(max(round(jama0, 3), 0) * power_factor),
        "jama1": str(max(round(jama1, 3), 0) * power_factor),
        "jama": str(max(round(jama, 3), 0) * power_factor),
        "sanpedro": str(max(round(sanpedro, 3), 0) * power_factor),
        "jamLas": str(max(round(jamLas, 3), 0) * power_factor),
        "lasCal": str(max(round(lasCal, 3), 0) * power_factor),
        "vlv": str(max(round(vlv, 3), 0) * power_factor),
        "vlvCal": str(max(round(vlvCal, 3), 0) * power_factor),
        "usy": str(max(round(usy, 3), 0) * power_factor),
        "cal": str(max(round(cal, 3), 0) * power_factor),
        "aza": str(max(round(aza, 3), 0) * power_factor),
        "calChu": str(max(round(calChu, 3), 0) * power_factor),
        "calSal": str(max(round(calSal, 3), 0) * power_factor),
        "salChu": str(max(round(salChu, 3), 0) * power_factor),
        "calNch": str(max(round(calNch, 3), 0) * power_factor),
        "nchChu": str(max(round(nchChu, 3), 0) * power_factor),
    }
    # Avoid -0.0 values
    for key, value in values.items():
        if value == "-0.0":
            values[key] = "0.0"
    return ",".join([values[order] for order in _get_order()])


def _get_temperature(time: datetime, peak_temperature_per_inverter: int = 10):
    jama0 = _get_solar_gaussian_value(time, peak_temperature_per_inverter)
    jama1 = _get_solar_gaussian_value(time, peak_temperature_per_inverter)

    values = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "jama0": str(jama0),
        "jama1": str(jama1),
        "jama": str(0),
        "sanpedro": str(0),
        "jamLas": str(0),
        "lasCal": str(0),
        "vlv": str(0),
        "vlvCal": str(0),
        "usy": str(0),
        "cal": str(0),
        "aza": str(0),
        "calChu": str(0),
        "calSal": str(0),
        "salChu": str(0),
        "calNch": str(0),
        "nchChu": str(0),
    }
    return ",".join([values[order] for order in _get_order()])


def _get_contingency(time: datetime):

    values = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "jama0": json.dumps(False),
        "jama1": json.dumps(False),
        "jama": json.dumps(False),
        "sanpedro": json.dumps(False),
        "jamLas": json.dumps(False),
        "lasCal": json.dumps(False),
        "vlv": json.dumps(False),
        "vlvCal": json.dumps(False),
        "usy": json.dumps(False),
        "cal": json.dumps(False),
        "aza": json.dumps(False),
        "calChu": json.dumps(False),
        "calSal": json.dumps(False),
        "salChu": json.dumps(False),
        "calNch": json.dumps(False),
        "nchChu": json.dumps(False),
    }
    return ",".join([values[order] for order in _get_order()])


def _get_frequency(time: datetime):
    # 50Hz for all generators
    values = {
        key: "50" if key != "timestamp" else time.strftime("%Y-%m-%d %H:%M:%S")
        for key in _get_order()
    }
    return ",".join([values[order] for order in _get_order()])


def _get_switch_status(time: datetime):
    # All switches are closed
    values = {
        key: (
            json.dumps(True)
            if key != "timestamp"
            else time.strftime("%Y-%m-%d %H:%M:%S")
        )
        for key in _get_order()
    }
    return ",".join([values[order] for order in _get_order()])


def _get_available_active_power(time: datetime):
    # All generators with 25MW available
    values = {
        key: "25" if key != "timestamp" else time.strftime("%Y-%m-%d %H:%M:%S")
        for key in _get_order()
    }
    return ",".join([values[order] for order in _get_order()])


def get_headers():
    values = {
        "timestamp": "timestamp",
        "jama0": "PFVJama-0",
        "jama1": "PFVJama-1",
        "jama": "PFVJama",
        "sanpedro": "PFVSanPedro",
        "vlv": "PEValleDeLosVientos",
        "usy": "PFVUsya",
        "cal": "PECalama",
        "aza": "PFVAzabache",
        "jamLas": "JAM-LAS",
        "lasCal": "LAS-CAL",
        "vlvCal": "VLV-CAL",
        "calChu": "CAL-CHU",
        "calSal": "CAL-SAL",
        "salChu": "SAL-CHU",
        "calNch": "CAL-NCH",
        "nchChu": "NCH-CHU",
    }
    return ",".join([values[order] for order in _get_order()])


def get_active_power_and_power_set_point():
    start_date = datetime(2024, 1, 1, 0, 0, 0)
    with open("active_power.csv", "w", newline="") as active_power_file, open(
        "power_set_point.csv", "w", newline=""
    ) as power_set_point_file:
        headers = get_headers() + "\n"
        active_power_file.write(headers)
        power_set_point_file.write(headers)

        for _ in range(60 * 24):
            power_value = _get_power(start_date, peak_power_per_generator=10)
            active_power_file.write(power_value + "\n")
            # TODO: desync power set point from active power
            # active power is the generator response to the power set point
            power_set_point_file.write(power_value + "\n")
            start_date += timedelta(minutes=1)


def get_active_power_end():
    start_date = datetime(2024, 1, 1, 0, 0, 0)
    with open("active_power_end.csv", "w") as f:
        f.write(get_headers() + "\n")
        for _ in range(60 * 24):
            f.write(
                _get_power(start_date, peak_power_per_generator=10, power_end=True)
                + "\n"
            )
            start_date = start_date + timedelta(minutes=1)


def get_reactive_power():
    start_date = datetime(2024, 1, 1, 0, 0, 0)
    with open("reactive_power.csv", "w") as f:
        f.write(get_headers() + "\n")
        for _ in range(60 * 24):
            f.write(_get_power(start_date, peak_power_per_generator=10 * 0.08) + "\n")
            start_date = start_date + timedelta(minutes=1)


def get_temperature():
    start_date = datetime(2024, 1, 1, 0, 0, 0)
    with open("temperature.csv", "w") as f:
        f.write(get_headers() + "\n")
        for _ in range(60 * 24):
            f.write(
                _get_temperature(start_date, peak_temperature_per_inverter=37) + "\n"
            )
            start_date = start_date + timedelta(minutes=1)


def get_raw_daily_energy():
    df = pd.read_csv("active_power.csv")
    timestamp = df["timestamp"]
    df = df.drop(columns=["timestamp"], axis=1)
    df = df.shift(-1) - df
    df[df < 0] = 0
    df = df * 60
    df = df.cumsum()
    df = df.round(2)
    for col in df.columns:
        if col not in ["PFVJama-0", "PFVJama-1", "PFVJama"]:
            df[col] = 0
    col_order = ["timestamp"] + list(df.columns)
    df["timestamp"] = timestamp
    df = df[col_order]
    df.to_csv("raw_daily_energy.csv", index=False)


def get_contingency():
    start_date = datetime(2024, 1, 1, 0, 0, 0)
    with open("contingency.csv", "w") as f:
        f.write(get_headers() + "\n")
        for _ in range(60 * 24):
            f.write(_get_contingency(start_date) + "\n")
            start_date = start_date + timedelta(minutes=1)


def get_frequency():
    start_date = datetime(2024, 1, 1, 0, 0, 0)
    with open("frequency.csv", "w") as f:
        f.write(get_headers() + "\n")
        for _ in range(60 * 24):
            f.write(_get_frequency(start_date) + "\n")
            start_date = start_date + timedelta(minutes=1)


def get_switch_status():
    start_date = datetime(2024, 1, 1, 0, 0, 0)
    with open("switch_status.csv", "w") as f:
        f.write(get_headers() + "\n")
        for _ in range(60 * 24):
            f.write(_get_switch_status(start_date) + "\n")
            start_date = start_date + timedelta(minutes=1)


def get_available_active_power():
    start_date = datetime(2024, 1, 1, 0, 0, 0)
    with open("available_active_power.csv", "w") as f:
        f.write(get_headers() + "\n")
        for _ in range(60 * 24):
            f.write(_get_available_active_power(start_date) + "\n")
            start_date = start_date + timedelta(minutes=1)


def get_traces_json():
    traces = []
    for asset in get_headers().split(",")[1:]:
        for attribute in [
            "active_power",
            "active_power_end",
            "reactive_power",
            "temperature",
            "raw_daily_energy",
            "power_set_point",
        ]:
            traces.append(
                {
                    "name": f"Calama/{asset}/{attribute}",
                    "topic": f"Calama/{asset}/{attribute}",
                    "filename": f"{attribute}.csv",
                    "noise_factor": 0.01,
                    "match_timestamp_by": "hour",
                    "target_value": f"{asset}",
                },
            )
        for attribute in [
            "contingency",
            "frequency",
            "switch_status",
            "available_active_power",
        ]:
            traces.append(
                {
                    "name": f"Calama/{asset}/{attribute}",
                    "topic": f"Calama/{asset}/{attribute}",
                    "filename": f"{attribute}.csv",
                    "noise_factor": None,
                    "match_timestamp_by": "hour",
                    "target_value": f"{asset}",
                },
            )
    traces_json = {"traces": traces}
    with open("traces.json", "w") as f:
        json.dump(
            traces_json,
            f,
        )


if __name__ == "__main__":
    get_active_power_and_power_set_point()
    get_active_power_end()
    get_reactive_power()
    get_temperature()
    get_raw_daily_energy()
    get_contingency()
    get_frequency()
    get_switch_status()
    get_available_active_power()
    get_traces_json()
