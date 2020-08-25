#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 20 13:07:40 2019

@author: pat
"""
import os
import json
from subprocess import run
import psycopg2
import argparse

# commandline argument setup
parser = argparse.ArgumentParser(description='Process address data to a single osm file per state')
#parser.add_argument('state-list', nargs='+', help='lowercase 2 letter state abbreviation')
parser.add_argument('--update-osm', action='store_true')
parser.add_argument('--load-source', action='store_true')
parser.add_argument('--output-osm', action='store_true')
args = parser.parse_args()

# ensure compatibility with maps.me build pipeline, must be positive and 48 bits or below
id_start = 2**34  # worked with some data issues 2**33-2*10**6, counts down


def shp2osm(name, input_name, id_start, co=True):
    if co == True:
        os.system('python3 /opt/ogr2osm/ogr2osm.py -f --id={0} -t addr_{1}.py -o {1}_co_addresses.osm {2}'.format(id_start, name, input_name))
        stats = run('osmium fileinfo -ej {0}_co_addresses.osm'.format(name), shell=True, capture_output=True, encoding='utf8')
        id_end = json.loads(stats.stdout)['data']['minid']['nodes']
    return id_end


def pg2osm(name, number_field, id_start, co=True):
    if co == True:
        # check number field field type and changes sql statement accordingly
        if number_field:
            if 'character' in run('psql -d gis -c "select pg_typeof({0}) from \\"{1}\\" limit 1;"'.format(number_field, name), shell=True, capture_output=True, encoding='utf8').stdout:
                os.system('python3 /opt/ogr2osm/ogr2osm.py -f --id={0} -t addr_{1}.py -o {1}_co_addresses.osm "PG:dbname=gis user=pat password=password host=localhost" --sql "select * from \\"{1}\\" where {2} is not null and {2}!=\'\' and {2}!=\'0\'"'.format(id_start, name, number_field))
                stats = run('osmium fileinfo -ej {0}_co_addresses.osm'.format(name), shell=True, capture_output=True, encoding='utf8')
                id_end = json.loads(stats.stdout)['data']['minid']['nodes']
            elif 'integer' or 'numeric' in run('psql -d gis -c "select pg_typeof({0}) from \\"{1}\\" limit 1;"'.format(number_field, name), shell=True, capture_output=True, encoding='utf8').stdout:
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


def update_sources(url, name):
    # merge oa list and source list
    # if shp
    # curl
    # if esri
    #subprocess.run([os.path.join(env,'/opt/esridump/bin/python3', 'esri2geojson {0} {1}_co_addresses.geojson'].format(url, name))
    # esri2geojson https://gis.spokanecounty.org/arcgis/rest/services/OpenData/Property/MapServer/12 spokane_co_addresses.geojson
    # esri2geojson url '{0}_co_addresses.geojson'.format(name)
    return


def load_source(name, path):
    os.system('ogr2ogr PG:dbname=gis {0}_addresses.geojson -nln {0} -overwrite'.format(name, path))


# update osm data
def update_osm(state, state_expander):
    state_expanded = state_expander.get(state)
    # format for url
    state_expanded = state_expanded.replace(' ', '-')
    run('curl --output {0}-latest.osm.pbf https://download.geofabrik.de/north-america/us/{0}-latest.osm.pbf'.format(state_expanded), shell=True, capture_output=True, encoding='utf8')
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
    os.system('osmium tags-filter --overwrite /home/pat/projects/osmand_map_creation/background/wa_counties.osm r/name={0} -o /home/pat/projects/osmand_map_creation/background/wa_counties_covered.osm'.format(county_list_formatted_string))
    return


def generate_population_coverage(names):
    '''
    accepts list of county names
    returns population coverage and coverage as percentage of state population
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
    rows = cur.fetchall()
    rows_list = [i[0] for i in rows]
    total_coverage = sum(rows_list)
    cur.execute("select respop72018 from king_stats")
    rows = cur.fetchall()
    rows_list = [i[0] for i in rows]
    total = sum(rows_list)
    percentage = round(total_coverage/total, 2) * 100
    return total_coverage, percentage


# hold information for each source
class Source:
    def __init__(self, name):
        self.name = name
        source_url = ''
        source_path = ''

    def __str__(self):
        return self.name
    # translation file properties, would allow translating while going into db


target_list_county = ['king', 'snohomish', 'pierce', 'thurston', 'clark', 'spokane', 'whatcom', 'kitsap', 'cowlitz', 'franklin', 'skagit', 'grant', 'island']

state_expander = {'al':'alabama', 'ak':'alaska','ar':'arkansas','az':'arizona','ca':'california','co':'colorado','ct':'connecticut','de':'delaware','fl':'florida','ga':'georgia','hi':'hawaii','ia':'iowa','id':'idaho','il':'illinois','in':'indiana', 'ks':'kansas','ky':'kentucky', 'la':'louisiana','me':'maine','md':'maryland','ma':'massachusetts','mi':'michigan', 'mn':'minnesota','ms':'mississippi','mo':'missouri', 'mt':'montana', 'nd':'north dakota', 'ne':'nebraska','nh':'new hampshire','nj':'new jersey','nm':'new mexico','ny':'new york','nc':'north carolina', 'nv':'nevada','oh':'ohio','ok':'oklahoma', 'or':'oregon','pa':'pennsylvania','ri':'rhode island','sc':'south carolina','sd':'south dakota','tn':'tennessee','tx':'texas','ut':'utah','vt':'vermont','va':'virginia','wa':'washington','wv':'west virginia','wi':'wisconsin','wy':'wyoming'}

if args.update_osm == True:
    update_osm('wa', state_expander)
# instantiate objects for each source and load into dictionary
load_source
id = pg2osm('king', 'addr_num', id_start)
id_2 = pg2osm('snohomish', 'add_number', id)
id_3 = shp2osm('pierce', 'Address_Points.shp', id_2)
id_4 = shp2osm('thurston', 'Thurston_Address_Points_TCOMM.shp', id_3)
id_5 = shp2osm('clark', 'Situs.shp', id_4)
# id_6 = shp2osm('spokane', 'Addresses.shp', id_5)
# esri2geojson https://gis.spokanecounty.org/arcgis/rest/services/OpenData/Property/MapServer/12 spokane_co_addresses.geojson
# ogr2ogr PG:dbname=gis spokane_co_addresses.geojson -nln spokane -append
id_6 = pg2osm('spokane', 'addrnum', id_5)
id_7 = shp2osm('whatcom', 'COB_Shps/COB_land_AddressPoints.shp', id_6)
id_8 = shp2osm('kitsap', 'kitsap/parcel/siteaddr.shp', id_7)
# esri2geojson http://www.cowlitzinfo.net:6080/arcgis/rest/services/WSPublic/WSAddressPoints/MapServer/0 wa/cowlitz_co.geojson
# ogr2ogr PG:dbname=gis cowlitz_co.geojson -nln cowlitz -append
id_9 = pg2osm('cowlitz', 'add_number', id_8)
# http://franklingis.org/Data/Address_Web.zip
id_10 = shp2osm('franklin', 'franklin_co_addresses.shp', id_9)
id_11 = pg2osm('kennewick', 'streetnumber', id_10)
id_12 = pg2osm('skagit', 'housenumber', id_11)
# grant is sql keyword, needs to be double quoted and escaped from multiple shells
id_13 = pg2osm('grant', 'number', id_12)
id_14 = pg2osm('island', 'addrnum', id_13)
# esri2geojson http://www.skagitcounty.net/gispublic/rest/services/Assessor/PropertyMap/MapServer/3 skagit_co_addresses.geojson
# select * from planet_osm_polygon, skagit where ST_Disjoint(planet_osm_polygon.way,ST_Transform(skagit.wkb_geometry,3857));
# esri2geojson https://maps.ci.kennewick.wa.us/arcgis/rest/services/Public/AllGISLayers/MapServer/92/ kennewick_co_addresses.geojson
# ogr2ogr PG:dbname=gis city_of_kennewick_addresses.geojson -nln kennewick -append
# python3 /opt/ogr2osm/ogr2osm.py -f --id=8588423909 -t addr_yakima.py -o yakima_co_addresses.osm --sql "select * from yakima where street not like '%&%' AND street not like '%#%'AND street not like '%-%'AND street not like '%1/2%' AND street not like '%,%' AND street not like '%/%' AND street not like '%of%' AND street not like '%Ste%' AND street not like '% APT %' AND street not like '%UNIT%' AND number!=0 and number is not null" "PG:dbname=gis user=pat password=password host=localhost"
# https://data-islandcountygis.opendata.arcgis.com/datasets/address-points?page=3509

os.system('osmium merge -Of pbf king_co_addresses.osm snohomish_co_addresses.osm pierce_co_addresses.osm thurston_co_addresses.osm clark_co_addresses.osm spokane_co_addresses.osm whatcom_co_addresses.osm kitsap_co_addresses.osm cowlitz_co_addresses.osm franklin_co_addresses.osm city_of_kennewick_addresses.osm skagit_co_addresses.osm grant_co_addresses.osm island_co_addresses.osm washington-latest.osm.pbf -o Us_washington_northamerica_improved.osm.pbf')
# sort ascending for maps.me(osmconvert portion)
os.system('osmium sort --overwrite Us_washington_northamerica_improved.osm.pbf -o Us_washington_northamerica_improved.osm.pbf')
# Prep for QA
stats = run('osmium fileinfo -ej grant_co_addresses.osm', shell=True, capture_output=True, encoding='utf8')
stats_final = run('osmium fileinfo -ej Us_washington_northamerica_improved.osm.pbf', shell=True, capture_output=True, encoding='utf8')
stats_state = run('osmium fileinfo -ej washington-latest.osm.pbf', shell=True, capture_output=True, encoding='utf8')
# Check if items have unique ids
if json.loads(stats_final.stdout)['data']['multiple_versions'] == 'True':
    print('ERROR: Multiple items with same id')
# Check if added data overlaps with OSM ids
if json.loads(stats_state.stdout)['data']['maxid']['nodes'] >= json.loads(stats.stdout)['data']['minid']['nodes']:
    print('ERROR: Added data overlaps with OSM data')
os.system('mv Us_washington_northamerica_improved.osm.pbf ../../')
os.system('md5sum ../../Us_washington_northamerica_improved.osm.pbf > ../../Us_washington_northamerica_improved.osm.pbf.md5')
coverage, coverage_percentage = generate_population_coverage(target_list_county)
generate_coverage_file(target_list_county)
# run osmand build
# os.system('cd ~/projects/osmand_map_creation/OsmAndMapCreator-main')
# os.system('java -Djava.util.logging.config.file=logging.properties -Xms64M -Xmx6300M -cp "./OsmAndMapCreator.jar:lib/OsmAnd-core.jar:./lib/*.jar" net.osmand.util.IndexBatchCreator batch.xml')

# run mapsme build
# cd ~/projects/omim/tools/python
# add --config with different ini file for WA pbf
# python3 -m maps_generator --config maps_generator/var/etc/map_generator_washington.ini  --skip="coastline" --countries="US_Washington_Seattle,US_Washington_Coast,US_Washington_Yakima"
