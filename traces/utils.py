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
