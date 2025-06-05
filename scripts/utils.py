
from __future__ import annotations
import requests
import re
import haversine as hs 
import numpy as np
from splight_lib.models import Asset, SplightDatabaseBaseModel

OPEN_ELEVATION_URL = "https://api.open-elevation.com/api/v1/lookup"

class OpenElevationClient:
    def __init__(self, url: str = OPEN_ELEVATION_URL):
        self.url = url
    
    def get_altitude(self, lat: float, lng: float) -> float:
        response = requests.get(self.url, params={"locations": f"{lat},{lng}"})
        altitude = response.json()["results"][0]["elevation"]
        if altitude is None:
            error = response.json().get("status", {}).get("message", "Unknown error")
            raise ValueError(f"Error in response: {error}")

        if altitude < 0:
            raise ValueError(f"Negative altitude received: {altitude}")
        return altitude

class Location: 
    def __init__(self, latitude: float, longitude: float, altitude: float):
        self.lat = latitude
        self.lng = longitude
        self.alt = altitude 

    def distance_from(self, other_loc: Location) -> float:
        loc1 = (self.lat,self.lng)
        loc2 = (other_loc.lat,other_loc.lng)
        return hs.haversine(loc1,loc2,unit=hs.Unit.METERS)

class Tower:
    def __init__(self, full_asset: SplightDatabaseBaseModel = None, client: OpenElevationClient = None):
        if full_asset and client:
            self.create_from(full_asset, client)
        else:
            self.create_for_test()
        
    def create_from(self, full_asset: SplightDatabaseBaseModel, client: OpenElevationClient):
        self.id = full_asset.id
        self.location = get_location(full_asset, client)
        self.next_tower = get_next_tower(full_asset.name)
        metadata_dict = {meta.name: meta for meta in full_asset.metadata}
        # self.altitude_id = get_metadata_id(full_asset, "altitude")
        self.altitude_id = metadata_dict["altitude"].id
        self.distance_id = metadata_dict["distance_to_next_tower"].id
        self.span_length_id = metadata_dict["span_length"].id
        self.line_height = metadata_dict["line_height"].value
    
    def create_for_test(self):
        self.id = "the-test-0"
        self.location = None
        self.next_tower = "the-test-1"
        self.altitude_id = 0
        self.distance_id = "distance_id"
        self.span_length_id = "span_id"
        self.line_height = 35

    def span_length_from(self, other_tower: Tower) -> float: 
            # span_length^2 = distance^2 + diff_in_altitude^2
            diff_in_altitude = abs((self.location.alt + self.line_height) - (other_tower.location.alt + other_tower.line_height))
            distance = self.location.distance_from(other_tower.location)
            span_length_sq = (diff_in_altitude ** 2) + (distance ** 2)
            return np.sqrt(span_length_sq)

def get_location(asset: SplightDatabaseBaseModel, client: OpenElevationClient) -> Location:
    #coordinates saved as (long, lat) instead of the standard (lat, long)
    lng, lat = asset.centroid_coordinates
    return Location(lat, lng, client.get_altitude(lat, lng))

def get_next_tower(asset_name: str) -> str | None:
    #assumes segment 0 is connected to segement 1 i.e. segements created in order they are connected
    # TODO: add to segment kind the next segment's ID
    match = re.search(r'([^-]+-[^-]+)-(\d+)',asset_name)
    if match:
        prefix = match.group(1)
        number = int(match.group(2))
        next = prefix + "-" + f"{int(number)+1}"
        return next
    else: return None 

def get_metadata_id(full_asset: SplightDatabaseBaseModel, metadata_name: str) -> str:
    all_metadata = full_asset.metadata
    for entry in all_metadata:
        if entry.name == metadata_name:
            return entry.id
    raise ValueError(f"Metadata: {metadata_name} not found in asset: {full_asset.id}")

def get_metadata_value(full_asset: Asset, metadata_name: str):
    all_metadata = full_asset.metadata
    for entry in all_metadata:
        if entry.name == metadata_name:
            return entry.value
    raise ValueError(f"Metadata for {metadata_name} not found in asset: {full_asset.id}")


headers = {
    "Authorization": "Splight 89d27d63-a630-4a4e-bd50-d6bdd95104b7 82bd81b7182ec2b5bfef069b0371f3b4701c3cdc6d9e522b52db32db8e03955a"
}

host = "https://integrationapi.splight.com"

def get_metadata(metadata_name: str, asset_id: str) -> str:
    """
    returns: the value of the metadata with the given name for the asset with the given id
    """
    url = f"{host}/v4/engine/asset/assets/{asset_id}/"
    response = requests.get(
        url,
        headers=headers
    )
    assert response.status_code == 200, f"Failed to get metadata for {metadata_name} on asset {asset_id}"
    metadatas = response.json().get("metadata", {})
    for metadata in metadatas:
        if metadata["name"] == metadata_name:
            print(metadata)
            return metadata["id"]
    raise ValueError(f"Metadata {metadata_name} not found for asset {asset_id}")

def set_metadata(metadata_id, value: str) -> str:
    """
    returns: the value of the metadata after setting it
    """
    url = f"{host}/v4/engine/asset/metadata/{metadata_id}/set/"
    response = requests.post(
        url,
        headers=headers,
        json={"value": value}
    )
    # print(f"Status Code: {response.status_code}")
    assert response.status_code == 200, f"Failed to set metadata: {response.text}"
    return value
