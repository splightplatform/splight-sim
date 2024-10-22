import json
import random
from datetime import datetime, timedelta

import numpy as np


def _get_solar_gaussian_value(time: datetime, max_value: int = 5):
    x = time.hour + (time.minute / 60)
    # Mean ("center" of the curve)
    mu = 14
    # Standard deviation (spread or "width" of the curve)
    sigma = 2
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


def _get_power(time: datetime, peak_power_per_generator: int = 10):
    delta_vlv = -5
    delta_aza = 1
    delta_cal = 6
    delta_usy = -2
    jama1 = _get_solar_gaussian_value(time, peak_power_per_generator * 2 / 3)
    jama0 = _get_solar_gaussian_value(time, peak_power_per_generator / 3)
    jama = jama1 + jama0

    sanpedro = peak_power_per_generator - \
        _get_noise(peak_power_per_generator * 0.1)
    jamLas = jama1 + jama0 - _get_noise(peak_power_per_generator * 0.1)
    lasCal = jamLas - _get_noise(peak_power_per_generator * 0.1)

    vlv = peak_power_per_generator + delta_vlv - \
        _get_noise((peak_power_per_generator + delta_vlv) * 0.1)
    vlvCal = vlv - _get_noise((peak_power_per_generator + delta_vlv) * 0.1)

    usy = peak_power_per_generator + delta_usy - \
        _get_noise((peak_power_per_generator + delta_usy) * 0.1)

    cal = peak_power_per_generator + delta_cal - \
        _get_noise((peak_power_per_generator + delta_cal) * 0.1)

    aza = peak_power_per_generator + delta_aza - \
        _get_noise((peak_power_per_generator + delta_aza) * 0.1)

    calChu = lasCal + vlvCal + usy + aza + cal
    calSal = (calChu / 2) - _get_noise(peak_power_per_generator * 0.1)
    salChu = calSal - _get_noise(peak_power_per_generator * 0.1)
    calNch = (calChu / 2) - _get_noise(peak_power_per_generator * 0.1)
    nchChu = calNch - _get_noise(peak_power_per_generator * 0.1)

    values = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "jama0": str(round(max(jama0, 0), 3)),
        "jama1": str(round(max(jama1, 0), 3)),
        "jama": str(round(max(jama, 0), 3)),
        "sanpedro": str(round(max(sanpedro, 0), 3)),
        "jamLas": str(round(max(jamLas, 0), 3)),
        "lasCal": str(round(max(lasCal, 0), 3)),
        "vlv": str(round(max(vlv, 0), 3)),
        "vlvCal": str(round(max(vlvCal, 0), 3)),
        "usy": str(round(max(usy, 0), 3)),
        "cal": str(round(max(cal, 0), 3)),
        "aza": str(round(max(aza, 0), 3)),
        "calChu": str(round(max(calChu, 0), 3)),
        "calSal": str(round(max(calSal, 0), 3)),
        "salChu": str(round(max(salChu, 0), 3)),
        "calNch": str(round(max(calNch, 0), 3)),
        "nchChu": str(round(max(nchChu, 0), 3)),
    }
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


def get_headers():
    values = {
        "timestamp": "timestamp",
        "jama0": "PFVJama-0",
        "jama1": "PFVJama-1",
        "jama": "PFVJama",
        "sanpedro": "PFVSanPedro",
        "vlv": "PEValleDelosVientos",
        "usy": "PFVUsya",
        "cal": "PFVCal",
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


def get_active_power(time: datetime):
    return _get_power(time, peak_power_per_generator=10)


def get_reactive_power(time: datetime):
    return _get_power(time, peak_power_per_generator=2)


def get_temperature(time: datetime):
    return _get_temperature(time, peak_temperature_per_inverter=37)


def get_traces_json():
    traces = []
    for asset in get_headers().split(",")[1:]:
        for power_type in ["active_power", "reactive_power", "temperature"]:
            traces.append(
                {
                    "name": f"Calama/{asset}/{power_type}",
                    "topic": f"Calama/{asset}/{power_type}",
                    "filename": f"{power_type}.csv",
                    "noise_factor": 0.01,
                    "match_timestamp_by": "hour",
                    "target_value": f"{asset}",
                },
            )
    return {"traces": traces}


start_date = datetime(2024, 1, 1, 0, 0, 0)
with open("active_power.csv", "w") as f:
    f.write(get_headers() + "\n")
    for i in range(60 * 24):
        f.write(get_active_power(start_date) + "\n")
        start_date = start_date + timedelta(minutes=1)
start_date = datetime(2024, 1, 1, 0, 0, 0)
with open("reactive_power.csv", "w") as f:
    f.write(get_headers() + "\n")
    for i in range(60 * 24):
        f.write(get_reactive_power(start_date) + "\n")
        start_date = start_date + timedelta(minutes=1)
start_date = datetime(2024, 1, 1, 0, 0, 0)
with open("temperature.csv", "w") as f:
    f.write(get_headers() + "\n")
    for i in range(60 * 24):
        f.write(get_temperature(start_date) + "\n")
        start_date = start_date + timedelta(minutes=1)
with open("traces.json", "w") as f:
    json.dump(
        get_traces_json(),
        f,
    )
