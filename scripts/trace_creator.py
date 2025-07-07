import json
import random
from datetime import datetime, timedelta
from typing import Any, Callable, Sequence

import numpy as np
from splight_lib.models import Asset

KIND_INPUT_ATTRIBUTES: dict[str, list[str]] = {
    "Battery": ["active_power", "reactive_power", "state_of_charge"],
    "Bus": ["active_power", "reactive_power"],
    "ExternalGrid": [],
    "Generator": [
        "active_power",
        "available_active_power",
        "frequency",
        "power_set_point",
        "reactive_power",
        "switch_status",
    ],
    "Grid": [],
    "Line": [
        "active_power_end",
        "active_power_start",
        "contingency",
        "current_r_end",
        "current_r_start",
        "current_s_end",
        "current_s_start",
        "current_t_end",
        "current_t_start",
        "reactive_power_end",
        "reactive_power_start",
        "switch_status_end",
        "switch_status_start",
        "voltage_end",
        "voltage_start",
    ],
    "Load": ["active_power", "reactive_power", "switch_status"],
    "Segment": [],
    "SlackLine": [],
    "Transformer": [
        "active_power_end",
        "active_power_start",
        "active_power_loss",
        "contingency",
        "reactive_power_end",
        "reactive_power_loss",
        "reactive_power_start",
        "switch_status_end",
        "switch_status_start",
        "voltage_end",
        "voltage_start",
    ],
}

ALL_ASSETS = Asset.list()
START_DATE = datetime(2024, 1, 1)


class GenerationTask:
    def __init__(
        self,
        filename: str,
        asset_attr: str,
        row_fn: Callable[[list[str], datetime], str],
    ):
        self.filename = filename
        self.asset_attr = asset_attr
        self.row_fn = row_fn


def generic_row(
    asset_names: Sequence[str],
    timestamp: datetime,
    values: dict[str, Any],
    default: Any,
) -> str:
    sorted_names = sorted(asset_names)
    row = {}
    for n in sorted_names:
        raw = values.get(n, default)
        if isinstance(raw, float):
            raw = round(raw, 3)
        row[n] = str(raw)
        if row[n] == "-0.0":
            row[n] = "0.0"
        if isinstance(raw, bool):
            row[n] = row[n].lower()

    cells = [timestamp.strftime("%Y-%m-%d %H:%M:%S")] + [row[n] for n in sorted_names]
    return ",".join(cells) + "\n"


def solar_gaussian(
    time: datetime, max_value: float = 5, sigma: float = 2, mu: float = 14
) -> float:
    x = time.hour + time.minute / 60
    coef = 1 / (np.sqrt(2 * np.pi) * sigma)
    exponent = -((x - mu) ** 2) / (2 * sigma**2)
    amplitude = max_value * np.sqrt(2 * np.pi * sigma**2)
    return round(amplitude * coef * np.exp(exponent), 3)


def sinusoidal_component(time, amplitude, base_offset):
    time_fraction = (time.hour + time.minute / 60) / 24
    sine_value = amplitude * np.sin(2 * np.pi * time_fraction)
    return sine_value + base_offset


def bess_active_power(
    time: datetime, max_power: float = 5.0, peak_hours: list[float] = [6, 18]
) -> float:
    hours = time.hour + time.minute / 60
    cycles_per_day = len(peak_hours)
    first_peak = peak_hours[0]

    frequency = cycles_per_day / 24
    phase_shift = (np.pi / 2) - (2 * np.pi * frequency * first_peak)

    soc_change_rate = (
        50 * 2 * np.pi * frequency * np.cos(2 * np.pi * frequency * hours + phase_shift)
    )

    max_soc_rate = 50 * 2 * np.pi * frequency
    active_power = -(soc_change_rate / max_soc_rate) * max_power

    return round(active_power, 3)


def bess_soc(time: datetime, peak_hours: list[float] = [6, 18]) -> float:
    hours = time.hour + time.minute / 60
    cycles_per_day = len(peak_hours)
    first_peak = peak_hours[0]
    frequency = cycles_per_day / 24
    phase_shift = (np.pi / 2) - (2 * np.pi * frequency * first_peak)

    soc = 50 + 50 * np.sin(2 * np.pi * frequency * hours + phase_shift)

    # Keep between 0-100%
    soc = max(0, min(100, soc))
    return round(soc, 2)


def noise(scale: float = 1) -> float:
    return random.random() * scale


