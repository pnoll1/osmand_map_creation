# Linux Install
Put processing.py in directory where OpenAddresses download will be unzipped
Install ogr2ogr, osmium, postgresql, postgis, ogr2osm from github(install in /opt)
apt-get install curl osmium-tool postgresql postgis gdal-bin python3-gdal python3-lxml git
cd /opt
git clone --recursive https://github.com/pnorman/ogr2osm
Setup postgresql database and enable postgis
su root
su postgres
createdb gis
psql -d gis -c "create extension postgis;"
psql -d gis -c "create user pat with password 'password';"
Change details in pg2osm and load_csv to reflect database details
Change oa_root and root to correct paths

# Data Processing
Add to sql statements to --sql flag in ogr2osm calls or add code after load finished for complex processing

# Limitations
Setup for US states only
Running many states with update-osm will probably result in geofabrick rate limiting
ogr2osm xml writer will choke on unicode stops

