# osmand_map_creation
Osm data + open address data compiled for use in OSMAND
# Targets
- WA state
  - Counties
    - Clark
    - King
    - Pierce
    - Snohomish
    - Spokane
    - Thurston

# Usage
Option 1:  
Download file from releases to data folder for OSMAND and it will auto load.  
Option 2:  
Download file from releases to phone and open it. OSMAND will copy file into its data folder and load it.
This will leave a copy of the file in the Downloads folder.

Deactivate the default WA map file to ensure search pulls results from this file.
# Sources
Osm format sources prior to merge are supplied. The merged file is not supplied since its larger Github's max file size. 
Osmium merge is used to merge supplied sources with latest washington extract before being compiled to OSMAND format.
# License
ODBL 1.0
