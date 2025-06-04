#GOAL: develop a script that updates the alitude and cable span values
#of the CAL-NCH and CAL-SAL lines. Test these scripts and run them on
#Spligh Sim 
from __future__ import annotations

import haversine as hs
import requests
# import pvlib.location as pv
# import pyhigh 
import numpy as np
from pathlib import Path
import rasterio
import subprocess

from splight_lib.models import Asset, Alert 
from splight_lib.settings import workspace_settings

# TODO ask mariano why this is not using or considering the file .splight/config
#keys for Splight organization 
# workspace_settings.SPLIGHT_ACCESS_ID = "14c0f032-a263-4465-8577-c06bbcc77c9f"
# workspace_settings.SPLIGHT_SECRET_KEY = "7d3978bebc90b246818b55edb4fce5d1a891b11d97e528335b755dc551a3c958"

workspace_settings.SPLIGHT_ACCESS_ID = "89d27d63-a630-4a4e-bd50-d6bdd95104b7"
workspace_settings.SPLIGHT_SECRET_KEY = "82bd81b7182ec2b5bfef069b0371f3b4701c3cdc6d9e522b52db32db8e03955a"
#keys for SplightSim organization 

class Location: 
    def __init__(self, latitude: float, longitude: float):
        self.lat = latitude
        self.long = longitude
        self.alt = self.get_altitude() 
    
    # def get_altitude(self, latitude: float, longitude: float) -> float:
    #     api_url = "http://api.geonames.org/srtm3JSON"
    #     params = {"lat": latitude, "lng": longitude, "username": "pablomamani"}
    #     response = requests.get(api_url, params=params)
    #     response.raise_for_status()
    #     data = response.json()
    #     altitude = data.get("srtm3", None)
    #     return altitude

    def get_altitude(self):
        url = f"https://api.open-elevation.com/api/v1/lookup"
        response = requests.get(url, params={"locations": f"{self.lat},{self.long}"})
        return response.json()["results"][0]["elevation"]
    
    # def determine_altitude(self):
    #     needed_tif_filename = self.determine_tif_filename()
    #     tif_path  = Path(__file__).resolve().parent / "scripts/srtm" / needed_tif_filename
    #     if(tif_path.is_file()):
    #         return self.get_altitude_from_tif(tif_path)
    #     else: 
    #         self.download_tif(tif_path)
    #         return self.get_altitude_from_tif(tif_path)
    
    # def download_tif(self, tif_path: Path) -> Path: 
    #     cmd = [ "eio", "clip", "--bounds", str(self.min_long), str(self.min_lat), 
    #         str(self.max_long), str(self.min_lat), "--output", str(tif_path) ]
    #     subprocess.run(cmd, check=True)
    #     return tif_path

    # def get_altitude_from_tif(self, tif_path: Path):
    #     with rasterio.open(tif_path) as src: 
    #         coordinates = [(self.lat, self.long)]
    #         altitude = list(src.sample(coordinates))[0][0]
    #         return altitude

    # def determine_tif_filename(self) -> str:
    #     return f"srtm_{self.min_lat:.1f}_{self.min_long:.1f}_{self.max_lat:.1f}_{self.max_long:.1f}.tif"

    def distance_from(self, other_loc: Location) -> float:
        loc1 = (self.lat,self.long)
        loc2 = (other_loc.lat,other_loc.long)
        return hs.haversine(loc1,loc2,unit=hs.Unit.METERS)

    def span_length_from(self, other_loc: Location, this_tower_height: float, other_tower_height: float) -> float:
        # span_length^2 = distance^2 + diff_in_altitude^2
        diff_in_altitude = abs((self.alt + this_tower_height) - (other_loc.alt + other_tower_height))
        distance = self.distance_from(other_loc)
        span_length_sq = (diff_in_altitude ** 2) + (distance ** 2)
        return span_length_sq ** (1/2)


if __name__ == "__main__":
    all_assets = Asset.list()

    #create a dict with each assets id, name, and next_tower
    asset_dict: dict[str, dict] = {}
    for asset in all_assets:
        full_asset = Asset.retrieve(asset.id)
        asset_dict[asset.name] = {
            "id": asset.id
            # "location": get_location(asset)
            # "next_tower": get_next(asset.name)

        }

    print(f"Len assets: {len(all_assets)}, len asset_dict: {len(asset_dict)}")

    i = 0 
    for asset in all_assets:
            if asset.kind.name == 'Segment' and i < 1:
                id = asset.id
                print(asset)
                # single = Asset.retrieve(id)
                single = Asset.retrieve(id)
                for item in single.metadata:
                    print(item.name)
                i += 1
            # i += 1
    # print(all_assets)