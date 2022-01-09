#! /bin/sh
# Run in directory where OpenAddresses(OA) download will be unzipped  
install_dir=$PWD
# Install ogr2ogr, osmium, postgresql, postgis, ogr2osm globally via pip
sudo apt-get install curl osmium-tool postgresql postgis gdal-bin python3-gdal python3-lxml git  
sudo pip3 install --system ogr2osm
# Setup postgresql database and enable postgis
sudo -u postgres createdb gis
sudo -u postgres psql -d gis -c "create extension postgis;"
# Change user to your username
sudo -u postgres psql -d gis -c "create user pat with password 'password';"  
# Download Geofabrik index to same folder as script
cd $install_dir
curl https://download.geofabrik.de/index-v1.json -o geofabrik_index-v1.json
touch secrets.py
# add OA token obtained from OA website in secrets.py as oa_token = 'token_data'
# replace token_data with token leaving apostrophes since it should be a string
# Change details in config.py if needed

