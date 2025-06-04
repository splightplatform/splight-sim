import pytest
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts')))

import utils 

class Test_Location:
    def test_distance_calc(self):
        golden_gate = utils.Location(37.8199, -122.4786)
        coit_tower = utils.Location(37.802402, -122.405952)
        distance = golden_gate.distance_from(coit_tower)
        #true calced using calculator.net 
        assert distance == pytest.approx(6700,0.05)

    def test_distance_zero(self):
        loc = utils.Location(37.805, -122.40472) #Splight SF office
        assert loc.distance_from(loc) == 0 
    
    def test_get_altitude(self):
        loc = utils.Location(37.805, -122.40472)
        altitude = loc.get_altitude()
        print(altitude)
        assert altitude == pytest.approx(10, 0.1)
    
    def test_get_altitude_south_america(self):
        loc = utils.Location(-22.428174, -68.921705)
        altitude = loc.get_altitude()
        assert altitude == pytest.approx(2270, 0.05)

    def test_span_length(self):
        golden_gate = utils.Location(37.8199, -122.4786)
        coit_tower = utils.Location(37.802402, -122.405952)
        span = golden_gate.span_length_from(coit_tower, 0, 500)
        assert span == pytest.approx(6718.6, 0.05)

    def test_span_length(self):
        cal1 = utils.Location(-22.427552, -68.921585)
        cal0 = utils.Location(-22.428174, -68.921705)
        span = cal0.span_length_from(cal1, 2276, 2276)
        assert span == pytest.approx(70.25,0.05)
    
    @pytest.mark.parametrize(
            ('input_n', 'expected'),
            (
                ("CAL-NCH-0", "CAL-NCH-1"),
                ("CAL-NCH-10", "CAL-NCH-11"),
                ("VLV-CAL-45", "VLV-CAL-46"),
                ("CAL-SAL-15", "CAL-SAL-16"),
                ("JAM-LAS-7", "JAM-LAS-8")
            )
    )
    def test_get_next_tower(self, input_n, expected):
        assert utils.get_next_tower(input_n) == expected



