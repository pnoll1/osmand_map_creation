#! /bin/sh
# Run in directory where OpenAddresses download will be unzipped  
install_dir=$PWD
# Install ogr2ogr, osmium, postgresql, postgis, ogr2osm from github(install in /opt)  
sudo apt-get install curl osmium-tool postgresql postgis gdal-bin python3-gdal python3-lxml git  
cd /opt  
git clone --recursive https://github.com/pnorman/ogr2osm  
# Setup postgresql database and enable postgis
sudo -u postgres createdb gis
sudo -u postgres psql -d gis -c "create extension postgis;"
# Change user to your username
sudo -u postgres psql -d gis -c "create user pat with password 'password';"  
# Download Geofabrik index to same folder as script
cd $install_dir
curl https://download.geofabrik.de/index-v1.json -o geofabrik_index-v1.json
# Change details in config.py if needed