def compute_power_values(
    time: datetime, peak_power: float, end: bool = False
) -> dict[str, float]:
    peak_power *= -0.93 if end else 1
    delta_vlv = -1.4
    delta_aza = 1.3
    delta_cal = 1.7
    delta_usy = -1.6
    delta_melena = 2.1

    # Calama Grid
    # PFVs
    pfv_jama = solar_gaussian(time, peak_power)
    pfv_sanpedro = solar_gaussian(time, peak_power)
    pfv_azabache = solar_gaussian(time, peak_power + delta_aza, sigma=3)
    pfv_usya = solar_gaussian(time, peak_power + delta_usy, sigma=2.5)

    # PEs
    pe_vlv = peak_power + delta_vlv - noise((peak_power + delta_vlv) * 0.1)
    pe_calama = peak_power + delta_cal - noise((peak_power + delta_cal) * 0.1)

    # Lines
    jam_las = pfv_jama - noise(peak_power * 0.1)
    las_cal = jam_las + pfv_sanpedro - noise(peak_power * 0.1)
    vlv_cal = pe_vlv - noise((peak_power + delta_vlv) * 0.1)
    total_cal_chu = las_cal + vlv_cal + pfv_usya + pfv_azabache + pe_calama
    cal_sal = total_cal_chu / 2 - noise(peak_power * 0.1)
    sal_chu = cal_sal - noise(peak_power * 0.1)
    cal_nch = total_cal_chu / 2 - noise(peak_power * 0.1)
    nch_chu = cal_nch - noise(peak_power * 0.1)

    # Buses
    se_vlv = pe_vlv - noise((peak_power + delta_vlv) * 0.1)
    se_jam = jam_las
    se_las = las_cal
    se_cal = pfv_usya + pfv_azabache + pe_calama + las_cal - noise(peak_power * 2 * 0.1)
    se_sal = se_cal
    se_nchu = se_cal
    se_chu = se_sal + se_nchu

    # Marcona Grid
    sine_base = sinusoidal_component(time, amplitude=3, base_offset=7)
    cah_der_base = -1 * (sine_base + noise(0.2) - 0.1)  # Using existing noise function

    cah_der_0 = -cah_der_base + 0.5 if end else cah_der_base
    cah_der_1 = cah_der_0
    der_ica = cah_der_0 + cah_der_1 + 0.5 if end else -(cah_der_0 + cah_der_1)

    # Loads
    datacenter0 = 2 * cah_der_base * 0.2
    datacenter1 = 2 * cah_der_base * 0.5
    datacenter2 = 2 * cah_der_base * 0.3

    # Atlantica Grid
    # Buses
    se_melena = solar_gaussian(time, peak_power + delta_melena, sigma=2)
    # Batteries
    bess_melena = bess_active_power(time, peak_power, [14])

    return {
        # Atlantica Grid
        "SEMariaElena": se_melena,
        "BESSMariaElena": bess_melena,
        # Calama Grid
        "PFVJama": pfv_jama,
        "PFVSanPedro": pfv_sanpedro,
        "PFVAzabache": pfv_azabache,
        "PFVUsya": pfv_usya,
        "PEValleDeLosVientos": pe_vlv,
        "PECalama": pe_calama,
        "JAM-LAS": jam_las,
        "LAS-CAL": las_cal,
        "VLV-CAL": vlv_cal,
        "CAL-CHU": total_cal_chu,
        "CAL-SAL": cal_sal,
        "SAL-CHU": sal_chu,
        "CAL-NCH": cal_nch,
        "NCH-CHU": nch_chu,
        "SEValleDeLosVientos": se_vlv,
        "SEJama": se_jam,
        "SELasana": se_las,
        "SECalama": se_cal,
        "SENuevaChuquicamata": se_nchu,
        "SESalar": se_sal,
        "SEChuquicamata": se_chu,
        # Marcona Grid
        "CAH-DER-0": cah_der_0,
        "CAH-DER-1": cah_der_1,
        "DER-ICA": der_ica,
        "Datacenter0": datacenter0,
        "Datacenter1": datacenter1,
        "Datacenter2": datacenter2,
    }


def active_power_row(asset_names: Sequence[str], time: datetime) -> str:
    values = compute_power_values(time, peak_power=10)
    return generic_row(asset_names, time, values, default="0.0")


def active_power_start_row(asset_names: Sequence[str], time: datetime) -> str:
    return active_power_row(asset_names, time)


def active_power_end_row(asset_names: Sequence[str], time: datetime) -> str:
    values = compute_power_values(time, peak_power=10, end=True)
    return generic_row(asset_names, time, values, default="0.0")


def available_active_power_row(asset_names: Sequence[str], time: datetime) -> str:
    values = compute_power_values(time, peak_power=20)
    return generic_row(asset_names, time, values, default="0.0")


def reactive_power_row(asset_names: Sequence[str], time: datetime) -> str:
    values = compute_power_values(time, peak_power=0.8)
    return generic_row(asset_names, time, values, default="0.0")


def reactive_power_start_row(asset_names: Sequence[str], time: datetime) -> str:
    return reactive_power_row(asset_names, time)


def reactive_power_end_row(asset_names: Sequence[str], time: datetime) -> str:
    values = compute_power_values(time, peak_power=0.8, end=True)
    return generic_row(asset_names, time, values, default="0.0")


def power_set_point_row(asset_names: Sequence[str], time: datetime) -> str:
    values = compute_power_values(time, peak_power=10)
    return generic_row(asset_names, time, values, default="0.0")


def contingency_row(asset_names: Sequence[str], time: datetime) -> str:
    return generic_row(asset_names, time, {}, default="false")


