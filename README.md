# OpenSuperMaps
## What
OSMAnd Map files distributed monthly with tens of millions of addresses added
## Why
OSMAnd address search is painful and it doesn't have to be. These files allow searching for addresses normally again. This means you can copy/paste addresses from friends or websites!  
Before: 4th Avenue 600 Seattle  
After: 600 4th Ave Seattle

You get a huge upgrade in coverage. No more guessing if an address exists, no more web searches for addresses!

## When
Files posted around the 26th every month
## How
Data is added from OpenAddresses. OpenAddresses collates hundreds of millions of addresses from government sources and uses the normal abbreviated address format.
## Where
OSMAnd Files: AU, BE, CA, FR, MX, US  
Script: Worldwide depending on [GeoFabrik](https://download.geofabrik.de) and [OpenAddresses](https://openaddresses.io/) data availability
# Usage
## Getting the map files
Option 1:  
Download file from [opensupermaps.com](https://opensupermaps.com/) to data folder for OSMAND and it will auto load.  
Option 2:  
Download file from [opensupermaps.com](https://opensupermaps.com/) to phone and open it. OSMAND will copy file into its data folder and load it.
This will leave a copy of the file in the Downloads folder.

Deactivate the default map file(s) to ensure search pulls results from this file.  
Restart app after changes otherwise search may not work properly. Restarting is done 
by opening recent apps and flicking upward on app in Android.
## Searching for addresses
Search using the normal address format: 600 4th Ave Seattle

# Processing
## Data
OpenAddresses provides data downloads at https://batch.openaddresses.io/  
[OpenStreetMap](https://openstreetmap.org) extracts retrieved from [GeoFabrik](https://download.geofabrik.de)
## Processing.py
OA data is loaded into Postgresql, filtered with sql, exported to osm xml format and merged with OSM area extracts while converting to osm.pbf. See docs/processing_script_usage and processing.py file.

# Contributing
## Code
Contributors welcome! It's recommended to open an [issue](https://github.com/pnoll1/osmand_map_creation/issues) with the idea first. See docs/development.md.

## Building a new area
If there's an area you want added, please open an [issue](https://github.com/pnoll1/osmand_map_creation/issues/new?assignees=pnoll1&labels=Area+Request&template=area-request.md&title=) Any area that has OpenAddresses coverage is welcome.

## Problems, Bug reports
Open an [issue](https://github.com/pnoll1/osmand_map_creation/issues/new?assignees=pnoll1&labels=bug&template=bug_report.md&title=). 
# License
Map Files:[ODBL 1.0](https://opendatacommons.org/licenses/odbl/1-0/)  
Code: GPLv3
