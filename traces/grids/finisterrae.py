from datetime import datetime

from generic import GridDefinition
from utils import bess_active_power, bess_soc, normalize, solar_gaussian


class FinisTerraeGrid(GridDefinition):
    @property
    def name(self) -> str:
        return "FinisTerrae"

    @property
    def assets(self) -> dict[str, str]:
        return {
            "SEFinisTerrae": "Bus",
            "BESSFinisTerrae": "Battery",
            "PFVFinisTerrae": "Generator",
        }

    def get_active_power(self, time: datetime) -> dict[str, str]:
        result = super().get_active_power(time)
        result["SEFinisTerrae"] = normalize(
            self.power(time, 15).get("SEFinisTerrae", 0.0)
        )
        result["BESSFinisTerrae"] = normalize(
            self.power(time, 15).get("BESSFinisTerrae", 0.0)
        )

        return result

    @staticmethod
    def power(
        time: datetime, peak_power: float, end: bool = False, reactive: bool = False
    ):
        peak_power *= -0.93 if end else 1
        peak_power *= 0.08 if reactive else 1
        delta_fterrae = 2.9

        # Generator
        pfv_fterrae = solar_gaussian(time, peak_power + delta_fterrae, sigma=2.2)
        # Buses
        se_fterrae = pfv_fterrae
        # Batteries
        bess_fterrae = bess_active_power(time, [5, 13], [9, 16], 9, 6, 18)

        return {
            "SEFinisTerrae": se_fterrae,
            "BESSFinisTerrae": bess_fterrae,
            "PFVFinisTerrae": pfv_fterrae,
        }

    def get_reactive_power(self, time: datetime) -> dict[str, str]:
        result = super().get_reactive_power(time)
        result["SEFinisTerrae"] = normalize(
            self.power(time, 15, reactive=True).get("SEFinisTerrae", 0.0)
        )
        result["BESSFinisTerrae"] = normalize(
            self.power(time, 15, reactive=True).get("BESSFinisTerrae", 0.0)
        )
        return result

    def get_available_active_power(self, time: datetime) -> dict[str, str]:
        result = super().get_available_active_power(time)
        result["PFVFinisTerrae"] = normalize(
            self.power(time, 20).get("PFVFinisTerrae", 0.0)
        )
        return result

    def get_power_set_point(self, time: datetime) -> dict[str, str]:
        result = super().get_power_set_point(time)
        result["PFVFinisTerrae"] = normalize(
            self.power(time, 16).get("PFVFinisTerrae", 0.0)
        )
        return result

    def get_state_of_charge(self, time: datetime) -> dict[str, str]:
        result = super().get_state_of_charge(time)
        result["BESSFinisTerrae"] = normalize(
            bess_soc(time, [5, 13], [9, 16], 9, 6, 18)
        )
        return result
