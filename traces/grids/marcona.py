from datetime import datetime

from generic import GridDefinition
from utils import noise, sinusoidal

ASSETS: dict[str, str] = {
    "SECahuachi": "Bus",
    "SEDerivacion": "Bus",
    "SEIca": "Bus",
    "PoromaExternal": "ExternalGrid",
    "Marcona": "Grid",
    "CAH-DER-0": "Line",
    "CAH-DER-1": "Line",
    "DER-ICA": "Line",
    "Datacenter0": "Load",
    "Datacenter1": "Load",
    "Datacenter2": "Load",
}


def power(time: datetime, peak_power: float, end: bool = False, reactive: bool = False):
    peak_power *= -0.93 if end else 1
    peak_power *= 0.08 if reactive else 1

    # Marcona Grid
    sine_base = sinusoidal(time, amplitude=3, offset=7)
    cah_der_base = -1 * (sine_base + noise(1) - 0.1)

    cah_der_0 = -cah_der_base + 0.5 if end else cah_der_base
    cah_der_1 = cah_der_0
    der_ica = cah_der_0 + cah_der_1 + 0.5 if end else -(cah_der_0 + cah_der_1)

    se_cah = cah_der_0 + cah_der_1
    se_der = se_cah - noise(2)
    se_ica = se_der - noise(1)

    # Loads
    total_power = 2 * cah_der_base
    datacenter0 = total_power * 0.2
    datacenter1 = total_power * 0.5
    datacenter2 = total_power * 0.3
    return {
        "Datacenter0": datacenter0,
        "Datacenter1": datacenter1,
        "Datacenter2": datacenter2,
        "CAH-DER-0": cah_der_0,
        "CAH-DER-1": cah_der_1,
        "DER-ICA": der_ica,
        "SECahuachi": se_cah,
        "SEDerivacion": se_der,
        "SEIca": se_ica,
    }


class MarconaGrid(GridDefinition):
    @property
    def name(self) -> str:
        return "Marcona"

    @property
    def assets(self) -> dict[str, str]:
        return ASSETS

    def get_value(self, asset: str, attr: str, time: datetime):
        # Custom value functions for specific assets
        if asset == "Datacenter0" and attr == "active_power":
            return power(time, 12).get(asset, 0.0)
        elif asset == "Datacenter1" and attr == "active_power":
            return power(time, 12).get(asset, 0.0)
        elif asset == "Datacenter2" and attr == "active_power":
            return power(time, 12).get(asset, 0.0)
        elif asset == "CAH-DER-0" and attr in [
            "active_power_start",
            "active_power_end",
        ]:
            return power(time, 12, end=attr.endswith("_end")).get(asset, 0.0)
        elif asset == "CAH-DER-1" and attr in [
            "active_power_start",
            "active_power_end",
        ]:
            return power(time, 12, end=attr.endswith("_end")).get(asset, 0.0)
        elif asset == "DER-ICA" and attr in ["active_power_start", "active_power_end"]:
            return power(time, 12, end=attr.endswith("_end")).get(asset, 0.0)
        elif (
            asset in ["SECahuachi", "SEDerivacion", "SEIca"] and attr == "active_power"
        ):
            return power(time, 12).get(asset, 0.0)
        elif (
            asset in ["SECahuachi", "SEDerivacion", "SEIca"]
            and attr == "reactive_power"
        ):
            return power(time, 12, reactive=True).get(asset, 0.0)
        # Default values for other attributes
        else:
            return self.default_value(attr)


# Export the class
MarconaGrid = MarconaGrid
