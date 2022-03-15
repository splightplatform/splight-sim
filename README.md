# Grid Simulator #
A container to emulate a grid with Ieds from different protocols in one or multiple networks or VPNs.

Available protocols:

* __DNP3__
* __C37.118__
* __IEC61850__
* __IEC60870-5__

Available VPNs:
* __OpenVpn__
  * File auth
  * File + credentials auth

## Usage ##

First you have to create a configuration file named `network.json` on a directory named `data` in the repository root (`/data/network.json`).  
And then you can build and run.

### Configuration ###

The configuration file format is the following:
```json
{
  "vpns": [
    {
      "file": [str],               # OpenVpn file
      "ns":   [str],               # Name of the namespace where connect the VPN
      "user": [str] (optional),    # Username of the VPN
      "pass": [str] (optional)     # Password of the VPN
    }
  ],
  
  "ieds": [
    {
        "protocol": [dnp3 | iec61850 | iec60870 | c37118],    # Protocol of the IED
        "port":     [int],                                    # Port of where to bind the IED
        "ns":       [str] (optional)                          # Namespace of the VPN
                                                              # If not setted, uses the localhost
    }
  ]
}

```

### Build ###
```bash
docker-compose build
```

### Run ###
```bash
docker-compose up
```
