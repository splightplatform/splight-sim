from datetime import datetime

import numpy as np


def sinusoidal(time: datetime, amplitude: float, offset: float):
    time_fraction = (time.hour + time.minute / 60) / 24
    sine_value = amplitude * np.sin(2 * np.pi * time_fraction)
    return sine_value + offset


def solar_gaussian(
    time: datetime, peak: float, sigma: float = 2, mu: float = 14
) -> float:
    x = time.hour + time.minute / 60
    coef = 1 / (np.sqrt(2 * np.pi) * sigma)
    exponent = -((x - mu) ** 2) / (2 * sigma**2)
    amplitude = peak * np.sqrt(2 * np.pi * sigma**2)
    return round(amplitude * coef * np.exp(exponent), 3)


def normalize(value: float | str | bool | int) -> str:
    if isinstance(value, float):
        value = f"{round(value, 3):.3f}"
        return value if value != "-0.000" else "0.000"
    elif isinstance(value, str):
        return value
    elif isinstance(value, bool):
        return str(value).lower()
    elif isinstance(value, int):
        return str(value)
    else:
        raise ValueError(f"Invalid value type: {type(value)}")


def noise(peak: float) -> float:
    return np.random.normal(0, max(peak, 1))


def _in_interval(x: float, start: float, end: float) -> bool:
    if start <= end:
        return start <= x < end
    else:
        return x >= start or x < end


def _compute_windows(
    low_hours: list[float],
    peak_hours: list[float],
    charge_rate: float,  # MWh
    discharge_rate: float,  # MWh
    capacity: float,
):
    lows = sorted(low_hours)
    peaks = sorted(peak_hours)
    n = max(len(lows), len(peaks))
    cycles = []
    for i in range(n):
        low = lows[i % len(lows)]
        peak = peaks[i % len(peaks)]
        next_low = lows[(i + 1) % len(lows)]
        t_charge = capacity / charge_rate
        t_discharge = capacity / discharge_rate
        charge_start = (peak - t_charge) % 24
        discharge_start = (next_low - t_discharge) % 24

        cycles.append(
            {
                "low": low,
                "peak": peak,
                "next_low": next_low,
                "charge_start": charge_start,
                "discharge_start": discharge_start,
            }
        )
    return cycles


def bess_soc(
    time: datetime,
    low_hours: list[float],
    peak_hours: list[float],
    charge_rate: float,  # MWh
    discharge_rate: float,  # MWh
    capacity: float,
) -> float:
    h = time.hour + time.minute / 60 + time.second / 3600
    for c in _compute_windows(
        low_hours, peak_hours, charge_rate, discharge_rate, capacity
    ):
        lo, ps, nl = c["low"], c["peak"], c["next_low"]
        cs, ds = c["charge_start"], c["discharge_start"]

        if _in_interval(h, lo, cs):
            soc_mwh = 0.0

        elif _in_interval(h, cs, ps):
            hours_into = (h - cs) % 24
            soc_mwh = min(capacity, hours_into * charge_rate)

        elif _in_interval(h, ps, ds):
            soc_mwh = capacity

        elif _in_interval(h, ds, nl):
            hours_in = (h - ds) % 24
            soc_mwh = max(0.0, capacity - hours_in * discharge_rate)

        else:
            continue

        return round((soc_mwh / capacity) * 100.0, 2)
    return 0.0


def bess_active_power(
    time: datetime,
    low_hours: list[float],
    peak_hours: list[float],
    charge_rate: float,  # MWh
    discharge_rate: float,  # MWh
    capacity: float,
) -> float:
    # Negative = charging; positive = discharging; zero = hold.
    h = time.hour + time.minute / 60 + time.second / 3600
    for c in _compute_windows(
        low_hours, peak_hours, charge_rate, discharge_rate, capacity
    ):
        lo, ps, nl = c["low"], c["peak"], c["next_low"]
        cs, ds = c["charge_start"], c["discharge_start"]

        if _in_interval(h, lo, cs):
            return 0.0
        elif _in_interval(h, cs, ps):
            return -round(charge_rate, 3)
        elif _in_interval(h, ps, ds):
            return 0.0
        elif _in_interval(h, ds, nl):
            return round(discharge_rate, 3)

    return 0.0
