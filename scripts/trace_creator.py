import json
import random
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from splight_lib.models import Asset, AssetRelationship, Attribute
from rich import print

attributes = {}
all_attributes = Attribute.list()
print(all_attributes[:10])
all_relationships = AssetRelationship.list()
priority = ["Grid", "Bus", "Line"]

# Agrupa los assets por kind
assets_by_kind = {}
for asset in Asset.list():
    assets_by_kind.setdefault(asset.kind.name, []).append(asset)
    attributes[asset.name] = [attr for attr in all_attributes if attr.asset == asset.id]

# Ordena y aplana los assets según la prioridad y luego el resto
assets = []
for kind in priority:
    if kind in assets_by_kind:
        assets.extend(assets_by_kind[kind])
for kind, group in assets_by_kind.items():
    if kind not in priority:
        assets.extend(group)

def _get_order():
    return [asset.name for asset in assets]

def _get_grid(asset: Asset) -> Asset | None:
    for rel in all_relationships:
        if rel.asset == asset.id and rel.name == "Grid":
            return rel.related_asset
    return None

def _get_assets_with_attribute(attribute_name: str) -> list[str]:
    return [
        asset_name
        for asset_name, attributes in attributes.items()
        if any(attribute.name == attribute_name for attribute in attributes)
    ]

def _get_asset_from_name(asset_name: str) -> Asset | None:
    for asset in assets:
        if asset.name == asset_name:
            return asset
    return None

def _get_headers():
    return "timestamp," + ",".join(_get_order())

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


def power_row(
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


def temperature_row(time: datetime, peak_temperature_per_inverter: int = 10):
    values = {"timestamp": time.strftime("%Y-%m-%d %H:%M:%S")}
    for asset in assets:
        if asset.kind.name == "Inverter":
            temp = _get_solar_gaussian_value(time, peak_temperature_per_inverter)
            values[asset.name] = str(temp)
    return ",".join([values["timestamp"]] + [values[name] for name in _get_order() if name in values])


def contingency_row(asset_names: list[str], timestamp: datetime):
    row = {"timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S")}
    row.update({name: json.dumps(False) for name in asset_names})
    return row


def frequency_row(asset_names: list[str], timestamp: datetime):
    row = {"timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S")}
    row.update({name: "50.0" for name in asset_names})
    return row


def switch_status_row(asset_names: list[str], timestamp: datetime):
    row = {"timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S")}
    row.update({name: json.dumps(False) for name in asset_names})
    return row


def voltage_row(asset_names: list[str], timestamp: datetime):
    row = {"timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S")}
    row.update({name: "350" for name in asset_names})
    return row


def current_row(asset_names: list[str], timestamp: datetime):
    row = {"timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S")}
    row.update({name: "300" for name in asset_names})
    return row


def get_voltage_start_and_end():
    start_date = datetime(2024, 1, 1, 0, 0, 0)
    asset_names = _get_assets_with_attribute("voltage_start")
    with (
        open("voltage_start.csv", "w") as voltage_start,
        open("voltage_end.csv", "w") as voltage_end,
    ):
        voltage_start.write(_get_headers() + "\n")
        voltage_end.write(_get_headers() + "\n")
        for _ in range(60 * 24):
            voltage_value = voltage_row(asset_names, start_date)
            voltage_start.write(voltage_value + "\n")
            voltage_end.write(voltage_value + "\n")
            start_date = start_date + timedelta(minutes=1)


def get_current_start_and_end():
    start_date = datetime(2024, 1, 1, 0, 0, 0)
    for phase in ["r", "s", "t"]:
        with (
            open(f"current_{phase}_start.csv", "w") as current_start,
            open(f"current_{phase}_end.csv", "w") as current_end,
        ):
            current_start.write(_get_headers() + "\n")
            current_end.write(_get_headers() + "\n")
            for _ in range(60 * 24):
                current_value = current_row(start_date)
                current_start.write(current_value + "\n")
                current_end.write(current_value + "\n")
                start_date = start_date + timedelta(minutes=1)


def get_active_power_and_power_set_point():
    start_date = datetime(2024, 1, 1, 0, 0, 0)
    with (
        open("active_power.csv", "w", newline="") as active_power_file,
        open("power_set_point.csv", "w", newline="") as power_set_point_file,
        open("active_power_start.csv", "w") as active_power_start,
    ):
        headers = _get_headers() + "\n"
        active_power_file.write(headers)
        power_set_point_file.write(headers)
        active_power_start.write(headers)

        for _ in range(60 * 24):
            power_value = power_row(start_date, peak_power_per_generator=10)
            active_power_file.write(power_value + "\n")
            active_power_start.write(power_value + "\n")
            # TODO: desync power set point from active power
            # active power is the generator response to the power set point
            power_set_point_file.write(power_value + "\n")
            start_date += timedelta(minutes=1)


