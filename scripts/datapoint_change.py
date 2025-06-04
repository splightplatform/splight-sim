from splight_lib.models import Asset, Alert 
from splight_lib.settings import workspace_settings
import util 

workspace_settings.SPLIGHT_ACCESS_ID = "89d27d63-a630-4a4e-bd50-d6bdd95104b7"
workspace_settings.SPLIGHT_SECRET_KEY = "82bd81b7182ec2b5bfef069b0371f3b4701c3cdc6d9e522b52db32db8e03955a"

# workspace_settings.SPLIGHT_ACCESS_ID = "89d27d63-a630-4a4e-bd50-d6bdd95104b7"
# workspace_settings.SPLIGHT_SECRET_KEY = "82bd81b7182ec2b5bfef069b0371f3b4701c3cdc6d9e522b52db32db8e03955a"

if __name__ == "__main__":
    all_assets = Asset.list()
    # print(all_assets)
    segment_assets = [item for item in all_assets if item.kind.name == "Segment"]
    LUT = segment_assets[0]
    LUT_name = LUT.name
    LUT_id = LUT.id
    print(f"Name: {LUT_name}, ID: {LUT_id}")
    LUT_alt_id = util.get_metadata("altitude", LUT_id)
    print(f"Name: {LUT_name}, ID: {LUT_id}, Alt_id: {LUT_alt_id}")
    util.set_metadata(LUT_alt_id, str(50))


    # LUT_dict = full_asset.get_model_files_dict()
    # print(LUT_dict)
    # for data in full_asset.metadata:
    #     if data.name == "altitude":
    #         print(data)
    #         print(data.value)
    #         data.value = 50 
    #         print(data.value)
    # full_asset.save()
    # print(full_asset)

    # asset_dict: dict[str, dict] = {}
    #get segements 
    # print(all_assets[0])
    # print(all_assets[1])
    # print(all_assets[2])
    # for asset in all_assets:
    #     full_asset = Asset.retrieve(asset.id)
    #     asset_dict[asset.name] = {
    #         "id": asset.id
    #         # "location": get_location(asset)
    #         # "next_tower": get_next(asset.name)
    #     }