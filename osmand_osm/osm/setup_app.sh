#! /bin/sh
# Read script before running!
# Commands may overwrite existing files, backup before running
# Some comments describe manual steps that need to be done
# Made for Debian unstable, commands may need tweaking for other distros
# assumes setup_container.sh and lxc-attach have already been run
# Run this script in root level of container

# setup normal user
adduser --disabled-password --gecos "User" pat
mkdir /home/pat/projects
cd /home/pat/projects
# Install dependencies
sudo apt-get install -y curl osmium-tool postgresql postgis gdal-bin wget git python3-pip unzip
sudo pip3 install ogr2osm
# download source since switch to OA
sudo git clone https://github.com/pnoll1/osmand_map_creation.git --shallow-since='2020-08-25 22:00 -0700'
install_dir=/home/pat/projects/osmand_map_creation
cd $install_dir
# Create directory structure for map creator
mkdir osmand_obf
mkdir osmand_gen
mkdir terrain
# Download OsmAnd Map Creator
wget http://download.osmand.net/latest-night-build/OsmAndMapCreator-main.zip
unzip -o OsmAndMapCreator-main.zip
cp batch.xml.template batch.xml
# Fill out batch.xml with proper paths
# Download srtm files(~200GB)
# wget -r -nH https://builder.osmand.net/terrain/
# Setup postgresql database and enable postgis
sudo -u postgres createdb gis
sudo -u postgres psql -d gis -c "create extension postgis;"
# Change user to your username
sudo -u postgres psql -d gis -c "create user pat with password 'password';"  
# Download Geofabrik index to same folder as script
cd $install_dir/osmand_osm/osm
wget https://download.geofabrik.de/index-v1.json
touch secrets.py
echo "add OA token obtained from OA website in secrets.py as oa_token = 'token_data'"
cp config.template config.py
# Change details in config.py if needed
sudo chown -R pat /home/pat/projects
