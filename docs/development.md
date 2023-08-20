# Architecture
The program was built with flexibility and low maintenance as key factors.

The process is:
    1. OpenAddresses(OA) data is downloaded using wget
    1. OA data is loaded into Postgresql using ogr2ogr
    1. OA data is filtered with sql
    1. OA data is exported to osm xml format using ogr2osm
    1. OSM area extracts downloaded from Geofabrik
    1. OA data is merged with OSM area extracts while converting to osm.pbf using osmium merge
    1. files checked for errors
    1. areas with slice configs are sliced into smaller files
    1. merged files are moved to build folder
    1. osmand map creator builds obf files and puts output in osmand_obf folder
    1. merged files moved to osm folder
    1. repeat previous steps with next batch until all done
    1. obf file names cleaned
    1. file hashes calculated

# Contributing
It's recommended to open an issue with the idea first. Download setup_app.sh and setup_container.sh.

    ./setup_container.sh 
    lxc-start osmand_map_creation
    lxc-attach osmand_map_creation
    ./setup_app.sh. 

Try running unit tests to make sure everything is working. Start your own feature branch to make changes. Make a PR on Github when you've got your changes working.

# Testing
Project uses unittest for testing. In the osm directory, run python3 -m unittest tests.py to run tests. Run unit tests only with python3 -m unittest tests.UnitTests.

## Unit Tests
Test data is stored in aa and ab folders. Find a test case for your change and insert into corresponding geojson file. Use processing.py --load-oa aa(or ab depending on change) to load data into postgres. Use pg_dump -d gis -t tablename > filename.sql to replace current sql file. Add your test to tests.py.
