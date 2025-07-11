from datetime import datetime

from generic import GridDefinition
from utils import noise, solar_gaussian

ASSETS: dict[str, str] = {
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


def power(time: datetime, peak_power: float, end: bool = False, reactive: bool = False):
    peak_power *= -0.93 if end else 1
    peak_power *= 0.08 if reactive else 1
    delta_vlv = -1.4
    delta_aza = 1.3
    delta_cal = 1.7
    delta_usy = -1.6

    # Calama Grid
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
    se_cal = pfv_usya + pfv_azabache + pe_calama + las_cal - noise(peak_power * 2 * 0.1)
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


class CalamaGrid(GridDefinition):
    @property
    def name(self) -> str:
        return "Calama"

    @property
    def assets(self) -> dict[str, str]:
        return ASSETS

    def get_value(self, asset: str, attr: str, time: datetime):
        # Custom value functions for specific assets
        if (
            asset in ["PFVJama", "PFVSanPedro", "PFVAzabache", "PFVUsya"]
            and attr == "active_power"
        ):
            return power(time, 10).get(asset, 0.0)
        elif (
            asset in ["PFVJama", "PFVSanPedro", "PFVAzabache", "PFVUsya"]
            and attr == "available_active_power"
        ):
            return power(time, 20).get(asset, 0.0)
        elif (
            asset in ["PFVJama", "PFVSanPedro", "PFVAzabache", "PFVUsya"]
            and attr == "power_set_point"
        ):
            return power(time, 11).get(asset, 0.0)
        elif asset in ["PEValleDeLosVientos", "PECalama"] and attr == "active_power":
            return power(time, 10).get(asset, 0.0)
        elif (
            asset in ["PEValleDeLosVientos", "PECalama"]
            and attr == "available_active_power"
        ):
            return power(time, 20).get(asset, 0.0)
        elif asset in ["PEValleDeLosVientos", "PECalama"] and attr == "power_set_point":
            return power(time, 11).get(asset, 0.0)
        elif asset in ["PEValleDeLosVientos", "PECalama"] and attr == "frequency":
            return 50.0
        elif asset in ["PEValleDeLosVientos", "PECalama"] and attr == "switch_status":
            return "true"
        elif asset in [
            "CAL-NCH",
            "CAL-SAL",
            "SAL-CHU",
            "VLV-CAL",
            "JAM-LAS",
            "LAS-CAL",
            "NCH-CHU",
        ] and attr in ["active_power_start", "active_power_end"]:
            return power(time, 10, end=attr.endswith("_end")).get(asset, 0.0)
        elif asset in [
            "CAL-NCH",
            "CAL-SAL",
            "SAL-CHU",
            "VLV-CAL",
            "JAM-LAS",
            "LAS-CAL",
            "NCH-CHU",
        ] and attr in ["reactive_power_start", "reactive_power_end"]:
            return power(time, 10, reactive=True, end=attr.endswith("_end")).get(
                asset, 0.0
            )
        elif (
            asset
            in [
                "SEValleDeLosVientos",
                "SEJama",
                "SELasana",
                "SECalama",
                "SENuevaChuquicamata",
                "SESalar",
                "SEChuquicamata",
            ]
            and attr == "active_power"
        ):
            return power(time, 10).get(asset, 0.0)
        elif (
            asset
            in [
                "SEValleDeLosVientos",
                "SEJama",
                "SELasana",
                "SECalama",
                "SENuevaChuquicamata",
                "SESalar",
                "SEChuquicamata",
            ]
            and attr == "reactive_power"
        ):
            return power(time, 10, reactive=True).get(asset, 0.0)
        # Default values for other attributes
        else:
            return self.default_value(attr)


# Export the class
CalamaGrid = CalamaGrid
