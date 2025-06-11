# Splight Simulator

A container to emulate a grid with Ieds from different protocols in one or multiple networks or VPNs.

## Usage

### Build

```bash
docker-compose build
```

### Run

```bash
docker-compose up
```

## Uploading new traces

If you want to upload a new trace, you need to modify the `traces.json` file where you should add to the list a trace definition that looks like the following
```json
{
    "name": "<trace name>",
    "topic": "<topic where you can read your data>",
    "filename": "<filename which stores your data.csv>",
    "noise_factor": 0.1,
    "match_timestamp_by": "<matches the timestamp by this unit ex: minute>",
    "target_value": "<csv column to read>"
}
```

### Example to set "match_timestamp_by" correctly

Let `"match_timestamp_by"` be set to `minute"` this says that your data must define for a date at least 60 seconds which will be looped over. So in this case your csv file should look like the following
```csv
timestamp,col1
2024-01-01 00:00:00+00:00,130.4
2024-01-01 00:01:00+00:00,130.6
2024-01-01 00:02:00+00:00,131.3
2024-01-01 00:03:00+00:00,132.1
...
2024-01-01 00:58:00+00:00,121.3
2024-01-01 00:59:00+00:00,135.1
```
Where you set as many columns as you want to use for the 60 seconds defined.

Now let us suppose we set `"match_timestamp_by"` to `"hour"` then you should set in your csv file a value for every hour and every minute for 1 day.

## Alternative way to upload traces

After code your trace function in scripts/trace_creator.py you need to add the function to the main of the file and run the following command
```bash
make traces
```
This create a new traces files in the respective data directory and update the traces.json file.

## Segment Update

### Setup
`segment_updater` requires access to the splight-lib library. To utilize this library ensure you have properly setup a secret ID and secret key for the organization you wish to update. Add these credentials to your ~/.splight/config file as shown below:  

current_workspace: default
workspaces:
  default:
    SPLIGHT_ACCESS_ID: {accessID}
    SPLIGHT_PLATFORM_API_HOST: https://integrationapi.splight.com
    SPLIGHT_SECRET_KEY: {secretKey}

Also, update your environment to use the correct version using: 

export API_VERSION = v4

Setup is complete

### Run
To run `segment_updater` navigate to the scripts directory and run `python segment_updater.py`. The script will update the `distance_to_next_tower`, `altitude`, and `cable_span` metadata fields on every segment in the organization. 

