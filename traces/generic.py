from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict

import numpy as np

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


# --- ABC for Grid Definitions ---
class GridDefinition(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def assets(self) -> Dict[str, str]:  # asset_name -> kind
        pass

    @abstractmethod
    def get_value(self, asset: str, attr: str, time: datetime) -> Any:
        pass

    def get_attributes_for_asset(self, asset: str) -> list[str]:
        """Get attributes for a specific asset based on its kind"""
        if asset not in self.assets:
            return []
        kind = self.assets[asset]
        return KIND_INPUT_ATTRIBUTES.get(kind, [])

    def get_all_attributes(self) -> list[str]:
        """Get all unique attributes used by this grid's assets"""
        all_attrs = set()
        for asset in self.assets:
            all_attrs.update(self.get_attributes_for_asset(asset))
        return sorted(list(all_attrs))

    def default_value(attr: str) -> float | str:
        if "switch_status" in attr:
            return "true"
        if "voltage_start" in attr:
            return 350.0
        if "voltage_end" in attr:
            return 330.0
        if "current" in attr:
            return 300.0
        if attr == "contingency":
            return "false"
        if attr == "frequency":
            return 50.0
        return 0.0


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
