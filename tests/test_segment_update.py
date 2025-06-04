import pytest
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts')))

import segment_update as obj

class Test_Location:
    def test_distance_calc(self):
        golden_gate = obj.Location(37.8199, -122.4786)
        coit_tower = obj.Location(37.802402, -122.405952)
        distance = golden_gate.distance_from(coit_tower)
        #true calced using calculator.net 
        assert distance == pytest.approx(6700,0.05)

    def test_distance_zero(self):
        loc = obj.Location(37.805, -122.40472) #Splight SF office
        assert loc.distance_from(loc) == 0 
    
    def test_get_altitude(self):
        loc = obj.Location(37.805, -122.40472)
        altitude = loc.get_altitude()
        # print(altitude)
        assert altitude == pytest.approx(10, 0.1)
    
    def test_span_length(self):
        golden_gate = obj.Location(37.8199, -122.4786)
        coit_tower = obj.Location(37.802402, -122.405952)
        span = golden_gate.span_length_from(coit_tower, 0, 500)
        assert span == pytest.approx(6718.6, 0.05)

    # def test_determine_tif_filename(self):
    #     loc = obj.Location(37.805, -122.40472)
    #     filename = loc.determine_tif_filename()
    #     print(filename)
    #     assert filename == f"srtm_37.5_-122.5_38.5_-121.5.tif"
    
    # def test_download_tif(self, srtm_path): 
    #     loc = obj.Location(37.805, -122.40472)
    #     filename = f"srtm_37.5_-121.5_38.5_-122.5.tif"
    #     tif_path = Path(srtm_path / filename)
    #     # print(str(tif_path))
    #     loc.download_tif(tif_path)
    #     assert tif_path.is_file()

    # def test_get_altitude_from_tif(self, srtm_path): 
    #     loc = obj.Location(37.805, -122.40472)
    #     filename = f"srtm_37.5_-121.5_38.5_-122.5.tif"
    #     alt = loc.get_altitude_from_tif(srtm_path / filename)
    #     print(alt)
    #     assert 1 == 1




    # def test_span_altitude_lookup(self):
    #     #truth from freemaptools.com & Google Earth
    #     splight_office = obj.Location(37.805, -122.4047)
    #     assert splight_office.alt == pytest.approx(10,0.05)

        

