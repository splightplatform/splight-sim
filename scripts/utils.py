
from __future__ import annotations
import requests
import re
import haversine as hs 

class Location: 
    def __init__(self, latitude: float, longitude: float):
        self.lat = latitude
        self.long = longitude
        self.alt = self.get_altitude() 

    def get_altitude(self):
        url = f"https://api.open-elevation.com/api/v1/lookup"
        response = requests.get(url, params={"locations": f"{self.lat},{self.long}"})
        altitude = response.json()["results"][0]["elevation"]

        if altitude is None:
            error = response.json().get("status", {}).get("message", "Unknown error")
            raise ValueError(f"Error in response: {error}")

        if altitude < 0:
            raise ValueError(f"Negative altitude received: {altitude}")
        return altitude
    
    def distance_from(self, other_loc: Location) -> float:
        loc1 = (self.lat,self.long)
        loc2 = (other_loc.lat,other_loc.long)
        return hs.haversine(loc1,loc2,unit=hs.Unit.METERS)

    def span_length_from(self, other_loc: Location, this_line_height: float, other_line_height: float) -> float:
        # span_length^2 = distance^2 + diff_in_altitude^2
        diff_in_altitude = abs((self.alt + this_line_height) - (other_loc.alt + other_line_height))
        # print(f"Alt1: {self.alt}, Alt2: {other_loc.alt}, LH1: {this_line_height}, LH2: {other_line_height} ")
        distance = self.distance_from(other_loc)
        span_length_sq = (diff_in_altitude ** 2) + (distance ** 2)
        # print(f"Alt diff: {diff_in_altitude}, distance: {distance}, span_2: {span_length_sq}")
        return span_length_sq ** (1/2)

class Tower:
    def __init__(self, full_asset):
        self.id = full_asset.id
        self.location = get_location(full_asset)
        self.next_tower = get_next_tower(full_asset.name)
        self.altitude_id = get_metadata_id(full_asset, "altitude")
        self.distance_id = get_metadata_id(full_asset, "distance_to_next_tower")
        self.span_length_id = get_metadata_id(full_asset, "span_length")
        self.line_height = get_metadata_value(full_asset, "line_height")

def get_location(asset) -> Location:
    #coordinates saved as (long, lat) instead of the standard (lat, long)
    coordinates = asset.centroid_coordinates
    return Location(coordinates[1],coordinates[0])

def get_next_tower(asset_name: str) -> str:
    #assumes segment 0 is connected to segement 1 i.e. segements created in order they are connected
    # TODO: add to segment kind the next next segment's ID
    match = re.search(r'([^-]+-[^-]+)-(\d+)',asset_name)
    if match:
        prefix = match.group(1)
        number = int(match.group(2))
        next = prefix + "-" + f"{int(number)+1}"
        return next
    else: return "None" 

def get_metadata_id(full_asset, metadata_name):
    all_metadata = full_asset.metadata
    for entry in all_metadata:
        if entry.name == metadata_name:
            return entry.id
    raise ValueError(f"Metadata: {metadata_name} not found in asset: {full_asset.id}")

def get_metadata_value(full_asset, metadata_name):
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
