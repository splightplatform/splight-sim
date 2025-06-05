#GOAL: develop a script that updates the alitude and cable span values
#of the CAL-NCH and CAL-SAL lines. Test these scripts and run them on
#Spligh Sim 


from tqdm import tqdm
import utils
from splight_lib.models import Asset
from splight_lib.settings import workspace_settings


#keys for SplightSim organization 
workspace_settings.SPLIGHT_ACCESS_ID = "A"
workspace_settings.SPLIGHT_SECRET_KEY = "B"


if __name__ == "__main__":
    all_assets = Asset.list(type__in="Segment")
    i = 0

    asset_dict: dict[str, utils.Tower] = {}
    for asset in tqdm(all_assets, desc="Creating segment dictionary", unit="segments"):
        if i < 2: 
            full_asset = Asset.retrieve(asset.id)
            asset_dict[asset.name] = utils.Tower(full_asset)
            i += 1

    #go through each segment and update the database
    j = 0 #guard so that only one segment is updated during testing
    for asset_name in asset_dict.keys():
        if j == 0:
            print(f"Updating {asset_name}")
            tower = asset_dict[asset_name]
            utils.set_metadata(tower.altitude_id, tower.location.alt)
            if tower.next_tower != None:
                next_tower = asset_dict[tower.next_tower]
                _ = utils.set_metadata(tower.distance_id, str(tower.location.distance_from(next_tower.location)))
                span_length = tower.location.span_length_from(next_tower.location, tower.line_height, next_tower.line_height)
                _ = utils.set_metadata(tower.span_length_id, str(span_length))
            else:
                _ = utils.set_metadata(tower.distance_id, "0")
                _ = utils.set_metadata(tower.span_length_id, "0")

            j += 1
        