def get_active_power_end():
    start_date = datetime(2024, 1, 1, 0, 0, 0)
    with open("active_power_end.csv", "w") as active_power_end:
        active_power_end.write(_get_headers() + "\n")
        for _ in range(60 * 24):
            end_power_value = power_row(
                start_date, peak_power_per_generator=10, power_end=True
            )
            active_power_end.write(end_power_value + "\n")
            start_date = start_date + timedelta(minutes=1)


def get_reactive_power():
    start_date = datetime(2024, 1, 1, 0, 0, 0)
    with (
        open("reactive_power.csv", "w") as reactive_power,
        open("reactive_power_start.csv", "w") as reactive_power_start,
    ):
        reactive_power.write(_get_headers() + "\n")
        reactive_power_start.write(_get_headers() + "\n")
        for _ in range(60 * 24):
            power_value = power_row(start_date, peak_power_per_generator=10 * 0.08)
            reactive_power.write(power_value + "\n")
            reactive_power_start.write(power_value + "\n")
            start_date = start_date + timedelta(minutes=1)


def get_reactive_power_end():
    start_date = datetime(2024, 1, 1, 0, 0, 0)
    asset_names = _get_assets_with_attribute("reactive_power")
    with open("reactive_power_end.csv", "w") as reactive_power_end:
        reactive_power_end.write(_get_headers() + "\n")
        for _ in range(60 * 24):
            end_power_value = power_row(
                start_date, peak_power_per_generator=10 * 0.08, power_end=True
            )
            reactive_power_end.write(end_power_value + "\n")
            start_date = start_date + timedelta(minutes=1)


def get_temperature():
    start_date = datetime(2024, 1, 1, 0, 0, 0)
    with open("temperature.csv", "w") as f:
        f.write(_get_headers() + "\n")
        for _ in range(60 * 24):
            f.write(temperature_row(start_date, peak_temperature_per_inverter=37) + "\n")
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
    asset_names = _get_assets_with_attribute("contingency")
    with open("contingency.csv", "w") as f:
        f.write(_get_headers() + "\n")
        for _ in range(60 * 24):
            row = contingency_row(asset_names, start_date)
            f.write(",".join([row["timestamp"]] + [row[name] for name in asset_names]) + "\n")
            start_date += timedelta(minutes=1)


def get_frequency():
    start_date = datetime(2024, 1, 1, 0, 0, 0)
    asset_names = _get_assets_with_attribute("frequency")
    with open("frequency.csv", "w") as f:
        f.write(_get_headers() + "\n")
        for _ in range(60 * 24):
            f.write(frequency_row(asset_names, start_date) + "\n")
            start_date = start_date + timedelta(minutes=1)


def get_switch_status():
    start_date = datetime(2024, 1, 1, 0, 0, 0)
    with open("switch_status.csv", "w") as f:
        f.write(_get_headers() + "\n")
        for _ in range(60 * 24):
            f.write(_get_switch_status(start_date) + "\n")
            start_date = start_date + timedelta(minutes=1)


def get_switch_status_start_and_end():
    start_date = datetime(2024, 1, 1, 0, 0, 0)
    with (
        open("switch_status_start.csv", "w") as switch_status_start,
        open("switch_status_end.csv", "w") as switch_status_end,
    ):
        switch_status_start.write(_get_headers() + "\n")
        switch_status_end.write(_get_headers() + "\n")
        for _ in range(60 * 24):
            switch_status = _get_switch_status(start_date)
            switch_status_start.write(switch_status + "\n")
            switch_status_end.write(switch_status + "\n")
            start_date = start_date + timedelta(minutes=1)


def get_available_active_power():
    start_date = datetime(2024, 1, 1, 0, 0, 0)
    with open("available_active_power.csv", "w") as f:
        f.write(_get_headers() + "\n")
        for _ in range(60 * 24):
            f.write(power_row(start_date, peak_power_per_generator=20) + "\n")
            start_date = start_date + timedelta(minutes=1)


def get_traces_json():
    traces = []
    for asset_name in _get_order():
        asset = _get_asset_from_name(asset_name)
        for attribute in attributes[asset_name]:
            if attribute.origin.value != "Input":
                continue
            noise_factor = (
                0.02 if attribute.type.value == "Number" else None
            )
            grid = _get_grid(asset)
            if not grid:
                continue
            traces.append(
                {
                    "name": f"{grid.name}/{asset_name}/{attribute.name}",
                    "topic": f"{grid.name}/{asset_name}/{attribute.name}",
                    "filename": f"{attribute.name}.csv",
                    "noise_factor": noise_factor,
                    "match_timestamp_by": "hour",
                    "target_value": f"{asset_name}",
                },
            )

    traces_json = {"traces": traces}
    with open("traces.json", "w") as f:
        json.dump(
            traces_json,
            f,
        )


if __name__ == "__main__":
    get_contingency()
    get_traces_json()