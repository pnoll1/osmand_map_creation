# Linux Install
Edit setup.sh, if not using defaults
Run setup.sh
Edit config.py if not using defaults

# Script Usage
Configuration is done in config.py, processing.py contains the code. The script can be run from the command line or using batches from config.py. Each argument targets an iso3166-2(us:wa) or iso3166-1-alpha2(us) area except for update-oa which targets all urls in oa_urls(several GBs worth of data). Update-oa takes a long time so you may want to run it separately or download the files yourself if only building areas in one region. You must have OA data and a OSM area extract for the script to work properly.

cli usage is best for testing or one off builds: 
- ./processing.py --all us:wa

config usage:
- edit config.py 
  - fill in batches e.g. ['--update-oa', '--normal us:wa us:or us:id']
  - fill in Xmx with max amount of memory you can give (Extra ram will speed up builds)
- ./processing.py

# Data Processing
Add sql statements in the filter_data function to remove unwanted records  
Add to sql statements to --sql flag in ogr2osm calls to filter data without removing records

# Troubleshooting builds
If builds fail, try increasing Xmx. If that doesn't work, add a slice_config to break the area into smaller pieces. Log files from osmand_map_creator are in the osmand_obf folder with the obf.gen.log suffix. 

If data doesn't show up in finished builds check processing.py logs in osm folder. This often means unicode control characters were still in the source data after filtering. Processing.py stops processing a source once it hits a unicode control character.

# Limitations
Command line arguments are only used if batches is an empty list.
Not all options are avaiable from cli and config file 
Requires Geofabrik to have extract for area
Requires OpenAddresses to have data for area
iso3166-1-alpha2 areas are only supported if there are no iso3166-2 Geofabrik extracts eg. mx
No deduplication
Running many areas with update-osm may result in Geofabrik rate limiting  
ogr2osm xml writer will choke on unicode stops