def frequency_row(asset_names: Sequence[str], time: datetime) -> str:
    return generic_row(asset_names, time, {}, default="50")


def switch_status_row(asset_names: Sequence[str], time: datetime) -> str:
    return generic_row(asset_names, time, {}, default="true")


def switch_status_start_row(asset_names: Sequence[str], time: datetime) -> str:
    return generic_row(asset_names, time, {}, default="true")


def switch_status_end_row(asset_names: Sequence[str], time: datetime) -> str:
    return generic_row(asset_names, time, {}, default="true")


def voltage_start_row(asset_names: Sequence[str], time: datetime) -> str:
    return generic_row(asset_names, time, {}, default="350")


def voltage_end_row(asset_names: Sequence[str], time: datetime) -> str:
    return generic_row(asset_names, time, {}, default="330")


def current_row(asset_names: Sequence[str], time: datetime) -> str:
    return generic_row(asset_names, time, {}, default="300")


def state_of_charge_row(asset_names: Sequence[str], time: datetime) -> str:
    bess_melena = bess_soc(time, [14])
    values = {
        "BESSMariaElena": bess_melena,
    }
    return generic_row(asset_names, time, values, default="0.0")


def get_assets_with_attr(attr: str) -> list[str]:
    kinds = [k for k, attrs in KIND_INPUT_ATTRIBUTES.items() if attr in attrs]
    return [a.name for a in ALL_ASSETS if a.kind.name in kinds]


TASKS: list[GenerationTask] = [
    GenerationTask("voltage_start.csv", "voltage_start", voltage_start_row),
    GenerationTask("voltage_end.csv", "voltage_start", voltage_end_row),
    *[
        GenerationTask(
            f"current_{phase}_start.csv", f"current_{phase}_start", current_row
        )
        for phase in ["r", "s", "t"]
    ],
    *[
        GenerationTask(
            f"current_{phase}_end.csv", f"current_{phase}_start", current_row
        )
        for phase in ["r", "s", "t"]
    ],
    GenerationTask("active_power.csv", "active_power", active_power_row),
    GenerationTask(
        "active_power_start.csv", "active_power_start", active_power_start_row
    ),
    GenerationTask("active_power_end.csv", "active_power_end", active_power_end_row),
    GenerationTask("power_set_point.csv", "power_set_point", power_set_point_row),
    GenerationTask("reactive_power.csv", "reactive_power", reactive_power_row),
    GenerationTask(
        "reactive_power_start.csv", "reactive_power_start", reactive_power_start_row
    ),
    GenerationTask(
        "reactive_power_end.csv", "reactive_power_end", reactive_power_end_row
    ),
    GenerationTask("contingency.csv", "contingency", contingency_row),
    GenerationTask("frequency.csv", "frequency", frequency_row),
    GenerationTask("switch_status.csv", "switch_status", switch_status_row),
    GenerationTask(
        "switch_status_start.csv", "switch_status_start", switch_status_start_row
    ),
    GenerationTask("switch_status_end.csv", "switch_status_end", switch_status_end_row),
    GenerationTask(
        "available_active_power.csv",
        "available_active_power",
        available_active_power_row,
    ),
    GenerationTask("state_of_charge.csv", "state_of_charge", state_of_charge_row),
]


def run_generation(
    tasks: Sequence[GenerationTask],
    start: datetime = START_DATE,
    minutes: int = 24 * 60,
    step: timedelta = timedelta(minutes=1),
) -> None:
    for task in tasks:
        assets = get_assets_with_attr(task.asset_attr)
        with open(task.filename, "w", newline="") as f:
            f.write("timestamp," + ",".join(sorted(assets)) + "\n")
            current = start
            for _ in range(minutes):
                line = task.row_fn(assets, current)
                f.write(line)
                current += step


def generate_traces(filename: str = "traces.json") -> None:
    marcona_assets = [
        "Datacenter",
        "CAH-DER",
        "DER-ICA",
        "SEDerivacion",
        "SEIca",
        "SECahuachi",
        "PoromaExternal",
        "Marcona",
    ]
    traces: list[dict] = []
    for a in ALL_ASSETS:
        grid = "Marcona" if any(m in a.name for m in marcona_assets) else "Calama"
        for attr in KIND_INPUT_ATTRIBUTES[a.kind.name]:
            noise_factor = (
                0.02
                if attr not in ("contingency",) and "switch_status" not in attr
                else None
            )
            traces.append(
                {
                    "name": f"{grid}/{a.name}/{attr}",
                    "topic": f"{grid}/{a.name}/{attr}",
                    "filename": f"{attr}.csv",
                    "noise_factor": noise_factor,
                    "match_timestamp_by": "hour",
                    "target_value": a.name,
                }
            )
    with open(filename, "w") as f:
        json.dump({"traces": traces}, f, indent=2)


if __name__ == "__main__":
    start_date = datetime(2024, 1, 1)
    run_generation(TASKS)
    generate_traces()
