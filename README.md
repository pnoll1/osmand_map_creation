# OpenSuperMaps
## What
OSMAnd Map files distributed monthly with tens of millions of addresses added
## Why
OSMAnd address search is painful and it doesn't have to be. These files allow searching for addresses normally again. This means you can copy/paste addresses from friends or websites!  
Before: 4th Avenue 600 Seattle  
After: 600 4th Ave Seattle

You get a huge upgrade in coverage. No more guessing if an address exists, no more web searches for addresses!

## When
Files posted around the 26th ewvery month
## How
Data is added from OpenAddresses. OpenAddresses collates hundreds of millions of addresses from government sources and uses the normal abbreviated address format.
## Where
OSMAnd Files: North America(but slowly expanding)  
Script: Worldwide depending on [GeoFabrik](https://download.geofabrik.de) and [OpenAddresses](https://openaddresses.io/) data availability
# Usage
## Getting the map files
Option 1:  
Download file from [releases](https://github.com/pnoll1/osmand_map_creation/releases) to data folder for OSMAND and it will auto load.  
Option 2:  
Download file from [releases](https://github.com/pnoll1/osmand_map_creation/releases) to phone and open it. OSMAND will copy file into its data folder and load it.
This will leave a copy of the file in the Downloads folder.

Deactivate the default map file(s) to ensure search pulls results from this file.  
Restart app after changes otherwise search may not work properly. Restarting is done 
by opening recent apps and flicking upward on app in Android.
## Searching for addresses
Search using the normal address format: 600 4th Ave Seattle

# Processing
## Data
OpenAddresses provides data downloads at https://results.openaddresses.io/  
[OpenStreetMap](https://openstreetmap.org) extracts retrieved from [GeoFabrik](https://download.geofabrik.de)
## Processing.py
OA data is loaded into Postgresql, filtered with sql, exported to osm xml format and merged with OSM area extracts while converting to osm.pbf. See docs/processing_script_usage and processing.py file.
## OSMAnd
Run OSMAnd Map Creator after processing.py. See [OSMAnd Map Creator Wiki](https://wiki.openstreetmap.org/wiki/OsmAndMapCreator) for help.

# License
Map Files:[ODBL 1.0](https://opendatacommons.org/files/2018/02/odbl-10.txt)  
Code:TBD
