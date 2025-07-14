import os
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

from utils import normalize

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


class GridDefinition(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def assets(self) -> dict[str, str]:
        """Returns a dict of asset_name : kind_name"""
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

    @classmethod
    def default_value(self, attr: str) -> float | str:
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

    def build(
        self,
        output_base_dir="data/mqtt/traces",
        start_date=None,
        minutes=24 * 60,
        step_minutes=1,
    ):
        """
        Generate CSVs for each attribute in a grid directory and return traces for this grid.
        """

        if start_date is None:
            start_date = datetime(2024, 1, 1)
        step = timedelta(minutes=step_minutes)
        output_dir = os.path.join(output_base_dir, self.name)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        traces = []
        all_attributes = self.get_all_attributes()
        for attr in all_attributes:
            method_name = f"get_{attr}"
            filename = os.path.join(output_dir, f"{attr}.csv")

            # get assets with the attribute
            asset_list = [
                asset
                for asset in self.assets
                if attr in self.get_attributes_for_asset(asset)
            ]
            asset_list = sorted(asset_list)
            if not asset_list:
                continue
            with open(filename, "w") as f:
                f.write("timestamp," + ",".join(asset_list) + "\n")
                current = start_date
                for _ in range(minutes):
                    merged_values = {}
                    if hasattr(self, method_name):
                        method = getattr(self, method_name)
                        values = method(current)  # {asset: normalized_value}
                        merged_values.update(values)
                    row_values = [
                        merged_values.get(asset, normalize(self.default_value(attr)))
                        for asset in asset_list
                    ]
                    f.write(
                        f"{current.strftime('%Y-%m-%d %H:%M:%S')},"
                        + ",".join(row_values)
                        + "\n"
                    )
                    current += step
            # Add trace dicts for each asset/attribute
            for asset in asset_list:
                noise = (
                    0.02
                    if ("switch_status" not in attr and attr != "contingency")
                    else None
                )
                traces.append(
                    {
                        "name": f"{self.name}/{asset}/{attr}",
                        "topic": f"{self.name}/{asset}/{attr}",
                        "filename": f"{self.name}/{attr}.csv",
                        "noise_factor": noise,
                        "match_timestamp_by": "hour",
                        "target_value": asset,
                    }
                )
        return traces

    def get_active_power(self, time: datetime) -> dict[str, str]:
        result = {}
        for asset in self.assets:
            if "active_power" in self.get_attributes_for_asset(asset):
                value = self.default_value("active_power")
                result[asset] = normalize(value)
        return result

    def get_reactive_power(self, time: datetime) -> dict[str, str]:
        result = {}
        for asset in self.assets:
            if "reactive_power" in self.get_attributes_for_asset(asset):
                value = self.default_value("reactive_power")
                result[asset] = normalize(value)
        return result

    def get_state_of_charge(self, time: datetime) -> dict[str, str]:
        result = {}
        for asset in self.assets:
            if "state_of_charge" in self.get_attributes_for_asset(asset):
                value = self.default_value("state_of_charge")
                result[asset] = normalize(value)
        return result

    def get_available_active_power(self, time: datetime) -> dict[str, str]:
        result = {}
        for asset in self.assets:
            if "available_active_power" in self.get_attributes_for_asset(asset):
                value = self.default_value("available_active_power")
                result[asset] = normalize(value)
        return result

    def get_frequency(self, time: datetime) -> dict[str, str]:
        result = {}
        for asset in self.assets:
            if "frequency" in self.get_attributes_for_asset(asset):
                value = self.default_value("frequency")
                result[asset] = normalize(value)
        return result

    def get_power_set_point(self, time: datetime) -> dict[str, str]:
        result = {}
        for asset in self.assets:
            if "power_set_point" in self.get_attributes_for_asset(asset):
                value = self.default_value("power_set_point")
                result[asset] = normalize(value)
        return result

    def get_switch_status(self, time: datetime) -> dict[str, str]:
        result = {}
        for asset in self.assets:
            if "switch_status" in self.get_attributes_for_asset(asset):
                value = self.default_value("switch_status")
                result[asset] = normalize(value)
        return result

    def get_active_power_end(self, time: datetime) -> dict[str, str]:
        result = {}
        for asset in self.assets:
            if "active_power_end" in self.get_attributes_for_asset(asset):
                value = self.default_value("active_power_end")
                result[asset] = normalize(value)
        return result

    def get_active_power_start(self, time: datetime) -> dict[str, str]:
        result = {}
        for asset in self.assets:
            if "active_power_start" in self.get_attributes_for_asset(asset):
                value = self.default_value("active_power_start")
                result[asset] = normalize(value)
        return result

    def get_contingency(self, time: datetime) -> dict[str, str]:
        result = {}
        for asset in self.assets:
            if "contingency" in self.get_attributes_for_asset(asset):
                value = self.default_value("contingency")
                result[asset] = normalize(value)
        return result

    def get_current_r_end(self, time: datetime) -> dict[str, str]:
        result = {}
        for asset in self.assets:
            if "current_r_end" in self.get_attributes_for_asset(asset):
                value = self.default_value("current_r_end")
                result[asset] = normalize(value)
        return result

    def get_current_r_start(self, time: datetime) -> dict[str, str]:
        result = {}
        for asset in self.assets:
            if "current_r_start" in self.get_attributes_for_asset(asset):
                value = self.default_value("current_r_start")
                result[asset] = normalize(value)
        return result

    def get_current_s_end(self, time: datetime) -> dict[str, str]:
        result = {}
        for asset in self.assets:
            if "current_s_end" in self.get_attributes_for_asset(asset):
                value = self.default_value("current_s_end")
                result[asset] = normalize(value)
        return result

    def get_current_s_start(self, time: datetime) -> dict[str, str]:
        result = {}
        for asset in self.assets:
            if "current_s_start" in self.get_attributes_for_asset(asset):
                value = self.default_value("current_s_start")
                result[asset] = normalize(value)
        return result

    def get_current_t_end(self, time: datetime) -> dict[str, str]:
        result = {}
        for asset in self.assets:
            if "current_t_end" in self.get_attributes_for_asset(asset):
                value = self.default_value("current_t_end")
                result[asset] = normalize(value)
        return result

    def get_current_t_start(self, time: datetime) -> dict[str, str]:
        result = {}
        for asset in self.assets:
            if "current_t_start" in self.get_attributes_for_asset(asset):
                value = self.default_value("current_t_start")
                result[asset] = normalize(value)
        return result

    def get_reactive_power_end(self, time: datetime) -> dict[str, str]:
        result = {}
        for asset in self.assets:
            if "reactive_power_end" in self.get_attributes_for_asset(asset):
                value = self.default_value("reactive_power_end")
                result[asset] = normalize(value)
        return result

    def get_reactive_power_start(self, time: datetime) -> dict[str, str]:
        result = {}
        for asset in self.assets:
            if "reactive_power_start" in self.get_attributes_for_asset(asset):
                value = self.default_value("reactive_power_start")
                result[asset] = normalize(value)
        return result

    def get_switch_status_end(self, time: datetime) -> dict[str, str]:
        result = {}
        for asset in self.assets:
            if "switch_status_end" in self.get_attributes_for_asset(asset):
                value = self.default_value("switch_status_end")
                result[asset] = normalize(value)
        return result

    def get_switch_status_start(self, time: datetime) -> dict[str, str]:
        result = {}
        for asset in self.assets:
            if "switch_status_start" in self.get_attributes_for_asset(asset):
                value = self.default_value("switch_status_start")
                result[asset] = normalize(value)
        return result

    def get_voltage_end(self, time: datetime) -> dict[str, str]:
        result = {}
        for asset in self.assets:
            if "voltage_end" in self.get_attributes_for_asset(asset):
                value = self.default_value("voltage_end")
                result[asset] = normalize(value)
        return result

    def get_voltage_start(self, time: datetime) -> dict[str, str]:
        result = {}
        for asset in self.assets:
            if "voltage_start" in self.get_attributes_for_asset(asset):
                value = self.default_value("voltage_start")
                result[asset] = normalize(value)
        return result

    def get_active_power_loss(self, time: datetime) -> dict[str, str]:
        result = {}
        for asset in self.assets:
            if "active_power_loss" in self.get_attributes_for_asset(asset):
                value = self.default_value("active_power_loss")
                result[asset] = normalize(value)
        return result

    def get_reactive_power_loss(self, time: datetime) -> dict[str, str]:
        result = {}
        for asset in self.assets:
            if "reactive_power_loss" in self.get_attributes_for_asset(asset):
                value = self.default_value("reactive_power_loss")
                result[asset] = normalize(value)
        return result
