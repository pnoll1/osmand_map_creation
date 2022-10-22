#! /bin/sh

install_dir=/home/pat/projects/osmand_map_creation
# update dependencies
sudo apt-get update
sudo apt-get install -y curl osmium-tool postgresql postgis gdal-bin wget git python3-pip unzip
sudo pip3 install -U ogr2osm psycopg2-binary
# update code
git pull
# Download OsmAnd Map Creator
wget http://download.osmand.net/latest-night-build/OsmAndMapCreator-main.zip
unzip -o OsmAndMapCreator-main.zip
cd $install_dir
cp batch.xml.template batch.xml
