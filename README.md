# osmand_map_creation
Osm data + open address data compiled for use in OSMAND and Maps.me
# Targets
- WA state
  - Counties
    - Clark
    - Cowlitz
    - Franklin
    - King
    - Kitsap
    - Pierce
    - Skagit
    - Snohomish
    - Spokane
    - Thurston
    - Whatcom
  - Cities
    - Kennewick
- ID
  - Counties
    - Ada
    - Canyon
    - Kootenai

- OR
  - Counties
    - Deschutes
    - Jackson
    - Lane
    - Marion
  - Counties OSM already has
    - Clackamas
    - Multonomah
    - Washington
# Usage
## OSMAnd
Option 1:  
Download file from releases to data folder for OSMAND and it will auto load.  
Option 2:  
Download file from releases to phone and open it. OSMAND will copy file into its data folder and load it.
This will leave a copy of the file in the Downloads folder.

Deactivate the default WA map file to ensure search pulls results from this file.  
Restart app after changes otherwise search may not work properly. Restarting is done 
by opening recent apps and flicking upward on app in Android 9.

## Maps.me
Copy files to MapsWithMe folder on phone. Move, rename or delete map files that will conflict. They are in a dated folder i.e. 191019. Restart app for changes to take effect.

# Sources
Osm format sources prior to merge are supplied. The merged file is not supplied since its larger Github's max file size. 
Osmium merge is used to merge supplied sources with latest state extract before being compiled to OSMAND/Maps.me format. Osmium sort is required before building with Maps.me. Run osmium sort then osmconvert --fake-version if you want to open files with josm.
# License
ODBL 1.0
