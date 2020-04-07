# Current Process
Download data sources manually or using esridump
Create addr_county.py translation file to expand addresses and drop unneeded source fields
Add source to processing file in processing section and merge command
Run processing script
Move pbf file to osmand_osm folder
Run OsmAndMapCreator

# Dedupe Process(Proposed)
After processing script, reload .osm files into postgresql using osm2pgsql
Use SQL to dedupe
Run ogr2osm
Run OsmAndMapCreator
