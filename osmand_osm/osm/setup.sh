#! /bin/sh
# Read script before running!
# Commands may overwrite existing files, backup before running
# Some comments describe manual steps that need to be done
# Made for Debian unstable, commands may need tweaking for other distros
# Run in top level of project
install_dir=$PWD
# Install ogr2ogr, osmium, postgresql, postgis, ogr2osm globally via pip
sudo apt-get install curl osmium-tool postgresql postgis gdal-bin python3-gdal python3-lxml wget
sudo pip3 install --system ogr2osm
# Download OsmAnd Map Creator
wget http://download.osmand.net/latest-night-build/OsmAndMapCreator-main.zip
unzip -o OsmAndMapCreator-main.zip
cp batch.xml.template batch.xml
# Fill out batch.xml with proper paths
# Create directory structure for map creator
mkdir osmand_obf
mkdir osmand_osm
mkdir osmand_osm/osm
mkdir osmand_gen
# Download srtm files(~200GB)
#wget -r -nH https://builder.osmand.net/terrain/
# Setup postgresql database and enable postgis
sudo -u postgres createdb gis
sudo -u postgres psql -d gis -c "create extension postgis;"
# Change user to your username
sudo -u postgres psql -d gis -c "create user pat with password 'password';"  
# Download Geofabrik index to same folder as script
cd $install_dir/osmand_osm/osm
wget https://download.geofabrik.de/index-v1.json
touch secrets.py
# add OA token obtained from OA website in secrets.py as oa_token = 'token_data'
# replace token_data with token leaving apostrophes since it should be a string
cp config.py.template config.py
# Change details in config.py if needed

