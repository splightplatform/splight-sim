import pytest

from scripts import utils


class TestAltitudeClient:
    @pytest.mark.parametrize(
        ("lat", "lng", "expected"),
        (
            (37.805, -122.40472, 10),
            (-22.428174, -68.921705, 2270),
            (-22.380, -68.930, 2478),
        ),
    )
    def test_get_altitude(self, lat, lng, expected, altitude_client):
        assert altitude_client.get_altitude(lat, lng) == pytest.approx(expected, 0.05)


class TestLocation:
    def test_distance_calc(self):
        golden_gate = utils.Location(37.8199, -122.4786, 0.0)
        coit_tower = utils.Location(37.802402, -122.405952, 50.0)
        distance = golden_gate.distance_from(coit_tower)
        assert distance == pytest.approx(6700, 0.05)

    def test_distance_calc2(self):
        tower1 = utils.Location(-22.380, -68.930, 2478)
        tower2 = utils.Location(-22.377, -68.931, 2501)
        distance = tower1.distance_from(tower2)
        assert distance == pytest.approx(347.8, 0.05)

    def test_distance_zero(self):
        loc = utils.Location(37.805, -122.40472, 10.0)  # Splight SF office
        assert loc.distance_from(loc) == pytest.approx(0, abs=0.001)


class TestTower:
    def test_span_length_diff_heights(self):
        golden_gate_tower = utils.Tower()
        golden_gate_tower.location = utils.Location(37.8199, -122.4786, 0)
        coit_tower_tower = utils.Tower()
        coit_tower_tower.location = utils.Location(37.802402, -122.405952, 500)
        span = golden_gate_tower.span_length_from(coit_tower_tower)
        assert span == pytest.approx(6718.6, 0.05)

    def test_span_length2(self):
        cal0_tower = utils.Tower()
        cal0_tower.location = utils.Location(-22.428174, -68.921705, 2276)
        cal1_tower = utils.Tower()
        cal1_tower.location = utils.Location(-22.427552, -68.921585, 2276)
        span = cal0_tower.span_length_from(cal1_tower)
        assert span == pytest.approx(70.25, 0.05)


class TestUtils:
    @pytest.mark.parametrize(
        ("input_n", "expected"),
        (
            ("CAL-NCH-0", "CAL-NCH-1"),
            ("CAL-NCH-10", "CAL-NCH-11"),
            ("VLV-CAL-45", "VLV-CAL-46"),
            ("CAL-SAL-15", "CAL-SAL-16"),
            ("JAM-LAS-7", "JAM-LAS-8"),
        ),
    )
    def test_get_next_tower(self, input_n, expected):
        assert utils.get_next_tower(input_n) == expected
