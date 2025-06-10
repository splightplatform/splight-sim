#GOALS: 
# - develop a script that updates the alitude, cable span, and
#distance_to_next_tower values of the SplightSim line. 
# - Test these scripts and run them on SplighSim 


from tqdm import tqdm
import utils
from splight_lib.models import Asset


def main(): 
    altitude_client = utils.OpenElevationClient()
    all_assets = Asset.list(type__in="Segment")

    asset_dict: dict[str, utils.Tower] = {}
    for asset in tqdm(all_assets, desc="Creating segment dictionary", unit="segments"):
        full_asset = Asset.retrieve(asset.id)
        asset_dict[asset.name] = utils.Tower(full_asset, altitude_client)

    #go through each segment and update the database
    for asset_name in tqdm(asset_dict.keys(), desc="Updating metadata", unit="segments"):
        # print(f"Updating {asset_name}")
        tower = asset_dict[asset_name]
        utils.set_metadata(tower.altitude_id, str(tower.location.alt))
        if tower.next_tower in asset_dict.keys():
            next_tower = asset_dict[tower.next_tower]
            _ = utils.set_metadata(tower.distance_id, str(tower.location.distance_from(next_tower.location)))
            span_length = tower.span_length_from(next_tower)
            _ = utils.set_metadata(tower.span_length_id, str(span_length))
            # utils.set_metadata(tower.span_length_id, "20")
        else:
            _ = utils.set_metadata(tower.distance_id, "0")
            _ = utils.set_metadata(tower.span_length_id, "0")

if __name__ == "__main__":
    main()   

