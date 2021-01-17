#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 21 00:52:36 2019

@author: pat
"""

import os
import json
from subprocess import run, CalledProcessError
from pathlib import Path
import argparse
from multiprocessing import Pool
import shutil

# commandline argument setup
parser = argparse.ArgumentParser(description='Process address data to a single osm file per state')
parser.add_argument('area-list', nargs='+', help='lowercase ISO 3166-1 alpha-2 country code and state/province eg us:wa')
parser.add_argument('--update-oa', action='store_true', help='downloads OA data for entire US')
parser.add_argument('--load-oa', action='store_true', help='loads OA data into database, overwriting previous')
parser.add_argument('--filter-data', action='store_true', help='delete unwanted data from database')
parser.add_argument('--output-osm', action='store_true', help='output data from database to OSM files')
parser.add_argument('--update-osm', action='store_true', help='downloads latest state extract, overwrites previous')
parser.add_argument('--quality-check', action='store_true', help='sort output file and run basic quality checks')
parser.add_argument('--slice', action='store_true', help='splits states into smaller regions if config present')
parser.add_argument('--all', action='store_true', help='use all options')
args = parser.parse_args()
if args.all:
    args.update_oa == True
    args.update_osm == True
    args.load_oa == True
    args.output_osm == True
    args.quality_check == True
    args.filter_data == True
area_list = vars(args)['area-list']
# follows geofabrik conventions
region_lookup = {'north-america':['us', 'ca', 'mx']}
country_name_expander = {'ca':'canada', 'mx':'mexico', 'us':'us'}
name_expander = {'us':{'al':'alabama', 'ak':'alaska','ar':'arkansas','az':'arizona','ca':'california','co':'colorado','ct':'connecticut', 'dc':'district of columbia','de':'delaware','fl':'florida','ga':'georgia','hi':'hawaii','ia':'iowa','id':'idaho','il':'illinois','in':'indiana', 'ks':'kansas','ky':'kentucky', 'la':'louisiana','me':'maine','md':'maryland','ma':'massachusetts','mi':'michigan', 'mn':'minnesota','ms':'mississippi','mo':'missouri', 'mt':'montana', 'nd':'north dakota', 'ne':'nebraska','nh':'new hampshire','nj':'new jersey','nm':'new mexico','ny':'new york','nc':'north carolina', 'nv':'nevada','oh':'ohio','ok':'oklahoma', 'or':'oregon','pa':'pennsylvania','ri':'rhode island','sc':'south carolina','sd':'south dakota','tn':'tennessee','tx':'texas','ut':'utah','vt':'vermont','va':'virginia','wa':'washington','wv':'west virginia','wi':'wisconsin','wy':'wyoming'}}

# download https://download.geofabrik.de/index-v1.json prior to running
def geofabrik_lookup(working_area):
    '''
    input: iso3166-2 code
    output: geofabrik pbf url
    '''
    with open('geofabrik_index-v1.json') as index_file:
        geofabrik_index = json.load(index_file)
        area_list = geofabrik_index['features']
        #print(area_list)
        for i in area_list:
            try:
                # handle countries iso3166-1
                # if i['properties']['iso3166-1:alpha2']==[state.short_name]:
                # handle subdivisions iso3166-2
                if i['properties']['iso3166-2']==[working_area.country.upper()+'-'+working_area.short_name.upper()]:
                    return i['properties']['urls']['pbf']
            except:
                pass
    # could not find matching area
    url = None
    return url
     

class WorkingArea():
    def __init__(self, name):
        self.name = name
        name_list = name.split(':')
        self.short_name = name_list[1]
        # self.geofabrik_region = region_lookup[country]
        self.country = name_list[0]
        self.directory = Path(self.country + '/' + self.short_name)
        self.master_list = None
        # self.country_expanded_name = country_name_expander[country]
        # self.expanded_name = subregion.expander[short_name]

    def __string__(self):
        return str(self.short_name)

def update_oa(url):
    '''
    input: url
    action: downloads urls and unzips them overwriting previous files
    output: none
    '''
    filename = Path(url).name
    run(['curl', '-o', filename, url])
    run(['unzip', '-o', filename])

def pg2osm(path, id_start, working_area):
    '''
    input: path object of openaddresses file , id to start numbering at, state name as string
    action: creates osm format file excluding rows with empty or 0 number fields from postgres db
    output: finishing id if successfull, input id if failed
    '''
    source_name = path.stem
    numbier_field = 'number'
    working_table = '{0}_{1}_{2}'.format(working_area.country, working_area.short_name, source_name)
    # find type of number field
    r = run('psql -d gis -c "select pg_typeof({0}) from \\"{1}\\" limit 1;"'.format(number_field, working_table), shell=True, capture_output=True, encoding='utf8').stdout
    if 'character' in r:
        try:
            os.system('python3 /opt/ogr2osm/ogr2osm.py -f --id={0} -t addr_oa.py -o {1}/{2}_addresses.osm "PG:dbname=gis user=pat password=password host=localhost" --sql "select * from \\"{3}\\" where {4} is not null and {4}!=\'\' and {4}!=\'0\'"'.format(id_start, working_area.directory, source_name, working_table, number_field))
        except Exception:
            print('ogr2osm failure')
            raise
            return id_start
        def handle_hashes_only(stats, working_area, working_table, source_name):
            stats = run('osmium fileinfo -ej {0}/{1}_addresses.osm'.format(working_area.directory, source_name), shell=True, capture_output=True, encoding='utf8')
            # handle files with hashes only
            try:
                id_end = json.loads(stats.stdout)['data']['minid']['nodes']
            except Exception:
                print('{0} is hashes only'.format(working_table))
                raise
                return id_start
        handle_hashes_only(stats, working_area, working_table, source_name)
    elif 'integer' in r or 'numeric' in r:
        try:
            os.system('python3 /opt/ogr2osm/ogr2osm.py -f --id={0} -t addr_oa.py -o {1}/{2}_addresses.osm "PG:dbname=gis user=pat password=password host=localhost" --sql "select * from \\"{3}\\" where {4} is not null and {4}!=0"'.format(id_start, working_area.directory, source_name, working_table, number_field))
        except Exception:
            print('ogr2osm failure')
            raise
            return id_start
        handle_hashes_only(stats, working_area, working_table, source_name)
    # handle empty file
    else:
        print('{0} is empty'.format(working_table))
        raise
        return id_start
    return id_end


def create_master_list(working_area, master_list):
    '''
    input: state as 2 letter abbrev., dict for sources to go into, root directory for oa
    output: dict with 2 letter state abbrev. as key and list of sources as value
    goes through each state folder and creates list of vrt files
    '''
    file_list = [] 
    for filename in working_area.directory.iterdir():
        # - is not allowed in postgres
        if '-' in filename.name and filename.suffix == '.vrt':
            filename_new = filename.parent.joinpath(Path(filename.name.replace('-', '_')))
            os.rename(filename, filename_new)
            file_list.append(filename_new)
        elif filename.suffix == '.vrt':
            file_list.append(filename)
        
    working_area.master_list = file_list
    print(working_area.name + ' ' + 'Master List Created')
    return


def load_oa(working_area):
    '''
    input: state as 2 letter abbrev., dict for sources
    action: loads oa csv into postgres+postgis db  
    output: none
    '''
    for j in working_area.master_list:
        source_name = j.stem
        run('ogr2ogr PG:dbname=gis {0} -nln {1}_{2}_{3} -overwrite -lco OVERWRITE=YES'.format(j, working_area.country, working_area.short_name, source_name), shell=True, capture_output=True, encoding='utf8')
    print(working_area.name + ' ' + 'Load Finished')
    return


def output_osm(working_area, id):
    '''
    input: state as 2 letter abbrev., dict for sources, id to start from, root of working path
    action: create folder for osm files, call pg2osm, remove failed sources from master list
    output: master_list with sources that were successfully written to file
    '''
    removal_list = []
    for j in working_area.master_list:
        # catch error and log file for removal from master list
        # sql join then output once quicker?
        try:
            print('writing osm file for ' + j.as_posix())
            id = pg2osm(j, id, working_area)
        except Exception:
            removal_list.append(j)
    # remove file from file list so merge will work
    for i in removal_list:
        working_area.master_list.remove(i)
    return


def update_osm(working_area, url):
    '''
    input: state as 2 letter abbrev., dict to expand state abbrev.
    action: downloads osm extract to corresponding folder
    output: none
    '''
    run('curl --output {0}/{1}-latest.osm.pbf {2}'.format(working_area.directory, working_area.short_name, url), shell=True, capture_output=True, encoding='utf8')
    return


def merge(state, master_list, state_expander):
    '''
    input: state as 2 letter abbrev., dict of sources to be merged, dict to expand state abbrev. to full name
    action: merged state pbf in state folder
    output: none
    '''
    list_files_string = []
    file_list = master_list.get(state)
    for i in file_list:
        list_files_string.append(i.as_posix())
    file_list_string = ' '.join(list_files_string).replace('us/', '').replace('.vrt', '_addresses.osm')
    state_expanded = state_expander.get(state)
    state_expanded = state_expanded.replace(' ', '-')
    try:
        run('osmium merge -Of pbf {0} {1}/{2}-latest.osm.pbf -o {1}/Us_{2}_northamerica_alpha.osm.pbf'.format(file_list_string, state, state_expanded), shell=True, capture_output=True, check=True, encoding='utf8')
    except Exception as e:
        print(e.stderr)
        print(state + ' ' + 'Merge Failed')
        return
    print(state + ' ' + 'Merge Finished')
    return

def prep_for_qa(state, state_expander, master_list):
    '''
    input: state abbrev, state_expander dict, master_list
    output: stats for last source ran, state extract and final file
    '''
    state_expanded = state_expander.get(state)
    state_expanded = state_expanded.replace(' ', '-')
    # osmium sort runs everything in memory, may want to use osmosis instead
    run('osmium sort --overwrite {0}/Us_{1}_northamerica_alpha.osm.pbf -o {0}/Us_{1}_northamerica_alpha.osm.pbf'.format(state, state_expanded), shell=True, encoding='utf8')
    # find last source ran
    file_list = master_list.get(state)
    last_source = Path(Path(file_list[-1]).as_posix().replace('us/', '').replace('.vrt', '_addresses.osm'))
    print(last_source.as_posix())
    # get data for last source ran
    try:
        stats = run('osmium fileinfo -ej {0}'.format(last_source), shell=True, capture_output=True ,check=True , encoding='utf8')
    except Exception as e:
        print(e.stderr)
        ready_to_move=False
    # get data for OSM extract
    try:
        stats_state = run('osmium fileinfo -ej {0}/{1}-latest.osm.pbf'.format(state, state_expanded), shell=True, capture_output=True ,check=True , encoding='utf8')
    except Exception as e:
        print(e.stderr)
        ready_to_move=False
    # get data for completed state file
    try:
        stats_final = run('osmium fileinfo -ej {0}/Us_{1}_northamerica_alpha.osm.pbf'.format(state, state_expanded), shell=True, capture_output=True ,check=True , encoding='utf8')
    except Exception as e:
        print(e.stderr)
        ready_to_move=False
    return stats, stats_state, stats_final

def quality_check(stats, stats_state, stats_final, ready_to_move):
    '''
    input: stats for last source ran, state extract and final file
    output: boolean that is True for no issues or False for issues
    '''
    # file is not empty
    # Check if items have unique ids
    if json.loads(stats_final.stdout)['data']['multiple_versions'] == 'True':
        print('ERROR: Multiple items with same id')
        ready_to_move = False
    # Check if added data overlaps with OSM ids
    if json.loads(stats_state.stdout)['data']['maxid']['nodes'] >= json.loads(stats.stdout)['data']['minid']['nodes']:
        print('ERROR: Added data overlaps with OSM data')
        ready_to_move = False
    return ready_to_move

def move(state, state_expander, ready_to_move, pbf_output, sliced_state=None):
    '''
    input: state abbrev, state_expander dict, ready_to_move boolean, pbf_output location
    action: moves final file to pbf_output location
    output: nothing
    '''
    state_expanded = state_expander.get(state)
    state_expanded = state_expanded.replace(' ', '-')
    # move sliced files
    if sliced_state is not None and ready_to_move:
        for slice_config in sliced_state:
            slice_name = slice_config[0]
            run(['mv','{0}/Us_{1}_{2}_northamerica_alpha.osm.pbf'.format(state, state_expanded, slice_name), pbf_output])
    # move all other files
    elif ready_to_move:
        run(['mv','{0}/Us_{1}_northamerica_alpha.osm.pbf'.format(state, state_expanded), pbf_output])

def filter_data(working_area):
    '''
    input: state, master_list
    action: delete records with bad data
    output: none
    '''
    number_field = 'number'
    for j in working_area.master_list:
        source_name = j.stem
        working_table = '{0}_{1}_{2}'.format(working_area.country, working_area.short_name, source_name)
        # delete records with -- in nubmer field eg rancho cucamonga
        r = run('psql -d gis -c "DELETE from \\"{1}\\" where {0}="--";"'.format(number_field, working_table), shell=True, capture_output=True, encoding='utf8')
        print(r.stdout)
        # print('Removed -- from {0}_{1}'.format(name, state))
        # take standard shell and run through shlex.split to use run properly
        # delete record with illegal unicode chars in number field
        r = run( ['psql', '-d', 'gis', '-c', "delete from \"{1}\" where {0} ~ '[\x01-\x08\x0b\x0c\x0e-\x1F\uFFFE\uFFFF]';".format(number_field, working_table)], capture_output=True, encoding='utf8')
        print(r.stdout)
        # print('Removed illegal unicode from {0}_{1}'.format(name, state))

def slice(state, state_expander):
    '''
    input: state, state_expander, (name of slice and bounding box coordinates in lon,lat,lon,lat)
    file requirement: file must be sorted for osmium extract to work; running --quality-check handles this
    action: slices merged files according to config
    output: config of sliced state

    # states above ~200MB can crash osmand map generator, slice into smaller regions before processing
    '''
    config = {}
    config['co'] = [['north', '-109.11,39.13,-102.05,41.00'], ['south', '-109.11,39.13,-102.04,36.99']]
    config['fl'] = [['north', '-79.75,27.079,-87.759,31.171'], ['south', '79.508,24.237,-82.579,27.079']]
    config['tx'] = [['southeast','-96.680,24.847,-93.028,30.996'],['northeast','-96.680,24.847,-93.028,30.996'],['northwest','-96.028,30.996,-108.391,36.792'],['southwest','-96.028,30.996,-107.556,25.165']]
    config['ca'] = [['north','-119.997,41.998,-125.365,38.964'],['northcentral','-125.365,38.964,-114.049,37.029'],['central','-114.049,37.029,-123.118,34.547'],['southcentral','-123.118,34.547,-113.994,33.312'],['south','-113.994,33.312,-119.96,31.85']]
    state_expanded = state_expander.get(state)
    if state in config.keys():
        for slice_config in config[state]:
            # better as dict?
            slice_name = slice_config[0]
            bounding_box = slice_config[1]
            try:
                run('osmium extract -O -b {3} -o {0}/Us_{1}_{2}_northamerica_alpha.osm.pbf {0}/Us_{1}_northamerica_alpha.osm.pbf'.format(state, state_expanded, slice_name, bounding_box), shell=True, capture_output=True, check=True,encoding='utf8')
            except Exception as e:
                print(e.stderr)
        sliced_state = config[state]
        return sliced_state

# main program flow
def run_all(area):
    # root assumed to be child folder of pbf_output
    root = Path('/home/pat/projects/osmand_map_creation/osmand_osm/osm/')
    pbf_output = root.parent
    master_list = {}
    # id to count down from for each state
    id = 2**33
    working_area = WorkingArea(area)
    master_list = create_master_list(working_area, master_list)
    if args.load_oa == True:
        load_oa(working_area)
    if args.filter_data:
        filter_data(working_area)
    if args.output_osm:
        output_osm(working_area, id)
    if args.update_osm == True:
        url = geofabrik_lookup(working_area)
        update_osm(working_area, url)
    if args.output_osm:
        merge(state, master_list, state_expander)
    # allows running without quality check
    ready_to_move = True
    if args.quality_check:
        stats, stats_state, stats_final = prep_for_qa(state, state_expander, master_list)
        ready_to_move = quality_check(stats, stats_state, stats_final,ready_to_move)
    if args.slice:
        sliced_state = slice(state, state_expander)
    if args.output_osm and args.slice:
        move(state, state_expander, ready_to_move, pbf_output, sliced_state) 
    elif args.output_osm:
        move(state, state_expander, ready_to_move, pbf_output) 

if __name__ == '__main__':
    # Ram can be limit with large files, consider switching pool to 1 or doing 1 state at a time with cron job
    with Pool(2) as p:
        # OA regions don't correspond to states and download slowly, run before main flow
        if args.update_oa == True:
            oa_urls = ['https://data.openaddresses.io/openaddr-collected-us_midwest.zip', 'https://data.openaddresses.io/openaddr-collected-us_south.zip', 'https://data.openaddresses.io/openaddr-collected-us_west.zip', 'https://data.openaddresses.io/openaddr-collected-us_northeast.zip']
            p.map(update_oa, oa_urls)
        p.map(run_all, area_list)
