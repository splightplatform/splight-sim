import requests
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
    print(f"Status Code: {response.status_code}")
    assert response.status_code == 200, f"Failed to set metadata: {response.text}"
    # return response.json()["value"]