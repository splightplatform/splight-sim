from datetime import datetime

from generic import GridDefinition
from utils import noise, normalize, sinusoidal


class MarconaGrid(GridDefinition):
    @property
    def name(self) -> str:
        return "Marcona"

    @property
    def assets(self) -> dict[str, str]:
        return {
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

    @staticmethod
    def power(
        time: datetime, peak_power: float, end: bool = False, reactive: bool = False
    ):
        peak_power *= -0.93 if end else 1
        peak_power *= 0.08 if reactive else 1

        sine_base = sinusoidal(time, amplitude=3, offset=7)
        cah_der_base = -1 * (sine_base + noise(1) - 0.1)

        # Lines
        cah_der_0 = -cah_der_base + 0.5 if end else cah_der_base
        cah_der_1 = cah_der_0
        der_ica = cah_der_0 + cah_der_1 + 0.5 if end else -(cah_der_0 + cah_der_1)

        # Buses
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

    def default_value(self, attr: str) -> float | str:
        if "voltage_start" in attr:
            return 370.0
        return super().default_value(attr)

    def get_active_power(self, time: datetime) -> dict[str, str]:
        result = super().get_active_power(time)
        result["Datacenter0"] = normalize(self.power(time, 12).get("Datacenter0", 0.0))
        result["Datacenter1"] = normalize(self.power(time, 12).get("Datacenter1", 0.0))
        result["Datacenter2"] = normalize(self.power(time, 12).get("Datacenter2", 0.0))
        result["SECahuachi"] = normalize(self.power(time, 12).get("SECahuachi", 0.0))
        result["SEDerivacion"] = normalize(
            self.power(time, 12).get("SEDerivacion", 0.0)
        )
        result["SEIca"] = normalize(self.power(time, 12).get("SEIca", 0.0))
        return result

    def get_reactive_power(self, time: datetime) -> dict[str, str]:
        result = super().get_reactive_power(time)
        result["SECahuachi"] = normalize(
            self.power(time, 12, reactive=True).get("SECahuachi", 0.0)
        )
        result["SEDerivacion"] = normalize(
            self.power(time, 12, reactive=True).get("SEDerivacion", 0.0)
        )
        result["SEIca"] = normalize(
            self.power(time, 12, reactive=True).get("SEIca", 0.0)
        )
        return result

    def get_active_power_start(self, time: datetime) -> dict[str, str]:
        result = super().get_active_power_start(time)
        result["CAH-DER-0"] = normalize(
            self.power(time, 12, end=False).get("CAH-DER-0", 0.0)
        )
        result["CAH-DER-1"] = normalize(
            self.power(time, 12, end=False).get("CAH-DER-1", 0.0)
        )
        result["DER-ICA"] = normalize(
            self.power(time, 12, end=False).get("DER-ICA", 0.0)
        )
        return result

    def get_active_power_end(self, time: datetime) -> dict[str, str]:
        result = super().get_active_power_end(time)
        result["CAH-DER-0"] = normalize(
            self.power(time, 12, end=True).get("CAH-DER-0", 0.0)
        )
        result["CAH-DER-1"] = normalize(
            self.power(time, 12, end=True).get("CAH-DER-1", 0.0)
        )
        result["DER-ICA"] = normalize(
            self.power(time, 12, end=True).get("DER-ICA", 0.0)
        )
        return result
