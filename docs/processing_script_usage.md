# Linux Install
Download setup_app.sh and setup_container.sh. Run setup_container.sh and get shell access by running incus exec omc -- bash.

# Script Usage
Configuration is done in config.py, processing.py is the entry point for code. The script can be run from the command line or using batches from config.py. Each argument targets an iso3166-2(us:wa) or iso3166-1-alpha2(us) area. You'll need to download data from OA in browser and upload to container using incus file push. You must have OA data and a OSM area extract for the script to work properly.

cli usage is best for testing or one off builds: 
- ./processing.py --normal us:wa

config usage:
- edit config.py 
  - fill in batches e.g. ['--normal us:wa us:or us:id', '--normal ca']
  - fill in Xmx with max amount of memory you can give (Extra ram will speed up builds)
- env/bin/python processing.py

# Data Processing
Add sql statements in the filter_data function to remove unwanted records before reaching database
Add sql statement in datasource.set_query to filter data without removing records

# Troubleshooting builds
If builds fail, try increasing Xmx and/or running a smaller batch. If that doesn't work, add a slice_config to break the area into smaller pieces. Log files from osmand_map_creator are in the osmand_obf folder with the obf.gen.log suffix. 

If data doesn't show up in finished builds check processing.py logs in logs folder. This often means unicode control characters were still in the source data after filtering. Processing.py stops processing a source once it hits a unicode control character.

# Limitations
Not all options are avaiable from cli and config file  
Requires Geofabrik to have extract for area  
Requires OpenAddresses to have data for area  
iso3166-1-alpha2 areas are only supported if there are no iso3166-2 Geofabrik extracts eg. mx  
No deduplication  
Running many areas with update-osm may result in Geofabrik rate limiting  
ogr2osm xml writer will choke on unicode stops
can't download OA data directly
