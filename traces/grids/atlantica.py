from datetime import datetime

from generic import GridDefinition
from utils import bess_active_power, bess_soc, normalize, solar_gaussian


class AtlanticaGrid(GridDefinition):
    @property
    def name(self) -> str:
        return "Atlantica"

    @property
    def assets(self) -> dict[str, str]:
        return {
            "SEMariaElena": "Bus",
            "BESSMariaElena": "Battery",
        }

    def get_active_power(self, time: datetime) -> dict[str, str]:
        result = super().get_active_power(time)
        result["SEMariaElena"] = normalize(
            self.power(time, 15).get("SEMariaElena", 0.0)
        )
        result["BESSMariaElena"] = normalize(
            self.power(time, 15).get("BESSMariaElena", 0.0)
        )
        return result

    @staticmethod
    def power(
        time: datetime, peak_power: float, end: bool = False, reactive: bool = False
    ):
        peak_power *= -0.93 if end else 1
        peak_power *= 0.08 if reactive else 1
        delta_melena = 2.1

        # Buses
        se_melena = solar_gaussian(time, peak_power + delta_melena, sigma=2)
        # Batteries
        bess_melena = bess_active_power(time, peak_power, [14])

        return {
            "SEMariaElena": se_melena,
            "BESSMariaElena": bess_melena,
        }

    def get_reactive_power(self, time: datetime) -> dict[str, str]:
        result = super().get_reactive_power(time)
        result["SEMariaElena"] = normalize(
            self.power(time, 15, reactive=True).get("SEMariaElena", 0.0)
        )
        result["BESSMariaElena"] = normalize(
            self.power(time, 15, reactive=True).get("BESSMariaElena", 0.0)
        )
        return result

    def get_state_of_charge(self, time: datetime) -> dict[str, str]:
        result = super().get_state_of_charge(time)
        result["BESSMariaElena"] = normalize(bess_soc(time, [14]))
        return result
