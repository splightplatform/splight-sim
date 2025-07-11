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
