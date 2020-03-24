#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 20 13:07:40 2019

@author: pat
"""
import os
import json
from sys import argv
from subprocess import run
import psycopg2
'''
cli arguments

update-state
    download latest OSM state extract
'''
if len(argv) > 1:
    arg = argv[1]
else:
    arg = ''
    
def shp2osm(name, input_name,id_start, co=True):
    if co==True:
        os.system('python3 /opt/ogr2osm/ogr2osm.py -f --id={0} -t addr_{1}.py -o {1}_co_addresses.osm {2}'.format(id_start, name, input_name))
        stats = run('osmium fileinfo -ej {0}_co_addresses.osm'.format(name), shell=True, capture_output=True, encoding='utf8')
        id_end = json.loads(stats.stdout)['data']['minid']['nodes']
    return id_end
def pg2osm(name, number_field, id_start,co=True):
    if co==True:
        # check number field field type and changes sql statement accordingly
        if number_field:
            if 'character' in run('psql -d gis -c "select pg_typeof({0}) from \\"{1}\\" limit 1;"'.format(number_field, name), shell=True, capture_output=True, encoding='utf8').stdout:
                os.system('python3 /opt/ogr2osm/ogr2osm.py -f --id={0} -t addr_{1}.py -o {1}_co_addresses.osm "PG:dbname=gis user=pat password=password host=localhost" --sql "select * from \\"{1}\\" where {2} is not null and {2}!=\'0\'"'.format(id_start, name, number_field))
                stats = run('osmium fileinfo -ej {0}_co_addresses.osm'.format(name), shell=True, capture_output=True, encoding='utf8')
                id_end = json.loads(stats.stdout)['data']['minid']['nodes']
            elif 'integer' in run('psql -d gis -c "select pg_typeof({0}) from \\"{1}\\" limit 1;"'.format(number_field, name), shell=True, capture_output=True, encoding='utf8').stdout:
                os.system('python3 /opt/ogr2osm/ogr2osm.py -f --id={0} -t addr_{1}.py -o {1}_co_addresses.osm "PG:dbname=gis user=pat password=password host=localhost" --sql "select * from \\"{1}\\" where {2} is not null and {2}!=0"'.format(id_start, name, number_field))
                stats = run('osmium fileinfo -ej {0}_co_addresses.osm'.format(name), shell=True, capture_output=True, encoding='utf8')
                id_end = json.loads(stats.stdout)['data']['minid']['nodes']
    # handle cities
    else:
        if number_field:
            os.system('python3 /opt/ogr2osm/ogr2osm.py -f --id={0} -t addr_{1}.py -o city_of_{1}_addresses.osm "PG:dbname=gis user=pat password=password host=localhost" --sql "select * from \\"{1}\\" where {2} is not null and {2}!=0"'.format(id_start, name, number_field))
            stats = run('osmium fileinfo -ej city_of_{0}_addresses.osm'.format(name), shell=True, capture_output=True, encoding='utf8')
            id_end = json.loads(stats.stdout)['data']['minid']['nodes']
    # test case pg2osm('grant','number', 8588172730)
    return id_end
def all2osm():
    # decide if pg or shp source
    # run pg2osm or shp2osm
    return
def oa_upate():
    # sync oa sources
    return
def source_grab(url, name, oa_list, source_list):
    # merge oa list and source list
    # if shp
    # curl
    # if esri
    # esri2geojson url '{0}_co_addresses.geojson'.format(name)
    # ogr2ogr PG:dbname=gis {0}_co_addresses.geojson -nln {0} -append.format(name)
    return
def generate_coverage_file(names):
    '''
    accepts list of county names, creates osm file with those counties
    '''
    county_list_formatted = []
    county_list_formatted_string = ''
    for i in names:
        county_list_formatted.append(i.title() + '\ ' + 'County,')
    county_list_formatted_string = county_list_formatted_string.join(county_list_formatted)
    os.system('osmium tags-filter --overwrite /home/pat/projects/osmand_map_creation/background/or_counties.osm r/name={0} -o /home/pat/projects/osmand_map_creation/background/or_counties_covered.osm'.format(county_list_formatted_string))
    return
def generate_population_coverage(names):
    '''
    accepts list of county names, returns population coverage and coverage as percentage of state population
    '''
    county_list_formatted = []
    county_list_formatted_string = ''
    rows = []
    for i in names:
        county_list_formatted.append("'" + i.title() + " County, Washington',")
    county_list_formatted_string = county_list_formatted_string.join(county_list_formatted).rstrip(',')
    conn = psycopg2.connect("dbname='gis' user='pat' host='localhost' password='password'")
    cur = conn.cursor()
    cur.execute("select respop72018 from king_stats where geodisplaylabel in ({0})".format(county_list_formatted_string))
    rows=cur.fetchall()
    rows_list = [i[0] for i in rows]
    total_coverage = sum(rows_list)
    cur.execute("select respop72018 from king_stats")
    rows=cur.fetchall()
    rows_list = [i[0] for i in rows]
    total = sum(rows_list)
    percentage = round(total_coverage/total,2) * 100
    return total_coverage, percentage
#target_list = ['king', 'snohomish', 'pierce', 'thurston', 'clark', 'spokane', 'whatcom', 'kitsap', 'cowlitz', 'franklin', 'city of kennewick', 'skagit', 'grant']
target_list_county = ['lane', 'jackson', 'deschutes', 'marion', 'clackamas', 'multnomah', 'washington']

# ensure compatibility with maps.me build pipeline, must be positive and 48 bits or below
id_start = 2**33 # worked with some data issues 2**33-2*10**6, counts down
id_1 = pg2osm('lane', 'house_nbr', id_start)
# os.system('python3 /opt/ogr2osm/ogr2osm.py -f --id={0} -t addr_lane.py -o lane_co_addresses.osm "PG:dbname=gis user=pat password=password host=localhost" --sql "select * from lane where house_nbr is not null and house_nbr!=0"'.format(id_start))
# stats = run('osmium fileinfo -ej lane_co_addresses.osm', shell=True, capture_output=True, encoding='utf8')
# id_1 = json.loads(stats.stdout)['data']['minid']['nodes']
id_2 = pg2osm('jackson', 'addrnum', id_1)
# os.system('python3 /opt/ogr2osm/ogr2osm.py -f --id={0} -t addr_jackson.py -o jackson_co_addresses.osm "PG:dbname=gis user=pat password=password host=localhost" --sql "select * from jackson where addrnum is not null and addrnum!=\'0\'"'.format(id_1))
# stats = run('osmium fileinfo -ej jackson_co_addresses.osm', shell=True, capture_output=True, encoding='utf8')
# id_2 = json.loads(stats.stdout)['data']['minid']['nodes']
id_3 = pg2osm('deschutes', 'house_number', id_2)
# os.system('python3 /opt/ogr2osm/ogr2osm.py -f --id={0} -t addr_deschutes.py -o deschutes_co_addresses.osm "PG:dbname=gis user=pat password=password host=localhost" --sql "select * from deschutes where house_number is not null and house_number!=\'0\'"'.format(id_2))
# stats = run('osmium fileinfo -ej deschutes_co_addresses.osm', shell=True, capture_output=True, encoding='utf8')
# id_3 = json.loads(stats.stdout)['data']['minid']['nodes']
id_4 = shp2osm('marion', 'marion_co_address.shp', id_3)
# os.system('python3 /opt/ogr2osm/ogr2osm.py -f --id={0} -t addr_marion.py -o marion_co_addresses.osm marion_co_address.shp'.format(id_3))


if arg == 'update-state':
    os.system('curl --output oregon-latest.osm.pbf https://download.geofabrik.de/north-america/us/oregon-latest.osm.pbf')
os.system('osmium merge -Of pbf lane_co_addresses.osm jackson_co_addresses.osm deschutes_co_addresses.osm marion_co_addresses.osm oregon-latest.osm.pbf -o Us_oregon_northamerica_improved.osm.pbf')
# sort ascending for maps.me(osmconvert portion)
os.system('osmium sort --overwrite Us_oregon_northamerica_improved.osm.pbf -o Us_oregon_northamerica_improved.osm.pbf')
# Prep for QA
stats = run('osmium fileinfo -ej marion_co_addresses.osm', shell=True, capture_output=True, encoding='utf8')
stats_final = run('osmium fileinfo -ej Us_oregon_northamerica_improved.osm.pbf', shell=True, capture_output=True, encoding='utf8')
stats_state = run('osmium fileinfo -ej oregon-latest.osm.pbf', shell=True, capture_output=True, encoding='utf8')
# Check if items have unique ids
if json.loads(stats_final.stdout)['data']['multiple_versions'] == 'True':
    print('ERROR: Multiple items with same id')
# Check if added data overlaps with OSM ids
if json.loads(stats_state.stdout)['data']['maxid']['nodes'] >= json.loads(stats.stdout)['data']['minid']['nodes']:
    print('ERROR: Added data overlaps with OSM data') 
os.system('mv Us_oregon_northamerica_improved.osm.pbf ../../')
os.system('md5sum ../../Us_oregon_northamerica_improved.osm.pbf > ../../Us_oregon_northamerica_improved.osm.pbf.md5')
# coverage, coverage_percentage = generate_population_coverage(target_list_county)
# generate_coverage_file(target_list_county)

# run osmand build
#os.system('cd ~/projects/osmand_map_creation/OsmAndMapCreator-main')
#os.system('java -Djava.util.logging.config.file=logging.properties -Xms64M -Xmx6300M -cp "./OsmAndMapCreator.jar:lib/OsmAnd-core.jar:./lib/*.jar" net.osmand.util.IndexBatchCreator batch.xml')

# run mapsme build
# cd ~/projects/omim/tools/python
#python3 -m maps_generator --config maps_generator/var/etc/map_generator_oregon.ini  --skip="coastline" --countries="US_Oregon_Eugene,US_Oregon_Portland,US_Oregon_West"
