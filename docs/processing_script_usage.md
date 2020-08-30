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
Change details in pg2osm and load_csv to reflect database details  
Change oa_root and root to correct paths  

# Script Usage
Script is designed to be used from command line. The process is split into a separate arguments where possible. Each argument targets a state except for update-oa which targets the entire US. Update-oa takes a long time so you may want to run it separately or download the files yourself if only building states in one region. You must have OA data and a OSM state extract for the script to work properly. See a typical workflow below.

    ./processing.py wa --update-oa

Then as a cron job:

    00 02 20 * * cd /home/pat/projects/osmand_map_creation/osmand_osm/osm/;python3 processing.py ak hi mt ut nv az nm wy wa or id --load-oa --filter-data --output-osm --update-osm;cd /home/pat/projects/osmand_map_creation/;java -Djava.util.logging.config.file=logging.properties -Xms64M -Xmx7G -cp "./OsmAndMapCreator.jar:lib/OsmAnd-core.jar:./lib/*.jar" net.osmand.util.IndexBatchCreator batch.xml;cd /home/pat/projects/osmand_map_creation/osmand_osm;mv *.pbf osm/

This runs the script, builds the obfs, then moves the pbfs to the osm folder. Extra ram for osmand map creator will greatly speed up builds.

# Data Processing
Add sql statements in the filter_data function to remove unwanted records  
Add to sql statements to --sql flag in ogr2osm calls to filter data without removing records

# Limitations
Setup for US states only  
Running many states with update-osm may result in geofabrick rate limiting  
ogr2osm xml writer will choke on unicode stops  
