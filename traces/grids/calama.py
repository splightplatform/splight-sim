from datetime import datetime

from generic import GridDefinition
from utils import noise, normalize, solar_gaussian


class CalamaGrid(GridDefinition):
    @property
    def name(self) -> str:
        return "Calama"

    @property
    def assets(self) -> dict[str, str]:
        return {
            "Calama": "Grid",
            "SEValleDeLosVientos": "Bus",
            "SEJama": "Bus",
            "SELasana": "Bus",
            "SECalama": "Bus",
            "SENuevaChuquicamata": "Bus",
            "SESalar": "Bus",
            "SEChuquicamata": "Bus",
            "External": "ExternalGrid",
            "PFVJama": "Generator",
            "PEValleDeLosVientos": "Generator",
            "PFVSanPedro": "Generator",
            "PECalama": "Generator",
            "PFVAzabache": "Generator",
            "PFVUsya": "Generator",
            "CAL-NCH": "Line",
            "CAL-SAL": "Line",
            "SAL-CHU": "Line",
            "VLV-CAL": "Line",
            "JAM-LAS": "Line",
            "LAS-CAL": "Line",
            "NCH-CHU": "Line",
            "SlackSAL-CHU": "SlackLine",
        }

    @staticmethod
    def power(
        time: datetime, peak_power: float, end: bool = False, reactive: bool = False
    ):
        peak_power *= -0.93 if end else 1
        peak_power *= 0.08 if reactive else 1
        delta_vlv = -1.4
        delta_aza = 1.3
        delta_cal = 1.7
        delta_usy = -1.6

        # PFVs
        pfv_jama = solar_gaussian(time, peak_power)
        pfv_sanpedro = solar_gaussian(time, peak_power)
        pfv_azabache = solar_gaussian(time, peak_power + delta_aza, sigma=3)
        pfv_usya = solar_gaussian(time, peak_power + delta_usy, sigma=2.5)

        # PEs
        pe_vlv = peak_power + delta_vlv - noise((peak_power + delta_vlv) * 0.1)
        pe_calama = peak_power + delta_cal - noise((peak_power + delta_cal) * 0.1)

        # Lines
        jam_las = pfv_jama - noise(peak_power * 0.1)
        las_cal = jam_las + pfv_sanpedro - noise(peak_power * 0.1)
        vlv_cal = pe_vlv - noise((peak_power + delta_vlv) * 0.1)
        total_cal_chu = las_cal + vlv_cal + pfv_usya + pfv_azabache + pe_calama
        cal_sal = total_cal_chu / 2 - noise(peak_power * 0.1)
        sal_chu = cal_sal - noise(peak_power * 0.1)
        cal_nch = total_cal_chu / 2 - noise(peak_power * 0.1)
        nch_chu = cal_nch - noise(peak_power * 0.1)

        # Buses
        se_vlv = pe_vlv - noise((peak_power + delta_vlv) * 0.1)
        se_jam = jam_las
        se_las = las_cal
        se_cal = (
            pfv_usya + pfv_azabache + pe_calama + las_cal - noise(peak_power * 2 * 0.1)
        )
        se_sal = se_cal
        se_nchu = se_cal
        se_chu = se_sal + se_nchu

        return {
            "PFVJama": pfv_jama,
            "PFVSanPedro": pfv_sanpedro,
            "PFVAzabache": pfv_azabache,
            "PFVUsya": pfv_usya,
            "PEValleDeLosVientos": pe_vlv,
            "PECalama": pe_calama,
            "CAL-NCH": cal_nch,
            "CAL-SAL": cal_sal,
            "JAM-LAS": jam_las,
            "LAS-CAL": las_cal,
            "NCH-CHU": nch_chu,
            "SAL-CHU": sal_chu,
            "VLV-CAL": vlv_cal,
            "SEValleDeLosVientos": se_vlv,
            "SEJama": se_jam,
            "SECalama": se_cal,
            "SELasana": se_las,
            "SENuevaChuquicamata": se_nchu,
            "SEChuquicamata": se_chu,
            "SESalar": se_sal,
        }

    def get_active_power(self, time: datetime) -> dict[str, str]:
        result = super().get_active_power(time)
        result["PFVJama"] = normalize(self.power(time, 10).get("PFVJama", 0.0))
        result["PFVSanPedro"] = normalize(self.power(time, 10).get("PFVSanPedro", 0.0))
        result["PFVAzabache"] = normalize(self.power(time, 10).get("PFVAzabache", 0.0))
        result["PFVUsya"] = normalize(self.power(time, 10).get("PFVUsya", 0.0))
        result["PEValleDeLosVientos"] = normalize(
            self.power(time, 10).get("PEValleDeLosVientos", 0.0)
        )
        result["PECalama"] = normalize(self.power(time, 10).get("PECalama", 0.0))
        result["SEValleDeLosVientos"] = normalize(
            self.power(time, 10).get("SEValleDeLosVientos", 0.0)
        )
        result["SEJama"] = normalize(self.power(time, 10).get("SEJama", 0.0))
        result["SELasana"] = normalize(self.power(time, 10).get("SELasana", 0.0))
        result["SECalama"] = normalize(self.power(time, 10).get("SECalama", 0.0))
        result["SENuevaChuquicamata"] = normalize(
            self.power(time, 10).get("SENuevaChuquicamata", 0.0)
        )
        result["SESalar"] = normalize(self.power(time, 10).get("SESalar", 0.0))
        result["SEChuquicamata"] = normalize(
            self.power(time, 10).get("SEChuquicamata", 0.0)
        )
        return result

    def get_available_active_power(self, time: datetime) -> dict[str, str]:
        result = super().get_available_active_power(time)
        result["PFVJama"] = normalize(self.power(time, 20).get("PFVJama", 0.0))
        result["PFVSanPedro"] = normalize(self.power(time, 20).get("PFVSanPedro", 0.0))
        result["PFVAzabache"] = normalize(self.power(time, 20).get("PFVAzabache", 0.0))
        result["PFVUsya"] = normalize(self.power(time, 20).get("PFVUsya", 0.0))
        result["PEValleDeLosVientos"] = normalize(
            self.power(time, 20).get("PEValleDeLosVientos", 0.0)
        )
        result["PECalama"] = normalize(self.power(time, 20).get("PECalama", 0.0))
        return result

    def get_power_set_point(self, time: datetime) -> dict[str, str]:
        result = super().get_power_set_point(time)
        result["PFVJama"] = normalize(self.power(time, 11).get("PFVJama", 0.0))
        result["PFVSanPedro"] = normalize(self.power(time, 11).get("PFVSanPedro", 0.0))
        result["PFVAzabache"] = normalize(self.power(time, 11).get("PFVAzabache", 0.0))
        result["PFVUsya"] = normalize(self.power(time, 11).get("PFVUsya", 0.0))
        result["PEValleDeLosVientos"] = normalize(
            self.power(time, 11).get("PEValleDeLosVientos", 0.0)
        )
        result["PECalama"] = normalize(self.power(time, 11).get("PECalama", 0.0))
        return result

    def get_frequency(self, time: datetime) -> dict[str, str]:
        result = super().get_frequency(time)
        result["PEValleDeLosVientos"] = normalize(50.0)
        result["PECalama"] = normalize(50.0)
        return result

    def get_switch_status(self, time: datetime) -> dict[str, str]:
        result = super().get_switch_status(time)
        result["PEValleDeLosVientos"] = normalize("true")
        result["PECalama"] = normalize("true")
        return result

    def get_active_power_start(self, time: datetime) -> dict[str, str]:
        result = super().get_active_power_start(time)
        result["CAL-NCH"] = normalize(
            self.power(time, 10, end=False).get("CAL-NCH", 0.0)
        )
        result["CAL-SAL"] = normalize(
            self.power(time, 10, end=False).get("CAL-SAL", 0.0)
        )
        result["SAL-CHU"] = normalize(
            self.power(time, 10, end=False).get("SAL-CHU", 0.0)
        )
        result["VLV-CAL"] = normalize(
            self.power(time, 10, end=False).get("VLV-CAL", 0.0)
        )
        result["JAM-LAS"] = normalize(
            self.power(time, 10, end=False).get("JAM-LAS", 0.0)
        )
        result["LAS-CAL"] = normalize(
            self.power(time, 10, end=False).get("LAS-CAL", 0.0)
        )
        result["NCH-CHU"] = normalize(
            self.power(time, 10, end=False).get("NCH-CHU", 0.0)
        )
        return result

    def get_active_power_end(self, time: datetime) -> dict[str, str]:
        result = super().get_active_power_end(time)
        result["CAL-NCH"] = normalize(
            self.power(time, 10, end=True).get("CAL-NCH", 0.0)
        )
        result["CAL-SAL"] = normalize(
            self.power(time, 10, end=True).get("CAL-SAL", 0.0)
        )
        result["SAL-CHU"] = normalize(
            self.power(time, 10, end=True).get("SAL-CHU", 0.0)
        )
        result["VLV-CAL"] = normalize(
            self.power(time, 10, end=True).get("VLV-CAL", 0.0)
        )
        result["JAM-LAS"] = normalize(
            self.power(time, 10, end=True).get("JAM-LAS", 0.0)
        )
        result["LAS-CAL"] = normalize(
            self.power(time, 10, end=True).get("LAS-CAL", 0.0)
        )
        result["NCH-CHU"] = normalize(
            self.power(time, 10, end=True).get("NCH-CHU", 0.0)
        )
        return result

    def get_reactive_power_start(self, time: datetime) -> dict[str, str]:
        result = super().get_reactive_power_start(time)
        result["CAL-NCH"] = normalize(
            self.power(time, 10, reactive=True, end=False).get("CAL-NCH", 0.0)
        )
        result["CAL-SAL"] = normalize(
            self.power(time, 10, reactive=True, end=False).get("CAL-SAL", 0.0)
        )
        result["SAL-CHU"] = normalize(
            self.power(time, 10, reactive=True, end=False).get("SAL-CHU", 0.0)
        )
        result["VLV-CAL"] = normalize(
            self.power(time, 10, reactive=True, end=False).get("VLV-CAL", 0.0)
        )
        result["JAM-LAS"] = normalize(
            self.power(time, 10, reactive=True, end=False).get("JAM-LAS", 0.0)
        )
        result["LAS-CAL"] = normalize(
            self.power(time, 10, reactive=True, end=False).get("LAS-CAL", 0.0)
        )
        result["NCH-CHU"] = normalize(
            self.power(time, 10, reactive=True, end=False).get("NCH-CHU", 0.0)
        )
        return result

    def get_reactive_power_end(self, time: datetime) -> dict[str, str]:
        result = super().get_reactive_power_end(time)
        result["CAL-NCH"] = normalize(
            self.power(time, 10, reactive=True, end=True).get("CAL-NCH", 0.0)
        )
        result["CAL-SAL"] = normalize(
            self.power(time, 10, reactive=True, end=True).get("CAL-SAL", 0.0)
        )
        result["SAL-CHU"] = normalize(
            self.power(time, 10, reactive=True, end=True).get("SAL-CHU", 0.0)
        )
        result["VLV-CAL"] = normalize(
            self.power(time, 10, reactive=True, end=True).get("VLV-CAL", 0.0)
        )
        result["JAM-LAS"] = normalize(
            self.power(time, 10, reactive=True, end=True).get("JAM-LAS", 0.0)
        )
        result["LAS-CAL"] = normalize(
            self.power(time, 10, reactive=True, end=True).get("LAS-CAL", 0.0)
        )
        result["NCH-CHU"] = normalize(
            self.power(time, 10, reactive=True, end=True).get("NCH-CHU", 0.0)
        )
        return result
