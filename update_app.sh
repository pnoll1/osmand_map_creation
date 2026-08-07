#! /bin/sh

install_dir=/home/pat/projects/osmand_map_creation
# update dependencies
sudo apt-get update 
sudo apt-get upgrade -y
sudo pip3 install -U ogr2osm psycopg2-binary
# update code
git pull
# Download OsmAnd Map Creator
cd $install_dir
# remove old file
rm OsmAndMapCreator-main.zip
wget http://download.osmand.net/latest-night-build/OsmAndMapCreator-main.zip
unzip -o OsmAndMapCreator-main.zip -d osmand_map_creator
# restore settings
cp osmand_map_creator/batch.xml.template osmand_map_creator/batch.xml
