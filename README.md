# osmand_map_creation
OpenStreetMap(OSM) data + OpenAddresses(OA) data compiled for use in OSMAND
# Targets
US, addresses added based on [OpenAddresses](https://openaddresses.io/)
# Usage
Option 1:  
Download file from releases to data folder for OSMAND and it will auto load.  
Option 2:  
Download file from releases to phone and open it. OSMAND will copy file into its data folder and load it.
This will leave a copy of the file in the Downloads folder.

Deactivate the default WA map file to ensure search pulls results from this file.  
Restart app after changes otherwise search may not work properly. Restarting is done 
by opening recent apps and flicking upward on app in Android 9.

# Data
OpenAddresses provides data downloads at (http://results.openaddresses.io/).  
OpenStreetMap extracts retrieved from (https://download.geofabrik.de)

# Processing
## Processing.py
OA data is loaded into Postgresql, filtered with sql, exported to osm xml format and merged with OSM state extracts while converting to osm.pbf. See docs/processing_script_usage and processing.py file.
## OSMAnd
Move files to osmand_osm folder and run OSMAnd Map Creator. See [OSMAnd Map Creator Wiki](https://wiki.openstreetmap.org/wiki/OsmAndMapCreator) for help.

# License
Map Files:[ODBL 1.0](https://opendatacommons.org/files/2018/02/odbl-10.txt)  
Code:TBD
