# Linux Install
Put processing.py in directory where OpenAddresses download will be unzipped  
Install ogr2ogr, osmium, postgresql, postgis, ogr2osm from github(install in /opt)  
apt-get install curl osmium-tool postgresql postgis gdal-bin python3-gdal python3-lxml git  
cd /opt  
git clone --recursive https://github.com/pnorman/ogr2osm  
(Optional) comment out mergePoints() under # Main flow  
Setup postgresql database and enable postgis  
su root  
su postgres  
createdb gis  
psql -d gis -c "create extension postgis;"  
psql -d gis -c "create user pat with password 'password';"  
Change details in pg2osm and load_csv to reflect database details if needed 
Download Geofabrik index to same folder as script https://download.geofabrik.de/index-v1.json

# Script Usage
Script is designed to be used from command line. The process is split into a separate arguments where possible. Each argument targets an iso3166-2(us:wa) or iso3166-1-alpha2(us) area except for update-oa which targets all urls in oa_urls(several GBs worth of data). Update-oa takes a long time so you may want to run it separately or download the files yourself if only building ares in one region. You must have OA data and a OSM area extract for the script to work properly. See a typical workflow below.

    ./processing.py us:wa --update-oa

Then as a cron job:

    00 02 20 * * cd /home/pat/projects/osmand_map_creation/osmand_osm/osm/;python3 processing.py us:ak us:hi us:mt us:ut us:nv us:az us:nm us:wy us:wa us:or us:id --load-oa --filter-data --output-osm --update-osm --quality-check --slice;cd /home/pat/projects/osmand_map_creation/;java -Djava.util.logging.config.file=logging.properties -Xms64M -Xmx7G -cp "./OsmAndMapCreator.jar:lib/OsmAnd-core.jar:./lib/*.jar" net.osmand.util.IndexBatchCreator batch.xml;cd /home/pat/projects/osmand_map_creation/osmand_osm;mv *.pbf osm/

This runs the script, builds the obfs, then moves the pbfs to the osm folder. Extra ram for osmand map creator will greatly speed up builds.

# Data Processing
Add sql statements in the filter_data function to remove unwanted records  
Add to sql statements to --sql flag in ogr2osm calls to filter data without removing records

# Limitations
Requires Geofabrik to have extract for area
Requires OpenAddresses to have data for area
iso3166-1-alpha2 areas are only supported if there are no iso3166-2 Geofabrik extracts eg. mx
No deduplication
Database info is hardcoded
Number of threads to use is hardcoded
Running many areas with update-osm may result in Geofabrik rate limiting  
ogr2osm xml writer will choke on unicode stops  
