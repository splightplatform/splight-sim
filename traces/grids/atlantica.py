from datetime import datetime

from generic import GridDefinition, bess_active_power, bess_soc
from utils import solar_gaussian

ASSETS = {
    "SEMariaElena": "Bus",
    "BESSMariaElena": "Battery",
}


def power(time: datetime, peak_power: float, end: bool = False, reactive: bool = False):
    peak_power *= -0.93 if end else 1
    peak_power *= 0.08 if reactive else 1
    delta_melena = 2.1

    # Atlantica Grid
    # Buses
    se_melena = solar_gaussian(time, peak_power + delta_melena, sigma=2)
    # Batteries
    bess_melena = bess_active_power(time, peak_power, [14])

    return {
        "SEMariaElena": se_melena,
        "BESSMariaElena": bess_melena,
    }


class AtlanticaGrid(GridDefinition):
    @property
    def name(self) -> str:
        return "Atlantica"

    @property
    def assets(self) -> dict[str, str]:
        return ASSETS

    def get_value(self, asset: str, attr: str, time: datetime):
        # Custom value functions for specific assets
        if asset == "SEMariaElena" and attr == "active_power":
            return power(time, 15).get(asset, 0.0)
        elif asset == "SEMariaElena" and attr == "reactive_power":
            return power(time, 15, reactive=True).get(asset, 0.0)
        elif asset == "BESSMariaElena" and attr == "active_power":
            return power(time, 15).get(asset, 0.0)
        elif asset == "BESSMariaElena" and attr == "reactive_power":
            return power(time, 15, reactive=True).get(asset, 0.0)
        elif asset == "BESSMariaElena" and attr == "state_of_charge":
            return bess_soc(time, [14])
        # Default values for other attributes
        else:
            return self.default_value(attr)


# Export the class
AtlanticaGrid = AtlanticaGrid
